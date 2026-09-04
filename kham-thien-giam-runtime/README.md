# Khâm Thiên Giám — runtime

Đài thiên văn nhà Nguyễn tính ra bầu trời **đáng lẽ** phải thế nào, rồi đem so
với điều người đời đang tin. Runtime này làm đúng việc ấy trên Polymarket.

> **KHÔNG lên site. KHÔNG vào workflow nào.**
> Cùng luật với `tu-cam-thanh-runtime/` — xem mục "Hai runtime Python là ngoại
> lệ" trong `CLAUDE.md` ở gốc repo.

## Chạy

Máy này có Python 3.12 cài portable, **ngoài PATH**:

```powershell
$py = "D:\SUNSWaGz 2027\Python 3.12.10\python.exe"

& $py -m pip install -r requirements.txt
& $py scripts\selftest.py      # 277 phép kiểm số học, KHÔNG cần mạng
& $py run.py                   # buồng lái → http://localhost:5186
```

Xem cung tĩnh (từ gốc repo): `node server.js 5185`

| lệnh | làm gì |
|---|---|
| `python run.py` | buồng lái + vòng lặp, chế độ theo `config.json` |
| `python run.py --che=quan-sat` | chỉ đo, không mở vị thế nào kể cả trên sổ giấy |
| `python -m kham.snapshot` | ghi một lát cắt ra cung tĩnh rồi thoát |
| `python scripts/selftest.py` | 1.759 phép kiểm số học, không cần mạng |
| `node scripts/kiem-giao-dien.mjs` | 10 phép kiểm giao diện: tương phản, z-index, ô trống |
| `python scripts/dung-ket-qua.py` | dựng lại KẾT QUẢ cho băng đã ghi — chỉ cần Binance |
| `python scripts/thu-nan-lai.py` | A/B phép nắn trên băng thật: thô so với đã nắn |
| `python scripts/sinh-icon.py` | sinh lại 5 icon PNG cho cung |
| `node scripts/kiem-buong-lai.mjs` | vẽ thật 11 ô buồng lái, KHÔNG cần mạng |
| `python -m kham.tien_hoa --thu` | xem vòng tiến hoá sẽ làm gì, không ghi gì |
| `python -m kham.tien_hoa` | chạy một lượt tiến hoá THẬT |
| `python scripts/chay-phat-lai.py --von=100000 --moi-nan=7` | PHIÊN GIẤY trọn vẹn trên băng thật: tiền ảo, kế toán thật |
| `python scripts/do-mot-nut.py --nut=... --ngay=20` | quét CẢ TRỤC một nút, tự đo lại trên cửa sổ gấp đôi |
| `python scripts/quet-dot-bien.py --file=kham/....py` | đổi từng toán tử so sánh, tìm chỗ phép kiểm không với tới |

## Phiên giấy — tiền ảo bao nhiêu tuỳ ý, kế toán thật

    python scripts/chay-phat-lai.py --von=100000 --moi-nan=7

Dữ liệu THẬT (sổ lệnh Polymarket đã ghi từng khung hình, giá nền Binance,
σ đo được lúc đó, kết quả từng cửa sổ dựng từ nến Binance), tiền ẢO, kế
toán như một hệ thật: giá vốn, phí, lãi lỗ từng cửa sổ, đường vốn, sụt
vốn đỉnh-đáy, và cầu dao rủi ro có quyền ngắt giữa chừng.

**`--moi-nan=N` không phải tuỳ chọn cho vui.** Không có nó, phiên khai
sinh với sổ hiệu chỉnh RỖNG, `du_de_dung_kelly()` trả False suốt phiên,
cỡ lệnh ghim ở lô sàn — và `--von` KHÔNG đổi một lệnh nào: $1.000 với
$100.000 cho đúng cùng một chuỗi lệnh. `--moi-nan=N` dựng sổ nắn từ N
ngày nến Binance TRƯỚC khung đầu của băng, đúng bằng thứ máy chạy thật
đã có sẵn. Mồi lấn sang tương lai của băng là nhìn trộm, nên phiên TỪ
CHỐI chạy nếu khung đầu nằm trước mốc cuối của mồi.

Đo được 30/08/2026 (152.729 khung, mồi 7 ngày):

