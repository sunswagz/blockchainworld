/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — xuong

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của CHÍNH nhà máy — không thuộc cung nào.
   Đóng dấu bản số liệu, báo cáo sức khoẻ, giao hàng. */

import { VONG_XOAY, fileRa } from "../vong-xoay.mjs";

/* Đường ra của node `tien-hoa-xoay`, SINH TỪ chính danh sách xoay.

   Bản đầu tôi khai `ra: []` kèm câu "phần được NHẬN đi theo lệnh
   git add của chính cung ấy, vốn đã có sẵn". Câu đó SAI, và sai kiểu
   im lặng nhất: bước commit dùng `git add --pathspec-from-file` với
   đúng danh sách sinh từ `ra` của các node, mà `ra` của bảy cung
   trong vòng xoay chỉ khai file DỮ LIỆU (data.js, v/…) chứ không khai
   index.html hay app.css. Đếm thật trước khi vá: 0 trên 28 đường ấy
   có mặt trong danh sách 70 đường được commit.

   Nghĩa là node sẽ chạy, model sẽ sửa, cổng chặn sẽ NHẬN, rồi bước
   commit bỏ qua toàn bộ — mỗi ngày một lượt model vứt đi mà sổ vẫn
   ghi "ok".

   Sinh từ VONG_XOAY chứ không gõ tay 28 đường: thêm một cung vào
   vòng xoay mà quên thêm bốn đường ở đây thì đúng cung ấy im lặng
   không bao giờ được commit. `duong-ra` chỉ in đường CÓ THẬT trên
   đĩa nên cung thiếu file nào cũng không sinh lỗi pathspec.

   Và ĐÚNG VÌ THẾ mà tên file phải hỏi `fileRa`, không viết thẳng
   khuôn `${c}/assets/css/app.css` ra đây: Cổng Thành mang tên
   `portal.css`/`portal.js` ở gốc repo, nên khuôn ấy cho nó bốn đường
   không tồn tại — bị lọc sạch, không lỗi nào báo, và cung ấy mỗi tám
   ngày có một lượt model bị vứt. Cùng một cách hỏng như `ra: []` ở
   trên, chỉ nhỏ hơn tám lần nên khó thấy hơn tám lần. */
const RA_XOAY = VONG_XOAY.flatMap(fileRa);

