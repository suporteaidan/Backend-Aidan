"""
Password security utilities.

This module is responsible for handling password hashing and verification.
It centralizes all password-related logic, ensuring consistent and secure
password management across the application.
"""

from passlib.context import CryptContext

# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """
    Hash a plaintext password.

    Args:
        password (str): The plaintext password to hash.

    Returns:
        str: The hashed password.
    """
    if not isinstance(password, str):
        raise TypeError("password must be a string")

    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    Args:
        plain_password (str): The plaintext password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)