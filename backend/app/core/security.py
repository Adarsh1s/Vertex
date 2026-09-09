import base64
import json
import urllib.request
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

bearer_scheme = HTTPBearer()
_jwks_cache: Optional[Dict[str, Any]] = None

def _fetch_jwks() -> Dict[str, Any]:
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    try:
        req = urllib.request.Request(settings.NEON_AUTH_JWKS_URL, headers={"User-Agent": "FinPulse-Backend"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            _jwks_cache = json.loads(resp.read().decode())
            return _jwks_cache
    except Exception:
        return {"keys": []}

def _verify_eddsa_token(token: str) -> Optional[str]:
    """Verify an EdDSA token using the Neon Auth JWKS keys."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        
        # Decode header to find key ID
        header_padding = "=" * (-len(header_b64) % 4)
        header = json.loads(base64.urlsafe_b64decode(header_b64 + header_padding))
        if header.get("alg") != "EdDSA":
            return None
        
        kid = header.get("kid")
        jwks = _fetch_jwks()
        target_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid and key.get("crv") == "Ed25519":
                target_key = key
                break
        if not target_key:
            return None
        
        x_b64 = target_key.get("x")
        x_padding = "=" * (-len(x_b64) % 4)
        pub_bytes = base64.urlsafe_b64decode(x_b64 + x_padding)
        pubkey = Ed25519PublicKey.from_public_bytes(pub_bytes)
        
        message = f"{header_b64}.{payload_b64}".encode("ascii")
        sig_padding = "=" * (-len(sig_b64) % 4)
        sig_bytes = base64.urlsafe_b64decode(sig_b64 + sig_padding)
        
        pubkey.verify(sig_bytes, message)
        
        payload_padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + payload_padding))
        return payload.get("sub") or payload.get("id")
    except Exception:
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> str:
    token = credentials.credentials
    # 1. Try local HS256 token
    try:
        payload = jwt.decode(token, settings.LOCAL_AUTH_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id:
            return user_id
    except JWTError:
        pass

    # 2. Try Neon Auth EdDSA JWKS token
    if getattr(settings, "NEON_AUTH_JWKS_URL", None):
        user_id = _verify_eddsa_token(token)
        if user_id:
            return user_id

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
