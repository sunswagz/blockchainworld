# Thị Bạc Ty — runtime chênh lệch funding

Ty coi việc buôn bán giữa các cảng: xét hàng, thu thuế, và **đối chiếu giá
giữa các cảng** với nhau. Runtime này làm đúng việc ấy trên hợp đồng vĩnh cửu.

    PERPETUAL FUTURES
            │
            └── FUNDING SPREAD
                     ├─ Hyperliquid
                     ├─ Binance
                     ├─ OKX
                     └─ Bybit

Cùng một tài sản, cùng một lúc, mỗi sàn trả một mức funding khác nhau. LONG
nơi thấp, SHORT nơi cao, delta ≈ 0, thu chênh lệch. Không đoán giá lên xuống.

**Chỉ đọc dữ liệu CÔNG KHAI. Không đặt lệnh nào. Lớp đặt lệnh chưa được viết.**

## Chạy

```powershell
$py = "D:\SUNSWaGz 2027\Python 3.12.10\python.exe"
& $py -m pip install -r requirements.txt

& $py run.py                   # buồng lái ở http://localhost:5188
& $py -m bac.snapshot          # quét một lượt, ghi lát cắt, rồi thoát
& $py scripts/selftest.py      # 143 phép kiểm số học, KHÔNG cần mạng
& $py scripts/sinh-icon.py     # vẽ lại 5 icon cho cung tĩnh
```

| lệnh | làm gì |
|---|---|
| `python run.py` | vòng lặp nền + buồng lái, ghi sổ mỗi lượt |
| `python -m bac.snapshot` | một lượt rồi ghi `thi-bac-ty/assets/js/v/cang-phi.js` |
| `python scripts/selftest.py` | toán, không mạng, không chạm sổ thật |
| `pythonw dichvu/chay-nen.py` | chạy nền 24/7, log xoay vòng, ghi PID |
| `dichvu\bat.ps1` · `dung.ps1` · `trang-thai.ps1` | bật / tắt / xem bản chạy nền |

Buồng lái **chỉ sống ở localhost** và không bao giờ lên site. Cung tĩnh
`thi-bac-ty/` (cổng 5187) là thứ lên GitHub Pages — nó **quan sát**, runtime
**điều khiển**. Đó là hai giao diện khác nhau, cố ý.

## Hai phép tính, và vì sao lẫn chúng là mất tiền

### 1 · Chuẩn hoá — để SO SÁNH hai cảng

Mỗi cảng kết toán theo một chu kỳ riêng, và OKX còn đổi chu kỳ được giữa
chừng (8h → 4h → 2h → 1h tuỳ điều kiện thị trường). Con số sàn công bố mà
không kèm chu kỳ là một con số vô nghĩa:

```
Binance      +0,080% / 8 giờ   →  0,010% / giờ
Hyperliquid  +0,015% / 1 giờ   →  0,015% / giờ   ← cao hơn
```

Nhìn số thô thì Binance lớn gấp năm. Sau chuẩn hoá thì ngược lại. Đây là lỗi
một scanner sơ sài mắc ngay ở dòng đầu, và nó **không hề giống lỗi** — mọi
con số vẫn hợp lệ, chỉ bảng xếp hạng là sai thứ tự.

### 2 · Đếm mốc — để biết GIỮ NGẦN ẤY THÌ THU BAO NHIÊU

Chuẩn hoá xong vẫn **chưa được nhân với số giờ giữ**. Funding không chảy liên
tục; nó là một khoản trả **tại một mốc**. Sàn kết toán 8 giờ trả vào 00:00,
08:00, 16:00 UTC — không trả gì vào 03:47.

```
Vào 00:05, thoát 04:05 — giữ 4 giờ, funding 0,01%/8h
  nhân theo giờ:  0,01% × (4/8) = 0,005%      ← nghe hợp lý
  đếm theo mốc:   0,000%                      ← chưa qua mốc nào

Vào 07:55, thoát 08:05 — giữ 10 PHÚT
  đếm theo mốc:   0,010%                      ← thu trọn một chu kỳ
```

