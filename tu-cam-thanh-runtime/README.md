# Tử Cấm Thành — runtime (M0)

AI Trader Runtime: có mắt nhìn thị trường, có bộ não, có kho kỹ năng, có trí nhớ,
có kỷ luật rủi ro, có nhật ký và có hậu kiểm. Claude đóng vai **bộ não tổng hợp**,
không phải người giữ chìa khoá két.

Đây là **mốc M0** — vòng chạy kín nhỏ nhất mà vẫn học được. Không phải cả 18 tầng
trong bản thiết kế. Dựng hết một lượt thì không tầng nào chạy thật.

## Quan hệ với cung `tu-cam-thanh/`

Hai thứ khác nhau, cố ý:

| | ở đâu | làm gì | lên site? |
|---|---|---|---|
| **cung tĩnh** | `tu-cam-thanh/` | trang chỉ-đọc, công khai | có |
| **runtime** | `tu-cam-thanh-runtime/` | buồng lái: chat, nút bấm, SSE | **không** |

Cung là bản ghi công khai của phiên gần nhất; runtime là buồng lái. Trang tĩnh
trên GitHub Pages không có server và không được phép giữ khoá API, nên runtime
ghi ra `tu-cam-thanh/assets/js/v/phien.js` rồi **commit** — đúng cách Hoàng Thành
đang làm với rừng văn hoá. Xem mục "Tử Cấm Thành cũng là ngoại lệ" trong `CLAUDE.md`.

Thư mục này **không được thêm vào `HALLS`** của `build-dist.mjs`, và **đừng tạo
`tu-cam-thanh-runtime/index.html`** — bộ kiểm sẽ nhầm nó là cung.

## Chạy

**Chạy nền (khuyên dùng)** — cài một lần để có lối tắt ngoài desktop; bấm vào
thì runtime mới lên, **không** tự bật khi khởi động máy:

```powershell
powershell -ExecutionPolicy Bypass -File dichvu\cai-dat.ps1
```

Muốn nó tự chạy lúc đăng nhập thì bật trong buồng lái: **Hệ thống → Tự chạy khi
đăng nhập**. Mặc định tắt vì trên máy nhiều người qua lại, một cỗ máy đặt lệnh
tự khởi động là thứ không ai xin phép.

Chi tiết ở [`dichvu/README.md`](dichvu/README.md): bộ giám sát tự dựng lại
runtime khi nó chết, có nghỉ tăng dần và biết bỏ cuộc khi cấu hình sai; nhật ký
xoay vòng; và bốn cái bẫy Windows đã dẫm phải khi dựng nó.

**Chạy tay:**

```bash
pip install -r requirements.txt
python run.py                    # buồng lái: http://localhost:5182
python -m trader.snapshot        # ghi lát cắt một lần rồi thoát
python scripts/selftest.py       # kiểm một vòng kín, không gọi API, không mở cổng
python scripts/kiem-env.py       # soát .env (KHÔNG in khoá ra màn hình)
python scripts/kiem-testnet.py   # kiểm kết nối sàn testnet
python scripts/kiem-roi-ve.py    # kiểm đường rơi về sàn giấy
python scripts/thu-mot-lenh.py   # thử nguyên đường ống vào lệnh (--that để gửi thật)
python scripts/doi-so.py         # đối soát sổ cục bộ với sàn (--don để dọn)
python scripts/sinh-icon.py      # vẽ lại 5 icon PNG của cung
python scripts/chung-cat.py      # đúc lại PHÁT HIỆN từ mọi kho đo (vòng lặp tự gọi mỗi 20')
python scripts/do-mau-gia.py --ghi        # đo 13 mẫu giá kinh điển trên nến thật
python scripts/do-khung.py --ghi          # khung nào đỡ nổi mức RR đang đòi
python scripts/ban-giao.py --ghi          # bản tóm tắt cho lượt làm việc sau
python scripts/gia-thuyet.py --tra "..."  # cái này đã thử chưa? (tra TRƯỚC khi đo)
BRAIN=cli python run.py                   # bộ não thật bằng quota gói, không cần khoá
python scripts/bo-pha.py --ghi            # phí ×2 ×3, đoạn lịch sử tệ nhất
python scripts/soat-lai-bai-hoc.py --ghi   # hậu kiểm LẠI bài học cũ khi sổ đã dài hơn

python scripts/tai-lich-su.py --so 4000   # tải nến lịch sử để huấn luyện
python scripts/kiem-huanluyen.py          # kiểm cỗ máy chạy lại (cần nến ở trên)
python scripts/dau-chien-luoc.py --tat-ca # đấu mọi bộ luật với champion, ngoài mẫu
python scripts/dau-chien-luoc.py --tat-ca --cho BTCUSDT:4h,ETHUSDT:4h  # nhiều chợ
python scripts/tai-lich-su.py --so 6000 --coin BTCUSDT,ETHUSDT,SOLUSDT --khung 5m,15m,30m,1h,4h,1d
python scripts/kiem-nguon.py --offline    # kiểm phân loại tin, không chạm mạng
python scripts/do-huong.py --ghi --cho <ds>  # nửa LONG và nửa SHORT đáng bao nhiêu
python scripts/lo-luyen.py --cho <ds> --bien 20 --lat 4 --chi-long --ghi
python scripts/an-toan-dung-lai.py        # CÓ AN TOÀN để giết run.py không (mã thoát 0/1)
node scripts/kiem-giao-dien.mjs           # mọi trường app.js đọc phải có thật (runtime đang chạy)
```


