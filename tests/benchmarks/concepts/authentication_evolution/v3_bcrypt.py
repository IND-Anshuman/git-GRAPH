import bcrypt

def check_password(input_password, stored_hash):
    # Verification via bcrypt secure hashing
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_hash.encode('utf-8'))