| vốn | khớp | kết toán | lãi lỗ | phí | sụt vốn | lỗ nặng nhất |
|---|---|---|---|---|---|---|
| $5.000 | 38 | 12 | +8,01% | $38 | 0,00% | −$215 |
| $100.000 | 417 | 14 | +1,32% | $514 | 4,09% | −$3.341 |

Lợi suất GIẢM khi vốn tăng — lô to ăn sâu vào sổ và phí nhân lên. Đó là
SỨC CHỨA, và nó chỉ hiện ra khi cỡ lệnh thật sự theo vốn.

Cả hai khoảng tin đều CHỨA 0. Con số lãi ở trên **chưa nói được** rằng cỗ
máy này có lãi, và phiên tự in ra điều đó. Đọc nó như một CẬN TRÊN: phiên
giấy không có tác động thị trường, không có trượt giá theo thời gian,
không có chọn lọc bất lợi.

Mỗi lượt còn in ra **cửa rủi ro nào CHƯA CHẶN AI LẦN NÀO** — 30/08 là 3
trong 13, và mười cửa im lặng gần như là trọn phần giữ vốn. Một cửa không
bao giờ chạy thì không phân biệt được với một cửa hỏng.

## Sổ kết quả — mảnh khiến chạy lại chấm được điểm

Băng ghi khung hình lúc nó ĐANG diễn ra, nên không thể tự chứa kết quả:
với khung 5 phút thì kết quả mãi năm phút sau mới biết, và lúc đó dòng
băng đã nằm trong một file gzip đã đóng. Sửa ngược được thì cuốn băng
cũng không còn đáng tin.

Nên kết quả đi sổ RIÊNG (`data/ket-qua.jsonl`), nối với băng bằng `slug`.

Đo trước khi có sổ này: **5.854 bản ghi thị trường trong băng, 0 cái có
kết quả**. `chay_lai.mot_luot()` cần `upThang` để chấm, nên `soKhop` luôn
bằng 0 — cỗ máy chạy lại chưa từng chấm được một khung nào. Và cổng của
vòng tiến hoá thì dựa vào chính nó để phán một đề xuất là tốt hơn hay chỉ
khác đi.

Kết quả dựng lại được cho cả băng CŨ, chỉ cần Binance: `giaMo` băng đã
ghi, `giaDong` là nến 1 phút lúc khung kết thúc, và lúc kết thúc thì đọc
từ đuôi slug. Không cần Polymarket — nên toàn bộ băng ghi trong tuần vẫn
dùng được dù đường tới sàn đang đứt.

    python scripts/dung-ket-qua.py --thu     # đếm trước, không ghi
    python scripts/dung-ket-qua.py           # dựng thật

## Buồng lái — Đài Chỉ Huy trước, động cơ sau

Ô đầu tiên là **Đài Chỉ Huy**: một market một tấm, đọc từ trên xuống là
ra quyết định.

    còn bao lâu → đáng giá bao nhiêu → chợ hỏi bao nhiêu
    → ăn được bao nhiêu → đang mang gì → và VÌ VẬY nên làm gì

Mười ô còn lại mỗi ô là một động cơ. Đó là cách người **dựng** máy nghĩ;
người **vận hành** máy thì cần bảy dòng phía trên, và chỉ mở "Sâu hơn"
khi bảy dòng ấy nói điều gì lạ.

Dòng QUYẾT ĐỊNH không nghĩ hộ máy — nó đọc lại kết luận máy đã có (cầu
dao, cửa khung, sàng cơ hội) thành một câu. Nó mà nói khác các ô bên dưới
thì đó là lỗi của tấm hiển thị, không phải của máy.

### `kiem-buong-lai.mjs` — vì `node --check` không đủ

Loại lỗi đắt nhất của một trang như thế này **đúng cú pháp**: đọc một
trường không tồn tại rồi ném, và cả buồng lái trắng trang. Máy vẫn giao
dịch bình thường, chỉ người vận hành là mù.