## Nhiều chợ, và nửa chiến lược bot không chạy được

`config.symbols` liệt kê các chợ được QUÉT mỗi lượt ra quyết định; `symbol` là
chợ chính, luôn đứng đầu. Luật thuần chấm cả 15 chợ (miễn phí, chạy tại máy),
bộ não chỉ suy luận cho ứng viên được chọn — trần `brain.cli` là 8 lượt/ngày,
không phủ nổi 15 chợ mỗi vòng.

Hai hàng rào đi cùng nhau: `maxOpenPositions` 4 và `maxTongRuiRoPct` 2,0%.
15 lệnh crypto KHÔNG phải 15 cược độc lập — chúng thua cùng nhau.

Và một chỗ phải nhớ khi đọc MỌI con số ở đây: sàn spot chỉ bán được thứ đang
giữ, nên bot chạy thật **không đánh được SHORT**. Đo trên 48 chợ, 2.069 lệnh:

    riêng SHORT  1134 lệnh  +0,0911R   ← nửa có lãi
    riêng LONG    935 lệnh  −0,1474R   ← nửa bot chạy được

Nên mọi bảng "cả hai chiều" nói về một chiến lược bot không chạy nổi. Dùng
`--chi-long` khi dò tham số, và đọc `do-huong.json` để thấy khoảng cách.

### Làn demo hai chiều — cổng 5282

Con số trên nói nửa SHORT là nửa có lãi, và bản chạy lại thì nói mạnh hơn nữa:
MOCK_KEO_LUI_V1 trên 33 chợ 1d **chưa từng dùng** để tìm ra nó cho +0,205R qua
269 lệnh, khoảng tin [+0,063; +0,354] không chứa 0 — kết quả dương ngoài mẫu
duy nhất của cả hệ. Tách hướng: SHORT +0,303R/226 lệnh, LONG −0,306R/44 lệnh.

Chạy lại nói được đến đó rồi hết. Nên có làn thứ hai đo TIẾN TƯỚNG trên giá
thật: chế độ `paper` (ở đó `spot_only` tắt nên short được), vốn ảo riêng, sổ
riêng, 46 chợ, và KHÔNG ghi cung tĩnh.

    powershell -File dichvu\bat.ps1 -Demo      # bật, chạy nền, sống qua đăng xuất
    powershell -File dichvu\dung.ps1 -Demo     # dừng
    python scripts/so-hai-lan.py                 # đọc hai làn cạnh nhau

Nó KHÔNG chạy nghi thức: hai làn dùng chung `data/lich-su` và `data/chuoi`, nên
hai bộ việc đo nặng sẽ giẫm lên nhau. Đo đạc là việc của làn chính.

Giả thuyết đang chờ: `keo-lui-short-tien-tuong` — cần 30 lệnh SHORT đã đóng.
Chạy lại KHÔNG mô phỏng phí vay và rủi ro bị ép đóng của short thật, và làn demo
cũng không. Con số nó cho là cận TRÊN, không phải con số của một tài khoản
short thật.
## Phòng huấn luyện

Chạy lại chiến lược trên nến lịch sử, dò tham số, đúc bài học. Vào từ buồng lái
→ tầng 3 → **Phòng huấn luyện**, hoặc gọi thẳng:

```bash
python scripts/tai-lich-su.py --so 4000   # một lần, ~4000 nến 1h ≈ 6 tháng
curl -X POST localhost:5182/api/hoc -d '{"viec":"quet"}'   # dò tham số
curl localhost:5182/api/hoc                                # tiến độ + kết quả
```

Lượt đầu mất khoảng sáu phút để dựng chuỗi tín hiệu (chỉ báo phải tính lại trên
cửa sổ 400 nến ở mỗi bước). Chuỗi được cache ra `data/chuoi/`, nên từ lượt hai
trở đi mọi lượt chạy lại và cả phép dò 72 tổ hợp đều xong trong dưới một giây.

Cache gắn **vân tay** của bộ dữ liệu + khung thời gian + `candleLimit`. Đổi bất
kỳ thứ nào trong đó là chuỗi tự sinh lại — nếu không thì kết quả trả về trong
một giây, trông rất hợp lý, mà thuộc về cấu hình cũ.

### Bốn đường backtest tự lừa mình, và chỗ chặn từng đường

| Đường | Chặn ở đâu |
|---|---|
| Nhìn trộm tương lai | lát nến cắt tại `i`, khung lớn tìm bằng nhị phân trên mốc thời gian; `kiem-huanluyen.py` mục [3] so kết quả khi thêm 120 nến tương lai |
| Nến chạm cả SL lẫn TP | luôn tính **SL** — `_thoat()`, mục [1] |
| Quên chi phí | phí + trượt giá ở **cả hai đầu**; lệnh dính SL luôn lỗ hơn 1R, mục [7] |
| Dò rồi khoe chính con số đã dò | cắt đôi dữ liệu, chọn trong mẫu, chấm điểm ngoài mẫu, hiện thẳng **khớp trội** |

Một chỗ nữa đáng nhớ vì nó im lặng: bản chạy thật chỉ xin `candleLimit = 400`
nến, nên bản chạy lại cũng bị chặn đúng cửa sổ đó. Lần viết đầu tôi để lát nến
lớn dần tới hết lịch sử — không có gì đổ, chỉ là kết quả thuộc về một hệ thống
khác với hệ thống sắp chạy bằng tiền thật.

**Giới hạn đã biết:** chưa mô phỏng nhảy giá qua stop. Thật thì stop 95 có thể
khớp ở 90 khi tin ra lúc 2h sáng, nên số ở đây vẫn còn lạc quan hơn thực tế.

### Dò cái gì, và vì sao không dò ngưỡng rủi ro

Lưới dò chỉ chứa **tham số chiến lược** (`stopAtr`, `demTp`, `adxToiThieu`,
`chanBienDongCao`) — xem `THAM_MAC_DINH` trong `brain.py`. Ngưỡng rủi ro nằm
ngoài lưới có chủ ý: gộp chung thì rồi sẽ có lúc "tối ưu" bằng cách hạ hàng rào.
`kiem-giao-dien.mjs` mục [9] canh đúng chuyện này.

Lưới đầu tiên tôi dựng lại toàn ngưỡng rủi ro, và cả 108 tổ hợp cho ra một kết
quả duy nhất — vì bộ luật tự suy mục tiêu từ `minRR` để luôn vừa đủ qua cửa. Dò
một tham số mà chiến lược đã tự chiều theo thì chỉ đo được chính nó.

## Nguồn dữ liệu ngoài

`trader/nguon.py` — bốn nhóm, **không nhóm nào cần khoá API hay tốn tiền**:

| Nhóm | Nguồn | Nhịp |
|---|---|---|
| phái sinh | Binance Futures — funding, open interest, tỉ lệ long/short của **top trader** | 2 phút |
| vĩ mô | Yahoo Finance — DXY, lợi suất 10 năm, dầu, S&P 500, vàng | 5 phút |
| tâm lý | alternative.me — Sợ hãi / Tham lam | 30 phút |
| tin tức | RSS 9 feed — trong đó **Fed, SEC, BLS là nguồn sơ cấp** | 15 phút |

Chạy ở **luồng riêng**, không nằm trong vòng giao dịch: một lượt gom mất ~5 giây
trong khi nhịp tick là 20 giây, để chung thì sự cố mạng bên ngoài hoá thành sự
cố giao dịch.

Từng cân nhắc GDELT làm nguồn tin, nhưng đo tại máy này thì nó chặn theo tải chứ
không theo đồng hồ: giãn 5,5 giây rớt 4/5 truy vấn, giãn 8 giây vẫn rớt 3/5. RSS
không giới hạn nhịp và đọc thẳng từ Fed/SEC/BLS thì còn sớm hơn qua toà soạn.

