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

# Tìm lối tắt ở cả Desktop lẫn thư mục cha của runtime: `cai-dat.ps1` cho phép
# đặt nó ở đâu tuỳ ý (-ThuMucLoiTat), nên chỉ dọn mỗi Desktop là bỏ sót.
$GOC_RT = Split-Path -Parent $PSScriptRoot
foreach ($noi in @([Environment]::GetFolderPath("Desktop"),
                   (Split-Path -Parent $GOC_RT))) {
  $lnk = Join-Path $noi "Tử Cấm Thành.lnk"
  if (Test-Path $lnk) { Remove-Item $lnk -Force; Write-Host "  OK   đã xoá lối tắt: $lnk" }
}

Write-Host @"

  Đã gỡ. Dữ liệu vẫn còn nguyên: .env, data/, nhật ký.

  Chạy tay như trước:  python run.py
  Cài lại:             powershell -File dichvu\cai-dat.ps1

"@
