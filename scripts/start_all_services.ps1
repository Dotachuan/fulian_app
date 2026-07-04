param(
  [switch]$IncludeMiniappH5,
  [switch]$RebuildMiniapp
)

$ErrorActionPreference = 'Stop'

$ProjectRoot = "D:\website project"
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"
$MiniappDir = Join-Path $ProjectRoot "miniapp"
$LogDir = Join-Path $ProjectRoot ".runtime"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Step($message) {
  Write-Host ""
  Write-Host "==> $message" -ForegroundColor Cyan
}

function Test-PortListening([int]$Port) {
  $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  return [bool]$listener
}

function Test-TunnelRunning() {
  $processes = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -match '^cloudflared(\.exe)?$' -and $_.CommandLine -match 'tunnel run fulian-backend'
  }
  return [bool]$processes
}

function Start-LoggedPowerShellProcess(
  [string]$Name,
  [string]$WorkingDirectory,
  [string]$Command,
  [string]$StdoutFile,
  [string]$StderrFile
) {
  Start-Process `
    -FilePath "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $Command) `
    -WorkingDirectory $WorkingDirectory `
    -WindowStyle Hidden `
    -RedirectStandardOutput $StdoutFile `
    -RedirectStandardError $StderrFile | Out-Null

  Write-Host "$Name 已启动，日志输出到：" -ForegroundColor Green
  Write-Host "  $StdoutFile"
  Write-Host "  $StderrFile"
}

Write-Step "检查并启动本地后端"
if (Test-PortListening 8000) {
  Write-Host "后端端口 8000 已在监听，跳过启动。" -ForegroundColor Yellow
}
else {
  $backendOut = Join-Path $LogDir "backend.out.log"
  $backendErr = Join-Path $LogDir "backend.err.log"
  $backendCmd = "Set-Location -LiteralPath '$BackendDir'; & '.\.venv\Scripts\python.exe' -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
  Start-LoggedPowerShellProcess `
    -Name "后端服务" `
    -WorkingDirectory $BackendDir `
    -Command $backendCmd `
    -StdoutFile $backendOut `
    -StderrFile $backendErr
  Start-Sleep -Seconds 3
}

Write-Step "检查并启动 Cloudflare Tunnel"
if (Test-TunnelRunning) {
  Write-Host "Cloudflare Tunnel 已在运行，跳过启动。" -ForegroundColor Yellow
}
else {
  $tunnelOut = Join-Path $LogDir "cloudflare-tunnel.out.log"
  $tunnelErr = Join-Path $LogDir "cloudflare-tunnel.err.log"
  $tunnelCmd = "Set-Location -LiteralPath '$BackendDir'; cloudflared tunnel run fulian-backend"
  Start-LoggedPowerShellProcess `
    -Name "Cloudflare Tunnel" `
    -WorkingDirectory $BackendDir `
    -Command $tunnelCmd `
    -StdoutFile $tunnelOut `
    -StderrFile $tunnelErr
  Start-Sleep -Seconds 3
}

Write-Step "检查并启动管理员后台"
if (Test-PortListening 5173) {
  Write-Host "管理员后台端口 5173 已在监听，跳过启动。" -ForegroundColor Yellow
}
else {
  $frontendOut = Join-Path $LogDir "frontend.out.log"
  $frontendErr = Join-Path $LogDir "frontend.err.log"
  $frontendCmd = "Set-Location -LiteralPath '$FrontendDir'; npm.cmd run dev -- --host 127.0.0.1"
  Start-LoggedPowerShellProcess `
    -Name "管理员后台" `
    -WorkingDirectory $FrontendDir `
    -Command $frontendCmd `
    -StdoutFile $frontendOut `
    -StderrFile $frontendErr
  Start-Sleep -Seconds 3
}

if ($RebuildMiniapp) {
  Write-Step "重新构建微信小程序产物"
  Push-Location $MiniappDir
  try {
    & "npm.cmd" run build:mp-weixin
  }
  finally {
    Pop-Location
  }
}

if ($IncludeMiniappH5) {
  Write-Step "检查并启动 miniapp H5 调试"
  if (Test-PortListening 5175) {
    Write-Host "miniapp H5 端口 5175 已在监听，跳过启动。" -ForegroundColor Yellow
  }
  else {
    $miniappOut = Join-Path $LogDir "miniapp-h5.out.log"
    $miniappErr = Join-Path $LogDir "miniapp-h5.err.log"
    $miniappCmd = "Set-Location -LiteralPath '$MiniappDir'; npm.cmd run dev:h5"
    Start-LoggedPowerShellProcess `
      -Name "miniapp H5" `
      -WorkingDirectory $MiniappDir `
      -Command $miniappCmd `
      -StdoutFile $miniappOut `
      -StderrFile $miniappErr
    Start-Sleep -Seconds 3
  }
}

Write-Step "启动结果"
Write-Host ("后端 8000: " + ($(if (Test-PortListening 8000) { "OK" } else { "未启动" })))
Write-Host ("后台 5173: " + ($(if (Test-PortListening 5173) { "OK" } else { "未启动" })))
if ($IncludeMiniappH5) {
  Write-Host ("miniapp H5 5175: " + ($(if (Test-PortListening 5175) { "OK" } else { "未启动" })))
}
Write-Host ("Cloudflare Tunnel: " + ($(if (Test-TunnelRunning) { "OK" } else { "未启动" })))

Write-Host ""
Write-Host "常用访问地址：" -ForegroundColor Green
Write-Host "  后端健康检查: http://127.0.0.1:8000/health"
Write-Host "  固定域名健康检查: https://api.fulian520.com/health"
Write-Host "  管理后台: http://127.0.0.1:5173/"
if ($IncludeMiniappH5) {
  Write-Host "  miniapp H5: http://127.0.0.1:5175/"
}
