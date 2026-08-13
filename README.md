# Cổng Thành — SUNSWaGz

Cửa ngõ dẫn vào các cung. Mỗi cung là một web app tĩnh độc lập: **cài được lên máy,
chạy offline, số liệu tự cập nhật, và đóng gói thành app Android/iOS được về sau**.

| cung | là gì | nguồn số liệu |
|---|---|---|
| **/** Cổng Thành | trang cửa ngõ, liệt kê các cung | đọc ngày cập nhật từ chính file của từng cung |
| **/kinh-thanh/** | bản đồ 9 quốc gia Layer 1 | DefiLlama + L2BEAT (14 thành phố thuộc Ethereum) |
| **/dai-quan-trac/** | dòng chảy địa chính trị, 5 chiến trường, 8 đồng hồ | bản quét sinh trong GitHub Actions |
| **/do-sat-vien/** | bảng xét **toàn bộ** thành phố Layer 2 — dựng lại bố cục L2BEAT bằng tiếng Việt | L2BEAT: API `scaling/summary` + dữ liệu trang (106 dự án) |

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
├── do-sat-vien/                CUNG 3 — bảng xét Layer 2, dựng theo bố cục L2BEAT
│   ├── index.html · sw.js · manifest.webmanifest
│   └── assets/
│       ├── logos/              106 logo dự án tải từ L2BEAT (~520 KB)
│       └── js/
│           ├── data.js         TỰ SINH — 106 dự án + biểu đồ (~240 KB)
│           ├── glossary.js     bản dịch + diễn giải, SỬA TAY được
│           ├── app.js          sidebar, biểu đồ, 3 tab, bảng, hồ sơ, chú giải
│           └── halls.js · pwa.js
│
├── server.js                   máy chủ tĩnh, không phụ thuộc gói nào
├── package.json
├── scripts/
│   ├── build-live.mjs          DefiLlama → kinh-thanh/.../live.js
│   ├── build-l2beat.mjs        L2BEAT    → do-sat-vien/.../data.js
│   ├── build-scan.mjs          model     → dai-quan-trac/.../scan.js
│   ├── build-dist.mjs          gom cổng + các cung thành dist/, kèm 3 lớp kiểm tra
│   ├── pin-ipfs.mjs            pin cả site
│   ├── pin-snapshot.mjs        đóng dấu riêng bản số liệu (~1,8 KB)
│   └── check.mjs               kiểm cú pháp toàn bộ JS
└── .github/workflows/
    ├── refresh-data.yml        mỗi 6 giờ: build-live + build-l2beat rồi commit
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

## Đô Sát Viện — bảng xét Layer 2 (Việt hoá L2BEAT)

`/do-sat-vien/` dựng lại **bố cục của l2beat.com/scaling/summary** bằng tiếng Việt:
sidebar trái, biểu đồ tài sản, ba tab Rollup / Validium & Optimium / Dạng khác,
bảng có rosette 5 cánh, logo dự án, hệ chứng minh, thang tự trị, tài sản kèm thanh
tỉ lệ, và thao tác/giây.

Chạy tay: `npm run l2beat`

### Hai nguồn, và vì sao phải cả hai

| | API `/api/scaling/summary` | HTML `/scaling/summary` → `window.__SSR_DATA__` |
|---|---|---|
| cho gì | `tvs.breakdown`, `tvs.change7d`, `chart` | logo, tab, `proofSystem`, `activity`, `stage.missing`, mô tả |
| tính chất | giao diện công khai, ổn định | **dữ liệu nội bộ của trang, không cam kết gì** |
| vai | **bắt buộc** | làm giàu thêm |

L2BEAT đổi cấu trúc trang là nguồn 2 gãy. Nên build **không** coi đó là lỗi chí mạng:
nguồn 2 hỏng thì giữ nguyên phần làm giàu của bản trước, in cảnh báo, và app hiện một
dải nhắc ở đầu trang (`#canhBao`). Số liệu vẫn đúng vì số luôn lấy từ nguồn 1.

L2BEAT nấp sau Cloudflare và trả `error code: 1015` khi bị gọi dồn. Build thử lại 3
lần với khoảng nghỉ tăng dần, và nghỉ 120 ms giữa mỗi lần tải logo. Cron 4 lần/ngày
thì không bao giờ chạm ngưỡng; chạy tay liên tiếp thì có.

### Logo lưu trong repo, không hotlink

106 logo (~520 KB) tải về `do-sat-vien/assets/logos/`. URL của L2BEAT có hash nội
dung (`base.4840b6b2.png`) nên tên file đổi nghĩa là ảnh đổi — build bỏ qua file đã
có, chỉ tải cái mới. Hotlink thẳng sang l2beat.com sẽ hỏng khi họ đổi hash, và cũng
là ăn băng thông của người ta.

Service worker **cố ý không** nạp sẵn logo vào SHELL: gấp đôi dung lượng cài để lấy
ảnh mà phần lớn người dùng không cuộn tới. Chúng rơi vào nhánh cache-trước-cập-nhật-nền,
xem tới đâu lưu tới đó.

### Ba nguyên tắc của bản dịch

**1. Không bịa nghĩa.** Nhãn nào `glossary.js` chưa có thì bảng hiện **nguyên bản
tiếng Anh** kèm dấu `chưa dịch`. Mỗi dòng rủi ro kèm `<details>` mở ra mô tả gốc.
Riêng mục *"còn thiếu gì để lên thang sau"* **cố ý không dịch** — đó là tiêu chí kỹ
thuật L2BEAT dùng để chấm, dịch ra là làm sai lệch.

**2. Không tự chấm điểm.** Mọi đánh giá rủi ro là của L2BEAT.

**3. Mỗi nhãn trả lời "với người gửi tiền thì sao".** `glossary.js` cho mỗi mục ba
phần: `nhan` (nhãn tiếng Việt), `y` (nghĩa kỹ thuật), `vn` (hệ quả với người gửi tiền).

### Cạm bẫy đã xử lý: cùng một chữ, hai nghĩa

L2BEAT dùng lại chuỗi `"None"` cho **hai chiều rủi ro khác nhau**:

| chiều | `"None"` nghĩa là |
|---|---|
| State Validation | không ai kiểm chứng sổ sách, phải tin bên vận hành |
| Exit Window | nâng cấp có hiệu lực ngay, **không có thời gian để rút trước** |

Bảng tra phẳng theo giá trị sẽ gán nhầm nghĩa thứ nhất cho cả hai — và trông vẫn
rất hợp lý, nên rất khó phát hiện. Vì vậy có thêm `giaTheoChieu` trong `glossary.js`,
tra **trước** bảng chung. Quét 29 giá trị × 5 chiều của cả 106 dự án: đây là cặp duy
nhất đụng nhau.

### Hai con số khác nhau, cả hai đều đúng

| | |
|---|---|
| **$33.53b** — thẻ "Tài sản đang giữ" | chỉ cộng chuỗi **tầng 2**. Khớp đúng tiêu đề của L2BEAT. |
| **$39.47b** — thẻ "Tiền vào bằng đường nào" | cộng cả **tầng 3**. Phần chênh gần như toàn bộ là Hyperliquid ($5.86b, tầng 3). |

Đã truy ra nguyên nhân nên nói thẳng trên trang (`VI.ghiChuTong`) thay vì để người
đọc tưởng mình đọc nhầm hoặc số liệu sai.

Ba tab cũng là lý do thứ hạng nhìn khác: tab mặc định là **Rollup**, không tính
Hyperliquid hay Polygon PoS — giống hệt L2BEAT.

### Mốc thời gian của biểu đồ

`chart` trả 122 điểm nhưng lấy mẫu **6 giờ một lần**, tức 30 ngày chứ không phải 122
ngày. Nhãn tính khoảng thời gian từ chính mốc `timestamp`, không suy từ số điểm —
suy từ số điểm là ra "122 ngày qua", sai gấp bốn lần.

### Cổng Thành đọc ngày cập nhật mà không tải cả file

`data.js` nặng ~240 KB, nhưng tất cả những gì thẻ ở Cổng Thành cần (ngày, số dự án)
đều nằm trong ~900 byte đầu. `portal.js` đọc một khúc bằng `body.getReader()` rồi
`cancel()` luôn dòng tải. Trình duyệt không có streams thì rơi về `r.text()`.

### Vì sao cung này trông khác hai cung kia

Kinh Thành và Đài Quan Trắc dùng nền giấy sáng + chàm. Đô Sát Viện dùng nền xám lạnh,
Roboto, accent hồng sen — vì đây là bản dựng lại có chủ ý theo L2BEAT, không phải
sơ suất. Đổi về phong cách chung thì sửa `do-sat-vien/assets/css/app.css`, phần
`:root` và font ở `index.html`; markup và JS không phải động vào.

---

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
