/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — dai-quan-trac

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của cung dai-quan-trac.
   Sửa nhịp, thêm hay bỏ node của cung này thì sửa ĐÚNG file này —
   không phiên nào khác phải chạm vào, nên không ai xung đột với ai. */

export const NODE = [
  /* Đài Quan Trắc có HAI node, và cặp này là ví dụ rõ nhất trong repo
     cho luật "đo được thì đừng để model đoán":

       quan-trac-do    ba nguồn số, so ngưỡng số học → miễn phí, xác định
       dai-quan-trac   đọc tin rồi viết một câu    → cần phán đoán, tốn tiền

     Cùng một cung, cùng một câu hỏi ("tình hình có căng không"), nhưng
     phần trả lời được bằng số thì đã tách hẳn ra khỏi phần cần model.
     Nhờ vậy khi lịch quét AI phải tắt vì tiền — đã xảy ra 14/08 — cung
     vẫn còn đèn xanh/vàng/đỏ chạy đều 4 lượt/ngày. */
  {
    ma: "quan-trac-do", ten: "Bảng cảnh báo Quan Trắc", cung: "dai-quan-trac",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-quantrac.mjs",
    ra: ["dai-quan-trac/assets/js/do.js", "dai-quan-trac/assets/js/tq/do.js"],
    y: "Ba nguồn miễn phí không cần khoá (Yahoo Finance, open.er-api, " +
       "Federal Register), so ngưỡng số học rồi tự đặt đèn. KHÔNG gọi AI. " +
       "Đo cho CẢ HAI chủ thể; bảng đo cái gì nằm ở DODAC trong data.js của cung."
  },
  {
    ma: "dai-quan-trac", ten: "Bản quét Đài Quan Trắc", cung: "dai-quan-trac",
    tram: "M07", che: "claude", nhip: 12,
    lenh: "claude-code-action + node scripts/build-scan.mjs",
    ra: ["dai-quan-trac/assets/js/scan.js", "dai-quan-trac/assets/js/tq/scan.js"],
    y: "Việc DUY NHẤT trong xưởng thật sự cần phán đoán: đọc tin 7 ngày " +
       "rồi viết một câu tiếng Việt + phân loại xanh/vàng/đỏ. " +
       "Trả bằng quota gói, không còn khoá API."
  },
  {
    ma: "dong-tin", ten: "Dòng tin Đài Quan Trắc", cung: "dai-quan-trac",
    tram: "M08", che: "claude", nhip: 12,
    lenh: "claude-code-action + node scripts/build-dong-tin.mjs",
    ra: ["dai-quan-trac/assets/js/tin.js"],
    y: "Lấy bài từ 11 nguồn RSS đã chọn tay, chấm điểm liên quan theo " +
       "từng chủ thể, rồi để model viết một đoạn suy luận móc bài vào " +
       "mắt xích nào của mạch truyền dẫn. Khối lượng CHẶN ĐƯỢC: 6 bài " +
       "× 3 chủ thể, tiêu đề và tóm tắt có sẵn nên không phải kéo cả " +
       "trang web vào ngữ cảnh như bản quét."
  },
];
