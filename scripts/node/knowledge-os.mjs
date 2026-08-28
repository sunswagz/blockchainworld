/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — knowledge-os

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Đây KHÔNG phải một cung — `knowledge-os/` là dữ liệu, không có
   index.html, không lên site. Nhưng nó có node vì nó SINH RA thứ lên
   site: mười một lát cắt `<cung>/assets/js/v/tri-thuc.js`.

   ── VÌ SAO TRƯỚC ĐÂY KHÔNG CÓ NODE, VÀ VÌ SAO GIỜ CÓ ──
   Bản đầu cố ý để trống, và lý do khi đó đúng: chưa có PHIẾU ĐO nào
   cho lớp tri thức. `kiem.mjs` trả đúng/sai, mà đúng/sai thì không so
   được giữa hai lượt — cắm một node tiến hoá vào lúc ấy là cho model
   sửa dữ liệu mà cổng chặn không có gì để chấm ngoài "còn hợp lệ".

   `knowledge-os/do.mjs` lấp đúng chỗ đó: bảy thước bằng số, so được.
   Có số rồi thì mới có vòng, nên nay có hai node.

   ── HAI NODE, HAI VIỆC KHÁC HẲN ───────────────────────
   `tri-thuc`          giữ cho lát cắt KHỚP với dữ liệu — thuần script,
                       không gọi model, không phán đoán gì
   `tri-thuc-tien-hoa` mở rộng chính lớp tri thức — gọi model, và cổng
                       chặn quyết định nhận hay trả lại

   Tách ra vì cái đầu phải chạy được cả khi cái sau bị tắt vì tiền hay
   vì hỏng. Cùng bài học với cặp `quan-trac-do` / `dai-quan-trac`: phần
   trả lời được bằng số phải sống độc lập với phần cần model. */

export const NODE = [
  {
    ma: "tri-thuc", ten: "Lát cắt tri thức", cung: null,
    tram: "M12", che: "script", nhip: 24,
    lenh: "node knowledge-os/sinh.mjs",
    ra: [
      "cong-bo/assets/js/v/tri-thuc.js",
      "dai-quan-trac/assets/js/v/tri-thuc.js",
      "do-sat-vien/assets/js/v/tri-thuc.js",
      "ho-bo/assets/js/v/tri-thuc.js",
      "hoang-thanh/assets/js/v/tri-thuc.js",
      "kham-thien-giam/assets/js/v/tri-thuc.js",
      "tang-thu-cac/assets/js/v/tri-thuc.js",
      "tao-bien-xu/assets/js/v/tri-thuc.js",
      "thai-boc-tu/assets/js/v/tri-thuc.js",
      "thi-bac-ty/assets/js/v/tri-thuc.js",
      "tu-cam-thanh/assets/js/v/tri-thuc.js"
    ],
    y: "Dựng lại lát cắt cho 11 cung từ knowledge-os/data/. `sinh.mjs` " +
       "chạy validator trước và KHÔNG ghi gì nếu dữ liệu sai; nó cũng bỏ " +
       "qua cung nào nội dung không đổi, nên lượt không có gì mới thì " +
       "không sinh ra commit rỗng. Nhịp 24 giờ vì dữ liệu nguồn đổi khi " +
       "có người sửa, không đổi theo giờ như số liệu thị trường."
  },
  {
    ma: "tri-thuc-tien-hoa", ten: "Tiến hoá lớp tri thức", cung: null,
    tram: "M18", che: "claude", nhip: 24,
    lenh: "do.mjs de-bai → claude-code-action → do.mjs cong --so",
    ra: [
      "knowledge-os/data/bridges/repo.json",
      "knowledge-os/data/2026/concepts.json",
      "knowledge-os/data/2026/relations.json"
    ],
    y: "Phiếu đo bảy thước chỉ ra chỗ lớp tri thức còn hụt — phòng chưa " +
       "ánh xạ, khái niệm 2026 chưa nối tới trang nào — rồi model đề xuất " +
       "vá, rồi cổng chặn chấm lại bằng chính phiếu đó. Model CHỈ được " +
       "sửa lớp phân tích và lớp 2026; lớp SÁCH cấm tuyệt đối vì nó cần " +
       "người có PDF trong tay, và một số trang đoán trúng khoảng chương " +
       "thì qua được mọi phép kiểm mà vẫn là trích dẫn bịa."
  }
];
