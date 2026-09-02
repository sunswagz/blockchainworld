# Bộ giám sát Thị Bạc Ty: bật lại làn nào đã chết, và GHI LẠI mỗi lần bật.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\giam-sat.ps1          soi MỘT lượt
#     powershell -ExecutionPolicy Bypass -File dichvu\giam-sat.ps1 -Vong    thường trú
#
# ## Vì sao THƯỜNG TRÚ chứ không dùng tác vụ định kỳ
#
# Trên máy này **Task Scheduler đang TẮT** (`Get-Service Schedule` →
# Stopped, `Start-Service` → "Cannot open Schedule service"), và bật nó
# đòi quyền quản trị. Nên `schtasks` lẫn COM `Schedule.Service` đều
# không dùng được — thử cả hai đều ném.
#
# Móc khởi động DUY NHẤT còn lại là **thư mục Startup**, đúng thứ Tử Cấm
# Thành đang dùng. Mà lối tắt Startup chỉ bắn MỘT phát lúc đăng nhập:
# nó lấp được lỗ "khởi động lại máy", không lấp được lỗ "sập giữa
# chừng". Nên bộ giám sát phải tự lặp.
#
# ## Vì sao nó phải GHI SỔ, không được lặng lẽ bật lại
#
# Một bộ giám sát im lặng biến "cỗ máy chết mỗi chín tiếng" thành một
# chuyện không ai biết. Nó chữa triệu chứng và giấu luôn bệnh — đúng cái
# lớp lỗi mà cả runtime này sinh ra để chặn.
#
# Mỗi lần phải bật lại, nó ghi một dòng vào `data\nhat-ky\giam-sat.log`:
# lúc nào, làn nào, và CHẾT BAO LÂU RỒI — đo bằng tuổi file lưu danh
# mục, thứ runtime ghi mỗi vòng. Ba dòng trong một ngày là một câu khác
# hẳn một dòng trong một tháng, và chỉ có cuốn sổ mới nói được.
#
# ## Và chính nó cũng phải đếm được là còn sống
#
# Một tiến trình thường trú thì cũng chết được, và lúc ấy không còn ai
# canh ai. Nên mỗi vòng nó ghi đè `giam-sat-nhip.txt` bằng giờ UTC hiện
# tại. Tuổi file ấy là câu trả lời cho "bộ giám sát còn sống không" —
# `trang-thai.ps1` đọc nó. Không có nhịp này thì cái chết của người gác
# đêm là cái chết im lặng nhất trong cả hệ.
#
# ## Chuyện đã xảy ra, 30/08-02/09/2026
#
# Làn thật dừng lúc 30/08 16:53 UTC - nhật ký không một dòng lỗi, nó chỉ
# hết. Máy khởi động lại năm tiếng sau đó; Tử Cấm Thành sống dậy vì có
# lối tắt Startup, còn Thị Bạc Ty thì không có gì dựng nó lên. Nằm im
# **70,8 GIỜ**. Lúc nạp lại, 120 vị thế đều có cửa sổ kế toán dài quá
# trần nên bị BỎ và đếm: 8.493 vốn-giờ không ai đo được.
#
# ## File này PHẢI có BOM
#
# PowerShell 5.1 đọc .ps1 không BOM theo bảng mã ANSI của hệ, nên mọi
# dấu tiếng Việt hoá thành rác và một byte lạc đủ làm hỏng cú pháp. Đã
# cắn ngay lượt chạy đầu: "Missing closing '}'" ở một dòng hoàn toàn
# lành. `bat.ps1` và `dung.ps1` đều có BOM - giữ cho giống.

param([switch]$Vong, [int]$NhipGiay = 600)

$ErrorActionPreference = "Stop"
$GOC = Split-Path -Parent $PSScriptRoot
$NKY = Join-Path $GOC "data\nhat-ky"
$LOG = Join-Path $NKY "giam-sat.log"
$NHIP = Join-Path $NKY "giam-sat-nhip.txt"
New-Item -ItemType Directory -Force -Path $NKY | Out-Null

function Gio() { return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ") }

function Ghi([string]$cau) {
  Add-Content -Path $LOG -Value "$(Gio)  $cau" -Encoding utf8
}

# Cổng SỐNG hay không mới là câu hỏi thật, không phải "PID còn không".
# Một tiến trình treo vẫn giữ PID mà không trả lời ai - và với một cỗ
# máy đọc bốn sàn thì treo là chuyện có thật.
#
# Hỏi `/api/cau-hinh` chứ ĐỪNG hỏi `/api/trang-thai`. Đo trên làn thật:
# 0,061 giây so với **11,24 giây** - đường kia dựng cả ảnh chụp. Lượt
# thử đầu tiên của chính bộ giám sát này đã báo NHẦM làn thật là chết
# đúng vì thế, rồi gọi `bat.ps1`, và `bat.ps1` trả lời "đang chạy rồi".
# Không hỏng gì, nhưng sổ đã ghi một cái chết KHÔNG XẢY RA - và một
# cuốn sổ như thế còn tệ hơn không có sổ.
function Song([int]$cong) {
  try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:$cong/api/cau-hinh" -TimeoutSec 15 -UseBasicParsing
    return ($r.StatusCode -eq 200)
  } catch {
    return $false
  }
}

