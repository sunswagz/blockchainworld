# Cài Tử Cấm Thành chạy nền: tự dậy khi đăng nhập, lối tắt ngoài desktop.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\cai-dat.ps1
#
# ⚠ MỌI FILE .ps1 Ở ĐÂY PHẢI LƯU UTF-8 **CÓ BOM**.
#   Windows PowerShell 5.1 đọc .ps1 không BOM theo bảng mã ANSI, nên chữ tiếng
#   Việt vỡ thành ký tự lạ và script không parse nổi — lỗi báo ra là "Unexpected
#   token" ở một dòng chẳng liên quan gì, rất khó lần. Sửa bằng trình soạn thảo
#   nào lưu không BOM là hỏng lại. Kiểm nhanh:
#       [System.Management.Automation.Language.Parser]::ParseFile($f,[ref]$null,[ref]$e)
#
# ── Script này KHÔNG bật tự chạy lúc đăng nhập ────────────────────────────
# Nó chỉ tạo một lối tắt ngoài desktop. Bấm vào thì runtime mới lên.
#
# Mặc định đó là có chủ ý: trên một máy nhiều người qua lại, một cỗ máy đặt lệnh
# tự khởi động là thứ không ai xin phép — người ngồi vào máy sau không biết nó
# đang chạy, cũng không biết nó đang giữ vị thế nào.
#
# Muốn tự chạy thì bật trong buồng lái: **Hệ thống → Tự chạy khi đăng nhập**.
# Công tắc để ở đó chứ không để ở đây vì đây là lựa chọn theo TỪNG MÁY và người
# ta sẽ đổi ý nhiều lần — bắt mở terminal mỗi lần đổi là bắt sai chỗ.
#
# Ghi chú kỹ thuật: công tắc ấy đặt một lối tắt vào thư mục Startup chứ KHÔNG
# dùng Task Scheduler. Trên máy này dịch vụ Task Scheduler đang tắt (Status
# Stopped dù StartType Automatic) và bật lại cần quyền quản trị. Nó cũng không
# nói vậy: `schtasks` kêu "network address is invalid", cmdlet kêu "task XML
# contains an unexpected node" — cả hai nghe như lỗi cú pháp.

param(
  # Nơi đặt lối tắt. Mặc định Desktop cho dễ tìm, nhưng đổi được: máy nhiều
  # người qua lại thì một icon "Tử Cấm Thành" trên desktop là thứ đập vào mắt
  # đầu tiên. Đặt vào một thư mục khác thì chạy vẫn y hệt.
  #
  # Chạy lại script này mà không truyền tham số sẽ tạo lại icon ở Desktop — nên
  # nếu đã dời nó đi, nhớ truyền lại đúng chỗ cũ.
  [string]$ThuMucLoiTat = [Environment]::GetFolderPath("Desktop")
)

$ErrorActionPreference = "Stop"
$GOC = Split-Path -Parent $PSScriptRoot
$TEN_LNK = "Tử Cấm Thành.lnk"

function Ok($m)   { Write-Host "  OK   $m" }
function Loi($m)  { Write-Host "  LỖI  $m"; exit 1 }
function Nhac($m) { Write-Host "  ⚠    $m" }

Write-Host "`n=== Cài Tử Cấm Thành chạy nền ===`n"

# ── 1. Không cho cài từ worktree ─────────────────────────────────────────
# Worktree là thứ tạm: `git worktree remove` một cái là dịch vụ trỏ vào hư
# không, và nó hỏng ÂM THẦM — lối tắt vẫn còn đó, chỉ là không có gì để chạy.
if ($GOC -match "\\\.claude\\worktrees\\") {
  Write-Host "  Thư mục này là một git worktree:"
  Write-Host "    $GOC`n"
  Write-Host "  Worktree sẽ bị xoá khi xong việc, và dịch vụ sẽ hỏng lặng lẽ."
  Write-Host "  Cài từ cây chính:"
  Write-Host "    cd <repo>\tu-cam-thanh-runtime"
  Write-Host "    powershell -ExecutionPolicy Bypass -File dichvu\cai-dat.ps1"
  exit 1
}
Ok "chạy từ cây chính: $GOC"

# ── 2. Tìm Python ────────────────────────────────────────────────────────
$py = $null
foreach ($ung in @(
    "D:\SUNSWaGz 2027\Python 3.12.10\pythonw.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python313\pythonw.exe")) {
  if (Test-Path $ung) { $py = $ung; break }
}
if (-not $py) {
  $c = Get-Command pythonw.exe -ErrorAction SilentlyContinue
  if ($c) { $py = $c.Source }
}
if (-not $py) { Loi "không tìm thấy pythonw.exe. Sửa danh sách đường dẫn ở đầu file này." }
Ok "python: $py"

