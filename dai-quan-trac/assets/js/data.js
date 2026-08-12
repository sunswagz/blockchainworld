(function () {
"use strict";

/* ============================================================
   ĐÀI QUAN TRẮC — dữ liệu đã phân loại từ hồ sơ nguồn
   6 cụm chủ đề · 5 chiến trường · 8 đồng hồ · 11 mắt xích
   ============================================================ */

const IC = {
  flow:'<path d="M3 7h4l2 10h4l2-10h6"/><circle cx="19" cy="7" r="1.6"/>',
  chain:'<path d="M9 12h6"/><rect x="2" y="8" width="7" height="8" rx="3"/><rect x="15" y="8" width="7" height="8" rx="3"/>',
  gauge:'<path d="M12 20a8 8 0 1 1 8-8"/><path d="M12 12l4-3"/>',
  map:'<path d="M9 4l6 2 5-2v14l-5 2-6-2-5 2V6z"/><path d="M9 4v14M15 6v14"/>',
  play:'<path d="M6 4l13 8-13 8z"/>',
  stairs:'<path d="M3 20h4v-4h4v-4h4V8h4V4"/>',
  book:'<path d="M4 5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1-2-2z"/><path d="M8 3v18"/>',
  brain:'<path d="M12 5a3 3 0 0 0-6 0 3 3 0 0 0-1 5.8A3 3 0 0 0 8 16h4z"/><path d="M12 5a3 3 0 0 1 6 0 3 3 0 0 1 1 5.8A3 3 0 0 1 16 16h-4z"/><path d="M12 5v14"/>',
  radio:'<circle cx="12" cy="12" r="2"/><path d="M7.8 7.8a6 6 0 0 0 0 8.4M16.2 7.8a6 6 0 0 1 0 8.4M4.9 4.9a10 10 0 0 0 0 14.2M19.1 4.9a10 10 0 0 1 0 14.2"/>',
  ship:'<path d="M3 17l2-6h14l2 6"/><path d="M5 11V7h14v4M12 3v4"/><path d="M2 20c2 0 2-1.4 4-1.4S8 20 10 20s2-1.4 4-1.4S16 20 18 20s2-1.4 4-1.4"/>',
  fire:'<path d="M12 3c1 4-3 5-3 8a3 3 0 0 0 6 0c0-1-.5-2-.5-2 2 1 3.5 3 3.5 5a6 6 0 0 1-12 0c0-5 6-6 6-11z"/>',
  factory:'<path d="M3 20V10l5 3V10l5 3V10l5 3v7z"/><path d="M8 20v-3M13 20v-3M18 20v-3"/>',
  star:'<path d="M12 3l2.6 6 6.4.6-4.8 4.3 1.4 6.3L12 17l-5.6 3.2 1.4-6.3L3 9.6 9.4 9z"/>',
  eagle:'<path d="M3 8l9 4 9-4"/><path d="M12 12v8"/><path d="M5 5l7 3 7-3"/>',
  src:'<circle cx="12" cy="12" r="9"/><path d="M12 8v4l3 2"/>'
};
const svg = k => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+(IC[k]||IC.src)+'</svg>';

/* ---------- 5 CHIẾN TRƯỜNG ---------- */
const THEATERS = [
  {
    id:'hormuz', ic:'ship', flag:'⚓', name:'Eo biển Hormuz', short:'Hormuz',
    role:'Cổ chai biển toàn cầu',
    acc:'#e5484d',
    query:'Strait of Hormuz oil shipping tanker traffic insurance disruption',
    lede:'Không phải nguồn dầu — là cái cổ chai. Mọi thùng dầu đi bằng đường biển từ Vùng Vịnh đều phải chui qua đây. Nghẽn ở đây không làm mất dầu, nó làm <b>đắt dầu ở mọi nơi cùng lúc</b>.',
    mech:['GIÁ DẦU THẾ GIỚI ↑','phí bảo hiểm chiến tranh + cước tàu ↑','xăng dầu · logistics · xây dựng · vận tải · sản xuất VN ↑','CPI Việt Nam ↑'],
    ascii:'TRUNG ĐÔNG / HORMUZ\n        ↓\nGIÁ DẦU THẾ GIỚI ↑\n        ↓\nxăng dầu / logistics / xây dựng /\nvận tải / sản xuất Việt Nam ↑',
    keypoint:'Việt Nam có một đường nhạy cảm <b>trực tiếp</b> với địa chính trị năng lượng, không chỉ đi vòng qua Trung Quốc. Nghi Sơn — theo Bộ Công Thương cung cấp khoảng 40% nhu cầu xăng dầu trong nước — phải tìm nguồn dầu thô thay thế khi Hormuz gián đoạn.',
    clocks:['Giá dầu Brent (USD/thùng)','Phí bảo hiểm chiến tranh cho tàu chở dầu','Lưu lượng tàu qua eo biển','Tồn kho & nguồn dầu thô của Nghi Sơn','Giá xăng dầu bán lẻ trong nước'],
    hits:['Trực tiếp vào Việt Nam qua giá nhiên liệu và an ninh xăng dầu nội địa','Gián tiếp qua chi phí nhập khẩu đường biển của Trung Quốc'],
    scen:'Kịch bản A — sốc giá toàn cầu'
  },
  {
    id:'nga', ic:'fire', flag:'🛢️', name:'Nga – Ukraina', short:'Nga–Ukraina',
    role:'Chân lục địa + đường ống + dầu chiết khấu',
    acc:'#d29922',
    query:'Russia Ukraine war oil export pipeline China crude discount sanctions',
    lede:'Khác Hormuz về bản chất. Đây không phải cổ chai — đây là <b>một chân đứng</b> của Trung Quốc: dầu đi bằng đường ống, không qua biển, và thường có chiết khấu.',
    mech:['Trung Quốc mất một phần nguồn dầu lục địa / giá cạnh tranh','chi phí công nghiệp Trung Quốc ↑','giá đầu vào sang Việt Nam ↑','biên lợi nhuận doanh nghiệp VN ↓'],
    ascii:'NGA\n ↓ đường ống (không qua biển)\nTRUNG QUỐC\n ↓ chi phí công nghiệp ↑\nĐẦU VÀO SANG VIỆT NAM ↑\n ↓\nCHI PHÍ SẢN XUẤT VN ↑',
    keypoint:'Tác động <b>trực tiếp</b> tới Việt Nam yếu hơn Hormuz rõ rệt. Nhưng tác động <b>gián tiếp</b> qua chi phí công nghiệp Trung Quốc thì có thể đáng kể — vì Việt Nam nhập tư liệu sản xuất chủ yếu từ Trung Quốc.',
    clocks:['Sản lượng & giá xuất khẩu dầu Nga','Mức chiết khấu Nga bán cho Trung Quốc','Công suất các tuyến đường ống sang Trung Quốc','Diễn biến cấm vận / trần giá','Giá than và khí ở châu Á'],
    hits:['Gián tiếp là chính — đi vòng qua công xưởng Trung Quốc','Trực tiếp yếu: Việt Nam ít phụ thuộc dầu Nga'],
    scen:'Kịch bản B — sốc hub công xưởng'
  },
  {
    id:'tq', ic:'factory', flag:'🏭', name:'Trung Quốc', short:'Trung Quốc',
    role:'Bộ chuyển hóa — biến năng lượng thành hàng hóa toàn cầu',
    acc:'#f0503f',
    query:'China industrial output energy imports crude oil coal exports property crisis',
    lede:'Trung Quốc không đơn thuần là "nước mua dầu". Nó là <b>bộ máy chuyển năng lượng thành hàng hóa</b> cho cả thế giới. Cú sốc năng lượng ở đây không làm nó sập — nó làm <b>chi phí tăng, biên lợi nhuận giảm, giá xuất khẩu điều chỉnh</b>, rồi truyền tiếp xuống hạ lưu.',
    circuits:[
      {k:'Mạch A',t:'Điện và nhiệt công nghiệp',d:'Lõi điện vẫn dựa rất lớn vào than — theo EIA, than chiếm khoảng 62% tiêu thụ năng lượng sơ cấp và ~60% sản lượng điện. Nghĩa là chỉ sốc dầu thôi thì nhà máy Trung Quốc không tắt điện ngay.'},
      {k:'Mạch B',t:'Vận tải, logistics, máy công trình, hóa dầu',d:'Đây mới là chỗ dầu quan trọng: tàu biển, xe tải, máy xúc, hàng không, và naphtha/feedstock cho nhựa, sợi, phân bón, hóa chất nền. Dầu không phải "điện sinh mệnh" của nhà máy — nó là <b>máu của hệ tuần hoàn hàng hóa</b>.'},
      {k:'Mạch C',t:'Nhập dầu thô để lọc hóa',d:'Trung Quốc vẫn là nước nhập dầu cực lớn — EIA ghi nhận nhập khẩu dầu thô năm 2024 khoảng 11,1 triệu thùng/ngày. Phần lớn đi bằng đường biển, nên nhạy với cổ chai.'}
    ],
    buffers:[
      {t:'Than nội địa',d:'Xương sống điện năng và nhiệt công nghiệp — khiến Trung Quốc ít bị "tắt máy hàng loạt" chỉ vì dầu.'},
      {t:'Nhập khẩu đa nguồn',d:'Nga là nguồn lớn nhất nhưng không duy nhất: Saudi, Iran, Iraq, Oman, UAE, Brazil, Angola…'},
      {t:'Đường ống',d:'Một phần dầu vào bằng ống từ Nga và láng giềng, giảm phụ thuộc tuyệt đối vào đường biển.'},
      {t:'Quy mô nhà nước',d:'Điều phối được DNNN năng lượng, hạn ngạch nhập, kho dự trữ, tín dụng, một phần giá, và logistics.'}
    ],
    clocks:['Nhập khẩu dầu thô (triệu thùng/ngày)','Giá điện & sản lượng than','PMI sản xuất','Giá xuất xưởng (PPI)','Giá hàng trung gian xuất sang VN'],
    hits:['Là tầng truyền dẫn số 2 tới Việt Nam — qua giá đầu vào công nghiệp','Đồng thời là đối thủ cạnh tranh và nguồn dịch chuyển đơn hàng/FDI'],
    scen:'Trung tâm của cả kịch bản A lẫn B'
  },
  {
    id:'vn', ic:'star', flag:'🇻🇳', name:'Việt Nam', short:'Việt Nam',
    role:'Giao điểm — nơi nhiều cú sốc khác nguồn hội tụ',
    acc:'#d4a72c',
    query:'Vietnam economy exports credit growth real estate bond interest rate exchange rate',
    lede:'Cách nói đúng không phải "tất cả đang cùng đánh Việt Nam", mà là: <b>Việt Nam nằm đúng giao điểm của nhiều hệ thống, nên một số cú sốc khác nguồn có khả năng cùng hội tụ tại đây.</b>',
    layers:[
      {n:'Tầng truyền dẫn 1',t:'Trực tiếp qua giá năng lượng toàn cầu',d:'Hormuz/Trung Đông sốc → giá dầu thế giới ↑ → xăng dầu, logistics, xây dựng, vận tải, sản xuất trong nước ↑. Cộng thêm ràng buộc an ninh xăng dầu nội địa.'},
      {n:'Tầng truyền dẫn 2',t:'Gián tiếp qua Trung Quốc',d:'Nga/Hormuz sốc → chi phí công nghiệp Trung Quốc ↑ → đầu vào sang Việt Nam ↑ → chi phí sản xuất ↑ → bào mòn biên lợi nhuận, hàng Việt bớt cạnh tranh.'}
    ],
    clocks:['Lãi suất vay mua nhà','Số lượng giao dịch bất động sản','Tỷ lệ hấp thụ dự án mới','Giá thứ cấp (không phải giá rao bán)','Nợ xấu & xử lý tài sản bảo đảm'],
    danger:'Dấu hiệu đáng ngại nhất không phải "giá rao bán giảm 5%", mà là <b>giao dịch giảm + lãi suất tăng + số người buộc phải bán vì nợ tăng — cùng lúc</b>.',
    hits:['Bị đánh trực tiếp qua nhiên liệu và CPI','Bị đánh gián tiếp qua đầu vào từ Trung Quốc','Bị đánh ở đầu ra qua nhu cầu và thuế của Mỹ/EU','Bị khuếch đại từ bên trong qua ngân hàng – BĐS – niềm tin'],
    scen:'Điểm hạ lưu của cả ba kịch bản'
  },
  {
    id:'my', ic:'eagle', flag:'🦅', name:'Hoa Kỳ', short:'Hoa Kỳ',
    role:'Phía đầu ra — thuế, nhu cầu, và cái giá của đồng USD',
    acc:'#58a6ff',
    query:'US tariffs Vietnam trade Federal Reserve interest rate dollar consumer demand',
    lede:'Ba chiến trường kia đánh vào <b>đầu vào</b> của Việt Nam. Mỹ đánh vào <b>đầu ra</b> — và đánh thêm một đường thứ hai qua lãi suất USD.',
    mech:['nhu cầu tiêu dùng Mỹ ↓ → đơn hàng xuất khẩu VN ↓','thuế quan ↑ → biên lợi nhuận nhà máy VN ↓','lãi suất USD ↑ → áp lực tỷ giá VND','tỷ giá căng → lãi suất VN khó giảm'],
    ascii:'USD / LÃI SUẤT MỸ        THƯƠNG MẠI / THUẾ\n        ↓                        ↓\n   TỶ GIÁ VND              XUẤT KHẨU VN ↓\n        ↓                        ↓\n   LÃI SUẤT VN            DOANH THU DN ↓\n        └───────────┬────────────┘\n                    ↓\n              THU NHẬP / VIỆC LÀM',
    keypoint:'Đây là đường truyền dẫn có thể đánh vào bất động sản Việt Nam <b>mà không cần liên quan trực tiếp đến nhà đất</b>: nó đi qua đơn hàng, thu nhập, tỷ giá và lãi suất trước.',
    clocks:['Chính sách thuế quan với hàng Việt Nam','Lãi suất điều hành của Fed','Chỉ số USD và tỷ giá USD/VND','Doanh số bán lẻ & tồn kho Mỹ','Kim ngạch xuất khẩu VN sang Mỹ'],
    hits:['Đầu ra: đơn hàng và thuế','Tài chính: USD, tỷ giá, mặt bằng lãi suất'],
    scen:'Biến số nằm ngoài trục năng lượng — có thể cộng hưởng với A hoặc B'
  }
];

/* ---------- 8 ĐỒNG HỒ CẢNH BÁO SỚM ---------- */
const GAUGES = [
  {id:'nangluong', t:'Năng lượng',   d:'Giá dầu, cước vận tải, phí bảo hiểm, an ninh nguồn cung xăng dầu nội địa.'},
  {id:'tq',        t:'Trung Quốc',   d:'Chi phí công nghiệp, PPI, giá hàng trung gian xuất sang Việt Nam.'},
  {id:'xuatkhau',  t:'Xuất khẩu',    d:'Đơn hàng, kim ngạch, thuế quan, tồn kho ở thị trường đầu ra.'},
  {id:'tygia',     t:'Tỷ giá',       d:'USD/VND, dự trữ ngoại hối, áp lực từ lãi suất USD.'},
  {id:'laisuat',   t:'Lãi suất',     d:'Lãi suất điều hành, lãi vay mua nhà, chênh lệch huy động – cho vay.'},
  {id:'nganhang',  t:'Ngân hàng',    d:'Nợ xấu, tăng trưởng tín dụng, xử lý tài sản bảo đảm, trái phiếu doanh nghiệp.'},
  {id:'bds',       t:'Bất động sản', d:'Giao dịch, tỷ lệ hấp thụ, giá thứ cấp, số người buộc phải bán.'},
  {id:'niemtin',   t:'Niềm tin',     d:'Biến vô hình điều khiển rất nhiều biến hữu hình. Không có một con số duy nhất.'}
];

/* ---------- MẠCH TRUYỀN DẪN (chương XX) ---------- */
const CHAIN = [
  {id:'hormuz',  t:'Hormuz',              tag:'THƯỢNG NGUỒN', d:'Cổ chai biển toàn cầu. Nghẽn ở đây làm đắt dầu ở mọi nơi cùng lúc.', th:'hormuz'},
  {id:'gia_dau', t:'Giá dầu',             tag:'NĂNG LƯỢNG',   d:'Biến số đầu tiên có thể đo được bằng một con số duy nhất: USD/thùng.'},
  {id:'tq',      t:'Trung Quốc',          tag:'CÔNG XƯỞNG',   d:'Bộ chuyển hóa. Hấp thụ cú sốc bằng 4 bộ đệm rồi truyền phần còn lại xuống hạ lưu.', th:'tq'},
  {id:'dauvao',  t:'Giá đầu vào VN',      tag:'CÔNG NGHIỆP',  d:'Việt Nam nhập chủ yếu là tư liệu sản xuất, Trung Quốc là nguồn lớn nhất.'},
  {id:'cpi',     t:'CPI Việt Nam',        tag:'GIÁ CẢ',       d:'Nơi cú sốc bên ngoài chạm vào ví của người dân lần đầu tiên.'},
  {id:'tygia',   t:'Tỷ giá',              tag:'TIỀN TỆ',      d:'Chịu thêm một lực độc lập từ lãi suất USD — không chỉ từ năng lượng.'},
  {id:'laisuat', t:'Lãi suất',            tag:'CHÍNH SÁCH',   d:'Cái kim nguy hiểm nhất với bất động sản. Vừa là chi phí vay, vừa là mức hấp dẫn của tiền gửi.'},
  {id:'tindung', t:'Tín dụng',            tag:'NGÂN HÀNG',    d:'Bộ khuếch đại của toàn hệ thống. Siết ở đây thì mọi mắt xích phía dưới cùng co lại.'},
  {id:'bds',     t:'Bất động sản',        tag:'TÀI SẢN',      d:'Không đứng riêng: nó vừa là hàng hóa, vừa là tài sản thế chấp cho phần lớn tín dụng.'},
  {id:'niemtin', t:'Niềm tin',            tag:'NHẬN THỨC',    d:'Mắt xích duy nhất không đo được bằng một con số — nhưng điều khiển hành vi của tất cả các mắt xích trên.'},
  {id:'hanhvi',  t:'Hành vi tài chính',   tag:'HẠ NGUỒN',     d:'Mua/không mua · gửi/rút · đầu tư/không đầu tư · giữ VND hay vàng hay USD · tuyển/dừng tuyển.'}
];

/* ---------- 4 CẤP ĐỘ ---------- */
const LEVELS = [
  {n:1, t:'ÁP LỰC', d:'Dầu ↑, lãi suất ↑, chi phí ↑ — nhưng việc làm vẫn tốt, ngân hàng vẫn ổn, BĐS chưa bán tháo.', r:'Hệ thống chịu được.'},
  {n:2, t:'SUY YẾU', d:'Đơn hàng ↓, lợi nhuận doanh nghiệp ↓, BĐS ít giao dịch, lãi vay cao, người dân thận trọng.', r:'Tăng trưởng chậm.'},
  {n:3, t:'VÒNG PHẢN HỒI ÂM', d:'BĐS ↓ → nợ xấu ↑ → ngân hàng siết tín dụng → doanh nghiệp thiếu vốn → việc làm ↓ → thu nhập ↓ → BĐS ↓ tiếp.', r:'Nguy hiểm — vòng lặp đã tự chạy.'},
  {n:4, t:'KHỦNG HOẢNG HỆ THỐNG', d:'Cú sốc ngoài + ngân hàng/BĐS yếu + doanh nghiệp yếu + niềm tin giảm → mọi người cùng phòng thủ cùng lúc.', r:'Khủng hoảng tự khuếch đại.'}
];

/* ---------- KỊCH BẢN ---------- */
const SCEN = [
  {k:'A', t:'Chỉ Hormuz sốc', w:'Sốc giá toàn cầu', acc:'#d29922',
   pts:['Giá dầu thế giới tăng','Việt Nam bị đánh trực tiếp qua xăng dầu, logistics, Nghi Sơn, CPI','Trung Quốc cũng bị tăng chi phí nhập khẩu đường biển','Tác động đến Việt Nam vừa trực tiếp vừa gián tiếp'],
   asc:'HORMUZ nghẽn\n     ↓\ngiá dầu thế giới ↑\n     ↓            ↘\nVIỆT NAM      TRUNG QUỐC\n(trực tiếp)   (chi phí biển ↑)\n     ↓            ↓\n     └──── cộng dồn ────┘'},
  {k:'B', t:'Chỉ Nga sốc', w:'Sốc hub công xưởng', acc:'#58a6ff',
   pts:['Trung Quốc mất một phần nguồn dầu lục địa / giá cạnh tranh','Tác động trực tiếp đến Việt Nam yếu hơn Hormuz','Nhưng gián tiếp qua chi phí công nghiệp Trung Quốc có thể đáng kể'],
   asc:'NGA nghẽn\n     ↓\nTRUNG QUỐC mất chân lục địa\n     ↓\nchi phí công nghiệp TQ ↑\n     ↓\nđầu vào VN ↑ (gián tiếp)'},
  {k:'C', t:'Nga + Hormuz cùng sốc', w:'Cú sốc hệ thống khu vực', acc:'#f0503f',
   pts:['Trung Quốc mất cả chân lục địa lẫn chân biển ở mức độ nào đó','Chi phí dầu / bảo hiểm / logistics / hóa dầu cùng tăng','Áp lực truyền sang toàn bộ chuỗi Á châu','Việt Nam bị đánh kép'],
   asc:'Nga bị nghẽn  +  Hormuz bị căng\n         ↓\nTrung Quốc mất cả chân lục địa\nlẫn chân biển ở mức độ nào đó\n         ↓\nchi phí dầu / bảo hiểm /\nlogistics / hóa dầu cùng tăng\n         ↓\náp lực truyền sang toàn chuỗi Á châu\n         ↓\nVIỆT NAM BỊ ĐÁNH KÉP'}
];

/* ---------- THƯ VIỆN: 6 CỤM PHÂN LOẠI ---------- */
const LIB = [
 {id:'ngam', n:'A', t:'Tài chính ngầm', d:'Công ty ma, layering, và vì sao "che giấu" không đồng nghĩa với "không thể tìm ra".',
  blocks:[
   {h:'Cơ chế tạo lớp', p:'Công ty ma che giấu nguồn tiền không phải vì tiền biến mất, mà vì nó <b>tạo thêm nhiều lớp giấy tờ và pháp nhân giữa tiền và người sở hữu thật</b>. Người điều tra phải lần ngược từng lớp để xác định chủ sở hữu hưởng lợi thực sự.',
    a:'NGUỒN TIỀN THẬT\n     │  khó giải thích nguồn gốc\n     ↓\nCông ty A\n     ├── giao dịch / hợp đồng / khoản phải thu\n     ↓\nCông ty B\n     ├── thêm một lớp pháp nhân\n     ↓\nTÀI SẢN / DOANH THU CÓ VẺ HỢP PHÁP\n     ↓\nNGƯỜI HƯỞNG LỢI THỰC SỰ'},
   {h:'"Rửa" nghĩa là gì', p:'Không phải biến tiền bẩn thành loại tiền khác, mà là đổi câu chuyện trên giấy tờ từ <i>"tôi có số tiền này nhưng không giải thích được nguồn gốc"</i> thành <i>"đây là tiền phát sinh từ hoạt động kinh doanh"</i>. Ba ý niệm quen thuộc: <b>placement → layering → integration</b>, trong đó công ty ma phục vụ khâu layering.'},
   {h:'Vì sao vẫn tìm ra được', p:'Ngân hàng và cơ quan điều tra đối chiếu chủ sở hữu thực sự, lịch sử tài khoản, thuế, hóa đơn, dòng tiền, IP/thiết bị, người ký giấy tờ, quan hệ chéo giữa các công ty — và xem doanh nghiệp có hoạt động kinh tế thật không. Một công ty khai doanh thu rất lớn nhưng gần như không có nhân viên, khách hàng hay hàng hóa sẽ tạo ra rất nhiều dấu hiệu bất thường.'}
  ]},
 {id:'thanhpho', n:'B', t:'Thành phố ma & bong bóng', d:'Vì sao "xây mà không có người ở" chưa đủ để kết luận, và đâu mới là cụm dấu hiệu thật.',
  blocks:[
   {h:'Đừng nhảy sang kết luận', p:'Bất động sản được FATF đánh giá có rủi ro rửa tiền đáng kể — giá trị lớn, giao dịch phức tạp, dễ dùng pháp nhân trung gian. Nhưng <b>"xây mà không có người ở" có rất nhiều nguyên nhân hoàn toàn hợp pháp</b>: cung vượt cầu, đầu cơ, quy hoạch trước dân số, mua để giữ tài sản, hạ tầng/việc làm chưa hình thành, hoặc chủ đầu tư đã lỡ bỏ vốn quá nhiều nên phải hoàn thiện.'},
   {h:'Cụm dấu hiệu đáng nghi thật sự', p:'Điều đáng chú ý không phải một dấu hiệu đơn lẻ mà là <b>một cụm cùng xuất hiện</b>:',
    a:'DỰ ÁN RẤT LỚN\n     +\nnhu cầu thực rất thấp\n     +\ndòng tiền vẫn liên tục đổ vào\n     +\nnhiều công ty liên quan chéo\n     +\nchủ sở hữu thực khó xác định\n     +\ngiá mua bán / định giá bất thường\n     +\ngiao dịch qua nhiều lớp pháp nhân'},
   {h:'Một thành phố có thể "chết" về xã hội nhưng "sống" về tài chính', p:'Bất động sản không nhất thiết cần có người ở mới có giá trị tài chính. Chừng nào nó còn được định giá và còn được nhận làm tài sản thế chấp, nó vẫn vận hành trong hệ thống tín dụng — kể cả khi không ai bật đèn.'}
  ]},
 {id:'comay', n:'C', t:'Cỗ máy BĐS – ngân hàng', d:'Vòng quay tài sản thế chấp → tín dụng → tài sản, và điều gì xảy ra khi nó chạy ngược.',
  blocks:[
   {h:'Vòng quay bình thường', p:'Bất động sản không đứng riêng. Nó nối với ngân hàng; ngân hàng nối với doanh nghiệp; doanh nghiệp nối với việc làm; việc làm nối lại với thu nhập — và thu nhập quay lại nuôi bất động sản.',
    a:'                        THẾ GIỚI\n       ┌───────────────────┼─────────────────────┐\n       ↓                   ↓                     ↓\n CHÍNH TRỊ/CHIẾN TRANH  THƯƠNG MẠI         USD / LÃI SUẤT\n       ↓                   ↓                     ↓\n dầu/vận tải ↑        xuất khẩu ↓          tỷ giá VND\n       ↓                   ↓                     ↓\n   LẠM PHÁT ↑         doanh thu DN ↓       LÃI SUẤT VN\n       └────────────┬──────┴────────────┬────────┘\n                    ↓                   ↓\n                 THU NHẬP           NGÂN HÀNG\n                    ↓                   │ tín dụng\n              NGƯỜI MUA NHÀ             │\n                    ↓                   ↓\n                 BẤT ĐỘNG SẢN ←─────────┘\n                    ↓\n             GIÁ TÀI SẢN THẾ CHẤP\n                    ↓\n                 NGÂN HÀNG\n                    ↓\n             TÍN DỤNG TOÀN NỀN KINH TẾ\n                    ↓\n             DOANH NGHIỆP / VIỆC LÀM\n                    └──────────→ quay lại THU NHẬP'},
   {h:'Công thức chạy ngược', p:'Hệ thống không "vỡ" chỉ vì giá bất động sản giảm hay lãi suất tăng. Điểm nguy hiểm là khi một cú sốc bên ngoài đánh trúng <b>đúng lúc các mắt xích bên trong đã căng</b>, khiến chúng khuếch đại lẫn nhau.',
    a:'DÒNG TIỀN THỰC ↓\n        +\nKHÔNG ĐẢO/ĐÁO HẠN ĐƯỢC NỢ\n        +\nGIÁ TÀI SẢN THẾ CHẤP ↓\n        +\nNIỀM TIN ↓\n        ↓\n     ĐÒN BẨY\n        ↓\nKHỦNG HOẢNG TỰ KHUẾCH ĐẠI'},
   {h:'Mắt xích đáng sợ nhất: bán cưỡng bức', p:'Quan trọng hơn cả lãi suất. Người bán vì <i>muốn</i> bán thì thị trường chỉ chậm lại. Người bán vì <i>buộc phải</i> bán — do nợ đến hạn, do bị gọi thêm tài sản bảo đảm — mới là thứ kéo giá thứ cấp xuống thật.'}
  ]},
 {id:'nangluong', n:'D', t:'Năng lượng & địa chính trị', d:'Vì sao nền kinh tế không chỉ chạy bằng tiền mà chạy bằng dòng năng lượng và vật chất.',
  blocks:[
   {h:'Thứ tự các dòng', p:'Một nền kinh tế không chỉ có "dòng tiền". Nó có <b>dòng năng lượng → dòng vật chất → dòng hàng hóa → dòng tiền → dòng tín dụng → dòng tài sản → dòng thông tin → dòng niềm tin</b>. Khi một dòng bị tắc, hệ thống thường chịu được; khi nhiều dòng cùng tắc và bắt đầu khuếch đại lẫn nhau, đó mới là lúc rủi ro hệ thống xuất hiện.'},
   {h:'Hai vai trò rất khác nhau', p:'Nga là <b>chân lục địa</b> — đường ống, dầu chiết khấu, không qua biển. Hormuz là <b>cổ chai biển toàn cầu</b> — không sở hữu dầu nhưng kiểm soát đường đi của phần lớn dầu vận chuyển bằng tàu. Nhầm hai thứ này với nhau sẽ dẫn tới đánh giá sai mức độ tác động.'},
   {h:'Bản đồ 5 tầng', p:'Cách gọn nhất để giữ toàn bộ bức tranh trong đầu:',
    a:'1  ĐỊA CHÍNH TRỊ\n        ↓\n2  NĂNG LƯỢNG\n        ↓\n3  CÔNG XƯỞNG TRUNG QUỐC\n        ↓\n4  CHUỖI CÔNG NGHIỆP VIỆT NAM\n        ↓\n5  NGÂN HÀNG – BĐS – KINH TẾ NỘI ĐỊA'}
  ]},
 {id:'nhanthuc', n:'E', t:'Hệ nhận thức & niềm tin', d:'Mắt xích duy nhất không đo được — và là mắt xích điều khiển tất cả những mắt xích đo được.',
  blocks:[
   {h:'Vì sao niềm tin lạ', p:'Tất cả những thứ trước nó đều đo được: dầu → USD/thùng, lãi suất → %, nợ → tỷ đồng, BĐS → đồng/m², GDP → %. Nhưng niềm tin không có một con số duy nhất — trong khi nó quyết định: mua/không mua, gửi/rút, đầu tư/không đầu tư, giữ VND hay vàng hay USD, tuyển dụng hay dừng tuyển.'},
   {h:'Nguyên nhân ≠ kích hoạt', p:'Một luồng thông tin lớn không tự nó làm hệ thống vỡ. Nó là <b>kích hoạt</b>, không phải <b>nguyên nhân</b>. Nguyên nhân nằm ở đòn bẩy, ở nợ đến hạn, ở giá tài sản thế chấp. Nhưng nếu nội dung đụng đúng vào lúc niềm tin kinh tế đang yếu thì một kích hoạt nhỏ vẫn có thể đẩy hệ thống sang trạng thái khác.'},
   {h:'Điều kiện nguy hiểm nhất', p:'Không phải một người lo sợ, cũng không phải mười nghìn người. Mà là <b>hàng triệu người cùng đổi hành vi cùng lúc</b> — vì khi đó cầu, tiền gửi, tiêu dùng và giá tài sản có thể đổi trạng thái đồng thời.'}
  ]},
 {id:'mainboard', n:'F', t:'Mainboard', d:'Toàn bộ bốn hệ ghép lại trong một sơ đồ duy nhất.',
  blocks:[
   {h:'Bốn hệ, một cỗ máy', p:'Thế giới → kinh tế Việt Nam → hệ tài chính → hệ nhận thức, và hệ nhận thức lại đẩy ngược lên hệ tài chính.',
    a:'╔══════════════════════════════════════════════╗\n║                THẾ GIỚI                      ║\n║ Nga ──┐                                      ║\n║       ├→ NĂNG LƯỢNG                          ║\n║ Hormuz┘        ↓                             ║\n║             TRUNG QUỐC ←── MỸ                ║\n║                           thương mại         ║\n╚════════════════╪═════════════════════════════╝\n                 ↓\n╔══════════════════════════════════════════════╗\n║              KINH TẾ VIỆT NAM                ║\n║ nhập nguyên liệu → NHÀ MÁY → XUẤT KHẨU       ║\n║              ↓                               ║\n║        VIỆC LÀM / THU NHẬP                   ║\n╚════════════════╪═════════════════════════════╝\n                 ↓\n╔══════════════════════════════════════════════╗\n║             HỆ TÀI CHÍNH                     ║\n║  NGƯỜI DÂN → NGÂN HÀNG → TÍN DỤNG            ║\n║                    ↓                         ║\n║                BẤT ĐỘNG SẢN                  ║\n║                    ↓                         ║\n║              TÀI SẢN THẾ CHẤP                ║\n║                    ↓                         ║\n║                 NGÂN HÀNG                    ║\n╚════════════════╪═════════════════════════════╝\n                 ↑\n╔══════════════════════════════════════════════╗\n║             HỆ NHẬN THỨC                     ║\n║ mạng xã hội → livestream → hàng triệu người  ║\n║                     ↓                        ║\n║                  NIỀM TIN                    ║\n║                     ↓                        ║\n║              HÀNH VI TÀI CHÍNH               ║\n╚══════════════════════════════════════════════╝'},
   {h:'Câu kết của toàn bộ hồ sơ', p:'<b>Hiện có áp lực thật ở một số mắt xích — nhưng những dữ kiện đó chưa đủ để kết luận một cuộc khủng hoảng hệ thống đang xảy ra.</b> Đó chính là lý do cần một bảng đồng hồ thay vì một kết luận.'}
  ]}
];

window.DQT_DATA = { IC: IC, svg: svg, THEATERS: THEATERS, GAUGES: GAUGES,
  CHAIN: CHAIN, LEVELS: LEVELS, SCEN: SCEN, LIB: LIB };
})();
