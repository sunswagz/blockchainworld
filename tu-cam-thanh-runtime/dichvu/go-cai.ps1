# Gỡ Tử Cấm Thành khỏi chế độ chạy nền.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\go-cai.ps1
#
# Chỉ gỡ tác vụ và lối tắt. KHÔNG đụng vào .env, data/, hay nhật ký — gỡ dịch
# vụ là chuyện khác hẳn với xoá lịch sử giao dịch, và một script "dọn sạch" thì
# không có nút hoàn tác.

$KHOI_DONG = Join-Path ([Environment]::GetFolderPath("Startup")) "Tu Cam Thanh - runtime.lnk"

Write-Host "`n=== Gỡ Tử Cấm Thành khỏi chạy nền ===`n"

& (Join-Path $PSScriptRoot "dung.ps1") | Out-Null
Write-Host "  OK   đã dừng"

if (Test-Path $KHOI_DONG) {
  Remove-Item $KHOI_DONG -Force
  Write-Host "  OK   đã xoá lối tắt tự chạy lúc đăng nhập"
} else { Write-Host "  —    lối tắt tự chạy chưa có" }

$lnk = Join-Path ([Environment]::GetFolderPath("Desktop")) "Tử Cấm Thành.lnk"
if (Test-Path $lnk) { Remove-Item $lnk -Force; Write-Host "  OK   đã xoá lối tắt desktop" }

Write-Host @"

  Đã gỡ. Dữ liệu vẫn còn nguyên: .env, data/, nhật ký.

  Chạy tay như trước:  python run.py
  Cài lại:             powershell -File dichvu\cai-dat.ps1

"@
