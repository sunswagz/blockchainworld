# knowledge-os

Lớp tri thức nền dùng chung cho `sunswagz/blockchainworld`.

**Đây KHÔNG phải một cung.** Thư mục này không có `index.html`, không nằm
trong `HALLS` của `scripts/build-dist.mjs`, nên nó tự ở ngoài `dist/` —
không lên GitHub Pages, không lên IPFS. Nó là **nguồn**, và thứ lên site
là những lát cắt nhỏ nó sinh ra cho từng cung.

Và **KHÔNG dựng cung đọc sách**. Cả gói này tồn tại để trả lời một câu
hỏi mà số liệu không trả lời được: *cái đang đo trên màn hình đóng vai
trò kinh tế gì?* Nó không dạy ai đọc *The Bitcoin Standard*.

## Luồng

    nguồn → khái niệm → quan hệ → cầu nối cung/phòng → lát cắt cho trang

Ví dụ đang chạy thật:

    time_preference → interest_rate → capital_market
      → thi-bac-ty/#co-hoi → "funding là lãi suất của một vị thế đòn bẩy"

## Ba lệnh

    node knowledge-os/kiem.mjs              kiểm dữ liệu, và kiểm nó khớp repo thật
    node knowledge-os/sinh.mjs              sinh lát cắt cho mọi cung đã ánh xạ phòng
    node knowledge-os/sinh.mjs ho-bo        chỉ một cung
    node knowledge-os/sinh.mjs --thu        xem sẽ ghi gì, chưa ghi

    node knowledge-os/tra.mjs khai-niem interest_rate
    node knowledge-os/tra.mjs tim "lãi suất"
    node knowledge-os/tra.mjs cung thi-bac-ty
    node knowledge-os/tra.mjs vai-von time_price
    node knowledge-os/tra.mjs 2026

`sinh.mjs` **chạy `kiem.mjs` trước, và không ghi gì nếu dữ liệu sai**.
Cùng lý do `scripts/build-scan.mjs` không cho model ghi thẳng `scan.js`:
một dòng sai ở đây không nằm yên trong file JSON, nó thành chữ trên trang
người ta đọc — mà một câu giải nghĩa sai trông y hệt một câu đúng.

## Lát cắt sinh ra là SINH TAY, PHẢI commit

    thai-boc-tu/assets/js/v/tri-thuc.js
    ho-bo/assets/js/v/tri-thuc.js
    thi-bac-ty/assets/js/v/tri-thuc.js

Cùng loại với `hoang-thanh/assets/js/data.js` và ba lát cắt của ba runtime
Python: máy sinh, nhưng **không workflow nào chạy lệnh này**, nên người
chạy phải commit kết quả.

Đừng khai nó trong `scripts/node/` — một node có `nhip` mà không workflow
nào gọi thì Bảng vận hành sẽ mãi báo "đến hạn" cho thứ không bao giờ chạy.

Đường ghi nằm ở `assets/js/v/`, nhánh **MẠNG-TRƯỚC** của mọi `sw.js`, nên
sửa nó **không cần nâng `CACHE_VERSION`**.

## Ranh giới nguồn — thứ cả gói này dựng ra để giữ

Ba lớp không được ghi đè nhau, và một khi lẫn thì không tách lại được vì
không ai còn biết dòng nào vốn thuộc lớp nào:

| lớp | nghĩa | ở đâu |
|---|---|---|
| **sách** (`stance: source`) | tác giả mô tả, tra lại được bằng chương/trang | `data/concepts/`, `data/relations/` |
| **tác giả** (`stance: author_claim`) | lập trường riêng của tác giả, không phải sự thật đo được | như trên |
| **phân tích** (`stance: analysis`) | SUNSWaGz suy ra — sách không nói gì về repo này | `data/bridges/` |
| **repo** (`stance: repo`) | đo được từ chính repo/runtime này, năm 2026 | `data/2026/` |

