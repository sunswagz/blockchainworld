(function () {
"use strict";

/* ============================================================
   TRUNG QUỐC — dữ liệu nền

   ── ĐIỀU QUAN TRỌNG NHẤT PHẢI ĐỌC TRƯỚC ─────────────────────
   Đây KHÔNG phải bản sao cấu trúc Việt Nam với tên nước khác.
   Hai chủ thể hỏi hai câu khác nhau, nên mạch kết thúc ở hai
   chỗ khác nhau:

     VIỆT NAM   cú sốc ngoài → … → CPI · tỷ giá · việc làm
                (câu hỏi: nền kinh tế chịu được không)

     TRUNG QUỐC cú sốc ngoài → … → CHẾ ĐỘ CÓ SỐNG SÓT KHÔNG
                (câu hỏi: quyền lực có giữ được không)

   Chép nguyên khuôn Việt Nam sang đây là mất đúng phần cốt lõi
   của phân tích: cú sốc kinh tế KHÔNG trực tiếp đe doạ chế độ.
   Nó phải chuyển hoá thành XUNG ĐỘT PHÂN PHỐI TRONG NỘI BỘ
   trước đã. Đó là lý do mạch dưới đây có ba "ổ cứng" mà mạch
   Việt Nam không có: tài khoá · cán bộ · an ninh.

   ── HỆ QUẢ CHO BẢNG ĐỒNG HỒ ─────────────────────────────────
   Sáu trong mười hai đồng hồ ở đây đo QUYỀN LỰC, không đo kinh tế;
   sáu cái còn lại đo TÀI KHOÁ chứ không đo tăng trưởng. Không cái
   nào là GDP hay CPI.
   Đó là chủ ý, không phải thiếu sót: một chế độ có thể nghèo đi
   rất nhiều mà vẫn đứng, và có thể giàu mà vẫn vỡ. GDP là đồng
   hồ tệ nhất để đo chuyện này.
   ============================================================ */

/* ── CHIẾN TRƯỜNG: cú sốc từ ngoài đánh vào ────────────────── */
const THEATERS = [
  {
    id:'nangluong', ic:'ship', flag:'🛢', name:'Năng lượng — Hormuz và Malacca',
    short:'Năng lượng', role:'Phụ thuộc nhập khẩu lớn nhất', acc:'#e5484d',
    query:'China crude oil imports Hormuz Malacca strait energy security',
    lede:'Đây là điểm yếu thật, nhưng <b>không</b> đơn giản như "Hormuz đóng → Trung Quốc hết dầu → sụp". Bắc Kinh đã đa dạng hoá nguồn rất rõ, và một cú sốc ở Hormuz đánh cả Nhật, Hàn, Ấn Độ, châu Âu chứ không chọn riêng Trung Quốc.',
    mech:[
      'GIÁ DẦU THẾ GIỚI ↑ · phí bảo hiểm chiến tranh ↑',
      'chi phí sản xuất của công xưởng ↑',
      'biên lợi nhuận doanh nghiệp ↓',
      'việc làm ↓ · thu nhập ↓ · thu ngân sách ↓'
    ],
    ascii:'VÙNG VỊNH                    NGA\n   ↓                          ↓\nHORMUZ                  đường ống\n   ↓                    cảng Viễn Đông\nẤN ĐỘ DƯƠNG                  ↓\n   ↓                          │\nMALACCA                       │\n   ↓                          │\n   └──────── TRUNG QUỐC ──────┘\n\n     tuyến A (biển)      tuyến B (lục địa)\n     dễ bị chặn         khó chặn hơn',
    keypoint:'Năm 2024 Trung Quốc tiêu thụ khoảng <b>16,3 triệu thùng/ngày</b>, sản xuất nội địa chỉ ~4,3 triệu và nhập khoảng <b>11,1 triệu</b>. Nguồn nhập chia rất rộng: Nga ~20%, Saudi ~14%, Iran ~11%, Iraq ~10%, Oman ~7%, UAE ~6%, Brazil ~6%, Angola ~5%. Ngoài hai tuyến chính còn có <b>Kazakhstan</b> và <b>Myanmar</b> bằng đường ống cộng sản xuất nội địa. UNCTAD đánh giá Hormuz mang khoảng một phần tư thương mại dầu đường biển toàn cầu — nên nghẽn ở đó là cú sốc giá toàn cầu, không phải công tắc tắt riêng Trung Quốc.',
    clocks:['Giá dầu Brent','Tỷ trọng nhập khẩu từ Nga','Lưu lượng qua Hormuz và Malacca','Dự trữ dầu chiến lược'],
    hits:['Chi phí sản xuất toàn bộ công xưởng','Lạm phát nhập khẩu','Biên lợi nhuận doanh nghiệp xuất khẩu'],
    scen:'Kịch bản A — cú sốc đơn lẻ, hệ thống hấp thụ được'
  },
  {
    id:'congnghe', ic:'factory', flag:'💾', name:'Công nghệ — tầng chip và thiết bị',
    short:'Công nghệ', role:'Đòn bẩy chọn lọc nhất', acc:'#a371f7',
    query:'China semiconductor export controls advanced chips lithography EDA',
    lede:'Khác hẳn dầu. Dầu đánh vào <b>toàn bộ</b> nền kinh tế; chip tiên tiến chỉ đánh vào <b>tiền tuyến công nghệ</b> — AI, siêu máy tính, chế tạo cao cấp, một phần hệ thống quân sự. Nên nó rất mạnh về dài hạn nhưng gần như không gây sụp trong ngắn hạn.',
    mech:[
      'chip tiên tiến · EDA · thiết bị quang khắc khó tiếp cận',
      'tiền tuyến AI và bán dẫn chậm lại',
      'năng suất và ngành chiến lược ↓',
      'buộc nội địa hoá — tốn kém nhưng không đứng lại'
    ],
    ascii:'    MỸ            HÀ LAN         NHẬT\n  GPU · EDA      quang khắc    thiết bị\n  IP · một phần   cao cấp      vật liệu\n     thiết bị\n     └──────────────┼─────────────┘\n                    ↓\n              ĐÀI LOAN\n           foundry tiên tiến\n                    ↓\n              HÀN QUỐC\n              HBM · memory\n                    ↓\n              TRUNG QUỐC',
    keypoint:'Chuỗi bán dẫn tiên tiến <b>không nằm trong một quốc gia</b>. Nên một hạn chế đơn lẻ thì Trung Quốc tìm được đường vòng; chỉ khi nhiều tầng bị giới hạn cùng lúc mới tạo nút thắt lâu dài. Đó cũng là lý do Mỹ muốn kiểm soát hiệu quả thì bản thân Mỹ cũng cần Hà Lan, Nhật, Hàn và Đài Loan. Hoa Kỳ (qua <b>BIS</b>) vẫn duy trì kiểm soát với chip điện toán tiên tiến và thiết bị sản xuất bán dẫn, và tiếp tục siết một số quy định trong 2025. Nhưng Trung Quốc vẫn có chip trưởng thành, SMIC, Huawei, thiết bị nội địa và trợ cấp nhà nước.',
    clocks:['Tiến độ nội địa hoá thiết bị','Sản lượng chip trưởng thành','Đầu tư quỹ nhà nước cho bán dẫn'],
    hits:['Năng lực công nghệ dài hạn','Ngành chiến lược và quân sự','Năng suất tổng thể'],
    scen:'Kịch bản A về ngắn hạn, nhưng là đòn dài hạn mạnh nhất bảng'
  },
  {
    id:'thuongmai', ic:'flow', flag:'📦', name:'Thương mại — thị trường Mỹ và EU',
    short:'Thương mại', role:'Van đang bù cho nội địa yếu', acc:'#f0503f',
    query:'China exports United States European Union tariffs trade restrictions',
    lede:'Đây là chỗ nguy hiểm <b>ngay lúc này</b>, vì nó đánh đúng cái van đang gánh phần yếu của trong nước. Nhu cầu nội địa yếu nên xuất khẩu đang là thứ giữ tăng trưởng — và đó chính là chỗ bị siết.',
    mech:[
      'Mỹ 14,7% · EU 14,5% · Hong Kong 8,1% · Việt Nam 4,5% · Nhật 4,3% · Hàn 4,1% · Ấn 3,4% · Nga 3,2%',
      'riêng Mỹ + EU ≈ 29% xuất khẩu hàng hoá',
      'đơn hàng nhà máy ↓',
      'việc làm ↓ · thu nhập hộ gia đình ↓',
      'tiêu dùng ↓ — mà tiêu dùng vốn đã yếu'
    ],
    ascii:'Mỹ một mình\n     ↓\nTrung Quốc chuyển hướng\n     ↓\nASEAN · Mexico · Global South · EU\n\n────────────────────────────────\n\nMỹ + EU + các thị trường lớn\n     ↓\nkhó chuyển hướng hơn NHIỀU\n     ↓\n  ĐÒN BẨY THẬT\n  nằm ở LIÊN MINH,\n  không ở một nước đơn lẻ',
    keypoint:'Xuất khẩu tính bằng USD tháng <b>1–5/2026 tăng 15,5%</b> so với cùng kỳ — tức nó đang thật sự gánh phần nhu cầu nội địa yếu, và đó là lý do siết thương mại đánh trúng hơn người ta tưởng. Đây cũng là chỗ Việt Nam xuất hiện, ở vị trí rất nhạy cảm: nếu đầu ra trực tiếp bị khó thì dòng đi vòng <b>Trung Quốc → FDI/linh kiện → ASEAN → sản phẩm → Mỹ/EU</b> trở thành lối thoát. Vì vậy quy tắc xuất xứ và chống chuyển tải trở thành mắt xích của chính cuộc chiến thương mại. Chỉ khoá "China → US" mà không nhìn "China → nước thứ ba → US" thì hiệu quả giảm hẳn.',
    clocks:['Xuất khẩu tính bằng USD','Tỷ trọng Mỹ + EU','Đơn hàng nhà máy mới','Chuyển tải qua nước thứ ba'],
    hits:['Việc làm công xưởng','Thu ngân sách','Tiêu dùng hộ gia đình'],
    scen:'Kịch bản B — đánh đúng cái van đang bù cho nội địa yếu'
  },
  {
    id:'hanghai', ic:'ship', flag:'⚓', name:'Hàng hải — Malacca và đường biển',
    short:'Hàng hải', role:'Động mạch của công xưởng', acc:'#58a6ff',
    query:'Malacca strait shipping chokepoint China maritime logistics insurance',
    lede:'Hormuz chỉ là cửa ra của Vùng Vịnh; sau đó phần lớn hàng còn phải đi tiếp sang Đông Á. Và thứ quan trọng hơn dầu là <b>container, nguyên liệu, linh kiện, LNG và hàng xuất khẩu</b> — tất cả đều dùng cùng hệ logistics biển.',
    mech:[
      'tàu biển = động mạch · cảng = van · bảo hiểm và tài chính vận tải = máu',
      'gián đoạn vật lý ở chokepoint = tình huống chiến tranh quy mô lớn',
      'thiệt hại toàn cầu, không phải công cụ chọn lọc'
    ],
    ascii:'VÙNG VỊNH\n    ↓\n HORMUZ\n    ↓\nẤN ĐỘ DƯƠNG\n    ↓\n MALACCA          ← cổ chai thứ hai\n    ↓\nBIỂN ĐÔNG\n    ↓\nTRUNG QUỐC',
    keypoint:'Đây là điểm dễ bị bỏ sót vì người ta chỉ nghĩ tới dầu. Nhưng một gián đoạn vật lý ở các chokepoint này là <b>tình huống chiến tranh quy mô lớn</b> gây thiệt hại toàn cầu — không phải một công cụ có thể dùng chọn lọc chỉ để tác động Trung Quốc.',
    clocks:['Cước container','Phí bảo hiểm chiến tranh','Lưu lượng qua Malacca'],
    hits:['Toàn bộ chuỗi xuất nhập khẩu','Chi phí nguyên liệu và linh kiện'],
    scen:'Kịch bản A — khuếch đại mọi cú sốc khác, không tự là cú sốc'
  },
  {
    id:'nga', ic:'map', flag:'🐻', name:'Nga — đường vòng chiến lược',
    short:'Nga', role:'Vùng đệm, không phải đồng minh thường', acc:'#d29922',
    query:'Russia China crude oil pipeline energy trade strategic partnership',
    lede:'Đây là chỗ Nga–Ukraina nối vào câu chuyện Trung Quốc, và nó ngược với trực giác: Nga <b>không</b> chủ yếu là đối tác ngoại giao — nó là <b>đường vòng làm giảm phụ thuộc vào tuyến biển phía Nam</b>.',
    mech:[
      'Nga là nguồn dầu thô lớn nhất của Trung Quốc năm 2024 (~20%)',
      'dầu, khí, khoáng sản đi bằng đường ống và cảng Viễn Đông',
      'nếu Trung Đông bất ổn → Nga là vùng đệm',
      'nếu phương Tây siết thương mại → Nga là thị trường và hậu phương lục địa'
    ],
    ascii:'         NGA\n          │\n  ┌───────┼───────┐\n dầu    khí   khoáng sản\n  └───────┼───────┘\n          ↓\n     TRUNG QUỐC\n          ↓\n  giảm phụ thuộc vào\n  tuyến biển phía Nam',
    keypoint:'Hệ quả cho mô hình sức ép: <b>Nga yếu đi ĐỒNG THỜI với một khủng hoảng năng lượng Trung Đông</b> nguy hiểm cho Trung Quốc hơn rất nhiều so với từng sự kiện riêng lẻ. Còn Biển Đen thì không phải socket trực tiếp mạnh — nó là <b>bộ khuếch đại</b> qua giá hàng hoá thế giới, không phải tim của Trung Quốc.',
    clocks:['Tỷ trọng dầu Nga trong nhập khẩu','Công suất đường ống và cảng Viễn Đông'],
    hits:['Khả năng chịu cú sốc Hormuz','Đòn bẩy đàm phán năng lượng'],
    scen:'KHÔNG phải mắt xích chịu đòn — là đường vòng làm giảm hiệu lực đòn đánh'
  },
  {
    id:'taichinh', ic:'gauge', flag:'💵', name:'Tài chính quốc tế — đô la và thanh toán',
    short:'Tài chính', role:'Đòn bẩy mạnh, nhưng có đệm lớn', acc:'#2ea043',
    query:'China foreign exchange reserves capital controls RMB settlement CIPS',
    lede:'Đòn bẩy cực mạnh nhưng cực kỳ nguy hiểm cho <b>cả hai phía</b>. Và Trung Quốc không giống một nước nhỏ dễ bị khủng hoảng ngoại hối.',
    mech:[
      'xuất khẩu → USD/EUR/JPY → ngân hàng → nhập dầu, chip, nguyên liệu',
      'nhưng có kiểm soát vốn, ngân hàng nhà nước, thanh toán bằng NDT, CIPS',
      'cộng dự trữ và thặng dư thương mại → khả năng chống sốc lớn'
    ],
    ascii:'sức ép tài chính     ██████████  8/10\nsụp đổ tức thì       ███░░░░░░░  3/10\n\n→ mạnh, nhưng có đệm dày',
    keypoint:'Cuối tháng 6/2026, dự trữ ngoại hối chính thức khoảng <b>3.416 tỷ USD</b>. Cộng với kiểm soát vốn và hệ ngân hàng quốc doanh, khả năng chống sốc khá lớn. Cú sốc tài chính chỉ thật sự đổi tính chất nếu xảy ra <b>đồng thời</b> với xuất khẩu giảm mạnh, bất động sản, ngân hàng và dòng vốn.',
    clocks:['Dự trữ ngoại hối','Áp lực tỷ giá NDT','Dòng vốn ra'],
    hits:['Khả năng nhập khẩu chiến lược','Chi phí vốn quốc tế'],
    scen:'Kịch bản C — mạnh nhưng có đệm dày, chỉ đổi tính chất khi cộng dồn'
  }
];

/* ── MẠCH TRUYỀN DẪN ────────────────────────────────────────
   Khác Việt Nam ở nửa dưới. Ba mắt xích 'ổ cứng' và một mắt
   xích 'meta' là phần Việt Nam không có, vì câu hỏi cuối của
   Việt Nam là kinh tế còn của Trung Quốc là quyền lực. */
const CHAIN = [
  {id:'nangluong', vi:'TRUYỀN CHẬM. Nhập ~11,1 triệu thùng/ngày trên tổng tiêu thụ ~16,3 nên phụ thuộc là thật, nhưng nguồn đã rải: Nga ~20%, Saudi ~14%, Iran ~11%, Iraq ~10%, cộng Kazakhstan, Myanmar và ~4,3 triệu thùng nội địa. Và cú sốc Hormuz đánh cả Nhật, Hàn, Ấn, châu Âu — nó không chọn riêng Trung Quốc, nên hiệu ứng tương đối nhỏ hơn hiệu ứng tuyệt đối.', t:'Năng lượng', tag:'SOCKET NGOÀI', th:'nangluong',
   d:'Nhập ~11,1 triệu thùng/ngày. Điểm yếu thật, nhưng nguồn đã đa dạng và cú sốc đánh cả thế giới.'},
  {id:'congnghe', vi:'TRUYỀN CHẬM NHƯNG SÂU. Khác dầu ở chỗ nó không đánh vào sản lượng hôm nay mà vào BIÊN NGHIÊN CỨU của mười năm tới: AI, siêu máy tính, sản xuất tiên tiến. Trung Quốc còn mature-node, SMIC, Huawei, thiết bị nội địa và trợ cấp, nên cấm vận làm chậm và làm đắt chứ không làm dừng. Một tầng bị chặn thì tìm được đường vòng; phải chip + phần mềm + thiết bị chặn ĐỒNG THỜI mới thành nút thắt.', t:'Công nghệ', tag:'SOCKET NGOÀI', th:'congnghe',
   d:'Chip tiên tiến, EDA, thiết bị. Đòn bẩy chọn lọc nhất — mạnh dài hạn, yếu ngắn hạn.'},
  {id:'thuongmai', vi:'TRUYỀN NHANH NHẤT trong bốn ổ ngoài, vì nó chạm thẳng vào đơn hàng. Mỹ 14,7% + EU 14,5% ≈ 29% xuất khẩu hàng hoá. Một nước siết thì chuyển hướng ASEAN, Mexico, Global South; nhiều thị trường lớn cùng siết thì khó chuyển hẳn — đó là chỗ liên minh có đòn bẩy mà một nước không có.', t:'Thương mại', tag:'SOCKET NGOÀI', th:'thuongmai',
   d:'Mỹ + EU ≈ 29% xuất khẩu. Đánh đúng cái van đang bù cho nội địa yếu.'},
  {id:'hanghai', vi:'HAY BỊ BỎ SÓT. Hormuz mới là cửa ra của Vùng Vịnh; phần lớn hàng còn phải qua Malacca. Nhưng thứ đi qua đó không chỉ là dầu — container, nguyên liệu, linh kiện, LNG và hàng xuất khẩu đều dùng cùng hệ logistics biển. Tàu là động mạch, cảng là van, bảo hiểm và tài chính vận tải là máu. Gián đoạn vật lý ở đây là tình huống chiến tranh lớn, gây thiệt hại toàn cầu — không phải công cụ chọn lọc.', t:'Hàng hải', tag:'SOCKET NGOÀI', th:'hanghai',
   d:'Malacca và hệ logistics biển. Container quan trọng hơn dầu.'},
  {id:'nga', vi:'HẤP THỤ, không truyền. Đây là lý do Nga có giá trị chiến lược với Trung Quốc lớn hơn giá trị thương mại: nó là ĐƯỜNG BYPASS cho tuyến biển phía Nam. Trung Đông bất ổn thì Nga là bộ đệm; phương Tây siết thương mại thì Nga là thị trường, nguyên liệu và hậu phương lục địa. Vì vậy điều nguy hiểm không phải Nga mạnh mà là <b>Nga yếu ĐỒNG THỜI với khủng hoảng Trung Đông</b>.', t:'Nga', tag:'ĐƯỜNG VÒNG', th:'nga',
   d:'Không phải mắt xích chịu đòn — là vùng đệm làm giảm hiệu lực của đòn đánh vào tuyến biển.'},

  {id:'loinhuan', vi:'ĐIỂM GHÉP. Đây là chỗ ba ổ ngoài cộng lại: chi phí năng lượng ↑ và biên nghiên cứu chậm và đơn hàng ↓ đều đổ vào cùng một dòng lợi nhuận. Từng cú một thì doanh nghiệp chịu được; ba cú cùng lúc thì bắt đầu cắt.', t:'Lợi nhuận doanh nghiệp', tag:'KINH TẾ',
   d:'Chi phí năng lượng ↑ và đơn hàng ↓ gặp nhau ở đây. Đây là chỗ ba cú sốc ngoài cộng dồn.'},
  {id:'vieclam', vi:'TRUYỀN TỪ BẢNG CÂN ĐỐI SANG ĐỜI SỐNG. Lợi nhuận ↓ → tuyển ít, cắt giảm. Mắt xích này quan trọng vì nó là chỗ một con số kế toán biến thành một vấn đề xã hội, và xã hội mới là thứ tạo khối lượng việc cho ổ cứng thứ ba.', t:'Việc làm', tag:'KINH TẾ',
   d:'Lợi nhuận ↓ → tuyển ít, cắt giảm. Mắt xích chuyển từ bảng cân đối sang đời sống.'},
  {id:'tieudung', vi:'VÒNG NGƯỢC. Việc làm ↓ và tài sản ↓ thì tiêu dùng ↓, mà tiêu dùng yếu lại buộc nền kinh tế dựa nhiều hơn vào xuất khẩu — tức dựa nhiều hơn vào đúng cái van đang bị siết. IMF và World Bank đều nhấn mạnh vòng này: xuất khẩu 1–5/2026 tăng 15,5% chính là đang gánh phần nhu cầu nội địa yếu.', t:'Tiêu dùng', tag:'KINH TẾ',
   d:'Nhu cầu nội địa vốn đã yếu vì bất động sản và niềm tin. Nên nền kinh tế phải dựa nhiều vào xuất khẩu — và vòng lặp khép lại.'},

  {id:'bds', vi:'CỬA VÀO BÊN TRONG. Đây là chỗ cú sốc ngoài gặp điểm yếu trong, và nó nguy hiểm hơn Hormuz về mặt cấu trúc vì nó là vòng phản hồi NỘI SINH: nhà đất ↓ → chủ đầu tư ↓ → đất bán ↓ → thu địa phương ↓ → LGFV căng → rủi ro ngân hàng ↑ → tín dụng ↓ → kinh tế ↓ → nhà đất ↓. Đầu tư phát triển bất động sản 2025 giảm 17,2%.', t:'Bất động sản', tag:'TÀI SẢN',
   d:'Cửa vào bên trong. Đầu tư phát triển BĐS năm 2025 giảm 17,2%. Đây là chỗ cú sốc ngoài gặp điểm yếu trong.'},
  {id:'lgfv', vi:'MẮT XÍCH NỐI TÀI SẢN VỚI CHÍNH QUYỀN. Nợ ẩn ~14,3 nghìn tỷ NDT ước tính năm 2023 phần lớn nằm ở đây. Đây cũng là bậc thang nơi lỗ bắt đầu rời khỏi khu vực doanh nghiệp và bước vào khu vực nhà nước — sau bậc này thì mọi tổn thất đều là bài toán chính trị.', t:'LGFV & chính quyền địa phương', tag:'TÀI SẢN',
   d:'Nhà đất ↓ → bán đất ↓ → thu ngân sách địa phương ↓ → LGFV căng. "Nợ ẩn" ước ~14,3 nghìn tỷ NDT năm 2023.',
   vi:'Nợ ẩn ~14,3 nghìn tỷ NDT (ước tính 2023) phần lớn nằm ở đây. Chi phí vay và kỳ hạn là hai thứ cho biết chương trình hoán đổi nợ đang mua được bao nhiêu thời gian.'},
  {id:'nganhang', vi:'VỪA LÀ ĐIỂM YẾU VỪA LÀ BỘ GIẢM XÓC. Nền kinh tế thông thường: nợ xấu → ngân hàng lỗ → phá sản. Ở đây: nợ xấu → ngân hàng quốc doanh → gia hạn → cứu trợ địa phương → thanh khoản trung ương → tái cấu trúc. Nó MUA THỜI GIAN, và đó là lý do nhiều dự đoán sụp đổ đã sai. Mặt trái: lỗ không biến mất, nó tích lại và leo lên.', t:'Ngân hàng', tag:'TÀI SẢN',
   d:'Vừa là điểm yếu vừa là BỘ GIẢM XÓC: khoản xấu được gia hạn, đảo nợ, hoán đổi — lỗ không biến mất mà được DI CHUYỂN.'},

  {id:'taikhoa', vi:'Ổ CỨNG THỨ NHẤT — và không chỉ là ngân sách. Đây là khả năng trả lương công chức, giáo viên, cảnh sát, quân đội, lương hưu và phúc lợi, tức khả năng giữ bộ máy DÍNH VÀO NHAU. Đường đáy có tên riêng là "tam bảo". Một cú sốc bên ngoài chỉ nguy hiểm cho chế độ khi nó biến thành vấn đề phân phối nguồn lực bên trong Đảng — và đây đúng là chỗ chuyển hoá đó xảy ra.', t:'Tài khoá', tag:'Ổ CỨNG 1',
   d:'Không chỉ là ngân sách. Là khả năng trả lương công chức, giáo viên, cảnh sát, quân đội, lương hưu — tức khả năng giữ bộ máy dính vào nhau. Ngân sách 2026: thâm hụt ~5,89 nghìn tỷ NDT (~4% GDP), trung ương chuyển ~10,415 nghìn tỷ cho địa phương trong khi địa phương tự thu ~12,503 nghìn tỷ. Đường đáy có tên riêng — <b>“tam bảo”</b>: dân sinh cơ bản, tiền lương, hoạt động bộ máy.'},
  {id:'canbo', vi:'Ổ CỨNG THỨ HAI — bộ truyền động. Không có cán bộ thì Trung ương chỉ là văn kiện. Hai điểm yếu nội sinh: thông tin méo (cấp dưới muốn thăng chức nên báo cáo đẹp — chính Trung ương 2026 vẫn phải nhắc chống "thành tích bằng số liệu giả"), và xung đột chỉ tiêu khi nguồn lực co lại.', t:'Cán bộ', tag:'Ổ CỨNG 2',
   d:'Bộ truyền động. Trung ương không điều khiển từng người mà kiểm soát ĐƯỜNG THĂNG TIẾN. Nhưng chính cơ chế đó sinh ra báo cáo đẹp và "không dám làm". Quy mô kỷ luật năm 2025: ~1,012 triệu vụ, ~47.000 người bị lưu trí, ~983.000 quyết định — vừa là kiểm soát mạnh lên, vừa có thể là lòng tin nội bộ giảm.'},
  {id:'anninh', vi:'Ổ CỨNG THỨ BA — khoá hệ thống. Nhưng nó dựa trên NĂM thứ chứ không chỉ súng: chuỗi mệnh lệnh, lương và nguồn lực, trung thành chính trị, thông tin, và niềm tin rằng Trung ương vẫn đang kiểm soát. Đó là lý do tài khoá quay lại chạm vào đây — và là lý do nó chịu kéo kép khi kinh tế xuống.', t:'An ninh', tag:'Ổ CỨNG 3',
   d:'Công an, an ninh nhà nước, chính pháp, quân đội. Cohesion ở đây dựa trên chuỗi mệnh lệnh, lương bổng, lòng trung thành và niềm tin rằng trung tâm còn kiểm soát được.'},

  {id:'elite', vi:'Ổ META. Ba ổ cứng trên đều quy về đây. Một chế độ độc đảng không cần 1,4 tỷ người đồng ý; nó cần những người CÓ KHẢ NĂNG thay đổi quyền lực tiếp tục tin rằng giữ hệ thống tốt hơn phá nó. Đó là một vòng trao đổi: Trung ương cho sự nghiệp, địa vị, quyền hành, nguồn lực và bảo vệ; elite trả lại trung thành, thực thi, thông tin và kiểm soát địa bàn.', t:'Thống nhất tầng lãnh đạo', tag:'Ổ META',
   d:'Chế độ không cần 1,4 tỷ người đồng ý. Nó cần những người CÓ KHẢ NĂNG THAY ĐỔI QUYỀN LỰC tiếp tục tin rằng giữ hệ thống tốt hơn phá nó.'},
  {id:'chedo', vi:'HẠ NGUỒN. Và đây là chỗ phải nói cho chính xác nhất cả mạch: hệ 1 hỏng là SUY THOÁI; hệ 1 + 2 hỏng là KHỦNG HOẢNG NHÀ NƯỚC; phải cả ba hệ — kinh tế, tài khoá, chính trị — cùng mất khả năng bù cho nhau thì mới nói tới nguy cơ sụp chế độ. Trộn ba thứ đó là chỗ mọi phân tích "đánh Trung Quốc" trở nên vô dụng.', t:'Chế độ tồn tại', tag:'HẠ NGUỒN',
   d:'Điểm cuối thật sự. Khủng hoảng kinh tế ≠ khủng hoảng chế độ — một chế độ có thể nghèo mà tồn tại rất lâu.'}
];

/* ── BẢNG ĐỒNG HỒ: sáu cái tài khoá, sáu cái quyền lực ──────
   Đây là phát biểu mạnh nhất của cả hồ sơ. Đo GDP để đoán số
   phận một chế độ là đo sai đại lượng. */
const GAUGES = [
  {id:'thudiaphuong', t:'Thu địa phương / chi bắt buộc', d:'Địa phương có tự trả nổi phần phải trả không, hay ngày càng phải xin trung ương.',
   vi:'Đây là đồng hồ số một vì nó đo đúng thứ giữ bộ máy dính vào nhau. Địa phương tự thu ~12,503 nghìn tỷ nhưng nhận ~10,415 nghìn tỷ chuyển giao — gần một nửa chi đến từ trên. Tỷ lệ đó nhích lên là tài khoá đang trượt từ cấp 2 sang cấp 3.'},
  {id:'bandat', t:'Doanh thu bán đất', d:'Nguồn thu từng gánh phần lớn ngân sách địa phương. Đây là đồng hồ nối bất động sản với chính trị.',
   vi:'Đất là mắt xích nối tài sản với chính quyền: dân mua nhà → chủ đầu tư mua đất → địa phương thu ngân sách → hạ tầng → LGFV → ngân hàng. Chạy ngược thì cả chuỗi ngược, và đây là chỗ chạy ngược ĐẦU TIÊN.'},
  {id:'lgfv', vi:'Nợ ẩn ~14,3 nghìn tỷ NDT (ước tính 2023) phần lớn nằm ở đây. Chi phí vay và kỳ hạn là hai thứ cho biết chương trình hoán đổi nợ đang mua được bao nhiêu thời gian — và mua thêm thời gian chính là toàn bộ chiến lược ở cấp 2.', t:'Chi phí và kỳ hạn LGFV', d:'Nợ ngoài bảng của chính quyền địa phương — lãi bao nhiêu, đáo hạn năm nào, đảo được không.'},
  {id:'chuyengiao', t:'Trung ương phải tăng transfer bao nhiêu', d:'Tỷ lệ địa phương sống bằng tiền trung ương. Càng cao thì gánh nặng càng dồn về một chỗ.',
   vi:'Đo trực tiếp việc lỗ đang leo lên bậc nào của thang. Trung ương phải tăng chuyển giao nghĩa là bậc địa phương đã đầy.'},
  {id:'bomvon', t:'Quy mô bơm vốn ngân hàng', d:'Trái phiếu đặc biệt để bổ sung vốn cho ngân hàng quốc doanh — dấu hiệu lỗ đang được chuyển lên tầng trên.',
   vi:'Trái phiếu đặc biệt bổ sung vốn ngân hàng quốc doanh (2026: 300 tỷ NDT) là dấu hiệu lỗ đã đi từ chủ đầu tư qua ngân hàng và đang được đẩy tiếp lên trung ương.'},
  {id:'tambao', t:'"Tam bảo" ở cơ sở', d:'Dân sinh cơ bản · tiền lương · hoạt động bộ máy. Đây là ĐƯỜNG ĐÁY tài khoá; chạm nó là chạm chỗ khác hẳn GDP.',
   vi:'"Tam bảo" — dân sinh cơ bản, tiền lương, hoạt động bộ máy — là ĐƯỜNG ĐÁY mà chính ngân sách 2026 gọi tên. GDP thấp chưa chắc gây khủng hoảng quyền lực; địa phương không trả nổi lương thì khác hẳn.'},
  {id:'khongdam', t:'Mức "không dám làm" trong bộ máy', d:'Kỷ luật mạnh → cán bộ sợ sai → không quyết → tê liệt hành chính. Nghịch lý cốt lõi thời Tập.',
   vi:'Nghịch lý trung tâm của thời Tập: kỷ luật mạnh → sợ sai → không dám quyết → tê liệt hành chính. Chính Trung ương nhận ra và vừa đòi "quản nghiêm" vừa đòi bảo vệ người dám làm — hai yêu cầu kéo ngược nhau.'},
  {id:'thanhloc', t:'Số lượng và cấp bậc cán bộ bị thanh lọc', d:'Đọc hai chiều: vừa là kiểm soát mạnh lên, vừa có thể là mạng quan hệ bị phá và lòng tin nội bộ giảm.',
   vi:'Đọc HAI CHIỀU, và đây là chỗ dễ sai nhất bảng: thanh lọc vừa có thể là Trung ương kiểm soát mạnh hơn, vừa có thể là niềm tin nội bộ giảm. Hai thứ có thể xảy ra cùng lúc, nên một đợt khai trừ KHÔNG tự chứng minh điều gì.'},
  {id:'nhansu', t:'Thay đổi bất thường ở Bộ Chính trị · Quân uỷ · Chính pháp', d:'Danh sách lãnh đạo ngắn bất thường hoặc thay đổi nhanh là dấu hiệu cần theo dõi.',
   vi:'Thay đổi bất thường ở Thường vụ, Quân uỷ hay Chính pháp là tín hiệu sớm nhất của ngưỡng elite. Danh sách Quân uỷ hiện ngắn bất thường sau các đợt thanh lọc 2023–26.'},
  {id:'menhlenh', t:'Nhất quán mệnh lệnh trung ương ↔ thực thi địa phương', d:'Mệnh lệnh có bị trì hoãn, vô hiệu hoá hay cạnh tranh không — đây là dấu hiệu sớm của rạn nứt.',
   vi:'Mức nhất quán giữa mệnh lệnh trung ương và thực thi địa phương. Lệch không có nghĩa là chống đối — nó thường là xung đột chỉ tiêu. Nhưng lệch kéo dài thì bộ truyền động đang mòn.'},
  {id:'batdong', t:'Bất đồng công khai ở tầng lãnh đạo cao', d:'Không phải chỉ trích kinh tế, mà là các nhóm cấp cao không còn chấp nhận cùng một quy tắc.',
   vi:'Bất đồng công khai ở tầng cao là NGƯỠNG THỨ NHẤT. Tài liệu chính thức 2026 liên tục nhấn mạnh giữ quyền uy Trung ương — việc phải nhấn mạnh không chứng minh có chia rẽ, nhưng cho thấy cohesion được coi là mục tiêu sống còn.'},
  {id:'chuoilenh', t:'Công an và quân đội có cùng chuỗi mệnh lệnh không', d:'ĐỒNG HỒ QUAN TRỌNG NHẤT. Khi hai lực lượng cưỡng chế không còn nhận cùng một chuỗi lệnh thì mọi đồng hồ khác thành thứ yếu.',
   vi:'Đồng hồ QUAN TRỌNG NHẤT bảng, và cũng là cái khó đo nhất: công an và quân đội có tiếp tục nhận cùng một chuỗi mệnh lệnh hay không. Đây là NGƯỠNG THỨ HAI — thứ phân biệt một chế độ đang khó khăn với một chế độ đang mất quyền lực.'}
];

/* ── NĂM CẤP ĐỘ (Việt Nam có bốn) ───────────────────────────
   Thêm một bậc vì bậc cuối của Trung Quốc không phải "khủng
   hoảng kinh tế" mà là "rạn nứt tầng lãnh đạo và an ninh". */
const LEVELS = [
  {n:1, t:'CÚ SỐC KINH TẾ',
   co:'Đây là lớp NGOÀI CÙNG, và hệ thống chịu khá tốt — đó là điều phần lớn phân tích "đánh Trung Quốc" bỏ qua. Dầu đã đa dạng nguồn: Nga ~20%, Saudi ~14%, Iran ~11%, Iraq ~10%, cộng Kazakhstan, Myanmar và sản xuất nội địa ~4,3 triệu thùng/ngày. Chip bị siết thì còn mature-node, SMIC, Huawei, thiết bị nội địa và trợ cấp nhà nước — cấm vận làm CHẬM biên nghiên cứu và TĂNG chi phí, không làm nhà máy ngừng chạy. Xuất khẩu bị một thị trường siết thì chuyển hướng ASEAN, Mexico, Global South. Ba đòn này làm Trung Quốc NGHÈO HƠN hoặc CHẬM HƠN; chúng không làm nó gãy.',
   dau:'Chưa đồng hồ nào trong mười hai cái phải đỏ, vì cú sốc chưa chạm tới bảng cân đối. Số đo nền — Brent, SOXX, FXI, Hang Seng — mới là chỗ thấy trước.',
   day:'Nó chỉ nguy hiểm khi rơi ĐÚNG LÚC bất động sản đang yếu: chi phí năng lượng ↑ và đơn hàng ↓ chồng lên tài sản ↓ và thu đất ↓. Một cú sốc đúng thời điểm mạnh hơn ba cú sốc rời rạc.',
   d:'Xuất khẩu ↓, dầu ↑, hạn chế công nghệ. Chi phí tăng, tăng trưởng chậm lại.',
   r:'Chịu được khá tốt.'},
  {n:2, t:'CÚ SỐC BẢNG CÂN ĐỐI', hien:true,
   co:'Đây là chỗ hệ thống mạnh hơn người ta tưởng, và là lý do rất nhiều dự đoán "Trung Quốc sắp Lehman" đã sai. Trong một nền kinh tế thông thường, chủ đầu tư vỡ kéo ngân hàng vỡ. Ở đây lỗ KHÔNG biến mất mà DI CHUYỂN QUA HỆ THỐNG: chủ đầu tư → ngân hàng gia hạn → tái cấp vốn → LGFV và tỉnh → hoán đổi nợ → trung ương phát trái phiếu đặc biệt. "Nợ ẩn" ~14,3 nghìn tỷ NDT ước tính năm 2023 đang được chuyển dần sang nợ chính thức dài hạn hơn và rẻ hơn. Ngân sách 2026 bố trí 4,4 nghìn tỷ trái phiếu đặc biệt địa phương và 300 tỷ bơm vốn cho các ngân hàng quốc doanh lớn.',
   dau:'Đầu tư phát triển bất động sản 2025 giảm 17,2%. Ba đồng hồ đầu bảng — thu địa phương, doanh thu bán đất, chi phí và kỳ hạn LGFV — là chỗ nhìn thấy sớm nhất.',
   day:'Khi các bậc trên thang đều đầy: hộ gia đình không muốn gánh nữa, doanh nghiệp tư nhân lợi nhuận quá mỏng, địa phương nợ quá cao, ngân hàng bảng cân đối yếu, SOE hiệu quả thấp. Lúc đó chỉ còn một bậc.',
   d:'Bất động sản ↓, LGFV căng, ngân hàng chịu rủi ro. Hoán đổi nợ, chuyển giao trung ương, đảo nợ ngân hàng.',
   r:'Vẫn chịu được — và đây là chỗ dữ liệu hiện tại cho thấy Trung Quốc đang đứng.'},
  {n:3, t:'CĂNG THẲNG TÀI KHOÁ',
   co:'Trung ương gánh thay, và con số cho thấy việc đó đã đang diễn ra. Ngân sách 2026: thâm hụt ~5,89 nghìn tỷ NDT (~4% GDP), trung ương chuyển ~10,415 nghìn tỷ cho địa phương trong khi địa phương tự thu ~12,503 nghìn tỷ — tức gần một nửa nguồn chi của địa phương đến từ trên. IMF nói khá thẳng: nếu có một đợt giảm tốc mạnh do giảm đòn bẩy trên diện rộng thì hỗ trợ tài khoá bổ sung nên đến từ chính quyền trung ương và nằm TRÊN bảng cân đối ngân sách chính thức, tức thôi giấu ngoài bảng.',
   dau:'Đường đáy có tên riêng — "tam bảo": dân sinh cơ bản, tiền lương, hoạt động bộ máy. Đồng hồ chuyển giao trung ương và đồng hồ bơm vốn ngân hàng là hai cái đo trực tiếp cấp này.',
   day:'Khi chính trung ương cũng phải CHỌN ai được cứu — bất động sản, ngân hàng, địa phương, lương hưu, quân đội, công nghệ, SOE hay người tiêu dùng. Không lựa chọn nào miễn phí; mỗi phương án chuyển đau từ nhóm này sang nhóm khác. Đó là lúc tài khoá biến thành CHÍNH TRỊ PHÂN PHỐI.',
   d:'Địa phương khó duy trì chi tiêu. Trung ương phải gánh ngày càng nhiều.',
   r:'Khó hơn nhiều, nhưng chưa phải khủng hoảng chế độ.'},
  {n:4, t:'CĂNG THẲNG CÁN BỘ VÀ AN NINH',
   co:'Đây là chỗ hệ thống bắt đầu ăn vào chính BỘ TRUYỀN ĐỘNG của nó. Một bí thư tỉnh cùng lúc bị đòi: tăng GDP, giảm nợ, giữ giá bất động sản, không cứu doanh nghiệp yếu, tăng việc làm, giữ môi trường, không để xảy ra biểu tình, không tham nhũng, và thực hiện đủ chỉ thị trung ương. Dư dả thì làm được; nguồn lực co lại thì buộc phải chọn — và chọn nào cũng vi phạm một chỉ tiêu khác. Cộng thêm kỷ luật rất mạnh (2025: ~1,012 triệu vụ, ~983.000 quyết định) sinh ra nghịch lý "sợ sai nên không dám quyết". An ninh thì chịu KÉO KÉP: việc tăng trong khi tiền nuôi giảm. Nhưng Bắc Kinh biết rõ nên ngân sách 2026 vẫn đặt quốc phòng, ngoại giao và chính pháp trong nhóm phải bảo đảm nguồn lực — nên đây vẫn CHƯA phải gãy.',
   dau:'Ba đồng hồ cuối bảng: "không dám làm" trong bộ máy, số lượng và cấp bậc cán bộ bị thanh lọc, và mức nhất quán giữa mệnh lệnh trung ương với thực thi địa phương.',
   day:'Phải qua thêm HAI NGƯỠNG chứ không phải một: ngưỡng thứ nhất là rạn nứt trong tầng elite, ngưỡng thứ hai là rạn nứt trong chuỗi an ninh. Thiếu ngưỡng nào cũng chưa thành khủng hoảng chế độ.',
   d:'Nguồn lực ↓ trong khi mục tiêu xung đột nhau. Bất ổn xã hội ↑, thanh lọc ↑, tê liệt hành chính ↑.',
   r:'Sức ép lên chính chế độ.'},
  {n:5, t:'RẠN NỨT TẦNG LÃNH ĐẠO VÀ AN NINH',
   co:'KHÔNG CÒN CƠ CHẾ HẤP THỤ NÀO. Đây là chỗ phải nói cho chính xác: cấp 5 không phải "kinh tế xấu hơn cấp 4" — nó KHÁC LOẠI. Bốn cấp trên đều là bài toán phân phối tổn thất; cấp 5 là lúc chính cái cơ chế phân phối ấy không còn ai công nhận. Một chế độ độc đảng không cần 1,4 tỷ người đồng ý; nó cần những người CÓ KHẢ NĂNG thay đổi quyền lực tiếp tục tin rằng giữ hệ thống hiện tại tốt hơn phá nó.',
   dau:'Không phải "có người chỉ trích kinh tế". Mà là: các nhóm cấp cao không còn chấp nhận cùng một quy tắc; mệnh lệnh bắt đầu bị trì hoãn, vô hiệu hoá hoặc cạnh tranh; và dấu hiệu nặng nhất — công an và quân đội không còn nhận cùng một chuỗi mệnh lệnh.',
   day:'CHƯA CÓ CƠ SỞ NÀO nói Trung Quốc đang ở cấp này. Bằng chứng hiện tại chỉ tới cấp 2, còn trung ương vẫn giữ được cả ba ổ cứng. Ghi cấp 5 ra đây là để biết ĐANG CÒN BAO XA, không phải để dự đoán nó sắp tới.',
   d:'Tầng lãnh đạo chia rẽ + chuỗi an ninh chia rẽ + trung tâm mất khả năng tài khoá — cùng lúc.',
   r:'Đây mới là khủng hoảng chế độ.'}
];

/* ── KỊCH BẢN ───────────────────────────────────────────────── */
/* Trung Quốc KHÔNG xếp theo nguồn cú sốc mà theo việc BA HỆ CÒN BÙ
   ĐƯỢC CHO NHAU HAY KHÔNG. Dùng chung câu dẫn của Việt Nam ở đây là
   nói sai trục phân nhánh — đúng lỗi đã xảy ra trước lượt này. */
const KB = {
  tieu:'Ba nhánh, một câu hỏi về sức chịu',
  lede:'Ba nhánh này không chia theo nguồn cú sốc mà theo <b>việc các hệ còn bù được cho nhau hay không</b>. Cùng một cú sốc, đặt vào ba trạng thái khác nhau của bất động sản, tài khoá địa phương và niềm tin, cho ba kết cục khác hẳn nhau.',
  ket:'Ranh giới nằm giữa B và C. Ở B từng hệ chịu đau nhưng vẫn còn hệ khác gánh sang — trung ương gánh cho địa phương, ngân hàng quốc doanh gia hạn nợ, tiết kiệm hộ gia đình đỡ phần còn lại. Ở C thì tài khoá, ngân hàng và tài sản hộ gia đình mất khả năng bù cho nhau <b>cùng lúc</b>, và câu hỏi chuyển từ tăng trưởng sang tính chính danh.'
};
const RANH = 'Ranh giới thật sự nằm giữa cấp 2 và cấp 3: cấp 3 là lúc <b>vòng lặp bắt đầu tự chạy</b> mà không cần thêm cú sốc mới nào từ bên ngoài. Và cascade chạy được <b>cả hai chiều</b> — kinh tế đẩy chính trị, nhưng chính trị hỏng cũng kéo kinh tế xuống theo.';

const SCEN = [
  {k:'A', t:'Chỉ cú sốc kinh tế', w:'Hệ thống hấp thụ', acc:'#2ea043',
   pts:[
     'Dầu ↑, chip bị hạn chế, đơn hàng ↓ — nhưng từng cái một',
     'Chi phí tăng, tăng trưởng chậm, không chạm tầng tài sản',
     'Trung Quốc đổi thị trường, đổi nhà cung cấp, đổi tuyến logistics',
     'Nga làm vùng đệm cho phần năng lượng'
   ],
   asc:'CÚ SỐC ĐƠN LẺ\n      ↓\nchi phí ↑ · đơn hàng ↓\n      ↓\ntăng trưởng chậm lại\n      ↓\n  HẤP THỤ ĐƯỢC\n\n→ Cấp độ 1'},
  {k:'B', t:'Cú sốc ngoài gặp bất động sản yếu', w:'Bắt đầu thành hệ thống', acc:'#d29922',
   pts:[
     'Năng lượng ↑ và thương mại ↓ đúng lúc bất động sản đang giảm',
     'Nhà đất ↓ → bán đất ↓ → thu địa phương ↓ → LGFV căng → ngân hàng',
     'Nhu cầu nội địa yếu nên phải dựa xuất khẩu — mà xuất khẩu đúng là chỗ bị siết',
     'Đây là chỗ dữ liệu hiện tại cho thấy Trung Quốc đang đứng'
   ],
   asc:'HORMUZ / THƯƠNG MẠI\n        ↓\n   chi phí ↑ · đơn hàng ↓\n        ↓            ↘\n   việc làm ↓    BẤT ĐỘNG SẢN ↓\n        ↓            ↓\n   tiêu dùng ↓   bán đất ↓\n        └─────┬──────┘\n              ↓\n         LGFV · NGÂN HÀNG\n\n→ Cấp độ 2'},
  {k:'C', t:'Ba hệ mất khả năng bù cho nhau', w:'Khủng hoảng chế độ', acc:'#f0503f',
   pts:[
     'HỆ 1 kinh tế: xuất khẩu + năng lượng + công nghệ + BĐS + ngân hàng không còn tự bù được',
     'HỆ 2 tài khoá: trung ương không còn đủ khả năng cứu ngân hàng, địa phương, việc làm, BĐS, SOE',
     'HỆ 3 chính trị: tầng lãnh đạo + an ninh + quân đội + cán bộ địa phương không còn cùng một hướng',
     'Hệ 1 hỏng → suy thoái. Hệ 1+2 hỏng → khủng hoảng nhà nước. Cả ba → mới là nguy cơ sụp chế độ.'
   ],
   asc:'HỆ 1 KINH TẾ ✗\n      ↓\nHỆ 2 TÀI KHOÁ ✗\n      ↓\n  ── NGƯỠNG 1 ──\n  RẠN NỨT LÃNH ĐẠO\n      ↓\n  ── NGƯỠNG 2 ──\n  RẠN NỨT AN NINH\n      ↓\nHỆ 3 CHÍNH TRỊ ✗\n      ↓\nKHỦNG HOẢNG CHẾ ĐỘ\n\n→ Cấp độ 5'}
];

/* ── HỒ SƠ NỀN ──────────────────────────────────────────────── */
const LIB = [
  {
    id:'sausanh', n:1, t:'Sáu dấu ≠ — ranh giới giữ điều tra khỏi thành thuyết âm mưu',
    d:'Cụm quan trọng nhất của toàn bộ chủ thể Trung Quốc. Chính việc giữ sáu ranh giới này mới cho phép phát hiện MỐI LIÊN HỆ THẬT khi nó xuất hiện.',
    blocks:[
      {h:'Sáu dấu ≠',
       p:'Mỗi dòng dưới đây là một bước nhảy mà rất nhiều phân tích thực hiện <b>mà không có bằng chứng cho bước nhảy đó</b>. Bỏ qua một dấu ≠ là biến một quan sát đúng thành một kết luận sai.',
       a:'CÓ CHI BỘ ĐẢNG\n  ≠  công ty thuộc Nhà nước\n\nĐƯỢC MẶT TRẬN THỐNG NHẤT TIẾP XÚC\n  ≠  điệp viên\n\nCÓ QUAN HỆ VỚI ĐCSTQ\n  ≠  nhận lệnh từ Tập\n\nTAM HOÀNG THÂN BẮC KINH\n  ≠  cơ quan chính thức của ĐCSTQ\n\nCHÍNH PHÁP DO ĐẢNG LÃNH ĐẠO\n  ≠  Tập quyết định từng bản án\n\nTẬP QUYỀN\n  ≠  trung ương biết và điều khiển mọi thứ'},
      {h:'Năm mức rất dễ bị trộn',
       p:'Cùng một logic đã dùng cho Vingroup: <b>phụ thuộc chính sách · liên minh lợi ích · hợp tác chiến lược · quyền chi phối · quyền sở hữu</b> là năm thứ khác nhau. Ở Trung Quốc còn thêm một mức nữa mà phương Tây hay bỏ sót — <b>hấp thụ</b>: Đảng không tiêu diệt tầng lớp doanh nhân như thời Mao, nó <b>hấp thụ</b> họ.',
       a:'QUAN HỆ\n   ≠\nQUYỀN SỞ HỮU\n   ≠\nCHỈ HUY'},
      {h:'Vì sao ranh giới lại làm điều tra MẠNH hơn, không yếu đi',
       p:'Nếu mọi quan hệ đều bị đọc thành "nhận lệnh", thì khi tìm được một trường hợp <b>thật sự</b> nhận lệnh, ta không còn cách nào phân biệt nó với phần còn lại. Giữ ranh giới chính là giữ khả năng phát hiện.'}
    ]
  },
  {
    id:'os', n:2, t:'ĐCSTQ như một hệ điều hành',
    d:'Không nhìn Trung Quốc như một chính phủ có vài bộ ngành, mà như một mạng tổ chức nằm phía trên, bên trong và xuyên qua nhà nước.',
    blocks:[
      {h:'Đảng không phải khách thuê của nhà nước',
       p:'Điều lệ hiện hành tự xác định Đảng là <b>"lực lượng lãnh đạo chính trị cao nhất"</b> và "Đảng lãnh đạo tất cả", đồng thời nói Đảng phải hoạt động trong khuôn khổ Hiến pháp và pháp luật. Cuối 2025: khoảng <b>101,286 triệu đảng viên</b> và <b>5,431 triệu tổ chức cơ sở</b>, trong đó ~1,692 triệu nằm trong doanh nghiệp.',
       a:'                ĐCSTQ\n                  │\n     ┌────────────┼────────────┐\n  NHÀ NƯỚC     QUÂN ĐỘI      XÃ HỘI\n     │            │            │\n chính phủ       PLA      tổ chức đảng\n quốc hội                 đoàn thể\n tư pháp                  doanh nghiệp\n                          trường học'},
      {h:'Bằng chứng trực tiếp nhất về thứ bậc',
       p:'Ngày <b>8/1/2026</b>, Thường vụ Bộ Chính trị nghe báo cáo công tác từ các đảng đoàn của Quốc hội, Quốc vụ viện, Chính hiệp, Toà án Nhân dân Tối cao và Viện Kiểm sát Nhân dân Tối cao. Nhà nước không đứng song song với Đảng — nó nằm dưới.',
       a:'NHÀ NƯỚC\nkhông đứng song song với ĐẢNG\n\n     ĐẢNG\n      ↓\n  định hướng\n      ↓\n  NHÀ NƯỚC\n      ↓\n  thi hành'},
      {h:'Hai mươi ổ cắm, không ổ nào một mình đủ',
       p:'Nhân sự (Ban Tổ chức) · Kỷ luật (CCDI) · An ninh (Chính pháp, Công an, An ninh Nhà nước) · Thông tin (Tuyên truyền, CAC) · Thống chiến · Tài chính (Uỷ ban Tài chính TW, lập 2023) · Khoa học công nghệ (Uỷ ban KHCN TW, lập 2023) · Doanh nghiệp nhà nước · Doanh nghiệp tư nhân · Dữ liệu · Công tác xã hội (lập 2023) · Lưới cộng đồng · Trường học · Đoàn Thanh niên · Công đoàn · Đoàn thể · Tôn giáo · Địa phương · Kế hoạch 5 năm · Biên chế cơ cấu.',
       a:'Ổ CẮM MẠNH NHẤT\nkhông phải camera\nmà là NHÂN SỰ\n\n"Nếu anh kiểm soát đường thăng tiến,\nanh không cần gọi điện ra lệnh từng ngày.\nNgười ở dưới TỰ HỌC cách biết\ntrung ương muốn gì."'},
      {h:'Bốn uỷ ban chiến lược, và hai cơ quan hay bị bỏ quên',
       p:'Ngoài Uỷ ban Tài chính và Uỷ ban Khoa học Công nghệ (đều lập 2023) còn có <b>Uỷ ban An ninh Quốc gia Trung ương</b> và <b>Uỷ ban Cải cách Sâu rộng Trung ương</b>. Bên nhà nước, <b>Cục Dữ liệu Quốc gia</b> điều phối hạ tầng dữ liệu, kinh tế số và quản trị xã hội số — nhưng đừng tin huyền thoại "mọi dữ liệu Trung Quốc nằm trong một máy chủ": thực tế là bộ ngành, tỉnh, công an, doanh nghiệp và viễn thông đều có cơ sở dữ liệu riêng, và thách thức của trung ương chính là KẾT NỐI và tiêu chuẩn hoá chúng.'},
      {h:'Toà án và kiểm sát — nói cho đúng, không nói quá',
       p:'Sai nếu bảo "mọi thẩm phán đều nhận điện thoại của Tập". Cũng sai nếu áp mô hình tam quyền phân lập của Mỹ. Chánh án Toà án Nhân dân Tối cao <b>Trương Quân</b> từng nhấn mạnh toà án trước hết là <b>cơ quan chính trị</b> và phải kiên trì sự lãnh đạo tuyệt đối của Đảng; Viện trưởng Viện Kiểm sát Tối cao <b>Ứng Dũng</b> dùng cấu trúc tương tự. Hai lớp — chuyên môn pháp lý và đường lối chính trị — tồn tại CÙNG LÚC.',
       a:'PHÁP LUẬT → toà · kiểm sát → chuyên môn\n\n        NHƯNG\n\nĐẢNG → đường lối → CPLC · đảng đoàn → toàn hệ'},
      {h:'Kế hoạch 5 năm — vòng truyền lệnh, không phải kinh tế mệnh lệnh',
       p:'Trung ương định hướng chiến lược → Quốc vụ viện và <b>NDRC</b> dựng kế hoạch → Quốc hội thông qua → bộ ngành và tỉnh làm kế hoạch chuyên ngành → dự án, ngân sách, tín dụng. "Planning" ở đây KHÔNG đồng nghĩa nền kinh tế mệnh lệnh kiểu Stalin: doanh nghiệp tư nhân và thị trường vẫn tồn tại mạnh. Nhưng thị trường được ghép với quy hoạch chiến lược, chính sách công nghiệp và tài chính nhà nước.'},
      {h:'Vòng lặp thật sự chạy thế nào — ví dụ bán dẫn',
       p:'Không phải "Tập gọi điện cho SMIC". Chuỗi thật là: Trung ương xác định chip là chiến lược → Uỷ ban Khoa học Công nghệ TW → <b>MIIT · NDRC · MOST</b> → quỹ nhà nước và ngân hàng → tỉnh → phòng thí nghiệm, đại học, doanh nghiệp → KPI và báo cáo → kiểm tra trung ương → đánh giá cán bộ → chỉnh chính sách. Mệnh lệnh đi xuống, dữ liệu đi lên, rồi vòng lại — đó là lý do gọi nó là quản trị KHÉP VÒNG chứ không phải "độc tài" đơn thuần.',
       a:'TRUNG ƯƠNG → định hướng · KPI · cán bộ · kỷ luật\n     ↓\nTỈNH → tự tìm cách thực hiện\n     ↓\nTHÀNH PHỐ → HUYỆN → cơ sở\n     ↓\ndữ liệu · báo cáo · thanh tra\n     ↓\nTRUNG ƯƠNG'},
      {h:'Và cơ chế ngăn LIÊN MINH NGANG',
       p:'Trong một hệ phi tập trung, một thống đốc có thể có quyền lực riêng. ĐCSTQ cố ngăn tỉnh–tỉnh–quân đội–ngân hàng nối thành một mạng độc lập bằng <b>luân chuyển cán bộ, bổ nhiệm từ trên, kỷ luật, đảng uỷ và thanh tra trung ương</b>. Mục đích là biến cấu trúc thành hình nan hoa — mọi nhánh nối về tâm — thay vì thành một liên minh ngang. Đây là một trong những cơ chế quan trọng nhất chống hình thành trung tâm quyền lực cạnh tranh.',
       a:'MUỐN:              KHÔNG MUỐN:\n  TRUNG ƯƠNG          A──B──C\n   ╱   │   ╲           ╲ │ ╱\n  A    B    C        liên minh độc lập'},
      {h:'META-SOCKET: quyền sửa chính bo mạch',
       p:'Uỷ ban Biên chế Cơ cấu Trung ương nắm quyền <b>tạo cơ quan, xoá cơ quan, gộp cơ quan, chuyển chức năng, đổi biên chế</b>. Cải cách 2023 chính là ví dụ — lập một loạt uỷ ban trung ương mới với mục tiêu ghi thẳng trong văn kiện là "tăng cường sự lãnh đạo tập trung thống nhất của Trung ương Đảng".',
       a:'CPU CÓ THỂ\nTHIẾT KẾ LẠI MAINBOARD'},
      {h:'Đoàn thể là "dây truyền động", và tôn giáo cũng có khung riêng',
       p:'Công nhân → ACFTU · thanh niên → Đoàn · phụ nữ → ACWF · doanh nhân → hội ngành · tôn giáo → các hội đoàn. Các nhóm xã hội KHÔNG nhất thiết bị xoá; nhiều nhóm được tổ chức lại thành <b>"transmission belt"</b> nối xã hội với Đảng. Tôn giáo cũng vậy: được tồn tại, nhưng tổ chức phải nằm trong khung quản lý chính trị — tài liệu thống chiến 2026 tiếp tục nhấn mạnh <b>"Trung Quốc hoá"</b> tôn giáo và tăng giáo dục chính trị. Và quy định về hoạt động tôn giáo <b>trực tuyến</b> đòi dùng nền tảng có phép, đồng thời ủng hộ sự lãnh đạo của Đảng — cùng một khung cho cả chùa/nhà thờ lẫn website/livestream. MERICS mô tả thời Tập là quá trình Đảng <b>tái cài sâu hơn</b> vào doanh nghiệp tư nhân, làng và cộng đồng đô thị.'},
      {h:'Từ "nhà nước chiến dịch" sang "hệ điều hành"',
       p:'Thời Mao: lãnh tụ phát động phong trào → quần chúng → đấu tố → hỗn loạn → tái lập trật tự. Thời Tập: uỷ ban trung ương → quy định → cơ quan → cơ sở dữ liệu → KPI → kiểm tra → kỷ luật → phản hồi. Không có nghĩa các chiến dịch biến mất — nghĩa là <b>năng lực kiểm soát được thể chế hoá hơn</b>.'}
    ]
  },
  {
    id:'thongchien', n:3, t:'Mặt trận Thống nhất — ổ cắm dễ bị bỏ qua nhất',
    d:'Cơ chế xử lý những người KHÔNG phải đảng viên. Đây là chỗ nối trực tiếp sang hồ sơ Hướng Hoa Cường.',
    blocks:[
      {h:'Logic: người ngoài Đảng không mặc nhiên là kẻ thù',
       p:'ĐCSTQ công khai gọi thống chiến là một <b>"pháp bảo"</b> — không phải mọi lực lượng bên ngoài đều phải tiêu diệt; lực lượng nào đoàn kết, phân hoá, tranh thủ hay sử dụng được thì đưa vào một mặt trận rộng hơn. Thí nghiệm đầu tiên là 1923–27: đảng viên cộng sản gia nhập KMT với tư cách cá nhân nhưng ĐCSTQ giữ tổ chức riêng, rồi cán bộ đi vào công đoàn, phong trào nông dân, tuyên truyền, quân đội và Học viện Hoàng Phố. <i>Cửu Bình</i> gọi đó là <b>"ký sinh"</b>; ĐCSTQ gọi là Mặt trận Thống nhất lần thứ nhất — sự kiện là có thật, tranh cãi nằm ở cách diễn giải mục đích. Quy định hiện hành gọi thống chiến là phương thức nhằm "ngưng tụ lòng người, tập hợp lực lượng" và củng cố địa vị cầm quyền của Đảng. Đối tượng gồm: các đảng nhỏ, người không đảng phái, trí thức, dân tộc, tôn giáo, doanh nhân tư nhân, "giai tầng xã hội mới", Hong Kong, Macau, Đài Loan, Hoa kiều và cộng đồng hải ngoại.',
       a:'        NGƯỜI NGOÀI ĐẢNG\n               │\n   ┌───────────┼───────────┐\nđối kháng   trung lập   có thể dùng\n   │           │           │\nchống      tranh thủ    đoàn kết\n/trấn áp   /thuyết phục /hợp tác'},
      {h:'Nhưng thống chiến ≠ điệp viên',
       p:'Đây là chỗ phải giữ nghiêm nhất. Thống chiến hoạt động ở nhiều cấp: <b>networking → quan hệ → thuyết phục chính trị → hấp thụ tinh hoa → hợp tác tổ chức</b>. Chỉ khi có chứng cứ riêng mới được nâng lên mức <b>bí mật · tài trợ · nhiệm vụ · chỉ huy · tình báo</b>.',
       a:'Một doanh nhân được UF tiếp xúc\n   ≠  đặc vụ\n\nMột hội người Hoa dự sự kiện\n   ≠  cơ sở tình báo\n\nMột nhân vật Hong Kong thân Bắc Kinh\n   ≠  nhận lệnh từ Tập'},
      {h:'Ngoại giao song song',
       p:'Một nước bình thường chủ yếu có Bộ Ngoại giao. Trung Quốc vận hành ba mạng: <b>ngoại giao nhà nước</b> (MFA), <b>ngoại giao đảng</b> (Ban Liên lạc Đối ngoại Trung ương — quan hệ thẳng với đảng cầm quyền, đảng đối lập, phong trào chính trị nước ngoài), và <b>thống chiến</b> với cộng đồng hải ngoại. Ba mạng có thể phối hợp nhưng không phải một cơ quan.'}
    ]
  },
  {
    id:'kmt', n:4, t:'Quốc Dân Đảng — 130 năm, và vì sao nó giải thích nhà Hướng',
    d:'Không phải chuyện Đài Loan. Đây là gốc chính trị của gia tộc Hướng, và là ví dụ về một mạng lưới đổi trục qua nhiều thế hệ.',
    blocks:[
      {h:'KMT ban đầu không phải "đảng của Tưởng Giới Thạch"',
       p:'Nó sinh ra từ phong trào cách mạng của <b>Tôn Trung Sơn</b>: Hưng Trung Hội (1894) → Đồng Minh Hội (1905) → Cách mạng Tân Hợi (1911) → Quốc dân đảng (1912) → <b>Trung Hoa Cách mạng Đảng (1914)</b> → Trung Quốc Quốc dân đảng (1919) — chính KMT ngày nay cũng tự mô tả lịch sử mình theo đúng chuỗi tái tổ chức này. Cách mạng 1911 thành công KHÔNG lập tức cho ra một nước cộng hoà ổn định: quyền lực trung ương yếu, <b>Viên Thế Khải</b> và các quân phiệt địa phương chia cắt đất nước, còn Tôn Trung Sơn có lý tưởng mà không có quân đội đủ mạnh — đó mới là chỗ Liên Xô bước vào. Tư tưởng gốc là Tam Dân Chủ Nghĩa — dân tộc, dân quyền, dân sinh. Tôn Trung Sơn chết năm 1925; người lấp khoảng trống là <b>Tưởng Giới Thạch</b>, vì ông có thứ nhiều chính trị gia KMT không có — QUÂN ĐỘI. Năm 1926 ông chỉ huy <b>Bắc phạt</b> đánh các quân phiệt để thống nhất Trung Quốc, và thắng rất nhanh. Không phải phát xít, không phải cộng sản, không phải quân phiệt.'},
      {h:'Nghịch lý lịch sử: KMT và ĐCSTQ có chung một phần "DNA tổ chức"',
       p:'Từ 1923, cố vấn Liên Xô — nổi bật là Mikhail Borodin — giúp KMT tái tổ chức theo mô hình đảng tập trung, kỷ luật cao kiểu Bolshevik. Liên Xô cũng giúp lập Học viện quân sự Hoàng Phố. Hai lực lượng sau này thành tử thù từng nằm trong <b>cùng một dự án liên minh chống quân phiệt</b>.',
       a:'         LIÊN XÔ\n            ↓\n        COMINTERN\n            ↓\n     ┌──────┴──────┐\n    KMT          ĐCSTQ\n     │             │\n tổ chức đảng   tổ chức đảng\n tuyên truyền   tuyên truyền\n cán bộ         cán bộ\n quân đội       quân đội\n chính trị hoá  chính trị hoá\n     └──────┬──────┘\n            ↓\n   LIÊN MINH LẦN 1 · 1924'},
      {h:'Bốn lần đổi quan hệ trong một thế kỷ',
       p:'1924 hợp tác → 1927 thanh trừng Thượng Hải và nội chiến → 1937 lại liên minh chống Nhật → 1946–49 nội chiến, KMT thua và rút sang Đài Loan. Giữa chặng đó, khoảng <b>1928</b> Tưởng dựng <b>chính phủ Nam Kinh</b> — trên danh nghĩa là Trung Hoa Dân Quốc, trên thực tế là khuôn ĐẢNG → NHÀ NƯỚC → QUÂN ĐỘI → HÀNH CHÍNH → XÃ HỘI mà sau này KMT đem sang Đài Loan. Từ <b>1931</b> và nhất là 1937 Nhật mở rộng xâm lược, và phần lớn chiến tranh chính quy chống Nhật nằm dưới chính phủ Quốc dân; sau khi Nhật đầu hàng, chính quyền ROC là bên tiếp nhận sự đầu hàng của quân Nhật tại Trung Quốc. Phải giữ CẢ HAI mặt — độc tài và đàn áp, nhưng cũng chống quân phiệt và lãnh đạo cuộc chiến chống Nhật.'},
      {h:'Tội ác: phải chia ba cấp mới nói chính xác được',
       p:'<b>Cấp 1 — lịch sử: CÓ.</b> Sự kiện 228 năm 1947 và thời White Terror là đàn áp chính trị nghiêm trọng; tài liệu của Quỹ Tưởng niệm 228 ghi Tưởng Giới Thạch ra lệnh một trung đoàn bộ binh và một tiểu đoàn quân cảnh sang Đài Loan; lực lượng tiếp viện đến <b>Keelung ngày 8/3</b> và chiến dịch trấn áp quy mô lớn tiếp diễn. Báo cáo của Hành chính viện Đài Loan ước tính <b>18.000–28.000 người chết</b> liên quan 228 — đây không còn là "tin đồn chống KMT" mà là kết quả điều tra do chính phía Đài Loan thời dân chủ hoá công bố. <b>Cấp 2 — trách nhiệm chế độ: RẤT MẠNH</b>, đó là hệ thống nhà nước độc tài dưới quyền KMT, không phải vài cảnh sát tự ý. <b>Cấp 3 — toà án tuyên toàn KMT là tổ chức tội phạm: KHÔNG.</b> Không có "Nuremberg của KMT"; Tưởng không bị xét xử hình sự trước khi chết năm 1975.',
       a:'VI PHẠM NHÂN QUYỀN LỊCH SỬ  =  CÓ\nTRÁCH NHIỆM CHẾ ĐỘ          =  CÓ\nTOÀ TUYÊN "TỔ CHỨC TỘI PHẠM" =  KHÔNG'},
      {h:'Và KMT tự biến đổi — điều rất khác ĐCSTQ',
       p:'Tưởng chết năm 1975, quyền lực chuyển sang con trai <b>Tưởng Kinh Quốc</b>; cuối thời ông hệ thống nới lỏng và thiết quân luật được dỡ bỏ năm <b>1987</b>. <b>Lý Đăng Huy</b> tiếp tục dân chủ hoá, rồi tới lượt <b>Mã Anh Cửu</b> đưa KMT trở lại cầm quyền một thời kỳ; năm 2000 KMT lần đầu mất chức tổng thống vào tay DPP và hệ thống không quay lại quân đội để lật kết quả. Một đảng từng cai trị độc tài đã chấp nhận cạnh tranh bầu cử và chuyển giao quyền lực. Chủ tịch KMT hiện nay là <b>Trịnh Lệ Văn</b>, nhậm chức 1/11/2025.'},
      {h:'Mặt tối của chiến tranh tổng lực — và ranh giới pháp lý',
       p:'Năm <b>1938</b> quân Quốc dân cố tình phá hệ thống đê <b>Hoàng Hà</b> để tạo lũ chặn bước tiến quân Nhật. Cùng năm, ở <b>Trường Sa/Changsha</b>, chính sách tiêu thổ dẫn tới một đám cháy bị kích hoạt quá sớm, thiêu phần lớn thành phố. Ước tính số người chết khác nhau rất lớn và hậu quả kéo dài trên vùng rộng. Đây là những quyết định quân sự gây thảm hoạ dân sự rất lớn — nhưng <b>chưa từng có toà án quốc tế xét xử và tuyên "tội ác chiến tranh"</b> về các vụ này, nên không được tự nâng thành bản án pháp lý.',
       a:'MỤC TIÊU\nkhông để Nhật dùng thành phố / chặn quân Nhật\n        ↓\nBIỆN PHÁP\ntiêu thổ · phá đê\n        ↓\nHỆ QUẢ\nthảm hoạ cho chính dân Trung Quốc'},
      {h:'Vì sao KMT thua Mao — không phải vì Mao "giỏi hơn"',
       p:'Tám năm chống Nhật làm KMT kiệt quệ: kinh tế suy yếu, lạm phát, tham nhũng, mất lòng dân, quân đội mệt mỏi. Trong khi ĐCSTQ đi đường khác — nông thôn, cải cách ruộng đất, tổ chức cơ sở, du kích, mở rộng quân đội. Sau khi Nhật đầu hàng năm 1945 nội chiến bùng lại; đến 1949 chính phủ Quốc dân thất bại trên đại lục và rút sang Đài Loan.'},
      {h:'Công lý chuyển tiếp — điều làm KMT khác hẳn ĐCSTQ',
       p:'Bảo tàng Nhân quyền Quốc gia Đài Loan gọi giai đoạn đàn áp kéo dài khoảng bốn thập niên là <b>White Terror</b>, và đối tượng không chỉ có đảng viên cộng sản: còn có người bị nghi là cộng sản, trí thức, nhà báo, nhà hoạt động, người đòi dân chủ, người đòi độc lập Đài Loan, người chỉ trích chính quyền. Điều quan trọng là <b>nhà nước dân chủ Đài Loan sau này đã tiến hành công lý chuyển tiếp</b> — huỷ nhiều bản án sai và bồi thường nạn nhân. Đó là thứ chưa xảy ra ở phía bên kia eo biển.'},
      {h:'Và vòng tròn khép lại',
       p:'Sau khi Trịnh Lệ Văn thắng chức chủ tịch, Tập Cận Bình gửi thông điệp chúc mừng với tư cách Tổng Bí thư ĐCSTQ, kêu gọi hai đảng củng cố "nền tảng chính trị chung". Trịnh không đáp lại bằng cam kết thống nhất mà nhấn mạnh hoà bình và giao lưu; năm 2026 còn nói cải thiện quan hệ với Bắc Kinh không đồng nghĩa chống Mỹ, và KMT vẫn ủng hộ <b>mua vũ khí Mỹ</b> nếu ngân sách hợp lý. <b>ĐCSTQ giao lưu với KMT ≠ KMT nằm dưới ĐCSTQ</b> — đúng nguyên tắc đã dùng với nhà Hướng.'}
    ]
  },
  {
    id:'cuubinh', n:5, t:'Đọc Cửu Bình cho đúng — nguồn luận chiến, không phải sử liệu',
    d:'Cụm phương pháp. Dùng một bản cáo trạng làm GIẢ THUYẾT ĐỂ KIỂM, không dùng kết luận của nó làm dữ kiện.',
    blocks:[
      {h:'Ba tầng, và chỉ hai tầng kiểm chứng được',
       p:'<b>Tầng 1 lịch sử</b> và <b>tầng 2 cơ chế</b> (bạo lực, tuyên truyền, đấu tranh, kiểm soát tư tưởng, thống chiến) có rất nhiều nội dung kiểm chứng độc lập được. <i>Cửu Bình</i> do <b>Epoch Times</b> xuất bản lần đầu tháng 11/2004, và chính trang của bộ sách mô tả nó như một dự án nhằm phơi bày bản chất ĐCSTQ và thúc đẩy thoái đảng — tức một tác phẩm luận chiến, không phải công trình sử học trung lập. <b>Tầng 3</b> — "tà giáo", "phản vũ trụ", "ác linh" — là phán xét đạo đức và tôn giáo của tác giả, không phải mệnh đề có thể chứng minh như một sự kiện lịch sử.'},
      {h:'ĐCSTQ ra đời từ đâu — Comintern CỘNG điều kiện nội sinh',
       p:'Đại hội I họp <b>23/7/1921</b> với hơn 50 đảng viên; nguồn chính thức của Đảng ghi rõ đại hội được tổ chức "với sự giúp đỡ của Quốc tế Cộng sản", có hai đại diện Comintern là <b>Maring</b> và <b>Nikolsky</b> dự. Cương lĩnh đầu tiên đặt mục tiêu dùng quân đội cách mạng vô sản để thiết lập <b>chuyên chính vô sản</b> — đây không phải lời cáo buộc của Cửu Bình mà là nội dung do chính nguồn giáo dục lịch sử của Đảng công bố. Nhưng phong trào cũng sinh từ khủng hoảng nội tại: nhà Thanh sụp, quân phiệt, ngoại bang, <b>Phong trào Ngũ Tứ</b>, trí thức đi tìm mô hình cứu nước. Nói gọn: Comintern cung cấp tư tưởng, kinh nghiệm tổ chức và trợ giúp quan trọng — nhưng ĐCSTQ không phải một văn phòng Moscow đặt tại Trung Quốc.'},
      {h:'1927–1949: Đảng học cách vận hành một nhà nước BÊN TRONG nhà nước',
       p:'Sau thanh trừng 1927, ĐCSTQ mất căn cứ đô thị và đi về nông thôn: <b>Hồng quân · căn cứ địa · thuế · toà án · tuyên truyền · cải cách ruộng đất · chính quyền địa phương</b>. Đây là điểm hay bị bỏ khi người ta chỉ kể chuyện "cộng sản thắng nhờ du kích": trước 1949 Đảng đã có kinh nghiệm CAI TRỊ, không chỉ kinh nghiệm chiến đấu.',
       a:'ĐẢNG CÁCH MẠNG\n      ↓\n  trở thành\n      ↓\nĐẢNG–NHÀ NƯỚC'},
      {h:'1978 và 1989 và Giang — ba lần Đảng đổi mà không đổi phần cốt lõi',
       p:'<b>1978, Đặng Tiểu Bình</b>: bỏ nhiều cơ chế kinh tế Mao — thị trường, đầu tư nước ngoài, doanh nghiệp tư nhân, xuất khẩu — nhưng KHÔNG từ bỏ độc quyền chính trị. <b>1989</b>: bài học rút ra là "cải cách kinh tế thì có thể, mất độc quyền chính trị thì không". <b>Giang Trạch Dân</b>: thay vì tiêu diệt tầng lớp doanh nhân như thời Mao, Đảng <b>hấp thụ</b> họ — đây chính là mức thứ sáu mà phương Tây hay bỏ sót khi chấm quan hệ nhà nước–doanh nghiệp.',
       a:'Kinh tế:  Maoism → thay đổi RẤT LỚN\nChính trị: độc quyền → KHÔNG đổi căn bản'},
      {h:'Bốn chỗ Cửu Bình sai hoặc quá đà',
       p:'<b>1.</b> "ĐCSTQ chỉ là chi nhánh Liên Xô" — quá đơn giản; Comintern có vai trò lớn thật nhưng phong trào cộng sản Trung Quốc cũng sinh từ khủng hoảng nội tại. <b>2.</b> "60–80 triệu người bị giết" như một con số duy nhất — phương pháp quá thô, gộp xử tử, nạn đói, bạo lực chính trị, tự sát, lao cải; riêng nạn đói Đại Nhảy Vọt đã có phạm vi ước tính 15–43 triệu tử vong vượt mức. <b>3.</b> "Cải cách kinh tế chỉ là trò lừa" — quá tuyệt đối; World Bank ghi nhận gần 800 triệu người vượt chuẩn nghèo cùng cực trong bốn thập niên. <b>4.</b> "Evil cult" — phán xét siêu hình, không phải khoa học chính trị.'},
      {h:'Nhưng nó đúng ở đâu',
       p:'Comintern có vai trò lớn trong sự ra đời ĐCSTQ · Đảng dùng bạo lực cách mạng · các chiến dịch chính trị gây thảm hoạ lớn · Cách mạng Văn hoá là thảm hoạ (<b>chính nghị quyết của Đảng sau thời Mao</b> gọi đó là "tai hoạ nghiêm trọng"; nghiên cứu của Andrew Walder dựa trên hơn 2.200 biên niên sử địa phương ước tính ~1,6 triệu người chết) · Thiên An Môn bị quân đội đàn áp · kiểm soát mạnh thông tin · thống chiến được ghi công khai trong quy định Đảng · Đảng xuyên vào nhà nước và xã hội — điều lệ xác nhận.'},
      {h:'Và điều nó không thể thấy vì viết năm 2004',
       p:'Tập Cận Bình và việc tập trung quyền lực · các uỷ ban trung ương mới · chống tham nhũng quy mô lớn · chi bộ đảng trong kinh tế tư nhân · CAC và quản trị nền tảng · kiến trúc an ninh Tân Cương · Luật An ninh Hong Kong · Ban Công tác Xã hội Trung ương · AI, dữ liệu và quản trị số.'},
      {h:'Chuỗi chiến dịch chính trị — tách từng loại, đừng cộng thành một số',
       p:'<b>Đầu 1950s</b> cải cách ruộng đất và trấn áp phản cách mạng: xử tử, bắt giữ, đấu tố, cưỡng chế quy mô lớn. <b>1957 Phản Hữu</b>: khoảng <b>552.000 người</b> bị gắn nhãn "hữu phái" — cơ chế đáng nhớ là <i>mở cửa phản biện → thu tiếng nói bất mãn → đổi định nghĩa → thanh lọc</i>. <b>1958–61 Đại Nhảy Vọt</b>: 15–43 triệu tử vong vượt mức; cơ chế gồm chính sách sai, cưỡng bức tập thể hoá, thu mua lương thực, đói, bệnh, bạo lực địa phương và che giấu thông tin — <b>không</b> thể mô tả đơn giản là thiên tai, nhưng cũng <b>không</b> đồng nghĩa "Đảng trực tiếp sát hại 30 triệu người". <b>1966–76 Cách mạng Văn hoá</b>: cơ chế là lãnh tụ → ý thức hệ → <b>Hồng Vệ Binh</b> → đánh <b>"Tứ cựu"</b> → thanh trừng → đấu tố → phe phái → quân đội tái lập trật tự; ~1,6 triệu người chết theo Walder, và cuối cùng chính bộ máy Đảng thành nạn nhân của cuộc cách mạng do lãnh tụ Đảng phát động. <b>1989 Thiên An Môn</b>: quân đội vào trung tâm Bắc Kinh, số người chết tới nay vẫn không được xác định chắc chắn.',
       a:'TRUNG ƯƠNG\n    ↓\nxác định "kẻ thù"\n    ↓\nTUYÊN TRUYỀN\n    ↓\nPHÂN LOẠI CON NGƯỜI\n    ↓\nđấu tố · tổ chức quần chúng\n    ↓\ncông an · cán bộ · toà án\n    ↓\ncả xã hội học thông điệp'},
      {h:'Pháp Luân Công và nội tạng — HAI mức bằng chứng khác nhau',
       p:'Có bằng chứng quốc tế lâu dài về <b>bắt giữ, giam giữ tuỳ tiện, tra tấn và đàn áp</b> người tập Pháp Luân Công từ 1999; các cơ chế nhân quyền LHQ đã nhiều lần nêu. Nhưng cáo buộc <b>cưỡng bức thu hoạch nội tạng phải tách riêng</b>: năm 2021 các chuyên gia độc lập của LHQ tuyên bố họ "báo động" trước những cáo buộc này. Đó là <b>yêu cầu Trung Quốc giải trình và cho giám sát độc lập</b> — không phải một bản án quốc tế đã kết tội.'},
      {h:'Hong Kong — xem ổ cắm "an ninh quốc gia" chạy thế nào',
       p:'2020 Luật An ninh Quốc gia → 2024 luật an ninh theo Điều 23 → không gian chính trị thu hẹp. Cao uỷ Nhân quyền LHQ nhiều lần chỉ trích tác động tới tự do ngôn luận, báo chí, hội họp; tháng 2/2026 kêu gọi trả tự do cho Jimmy Lai sau bản án 20 năm và nói tự do báo chí đã suy giảm mạnh kể từ 2020. Phía chính quyền đặt ổn định, an ninh quốc gia và chủ quyền lên trên. <b>Ghi cả hai hệ giá trị</b> — bỏ một bên là mất chính chỗ xung đột.'},
      {h:'Nói cho đúng về nhân quyền',
       p:'Đánh giá năm 2022 của OHCHR kết luận tại Tân Cương đã xảy ra <b>vi phạm nhân quyền nghiêm trọng</b>, và việc giam giữ tuỳ tiện, phân biệt đối xử với người Uyghur và các cộng đồng Hồi giáo khác <b>"có thể cấu thành tội ác chống loài người"</b>. Trung Quốc bác bỏ và nói đó là chương trình chống khủng bố, chống cực đoan và đào tạo nghề hợp pháp. Đến tháng 1/2026 các chuyên gia LHQ vẫn nêu lo ngại mới về cáo buộc <b>lao động cưỡng bức</b> đối với người Uyghur, người <b>Tây Tạng</b> và các nhóm thiểu số khác. Phải giữ đúng chữ:',
       a:'OHCHR:\n"may constitute crimes against humanity"\n\n         ≠\n\nmột toà án quốc tế\nĐÃ xét xử và tuyên bản án cuối cùng'}
    ]
  },
  {
    id:'doiung', n:6, t:'Đòn không đi một chiều — và ba nghịch lý của chính hệ thống',
    d:'Phần dễ bị bỏ nhất khi phân tích sức ép: Trung Quốc cũng nắm ổ cắm ngược lại, và hệ thống này tự sinh ra điểm yếu từ chính chỗ nó mạnh.',
    blocks:[
      {h:'Trung Quốc giữ ổ cắm NGƯỢC lại đối với phương Tây',
       p:'USGS năm 2026 ghi nhận Trung Quốc sản xuất <b>74 trong 77</b> loại khoáng sản được khảo sát và đứng <b>số một thế giới về sản lượng ở 39 loại</b>. Đây không phải ván cờ một chiều: một cuộc tách rời quá nhanh có thể tự gây lạm phát, thiếu linh kiện và gián đoạn chuỗi cung ứng cho chính bên gây áp lực.',
       a:'MỸ / EU              TRUNG QUỐC\n   │                     │\nCHIP                KHOÁNG SẢN\nTÀI CHÍNH           NAM CHÂM\nTHỊ TRƯỜNG          CHẾ BIẾN\n   │                CHẾ TẠO · PIN\n   │                     │\n   └──── phụ thuộc lẫn nhau ────┘'},
      {h:'Vì sao không thể lấy công thức đánh Liên Xô áp nguyên xi',
       p:'Liên Xô cuối kỳ có một tổ hợp rất khác: kinh tế kế hoạch, công nghệ kém, ít tích hợp thương mại toàn cầu. Trung Quốc hiện có thị trường, chế tạo khổng lồ, ngoại thương, doanh nghiệp tư nhân, SOE, ngân hàng nhà nước, kinh tế số, thị trường nội địa rất lớn và khoảng <b>3.416 tỷ USD dự trữ ngoại hối</b>. Đó là lý do nhiều dự báo kiểu "Trung Quốc sắp có Lehman" liên tục sai.'},
      {h:'Đòn bẩy lớn nhất không nằm ở MỘT nước — nằm ở LIÊN MINH',
       p:'Các ổ cắm nằm rải: Mỹ (tài chính, GPU, EDA, thị trường) · Hà Lan (quang khắc) · Nhật (thiết bị, vật liệu) · Hàn Quốc (memory, HBM) · Đài Loan (foundry) · EU (thị trường) · Trung Đông (năng lượng) · Nga (đường vòng) · ASEAN (chuyển tải và chế tạo) · vận tải biển toàn cầu. Nếu các nước không phối hợp, Trung Quốc đổi được thị trường, đổi nhà cung cấp, đổi tuyến logistics, dùng nước thứ ba, hoặc đầu tư nội địa hoá.'},
      {h:'Dân số — thuốc độc chậm, không phải cú sốc',
       p:'Năm 2025 Trung Quốc có <b>7,92 triệu ca sinh</b> nhưng <b>11,31 triệu ca tử</b>; tăng dân số tự nhiên <b>-2,41‰</b>. Nó không gây sụp ngay và vì thế hay bị bỏ khỏi bảng — nhưng trong 10–20 năm nó đi thẳng vào ổ cứng tài khoá.',
       a:'trẻ em ↓\n   ↓\nlao động ↓\n   ↓\nngười mua nhà ↓\n   ↓\ncơ cấu tiêu dùng đổi\n   ↓\nngười già ↑\n   ↓\nlương hưu + y tế ↑\n   ↓\nGÁNH NẶNG TÀI KHOÁ ↑'},
      {h:'Ba nghịch lý hệ thống tự sinh ra',
       p:'<b>1. Tập quyền:</b> mệnh lệnh rõ hơn, nhưng hệ phụ thuộc nhiều hơn vào chất lượng và tính liên tục của chính trung tâm — và câu hỏi kế vị càng khó xuất hiện khi lãnh đạo càng mạnh. <b>2. Kỷ luật:</b> siết mạnh thì tuân thủ tăng, nhưng cán bộ sợ sai → không quyết → tê liệt hành chính; chính Trung ương phải vừa đòi "không tham nhũng" vừa chống "không làm gì". <b>3. Thông tin:</b> cấp dưới muốn thăng chức nên báo cáo đẹp, trung ương nhận dữ liệu méo — Đại Nhảy Vọt là ví dụ lịch sử của đúng chuỗi đó. Số hoá tăng khả năng lấy dữ liệu nhưng <b>không tự loại bỏ</b> động cơ chính trị làm méo thông tin.',
       a:'CONTROL ↑\n   ↓\nFEAR ↑\n   ↓\nINITIATIVE ↓'},
      {h:'Thang chuyển lỗ có bao nhiêu bậc — và bậc cuối là ai',
    p:'Đây là điểm MẠNH của hệ thống, và cũng là chỗ nó cạn. Một nền kinh tế thông thường thì chủ đầu tư vỡ kéo ngân hàng vỡ. Trung Quốc có nhiều bậc hơn: lỗ đi từ chủ đầu tư → ngân hàng gia hạn → tái cấp vốn → LGFV và tỉnh → hoán đổi nợ → trung ương phát trái phiếu đặc biệt. <b>Lỗ không biến mất, nhưng nó DI CHUYỂN QUA HỆ THỐNG</b> — và đó là lý do rất nhiều dự đoán "Trung Quốc sắp Lehman" đã sai.<br><br>Nguy hiểm không nằm ở một bậc nào, mà ở lúc <b>không còn nơi để chuyển</b>: hộ gia đình không muốn gánh nữa, doanh nghiệp tư nhân lợi nhuận quá mỏng, chính quyền địa phương nợ quá cao, ngân hàng bảng cân đối yếu, SOE hiệu quả thấp. Khi các bậc trên đều đầy thì <b>trung ương là NGƯỜI GÁNH CUỐI</b> — và chính IMF cũng nói nếu có một đợt giảm tốc mạnh do giảm đòn bẩy trên diện rộng thì hỗ trợ tài khoá bổ sung nên đến từ chính quyền trung ương và nằm TRÊN bảng cân đối ngân sách chính thức, tức thôi giấu ngoài bảng.',
    a:'HỘ GIA ĐÌNH   ✗ không muốn gánh nữa\n     ↓\nDN TƯ NHÂN    ✗ lợi nhuận quá mỏng\n     ↓\nĐỊA PHƯƠNG    ✗ nợ quá cao\n     ↓\nNGÂN HÀNG     ✗ bảng cân đối yếu\n     ↓\nSOE           ✗ hiệu quả thấp\n     ↓\n───────────────────────────\nTRUNG ƯƠNG    ← NGƯỜI GÁNH CUỐI'},
   {h:'Ngày 19/8/2026 — một ngày cho thấy nền kinh tế HAI TỐC ĐỘ',
    p:'Hôm đó thị trường Trung Quốc bán tháo: Shanghai Composite đóng cửa giảm ~2,4%, Shenzhen Component giảm tới ~5,01%; trong phiên chỉ số robot giảm hơn 6%, bán dẫn khoảng 7%. Nhưng CÙNG NGÀY, Unitree Robotics tăng gần 500% trong phiên IPO.<br><br>Hai dữ kiện đó không mâu thuẫn — chúng là cùng một hiện tượng. Đây không phải \'mọi người tháo chạy khỏi Trung Quốc\' mà là một cuộc <b>định giá lại cực mạnh BÊN TRONG</b>: bán thứ có lợi nhuận yếu và cầu nội địa yếu, mua thứ nằm trong danh mục chiến lược quốc gia. Đó chính là thang chuyển lỗ ở trên nhìn từ phía thị trường: vốn tự động rời khỏi những bậc không ai đỡ.<br><br>Một con số lan rất rộng hôm đó — \'1,65 nghìn tỷ NDT vốn hoá bị xoá trong một ngày\' — thì <b>chưa xác minh được</b> từ nguồn chính thống; nó có thể là phép tính riêng của một tài khoản mạng xã hội. Xu hướng thật, con số chưa đứng được, nên ghi rõ ra chứ đừng dùng.',
    a:'BÁN                     MUA\nlợi nhuận yếu       →   danh mục quốc gia\ncầu nội địa yếu     →   AI · chip · robot\nbất động sản        →   EV · quốc phòng\n\n        CÙNG MỘT NGÀY\n     Shenzhen −5,01%\n     Unitree   +500%'},
   {h:'Và đúng lúc đó an ninh chịu một cái kéo KÉP',
    p:'Đây là chỗ tài khoá chạm vào ổ cắm cứng thứ ba. Kinh tế xuống → thất nghiệp tăng → bất mãn xã hội tăng → <b>KHỐI LƯỢNG VIỆC của an ninh tăng</b>. Cùng lúc đó tài khoá yếu → nguồn lực địa phương giảm → <b>KHẢ NĂNG CHI cho an ninh bị ép</b>. Nhu cầu tăng trong khi năng lực nuôi giảm — hai mũi kéo ngược chiều trên cùng một cơ quan. Tài liệu nguồn gọi đúng tình trạng ấy là an ninh <b>QUÁ TẢI</b>, và xếp nó vào cấp 4 — cấp cuối trước khi tới rạn nứt elite. Đó mới là mối nguy chứ không phải bản thân con số tăng trưởng.<br><br>Nhưng Bắc Kinh biết rõ điều đó, nên trong khủng hoảng <b>không phải mọi khoản bị cắt ngang nhau</b>: báo cáo ngân sách 2026 vẫn đặt quốc phòng, ngoại giao và chính pháp trong nhóm phải bảo đảm nguồn lực. Đó cũng là lý do "làm dân nghèo đi" chưa chắc làm chế độ sụp — hệ thống chịu được mức sống giảm nếu vẫn giữ được lương an ninh, lương cán bộ, lương thực, năng lượng và hệ ngân hàng. Phân tích chỉ dựa trên GDP rất dễ sai ở đúng chỗ này.',
    a:'kinh tế ↓                 tài khoá ↓\n    ↓                         ↓\nthất nghiệp ↑           nguồn lực ↓\n    ↓                         ↓\nbất mãn ↑                     ↓\n    ↓                         ↓\nVIỆC của an ninh ↑   TIỀN nuôi an ninh ↓\n        ╲                   ╱\n         ╲                 ╱\n          CÙNG MỘT CƠ QUAN'},
   {h:'Xếp hạng chín ổ cắm theo khả năng gây STRESS HỆ THỐNG',
       p:'Không phải ổ nào cũng nặng bằng nhau, và thứ tự này ngược với trực giác thông thường — thứ đứng đầu nằm BÊN TRONG, không phải Hormuz.',
       a:'1  BẤT ĐỘNG SẢN + LGFV + NGÂN HÀNG   ██████████  đã nằm bên trong\n2  XUẤT KHẨU + THỊ TRƯỜNG MỸ/EU      █████████░  khi nội địa yếu\n3  TẦNG CÔNG NGHỆ TIÊN TIẾN          █████████░  cực mạnh DÀI HẠN\n4  DẦU + VẬN TẢI BIỂN                ████████░░  kinh tế rất nhạy\n5  THANH TOÁN TÀI CHÍNH              ████████░░  mạnh, nhưng đệm dày\n6  NGA / HẬU PHƯƠNG LỤC ĐỊA          ██████░░░░  là ĐỆM, không phải đòn\n7  DÂN SỐ                            ██████░░░░  chậm nhưng sâu\n8  BIỂN ĐEN riêng lẻ                 ████░░░░░░  chủ yếu khuếch đại\n9  THỐNG NHẤT ELITE + AN NINH        ██████████  không phải kinh tế,\n                                                 nhưng QUYẾT ĐỊNH'},
      {h:'Kịch bản nguy hiểm nhất không phải một đòn — mà NĂM VÒNG cùng quay ngược',
       p:'Từng cú sốc riêng lẻ đều hấp thụ được. Thứ đổi tính chất là khi năng lượng, công nghệ, thị trường xuất khẩu, bất động sản và niềm tin cùng xấu một lúc — lúc đó trung ương phải cứu ngân hàng, địa phương, việc làm, bất động sản, tỷ giá và doanh nghiệp CÙNG LÚC, và gánh nặng tài khoá mới thật sự bật lên.',
       a:'[1] NĂNG LƯỢNG · VẬN TẢI      chi phí sản xuất ↑\n[2] CÔNG NGHỆ                 năng suất · ngành chiến lược ↓\n[3] THỊ TRƯỜNG XUẤT KHẨU      đơn hàng ↓\n         └──── cả ba ────┐\n                         ↓\n        lợi nhuận ↓ · việc làm ↓ · tiêu dùng ↓\n\n[4] BẤT ĐỘNG SẢN   bán đất ↓ → LGFV → NGÂN HÀNG\n[5] NIỀM TIN       vốn tìm chỗ an toàn → tỷ giá → tín dụng\n                         ↓\n              TRUNG ƯƠNG PHẢI CỨU TẤT CẢ\n                         ↓\n                 GÁNH NẶNG TÀI KHOÁ ↑'},
      {h:'Và cascade chạy HAI chiều',
       p:'Không chỉ kinh tế → chính trị. Còn chiều ngược: rạn nứt lãnh đạo → cán bộ không biết nghe ai → chính sách thực thi kém → kinh tế xuống → tài khoá xuống → an ninh chịu áp lực. Khi <b>hai chiều cùng quay một lúc</b> thì mới thành xoáy tự khuếch đại — và đó mới là thứ một hệ thống quyền lực thật sự sợ.',
       a:'KINH TẾ → CHÍNH TRỊ\n       và\nCHÍNH TRỊ → KINH TẾ\n       ↓\nxoáy tự khuếch đại'}
    ]
  }
];

/* Mắt xích nào sáng theo cái gì — xem chú thích đầy đủ ở data.js.

   Ba mắt xích kinh tế thường (lợi nhuận · việc làm · tiêu dùng) cố ý
   để ['max'] rỗng, tức XÁM. Đó không phải thiếu sót mà là chính thông
   điệp của bảng đồng hồ Trung Quốc: nó không đo kinh tế thường, vì một
   chế độ có thể nghèo đi rất nhiều mà vẫn đứng. Muốn biết tăng trưởng
   thì có hàng trăm bảng khác; bảng này đo thứ khác. */
/* Thứ nằm GIỮA các mắt xích và làm chậm cú sốc. Khai theo chủ thể
   vì bộ đệm của mỗi nước khác hẳn nhau. */
const DEM = ['than nội địa và dự trữ chiến lược', 'dự trữ ngoại hối ~3,416 nghìn tỷ USD',
  'kiểm soát vốn', 'ngân hàng quốc doanh gia hạn được nợ', 'trái phiếu đặc biệt của trung ương',
  'tiết kiệm rất cao của hộ gia đình'];
const CHAIN_SRC = {
  nangluong:['th','nangluong'], congnghe:['th','congnghe'],
  thuongmai:['th','thuongmai'], hanghai:['th','hanghai'], nga:['th','nga'],

  loinhuan:['max'], vieclam:['max'], tieudung:['max'],

  bds:['gg','bandat'], lgfv:['gg','lgfv'], nganhang:['gg','bomvon'],

  taikhoa:['max','thudiaphuong','chuyengiao','tambao'],
  canbo:['max','khongdam','thanhloc','menhlenh'],
  anninh:['max','nhansu','chuoilenh'],
  elite:['max','batdong','nhansu'],
  chedo:['max','chuoilenh','batdong','tambao']
};

const SOLIEU = [
  'Trung Quốc tháng 7/2026: bán lẻ chỉ +0,6% trong khi sản xuất công nghiệp +4,5% — đầu ra vẫn chạy nhanh hơn khả năng hấp thụ của thị trường nội địa. Đầu tư tài sản cố định 7 tháng −6,7%.',
  'Tín dụng ngân hàng mới tháng 7/2026 CO LẠI 340 tỷ NDT — mức giảm lớn nhất từng ghi nhận; riêng vay hộ gia đình giảm 460,3 tỷ NDT. Lãi suất đã thấp mà dân vẫn không vay thì vấn đề nằm ở KỲ VỌNG, không phải giá tiền.',
  'Xuất khẩu tháng 7/2026 +23,9%; bán dẫn 7 tháng gần gấp đôi, hàng công nghệ cao +40,7%. Xuất khẩu đang gánh phần cầu nội địa yếu — nên nó vừa là phao vừa là chỗ dễ tổn thương khi hàng rào dựng lên.',
  'Thất nghiệp đô thị nhóm trẻ tăng từ 14,9% (tháng 6) lên 17,9% (tháng 7/2026), cao nhất 11 tháng.',
  'Doanh thu bán quyền sử dụng đất của chính quyền địa phương nửa đầu 2026 giảm 31,5%, còn ~978 tỷ NDT. Giá nhà mới tháng 7 giảm 3,2% so cùng kỳ, mà ~52% tài sản hộ gia đình gắn với bất động sản.',
  'Kho dầu chiến lược và thương mại ước hơn 1,2 tỷ thùng; tháng 7/2026 còn tích thêm ~210.000 thùng/ngày — nên cú sốc Hormuz với Trung Quốc là chuyện GIÁ, chưa phải chuyện THIẾU.',
  'Ngày 19/8/2026, ảnh vệ tinh cho thấy hoàn thành giai đoạn đầu đảo nhân tạo tại Antelope Reef thuộc Hoàng Sa — dài gần 6 km, có cảng nước sâu. Cùng ngày thị trường trong nước bán tháo mạnh: suy yếu kinh tế KHÔNG đồng nghĩa lùi bước chiến lược.',
  'Trung Quốc năm 2024 tiêu thụ ~16,3 triệu thùng dầu/ngày, sản xuất nội địa ~4,3 triệu, nhập ~11,1 triệu — theo EIA.',
  'Nguồn nhập dầu 2024: Nga ~20%, Saudi ~14%, Iran ~11%, Iraq ~10% — theo EIA.',
  'Mỹ 14,7% và EU 14,5% trong xuất khẩu hàng hoá Trung Quốc năm 2025 — theo WTO.',
  'Dự trữ ngoại hối chính thức cuối tháng 6/2026 khoảng 3.416 tỷ USD — theo SAFE.',
  'Đầu tư phát triển bất động sản năm 2025 giảm 17,2% — theo Cục Thống kê Quốc gia.',
  '"Nợ ẩn" của chính quyền địa phương ước khoảng 14,3 nghìn tỷ NDT năm 2023 — theo IMF dẫn số nhà chức trách.',
  'Cuối 2025: ~101,286 triệu đảng viên và 5,431 triệu tổ chức cơ sở đảng — theo nguồn chính thức.',
  'Năm 2025 hệ thống kỷ luật lập ~1,012 triệu vụ, lưu trí ~47.000 người và ra ~983.000 quyết định — theo CCDI.',
  'Ngân sách 2026: thâm hụt ~5,89 nghìn tỷ NDT (~4% GDP), riêng trung ương 5,09 nghìn tỷ — theo Bộ Tài chính.',
  'Trung ương dự kiến chuyển ~10,415 nghìn tỷ NDT cho địa phương, trong khi địa phương tự thu ~12,503 nghìn tỷ — theo Bộ Tài chính.',
  '4,4 nghìn tỷ NDT trái phiếu đặc biệt địa phương và 300 tỷ NDT bổ sung vốn cho các ngân hàng quốc doanh lớn — theo Bộ Tài chính.',
  'Năm 2025: 7,92 triệu ca sinh, 11,31 triệu ca tử, tăng dân số tự nhiên -2,41‰ — theo Cục Thống kê Quốc gia.',
  'Xuất khẩu tính bằng USD tháng 1–5/2026 tăng 15,5% so với cùng kỳ — theo World Bank.',
  'USGS 2026: Trung Quốc sản xuất 74 trong 77 khoáng sản được khảo sát và đứng số một thế giới về sản lượng ở 39 loại.',
  'Điểm đến xuất khẩu 2025: Mỹ 14,7% · EU 14,5% · Hong Kong 8,1% · Việt Nam 4,5% · Nhật 4,3% · Hàn Quốc 4,1% · Ấn Độ 3,4% · Nga 3,2% — theo WTO.',
  'Cuối 2025 còn ~201.000 tổ chức đảng trong các tổ chức xã hội — theo nguồn chính thức.',
  'CCDI 2025 xử lý ~1,976 triệu manh mối và mở ~789.000 vụ — theo CCDI.',
  'Nghiên cứu 2026: trong 33 văn kiện trung ương về xây dựng đảng ở các "tổ chức mới", 21 văn kiện xuất hiện sau khi Tập nắm quyền.'
];

/* Bốn phía của Trung Quốc KHÔNG cùng loại với Việt Nam. Việt Nam bị
   kẹp giữa các nguồn cú sốc vật chất; Trung Quốc thì ba phía ngoài chỉ
   là LỚP GÂY SỐC, còn thứ quyết định nằm ở LÕI — ba ổ cứng tài khoá,
   an ninh, cán bộ. Nên lõi ở đây không phải một chiến trường bấm vào
   được, mà là chính bộ máy. */
const COMPASS = {
  chuong:'Lớp ngoài và lõi',
  tieu:'Ba phía ngoài chỉ gây sốc — thứ quyết định nằm ở lõi',
  lede:'Khác Việt Nam ở chỗ căn bản: ba hướng ngoài <b>không tự làm chế độ sụp</b>. Chúng chỉ nguy hiểm khi biến thành <b>xung đột phân phối bên trong</b> — và đó là việc của lõi, không phải của cú sốc.',
  loi:{co:'☭', ten:'ĐCSTQ', d:'tài khoá · an ninh · cán bộ', th:null},
  huong:[
    {v:'n', side:'PHÍA TRÊN', t:'Năng lượng', p:'Hormuz · Malacca · Nga — nhập ~11,1 triệu thùng/ngày, nhưng nguồn đã chia rộng.', th:'nangluong'},
    {v:'w', side:'PHÍA TRÁI', t:'Công nghệ & tài chính', p:'Chip tiên tiến, EDA, thiết bị, đô la — đòn bẩy chọn lọc nhất, mạnh về dài hạn.', th:'congnghe'},
    {v:'e', side:'PHÍA PHẢI', t:'Thương mại', p:'Mỹ + EU ≈ 29% xuất khẩu — đánh đúng cái van đang bù cho nội địa yếu.', th:'thuongmai'},
    {v:'s', side:'PHÍA DƯỚI', t:'Nội bộ', p:'Bất động sản → LGFV → ngân hàng → niềm tin → tiêu dùng → việc làm.', th:null}
  ],
  ket:'Ba phía ngoài có thể làm Trung Quốc <b>nghèo đi</b> mà chế độ vẫn đứng. Chỉ khi cú sốc vật chất chuyển thành <b>khủng hoảng phân phối trong tầng lãnh đạo</b>, rồi làm chuỗi cán bộ và chuỗi an ninh không còn cùng hướng, bài toán mới đổi từ kinh tế sang quyền lực.'
};

/* ── SỐ ĐO TỰ ĐỘNG ──────────────────────────────────────────
   PHẢI ĐỌC TRƯỚC KHI THÊM DÒNG: mười hai đồng hồ của Trung Quốc
   đều đo TÀI KHOÁ và QUYỀN LỰC — thu địa phương, LGFV, tam bảo,
   thanh lọc cán bộ, chuỗi mệnh lệnh. Không cái nào có nguồn công
   khai miễn phí đủ tin, nên cả mười hai Ở LẠI ĐẶT TAY. Đó không
   phải thiếu sót mà là chính luận điểm: GDP là đồng hồ tệ nhất để
   đo số phận một chế độ.

   Sáu dòng dưới là SỐ ĐO NỀN — 'gg' đều null, tức chúng KHÔNG
   thắp đồng hồ nào. Chúng chỉ nói lớp cú sốc bên ngoài đang căng
   hay chùng, và mỗi dòng dùng đúng một nguồn đã chạy thật bên
   Việt Nam, không thêm API mới, không thêm khoá.
   ────────────────────────────────────────────────────────── */
const DODAC = [
  {id:'brent', gg:null, th:'nangluong', nhan:'Dầu Brent', dv:'USD/thùng',
   nguon:'yahoo', ma:'BZ=F', g:75, r:90,
   ghi:'Cùng một số với bảng Việt Nam — cú sốc Hormuz đánh cả hai nước, đó là điểm chứ không phải trùng lặp.',
   can:'Trên 90 là vượt vùng dự báo EIA; dưới 75 là về mức trước xung đột.'},
  {id:'nhandante', gg:null, th:'taichinh', nhan:'USD/CNY', dv:'nhân dân tệ',
   nguon:'erapi', ma:'CNY', g:7.00, r:7.30,
   ghi:'Lấy chung một lượt gọi với USD/VND — cùng phản hồi, không tốn thêm lượt nào.',
   can:'NGƯỠNG TẠM, neo vào lượt đo đầu tiên (6,76). Vượt 7,30 kéo dài mới là áp lực dòng vốn ra thấy rõ.'},
  {id:'bandan', gg:null, th:'congnghe', nhan:'Chỉ số bán dẫn (SOXX)', dv:'USD',
   nguon:'yahoo', ma:'SOXX', g:480, r:400, nghich:true,
   ghi:'Chỉ báo THAY THẾ và phải đọc rất cẩn thận: nó đo sức khoẻ NGÀNH bán dẫn toàn cầu, KHÔNG đo năng lực chip của Trung Quốc. Ngành nóng lên không có nghĩa Trung Quốc tiếp cận được tầng tiên tiến.',
   can:'NGƯỠNG TẠM, neo vào lượt đo đầu tiên (521 USD) chứ chưa có chuỗi dài để hiệu chỉnh — cùng hạng yếu với đồng hồ văn bản liên bang bên Việt Nam. Đọc để theo nhịp, không để kết luận.'},
  {id:'thitruongtq', gg:null, th:'thuongmai', nhan:'Quỹ ETF Trung Quốc (FXI)', dv:'USD',
   nguon:'yahoo', ma:'FXI', g:38, r:30, nghich:true,
   ghi:'Chỉ báo THAY THẾ — đánh giá của nhà đầu tư nước ngoài về cổ phiếu Trung Quốc, đối xứng với VNM bên Việt Nam.',
   can:'Đặt theo biên độ quan sát. Đỏ khi về sát đáy vùng giao dịch.'},
  {id:'vanban', gg:null, th:'thuongmai', nhan:'Văn bản liên bang Mỹ nhắc Trung Quốc', dv:'văn bản / 30 ngày',
   nguon:'fedreg', ma:'China', g:150, r:250,
   ghi:'Đếm NHỊP ĐỘ chú ý của bộ máy quản lý Mỹ, không đếm mức nghiêm trọng. Nền cao hơn Việt Nam nhiều nên ngưỡng cũng khác.',
   can:'Nền quan sát ở lượt đo đầu: 128 văn bản/30 ngày — cao hơn Việt Nam khoảng bốn lần. NGƯỠNG YẾU, chưa đủ chuỗi để hiệu chỉnh. Đọc như nhịp độ chú ý, không phải mức nghiêm trọng.'},
  /* Sắc thái tin GDELT đã gỡ 20/08/2026 — nguồn hỏng 7 lượt liền, xem
     đầu scripts/build-quantrac.mjs. KHÔNG thay bằng gì: bảng này đã có
     FXI, Hang Seng và chỉ số thị trường, thêm nữa là thừa. */
  {id:'hangseng', gg:null, th:'taichinh', nhan:'Hang Seng', dv:'điểm',
   nguon:'yahoo', ma:'^HSI', g:25000, r:23000, nghich:true,
   ghi:'Chỉ báo THAY THẾ cho đánh giá của thị trường về Trung Quốc–Hong Kong. Nó KHÔNG đo tài khoá hay chuỗi mệnh lệnh — tức không đo thứ mười hai đồng hồ đang đo. Đọc như nhiệt kế niềm tin bên ngoài.',
   can:'Biên độ 3 tháng quan sát được: 22.672–26.038. Xanh khi ≥25.000, đỏ khi ≤23.000.'}
];


/* ═══════════════════════════════════════════════════════
   BO MẠCH QUYỀN LỰC — hai mươi ổ cắm

   Vì sao đây là MỤC RIÊNG chứ không nằm trong hồ sơ Hướng Hoa
   Cường như trước: đây là bản đồ bộ máy ĐCSTQ. Nó không phụ thuộc
   vào việc có soi nhà Hướng hay không, và người muốn hiểu bộ máy
   không nên phải mở hồ sơ một doanh nhân Hong Kong mới thấy nó.
   Đặt sai chỗ thì một bản đồ tốt vẫn không ai tìm ra.

   MỖI Ổ CẮM CÓ BỐN Ô, và ô thứ ba mới là ô đáng giá:
     · ai đang nắm
     · cơ quan
     · ĐƯỜNG CHỈ HUY — mệnh lệnh chạy theo lối nào
     · CHẠM TỚI — nó với tay được đến đâu

   Chỉ hai ô đầu thì đây là một danh bạ. Có ô thứ ba và thứ tư thì
   nó mới trả lời được câu hỏi thật: đánh vào đây thì cái gì động.

   ── VÀ ĐÂY LÀ CHỖ PHẢI DỪNG LẠI ─────────────────────────
   Tài liệu nguồn đề xuất một tầng nữa — "phiên bản 3.0": mỗi
   người thì xuất thân phe nào, ai nâng đỡ, từng giữ chức ở tỉnh
   nào, doanh nghiệp nào nằm dưới đường quyền lực của họ.

   Tầng đó KHÔNG dựng ở đây, vì tài liệu mới chỉ ĐỀ XUẤT chứ chưa
   đưa bằng chứng cho nó. Suy phe phái từ chức vụ là đúng thứ mà
   chính cung này liệt vào "sáu dấu ≠" — quan hệ không phải chỉ
   huy. Bịa một cây phả hệ chính trị rồi vẽ nó ra thành sơ đồ là
   cách nhanh nhất biến một bản đồ thành thuyết âm mưu.
   ═══════════════════════════════════════════════════════ */
const BOMACH = {
  lede:'Không nhìn Trung Quốc như một chính phủ có vài bộ ngành, mà như một hệ điều hành nhiều lớp. Điều lệ ĐCSTQ tự viết Đảng là "lực lượng lãnh đạo chính trị cao nhất" và "Đảng lãnh đạo tất cả" — nên nhà nước là một LỚP rất lớn của hệ thống, không phải tầng quyền lực tối cao.',
  a:'                    Ý THỨC HỆ\n                        │\n                      ĐẢNG\n                        │\n      ┌─────────────────┼─────────────────┐\n   NHÂN SỰ         THÔNG TIN          AN NINH\n      │                │                 │\n  Tổ chức          Tuyên truyền      Chính pháp\n  cán bộ           · CAC             MPS · MSS\n      └─────────────────┼─────────────────┘\n                        │\n                   ĐẢNG–NHÀ NƯỚC\n                        │\n      ┌─────────┬───────┼───────┬─────────┐\n  Quốc vụ    Quốc hội  Toà   Kiểm sát  Quân uỷ\n     viện                                  │\n      │                                   PLA\n   KINH TẾ\n      │\n  SOE · ngân hàng · doanh nghiệp tư nhân\n      │\n                   1,4 TỶ NGƯỜI',
  ghi:'Cuối 2025: <b>101,286 triệu đảng viên</b> và <b>5,431 triệu tổ chức cơ sở</b> — trong đó ~1,692 triệu nằm trong doanh nghiệp và ~201.000 trong tổ chức xã hội. Nên khi nói "Trung ương quyết", đừng hình dung một trăm người ở Bắc Kinh; hình dung một mạng thần kinh tổ chức bảy tầng từ bảy người Thường vụ xuống tới tổ dân phố.',
  tang:[
    {id:'loi', n:1, tn:'Lõi', acc:'#f0503f', t:'LÕI — ổ cắm giữ cả hệ thống lại với nhau',
     d:'Bốn ổ đầu tiên không điều hành ngành nào cả. Chúng quyết ai được làm, ai bị loại, và ai biết chuyện gì — tức là quyết cả những người điều hành ngành.',
     ds:[
      {ten:'Tập Cận Bình', o:'Tổng Bí thư · Chủ tịch nước · Chủ tịch Quân uỷ Trung ương',
       chi:'Ba chức, nhưng chức mạnh nhất KHÔNG phải Chủ tịch nước — mà là Tổng Bí thư và Chủ tịch Quân uỷ.',
       cham:'Toàn hệ. Đồng thời trực tiếp đứng đầu Uỷ ban An ninh Quốc gia Trung ương.',
       ghi:'Tính đến 8/2026 vẫn giữ cả ba.'},
      {ten:'Thường vụ Bộ Chính trị', o:'7 người: Tập · Lý Cường · Triệu Lạc Tế · Vương Hộ Ninh · Thái Kỳ · Đinh Tiết Tường · Lý Hi',
       chi:'Bo mạch trung tâm. Nhưng mỗi người KHÔNG chỉ phụ trách một "bộ" — họ ngồi ở điểm nối nhiều hệ thống.',
       cham:'Đảng · chính phủ · quốc hội · chính hiệp · kỷ luật.',
       ghi:'Ngày 8/1/2026 chính Thường vụ nghe báo cáo công tác của các đảng đoàn thuộc Quốc hội, Quốc vụ viện, Chính hiệp, Toà án Tối cao và Viện Kiểm sát Tối cao — bằng chứng trực tiếp nhất cho việc nhà nước nằm DƯỚI lớp đảng.'},
      {ten:'Thái Kỳ', o:'Thường vụ · Bí thư Ban Bí thư · Chủ nhiệm Văn phòng Trung ương',
       chi:'Nếu Tập là CPU thì Văn phòng Trung ương là bus dữ liệu: lịch lãnh đạo, văn kiện mật, chỉ thị, luồng tin lên và luồng quyết định xuống.',
       cham:'Mọi bộ · tỉnh · cơ quan trung ương đều đi qua đây cả hai chiều.',
       ghi:'Quyền lực THÔNG TIN rất dễ bị bỏ sót khi người ta chỉ nhìn chức danh bộ trưởng. Đây là một trong những "gatekeeper" quan trọng nhất quanh Tập.'},
      {ten:'Thạch Thái Phong', o:'Trưởng Ban Tổ chức Trung ương',
       chi:'Trung ương → Ban Tổ chức → tỉnh uỷ → ban tổ chức tỉnh → thành phố → huyện → cán bộ.',
       cham:'Ai làm bí thư tỉnh, ai vào bộ, ai được luân chuyển, ai bị đánh giá kém.',
       ghi:'Ổ cắm mạnh nhất bảng, và lý do rất phản trực giác: <b>nếu kiểm soát được đường thăng tiến thì không cần gọi điện ra lệnh từng ngày</b>. Người ở dưới tự học cách đoán Trung ương muốn gì. Đó là cơ chế TỰ CĂN CHỈNH.'},
      {ten:'Lý Hi · Lưu Kim Quốc', o:'Bí thư CCDI · và Phó Bí thư CCDI kiêm Chủ nhiệm Uỷ ban Giám sát Quốc gia',
       chi:'Một bộ máy hai danh nghĩa: CCDI là kỷ luật ĐẢNG, Uỷ ban Giám sát là giám sát NHÀ NƯỚC. Cán bộ bị xử đi qua kỷ luật đảng trước, có dấu hiệu hình sự mới chuyển kiểm sát.',
       cham:'Mọi cán bộ, mọi cấp, kể cả tướng lĩnh.',
       ghi:'Năm 2025: ~1,012 triệu vụ được lập, ~47.000 người bị lưu trí, ~983.000 quyết định kỷ luật. Đây không phải một văn phòng tượng trưng.'}
     ]},
    {id:'cuongche', n:2, tn:'Cưỡng chế & thông tin', acc:'#d29922', t:'CƯỠNG CHẾ VÀ THÔNG TIN',
     d:'Năm hòn đảo — công an, an ninh, toà, kiểm sát, tư pháp — KHÔNG độc lập với nhau; phía trên có một trục điều phối chính trị.',
     ds:[
      {ten:'Trần Văn Thanh', o:'Bí thư Uỷ ban Chính pháp Trung ương',
       chi:'Trung ương Đảng → Uỷ ban Chính pháp → công an · toà án · kiểm sát · an ninh nhà nước.',
       cham:'Toàn bộ hệ cưỡng chế và tư pháp.',
       ghi:'Hội nghị Chính pháp Trung ương 1/2026 tiếp tục yêu cầu "sự lãnh đạo TUYỆT ĐỐI của Đảng". Nhưng phải giữ đúng ranh: lãnh đạo chính trị hệ thống ≠ Tập quyết từng bản án.'},
      {ten:'Vương Tiểu Hồng', o:'Bộ trưởng Công an · đồng thời Bí thư Ban Bí thư',
       chi:'Trật tự · tội phạm · hộ khẩu · an ninh nội địa · quản lý hành chính.',
       cham:'Đời sống thường ngày của dân, ở mọi cấp xuống tới tổ dân phố.',
       ghi:'Việc một bộ trưởng công an đồng thời ngồi Ban Bí thư cho thấy dây thần kinh cưỡng chế nối thẳng lên tầng điều phối của Đảng.'},
      {ten:'Trần Nhất Tâm', o:'Bộ trưởng An ninh Nhà nước',
       chi:'Phản gián · tình báo · an ninh quốc gia — KHÁC hẳn công an.',
       cham:'Hoạt động bị coi là đe doạ nhà nước, trong và ngoài nước.',
       ghi:'Trộn MPS với MSS là lỗi thường gặp nhất khi đọc tin về Trung Quốc.'},
      {ten:'Lý Thư Lỗi · Trang Vinh Văn', o:'Trưởng Ban Tuyên truyền · và Phó Ban kiêm người đứng đầu CAC',
       chi:'Hai nhánh: NGĂN CHẶN (kiểm duyệt, lọc) và TẠO RA (tự sự, tin, lịch sử, ý thức hệ).',
       cham:'Báo chí · xuất bản · điện ảnh · giáo dục tư tưởng · Internet · nền tảng · thuật toán · AI · dữ liệu.',
       ghi:'Chỉ nhìn Great Firewall là mất một nửa hệ thống. Mục tiêu không chỉ là "bạn không được đọc X" mà còn là "đây là cách X nên được hiểu". Quy định GenAI đòi nội dung phù hợp "giá trị cốt lõi xã hội chủ nghĩa".'},
      {ten:'Quân uỷ Trung ương · PLA', o:'Tập (Chủ tịch) · Trương Hựu Hiệp · Trương Thăng Dân (Phó) · Lưu Chấn Lập (Uỷ viên)',
       chi:'ĐẢNG → QUÂN UỶ → PLA. Không phải NHÀ NƯỚC → quân đội độc lập chính trị.',
       cham:'PLA · và PAP nằm trong cụm an ninh vũ trang liên quan.',
       ghi:'Danh sách ngắn bất thường sau các đợt thanh lọc 2023–26 (Hà Vệ Đông, Miêu Hoa và nhiều tướng khác bị khai trừ). Nhưng thanh lọc ≠ elite split: nó chứng minh tướng cấp cao KHÔNG đứng ngoài kỷ luật đảng, chứ chưa chứng minh PLA đang chống Tập.'}
     ]},
    {id:'tien', n:3, tn:'Tiền & công nghệ', acc:'#58a6ff', t:'TIỀN · CÔNG NGHỆ · VÀ QUYỀN SỬA CHÍNH BO MẠCH',
     d:'Cải cách 2023 là chìa khoá hiểu "CCP 2.0": Trung ương lập thêm một tầng uỷ ban chiến lược NẰM TRÊN các bộ quản lý nhà nước.',
     ds:[
      {ten:'Lý Cường · Hà Lập Phong', o:'Chủ nhiệm Uỷ ban Tài chính Trung ương · và Chủ nhiệm Văn phòng kiêm Bí thư Uỷ ban Công tác Tài chính Trung ương',
       chi:'ĐCSTQ → Uỷ ban Tài chính TW → thiết kế tầng đỉnh → bộ quản lý nhà nước (PBOC · NFRA · CSRC) → ngân hàng, bảo hiểm, chứng khoán.',
       cham:'Hướng tín dụng · rủi ro hệ thống · ưu tiên chiến lược · nhân sự cao cấp · ổn định tài chính.',
       ghi:'Văn kiện cải cách nói thẳng mục tiêu là "tăng cường sự lãnh đạo tập trung thống nhất của Trung ương Đảng đối với công tác tài chính". KHÔNG suy ra được "Tập phê duyệt từng khoản vay".'},
      {ten:'Đinh Tiết Tường', o:'Thường vụ · Phó Thủ tướng · đứng đầu Uỷ ban Khoa học Công nghệ Trung ương',
       chi:'Uỷ ban KHCN TW → MIIT · NDRC · MOST → quỹ nhà nước và ngân hàng → tỉnh → phòng thí nghiệm, đại học, doanh nghiệp.',
       cham:'AI · bán dẫn · vũ trụ · lượng tử · sinh học · phòng thí nghiệm quốc gia · phối hợp quân–dân.',
       ghi:'Đây là <b>whole-of-nation / cử quốc thể chế</b> phiên bản công nghệ: Huawei, SMIC, CATL và các "national champions" được kỳ vọng tham gia cùng phòng thí nghiệm, startup và doanh nghiệp khác trong một mô hình đổi mới do Trung ương định hướng. Sau bước này, khoa học không còn là một bộ chuyên môn — nó được đặt vào an ninh + công nghiệp + cạnh tranh Mỹ–Trung + quân sự cùng lúc.'},
      {ten:'Trình Phúc Ba', o:'Người đứng đầu SASAC',
       chi:'Đảng → SASAC → doanh nghiệp nhà nước trung ương.',
       cham:'Điện · dầu khí · viễn thông · hạ tầng · công nghiệp quốc phòng.',
       ghi:'Ghép SOE + ngân hàng quốc doanh + quỹ chính phủ + chính quyền địa phương thì ra khả năng TẬP TRUNG VỐN rất lớn — thứ một nền kinh tế phi tập trung hoàn toàn khó bắt chước.'},
      {ten:'Doanh nghiệp tư nhân', o:'Không một người nắm — bốn ổ cắm cùng lúc',
       chi:'Sở hữu (cổ đông/HĐQT) · nhà nước (luật, regulator) · tổ chức đảng (party cell) · và THỊ TRƯỜNG NHÀ NƯỚC (mua sắm công, tín dụng, đất, giấy phép, trợ cấp).',
       cham:'Huawei · Alibaba · Tencent · ByteDance · SMIC · CATL và hàng triệu doanh nghiệp khác.',
       ghi:'Luật Thúc đẩy Kinh tế tư nhân 2025 quy định tổ chức đảng trong doanh nghiệp tư nhân hoạt động theo Điều lệ Đảng; nơi có từ ba đảng viên chính thức trở lên thì nên lập tổ chức đảng riêng. Nhưng nghiên cứu học thuật cho thấy vai trò party cell KHÁC NHAU rất lớn giữa các công ty — từ nghi lễ tới tham gia quyết định. "Mọi CEO Trung Quốc chỉ là bù nhìn" là kết luận bằng chứng KHÔNG cho phép.'},
      {ten:'Uỷ ban Biên chế Cơ cấu Trung ương', o:'META-SOCKET',
       chi:'Không chỉ điều khiển cơ quan — mà TẠO, XOÁ, GỘP cơ quan, chuyển chức năng, đổi biên chế.',
       cham:'Chính cấu trúc của bộ máy.',
       ghi:'Tức là CPU có quyền thiết kế lại mainboard. Cải cách 2023 chính là ví dụ: lập Uỷ ban Tài chính TW, Uỷ ban KHCN TW, Ban Công tác Xã hội TW, Văn phòng Công tác Hong Kong–Macau TW.'}
     ]},
    {id:'noira', n:4, tn:'Nối ra ngoài', acc:'#a371f7', t:'NỐI RA NGOÀI VÀ XUỐNG DƯỚI — chỗ chạm Hong Kong và Việt Nam',
     d:'Năm ổ cắm cuối là chỗ bộ máy với tay ra khỏi biên giới đảng viên: tới người ngoài đảng, ra hải ngoại, và xuống tận shipper.',
     ds:[
      {ten:'Lý Cán Kiệt', o:'Trưởng Ban Công tác Mặt trận Thống nhất',
       chi:'Người ngoài đảng KHÔNG mặc định là kẻ thù. Phân ba: đối kháng → chống/trấn áp; trung lập → tranh thủ; có thể dùng → đoàn kết.',
       cham:'Các đảng nhỏ · người không đảng phái · trí thức · dân tộc · tôn giáo · doanh nhân tư nhân · "giai tầng xã hội mới" · Hong Kong · Macau · Đài Loan · Hoa kiều và cộng đồng hải ngoại.',
       ghi:'Đây là ổ cắm quan trọng nhất để nối lại câu chuyện KMT — Tam Hoàng — Hướng Hoa Cường. Và cũng là chỗ dễ trượt nhất: <b>tiếp xúc thống chiến ≠ điệp viên</b>. Chỉ khi có chứng cứ riêng về bí mật, tài trợ, nhiệm vụ, chỉ huy thì mới được nâng mức.'},
      {ten:'Hạ Bảo Long', o:'Văn phòng Công tác Hong Kong–Macau TW = Văn phòng Sự vụ HK–Macau Quốc vụ viện',
       chi:'Bắc Kinh → Văn phòng TW → Liaison Office và cơ quan an ninh NSL → HKSAR → Đặc khu trưởng → chính quyền · toà · công vụ · cảnh sát.',
       cham:'Hong Kong và Macau.',
       ghi:'Một cơ quan mang hai mặt đảng/nhà nước — ví dụ rõ nhất của cấu trúc party-state. Hong Kong vẫn có hệ pháp luật riêng dưới "một quốc gia, hai chế độ", nhưng chính sách trung ương về Hong Kong nằm dưới cấu trúc của Đảng.'},
      {ten:'Tống Đào', o:'Văn phòng Công tác Đài Loan TW = Taiwan Affairs Office của Quốc vụ viện',
       chi:'Lại là một cơ quan hai danh nghĩa.',
       cham:'Quan hệ hai bờ · giao lưu · kinh tế · chính trị · chống Đài Loan độc lập · thúc đẩy thống nhất.',
       ghi:'KMT KHÔNG nằm dưới ĐCSTQ. Tập gửi thư chúc mừng Trịnh Lệ Văn năm 2025 và kêu gọi "nền tảng chính trị chung"; Trịnh đáp lại bằng hoà bình và giao lưu, không bằng cam kết thống nhất — và năm 2026 còn nói cải thiện quan hệ với Bắc Kinh không đồng nghĩa chống Mỹ.'},
      {ten:'Vương Nghị · Lưu Hải Tinh', o:'Bộ trưởng Ngoại giao kiêm Chủ nhiệm Văn phòng Uỷ ban Đối ngoại TW · và Trưởng Ban Liên lạc Đối ngoại TW (IDCPC)',
       chi:'NGOẠI GIAO SONG SONG: nhà nước (MFA) · đảng (IDCPC) · và thống chiến (UFWD) — ba mạng phối hợp được nhưng KHÔNG phải một cơ quan.',
       cham:'Chính phủ nước ngoài · đảng cầm quyền và đảng đối lập nước ngoài · phong trào chính trị · cộng đồng hải ngoại.',
       ghi:'Một nước bình thường chủ yếu chỉ có kênh thứ nhất. Ba kênh cùng lúc là nguồn ảnh hưởng rất đặc biệt — và là chỗ Việt Nam tiếp xúc nhiều nhất.'},
      {ten:'Trường học · Đoàn · Đội', o:'Cơ chế "hiệu trưởng phụ trách dưới sự lãnh đạo của Đảng uỷ"',
       chi:'Đảng uỷ lãnh đạo → <b>hiệu trưởng</b> phụ trách chuyên môn. Ở phổ thông cũng đang triển khai cùng cơ chế đó.',
       cham:'TRẺ EM → trường học → Đội → Đoàn Thanh niên → Đảng → cán bộ.',
       ghi:'Ổ cắm DÀI HẠN NHẤT bảng. Điều lệ Đoàn Thanh niên Cộng sản xác định tổ chức này chịu sự lãnh đạo của ĐCSTQ và là "trợ thủ, lực lượng dự bị" của Đảng — tức nó không phải câu lạc bộ sinh viên mà là một đường ống tái tạo nhân sự. Cùng họ với ACFTU (công nhân) và ACWF (phụ nữ): các nhóm xã hội không bị xoá mà được tổ chức lại thành dây truyền động nối xã hội với Đảng.'},
      {ten:'Ngô Hán Thánh', o:'Trưởng Ban Công tác Xã hội Trung ương (lập 2023)',
       chi:'Đảng đi xuống tận nhóm KHÔNG nằm trong đơn vị công tác truyền thống.',
       cham:'Tổ chức xã hội · doanh nghiệp mới · nền tảng · shipper Meituan · tài xế Didi · lao động gig · xinfang/khiếu nại · quản trị cộng đồng · lưới grid xuống tới toà nhà và hộ dân.',
       ghi:'Thời Mao: công nhân → nhà máy nhà nước → chi bộ. Nay những người này không có "đơn vị" nào, nên Đảng xây ổ cắm mới để nối tới họ. Nhưng đừng biến mọi grid thành "mạng lưới mật vụ" — phần lớn chức năng rất đời thường: rác, người già, tranh chấp, an sinh. Cùng một mạng đó đồng thời làm tăng khả năng nhận biết xã hội ở cấp rất nhỏ.'}
     ]}
  ]
};

/* ═══════════════════════════════════════════════════════
   BÀN CỜ MỸ–TRUNG — hai bo mạch đối nhau

   Tài liệu nguồn gọi đây là bước logic tiếp theo, và nó đúng là
   thứ Đài Quan Trắc thiếu hẳn: cung đã có bo mạch Trung Quốc, đã
   có bảng đo Việt Nam, nhưng chưa có chỗ nào cho thấy AI KHOÁ
   ĐƯỢC GÌ CỦA AI — mà đó mới là chuyện quyết định dòng chảy.

   Ba điều phải giữ, vì bỏ điều nào cũng ra một bàn cờ sai:

   1. ĐÒN KHÔNG ĐI MỘT CHIỀU. Trung Quốc giữ ổ cắm ngược lại —
      USGS 2026 ghi nước này sản xuất 74/77 loại khoáng sản khảo
      sát và đứng số một thế giới ở 39 loại.
   2. MỸ MỘT MÌNH KHÔNG TẠO ĐƯỢC CHUỖI. Các ổ cắm nằm rải ở Hà
      Lan, Nhật, Hàn, Đài Loan, EU, Trung Đông. Đòn bẩy lớn nhất
      là LIÊN MINH, không phải một nước đơn lẻ.
   3. BA THỨ KHÁC NHAU RẤT XA: làm Trung Quốc suy thoái ≠ làm hệ
      tài chính khủng hoảng ≠ làm ĐCSTQ mất quyền lực.
   ═══════════════════════════════════════════════════════ */
const BANCO = {
  lede:'Không tồn tại một Hormuz, một Đài Loan hay một con chip duy nhất làm hệ thống sụp. Muốn có tình trạng mang tính hệ thống thì phải NHIỀU VÒNG TUẦN HOÀN BỊ ĐÁNH GÃY CÙNG LÚC, rồi cú sốc bên ngoài phải kích hoạt đúng các điểm yếu đang tồn tại bên trong.',
  a:'        MỸ + ĐỒNG MINH                    TRUNG QUỐC\n   ┌──────────────────────┐        ┌──────────────────────┐\n   │ Mỹ    GPU·EDA·IP     │        │ khoáng sản  74/77    │\n   │ Hà Lan  lithography  │  ⇄     │ nam châm · chế biến  │\n   │ Nhật  thiết bị·vật liệu│      │ pin · chuỗi cung ứng │\n   │ Hàn   HBM·memory     │        │ sản xuất quy mô lớn  │\n   │ Đài Loan  foundry    │        │ thị trường nội địa   │\n   │ EU    thị trường     │        │ 3,4 nghìn tỷ dự trữ  │\n   └──────────────────────┘        └──────────────────────┘\n              │                              │\n              └──────────┬───────────────────┘\n                         │\n              VIỆT NAM · ASEAN · MEXICO\n              đường vòng của chuỗi cung\n                         │\n              rules of origin · chống chuyển tải',
  cot:[
    {t:'MỸ VÀ ĐỒNG MINH KHOÁ ĐƯỢC GÌ', acc:'#58a6ff', ds:[
      {n:'Bán dẫn tiên tiến', d:'Mỹ duy trì kiểm soát với advanced computing chips và thiết bị sản xuất; BIS còn siết thêm trong 2025. Nhưng đây là đòn bẩy CHỌN LỌC hơn năng lượng: nó đánh vào AI, siêu máy tính, sản xuất tiên tiến và biên nghiên cứu — <b>không</b> làm nhà máy Trung Quốc ngừng chạy ngày mai. Trung Quốc còn mature-node, SMIC, Huawei, thiết bị nội địa và trợ cấp nhà nước.'},
      {n:'Cả tầng công nghệ, không chỉ chip', d:'Một hạn chế duy nhất thì Trung Quốc tìm được đường vòng. Phải chip + phần mềm (EDA, IP) + thiết bị (lithography, metrology, vật liệu) bị giới hạn ĐỒNG THỜI mới tạo được nút thắt lâu dài. Và đó chính là lý do Mỹ cần Hà Lan, Nhật, Hàn, Đài Loan.'},
      {n:'Thị trường xuất khẩu', d:'Mỹ 14,7% + EU 14,5% ≈ <b>29%</b> xuất khẩu hàng hoá Trung Quốc. Mỹ một mình thì Trung Quốc chuyển hướng sang ASEAN, Mexico, Global South. Mỹ + EU + các thị trường lớn cùng lúc thì khó chuyển hơn nhiều — đây là chỗ liên minh có đòn bẩy mà một nước không có.'},
      {n:'Thanh toán và tài chính', d:'Rất mạnh nhưng cũng rất nguy hiểm cho cả hai phía. Trung Quốc có kiểm soát vốn, ngân hàng quốc doanh, thanh toán NDT, CIPS, thặng dư thương mại và ~3,416 nghìn tỷ USD dự trữ (cuối 6/2026). Áp lực tài chính 8/10; sụp đổ tức thì 3/10.'}
    ]},
    {t:'TRUNG QUỐC PHẢN ĐÒN BẰNG GÌ', acc:'#f0503f', ds:[
      {n:'Khoáng sản và chế biến', d:'USGS 2026: sản xuất <b>74 trong 77</b> loại khoáng sản khảo sát, đứng số một thế giới ở <b>39 loại</b>. Đây không phải game một chiều — một cuộc tách rời quá nhanh có thể tự gây lạm phát, thiếu linh kiện và gián đoạn chuỗi cung cho chính bên gây áp lực.'},
      {n:'Nga là đường bypass chiến lược', d:'Nga là nguồn dầu thô lớn nhất của Trung Quốc năm 2024 (~20%), cộng Kazakhstan, Myanmar và sản xuất nội địa. Nên Hormuz là cú đánh kinh tế rất lớn nhưng KHÔNG phải kill-switch riêng của Trung Quốc — UNCTAD đánh giá Hormuz mang ~1/4 thương mại dầu đường biển toàn cầu, tức nó đánh cả Nhật, Hàn, Ấn, châu Âu.'},
      {n:'Quy mô sản xuất và thị trường', d:'Khác Liên Xô cuối kỳ ở đúng chỗ này: Trung Quốc có thị trường, sản xuất khổng lồ, ngoại thương, doanh nghiệp tư nhân, SOE, ngân hàng nhà nước, kinh tế số và thị trường nội địa lớn. Không thể lấy "công thức đánh Liên Xô" áp nguyên xi.'},
      {n:'Đổi đường thay vì chịu đòn', d:'Nếu các nước không phối hợp, Trung Quốc đổi thị trường, đổi nhà cung cấp, đổi tuyến logistics, đầu tư nội địa hoá, dùng nước thứ ba.'}
    ]},
    {t:'VIỆT NAM ĐỨNG Ở ĐÂU', acc:'#d29922', ds:[
      {n:'Là đường vòng — và vì thế là mục tiêu kiểm tra', d:'Nếu đầu ra trực tiếp của Trung Quốc bị khó: Trung Quốc → FDI, linh kiện, nhà máy → ASEAN → sản phẩm → Mỹ/EU. Nên <b>rules of origin</b> và chống chuyển tải trở thành mắt xích của chính cuộc chiến thương mại. Khoá "China → US" mà không nhìn "China → nước thứ ba → US" thì hiệu quả giảm hẳn.'},
      {n:'Việt Nam chiếm 4,5% xuất khẩu Trung Quốc', d:'Đứng thứ tư sau Mỹ, EU và Hong Kong — trên cả Nhật (4,3%), Hàn (4,1%), Ấn (3,4%) và Nga (3,2%). Vị trí đó vừa là cơ hội đơn hàng vừa là chỗ dễ bị soi.'},
      {n:'Đây là lý do hai bảng phải đọc cùng nhau', d:'Bảng Việt Nam hỏi "nền kinh tế chịu được không". Bảng Trung Quốc hỏi "quyền lực giữ được không". Bàn cờ này là chỗ hai câu hỏi gặp nhau: một cú siết vào ổ cắm Trung Quốc chảy tới đơn hàng, việc làm và tỷ giá Việt Nam qua đúng những đường mà chiến trường của cả hai bảng đang theo dõi.'}
    ]}
  ],
  ket:'<b>Ba thứ phải phân biệt, và trộn chúng là chỗ mọi phân tích "đánh Trung Quốc" trở nên vô dụng:</b> làm Trung Quốc SUY THOÁI · làm hệ tài chính Trung Quốc KHỦNG HOẢNG · làm ĐCSTQ MẤT QUYỀN LỰC. Khi FISCAL CAPACITY + CADRE COHESION + SECURITY COHESION còn đồng thời tồn tại, một cú sốc rất lớn về dầu, chip hay xuất khẩu có thể làm Trung Quốc nghèo hơn hoặc tăng trưởng chậm lại nhưng CHƯA tự động làm chế độ sụp. Chỉ khi cú sốc vật chất biến thành khủng hoảng PHÂN PHỐI bên trong elite, rồi khiến chuỗi cán bộ và chuỗi an ninh không còn cùng hướng, thì bài toán mới chuyển từ chiến tranh kinh tế sang sinh tồn chế độ.'
};

window.DQT_TQ = {
  BOMACH: BOMACH, BANCO: BANCO, DEM: DEM,
  COMPASS: COMPASS, DODAC: DODAC,
  THEATERS: THEATERS, GAUGES: GAUGES, CHAIN: CHAIN, CHAIN_SRC: CHAIN_SRC,
  LEVELS: LEVELS, SCEN: SCEN, LIB: LIB, SOLIEU: SOLIEU, KB: KB, RANH: RANH
};
})();
