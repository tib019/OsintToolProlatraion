from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import settings


def get_fernet() -> Fernet:
    """Derive a Fernet key from APP_SECRET_KEY using SHA-256."""
    raw = hashlib.sha256(settings.APP_SECRET_KEY.encode()).digest()
    key = base64.urlsafe_b64encode(raw)
    return Fernet(key)


def encrypt(value: str) -> str:
    """Encrypt a plaintext string and return the ciphertext as a string."""
    return get_fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    """Decrypt a ciphertext string and return the plaintext."""
    return get_fernet().decrypt(value.encode()).decode()
