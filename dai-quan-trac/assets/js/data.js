(function () {
"use strict";

/* ============================================================
   ĐÀI QUAN TRẮC — dữ liệu đã phân loại từ hồ sơ nguồn
   7 cụm chủ đề · 6 chiến trường · 11 đồng hồ · 16 mắt xích
   ============================================================ */

/* ────────────────────────────────────────────────────────────
   QUYẾT ĐỊNH KIẾN TRÚC — đọc trước khi thêm chủ thể thứ hai

   Ghi lại vì đây là loại quyết định mà vài tháng nữa sẽ có người
   đem ra bàn lại từ đầu, không phải vì nó sai mà vì không ai biết
   là đã cân nhắc rồi.

   ① MỘT CUNG = MỘT LĂNG KÍNH, KHÔNG PHẢI MỘT CHỦ THỂ.
   Đó là quy luật sẵn có của repo, không phải luật đặt riêng ở đây:
   Đô Sát Viện chứa 106 dự án L2, Hoàng Thành 16 nền văn hoá, Kinh
   Thành 9 quốc gia — mỗi cung một cách hỏi, nhiều đối tượng.

   Đài Quan Trắc là lăng kính "cú sốc nào, qua ổ cắm nào, ai gánh".
   Hiện chỉ có MỘT chủ thể là Việt Nam. Muốn hỏi đúng câu đó về
   Trung Quốc thì nó vào ĐÂY, không phải cung mới.

   Cung mới là khi ĐỔI LĂNG KÍNH (nhìn Việt Nam qua trục lịch sử,
   pháp luật, nhân khẩu…), không phải khi đổi chủ thể.

   ② VÌ SAO KHÔNG TÁCH APP RIÊNG CHO MỖI NƯỚC
   · Phương pháp dùng chung. TIEUCHI và THANG ở cuối file này cố ý
     KHÔNG nhắc tên nước nào. Tách app là chép đôi chúng, và repo
     này đã bị cắn đúng chỗ đó — xem ghi chú đầu scripts/tuoi-du-lieu.mjs.
   · So sánh mới là chỗ có giá trị. Phát hiện của hồ sơ Vingroup là
     một KHUÔN MẪU (Nhà nước điều khiển qua ổ cắm chứ không qua cổ
     phần). Khuôn mẫu chỉ thành phát hiện khi đặt cạnh nước khác.
     Hai app thì không bao giờ đặt hai bảng chấm cạnh nhau được.

   ③ KHI THÊM CHỦ THỂ, CHIA BA TẦNG — KHÔNG PHẢI HAI
   Đừng gom tất cả vào "VIỆT NAM" rồi dựng "TRUNG QUỐC" song song:

       PHƯƠNG PHÁP   TIEUCHI · THANG · LEVELS
       (dùng chung)  ← đứng TRÊN chỗ chia chủ thể, không nằm trong

       CHỦ THỂ       VIỆT NAM  { THEATERS · CHAIN · GAUGES · SCEN · SOI }
                     TRUNG QUỐC { bộ của riêng nó }

       HỒ SƠ NỀN     LIB — phải rà lại: cụm nào phổ quát, cụm nào riêng VN

   ④ BẪY TÊN GỌI, CHẶN TỪ ĐẦU
   Lúc đó "Trung Quốc" tồn tại hai chỗ với hai nghĩa NGƯỢC CHIỀU:
       chiến trường 'tq' trong bộ của Việt Nam = Trung Quốc làm gì TỚI ta
       chủ thể TRUNG QUỐC                      = cái gì đang xảy ra VỚI họ
   Không đặt tên tách bạch ngay từ lần thêm đầu tiên thì đây là nguồn
   rối lớn nhất, lớn hơn cả chuyện gom mục.

   ⑤ CHỖ SẼ CHẠM TRẦN TRƯỚC, VÀ LỐI THOÁT CÓ SẴN
   File này đã 73 KB và nạp mỗi lần mở trang; thêm một chủ thể đầy
   đủ là khoảng 150 KB. Chưa phải vấn đề, nhưng sẽ đau trước tiên ở
   lần tải đầu trên điện thoại. Lối thoát không phải nghĩ ra: Kinh
   Thành đã tách assets/js/data/ thành nhiều file. Khi tới lúc, tách
   data/vn.js + data/tq.js và chỉ nạp chủ thể đang xem.
   ──────────────────────────────────────────────────────────── */

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
    keypoint:'Đây không còn là kịch bản lý thuyết. EIA ngày 11/8/2026 ước tính dòng dầu qua Hormuz chỉ khoảng <b>4,9 triệu thùng/ngày trong quý II/2026</b>, so với <b>21,6 triệu</b> trước xung đột, và giả định vận chuyển tiếp tục bị hạn chế nghiêm trọng trong tháng 8; EIA dự báo Brent trung bình khoảng <b>85 USD/thùng</b> trong quý III. IEA ngày 12/8 cũng mô tả nguồn cung vùng Vịnh còn thấp hơn nhiều so với trước chiến tranh.<br><br>Việt Nam có một đường nhạy cảm <b>trực tiếp</b> với địa chính trị năng lượng, không chỉ đi vòng qua Trung Quốc. Nghi Sơn — theo Bộ Công Thương cung cấp khoảng 40% nhu cầu xăng dầu trong nước — phải tìm nguồn dầu thô thay thế khi Hormuz gián đoạn.',
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
    mechs:{ h:'Bị Mỹ ép, dòng chảy Trung Quốc đổi hướng — ba loại rất khác nhau', ds:[
      {ma:'A', t:'Chuyển nhà máy sang Việt Nam', tt:'hợp pháp', c:'g',
       d:'Nếu quá trình sản xuất tạo ra giá trị thật tại Việt Nam. Riêng Bắc Ninh, Trung Quốc hiện đứng <b>đầu về số lượng dự án FDI</b> và thứ ba về tổng vốn với trên 11 tỷ USD; nhiều doanh nghiệp tiếp tục khảo sát dự án AI, điện tử, trung tâm dữ liệu.'},
      {ma:'B', t:'Kéo dài chuỗi sang Việt Nam', tt:'hợp pháp', c:'g',
       d:'Nhập linh kiện Trung Quốc rồi sản xuất tại Việt Nam <b>không tự động là gian lận xuất xứ</b>. Nếu đáp ứng quy tắc xuất xứ / substantial transformation thì hoàn toàn hợp lệ. Đây là chỗ dễ đọc sai nhất của cả hồ sơ.'},
      {ma:'C', t:'Chuyển tải, giả xuất xứ', tt:'vi phạm', c:'r',
       d:'Chỉ đổi nhãn hoặc xử lý không đủ rồi khai xuất xứ Việt Nam để né thuế. Tháng 7/2026 quan chức hải quan Mỹ được báo cáo đã kiểm tra đột xuất một số nhà máy tại Việt Nam có liên hệ với Trung Quốc. Nhưng chính báo cáo đó cũng nói <b>không có bằng chứng đáng kể cho thấy chuyển tải bất hợp pháp diễn ra trên diện rộng</b>, và Reuters lưu ý họ chưa tự xác minh được.'}
    ]},
    keypoint:'Tháng 7/2026 xuất khẩu Trung Quốc vẫn tăng <b>23,9%</b> so với cùng kỳ nhờ hàng công nghệ cao và AI, dù nhu cầu nội địa còn yếu. Nghĩa là Mỹ ép Trung Quốc <b>không làm Trung Quốc biến mất</b> — nó làm dòng vốn, nhà máy và hàng hoá <b>đổi tuyến</b>. Và Việt Nam nằm ngay phía nam. Việt Nam vì thế nhận <b>hai mặt của cùng một dòng chảy</b>: FDI, việc làm, công nghệ, hạ tầng khu công nghiệp — đồng thời là cạnh tranh nội địa gay gắt hơn, phụ thuộc đầu vào sâu hơn, và bị Mỹ soi xuất xứ kỹ hơn.',
    clocks:['Nhập khẩu dầu thô (triệu thùng/ngày)','Giá điện & sản lượng than','PMI sản xuất','Giá xuất xưởng (PPI)','Giá hàng trung gian xuất sang VN','FDI Trung Quốc đăng ký vào Việt Nam','Tần suất Mỹ kiểm tra nhà máy có liên hệ Trung Quốc'],
    hits:['Là tầng truyền dẫn số 2 tới Việt Nam — qua giá đầu vào công nghiệp','Nguồn dịch chuyển nhà máy và FDI — mặt được của dòng chảy','Đối thủ cạnh tranh ngay tại thị trường nội địa Việt Nam, kể cả bán thẳng qua sàn','Kéo theo rủi ro xuất xứ mà phía Mỹ đang soi'],
    scen:'Trung tâm của cả kịch bản A lẫn B'
  },
  {
    id:'vn', ic:'star', flag:'🇻🇳', name:'Việt Nam', short:'Việt Nam',
    role:'Giao điểm — nơi nhiều cú sốc khác nguồn hội tụ',
    acc:'#d4a72c',
    query:'Vietnam economy exports credit growth real estate bond interest rate exchange rate',
    lede:'Cách nói đúng không phải "tất cả đang cùng đánh Việt Nam", mà là: <b>Việt Nam nằm đúng giao điểm của nhiều hệ thống, nên một số cú sốc khác nguồn có khả năng cùng hội tụ tại đây.</b>',
    layersH:'Bốn tầng truyền dẫn — hai từ đầu vào, một từ đầu ra, một từ bên trong',
    layers:[
      {n:'Tầng truyền dẫn 1',t:'Trực tiếp qua giá năng lượng toàn cầu',d:'Hormuz/Trung Đông sốc → giá dầu thế giới ↑ → xăng dầu, logistics, xây dựng, vận tải, sản xuất trong nước ↑. Cộng thêm ràng buộc an ninh xăng dầu nội địa.'},
      {n:'Tầng truyền dẫn 2',t:'Gián tiếp qua Trung Quốc',d:'Nga/Hormuz sốc → chi phí công nghiệp Trung Quốc ↑ → đầu vào sang Việt Nam ↑ → chi phí sản xuất ↑ → bào mòn biên lợi nhuận, hàng Việt bớt cạnh tranh.'},
      {n:'Tầng truyền dẫn 3',t:'Đầu ra qua hàng rào Mỹ',d:'Không chỉ thuế 20%: cộng thêm 12,5% Section 301 lao động, rủi ro 40% nếu bị xác định chuyển tải, AD/CVD theo ngành, và một cuộc điều tra Section 301 về sở hữu trí tuệ chưa có kết quả. Chi phí tuân thủ hồ sơ tăng song song với chi phí thuế.'},
      {n:'Tầng truyền dẫn 4',t:'Bên trong qua kênh phân phối',d:'Hai sàn nắm gần 98% thị trường TMĐT lớn, tổng chi phí bán hàng ước tính lên khoảng 33,8% giá trị đơn năm 2026, trong khi hàng Trung Quốc bán thẳng cho người Việt. Người bán nội địa bị kẹp cả giá vốn lẫn phí kênh.'}
    ],
    mechs:{ h:'Bên trong: không phải sụp, mà là sàng lọc', ds:[
      {ma:'≈155.000', t:'Doanh nghiệp rời thị trường', tt:'7 tháng đầu 2026', c:'r',
       d:'87.518 tạm ngừng có thời hạn, 36.618 chờ giải thể, 31.189 đã giải thể.'},
      {ma:'187.173', t:'Doanh nghiệp vào thị trường', tt:'cùng kỳ', c:'g',
       d:'125.923 thành lập mới và 61.250 quay trở lại — <b>nhiều hơn số rời đi</b>. Nên không thể gọi đây là "đóng cửa hàng loạt"; đúng hơn là vừa mở mới rất mạnh vừa đào thải rất mạnh.'},
      {ma:'38,06 tỷ', t:'FDI đăng ký', tt:'7 tháng đầu 2026', c:'g',
       d:'Tăng mạnh so với cùng kỳ. Dòng vốn lớn vẫn đang vào, nhưng doanh nghiệp nhỏ, biên mỏng, phụ thuộc sàn hoặc phụ thuộc nợ có thể bị ép ra ngoài nhanh hơn.'},
      {ma:'+42% · 25,5%', t:'Tín dụng bất động sản', tt:'World Bank, năm 2025', c:'y',
       d:'Tín dụng BĐS tăng 42% trong năm 2025 và chiếm 25,5% tổng dư nợ; hệ thống ngân hàng gặp áp lực nguồn vốn, từng phải cạnh tranh huy động 6–12 tháng ở khoảng 6–8% vào tháng 3/2026.'},
      {ma:'−3% / −6%', t:'Giá căn hộ sơ cấp TP.HCM', tt:'CBRE, 12/8/2026', c:'y',
       d:'Quý II giảm 3% theo quý và 6% theo năm; người mua nhà thận trọng hơn trong môi trường lãi suất cao.'},
      {ma:'−30%', t:'Đề xuất giảm thuế thu nhập', tt:'Chính phủ, 10/8/2026', c:'b',
       d:'Đề xuất giảm 30% thuế thu nhập cho một số doanh nghiệp nhỏ và hộ kinh doanh — cho thấy chính nhóm bị ép biên đang trở thành vấn đề chính sách.'}
    ]},
    clocks:['Lãi suất vay mua nhà','Số lượng giao dịch bất động sản','Tỷ lệ hấp thụ dự án mới','Giá thứ cấp (không phải giá rao bán)','Nợ xấu & xử lý tài sản bảo đảm','Số doanh nghiệp rời so với số vào thị trường','Tỷ trọng tín dụng bất động sản trên tổng dư nợ'],
    danger:'Dấu hiệu đáng ngại nhất không phải "giá rao bán giảm 5%", mà là <b>giao dịch giảm + lãi suất tăng + số người buộc phải bán vì nợ tăng — cùng lúc</b>. Và ở tầng doanh nghiệp, con số cần nhìn không phải "155.000 rời đi" đứng một mình, mà là <b>tỷ lệ giữa số rời và số vào</b> — hiện số vào vẫn nhiều hơn.',
    hits:['Bị đánh trực tiếp qua nhiên liệu và CPI','Bị đánh gián tiếp qua đầu vào từ Trung Quốc','Bị siết ở đầu ra qua thuế, xuất xứ và sở hữu trí tuệ của Mỹ','Bị ép biên ngay trong nước qua phí sàn và hàng Trung Quốc bán trực tiếp','Bị khuếch đại từ bên trong qua ngân hàng – BĐS – niềm tin'],
    scen:'Điểm hạ lưu của cả ba kịch bản'
  },
  {
    id:'my', ic:'eagle', flag:'🦅', name:'Hoa Kỳ', short:'Hoa Kỳ',
    role:'Phía đầu ra — không chỉ thuế, mà nhiều cơ chế pháp lý song song',
    acc:'#58a6ff',
    query:'USTR Vietnam Section 301 tariff Special 301 intellectual property transshipment origin',
    lede:'Ba chiến trường kia đánh vào <b>đầu vào</b> của Việt Nam. Mỹ đánh vào <b>đầu ra</b>. Nhưng cách nói "Mỹ áp thuế 20%" là chưa đủ: Việt Nam đang cùng lúc nằm trong <b>nhiều cơ chế thương mại – sở hữu trí tuệ – lao động – xuất xứ</b> khác nhau, mỗi cơ chế có luật riêng, mốc thời gian riêng và có thể cộng dồn.',
    mech:['nhu cầu tiêu dùng Mỹ ↓ → đơn hàng xuất khẩu VN ↓','thuế quan cộng dồn ↑ → biên lợi nhuận nhà máy VN ↓','kiểm tra xuất xứ chặt hơn → chi phí tuân thủ và rủi ro hồ sơ ↑','lãi suất USD ↑ → áp lực tỷ giá VND','tỷ giá căng → lãi suất VN khó giảm'],
    ascii:'MỘT MẶT HÀNG KHÔNG ĐƯỢC MIỄN,\nTHUỘC CẢ HAI CƠ CHẾ:\n\n  Thuế đối ứng            +20%\n  Section 301 lao động  +12,5%\n                        ───────\n  THUẾ BỔ SUNG          +32,5%\n\nCHƯA TÍNH: thuế MFN thông thường ·\nAD/CVD nếu mặt hàng bị áp ·\nSection 232 nếu thuộc ngành liên quan',
    mechs:{ h:'Các cơ chế Mỹ đang áp hoặc đang mở với Việt Nam', ds:[
      {ma:'20%', t:'Thuế đối ứng', tt:'đang áp', c:'r',
       d:'USTR xác nhận Mỹ duy trì thuế đối ứng 20% với hàng có xuất xứ Việt Nam, theo khung thoả thuận thương mại; một số danh mục thuộc diện miễn hoặc được điều chỉnh.'},
      {ma:'+12,5%', t:'Section 301 — lao động cưỡng bức', tt:'đang áp từ 24/7/2026', c:'r',
       d:'Federal Register ghi đích danh Việt Nam ở mức 12,5%, trong cuộc điều tra về việc các nền kinh tế không có hoặc không thực thi hiệu quả lệnh cấm nhập hàng sản xuất bằng lao động cưỡng bức. Quy định Mỹ nói khoản này <b>có thể cộng với các khoản bổ sung khác trong Chapter 99</b>. Đây <b>không phải</b> kết luận rằng toàn bộ hàng Việt được làm bằng lao động cưỡng bức.'},
      {ma:'PFC', t:'Special 301 — sở hữu trí tuệ', tt:'xếp loại', c:'y',
       d:'Báo cáo Special 301 2026 xếp Việt Nam vào <b>Priority Foreign Country</b> — mức nghiêm trọng nhất, và là nước duy nhất ở nhóm này trong báo cáo 2026; USTR nói đây là lần đầu sau 13 năm họ dùng tới nhóm đó. Năm nhóm quan ngại: vi phạm bản quyền trực tuyến, hàng giả, thực thi tại biên giới, phần mềm không phép, và xâm phạm tín hiệu truyền hình.'},
      {ma:'?', t:'Section 301 — điều tra IP riêng', tt:'đang điều tra', c:'y',
       d:'Ngày 29/5/2026 USTR mở điều tra Section 301 về bảo vệ và thực thi sở hữu trí tuệ của Việt Nam. Thời hạn thông thường để ra xác định là sáu tháng kể từ khi mở, có thể gia hạn thêm ba tháng. <b>Chưa có quyết định cuối cùng</b> — đây là quả chưa nổ, không phải khoản thuế đang tồn tại.'},
      {ma:'40%', t:'Chuyển tải né thuế', tt:'áp khi bị xác định', c:'y',
       d:'Executive Order 14326: hàng bị CBP xác định là <i>transshipped to evade duties</i> chịu mức bổ sung 40% thay cho thuế đối ứng thông thường, cùng các chế tài khác. Điều kiện là <b>bị xác định lách xuất xứ</b>, không phải cứ dùng nguyên liệu Trung Quốc.'},
      {ma:'AD/CVD', t:'Biện pháp theo từng ngành', tt:'đang áp với một số ngành', c:'y',
       d:'Ngoài thuế cấp quốc gia còn có biện pháp theo ngành. Rõ nhất là pin mặt trời: Bộ Thương mại Mỹ và USITC đã có kết luận với solar cells/modules từ Việt Nam, dẫn tới lệnh chống bán phá giá / chống trợ cấp. Vì vậy cấu trúc thuế của hai doanh nghiệp có thể rất khác nhau.'},
      {ma:'—', t:'Danh sách theo dõi tiền tệ', tt:'giám sát, không phải trừng phạt', c:'b',
       d:'Ngày 23/7/2026 Bộ Tài chính Mỹ vẫn để Việt Nam trong Monitoring List cùng Trung Quốc, Nhật, Hàn, Đài Loan, Thái Lan, Singapore và vài nền kinh tế châu Âu. Nhưng <b>Mỹ không kết luận Việt Nam thao túng tiền tệ</b>. Đây là giám sát, không phải một lệnh trừng phạt.'},
      {ma:'NTE', t:'Các "ổ cắm" ngoài hàng hoá', tt:'đang đàm phán', c:'b',
       d:'Báo cáo NTE 2026 cho thấy Washington còn gây sức ép ở thương mại số, dữ liệu xuyên biên giới, an ninh mạng, dịch vụ tài chính và thanh toán, mua sắm công, sở hữu nước ngoài, doanh nghiệp nhà nước, lao động, môi trường và hải quan. Nói cách khác: Mỹ không chỉ đánh vào <b>giá hàng hoá</b>, mà muốn đổi một phần <b>luật chơi phía sau</b> hàng hoá.'}
    ]},
    keypoint:'Vì sao Việt Nam vào tầm ngắm mạnh đến vậy, một con số giải thích phần lớn: năm 2025 Mỹ xuất sang Việt Nam <b>15,7 tỷ USD</b> nhưng nhập từ Việt Nam <b>193,8 tỷ USD</b> — thâm hụt <b>178,2 tỷ USD</b>, và theo chính USTR con số này tăng <b>44,3%</b> so với 2024. Ở góc nhìn chính sách tái cân bằng thương mại, Việt Nam trở thành đối tượng rất tự nhiên.',
    danger:'Đọc cho đúng: <b>xếp loại PFC là kết luận hành chính của USTR về mức độ thực thi</b>, không phải một phán quyết đạo đức về người Việt. Và mức 12,5% dựa trên cơ chế kiểm soát nhập khẩu hàng có lao động cưỡng bức, <b>không</b> phải kết luận rằng hàng Việt nói chung được sản xuất bằng lao động cưỡng bức. Con số 32,5% cũng là <b>điểm phần trăm thuế bổ sung</b> cho một mặt hàng thuộc cả hai diện, không phải tổng thuế mà mọi hàng Việt đều đóng — mã HS và các diện miễn quyết định mức thực tế.',
    clocks:['Kết quả điều tra Section 301 về sở hữu trí tuệ','Danh mục được miễn / không miễn của từng cơ chế','Tần suất CBP kiểm tra xuất xứ hàng từ Việt Nam','Các vụ AD/CVD mới theo ngành','Lãi suất điều hành của Fed và tỷ giá USD/VND','Kim ngạch xuất khẩu VN sang Mỹ và thâm hụt song phương'],
    hits:['Đầu ra: thuế cộng dồn làm giá hàng vào Mỹ đắt lên','Hồ sơ: xuất xứ, sở hữu trí tuệ, lao động — chi phí tuân thủ chứ không chỉ chi phí thuế','Tài chính: USD, tỷ giá, mặt bằng lãi suất','Thể chế: các đòi hỏi về dữ liệu, thanh toán, mua sắm công, DNNN'],
    scen:'Biến số nằm ngoài trục năng lượng — có thể cộng hưởng với A hoặc B'
  },
  {
    id:'san', ic:'flow', flag:'🛒', name:'Sàn thương mại điện tử', short:'Sàn TMĐT',
    role:'Kênh phân phối nội địa — nơi biên lợi nhuận bị ép từ bên trong',
    acc:'#a371f7',
    query:'Shopee TikTok Shop Vietnam seller fees commission market share e-commerce growth',
    lede:'Bốn chiến trường trên đều ở <b>ngoài biên giới</b>. Đường này nằm hẳn <b>bên trong</b> Việt Nam, và nó ép đúng chỗ mà thuế quan không với tới: người bán nội địa. Hai nền tảng hiện nắm gần như toàn bộ thương mại điện tử lớn, nên mức phí họ đặt ra không còn là chuyện thương lượng của từng shop.',
    mech:['sàn tăng phí → chi phí bán hàng của người bán ↑','hàng Trung Quốc bán thẳng qua sàn → áp lực giảm giá ↑','giá vốn nhập từ Trung Quốc + phí sàn cùng tăng → biên lợi nhuận ↓','shop nhỏ biên mỏng rời thị trường → sàng lọc doanh nghiệp nội địa'],
    ascii:'TỔNG CHI PHÍ SÀN / GIÁ TRỊ ĐƠN\n(ước tính SHS, dẫn lại qua VietnamFinance)\n\n  2022   ~ 8%\n  2023   ~13%\n  2024   ~18%\n  2026   ~33,8%  (ước tính)\n\n\nMỘT ĐƠN HÀNG 100 CÓ THỂ THÀNH:\n\n  giá vốn            60\n  phí sàn            25\n  quảng cáo/vận hành 10\n                    ────\n  CÒN                 5\n\nchỉ cần thêm hoàn hàng, giảm giá,\nnhân công, hàng hư:   5 → 0 → ÂM',
    mechs:{ h:'Chi phí đến từ đâu — và cái nào không phải thuế', ds:[
      {ma:'6% + hoa hồng', t:'TikTok Shop', tt:'phí nền tảng', c:'y',
       d:'Thu 6% phí giao dịch, cộng hoa hồng nền tảng tuỳ ngành hàng, cộng 3.000 đồng phí xử lý mỗi đơn thành công. Biểu phí giữa 2026 cho thấy nhiều ngành có hoa hồng Marketplace khoảng 10–15%, Mall có ngành lên tới 17,1%; affiliate và chương trình vận chuyển có thể cộng thêm.'},
      {ma:'6% + phí ngành', t:'Shopee', tt:'phí nền tảng', c:'y',
       d:'Phí xử lý giao dịch 6% cộng phí cố định theo ngành; một số nhóm tiêu dùng, sức khoẻ, làm đẹp ở khoảng 10–17%. Ngoài ra còn Voucher Xtra, các chương trình đồng tài trợ mã giảm giá và duy trì hiển thị.'},
      {ma:'≈33,8%', t:'Tổng chi phí bán hàng', tt:'ước tính 2026', c:'r',
       d:'Ước tính SHS tách ra khoảng 16% hoa hồng, 9% freeship/voucher/gói dịch vụ, 6% xử lý giao dịch và 1% duy trì hiển thị. Một shop biên lợi nhuận hàng hoá vốn chỉ 15–20% hoàn toàn có thể rơi vào cảnh <b>bán càng nhiều càng khó có lãi</b>.'},
      {ma:'≠', t:'Thuế nhà nước là lớp khác', tt:'đừng gộp vào 33,8%', c:'b',
       d:'Từ 2025, sàn có chức năng thanh toán phải khấu trừ / kê khai / nộp thay một số nghĩa vụ thuế của hộ và cá nhân bán hàng; quy định 2026 tiếp tục hoàn thiện cơ chế này. Đây <b>không</b> nằm trong con số phí sàn ở trên — gộp hai thứ lại rồi gọi là "thuế sàn 30%" là sai.'}
    ]},
    keypoint:'Nửa đầu 2026 Shopee chiếm khoảng <b>54,5%</b> và TikTok Shop <b>43,4%</b> — hai nền tảng cộng lại gần <b>98%</b> thị trường TMĐT lớn được thống kê. Cùng lúc, tốc độ tăng trưởng TMĐT đã chậm lại và người tiêu dùng nhạy cảm hơn về giá. Khi kênh phân phối tập trung tới mức đó, mức phí không còn là điều kiện thương mại — nó gần với <b>một mức thuế tư nhân</b> lên toàn bộ người bán.',
    danger:'Đọc cho đúng: đây là <b>phí sàn cộng chi phí bán hàng</b>, <b>không phải "thuế Shopee 30%"</b>. Nó gồm hoa hồng, thanh toán, voucher, affiliate, quảng cáo, logistics và hoàn hàng — phần lớn là <b>tuỳ chọn theo mức độ tham gia</b>, không phải khoản bắt buộc đồng loạt. Con số 33,8% là ước tính của một báo cáo, không phải biểu phí chính thức.',
    clocks:['Biểu phí công bố của Shopee và TikTok Shop','Thị phần giữa các sàn','Tốc độ tăng trưởng TMĐT và giá trị đơn trung bình','Tỷ lệ hoàn hàng','Số shop nội địa rời sàn','Doanh số của thương hiệu Trung Quốc bán trực tiếp cho người Việt'],
    hits:['Ép biên lợi nhuận người bán Việt ngay tại thị trường nội địa','Cộng hưởng với giá vốn nhập từ Trung Quốc — bị kẹp cả hai đầu','Là một trong những đường dẫn tới làn sàng lọc doanh nghiệp nhỏ'],
    scen:'Không thuộc trục năng lượng — là bộ ép biên nội địa, chạy song song mọi kịch bản'
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
  {id:'xuatxu',    t:'Xuất xứ & SHTT', d:'Kiểm tra xuất xứ, kết quả điều tra Section 301 về sở hữu trí tuệ, các diện miễn thuế còn hay mất.'},
  {id:'san',       t:'Kênh sàn',     d:'Biểu phí Shopee/TikTok Shop, thị phần, tỷ lệ hoàn hàng, tổng chi phí bán hàng trên giá trị đơn.'},
  {id:'doanhnghiep', t:'Sức khoẻ doanh nghiệp', d:'Số rời thị trường so với số vào, FDI đăng ký, tỷ lệ doanh nghiệp nhỏ thu hẹp.'},
  {id:'niemtin',   t:'Niềm tin',     d:'Biến vô hình điều khiển rất nhiều biến hữu hình. Không có một con số duy nhất.'}
];

/* ---------- MẠCH TRUYỀN DẪN (chương XX) ---------- */
const CHAIN = [
  {id:'hormuz',  t:'Hormuz',              tag:'THƯỢNG NGUỒN', d:'Cổ chai biển toàn cầu. Nghẽn ở đây làm đắt dầu ở mọi nơi cùng lúc.', th:'hormuz'},
  {id:'gia_dau', t:'Giá dầu',             tag:'NĂNG LƯỢNG',   d:'Biến số đầu tiên có thể đo được bằng một con số duy nhất: USD/thùng.'},
  {id:'tq',      t:'Trung Quốc',          tag:'CÔNG XƯỞNG',   d:'Bộ chuyển hóa. Hấp thụ cú sốc bằng 4 bộ đệm rồi truyền phần còn lại xuống hạ lưu.', th:'tq'},
  {id:'dauvao',  t:'Giá đầu vào VN',      tag:'CÔNG NGHIỆP',  d:'Việt Nam nhập chủ yếu là tư liệu sản xuất, Trung Quốc là nguồn lớn nhất.'},
  {id:'cpi',     t:'CPI Việt Nam',        tag:'GIÁ CẢ',       d:'Nơi cú sốc bên ngoài chạm vào ví của người dân lần đầu tiên.'},
  {id:'hangrao', t:'Hàng rào Mỹ',         tag:'ĐẦU RA',       d:'Không phải một mức thuế mà nhiều cơ chế song song: thuế đối ứng, Section 301 lao động, rủi ro chuyển tải, AD/CVD theo ngành, và một cuộc điều tra sở hữu trí tuệ chưa có kết quả.', th:'my'},
  {id:'phisan',  t:'Phí kênh phân phối',  tag:'KÊNH BÁN',     d:'Hai sàn nắm gần 98% thị trường TMĐT lớn. Khi kênh tập trung tới mức đó, mức phí gần với một khoản thuế tư nhân lên người bán.', th:'san'},
  {id:'bienloi', t:'Biên lợi nhuận DN',   tag:'DOANH NGHIỆP', d:'Chỗ mọi đường phía trên gặp nhau: giá vốn tăng từ đầu vào, giá bán bị ép từ đầu ra và từ kênh. Đây là mắt xích bị kẹp hai đầu.'},
  {id:'sangloc', t:'Sàng lọc doanh nghiệp', tag:'ĐÀO THẢI',   d:'Không phải "đóng cửa hàng loạt". Bảy tháng đầu 2026 có khoảng 155.000 doanh nghiệp rời thị trường nhưng 187.173 vào — con số cần nhìn là tỷ lệ giữa hai chiều.'},
  {id:'vieclam', t:'Việc làm & thu nhập', tag:'LAO ĐỘNG',     d:'Nơi áp lực doanh nghiệp chuyển thành áp lực hộ gia đình — và từ đó chạm tới tiêu dùng, tiền gửi và khả năng trả nợ mua nhà.'},
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
   {h:'Điều kiện nguy hiểm nhất', p:'Không phải một người lo sợ, cũng không phải mười nghìn người. Mà là <b>hàng triệu người cùng đổi hành vi cùng lúc</b> — vì khi đó cầu, tiền gửi, tiêu dùng và giá tài sản có thể đổi trạng thái đồng thời.'},
   {h:'Quy mô đã đo được', p:'Phiên livestream ngày 5/8/2026 có lúc màn hình TikTok hiển thị <b>hơn 2,1 triệu người xem đồng thời</b> — tuy đây chưa phải con số được TikTok chính thức xác nhận như một kỷ lục, và phiên sau đó bị nền tảng khoá. Điều <b>đã xác nhận được</b> không phải tính đúng sai của từng nội dung, mà là <b>khả năng tập trung sự chú ý công chúng ở quy mô cực lớn trong thời gian rất ngắn</b>. Đó mới là biến số hệ thống.',
    a:'MỘT PHÁT NGÔN\n      ↓\n2,1 TRIỆU+ NGƯỜI CÙNG NGHE\n      ↓\nclip cắt lại\n      ↓\nFacebook / TikTok / YouTube\n      ↓\nhàng triệu người khác\n      ↓\nNHẬN THỨC → NIỀM TIN → HÀNH VI'},
   {h:'Truyền thông và tài chính đang nhập vào một đường ống', p:'Có báo cáo cho biết khoảng <b>84.000 tài khoản gửi quà tặng</b> trong phiên đó. Tại thảo luận dự luật chống rửa tiền, một đại biểu Quốc hội đã đặt vấn đề chung rằng các luồng quà tặng livestream có thể bị lợi dụng cho rửa tiền hay không. Đây <b>không phải cáo buộc nhằm vào cá nhân nào</b>; nó cho thấy cơ quan lập pháp bắt đầu nhìn livestream như một <b>hạ tầng dòng tiền mới cần giám sát</b>.',
    a:'TRUYỀN THÔNG NGÀY XƯA\n   chỉ truyền THÔNG TIN\n\nLIVESTREAM HIỆN NAY\n   THÔNG TIN\n   + SỰ CHÚ Ý\n   + QUÀ TẶNG\n   + DÒNG TIỀN\n   + CỘNG ĐỒNG'}
  ]},
 {id:'mainboard', n:'F', t:'Mainboard', d:'Toàn bộ bốn hệ ghép lại trong một sơ đồ duy nhất.',
  blocks:[
   {h:'Bốn hệ, một cỗ máy', p:'Thế giới → kinh tế Việt Nam → hệ tài chính → hệ nhận thức, và hệ nhận thức lại đẩy ngược lên hệ tài chính.',
    a:'╔══════════════════════════════════════════════╗\n║                THẾ GIỚI                      ║\n║ Nga ──┐                                      ║\n║       ├→ NĂNG LƯỢNG                          ║\n║ Hormuz┘        ↓                             ║\n║             TRUNG QUỐC ←── MỸ                ║\n║                           thương mại         ║\n╚════════════════╪═════════════════════════════╝\n                 ↓\n╔══════════════════════════════════════════════╗\n║              KINH TẾ VIỆT NAM                ║\n║ nhập nguyên liệu → NHÀ MÁY → XUẤT KHẨU       ║\n║              ↓                               ║\n║        VIỆC LÀM / THU NHẬP                   ║\n╚════════════════╪═════════════════════════════╝\n                 ↓\n╔══════════════════════════════════════════════╗\n║             HỆ TÀI CHÍNH                     ║\n║  NGƯỜI DÂN → NGÂN HÀNG → TÍN DỤNG            ║\n║                    ↓                         ║\n║                BẤT ĐỘNG SẢN                  ║\n║                    ↓                         ║\n║              TÀI SẢN THẾ CHẤP                ║\n║                    ↓                         ║\n║                 NGÂN HÀNG                    ║\n╚════════════════╪═════════════════════════════╝\n                 ↑\n╔══════════════════════════════════════════════╗\n║             HỆ NHẬN THỨC                     ║\n║ mạng xã hội → livestream → hàng triệu người  ║\n║                     ↓                        ║\n║                  NIỀM TIN                    ║\n║                     ↓                        ║\n║              HÀNH VI TÀI CHÍNH               ║\n╚══════════════════════════════════════════════╝'},
   {h:'Câu kết của toàn bộ hồ sơ', p:'<b>Hiện có áp lực thật ở một số mắt xích — nhưng những dữ kiện đó chưa đủ để kết luận một cuộc khủng hoảng hệ thống đang xảy ra.</b> Đó chính là lý do cần một bảng đồng hồ thay vì một kết luận.'}
  ]},
 {id:'docdung', n:'G', t:'Đọc cho đúng', d:'Mười chỗ rất dễ đọc sai — và câu chính xác thay cho mỗi chỗ.',
  blocks:[
   {h:'Vì sao cụm này tồn tại', p:'Đài quan trắc chỉ có ích khi nó <b>không phóng đại</b>. Mỗi mục dưới đây là một cách nói phổ biến, kèm câu đúng hơn. Cái sai thường không nằm ở số liệu mà ở <b>một chữ</b>: gộp "đang điều tra" với "đang áp", gộp "xếp loại hành chính" với "phán quyết", gộp "phí dịch vụ" với "thuế".'},
   {h:'Về bức tranh tổng thể', p:'<b>Nói sai:</b> "Tất cả đang cùng đánh Việt Nam."<br><b>Nói đúng:</b> không có bằng chứng cho thấy Mỹ, Trung Quốc, Hormuz, Nga–Ukraina, các sàn TMĐT hay một hiện tượng truyền thông nào phối hợp với nhau. Điều đáng chú ý chính là <b>chúng độc lập với nhau nhưng cuối cùng lại cùng truyền áp lực vào một hệ thống</b>. Đó là "hội tụ", không phải "chiến dịch".',
    a:'KHÔNG PHẢI            MÀ LÀ\n\nmột chiến dịch    nhiều dòng áp lực\nphối hợp          độc lập, cùng đổ\n    ↓             về một giao điểm\nVIỆT NAM                ↓\n                  VIỆT NAM'},
   {h:'Về phía Mỹ', p:'<b>Nói sai:</b> "Mỹ áp thuế 20% với hàng Việt."<br><b>Nói đúng:</b> 20% là thuế đối ứng; ngoài ra còn 12,5% Section 301 lao động từ 24/7/2026, và quy định Mỹ nói các khoản này có thể cộng với khoản bổ sung khác trong Chapter 99. Nhưng <b>32,5% là điểm phần trăm thuế bổ sung cho một mặt hàng thuộc cả hai diện</b> — mã HS và các diện miễn quyết định mức thực tế, không phải mọi hàng Việt đều đóng như nhau.<br><br><b>Nói sai:</b> "Mỹ kết luận hàng Việt làm bằng lao động cưỡng bức."<br><b>Nói đúng:</b> cơ sở của hành động là chính sách kiểm soát nhập khẩu hàng có lao động cưỡng bức. Đây không phải kết luận về toàn bộ hàng Việt.<br><br><b>Nói sai:</b> "Mỹ nói người Việt ăn cắp bản quyền."<br><b>Nói đúng:</b> Special 301 là <b>xếp loại trong cơ chế sở hữu trí tuệ của Mỹ</b>, không phải bảng xếp hạng quốc gia và không phải phán quyết về con người. USTR cáo buộc thiếu thực thi hiệu quả ở năm nhóm cụ thể.<br><br><b>Nói sai:</b> "Mỹ đã áp thêm thuế IP lên Việt Nam."<br><b>Nói đúng:</b> cuộc điều tra Section 301 về sở hữu trí tuệ mở ngày 29/5/2026 và <b>chưa có quyết định cuối cùng</b>. Đây là quả chưa nổ.<br><br><b>Nói sai:</b> "Mỹ kết luận Việt Nam thao túng tiền tệ."<br><b>Nói đúng:</b> Việt Nam nằm trong Monitoring List từ 23/7/2026, nhưng <b>Mỹ không kết luận thao túng</b>. Đây là giám sát, không phải trừng phạt.'},
   {h:'Về Trung Quốc và xuất xứ', p:'<b>Nói sai:</b> "Nhập linh kiện Trung Quốc rồi lắp ở Việt Nam là gian lận xuất xứ."<br><b>Nói đúng:</b> nếu quá trình sản xuất đáp ứng quy tắc xuất xứ / substantial transformation thì hoàn toàn hợp pháp. Mức 40% của EO 14326 chỉ áp khi <b>bị CBP xác định là chuyển tải để né thuế</b>.<br><br><b>Nói sai:</b> "Hàng Trung Quốc đội lốt Việt Nam tràn lan."<br><b>Nói đúng:</b> tháng 7/2026 hải quan Mỹ có kiểm tra một số nhà máy tại Việt Nam có liên hệ Trung Quốc, nhưng chính báo cáo đó nói <b>không có bằng chứng đáng kể cho thấy chuyển tải bất hợp pháp trên diện rộng</b>, và Reuters lưu ý chưa tự xác minh được. Rủi ro là thật; "tràn lan" thì chưa có căn cứ.<br><br><b>Nói sai:</b> "Mỹ đánh Trung Quốc nên Trung Quốc suy sụp, Việt Nam giảm theo."<br><b>Nói đúng:</b> tháng 7/2026 xuất khẩu Trung Quốc vẫn tăng 23,9%. Họ <b>đổi tuyến</b> chứ không biến mất — và một phần tuyến mới chạy thẳng vào Việt Nam, vừa là FDI vừa là cạnh tranh.'},
   {h:'Về sàn và về nội địa', p:'<b>Nói sai:</b> "Sàn thu thuế 30%."<br><b>Nói đúng:</b> con số ~33,8% là <b>ước tính tổng chi phí bán hàng</b> của một báo cáo, gồm hoa hồng, thanh toán, voucher, affiliate, quảng cáo, logistics, hoàn hàng — phần lớn tuỳ mức độ tham gia. <b>Thuế nhà nước là một lớp hoàn toàn khác</b>, không nằm trong con số đó.<br><br><b>Nói sai:</b> "155.000 doanh nghiệp chết, kinh tế đang sụp."<br><b>Nói đúng:</b> cùng bảy tháng đó có 125.923 thành lập mới và 61.250 quay lại — <b>vào nhiều hơn ra</b> — và FDI đăng ký đạt 38,06 tỷ USD. Đúng hơn là một giai đoạn <b>sàng lọc</b>: ai yếu bị đào thải nhanh hơn, ai mạnh lớn hơn.',
    a:'KHÔNG PHẢI        MÀ LÀ\n\n  VIỆT NAM      các dòng chảy cũ\n     ↓            bị ép / đổi hướng\n    SỤP                ↓\n                  VIỆT NAM\n                       ↓\n              ĐANG TÁI CẤU TRÚC\n\n        ai yếu  → bị đào thải\n        ai mạnh → lớn hơn\n        vốn ngoại → vào mạnh\n        cạnh tranh → khốc liệt hơn'},
   {h:'Về tầng nhận thức', p:'<b>Nói sai:</b> "Một phiên livestream đang làm suy yếu hệ thống tài chính Việt Nam."<br><b>Nói đúng:</b> hiện chưa có căn cứ cho điều đó. Tầng nhận thức là <b>bộ khuếch đại</b>, không phải nguyên nhân — nó chỉ có ý nghĩa kinh tế nếu nội dung chạm vào ngân hàng, BĐS, tiền gửi, tỷ giá và khiến <b>đủ nhiều người đổi hành vi thật</b>. Xem cụm E.'}
  ]}
];

window.DQT_DATA = { IC: IC, svg: svg, THEATERS: THEATERS, GAUGES: GAUGES,
  CHAIN: CHAIN, LEVELS: LEVELS, SCEN: SCEN,
  LIB: LIB };
})();
