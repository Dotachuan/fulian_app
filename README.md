# 基金会捐款管理系统

前后端分离的捐款管理系统。

- 前端：Vue 3 + Vite + Element Plus + Pinia
- 后端：FastAPI + SQLAlchemy
- 数据库：MySQL 8

当前项目已完成本地环境打通、核心流程验收和页面级联调，可继续进入部署固化与自动化验收阶段。

## 目录结构

```text
frontend/        Vue 3 + Vite 前端
backend/         FastAPI 后端
SESSION_LOG.md   联调记录与阶段性结论
需求.txt
项目设计信息.txt
```

## 环境要求

- Node.js `24.14.0`
- npm `11.9.0`
- Python `3.11.6`
- MySQL `8.0`

注意事项：

- PowerShell 下请使用 `npm.cmd`
- 后端建议固定使用 Python 3.11
- 当前后端密码哈希方案为 `pbkdf2_sha256`

## 默认账号

- 用户名：`admin`
- 密码：`Admin@123`

## 后端配置

编辑 [backend/.env](/D:/website%20project/backend/.env)：

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的数据库密码
DB_NAME=foundation_donation

SECRET_KEY=请替换为随机密钥
ACCESS_TOKEN_EXPIRE_MINUTES=480
UPLOAD_DIR=./uploads
```

创建数据库：

```sql
CREATE DATABASE foundation_donation CHARACTER SET utf8mb4;
```

## 前端环境变量

开发环境文件：[frontend/.env.development](/D:/website%20project/frontend/.env.development)

```env
VITE_API_BASE=/api/v1
VITE_API_PROXY_TARGET=http://127.0.0.1:8000
VITE_DEV_HOST=127.0.0.1
VITE_DEV_PORT=5173
```

生产环境文件：[frontend/.env.production](/D:/website%20project/frontend/.env.production)

```env
VITE_API_BASE=/api/v1
```

说明：

- `VITE_API_BASE` 是前端请求基地址
- 开发环境通过 Vite 代理将 `/api` 转发到后端
- 生产环境默认假定由 Nginx 做同域反向代理，因此仍使用 `/api/v1`

## 本地启动

### 1. 启动后端

首次安装依赖：

```powershell
cd "D:\website project\backend"
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

启动服务：

```powershell
cd "D:\website project\backend"
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

访问：

- 健康检查：`http://127.0.0.1:8000/health`
- Swagger：`http://127.0.0.1:8000/docs`

### 2. 启动前端

```powershell
cd "D:\website project\frontend"
npm.cmd install
npm.cmd run dev -- --host 127.0.0.1
```

访问：

- 前端：`http://127.0.0.1:5173/`

## 生产构建

### 前端构建

```powershell
cd "D:\website project\frontend"
npm.cmd install
npm.cmd run build
```

构建产物目录：

- [frontend/dist](/D:/website%20project/frontend/dist)

### 后端启动

建议使用进程管理工具启动，例如 `systemd`、`supervisor` 或 Windows 服务。

示例：

```powershell
cd "D:\website project\backend"
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 自动化验收

当前已补充一份后端 smoke 验收脚本：

- [backend/scripts/smoke_acceptance.py](/D:/website%20project/backend/scripts/smoke_acceptance.py)

覆盖范围：

- 管理员登录
- 捐款人新增
- 捐款目标新增
- 捐款新增
- 捐款列表加载
- 捐款详情加载
- 操作日志加载
- 统计接口加载
- 导出接口可用性
- 测试数据自动清理

运行方式：

```powershell
cd "D:\website project\backend"
.venv\Scripts\python.exe scripts\smoke_acceptance.py
```

预期输出：

```text
Smoke acceptance passed.
```

## Nginx 反向代理示例

适用于前后端同域部署场景。

```nginx
server {
    listen 80;
    server_name your-domain.example.com;

    root /path/to/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 部署检查清单

- 数据库已创建，`backend/.env` 已配置
- 后端依赖已安装，服务可访问 `/health`
- 前端已执行 `npm.cmd run build`
- Nginx 已正确代理 `/api/` 和 `/uploads/`
- 默认管理员账号已验证可登录

## 当前状态

- 核心流程接口级验收已通过
- 页面级联调已通过
- 前端 API 地址已抽离至环境变量
- 部署说明已补齐

详细过程见 [SESSION_LOG.md](/D:/website%20project/SESSION_LOG.md)。
## 用户端前台自动化验收

新增用户端前台与配套后台能力验收脚本：
- [backend/scripts/portal_acceptance.py](/D:/website%20project/backend/scripts/portal_acceptance.py)

覆盖范围：
- 管理员登录
- 创建捐赠人、捐赠目标、捐赠记录
- 用户端公开捐赠查询
- 用户端历年捐赠统计
- 后台创建基金与基金收支明细
- 用户端基金使用查询
- 用户端开票申请提交
- 后台开票申请列表、处理、导出
- 测试数据自动清理

运行方式：
```powershell
cd "D:\website project\backend"
.venv\Scripts\python.exe scripts\portal_acceptance.py
```

预期输出：
```text
Portal acceptance passed.
```

## donate.xls 预导入转换

用于将当前目录下的 `donate.xls` 按“项目明细”转换为标准化 JSON：
- [backend/scripts/convert_donate_xls.py](/D:/website%20project/backend/scripts/convert_donate_xls.py)

转换规则：
- 读取 `2020年` 至 `2026年` 工作表。
- 每个“理事 + 年份 + 非零项目金额”转换为一条捐赠记录。
- 捐赠日期暂按年度占位日期生成：`YYYY-12-31`。
- `天凯法律` 统一为 `天凯法学`。
- `东台杯专项` 统一为 `东台杯素养赛`。
- 只生成 JSON，不写入数据库。

运行方式：
```powershell
cd "D:\website project\backend"
.venv\Scripts\python.exe scripts\convert_donate_xls.py
```

默认输出：
```text
D:\website project\backend\.tmp\donate.normalized.json
```

## 后台捐赠数据导入

后台管理端已提供“捐赠数据导入”页面：

```text
http://127.0.0.1:5173/imports/donations
```

使用流程：
- 登录后台管理端。
- 进入“捐赠数据导入”菜单。
- 上传 `donate.xls`。
- 点击“预分析”，检查捐赠人、项目、记录数、总金额、预警。
- 确认无误后点击“确认导入”。

后端接口：
- `POST /api/v1/imports/donations/preview`
- `POST /api/v1/imports/donations/commit`

第一版导入规则：
- 支持当前 `donate.xls` 年度项目明细格式。
- 默认将每个非零项目金额导入为一条捐赠记录。
- 导入时会按捐赠目标自动创建或匹配基金，并同步生成基金收入流水。
- 默认跳过重复记录。
- 暂不支持覆盖已有记录。

历史导入捐赠同步到基金收入：
- [backend/scripts/sync_imported_donations_to_funds.py](/D:/website%20project/backend/scripts/sync_imported_donations_to_funds.py)

运行方式：
```powershell
cd "D:\website project\backend"
.venv\Scripts\python.exe scripts\sync_imported_donations_to_funds.py
```
