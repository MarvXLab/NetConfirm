import os
import hashlib
import secrets
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

_MASTER_KEY = os.getenv("NETCONFIRM_API_KEY", "dev-key-change-in-production")


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def make_api_key() -> tuple[str, str, str]:
    """
    Generate a new raw API key.
    Returns (raw_key, key_hash, key_prefix)
    """
    raw    = f"nc-{secrets.token_urlsafe(32)}"
    hashed = _hash_key(raw)
    prefix = raw[:12]
    return raw, hashed, prefix


def _is_valid(raw_key: str) -> bool:
    # Master key always works
    if raw_key == _MASTER_KEY:
        return True
    # Check DB
    try:
        from db.queries import validate_api_key_db
        return validate_api_key_db(_hash_key(raw_key))
    except Exception:
        return False


async def require_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Get a free key at the NetConfirm app → ⚡ API tab.",
        )
    if not _is_valid(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or revoked API key.",
        )
    return api_key
