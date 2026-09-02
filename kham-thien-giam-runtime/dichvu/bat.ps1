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

function Ok($m)   { Write-Host "  OK   $m" }
function Loi($m)  { Write-Host "  LỖI  $m"; exit 1 }
function Nhac($m) { Write-Host "  ~    $m" }

# Câu hỏi "nó có đang chạy không" nằm ở MỘT chỗ: chung.ps1. Ba script
# này từng có ba bản sao của `Lay-Pid`, và cả ba hỏng cùng một kiểu.
. (Join-Path $PSScriptRoot "chung.ps1")


$dang = Lay-Runtime
if ($dang) {
  Nhac "đang chạy rồi, PID $($dang.Id) — giữ cổng $(Doc-Cong)"
  exit 0
}

# Cổng trống nhưng pid.txt còn sót thì chỉ là rác, dọn rồi đi tiếp.
# TRƯỚC ĐÂY chỗ này đọc pid.txt: không có file ⇒ dựng runtime THỨ HAI
# ghi chung một quyển sổ. Nay cổng trả lời, nên chuyện ấy không xảy ra.
if (Doc-Pid-File) { Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue }

if (-not (Test-Path $PYW)) { Loi "không thấy pythonw ở $PYW" }
# Tham số PHẢI được bọc dấu nháy. Đường dẫn máy này có dấu cách
# ("SUNSWaGz 2027"), và `-ArgumentList` không bọc sẽ TÁCH nó thành nhiều
# tham số — pythonw nhận "D:\SUNSWaGz" làm tên script rồi chết ngay, không
# kịp ghi dòng nhật ký nào. Triệu chứng: bat.ps1 báo "không lên" mà
# runtime.log trống trơn, nên không có gì để lần.
# Bật NGƯỜI CANH GÁC, không bật runtime thẳng.
#
# `chay-nen.py` gọi thẳng uvicorn, không có vòng nào bọc ngoài, nên
# tiến trình chết là hết. Đo 02/09/2026: runtime chết lúc nào đó sau
# 30/08 23:44 và nằm im BA NGÀY — máy vẫn chạy liên tục, không ai
# dựng lại, và không một dòng lỗi nào trong nhật ký.
#
# Người canh gác hỏi cổng mỗi 20 giây rồi dựng lại. Nó tự bật
# `chay-nen.py`, nên đường đi cũ vẫn nguyên — chỉ thêm một lớp ngoài.
$kich = '"' + (Join-Path $PSScriptRoot "canh-gac.py") + '"'
Start-Process -FilePath $PYW -ArgumentList $kich `
  -WorkingDirectory $GOC -WindowStyle Hidden
# Chờ 12 giây chứ không 3: runtime nạp hơn 20 module rồi mới ghi PID.
# Bản đầu chờ 3 giây và luôn báo "không lên" trong khi nó đang lên bình
# thường — một báo động giả ở đúng lúc mọi thứ đang đúng.
Start-Sleep -Seconds 12

$moi = Lay-Runtime
if ($moi) {
  Ok "đã bật, PID $($moi.Id)"
  Ok "buồng lái → http://localhost:$(Doc-Cong)"
  Nhac "vòng tiến hoá chạy mỗi ngày MỘT lượt, trong chính tiến trình này"
} else {
  Loi "không lên — xem data/nhat-ky/runtime.log"
}
