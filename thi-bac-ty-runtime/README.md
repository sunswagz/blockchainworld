# THỊ BẠC TY — bộ máy quản lý và vận hành vốn

Thị Bạc Ty **không phải một chiến lược**. Nó là cả cỗ máy: quan sát thị
trường · phát hiện cơ hội · định giá · kiểm soát rủi ro · phân bổ vốn · thực
thi · kế toán · học từ kết quả.

```
                    THỊ BẠC TY
                         │
           ┌─────────────┴─────────────┐
           │                           │
      TRUNG ƯƠNG                    CÁC TY
    thi_bac_ty/                   bac/ ← ty đầu tiên
    Data · Risk · Capital         Phái sinh · Tín dụng ·
    Ledger · Execution            Chênh lệch · Thanh khoản ·
                                  Thanh lý · MEV · Cầu nối
```

Thứ đang chạy trong `bac/` là **`perpetual.funding_spread.v1`** — ty đầu
tiên đã hoạt động, không phải toàn bộ Thị Bạc Ty và cũng chưa phải toàn bộ
ty Phái Sinh.

## Luật chung của mọi ty

```
KHÔNG ty nào được tự quản toàn bộ vốn của hệ thống.
KHÔNG ty nào được tự dựng Rủi Ro Tổng riêng.
KHÔNG ty nào được tự quyết danh mục.

MỌI ty chỉ: phát hiện → đánh giá → xuất TỜ TRÌNH.
```

Không có luật này thì mười ba ty là mười ba đứa đều tưởng tiền trong ví là
của mình, và không đứa nào nhìn thấy tổng.

## Tờ trình — đồng tiền ngôn ngữ

Mọi ty nói với trung ương bằng đúng một kiểu: `thi_bac_ty.to_trinh.ToTrinh`.

    bac.models.CoHoi   thứ ty TỰ TÌM RA — nội bộ, đầy thuật ngữ funding
    ToTrinh            thứ ty TRÌNH LÊN — chung, mọi ty đều hiểu

`CoHoi` có `soMocLong`, `intervalShortGio` — những từ ty Tín Dụng không hiểu
và không cần hiểu. `bac/xuat_to_trinh.py` dịch giữa hai thứ, và **không viết
lại thuật toán nào**.

### Ba luật của hợp đồng

**1. KHÔNG BIẾT phải khác KHÔNG.** Ty Phái Sinh không chạm hợp đồng thông
minh nên `ruiRo.giaoThuc = None`, **không phải 0**. Ghi 0 là nói "đã xét,
không có rủi ro", rồi Rủi Ro Tổng cộng những số 0 ấy lại thành một danh mục
an toàn giả.

**2. Con số chưa đủ mô hình phải TỰ KHAI.** Khi trung ương xếp hạng:

    perp.funding_spread   18 bps   ← chặn trên, thiếu bốn khoản phí
    credit.lending_rate   11 bps   ← đã trừ đủ

kết luận "cái đầu tốt hơn" là kết luận SAI rút ra từ hai con số không cùng
đơn vị. `moHinhPhiDuChua` và `moHinhSucChuaDuChua` tồn tại để chặn đúng
chuyện đó.

**3. Hợp đồng tự soát mình.** `ToTrinh.kiem()` chạy không cần mạng, không
cần trung ương. Tờ trình sai khuôn chết ở CỬA TY, không trôi vào sổ đăng ký
rồi làm hỏng thống kê ba tháng sau.

### `netMoiGioBps` — thước so sánh giữa các ty

Không so `netUocBps` trần được:

    20 bps giữ 24 giờ   →  0,83 bps/giờ
     6 bps giữ  2 giờ   →  3,00 bps/giờ   ← thắng, vì vốn quay 12 lượt

Vẫn chưa phải thước cuối: nó chưa xét sức chứa (rót được bao nhiêu) và chưa
xét rủi ro. Người phân bổ vốn phải nhìn cả ba.