Trên trang, mỗi khái niệm và mỗi quan hệ đeo đúng một nhãn trong bốn nhãn
ấy. Gộp "tác giả" vào "sách" là biến một lập trường thành sự thật; gộp
"phân tích" vào "sách" là mượn uy tín của sách cho suy luận của mình. Cả
hai đều là nói dối mà không câu nào sai ngữ pháp.

Luật đầy đủ ở [docs/SOURCE_POLICY.md](docs/SOURCE_POLICY.md).

## Lớp 2018 → 2026 nằm RIÊNG

`data/2026/` là lớp thứ hai. Sách viết năm 2018 và tác giả rất hoài nghi
mọi blockchain ngoài Bitcoin; thứ đổi từ đó tới nay là **thế giới**, không
phải sách.

Nên **đừng bao giờ sửa dữ liệu sách để "cập nhật" nó**. Sửa là mất luôn
khả năng nói "chỗ này tác giả sai" — vì không còn bản gốc để so.

Quan hệ trong lớp này chỉ mang bốn loại nói rõ nó đứng thế nào với sách:
`extends` (nối dài), `supports` (củng cố), `challenges` (chống lại),
`carries` (mang theo rủi ro). Và không quan hệ nào được lấy `source_type:
book` — sách không phải bằng chứng cho dữ kiện 2026.

`kiem.mjs` chặn cả hai chiều: concept 2026 mang chương/trang sách là lỗi,
và concept sách trùng id với lớp 2026 cũng là lỗi.

## Thêm ánh xạ cho một cung

Sửa `data/bridges/repo.json`, thêm `rooms` vào mục của cung đó:

```json
{ "id": "loi-suat", "name_vi": "Lợi Suất",
  "concepts": ["interest_rate", "capital_market"],
  "note_vi": "Một con số % là ba thứ cộng lại: giá của thời gian, phần bù rủi ro, và nhu cầu thanh khoản." }
```

`id` phải là **mã phòng có thật** trong mã nguồn của cung. `kiem.mjs` đọc
mã đó thẳng từ nguồn — `toa.js` của Thái Bộc Tự, mảng `PHONG` của Hộ Bộ,
`<section id>` của Thị Bạc Ty — chứ không giữ bản chép. Ánh xạ tới một mã
không tồn tại thì trang vẫn mở bình thường và lặng lẽ không hiện gì; đó
đúng cái bẫy `thai-boc-tu/assets/js/toa.js` đã ghi biển báo.

Cung nào bộ kiểm chưa đọc được mã phòng thì nó **nói thẳng là không kết
luận được**, không buộc tội. Thêm cung mới thì thêm một nhánh vào hàm
`maPhong()` trong `kiem.mjs`.

Rồi:

    node knowledge-os/kiem.mjs
    node knowledge-os/sinh.mjs <cung>

và thêm một dòng vào `index.html` của cung, ngay trước `app.js`:

```html
<!-- lớp tri thức nền · SINH TAY, xem knowledge-os/sinh.mjs -->
<script src="assets/js/v/tri-thuc.js"></script>
```

## Hợp đồng V1

`kiem.mjs` có một bảng `HOP_DONG` đóng cứng những ánh xạ mà V1 đã hứa —
`thai-boc-tu/t01, t04, t05, t06`, `ho-bo/tien-cho, loi-suat`,
`thi-bac-ty/co-hoi`. Không có bảng đó thì một lượt sửa dữ liệu sau có thể
gỡ chúng ra mà không ai hay: dữ liệu vẫn hợp lệ, validator vẫn xanh, chỉ
có trang là bớt đi một mẩu giải nghĩa.

## Cái gói này KHÔNG làm

- **Không đổi công thức tài chính nào.** TVL, lợi suất, chế độ rủi ro,
  funding, NET, đếm mốc — tất cả tính y như trước. Lớp này chỉ giải nghĩa.
- **Không ra quyết định vốn.** Đường quyết định vẫn là
  `Opportunity → Risk Engine → Capital Allocator → Execution`.
- **Không chép đoạn dài từ PDF.** Chỉ lưu diễn giải ngắn kèm locator.
