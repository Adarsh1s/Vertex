#!/usr/bin/env python3
"""
FinPulse / Vertex — Local Database Proxy for DBeaver & SQL Clients
Bypasses ISP / Firewall blocks on port 5432 by tunneling database traffic 
over HTTPS WebSocket (Port 443) directly into Neon Cloud PostgreSQL.
"""
import asyncio
import sys
import logging

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import websockets
except ImportError:
    print("\n[ERROR] 'websockets' library is required. Run: pip install websockets\n")
    sys.exit(1)

NEON_HOST = "ep-long-meadow-a10ypauu.ap-southeast-1.aws.neon.tech"
LOCAL_PORT = 5434
TARGET_WS_URL = f"wss://{NEON_HOST}/v2"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("db_proxy")

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    client_addr = writer.get_extra_info('peername')
    logger.info(f"Incoming SQL connection from {client_addr}")
    try:
        async with websockets.connect(
            TARGET_WS_URL,
            max_size=None,
            ping_interval=20,
            ping_timeout=20
        ) as ws:
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
            for t in pending:
                t.cancel()
    except Exception as exc:
        logger.warning(f"Connection closed for {client_addr}: {exc}")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", LOCAL_PORT)
    banner = f"""
========================================================================
  [*] FINPULSE / VERTEX: LOCAL DATABASE PROXY ACTIVE
========================================================================
  Listening on:     127.0.0.1:{LOCAL_PORT}
  Forwarding to:    {TARGET_WS_URL} (Port 443 WSS)
------------------------------------------------------------------------
  [+] IN DBEAVER / PGADMIN / DATAGRIP, CONNECT USING:
  * Host:           127.0.0.1   (or localhost)
  * Port:           5434
  * Database:       FinPulse
  * Username:       neondb_owner
  * Password:       npg_Nknlf8FTow7Q
  * SSL Tab:        Unchecked / Disabled
                    (Traffic is already encrypted over HTTPS WSS port 443)
------------------------------------------------------------------------
  Keep this window OPEN while running queries in DBeaver.
  Press Ctrl + C to stop the proxy anytime.
========================================================================
"""
    print(banner)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Database proxy stopped by user.")
