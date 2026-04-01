from services.roleQuery import RoleQuery

role = RoleQuery()


def get_app_roles_info():
    return role.get_all_app_roles_by_status(status=0)


def process_app_role(user_id, app_id, status):
    return role.update_app_roles(user_id, app_id, status)
