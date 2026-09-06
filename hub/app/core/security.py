"""
Installation-credential helpers.

The plugin<->Hub credential (see PublisherInstallation) is a bearer token
issued by the Hub. Only its SHA-256 hash is ever persisted — the same
pattern used for API keys — so a database read alone can never yield a
usable credential.
"""
import hashlib
import secrets

TOKEN_PREFIX = "sfhub"


def generate_installation_token() -> str:
    """A new plaintext token to hand to an installer exactly once."""
    return f"{TOKEN_PREFIX}_{secrets.token_urlsafe(32)}"


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
