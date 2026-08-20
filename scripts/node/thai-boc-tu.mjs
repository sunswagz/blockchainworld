/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — thai-boc-tu

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của cung thai-boc-tu.
   Sửa nhịp, thêm hay bỏ node của cung này thì sửa ĐÚNG file này —
   không phiên nào khác phải chạm vào, nên không ai xung đột với ai. */

export const NODE = [
  {
    ma: "thai-boc-tu", ten: "Đoàn tàu Thái Bộc Tự", cung: "thai-boc-tu",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-thaiboc.mjs",
    ra: ["thai-boc-tu/assets/js/v/doan-tau.js"],
    y: "Ba đường DefiLlama công khai. Không gọi AI, không khoá nào. Việc nặng nhất " +
       "làm ở đây chứ không ở trình duyệt: xếp hơn 8.000 giao thức vào 18 toa và " +
       "dựng quan hệ phụ thuộc oracle từ khai báo của từng cái."
  },
  /* Thái Bộc Tự có HAI node, và tách đôi là có chủ ý — cùng lý do
     cặp node của Đài Quan Trắc, nhưng tách theo NGUỒN chứ không theo
     "cần model hay không":

       thai-boc-tu            DefiLlama → tiền đang nằm ở đâu
       thai-boc-tu-cong-truong  GitHub   → ai đang xây cái gì

     GitHub chạm hạn mức thì bảng đoàn tàu vẫn cập nhật, và DefiLlama
     ngã thì bảng công trường vẫn cập nhật. Gộp một node là để một
     nguồn ngã kéo cả hai bảng đứng im. */
  {
    ma: "thai-boc-tu-cong-truong", ten: "Công trường Thái Bộc Tự", cung: "thai-boc-tu",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-congtruong.mjs",
    ra: ["thai-boc-tu/assets/js/v/cong-truong.js"],
    y: "Hỏi GitHub 14 kho mã và lịch sử đề xuất ERC/EIP: nút thắt nào còn " +
       "người xây, chuẩn nào vừa mở. Dùng GITHUB_TOKEN Actions tự cấp — không " +
       "thêm secret nào, không gọi AI."
  },
  {
    ma: "thai-boc-tu-tin", ten: "Tin tức Thái Bộc Tự", cung: "thai-boc-tu",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-tintuc.mjs",
    ra: ["thai-boc-tu/assets/js/v/tin-tuc.js"],
    y: "Sáu nguồn RSS công khai (CoinDesk, Cointelegraph, Decrypt, Bitcoin Magazine, " +
       "blog Ethereum Foundation, Vitalik). Gắn nhãn toa bằng từ khoá. Ảnh TRỎ THẲNG " +
       "sang CDN toà soạn, không tải về repo. Không khoá nào, không gọi AI."
  },
  /* Cung thứ HAI vào vòng tiến hoá, và đó là phép thử cho lời hứa
     "thêm một cung là thêm một tham số, không phải thêm một script"
     ở đầu scripts/tien-hoa.mjs. Đúng vậy thật: node này không kèm
     script mới nào, chỉ đổi tên cung trong cùng bốn bước.

     Khác Hộ Bộ đúng một chỗ: `ra` KHÔNG có toa.js. File đó là sổ
     18 toa — luận, thứ tự bị đốt, hồ sơ input/output — tức là NỘI
     DUNG chứ không phải giao diện. Model sửa giao diện thì không có
     việc gì phải viết lại luận, và mở quyền đó ra là mời nó đi lạc
     khỏi điểm yếu đo được. */
  {
    ma: "thai-boc-tu-tien-hoa", ten: "Tiến hoá giao diện Thái Bộc Tự", cung: "thai-boc-tu",
    tram: "M18", che: "claude", nhip: 24,
    lenh: "tien-hoa.mjs de-bai + claude-code-action + tien-hoa.mjs cong --so",
    ra: ["thai-boc-tu/assets/css/app.css", "thai-boc-tu/assets/js/app.js",
         "thai-boc-tu/index.html", "thai-boc-tu/sw.js"],
    y: "Cùng khuôn ho-bo-tien-hoa, đổi tên cung. Phiếu đo lúc bật: 6/7 — trượt " +
       "thước tương phản màu, 5/15 cặp dưới WCAG AA."
  }
];
