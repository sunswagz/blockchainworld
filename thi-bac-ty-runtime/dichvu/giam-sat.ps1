# Bộ giám sát Thị Bạc Ty: bật lại làn nào đã chết, và GHI LẠI mỗi lần bật.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\giam-sat.ps1          soi MỘT lượt
#     powershell -ExecutionPolicy Bypass -File dichvu\giam-sat.ps1 -Vong    thường trú
#
# ## Cỗ máy TỰ CHẾT, không phải mất theo máy
#
# Làn thật dừng lúc **30/08 16:53 UTC** và nằm im **70,8 giờ**.
# `runtime.log` không một dòng lỗi — dòng cuối là biểu ngữ khởi động, rồi
# hết.
#
# ⚠ Bản đầu của chú thích này ghi "máy khởi động lại năm tiếng sau đó",
# và câu ấy SAI. Đo lại: `LastBootUpTime` là 28/08 13:03, máy chạy liền
# **131,9 giờ** — nó chưa hề khởi động lại. Chỗ tôi sai là đọc
# `StartTime` của mấy tiến trình Python rồi coi đó là giờ máy lên. **Giờ
# tiến trình lên không phải giờ máy lên**, và hai thứ ấy khác nhau đúng
# ở chỗ quyết định: nếu máy có khởi động lại thì lỗi nằm ở "thiếu mục tự
# chạy"; máy chạy liền mà cỗ máy vẫn chết thì lỗi là **nó tự chết**, và
# một lối tắt Startup không cứu được gì.
#
# Nên thứ THẬT SỰ cần là bộ giám sát thường trú này. Lối tắt Startup vẫn
# đáng có — nó lấp ca khởi động lại, ca chưa xảy ra — nhưng đừng nhầm nó
# là thứ đã cứu Tử Cấm Thành. Tử Cấm Thành sống vì `chay-nen.py` của nó
# tự bọc một vòng giám sát bên trong.
#
# ## Vì sao THƯỜNG TRÚ chứ không dùng tác vụ định kỳ
#
# Trên máy này **Task Scheduler đang TẮT** (`Get-Service Schedule` →
# Stopped; `Start-Service` → "Cannot open Schedule service", thiếu quyền
# quản trị). `schtasks` lẫn COM `Schedule.Service` đều cụt — thử cả hai
# đều ném. Móc khởi động duy nhất còn lại là thư mục Startup, mà nó chỉ
# bắn MỘT phát lúc đăng nhập. Nên vòng lặp phải nằm trong chính script.
#
# ## Ba điều nó phải làm, cả ba đều học từ chỗ đã sai
#
# **1. GHI SỔ mỗi lần bật lại.** Một bộ giám sát im lặng biến "cỗ máy
# chết mỗi chín tiếng" thành chuyện không ai biết — nó chữa triệu chứng
# và giấu luôn bệnh. Sổ ghi lúc nào, làn nào, và CHẾT BAO LÂU RỒI.
#
# **2. Thăm dò bằng đường RẺ, và HỎI LẠI trước khi kết luận.** Lượt thử
# đầu hỏi `/api/trang-thai` — **11,24 giây** vì nó dựng cả ảnh chụp —
# nên nó báo NHẦM làn thật là chết và ghi vào sổ một cái chết KHÔNG XẢY
# RA. Một cuốn sổ như thế còn tệ hơn không có sổ. Nay hỏi
# `/api/cau-hinh` (0,061 giây) và đòi hai lần trượt liên tiếp.
#
# **3. Có ĐIỂM BỎ CUỘC.** Học từ `tu-cam-thanh-runtime/dichvu/chay-nen.py`,
# chỗ đã ghi sẵn: "cấu hình sai làm tiến trình chết trong một giây, và
# nếu không có nghỉ tăng dần + điểm bỏ cuộc thì bộ giám sát sẽ dựng lại
# nó hàng nghìn lượt một phút — nện API sàn và làm nóng máy suốt đêm mà
# không ai hay". Ở nhịp mười phút thì không tới mức ấy, nhưng cái sai
# vẫn y nguyên về CHẤT: **bật lại mãi biến một hỏng VĨNH VIỄN thành một
# chuỗi trục trặc, và không ai đọc ra**. Nên sau
# `TOI_DA_LIEN_TIEP` lượt phải bật lại liên tiếp, nó THÔI bật và ghi một
# dòng to. Làn ấy sống lại (do người bật tay) thì nó tự thôi bỏ cuộc.
#
# ## Và chính nó cũng phải đếm được là còn sống
#
# Một tiến trình thường trú thì cũng chết được, và lúc ấy không còn ai
# canh ai. Mỗi vòng nó ghi đè `giam-sat-nhip.txt` bằng giờ UTC — tuổi
# file ấy trả lời "người gác đêm còn sống không". Chuyện đã xảy ra thật
# ở cung khác: 30/08 lúc 12:56 cả hai bộ giám sát của Tử Cấm Thành cùng
# biến mất, và nhật ký không có một dòng nào để lần.
#
# ## File này PHẢI có BOM
#
# PowerShell 5.1 đọc .ps1 không BOM theo bảng mã ANSI, nên dấu tiếng
# Việt hoá rác và một byte lạc đủ làm hỏng cú pháp. Đã cắn ngay lượt
# chạy đầu: "Missing closing '}'" ở một dòng hoàn toàn lành.

