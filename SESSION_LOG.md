# 会话记录 - 基金会捐款管理系统

## 项目信息
- 项目名称：基金会捐款管理系统
- 技术栈：Vue 3 + Vite + Element Plus + Pinia（前端） / FastAPI + SQLAlchemy + MySQL 8（后端）
- 工作目录：`D:\website project`
- 当前状态：前后端基础框架已完成，本地环境已打通，核心流程已完成一轮接口级验收

---

## 已完成内容

### 初始框架
- 已提供前端基础框架：登录页、布局、路由、Pinia 状态管理、权限控制、各业务页面骨架
- 已提供后端基础框架：FastAPI 入口、SQLAlchemy 模型、CRUD、认证、统计、导出等 API 模块

### 已完成的环境与联调工作
- 已确认前端可通过 `npm.cmd run dev` 启动
- 已补充前端缺失静态资源：`frontend/public/favicon.svg`
- 已确认前端生产构建通过：`npm.cmd run build`
- 已确认后端使用 `Python 3.11.6` 可正常运行
- 已创建后端虚拟环境：`backend/.venv`
- 已安装后端依赖：`backend/requirements.txt`
- 已确认 MySQL 8 服务可用，端口 `3306` 正常
- 已创建数据库：`foundation_donation`
- 已确认后端健康检查可访问：`http://127.0.0.1:8000/health`
- 已确认 Swagger 文档可访问：`http://127.0.0.1:8000/docs`
- 已确认前端页面可访问：`http://127.0.0.1:5173/`
- 默认管理员账号可用：
  - 用户名：`admin`
  - 密码：`Admin@123`

### 已完成的代码修复
- 修复 `backend/app/main.py` 中异常字符和路由注册问题，恢复后端入口可启动状态
- 修复 `backend/app/api/v1/users.py` 中模型导入与异常字符串问题
- 修复 `backend/app/models/donor.py` 与 `backend/app/models/target.py` 中不兼容的关系配置
- 将 `backend/app/core/security.py` 的密码哈希方案调整为 `pbkdf2_sha256`
- 在 `backend/requirements.txt` 中补充 `bcrypt<5` 约束说明，便于后续兼容性处理

---

## 当前运行方式

### 前端
```powershell
cd "D:\website project\frontend"
npm.cmd install
npm.cmd run dev -- --host 127.0.0.1
```

- 访问地址：`http://127.0.0.1:5173/`

### 后端
```powershell
cd "D:\website project\backend"
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- 健康检查：`http://127.0.0.1:8000/health`
- API 文档：`http://127.0.0.1:8000/docs`

### 数据库
- 数据库类型：MySQL 8
- 数据库名：`foundation_donation`
- 配置文件：`backend/.env`

---

## 当前环境基线
- Node.js：`v24.14.0`
- npm：`11.9.0`
- Python：`3.11.6`
- MySQL：`8.0`

### 环境说明
- PowerShell 下建议使用 `npm.cmd`，避免执行策略影响 `npm`
- 当前项目已验证 `Python 3.14.x` 不适合直接安装后端依赖，建议固定使用 `Python 3.11.x`
- 后端当前采用 `pbkdf2_sha256` 作为密码哈希方案；若后续需要切回 `bcrypt`，需重新验证 `passlib` 与 `bcrypt` 的兼容版本

---

## 2026-03-21 核心流程验收结果

### 验收范围
- 登录鉴权
- 仪表盘统计接口
- 捐款人管理：新增、列表查询、编辑、删除
- 捐款目标管理：新增、列表查询、编辑、删除
- 用户管理：新增、列表查询、编辑、禁用
- 捐款管理：新增、列表查询、详情、编辑、删除、导出
- 统计报表：趋势、按目标统计、按支付方式统计
- 操作日志列表

