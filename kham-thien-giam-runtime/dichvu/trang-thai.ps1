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
$PID_FILE = Join-Path $PSScriptRoot "pid.txt"

function Ok($m)   { Write-Host "  OK   $m" }
function Nhac($m) { Write-Host "  ~    $m" }

function Lay-Pid {
  if (-not (Test-Path $PID_FILE)) { return $null }
  $p = (Get-Content $PID_FILE -Raw).Trim()
  if (-not $p) { return $null }
  $tt = Get-Process -Id $p -ErrorAction SilentlyContinue
  if (-not $tt) { Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue; return $null }
  return $tt
}

$tt = Lay-Pid
if (-not $tt) {
  Nhac "KHÔNG chạy"
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
if (Test-Path $log) {
  Write-Host ""
  Write-Host "  --- 10 dòng nhật ký cuối ---"
  Get-Content $log -Tail 10 -Encoding UTF8 | ForEach-Object { Write-Host "  $_" }
} else {
  Write-Host ""
  Nhac "chưa có nhật ký ở $log"
}
