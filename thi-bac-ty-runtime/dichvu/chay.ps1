# Bật Thị Bạc Ty ở chế độ nền.
#   .\dichvu\chay.ps1
#
# `pythonw.exe` chứ không phải `python.exe`: không cửa sổ đen nào bật lên.
# Hệ quả là mọi lỗi chỉ nằm trong data/nhat-ky/runtime.log.

$goc = Split-Path -Parent $PSScriptRoot
$py  = "D:\SUNSWaGz 2027\Python 3.12.10\pythonw.exe"
$pid_file = Join-Path $PSScriptRoot "pid.txt"

if (Test-Path $pid_file) {
  $cu = Get-Content $pid_file -ErrorAction SilentlyContinue
  if ($cu -and (Get-Process -Id $cu -ErrorAction SilentlyContinue)) {
    Write-Host "Đang chạy rồi (PID $cu). Dừng trước bằng .\dichvu\dung.ps1"
    exit 1
  }
}

if (-not (Test-Path $py)) {
  Write-Host "Không thấy pythonw.exe ở: $py"
  Write-Host "Sửa đường dẫn `$py trong file này."
  exit 1
}

Start-Process -FilePath $py `
  -ArgumentList (Join-Path $PSScriptRoot "chay-nen.py") `
  -WorkingDirectory $goc -WindowStyle Hidden

Start-Sleep -Seconds 3
Write-Host "Thị Bạc Ty đã chạy nền  ->  http://localhost:5188"
Write-Host "Nhật ký: data\nhat-ky\runtime.log"