Phép kiểm này dựng một DOM tối thiểu rồi gọi thật cả 11 hàm vẽ trên một
mẫu **dựng tay** (`scripts/mau-buong-lai.json`) — không cần mạng, không
cần runtime đang chạy. Mẫu là dựng tay chứ không phải ảnh chụp máy: ảnh
chụp chỉ có trạng thái tình cờ lúc chụp, còn mẫu tay giữ được đủ các
trường hợp khó và không đổi theo chợ.

Nó đã bắt bốn lỗi thật ngay lần chạy đầu, và một trong số đó là lỗi ở
chính cái mẫu — hợp đồng dữ liệu tôi nhớ sai so với hợp đồng thật.

## Chạy nền, và vòng tiến hoá mỗi ngày

```powershell
powershell -ExecutionPolicy Bypass -File dichvuat.ps1          # bật
powershell -ExecutionPolicy Bypass -File dichvu	rang-thai.ps1   # xem
powershell -ExecutionPolicy Bypass -File dichvu\dung.ps1         # dừng
powershell -ExecutionPolicy Bypass -File dichvu\cai-dat.ps1 -TuChay
```

Vòng tiến hoá chạy **trong chính runtime**, mỗi ngày UTC một lượt sau
`tienHoa.gioUTC`. Không dùng Task Scheduler: dịch vụ đó trên máy này đang
tắt và bật lại cần quyền quản trị.

Ba bẫy đã trả giá khi dựng bộ này, ghi lại để đừng lặp:

- **`.ps1` phải UTF-8 CÓ BOM.** PowerShell 5.1 đọc file không BOM theo ANSI
  → chữ tiếng Việt vỡ → "Unexpected token" ở một dòng chẳng liên quan.
- **`-ArgumentList` phải bọc dấu nháy.** Đường dẫn máy này có dấu cách
  (`SUNSWaGz 2027`), không bọc thì bị tách thành nhiều tham số và pythonw
  chết ngay, không kịp ghi dòng log nào — triệu chứng là "không lên" với
  nhật ký trống trơn.
- **`uvicorn.run(log_config=None)`.** Không có nó, uvicorn dựng lại logging
  và ném `Unable to configure formatter 'default'` — một câu không nhắc gì
  tới stdout, nên rất khó lần ra rằng nguyên nhân là lớp chuyển hướng
  nhật ký.

## Vòng tiến hoá — bảy bước, model chỉ chạm bước thứ tư

```
1  THU HOẠCH   đọc băng + sổ kết toán
2  ĐO          kỳ vọng · đuôi · hiệu chỉnh · theo chiến thuật
3  CHẨN        tìm bệnh bằng SỐ            <- chan_doan.py
4  ĐỀ XUẤT     model đề nghị vặn nút       <- chỗ DUY NHẤT
5  THỬ         chạy lại băng thật          <- chay_lai.py
6  CỔNG        tốt hơn VÀ đuôi không tệ hơn
7  GHI SỔ      hôm nay so hôm qua
```

Model bị kẹp giữa hai lớp số học nó không viết. Bề mặt nó được chạm là
**mười nút tham số**, mỗi nút một trần cứng — không sửa code, không thêm
chiến thuật, không đổi kiến trúc. Lý do: đề xuất sửa code thì cổng KHÔNG
kiểm được bằng số.

**Vắng khoá model thì vòng vẫn quay** — bước 4 rơi về người đề xuất tất
định (quét lưới một nút). Chậm hơn, nhưng vẫn tiến hoá mỗi ngày.

Ba kết cục đều hợp lệ: **NHẬN** · **TRẢ LẠI** (cổng làm đúng việc) ·
**ĐỨNG YÊN** (không bệnh nào vượt ngưỡng).

`data/tien-hoa.jsonl` ghi mỗi lượt: tham số trước/sau, kỳ vọng trước/sau,
lý do. Không có sổ đó thì "mạnh hơn mỗi ngày" là chuyện kể.

## Ba chế độ, và ba cửa

```
quan-sat   không có vị thế nào. Chỉ đo.
giay       khớp mô phỏng trên sổ lệnh THẬT, phí THẬT, tiền GIẢ.   ← mặc định
that       lệnh rời khỏi máy.
```

Một lệnh thật chỉ đi khi **cả ba cửa cùng mở**:

1. `config.json` → `che: "that"`
2. `config.json` → `datLenh.toiXacNhanDaDocRuiRo: true`
3. `.env` → `POLYMARKET_PRIVATE_KEY` có giá trị

