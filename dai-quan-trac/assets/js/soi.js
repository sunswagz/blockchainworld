(function () {
"use strict";

/* ============================================================
   SOI QUYỀN LỰC — khung điều tra + hồ sơ từng đối tượng

   Tách khỏi data.js vì hai lý do, lý do thứ hai mới là chính:

   1. data.js đã 73 KB và hồ sơ sẽ còn dài thêm mỗi lần soi.
   2. data.js mô tả CÚ SỐC TỪ NGOÀI VÀO. File này mô tả BỘ MÁY
      BÊN TRONG. Hai trục khác nhau thì để hai file, không thì
      lần tách sau phải gỡ rối.

   ── CẤU TRÚC MỘT HỒ SƠ ──────────────────────────────────────
   Phần LUÔN HIỆN, vì nó là kết luận:
     gt    hai giả thuyết đối lập
     diem  chấm trên 7 tiêu chí

   Phần THU GỌN ĐƯỢC, vì nó là chứng cứ:
     muc[] các mục, mỗi mục một chủ đề, mở/đóng độc lập

   Mỗi mục chứa các KHỐI có kiểu. Thêm kiểu mới thì thêm một
   nhánh trong veKhoi() của app.js, không sửa gì ở đây:

     {k:'p',   d}          đoạn văn (cho phép HTML)
     {k:'q',   d, do}      trích dẫn nổi bật; do:1 = viền đỏ
     {k:'a',   d}          sơ đồ ASCII
     {k:'the', ds:[{t,d,vd,acc}]}   thẻ xếp lưới
     {k:'moc', ds:[{y,t,d,hot}]}    mốc thời gian
     {k:'so',  ds:[{t,v,d,acc}]}    ô số liệu
     {k:'sd',  ds:[{sai,dung}]}     nói sai / nói đúng
     {k:'ds',  ds:['...']}          danh sách đánh số
     {k:'oc',  ds:['...']}          chip ổ cắm

   ── VÌ SAO PHẢI THU GỌN ĐƯỢC ────────────────────────────────
   Một hồ sơ đầy đủ dài hơn màn hình rất nhiều. Đổ hết ra một
   mạch thì phần quan trọng nhất — bảng chấm — bị đẩy lên trên
   rồi trôi mất, và người đọc không biết mình đang ở đâu trong
   lập luận. Chia mục thì mỗi mục trả lời đúng một câu hỏi, và
   mở cái nào là chọn đọc câu hỏi đó.
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

/* Bảy tiêu chí — phần KHÔNG đổi khi sang đối tượng khác. */
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

/* ============================================================
   HỒ SƠ
   ============================================================ */
const SOI = [

/* ══════════════════ VINGROUP ══════════════════ */
{
  id:'vingroup', ten:'Vingroup', nguoi:'Phạm Nhật Vượng', ic:'star', acc:'#d29922',
  vai:'Tập đoàn tư nhân · đối tác chiến lược hạ tầng quốc gia',
  lede:'Câu hỏi thường gặp là "Vingroup có phải chân sau của Nhà nước không". Đó là câu hỏi sai — nó chỉ có hai đáp án và cả hai đều dẫn tới chỗ cụt. Câu hỏi soi được là: <b>quyền lực thật sự chảy qua những ổ cắm nào</b>, và ở mỗi ổ cắm đó bằng chứng mạnh tới đâu.',

  gt:[
    {k:'A', t:'Vingroup là doanh nghiệp Nhà nước trá hình',
     kl:'KHÔNG ĐỨNG VỮNG', acc:'#4b5563',
     d:'Ba tiêu chí xương sống — sở hữu, HĐQT, gánh lỗ — đều trống. Mạng sở hữu chỉ về một tâm rất rõ là ông Vượng và các pháp nhân liên quan, không về phía Nhà nước.'},
    {k:'B', t:'Doanh nghiệp tư nhân được dựng thành đầu tàu quốc gia',
     kl:'RẤT PHÙ HỢP', acc:'#f0503f',
     d:'Bốn tiêu chí còn lại — vốn, dự án, phối hợp, mạng quy mô — đều mạnh hoặc rất mạnh. Nhà nước không cần sở hữu; nó nắm các ổ cắm mà doanh nghiệp buộc phải cắm vào.'}
  ],

  diem:{
    sohuu:{m:'khong', d:'Hồ sơ ứng viên HĐQT 2026: ông Vượng nắm trực tiếp <b>9,10%</b> Vingroup và <b>94,8%</b> Công ty CP Tập đoàn Đầu tư Việt Nam — pháp nhân đang là cổ đông lớn nhất với khoảng <b>32,59%</b>. VinSpeed cũng thành cổ đông lớn với <b>10,787%</b>. Mọi nhánh quy về một tâm, và tâm đó là cá nhân chứ không phải cơ quan Nhà nước.'},
    hdqt:{m:'khong', d:'ĐHĐCĐ tháng 4/2026 bầu HĐQT nhiệm kỳ 2026–2031, ông Vượng tiếp tục làm Chủ tịch. Đường quyền lực đọc được trong hồ sơ là cổ đông → ĐHĐCĐ → HĐQT. Không thấy cơ quan Nhà nước nào có quyền bổ nhiệm ghế nào.'},
    von:{m:'manh', d:'Reuters 12/8/2026: một số dự án hạ tầng lớn, <b>trong đó có tuyến đường sắt do Vingroup phát triển, được miễn khỏi giới hạn tăng trưởng tín dụng thông thường</b>. Phải đọc chính xác: đây là ưu tiên <b>theo dự án</b> và mở cho nhiều tập đoàn lớn, không phải giấy phép vay vô hạn cấp riêng cho một cái tên. Nhưng nó chứng minh Nhà nước vặn được núm tín dụng.'},
    duan:{m:'ratmanh', d:'Đường sắt Hà Nội–Quảng Ninh ~<b>5,8 tỷ USD</b> theo PPP, riêng ~10,27 nghìn tỷ giải phóng mặt bằng do Nhà nước chi. Hà Nội giao liên danh Vinhomes–VinSpeed làm tổng thầu EPC <b>cả 5 tuyến metro</b>, sơ bộ hơn <b>49 tỷ USD</b>. Khu đô thị thể thao Olympic hơn <b>9.000 ha</b>. Cần Giờ <b>2.870 ha</b>, gần 9 tỷ USD.'},
    chidao:{m:'vua', d:'Reuters 11/2025 dẫn ba người được thông báo về các trao đổi nội bộ, nói quan chức đã <b>khuyến khích</b> Vingroup tham gia đề xuất đường sắt Bắc–Nam. Nguồn ẩn danh; Vingroup nói không thảo luận về đối xử đặc quyền. Nên đây là <b>phối hợp</b>, chưa phải <b>chỉ huy</b>.'},
    lailo:{m:'khong', d:'VinFast lỗ nhiều năm, nhưng dòng đỡ công khai đến từ chính ông Vượng và Vingroup — Reuters theo dõi khoảng <b>13,5 tỷ USD</b> vốn và khoản vay, sau đó cam kết thêm gần 3,5 tỷ. Không tìm thấy bằng chứng công khai về ngân sách Nhà nước rót vào hay bảo lãnh nợ.'},
    mang:{m:'khong', d:'Mạng pháp nhân quanh Vingroup ngày càng dày — Đầu tư Việt Nam, VinSpeed, VinEnergo, GSM, VinSpace — và Reuters 5/2026 đã nêu quan ngại minh bạch quanh kế hoạch chuyển gần <b>7 tỷ USD nợ</b> cùng nhà máy ra ngoài VinFast. Đáng theo dõi về quản trị. Nhưng mạng đó <b>quy về ông Vượng</b>, không quy về Nhà nước.'}
  },

  muc:[
    {id:'phanchung', t:'Ba mảnh phản chứng', ic:'gauge', mo:true, khoi:[
      {k:'p', d:'Phần dễ bị bỏ qua nhất, và là phần làm kết luận đáng tin: nếu giả thuyết A đúng thì <b>không thể có</b> những chuyện dưới đây.'},
      {k:'the', ds:[
        {t:'Chính bộ máy Nhà nước phản biện', acc:'#2ea043',
         d:'VinSpeed đề xuất làm đường sắt Bắc–Nam với 20% vốn tự có và 80% vay Nhà nước lãi 0%. NHNN cảnh báo Vingroup đòn bẩy cao và ít kinh nghiệm đường sắt; Bộ Tài chính nói khoản vay 0% thực chất là một <b>trợ cấp</b> và có thể ảnh hưởng xếp hạng tín nhiệm quốc gia.'},
        {t:'Đề xuất bị rút', acc:'#2ea043',
         d:'Cuối tháng 12/2025 Vingroup rút đề xuất Bắc–Nam. Nếu là cánh tay Nhà nước thì kịch bản phải là đề xuất → duyệt, chứ không phải đề xuất → bị cảnh báo → rút.'},
        {t:'Tiền vay không rẻ', acc:'#2ea043',
         d:'Coupon trái phiếu Vingroup theo Reuters: khoảng 9,6% (2022), 10,6% (2023), tới 12,5% ở đợt được theo dõi năm 2024. Nợ Vinhomes từng bị xếp mức đầu cơ. Vay được nhiều không đồng nghĩa vay được rẻ.'}
      ]}
    ]},

    {id:'tang', t:'Bốn tầng doanh nghiệp — chỗ hay bị gộp một rổ', ic:'stairs', khoi:[
      {k:'p', d:'Xếp năm tập đoàn cạnh nhau theo <b>quy mô</b> là so sánh đúng. Xếp cạnh nhau rồi kết luận <b>cùng một loại về cấu trúc sở hữu</b> là sai. Đây là bốn tầng hoàn toàn khác nhau.'},
      {k:'the', ds:[
        {t:'Tầng 1 · DNNN trực tiếp', vd:'EVN · Petrovietnam · Viettel', acc:'#f0503f',
         d:'Nhà nước sở hữu và kiểm soát trực tiếp.'},
        {t:'Tầng 2 · Niêm yết, Nhà nước chi phối', vd:'Petrolimex', acc:'#d29922',
         d:'Có cổ đông ngoài, nhưng Nhà nước nắm trên 50%.'},
        {t:'Tầng 3 · Đầu tàu tư nhân', vd:'Vingroup · THACO', acc:'#58a6ff',
         d:'Không phải DNNN theo hồ sơ, nhưng hoạt động trong đất, hạ tầng, năng lượng, đường sắt — toàn ngành cần Nhà nước ở mức rất cao.'},
        {t:'Tầng 4 · FDI', vd:'Samsung · LG', acc:'#a371f7',
         d:'Vốn ngoài, chịu chính sách nhưng không thuộc hệ thống sở hữu trong nước.'}
      ]},
      {k:'a', d:'  EVN / PVN / Viettel  → tầng 1\n  Petrolimex          → tầng 2\n  Vingroup / THACO    → tầng 3\n  Samsung / LG        → tầng 4\n\nCùng bảng xếp hạng quy mô.\nKHÔNG cùng cấu trúc sở hữu.'}
    ]},

    {id:'socket', t:'Ổ cắm — quyền lực không nằm ở cổ phần', ic:'chain', khoi:[
      {k:'p', d:'Đây là điểm dễ bỏ lỡ nhất. Nhà nước không cần nắm 51% một công ty nếu nó nắm những thứ mà công ty đó buộc phải xin. Sở hữu là <b>một</b> ổ cắm, và không phải ổ mạnh nhất.'},
      {k:'oc', ds:['Quy hoạch','Đất','Giấy phép','Hạ tầng kết nối','Tiêu chuẩn ngành','Đấu thầu / giao dự án','Hạn mức tín dụng','Đầu tư công']},
      {k:'a', d:'          NHÀ NƯỚC\n              │\n   ┌──────────┼──────────┐\n QUY HOẠCH   ĐẤT    TÍN DỤNG\n   └──────────┼──────────┘\n              │\n      ĐẦU TÀU TƯ NHÂN\n              │\n        DỰ ÁN KHỔNG LỒ\n              │\n          NGÂN HÀNG\n              │\n   ┌──────────┴──────────┐\nTIỀN GỬI DÂN      VỐN QUỐC TẾ'},
      {k:'q', d:'Nếu một Nhà nước kiểm soát các nút đó thì <b>không cần sở hữu 51% một công ty vẫn có khả năng ảnh hưởng rất lớn đến hướng công ty đi</b>. Nhưng "ảnh hưởng rất lớn" vẫn chưa bằng "điều khiển bí mật".'}
    ]},

    {id:'hesinhthai', t:'Hệ sinh thái Vin — nó nối được bao nhiêu dòng cùng lúc', ic:'flow', khoi:[
      {k:'p', d:'Đây là lý do Vingroup đáng nghiên cứu hơn một nhà phát triển bất động sản thông thường: nó chạm nhiều dòng chảy khác nhau <b>cùng một lúc</b>, và mỗi dòng lại cần Nhà nước ở mức rất cao.'},
      {k:'a', d:'                    VINGROUP\n                       │\n      ┌────────────────┼─────────────────┐\n  VINHOMES          VINFAST         VINSPEED\n      │                │                │\n     ĐẤT            XE ĐIỆN         ĐƯỜNG SẮT\n      │                │                │\n      └────────────────┼────────────────┘\n                       │\n                   HẠ TẦNG\n                       │\n           ┌───────────┼───────────┐\n         CẢNG      LOGISTICS   NĂNG LƯỢNG\n                                   │\n                               VINENERGO'},
      {k:'q', d:'Đây không còn là một developer bất động sản. Nó bắt đầu giống một <b>private infrastructure conglomerate</b> — tập đoàn hạ tầng tư nhân đa ngành.'}
    ]},

    {id:'dongtien', t:'Truy dòng tiền — chuyện "mì gói" không khớp mốc', ic:'src', khoi:[
      {k:'p', d:'Cách kể phổ biến là bán Technocom cho Nestlé rồi mang tiền về dựng Vingroup. Mốc thời gian không cho phép đọc như vậy.'},
      {k:'moc', ds:[
        {y:'1993', t:'Technocom / Mivina, Kharkiv', d:'Khởi nghiệp bằng vốn vay nhỏ. Đến 2010 có 2 nhà máy, 1.900 nhân viên, xuất sang 20 nước, quy mô ~100 triệu USD/năm.'},
        {y:'2002', t:'Vincom lập, vốn 196 tỷ', d:'Nhóm sáng lập Technocom xuất hiện thẳng trong danh sách cổ đông Vincom, một người có địa chỉ tại Kharkiv.', hot:1},
        {y:'2006–07', t:'Vốn 313,5 → 600 → 800 tỷ · niêm yết', d:'Tăng vốn bằng lợi nhuận chưa phân phối. Rồi 1.000 tỷ trái phiếu (2007), thêm 2.000 tỷ (2008).'},
        {y:'2009', t:'100 triệu USD trái phiếu quốc tế', d:'Không có tài sản bảo đảm, niêm yết tại Singapore, Credit Suisse bảo lãnh. Đã huy động được vốn quốc tế mà chưa cần bán Technocom.', hot:1},
        {y:'2010', t:'Nestlé mua Technocom', d:'Nestlé <b>không công bố giá</b>. Con số 150 triệu USD lặp trên báo chí nhưng chưa thấy Nestlé xác nhận.'},
        {y:'2013', t:'Warburg Pincus 200 triệu USD', d:'Vào Vincom Retail, ~20% cổ phần, định giá nền tảng ~1,1 tỷ USD, có đại diện trong HĐQT.'},
        {y:'2018', t:'GIC ~853 triệu USD', d:'Trước IPO Vinhomes. Đợt chào bán sau đó lên tới ~1,4 tỷ USD, chủ yếu là cổ phần thứ cấp.'},
        {y:'2019', t:'SK Group 1 tỷ USD', d:'Mua 6,1% Vingroup.'},
        {y:'2026', t:'~1,309 triệu tỷ tài sản · ~356 nghìn tỷ nợ vay', d:'Lãi vay bình quân ~10,9%, kỳ hạn ~3,2 năm. Không phải một khoản vay — hàng trăm khoản, xoay vòng liên tục.'}
      ]},
      {k:'q', d:'Vincom đã lớn và đã chạm được thị trường vốn quốc tế <b>trước</b> thương vụ Nestlé. Nên tiền bán Technocom có thể thêm thanh khoản, nhưng không thể là nguồn gốc duy nhất của đế chế.'},
      {k:'p', d:'Và từ đây cỗ máy đổi bản chất: từ <b>kiếm tiền kinh doanh</b> sang <b>huy động vốn</b>. Khi doanh nghiệp đủ lớn thì tài sản → uy tín → dự án → thị trường vốn, và ông chủ không cần có sẵn toàn bộ tiền mặt để xây dự án mới.'}
    ]},

    {id:'nganhang', t:'Ngân hàng — nút tuần hoàn vốn, và Techcombank', ic:'gauge', khoi:[
      {k:'p', d:'Đây là chỗ dễ nói sai nhất trong toàn bộ hồ sơ, nên tách riêng ra.'},
      {k:'sd', ds:[
        {sai:'Techcombank là ngân hàng Nhà nước.',
         dung:'Techcombank là <b>ngân hàng thương mại cổ phần tư nhân</b>, tự gọi mình là ngân hàng khu vực tư nhân lớn nhất, thành lập 1993 với vốn điều lệ ban đầu chỉ 20 tỷ đồng.'},
        {sai:'Ông chủ ngân hàng lấy tiền túi cho Vingroup vay.',
         dung:'Ngân hàng là một <b>hồ chứa</b>. 30/6/2026 Techcombank có ~662 nghìn tỷ tiền gửi khách hàng, ~164 nghìn tỷ vay tổ chức khác, ~212 nghìn tỷ giấy tờ có giá, ~189 nghìn tỷ vốn chủ — cộng thành bảng cân đối ~1,27 triệu tỷ.'},
        {sai:'Dân gửi 662 nghìn tỷ mà ngân hàng cho vay 847 nghìn tỷ, vậy là in tiền.',
         dung:'Phần chênh đến từ vay tổ chức khác, phát hành giấy tờ có giá và vốn cổ đông. Ngân hàng <b>không</b> chuyển 1:1 tiền gửi sang người vay — nhưng cũng không tạo tín dụng vô hạn: vẫn bị chặn bởi hệ số an toàn vốn, thanh khoản, tỷ lệ cho vay trên huy động và quy định NHNN.'}
      ]},
      {k:'p', d:'Điểm đáng nghiên cứu thật sự nằm ở <b>mạch lịch sử</b>: Techcombank – Masan – nhóm doanh nhân trở về từ Đông Âu là một mạng có thật. Ông Hồ Hùng Anh học ở Liên Xô, vào HĐQT 2004, làm Chủ tịch từ 2008; ông Nguyễn Đăng Quang tham gia quản trị từ 1995 và nay là Phó Chủ tịch thứ nhất. HSBC từng là cổ đông chiến lược, nâng sở hữu lên 20% năm 2008.'},
      {k:'q', d:'Nhưng giao nhau về địa lý và quan hệ <b>không</b> chứng minh cùng một chủ sở hữu. Đây là đường đáng đào, không phải kết luận đã có.'}
    ]},

    {id:'doc', t:'Đọc cho đúng', ic:'brain', khoi:[
      {k:'sd', ds:[
        {sai:'Nhà nước lấy tiền gửi của dân đưa thẳng cho Vingroup.',
         dung:'Ngân hàng là đường ống gom tiết kiệm trong nước và vốn nước ngoài. Nhà nước điều tiết <b>quy tắc</b> tín dụng để ưu tiên dự án chiến lược. Đó là hai chuyện khác nhau.'},
        {sai:'Gắn rất chặt với Nhà nước nghĩa là Nhà nước sở hữu ngầm.',
         dung:'Hai chuyện phải giữ riêng. <b>Phụ thuộc chính sách, liên minh lợi ích, hợp tác chiến lược, quyền chi phối và quyền sở hữu</b> là năm thứ khác nhau, rất dễ bị trộn.'},
        {sai:'Ảnh của mạng xã hội xếp 5 tập đoàn cạnh nhau, vậy chúng cùng một loại.',
         dung:'Đó là infographic xếp theo quy mô, không phải bằng chứng về quan hệ sở hữu. Về cấu trúc sở hữu thì năm cái đó thuộc bốn tầng khác nhau.'}
      ]}
    ]},

    {id:'ruiro', t:'Mặt nguy hiểm của mô hình', ic:'fire', khoi:[
      {k:'p', d:'Nếu quan hệ Nhà nước – tập đoàn quá chặt mà thiếu minh bạch, rủi ro không nằm ở chỗ ai sở hữu, mà ở chỗ <b>ai gánh lỗ</b>.'},
      {k:'a', d:'quy hoạch / đất / dự án\n        ↓\n  một số tập đoàn\n        ↓\n quy mô ngày càng lớn\n        ↓\n tín dụng ngày càng lớn\n        ↓\n  "TOO BIG TO FAIL"\n        ↓\nLÃI  → tư nhân hưởng\nLỖ   → hệ thống không dám để sập'},
      {k:'p', d:'Và ở tầng đất đai, hai kết quả rất khác nhau lại nhìn giống hệt nhau từ bên ngoài: <b>land-value capture</b> — hạ tầng làm đất tăng giá, phần tăng đó tài trợ ngược cho hạ tầng — là mô hình hiệu quả; còn nếu thiếu cạnh tranh và minh bạch thì cùng một chuỗi việc đó trở thành lợi ích nhóm.'},
      {k:'a', d:'quy hoạch\n   ↓\nmột nhóm biết trước / được tiếp cận trước\n   ↓\nđất rẻ\n   ↓\nhạ tầng được quyết định\n   ↓\ngiá đất tăng khổng lồ'},
      {k:'q', do:1, d:'Phân biệt được hai cái đó cần đúng thứ đang thiếu: <b>hồ sơ đấu thầu, giá đất, và thời điểm ai biết quy hoạch trước</b>.'}
    ]},

    {id:'gap', t:'Sáu khoảng trống chưa giải được', ic:'src', khoi:[
      {k:'p', d:'Ghi ra để lần điều tra sau biết bắt đầu từ đâu, và để người đọc biết chỗ nào là chứng cứ, chỗ nào là chưa biết.'},
      {k:'ds', ds:[
        '196 tỷ vốn Vincom năm 2002 cụ thể đến từ tài khoản nào, ai góp bao nhiêu.',
        'Technocom trước 2010: ai sở hữu bao nhiêu phần trăm.',
        'Nestlé trả bao nhiêu, và chia cho những chủ sở hữu nào.',
        'Dòng vốn Ukraine → Việt Nam giai đoạn 2000–2010 đi qua cấu trúc pháp nhân nào.',
        'Các dự án Vincom/Vinpearl đầu tiên: đất được tiếp cận theo cơ chế nào, ngân hàng nào cấp khoản vay đầu, tài sản nào được thế chấp.',
        'Hiện nay: từng ngân hàng cho hệ Vingroup vay bao nhiêu, tài sản bảo đảm gì, đáo hạn năm nào, bảo lãnh chéo ra sao.'
      ]},
      {k:'q', d:'Hai khoảng trống đầu và thứ tư mới là chỗ đáng đào nhất. Muốn kiểm giả thuyết "ban đầu được một nguồn lực khác nâng lên" thì đừng nhìn VinFast năm 2026 — phải quay về <b>1999–2007</b>.'}
    ]}
  ],

  noi:['tindung','bds','laisuat']
},

/* ══════════════════ THACO ══════════════════ */
{
  id:'thaco', ten:'THACO', nguoi:'Trần Bá Dương', ic:'factory', acc:'#58a6ff',
  vai:'Tập đoàn tư nhân đa ngành · lõi công nghiệp cơ khí',
  lede:'Vingroup đi từ <b>đất → vốn → công nghiệp</b>. THACO đi ngược lại: <b>cơ khí → ô tô → công nghiệp → logistics → rồi mới tới đất và hạ tầng</b>. Hai đường xuất phát trái ngược nhau — nên nếu bảng chấm bảy tiêu chí vẫn ra cùng một hình dạng, thì thứ ta đang nhìn không phải đặc điểm của một doanh nghiệp, mà là <b>đặc điểm của mô hình</b>.',

  gt:[
    {k:'A', t:'THACO là doanh nghiệp Nhà nước trá hình',
     kl:'KHÔNG ĐỨNG VỮNG', acc:'#4b5563',
     d:'Sở hữu quy về ông Trần Bá Dương và nhóm liên quan, cộng một cổ đông ngoại lớn. HĐQT không có ghế nào do cơ quan Nhà nước chỉ định. Và tổ chức xếp hạng tín nhiệm nói thẳng là họ <b>không tính</b> bất kỳ hỗ trợ Nhà nước nào vào xếp hạng.'},
    {k:'B', t:'Doanh nghiệp tư nhân được dựng thành đầu tàu quốc gia',
     kl:'RẤT PHÙ HỢP', acc:'#f0503f',
     d:'Giao diện với Nhà nước ở tầng đất và dự án thì rất lớn: khu kinh tế Chu Lai, hợp đồng BT đổi hạ tầng lấy đất ở Thủ Thiêm, chuỗi khu công nghiệp, cảng, và nay là đường sắt. Cùng hình dạng với Vingroup dù xuất phát ngược chiều.'}
  ],

  diem:{
    sohuu:{m:'khong', d:'Ông Trần Bá Dương và gia đình là tâm sở hữu. Cổ đông chiến lược <b>Jardine Cycle &amp; Carriage nắm 26,7%</b> tính đến cuối 2025 — một tập đoàn niêm yết ở Singapore, tức vốn tư nhân quốc tế chứ không phải pháp nhân trung gian trong nước. Không tìm thấy mắt xích Nhà nước → người đứng tên → cổ đông lớn.'},
    hdqt:{m:'khong', d:'Ông Dương làm Chủ tịch; đại diện Jardine, ông Cheah Kim Teck, làm <b>Phó Chủ tịch</b>. Đây còn là điểm khác Vingroup: có một <b>đối trọng cổ đông tổ chức nước ngoài</b> ngồi trong HĐQT. Không thấy cơ chế Nhà nước bổ nhiệm ghế nào.'},
    von:{m:'manh', d:'Vốn đến từ kinh doanh, ngân hàng, trái phiếu, Jardine và cả tín dụng xuất khẩu quốc tế. Nhà nước Việt Nam không cấp tiền, nhưng với dự án hạ tầng chiến lược thì <b>cơ chế PPP, quy hoạch và giải phóng mặt bằng quyết định dự án đó có huy động được vốn hay không</b>.'},
    duan:{m:'ratmanh', d:'Chu Lai, Thủ Thiêm theo hợp đồng BT, chuỗi KCN, cảng, và ~86.000 ha đất nông nghiệp. Xem mục "Sổ đất" bên dưới.'},
    chidao:{m:'vua', d:'Chính phủ công khai đề nghị THACO nghiên cứu và tham gia sản xuất toa tàu, đường sắt đô thị và công nghiệp đường sắt. Nhưng <b>"hãy nghiên cứu, hãy tham gia" khác hẳn "phải làm vì Nhà nước ra lệnh"</b> — chưa thấy tài liệu dạng thứ hai.'},
    lailo:{m:'khong', d:'Không tìm thấy giải cứu bằng ngân sách. Ngược lại, chính THACO bỏ hơn <b>10.500 tỷ</b> ứng ra tái cấu trúc HAGL Agrico — tập đoàn tư nhân này đang là bên đi cứu, không phải bên được cứu.'},
    mang:{m:'khong', d:'Mạng nội bộ giữa sáu khối <b>rất dày và rất đáng soi</b> — xem mục "Thác vốn nội bộ". Nhưng nó là mạng <b>tư nhân</b>, quy về founder và Jardine, không quy về Nhà nước.'}
  },

  muc:[
    {id:'phanchung', t:'Ba mảnh phản chứng', ic:'gauge', mo:true, khoi:[
      {k:'p', d:'Ở hồ sơ này phản chứng còn mạnh hơn Vingroup, vì có một bên thứ ba chuyên nghiệp đã phải trả lời đúng câu hỏi đó bằng tiền của chính họ.'},
      {k:'the', ds:[
        {t:'Tổ chức xếp hạng nói thẳng: không tính hỗ trợ Nhà nước', acc:'#2ea043',
         d:'VIS Rating đánh giá giả định hỗ trợ Chính phủ ở mức <b>LOW</b> và tuyên bố không đưa bất kỳ hỗ trợ nào của Chính phủ hay bên liên quan vào xếp hạng THACO. Nếu tồn tại bảo lãnh ngầm cho mọi khoản nợ thì đây là chỗ nó phải hiện ra, vì nó thay đổi hẳn rủi ro tín dụng.'},
        {t:'Chi phí tài chính lớn hơn lợi nhuận', acc:'#2ea043',
         d:'Năm 2025: doanh thu ~3,115 tỷ USD, lợi nhuận sau thuế ~251 triệu USD, còn <b>chi phí tài chính ~260 triệu USD</b>. Một doanh nghiệp được bơm vốn giá rẻ thì bảng này không trông như vậy.'},
        {t:'Có đối trọng cổ đông ngoại trong HĐQT', acc:'#2ea043',
         d:'Jardine nắm 26,7% và người của họ giữ ghế Phó Chủ tịch. Chaebol cổ điển là hệ đóng quanh gia đình; ở đây có một cổ đông tổ chức nước ngoài đủ lớn để không thể bỏ qua.'}
      ]}
    ]},

    {id:'khoi', t:'Sáu khối ngành — một nền kinh tế thu nhỏ', ic:'factory', khoi:[
      {k:'p', d:'THACO không còn là hãng ô tô. Sáu khối được thiết kế theo hướng <b>bổ trợ và tích hợp với nhau</b> — đó là chữ chính cổ đông ngoại dùng khi mô tả tập đoàn.'},
      {k:'the', ds:[
        {t:'THACO AUTO', vd:'ô tô · đại lý · lắp ráp', acc:'#58a6ff',
         d:'Hơn 440 điểm bán và đại lý. Lắp ráp cho Kia, Mazda, Peugeot và sản xuất nội địa hoá. Đây là cỗ máy doanh thu gốc.'},
        {t:'THACO INDUSTRIES', vd:'cơ khí · công nghiệp hỗ trợ', acc:'#a371f7',
         d:'Tổ hợp sản xuất khoảng <b>320 ha</b>. Đây là thứ Vingroup yếu hơn: năng lực chế tạo vật chất thật, không phải chỉ vốn.'},
        {t:'THACO AGRI', vd:'nông nghiệp', acc:'#d29922',
         d:'Khoảng <b>86.000 ha</b> ở Việt Nam, Lào, Campuchia. Ngành hấp thụ vốn lớn nhất và chưa có lãi.'},
        {t:'THADICO', vd:'bất động sản · xây dựng', acc:'#2ea043',
         d:'Sala/Thủ Thiêm. Được kỳ vọng đóng góp 10–15% doanh thu 2025–2027 với biên EBITDA 50–65%.'},
        {t:'THILOGI', vd:'logistics · cảng', acc:'#e5484d',
         d:'Cảng Chu Lai. Nối nông sản và hàng công nghiệp ra xuất khẩu, đồng thời phục vụ nội bộ tập đoàn.'},
        {t:'THISO', vd:'thương mại · dịch vụ · bán lẻ', acc:'#6f7b8a',
         d:'Trung tâm thương mại trên chính quỹ đất do THADICO phát triển.'}
      ]}
    ]},

    {id:'vong', t:'Vòng tuần hoàn nội bộ — vì sao đây mới là chaebol logic', ic:'chain', khoi:[
      {k:'p', d:'Không phải cứ sở hữu nhiều công ty là chaebol. Điểm quan trọng là <b>các công ty bên trong mua, bán, cung cấp hạ tầng và bổ trợ cho nhau, làm tập đoàn ngày càng ít phụ thuộc vào bên ngoài</b>.'},
      {k:'a', d:'THACO AUTO\n    ↓ cần linh kiện\nTHACO INDUSTRIES\n    ↓ cần vận chuyển\nTHILOGI\n    ↓ cần nhà máy / KCN\nTHADICO'},
      {k:'a', d:'THACO AGRI\n    ↓ nông sản\ncchế biến\n    ↓\nTHILOGI\n    ↓\nCẢNG CHU LAI\n    ↓\nXUẤT KHẨU'},
      {k:'a', d:'THADICO\n    ↓ BĐS / đô thị\nTHISO\n    ↓\ntrung tâm thương mại · dịch vụ · bán lẻ'},
      {k:'q', d:'Ô tô → cơ khí → logistics → bất động sản → thương mại → nông nghiệp → logistics → <b>quay lại hệ thống</b>. Mỗi khối vừa là khách hàng vừa là nhà cung cấp của khối khác.'}
    ]},

    {id:'thac', t:'Thác vốn nội bộ — phát hiện lớn nhất', ic:'flow', mo:true, khoi:[
      {k:'p', d:'Trên giấy tờ, sáu khối là sáu pháp nhân riêng. Về tín dụng thì không: chúng cho nhau vay, và <b>phần lớn ngân hàng yêu cầu công ty mẹ bảo lãnh cho khoản vay của công ty con</b>. Nghĩa là THACO vận hành như một bảng cân đối hợp nhất khổng lồ chứ không phải sáu doanh nghiệp tách biệt.'},
      {k:'thac', ds:[
        {n:'A', t:'THACO AUTO', vai:'CỖ MÁY TIỀN MẶT', acc:'#2ea043',
         d:'Ô tô tạo doanh thu và khả năng vay. Giữ hơn <b>75% nợ ngắn hạn</b> của cả tập đoàn — vốn lưu động và hàng tồn kho xe rất lớn — và cho công ty mẹ vay nội bộ khoảng <b>30.000 tỷ</b>.'},
        {n:'B', t:'THACO mẹ', vai:'TRUNG TÂM ĐIỀU PHỐI', acc:'#58a6ff',
         d:'Phân bổ vốn và <b>đứng ra bảo lãnh</b> cho khoản vay của các công ty con. Giữ khoảng 41% nợ dài hạn. Chuyển tiếp khoảng <b>43.000 tỷ</b> xuống nông nghiệp — tương đương ~40% nợ hợp nhất.'},
        {n:'C', t:'THACO AGRI', vai:'NƠI HẤP THỤ VỐN', acc:'#d29922',
         d:'Cho HAGL Agrico vay tiếp hơn <b>9.300 tỷ</b>, phần lớn <b>không có tài sản bảo đảm</b>, lãi 6,5–8,5%. Tỷ lệ lợi nhuận hoạt động trên chi phí lãi chỉ khoảng <b>0,2 lần</b>.'},
        {n:'D', t:'THADICO / SALA', vai:'KỲ VỌNG THU TIỀN VỀ', acc:'#a371f7',
         d:'Giữ khoảng 34% nợ dài hạn. Bất động sản Thủ Thiêm được kỳ vọng đem tiền về cải thiện dòng tiền cho cả hệ, với biên EBITDA 50–65%.'}
      ]},
      {k:'a', d:'  KHÁCH MUA Ô TÔ\n        ↓\n   THACO AUTO ──── ~30.000 tỷ ────┐\n        ↓                          │\n   (>75% nợ ngắn hạn               ↓\n    của cả tập đoàn)         THACO mẹ\n                                   │\n                        bảo lãnh + ~43.000 tỷ\n                                   ↓\n                             THACO AGRI\n                                   │\n                            >9.300 tỷ\n                                   ↓\n                            HAGL AGRICO\n\n   THADICO / SALA ──── bán BĐS ──→ tiền về bảng cân đối'},
      {k:'p', d:'Cần đọc đúng một điều: sơ đồ này <b>không</b> có nghĩa cùng một tờ tiền được chuyển nguyên xi từ khách mua xe sang một trang trại. Đây là dấu vết cấu trúc bảng cân đối và tài trợ nội bộ. Nhưng về <b>kiến trúc vốn</b> thì nó cực kỳ rõ.'},
      {k:'q', d:'Nghịch lý đáng chú ý: THACO sinh ra từ ô tô và cơ khí, nhưng khi đòn bẩy căng lên thì thứ được kỳ vọng cứu dòng tiền lại là <b>bất động sản</b>. Đúng chỗ đó nó bắt đầu giống Vingroup.'},
      {k:'q', do:1, d:'Rủi ro của chính cấu trúc này: nếu ô tô bán chậm, lãi suất tăng, nông nghiệp vẫn cần bơm và bất động sản chưa bán được — <b>cùng lúc</b> — thì áp lực truyền <b>ngược</b> từ Agri lên công ty mẹ rồi lên chính Auto. Đây là lây lan <b>bên trong một tập đoàn</b>, không cần cú sốc nào từ ngoài.'}
    ]},

    {id:'no', t:'Nợ và đòn bẩy — những con số nên nhìn', ic:'gauge', khoi:[
      {k:'p', d:'THACO chưa niêm yết nên không có thuyết minh chi tiết như VIC. Số dưới đây đến từ báo cáo của cổ đông ngoại và tổ chức xếp hạng — tức nhìn qua tay thứ ba, và phải ghi rõ như vậy.'},
      {k:'so', ds:[
        {t:'Tổng tài sản', v:'8,77 tỷ USD', d:'Dài hạn 4,415 + ngắn hạn 4,356 (cuối 2025)'},
        {t:'Nợ tài chính', v:'4,87 tỷ USD', d:'Dài hạn 2,166 + ngắn hạn 2,703', acc:'#d29922'},
        {t:'Vốn ròng cổ đông', v:'2,15 tỷ USD', d:'Nợ tài chính / vốn chủ ≈ 2,27 lần'},
        {t:'Tiền mặt', v:'307 triệu USD', d:'Không nên so thẳng với 4,87 tỷ nợ rồi kết luận mất khả năng trả'},
        {t:'Nợ hợp nhất', v:'~105.000 tỷ', d:'~60% là nợ ngắn hạn, >75% số đó nằm ở AUTO', acc:'#d29922'},
        {t:'Doanh thu 2025', v:'3,12 tỷ USD', d:'Lợi nhuận sau thuế ~251 triệu USD'},
        {t:'Chi phí tài chính', v:'260 triệu USD', d:'LỚN HƠN lợi nhuận sau thuế', acc:'#f0503f'},
        {t:'Debt / EBITDA', v:'4x → 10x', d:'Từ 2021 tới nửa đầu 2025', acc:'#f0503f'},
        {t:'Debt / Equity', v:'97% → 196%', d:'Cùng giai đoạn', acc:'#f0503f'},
        {t:'EBIT / lãi vay', v:'6,7x → 1,9x', d:'Hợp nhất. Riêng AGRI 0,2x · THADICO 1,2x', acc:'#f0503f'},
        {t:'Dòng tiền hoạt động', v:'ÂM 3 kỳ', d:'2023, 2024, nửa đầu 2025', acc:'#f0503f'}
      ]},
      {k:'q', do:1, d:'Đồng hồ đáng nhìn không phải "THACO có bao nhiêu đất" mà là <b>khả năng trả lãi</b>. Một tập đoàn có thể sở hữu rất nhiều tài sản mà vẫn kẹt, nếu dòng tiền nhỏ hơn lãi cộng gốc — lúc đó chỉ còn ba cửa: bán tài sản, vay mới, hoặc tăng vốn.'},
      {k:'p', d:'Nguyên nhân đòn bẩy tăng, theo tổ chức xếp hạng, chủ yếu là tài trợ cho các khoản đầu tư dài hạn mới trong <b>nông nghiệp và bất động sản</b>; dòng tiền âm phần lớn do vốn lưu động cho mở rộng nông nghiệp và việc bán bất động sản bị trì hoãn vì vấn đề pháp lý.'}
    ]},

    {id:'vonquocte', t:'Vốn quốc tế — Jardine, HSBC và một cơ quan Ý', ic:'ship', khoi:[
      {k:'p', d:'Đây là điểm khác Vingroup rõ nhất về nguồn vốn: THACO có một cổ đông tổ chức nước ngoài rất lớn từ sớm, và đã mở được cả đường tín dụng xuất khẩu quốc tế.'},
      {k:'moc', ds:[
        {y:'2008', t:'Jardine Cycle &amp; Carriage vào', d:'Tập đoàn niêm yết Singapore thuộc hệ Jardine. Forbes xem đây là bước ngoặt lớn của THACO.', hot:1},
        {y:'2023', t:'Thêm ~350 triệu USD trái phiếu chuyển đổi', d:'JC&amp;C nói thẳng công cụ này tạo con đường để họ <b>tăng mức sở hữu THACO trong tương lai</b>.'},
        {y:'2025', t:'HSBC 60 triệu USD cho THACO Agri', d:'Kỳ hạn 5 năm, <b>bảo lãnh bởi SACE</b> — cơ quan tín dụng xuất khẩu thuộc Bộ Kinh tế &amp; Tài chính Ý. Nhằm mở rộng nông nghiệp và mua công nghệ, thiết bị.', hot:1},
        {y:'2025', t:'JC&amp;C nắm 26,7%', d:'Đại diện Jardine, ông Cheah Kim Teck, giữ ghế Phó Chủ tịch HĐQT.'}
      ]},
      {k:'a', d:'THỊ TRƯỜNG VỐN QUỐC TẾ\n         ↓\n  ECA / bảo lãnh (SACE)\n         ↓\n   NGÂN HÀNG QUỐC TẾ (HSBC)\n         ↓\n       THACO'},
      {k:'p', d:'Trong nước, THACO cũng huy động trái phiếu: cuối 2025 phát hành thêm <b>2.000 tỷ</b> kỳ hạn 5 năm lãi 8,5% có tài sản bảo đảm; tính từ 2019 đã huy động khoảng <b>18.380 tỷ</b> qua kênh này.'},
      {k:'q', d:'Đây là lý do một doanh nghiệp không cần ông chủ có sẵn hàng trăm nghìn tỷ tiền mặt. Tập đoàn phải xây được <b>khả năng huy động vốn</b> — và đó mới là tài sản thật sự lớn.'}
    ]},

    {id:'dat', t:'Sổ đất — ba loại hoàn toàn khác nhau', ic:'map', khoi:[
      {k:'p', d:'Gộp chung "THACO có nhiều đất" là bỏ mất điều quan trọng nhất: ba loại đất này <b>sinh dòng tiền rất khác nhau</b>, và chỉ một loại có biên lợi nhuận đủ lớn để cứu bảng cân đối.'},
      {k:'the', ds:[
        {t:'Đất đô thị', vd:'Sala / Thủ Thiêm ~106 ha', acc:'#a371f7',
         d:'Đất → hạ tầng → quy hoạch → căn hộ/villa → giá bán. Biên EBITDA ước 50–65%. Đây là loại được kỳ vọng tạo tiền mặt.'},
        {t:'Đất công nghiệp', vd:'Chu Lai ~2,4 triệu m² · cơ khí 320 ha', acc:'#58a6ff',
         d:'Đất → nhà máy → sản xuất. Biên công nghiệp, thấp hơn BĐS nhưng ổn định và tạo tài sản thật.'},
        {t:'Đất nông nghiệp', vd:'~86.000 ha · VN, Lào, Campuchia', acc:'#d29922',
         d:'Đất → trồng → thu hoạch → xuất khẩu. Biên thấp nhất, và hiện đang là nơi hấp thụ vốn chứ chưa sinh lời.'}
      ]},
      {k:'p', d:'<b>Chu Lai</b> là khu kinh tế mở <b>do Nhà nước quy hoạch</b>, không phải đất riêng Nhà nước cho THACO. Nhà nước làm quy hoạch, đường, cảng, sân bay, KCN, cơ chế đầu tư — rồi thu hút doanh nghiệp. THACO vào từ 2003 và đầu tư nhà máy, cơ khí, logistics, cảng. Qua thời gian hai bên <b>khoá vào nhau</b>: quy hoạch tỉnh nay đặt mục tiêu phát triển trung tâm cơ khí và ô tô quốc gia quanh chính Chu Lai.'},
      {k:'a', d:'   QUY HOẠCH QUẢNG NAM\n            ↓\n    KHU KINH TẾ CHU LAI\n            ↓\n   ┌────────┼────────┐\n cảng      KCN   logistics\n   └────────┼────────┘\n          THACO\n            ↓\n         Ô TÔ → CƠ KHÍ\n            ↓\n   CÔNG NGHIỆP HỖ TRỢ'},
      {k:'q', d:'Nhà nước quy hoạch <b>+</b> THACO phát triển theo quy hoạch <b>≠</b> Nhà nước sở hữu THACO. Đây là <b>state–private alignment</b>, một dạng phối hợp, không phải quan hệ sở hữu.'}
    ]},

    {id:'bt', t:'Thủ Thiêm — cơ chế BT, và chỗ phải cẩn thận', ic:'stairs', khoi:[
      {k:'p', d:'Đây là chỗ THACO chạm đúng cơ chế đất mà Vingroup dùng, nên phải soi kỹ nhất — và cũng là chỗ dễ kết luận vội nhất.'},
      {k:'moc', ds:[
        {y:'2013', t:'Chỉ định nhà đầu tư', d:'UBND TP.HCM <b>chỉ định</b> Đại Quang Minh làm dự án 4 tuyến đường chính tại Thủ Thiêm theo hợp đồng BT.', hot:1},
        {y:'2014', t:'Thanh toán bằng quỹ đất', d:'Giao gần <b>79 ha</b>: ~36 ha đất ở và thương mại dịch vụ, 8,73 ha công trình công cộng, 1,79 ha công viên cây xanh, 31,25 ha giao thông.', hot:1},
        {y:'sau đó', t:'Sala thành hình', d:'Cùng các khu đất khác, quy mô Sala được mô tả khoảng <b>106 ha</b>. THACO cũng tham gia cầu Thủ Thiêm 2.'}
      ]},
      {k:'a', d:'ĐẤT THỦ THIÊM\n      ↓ ban đầu\n  giá trị thấp\n      ↓\nHẠ TẦNG GIAO THÔNG\n      ↓ kết nối tốt hơn\n  GIÁ TRỊ ĐẤT ↑\n      ↓\n    SALA\n      ↓\n BẤT ĐỘNG SẢN\n      ↓\n  DÒNG TIỀN'},
      {k:'q', do:1, d:'<b>Điều này KHÔNG tự động chứng minh ưu ái bất thường.</b> BT "đổi hạ tầng lấy quỹ đất" là một cơ chế đầu tư đã từng được sử dụng hợp pháp.'},
      {k:'p', d:'Muốn kết luận có lợi ích bất thường thì phải đi thêm đúng một tầng nữa, và đó là những câu chưa có hồ sơ để trả lời:'},
      {k:'ds', ds:[
        'Giá trị 4 tuyến đường được định là bao nhiêu, tại thời điểm nào?',
        'Giá trị quỹ đất được giao định là bao nhiêu, tại thời điểm nào?',
        'Ai thẩm định, theo phương pháp gì?',
        'Có đấu giá hay chỉ định?',
        'Định giá lại sau này thế nào, và chênh lệch ai hưởng?'
      ]}
    ]},

    {id:'donbay', t:'Đòn bẩy dự án — một ví dụ nhỏ mà đầy đủ', ic:'gauge', khoi:[
      {k:'p', d:'KCN Thaco–Thái Bình là ví dụ đẹp nhất về cơ chế, vì con số nằm trong quyết định chủ trương đầu tư được công bố công khai.'},
      {k:'so', ds:[
        {t:'Tổng vốn dự án', v:'2.132,6 tỷ', d:'Toàn bộ hạ tầng khu công nghiệp'},
        {t:'Vốn chủ sở hữu', v:'319,9 tỷ', d:'≈ 15%', acc:'#2ea043'},
        {t:'Vay ngân hàng', v:'1.812,7 tỷ', d:'≈ 85%', acc:'#d29922'}
      ]},
      {k:'a', d:'CÓ 15 ĐỒNG VỐN CHỦ\n        +\nNGÂN HÀNG CHO 85\n        =\n100 ĐỒNG TÀI SẢN\n        ↓\n      KCN\n        ↓\n  đất công nghiệp\n        ↓\n   khách thuê\n        ↓\n   DÒNG TIỀN'},
      {k:'q', d:'Nếu dự án thành công, <b>15 đồng vốn chủ kiểm soát một tài sản được xây bằng 100 đồng vốn</b>. Đó chính là sức mạnh của leverage — và cũng là lý do lãi suất là cái kim nguy hiểm nhất với mô hình này.'},
      {k:'p', d:'Cùng logic đó ở quy mô lớn hơn: KCN cơ khí chuyên dụng tại Bình Dương quy mô khoảng <b>786 ha</b>, tổng vốn dự kiến hơn <b>75.000 tỷ</b>, đồng thời nghiên cứu năng lực phục vụ công nghiệp đường sắt.'}
    ]},

    {id:'hagl', t:'HAGL Agrico — M&A cứu doanh nghiệp, và cross-subsidy', ic:'chain', khoi:[
      {k:'p', d:'Năm 2018 THACO bắt đầu hợp tác với Hoàng Anh Gia Lai. Chính THACO nói đã <b>ứng trên 10.500 tỷ</b> để hỗ trợ tái cấu trúc nợ và phát triển lại hệ nông nghiệp.'},
      {k:'a', d:'HAGL AGRICO\n     ↓ nợ cao / khó khăn\n   THACO\n     ↓ bơm vốn\n tái cấu trúc\n     ↓\nTHACO AGRI\n     ↓\nnông nghiệp quy mô lớn'},
      {k:'p', d:'Đến nay đây vẫn là phần nhiều rủi ro: HAGL Agrico tiếp tục có gánh nợ lớn và THACO Agri trở thành một trong những chủ nợ quan trọng nhất, với hơn <b>9.300 tỷ</b> cho vay phần lớn không có tài sản bảo đảm.'},
      {k:'q', d:'Đây là <b>cross-subsidy</b> — tiền từ ô tô và vốn tập đoàn chuyển sang nông nghiệp, cùng logic Vingroup dùng bất động sản nuôi VinFast. Khác ở chỗ nguồn tiền gốc của THACO đa dạng hơn về công nghiệp thực.'}
    ]},

    {id:'baolanh', t:'Bảo lãnh chéo và tài sản bảo đảm biết di chuyển', ic:'chain', khoi:[
      {k:'p', d:'Đây là thứ làm hệ sinh thái <b>không thực sự độc lập về tài chính</b>, dù trên giấy là các pháp nhân riêng.'},
      {k:'a', d:'                 THACO mẹ\n                     │\n            PARENT GUARANTEE\n                     │\n       ┌─────────────┼─────────────┐\n     AUTO          AGRI         THADICO'},
      {k:'p', d:'Ngân hàng do đó không chỉ hỏi "THACO Agri có trả nổi nợ không?" mà hỏi "<b>nếu Agri gặp vấn đề thì mẹ có đứng sau không?</b>". Đó là <b>group credit support</b>.'},
      {k:'p', d:'Và tài sản bảo đảm thì di chuyển được. Trái phiếu THACO Agri trị giá <b>2.400 tỷ</b> phát hành 2021, có mẹ bảo lãnh thanh toán, ban đầu bảo đảm bằng khoảng <b>240 triệu cổ phần THACO</b>, sau đó được <b>thay bằng quyền sử dụng đất</b> — hai thửa tại An Lợi Đông, TP Thủ Đức, tổng diện tích hơn 2 ha. Khoản này được mua lại trước hạn tháng 8/2025.'},
      {k:'q', d:'Cổ phần → tài sản bảo đảm, rồi đất → tài sản bảo đảm. Tức <b>đất và cổ phần đều chuyển hoá được thành khả năng vay</b>. Đây là cùng một cơ chế với vòng "đất → thế chấp → tín dụng" ở mạch truyền dẫn.'}
    ]},

    {id:'duongsat', t:'Đường sắt Bắc–Nam — test case lớn nhất', ic:'play', khoi:[
      {k:'p', d:'THACO đề xuất tham gia đường sắt tốc độ cao Bắc–Nam với cơ cấu vốn do chính họ công bố:'},
      {k:'a', d:'DỰ ÁN 100\n   │\n   ├── 20\n   │   vốn chủ / vốn huy động chịu trách nhiệm\n   │\n   └── 80\n       NỢ / HUY ĐỘNG'},
      {k:'p', d:'Cách nghĩ về megaproject không phải là "ông chủ rút tiền túi xây đường sắt", mà là: vốn chủ + ngân hàng + trái phiếu + nhà đầu tư + đối tác trong nước + đối tác quốc tế → megaproject. Và ở đó THACO có một thứ Vingroup yếu hơn — <b>năng lực chế tạo</b>: ray, toa xe, kết cấu thép, thiết bị, lắp ráp, bảo trì, logistics.'},
      {k:'q', do:1, d:'<b>Đề xuất không phải là tiền đã được cấp.</b> Hiện chỉ có thể nói "THACO muốn dùng 20% vốn chịu trách nhiệm và 80% huy động/vay". Chưa thể nói "Nhà nước đã cho THACO 80% với lãi 0%" — đó sẽ là kết luận sai khi chưa có quyết định cuối cùng.'}
    ]},

    {id:'nhanuoc', t:'Nhà nước xuất hiện ở đâu — và không ở đâu', ic:'map', khoi:[
      {k:'p', d:'Tách hai chuyện này ra là toàn bộ giá trị của hồ sơ, vì chúng bị trộn thường xuyên nhất.'},
      {k:'the', ds:[
        {t:'CHƯA THẤY', vd:'sở hữu · HĐQT · bảo lãnh toàn tập đoàn · bailout', acc:'#4b5563',
         d:'Không có mạng pháp nhân Nhà nước đứng sau sở hữu. Không có ghế HĐQT do cơ quan Nhà nước chỉ định. Tổ chức xếp hạng đánh giá hỗ trợ Chính phủ ở mức thấp và không đưa vào kết quả.'},
        {t:'RẤT MẠNH', vd:'quy hoạch · đất · BT · PPP · hạ tầng · dự án chiến lược', acc:'#f0503f',
         d:'Chu Lai, Thủ Thiêm, KCN, cảng, đường bộ, và nay là đường sắt. Chính sách quốc gia hiện chủ động khuyến khích doanh nghiệp tư nhân lớn tham gia dự án chiến lược, có cơ chế như đấu thầu hạn chế hoặc chỉ định trong một số bối cảnh.'}
      ]},
      {k:'a', d:'NHÀ NƯỚC\n   ├── cơ chế PPP\n   ├── quy hoạch\n   ├── giải phóng mặt bằng\n   ├── cơ chế tín dụng?\n   ├── thuế?\n   ├── đất\n   └── hợp đồng dự án\n           ↓\n         THACO\n           ↓\n   mang dự án đó tới\n   ngân hàng · trái chủ ·\n   Jardine · nhà đầu tư quốc tế\n           ↓\n     HUY ĐỘNG VỐN'},
      {k:'q', d:'Nhà nước không nhất thiết phải chuyển 50 tỷ USD cho ai. Chỉ cần <b>mở các ổ cắm</b>, thì doanh nghiệp tự mang dự án đi huy động được. Đấy mới là quyền lực thực sự của một đầu tàu quốc gia.'}
    ]},

    {id:'khac', t:'Khác Vingroup ở chỗ nào', ic:'stairs', khoi:[
      {k:'a', d:'          VINGROUP\n              ↓\n       BĐS / TÀI SẢN\n              ↓\n          DÒNG VỐN\n              ↓\n   ┌──────────┼──────────┐\n  Ô TÔ    HẠ TẦNG   NĂNG LƯỢNG'},
      {k:'a', d:'            THACO\n              ↓\n            Ô TÔ\n              ↓\n           CƠ KHÍ\n              ↓\n   ┌──────────┼──────────┐\nLOGISTICS   KCN    NÔNG NGHIỆP\n    ↓        ↓         ↓\n  CẢNG     BĐS     XUẤT KHẨU\n   └────────┼─────────┘\n            ↓\n         HẠ TẦNG\n            ↓\n        ĐƯỜNG SẮT'},
      {k:'the', ds:[
        {t:'Lõi công nghiệp thật', acc:'#2ea043',
         d:'THACO tạo ra nhà máy, cảng, dây chuyền cơ khí, máy móc, kho, xe, KCN, nông trại — không chỉ đất và kỳ vọng giá. Đây là <b>lá chắn</b> Vingroup không mạnh bằng.'},
        {t:'Có đối trọng ngoại', acc:'#58a6ff',
         d:'Jardine 26,7% và ghế Phó Chủ tịch. Chaebol cổ điển là hệ đóng quanh gia đình; đây thì không hoàn toàn.'},
        {t:'Rủi ro dàn trải, không tập trung', acc:'#f0503f',
         d:'Vingroup có một hố đốt vốn tên VinFast. THACO không có một hố duy nhất mà có <b>quá nhiều ngành thâm dụng vốn cùng lúc</b>: ô tô, cơ khí, BĐS, nông nghiệp, logistics, hạ tầng, đường sắt.'}
      ]}
    ]},

    {id:'doc', t:'Đọc cho đúng', ic:'brain', khoi:[
      {k:'sd', ds:[
        {sai:'Nhà nước đã cho THACO vay 80% dự án đường sắt Bắc–Nam.',
         dung:'THACO <b>đề xuất</b> cơ cấu 20% vốn chịu trách nhiệm và 80% huy động/vay. Đề xuất, dự thảo và quyết định giải ngân là ba trạng thái khác nhau; hiện chưa có quyết định cuối cùng.'},
        {sai:'Được chỉ định làm đường ở Thủ Thiêm rồi nhận đất, vậy là ưu ái bất thường.',
         dung:'BT "đổi hạ tầng lấy quỹ đất" là một cơ chế đầu tư đã từng được dùng. Muốn kết luận bất thường phải so <b>giá trị 4 tuyến đường với giá trị quỹ đất được giao</b>, và biết ai định giá, tại thời điểm nào, có đấu giá không. Chưa có đủ hồ sơ đó.'},
        {sai:'THACO cũng chỉ là một công ty bất động sản trá hình.',
         dung:'Nó tạo ra tài sản sản xuất thật. Đó là <b>năng lực chế tạo</b> — thứ khiến nó hấp dẫn với chiến lược công nghiệp hoá, và cũng là thứ khiến nó khác Vingroup về bản chất.'},
        {sai:'Chính phủ bảo THACO làm đường sắt, vậy là ra lệnh.',
         dung:'"Hãy nghiên cứu, hãy tham gia" khác hoàn toàn "phải làm vì Nhà nước ra lệnh". Bằng chứng hiện có thuộc loại thứ nhất; loại thứ hai chưa tìm thấy.'}
      ]}
    ]},

    {id:'gap', t:'Năm khoảng trống cho vòng sau', ic:'src', khoi:[
      {k:'p', d:'THACO chưa niêm yết nên phần lớn số liệu ở trên nhìn qua tay thứ ba. Đây là những chỗ cần hồ sơ gốc mới đi tiếp được.'},
      {k:'ds', ds:[
        '<b>Bank-by-bank:</b> ngân hàng nào cho pháp nhân nào vay, bao nhiêu, kỳ hạn, thế chấp gì, đáo hạn năm nào.',
        '<b>Sổ đất:</b> THACO / Đại Quang Minh / THADICO kiểm soát bao nhiêu đất, lấy theo đấu giá, BT, đấu thầu hay giao/thuê, giá gốc bao nhiêu.',
        '<b>Bảo lãnh chéo:</b> công ty nào bảo lãnh cho công ty nào, tài sản nào bảo đảm cho trái phiếu nào.',
        '<b>Dòng tiền nội bộ chi tiết:</b> Auto → mẹ → Agri → HAGL, và Jardine rót vào pháp nhân nào.',
        '<b>Ưu đãi Nhà nước:</b> cái nào áp dụng chung cho cả ngành, cái nào dành riêng cho dự án THACO.'
      ]},
      {k:'q', d:'Vòng sau đáng làm nhất là <b>bản đồ ngân hàng – trái phiếu – tài sản bảo đảm</b>. Chỉ có nó mới trả lời được câu quan trọng nhất: nếu một mắt xích THACO gặp vấn đề thì cú sốc truyền sang ngân hàng nào và pháp nhân nào trước tiên.'}
    ]}
  ],

  noi:['tindung','bds','laisuat']
}

];

/* ─────────────────────────────────────────────────────────────
   DANH SÁCH SOI — lộ trình, không phải bảng xếp hạng giàu

   Xếp theo khả năng trở thành CÔNG CỤ DOANH NGHIỆP TƯ NHÂN CÓ
   VAI TRÒ CHIẾN LƯỢC, không theo quy mô tài sản. Một tập đoàn
   rất giàu mà không đứng ở ổ cắm nào của Nhà nước thì không
   thuộc mô hình này.
   ───────────────────────────────────────────────────────────── */
const DANHSACH = [
  {muc:1, t:'Gần mô hình đầu tàu quốc gia nhất', acc:'#f0503f', ds:[
    {ten:'Vingroup', o:'đất · hạ tầng · năng lượng', soi:'vingroup'},
    {ten:'THACO',    o:'công nghiệp · cơ khí · đường sắt', soi:'thaco'},
    {ten:'Hoà Phát', o:'thép — nguyên liệu nền của mọi công trình',
     ghi:'Không cần hệ sinh thái tiêu dùng. Nó nằm ở tầng vật liệu: đường sắt, cảng, cầu, đô thị đều phải đi qua thép. Vingroup xây hệ sinh thái; Hoà Phát cung cấp xương cho hệ sinh thái đó.'},
    {ten:'FPT',      o:'AI · bán dẫn · dữ liệu · phần mềm',
     ghi:'Ổ cắm "não số". Cuối 2025 công bố đầu tư 5 công nghệ chiến lược — Quantum AI, an ninh mạng, UAV, dữ liệu và công nghệ đường sắt; đầu 2026 lập nhà máy kiểm thử/đóng gói bán dẫn và bắt tay Viettel cho chuỗi từ đào tạo tới thương mại hoá.'}
  ]},
  {muc:2, t:'Giữ một ổ cắm chiến lược rất mạnh', acc:'#d29922', ds:[
    {ten:'Sun Group', o:'sân bay · du lịch · hạ tầng đô thị',
     ghi:'Cấu trúc đất → hạ tầng → du lịch → sân bay → đô thị. Cuối 2025 nhận dự án chỉnh trang sông Tô Lịch; tháng 5/2026 ký hợp tác với GMR về phát triển hạ tầng sân bay. Chưa có chiều sâu công nghiệp như THACO hay Hoà Phát.'},
    {ten:'Sovico',   o:'hàng không · ngân hàng · tài chính',
     ghi:'ĐÁNG SOI SỚM NHẤT. Sovico – HDBank – Vietjet là hệ có ngân hàng nằm ngay bên trong, tức nút tuần hoàn vốn không phải đi thuê. Tháng 2/2026 còn công khai mời các hãng sản xuất, ngân hàng, leasing, bảo hiểm và công nghệ cùng xây hệ sinh thái tài chính hàng không tại TP.HCM.'},
    {ten:'Masan',    o:'phân phối tiêu dùng · khoáng sản chiến lược',
     ghi:'Quyền lực khác hẳn: đứng gần túi tiền hàng ngày của hàng chục triệu người. WinCommerce dự kiến ~6.100 cửa hàng cuối 2026, cộng chuỗi vonfram và khoáng sản chiến lược. Cặp Masan – Techcombank cũng đáng soi vì cùng mạch doanh nhân Đông Âu.'}
  ]},
  {muc:3, t:'Có thể nổi lên nhờ hạ tầng', acc:'#58a6ff', ds:[
    {ten:'GELEX',    o:'điện · thiết bị · khu công nghiệp',
     ghi:'Nhỏ hơn nhóm trên nhưng đứng đúng ổ cắm điện: thiết bị điện chiếm gần 60% cơ cấu doanh thu theo kế hoạch 2025, đúng lúc Việt Nam phải đầu tư mạnh cho lưới và hạ tầng truyền tải.'}
  ]}
];

window.DQT_SOI = { THANG: THANG, TIEUCHI: TIEUCHI, SOI: SOI, DANHSACH: DANHSACH };
})();
