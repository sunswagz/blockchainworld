# Dừng Khâm Thiên Giám.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\dung.ps1
#
# ⚠ FILE .ps1 Ở ĐÂY PHẢI LƯU UTF-8 **CÓ BOM**.
#   Windows PowerShell 5.1 đọc .ps1 không BOM theo bảng mã ANSI, nên chữ tiếng
#   Việt vỡ và script không parse nổi — lỗi báo ra là "Unexpected token" ở một
#   dòng chẳng liên quan gì. Sửa bằng trình soạn thảo nào lưu không BOM là hỏng
#   lại. Cùng bẫy đã ghi ở tu-cam-thanh-runtime/dichvu/.

$ErrorActionPreference = "Stop"
$GOC = Split-Path -Parent $PSScriptRoot
$PY  = "D:\SUNSWaGz 2027\Python 3.12.10\python.exe"
$PYW = "D:\SUNSWaGz 2027\Python 3.12.10\pythonw.exe"
$PID_FILE = Join-Path $PSScriptRoot "pid.txt"

function Ok($m)   { Write-Host "  OK   $m" }
function Loi($m)  { Write-Host "  LỖI  $m"; exit 1 }
function Nhac($m) { Write-Host "  ~    $m" }

function Lay-Pid {
  if (-not (Test-Path $PID_FILE)) { return $null }
  $p = (Get-Content $PID_FILE -Raw).Trim()
  if (-not $p) { return $null }
  $tt = Get-Process -Id $p -ErrorAction SilentlyContinue
  if (-not $tt) { Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue; return $null }
  return $tt
}


$tt = Lay-Pid
if (-not $tt) { Nhac "không chạy"; exit 0 }
Stop-Process -Id $tt.Id -Force
Start-Sleep -Seconds 2
Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
Ok "đã dừng PID $($tt.Id)"