export const NODE = [
  {
    ma: "dong-dau", ten: "Đóng dấu bản số liệu",
    tram: "M16", che: "script", nhip: 6,
    lenh: "node scripts/pin-snapshot.mjs",
    ra: [],
    y: "Pin bản số liệu 1,8 KB lên IPFS. Tự bỏ qua nếu sha256 trùng bản trước."
  },
  {
    ma: "bao-cao", ten: "Báo cáo sức khoẻ xưởng",
    tram: "M18", che: "claude", nhip: 24,
    lenh: "anthropics/claude-code-action",
    ra: ["factory/bao-cao.md"],
    y: "Claude Code Action đọc state.json rồi viết vài dòng tiếng Việt: " +
       "node nào đang ốm, ốm từ bao giờ, nên xem chỗ nào trước."
  },
  /* DÒ KHO — nguồn ý tưởng MỚI cho vòng tiến hoá.

     `tien-hoa.mjs ky-nang` chỉ chọn kỹ năng hợp với THƯỚC ĐANG
     TRƯỢT, nên nó không bao giờ tìm ra thứ đáng canh mà ta chưa nghĩ
     tới. Đó là trần thật: cung nào đạt hết thước thì model chỉ còn
     được bảo "tìm chỗ nào không thước nào đo được".

     Node này lục 3.696 kỹ năng của Tàng Thư Các theo sáu lĩnh vực,
     bỏ những cái đã khai thác (sổ ở factory/kho-da-dung.json), rồi
     tải vài ứng viên đầu bảng về kèm đoạn trích.

     Nhịp 168 giờ — MỘT LƯỢT MỖI TUẦN. Kho chỉ được quét lại vài
     lượt mỗi ngày và ứng viên mới nhỏ giọt; dò mỗi 6 giờ là 28 lượt
     tải cho cùng một danh sách không đổi. */
  {
    ma: "do-kho", ten: "Dò kho Tàng Thư Các",
    tram: "M11", che: "script", nhip: 168,
    lenh: "node scripts/do-kho.mjs quet",
    ra: ["factory/kho-de-xuat.json"],
    y: "Tìm kỹ năng CHƯA khai thác trong 3.696 cái, xếp hạng theo sáu lĩnh vực, " +
       "tải SKILL.md kèm trích dẫn. Máy lo tìm và xếp; model lo đọc hiểu — đã thử " +
       "rút luật bằng regex và bỏ vì cho ra rác."
  },
  /* VÒNG TIẾN HOÁ XOAY — bảy cung dùng chung một node.

     Năm cung có vòng riêng chạy mỗi ngày; bảy cung còn lại trước
     node này không có gì cả, chúng chỉ tiến khi có người ngồi vào
     sửa. Thêm bảy node nữa là thêm ~21 phút model mỗi lượt và đệm
     ngân sách tụt từ 4× xuống 2,4× — dưới ngưỡng mà phép canh trong
     `npm run kiem` đòi. Xoay thì tốn bằng MỘT vòng.

     Đổi lại mỗi cung chỉ được một bước mỗi tuần. So sánh đúng không
     phải "mỗi tuần" với "mỗi ngày", mà "mỗi tuần" với "không bao
     giờ".

     `ra` khai BỐN file của CẢ BẢY cung (xem RA_XOAY ở đầu file), chứ
     không rỗng: node sửa cung nào là tuỳ ngày, nhưng `git add` cần
     biết trước mọi đường có thể đụng tới. Khai rỗng là model sửa
     xong, cổng chặn nhận, rồi bước commit bỏ qua toàn bộ. */
  {
    ma: "tien-hoa-xoay", ten: "Tiến hoá xoay vòng (7 cung)",
    tram: "M14", che: "claude", nhip: 24,
    lenh: "tien-hoa.mjs xoay → do/de-bai → claude-code-action → cong --so",
    ra: RA_XOAY,
    y: "Mỗi ngày một cung trong scripts/vong-xoay.mjs, bảy ngày giáp vòng. " +
       "Cùng đường với năm vòng riêng, chỉ khác tên cung là biến."
  },
  /* PHIẾU TOÀN THÀNH — nhìn cả mười hai cung một lượt.

     `tien-hoa.mjs do` chấm được MỌI cung, nhưng chỉ BỐN cung có vòng
     tiến hoá gọi tới nó. Tám cung còn lại chưa từng được chấm trong
     một lượt bot nào, nên điểm của chúng chỉ hiện khi có người ngồi
     gõ lệnh — tức là gần như không bao giờ.

     Lượt chấm đầu tiên lộ ngay hai chuyện không ai biết: Thị Bạc Ty
     và Tử Cấm Thành đều trượt thước `ve` — phòng của chúng KHÔNG
     VẼ ĐƯỢC — và 11 trên 12 cung chưa có đường nhảy qua thanh bên.

     `che: "script"`: không gọi model, không tốn quota. Thấy được
     vấn đề là việc rẻ; sửa mới là việc đắt, và sửa vẫn là việc của
     vòng tiến hoá hoặc của người. Cả mười hai cung chấm xong trong
     ~8 giây, nên nhịp 24 giờ là rộng rãi. */
  {
    ma: "phieu", ten: "Phiếu toàn thành",
    tram: "M18", che: "script", nhip: 24,
    lenh: "node scripts/phieu-toan-thanh.mjs",
    ra: ["factory/phieu.json"],
    y: "Chấm cả 12 cung bằng đúng bộ thước của vòng tiến hoá, rồi xếp thước nào " +
       "đang trượt ở NHIỀU cung nhất. Nhìn từng cung thì mỗi lỗi trông như chuyện " +
       "riêng của cung đó; nhìn cả bảng mới thấy cái nào là bệnh chung."
  },
  /* HƯỚNG — node DUY NHẤT không sinh bản vá.

     Bảy vòng tiến hoá đều là vòng SỬA: thước hỏi "có gì hỏng
     không", hỏng thì vá xong là hết. Khi phiếu đầy thì model chỉ
     còn được bảo "tìm chỗ nào không thước nào đo" — nó làm được,
     nhưng đó là phán đoán trong phạm vi MỘT TRANG. Không cơ chế
     nào hỏi "cả cái này nên thành cái gì tiếp".

     Node này làm nửa suy ra được của câu ấy: đọc sổ tiến hoá xem
     model tự chọn việc gì khi được tự do, dò năng lực LỆCH giữa
     12 cung, tìm thứ xưởng sinh ra mà không trang nào đọc. Ra một
     danh sách ĐỀ XUẤT có số đếm kèm, xếp theo số cung chịu ảnh
     hưởng — người chọn, máy không chọn.

     Nhịp 168 giờ. Hướng không đổi theo ngày; chạy nó mỗi ngày chỉ
     đẻ ra một file giống hệt hôm qua và dạy người ta thôi đọc nó. */
  {
    ma: "huong", ten: "Đề xuất hướng",
    tram: "M18", che: "script", nhip: 168,
    lenh: "node scripts/huong.mjs",
    ra: ["factory/huong.json"],
    y: "Bốn tín hiệu từ chính repo — model tự chọn gì, cung nào lệch cung nào, " +
       "xưởng sinh gì không ai đọc, node nào chạy mà chưa đổi được gì. Mỗi đề xuất " +
       "kèm một con số và một lệnh để BÁC nó."
  },
  /* THƯỚC MỚI — khâu duy nhất SINH RA đích, thay vì đi về phía đích cũ.

     Mọi node tiến hoá hiện có đều tối ưu về phía bộ thước đang có.
     Không node nào làm bộ thước ấy dài ra. Hệ quả đo được 02/09/2026:
     mười hai cung đều 16/16 hoặc 17/17, và 26 lượt tiến hoá gần nhất
     đều là "16/16 → 16/16" — cổng chỉ còn chặn được tụt, không còn
     chỉ được hướng. Bản ghi cuối tự khai: "mọi thước đã đạt, nên vá
     một chỗ không thước nào đo".

     `do-kho` đã lo nửa đầu (lục 3.696 kỹ năng, ghi ứng viên vào
     kho-de-xuat.json) và `themUngVienMoi` đã nối ứng viên vào đề bài.
     Thiếu đúng khâu cuối: biến một kỹ năng thành một CÂY THƯỚC.

     `ra` là TỜ TRÌNH, không phải scripts/tien-hoa.mjs — và đó là chỗ
     node này cố ý khác mọi vòng khác. Vòng giao diện cho model sửa CSS
     rồi commit thẳng: sai thì thấy ngay trên trang. Đây model sửa
     chính cây thước, tức sửa định nghĩa "thế nào là tốt hơn". Cổng
     canh được thước mới chạy được, phân biệt được, và không làm thước
     cũ đổi phán quyết trên bất kỳ cung nào — nhưng KHÔNG canh được nó
     có đo đúng thứ đáng đo không. Một thước đếm dấu chấm phẩy cũng qua
     cả bốn cửa.

     Cho model tự cắm thước là cho nó tự ra đề thi cho chính nó, và
     `knowledge-os` đã gặp đúng chuyện đó: thước thứ tám của gói ấy cố
     ý KHÔNG có danh sách khai-bỏ-qua, vì danh sách ấy sẽ nằm trong
     lớp model được phép sửa. Nên bot dừng ở tờ trình; người áp bản vá.

     Nhịp 168 giờ vì nó ăn theo `do-kho` (cũng 168) và vì bộ thước
     không nên đổi mỗi ngày — mỗi cây thước mới làm cả mười hai cung
     tụt điểm, và tụt điểm là tín hiệu, không phải tiếng ồn. */
  {
    ma: "thuoc-moi", ten: "Đề xuất thước mới",
    tram: "M18", che: "claude", nhip: 168,
    lenh: "thuoc-moi.mjs de-bai → claude-code-action → cong --ghi",
    ra: ["factory/thuoc-de-xuat.md"],
    y: "Khâu sinh ĐÍCH mới. Model đọc kệ kỹ năng + điểm 12 cung rồi viết MỘT " +
       "cây thước; cổng bốn cửa kiểm; kết quả là một tờ trình để người duyệt, " +
       "KHÔNG phải một bản vá tự nhập."
  },
  {
    ma: "giao-hang", ten: "Giao hàng lên Pages",
    tram: "M16", che: "theo", nhip: 0,
    lenh: ".github/workflows/deploy-pages.yml",
    ra: [],
    y: "Không có nhịp riêng — chạy khi có commit số liệu. 27/27 lượt thành công."
  }
];