### Sức chứa còn THÔ, và nói thẳng là thô

`ToTrinh` đòi `sucChuaToiDaUsd` — rót thêm tới đâu thì chính cơ hội tự giết
mình. Sức chứa thật đo bằng **độ sâu sổ lệnh**, mà runtime chưa hỏi sổ lệnh
của cảng nào. `bac/suc_chua.py` tạm suy từ open interest (0,05%, lấy MIN hai
chân, có trần và sàn), và **luôn** khai `moHinhSucChuaDuChua = False`.

Vì sao không trả `None` cho xong: người phân bổ vốn gặp `None` thì không
sizing được gì, và mọi tờ trình của ty này thành vô dụng — trong khi ta vẫn
biết chắc một điều, **không phải vô hạn**.

### Chiều phụ thuộc, một chiều

    bac/  (ty)  ──import──►  thi_bac_ty/  (trung ương)

Trung ương không được import ngược, và có phép kiểm canh việc đó. Ngày trung
ương phải `import bac` để xử một trường hợp riêng là ngày hợp đồng đã hỏng:
chỗ phải sửa là hợp đồng, không phải thêm một nhánh `if`.

## Trung Ương — chín tầng, và vòng khép kín

`bac/` là MỘT ty. `thi_bac_ty/` là cỗ máy chia vốn đứng trên mọi ty. Thứ tự
này không đảo được: một ty không bao giờ nhìn thấy tổng danh mục, nên nó
không bao giờ được quyết chuyện của tổng.

```
THỊ TRƯỜNG
   │  các ty quét
   ▼
TỜ TRÌNH ──► THÔNG CHÍNH TY ──► SỔ ĐĂNG KÝ (PHAT_HIEN)
                                     │
                                     ▼
                               RỦI RO TỔNG  ◄── DANH MỤC
                              cho tối đa $X
                                     │
                                     ▼
                               PHÂN BỔ VỐN   (cấp TUẦN TỰ)
                                     │
                                     ▼
                          ĐIỀU PHỐI THỰC THI (máy trạng thái hai chân)
                                     │
                                     ▼
                                 SỔ CÁI ──► CHẨN ĐOÁN ──► XÉT THAM SỐ
                                                              │
                                     ┌────────────────────────┘
                                     ▼
                                THỊ TRƯỜNG
```

| tệp | việc |
|---|---|
| `to_trinh.py` | hợp đồng — đồng tiền ngôn ngữ giữa các ty |
| `khuon_ty.py` | khuôn một ty mới phải điền, và **chỉ** được điền |
| `thong_chinh.py` | sàn nhận tờ trình, chặn sai khuôn ngay ở cửa |
| `so_dang_ky.py` | vòng đời mọi tờ trình, và **cái phễu** |
| `danh_muc.py` | ba thước phơi nhiễm: ròng · thô · theo cảng |
| `rui_ro_tong.py` | trả về một **TRẦN**, không phải một chữ có/không |
| `phan_bo.py` | xếp hạng rồi cấp **tuần tự**, xét lại sau mỗi lần |
| `so_cai.py` | sổ chỉ-thêm; sửa sai chỉ có một đường là **đảo** |
| `thuc_thi.py` | máy trạng thái hai chân, có đường lùi |
| `cau_dao.py` | ngắt **tự động**, đóng lại **phải có người** |
| `chan_doan_he.py` | bệnh của cả bộ máy, và đề xuất vặn tham số phân bổ |
| `trung_uong.py` | khép vòng, và ép mọi tầng đi đúng thứ tự |

### Bảy việc một ty KHÔNG được làm

    ✗ giữ tiền, biết NAV, biết ty khác đang giữ gì
    ✗ tự đặt trần vốn cho mình          ✗ dựng Rủi Ro Tổng riêng
    ✗ gọi thẳng một ty khác             ✗ đặt lệnh
    ✗ ghi thẳng vào Sổ Cái              ✗ đóng/mở cầu dao

