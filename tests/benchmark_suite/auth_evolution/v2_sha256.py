"""Benchmark auth_evolution v2: SHA-256 password hashing and comparison."""

import hashlib

def check_password(stored_hash, provided_password):
    """SHA-256 password hashing comparison."""
    provided_hash = hashlib.sha256(provided_password.encode('utf-8')).hexdigest()
    return stored_hash == provided_hash
