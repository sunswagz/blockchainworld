/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — kinh-thanh

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của cung kinh-thanh.
   Sửa nhịp, thêm hay bỏ node của cung này thì sửa ĐÚNG file này —
   không phiên nào khác phải chạm vào, nên không ai xung đột với ai. */

export const NODE = [
  {
    ma: "kinh-thanh", ten: "Số liệu Kinh Thành", cung: "kinh-thanh",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-live.mjs",
    ra: ["kinh-thanh/assets/js/data/live.js",
         "kinh-thanh/assets/js/data/provenance.js",
         "kinh-thanh/assets/data/history.json"],
    y: "TVL và số on-chain 9 quốc gia L1, lấy từ DefiLlama."
  },
];
