# Chuyển runtime sang thư mục khác, sửa hết mọi thứ trỏ vào nó.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\chuyen-nha.ps1 -Den "D:\Chỗ\Khác\tct"
#     powershell -ExecutionPolicy Bypass -File dichvu\chuyen-nha.ps1 -Den "..." -An
#
#   -An   đặt thuộc tính ẩn cho thư mục đích
#
# ⚠ File này phải lưu UTF-8 CÓ BOM (xem đầu cai-dat.ps1).
#
# Runtime chạy được ở bất cứ đâu — nó không cần nằm trong repo. Nhưng có ba sợi
# dây trỏ vào nó, và cả ba đứt ÂM THẦM chứ không báo lỗi:
#
#   1. Lối tắt desktop và lối tắt Startup giữ đường dẫn TUYỆT ĐỐI. Chuyển thư
#      mục xong bấm lối tắt thì không có gì xảy ra cả.
#   2. `snapshot.py` ghi ảnh chụp sang cung tĩnh bằng đường dẫn thư mục anh em.
#      Ra khỏi repo là nó không thấy cung nữa. (Đã sửa để bỏ qua và nhắc một
#      lần, thay vì đẻ ra một thư mục rác rồi ghi vào đó như trước.)
#   3. Nếu thư mục cũ nằm trong repo, git sẽ coi là ĐÃ XOÁ. Commit sau đó sẽ
#      xoá runtime khỏi repo thật.
#
# Script này lo cả ba.

param(
  [Parameter(Mandatory = $true)][string]$Den,
  [string]$Tu,          # nội bộ — thư mục nguồn, dùng khi script đã tự sao ra ngoài
  [switch]$An
)

$ErrorActionPreference = "Stop"
$GOC = if ($Tu) { $Tu } else { Split-Path -Parent $PSScriptRoot }

function Ok($m)   { Write-Host "  OK   $m" }
function Loi($m)  { Write-Host "  LỖI  $m"; exit 1 }
function Nhac($m) { Write-Host "  ⚠    $m" }

# ── 0. Tự dọn mình ra khỏi thư mục sắp chuyển ────────────────────────────
# Windows không cho chuyển một thư mục đang có file bị mở, và PowerShell giữ
# file .ps1 đang chạy ở trạng thái mở. Nên script phải rời khỏi thư mục nguồn
# trước khi động vào nó.
#
# Sao sang %TEMP% rồi gọi lại là chưa đủ: tiến trình cha vẫn sống để chờ con,
# và bản thân nó cũng đang giữ file trong thư mục nguồn. Phải chạy RỜI HẲN
# (`Start-Process`, không chờ) rồi cha thoát ngay để nhả khoá.
#
# Vì lý do đó, từ đây trở xuống KHÔNG được gọi bất cứ script nào nằm trong
# $GOC — gọi `dichvu\dung.ps1` ở đó là khoá lại thư mục vừa mới nhả ra.
if (-not $Tu) {
  if (-not (Test-Path (Join-Path $GOC "config.json"))) {
    Loi "không thấy config.json ở $GOC — chạy script này từ trong thư mục runtime"
  }
  $tam = Join-Path $env:TEMP ("chuyen-nha-" + [guid]::NewGuid().ToString("N") + ".ps1")
  Copy-Item -LiteralPath $PSCommandPath -Destination $tam -Force
  $doi = @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", $tam,
           "-Den", $Den, "-Tu", $GOC)
  if ($An) { $doi += "-An" }
  Start-Process powershell -ArgumentList $doi
  Write-Host "`n  Đã mở một cửa sổ mới để làm việc chuyển nhà."
  Write-Host "  Cửa sổ này phải đóng lại thì thư mục mới hết bị khoá — đóng ngay bây giờ.`n"
  exit 0
}

# Đợi tiến trình cha thoát hẳn để nhả khoá thư mục nguồn.
Start-Sleep -Seconds 3
# Và đứng ở một chỗ chắc chắn nằm ngoài thư mục sắp chuyển. Một tiến trình đang
# "đứng trong" thư mục là đủ để Windows từ chối chuyển nó.
Set-Location -LiteralPath $env:TEMP

Write-Host "`n=== Chuyển Tử Cấm Thành sang chỗ khác ===`n"
Write-Host "  từ : $GOC"
Write-Host "  tới: $Den`n"

