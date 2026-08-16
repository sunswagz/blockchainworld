(function () {
"use strict";

/* ============================================================
   KHUNG — lớp PHƯƠNG PHÁP, đứng TRÊN chỗ chia chủ thể

   File này cố ý KHÔNG biết Việt Nam hay Trung Quốc là gì. Nó
   chỉ chứa thang bằng chứng và bảy tiêu chí — thứ dùng lại
   nguyên vẹn cho mọi đối tượng.

   Vì sao tách hẳn ra: nếu để mỗi chủ thể giữ một bản, hai bản
   sẽ lệch nhau sau vài lần sửa, và lúc đó mọi so sánh hình dạng
   bảng chấm giữa các nước thành vô nghĩa — vì chúng không còn
   được chấm bằng cùng một thước.

   Đây cũng là lý do bảng chấm Hướng Hoa Cường so được thẳng với
   Vingroup và THACO dù một bên là cá nhân, một bên là tập đoàn.
   ============================================================ */

/* Thang bằng chứng. Năm mức, vì "có" và "chưa thấy" không đủ:
   phần lớn tranh cãi nằm ở khoảng giữa, chỗ có dấu hiệu nhưng
   chưa đủ kết luận. Gộp khoảng giữa lại là chỗ suy đoán trà trộn
   vào chứng cứ. */
const THANG = [
  {k:'ratmanh', n:4, t:'RẤT MẠNH',   acc:'#f0503f', d:'Tài liệu chính thức, nhiều nguồn độc lập trùng khớp.'},
  {k:'manh',    n:3, t:'MẠNH',       acc:'#d29922', d:'Nguồn uy tín, kiểm chứng được, chưa bị phản bác.'},
  {k:'vua',     n:2, t:'CÓ DẤU HIỆU',acc:'#58a6ff', d:'Báo uy tín nhưng nguồn ẩn danh, hoặc suy ra từ hành vi.'},
  {k:'yeu',     n:1, t:'YẾU',        acc:'#6f7b8a', d:'Chỉ có tin đồn, infographic, hoặc suy diễn từ quy mô.'},
  {k:'khong',   n:0, t:'CHƯA THẤY',  acc:'#4b5563', d:'Đã tìm đúng chỗ và không thấy. Khác với "chưa tìm".'}
];

/* Bảy tiêu chí — phần KHÔNG đổi khi sang đối tượng khác.
   Đã kiểm: không câu nào nhắc tên một quốc gia cụ thể. */
const TIEUCHI = [
  {id:'sohuu', n:1, t:'Chủ sở hữu hưởng lợi', en:'beneficial ownership',
   hoi:'Bóc hết công ty trung gian thì ai thực sự cầm cổ phần?',
   tim:'Chuỗi sở hữu qua pháp nhân trung gian, người đứng tên hộ, cổ đông lớn thật sự đằng sau.'},
  {id:'hdqt', n:2, t:'Quyền kiểm soát HĐQT', en:'board control',
   hoi:'Ai có quyền bổ nhiệm hoặc buộc thay lãnh đạo?',
   tim:'Cơ chế bầu HĐQT, ai đề cử, có ghế nào do bên ngoài chỉ định không.'},
  {id:'von', n:3, t:'Kiểm soát nguồn vốn', en:'capital control',
   hoi:'Vốn đến theo điều kiện thị trường, hay theo một cơ chế riêng?',
   tim:'Bảo lãnh, tín dụng ưu đãi, ngoại lệ khỏi hạn mức, lãi suất khác thường.'},
  {id:'duan', n:4, t:'Giao đất & giao dự án', en:'project allocation',
   hoi:'Nguồn lực có được giao liên tục theo một cơ chế đặc biệt không?',
   tim:'Chỉ định thầu, giao đất, quy hoạch, quy mô và tần suất các lần được chọn.'},
  {id:'chidao', n:5, t:'Mệnh lệnh', en:'directive',
   hoi:'Có ai ra lệnh ngoài quyền của cổ đông và HĐQT không?',
   tim:'Tài liệu, biên bản, hoặc lời kể có kiểm chứng về chỉ đạo từ bên ngoài.'},
  {id:'lailo', n:6, t:'Chia lãi và gánh lỗ', en:'profit / loss sharing',
   hoi:'Lãi thuộc tư nhân, nhưng lỗ thì ai gánh?',
   tim:'Giải cứu bằng ngân sách, bảo lãnh nợ, khoanh nợ, mua lại tài sản xấu.'},
  {id:'mang', n:7, t:'Mạng liên quan', en:'related-party network',
   hoi:'Mạng sở hữu và người đại diện nối về đâu?',
   tim:'Giao dịch nội bộ, người thân, pháp nhân vệ tinh, ai là tâm của mạng.'}
];

window.DQT_KHUNG = { THANG: THANG, TIEUCHI: TIEUCHI };
})();
