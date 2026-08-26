<#
    sua-dong-ho.ps1 — bật lại đồng bộ giờ, và vì sao việc này thuộc runtime.

    PHẢI CHẠY BẰNG QUYỀN ADMIN. Chỉnh đồng hồ hệ thống cần đặc quyền
    SeSystemtimePrivilege; tài khoản thường không có, và lỗi báo ra là
    "A required privilege is not held by the client".

    ── Vì sao một script hệ thống lại nằm trong thư mục runtime ──────────

    Vì đồng hồ lệch KHÔNG phải chuyện vặt ở đây, nó là chuyện làm hỏng số:

      · Funding trả theo MỐC kết toán. Đếm mốc bằng giờ máy lệch 7 phút là
        đếm nhầm cả mốc — thu 0 mà tưởng thu đủ, hoặc ngược lại.
      · Cửa `lechDongHoToiDaGiay` của ty (10 giây) loại sạch mọi cơ hội.
      · Cầu dao Trung Ương (60 giây) NGẮT, nên không đồng nào được cấp.

    Ngày 26/08/2026 máy này lệch 447 giây và dịch vụ W32Time đang bị
    DISABLED — nên nó không tự sửa được, và sẽ trôi tiếp mãi.

    ── Chạy ─────────────────────────────────────────────────────────────

        chuột phải → Run with PowerShell (as Administrator)

    hoặc từ một cửa sổ PowerShell đã nâng quyền:

        powershell -ExecutionPolicy Bypass -File .\sua-dong-ho.ps1
#>

$ErrorActionPreference = "Stop"

function Nói($nhãn, $chữ) { Write-Host ("  {0,-5} {1}" -f $nhãn, $chữ) }

Write-Host ""
Write-Host "  ── SỬA ĐỒNG HỒ MÁY ──────────────────────────────────────────"

# ── 1. phải là admin, và nói thẳng nếu không ─────────────────────────────
$tôi = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $tôi.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Nói "LỖI" "script này PHẢI chạy bằng quyền Administrator."
    Nói ""    "chuột phải vào file → Run as administrator"
    exit 1
}

Nói "~" ("giờ máy trước khi sửa: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))

# ── 2. bật lại dịch vụ ───────────────────────────────────────────────────
# Disabled thì Start-Service ném lỗi chứ không tự bật — phải đổi StartupType
# trước. Đây đúng là chỗ máy này đang mắc.
$dv = Get-Service W32Time
Nói "~" ("W32Time: " + $dv.Status + " / " + $dv.StartType)

if ($dv.StartType -eq "Disabled") {
    Set-Service W32Time -StartupType Automatic
    Nói "OK" "đã đổi W32Time sang Automatic (trước đó bị DISABLED)"
}
if ((Get-Service W32Time).Status -ne "Running") {
    Start-Service W32Time
    Nói "OK" "đã bật W32Time"
}

# ── 3. chỉ đúng máy chủ giờ ──────────────────────────────────────────────
# `time.windows.com` mặc định hay không với tới được. pool.ntp.org có nhiều
# máy chủ hơn nên bền hơn; giữ cả hai để còn đường lui.
w32tm /config /manualpeerlist:"time.windows.com,0x8 pool.ntp.org,0x8 time.google.com,0x8" /syncfromflags:manual /reliable:no /update | Out-Null
Nói "OK" "đã đặt danh sách máy chủ giờ"

Restart-Service W32Time
Start-Sleep -Seconds 2

# ── 4. đồng bộ ───────────────────────────────────────────────────────────
# Lệch 7 phút vượt ngưỡng `MaxPosPhaseCorrection` mặc định của một số bản
# Windows, và khi vượt thì w32tm TỪ CHỐI sửa thay vì sửa — im lặng. Nên
# /force, và nên kiểm lại bằng mắt ở bước 5.
$kq = w32tm /resync /force 2>&1
Nói "~" ($kq -join " ")

if ($LASTEXITCODE -ne 0) {
    Nói "~" "resync chưa ăn — thử lại sau 5 giây (dịch vụ có thể chưa sẵn)"
    Start-Sleep -Seconds 5
    $kq = w32tm /resync /force 2>&1
    Nói "~" ($kq -join " ")
}

# ── 5. kiểm lại bằng mắt, đừng tin mã thoát ──────────────────────────────
Write-Host ""
Nói "OK" ("giờ máy sau khi sửa:  " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
w32tm /query /status 2>&1 | Select-Object -First 8 | ForEach-Object { Nói "" $_ }

Write-Host ""
Nói "~" "kiểm lại bằng chính runtime (nó đo với BỐN SÀN, không với NTP):"
Nói ""  '      cd ..'
Nói ""  '      py -m bac.snapshot        # rồi xem dòng lệch đồng hồ'
Nói ""
Nói ""  '  Dưới 1 giây là xong. Lý do ngắt "dong-ho-lech" khai tuMo=True nên'
Nói ""  '  cầu dao TỰ đóng lại ở vòng quét kế tiếp — không phải bấm gì.'
Nói ""  '  Dịch vụ nền đang chạy thì không cần khởi động lại.'
Write-Host ""
