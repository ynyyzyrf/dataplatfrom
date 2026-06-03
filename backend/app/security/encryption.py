"""Credential encryption using Fernet symmetric encryption.

All API tokens, API keys, and other secrets are encrypted before
persisting to the database and decrypted on read.
"""

from __future__ import annotations

from cryptography.fernet import Fernet

from app.config import settings

_fernet = Fernet(settings.encryption_key_bytes)


def encrypt(plain_text: str) -> bytes:
    """Encrypt *plain_text* and return the Fernet token (bytes)."""
    return _fernet.encrypt(plain_text.encode("utf-8"))


def decrypt(token: bytes | str) -> str:
    """Decrypt a Fernet token and return the original plain text."""
    return _fernet.decrypt(token).decode("utf-8")
