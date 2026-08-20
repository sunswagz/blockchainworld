/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — hoang-thanh

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của cung hoang-thanh.
   Sửa nhịp, thêm hay bỏ node của cung này thì sửa ĐÚNG file này —
   không phiên nào khác phải chạm vào, nên không ai xung đột với ai. */

export const NODE = [
  {
    ma: "hoang-thanh", ten: "Rừng văn hoá Hoàng Thành", cung: "hoang-thanh",
    tram: "M12", che: "tay", nhip: 0,
    lenh: "npm run hoangthanh",
    ra: ["hoang-thanh/assets/js/data.js", "hoang-thanh/assets/js/v/"],
    y: "Nguồn nằm NGOÀI repo (sunswagz-hub/08_world_culture_forest) nên " +
       "Actions không quét được. Chạy tay rồi commit là cách duy nhất."
  },
];
