from services.roleQuery import RoleQuery

role = RoleQuery()

def get_app_roles_info():
    app_roles = role.get_all_app_roles_by_status(status=0)
    return app_roles

def process_app_role(user_id, app_id, status):
    update_status, msg = role.update_app_roles(user_id, app_id, status)
    return update_status, msg