Cùng một cặp sàn, cùng một mức funding, hai câu trả lời lệch nhau vô hạn lần.
`bac/dongho.py` làm phép thứ hai; `moi_gio()` chỉ dùng cho phép thứ nhất, và
hai hàm ấy cố ý không gọi lẫn nhau.

### 3 · Rồi mới trừ

```
funding thực thu   (đếm theo mốc, hai chân đếm RIÊNG)
  − phí taker vào    × 2 chân
  − phí taker ra     × 2 chân
  − trượt giá        × 4 lần khớp
  ─────────────────────────────
  = NET EDGE
```

**Bốn khoản chưa trừ**, và phải biết là chưa: chi phí vay coin, phí chuyển
vốn giữa sàn, rủi ro basis khi hai mark rời nhau lúc thoát, và vốn bị khoá.
Nên NET ở đây là **chặn trên**, không phải lợi nhuận.

## Tám cửa rủi ro

`bac/rui_ro.py` là Python thuần, tất định, có quyền phủ quyết. Mỗi cửa nằm đó
vì một cách mất tiền cụ thể:

| cửa | chặn cái gì |
|---|---|
| `grossToiThieuBpsNgay` | chênh lệch quá mỏng, không đáng chạm vào |
| `netToiThieuBps` | phí ăn hết biên — càng làm càng lỗ |
| `doiHoiItNhatMotMoc` | **giữ hết cửa sổ mà không mốc nào rơi vào → thu = 0** |
| `lechMarkToiDaBps` | hai mark rời nhau → không còn delta-neutral |
| `doiHoiHaiMark` | thiếu mark một bên → *không biết* có lệch hay không |
| `tuoiToiDaGiay` | dữ liệu cũ → đang cược vào một thế giới đã qua |
| `nhanUocLuongMoc` | mốc phải đoán → sai số nằm ngoài tầm đo |
| `lechDongHoToiDaGiay` | **đồng hồ máy lệch giờ sàn** → mọi phép đếm mốc sai theo |

Cửa thứ ba và thứ bảy là hai cửa mà một scanner chỉ nhân `spread × giờ`
**không thể có** — nó không biết mốc nằm ở đâu.

Cửa thứ tám thêm vào sau khi đo được **đồng hồ máy chậm 6,94 phút** so với cả
ba sàn (21/08/2026). Nó hỏng theo hai đường, cả hai im lặng: phép đếm mốc so
giờ SÀN với giờ MÁY nên gần biên là lật hẳn kết quả; và `tuoi_giay()` kẹp hiệu
âm về 0, biến "dấu thời gian ở tương lai" thành "vừa mới tinh" — cửa
`tuoiToiDaGiay` đứng đó suốt mà không chặn nổi gì, kể cả khi cấy vào một báo
giá cũ 10 phút. Xem `bac/dong_ho.py`.

Gặp cơ hội bị chặn, buồng lái gom **đủ mọi lý do** chứ không dừng ở cái đầu.
Dừng sớm thì người vận hành nới một ngưỡng, chạy lại, gặp lý do thứ hai, nới
tiếp — và không bao giờ thấy bức tranh đầy đủ.

## Bốn cảng, bốn cách công bố khác nhau

| cảng | funding | chu kỳ lấy từ đâu | mark |
|---|---|---|---|
| Hyperliquid | `metaAndAssetCtxs` → `funding` | **1 giờ**, cố định | `markPx` |
| Binance | `premiumIndex` → `lastFundingRate` | `fundingInfo` (chỉ symbol đã điều chỉnh), mặc định 8h | `markPrice` |
| OKX | `funding-rate` → `fundingRate` | `nextFundingTime − fundingTime` | `mark-price` |
| Bybit | `tickers` → `fundingRate` | `instruments-info.fundingInterval`, **đơn vị PHÚT** | `markPrice` |

Ba cái bẫy đã gỡ, và cả ba đều hỏng im lặng:

