from services.favouriteQuery import FavouriteQuery
from services.loggerQuery import VisitLoggerQuery
from services.appQuery import AppQuery
from services.versionQuery import AppVersionQuery

app = AppQuery()
favourite = FavouriteQuery()
visitLogger = VisitLoggerQuery()
app_version = AppVersionQuery()

def get_apps_count():
    app_count = app.get_app_count()
    return app_count

def get_user_favourite(user_id: str):
    """获取用户收藏app列表"""
    app_data = favourite.get_user_favourites(user_id)
    return app_data

def get_user_frequent(user_id: str):
    """获取用户常用列表"""
    app_data = visitLogger.get_user_visit_count(user_id)
    return app_data

def get_app_description():
    app_create_list = app.get_all_apps()
    create_list = [
        {
            'app_name': item['app_name'],
            'description': item['short_description'],
            'created_at': item['created_at'],
            'display_type': 'new'
        }
        for item in app_create_list
        if item['is_deleted'] == 0 and item['is_published'] == "是"
    ]

    app_update_list, msg = app_version.get_all_app_version()
    update_list = [
        {
            'app_name': item['app_name'],
            'description': item['description'],
            'created_at': item['created_at'],
            'display_type': 'update'
        }
        for item in app_update_list
        if item['is_deleted'] == 0 and item['is_published'] == "是"
    ]

    return create_list + update_list



