# Tử Cấm Thành đang thế nào.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\trang-thai.ps1

$GOC = Split-Path -Parent $PSScriptRoot
$cong = (Get-Content "$GOC\config.json" -Raw | ConvertFrom-Json).port
$KHOI_DONG = Join-Path ([Environment]::GetFolderPath("Startup")) "Tu Cam Thanh - runtime.lnk"

Write-Host "`n=== Tử Cấm Thành ===`n"

# ── tự chạy lúc đăng nhập ────────────────────────────────────────────────
if (-not (Test-Path $KHOI_DONG)) {
  Write-Host "  tự chạy    : CHƯA CÀI"
  Write-Host "               powershell -ExecutionPolicy Bypass -File dichvu\cai-dat.ps1"
} else {
  $k = (New-Object -ComObject WScript.Shell).CreateShortcut($KHOI_DONG)
  # Lối tắt trỏ sai chỗ là kiểu hỏng im lặng nhất: nó vẫn nằm đó, vẫn chạy lúc
  # đăng nhập, chỉ là chạy một thư mục không còn tồn tại.
  $khop = ($k.WorkingDirectory -eq $GOC)
  Write-Host "  tự chạy    : có$(if (-not $khop) { "  ⚠ TRỎ SANG CHỖ KHÁC: $($k.WorkingDirectory)" })"
}

# ── tiến trình ───────────────────────────────────────────────────────────
$tt = Join-Path $PSScriptRoot "trang-thai.json"
if (Test-Path $tt) {
  $s = Get-Content $tt -Raw | ConvertFrom-Json
  if ($s.dungHan) {
    Write-Host "  giám sát   : ĐÃ DỪNG HẲN — $($s.lyDo)"
    Write-Host "               sửa xong chạy: powershell -File dichvu\bat.ps1"
  } else {
    $gs = if ($s.giamSatPid -and (Get-Process -Id $s.giamSatPid -ErrorAction SilentlyContinue)) { "sống" } else { "chết" }
    $rt = if ($s.conPid -and (Get-Process -Id $s.conPid -ErrorAction SilentlyContinue)) { "sống" } else { "chết" }
    Write-Host "  giám sát   : pid $($s.giamSatPid) ($gs) · đã khởi động runtime $($s.lanChay) lượt"
    Write-Host "  runtime    : pid $($s.conPid) ($rt)"
  }
}

# ── cổng + API ───────────────────────────────────────────────────────────
try {
  $r = Invoke-WebRequest "http://127.0.0.1:$cong/api/state" -UseBasicParsing -TimeoutSec 4
  # Giải mã UTF-8 tường minh. `$r.Content` của PowerShell 5.1 đoán bảng mã theo
  # header rồi thường rơi về Latin-1, nên "≥" và mọi chữ có dấu trong thông báo
  # rủi ro hiện thành ký tự vỡ — đúng dòng mà người ta đọc lúc đang lo lắng.
  $st = [System.Text.Encoding]::UTF8.GetString($r.RawContentStream.ToArray()) | ConvertFrom-Json
  Write-Host "  buồng lái  : http://localhost:$cong  (đang trả lời)"
  Write-Host "  phiên      : $($st.symbol) $([math]::Round($st.price,2)) · $($st.mode) · $($st.regime.primary) · vòng $($st.ticks)"
  $a = $st.account
  Write-Host "  tài khoản  : vốn $([math]::Round($a.equityMarked,2)) · $($a.positions.Count) vị thế mở · $($a.closedCount) lệnh đã đóng"
  if ($st.risk.halted) { Write-Host "  RỦI RO     : ĐÃ DỪNG — $($st.risk.halted)" }
} catch {
  Write-Host "  buồng lái  : KHÔNG TRẢ LỜI ở cổng $cong"
}

# ── log ──────────────────────────────────────────────────────────────────
$log = Join-Path $GOC "data\nhat-ky\runtime.log"
if (Test-Path $log) {
  $f = Get-Item $log
  Write-Host "`n  nhật ký    : $log  ($([math]::Round($f.Length/1KB,1)) KB)"
  Write-Host "  --- 12 dòng cuối ---"
  Get-Content $log -Tail 12 -Encoding UTF8 | ForEach-Object { Write-Host "  $_" }
} else {
  Write-Host "`n  nhật ký    : chưa có ($log)"
}
Write-Host ""