Phân loại tin bằng **từ khoá có ranh giới từ**, và mỗi bài mang theo từ khoá đã
khớp nên xếp sai là nhìn ra ngay. `kiem-nguon.py --offline` gác chỗ này — nó đã
bắt được hai lỗi thật: `"SEC Charges **Boiler** Room"` rơi vào nhóm dầu vì "oil"
nằm trong "b-oil-er", và nhóm "quy định crypto" nuốt trọn mọi án lừa đảo thường
của SEC.

## Hai chế độ sàn

`"mode"` trong `config.json`:

| | khớp ở đâu | tiền | cần khoá |
|---|---|---|---|
| `paper` (mặc định) | mô phỏng trong tiến trình | giả, nội bộ | không |
| `testnet` | Binance Spot Testnet, sổ lệnh thật | giả, do Binance cấp | có |

**Không có chế độ mainnet, và cố ý không có.** Base URL cắm cứng trong
`trader/exchange.py`, không đọc từ config — một biến `base_url` trong file cấu
hình là một dòng sửa nhầm giữa tiền giả và tiền thật.

### Nối testnet

1. Vào https://testnet.binance.vision, đăng nhập bằng GitHub, bấm
   **Generate HMAC_SHA256 Key**. Khoá hiện ra **đúng một lần** — chép ngay.
2. `cp .env.example .env` rồi điền `BINANCE_TESTNET_KEY` / `BINANCE_TESTNET_SECRET`.
3. Đổi `"mode": "testnet"` trong `config.json`.
4. `python scripts/kiem-testnet.py` — phải xanh hết trước khi chạy `run.py`.

Khai `testnet` mà không nối được thì runtime **rơi về sàn giấy và báo to**, chứ
không đứng im: rơi về im lặng là mọi con số vẫn đẹp trong khi không có lệnh nào
tồn tại trên sàn.

### Ba chỗ testnet khác sàn giấy

**Phân tích chạy trên nến mainnet, khớp lệnh ở testnet.** Testnet chỉ có ~236
nến 1H và **60 nến 4H** — không đủ cho EMA200, nên regime sẽ luôn là UNKNOWN và
bộ não không bao giờ được gọi. Giá hai bên lệch ~0.00%, nên lấy nến sâu ở
mainnet là an toàn; `kiem-testnet.py` canh chừng và báo nếu lệch vượt 0.5%.

**Spot không short được.** Luận điểm SHORT bị Risk Engine chặn bằng cờ
`spot_only` — chặn ở đó chứ không để rơi xuống sàn rồi mới nổ, vì xuống tới đó
là đã tốn một lượt gọi model.

**Thoát lệnh do SÀN giữ, không do vòng lặp.** Vào lệnh xong đặt ngay một OCO
(chốt lãi + cắt lỗ) nằm trên sổ lệnh Binance. Tắt máy, mất điện hay một
exception thì vị thế vẫn có người canh. `doi_soat()` chạy lúc khởi động để soát
lệch giữa sổ cục bộ và sàn.

Số dư testnet do Binance cấp và có thể bị đặt lại bất cứ lúc nào — đó là chuyện
bình thường của testnet, không phải hỏng. `reset` chỉ huỷ lệnh treo và xoá sổ
cục bộ; nó **không** nạp lại số dư.

### "Vốn" không phải "tiền mua được"

Tài khoản testnet có 10.000 USDT **và** 1 BTC, nên vốn là ~73.000 nhưng chỉ mua
được bằng 10.000 kia. Tính kích thước vị thế trên vốn tổng thì mọi lệnh đều bị
sàn từ chối vì thiếu số dư — sau khi đã tốn một lượt gọi model. Nên broker khai
thêm `availableQuote` và Risk Engine cắt trần notional theo con số đó.

Sàn giấy không bao giờ chỉ ra chuyện này vì nó chỉ giữ đúng một con số.

### Khi thấy `MAX_POSITIONS` mà trên sàn không có gì

Đó là **vị thế ma**: sổ cục bộ còn, sàn đã phẳng. Xảy ra khi runtime chết giữa
chừng. Chạy:

    python scripts/doi-so.py --don

Sàn luôn đúng; sổ cục bộ chỉ là bản chép.