if (Test-Path $Den) {
  if ((Get-ChildItem $Den -Force | Measure-Object).Count -gt 0) {
    Loi "thư mục đích đã tồn tại và KHÔNG rỗng — chọn chỗ khác cho chắc"
  }
}

# ── 1. Dừng đã ───────────────────────────────────────────────────────────
# Chuyển thư mục trong lúc Python đang chạy trong đó thì Windows khoá file và
# lệnh move hỏng giữa chừng — tệ hơn hẳn là hỏng ngay từ đầu.
#
# Viết thẳng ở đây thay vì gọi `dichvu\dung.ps1`: gọi script nằm trong $GOC là
# khoá lại đúng thư mục sắp chuyển.
$cong = (Get-Content "$GOC\config.json" -Raw | ConvertFrom-Json).port
$tt = Join-Path $GOC "dichvu\trang-thai.json"
if (Test-Path $tt) {
  $s = Get-Content $tt -Raw | ConvertFrom-Json
  # Giám sát trước, runtime sau — ngược lại thì giám sát dựng runtime mới ngay.
  foreach ($p in @($s.giamSatPid, $s.conPid)) {
    if ($p) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
  }
}
foreach ($c in (Get-NetTCPConnection -LocalPort $cong -State Listen -ErrorAction SilentlyContinue)) {
  Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2
if (Get-NetTCPConnection -LocalPort $cong -State Listen -ErrorAction SilentlyContinue) {
  Loi "vẫn còn tiến trình giữ cổng $cong — dừng hẳn rồi chạy lại"
}
Ok "đã dừng runtime"

# ── 2. Nhớ đường tới cung tĩnh TRƯỚC khi chuyển ──────────────────────────
$cung = Join-Path (Split-Path -Parent $GOC) "tu-cam-thanh"
$coCung = Test-Path (Join-Path $cung "index.html")
if ($coCung) { Ok "cung tĩnh: $cung" }
else { Nhac "không thấy cung tĩnh cạnh đây — sẽ bỏ trống cungTinh" }

# ── 3. Cảnh báo nếu đang nằm trong repo git ──────────────────────────────
$trongRepo = $false
try {
  # `git -C` chứ KHÔNG `Push-Location`: đặt vị trí hiện tại của PowerShell vào
  # bên trong thư mục sắp chuyển là tự khoá nó lại, và `Move-Item` sau đó hỏng
  # với "the item is in use" — không tiến trình nào của mình còn mở file nào cả,
  # nên nhìn vào thì tưởng là Defender hay trình đánh chỉ mục giữ. Mất một lúc
  # mới lần ra chính script là thủ phạm.
  git -C $GOC rev-parse --is-inside-work-tree *> $null
  $trongRepo = ($LASTEXITCODE -eq 0)
} catch { }
if ($trongRepo) {
  Nhac "thư mục này đang nằm trong một repo git."
  Write-Host "       Sau khi chuyển, git sẽ thấy toàn bộ runtime là ĐÃ XOÁ."
  Write-Host "       Đừng commit thay đổi đó nếu bạn muốn giữ mã trong repo —"
  Write-Host "       dùng: git checkout -- tu-cam-thanh-runtime"
  Write-Host ""
}

# ── 4. Chuyển ───────────────────────────────────────────────────────────
$cha = Split-Path -Parent $Den
if (-not (Test-Path $cha)) { New-Item -ItemType Directory -Force $cha | Out-Null }

# Thử lại vài lượt. Trên Windows, thư mục vừa bị ghi thường bị Defender hoặc
# trình đánh chỉ mục giữ handle thêm vài giây — `Move-Item` khi đó báo "the item
# is in use" dù chẳng tiến trình nào của mình còn mở nó. Đo tại máy này: hỏng ở
# lượt đầu, rồi vài phút sau chạy cái một. Bỏ cuộc ngay lượt đầu là bỏ cuộc
# trước một khoá sẽ tự tan.
$chuyenXong = $false
foreach ($lan in 1..10) {
  try {
    Move-Item -LiteralPath $GOC -Destination $Den -Force -ErrorAction Stop
    $chuyenXong = $true
    Ok "đã chuyển thư mục$(if ($lan -gt 1) { " (thử $lan lượt)" })"
    break
  } catch {
    if ($lan -eq 10) { Loi "không chuyển được sau 10 lượt: $($_.Exception.Message)" }
    Start-Sleep -Milliseconds 1500
  }
}
if (-not $chuyenXong) { Loi "không chuyển được" }

# ── 5. Trỏ lại cung tĩnh ────────────────────────────────────────────────
$cfgF = Join-Path $Den "config.json"
$cfg = Get-Content $cfgF -Raw -Encoding UTF8
if ($coCung) {
  # Để ConvertTo-Json lo việc escape, đừng tự nhân đôi dấu gạch chéo bằng
  # -replace: chuỗi thay thế của .NET không coi `\` là ký tự escape, nên
  # '\\\\' đẻ ra BỐN gạch chéo chứ không phải hai. Kết quả là đường dẫn thành
  # `C:\\Users\\...`, mà Windows lại chấp nhận dấu phân cách lặp — nên nó chạy
  # đúng một cách tình cờ, và sẽ hỏng ở chỗ nào đó khó đoán sau này.
  $duongJson = ConvertTo-Json $cung          # đã kèm dấu nháy và escape đúng
  $thay = $duongJson -replace '\$', '$$$$'   # `$` là ký tự đặc biệt của -replace
  $cfg = $cfg -replace '"cungTinh"\s*:\s*"[^"]*"', ('"cungTinh": ' + $thay)
  # Ghi UTF-8 KHÔNG BOM: config.json do Python đọc, và json.loads nghẹn ở BOM.
  [System.IO.File]::WriteAllText($cfgF, $cfg, (New-Object System.Text.UTF8Encoding($false)))
  Ok "đã đặt cungTinh trong config.json"
}

# ── 6. Sửa lối tắt ──────────────────────────────────────────────────────
$sh = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$startup = [Environment]::GetFolderPath("Startup")

function SuaLnk($duongLnk, $thamSo, $nhan) {
  if (-not (Test-Path $duongLnk)) { return $false }
  # COM không đọc/ghi nổi tên file có dấu — làm việc trên bản sao tên ASCII.
  $tam = Join-Path $env:TEMP ("sua-lnk-" + [guid]::NewGuid().ToString("N") + ".lnk")
  Copy-Item -LiteralPath $duongLnk $tam -Force
  $l = $sh.CreateShortcut($tam)
  $l.WorkingDirectory = $Den
  $l.Arguments = $thamSo
  $l.Save()
  Remove-Item -LiteralPath $duongLnk -Force
  Move-Item -LiteralPath $tam -Destination $duongLnk -Force
  Ok "đã trỏ lại $nhan"
  return $true
}

SuaLnk (Join-Path $desktop "Tử Cấm Thành.lnk") "dichvu\mo.py" "lối tắt desktop" | Out-Null
SuaLnk (Join-Path $startup "Tu Cam Thanh - runtime.lnk") "dichvu\chay-nen.py" "lối tắt tự chạy" | Out-Null

# ── 7. Ẩn ───────────────────────────────────────────────────────────────
if ($An) {
  (Get-Item -LiteralPath $Den -Force).Attributes = 'Directory, Hidden'
  Ok "đã đặt thuộc tính ẩn cho thư mục"
  Nhac "ẩn chỉ là ẩn khỏi Explorer mặc định, KHÔNG phải bảo mật."
}

# ── 8. Chạy lại ─────────────────────────────────────────────────────────
$py = $null
foreach ($ung in @(
    "D:\SUNSWaGz 2027\Python 3.12.10\pythonw.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python313\pythonw.exe")) {
  if (Test-Path $ung) { $py = $ung; break }
}
if ($py) {
  Start-Process -FilePath $py -ArgumentList "dichvu\chay-nen.py" -WorkingDirectory $Den -WindowStyle Hidden
  foreach ($i in 1..45) {
    Start-Sleep -Seconds 1
    try { Invoke-WebRequest "http://127.0.0.1:$cong/api/state" -UseBasicParsing -TimeoutSec 2 | Out-Null
          Ok "chạy lại được từ chỗ mới sau $i giây"; break } catch {}
  }
}

Write-Host @"

=== Xong ===

  Runtime    $Den
  Buồng lái  http://localhost:$cong
  Lối tắt    Desktop\Tử Cấm Thành.lnk  (đã trỏ lại chỗ mới)

  Kiểm lại:  powershell -File "$Den\dichvu\trang-thai.ps1"

"@
