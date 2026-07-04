Set-Location -LiteralPath "D:\website project\backend"

if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
  Write-Error "cloudflared is not installed."
  exit 1
}

cloudflared tunnel run fulian-backend
