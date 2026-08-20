/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — ho-bo

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của cung ho-bo.
   Sửa nhịp, thêm hay bỏ node của cung này thì sửa ĐÚNG file này —
   không phiên nào khác phải chạm vào, nên không ai xung đột với ai. */

export const NODE = [
  {
    ma: "ho-bo", ten: "Dòng tiền Hộ Bộ", cung: "ho-bo",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-hobu.mjs",
    ra: ["ho-bo/assets/js/v/dong-tien.js"],
    y: "Mười một đường DefiLlama công khai (TVL, phí, DEX, stablecoin, vụ mất tiền, " +
       "lợi suất) cộng lịch sử 20 chuỗi, gộp thành một file. KHÔNG gọi AI, không khoá nào."
  },
  /* Node DUY NHẤT trong xưởng sửa MÃ chứ không sửa dữ liệu. Mọi node
     khác ghi vào assets/js/v/ hoặc data.js; node này ghi thẳng vào
     app.js, app.css, index.html — thứ trình duyệt nạp làm hành vi.

     Vì sao dám: nó bị kẹp giữa hai lớp số học mà model không viết.
     `tien-hoa.mjs do --ghi` chấm phiếu TRƯỚC, `cong --so` chấm lại
     SAU và chặn nếu vỡ hoặc nếu điểm tụt. Trượt là workflow trả cả
     thư mục cung về bản cũ, không có gì lên site.

     Nhịp 24 giờ chứ không 6: một bước tiến giao diện mỗi ngày là
     nhanh hơn bất kỳ ai ngồi sửa tay, mà vẫn đủ thưa để người kịp
     nhìn lượt trước trước khi lượt sau đè lên. */
  {
    ma: "ho-bo-tien-hoa", ten: "Tiến hoá giao diện Hộ Bộ", cung: "ho-bo",
    tram: "M18", che: "claude", nhip: 24,
    lenh: "tien-hoa.mjs de-bai + claude-code-action + tien-hoa.mjs cong --so",
    ra: ["ho-bo/assets/css/app.css", "ho-bo/assets/js/app.js",
         "ho-bo/index.html", "ho-bo/sw.js"],
    y: "Đo cung bằng 7 thước, lấy kỹ năng khớp từ 3.600 skill Tàng Thư Các, " +
       "rồi để model đề xuất sửa giao diện. Cổng chặn quyết định, không phải model."
  },
];