Xem cung tĩnh ở máy: `node server.js 5181` từ gốc repo, rồi mở
`http://localhost:5181/tu-cam-thanh/`.

Không có `ANTHROPIC_API_KEY` thì brain tự chạy chế độ **mock** (suy luận bằng luật,
không tốn tiền). Mọi tầng khác — dữ liệu, chỉ báo, regime, risk engine, sàn giấy,
nhật ký, hậu kiểm — chạy y hệt. Muốn bật Claude:

```bash
cp .env.example .env        # rồi điền ANTHROPIC_API_KEY
python run.py
python run.py --brain=mock  # ép tắt, dù có khoá
```

Cờ khác: `--symbol=ETHUSDT --port=5231 --model=claude-sonnet-5 --loop=30`

**Tiền giả. Sàn giấy. Đừng nối vào tài khoản thật ở mốc này.**

## Cỗ máy tuần hoàn

```
THẾ GIỚI → MARKET DATA → FEATURE FACTORY → MARKET STATE / REGIME
    → CLAUDE BRAIN  (+ MEMORY + SKILLS) → TRADE THESIS
    → RISK ENGINE → chấp nhận / TỪ CHỐI → EXECUTION
    → RESULT → JOURNAL → POST-MORTEM → LESSON → MEMORY ↺
```

Dashboard vẽ đúng sơ đồ này và tô sáng từng ô khi nó phát sự kiện.

## Bức tường cứng

`trader/risk.py` là Python thuần, không gọi model, không đọc mạng. Nó **không
tranh luận với Claude**:

| Luật | Trị số | Ở đâu |
|---|---|---|
| Rủi ro mỗi lệnh | ≤ 0.5% vốn | `maxRiskPerTradePct` |
| RR tối thiểu (tính trên TP1, **sau phí + trượt giá**) | 2.0 | `minRR` |
| Khoảng stop | 0.3–3 × ATR | `minStopAtr` / `maxStopAtr` |
| Trần lỗ ngày | 2% → nghỉ tới 00:00 UTC | `maxDailyLossPct` |
| Kill switch drawdown | 10% từ đỉnh → dừng hẳn | `maxDrawdownPct` |
| Vị thế mở đồng thời | 1 | `maxOpenPositions` |

`confidence = 0.99` không mua được thêm một xu rủi ro nào. Brain đề xuất
`suggested_risk_pct`; Risk Engine **tính lại size từ đầu** và cắt trần.
`selftest.py` chứng minh điều đó bằng một luận điểm xin 25% vốn.

## Ba thứ tìm ra khi dựng, đã sửa

**1. Sổ ghi rủi ro theo giá yêu cầu, không theo giá khớp.** R-multiple là tín hiệu
học chính của hậu kiểm. Ghi theo giá yêu cầu là mọi bài học đều dựa trên một mẫu
số đẹp hơn thực tế — và không có gì báo. Giờ ghi theo giá khớp.

**2. Ngưỡng "RR ≥ 2.0" từng là hư cấu.** Đo thật trên BTC 1H: RR danh nghĩa 2.0
chỉ còn **1.15** sau 15bps phí + trượt giá. Cửa gác một con số không bao giờ xảy
ra, và nó hư cấu theo hướng *cho lệnh đi qua*. Giờ thẩm định trên giá khớp dự kiến.

Hệ quả số học đáng biết: với stop 1.5×ATR và chi phí 15bps, **TP1 phải đặt ở
≈4.8×ATR** mới giữ nổi RR 2.0. Mục tiêu 3×ATR nghe hợp lý nhưng không qua nổi cửa.

**3. Luật "SL quá hẹp" từng chết âm thầm.** Vì đo từ giá khớp, mà riêng trượt giá
đã là 0.6×ATR — tự nó vượt ngưỡng 0.3, nên không stop nào còn bị coi là hẹp. Giờ
tách hai phép đo: **cấu trúc** (stop có nằm trong vùng nhiễu không — đo từ giá
tham chiếu) và **kế toán** (mất bao nhiêu tiền — đo từ giá khớp).

## Chi phí model

Đường ống gọi model theo lịch mà không có trần chi phí thì chuyện duy nhất chưa
xảy ra là hoá đơn chưa về. Nên:

- Brain **không** chạy mỗi vòng lặp. Chỉ thức khi có nến mới đóng, khi regime đổi,
  hoặc khi bấm tay — và cách lần trước tối thiểu `minSecondsBetweenTheses`.
