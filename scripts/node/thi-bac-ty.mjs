/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — thi-bac-ty

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

export const NODE = [
  {
    ma: "thi-bac-ty", ten: "Lát cắt Thị Bạc Ty", cung: "thi-bac-ty",
    tram: "M13", che: "tay", nhip: 0,
    lenh: "cd thi-bac-ty-runtime && python -m bac.snapshot",
    ra: ["thi-bac-ty/assets/js/v/cang-phi.js"],
    y: "Runtime chênh lệch funding là tiến trình Python chạy dài, hỏi bốn " +
       "sàn perp theo nhịp giây và có chỗ để cắm khoá API đặt lệnh — Actions " +
       "không chạy được, và cũng KHÔNG ĐƯỢC cho chạy. Chạy tay rồi commit " +
       "lát cắt, cùng kiểu Tử Cấm Thành và Khâm Thiên Giám.\n\n" +
       "Còn một lý do riêng cho cung này: funding đổi theo GIỜ. Một lát cắt " +
       "sinh tự động 4 lượt/ngày vẫn là ảnh của một thế giới đã qua, nên " +
       "chạy tự động không mua lại được gì mà lại dựng ra vẻ tươi mới giả."
  }
];
