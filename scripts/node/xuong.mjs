/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — xuong

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của CHÍNH nhà máy — không thuộc cung nào.
   Đóng dấu bản số liệu, báo cáo sức khoẻ, giao hàng. */

export const NODE = [
  {
    ma: "dong-dau", ten: "Đóng dấu bản số liệu",
    tram: "M16", che: "script", nhip: 6,
    lenh: "node scripts/pin-snapshot.mjs",
    ra: [],
    y: "Pin bản số liệu 1,8 KB lên IPFS. Tự bỏ qua nếu sha256 trùng bản trước."
  },
  {
    ma: "bao-cao", ten: "Báo cáo sức khoẻ xưởng",
    tram: "M18", che: "claude", nhip: 24,
    lenh: "anthropics/claude-code-action",
    ra: ["factory/bao-cao.md"],
    y: "Claude Code Action đọc state.json rồi viết vài dòng tiếng Việt: " +
       "node nào đang ốm, ốm từ bao giờ, nên xem chỗ nào trước."
  },
  /* DÒ KHO — nguồn ý tưởng MỚI cho vòng tiến hoá.

     `tien-hoa.mjs ky-nang` chỉ chọn kỹ năng hợp với THƯỚC ĐANG
     TRƯỢT, nên nó không bao giờ tìm ra thứ đáng canh mà ta chưa nghĩ
     tới. Đó là trần thật: cung nào đạt hết thước thì model chỉ còn
     được bảo "tìm chỗ nào không thước nào đo được".

     Node này lục 3.696 kỹ năng của Tàng Thư Các theo sáu lĩnh vực,
     bỏ những cái đã khai thác (sổ ở factory/kho-da-dung.json), rồi
     tải vài ứng viên đầu bảng về kèm đoạn trích.

     Nhịp 168 giờ — MỘT LƯỢT MỖI TUẦN. Kho chỉ được quét lại vài
     lượt mỗi ngày và ứng viên mới nhỏ giọt; dò mỗi 6 giờ là 28 lượt
     tải cho cùng một danh sách không đổi. */
  {
    ma: "do-kho", ten: "Dò kho Tàng Thư Các",
    tram: "M11", che: "script", nhip: 168,
    lenh: "node scripts/do-kho.mjs quet",
    ra: ["factory/kho-de-xuat.json"],
    y: "Tìm kỹ năng CHƯA khai thác trong 3.696 cái, xếp hạng theo sáu lĩnh vực, " +
       "tải SKILL.md kèm trích dẫn. Máy lo tìm và xếp; model lo đọc hiểu — đã thử " +
       "rút luật bằng regex và bỏ vì cho ra rác."
  },
  /* PHIẾU TOÀN THÀNH — nhìn cả mười hai cung một lượt.

     `tien-hoa.mjs do` chấm được MỌI cung, nhưng chỉ BỐN cung có vòng
     tiến hoá gọi tới nó. Tám cung còn lại chưa từng được chấm trong
     một lượt bot nào, nên điểm của chúng chỉ hiện khi có người ngồi
     gõ lệnh — tức là gần như không bao giờ.

     Lượt chấm đầu tiên lộ ngay hai chuyện không ai biết: Thị Bạc Ty
     và Tử Cấm Thành đều trượt thước `ve` — phòng của chúng KHÔNG
     VẼ ĐƯỢC — và 11 trên 12 cung chưa có đường nhảy qua thanh bên.

     `che: "script"`: không gọi model, không tốn quota. Thấy được
     vấn đề là việc rẻ; sửa mới là việc đắt, và sửa vẫn là việc của
     vòng tiến hoá hoặc của người. Cả mười hai cung chấm xong trong
     ~8 giây, nên nhịp 24 giờ là rộng rãi. */
  {
    ma: "phieu", ten: "Phiếu toàn thành",
    tram: "M18", che: "script", nhip: 24,
    lenh: "node scripts/phieu-toan-thanh.mjs",
    ra: ["factory/phieu.json"],
    y: "Chấm cả 12 cung bằng đúng bộ thước của vòng tiến hoá, rồi xếp thước nào " +
       "đang trượt ở NHIỀU cung nhất. Nhìn từng cung thì mỗi lỗi trông như chuyện " +
       "riêng của cung đó; nhìn cả bảng mới thấy cái nào là bệnh chung."
  },
  {
    ma: "giao-hang", ten: "Giao hàng lên Pages",
    tram: "M16", che: "theo", nhip: 0,
    lenh: ".github/workflows/deploy-pages.yml",
    ra: [],
    y: "Không có nhịp riêng — chạy khi có commit số liệu. 27/27 lượt thành công."
  }
];
