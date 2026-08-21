# Dừng Thị Bạc Ty đang chạy nền.
#   .\dichvu\dung.ps1
#
# Giết theo PID đã ghi, KHÔNG quét theo tên tiến trình: trên máy này có ba
# runtime Python cùng chạy, và `Stop-Process -Name pythonw` sẽ giết cả ba.

$pid_file = Join-Path $PSScriptRoot "pid.txt"
if (-not (Test-Path $pid_file)) { Write-Host "Không có pid.txt — chưa chạy nền?"; exit 0 }

$id = Get-Content $pid_file -ErrorAction SilentlyContinue
if (-not $id) { Write-Host "pid.txt rỗng"; exit 0 }

$p = Get-Process -Id $id -ErrorAction SilentlyContinue
if (-not $p) {
  Write-Host "PID $id không còn chạy — dọn pid.txt"
  Remove-Item $pid_file -Force -ErrorAction SilentlyContinue
  exit 0
}

# Đóng băng ghi tử tế: gửi tín hiệu dừng rồi mới ép. Giết thẳng thì thành
# viên gzip cuối bị cụt — băng vẫn đọc được (trình đọc chịu được đuôi cụt)
# nhưng mất tối đa 50 khung chưa xả.
Stop-Process -Id $id -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Remove-Item $pid_file -Force -ErrorAction SilentlyContinue
Write-Host "Đã dừng (PID $id)."
