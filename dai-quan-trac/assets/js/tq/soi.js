(function () {
"use strict";

/* ============================================================
   SOI QUYỀN LỰC — TRUNG QUỐC

   Dùng LẠI nguyên khung 7 tiêu chí và thang bằng chứng của
   Việt Nam. Không định nghĩa lại — chúng nằm ở khung.js, vì
   phương pháp đứng TRÊN chỗ chia chủ thể.

   ── VÌ SAO HỒ SƠ NÀY QUAN TRỌNG HƠN NÓ TRÔNG ────────────────
   Hai hồ sơ Việt Nam đều là TẬP ĐOÀN. Đây là một CÁ NHÂN và
   một gia tộc. Nếu khung vẫn chấm được, và ra một hình dạng
   KHÁC HẲN, thì khung đang đo thật chứ không phải cỗ máy dán
   nhãn "ai cũng là công cụ nhà nước".

   Và nó ra hình khác thật:

     Vingroup · THACO   quan hệ Nhà nước qua VỐN và DỰ ÁN
     Hướng Hoa Cường    quan hệ qua MẠNG LƯỚI, mệnh lệnh TRỐNG

   Đó là kết quả đáng giá nhất của việc thêm chủ thể thứ hai.
   ============================================================ */

const SOI = [
{
  id:'huonghoacuong', ten:'Hướng Hoa Cường', nguoi:'向華強 · Charles Heung',
  ic:'star', acc:'#a371f7',
  vai:'Chủ tịch China Star Entertainment · gia tộc Hong Kong',
  lede:'Câu hỏi thường gặp là "Hướng Hoa Cường có phải người của Tập Cận Bình không". Đó lại là câu hỏi sai, cùng kiểu với "Vingroup có phải chân sau của Nhà nước không". Câu soi được là: <b>ông nằm ở ổ cắm nào trong hệ thống quyền lực Trung Quốc–Hong Kong</b> — và mắt xích quan trọng nhất hình thành <b>trước thời Tập hàng chục năm</b>.',

  gt:[
    {k:'A', t:'Hướng Hoa Cường là người của Tập Cận Bình',
     kl:'KHÔNG ĐỦ BẰNG CHỨNG', acc:'#4b5563',
     d:'Đã tìm bằng cả tiếng Trung lẫn tiếng Anh. Không tìm thấy hồ sơ công khai đáng tin cậy nào cho thấy Tập gặp riêng ông, hai gia đình có liên doanh, ông nhận chỉ đạo trực tiếp, hay thuộc một "phe Tập" đã được chứng minh. Các kết quả khẳng định mạnh chủ yếu là bình luận chính trị và nguồn có lập trường rất mạnh.'},
    {k:'B', t:'Một mạng lưới hình thành TRƯỚC thời Tập, sau đó được hấp thụ',
     kl:'RẤT PHÙ HỢP', acc:'#f0503f',
     d:'Mắt xích mạnh nhất có từ đầu thập niên 1990 — tức trước khi Tập là trung tâm quyền lực quốc gia. Sau 2012, toàn bộ hệ thống đó nằm dưới một cấu trúc ngày càng tập trung. Nhưng điều đó <b>không tự động biến mọi người thân Bắc Kinh thành "người của Tập"</b>.'}
  ],

  diem:{
    sohuu:{m:'khong', d:'Hồ sơ doanh nghiệp Hong Kong xác nhận ông là chủ tịch kiêm giám đốc điều hành <b>China Star Entertainment</b>, một công ty <b>niêm yết tại Hong Kong</b>, và tới hồ sơ HKEX tháng 6/2026 ông vẫn trong ban lãnh đạo. Không tìm thấy mạng pháp nhân nhà nước Trung Quốc đứng sau sở hữu.'},
    hdqt:{m:'khong', d:'Không thấy cơ chế cơ quan Trung Quốc bổ nhiệm ghế nào trong HĐQT China Star. Đây là công ty niêm yết, quản trị theo luật Hong Kong.'},
    von:{m:'yeu', d:'Đây là <b>khoảng trống lớn</b>, không phải kết luận. Chưa có hồ sơ công khai về cơ cấu tài trợ, chủ nợ hay dòng vốn của China Star và các pháp nhân liên quan. Suy từ quy mô sang "được nhà nước bơm vốn" là đúng thứ phải tránh.'},
    duan:{m:'vua', d:'Không phải ngành xin giao đất như Vingroup. Nhưng có dấu hiệu tiếp cận đáng chú ý: đầu thập niên 1990 gia đình Hướng đầu tư vào <b>đặc khu kinh tế Thâm Quyến</b>, và lễ khai trương studio điện ảnh năm 1993 có sự hiện diện của một nhân vật cấp cao — xem mục "Diệp gia".'},
    chidao:{m:'khong', d:'<b>ĐÂY LÀ Ô TRỐNG QUAN TRỌNG NHẤT CỦA CẢ HỒ SƠ.</b> Đã tìm 向華強+習近平 và các biến thể. Không thấy: gặp riêng, bạn cá nhân, liên doanh hai gia đình, nhận chỉ đạo, thuộc phe. Chính chỗ này làm hình dạng bảng chấm khác hẳn Vingroup và THACO.'},
    lailo:{m:'khong', d:'Không tìm thấy bằng chứng về việc ngân sách hay thiết chế nhà nước gánh lỗ cho hệ China Star, cũng như chiều ngược lại.'},
    mang:{m:'ratmanh', d:'Ô ĐẦY NHẤT, và là toàn bộ giá trị của hồ sơ. <b>Diệp Tuyển Bình</b> hiện diện tại lễ khai trương 1993, con trai <b>Diệp Tân Long</b> sau đó thành đối tác trong một công ty đầu tư Hong Kong. Ông từng giữ vai trò <b>phó chủ tịch danh dự China Film Foundation</b>. Con trai <b>Hướng Tả</b> tham gia uỷ ban <b>All-China Youth Federation</b>. Và 2020 ông nằm trong danh sách hơn 2.600 người giới văn hoá–nghệ thuật Hong Kong ký ủng hộ Luật An ninh Quốc gia.'}
  },

  muc:[
    {id:'phanchung', t:'Ba mảnh phản chứng', ic:'gauge', mo:true, khoi:[
      {k:'p', d:'Nếu giả thuyết A đúng — ông là người của Tập — thì <b>không thể có</b> những chuyện dưới đây.'},
      {k:'the', ds:[
        {t:'Gốc chính trị của gia tộc là QUỐC DÂN ĐẢNG', acc:'#2ea043',
         d:'Cha ông, <b>Hướng Tiền</b>, mang quân hàm thiếu tướng Quốc dân đảng và tham gia hoạt động chống Nhật tại Hong Kong. Đây là gốc <b>chống cộng</b>, không phải gốc ĐCSTQ. Một mạng lưới xuất phát như vậy mà nay thân Bắc Kinh là chuyện <b>đổi trục</b>, không phải chuyện "vốn là người của Đảng".'},
        {t:'Đài Loan bác đơn cư trú', acc:'#2ea043',
         d:'Năm 2021 cơ quan Đài Loan bác đơn của ông và con trai, viện dẫn lợi ích quốc gia và an ninh. Nếu ông là một mắt xích được điều hành trơn tru thì một hồ sơ bị soi và bị chặn công khai như vậy là kết quả khó hiểu.'},
        {t:'Mọi mũi tên đều dừng trước một chỗ', acc:'#2ea043',
         d:'Tìm được rất nhiều về mạng lưới, thiết chế, quan hệ lịch sử. Nhưng đúng ô "nhận chỉ đạo cá nhân" thì <b>trống</b>. Một điều tra trung thực phải để nguyên ô trống đó thay vì lấp bằng suy diễn.'}
      ]}
    ]},

    {id:'giapha', t:'Gia phả quyền lực — ba anh em, ba hướng', ic:'chain', khoi:[
      {k:'p', d:'Phải dựng đúng gia phả trước, không thì mọi kết luận sau đều lệch. Nguồn Caixin năm 2025 mô tả <b>Hướng Tiền (向前)</b> — cha ông — như người được xem là nhà sáng lập hoặc nền móng của <b>Tân Nghĩa An</b>.'},
      {k:'a', d:'              HƯỚNG TIỀN 向前\n        Quốc dân đảng · Nghĩa An\n                   │\n     ┌─────────────┼─────────────┐\n     │             │             │\nHƯỚNG HOA VIÊM  HƯỚNG HOA CƯỜNG  HƯỚNG HOA THẮNG\n     │             │             │\nTân Nghĩa An    điện ảnh       điện ảnh\nbị cáo buộc     Win\'s /         Win\'s\nlãnh đạo        China Star'},
      {k:'p', d:'Con trưởng <b>Hướng Hoa Viêm</b> được nhiều nguồn xem là người đứng đầu Tân Nghĩa An từ thập niên 1950 tới khoảng 1990. Nhưng phải ghi đủ cả hai vế: ông từng bị kết án trong một vụ án liên quan hội Tam Hoàng năm 1988, <b>và bản án đó sau bị huỷ khi kháng cáo</b>.'},
      {k:'q', do:1, d:'Đây là chỗ dễ biến cáo buộc thành bản án nhất. Bỏ vế thứ hai đi là viết sai lịch sử tư pháp — dù vế thứ nhất có đúng.'}
    ]},

    {id:'diepgia', t:'Diệp gia và mắt xích 1993 — phát hiện lớn nhất', ic:'flow', mo:true, khoi:[
      {k:'q', d:'Nguồn của cả mảng này là nghiên cứu học thuật của <b>Emmanuel Jourda</b> về quan hệ ĐCSTQ — Mặt trận Thống nhất — hội Tam Hoàng, cộng nguồn báo chí đương thời mà nghiên cứu đó dẫn lại.'},
      {k:'p', d:'Đây mới là phần đáng chú ý hơn rất nhiều so với việc cố tìm một bức ảnh bắt tay. Nghiên cứu học thuật về quan hệ giữa ĐCSTQ, Mặt trận Thống nhất và các hội Tam Hoàng ghi nhận một chuyển dịch cuối thập niên 1980 – đầu 1990: các thành viên gia đình Hướng bắt đầu đầu tư vào <b>đặc khu kinh tế Thâm Quyến</b> và xây quan hệ với quan chức cấp cao ĐCSTQ ở Quảng Đông.'},
      {k:'moc', ds:[
        {y:'1991', t:'Sinh nhật ở Hong Kong', d:'Quan chức cấp cao Quảng Đông đến Hong Kong dự sinh nhật Hướng Hoa Viêm. Nghiên cứu dẫn nguồn đương thời cho sự kiện đó.'},
        {y:'1993', t:'Studio Thâm Quyến — và Diệp Tuyển Bình', d:'Hướng Hoa Cường và Hướng Hoa Thắng mở một studio điện ảnh tại Thâm Quyến. Lễ khai trương có sự hiện diện của <b>Diệp Tuyển Bình (葉選平)</b> — khi đó là nhân vật cấp cao của Chính hiệp toàn quốc, trước đó là lãnh đạo Quảng Đông, và là con của nguyên soái Diệp Kiếm Anh.', hot:1},
        {y:'sau đó', t:'Diệp Tân Long thành đối tác', d:'Con trai Diệp Tuyển Bình, <b>Diệp Tân Long</b>, sau đó trở thành đối tác của Hướng Hoa Cường trong một công ty đầu tư Hong Kong.', hot:1}
      ]},
      {k:'a', d:'          BẮC KINH\n             ↓\n           ĐCSTQ\n             ↓\n        QUẢNG ĐÔNG\n             ↓\n     DIỆP TUYỀN BÌNH\n             ↓\n     ┌───────┴────────┐\nDIỆP TÂN LONG    hệ Chính hiệp\n     ↓\nđối tác đầu tư\n     ↓\nHƯỚNG HOA CƯỜNG\n     ↓\nđiện ảnh + vốn\n     ↓\n  THÂM QUYẾN'},
      {k:'q', d:'<b>Đây có vẻ là một ổ cắm chính trị thật sự</b>, vì nó dựa vào quan hệ doanh nghiệp cụ thể và sự hiện diện của một nhân vật cấp cao — chứ không chỉ là tin đồn "quen lãnh đạo".'},
      {k:'q', do:1, d:'Và mốc <b>1993</b> cực kỳ quan trọng: lúc đó Tập Cận Bình chưa phải trung tâm quyền lực quốc gia. Nghĩa là mắt xích mạnh nhất của nhà Hướng <b>không đi qua Tập</b>, mà đi qua một thế hệ lãnh đạo khác hẳn.'}
    ]},

    {id:'1993', t:'Vì sao đúng năm 1993 — Bắc Kinh công khai đổi thái độ', ic:'book', khoi:[
      {k:'p', d:'Mắt xích trên không phải ngẫu nhiên rơi vào 1993. Cùng năm đó chính sách với các hội đoàn ngầm đổi công khai.'},
      {k:'p', d:'Ngày <b>8/4/1993</b>, Bộ trưởng Công an Trung Quốc <b>Đào Tứ Cầu</b> công khai phát biểu rằng có thể đoàn kết với các tổ chức Tam Hoàng nếu họ "yêu nước" và quan tâm tới ổn định, thịnh vượng Hong Kong. Phát biểu này được ghi nhận cả trong báo chí đương thời lẫn nghiên cứu học thuật sau này.'},
      {k:'p', d:'Nghiên cứu Cambridge năm 2023 đi xa hơn: từ thập niên 1990, giữa một số nhóm Tam Hoàng "ái quốc" và chính quyền trung ương Trung Quốc hình thành các quan hệ mà tác giả mô tả như <b>patron–client</b> — bảo trợ và khách hàng: mạng lưới địa phương hỗ trợ duy trì trật tự chính trị, đổi lại tiếp cận kinh doanh và không gian hoạt động có thể được mở rộng.'},
      {k:'a', d:'TRƯỚC                    SAU CẢI CÁCH MỞ CỬA\n\nQuốc dân đảng                 ĐCSTQ\n     ↓                          ↓\nHướng Tiền                  "ÁI QUỐC"\n     ↓                          ↓\nNghĩa An            ┌───────────┼───────────┐\n                doanh nhân   hội đoàn   giới ngầm\n                    └───────────┼───────────┘\n                                ↓\n                          HONG KONG\n                                ↓\n                           NHÀ HƯỚNG'},
      {k:'q', d:'Đây là bài học chung, không riêng nhà Hướng: <b>một mạng lưới có xuất phát điểm chống cộng không nhất thiết tiếp tục chống Bắc Kinh</b>. Khi tương quan quyền lực đổi, nó có thể được <b>tái hấp thụ</b>. Đó chính là cơ chế thống chiến ở dạng thực tế nhất.'}
    ]},

    {id:'doitruc', t:'Đổi trục qua ba thế hệ', ic:'stairs', khoi:[
      {k:'a', d:'THẾ HỆ CHA\n\nHướng Tiền\n    ↓\nKMT / Trung Hoa Dân Quốc\n    ↓\n  CHỐNG CỘNG\n\n────────────────────\n\nTHẾ HỆ CON\n\nHướng Hoa Cường\n    ↓\nlàm ăn đại lục\n    ↓\nquan hệ giới chính trị PRC\n    ↓\nỦNG HỘ CHÍNH SÁCH BẮC KINH'},
      {k:'p', d:'Đặt vào đúng hoàn cảnh lịch sử thì cả câu chuyện đổi nghĩa. Không phải "một gia đình giang hồ tự nhiên xuất hiện ở Hong Kong", mà là:'},
      {k:'a', d:'NỘI CHIẾN TRUNG QUỐC\n        ↓\n   KMT ─ ĐCSTQ\n        ↓\ntình báo + quân đội + hội đoàn\n        ↓\n   HONG KONG\n        ↓\nmạng người Hoa chống cộng\n        ↓\n   GIA ĐÌNH HƯỚNG'},
      {k:'q', d:'Đó mới là một <b>chuyển trục quyền lực qua nhiều thế hệ</b>, chứ không phải câu chuyện đơn giản kiểu "nhà Hướng vốn là người của ĐCSTQ".'}
    ]},

    {id:'thiethche', t:'Các thiết chế — chỗ ổ cắm bắt đầu rõ', ic:'map', khoi:[
      {k:'p', d:'Quan hệ cá nhân khó kiểm chứng. Nhưng <b>chức danh trong thiết chế</b> thì kiểm được, và đây là chỗ hồ sơ chắc nhất.'},
      {k:'the', ds:[
        {t:'China Film Foundation', vd:'中国电影基金会', acc:'#a371f7',
         d:'Trong vụ xin cư trú Đài Loan 2021, nguồn Taipei Times/CNA cho biết phía an ninh Đài Loan xác định ông từng là <b>phó chủ tịch danh dự</b> của tổ chức này — một tổ chức gắn với hệ thống quản lý điện ảnh nhà nước Trung Quốc.'},
        {t:'All-China Youth Federation', vd:'Trung Hoa Toàn quốc Thanh niên Liên hiệp hội', acc:'#58a6ff',
         d:'Con trai ông, <b>Hướng Tả (Jacky Heung)</b>, được phía Đài Loan xác định là thành viên uỷ ban — một tổ chức nằm trong hệ thống các tổ chức quần chúng chính trị của Trung Quốc.'},
        {t:'China Star Entertainment', vd:'niêm yết HKEX', acc:'#2ea043',
         d:'Doanh nghiệp thật, niêm yết thật, hồ sơ công khai. Tới tháng 6/2026 ông vẫn là executive director — tức không chỉ là một nhân vật của lịch sử điện ảnh thập niên 1990.'}
      ]},
      {k:'a', d:'                    ĐCSTQ\n                      │\n        ┌─────────────┼─────────────┐\n    CHÍNH HIỆP     ĐIỆN ẢNH     THANH NIÊN\n        │             │             │\n Diệp Tuyển Bình      │      All-China Youth\n        │             │        Federation\n        │      China Film          │\n        │      Foundation      HƯỚNG TẢ\n        │             │\n        └──── HƯỚNG HOA CƯỜNG ────┘\n                      │\n                 CHINA STAR\n                      │\n            điện ảnh Hong Kong'},
      {k:'q', d:'Đến đây nó bắt đầu giống <b>một hệ sinh thái hơn là một quan hệ cá nhân</b>. Và đó chính là điều khiến nhân vật này đáng nghiên cứu: ông <b>không phải quan chức</b>, nhưng đứng ở giao điểm giữa tiền, điện ảnh, giới tinh hoa Hong Kong, Macau và quan hệ với đại lục.'}
    ]},

    {id:'my', t:'Hồ sơ Mỹ 1992 — và vì sao phải cẩn thận với chính nó', ic:'src', khoi:[
      {k:'p', d:'Đây là bằng chứng mạnh nhất cho phía cáo buộc, và cũng là chỗ dễ dùng sai nhất.'},
      {k:'p', d:'Báo cáo năm 2013 của Uỷ ban Kinh tế và An ninh Mỹ–Trung thuộc Quốc hội Mỹ nhắc lại rằng một báo cáo năm 1992 của Tiểu ban Điều tra Thường trực Thượng viện Mỹ đã xác định <b>Charles Heung là một "officer" của Sun Yee On</b>.'},
      {k:'q', do:1, d:'Nhưng The Guardian kiểm tra lại và chỉ ra: báo cáo 1992 <b>đặt tên ông trong một sơ đồ tổ chức nhưng không giải thích nguồn của kết luận đó trong phần nội dung</b>. Ông nhiều lần phủ nhận tham gia Tân Nghĩa An, thừa nhận gia đình có "triad background" nhưng nói bản thân không dính líu. Guardian cũng ghi ông chưa từng bị bắt, truy tố hay kết án vì cáo buộc thành viên Sun Yee On.'},
      {k:'so', ds:[
        {t:'Cha — nguồn gốc Tân Nghĩa An', v:'RẤT MẠNH', d:'Caixin 2025', acc:'#f0503f'},
        {t:'Anh — lãnh đạo lịch sử', v:'MẠNH', d:'nhưng bản án 1988 đã bị huỷ khi kháng cáo', acc:'#d29922'},
        {t:'Bản thân — là lãnh đạo Tân Nghĩa An', v:'CHƯA ĐỦ', d:'có hồ sơ cáo buộc đáng kể, KHÔNG đủ để gọi là sự thật tư pháp', acc:'#6f7b8a'}
      ]},
      {k:'q', d:'Đây là khác biệt rất quan trọng, và nó là <b>cùng một nguyên tắc</b> đã dùng ở hồ sơ Vingroup với chuyện "150 triệu USD Nestlé": một con số lặp nhiều lần trên báo chí không tự biến thành một con số đã được xác nhận.'}
    ]},

    {id:'dailoan', t:'Vụ Đài Loan 2021 — rủi ro an ninh ≠ điệp viên', ic:'gauge', khoi:[
      {k:'p', d:'Đài Loan bác đơn cư trú của Hướng Hoa Cường và Hướng Tả. Cơ quan nhập cư viện dẫn Điều 22, trong đó có các căn cứ liên quan lợi ích quốc gia, an ninh và mối liên hệ với các thực thể chính quyền Trung Quốc; vụ việc được phối hợp xem xét giữa Cơ quan Di trú, Cục An ninh Quốc gia và Hội đồng Đại lục.'},
      {k:'p', d:'Nguồn an ninh Đài Loan còn nói họ <b>không thể loại trừ</b> khả năng gia đình Hướng có mục đích mang tính nhiệm vụ.'},
      {k:'a', d:'ĐÀI LOAN COI LÀ RỦI RO AN NINH\n\n            ≠\n\nĐÀI LOAN CHỨNG MINH HƯỚNG LÀ ĐIỆP VIÊN'},
      {k:'q', do:1, d:'"Không thể loại trừ" là <b>nhận định an ninh được báo chí dẫn lại</b>, không phải phán quyết tư pháp. Một cơ quan an ninh có nghĩa vụ nghi ngờ; đó là công việc của họ, không phải bằng chứng.'}
    ]},

    {id:'nsl', t:'Dưới thời Tập — điều KHÔNG chứng minh được và điều chứng minh được', ic:'brain', mo:true, khoi:[
      {k:'p', d:'Đây là mục trả lời thẳng câu hỏi ban đầu, và nó tách hai chuyện hoàn toàn khác nhau.'},
      {k:'sd', ds:[
        {sai:'Tập chỉ đạo cá nhân Hướng Hoa Cường.',
         dung:'<b>Không chứng minh được.</b> Đã tìm bằng cả tiếng Trung lẫn tiếng Anh. Không có hồ sơ công khai đáng tin cậy nào cho thấy gặp riêng, bạn cá nhân, liên doanh hai gia đình, nhận chỉ đạo, hay thuộc một "phe Tập" đã được chứng minh.'},
        {sai:'Vậy thì không có liên hệ nào đáng nói.',
         dung:'<b>Sai theo hướng ngược lại.</b> Năm 2020 ông nằm trong danh sách hơn <b>2.600</b> nhân vật giới văn hoá–nghệ thuật Hong Kong ký tuyên bố ủng hộ việc Bắc Kinh xây dựng Luật An ninh Quốc gia Hong Kong. Đó là hành vi công khai, kiểm chứng được, và nó khớp đúng với trục "ái quốc – ổn định – Hong Kong".'}
      ]},
      {k:'a', d:'KHÔNG chứng minh được:\n\n  TẬP ──✕── HƯỚNG\n     chỉ đạo cá nhân\n\n────────────────────────────\n\nNHƯNG chứng minh được:\n\n        TẬP\n         ↓\n       ĐCSTQ\n         ↓\n chính sách Hong Kong\n         ↓\n  ┌──────┼──────┐\nan ninh  ái quốc  thống chiến\n quốc gia trị Cảng\n  └──────┼──────┘\n         ↓\ngiới doanh nghiệp và\nvăn hoá thân Bắc Kinh\n         ↓\n  HƯỚNG HOA CƯỜNG\n         ↓\n  công khai ủng hộ NSL'},
      {k:'p', d:'Và chính Tập đã mô tả ổ cắm đó gần như công khai: trong bài phát biểu về công tác Mặt trận Thống nhất, ông nhấn mạnh phát triển lực lượng <b>"ái quốc ái Cảng"</b>, củng cố nhận thức quốc gia tại Hong Kong, duy trì Hong Kong ổn định, và tăng cường sự lãnh đạo toàn diện của Đảng đối với công tác thống chiến.'},
      {k:'q', d:'Hướng Hoa Cường <b>phù hợp với tầng dưới của sơ đồ đó về hành vi và mạng lưới được công khai</b>. Nhưng điều đó vẫn không đủ để nói ông là "đặc vụ" hay "thuộc hạ của Tập". Hai chuyện hoàn toàn khác nhau.'}
    ]},

    {id:'socket', t:'Đặt nhà Hướng vào đâu trên bản đồ — kèm một dấu hỏi', ic:'chain', khoi:[
      {k:'p', d:'Nhà Hướng <b>không nằm trong organigram chính thức</b> của bộ máy. Nên không được vẽ mũi tên thẳng từ Tập xuống. Vị trí hợp lý hơn là ở vành đai:'},
      {k:'a', d:'              BẮC KINH\n                 ↓\n     chính sách Hong Kong\n                 ↓\n      United Front / tinh hoa\n                 ↓\n   ┌─────────────┼─────────────┐\ndoanh nhân   hội đoàn      văn hoá\n   │\n   ↓\nmạng lưới HK\n   │\n   ?      ← dấu hỏi này là NỘI DUNG,\n   │        không phải chỗ chưa làm xong\n   ↓\nNHÀ HƯỚNG / SUN YEE ON'},
      {k:'q', do:1, d:'Nghiên cứu Cambridge mô tả quan hệ patron–client giữa một số nhóm "ái quốc" và nhà nước. Nhưng <b>quan hệ ≠ chỉ huy · clientelism ≠ chi bộ đảng · hợp tác ≠ cơ quan an ninh</b>. Nhà Hướng có thể nằm ở vành đai mạng lưới xã hội–kinh doanh–Hong Kong, nhưng chưa có bằng chứng để đặt vào một ổ cắm chính thức.'}
    ]},

    {id:'doc', t:'Đọc cho đúng', ic:'brain', khoi:[
      {k:'sd', ds:[
        {sai:'Hướng Hoa Cường thân Bắc Kinh, vậy là người của Tập.',
         dung:'Thân Bắc Kinh, nằm trong mạng lưới quyền lực, và quan hệ cá nhân trực tiếp với Tập là <b>ba mức khác nhau</b>. Mức một và hai có bằng chứng; mức ba chưa.'},
        {sai:'Cơ quan Mỹ đã xác định ông là officer của Sun Yee On, vậy là xong.',
         dung:'Có tài liệu chính phủ Mỹ thật. Nhưng cơ sở của sơ đồ 1992 không được giải thích đầy đủ, ông phủ nhận, và ông chưa từng bị bắt, truy tố hay kết án vì cáo buộc đó. Đó là <b>hồ sơ cáo buộc đáng kể</b>, không phải sự thật tư pháp.'},
        {sai:'Đài Loan nói không loại trừ nhiệm vụ, vậy ông là điệp viên.',
         dung:'Đó là nhận định an ninh được báo chí dẫn lại, không phải phán quyết. Một cơ quan an ninh có nghĩa vụ không loại trừ.'},
        {sai:'Tam Hoàng ái quốc là cánh tay của ĐCSTQ.',
         dung:'Nghiên cứu mô tả quan hệ <b>patron–client</b>, tức bảo trợ và khách hàng. Đó không phải quan hệ cơ quan. Gọi nó là cơ quan chính thức của Đảng là bước nhảy không có bằng chứng.'}
      ]}
    ]},

    {id:'gap', t:'Vòng sau — chỗ chuỗi có thể khép lại', ic:'src', khoi:[
      {k:'p', d:'Chuỗi đáng đào nhất đã lộ ra khá rõ, và nó KHÔNG đi qua Tập:'},
      {k:'ds', ds:[
        '<b>Diệp Tuyển Bình → Diệp Tân Long → pháp nhân đầu tư chung với Hướng Hoa Cường</b> — cổ đông, dòng tiền, thời điểm.',
        'Macau và junket: đường nối giữa vốn, casino và mạng lưới Hong Kong.',
        'Nguồn năm <b>1997</b> nói ông có quan hệ kinh doanh giải trí ở Bắc Kinh và mạng lưới liên quan giới chính trị Trung Quốc. Đây là tuyên bố mạnh dựa trên báo chí cũ — coi là <b>mảnh đáng theo</b>, chưa đặt ngang hồ sơ doanh nghiệp hay bản án.',
        'China Film Foundation: vai trò cụ thể, thời gian giữ, và những ai cùng ban.',
        'Các nhân vật chính trị mà Hướng <b>thực sự</b> gặp — có hồ sơ, không phải lời kể.',
        'Chuỗi xa hơn: <b>KMT → hệ tình báo thời Tưởng → Cục Quân Thống → mạng Hong Kong–Macau–Đông Nam Á → hội Tam Hoàng chống cộng → Hướng Tiền</b>.'
      ]},
      {k:'q', d:'Nếu chuỗi đó khép lại bằng <b>hồ sơ doanh nghiệp và giao dịch</b> chứ không chỉ bài báo, chúng ta bắt đầu nhìn thấy đường dây quyền lực thật thay vì tin đồn. Và đây cũng là chỗ phải phân biệt cực kỹ giữa <b>hồ sơ tình báo thật</b> với <b>truyền thuyết giang hồ</b>.'}
    ]}
  ],

  noi:['elite','anninh']
}
];

/* ─────────────────────────────────────────────────────────────
   DANH SÁCH SOI — hai mươi ổ cắm, không phải hai mươi người

   Khác Việt Nam ở chỗ: bên kia xếp theo TẬP ĐOÀN, bên này xếp
   theo Ổ CẮM. Vì ở Trung Quốc quyền lực gắn với ghế nhiều hơn
   gắn với tài sản — một người rời ghế là rời quyền lực, còn
   một tập đoàn thì không mất tài sản khi đổi chủ tịch.
   ───────────────────────────────────────────────────────────── */
const DANHSACH = [
  {muc:1, t:'LÕI — ổ cắm giữ cả hệ thống lại với nhau', acc:'#f0503f', ds:[
    {ten:'Tập Cận Bình', o:'Tổng Bí thư · Chủ tịch nước · Chủ tịch Quân uỷ',
     ghi:'Chức mạnh nhất KHÔNG phải Chủ tịch nước mà là Tổng Bí thư và Chủ tịch Quân uỷ Trung ương. Ông cũng trực tiếp đứng đầu Uỷ ban An ninh Quốc gia Trung ương — nơi "an ninh" được mở rộng sang kinh tế, tài chính, công nghệ, mạng, dữ liệu, văn hoá, sinh học, chuỗi cung ứng. Hệ quả phải nhớ: một vấn đề kinh tế có thể ĐỒNG THỜI là một vấn đề an ninh.'},
    {ten:'Thường vụ Bộ Chính trị', o:'bảy người',
     ghi:'Tập Cận Bình · Lý Cường · Triệu Lạc Tế · Vương Hộ Ninh · Thái Kỳ · Đinh Tiết Tường · Lý Hi. Mỗi người thường không phụ trách "một bộ" mà ngồi ở điểm nối nhiều hệ.'},
    {ten:'Thái Kỳ', o:'Văn phòng Trung ương · Ban Bí thư',
     ghi:'Ổ cắm ít nổi tiếng mà cực mạnh. Nếu Tập là CPU thì Văn phòng Trung ương là bus dữ liệu: lịch lãnh đạo, văn kiện mật, luồng báo cáo đi lên và luồng chỉ thị đi xuống. Quyền lực thông tin rất dễ bị bỏ sót khi chỉ nhìn chức danh bộ trưởng.'},
    {ten:'Thạch Thái Phong', o:'Ban Tổ chức Trung ương — nhân sự · đường thăng tiến',
     ghi:'Ổ CẮM MẠNH NHẤT CỦA CẢ HỆ. Kiểm soát ai lên ai xuống thì không cần gọi điện ra lệnh từng ngày — cấp dưới TỰ HỌC cách biết trung ương muốn gì. Tài liệu tổ chức năm 2026 đặt "yêu cầu chính trị" làm tiêu chí đầu tiên khi chọn cán bộ.'},
    {ten:'Lý Hi · Lưu Kim Quốc', o:'CCDI · Uỷ ban Giám sát Quốc gia',
     ghi:'Một bộ máy hai danh nghĩa Đảng/Nhà nước — Lưu Kim Quốc đồng thời là Bí thư Ban Bí thư, Phó Bí thư CCDI và Chủ nhiệm Uỷ ban Giám sát Quốc gia. Năm 2025 lập ~1,012 triệu vụ, lưu trí ~47.000 người, ~983.000 quyết định kỷ luật hoặc xử lý công vụ. Không phải văn phòng tượng trưng.'}
  ]},
  {muc:2, t:'CƯỠNG CHẾ VÀ THÔNG TIN', acc:'#d29922', ds:[
    {ten:'Trần Văn Thanh', o:'Uỷ ban Chính pháp Trung ương',
     ghi:'Công an · toà án · viện kiểm sát · an ninh nhà nước · tư pháp KHÔNG phải năm hòn đảo độc lập — có một trục điều phối chính trị phía trên. Hội nghị chính pháp tháng 1/2026 tiếp tục yêu cầu "sự lãnh đạo tuyệt đối của Đảng". Năm 2025 hệ thống kỷ luật xử lý ~1,976 triệu manh mối và mở ~789.000 vụ.'},
    {ten:'Vương Tiểu Hồng', o:'Bộ Công an · Bí thư Ban Bí thư',
     ghi:'Trật tự, tội phạm, hộ khẩu, cảnh sát, an ninh nội địa, quản lý hành chính. Khác hẳn Bộ An ninh Nhà nước — hai cơ quan, hai bài toán, người ngoài hay gộp nhầm.'},
    {ten:'Trần Nhất Tâm', o:'Bộ An ninh Nhà nước',
     ghi:'Phản gián, tình báo, an ninh quốc gia, chống các hoạt động bị coi là đe doạ nhà nước.'},
    {ten:'Lý Thư Lỗi · Trang Vinh Văn', o:'Ban Tuyên truyền · CAC',
     ghi:'Kiểm soát thông tin có HAI nhánh, và chỉ nhìn Great Firewall là mất một nửa: NGĂN CHẶN, và SẢN XUẤT "thực tại chính thống". Không chỉ "bạn không được đọc X" mà còn "đây là cách X nên được hiểu". Quy định GenAI buộc nội dung phù hợp "giá trị cốt lõi xã hội chủ nghĩa" — tuyên truyền 2.0 cộng quản trị dữ liệu 2.0.'},
    {ten:'Quân uỷ Trung ương · PLA', o:'Trương Hựu Hiệp · Trương Thăng Dân · Lưu Chấn Lập',
     ghi:'Quân đội thuộc ĐẢNG, không thuộc nhà nước — cạnh PLA còn PAP (vũ cảnh) và các cấu phần an ninh quân sự liên quan. Danh sách lãnh đạo tháng 7/2026 NGẮN BẤT THƯỜNG sau loạt thanh lọc 2023–2026 — Hà Vệ Đông, Miêu Hoa và nhiều tướng cấp cao bị khai trừ. Nhưng thanh lọc đọc được hai chiều: vừa là trung tâm kiểm soát mạnh lên, vừa có thể là mạng quan hệ bị phá và lòng tin nội bộ giảm. CHƯA chứng minh được chuỗi mệnh lệnh bị chia.'}
  ]},
  {muc:3, t:'TIỀN · CÔNG NGHỆ · VÀ QUYỀN SỬA CHÍNH BO MẠCH', acc:'#a371f7', ds:[
    {ten:'Lý Cường · Hà Lập Phong', o:'Uỷ ban Tài chính Trung ương (lập 2023)',
     ghi:'Văn kiện nói thẳng mục tiêu: tăng cường sự lãnh đạo tập trung thống nhất của Trung ương Đảng đối với công tác tài chính. Bên nhà nước vẫn có PBOC, NFRA, CSRC — nhưng tầng chiến lược nằm trên, cộng thêm Uỷ ban Công tác Tài chính Trung ương lo phần công tác đảng. KHÔNG có nghĩa Tập duyệt từng khoản vay: trung ương nắm hướng tín dụng, rủi ro hệ thống, ưu tiên chiến lược và nhân sự cao cấp.'},
    {ten:'Đinh Tiết Tường', o:'Uỷ ban Khoa học Công nghệ Trung ương (lập 2023)',
     ghi:'AI, bán dẫn, vũ trụ, lượng tử, sinh học, phòng thí nghiệm quốc gia, phối hợp quân–dân. Mô hình gọi là "whole-of-nation": chiến lược → đại học + phòng thí nghiệm + doanh nghiệp (Huawei, SMIC, CATL và các national champions) → quỹ nhà nước → công nghiệp. Nhưng đó KHÁC với nói "Huawei là bộ phận bí mật của ĐCSTQ". Khoa học không còn là một bộ chuyên môn mà được đặt vào giao điểm an ninh + công nghiệp + cạnh tranh Mỹ–Trung + quân sự.'},
    {ten:'Trình Phúc Ba', o:'SASAC — doanh nghiệp nhà nước trung ương',
     ghi:'Nơi tài sản nhà nước, doanh nghiệp và Đảng giao nhau. Cộng ngân hàng quốc doanh, quỹ chính phủ và chính quyền địa phương, đây là năng lực tập trung vốn mà một nền kinh tế hoàn toàn phi tập trung khó bắt chước.'},
    {ten:'Doanh nghiệp tư nhân', o:'bốn ổ cắm, không phải một',
     ghi:'Đây là chỗ dễ hiểu sai nhất khi nhìn Huawei, Alibaba, Tencent hay ByteDance. Bốn ổ cắm: sở hữu · quản trị · tổ chức đảng · và THỊ TRƯỜNG NHÀ NƯỚC (mua sắm công, tín dụng, đất, giấy phép, trợ cấp). Quy định tổ chức cơ sở: doanh nghiệp tư nhân có từ BA đảng viên chính thức trở lên thì nên lập tổ chức đảng riêng; toàn quốc ~1,692 triệu chi bộ trong doanh nghiệp và ~201.000 trong các tổ chức xã hội. Nghiên cứu 2026: trong 33 văn kiện trung ương về xây dựng đảng ở "tổ chức mới", 21 văn kiện ra đời SAU khi Tập nắm quyền. Nhưng vai trò chi bộ khác nhau rất lớn giữa các công ty — có chỗ gần như nghi lễ, có chỗ tham gia quyết định quan trọng. Bằng chứng KHÔNG cho phép kết luận "mọi CEO Trung Quốc chỉ là bù nhìn".'},
    {ten:'Uỷ ban Biên chế Cơ cấu Trung ương', o:'META — quyền sửa chính bo mạch',
     ghi:'Không chỉ điều khiển cơ quan, mà TẠO · XOÁ · GỘP cơ quan, chuyển chức năng, đổi biên chế. Cải cách 2023 chính là ví dụ. Nói cách khác: CPU có quyền thiết kế lại mainboard — đây là thứ phân biệt hệ thống này với một chính phủ thông thường.'}
  ]},
  {muc:4, t:'NỐI RA NGOÀI VÀ XUỐNG DƯỚI — chỗ chạm Hong Kong và Việt Nam', acc:'#58a6ff', ds:[
    {ten:'Lý Cán Kiệt', o:'Ban Công tác Mặt trận Thống nhất',
     ghi:'ĐÁNG SOI NHẤT SAU HỒ SƠ ĐẦU TIÊN. Ổ cắm nối thẳng sang hồ sơ Hướng Hoa Cường, và là cơ chế "HẤP THỤ" thay vì "tiêu diệt" — thứ dễ bị đọc sai nhất từ bên ngoài. Đối tượng: các đảng nhỏ, người không đảng phái, trí thức, dân tộc, tôn giáo, doanh nhân tư nhân, "giai tầng xã hội mới", Hong Kong, Macau, Đài Loan, Hoa kiều và cộng đồng hải ngoại.'},
    {ten:'Hạ Bảo Long', o:'Văn phòng Hong Kong–Macau Trung ương',
     ghi:'Một cơ quan hai danh nghĩa: mặt Đảng và mặt Quốc vụ viện. Ví dụ rõ nhất của cấu trúc party-state. Hong Kong vẫn có hệ pháp luật và hành chính riêng dưới "một quốc gia, hai chế độ", nhưng tầng chính sách trung ương nằm dưới cấu trúc Đảng.'},
    {ten:'Tống Đào', o:'Văn phòng Đài Loan Trung ương + Quốc vụ viện',
     ghi:'Lại là một cơ quan hai danh nghĩa. Nhiệm vụ: quan hệ hai bờ, giao lưu, kinh tế, chính trị, chống Đài Loan độc lập, thúc đẩy thống nhất. Nhưng ĐCSTQ giao lưu với KMT ≠ KMT nằm dưới ĐCSTQ — đúng nguyên tắc đã dùng với nhà Hướng.'},
    {ten:'Vương Nghị · Lưu Hải Tinh', o:'ngoại giao SONG SONG',
     ghi:'Một nước bình thường chủ yếu có Bộ Ngoại giao. Trung Quốc chạy ba mạng: ngoại giao nhà nước (MFA — Vương Nghị, đồng thời đứng đầu Văn phòng Uỷ ban Đối ngoại Trung ương), ngoại giao ĐẢNG (Ban Liên lạc Đối ngoại Trung ương — Lưu Hải Tinh, quan hệ thẳng với đảng cầm quyền, đảng đối lập và phong trào chính trị nước ngoài), và thống chiến với cộng đồng hải ngoại. Ba mạng phối hợp được nhưng không phải một cơ quan.'},
    {ten:'Ngô Hán Thánh', o:'Ban Công tác Xã hội Trung ương (lập 2023) · đoàn thể · lưới',
     ghi:'Thứ Cửu Bình 2004 hoàn toàn chưa thể thấy. Kinh tế đã đổi: shipper (Meituan), tài xế (Didi), người bán trên nền tảng, freelancer KHÔNG nằm trong đơn vị công tác truyền thống — nên Đảng xây ổ cắm mới để nối tới họ. Cộng TRƯỜNG HỌC — mô hình chính thức là "hiệu trưởng phụ trách dưới sự lãnh đạo của Đảng uỷ", cho Đảng một ổ cắm cực dài hạn: trẻ em → trường → Đội → Đoàn → Đảng → cán bộ. Cộng Đoàn Thanh niên (điều lệ ghi là trợ thủ và lực lượng dự bị của Đảng), Công đoàn ACFTU, Hội Phụ nữ ACWF, lưới quản trị cộng đồng, và cả công tác tiếp nhận thư từ khiếu nại (xinfang). Đừng biến mọi lưới thành "mạng mật vụ": phần lớn chức năng rất đời thường — rác, người già, tranh chấp, an sinh. Nhưng cùng mạng đó làm tăng khả năng nhận biết xã hội ở cấp rất nhỏ.'}
  ]}
];

window.DQT_TQ_SOI = { SOI: SOI, DANHSACH: DANHSACH };
})();
