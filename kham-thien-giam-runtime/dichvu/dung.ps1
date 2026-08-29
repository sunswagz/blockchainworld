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

function Ok($m)   { Write-Host "  OK   $m" }
function Loi($m)  { Write-Host "  LỖI  $m"; exit 1 }
function Nhac($m) { Write-Host "  ~    $m" }

# Câu hỏi "nó có đang chạy không" nằm ở MỘT chỗ: chung.ps1. Ba script
# này từng có ba bản sao của `Lay-Pid`, và cả ba hỏng cùng một kiểu.
. (Join-Path $PSScriptRoot "chung.ps1")


# Giết theo CỔNG, không giết theo pid.txt. Windows dùng lại số PID: một
# pid cũ rơi vào tay tiến trình khác thì bản trước `Stop-Process -Force`
# thẳng vào người vô can, không hỏi một câu. Ai đang giữ cổng thì người
# đó đúng là runtime — không cần đoán.
$tt = Lay-Runtime
if (-not $tt) {
  Nhac "không chạy (không ai giữ cổng $(Doc-Cong))"
  if (Doc-Pid-File) {
    Nhac "pid.txt còn sót, dọn đi"
    Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
  }
  $lac = Xac-Tien-Trinh-Lac
  if ($lac.Count -gt 0) { Nhac "xác treo còn nằm lại: $($lac -join ', ')" }
  exit 0
}
Stop-Process -Id $tt.Id -Force
Start-Sleep -Seconds 2
Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
Ok "đã dừng PID $($tt.Id)"

$con = Lay-Runtime
if ($con) { Loi "cổng $(Doc-Cong) VẪN có người giữ (PID $($con.Id)) — còn tiến trình thứ hai" }
