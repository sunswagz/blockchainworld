# Xem Khâm Thiên Giám đang thế nào.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\trang-thai.ps1
#
# ⚠ FILE .ps1 Ở ĐÂY PHẢI LƯU UTF-8 **CÓ BOM**.
#   Windows PowerShell 5.1 đọc .ps1 không BOM theo bảng mã ANSI, nên chữ tiếng
#   Việt vỡ và script không parse nổi — lỗi báo ra là "Unexpected token" ở một
#   dòng chẳng liên quan gì. Cùng bẫy đã ghi ở tu-cam-thanh-runtime/dichvu/.

$ErrorActionPreference = "Stop"

# Console PowerShell mặc định đọc/ghi theo bảng mã ANSI. Không đặt hai dòng
# này thì mọi chữ tiếng Việt lấy từ nhật ký hoặc từ API hiện ra thành ký tự
# rác — nội dung ĐÚNG, chỉ có màn hình sai, nên rất dễ tưởng runtime hỏng.
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$OutputEncoding = [Text.Encoding]::UTF8
$GOC = Split-Path -Parent $PSScriptRoot

function Ok($m)   { Write-Host "  OK   $m" }
function Nhac($m) { Write-Host "  ~    $m" }

# Câu hỏi "nó có đang chạy không" nằm ở MỘT chỗ: chung.ps1. Ba script
# này từng có ba bản sao của `Lay-Pid`, và cả ba hỏng cùng một kiểu.
. (Join-Path $PSScriptRoot "chung.ps1")

# ĐƯỜNG NÀY CHỈ ĐỌC. Không Remove-Item, không Stop-Process, không ghi
# gì hết. Bản trước hỏi "nó có chạy không" rồi XOÁ pid.txt — sau câu hỏi
# ấy thì `dung.ps1` không còn tay nắm nào để dừng runtime cho tử tế.
$tt = Lay-Runtime
if (-not $tt) {
  Nhac "KHÔNG chạy — không ai giữ cổng $(Doc-Cong)"
} else {
  Ok "đang chạy, PID $($tt.Id), từ $($tt.StartTime)"
  try {
    # Invoke-RestMethod đoán bảng mã từ header; API trả JSON UTF-8 nhưng
    # PowerShell 5.1 vẫn giải bằng ANSI. Lấy chuỗi thô rồi tự giải.
    $tho = (Invoke-WebRequest -Uri "http://localhost:5186/api/trang-thai" -TimeoutSec 6).RawContentStream
    $ms = New-Object IO.StreamReader($tho, [Text.Encoding]::UTF8)
    $r = $ms.ReadToEnd() | ConvertFrom-Json
    Ok "vòng $($r.vong) · chế độ $($r.che) · băng $($r.bang.soKhung) khung"
    if ($r.dongSong) {
      Ok "dòng sống: $(if ($r.dongSong.dangNoi) { 'đã nối' } else { 'chưa nối' }) · $($r.dongSong.soToken) token · $($r.dongSong.tinNhan) tin"
    }
    if ($r.tienHoa) {
      $d = $r.tienHoa.duong
      Ok "tiến hoá: $($d.soLuot) lượt · nhận $($d.soLanNhan) · trả lại $($d.soLanTraLai) · đứng yên $($d.soLanDungYen)"
      if ($r.tienHoa.ngayDaChay) { Ok "lượt gần nhất: $($r.tienHoa.ngayDaChay)" }
    }
    if ($r.boQua -and $r.boQua.PSObject.Properties.Count -gt 0) {
      Nhac "đang bỏ qua:"
      $r.boQua.PSObject.Properties | ForEach-Object { Write-Host "         $($_.Name): $($_.Value)" }
    }
  } catch {
    Nhac "tiến trình sống nhưng buồng lái chưa trả lời"
  }
}

# Join-Path nhiều đoạn thay vì một chuỗi có dấu chéo ngược. Bản đầu viết
# đường dẫn thành một chuỗi và ký tự thoát biến thành XUỐNG DÒNG THẬT lúc
# sinh file, nên PowerShell báo "Illegal characters in path" ở một dòng
# trông hoàn toàn bình thường.
$log = Join-Path (Join-Path (Join-Path $GOC "data") "nhat-ky") "runtime.log"
# Ba nguồn tin có thể lệch nhau, và im lặng về chuyện lệch là cách buồng
# lái nói dối mà không ai bắt được. Khai hết ra.
$idThat = -1
if ($tt) { $idThat = $tt.Id }
$idFile = Doc-Pid-File
if ($idFile -and $idFile -ne $idThat) {
  Write-Host ""
  Nhac "pid.txt ghi $idFile nhưng người giữ cổng là $idThat — pid.txt LẠC"
  Nhac "(không xoá ở đây: câu hỏi chỉ đọc thì không được sửa gì)"
}
if (-not $idFile -and $tt) {
  Write-Host ""
  Nhac "runtime đang chạy nhưng KHÔNG có pid.txt — chắc chạy tay bằng run.py"
}
$lac = Xac-Tien-Trinh-Lac
if ($lac.Count -gt 0) {
  Write-Host ""
  Nhac "xác treo (tiến trình của thư mục này mà không giữ cổng): $($lac -join ', ')"
}

if (Test-Path $log) {
  Write-Host ""
  # Nhật ký này có thể CŨ HƠN tiến trình đang chạy: `chay-nen.py` ghi
  # vào đây, `python run.py` chạy tay thì KHÔNG. Đo được thật 30/08:
  # runtime sống 40 phút, mà mười dòng in ra là chuyện của hôm trước —
  # trình bày như tin mới. Nên phải dán nhãn tuổi lên nó.
  $sua = (Get-Item $log).LastWriteTime
  $tuoi = [math]::Round(((Get-Date) - $sua).TotalHours, 1)
  $nhan = "  --- 10 dòng nhật ký cuối (ghi lúc $sua, $tuoi giờ trước) ---"
  Write-Host $nhan
  if ($tt -and $sua -lt $tt.StartTime) {
    Nhac "NHẬT KÝ CŨ HƠN TIẾN TRÌNH ĐANG CHẠY — mấy dòng dưới KHÔNG nói"
    Nhac "về nó. Đừng đọc như tin mới."
  }
  Get-Content $log -Tail 10 -Encoding UTF8 | ForEach-Object { Write-Host "  $_" }
} else {
  Write-Host ""
  Nhac "chưa có nhật ký ở $log"
}
