from __future__ import annotations

import os
from dataclasses import dataclass, field

from models import AppVersion, Apps, Directories, Role, RoleMapping, User, Version
from models.base import Base
from services.base import SessionLocal, engine
from services.userQuery import UserQuery
from services.versionQuery import version_to_int

from core.constants import (
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_REAL_NAME,
    DEFAULT_ADMIN_USER_ID,
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ROLE_MAPPINGS,
    EXAMPLE_APP_VERSION_DESCRIPTION,
    EXAMPLE_DIRECTORY_DESCRIPTION,
    EXAMPLE_DIRECTORY_NAME,
    ROLE_SUPER_ADMIN,
)
from core.paths import (
    ensure_default_runtime_files,
    ensure_example_plugin_installed,
    ensure_example_plugin_storage,
    ensure_update_launcher_in_api_app_data,
    read_example_manifest,
)


@dataclass
class BootstrapResult:
    created_tables: bool = False
    created_roles: list[str] = field(default_factory=list)
    created_role_mappings: list[str] = field(default_factory=list)
    created_users: list[str] = field(default_factory=list)
    created_directories: list[str] = field(default_factory=list)
    created_apps: list[str] = field(default_factory=list)
    created_versions: list[str] = field(default_factory=list)
    plugin_targets: list[str] = field(default_factory=list)


def create_all_tables() -> None:
    Base.metadata.create_all(engine)


def ensure_default_roles(session, result: BootstrapResult) -> dict[str, Role]:
    role_map: dict[str, Role] = {}
    for role_name, navigations in DEFAULT_ROLE_MAPPINGS.items():
        role = session.query(Role).filter(Role.role_name == role_name).first()
        if role is None:
            role = Role(role_name=role_name)
            session.add(role)
            session.flush()
            result.created_roles.append(role_name)
        role_map[role_name] = role

        for navigation in navigations:
            mapping = session.query(RoleMapping).filter(
                RoleMapping.role_id == role.role_id,
                RoleMapping.navigation == navigation,
            ).first()
            if mapping is None:
                session.add(RoleMapping(role_id=role.role_id, navigation=navigation))
                result.created_role_mappings.append(f"{role_name}:{navigation}")
    return role_map


def ensure_default_admin(session, role_map: dict[str, Role], result: BootstrapResult) -> User:
    admin_username = os.getenv("SYNTHOS_ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME)
    admin_password = os.getenv("SYNTHOS_ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
    admin_user_id = os.getenv("SYNTHOS_ADMIN_USER_ID", DEFAULT_ADMIN_USER_ID)
    admin_real_name = os.getenv("SYNTHOS_ADMIN_REAL_NAME", DEFAULT_ADMIN_REAL_NAME)

    admin = session.query(User).filter(User.username == admin_username).first()
    if admin is None:
        salt, password_hash = UserQuery().create_hash(admin_password)
        admin = User(
            userId=admin_user_id,
            username=admin_username,
            real_name=admin_real_name,
            password_hash=password_hash,
            salt=salt,
            enable=1,
            role_id=role_map[ROLE_SUPER_ADMIN].role_id,
        )
        session.add(admin)
        result.created_users.append(admin_username)
    else:
        admin.real_name = admin_real_name
        admin.enable = 1
        admin.role_id = role_map[ROLE_SUPER_ADMIN].role_id
    return admin


def ensure_example_app(session, result: BootstrapResult) -> None:
    manifest = read_example_manifest()

    directory = session.query(Directories).filter(
        Directories.directory_name == EXAMPLE_DIRECTORY_NAME
    ).first()
    if directory is None:
        directory = Directories(
            directory_name=EXAMPLE_DIRECTORY_NAME,
            description=EXAMPLE_DIRECTORY_DESCRIPTION,
            sort_order=10,
            is_deleted=0,
        )
        session.add(directory)
        session.flush()
        result.created_directories.append(EXAMPLE_DIRECTORY_NAME)

    app = session.query(Apps).filter(Apps.app_id == manifest["app_id"]).first()
    if app is None:
        app = Apps(
            app_id=manifest["app_id"],
            app_name=manifest["app_name"],
            owner=manifest["owner"],
            icon=manifest.get("icon", "icon"),
            version=manifest["version"],
            short_description=manifest["description"][:200],
            description=manifest["description"],
            directory_id=directory.id,
            tutorial="example",
            is_published=1,
            is_deleted=0,
        )
        session.add(app)
        result.created_apps.append(manifest["app_name"])
    else:
        app.app_name = manifest["app_name"]
        app.owner = manifest["owner"]
        app.icon = manifest.get("icon", "icon")
        app.version = manifest["version"]
        app.short_description = manifest["description"][:200]
        app.description = manifest["description"]
        app.directory_id = directory.id
        app.tutorial = app.tutorial or "example"
        app.is_published = 1
        app.is_deleted = 0

    app_version = session.query(AppVersion).filter(
        AppVersion.app_id == manifest["app_id"],
        AppVersion.version == manifest["version"],
    ).first()
    if app_version is None:
        session.add(
            AppVersion(
                app_id=manifest["app_id"],
                version=manifest["version"],
                version_int=version_to_int(manifest["version"]),
                description=EXAMPLE_APP_VERSION_DESCRIPTION,
            )
        )
        result.created_versions.append(f"{manifest['app_name']}:{manifest['version']}")


def ensure_default_client_version(session, result: BootstrapResult) -> None:
    """Keep update checks available by ensuring one latest client version exists."""
    import settings

    session.query(Version).update({Version.is_latest: False})
    exists = session.query(Version).filter(Version.version == settings.VERSION).first()
    if exists is None:
        session.add(
            Version(
                version=settings.VERSION,
                version_int=version_to_int(settings.VERSION),
                description="Bootstrap seeded default client version.",
                download_url=f"{settings.SERVER_URL}download/exe/{settings.APP_NAME}.zip",
                is_latest=True,
            )
        )
        result.created_versions.append(f"client:{settings.VERSION}")
    else:
        exists.version_int = version_to_int(settings.VERSION)
        exists.download_url = f"{settings.SERVER_URL}download/exe/{settings.APP_NAME}.zip"
        exists.is_latest = True


def bootstrap_project() -> BootstrapResult:
    """Create tables and seed default records in an idempotent way."""
    result = BootstrapResult(created_tables=True)
    create_all_tables()

    with SessionLocal() as session:
        role_map = ensure_default_roles(session, result)
        ensure_default_admin(session, role_map, result)
        ensure_example_app(session, result)
        ensure_default_client_version(session, result)
        session.commit()

    example_app_id, local_target = ensure_example_plugin_installed(overwrite=False)
    _, api_target = ensure_example_plugin_storage(overwrite=False)
    result.plugin_targets.extend([f"{example_app_id}:{local_target}", f"{example_app_id}:{api_target}"])

    update_launcher_target = ensure_update_launcher_in_api_app_data(overwrite=False)
    if update_launcher_target is not None:
        result.plugin_targets.append(f"update_launcher:{update_launcher_target}")

    generated = ensure_default_runtime_files()
    result.plugin_targets.extend([f"default_avatar:{path}" for path in generated["avatars"]])
    result.plugin_targets.extend([f"resource_json:{path}" for path in generated["resources"]])
    return result