- **Bybit trả chu kỳ bằng PHÚT.** Đọc 480 rồi coi là giờ thì funding/giờ nhỏ
  đi 60 lần, Bybit tụt xuống cuối mọi bảng và không bao giờ được ghép cặp.
  Không lỗi nào báo — chỉ là một cảng tự nhiên biến mất khỏi kết quả.
- **OKX ticker `last` không phải mark.** Bản đầu lấy `last` rồi so với
  `markPrice` của Binance: một bên là giá khớp cuối nhảy theo từng lệnh lẻ,
  bên kia là giá dùng để thanh lý. Độ lệch tính ra là hỗn hợp của lệch thật
  và tiếng ồn vi cấu trúc, rồi cửa `lechMarkToiDaBps` chặn nhầm hoặc thả nhầm
  theo.
- **Hyperliquid ghép meta với ctxs theo CHỈ SỐ.** Lệch một nấc là gán funding
  của SOL cho BTC — mọi con số vẫn hợp lệ. Dùng `zip(..., strict=True)` để nổ
  ngay lúc ghép thay vì lệch nhãn từ đó về sau.

Một cảng chết **không** kéo theo ba cảng còn sống: `Cang.bao_gia()` nuốt lỗi
vào `SucKhoe` rồi trả danh sách rỗng. Nhưng buồng lái hiện **MÙ MỘT MẮT** ở
dải trên cùng — vì bảng đủ ba cảng còn lại trông y hệt "thị trường không có
chênh lệch".

## Sổ quét ghi CẢ lượt trống

Một tuần không cơ hội nào là một **phát hiện** (chênh lệch đã đóng, hoặc phí
đã ăn hết biên), không phải một tuần không có dữ liệu. Sổ chỉ ghi lượt "có
hàng" sẽ dựng nên một lịch sử toàn ngày đẹp trời.

Từ đó tính được **độ dai** — thứ phân biệt hai chuỗi có cùng giá trị hiện tại:

```
30 → 21 → 12 → 3 → 0        chênh lệch đang tắt, vào là muộn
25 → 28 → 22 → 31 → 27      chênh lệch dai, đáng săn
```

`/api/do-dai` trả `tiLeDuong` — bao nhiêu phần lượt quét thấy NET còn dương.
NET 12 bps mà `tiLeDuong` 0,2 là một cú loé; NET 8 bps mà 0,9 thì đáng giá
hơn, dù con số nhỏ hơn.

## Chế độ và ba cửa

```
quan-sat   chỉ đo, không mở vị thế nào     ← mặc định
giay       cân trên số liệu thật, tiền giả
that       lệnh rời khỏi máy               ← CHƯA MỞ ĐƯỢC
```

Một lệnh thật cần **cả ba cửa cùng mở**, ở ba nơi khác nhau về bản chất:

1. `config.json` → `che: "that"`
2. `config.json` → `datLenh.toiXacNhanDaDocRuiRo: true`
3. `.env` → khoá API của ít nhất một sàn

Và một **cửa thứ tư không mở được bằng cấu hình**: lớp đặt lệnh chưa tồn tại.
`ly_do_khong_that()` in ra đúng cửa nào đang đóng, không rơi trong im lặng.

## Đào tạo — bốn tầng, và thứ tự phụ thuộc là bắt buộc

```
1. CHẠY NỀN     tích băng 24/7          dichvu/chay-nen.py
       ↓
2. BĂNG GHI     nguyên liệu thô         bac/bang.py
       ↓
3. CHẠY LẠI     đo funding THỰC NHẬN    bac/chay_lai.py
       ↓
4. CHẨN + TIẾN HOÁ   vặn ngưỡng có bằng chứng   bac/chan_doan.py · bac/tien_hoa.py
```

Không nhảy cóc được. Sổ ở `so.py` ghi **kết luận**; băng ghi **nguyên liệu**:

    sổ    "hôm qua ta đã quyết thế nào"
    băng  "nếu ngưỡng khác đi thì ta ĐÃ quyết thế nào"

Thiếu băng thì mọi lần vặn ngưỡng đều là đổi số cho vui.

