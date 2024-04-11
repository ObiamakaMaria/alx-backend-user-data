#!/usr/bin/env python3
"""Password encryption utilities"""

import bcrypt


def hash_password(password: str) -> bytes:
    """Hashes a password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed


def is_valid(hashed_password: bytes, password: str) -> bool:
    '''Checks if a hashed password matches a given password'''
    if bcrypt.checkpw(password.encode(), hashed_password):
        return True
    return False
