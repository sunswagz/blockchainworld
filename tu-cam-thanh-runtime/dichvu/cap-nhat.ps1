# Đẩy mã nguồn từ repo sang bản đang chạy.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\cap-nhat.ps1 -Den "D:\SUNSWaGz 2027\tu-cam-thanh-runtime"
#     powershell -ExecutionPolicy Bypass -File dichvu\cap-nhat.ps1 -Den "..." -Thu   # chỉ xem, không ghi
#
# ⚠ File này phải lưu UTF-8 CÓ BOM (xem đầu cai-dat.ps1).
#
# ── Vì sao cần script này ────────────────────────────────────────────────
# Bản đang CHẠY nằm ngoài repo (để khỏi lẫn với mã nguồn, và để giấu đi nếu
# muốn). Nhưng nằm ngoài repo thì `git pull` không với tới nó: sửa mã trong
# repo, commit, pull — bản đang chạy vẫn y nguyên. Không có gì báo cả, và
# người ta sẽ ngồi tự hỏi vì sao thay đổi không có tác dụng.
#
# Nên: repo giữ MÃ NGUỒN, thư mục ngoài giữ MÃ + KHOÁ + DỮ LIỆU. Script này
# đẩy mã sang, và **không bao giờ đụng** vào `.env` hay `data/` — mất `.env`
# là mất khoá sàn, mất `data/` là mất toàn bộ lịch sử giao dịch và bài học.

param(
  [Parameter(Mandatory = $true)][string]$Den,
  [switch]$Thu
)

$ErrorActionPreference = "Stop"
$GOC = Split-Path -Parent $PSScriptRoot

# Chỉ những thứ này được đẩy đi. Danh sách TƯỜNG MINH chứ không phải "chép tất
# rồi trừ ra": thêm một thư mục mới vào repo mà quên sửa danh sách thì nó không
# được đẩy — dễ nhận ra. Còn "chép tất rồi trừ" mà quên trừ thì nó ĐÈ MẤT dữ
# liệu, và không lấy lại được.
$MA = @("trader", "scripts", "skills", "web", "dichvu", "run.py", "requirements.txt", "README.md")
$GIU = @(".env", "data", "config.json", "dichvu\trang-thai.json", "dichvu\dung-lai")

function Ok($m)  { Write-Host "  OK   $m" }
function Loi($m) { Write-Host "  LỖI  $m"; exit 1 }

Write-Host "`n=== Cập nhật mã cho bản đang chạy ===`n"
Write-Host "  từ : $GOC"
Write-Host "  tới: $Den`n"

if (-not (Test-Path (Join-Path $Den "config.json"))) {
  Loi "không thấy config.json ở đích — đó có phải thư mục runtime không?"
}
if ($GOC -eq $Den) { Loi "nguồn và đích là một" }

# config.json KHÔNG bị ghi đè: bản đang chạy có "cungTinh" trỏ về cung tĩnh,
# và có thể có mode/cặp khác. Đè lên là âm thầm đổi cấu hình vận hành.
Write-Host "  giữ nguyên, không đụng tới: $($GIU -join ', ')`n"

$soChep = 0
foreach ($m in $MA) {
  $tu = Join-Path $GOC $m
  if (-not (Test-Path $tu)) { continue }
  $toi = Join-Path $Den $m
  if ($Thu) {
    Write-Host "  [thử] sẽ chép $m"
    $soChep++
    continue
  }
  if (Test-Path $tu -PathType Container) {
    # Xoá thư mục đích trước rồi chép mới: chép đè không dọn được file đã bị
    # xoá ở repo, và một file .py cũ sót lại vẫn được Python nạp bình thường.
    if (Test-Path $toi) { [System.IO.Directory]::Delete($toi, $true) }
    Copy-Item -LiteralPath $tu -Destination $toi -Recurse -Force
  } else {
    Copy-Item -LiteralPath $tu -Destination $toi -Force
  }
  Ok "đã chép $m"
  $soChep++
}

if ($Thu) { Write-Host "`n  (chế độ thử — chưa ghi gì)`n"; exit 0 }

# Trạng thái chạy của bản cũ đi theo `dichvu/` là sai — nó chứa PID của tiến
# trình khác.
foreach ($f in @("dichvu\trang-thai.json", "dichvu\dung-lai")) {
  $p = Join-Path $Den $f
  if ([System.IO.File]::Exists($p)) { [System.IO.File]::Delete($p) }
}

Write-Host @"

  Đã chép $soChep mục.

  Khởi động lại để mã mới có hiệu lực:
    powershell -File "$Den\dichvu\dung.ps1"
    powershell -File "$Den\dichvu\bat.ps1"

"@
