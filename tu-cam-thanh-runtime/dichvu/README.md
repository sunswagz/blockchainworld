# Chạy nền

Cài một lần để có lối tắt ngoài desktop. **Bấm vào thì runtime mới chạy** —
không tự bật khi khởi động máy.

```powershell
powershell -ExecutionPolicy Bypass -File dichvu\cai-dat.ps1
```

| Lệnh | Việc |
|---|---|
| `dichvu\cai-dat.ps1` | cài: tạo lối tắt desktop, chạy thử một lượt |
| `dichvu\trang-thai.ps1` | đang thế nào, kèm 12 dòng nhật ký cuối |
| `dichvu\dung.ps1` | dừng |
| `dichvu\bat.ps1` | bật lại |
| `dichvu\go-cai.ps1` | gỡ (KHÔNG đụng `.env`, `data/`, nhật ký) |
| `dichvu\kiem-giam-sat.py` | kiểm bộ giám sát |
| `dichvu\kiem-tu-chay.py` | kiểm công tắc tự chạy |

Lối tắt **Tử Cấm Thành** ngoài desktop mở buồng lái, và tự bật runtime nếu nó
chưa chạy — bấm một lần là ra, không cần biết nó đang bật hay tắt.

## Tự chạy lúc đăng nhập: mặc định TẮT

Công tắc nằm **trong buồng lái**: *Hệ thống → Tự chạy khi đăng nhập*.

Mặc định tắt là có chủ ý. Trên một máy nhiều người qua lại, một cỗ máy đặt lệnh
tự khởi động là thứ không ai xin phép — người ngồi vào máy sau không biết nó
đang chạy, cũng không biết nó đang giữ vị thế nào.

Công tắc để trong app chứ không để trong script cài đặt vì đây là lựa chọn theo
**từng máy** và người ta sẽ đổi ý nhiều lần: máy chung thì tắt, máy riêng thì
bật. Bắt mở terminal mỗi lần đổi là bắt sai chỗ.

Trên VPS thì **đừng dùng công tắc này** — Linux tự chạy bằng `systemd`, và nó
khởi động theo *máy* chứ không theo *phiên đăng nhập*, đúng thứ một con bot chạy
24/7 cần. `trang_thai()` trả `coThe=False` kèm lời giải thích thay vì giấu nút
đi, để người dùng trên VPS biết vì sao nó không bấm được.

## Cách nó chạy

```
Desktop\Tử Cấm Thành.lnk  ─ hoặc ─  Startup\... (nếu bật tự chạy)
    └── pythonw.exe dichvu\chay-nen.py        ← bộ giám sát, không cửa sổ
            └── python.exe run.py             ← runtime thật
                    stdout ──► data\nhat-ky\runtime.log   (xoay vòng, 5 MB × 5)
```

## Tắt hẳn

Nút **Tắt hẳn runtime** ở phòng Hệ thống. Đóng trình duyệt *không* tắt bot —
nó chạy ngầm, không cửa sổ nào.

Nút này đặt một file cờ `dichvu/dung-lai` **trước khi** tiến trình thoát. Không
có cờ đó thì nó vô dụng: bộ giám sát thấy con chết và dựng lại ngay sau vài
giây — đúng việc của nó — nên người dùng sẽ thấy như nút không có tác dụng.
Giám sát xoá cờ khi đọc xong, và cũng xoá lúc khởi động, vì một cờ sót lại từ
lượt trước sẽ làm lượt sau vừa lên đã tự tắt.

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

## Bản đang chạy nằm ở đâu

Runtime **chạy được ở bất cứ đâu** — nó không cần nằm trong repo. Cách bố trí
đang dùng:

```
D:\SUNSWaGz 2027\tu-cam-thanh-runtime\          ← BẢN ĐANG CHẠY
    .env, data/, config.json  (chỉ có ở đây)        lối tắt desktop trỏ vào đây

<repo>\tu-cam-thanh-runtime\                     ← MÃ NGUỒN
    không có .env, không có data/                   git quản, `git pull` cập nhật
```

Tách vậy vì hai thứ có vòng đời khác nhau: mã thì versioned và thay đổi liên
tục; khoá với lịch sử giao dịch thì **không được** nằm trong git và không được
mất. Bản chạy vẫn ghi ảnh chụp ngược về cung tĩnh trong repo qua `cungTinh`.

Đổi lại: `git pull` không với tới bản đang chạy. Sửa mã xong phải đẩy sang:

```powershell
powershell -ExecutionPolicy Bypass -File dichvu\cap-nhat.ps1 -Den "D:\SUNSWaGz 2027\tu-cam-thanh-runtime" -Thu   # xem trước
powershell -ExecutionPolicy Bypass -File dichvu\cap-nhat.ps1 -Den "D:\SUNSWaGz 2027\tu-cam-thanh-runtime"
```

