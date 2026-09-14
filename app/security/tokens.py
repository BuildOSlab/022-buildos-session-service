"""Security primitives for generating and hashing session tokens."""


# Standard library imports
import hashlib
import secrets


# Token generation
def generate_token() -> str:
    """Generate a cryptographically secure opaque token."""
    return secrets.token_urlsafe(32)


# Token hashing
def hash_token(token: str) -> str:
    """Return the SHA-256 hexadecimal digest of a token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
