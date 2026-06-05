"""Benchmark auth_evolution v3: Bcrypt cryptographic hash verification."""

import bcrypt

def check_password(stored_hash, provided_password):
    """Bcrypt password verification."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))
