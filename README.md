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
├─ example/              # 仓库内置 example 插件
├─ main.py
└─ settings.py
```

## 环境要求

- Python 3.11 推荐
- MySQL
- Windows 客户端环境

使用命令行安装依赖：

```bash
pip install -r requirements.txt
```

## 快速开始
### API部署

`api/` 目录中包含：

- [Dockerfile](/E:/Synthos%202.0/api/Dockerfile)
- [docker-compose.yml](/E:/Synthos%202.0/api/docker-compose.yml)
- [.env.example](/E:/Synthos%202.0/api/.env.example)

1. 进入 `api` 目录并创建 `.env`

```bash
cd api
cp .env.example .env
```

如果是 Windows PowerShell:

```powershell
cd api
Copy-Item .env.example .env
```

2. 命令行生成 `API_KEY`

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. 打开 `api/.env`，把上一步输出填到 `API_KEY=...`

建议同时确认：

```env
APP_DATA_DIR=/app/app_data
API_KEY=your-generated-key
```

4. 启动 API（Docker Compose）

```bash
docker compose up -d --build
docker compose ps
```

查看实时日志：

```bash
docker compose logs -f
```

容器数据持久化目录：

- `/app/app_data/plugin`：插件文件
- `/app/app_data/resource`：资源压缩包与资源索引
- `/app/app_data/avatar`：用户头像
- 对应宿主机目录：`api/app/app_data`

### 初始化配置

运行初始化命令后，会执行以下内容：

1. 创建数据库表。
2. 创建默认管理员账号。
3. 创建基础角色与导航映射。
4. 创建 `example` 目录、示例应用和版本数据。
5. 将仓库内 `example/plugins` 插件复制到客户端默认插件目录。
6. 将 example 插件同步到本地 API 默认数据目录，便于直接运行 `api/`。
7. 将 `example/update_launcher.exe` 复制到 `app_data` 目录。

启动客户端前，请先配置 [settings.py](/Synthos/settings.py)（重点：数据库连接、`SERVER_URL`、`API_KEY`）。

#### 配置说明

初始化默认从 `settings.py` 读取配置：

```bash
DB_USER=your_user  ## 数据库用户名
DB_PASSWORD=your_password ## 数据库密码
DB_HOST=your_host  ## 数据库连接
DB_PORT=3306       ## 数据库端口
DB_NAME=your_db    ## 数据库名称 
SERVER_URL=https://your-api-host/  ## api连接（如http://127.0.0.1:8000/）
API_KEY=your-api-key ## api部署时使用的api_key
```

### 默认管理员

- 用户名：`admin`
- 密码：`123456`

初始化设置：

```bash
python scripts/initialize_project.py
```

### 启动 Synthos 客户端

客户端运行时数据默认存放在：

- `%LOCALAPPDATA%/Synthos`
- 插件目录：`%LOCALAPPDATA%/Synthos/plugins`
- 资源目录：`%LOCALAPPDATA%/Synthos/resource`
  - lib: 存放插件必需的官方包
  - dependencies: 存放插件运行所必须依赖的第三方库或外部组件
  - packages: 其他功能模块

启动客户端：

```bash
python main.py
```

## 打包说明

项目根目录已保留打包脚本：

- 主程序：`nuitka_to_exe.py`
- 更新替换工具：`nuitka_to_exe_updater.py`

## 插件示例
- 见`example\plugins_template`示例插件；
- `main.py`作为插件入口，函数名称和参数必须保持一致；

## 相关文件

- [README.md](./README.md)
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)
- [initialize_project.py](/E:/Synthos%202.0/initialize_project.py)
- [init_project.bat](/E:/Synthos%202.0/init_project.bat)
