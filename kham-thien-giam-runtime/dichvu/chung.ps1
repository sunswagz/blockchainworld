# MỘT chỗ duy nhất trả lời "Khâm Thiên Giám có đang chạy không".
#
#   . (Join-Path $PSScriptRoot "chung.ps1")
#
# ⚠ FILE .ps1 Ở ĐÂY PHẢI LƯU UTF-8 **CÓ BOM**. Xem ghi chú ở bat.ps1.
#
# ## Vì sao không tin pid.txt nữa
#
# Ba script từng có ba bản sao của cùng một hàm `Lay-Pid`, và cả ba đều
# hỏng theo cùng một kiểu. Đo được thật vào 30/08/2026:
#
#   · pid.txt ghi 58356 — tiến trình ấy đã chết từ hôm trước
#   · cổng 5186 đang được pid 4152 giữ, runtime SỐNG và khoẻ
#   · `trang-thai.ps1` in "KHÔNG chạy" — rồi XOÁ LUÔN pid.txt
#
# Ba cái sai nằm chồng lên nhau:
#
# 1. Câu hỏi CHỈ ĐỌC lại đi SỬA trạng thái. Hỏi "nó có chạy không" mà
#    xoá mất cái tay nắm duy nhất của `dung.ps1` — sau câu hỏi ấy thì
#    không còn cách nào dừng runtime cho tử tế nữa.
#
# 2. pid.txt bị coi là CĂN CƯỚC. Windows dùng lại số PID. Một pid cũ
#    rơi vào tay tiến trình khác thì `dung.ps1` giết nhầm người vô can,
#    bằng `Stop-Process -Force`, không hỏi một câu.
#
# 3. Cổng cửa "đã chạy rồi thì thôi" của `bat.ps1` cũng đọc pid.txt.
#    Không có file ⇒ nó dựng runtime THỨ HAI ghi chung một quyển sổ.
#    Hai người cùng ghi một sổ là hỏng sổ.
#
# Nay: **CỔNG là sự thật.** Ai giữ cổng, người đó là runtime. pid.txt
# tụt xuống hàng gợi ý, và không bao giờ được dùng một mình để giết.

$PID_FILE = Join-Path $PSScriptRoot "pid.txt"

function Doc-Cong {
  # Đọc cổng từ config.json chứ không chép số 5186 vào đây. Chép số là
  # tự hẹn một ngày đổi cổng rồi quên mất chỗ này.
  $goc = Split-Path -Parent $PSScriptRoot
  $f = Join-Path $goc "config.json"
  if (Test-Path $f) {
    try {
      $c = (Get-Content $f -Raw -Encoding UTF8) | ConvertFrom-Json
      if ($c.port) { return [int]$c.port }
    } catch { }
  }
  return 5186
}

function Ai-Giu-Cong {
  param([int]$Cong)
  # Get-NetTCPConnection có từ Windows 8. Vẫn bọc try: máy nào thiếu thì
  # lùi về netstat chứ không được ném lỗi rồi làm cả script chết.
  $id = $null
  try {
    $c = @(Get-NetTCPConnection -LocalPort $Cong -State Listen -ErrorAction Stop)
    if ($c.Count -gt 0) { $id = $c[0].OwningProcess }
  } catch {
    $d = netstat -ano -p TCP | Select-String ":$Cong\s" | Select-String "LISTENING"
    if ($d) { $id = ($d[0].ToString() -split "\s+")[-1] }
  }
  if (-not $id) { return $null }
  return (Get-Process -Id $id -ErrorAction SilentlyContinue)
}

function Lay-Runtime {
  # Trả tiến trình runtime đang sống, hoặc $null. KHÔNG sửa gì hết —
  # hàm này được gọi từ đường CHỈ ĐỌC.
  return (Ai-Giu-Cong -Cong (Doc-Cong))
}

function Doc-Pid-File {
  if (-not (Test-Path $PID_FILE)) { return $null }
  $p = (Get-Content $PID_FILE -Raw).Trim()
  if (-not $p) { return $null }
  return [int]$p
}

function Xac-Tien-Trinh-Lac {
  # Những tiến trình pythonw chạy chay-nen.py / run.py của CHÍNH thư mục
  # này mà KHÔNG giữ cổng. Chúng là xác treo: đã có một cái nằm đó 28
  # tiếng với đúng 1 luồng và 5 MB, chẳng làm gì, chỉ làm rối người đọc.
  $goc = Split-Path -Parent $PSScriptRoot
  $chu = Lay-Runtime
  $idChu = -1
  if ($chu) { $idChu = $chu.Id }
  $ra = @()
  try {
    $ds = Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" -ErrorAction Stop
  } catch { return $ra }
  foreach ($x in $ds) {
    if ($x.ProcessId -eq $idChu) { continue }
    $cl = $x.CommandLine
    if (-not $cl) { continue }
    $la = ($cl -like "*chay-nen.py*") -or ($cl -like "*run.py*")
    if (-not $la) { continue }
    # `pythonw run.py` KHÔNG mang đường dẫn gốc trong chuỗi lệnh. Chỉ
    # kể tên khi chuỗi lệnh CHỨA thư mục gốc — xác minh được thì mới
    # nói. Thà sót một xác treo còn hơn kể tên nhầm tiến trình của
    # người khác rồi mời người dùng đi giết nó.
    if ($cl -like "*$goc*") { $ra += $x.ProcessId }
  }
  return $ra
}

