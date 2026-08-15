# Chạy nền

Cài một lần, sau đó bật máy là runtime tự chạy. Không cần mở terminal nữa.

```powershell
powershell -ExecutionPolicy Bypass -File dichvu\cai-dat.ps1
```

| Lệnh | Việc |
|---|---|
| `dichvu\cai-dat.ps1` | cài: tự chạy lúc đăng nhập + lối tắt desktop |
| `dichvu\trang-thai.ps1` | đang thế nào, kèm 12 dòng nhật ký cuối |
| `dichvu\dung.ps1` | dừng |
| `dichvu\bat.ps1` | bật lại |
| `dichvu\go-cai.ps1` | gỡ (KHÔNG đụng `.env`, `data/`, nhật ký) |
| `dichvu\kiem-giam-sat.py` | kiểm bộ giám sát |

Lối tắt **Tử Cấm Thành** ngoài desktop mở buồng lái, và tự bật dịch vụ nếu nó
chưa chạy — bấm một lần là ra, không cần biết nó đang bật hay tắt.

## Cách nó chạy

```
Startup\Tu Cam Thanh - runtime.lnk
    └── pythonw.exe dichvu\chay-nen.py        ← bộ giám sát, không cửa sổ
            └── python.exe run.py             ← runtime thật
                    stdout ──► data\nhat-ky\runtime.log   (xoay vòng, 5 MB × 5)
```

Bộ giám sát trông chừng runtime và dựng lại khi nó chết. Ba luật của nó:

- **Một bản một lúc.** Cổng đã bận thì thoát ngay, không dựng bản thứ hai —
  hai vòng lặp cùng đặt lệnh trên một tài khoản là hỏng nặng.
- **Nghỉ tăng dần.** Chết nhanh (dưới 30 giây) thì giãn 5→10→30→60→120→300 giây.
- **Biết bỏ cuộc.** Chết nhanh 10 lần liên tiếp thì dừng hẳn và ghi rõ lý do.
  Cấu hình sai mà cứ dựng lại là quay tít: ăn CPU, nện API sàn hàng nghìn lượt
  một phút, suốt đêm, và không báo cho ai cả.

`kiem-giam-sat.py` gác cả ba luật này bằng cách chạy chính bộ giám sát thật trên
một thư mục giả có `run.py` chết ngay.

## Bốn cái bẫy đã dẫm phải, ghi lại để khỏi dẫm lần nữa

**1. Task Scheduler không dùng được trên máy này.** Bản đầu tôi đăng ký một tác
vụ lịch. `schtasks` trả `ERROR: The network address is invalid.`, cmdlet trả
`The task XML contains an unexpected node.` — cả hai nghe như lỗi cú pháp. Sự
thật: **dịch vụ Task Scheduler đang tắt** (`Stopped` dù `StartType Automatic`),
bật lại cần quyền quản trị. Thư mục Startup làm đúng việc cần mà không cần admin.

**2. `.ps1` có tiếng Việt phải lưu UTF-8 CÓ BOM.** PowerShell 5.1 đọc `.ps1`
không BOM theo bảng mã ANSI ⇒ chữ vỡ ⇒ script không parse nổi, báo
`Unexpected token` ở một dòng chẳng liên quan. Kiểm:

```powershell
$e = $null
[System.Management.Automation.Language.Parser]::ParseFile($f, [ref]$null, [ref]$e); $e
```

**3. COM `WScript.Shell` không tạo được file có tên tiếng Việt.** Nó ép đường
dẫn về ANSI, `Tử Cấm Thành.lnk` thành `T? C?m Thành.lnk`, rồi `Save()` ném
`FileNotFoundException` — nghe như thiếu thư mục, không nhắc gì tới bảng mã.
Cách đi vòng: tạo bằng tên ASCII rồi `Rename-Item` (đi qua .NET, Unicode đủ).

**4. Chạy nền làm lộ một lỗi có sẵn ở Risk Engine.** Lúc khởi động, `peakEquity`
nạp từ đĩa trong khi số dư sàn chưa về nên `equity` còn 0 ⇒ ngắt mạch tính
drawdown 100% rồi **chốt cứng kill switch**. Số dư về sau vài giây, drawdown
thật 0%, nhưng chốt không tự mở — bot đứng im vĩnh viễn với dòng chữ không khớp
con số nào trên màn hình. Chạy tay thì hoạ hoằn mới gặp; tự chạy lúc đăng nhập
thì **lặp lại mỗi lần bật máy**. Đã sửa: `equityKnown` tách "chưa đọc được vốn"
khỏi "mất sạch vốn", và `selftest.py` mục [8] gác nó.

## Nhật ký

`data\nhat-ky\runtime.log` — 5 MB một file, giữ 5 file. stdout của runtime đi
qua bộ giám sát rồi mới xuống đĩa, nên nó xoay vòng liên tục chứ không chỉ xoay
lúc khởi động lại.

## Còn thiếu gì so với một dịch vụ thật

Chạy lúc **đăng nhập**, không phải lúc **khởi động máy** — máy bật mà chưa đăng
nhập thì runtime chưa chạy. Muốn sớm hơn thì cần dịch vụ Windows thật (`sc.exe`
hoặc NSSM) và quyền quản trị.

Và nó vẫn tắt khi máy ngủ hoặc mất điện. Với một con bot đang giữ vị thế, đó là
lý do thật để chuyển lên VPS chứ không phải chuyện tiện lợi — xem mục "Mốc sau"
ở README chính.
