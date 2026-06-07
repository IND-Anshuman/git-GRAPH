def check_access(user_role, resource, action, user_attributes):
    # Monolithic Access Control Check
    if user_role == "admin":
        return True
    if action == "read" and user_attributes.get("department") == resource.get("owner_department"):
        return True
    return False
