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
# ── Vì sao dùng thư mục Startup chứ không dùng Task Scheduler ──────────────
# Bản đầu tôi đăng ký một tác vụ lịch. Trên máy này nó hỏng, và hỏng theo kiểu
# đánh lạc hướng: `schtasks` trả "ERROR: The network address is invalid.", còn
# cmdlet trả "The task XML contains an unexpected node." Cả hai đều nghe như lỗi
# cú pháp. Nguyên nhân thật là **dịch vụ Task Scheduler đang tắt** (Status
# Stopped dù StartType Automatic), và bật lại cần quyền quản trị.
#
# Thư mục Startup làm đúng việc cần: chạy lúc đăng nhập, không cần admin, không
# phụ thuộc dịch vụ nào. Thứ duy nhất mất đi là "tự khởi động lại khi hỏng" của
# Task Scheduler — mà `chay-nen.py` vốn đã tự lo, còn kỹ hơn: nó có nghỉ tăng
# dần và biết bỏ cuộc khi cấu hình sai.

$ErrorActionPreference = "Stop"
$GOC = Split-Path -Parent $PSScriptRoot
$TEN_LNK = "Tử Cấm Thành.lnk"
$KHOI_DONG = Join-Path ([Environment]::GetFolderPath("Startup")) "Tu Cam Thanh - runtime.lnk"

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

# ── 4. Lối tắt tự chạy lúc đăng nhập ─────────────────────────────────────
$sh = New-Object -ComObject WScript.Shell
$k = $sh.CreateShortcut($KHOI_DONG)
$k.TargetPath = $py
$k.Arguments = "dichvu\chay-nen.py"
$k.WorkingDirectory = $GOC
$k.Description = "Runtime giao dịch Tử Cấm Thành (chạy nền, không cửa sổ)"
$k.WindowStyle = 7
$k.Save()
Ok "tự chạy lúc đăng nhập: $KHOI_DONG"

# ── 5. Lối tắt desktop ───────────────────────────────────────────────────
# Tạo bằng tên ASCII rồi mới đổi sang tên có dấu.
#
# COM WScript.Shell ép đường dẫn về bảng mã ANSI, nên "Tử Cấm Thành.lnk" tới
# tay nó thành "T? C?m Thành.lnk" và Save() ném FileNotFoundException — thông
# báo nghe như thiếu thư mục, chứ không hề nhắc gì tới bảng mã. Rename-Item thì
# đi qua .NET nên Unicode nguyên vẹn.
$desktop = [Environment]::GetFolderPath("Desktop")
$tam = Join-Path $desktop "Tu Cam Thanh.lnk"
$dich = Join-Path $desktop $TEN_LNK

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
Ok "lối tắt: Desktop\$TEN_LNK"

# ── 6. Chạy luôn ─────────────────────────────────────────────────────────
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
  Lối tắt       Desktop\$TEN_LNK
  Nhật ký       $GOC\data\nhat-ky\runtime.log

  Xem trạng thái   powershell -File dichvu\trang-thai.ps1
  Dừng             powershell -File dichvu\dung.ps1
  Bật lại          powershell -File dichvu\bat.ps1
  Gỡ cài đặt       powershell -File dichvu\go-cai.ps1

  Từ giờ bật máy là nó tự chạy. Không cần mở terminal nữa.

"@