Ba cửa nằm ở ba nơi khác nhau về bản chất, nên không thao tác đơn lẻ nào mở
được cả ba. Một dòng cấu hình duy nhất ngăn giữa mô phỏng và tiền thật là quá
mỏng: sửa nhầm một ký tự, hoặc `git checkout` một file, là tiền thật bắt đầu
chạy mà không ai kịp nhận ra.

Thiếu bất kỳ cửa nào thì **rơi về sổ giấy** — và không rơi trong im lặng,
`ly_do_khong_that()` in ra đúng cửa nào đang đóng.

## Ba làn tốc độ — và Claude nằm ở đâu

```
LÀN NHANH     0–1000 ms      KHÔNG có Claude
  giá Binance · sổ lệnh Polymarket · đồng hồ chợ · tồn kho · độ trễ
  → toán thuần Python, quyết định trong vài mili-giây

LÀN VỪA       1–60 giây      KHÔNG có Claude
  biến động thực nghiệm · quan hệ chéo market · hiệu chỉnh lại fair value

LÀN CHẬM      phút – giờ     CÓ Claude
  hậu kiểm · đọc lại băng · đề xuất giả thuyết · sinh chiến thuật mới
```

Nghiên cứu OpenMarket đo được Polymarket phản ứng sau Binance với trung vị
khoảng **347 ms**. Một lượt gọi model không bao giờ về kịp trong cửa sổ đó, và
có kịp cũng không nên: đường quyết định phải **tất định** thì mới chạy lại
được, mà chạy lại được mới biết một thay đổi là *tốt hơn* hay chỉ là *khác đi*.

Nên Claude ở đây là **nhà khoa học của cỗ máy**, không phải phản xạ của nó.
Runtime chạy kín vòng và đầy đủ mà không cần một lượt gọi model nào —
`ANTHROPIC_API_KEY` chỉ mở thêm làn chậm.

## Câu treo trên tường

```
CORRELATION   không phải ALPHA
SIGNAL        không phải ALPHA
LATENCY       không phải ALPHA
ACCURACY      không phải ALPHA

NET EXECUTABLE EDGE  =  ALPHA
```

OpenMarket ghép 727 triệu bản ghi Polymarket–Binance ở mức mili-giây, 43 đặc
trưng vi cấu trúc, walk-forward đàng hoàng. Họ **xác nhận** Polymarket phản
ứng trễ. Và mô hình của họ **vẫn không tạo được lợi thế ngoài mẫu sau phí và
trượt giá**.

Tín hiệu có thật, độ trễ có thật, và cả hai cộng lại vẫn ra một chiến lược lỗ.

## Bản đồ mã

```
kham/
  config.py      cấu hình + ba cửa của chế độ chạy
  khung.py       VÒNG ĐỜI khung — đọc file này trước       ← đắt nhất
  dong_song.py   WebSocket CLOB, sổ lệnh sống
  cap_token.py   UP/DOWN là MỘT sổ nhìn hai phía
  dongho.py      đồng hồ chợ, lệch đồng hồ sàn
  nguon.py       Polymarket (đọc) + Binance (đọc). Không đường nào ghi.
  so_lenh.py     sổ L2, VWAP theo khối lượng, sức chứa, thang chờ
  dinh_gia.py    fair value, bất định, rủi ro nhảy, hiệu chỉnh
  can_loi.py     net executable edge, phí, giá cặp
  kho_doi.py     tồn kho ba phần, giá cặp, tương quan chéo
  chan_rui_ro.py QUYẾT gì sau cú khớp đầu tiên
  do_thi.py      đồ thị chợ — so lệch, không so giá thô
  chien_thuat.py sáu ngón nghề cắm vào một nền máy
  rui_ro.py      Risk Engine — Python thuần, quyền phủ quyết
  dat_lenh.py    sổ giấy khớp trên sổ THẬT + cổng lệnh thật
  sdk_polymarket.py  lớp DUY NHẤT chạm tới khoá ví
  ket_toan.py    KHÉP VÒNG HỌC — không có nó bot không học được
  bang.py        băng ghi
  chay_lai.py    chạy lại theo sự kiện + đối chiếu hai tham số
  chan_doan.py   tìm bệnh bằng SỐ + mười nút model được vặn
  tien_hoa.py    VÒNG TIẾN HOÁ NGÀY — mạnh hơn mỗi ngày, đo được
  vo_dich.py     Champion/Challenger — không có `--force`
  vi.py          Đài Quan Ví — chỉ quan sát
  so.py          nhật ký + thống kê (kỳ vọng, đuôi, thua lớn nhất)
  vong.py        vòng lặp chính
  server.py      buồng lái FastAPI, chỉ localhost
  snapshot.py    cầu nối sang cung tĩnh
  sach.py        bỏ inf/nan trước khi ra JSON
```

