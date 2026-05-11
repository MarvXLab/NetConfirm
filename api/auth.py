import os
import hashlib
import secrets
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Master key from environment — set NETCONFIRM_API_KEY on Render
# Falls back to a dev key if not set (dev only)
_MASTER_KEY = os.getenv("NETCONFIRM_API_KEY", "dev-key-change-in-production")

# In-memory key store — in production swap for DB-backed store
# Format: { hashed_key: {"name": str, "active": bool} }
_KEY_STORE: dict[str, dict] = {}


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key(name: str = "default") -> str:
    """Generate a new API key, store its hash, return the raw key."""
    raw = f"nc-{secrets.token_urlsafe(32)}"
    _KEY_STORE[_hash_key(raw)] = {"name": name, "active": True}
    return raw


def revoke_api_key(raw_key: str) -> bool:
    h = _hash_key(raw_key)
    if h in _KEY_STORE:
        _KEY_STORE[h]["active"] = False
        return True
    return False


def list_keys() -> list[dict]:
    return [{"hash_prefix": k[:8] + "...", **v} for k, v in _KEY_STORE.items()]


def _is_valid(raw_key: str) -> bool:
    # Master key always works
    if raw_key == _MASTER_KEY:
        return True
    h = _hash_key(raw_key)
    entry = _KEY_STORE.get(h)
    return entry is not None and entry["active"]


async def require_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """FastAPI dependency — raises 401 if key is missing or invalid."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Pass it in the X-API-Key header.",
        )
    if not _is_valid(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or revoked API key.",
        )
    return api_key
