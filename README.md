# Cổng Thành — SUNSWaGz

Cửa ngõ dẫn vào các cung. Mỗi cung là một web app tĩnh độc lập: **cài được lên máy,
chạy offline, số liệu tự cập nhật, và đóng gói thành app Android/iOS được về sau**.

| cung | là gì | nguồn số liệu |
|---|---|---|
| **/** Cổng Thành | trang cửa ngõ, liệt kê các cung | đọc ngày cập nhật từ chính file của từng cung |
| **/kinh-thanh/** | bản đồ 9 quốc gia Layer 1 | DefiLlama + L2BEAT (14 thành phố thuộc Ethereum) |
| **/dai-quan-trac/** | dòng chảy địa chính trị, 5 chiến trường, 8 đồng hồ | bản quét sinh trong GitHub Actions |
| **/do-sat-vien/** | bản Việt hoá của L2BEAT — 23 mục trong 7 nhóm, đủ cây điều hướng | L2BEAT: API `scaling/summary` + dữ liệu 21 trang |
| **/cong-bo/** | bộ đồ nghề — giải mã lời gọi, nhật ký đổi thay on-chain, kính lúp hồ sơ | L2BEAT: `um-prod/discovery/changes` + `fe-stag/api/discolupe` |
| **/tang-thu-cac/** | kho tra cứu Claude Skills — mỗi skill làm gì, giúp được gì cho bạn | GitHub: `topic:claude-skills` + `anthropics/skills` |

Các file gốc trong `SUNSWaGz app/` không bị đụng vào — vẫn nằm nguyên chỗ cũ để đối chiếu.

Thêm một cung mới = thêm một thư mục + một dòng trong `HALLS` của `scripts/build-dist.mjs`
+ một thẻ ở `index.html` + một dòng trong `halls.js` của các cung khác.

---

## Chạy thử

```bash
cd "D:\SUNSWaGz 2027\SUNSWaGz\kinh-thanh-app"
npm start                 # hoặc: node server.js
```

Mở http://localhost:5173

> Đừng mở thẳng `index.html` bằng `file://` nếu muốn thử offline —
> service worker chỉ hoạt động qua `http://` hoặc `https://`.
> (Mở bằng file:// thì bản đồ vẫn chạy, chỉ là không cài và không offline được.)

Kiểm tra cú pháp toàn bộ JS: `npm run check`

---

## Cấu trúc

```
kinh-thanh-app/
├── index.html                  CỔNG THÀNH — trang cửa ngõ
├── manifest.webmanifest        · tên app, icon, màu
├── sw.js                       · service worker riêng, CỐ Ý không cache các cung
├── assets/{css,js,icons}/      · portal.css, portal.js
│
├── kinh-thanh/                 CUNG 1 — bản đồ 9 quốc gia L1
│   ├── index.html · sw.js · manifest.webmanifest
│   └── assets/
│       ├── css/                app.css, app-shell.css, l2beat.css, provenance.css,
│       │                       passport.css, halls.css, onchain.css
│       ├── icons/              192 / 512 / maskable / apple-touch / favicon
│       └── js/
│           ├── data/chains.js      9 quốc gia L1, các tầng và mục bên trong
│           ├── data/strength.js    số chụp 10/08/2026 + trọng số xếp hạng
│           ├── data/live.js        TỰ SINH — số mới đè lên số chụp
│           ├── data/provenance.js  TỰ SINH — CID + sha256 của bản số liệu
│           ├── data/entities.js    hồ sơ chi tiết từng thành phần
│           ├── data/cities.js      sơ đồ dòng chảy của từng "thành phố" L2
│           ├── app.js              toàn bộ logic giao diện (3 móc có rào)
│           ├── l2beat.js           hồ sơ tự trị của thành phố (Stage, rủi ro)
│           ├── provenance.js       khối "bản số liệu này đóng dấu được"
│           ├── wallets.js          phát hiện ví theo EIP-6963
│           ├── passport.js         hộ chiếu ví — chỉ đọc và personal_sign
│           ├── pulse.js            nhịp tim realtime qua WebSocket RPC
│           ├── halls.js            thanh bên gập được + lối sang cung khác
│           └── pwa.js              service worker, nút cài, báo bản mới
│
├── dai-quan-trac/              CUNG 2 — dòng chảy địa chính trị
│   └── assets/js/{data.js, app.js, scan.js(TỰ SINH), halls.js, pwa.js}
│
├── do-sat-vien/                CUNG 3 — bản Việt hoá L2BEAT, 23 mục
│   ├── index.html · sw.js · manifest.webmanifest
│   └── assets/
│       ├── logos/              200 logo tải từ L2BEAT (~990 KB)
│       └── js/
│           ├── data.js         TỰ SINH — 106 dự án + từ điển + biểu đồ (~246 KB)
│           ├── v/<mã>.js       TỰ SINH — 21 mục, NẠP THEO YÊU CẦU
│           ├── glossary.js     bản dịch + diễn giải, SỬA TAY được
│           ├── app.js          định tuyến hash, sidebar, bộ máy bảng, 23 màn hình
│           └── halls.js · pwa.js
│
├── cong-bo/                    CUNG 4 — bộ đồ nghề, Việt hoá tools.l2beat.com
│   ├── index.html · sw.js · manifest.webmanifest   (nền tối như bản gốc)
│   └── assets/js/
│       ├── data.js         TỰ SINH — 460 thay đổi + 198 dự án (~129 KB)
│       ├── v/nhat-ky.js    TỰ SINH — nguyên văn diff (~797 KB), NẠP THEO YÊU CẦU
│       ├── logos.js        TỰ SINH — bảng tra id → logo, ảnh dùng chung Đô Sát Viện
│       ├── decoder.js      bộ giải mã calldata, TỰ VIẾT, chạy trong trình duyệt
│       ├── glossary.js     bản dịch, SỬA TAY được
│       └── app.js · halls.js · pwa.js
│
├── tang-thu-cac/               CUNG 5 — kho tra cứu Claude Skills
│   ├── index.html · sw.js · manifest.webmanifest   (nền giấy ngà)
│   └── assets/js/
│       ├── data.js         TỰ SINH — 321 skill + 61 kho (~230 KB)
│       ├── glossary.js     dịch tay 17 skill chính thức, SỬA TAY được
│       └── app.js · halls.js · pwa.js
│
├── server.js                   máy chủ tĩnh, không phụ thuộc gói nào
├── package.json
├── scripts/
│   ├── build-live.mjs          DefiLlama → kinh-thanh/.../live.js
│   ├── build-l2beat.mjs        L2BEAT    → do-sat-vien/.../data.js
│   ├── build-congbo.mjs        công cụ   → cong-bo/.../data.js
│   ├── build-tangthu.mjs       GitHub    → tang-thu-cac/.../data.js
│   ├── build-scan.mjs          model     → dai-quan-trac/.../scan.js
│   ├── build-dist.mjs          gom cổng + các cung thành dist/, kèm 3 lớp kiểm tra
│   ├── pin-ipfs.mjs            pin cả site
│   ├── pin-snapshot.mjs        đóng dấu riêng bản số liệu (~1,8 KB)
│   └── check.mjs               kiểm cú pháp toàn bộ JS
└── .github/workflows/
    ├── refresh-data.yml        mỗi 6 giờ: build-live + l2beat + congbo + tangthu
    ├── scan-observatory.yml    mỗi 6 giờ: build-scan rồi commit
    ├── deploy-pages.yml        đóng gói dist/ → GitHub Pages
    └── deploy-ipfs.yml         đóng gói dist/ → IPFS
```

> **`paths:` của hai workflow deploy phải liệt kê từng cung.** Sau khi tách thư mục,
> `assets/**` chỉ còn khớp assets của Cổng Thành — sửa app trong một cung mà quên
> thêm `<cung>/**` thì thay đổi **không bao giờ lên site, và không có lỗi nào báo**.
> Đã dính đúng lỗi này một lần với commit realtime pulse.

### Vì sao tách như vậy

Dữ liệu và logic tách hẳn ra. Muốn thêm một quốc gia, sửa một chỉ số hay viết
thêm hồ sơ cho một dự án thì chỉ động vào `assets/js/data/` — không phải cuộn qua
hàng nghìn dòng để tìm chỗ.

Các file dữ liệu là script thường (không phải ES module), nạp theo thứ tự trong
`index.html` và gắn kết quả vào `window.KT_DATA`. `app.js` đọc lại từ đó ở đầu file.
Không có bước build, không có bundler — sửa file, F5 là thấy.

`app.js` giữ nguyên từng dòng của bản gốc, chỉ đổi phần khai báo dữ liệu ở đầu.
`app.css` cũng là bản chép nguyên. Mọi thứ thêm cho app đều nằm riêng trong
`app-shell.css` và `pwa.js` — bỏ hai file này đi thì quay lại đúng bản web ban đầu.

---

## Những gì đã thêm so với bản gốc

| | |
|---|---|
| **Cài được** | Chrome/Edge trên Android và desktop hiện nút "Cài ứng dụng" ở chân thanh bên. iOS: Safari → Chia sẻ → Thêm vào MH chính. |
| **Chạy offline** | Service worker lưu sẵn toàn bộ vỏ app ngay lần mở đầu. Phông chữ Google được lưu khi dùng lần đầu. |
| **Báo bản mới** | Khi phát hành bản mới, app hiện toast "Đã có bản mới · Tải lại". |
| **Toàn màn hình** | `display: standalone` — mở ra không có thanh địa chỉ, giống app thật. |
| **Vùng an toàn** | Chừa chỗ cho tai thỏ và thanh cử chỉ trên iPhone/Android. |
| **Lối tắt** | Nhấn giữ icon app → nhảy thẳng vào Bảng xếp hạng, Ethereum, Solana. |

Số liệu TVL vẫn gọi thẳng DefiLlama như cũ; service worker **không** cache API đó,
nên nút "cập nhật số" luôn lấy số mới.

---

## Số liệu tự cập nhật

Bảng xếp hạng không còn đóng băng ở ngày 10/08/2026 nữa.

`.github/workflows/refresh-data.yml` chạy **mỗi 6 giờ**, gọi DefiLlama, rồi commit đè
`assets/js/data/live.js`. File đó nạp **sau** `strength.js` và đè số mới lên số chụp.

Chạy tay: `npm run refresh`

### Chỉ số nào sống, chỉ số nào không

| Chỉ số | Trạng thái | Nguồn |
|---|---|---|
| Vốn khoá (TVL) | **tự cập nhật** | `api.llama.fi/v2/chains` |
| Tiền lưu hành | **tự cập nhật** | `stablecoins.llama.fi/stablecoinchains` |
| Hệ sinh thái | **tự cập nhật** | `api.llama.fi/protocols`, đếm theo chuỗi |
| Hoạt động (địa chỉ 24h) | đóng băng | chưa có nguồn miễn phí phủ cả 9 nước |
| Phi tập trung | đóng băng | là đánh giá, không phải số đo |

Từ 1/5 chỉ số sống lên **3/5**. Hai chỉ số còn lại được ghi rõ lý do trong
`live.js` (khoá `frozen`) để sau này không ai phải đoán.

### Vì sao sinh file `.js` chứ không phải `.json` + fetch

`app.js` tính điểm **đồng bộ ngay khi tải xong**. Nếu số liệu đến bằng `fetch`
thì bảng xếp hạng sẽ vẽ bằng số cũ rồi mới nhảy — hoặc phải sửa `app.js`.
Nạp `live.js` như script thường thì số đã sẵn sàng trước khi `app.js` chạy dòng đầu tiên,
và **không phải đụng một dòng nào trong `app.js`**.

### Ba tính chất đã kiểm chứng

- **Hỏng một nguồn thì giữ số cũ của nguồn đó**, không xoá trắng — build chạy trong
  cron, không ai canh. Hỏng cả ba nguồn thì thoát với mã lỗi và không ghi gì.
- **Xoá `live.js` đi app vẫn chạy**, tự quay về số chụp 10/08/2026 (đã thử: 9/9 nước
  vẫn render, điểm về đúng bộ cũ).
- **Service worker lấy `live.js` theo kiểu mạng-trước**, ngược với phần còn lại của app.
  Số liệu đổi mỗi 6 giờ nên phải hỏi mạng; hỏng mạng mới dùng bản đã lưu.

### Cạm bẫy tên chuỗi

Mỗi endpoint của DefiLlama gọi cùng một chuỗi một kiểu khác nhau:

| | `/v2/chains` | `stablecoinchains` | `/protocols` |
|---|---|---|---|
| BNB Chain | `BSC` | `BSC` | **`Binance`** |

Dùng nhầm `BSC` cho `/protocols` thì được **0** giao thức mà **không có lỗi nào** —
chỉ số âm thầm về 0 và tụt hạng. Vì vậy bảng `MAP` trong `build-live.mjs` khai báo
tên **riêng cho từng endpoint**, và build luôn in ra dòng `KHÔNG khớp tên` khi trượt.

Cosmos và Polkadot không tồn tại như một "chuỗi" trong API — chúng là liên minh,
nên được cộng dồn từ danh sách thành viên (`AGG`). Build in ra tỉ lệ khớp
(`gộp 14/18 thành viên`) để bạn biết con số đang thiếu bao nhiêu.

### Khi bật trên GitHub

- Repo cần bật quyền ghi cho Actions: **Settings → Actions → General → Workflow
  permissions → Read and write**.
- Nếu `kinh-thanh-app` **không** phải gốc repo, thêm `working-directory` vào bước
  "Lấy số mới" và sửa đường dẫn trong bước commit.
- GitHub **tự tắt workflow theo lịch sau 60 ngày repo không có hoạt động nào**.
  Mỗi lần cron commit cũng tính là hoạt động, nên thực tế nó tự nuôi chính nó.

---

## Hồ sơ tự trị của thành phố (L2BEAT)

Mỗi thẻ thành phố trên bản đồ có huy hiệu **S0 / S1 / S2**, và mở trang thành phố
sẽ thấy khối hồ sơ ngay dưới tên: thang tự trị, tài sản đang giữ, và **5 dòng rủi ro**.

Đây không phải số liệu trang trí — nó trả lời đúng câu hỏi trung tâm của bản đồ này:
*thành phố tự trị đến đâu, và ai đang thật sự cầm chìa khoá.* Ví dụ Base hiện
`Stage 1` với bốn dòng xanh nhưng **"Cửa thoát khi bị nâng cấp: None"** màu đỏ —
một câu tóm gọn cả điểm mạnh lẫn điểm yếu mà đoạn văn mô tả không nói ra được.

Năm nhãn của L2BEAT được dịch theo phép ví kinh thành, bảng dịch nằm ở đầu
`l2beat.js` (`RISK_VI`). Di chuột vào từng dòng hiện mô tả gốc tiếng Anh của L2BEAT.

### Chỉ nhận thành phố thuộc Ethereum — và vì sao

L2BEAT chỉ chấm lớp mở rộng của Ethereum. Bản đầu tôi quét cả 9 nước thì khớp
17/56, nhưng trong đó có **ba cái sai**:

| app | khớp nhầm thành |
|---|---|
| `basechain` của TON | **Base**, L2 của Ethereum — Stage 1, $11.6b |
| `phala` của Polkadot | dự án trùng tên bên Ethereum |
| `eclipse` (app xếp dưới Solana) | Eclipse L2 — đúng dự án nhưng sai ngữ cảnh |

Gán "Stage 1 · $11.6b" cho basechain của TON là bịa số. Nên builder chỉ lấy thành
phố thuộc `eth`: **khớp 14/14, không còn nhầm lẫn**.

Với thành phố của nước khác (Moonbeam, Osmosis, opBNB…), app hiện một ghi chú
giải thích **vì sao không có thang** — bản thân điều đó là một thông tin, không
phải chỗ trống.

### Hai móc trong app.js

Đây là lần đầu `app.js` không còn là bản chép nguyên của file gốc. Nó nhận đúng
**hai dòng**, cả hai đều có rào:

```js
if (window.KT_L2B) window.KT_L2B.badge(b, item, ctx);        // trong makeCard()
if (window.KT_L2B) window.KT_L2B.section(frame, city.n, P.id); // trong openCity()
```

Xoá `l2beat.js` đi thì hai dòng này tự vô hiệu. **Đã thử với profile trình duyệt
sạch: 0 markup `l2b-`, trang thành phố vẫn render đủ 32 ô.** Toàn bộ logic hiển
thị nằm trong `l2beat.js` + `l2beat.css`, không rải rác vào `app.js`.

---

## Đô Sát Viện — bản Việt hoá của L2BEAT

`/do-sat-vien/` dựng lại **toàn bộ cây điều hướng của l2beat.com** bằng tiếng Việt:
23 mục trong 7 nhóm, sidebar nhiều cấp, biểu đồ, ba tab, rosette 5 cánh, logo dự án.

Chạy tay: `npm run l2beat` · chạy lại riêng vài mục: `npm run l2beat -- rui-ro zk`

| nhóm | mục |
|---|---|
| **Lớp 2** | Tổng quan · Rủi ro (Tổng hợp, Kiểm chứng trạng thái, Dữ liệu sẵn có, Xếp thứ tự) · Hoạt động · Độ sống · Đã ngừng |
| **Liên thông** | Tổng quan · Khung token · Cầu ý định |
| **Quyền riêng tư** | Quyền riêng tư |
| **Dữ liệu sẵn có** | Tổng quan · Rủi ro · Thông lượng · Độ sống · Đã ngừng |
| **Bằng chứng** | Danh mục ZK |
| **Hệ sinh thái** | Arbitrum Orbit · The Elastic Network · Superchain · Agglayer |
| **Tra cứu** | Từ điển (120 thuật ngữ) |

**Chưa có: Chi phí.** Trang `/scaling/costs` của L2BEAT chỉ trả về thứ tự sắp xếp
trong SSR; số tiền thật đến từ một lời gọi phía trình duyệt mà tôi chưa lần ra.
Đưa vào mà để cột trống thì tệ hơn là không đưa.

### Hai nguồn, và vì sao phải cả hai

| | API `/api/scaling/summary` | HTML mỗi trang → `window.__SSR_DATA__` |
|---|---|---|
| cho gì | `tvs.breakdown`, `tvs.change7d`, `chart` | 21 mục còn lại + logo + từ điển 120 thuật ngữ |
| tính chất | giao diện công khai, ổn định | **dữ liệu nội bộ của trang, không cam kết gì** |
| vai | **bắt buộc** | làm giàu thêm |

L2BEAT đổi cấu trúc trang là nguồn 2 gãy. Build **không** coi đó là lỗi chí mạng:
mục nào hỏng thì giữ nguyên file cũ của mục đó, in cảnh báo, và app hiện dải nhắc
ở đầu trang liệt kê đúng những mục chưa lấy được. Số của trang tổng quan vẫn đúng
vì luôn lấy từ nguồn 1.

L2BEAT nấp sau Cloudflare, gọi dồn là `error code: 1015`. Build thử lại 3 lần với
khoảng nghỉ tăng dần, nghỉ 2,2 giây giữa các trang và 120 ms giữa mỗi logo. Cron
4 lần/ngày không bao giờ chạm ngưỡng; chạy tay liên tiếp thì có — lúc đó dùng
`npm run l2beat -- <mã mục>` để chỉ lấy lại phần hỏng.

### Nạp theo yêu cầu, không nhồi một cục

Gộp cả 21 mục vào một file là ~1 MB. Thay vào đó:

```
assets/js/data.js      246 KB  chỉ mục chung: 106 dự án, từ điển, biểu đồ
assets/js/v/<mã>.js    1–120 KB  từng mục, chèn <script> khi người dùng bấm vào
assets/logos/          200 logo, ~990 KB
```

Service worker **cố ý không** nạp sẵn `v/*.js` và logo vào SHELL — gấp ba dung lượng
cài để lấy về thứ phần lớn người dùng không mở. Cả hai rơi vào nhánh cache-trước-
cập-nhật-nền, xem tới đâu lưu tới đó. `build-dist.mjs` bỏ qua chúng khi kiểm SHELL,
và ghi rõ lý do tại chỗ.

Định tuyến bằng **hash** (`#/rui-ro`) chứ không phải History API: trang này còn được
pin lên IPFS, mà gateway IPFS không có server để rewrite URL.

### Ba nguyên tắc của bản dịch

**1. Không bịa nghĩa.** Nhãn nào `glossary.js` chưa có thì hiện **nguyên bản tiếng
Anh** kèm dấu `chưa dịch`. Mỗi dòng rủi ro kèm `<details>` mở ra mô tả gốc. Riêng
mục *"còn thiếu gì để lên thang sau"* và **từ điển 120 thuật ngữ** cố ý giữ nguyên
tiếng Anh — đó là tiêu chí kỹ thuật L2BEAT dùng để chấm và định nghĩa mật mã học;
dịch ra dễ làm sai lệch hơn là giúp.

**2. Không tự chấm điểm.** Mọi đánh giá rủi ro là của L2BEAT.

**3. Mỗi nhãn trả lời "với người gửi tiền thì sao".** `glossary.js` cho mỗi mục ba
phần: `nhan` (nhãn tiếng Việt), `y` (nghĩa kỹ thuật), `vn` (hệ quả với người gửi tiền).
Hiện phủ 17 chiều rủi ro, 80 giá trị, 23 tên mục.

### Bốn cạm bẫy đã xử lý

**Cùng một chữ, hai nghĩa.** L2BEAT dùng lại `"None"` cho nhiều chiều: ở State
Validation nghĩa là không ai kiểm chứng sổ sách, ở Exit Window nghĩa là nâng cấp có
hiệu lực ngay. Bảng tra phẳng gán nhầm nghĩa thứ nhất cho cả hai mà trông vẫn rất
hợp lý. `giaTheoChieu` tra **trước** bảng chung.

**Cùng một chiều, hai cách viết.** Trang rủi ro DA gọi `committeeSecurity`, trang
tổng quan DA gọi `Committee security`. Khai cả hai cách — rẻ hơn chuẩn hoá khoá lúc
build rồi lỡ sót một chỗ.

**Rủi ro tới ở hai hình.** Mảng `[{name, value}]` ở trang scaling, object
`{economicSecurity: {...}}` ở hai trang DA. `rrArr()` nhận cả hai.

**Dấu "chưa dịch" đóng nhầm lên số đo.** Nhãn liệt kê của L2BEAT không bao giờ chứa
chữ số; thứ có số luôn là số đo (`"9d"`, `"1/2"`, `"3466 sequencers"`). Nên quy tắc
là: **có chữ số thì không đóng dấu.** Đóng dấu lên một con số chỉ làm người đọc
tưởng trang bị lỗi.

### Cột bảng suy từ dữ liệu, không chép cứng

Ba mục Dữ liệu sẵn có dùng chung một hàm dựng bảng. Cột rủi ro lấy **hợp của mọi
hàng đang hiện** rồi tra theo **tên** chiều, không theo vị trí — mỗi lớp dữ liệu
khai một bộ chiều khác nhau, lấy theo hàng đầu thì vừa thiếu chiều vừa trùng tên
cột. Chiều nào dịch ra trùng nhãn với cột đã có thì bỏ (`DA Layer` → "Lớp dữ liệu",
đúng tên cột chứa tên hàng).

### Hai con số khác nhau, cả hai đều đúng

| | |
|---|---|
| **$33.53b** — thẻ "Tài sản đang giữ" | chỉ cộng chuỗi **tầng 2**. Khớp đúng tiêu đề L2BEAT. |
| **$39.47b** — thẻ "Tiền vào bằng đường nào" | cộng cả **tầng 3**. Chênh lệch gần như toàn bộ là Hyperliquid ($5.86b, tầng 3). |

Đã truy ra nguyên nhân nên nói thẳng trên trang (`VI.ghiChuTong`) thay vì để người
đọc tưởng số liệu sai. Ba tab cũng là lý do thứ hạng nhìn khác bản gốc: tab mặc định
là **Rollup**, không tính Hyperliquid hay Polygon PoS — giống hệt L2BEAT.

### Mốc thời gian của biểu đồ

`chart` trả 122 điểm nhưng lấy mẫu **6 giờ một lần**, tức 30 ngày chứ không phải 122
ngày. Nhãn tính khoảng thời gian từ chính mốc `timestamp`, không suy từ số điểm —
suy từ số điểm là sai gấp bốn lần.

Nhãn trục tung dựng bằng **HTML đè lên SVG**, không phải `<text>` bên trong: svg đó
có `preserveAspectRatio="none"` để giãn hết bề ngang, nên mọi thứ bên trong bị kéo
méo theo — thử thêm viền trắng cho `<text>` thì nhãn thành một vệt trắng còn khó đọc
hơn lúc chưa sửa.

### Logo lưu trong repo, không hotlink

200 logo tải về `do-sat-vien/assets/logos/`. URL của L2BEAT có hash nội dung
(`base.4840b6b2.png`) nên tên file đổi nghĩa là ảnh đổi — build bỏ qua file đã có,
chỉ tải cái mới. Hotlink thẳng sẽ hỏng khi họ đổi hash, và cũng là ăn băng thông
của người ta.

### Cổng Thành đọc ngày cập nhật mà không tải cả file

`data.js` nặng ~246 KB, nhưng ngày và số dự án đều nằm trong ~900 byte đầu.
`portal.js` đọc một khúc bằng `body.getReader()` rồi `cancel()` luôn dòng tải.
Trình duyệt không có streams thì rơi về `r.text()`.

### Vì sao cung này trông khác hai cung kia

Kinh Thành và Đài Quan Trắc dùng nền giấy sáng + chàm. Đô Sát Viện dùng nền xám lạnh,
Roboto, accent hồng sen — vì đây là bản dựng lại có chủ ý theo L2BEAT, không phải sơ
suất. Đổi về phong cách chung thì sửa `:root` trong `do-sat-vien/assets/css/app.css`
và font ở `index.html`; markup và JS không phải động vào.

---

## Công Bộ — bộ đồ nghề (Việt hoá tools.l2beat.com)

`/cong-bo/` khác ba cung kia ở chỗ: **đây không phải trang dữ liệu để dịch mà là bộ
công cụ cho thợ.** "Việt hoá" ở đây nghĩa là dựng lại, không phải chép chữ. Nền tối
theo đúng bản gốc (họ dùng `zinc-950`).

Chạy tay: `npm run congbo`

| công cụ | làm gì | nguồn |
|---|---|---|
| **Giải mã lời gọi** | dán calldata → tên hàm + từng tham số | **tự viết**, chạy trong trình duyệt |
| **Nhật ký đổi thay** | 460 thay đổi hợp đồng on-chain, 83 dự án, 30 ngày | `um-prod.l2beat.com/discovery/changes` |
| **Kính lúp hồ sơ** | 198 dự án × 11 hạng mục, ai còn bỏ trống gì | `fe-stag.l2beat.com/api/discolupe` |

### Vì sao bộ giải mã tự viết

L2BEAT có sẵn `tools-api.l2beat.com/api/decode`, **nhưng nó đang trả 500** — thử cả
POST đúng dạng vẫn vậy. Mà việc này vốn không cần máy chủ: bóc 4 byte đầu làm
selector, tra tên hàm, rồi đọc tham số theo quy tắc mã hoá ABI.

Chỉ một chỗ cần mạng là tra tên hàm từ selector. Dùng **api.openchain.xyz** (có CORS)
và có **29 hàm tra sẵn** trong `decoder.js`, nên phần lớn lời gọi thường đọc được
ngay cả khi mất mạng.

**Không dùng 4byte.directory** dù nó phổ biến hơn: nó không trả header CORS nên
trình duyệt chặn thẳng.

Đọc được mọi kiểu tĩnh (`uintN`, `intN`, `address`, `bool`, `bytesN`) và kiểu động
một tầng (`string`, `bytes`, `T[]`). **Tuple lồng nhau thì báo "chưa đọc được" chứ
không đoán bừa** — đọc sai một tham số còn tệ hơn nói thẳng là không đọc được.

### Nguồn mong manh, nói thẳng

`fe-stag` là host **staging** của L2BEAT, không phải bản chính thức — có thể đổi hoặc
tắt bất cứ lúc nào mà không ai nợ mình lời báo trước. Nên cùng cách xử lý như
`build-l2beat.mjs`: hỏng thì giữ bản cũ, in cảnh báo, và app hiện dải nhắc ở đầu
trang nói rõ mục nào đang là bản cũ.

### Hai công cụ đã bỏ, và vì sao

| | |
|---|---|
| **Simulator** | cần khoá Tenderly (`tdly.co`) — không có thì chỉ là nút chết |
| **Logo generator** | dùng để làm nhận diện cho chính L2BEAT, không có việc gì ở đây |

Thà bỏ hẳn còn hơn để một nút bấm vào không ra gì — đúng lỗi mà bản gốc
`dai-quan-trac.html` từng mắc với nút "Quét trực tiếp".

### Tiết kiệm chỗ

```
data.js          129 KB  nạp đầu: tóm tắt 460 thay đổi + 198 dự án
v/nhat-ky.js     797 KB  nguyên văn diff, chỉ nạp khi mở một diff
logos.js           4 KB  bảng tra id → tên file
```

Diff dài nhất trong một lần chạy là **436 KB** — một hợp đồng bị dựng lại toàn bộ.
Cắt ở 6 KB và ghi rõ đã cắt, kèm liên kết sang bản đầy đủ.

200 logo **dùng chung với Đô Sát Viện** qua bảng tra `id → tên file`; ảnh vẫn nằm ở
`do-sat-vien/assets/logos/`. Chép sang đây là nhân đôi 1 MB trong repo mà chẳng được gì.

### Hai lỗi shell đáng nhớ

Cả hai đều do chèn nội dung qua `node -e`, và **cả hai đều hỏng lặng lẽ**:

- **YAML**: `\n` trong chuỗi thành hai ký tự thật, làm hỏng lệnh `git add` nhiều dòng
  trong workflow — lỗi chỉ lộ khi Actions chạy.
- **Regex**: shell nuốt một tầng backslash, `\s*` thành `s*` và `\d+` thành `d+`.
  Thẻ ở Cổng Thành im lặng không hiện số, không báo lỗi gì.

Cách chữa: viết ra file `.mjs` rồi chạy, đừng nhét chuỗi có backslash qua `node -e`.

---

## Tàng Thư Các — kho tra cứu Claude Skills

`/tang-thu-cac/` giải một vấn đề rất cụ thể: **skill thì hàng trăm, mà tên như
`pdf` hay `mcp-builder` chẳng nói được gì.** Mô tả gốc lại viết cho MÁY đọc — nó
trả lời "khi nào agent nên tự bật skill này", không trả lời "cái này giúp gì cho tôi".

Chạy tay: `npm run tangthu` · quét nhiều kho hơn: `TT_SO_KHO=40 npm run tangthu`

### Bốn phần cho mỗi skill

| phần | trả lời |
|---|---|
| **Nó là gì** | một câu |
| **Làm được gì** | danh sách việc cụ thể |
| **Khi nào Claude tự bật nó** | điều kiện kích hoạt |
| **Với hệ thống của bạn** | gắn vào đúng việc đang làm ở repo này |

Phần thứ tư là thứ không kho skill nào khác có. Ví dụ `webapp-testing`:

> *Chính là việc tôi vẫn làm tay suốt: mở trình duyệt thật, quét 23 mục của Đô Sát
> Viện, đọc console, chụp ảnh. Skill này gói việc đó lại thành quy trình sẵn.*

### Trung thực về độ phủ

| | |
|---|---|
| **17 skill chính thức của Anthropic** | dịch và diễn giải tay trong `glossary.js` |
| **304 skill cộng đồng** | giữ nguyên mô tả tiếng Anh, gắn nhãn **"chưa dịch tay"** |

Bịa mô tả tiếng Việt cho skill chưa đọc kỹ còn tệ hơn để nguyên bản.

### Cập nhật từ GitHub — khác bốn cung kia

`api.github.com` có CORS mở, nên trang này **gọi thẳng được từ trình duyệt**:

- **Bản chụp lúc build** luôn có sẵn — mở là thấy ngay, offline vẫn xem được
- **Nút "Làm mới"** lấy số sao mới nhất tại chỗ, không cần chờ cron

Hạn mức 60 lượt/giờ mỗi IP (không token), quá đủ cho một người. Hết hạn mức thì
chỉ mất phần làm mới chứ **không mất bản chụp**.

Trong Actions, `GITHUB_TOKEN` nâng hạn mức lên 5.000/giờ — nên workflow quét được
40 kho thay vì 6.

### Quét thế nào cho rẻ

```
1 lời gọi   search/repositories?q=topic:claude-skills   → bảng xếp hạng
N lời gọi   git/trees/<nhánh>?recursive=1               → MỘT lời gọi lấy cả cây repo
M lần tải   raw.githubusercontent.com/.../SKILL.md      → CDN, KHÔNG tính hạn mức
```

Phần nặng nhất (đọc hàng trăm file SKILL.md) lại là phần rẻ nhất, vì `raw.*` không
qua API. Script tự dừng quét khi hạn mức xuống dưới 5 lượt thay vì đâm vào lỗi 403.

### Ba lỗi đã bắt

**Kho chính thức không nằm trong kết quả tìm.** `anthropics/skills` gắn thẻ
`agent-skills` chứ **không phải** `claude-skills`, nên tìm theo topic không ra nó —
bảng đầu tiên tôi dựng có **0 skill chính thức**. Giờ có danh sách `LUON_CO` nạp
thẳng, không trông vào kết quả tìm kiếm.

**Frontmatter dạng block scalar.** `description: |-` rồi nội dung thụt vào dòng
dưới — không xử lý thì mô tả của `claude-api` bắt đầu bằng đúng hai ký tự `|-`.

**Phân nhóm sai vì xét mô tả trước tên.** `canvas-design` có chữ `.pdf` trong mô tả
nên bị xếp thành công cụ tài liệu. Sửa: xét **tên trước mô tả**, và nhóm hẹp
(`kiem-thu`) đứng trước nhóm rộng (`giao-dien`, `tai-lieu`) trong bảng luật.

Nhóm `khac` luôn xuống cuối màn Tổng quan dù đông nhất — nhóm rác dẫn đầu thì trông
như chưa phân loại được gì.

### Vì sao chỉ làm Claude Skills

Ba hệ khác nhau về cả định dạng lẫn cách cài:

| | định dạng | cài kiểu gì |
|---|---|---|
| Claude Skills | thư mục có `SKILL.md` | chép vào `~/.claude/skills/` hoặc marketplace |
| ChatGPT GPTs | cấu hình trên nền tảng OpenAI | không tải về được |
| GitHub Copilot | `.github/` + extension | khác hẳn |

Gộp một bảng thì trông gọn mà dùng thì sai. Làm sâu một hệ hơn làm nông ba hệ.

## Phát hành bản mới

1. Sửa file trong `assets/`.
2. Mở `sw.js`, tăng `CACHE_VERSION` (`"v1"` → `"v2"`).

Bỏ qua bước 2 thì máy người dùng vẫn chạy bản cũ đã lưu trong cache.

### Đưa lên mạng (cách thường)

Thư mục này là web tĩnh thuần — kéo thả lên Netlify, Vercel, Cloudflare Pages
hoặc GitHub Pages là chạy. Chỉ cần **HTTPS** (bắt buộc cho service worker).

Nếu đặt trong thư mục con (ví dụ `example.com/kinh-thanh/`) thì mọi đường dẫn đã
là tương đối sẵn, không phải sửa gì.

---

## Ba lớp hạ tầng, ba vai khác nhau

| lớp | vai | chi phí |
|---|---|---|
| **GitHub Pages** | nơi người dùng mở app hằng ngày, cài lên điện thoại | miễn phí |
| **IPFS / Pinata** | bản lưu bất biến + đóng dấu số liệu | miễn phí |
| **Base / ENS** | neo lên chuỗi, tên miền web3 | tốn gas — **để sau** |

App **chạy được ngay** chỉ với hai lớp đầu. Lớp thứ ba nối vào lúc nào cũng được,
không phải làm lại gì.

Bật GitHub Pages: **Settings → Pages → Source = GitHub Actions**. Xong thì mỗi lần
số liệu đổi, `refresh-data.yml` tự gọi cả hai workflow deploy.

### Pinata thật sự cho những gì

Dò bằng API trên tài khoản thật:

| | |
|---|---|
| Pinning + dung lượng | ✅ dùng được |
| Files API v3 | ✅ dùng được |
| Gateway `*.mypinata.cloud` | ⚠️ `custom_domains: []` → **chặn HTML**, chỉ phục vụ CSS/JS/JSON |
| IPNS | ❌ 404 |
| Groups / Farcaster | ❌ 404 |

Nên đừng trông chờ Pinata làm chỗ chạy app. Nó là **kho lưu**, và đó mới là chỗ
nó có giá trị thật — xem mục dưới.

---

## Đóng dấu số liệu (`npm run snapshot`)

Vấn đề: hôm nay bảng xếp hạng nói Ethereum 97 điểm. Ba tháng nữa **không gì chứng
minh được hôm nay nó đúng là 97** — `live.js` bị ghi đè mỗi 6 giờ, còn git history
thì ai có quyền đẩy cũng sửa được.

`scripts/pin-snapshot.mjs` pin mỗi bản số liệu thành một CID riêng. CID **chính là
hash của nội dung**, đổi một chữ số là ra CID khác. Đây đã là tính chất web3 thật,
**không tốn một đồng gas**.

Bản đầu tiên, đã kiểm chứng thật:

```
ngày 12/08/2026 · 9 quốc gia · 14 thành phố · 1.786 byte
CID     bafkreie4mazfwj5dqwd4rbbptkjhfzc4xmh665gfmrd5bhhl4druz5zzay
sha256  9c60325b27a38587c8842f9a9272e45cbb0fef74c56447d09cebe0e34cf73906
```

Tải lại từ IPFS rồi băm lại → **khớp**. Ethereum hôm đó $41.61b, Base Stage 1 $11.69b.

Chỉ đóng dấu phần **số**, bỏ vài chục KB mô tả tiếng Anh của L2BEAT — muốn chứng minh
"hôm đó TVL bao nhiêu" thì không cần kèm văn bản. Nhờ vậy mỗi bản chỉ ~1,8 KB:
4 bản/ngày trong một năm cũng chưa tới 3 MB.

Chạy lại mà số liệu không đổi thì **tự bỏ qua** (so sánh sha256), nên không tạo rác.

### Đây chính là cầu nối sang Base

Khi nào muốn neo lên chuỗi, thứ cần ghi **không phải cả bộ dữ liệu** — chỉ là
cột `sha256` trong `assets/data/history.json`, **32 byte mỗi bản**. Nội dung vẫn
nằm trên IPFS. Chi phí gas gần như không đáng kể, và cột `anchored` trong
history.json đã chừa sẵn chỗ điền tx hash.

Nói cách khác: **phần chuẩn bị cho Base đã xong từ bây giờ.** Lúc nối chỉ là viết
một hợp đồng lưu `bytes32` và gọi nó — không phải sửa gì trong app.

### Người dùng thấy gì

Cuối trang Bảng xếp hạng có khối **"Bản số liệu này đóng dấu được"**: CID bấm mở
được, SHA-256, số bản đã lưu. Khi nào neo lên Base thì dòng cuối tự đổi thành tx hash.

Móc thứ ba trong `app.js` (`if(window.KT_PROV)`), cùng kiểu rào như L2BEAT.

---

## Hosting phi tập trung (IPFS + ENS)

```bash
npm run dist      # gom dist/ + chạy ba lớp kiểm tra
npm run pin       # đẩy lên IPFS, in ra CID
npm run deploy    # cả hai
```

`.github/workflows/deploy-ipfs.yml` làm đúng hai bước đó mỗi khi có thay đổi.

### Ba lớp kiểm tra trước khi pin

Pin lên IPFS là **không rút lại được** — CID sai thì sai vĩnh viễn. Nên `build-dist`
từ chối ghi `dist/` nếu:

1. **Có đường dẫn tuyệt đối.** Gateway hay phục vụ app dưới `/ipfs/<CID>/`, nên
   một cái `src="/assets/..."` sẽ trỏ ra gốc gateway và 404 sạch. *Đã thử bằng cách
   cố tình đổi một dòng thành `/assets/js/pwa.js`: build dừng, chỉ đúng
   `index.html:138`, không ghi gì.*
2. **`sw.js` khai file không tồn tại**, hoặc có file trong `dist/` mà `sw.js` quên
   cache — lỗi này âm thầm làm hỏng chế độ offline.
3. **Số liệu quá cũ** (cảnh báo nếu `live.js` sinh cách đây hơn 2 ngày).

### Đã kiểm chứng: app chạy dưới đường dẫn con

Dựng một gateway giả tại `/ipfs/bafybei…zdi/` rồi mở bằng trình duyệt thật:
**88 thẻ, 12 huy hiệu Stage, trang thành phố Base đủ 32 ô.** Hash routing (`#eth/base`)
là lựa chọn may mắn ở đây — IPFS không có server để rewrite URL, nên mọi kiểu
routing khác đều sẽ vỡ.

### Bản đã đưa lên (12/08/2026)

```
bafybeidxf3qaqruf6ajg2rodyyccbp6m2fxxh4vg3crdqsvf24rjwx2csi
```

19 file · 433 KB · Pinata xác nhận đã pin.

**Đã kiểm chứng dứt điểm:** tải lại toàn bộ 19 file từ mạng IPFS **chỉ bằng CID**,
dựng lại và mở bằng trình duyệt thật → 9 quốc gia, 88 thẻ, 12 huy hiệu Stage,
trang Base đủ 32 ô và 5 dòng rủi ro. SHA256 của từng file khớp với bản build.

### Thực tế về gateway — đọc trước khi bực mình

Ba chuyện có thật, đều đã gặp:

**1. Gateway `*.mypinata.cloud` chặn HTML.** Trả `403` cho `index.html` nhưng vẫn
phục vụ CSS/JS bình thường. Đây là chính sách chống lừa đảo của Pinata: muốn phục
vụ HTML thì phải **gắn custom domain** vào gateway. Đừng dùng link mypinata.cloud
để khoe site — nó sẽ hiện trang lỗi.

**2. Gateway công cộng giờ trả về trang bootstrap, không phải nội dung.**
`ipfs.io`, `dweb.link`, `w3s.link` đều chuyển sang kiểu *Service Worker Gateway*:
gửi cho trình duyệt một trang mồi ~12 KB, trang này cài service worker rồi mới
kéo nội dung về và tự kiểm tra từng block theo CID. Trình duyệt thật xử lý được;
trình duyệt headless trong kiểm thử tự động thì thường không kịp.

**3. `ipfs.io` chèn thêm byte vào HTML.** Bản index.html qua ipfs.io dài hơn bản
gốc đúng 292 byte — Cloudflare gắn một thẻ `<a>` ẩn (`/cdn-cgi/content?id=…`) sau
`</html>`. Nội dung của mình không sai; nhưng đây đúng là lý do tồn tại của kiểu
gateway ở mục 2: *trình duyệt tự kiểm chứng, không tin server.*

**Đường dùng thật nên là `eth.limo`** (sau khi trỏ ENS) — nó sinh ra để phục vụ
website từ contenthash, không dính hai vấn đề đầu.

### Lấy PINATA_JWT

1. Đăng ký ở pinata.cloud (gói miễn phí đủ dùng cho app 432 KB này).
2. API Keys → New Key → quyền `pinFileToIPFS`.
3. Cục bộ: `$env:PINATA_JWT="..."` · CI: Settings → Secrets and variables →
   Actions → New repository secret, tên `PINATA_JWT`.

`scripts/pin-ipfs.mjs` gọi thẳng API bằng `fetch` + `FormData` có sẵn của Node 20 —
**không cài gói nào, không dùng action của bên thứ ba**. Toàn bộ chỗ chạm vào token
gói gọn trong một file đọc hết trong một phút.

> **Khoá phải xoay vòng:** nếu JWT từng bị dán vào chat, email hay chỗ nào khác
> ngoài GitHub Secrets, hãy vào Pinata → API Keys → **revoke** rồi tạo khoá mới.
> Khoá `pinFileToIPFS` cho phép ghi vào tài khoản của bạn.

### Cái bẫy đã xử lý: hai workflow không tự gọi nhau

Commit tạo bởi `GITHUB_TOKEN` **không kích hoạt workflow khác** — GitHub chặn thế
để tránh vòng lặp vô hạn. Nếu chỉ dựa vào `on: push` thì mỗi 6 giờ số liệu cập nhật,
commit thành công, mà bản trên IPFS **vẫn là bản cũ mãi mãi** — và không có lỗi nào
để mà biết.

Nên `refresh-data.yml` gọi thẳng sang bằng `workflow_call`, chỉ khi có commit thật:

```yaml
deploy:
  needs: refresh
  if: needs.refresh.outputs.changed == 'true'
  uses: ./.github/workflows/deploy-ipfs.yml
  secrets: inherit
```

### Trỏ tên miền: Ethereum giữ tên, Base để ghi

Quyết định là **Base + ENS**, và trong thực tế nó chia làm hai phần:

| | ở đâu | vì sao |
|---|---|---|
| Tên miền + contenthash | **Ethereum mainnet** | Bản ghi `contenthash` của ENS nằm ở mainnet — đó là chỗ trình duyệt và gateway tra. Không tránh được gas mainnet cho việc này. |
| Ghi onchain về sau | **Base** | Neo dấu vân tay snapshot mỗi 6 giờ, hoặc bất cứ thứ gì cần ghi thường xuyên. Rẻ hơn hàng trăm lần. |

Đặt contenthash sau mỗi lần pin:

```
ipfs://<CID mà npm run pin in ra>
```

Vào app.ens.domains → tên của bạn → Records → Content Hash. Xong thì mở được tại:

- `https://<tên>.eth.limo/` — Brave và Cloudflare hỗ trợ sẵn
- `https://<CID>.ipfs.dweb.link/` — không cần ENS, dùng ngay

**Một điều cần biết trước:** tôi có cân nhắc dùng Basename (`.base.eth`) để mọi thứ
nằm hẳn trên Base, nhưng hỗ trợ gateway cho việc *phục vụ website* từ contenthash
của Basename chưa chắc chắn bằng `.eth` thường. Nên cách chia trên là chắc ăn hơn:
tên ở mainnet (đặt một lần, ít khi đổi), ghi thường xuyên ở Base.

Việc đặt contenthash hiện làm tay. Tự động hoá được (ký bằng private key trong CI),
nhưng để private key có quyền đổi tên miền vào GitHub Secrets là đánh đổi lớn — nên
tôi để bạn quyết, chưa làm.

---

## Đóng gói thành app Android / iOS

Cấu trúc hiện tại đã sẵn sàng cho Capacitor:

```bash
npm install @capacitor/core @capacitor/cli
npx cap init "Kinh Thành" com.sunswagz.kinhthanh --web-dir=.
npm install @capacitor/android
npx cap add android
npx cap open android          # build APK/AAB bằng Android Studio
```

Vài lưu ý khi tới bước đó:

- **Đường dẫn có dấu cách** — Gradle của Android hay khó chịu với đường dẫn kiểu
  `D:\SUNSWaGz 2027\...`. Nếu build lỗi lạ, copy thư mục sang chỗ như `D:\dev\kinh-thanh-app`.
- **Bỏ `pwa.js`** khi chạy trong Capacitor. App native không cần service worker
  (file đã tự bỏ qua khi giao thức không phải http/https, nên thực tế không hại gì).
- **Gọi DefiLlama** cần khai báo quyền mạng — Android có sẵn, iOS thì thêm
  `NSAppTransportSecurity` nếu cần.
- **Icon app native** lấy từ `assets/icons/icon-512.png`.

---

## Còn có thể thêm

- **WalletConnect** cho ví trên điện thoại — hiện `wallets.js` chỉ phát hiện ví
  cắm sẵn trong trình duyệt (EIP-6963).
- **Neo sha256 lên Base** — cột `anchored` trong `history.json` đã chừa sẵn chỗ.
- **ENS contenthash** trỏ vào CID mới nhất.
- Tự tải phông chữ về `assets/fonts/` để lần mở đầu tiên cũng không cần mạng.
- Chú giải của Đô Sát Viện mới phủ tới đúng những nhãn L2BEAT đang dùng. L2BEAT
  thêm nhãn mới thì bảng hiện nguyên bản tiếng Anh kèm dấu **"chưa dịch"** — cứ
  mở `do-sat-vien/assets/js/glossary.js` thêm vào, không phải sửa gì khác.
