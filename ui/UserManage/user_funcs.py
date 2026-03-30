from services.userQuery import UserQuery


user_query = UserQuery()


def load_users():
    all_users = user_query.get_users()
    items_per_page = 20
    total_pages = max(1, (len(all_users) + items_per_page - 1) // items_per_page)
    return all_users, total_pages


def create_user_task(dialog):
    user_id = dialog.UserIDEdit.text().strip()
    username = dialog.UserNameEdit.text().strip()
    real_name = dialog.RealNameEdit.text().strip()
    password = dialog.PassWordEdit.text().strip()
    role_id = next(
        (
            role["role_id"]
            for role in dialog.role_data
            if role["role_name"] == dialog.RoleComboBox.text().strip()
        ),
        None,
    )
    return user_query.create_user(username, real_name, user_id, password, role_id)


def update_user_task(uid, dialog):
    user_id = dialog.UserIDEdit.text().strip()
    real_name = dialog.RealNameEdit.text().strip()
    role_id = next(
        (
            role["role_id"]
            for role in dialog.role_data
            if role["role_name"] == dialog.RoleComboBox.text().strip()
        ),
        None,
    )
    enable_id = next(
        (
            enable["id"]
            for enable in dialog.enable_data
            if enable["text"] == dialog.EnablBox.text().strip()
        ),
        None,
    )
    if uid == user_id:
        user_query.update_user(user_id=user_id, real_name=real_name, role_id=role_id, enable=enable_id)


def delete_user_task(uid):
    user_query.delete_user(user_id=uid)


def reset_user_password(uid, new_password):
    user_query.update_user(user_id=uid, password=new_password)


def search_users(keyword):
    """根据关键字模糊搜索用户。"""
    all_users, _ = load_users()
    keyword = keyword.lower()
    return [
        user
        for user in all_users
        if keyword in str(user["userId"]).lower()
        or keyword in user["username"].lower()
        or keyword in user.get("real_name", "").lower()
    ]