Bảy điều ấy thuộc Trung Ương, và không phải vì tập trung cho đẹp: mỗi điều
trong đó **cần nhìn thấy toàn bộ danh mục** — thứ mà theo định nghĩa không ty
nào nhìn thấy.

### Vì sao cấp vốn TUẦN TỰ, không song song

Hai tờ trình cùng chạm Binance. Xét riêng từng tờ trên danh mục hiện tại thì
cả hai đều lọt; cấp cả hai rồi cộng lại mới vượt trần cảng. Nên `phan_bo.py`
xếp hạng trước, rồi cấp từng tờ một và **gọi lại `rui_ro_tong.xet()` sau mỗi
lần cấp** trên danh mục đã cập nhật.

Cái giá là chậm hơn. Cái được là trần thật sự là trần.

### Vì sao Rủi Ro Tổng trả về một TRẦN

Trả nhị phân thì một cơ hội tốt xin $500 trong lúc chỉ còn chỗ cho $120 sẽ bị
vứt cả. Trả một trần thì nó được cấp $120, và `lyDoCat` nói rõ trần nào đã
chặn — người đọc cãi lại được.

### Cầu dao: ngắt tự động, đóng lại phải có NGƯỜI

Bất đối xứng có chủ ý. Máy phát hiện sự cố nhanh hơn người, nhưng máy không
phân biệt được *"sự cố đã qua"* với *"sự cố vẫn còn nhưng tín hiệu tạm im"* —
và cái thứ hai chính là lúc đóng lại thì mất tiền. Nên `dong_lai(ma, nguoi)`
không có mặc định cho `nguoi`.

Ngoại lệ duy nhất là những lý do đo được trực tiếp và không mơ hồ (đồng hồ đã
khớp lại): chúng khai `tuMo=True` và tự đóng. `sut-von` thì **không** — sụt
vốn là hậu quả, không phải tín hiệu; nó "hết" không có nghĩa là nguyên nhân
đã hết.

### Ngắt rồi thì vẫn quan sát

`mot_vong()` hỏi cầu dao **trước** khi phân bổ. Ngắt thì vẫn quét, vẫn ghi
nhận vào sổ đăng ký, vẫn chẩn đoán — chỉ không cam kết vốn. Dừng cả việc quan
sát là tự làm mình mù đúng lúc cần nhìn nhất.

### Cùng một cơ hội chỉ vào sổ MỘT lần mỗi giờ

Ty quét mỗi 30 giây; một chênh lệch funding sống hàng giờ. Không có cửa chống
trùng thì một cơ hội duy nhất vào sổ 120 lần mỗi giờ, và **cái phễu nói dối**:
mẫu số thành 86.400 "phát hiện" cho 30 cơ hội có thật, nên mọi tỉ lệ sống sót
đều chia cho một con số bịa. Xem `nhipGhiNhanGiay` và `_dau_van()`.

### Trung Ương chỉ ĐỀ XUẤT vặn tham số, không tự vặn

Khác hẳn vòng tiến hoá của ty. Ty tự vặn được vì nó **chạy lại băng** rồi đo
A/B trên cùng dữ liệu. Đổi tham số phân bổ thì không chạy lại được: muốn biết
một trần rộng hơn có tốt hơn không thì phải biết những cơ hội đã KHÔNG được
cấp diễn biến ra sao — mà chúng không được mở nên không có kết cục.

Không A/B được thì không tự nhận được. Người duyệt.

### Câu hỏi thành/bại của cả lớp trừu tượng này

> *Hai chiến lược hoàn toàn khác nhau có sống dưới cùng một Thị Bạc Ty không?*

