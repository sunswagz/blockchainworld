/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — kham-thien-giam

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của cung kham-thien-giam.
   Sửa nhịp, thêm hay bỏ node của cung này thì sửa ĐÚNG file này —
   không phiên nào khác phải chạm vào, nên không ai xung đột với ai. */

export const NODE = [
  {
    ma: "kham-thien-giam", ten: "Lát cắt Khâm Thiên Giám", cung: "kham-thien-giam",
    tram: "M12", che: "tay", nhip: 0,
    lenh: "cd kham-thien-giam-runtime && python -m kham.snapshot",
    ra: ["kham-thien-giam/assets/js/v/dai-chiem.js"],
    y: "Runtime thị trường tiên đoán là tiến trình Python chạy dài, giữ một " +
       "WebSocket tới sổ lệnh Polymarket theo nhịp giây và có thể cầm khoá ví " +
       "— Actions không chạy được, và cũng KHÔNG ĐƯỢC cho chạy. Chạy tay rồi " +
       "commit lát cắt, cùng kiểu Tử Cấm Thành."
  },
];