## Vòng đời khung — phát hiện đắt nhất, đọc trước khi sửa gì

Một khung Up/Down có **hai cửa**, và chúng KHÔNG trùng nhau:

```
[eventStart − 300s , eventStart]    ĐẶT CƯỢC   <- bot làm việc ở đây
[eventStart        , endDate   ]    QUAN SÁT   <- sổ đóng băng
```

Bản đầu nhắm vào cửa quan sát và chỉ thấy **thang chờ** — dải lệnh trải từ
0,1¢ tới 99,9¢, hơn một triệu cổ, không mức nào là báo giá thật.

Bốn chi tiết phải nhớ, cả bốn đo được:

- `startDate` là **bẫy** — nó cách `endDate` gần một NGÀY (lúc tạo market).
  Mốc đúng là `eventStartTime`, bằng đúng con số Unix trong slug.
- Gamma **chặn cứng 100 kết quả** dù xin bao nhiêu. Nên dựng thẳng slug từ
  mốc thời gian thay vì quét theo tiền tố.
- Sổ **một chiều mỗi token là bình thường**: mua UP ≡ bán DOWN, nên một
  lệnh hiện ra ở cả hai token, soi gương qua trục 0,5.
- Báo giá hai chiều **ngắt quãng**, không liên tục. Không có quote thì
  runtime đứng ngoài — đó là hành vi đúng, không phải hỏng.

## Năm chỗ dễ hỏng IM LẶNG — đều có phép kiểm

Đây là loại lỗi đã cắn `tu-cam-thanh-runtime` bốn lần: số vẫn ra, bảng vẫn
xanh, chỉ có kết quả là sai.

1. **τ → 0 làm nổ mô hình.** Còn 0,2 giây thì `σ√τ ≈ 0` và P(UP) thành đúng
   `1.0000000000` — mô hình tuyên bố chắc chắn 100% đúng lúc nó biết ít nhất.
   Chặn bằng hai lớp: sàn cho τ, và làm phẳng kết quả về `[2%, 98%]`.

2. **Bất định tụt khi tới gần kết quả.** Sai số tham số không đo được thứ nguy
   hiểm nhất của binary 5 phút. Thêm **rủi ro nhảy giá**: ngay lằn ranh + còn
   3 giây → bất định `0,23`; cách 3σ + còn 3 giây → `0,003`. Cả hai đều đúng.

3. **Năm dấu hiệu của một cú BTC bị đếm thành năm bằng chứng.** Volume, bid
   imbalance, ETH, SOL, taker flow — năm cái bóng của một nguyên nhân. Gộp
   theo **họ tín hiệu**, chỉ cái mạnh nhất mỗi họ giữ trọn trọng số.

4. **Kelly trên xác suất chưa ai kiểm.** Mô hình nói 60% mà thực tế thắng 52%
   thì Kelly phóng to đúng khoảng lệch đó. Kelly bị **khoá cứng** cho tới khi
   đủ mẫu hiệu chỉnh.

