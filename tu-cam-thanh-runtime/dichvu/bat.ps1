# Bật lại Tử Cấm Thành sau khi dừng.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\bat.ps1
#     powershell -ExecutionPolicy Bypass -File dichvu\bat.ps1 -Demo
#
# -Demo bật LÀN HAI CHIỀU ở cổng 5282: sàn giấy (SHORT không bị chặn), sổ riêng
# data-hai-chieu\, 46 chợ, và KHÔNG ghi cung tĩnh. Nó cần sống nhiều TUẦN —
# giả thuyết «keo-lui-short-tien-tuong» cần 30 lệnh SHORT, ước ~6 tuần — nên
# chạy bằng một cửa sổ terminal là hẹn trước cái chết của phép đo.
param([switch]$Demo)

$GOC = Split-Path -Parent $PSScriptRoot

if ($Demo) {
  $env:TCT_LAN      = "demo"
  $env:TCT_CONFIG   = "config-hai-chieu.json"
  $env:TCT_DATA_DIR = Join-Path $GOC "data-hai-chieu"
  $env:TCT_LAN_DEMO = "1"
  $env:BRAIN        = "mock"
  $cauHinh = Join-Path $GOC "config-hai-chieu.json"
} else {
  # Xoá sạch biến của làn demo: PowerShell giữ $env: trong cùng phiên, nên chạy
  # -Demo rồi chạy lại KHÔNG có -Demo sẽ bật làn chính bằng sổ của làn demo.
  foreach ($v in "TCT_LAN","TCT_CONFIG","TCT_DATA_DIR","TCT_LAN_DEMO","BRAIN") {
    Remove-Item "env:$v" -ErrorAction SilentlyContinue
  }
  $cauHinh = Join-Path $GOC "config.json"
}
$cong = (Get-Content $cauHinh -Raw | ConvertFrom-Json).port

$dang = Get-NetTCPConnection -LocalPort $cong -State Listen -ErrorAction SilentlyContinue
if ($dang) { Write-Host "`n  Đang chạy sẵn rồi → http://localhost:$cong`n"; exit 0 }

# Dò pythonw.exe theo cùng thứ tự với cai-dat.ps1. Hai bên dò ra hai bản Python
# khác nhau là kiểu lệch rất khó nhận ra: cả hai đều "chạy được", chỉ là một bản
# thiếu gói và chết ngay khi khởi động.
$py = $null
foreach ($ung in @(
    "D:\SUNSWaGz 2027\Python 3.12.10\pythonw.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python313\pythonw.exe")) {
  if (Test-Path $ung) { $py = $ung; break }
}
if (-not $py) { $c = Get-Command pythonw.exe -ErrorAction SilentlyContinue; if ($c) { $py = $c.Source } }
if (-not $py) { Write-Host "`n  Không tìm thấy pythonw.exe`n"; exit 1 }

Start-Process -FilePath $py -ArgumentList "dichvu\chay-nen.py" -WorkingDirectory $GOC -WindowStyle Hidden
Write-Host "`n  đang chờ cổng $cong..."
foreach ($i in 1..45) {
  Start-Sleep -Seconds 1
  try { Invoke-WebRequest "http://127.0.0.1:$cong/api/state" -UseBasicParsing -TimeoutSec 2 | Out-Null
        Write-Host "  OK   chạy sau $i giây → http://localhost:$cong`n"; exit 0 } catch {}
}
$soNhatKy = if ($Demo) { "data-hai-chieu" } else { "data" }
Write-Host "  ⚠    chưa lên sau 45 giây. Xem: $GOC\$soNhatKy\nhat-ky\runtime.log`n"
exit 1
