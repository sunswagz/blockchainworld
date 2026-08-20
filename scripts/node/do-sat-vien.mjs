/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — do-sat-vien

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của cung do-sat-vien.
   Sửa nhịp, thêm hay bỏ node của cung này thì sửa ĐÚNG file này —
   không phiên nào khác phải chạm vào, nên không ai xung đột với ai. */

export const NODE = [
  {
    ma: "do-sat-vien", ten: "Bảng xét Đô Sát Viện", cung: "do-sat-vien",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-l2beat.mjs",
    ra: ["do-sat-vien/assets/js/data.js", "do-sat-vien/assets/logos/"],
    y: "Xếp hạng Layer 2 theo L2BEAT, kèm logo tải về."
  },
];
