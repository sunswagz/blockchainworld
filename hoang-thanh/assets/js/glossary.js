/* ═══════════════════════════════════════════════════════
   Chú giải viết tay — Hoàng Thành.

   Mọi thứ trong file này do người viết, KHÔNG tự sinh. Sửa
   thoải mái, không cần chạy lại build.

   Tách khỏi data.js vì hai thứ có tuổi thọ khác nhau: data.js
   bị ghi đè mỗi lần `npm run hoangthanh`, còn diễn giải thì
   nên sống lâu hơn số liệu.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  /* Nhãn độ chắc chắn — do người biên soạn gắn trong chính chương,
     theo Scout Protocol v5. App chỉ đếm và tô lại, không tự phán. */
  var NHAN = {
    "FACT": {
      lop: "nh-fact", mau: "#2E8B62", ten: "Sự kiện",
      giai: "Có bằng chứng khảo cổ, văn bản hoặc khoa học xác nhận. Nói được là “điều này đã xảy ra”."
    },
    "PRIMARY SOURCE": {
      lop: "nh-ps", mau: "#4A90C2", ten: "Nguồn gốc",
      giai: "Trích thẳng từ văn bản cổ. Bản thân văn bản là thật; điều nó kể thì chưa chắc."
    },
    "TRADITION": {
      lop: "nh-trad", mau: "#C9A227", ten: "Truyền thống",
      giai: "Truyền thuyết, tín ngưỡng, ký ức tập thể. Thật với người kể, chưa chắc thật về mặt lịch sử."
    },
    "SCHOLARLY INTERPRETATION": {
      lop: "nh-schol", mau: "#8B6BB1", ten: "Diễn giải",
      giai: "Cách đọc của giới nghiên cứu. Có lý lẽ, nhưng là suy luận chứ không phải ghi chép."
    },
    "OPEN QUESTION": {
      lop: "nh-open", mau: "#C0392B", ten: "Còn ngỏ",
      giai: "Chưa có câu trả lời dứt khoát. Được ghi ra để không giả vờ là đã biết."
    }
  };

  /* Lời dẫn cho từng trang. Viết ngắn, nói đúng thứ trang đó làm. */
  var GIAI = {
    rung:
      "Mười lăm nền văn hoá, mỗi nền một khu rừng riêng. Bấm vào một nền để mở " +
      "<b>roadmap</b> của nó: chương xếp theo <b>nguyên</b> (epoch) rồi <b>pha</b> (phase), " +
      "đúng thứ tự dòng chảy mà người biên soạn đã dựng. Vòng tiến độ đếm số chương " +
      "đã tinh luyện trên tổng số chương trong kế hoạch — nên chỗ còn thiếu cũng hiện ra, " +
      "không bị giấu đi.",
    nen:
      "Mỗi ô là một chương. Ô <b>viền xanh</b> đã có nội dung — bấm vào đọc toàn văn. " +
      "Ô <b>mờ</b> nằm trong kế hoạch nhưng chưa viết. Thứ tự và cách chia giai đoạn lấy " +
      "thẳng từ file roadmap gốc của nền này.",
    dongchay:
      "Đây là chỗ đọc <b>ngang</b> thay vì đọc dọc. Cùng một câu hỏi — thế giới bắt đầu " +
      "từ đâu, chết rồi đi về đâu, ai được quyền cai trị — mười lăm nền trả lời khác nhau. " +
      "Đặt các câu trả lời cạnh nhau thì thấy cái gì là riêng của một dân tộc, cái gì là " +
      "chung của loài người.",
    baihoc:
      "Mỗi nguyên được rút một chương tiêu biểu. Tiêu biểu ở đây có nghĩa cụ thể: chương " +
      "đó vừa tự viết ra bài học của mình, vừa <b>được nhiều chương khác dẫn lại nhất</b> " +
      "trong cùng nguyên — tức là chương mà các chương khác phải dựa vào mới giải thích " +
      "được chính chúng.",
    xuhuong:
      "Mỗi chương gắn nhãn độ chắc chắn cho từng phát biểu. Gộp cả nghìn chương lại rồi " +
      "xếp theo nguyên thì thấy một chuyển động: các nguyên đầu gần như toàn " +
      "<b>truyền thống</b>, càng về sau <b>sự kiện</b> càng chiếm chỗ. Đó là lúc thần thoại " +
      "nhường chỗ cho lịch sử có bằng chứng — và biểu đồ này cho biết chỗ chuyển nằm ở đâu."
  };

  /* Giải thích thuật ngữ dùng xuyên app. */
  var TU = {
    nguyen: "Nguyên (epoch) — một thời đại lớn trong dòng chảy của nền văn hoá đó.",
    pha: "Pha (phase) — một chặng nhỏ trong nguyên, gom vài chương cùng chủ đề.",
    chuong: "Chương — đơn vị nhỏ nhất: một nhân vật, một sự kiện, một khái niệm."
  };

  window.RUNG_GIAI = { NHAN: NHAN, GIAI: GIAI, TU: TU };
})();