### Chạy lại đo được thứ mà ảnh chụp không đo được

`thuBps` là DỰ ĐOÁN: giả định rate hiện tại giữ nguyên tới lúc kết toán.
`thuThucBps` là ĐO ĐƯỢC: tra ngược từ băng, tại TỪNG MỐC kết toán, lấy đúng
rate sàn công bố lúc ấy.

Khoảng cách giữa hai con số là **funding decay**, và nó là thứ đáng học nhất.
`chan_doan` gọi nó là `du-doan-lac-quan` khi lệch quá 2 bps trung bình — lúc
đó mô hình không xui, nó lạc quan có hệ thống.

**Ba chỗ xấp xỉ, và cả ba đều làm kết quả ĐẸP HƠN sự thật:** rate tại mốc lấy
từ khung gần nhất (không phải rate sàn thật sự áp); không mô phỏng khớp lệnh;
không mô phỏng vốn bị kẹt. Nên `netThucBps` là **chặn trên**.

### Bốn luật chặn bốn cách tự lừa

| luật | chặn gì |
|---|---|
| cửa AN TOÀN không nằm trong `NUT_VAN` | đường nhanh nhất tới điểm cao là **tắt đèn báo** — nó sẽ tìm ra ngay |
| phí không phải núm vặn | vặn phí xuống là tự vẽ ra lợi nhuận |
| một lượt vặn ĐÚNG MỘT núm | vặn hai núm rồi khá lên thì không biết núm nào có công |
| nhận chỉ khi ≥30 mẫu **và** cải thiện > 0,15 bps | không thì "tiến bộ" mỗi ngày mà tổng lại không đi đâu |

`doiHoiHaiMark`, `doiHoiItNhatMotMoc`, `nhanUocLuongMoc`,
`lechDongHoToiDaGiay` cố ý **không** vặn được. Chúng không phải ngưỡng hiệu
năng — chúng là câu "ta không biết đủ để vào lệnh".

### File `.ps1` PHẢI lưu UTF-8 CÓ BOM

Windows PowerShell 5.1 đọc `.ps1` không BOM theo bảng mã ANSI. Chữ tiếng Việt
vỡ, và ký tự nhiều byte nuốt luôn dấu nháy — lỗi báo ra là
`The string is missing the terminator` ở một dòng chẳng liên quan gì.

Đã cắn ngay lượt chạy đầu của `bat.ps1`. Cùng bẫy đã ghi sẵn ở hai runtime
kia; kiểm bằng:

```powershell
Get-ChildItem dichvu\*.ps1 | ForEach-Object {
  $b = [IO.File]::ReadAllBytes($_.FullName)[0..2]
  "{0}  {1}" -f $_.Name, (($b -join ',') -eq '239,187,191')
}
```

### Bao lâu mới có mẫu đầu tiên

Với nhịp 30 giây và cửa sổ giữ 8 giờ: băng phải phủ **hết** cửa sổ mới hậu
kiểm được một cơ hội. Một phiên chạy tay vài chục phút sinh ra **đúng 0 mẫu**
— bảng vẫn xanh, sổ tiến hoá ghi "chưa đủ mẫu", và không có gì sai cả; chỉ là
chưa có gì để học. Đó là lý do `dichvu/chay-nen.py` tồn tại.

    POST /api/chay-lai                 chạy lại băng, tham số hiện tại
    POST /api/doi-chieu?nut=…&gtA=…&gtB=…   so hai giá trị trên CÙNG băng
    POST /api/tien-hoa?thu=true        xem sẽ vặn gì, không ghi gì
    GET  /api/duong-tien-hoa           sổ tiến hoá gộp
    GET  /api/bang                     băng có bao nhiêu khung, có lành không

Hoặc mở buồng lái, tab **Đào tạo**.

## Lộ trình — V0.6 là mốc duy nhất chạm tới tiền

