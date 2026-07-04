# miniapp

福莲教育促进会会员服务小程序前端，基于 `uni-app`。

## 当前包含页面

- 会员登录
- 首页
- 我的
- 会员入口
- 我的捐赠
- 捐赠证书
- 开票申请
- 会员名录
- 新闻列表 / 详情
- 公告列表 / 详情
- 财务公示 / 基金明细
- 关于福莲 / 机构简介

## 本地启动

```bash
cd miniapp
npm install
npm run dev:h5
```

H5 本地调试默认访问：

```text
http://127.0.0.1:8000/api/v1
```

## 微信开发者工具预览

1. 启动后端服务，确保 `http://127.0.0.1:8000` 可访问。
2. 在 `miniapp` 目录执行：

```bash
npm run dev:mp-weixin
```

或生成稳定产物：

```bash
npm run build:mp-weixin
```

3. 打开微信开发者工具，导入以下目录：

- 开发模式：`miniapp/dist/dev/mp-weixin`
- 构建产物：`miniapp/dist/build/mp-weixin`

4. 导入时使用当前小程序 `AppID`。
5. 开发阶段可在微信开发者工具中保留本地调试所需设置。

## 手机扫码预览

如果要在手机微信中扫码预览，当前后端接口不能继续使用 `127.0.0.1`，需要先暴露一个可访问的 HTTPS 地址。

当前项目已经预留了小程序侧环境变量：

```text
VITE_MP_WEIXIN_API_BASE_URL
```

本地临时预览可以这样做：

1. 启动后端服务。
2. 在 `backend` 目录执行：

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\start_backend_tunnel.ps1
```

3. 记录终端输出的 `https://xxxx.loca.lt` 地址。
4. 将该地址写入 `miniapp/.env.local`：

```text
VITE_MP_WEIXIN_API_BASE_URL=https://xxxx.loca.lt/api/v1
```

5. 重新执行：

```bash
npm run build:mp-weixin
```

6. 在微信开发者工具重新导入或重新编译 `dist/build/mp-weixin`。
7. 通过开发者工具的“预览”生成二维码，在手机微信扫码。

注意：

- `loca.lt` 是临时公网地址，重启后通常会变化。
- 手机扫码预览期间，后端服务和隧道进程都必须保持运行。
- 这适合开发预览，不适合作为长期正式访问方案。

## 请求配置

请求基址由 `src/config/env.js` 统一管理：

- H5 本地调试：`VITE_H5_API_BASE_URL`
- 微信开发者工具本地联调：`VITE_MP_WEIXIN_API_BASE_URL`

默认都指向：

```text
http://127.0.0.1:8000/api/v1
```

后续如果要切到真机预览或测试版，只需要把小程序侧地址替换为可访问的公网接口地址即可。