`scripts/selftest.py` trả lời bằng một ty **cho vay** giả — không funding,
không mốc kết toán, không hai chân perp — chạy song song với ty phái sinh
thật, dưới cùng một Trung Ương, **không sửa một dòng nào trong `thi_bac_ty/`**.
Cả hai cùng vào sổ đăng ký, cùng bị `rui_ro_tong` xét, cùng được xếp hạng bằng
`netMoiGioBps`, và danh mục cộng phơi nhiễm chéo hai ngành.

Ngày phép kiểm ấy phải sửa `thi_bac_ty/` mới chạy được là ngày lớp trừu tượng
này hoá ra là giả.

## Ty đầu tiên — chênh lệch funding


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
& $py scripts/selftest.py      # 359 phép kiểm số học, KHÔNG cần mạng
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

## Trần vốn CHƯA có hiệu lực — và vì sao nó không nằm chung với cửa

`config.json` có khối `von` với `moiCoHoiUsd`, `toiDaUsd`, `donBayToiDa`, và
một cờ `coHieuLuc: false` nói thẳng: **ba con số này chưa chặn gì cả**. Không
có lớp đặt lệnh thì không có vị thế nào để mà giới hạn, kể cả trên sổ giấy.

Chúng từng nằm trong khối `ruiRo`, nên buồng lái bày chúng dưới nhãn *"Cửa
rủi ro đang có hiệu lực"* — ba cái cửa không chặn gì, hiện ra như đang chặn.
Không lỗi nào báo, vì mọi con số đều hợp lệ.

Nay `rui_ro.py` khai một tuple `CUA` là **hợp đồng**: mọi khoá trong đó phải
được `xet()` thật sự đọc, và `xet()` không được đọc khoá nào ngoài đó. Phép
kiểm canh cả hai chiều bằng một dict do thám — cấy thử một cửa giả vào thì
hai phép nổ ngay.

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

### `netBps` là CHẶN TRÊN, và mỗi cơ hội tự khai điều đó

Mỗi `CoHoi` mang theo:

```
moHinhPhiDuChua = false
phiConThieu     = [vay-coin, chuyen-von, basis-luc-thoat, von-bi-khoa]
```

Không phải để trang trí. Khi Thị Bạc Ty có chiến lược thứ hai, bảng xếp hạng
sẽ đặt cạnh nhau:

    funding spread   18 bps   ← chặn trên, còn thiếu bốn khoản
    chiến lược khác  11 bps   ← đã trừ đủ

và kết luận *"funding tốt hơn"* là kết luận **sai**, rút ra từ hai con số
không cùng đơn vị. Không có cờ này thì không cách nào biết mà tránh — chính
cỗ máy sẽ bị đánh lừa bởi số liệu của chính nó.

Mỗi cơ hội cũng mang `maChienLuoc = "perp.funding_spread.v1"`. Hiện chưa phân
biệt được gì vì mới có một chiến lược; giữ vì cái giá là một dòng, còn cái
giá của việc thêm SAU là đi gắn nhãn ngược cho mọi băng đã ghi.

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

  xuat_to_trinh.py  CoHoi → ToTrinh    ← chỗ nối lên trung ương
  ty_perp.py        cắm vào khuôn Ty   ← mỏng có chủ ý

thi_bac_ty/       TRUNG ƯƠNG — không bao giờ import bac/
  to_trinh.py     hợp đồng            ← đọc trước
  khuon_ty.py     khuôn một ty mới    ← đọc ngay sau
  thong_chinh.py  sàn nhận tờ trình
  so_dang_ky.py   vòng đời + cái phễu
  danh_muc.py     ba thước phơi nhiễm
  rui_ro_tong.py  trả về một TRẦN
  phan_bo.py      xếp hạng, cấp tuần tự
  so_cai.py       sổ chỉ-thêm, sửa bằng ĐẢO
  thuc_thi.py     máy trạng thái hai chân
  cau_dao.py      ngắt tự động, đóng lại phải có người
  chan_doan_he.py bệnh của cả bộ máy
  trung_uong.py   khép vòng            ← đọc sau cùng
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