| | xây gì | được làm gì |
|---|---|---|
| **V0.1** | quét công khai, chuẩn hoá, đếm mốc, 8 cửa, sổ SQLite | xong |
| **V0.2** | băng ghi · chạy lại · chẩn đoán · tiến hoá · chạy nền | ← **đang ở đây** |
| V0.3 | độ dai dài hạn (half-life, z-score, regime) | biết chênh lệch nào dai |
| V0.4 | sổ lệnh thật → trượt giá thật, không phải tham số | NET hết là ước lượng |
| V0.4 | sổ giấy 24/7 + phân bổ lãi lỗ theo nguồn | biết tiền đến từ đâu |
| V0.5 | testnet + **máy trạng thái hai chân** + kill switch | tập vào lệnh mà không mất gì |
| V0.6 | vốn thật rất nhỏ + đối soát vị thế từ SÀN | mốc đầu tiên chạm tiền |
| V0.7 | Capital Router — xếp hạng và phân bổ vốn | |

**Vì sao máy trạng thái hai chân đứng trước tiền thật.** Không được viết
kiểu này:

```python
short_binance()          # khớp
long_hyperliquid()       # TRƯỢT
```

Giữa hai dòng ấy, BTC giảm 1%. Vị thế đang từ delta-neutral thành **short
một chiều** — *legging risk*, và đó là cách mất tiền nhanh nhất trong nghề
này. Phải là một máy trạng thái có đường lùi:

```
CHỜ → DUYỆT → GIỮ VỐN → MỞ CHÂN A → MỞ CHÂN B → ĐÃ PHÒNG HỘ → GIỮ
                              │
                        chân B hỏng
                              │
                    ┌─────────┼─────────┐
                 thử lại   sàn khác   ĐÓNG GẤP
```

Không dòng nào trong đường ấy được để model quyết định.

## AI nằm ở đâu

**Không nằm trong vòng ký lệnh.** Bản V0.1 không gọi model lần nào.

Về sau, model chỉ được gọi **khi có bất thường** — không phải mỗi tick:

```
vòng lặp Python 24/7          gần như $0
        │
   ┌────┴────┐
BÌNH THƯỜNG  BẤT THƯỜNG
   │              │
không gọi     gọi MỘT lần
```

Và khi gọi thì quyền của nó là `QUAN SÁT · TRA CỨU · GIẢI THÍCH · ĐỀ XUẤT` —
không bao giờ `KÝ · RÚT · VƯỢT CỬA RỦI RO`.

## Bản đồ mã

```
bac/
  dongho.py     đếm mốc kết toán      ← lõi, đọc trước
  dong_ho.py    lệch đồng hồ máy/sàn  ← đọc ngay sau
  models.py     BaoGia · CoHoi
  can_loi.py    ghép cặp, trừ phí, ra NET
  rui_ro.py     bảy cửa, tất định, phủ quyết
  san/          bốn cảng + sổ sức khoẻ
  so.py         SQLite: mọi lượt quét, kể cả lượt trống
  vong.py       vòng lặp nền, hỏi bốn cảng SONG SONG
  server.py     buồng lái :5188
  snapshot.py   cầu nối sang cung tĩnh

  bang.py       băng ghi nguyên liệu  ← tầng đào tạo
  chay_lai.py   hậu kiểm funding thực
  chan_doan.py  bệnh đo được
  tien_hoa.py   vặn ngưỡng có bằng chứng
```

Hỏi bốn cảng **song song không phải để nhanh**: hỏi tuần tự cách nhau vài
trăm mili giây là bốn ảnh chụp ở bốn thời điểm, rồi đem so như thể cùng lúc.
Trong một cú biến động, mark của cảng hỏi trước và cảng hỏi sau lệch nhau chỉ
vì thứ tự hỏi.

## Câu treo trên tường

> **NET EDGE mới là alpha.** Funding thô thì không.
>
> **Funding trả theo MỐC.** Giữ 4 giờ trên sàn kết toán 8 giờ có thể thu được
> đúng bằng không.
>
> **Signal đúng ≠ trade có lãi.** Ở giữa hai thứ đó là phí, trượt giá, và một
> chân lệnh không khớp.
