def verify_role_rbac(user_role, allowed_roles):
    # Role-Based Access Control
    return user_role in allowed_roles

def verify_policy_abac(user_attributes, resource_attributes):
    # Attribute-Based Access Control
    return user_attributes.get("department") == resource_attributes.get("owner_department")

def check_access(user_role, resource, action, user_attributes):
    if verify_role_rbac(user_role, ["admin"]):
        return True
    if action == "read" and verify_policy_abac(user_attributes, resource):
        return True
    return False
