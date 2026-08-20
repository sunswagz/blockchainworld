# Bật Khâm Thiên Giám chạy nền.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\bat.ps1
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


$dang = Lay-Pid
if ($dang) { Nhac "đang chạy rồi, PID $($dang.Id)"; exit 0 }

if (-not (Test-Path $PYW)) { Loi "không thấy pythonw ở $PYW" }
# Tham số PHẢI được bọc dấu nháy. Đường dẫn máy này có dấu cách
# ("SUNSWaGz 2027"), và `-ArgumentList` không bọc sẽ TÁCH nó thành nhiều
# tham số — pythonw nhận "D:\SUNSWaGz" làm tên script rồi chết ngay, không
# kịp ghi dòng nhật ký nào. Triệu chứng: bat.ps1 báo "không lên" mà
# runtime.log trống trơn, nên không có gì để lần.
$kich = '"' + (Join-Path $PSScriptRoot "chay-nen.py") + '"'
Start-Process -FilePath $PYW -ArgumentList $kich `
  -WorkingDirectory $GOC -WindowStyle Hidden
# Chờ 12 giây chứ không 3: runtime nạp hơn 20 module rồi mới ghi PID.
# Bản đầu chờ 3 giây và luôn báo "không lên" trong khi nó đang lên bình
# thường — một báo động giả ở đúng lúc mọi thứ đang đúng.
Start-Sleep -Seconds 12

$moi = Lay-Pid
if ($moi) {
  Ok "đã bật, PID $($moi.Id)"
  Ok "buồng lái → http://localhost:5186"
  Nhac "vòng tiến hoá chạy mỗi ngày MỘT lượt, trong chính tiến trình này"
} else {
  Loi "không lên — xem data/nhat-ky/runtime.log"
}
