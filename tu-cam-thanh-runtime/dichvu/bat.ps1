# Bật lại Tử Cấm Thành sau khi dừng.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\bat.ps1

$GOC = Split-Path -Parent $PSScriptRoot
$cong = (Get-Content "$GOC\config.json" -Raw | ConvertFrom-Json).port

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
Write-Host "  ⚠    chưa lên sau 45 giây. Xem: $GOC\data\nhat-ky\runtime.log`n"
exit 1
