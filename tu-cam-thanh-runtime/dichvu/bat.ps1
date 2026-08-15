# Bật lại Tử Cấm Thành sau khi dừng.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\bat.ps1

$GOC = Split-Path -Parent $PSScriptRoot
$cong = (Get-Content "$GOC\config.json" -Raw | ConvertFrom-Json).port
$KHOI_DONG = Join-Path ([Environment]::GetFolderPath("Startup")) "Tu Cam Thanh - runtime.lnk"

if (-not (Test-Path $KHOI_DONG)) {
  Write-Host "`n  Chưa cài. Chạy trước:`n    powershell -ExecutionPolicy Bypass -File dichvu\cai-dat.ps1`n"
  exit 1
}

$dang = Get-NetTCPConnection -LocalPort $cong -State Listen -ErrorAction SilentlyContinue
if ($dang) { Write-Host "`n  Đang chạy sẵn rồi → http://localhost:$cong`n"; exit 0 }

# Lấy đúng pythonw.exe mà lối tắt khởi động đang trỏ vào, thay vì dò lại — hai
# bên dò ra hai bản Python khác nhau là một kiểu lệch rất khó nhận ra.
$py = (New-Object -ComObject WScript.Shell).CreateShortcut($KHOI_DONG).TargetPath
Start-Process -FilePath $py -ArgumentList "dichvu\chay-nen.py" -WorkingDirectory $GOC -WindowStyle Hidden
Write-Host "`n  đang chờ cổng $cong..."
foreach ($i in 1..45) {
  Start-Sleep -Seconds 1
  try { Invoke-WebRequest "http://127.0.0.1:$cong/api/state" -UseBasicParsing -TimeoutSec 2 | Out-Null
        Write-Host "  OK   chạy sau $i giây → http://localhost:$cong`n"; exit 0 } catch {}
}
Write-Host "  ⚠    chưa lên sau 45 giây. Xem: $GOC\data\nhat-ky\runtime.log`n"
exit 1
