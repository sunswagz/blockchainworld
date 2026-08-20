/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — tu-cam-thanh

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của cung tu-cam-thanh.
   Sửa nhịp, thêm hay bỏ node của cung này thì sửa ĐÚNG file này —
   không phiên nào khác phải chạm vào, nên không ai xung đột với ai. */

export const NODE = [
  {
    ma: "tu-cam-thanh", ten: "Phiên Tử Cấm Thành", cung: "tu-cam-thanh",
    tram: "M12", che: "tay", nhip: 0,
    lenh: "cd tu-cam-thanh-runtime && python -m trader.snapshot",
    ra: ["tu-cam-thanh/assets/js/v/phien.js"],
    y: "Runtime là tiến trình Python chạy dài, cần ANTHROPIC_API_KEY và quyền " +
       "ghi đĩa — Actions không chạy được. Chạy tay rồi commit lát cắt, cùng " +
       "kiểu Hoàng Thành."
  },
];
