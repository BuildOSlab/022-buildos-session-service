"""Tests for session token security primitives."""

# Standard library imports
import re

# Application imports
from app.security.tokens import generate_token, hash_token


# Token generation tests
def test_generate_token_returns_non_empty_string() -> None:
    """A generated token should be a non-empty string."""
    token = generate_token()

    assert isinstance(token, str)
    assert token


def test_generate_token_returns_different_tokens() -> None:
    """Two generated tokens should not be identical."""
    token_one = generate_token()
    token_two = generate_token()

    assert token_one != token_two


def test_generate_token_has_expected_url_safe_format() -> None:
    """A generated token should contain only URL-safe characters."""
    token = generate_token()

    assert re.fullmatch(r"[A-Za-z0-9_-]+", token)


# Token hashing tests
def test_hash_token_returns_sha256_hex_digest() -> None:
    """A SHA-256 hash should contain exactly 64 hexadecimal characters."""
    token = generate_token()
    hashed_token = hash_token(token)

    assert len(hashed_token) == 64
    assert re.fullmatch(r"[0-9a-f]{64}", hashed_token)


def test_hash_token_is_deterministic() -> None:
    """The same token should always produce the same hash."""
    token = generate_token()

    first_hash = hash_token(token)
    second_hash = hash_token(token)

    assert first_hash == second_hash
