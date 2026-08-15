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

```bash
pip install -r requirements.txt
python run.py                 # buồng lái: http://localhost:5182
python -m trader.snapshot     # ghi lát cắt một lần rồi thoát
python scripts/selftest.py    # kiểm một vòng kín, không gọi API, không mở cổng
python scripts/sinh-icon.py   # vẽ lại 5 icon PNG của cung
```

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
  brain.py              Claude + mock + schema + đồng hồ chi phí
  risk.py               bức tường cứng
  broker.py             sàn giấy, tính phí và trượt giá thật
  journal.py            4 loại trí nhớ + truy hồi
  loop.py               điều phối
  server.py             HTTP + SSE
skills/*/SKILL.md       kho kỹ năng — sửa được mà không phải deploy lại
web/                    dashboard + chat
data/                   JSONL, gitignore
```

## Mốc sau

M0 mới đóng được vòng. Thứ tự đề nghị, mỗi mốc chỉ thêm một thứ:

1. **Backtest / replay** trên nến lịch sử — bắt buộc trước mọi thứ khác, vì hiện
   chưa có cách nào biết một thay đổi là tốt hơn hay chỉ là khác đi.
2. **Champion / Challenger** — chiến lược mới phải thắng bản đang chạy trên dữ
   liệu ngoài mẫu mới được lên.
3. Nhiều chiến lược + bộ chọn theo regime.
4. Order book, funding, OI (dữ liệu phái sinh).
5. Global Event Engine — tin tức thành dữ liệu có cấu trúc.
6. Chốt từng phần + trailing.
7. Binance Spot **Testnet** (cần key testnet, vẫn không phải tiền thật).

Bot kiểu này không thể biết trước thị trường. Nó chỉ có thể được thiết kế để
**ước lượng xác suất tốt hơn, nhận ra khi mình không biết, kiểm soát hậu quả khi
sai, và học có kiểm chứng từ lịch sử.**