5. **Băng ghi rách mà không ai báo.** Bản đầu mở băng bằng `gzip.open(...,
   "at")` — nối thêm vào file của ngày. Tiến trình bị giết giữa chừng để lại
   một thành viên gzip CỤT, lần chạy sau nối thành viên mới ngay sau đám byte
   cụt ấy, và giờ rác nằm GIỮA file. `zlib` chạy tới đó thì ném `invalid block
   type`, mà `doc_bang()` khi ấy chỉ bắt `OSError` — `zlib.error` không phải
   `OSError`, nên lời gọi ném ra ngoài và kéo theo cả những ngày NGUYÊN VẸN.

   Đo trên băng thật ngày 21/08/2026: đọc được **8.238 / 30.680 khung** (mất
   73%), và vòng tự tiến hoá chết ngay dòng đầu suốt từ đó — trong khi buồng
   lái vẫn hiện "đã chạy hôm nay". Nay mỗi phiên ghi một file riêng, trình đọc
   nhảy qua chỗ đứt rồi đọc tiếp, và `/api/bang` trả kèm số file hỏng.

   Và báo cáo ấy tách **cụt đuôi** khỏi **đứt giữa**: file của mọi phiên bị
   Ctrl+C đều thiếu block kết thúc, nên gộp hai loại lại là đèn báo đỏ vĩnh
   viễn — mà cảnh báo lúc nào cũng đỏ thì thôi ai nhìn, kể cả lần nó đúng.

Và một chỗ nữa mà `so_lenh.py` tồn tại để chặn: **"EDGE = 9¢" trên bảng điều
khiển**. Đó là `fair − best_ask`, đúng cho đúng 80 cổ đầu tiên. Giá thật cho
680 cổ là VWAP `0,4894` nên lợi thế còn `6,1¢`; ăn cả sổ thì `3,6¢`; sau năm
khoản trừ thì **âm**.

## Lộ trình — P10 là mốc duy nhất chạm tới tiền

| | xây gì | được làm gì |
|---|---|---|
| P0 | băng ghi Binance + Polymarket + đồng hồ | không giao dịch |
| P1 | sổ lệnh CLOB, tìm khung, dữ liệu kết toán | không giao dịch |
| P2 | fair value nền + hiệu chỉnh | không giao dịch |
| P3 | net executable edge + VWAP + phí + sức chứa | không giao dịch |
| P4 | chạy lại lịch sử theo sự kiện | không chạy thật |
| P5 | tồn kho + rủi ro chân + tương quan | sổ giấy |
| P6 | lệch giá định hướng + cặp theo thời | sổ giấy |
| P7 | giá trị tương đối + tạo lập + cận kết quả | sổ giấy |
| P8 | Đài Quan Ví | chỉ nghiên cứu |
| P9 | Champion/Challenger từng chiến thuật | chạy bóng |
| P10 | thật, rất nhỏ, nếu MỌI cửa đều đạt | trần cứng |

**P0 phải làm trước mô hình.** Không lưu sổ lệnh và tick ngay từ đầu thì ba
tháng nữa dù muốn nghiên cứu cũng không có ký ức thế giới nào để chạy lại. Mô
hình viết sau lúc nào cũng được; dữ liệu thì không quay lại.

## Hai chỗ PHẢI đối chiếu trước khi chạy tiền thật

1. **Hệ số phí taker** trong `config.json` (`phi.takerHeSo`) là **tham số**,
   không phải sự thật đã kiểm. Con số thật nằm ở
   `docs.polymarket.com/trading/fees` và Polymarket có đổi. Đặt sai thì mọi
   phép tính edge lệch theo cùng một chiều, và lệch im lặng.

2. **Đường đặt lệnh trong `sdk_polymarket.py` cố ý dừng ở
   `NotImplementedError`.** Nối vào đó cần hai quyết định thật: phân giải
   market sang token id, và chọn loại lệnh (GTC/FOK/GTD) theo luật từng
   market. Đoán một mặc định rồi gửi tiền thật đi theo phỏng đoán là cách hỏng
   đắt nhất có thể.

## SDK

`Polymarket/py-clob-client` đời cũ **đã bị archive 25/05/2026**; chính repo đó
ghi rõ không nên dùng cho tích hợp mới. SDK hợp nhất hiện hành là
`Polymarket/py-sdk`, gói `polymarket-client`.

Phần **đọc** ở đây dùng thẳng HTTP — ít phụ thuộc hơn, và API đọc thì ổn định.
Chỗ cần SDK (ký lệnh) nằm sau adapter `sdk_polymarket.py`, để SDK đổi thì chỉ
sửa một file chứ không sửa cả hệ thống. Polymarket còn đang chuyển CLOB V2, nên
điều này sẽ có ích.
