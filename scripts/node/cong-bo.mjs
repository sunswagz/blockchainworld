/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — cong-bo

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của cung cong-bo.
   Sửa nhịp, thêm hay bỏ node của cung này thì sửa ĐÚNG file này —
   không phiên nào khác phải chạm vào, nên không ai xung đột với ai. */

export const NODE = [
  {
    ma: "cong-bo", ten: "Đồ nghề Công Bộ", cung: "cong-bo",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-congbo.mjs",
    ra: ["cong-bo/assets/js/data.js", "cong-bo/assets/js/logos.js",
         "cong-bo/assets/js/v/nhat-ky.js", "cong-bo/assets/logos/"],
    y: "Bộ công cụ onchain. Nguồn có một phần là host staging của L2BEAT nên hay ngã."
  },
];
