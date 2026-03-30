from models import AppRole, Role, RoleMapping

from .base import SessionLocal


class RoleQuery:
    def get_roles(self) -> list:
        with SessionLocal() as session:
            all_roles = session.query(Role).all()
            return [{"role_id": role.role_id, "role_name": role.role_name} for role in all_roles]

    def create_roles_mapping(self, role_id: str, navigation: str):
        with SessionLocal() as session:
            roles_mapping = RoleMapping(role_id=role_id, navigation=navigation)
            session.add(roles_mapping)
            session.commit()
            return roles_mapping, "权限关联表创建成功"

    def create_app_roles(self, user_id: str, app_id: str, reason: str, status: int):
        with SessionLocal() as session:
            app_role = AppRole(userId=user_id, app_id=app_id, reason=reason, status=status)
            merged = session.merge(app_role)
            session.commit()
            is_new = merged is app_role
            message = "用户权限新增成功" if is_new else "用户权限更新成功"
            return app_role, message

    def get_all_app_roles_by_user(self, user_id: str) -> list:
        with SessionLocal() as session:
            all_app_roles = session.query(AppRole).filter(AppRole.userId == user_id).all()
            return [
                {
                    "user_id": role.userId,
                    "app_id": role.app_id,
                    "reason": role.reason,
                    "status": role.status,
                }
                for role in all_app_roles
            ]

    def get_all_app_roles_by_status(self, status: int) -> list:
        with SessionLocal() as session:
            all_app_roles = session.query(AppRole).filter(AppRole.status == status).all()
            return [
                {
                    "user_id": role.userId,
                    "user_name": role.user.real_name,
                    "app_id": role.app_id,
                    "app_name": role.app.app_name if role.app else "已删除的应用",
                    "reason": role.reason,
                    "status": role.status,
                    "created_at": role.created_at,
                    "updated_at": role.updated_at,
                }
                for role in all_app_roles
            ]

    def update_app_roles(self, user_id: str, app_id: str, status: int):
        with SessionLocal() as session:
            app_role = session.query(AppRole).filter(
                AppRole.userId == user_id,
                AppRole.app_id == app_id,
            ).first()

            if not app_role:
                return False, "未找到对应的应用权限记录"

            app_role.status = status
            session.commit()
            session.refresh(app_role)
            return True, "权限状态更新成功"
