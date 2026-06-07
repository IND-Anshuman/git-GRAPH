import hashlib

def check_password(input_password, stored_hash):
    # Verification via one-way cryptographic hash SHA256
    hash_obj = hashlib.sha256(input_password.encode('utf-8'))
    return hash_obj.hexdigest() == stored_hash
