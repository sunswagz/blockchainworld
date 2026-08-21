# Xem Thị Bạc Ty đang thế nào, và tầng đào tạo đã có gì chưa.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\trang-thai.ps1
#
# ⚠ FILE .ps1 Ở ĐÂY PHẢI LƯU UTF-8 **CÓ BOM** — xem đầu bat.ps1.

$ErrorActionPreference = "Stop"

# Console PowerShell mặc định đọc/ghi theo bảng mã ANSI. Không đặt hai dòng
# này thì mọi chữ tiếng Việt lấy từ API hiện ra thành ký tự rác — nội dung
# ĐÚNG, chỉ có màn hình sai, nên rất dễ tưởng runtime hỏng.
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$OutputEncoding = [Text.Encoding]::UTF8
$PID_FILE = Join-Path $PSScriptRoot "pid.txt"

function Ok($m)   { Write-Host "  OK   $m" }
function Nhac($m) { Write-Host "  ~    $m" }
function Xau($m)  { Write-Host "  ✗    $m" }

$id = $null
if (Test-Path $PID_FILE) { $id = (Get-Content $PID_FILE -Raw).Trim() }
if ($id -and (Get-Process -Id $id -ErrorAction SilentlyContinue)) {
  Ok "tiến trình nền đang chạy, PID $id"
} else {
  Nhac "không thấy tiến trình nền (pid.txt trống hoặc đã chết)"
}

try {
  $s = Invoke-RestMethod -Uri "http://127.0.0.1:5188/api/trang-thai" -TimeoutSec 30
} catch {
  Xau "không gọi được buồng lái: $($_.Exception.Message)"
  Nhac "xem data\nhat-ky\runtime.log"
  exit 1
}

Write-Host ""
Ok "vòng $($s.vong) · chế độ $($s.che) · nhịp $($s.nhipGiay)s"

$song = ($s.cang | Where-Object { $_.songSot }).Count
if ($song -eq $s.cang.Count) { Ok "cảng: $song/$($s.cang.Count) sống" }
else { Xau "cảng: $song/$($s.cang.Count) sống — MÙ MỘT MẮT" }

if ($s.dongHo.daDo) {
  $l = [math]::Round($s.dongHo.lechGiay, 1)
  if ($s.dongHo.dangKeu) { Xau "đồng hồ máy lệch $l giây so với sàn (đã bù, nhưng nên chỉnh NTP)" }
  else { Ok "đồng hồ khớp sàn (lệch $l giây)" }
} else {
  Xau "CHƯA đo được lệch đồng hồ — mọi phép đếm mốc đang chạy trên giờ MÁY"
}

Ok "cặp cân: $($s.coHoi.Count) · qua cửa: $($s.soDuyet)"

Write-Host ""
Write-Host "  ── tầng đào tạo ──"
Ok "băng phiên này: $($s.bang.soKhung) khung · đang ghi: $(if ($s.bang.bat) {'có'} else {'TẮT'})"
Ok "sổ: $($s.so.soLuot) lượt quét đã ghi"

try {
  $b = Invoke-RestMethod -Uri "http://127.0.0.1:5188/api/bang" -TimeoutSec 60
  if ($b.bao.lanhLan) { Ok "băng trên đĩa: $($b.soKhung) khung, $($b.bao.soFile) file, LÀNH" }
  else { Xau "băng: $($b.soKhung) khung · $($b.bao.soFileHong) file hỏng · bỏ $($b.bao.soByteBoQua) byte" }
} catch {
  Nhac "chưa đọc được băng: $($_.Exception.Message)"
}

Nhac "cửa sổ giữ $($s.giuGio) giờ — băng phải phủ HẾT ngần ấy mới hậu kiểm được một cơ hội"
Write-Host ""
Write-Host "  buồng lái → http://localhost:5188   (tab Đào tạo)"
