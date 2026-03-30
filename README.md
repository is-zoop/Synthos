# Synthos

Synthos 是一个基于 `PyQt5`、`qfluentwidgets` 与 `SQLAlchemy` 构建的 Windows 桌面应用平台，用于统一管理内部应用目录、用户权限、资源更新、插件分发和常用工作入口。

## 核心功能

- 登录与鉴权：支持记住密码、本地凭据加密存储、按角色动态生成导航。
- 首页工作台：展示应用统计、收藏入口和更新/审批相关信息。
- 应用目录：按目录分类浏览应用，支持打开、收藏、反馈、卸载与权限申请。
- 应用管理：支持目录管理、应用管理、版本发布和插件文件上传。
- 用户管理：支持新增、编辑、删除、搜索用户以及应用权限审批。
- 个人设置：支持头像上传、密码修改、Cookie 登录信息管理与本地目录打开。
- 资源与版本更新：启动时比对资源清单，支持增量同步与客户端版本检测。
- 插件机制：按统一接口动态加载插件，并在 Tab 中运行。

## 本次重构内容

- 新增 `core/` 公共层，统一常量、路径、自检和初始化逻辑。
- 新增 `ui/information/` 与 `ui/UserManage/user_funcs.py` 规范命名入口，同时保留旧路径兼容。
- 修复 example 插件首启未自动落地、本地版本表为空时更新检查崩溃、插件名称接口调用不一致等问题。
- 新增项目初始化脚本，可一键创建数据库表、默认管理员、基础角色/导航映射和 example 插件数据。
- 补充 `tests/` 中的基础 smoke tests。

## 目录结构

详细目录说明见 [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)。

```text
Synthos/
├─ core/                 # 公共常量、路径、自检、初始化逻辑
├─ models/               # SQLAlchemy 模型
├─ services/             # 查询与业务服务
├─ ui/                   # 桌面界面
├─ utils/                # 下载、插件、样式、更新工具
├─ api/                  # FastAPI 服务端
├─ scripts/              # 初始化与辅助脚本
├─ tests/                # 最小测试与 smoke check
├─ example/              # 仓库内置 example 插件
├─ main.py
└─ settings.py
```

## 环境要求

- Python 3.11 推荐
- MySQL
- Windows 客户端环境

常用依赖示例：

```bash
pip install PyQt5 PyQt-Fluent-Widgets qframelesswindow SQLAlchemy PyMySQL requests pywin32 pytest
```

API 依赖可直接使用 [requirements.txt]。

## 配置说明

客户端默认从 `settings.py` 读取配置，支持通过环境变量覆盖：

```bash
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=3306
DB_NAME=your_db
DATABASE_URL=mysql+pymysql://user:password@host:3306/dbname
ENVIRONMENT=development
SERVER_URL=https://your-api-host/
API_KEY=your-api-key
```

客户端运行时数据默认存放在：

- `%LOCALAPPDATA%/Synthos`
- 插件目录：`%LOCALAPPDATA%/Synthos/plugins`
- 资源目录：`%LOCALAPPDATA%/Synthos/resource`

## 一键初始化

### 作用

初始化脚本会执行以下动作：

1. 创建数据库表。
2. 创建默认管理员账号。
3. 创建基础角色与导航映射。
4. 创建 example 目录、示例应用和版本数据。
5. 将仓库内 `example/` 插件复制到客户端默认插件目录。
6. 将 example 插件同步到本地 API 默认数据目录，便于直接运行 `api/`。

### 默认管理员

- 用户名：`admin`
- 密码：`123456`

可通过环境变量覆盖：

```bash
SYNTHOS_ADMIN_USERNAME=admin
SYNTHOS_ADMIN_PASSWORD=123456
SYNTHOS_ADMIN_USER_ID=00000000
SYNTHOS_ADMIN_REAL_NAME=系统管理员
```

### 运行方式

优先推荐 Windows 一键脚本：

```bat
init_project.bat
```

如果本机已正确配置 Python，也可以直接运行：

```bash
python initialize_project.py
```

如果当前环境没有把 `python` 或 `py` 加入 PATH，请直接双击 `init_project.bat`，它会优先尝试自动查找解释器。

### 初始化后验证

初始化成功后可验证：

- 数据库已创建 `users`、`roles`、`roles_mapping`、`apps`、`directories` 等表。
- 默认管理员 `admin` 可登录。
- 管理员可看到 `目录`、`用户`、`应用`、`信息` 页面。
- example 插件目录已出现在 `%LOCALAPPDATA%/Synthos/plugins/<app_id>`。
- example 应用在目录页可见且可打开。

## 客户端启动

```bash
python main.py
```

应用启动时会自动执行一次轻量自检：

- 如果本地默认插件目录缺少 example 插件，会自动从仓库内 `example/` 补齐。
- 不会覆盖用户已有同名插件目录中的文件。

## API Docker 部署

`api/` 目录中已经包含：

- [Dockerfile](/E:/Synthos%202.0/api/Dockerfile)
- [docker-compose.yml](/E:/Synthos%202.0/api/docker-compose.yml)
- [.env.example](/E:/Synthos%202.0/api/.env.example)
- [docker_run](/E:/Synthos%202.0/api/docker_run)

### 方式一：Docker 命令

进入 `api/` 目录后执行：

```bash
docker build -t synthos-api:latest .
docker run -d -p 8000:8000 \
  -v ./app/app_data:/app/app_data \
  -e APP_DATA_DIR=/app/app_data \
  -e API_KEY=replace-me-with-your-own-api-key \
  --name synthos-api \
  synthos-api:latest
```

说明：

- `APP_DATA_DIR`：API 运行时数据目录，包含插件、资源和头像。
- `API_KEY`：客户端与 API 通信时使用的请求头密钥（请在 `.env` 或环境变量中自行设置，不要使用仓库默认值）。
- `./app/app_data:/app/app_data`：数据卷挂载，保证容器重建后插件、资源和头像仍然保留。

### 方式二：Docker Compose

进入 `api/` 目录后：

1. 复制环境变量模板

```bash
cp .env.example .env
```

Windows PowerShell 可使用：

```powershell
Copy-Item .env.example .env
```

2. 编辑 `.env`，至少设置：

```env
APP_DATA_DIR=/app/app_data
API_KEY=replace-me-with-your-own-api-key
```

3. 启动服务

```bash
docker compose up -d --build
```

Compose 默认会：

- 构建当前 `api/` 镜像
- 暴露 `8000` 端口
- 挂载 `./app/app_data` 到容器内 `/app/app_data`
- 读取 `.env` 中的 `APP_DATA_DIR` 和 `API_KEY`

### API 目录持久化说明

容器内会使用以下目录：

- `/app/app_data/plugin`：插件文件
- `/app/app_data/resource`：资源压缩包与资源索引
- `/app/app_data/avatar`：用户头像

这些都通过宿主机 `api/app/app_data` 持久化。

## 打包说明

项目根目录已保留打包脚本：

- 主程序：`nuitka_to_exe.py`
- 更新替换工具：`nuitka_to_exe_updater.py`

## 测试与 smoke check

新增了最小测试集合：

- [tests/test_paths.py](/E:/Synthos%202.0/tests/test_paths.py)
- [smoke_check.py](/E:/Synthos%202.0/smoke_check.py)

推荐在具备 Python 环境后执行：

```bash
pytest tests
```

或者执行更轻量的模块导入检查：

```bash
python smoke_check.py
```

## 相关文件

- [README.md](./README.md)
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)
- [initialize_project.py](/E:/Synthos%202.0/initialize_project.py)
- [init_project.bat](/E:/Synthos%202.0/init_project.bat)
