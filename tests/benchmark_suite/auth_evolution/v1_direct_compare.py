"""Benchmark auth_evolution v1: Direct password comparison."""

def check_password(stored_password, provided_password):
    """Simple direct password comparison."""
    return stored_password == provided_password