# ── 3. Kiểm phụ thuộc TRƯỚC khi cài ──────────────────────────────────────
# Cài một lối tắt chắc chắn hỏng thì tệ hơn không cài: nó thất bại mỗi lần
# đăng nhập, lặng lẽ, và không ai biết vì log chưa kịp sinh ra.
$pyExe = $py -replace "pythonw\.exe$", "python.exe"
$thu = & $pyExe -c "import uvicorn, fastapi, httpx; print('ok')" 2>&1
if ($LASTEXITCODE -ne 0) { Loi "thiếu gói: $thu`n       chạy: `"$pyExe`" -m pip install -r requirements.txt" }
Ok "gói phụ thuộc đủ"

if (-not (Test-Path "$GOC\.env")) {
  Nhac ".env chưa có — runtime sẽ chạy chế độ mock (không gọi API, không vào lệnh testnet)"
} else { Ok ".env có" }

# ── 4. Lối tắt ───────────────────────────────────────────────────────────
$sh = New-Object -ComObject WScript.Shell
if (-not (Test-Path $ThuMucLoiTat)) { New-Item -ItemType Directory -Force $ThuMucLoiTat | Out-Null }
# Tạo bằng tên ASCII rồi mới đổi sang tên có dấu.
#
# COM WScript.Shell ép đường dẫn về bảng mã ANSI, nên "Tử Cấm Thành.lnk" tới
# tay nó thành "T? C?m Thành.lnk" và Save() ném FileNotFoundException — thông
# báo nghe như thiếu thư mục, chứ không hề nhắc gì tới bảng mã. Rename-Item thì
# đi qua .NET nên Unicode nguyên vẹn.
$tam = Join-Path $ThuMucLoiTat "Tu Cam Thanh.lnk"
$dich = Join-Path $ThuMucLoiTat $TEN_LNK

$lnk = $sh.CreateShortcut($tam)
$lnk.TargetPath = $py
$lnk.Arguments = "dichvu\mo.py"
$lnk.WorkingDirectory = $GOC
$lnk.Description = "Mo buong lai Tu Cam Thanh (tu bat neu chua chay)"
$lnk.WindowStyle = 7
if (Test-Path "$GOC\dichvu\tct.ico") { $lnk.IconLocation = "$GOC\dichvu\tct.ico" }
$lnk.Save()

if (Test-Path $dich) { Remove-Item $dich -Force }
Rename-Item -LiteralPath $tam -NewName $TEN_LNK
Ok "lối tắt: $dich"

# ── 5. Chạy luôn ─────────────────────────────────────────────────────────
$cong = (Get-Content "$GOC\config.json" -Raw | ConvertFrom-Json).port
$dangChay = Get-NetTCPConnection -LocalPort $cong -State Listen -ErrorAction SilentlyContinue
if ($dangChay) {
  Ok "đã có bản đang chạy ở cổng $cong"
} else {
  Start-Process -FilePath $py -ArgumentList "dichvu\chay-nen.py" -WorkingDirectory $GOC -WindowStyle Hidden
  Write-Host "`n  đang chờ runtime mở cổng $cong..."
  $song = $false
  foreach ($i in 1..45) {
    Start-Sleep -Seconds 1
    try { Invoke-WebRequest "http://127.0.0.1:$cong/api/state" -UseBasicParsing -TimeoutSec 2 | Out-Null
          $song = $true; break } catch {}
  }
  if ($song) { Ok "runtime đã chạy sau $i giây" }
  else { Nhac "chưa thấy cổng $cong sau 45 giây — xem data\nhat-ky\runtime.log" }
}

Write-Host @"

=== Xong ===

  Buồng lái     http://localhost:$cong
  Lối tắt       $dich
  Nhật ký       $GOC\data\nhat-ky\runtime.log

  Xem trạng thái   powershell -File dichvu\trang-thai.ps1
  Dừng             powershell -File dichvu\dung.ps1
  Bật lại          powershell -File dichvu\bat.ps1
  Gỡ cài đặt       powershell -File dichvu\go-cai.ps1

  KHÔNG tự chạy khi bật máy — bấm lối tắt thì runtime mới lên.
  Muốn nó tự chạy: mở buồng lái → Hệ thống → "Tự chạy khi đăng nhập".

"@
