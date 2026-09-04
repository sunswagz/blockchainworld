# Cài lối tắt + (tuỳ chọn) tự chạy khi đăng nhập.
#
#     powershell -ExecutionPolicy Bypass -File dichvu\cai-dat.ps1
#
# ⚠ FILE .ps1 Ở ĐÂY PHẢI LƯU UTF-8 **CÓ BOM**.
#   Windows PowerShell 5.1 đọc .ps1 không BOM theo bảng mã ANSI, nên chữ tiếng
#   Việt vỡ và script không parse nổi — lỗi báo ra là "Unexpected token" ở một
#   dòng chẳng liên quan gì. Sửa bằng trình soạn thảo nào lưu không BOM là hỏng
#   lại. Cùng bẫy đã ghi ở tu-cam-thanh-runtime/dichvu/.

# ⚠ `param` PHẢI là câu lệnh ĐẦU TIÊN của script (chỉ chú thích được
#   đứng trước). Đặt nó sau một lệnh nào đó thì PowerShell không coi
#   đây là khai tham số nữa mà coi `param` là tên một LỆNH — và với
#   `ErrorActionPreference = "Stop"` ở trên, script CHẾT ngay tại
#   dòng ấy. Bản trước để nó ở dòng 31: `cai-dat.ps1 -TuChay` chưa
#   bao giờ chạy, nên cung này không có móc tự khởi động và đã nằm
#   chết hai ngày (03–05/09/2026) mà không ai hay.
param([switch]$TuChay)

$ErrorActionPreference = "Stop"
$GOC = Split-Path -Parent $PSScriptRoot

function Ok($m)   { Write-Host "  OK   $m" }
function Nhac($m) { Write-Host "  ~    $m" }

# ── Vì sao KHÔNG dùng Task Scheduler ──────────────────────────────────────
# Trên máy này dịch vụ Task Scheduler đang tắt (Status Stopped dù StartType
# Automatic) và bật lại cần quyền quản trị. Nó cũng không nói vậy: `schtasks`
# kêu "network address is invalid", cmdlet kêu "task XML contains an unexpected
# node" — cả hai nghe như lỗi cú pháp. Đã ghi ở tu-cam-thanh-runtime/dichvu/.
#
# Nên tự chạy = một lối tắt trong thư mục Startup. Thô sơ, và nó hoạt động.
#
# ── Vì sao tự chạy phải là TUỲ CHỌN ───────────────────────────────────────
# Trên máy nhiều người qua lại, một cỗ máy giao dịch tự khởi động là thứ
# không ai xin phép. Người ngồi vào máy sau không biết nó đang chạy.
# Mặc định chỉ tạo lối tắt ngoài Desktop; muốn tự chạy thì truyền -TuChay.

$W = New-Object -ComObject WScript.Shell

function Tao-LoiTat($duong, $ten) {
  $lnk = $W.CreateShortcut((Join-Path $duong $ten))
  $lnk.TargetPath = "powershell.exe"
  $lnk.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$(Join-Path $PSScriptRoot 'bat.ps1')`""
  $lnk.WorkingDirectory = $GOC
  $lnk.Description = "Khâm Thiên Giám — đài chiêm thị trường tiên đoán"
  $lnk.Save()
}

Tao-LoiTat ([Environment]::GetFolderPath("Desktop")) "Khâm Thiên Giám.lnk"
Ok "đã tạo lối tắt ngoài Desktop"

if ($TuChay) {
  Tao-LoiTat ([Environment]::GetFolderPath("Startup")) "Khâm Thiên Giám.lnk"
  Ok "đã bật TỰ CHẠY khi đăng nhập"
  Nhac "gỡ: xoá lối tắt trong thư mục Startup (shell:startup)"
} else {
  Nhac "chưa bật tự chạy. Muốn bật: cai-dat.ps1 -TuChay"
}