- Regime phân loại bằng **luật xác định**, không tốn token.
- Trần cứng `dailyBudgetUsd` + `maxCallsPerDay`. Vượt là brain tự tắt, vòng lặp
  vẫn chạy ở chế độ NO_TRADE. Đồng hồ hiện ngay trên thanh trên cùng.
- System prompt (luật + kho kỹ năng) được **prompt caching**; dữ liệu biến thiên
  nằm trong message, không nhét vào system prompt.

Mặc định `claude-opus-5`, hạn mức `$5/ngày`, `80 lượt/ngày`. Đổi trong `config.json`.
Muốn rẻ hơn: `--model=claude-sonnet-5` hoặc `claude-haiku-4-5`.

## Bố cục

```
run.py                  khởi động
config.json             mọi trị số — không hardcode ở nơi khác
scripts/selftest.py     kiểm một vòng kín
trader/
  data.py               3 nguồn nến; hỏng hết thì nến tổng hợp + báo đỏ
  indicators.py         EMA RSI MACD ATR ADX Bollinger swing S/R — Python thuần
  features.py           đo, KHÔNG kết luận
  regime.py             gán nhãn bằng luật xác định
  brain.py              Claude + mock + schema + đồng hồ chi phí + THAM_MAC_DINH
  cli_claude.py         đường thứ ba tới model: claude CLI, trả bằng QUOTA GÓI
  risk.py               bức tường cứng
  broker.py             sàn giấy, tính phí và trượt giá thật
  broker_testnet.py     Binance Spot Testnet — lệnh thật, tiền giả
  exchange.py           REST ký HMAC, bù lệch đồng hồ, bộ lọc sàn
  journal.py            5 loại trí nhớ + truy hồi
  chung_cat.py          LÒ CHƯNG CẤT — gộp mọi kho đo thành PHÁT HIỆN, và cầu dao chế độ
  mau_gia.py            13 mẫu biểu đồ kinh điển, nhận diện bằng hình học
  nghi_thuc.py          phép đo nặng tự chạy mỗi 6 tiếng, ở TIẾN TRÌNH riêng
  so_gia_thuyet.py      khai TRƯỚC khi đo, chốt SAU — và giữ cả KẾT QUẢ ÂM
  nguon.py              phái sinh · vĩ mô · tâm lý · tin tức — luồng riêng, không khoá
  huanluyen.py          chạy lại lịch sử, dò tham số, đúc bài học
  phien_hoc.py          một phiên huấn luyện chạy nền, có tiến độ
  loop.py               điều phối
  server.py             HTTP + SSE
  snapshot.py           ghi lát cắt cho cung tĩnh
skills/*/SKILL.md       kho kỹ năng — sửa được mà không phải deploy lại
web/                    buồng lái + chat
data/                   JSONL, gitignore
data/lich-su/           nến lịch sử để huấn luyện, gitignore
data/chuoi/             cache chuỗi tín hiệu, gitignore
```

## Mốc sau

Đã xong: **backtest / replay** (phòng huấn luyện), **dữ liệu phái sinh**
(funding, OI, vị thế top trader) và **tin tức có cấu trúc** — cả ba bằng nguồn
công khai miễn phí. Còn lại, mỗi mốc chỉ thêm một thứ:

1. **Champion / Challenger** — chiến lược mới phải thắng bản đang chạy trên dữ
   liệu ngoài mẫu mới được lên. Phòng huấn luyện đã có đủ phép đo cho việc này;
   thiếu là sổ đăng ký chiến lược có phiên bản và cửa duyệt.
2. Nhiều chiến lược + bộ chọn theo regime. Số liệu theo chế độ đã có sẵn, và nó
   đang chỉ ra chỗ nên bỏ bớt chứ không phải chỗ nên thêm.
3. Chạy lại trên nhiều cặp và nhiều đoạn thời gian — một đoạn sáu tháng chỉ chứa
   vài chế độ thị trường, nên kết luận hiện tại còn hẹp.
4. Mô phỏng nhảy giá qua stop, để bớt lạc quan.
5. Chốt từng phần + trailing.
6. On-chain (ô duy nhất còn trống trong bộ não thị trường — cần nguồn trả phí).

Bot kiểu này không thể biết trước thị trường. Nó chỉ có thể được thiết kế để
**ước lượng xác suất tốt hơn, nhận ra khi mình không biết, kiểm soát hậu quả khi
sai, và học có kiểm chứng từ lịch sử.**
