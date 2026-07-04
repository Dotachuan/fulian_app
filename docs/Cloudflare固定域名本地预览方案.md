# Cloudflare 固定域名本地预览方案

适用场景：

- 已购买域名：`fulian520.com`
- 后端暂时仍运行在本地电脑
- 希望微信小程序手机扫码时走固定域名，而不是临时 `loca.lt`

推荐目标：

- 小程序接口域名：`https://api.fulian520.com/api/v1`
- 本地后端地址：`http://127.0.0.1:8000`

---

## 一、先确认 Cloudflare NS 生效

你已经把 NS 改成：

- `anirban.ns.cloudflare.com`
- `asa.ns.cloudflare.com`

下一步先在 Cloudflare 控制台确认：

1. 站点 `fulian520.com` 状态为 `Active`
2. DNS 页面可以正常编辑记录

如果状态还不是 `Active`，先等待解析生效。

---

## 二、安装 cloudflared

如果本机还没装：

```powershell
winget install Cloudflare.cloudflared
```

装好后执行：

```powershell
cloudflared --version
```

---

## 三、登录 Cloudflare

第一次使用要先授权：

```powershell
cloudflared tunnel login
```

执行后会自动打开浏览器。

你需要：

1. 登录 Cloudflare
2. 选择站点 `fulian520.com`
3. 完成授权

授权成功后，本机会生成 Cloudflare 凭据文件。

---

## 四、创建固定 Tunnel

建议 tunnel 名称统一用：

```powershell
cloudflared tunnel create fulian-backend
```

创建成功后，Cloudflare 会返回一个 `Tunnel ID`。

同时本机通常会生成类似文件：

```text
C:\Users\admin\.cloudflared\<Tunnel-ID>.json
```

---

## 五、把子域名绑定到 Tunnel

执行：

```powershell
cloudflared tunnel route dns fulian-backend api.fulian520.com
```

执行成功后，`api.fulian520.com` 就会指向这条 tunnel。

---

## 六、配置本地 tunnel ingress

在目录：

```text
C:\Users\admin\.cloudflared\
```

新建或编辑：

```text
config.yml
```

内容示例：

```yaml
tunnel: <你的 Tunnel ID>
credentials-file: C:\Users\admin\.cloudflared\<你的 Tunnel ID>.json

ingress:
  - hostname: api.fulian520.com
    service: http://127.0.0.1:8000
  - service: http_status:404
```

注意：

- `tunnel` 换成你自己的 Tunnel ID
- `credentials-file` 换成你机器上的真实 json 路径

---

## 七、启动本地后端

确保本地 FastAPI 正常运行：

```powershell
cd "D:\website project\backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

先验证：

```text
http://127.0.0.1:8000/health
```

应返回：

```json
{"status":"ok"}
```

---

## 八、启动固定域名 Tunnel

可以直接执行：

```powershell
cd "D:\website project\backend"
powershell -ExecutionPolicy Bypass -File .\scripts\start_backend_cloudflare_tunnel.ps1
```

它本质上运行的是：

```powershell
cloudflared tunnel run fulian-backend
```

---

## 九、验证固定域名

浏览器直接打开：

```text
https://api.fulian520.com/health
```

如果能返回：

```json
{"status":"ok"}
```

说明固定域名已经成功打到你本地后端。

---

## 十、切换小程序接口地址

当上一步成功后，再修改：

文件：

```text
miniapp/.env.local
```

内容改为：

```env
VITE_MP_WEIXIN_API_BASE_URL=https://api.fulian520.com/api/v1
```

然后重新构建小程序：

```powershell
cd "D:\website project\miniapp"
npm run build:mp-weixin
```

---

## 十一、微信小程序后台配置

登录微信公众平台，进入：

- 开发
- 开发管理
- 开发设置
- 服务器域名

把以下域名加入 `request 合法域名`：

```text
https://api.fulian520.com
```

注意：

- 不要带 `/api/v1`
- 必须是 HTTPS

---

## 十二、真机预览

重新导入或重新编译：

```text
miniapp/dist/build/mp-weixin
```

然后重新生成预览二维码，用手机微信扫码。

---

## 常见问题

### 1. `api.fulian520.com/health` 打不开

先检查：

1. 本地后端是否在运行
2. `cloudflared tunnel run fulian-backend` 是否在运行
3. `config.yml` 的 Tunnel ID 和 json 路径是否正确
4. `api.fulian520.com` 是否已成功 route 到 tunnel

### 2. 浏览器能打开，但小程序仍请求失败

通常检查：

1. 微信后台是否已配置 `request 合法域名`
2. 小程序是否已重新构建
3. 微信开发者工具是否使用了最新产物
4. 手机扫码是否是新的预览码

### 3. 电脑关机后别人还能访问吗

不能。

这个方案虽然是固定域名，但后端仍然运行在你的本地电脑上：

- 电脑关机
- 电脑休眠
- 本地网络断开
- tunnel 进程退出

都会导致外部无法访问。

---

## 当前建议

先完成到这一步：

1. Cloudflare 站点激活
2. `cloudflared tunnel login`
3. `cloudflared tunnel create fulian-backend`
4. `cloudflared tunnel route dns fulian-backend api.fulian520.com`
5. `https://api.fulian520.com/health` 能打开

等这一步通了，再把小程序接口正式切过去。
