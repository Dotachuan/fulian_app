# 阿里云生产部署说明

适用目标：

- 正式上线 `api.fulian520.com`
- 正式上线 `admin.fulian520.com`
- 让微信小程序走正式生产接口
- 保留本地 Cloudflare Tunnel 仅用于开发预览

建议部署形态：

- 1 台阿里云 ECS
- Ubuntu 22.04 LTS
- 2 核 4G / 50GB SSD 起步
- Nginx + FastAPI + MySQL 同机

---

## 1. 服务器准备

### 1.1 安全组

至少放行：

- `22` SSH
- `80` HTTP
- `443` HTTPS

### 1.2 域名解析

在 DNS 中新增：

- `api.fulian520.com` -> ECS 公网 IP
- `admin.fulian520.com` -> ECS 公网 IP

---

## 2. 服务器初始化

登录服务器后，建议先执行：

```bash
sudo timedatectl set-timezone Asia/Shanghai
sudo apt update
sudo apt install -y git nginx mysql-server python3 python3-venv python3-pip nodejs npm unzip
```

如需 Node.js 20，建议改用 NodeSource 或 `nvm` 安装。

创建部署目录：

```bash
sudo mkdir -p /srv/foundation-donation
sudo chown -R $USER:$USER /srv/foundation-donation
cd /srv/foundation-donation
```

拉取代码：

```bash
git clone <你的仓库地址> .
```

---

## 3. 后端部署

### 3.1 Python 虚拟环境

```bash
cd /srv/foundation-donation/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3.2 生产环境变量

复制并编辑模板：

```bash
cp /srv/foundation-donation/deploy/aliyun/env/backend.env.production.example /srv/foundation-donation/backend/.env
```

必须确认以下值：

- `DB_HOST=127.0.0.1`
- `DB_PORT=3306`
- `DB_NAME=foundation_donation`
- `DB_USER`
- `DB_PASSWORD`
- `SECRET_KEY`
- `PUBLIC_ASSET_ORIGIN=https://api.fulian520.com`
- `WECHAT_MINIAPP_APPID`
- `WECHAT_MINIAPP_SECRET`
- `MEMBER_SMS_DEBUG_RETURN_CODE=false`

### 3.3 MySQL 初始化

进入 MySQL：

```bash
sudo mysql
```

执行：

```sql
CREATE DATABASE foundation_donation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'foundation_user'@'127.0.0.1' IDENTIFIED BY '请替换成强密码';
GRANT ALL PRIVILEGES ON foundation_donation.* TO 'foundation_user'@'127.0.0.1';
FLUSH PRIVILEGES;
```

### 3.4 导入本地数据

在本地机器导出：

```bash
mysqldump -u root -p --databases foundation_donation > foundation_donation.sql
```

上传到服务器后导入：

```bash
mysql -u foundation_user -p foundation_donation < foundation_donation.sql
```

### 3.5 上传目录迁移

把本地 `backend/uploads/` 全量同步到服务器：

```bash
rsync -av ./backend/uploads/ <server-user>@<server-ip>:/srv/foundation-donation/backend/uploads/
```

### 3.6 systemd 托管

复制服务模板：

```bash
sudo cp /srv/foundation-donation/deploy/aliyun/systemd/foundation-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable foundation-backend
sudo systemctl start foundation-backend
```

检查状态：

```bash
sudo systemctl status foundation-backend
curl http://127.0.0.1:8000/health
```

---

## 4. 管理后台部署

### 4.1 安装依赖并构建

```bash
cd /srv/foundation-donation/frontend
npm install
npm run build
```

默认 `frontend/.env.production` 已走 `/api/v1`，适合通过 `admin.fulian520.com` 同域反代使用。

这里的关键点是：

- 浏览器访问后台时，请求路径会是 `admin.fulian520.com/api/v1/...`
- 该路径由后台站点自己的 Nginx 直接转发到本机 `127.0.0.1:8000`
- 不需要让后台 API 再绕一圈走 `api.fulian520.com`

---

## 5. Nginx 配置

复制站点配置：

```bash
sudo cp /srv/foundation-donation/deploy/aliyun/nginx/api.fulian520.com.conf /etc/nginx/sites-available/
sudo cp /srv/foundation-donation/deploy/aliyun/nginx/admin.fulian520.com.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/api.fulian520.com.conf /etc/nginx/sites-enabled/api.fulian520.com.conf
sudo ln -sf /etc/nginx/sites-available/admin.fulian520.com.conf /etc/nginx/sites-enabled/admin.fulian520.com.conf
sudo nginx -t
sudo systemctl reload nginx
```

### 5.1 HTTPS 证书

建议使用阿里云 SSL 证书或 Let's Encrypt。

证书文件默认放到：

- `/etc/nginx/ssl/fulian520.com/fullchain.pem`
- `/etc/nginx/ssl/fulian520.com/privkey.pem`

如果证书路径不同，请同步修改两个 Nginx 配置文件。

---

## 6. 微信小程序生产切换

### 6.1 微信公众平台

在小程序后台配置合法域名：

- `request 合法域名`：`https://api.fulian520.com`
- `upload 合法域名`：`https://api.fulian520.com`
- `download 合法域名`：`https://api.fulian520.com`

如需 `web-view` 打开公众号文章，还要确认：

- 小程序已与目标公众号完成关联
- 当前 AppID 主体有权限打开该公众号推文

### 6.2 小程序构建

本地构建正式包：

```bash
cd miniapp
npm install
npm run build:mp-weixin
```

导入目录：

```text
miniapp/dist/build/mp-weixin
```

在微信开发者工具中上传体验版、提审、发布。

---

## 7. 上线验收

### 7.1 服务检查

```bash
curl https://api.fulian520.com/health
```

访问：

- `https://admin.fulian520.com`

### 7.2 业务检查

逐项验证：

- 后台管理员登录
- 新闻 / 公告 / 项目资讯管理
- 图片上传后的地址是否为 `https://api.fulian520.com/uploads/...`
- 小程序登录
- 会员绑定
- 我的捐赠 / 证书 / 开票 / 通讯录
- 意见建议提交与后台导出
- 公众号文章链接真机打开

---

## 8. 后续更新流程

### 8.1 后端 / 后台更新

```bash
cd /srv/foundation-donation
git pull
cd backend
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart foundation-backend

cd /srv/foundation-donation/frontend
npm install
npm run build
sudo systemctl reload nginx
```

### 8.2 小程序更新

```bash
cd miniapp
npm install
npm run build:mp-weixin
```

然后重新上传微信审核版本。

---

## 9. 备份建议

可直接使用仓库里的脚本模板：

- `deploy/aliyun/scripts/backup_mysql.sh`
- `deploy/aliyun/scripts/backup_uploads.sh`

建议通过 `crontab` 每日执行。