### 验收方式
- 使用 `backend/.venv` 下的 Python 环境，通过 FastAPI `TestClient` 对核心接口执行真实联调验收
- 使用管理员账号 `admin / Admin@123`
- 验收过程中创建临时测试数据，并在结束后完成清理
- 由于系统当前没有用户删除接口，验收创建的测试用户已统一设置为 `inactive`

### 验收结论
- 核心流程已完成一轮接口级验收，主链路通过
- 验收中发现 1 个阻断问题：`GET /api/v1/donations/export` 被 `/donations/{donation_id}` 错误匹配，返回 `422`
- 该问题已修复：调整 `backend/app/main.py` 中路由注册顺序，将导出路由提前到捐款路由之前
- 同时补充了 `http://127.0.0.1:5173` 到后端 CORS 白名单，减少本地联调地址差异带来的风险
- 修复后已完成回归验证：登录、创建捐款、导出 Excel、清理测试数据均通过

### 当前状态
- 核心流程可以继续进入页面级联调和人工操作验收
- 当前最优先的后续工作不再是继续堆功能，而是补充基础自动化验收与工程固化

---

## 下一步待办事项

### 优先级 1 - 页面级验收
- 验证登录后的仪表盘页面数据加载与展示是否稳定
- 验证捐款列表页面的筛选、分页、详情跳转、编辑、删除、导出操作
- 验证捐款人、目标、用户、日志、统计页面的基础交互是否正常
- 记录页面联调中发现的接口异常、数据格式不一致、权限问题和展示问题

### 优先级 2 - 工程固化
- 补充前端环境变量：增加 `frontend/.env.development` 与 `frontend/.env.production`，抽离 `VITE_API_BASE`
- 补充部署说明：整理生产环境启动方式、Nginx 代理、数据库初始化、默认账号说明
- 评估是否恢复 `bcrypt`，或明确固定使用 `pbkdf2_sha256`
- 增加基础后端启动检查或自动化脚本，降低环境重复配置成本

### 优先级 3 - 功能补全
- 实现附件上传接口：`POST /api/v1/donations/{id}/attachments`
- 实现审核流程接口：`PUT /api/v1/donations/{id}/review`
- 实现捐款人历史捐款接口：`GET /api/v1/donors/{id}/donations`

### 优先级 4 - 工程完善
- 引入 Alembic 迁移，替代当前 `create_all` 初始化方案
- 增加统一异常处理，返回统一 `{ code, message, data }` 结构
- 统一分页接口响应结构：`{ items, total, page, page_size }`
- 做一次完整生产构建与部署验证

---

## 2026-03-21 页面级验收结果

### 验收方式
- 基于前端页面源码逐页检查登录、布局、捐款、捐款人、目标、日志、统计、用户管理等核心页面
- 结合 `vite build` 进行页面可编译性与路由装配验证
- 验证时间：2026-03-21

### 发现的问题
- 前端存在多处源码损坏，表现为坏标签、坏引号、损坏字符串和路由文件语法错误
- 受影响页面包括：登录页、主布局、路由配置、捐款列表、捐款表单、捐款详情、捐款人管理、目标管理、日志页、统计页、用户管理页
- 这些问题会直接导致页面无法编译、路由守卫失效或页面无法打开

### 已完成修复
- 重写并修复 `frontend/src/router/index.js`
- 重写并修复 `frontend/src/layout/Layout.vue`
- 重写并修复 `frontend/src/views/Login.vue`
- 重写并修复捐款相关页面：列表、表单、详情
- 重写并修复捐款人、目标、日志、统计、用户管理页面
- 修复 `frontend/src/components/StatusTag.vue` 中的损坏映射配置

### 验收结论
- 页面级源码阻断问题已清理
- 前端生产构建已通过：`npm.cmd run build`
- 当前前端已达到“可编译、可路由、可继续人工页面联调”的状态

### 剩余风险
- 本轮未使用真实浏览器执行点击级手工回归，因此仍建议补一轮浏览器端人工联调
- 构建产物存在较大的 JS chunk，当前不阻断验收，但后续可再做性能优化

