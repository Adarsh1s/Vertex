import asyncio
import logging
from typing import Optional
import websockets

logger = logging.getLogger("finpulse.neon_proxy")

_proxy_server: Optional[asyncio.Server] = None
_proxy_port: int = 5434
_target_host: Optional[str] = None
_proxy_running: bool = False

async def _handle_client(target_ws_url: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Bridge bidirectional TCP traffic from local client to Neon WebSocket proxy."""
    try:
        async with websockets.connect(target_ws_url, max_size=None, ping_interval=20, ping_timeout=20) as ws:
            async def tcp_to_ws():
                try:
                    while True:
                        data = await reader.read(65536)
                        if not data:
                            break
                        await ws.send(data)
                except Exception:
                    pass
                finally:
                    try:
                        await ws.close()
                    except Exception:
                        pass

            async def ws_to_tcp():
                try:
                    async for msg in ws:
                        if isinstance(msg, str):
                            msg = msg.encode()
                        writer.write(msg)
                        await writer.drain()
                except Exception:
                    pass

            t1 = asyncio.create_task(tcp_to_ws())
            t2 = asyncio.create_task(ws_to_tcp())
            done, pending = await asyncio.wait([t1, t2], return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
    except Exception as exc:
        logger.debug(f"Neon proxy client error: {exc}")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

async def start_neon_proxy(target_host: str, listen_port: int = 5434) -> int:
    """Starts local TCP server that tunnels connections to Neon via WebSocket port 443."""
    global _proxy_server, _proxy_port, _target_host, _proxy_running
    if _proxy_running:
        return _proxy_port

    _target_host = target_host
    _proxy_port = listen_port
    target_ws_url = f"wss://{target_host}/v2"

    async def client_cb(reader, writer):
        await _handle_client(target_ws_url, reader, writer)

    _proxy_server = await asyncio.start_server(client_cb, "127.0.0.1", _proxy_port)
    _proxy_running = True
    logger.info(f"Neon WebSocket proxy listening on 127.0.0.1:{_proxy_port} -> {target_ws_url}")
    return _proxy_port

async def stop_neon_proxy():
    global _proxy_server, _proxy_running
    if _proxy_server and _proxy_running:
        _proxy_server.close()
        await _proxy_server.wait_closed()
        _proxy_running = False
        logger.info("Neon WebSocket proxy stopped.")
