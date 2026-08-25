# Lớp 2018 → 2026

Sách viết năm **2018**. Thứ đổi từ đó tới nay là **thế giới**, không phải
sách. Nên lớp này nằm riêng, và luật đầu tiên là:

> **Đừng bao giờ sửa dữ liệu sách để "cập nhật" nó.**

Sửa là mất luôn khả năng nói "chỗ này tác giả sai" — vì không còn bản gốc
để so. Tác giả đứng rõ trong truyền thống Kinh tế học Áo và hoài nghi mọi
blockchain ngoài Bitcoin; đó là dữ kiện về **sách**, phải giữ nguyên.

## Hai file

    concepts.json    khái niệm 2026 mà sách không có
    relations.json   chúng đứng thế nào với khái niệm của sách

## Luật, và `kiem.mjs` chặn từng cái

- Concept ở đây **không bao giờ** mang `stance: source` hay
  `author_claim` — chỉ `repo`, `analysis`, hoặc `web`.
- Concept ở đây **không được mang chương/trang sách**. Sách 2018 không
  nói gì về chuyện của 2026; gắn locator vào là bịa một câu trích.
- Concept ở đây **không được trùng id** với lớp sách. Lớp này nối thêm,
  không ghi đè.
- Mỗi concept phải có `source_ref` — một quan sát không chỉ được nguồn
  là tin đồn.
- Quan hệ chỉ mang bốn loại, và bốn loại đó nói **rõ** nó đứng thế nào
  với sách:

      extends     nối dài một khái niệm của sách sang hình thái mới
      supports    quan sát 2026 củng cố điều sách nói
      challenges  quan sát 2026 đi ngược điều sách nói
      carries     hình thái mới mang theo một rủi ro sách đã nêu

- Quan hệ **không được** `source_type: book` — không lấy sách làm bằng
  chứng cho dữ kiện 2026 (SOURCE_POLICY điều 4).

## Vì sao `source_type` ở đây phần lớn là `repo`

Bảy khái niệm hiện có đều neo vào thứ **repo này thật sự đo**: bảng
stablecoin của Hộ Bộ, bảng lợi suất, mười tám toa của Thái Bộc Tự, bảng
rủi ro L2 của Đô Sát Viện, runtime funding của Thị Bạc Ty, Risk Engine của
Tử Cấm Thành.

Đó là chủ ý. Một lớp "thực tại 2026" mà dẫn nguồn từ trí nhớ thì chính là
thứ SOURCE_POLICY dựng ra để chặn. Muốn thêm nguồn web thì dùng
`source_type: web` và ghi `source_ref` là đường dẫn thật, chứ đừng để nó
đội lốt `repo`.