param([switch]$Vong, [int]$NhipGiay = 600)

$ErrorActionPreference = "Stop"
$GOC = Split-Path -Parent $PSScriptRoot
$NKY = Join-Path $GOC "data\nhat-ky"
$LOG = Join-Path $NKY "giam-sat.log"
$NHIP = Join-Path $NKY "giam-sat-nhip.txt"
$DUONG_DEM = Join-Path $NKY "giam-sat-lien-tiep.json"
New-Item -ItemType Directory -Force -Path $NKY | Out-Null

# Bao nhiêu lượt phải bật lại LIÊN TIẾP thì thôi bật. Sáu lượt ở nhịp
# mười phút là một giờ liền cứ mười phút lại chết một lần — quá đủ để
# nói đây là hỏng thật chứ không phải trục trặc.
$TOI_DA_LIEN_TIEP = 6

function Gio() { return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ") }

function Ghi([string]$cau) {
  Add-Content -Path $LOG -Value "$(Gio)  $cau" -Encoding utf8
}

# Cổng SỐNG hay không mới là câu hỏi thật, không phải "PID còn không".
# Một tiến trình treo vẫn giữ PID mà không trả lời ai - và với một cỗ
# máy đọc bốn sàn thì treo là chuyện có thật.
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

# ⚠ HAI HÀM NÀY NHẬN ĐƯỜNG DẪN QUA THAM SỐ, cố ý — đừng "gọn hơn" bằng
# cách đọc biến ở ngoài.
#
# Bản đầu để `$DEM` là hằng số đường dẫn ở phạm vi script, còn `MotLuot`
# có biến cục bộ `$dem` là bộ đếm. **Trong PowerShell tên biến KHÔNG
# phân biệt hoa thường, nên `$DEM` và `$dem` là MỘT.** Cộng với phạm vi
# ĐỘNG — hàm được gọi nhìn thấy biến cục bộ của hàm gọi nó — `GhiDem`
# đọc `$DEM` ra chính cái hashtable, rồi `Set-Content -Path <hashtable>`
# đổi nó thành chuỗi và ghi ra một file tên
# **`System.Collections.Hashtable`** ở thư mục hiện hành.
#
# Không lỗi nào ném. `Get-Content $DEM` đọc lại đúng file rác ấy nên cả
# phép tự kiểm cũng thấy "ghi xong, đọc lại khớp". Thứ duy nhất sai là
# bộ đếm không bao giờ sống qua một lượt — tức điểm bỏ cuộc không bao
# giờ có hiệu lực, mà vẫn trông như có.
function DocDem([string]$duong) {
  if (-not (Test-Path $duong)) { return @{} }
  try {
    $o = Get-Content $duong -Raw | ConvertFrom-Json
    $h = @{}
    foreach ($p in $o.PSObject.Properties) { $h[$p.Name] = [int]$p.Value }
    return $h
  } catch { return @{} }
}

# KHÔNG nuốt lỗi ở đây. Đây là phép ghi làm cho điểm bỏ cuộc có hiệu
# lực qua các lượt; nuốt lỗi ở đúng chỗ này biến "bỏ cuộc" thành một
# con số chỉ sống trong bộ nhớ của một lượt, tức là không bỏ cuộc bao
# giờ. Đã cắn thật: bộ đếm trong sổ ghi "4/6" mà file vẫn nằm ở 3.
function GhiDem([string]$duong, $h) {
  try {
    ($h | ConvertTo-Json -Compress) | Set-Content -Path $duong -Encoding utf8 -ErrorAction Stop
  } catch {
    Ghi "KHONG ghi duoc bo dem lien tiep ($duong) - $($_.Exception.Message). Diem bo cuoc se KHONG co hieu luc qua cac luot."
  }
}

$lan = @()
$lan += ,@{ ten = "that"; cong = 5188; demo = $false; luu = (Join-Path $GOC "data\thi-bac-ty-danh-muc.json") }
$lan += ,@{ ten = "demo"; cong = 5288; demo = $true;  luu = (Join-Path $GOC "data-demo\thi-bac-ty-danh-muc.json") }

function MotLuot() {
  $dem = DocDem $DUONG_DEM
  foreach ($l in $lan) {
    $k = $l.ten
    if (-not $dem.ContainsKey($k)) { $dem[$k] = 0 }

    if (Song $l.cong) {
      # Sống lại sau khi đã bỏ cuộc: nói ra, và thôi bỏ cuộc. Không có
      # dòng này thì người bật tay không biết bộ giám sát đã nhận lại việc.
      if ($dem[$k] -ge $TOI_DA_LIEN_TIEP) {
        Ghi "lan $($k): da song lai - thoi bo cuoc, nhan canh tiep"
      }
      $dem[$k] = 0
      continue
    }

    # ĐÃ BỎ CUỘC thì im. Ghi mỗi mười phút một dòng "vẫn chết" là dựng ra
    # đúng thứ tiếng ồn làm người ta thôi đọc sổ.
    if ($dem[$k] -ge $TOI_DA_LIEN_TIEP) { continue }

    # HỎI LẠI trước khi kết luận. Một lượt quét nặng có thể chiếm máy đủ
    # lâu để một lần hỏi trượt, và bật lại vì thế là hành động dựa trên
    # một cái chết chưa xảy ra. Hai lần trượt liên tiếp thì mới tin.
    Start-Sleep -Seconds 20
    if (Song $l.cong) {
      Ghi "lan $($k): tra loi TRE o lan hoi dau, van song - khong bat lai"
      $dem[$k] = 0
      continue
    }

    $tuoi = TuoiGio $l.luu
    if ($null -eq $tuoi) { $viTuoi = "chua co ban luu" } else { $viTuoi = "da chet chung $tuoi gio" }
    $dem[$k] = $dem[$k] + 1
    Ghi "lan $k (cong $($l.cong)) KHONG tra loi - $viTuoi; bat lai (lien tiep $($dem[$k])/$TOI_DA_LIEN_TIEP)"

    $bat = Join-Path $PSScriptRoot "bat.ps1"
    try {
      if ($l.demo) { & $bat -Demo | Out-Null } else { & $bat | Out-Null }
    } catch {
      Ghi "lan $k : bat.ps1 NEM - $($_.Exception.Message)"
    }

    # Xác nhận bằng CỔNG, không tin lời `bat.ps1`. Nó chỉ biết tiến trình
    # đã sinh ra; còn tiến trình có lên nổi hay không thì cổng mới nói.
    Start-Sleep -Seconds 20
    if (Song $l.cong) {
      Ghi "lan $k : da len lai"
    } else {
      Ghi "lan $k : VAN KHONG LEN sau khi bat - xem runtime.log"
    }

    if ($dem[$k] -ge $TOI_DA_LIEN_TIEP) {
      Ghi "lan $k : BO CUOC - da phai bat lai $TOI_DA_LIEN_TIEP luot LIEN TIEP. Day gan nhu luon la hong that (cau hinh, cong ban, dia day) chu khong phai truc trac tam thoi. Bat lai tiep chi nen API san. Xem data\nhat-ky\runtime.log, sua, roi chay dichvu\bat.ps1 - giam sat se tu nhan canh lai."
    }
  }
  GhiDem $DUONG_DEM $dem
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