`cap-nhat.ps1` chỉ chép **mã** và không bao giờ đụng `.env`, `data/`,
`config.json`. Danh sách thứ được chép là **tường minh**, không phải "chép tất
rồi trừ ra": quên thêm một thư mục mới thì nó không được đẩy — dễ nhận ra ngay.
Còn quên *trừ* thì nó đè mất dữ liệu, và không lấy lại được.

## Chuyển sang chỗ khác

```powershell
powershell -ExecutionPolicy Bypass -File dichvu\chuyen-nha.ps1 -Den "D:\Chỗ\Khác\tct"
powershell -ExecutionPolicy Bypass -File dichvu\chuyen-nha.ps1 -Den "..." -An   # kèm ẩn thư mục
```

**Lưu ý khi chuyển từ trong repo ra:** Windows từ chối chuyển một thư mục nếu
có *bất kỳ* tiến trình nào đang "đứng trong" đó — kể cả một cửa sổ terminal đã
`cd` vào, hay VS Code đang mở thư mục. Lỗi báo ra là `Access to the path is
denied` hoặc `the item is in use`, không hề nhắc tới thủ phạm. Nếu vướng, cách
chắc ăn là **chép rồi xoá nguồn** thay vì chuyển.

Kéo thả bằng tay cũng được, nhưng ba sợi dây sẽ đứt **âm thầm**:

1. **Lối tắt** giữ đường dẫn tuyệt đối → bấm không có phản ứng gì.
2. **Ảnh chụp gửi sang cung tĩnh** tìm theo thư mục anh em → ra khỏi repo là
   không thấy cung. Đặt `cungTinh` trong `config.json` để trỏ lại.
3. **Git** coi thư mục cũ là đã xoá → commit sau đó xoá runtime khỏi repo thật.

Script lo cả ba, kèm dừng runtime trước và chạy lại sau.

### Ba cái bẫy khi viết script này

**Không thể chuyển thư mục chứa chính script đang chạy.** PowerShell giữ file
`.ps1` ở trạng thái mở, và tiến trình cha vẫn sống trong lúc chờ tiến trình con.
Nên script tự sao sang `%TEMP%`, chạy **rời hẳn** (`Start-Process`, không chờ),
rồi cha thoát ngay để nhả khoá.

**`Push-Location` vào thư mục sắp chuyển là tự khoá nó.** Đây là chỗ tốn công
nhất: `Move-Item` báo *"the item is in use"* dù không tiến trình nào của mình
còn mở file nào, nên nhìn vào cứ tưởng Defender giữ. Thủ phạm là chính script —
nó `Push-Location $GOC` để chạy `git rev-parse`. Dùng `git -C` thay thế.

**Chuỗi thay thế của `-replace` không coi `\` là ký tự escape.** `'\\\\'` đẻ ra
bốn gạch chéo chứ không phải hai, làm `cungTinh` thành `C:\\Users\\...`. Windows
lại chấp nhận dấu phân cách lặp nên nó *chạy đúng một cách tình cờ* — kiểu sai
tệ nhất. Để `ConvertTo-Json` lo việc escape.

## Muốn giấu nó đi

Cờ `-An` đặt thuộc tính ẩn cho thư mục. Nhưng nói thẳng: **ẩn không phải bảo
mật.** Bật "hiện file ẩn" trong Explorer là thấy ngay.

Và thứ dễ thấy nhất không phải thư mục mà là **lối tắt ngoài desktop** — đổi tên
hoặc xoá nó (`dichvu\go-cai.ps1`) rồi mở buồng lái bằng bookmark trình duyệt.

Quan trọng hơn cả hai: **buồng lái không có mật khẩu.** Nó nghe ở `127.0.0.1`,
mà trên Windows mọi phiên đăng nhập trên cùng máy đều với tới được `127.0.0.1`.
Ai ngồi vào máy này, mở `localhost:5182` là bấm được nút đặt lệnh. Giấu thư mục
không giải quyết chuyện đó — nếu bạn thật sự lo người khác dùng máy thì cần một
lớp khoá ở buồng lái, không phải một thư mục ẩn.

## Còn thiếu gì so với một dịch vụ thật

Kể cả khi bật tự chạy, nó chạy lúc **đăng nhập** chứ không phải lúc **khởi động
máy** — máy bật mà chưa ai đăng nhập thì runtime chưa lên. Muốn sớm hơn thì cần
một dịch vụ Windows thật (`sc.exe` hoặc NSSM) và quyền quản trị.

Và nó vẫn tắt khi máy ngủ hoặc mất điện. Với một con bot đang giữ vị thế, đó là
lý do thật để chuyển lên VPS chứ không phải chuyện tiện lợi — xem mục "Mốc sau"
ở README chính.