---

## 2026-03-21 页面联调问题修复记录

### 问题现象
- 人工联调时发现：
- 新增捐款保存成功后，捐款列表未显示对应记录
- 操作日志页面空白
- 统计报表页面空白
- 同时仪表盘统计数值正常

### 根因分析
- 前端列表、日志、统计页在默认查询时会把空筛选参数一并发送到后端
- 典型参数包括：`date_from=''`、`date_to=''`、`target_id=''`
- 后端 FastAPI 对 `Optional[date]`、`Optional[int]` 不会把空字符串自动当作 `None`，而是直接返回 `422`
- 因此这些页面实际不是“无数据”，而是初始请求失败后表现为空白
- 仪表盘接口不携带这些空筛选参数，所以显示正常

### 修复内容
- 修复文件：`frontend/src/utils/request.js`
- 在请求拦截器中统一清洗 `params`
- 自动剔除值为 `''`、`null`、`undefined` 的查询参数，避免空字符串触发后端校验错误
- 同时补充了对后端数组型 `detail` 错误响应的提示提取逻辑，便于前端展示更清晰的报错信息

### 回归结果
- `GET /api/v1/donations` 在清洗空参数后返回 `200`
- `GET /api/v1/logs` 在清洗空参数后返回 `200`
- `GET /api/v1/stats/trend` 在清洗空参数后返回 `200`
- 前端重新执行 `npm.cmd run build` 通过

### 后续建议
- 优先重新人工回归以下页面：
- 捐款列表
- 操作日志
- 统计报表
- 后续如新增更多筛选页，默认沿用统一请求清洗逻辑，避免重复出现同类问题

---

## 2026-03-21 工程固化记录

### 本次目标
- 补充前端环境变量配置
- 补充部署说明与交付文档

### 已完成内容
- 新增 `frontend/.env.development`
- 新增 `frontend/.env.production`
- 将前端请求基地址抽离为 `VITE_API_BASE`
- 将开发环境 Vite 代理目标抽离为 `VITE_API_PROXY_TARGET`
- 将开发环境主机和端口抽离为 `VITE_DEV_HOST`、`VITE_DEV_PORT`
- 更新 `frontend/vite.config.js`，改为通过 `loadEnv` 读取环境变量
- 更新 `frontend/src/utils/request.js`，改为使用 `import.meta.env.VITE_API_BASE`
- 重写 `README.md`，补充：
- 环境要求
- 默认账号
- 前后端配置
- 前端环境变量说明
- 本地启动方式
- 前端生产构建方式
- Nginx 反向代理示例
- 部署检查清单

### 验证结果
- 前端重新执行 `npm.cmd run build` 通过
- 当前前端 API 地址配置已不再依赖硬编码或隐式代理约定
- 当前项目已具备基础部署说明，可用于后续测试环境或生产环境交付整理

---

## 2026-03-21 自动化验收补充记录

### 本次目标
- 补充最基础的自动化验收能力
- 覆盖核心联调主链路，降低后续回归风险

### 已完成内容
- 新增后端 smoke 验收脚本：`backend/scripts/smoke_acceptance.py`
- 脚本基于 FastAPI `TestClient` 执行，不依赖额外测试框架
- 覆盖以下流程：
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
- 更新 `README.md`，补充自动化验收脚本的运行方式与覆盖范围说明

### 运行方式
- `cd "D:\website project\backend"`
- `.venv\Scripts\python.exe scripts\smoke_acceptance.py`

### 验证结果
- 脚本已在当前环境执行通过
- 输出结果：`Smoke acceptance passed.`

### 当前意义
- 后续修改登录、捐款、日志、统计、导出相关代码时，可先运行该脚本进行快速回归
- 该脚本已能覆盖本轮联调中暴露过的核心主链路风险
