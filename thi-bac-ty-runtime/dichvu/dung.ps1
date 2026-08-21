# Dừng Thị Bạc Ty đang chạy nền.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\dung.ps1
#
# ⚠ FILE .ps1 Ở ĐÂY PHẢI LƯU UTF-8 **CÓ BOM** — xem đầu bat.ps1.

$ErrorActionPreference = "Stop"
$PID_FILE = Join-Path $PSScriptRoot "pid.txt"

function Ok($m)   { Write-Host "  OK   $m" }
function Nhac($m) { Write-Host "  ~    $m" }

if (-not (Test-Path $PID_FILE)) { Nhac "không có pid.txt — chưa chạy nền?"; exit 0 }

$id = (Get-Content $PID_FILE -Raw).Trim()
if (-not $id) { Nhac "pid.txt rỗng"; Remove-Item $PID_FILE -Force; exit 0 }

$p = Get-Process -Id $id -ErrorAction SilentlyContinue
if (-not $p) {
  Nhac "PID $id không còn chạy — dọn pid.txt"
  Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
  exit 0
}

# Giết theo PID đã ghi, KHÔNG quét theo tên tiến trình. Máy này có BA runtime
# Python cùng chạy (5182, 5186, 5188), và `Stop-Process -Name pythonw` sẽ giết
# cả ba — hai cung kia chết theo mà không ai hiểu vì sao.
Stop-Process -Id $id -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
Ok "đã dừng, PID $id"
Nhac "thành viên gzip cuối của băng có thể cụt đuôi — bình thường, trình đọc chịu được"
