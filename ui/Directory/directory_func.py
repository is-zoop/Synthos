import os
import shutil

from core.paths import get_installed_plugin_dir
from services.appQuery import AppQuery
from services.directoryQuery import DirectoryQuery
from services.favouriteQuery import FavouriteQuery
from services.roleQuery import RoleQuery
from services.versionQuery import AppVersionQuery
from ui.GeneralWidgets.general_widget import info_bar


app_query = AppQuery()
directory = DirectoryQuery()
app_version = AppVersionQuery()
favourite = FavouriteQuery()
app_roles = RoleQuery()


def get_all_directories():
    return directory.get_all_directories()


def get_app_list(directory_id):
    return app_query.get_all_apps(directory_id=directory_id)


def get_all_apps():
    return app_query.get_all_apps()


def get_app_version(app_id):
    version, _ = app_version.get_app_version(app_id=app_id)
    return version


def get_recent_app_version(app_id, version):
    query_version = get_app_version(app_id)
    version_msg = "版本更新"
    for app in query_version:
        if app.version == version:
            version_msg = app.description
    return version_msg


def get_app_icon(app_id):
    image_types = ["png", "jpg", "jpeg", "icon"]
    plugin_dir = get_installed_plugin_dir(app_id)
    for image_type in image_types:
        path = plugin_dir / f"icon.{image_type}"
        if path.exists():
            return str(path)
    return ":/res/images/app_icon.png"


def uninstall_app(app_id, parent):
    plugins_path = get_installed_plugin_dir(app_id)
    try:
        if plugins_path.exists():
            shutil.rmtree(plugins_path)
            info_bar("", "应用卸载成功.", info_type="success", parent=parent)
    except PermissionError:
        info_bar("插件已加载,无法删除", "请在重启后再操作卸载插件.", info_type="error", parent=parent)


def favourite_func(user_id, app_id, operate_type):
    """用户收藏操作。"""
    if operate_type == "add":
        return favourite.create_favourite(user_id=user_id, app_id=app_id)
    if operate_type == "cancel":
        return favourite.cancel_favourite(user_id=user_id, app_id=app_id)
    return None


def submit_app_role_apply(user_id, app_id, reason, status=0):
    """用户申请 app 权限。"""
    return app_roles.create_app_roles(user_id, app_id, reason, status)


def get_all_app_roles(user_id):
    """获取用户当前 app 的所有权限状态。"""
    all_roles = app_roles.get_all_app_roles_by_user(user_id)
    user_app_roles = {}
    for role in all_roles:
        user_app_roles[role["app_id"]] = role["status"]
    return user_app_roles