# Chết bao lâu rồi: đo bằng tuổi file lưu danh mục - runtime ghi nó mỗi
# vòng, nên nó là dấu chân mới nhất mà một tiến trình đã chết để lại.
function TuoiGio([string]$duong) {
  if (-not (Test-Path $duong)) { return $null }
  return [math]::Round(((Get-Date) - (Get-Item $duong).LastWriteTime).TotalHours, 2)
}

$lan = @()
$lan += ,@{ ten = "that"; cong = 5188; demo = $false; luu = (Join-Path $GOC "data\thi-bac-ty-danh-muc.json") }
$lan += ,@{ ten = "demo"; cong = 5288; demo = $true;  luu = (Join-Path $GOC "data-demo\thi-bac-ty-danh-muc.json") }

function MotLuot() {
  foreach ($l in $lan) {
    if (Song $l.cong) { continue }

    # HỎI LẠI trước khi kết luận. Một lượt quét nặng có thể chiếm máy đủ
    # lâu để một lần hỏi trượt, và bật lại vì thế là hành động dựa trên
    # một cái chết chưa xảy ra. Hai lần trượt liên tiếp thì mới tin.
    Start-Sleep -Seconds 20
    if (Song $l.cong) {
      Ghi "lan $($l.ten): tra loi TRE o lan hoi dau, van song - khong bat lai"
      continue
    }

    $tuoi = TuoiGio $l.luu
    if ($null -eq $tuoi) { $viTuoi = "chua co ban luu" } else { $viTuoi = "da chet chung $tuoi gio" }
    Ghi "lan $($l.ten) (cong $($l.cong)) KHONG tra loi - $viTuoi; dang bat lai"

    $bat = Join-Path $PSScriptRoot "bat.ps1"
    try {
      if ($l.demo) { & $bat -Demo | Out-Null } else { & $bat | Out-Null }
    } catch {
      Ghi "lan $($l.ten): bat.ps1 NEM - $($_.Exception.Message)"
      continue
    }

    # Xác nhận bằng CỔNG, không tin lời `bat.ps1`. Nó chỉ biết tiến trình
    # đã sinh ra; còn tiến trình có lên nổi hay không thì cổng mới nói.
    Start-Sleep -Seconds 20
    if (Song $l.cong) {
      Ghi "lan $($l.ten): da len lai"
    } else {
      Ghi "lan $($l.ten): VAN KHONG LEN sau khi bat - xem runtime.log"
    }
  }
}

if (-not $Vong) { MotLuot; exit 0 }

# ── chế độ THƯỜNG TRÚ ────────────────────────────────────────────────
#
# Một bản duy nhất. Hai bản cùng chạy thì cả hai cùng thấy làn chết và
# cùng gọi `bat.ps1`; `bat.ps1` tự thoát khi thấy máy đang chạy nên
# không hỏng gì, nhưng sổ sẽ có hai dòng cho một sự việc và người đọc
# đếm gấp đôi số lần chết.
$KHOA = Join-Path $NKY "giam-sat-pid.txt"
if (Test-Path $KHOA) {
  $cu = (Get-Content $KHOA -ErrorAction SilentlyContinue | Select-Object -First 1)
  if ($cu -match '^\d+$') {
    $p = Get-Process -Id ([int]$cu) -ErrorAction SilentlyContinue
    if ($p -and $p.ProcessName -like "*powershell*") {
      Ghi "da co mot ban giam sat dang chay (PID $cu) - ban nay thoat"
      exit 0
    }
  }
}
Set-Content -Path $KHOA -Value $PID -Encoding ascii
Ghi "giam sat THUONG TRU len, PID $PID, nhip $NhipGiay giay"

while ($true) {
  try { MotLuot } catch { Ghi "vong giam sat NEM - $($_.Exception.Message)" }
  # Nhịp ghi SAU mỗi lượt soi, không phải trước: nó phải chứng minh
  # lượt soi đã chạy xong, chứ không chỉ chứng minh tiến trình còn thở.
  Set-Content -Path $NHIP -Value (Gio) -Encoding ascii
  Start-Sleep -Seconds $NhipGiay
}
