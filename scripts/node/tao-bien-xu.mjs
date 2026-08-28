/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — tao-bien-xu

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của cung tao-bien-xu.
   Sửa nhịp, thêm hay bỏ node của cung này thì sửa ĐÚNG file này —
   không phiên nào khác phải chạm vào, nên không ai xung đột với ai.

   Lưu ý một chỗ dễ nhầm: `tao-bien-xu/assets/js/v/van-hanh.js` KHÔNG
   nằm ở đây. Nó là bản chiếu của sổ nhà máy — thuộc chính nhà máy,
   khai ở hằng số DUONG_CHIEU trong nha-may.mjs, và mọi cung đều đọc
   nó. Cung này chỉ tình cờ là nơi nó được hiển thị. */

export const NODE = [
  /* Cung THỨ NĂM vào vòng tiến hoá, sau Hộ Bộ, Thái Bộc Tự, Khâm
     Thiên Giám và Đài Quan Trắc. Vẫn không thêm script nào — chỉ đổi
     tên cung, đúng lời hứa ở đầu scripts/tien-hoa.mjs.

     Vì sao cung này đáng vào vòng, dù phiếu đo lúc bật đã 7/7:

     Bảy thước đo SÀN — trang có vẽ được không, chữ có đọc được
     không, nút có nhãn không. Chúng không đo được thứ bậc thị giác,
     nhịp khoảng cách, hay giọng của trang. Một cung 7/7 vẫn có thể
     nhàm, và lượt tiến hoá có nhánh riêng cho đúng chuyện đó: "nếu
     cả bảy thước đều đạt, tìm MỘT chỗ làm trang dễ đọc hơn mà không
     thước nào đo được".

     Và cung này đáng được chăm hơn cả: nó là chỗ người ta MỞ RA ĐỂ
     NHÌN cả nhà máy. Bảng vận hành hỏng thì mọi cung khác vẫn chạy
     nhưng không ai thấy chúng chạy.

     `ra` KHÔNG có assets/js/data.js. File đó là bản thiết kế 18 máy
     viết tay — nội dung, không phải giao diện. Cùng lý do node của
     Thái Bộc Tự không mở quyền vào toa.js. */
  {
    ma: "tao-bien-xu-tien-hoa", ten: "Tiến hoá giao diện Tạo Biện Xứ", cung: "tao-bien-xu",
    tram: "M18", che: "claude", nhip: 24,
    lenh: "tien-hoa.mjs de-bai + claude-code-action + tien-hoa.mjs cong --so",
    ra: ["tao-bien-xu/assets/css/app.css", "tao-bien-xu/assets/js/app.js",
         "tao-bien-xu/index.html", "tao-bien-xu/sw.js"],
    y: "Cùng khuôn ho-bo-tien-hoa, đổi tên cung. Phiếu đo lúc bật: 7/7 — nên " +
       "lượt đầu đi thẳng vào nhánh 'không thước nào đo được': thứ bậc, nhịp " +
       "khoảng cách, giọng của trang."
  }
];
