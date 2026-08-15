# Dừng Tử Cấm Thành.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\dung.ps1
#
# Thứ tự quan trọng: GIẾT GIÁM SÁT TRƯỚC. Giết runtime trước thì giám sát thấy
# con chết và lập tức dựng con mới — trông như lệnh dừng không có tác dụng.

$GOC = Split-Path -Parent $PSScriptRoot
$tt  = Join-Path $PSScriptRoot "trang-thai.json"

Write-Host "`n=== Dừng Tử Cấm Thành ===`n"

if (Test-Path $tt) {
  $s = Get-Content $tt -Raw | ConvertFrom-Json
  foreach ($p in @($s.giamSatPid, $s.conPid)) {
    if (-not $p) { continue }
    $pr = Get-Process -Id $p -ErrorAction SilentlyContinue
    if ($pr) {
      Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
      Write-Host "  OK   đã dừng pid $p ($($pr.ProcessName))"
    }
  }
}

# Quét lần cuối theo cổng: giám sát có thể đã bị giết trước đó mà bỏ lại con
# mồ côi, và một tiến trình mồ côi giữ cổng sẽ chặn lần bật kế tiếp — im lặng.
$cong = (Get-Content "$GOC\config.json" -Raw | ConvertFrom-Json).port
$conn = Get-NetTCPConnection -LocalPort $cong -State Listen -ErrorAction SilentlyContinue
foreach ($c in $conn) {
  Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
  Write-Host "  OK   đã dừng tiến trình còn giữ cổng $cong (pid $($c.OwningProcess))"
}

Start-Sleep -Milliseconds 600
$con = Get-NetTCPConnection -LocalPort $cong -State Listen -ErrorAction SilentlyContinue
if ($con) { Write-Host "  ⚠    cổng $cong vẫn còn bị giữ" }
else      { Write-Host "  OK   cổng $cong đã nhả`n`n  Bật lại: powershell -File dichvu\bat.ps1`n" }
