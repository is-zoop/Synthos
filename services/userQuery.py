import hashlib
import os

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, subqueryload

from models import User

from .base import SessionLocal
from .common import apply_model_updates, status_to_text


class UserQuery:
    def create_hash(self, password: str):
        salt = os.urandom(16).hex()
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000,
        ).hex()
        return salt, password_hash

    def create_user(self, username: str, real_name: str, user_id: str, password: str, role_id: int) -> tuple[User | None, str]:
        with SessionLocal() as session:
            try:
                salt, password_hash = self.create_hash(password)
                user = User(
                    userId=user_id,
                    username=username,
                    real_name=real_name,
                    password_hash=password_hash,
                    salt=salt,
                    enable=1,
                    role_id=role_id,
                )
                session.add(user)
                session.commit()
                return user, "用户创建成功"
            except IntegrityError as exc:
                session.rollback()
                if "duplicate" in str(exc.orig).lower() or "userid" in str(exc.orig).lower():
                    return None, "用户已存在"
                return None, "用户创建失败"
            except Exception:
                session.rollback()
                return None, "用户创建失败"

    def delete_user(self, user_id: str) -> bool:
        with SessionLocal() as session:
            user = session.query(User).filter_by(userId=user_id).first()
            if not user:
                return False
            try:
                session.delete(user)
                session.commit()
                return True
            except Exception as exc:
                session.rollback()
                print(f"删除用户失败: {exc}")
                raise

    def update_user(self, user_id: str, **kwargs) -> bool:
        with SessionLocal() as session:
            user = session.query(User).filter_by(userId=user_id).first()
            if not user:
                return False

            if "password" in kwargs:
                salt, password_hash = self.create_hash(kwargs.pop("password"))
                user.password_hash = password_hash
                user.salt = salt

            apply_model_updates(user, **kwargs)
            session.commit()
            return True

    def process_user_data(self, users):
        processed = []
        for user in users:
            processed.append(
                {
                    "userId": user["userId"],
                    "username": user["username"],
                    "real_name": user["real_name"],
                    "enable": status_to_text(user["enable"]),
                    "role_name": user["role_name"],
                    "created_at": user["created_at"].strftime("%Y-%m-%d"),
                }
            )
        return processed

    def get_users(self, user_id: str = None) -> list | dict | None:
        with SessionLocal() as session:
            query = session.query(User).join(User.role)
            if user_id:
                user = query.filter(User.userId == user_id).first()
                if not user:
                    return None
                user_info = [
                    {
                        "id": user.id,
                        "userId": user.userId,
                        "username": user.username,
                        "real_name": user.real_name,
                        "enable": user.enable,
                        "role_id": user.role_id,
                        "role_name": user.role.role_name,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at,
                    }
                ]
            else:
                all_users = query.all()
                user_info = [
                    {
                        "id": user.id,
                        "userId": user.userId,
                        "username": user.username,
                        "real_name": user.real_name,
                        "enable": user.enable,
                        "role_id": user.role_id,
                        "role_name": user.role.role_name,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at,
                    }
                    for user in all_users
                ]
            return self.process_user_data(user_info)

    def verify_user(self, username: str, password: str) -> tuple[dict | None, bool]:
        with SessionLocal() as session:
            user = session.query(User).options(
                joinedload(User.role),
                subqueryload(User.favourite),
            ).filter_by(username=username).first()

            if not user:
                return None, False

            input_password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode(),
                user.salt.encode(),
                100000,
            ).hex()

            if input_password_hash != user.password_hash:
                return None, False

            user_data = {
                "userId": str(user.userId),
                "username": user.username,
                "real_name": user.real_name,
                "role_id": user.role_id,
                "role_name": user.role.role_name,
                "roles_mapping": user.role.roles_mapping,
                "favourite_app_ids": [fav.app_id for fav in user.favourite] if user.favourite else [],
            }
            return user_data, True
