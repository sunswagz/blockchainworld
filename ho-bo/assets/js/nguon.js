/* ═══════════════════════════════════════════════════════
   SỔ BỘ NGUỒN — VIẾT TAY, không phải file tự sinh.

   Bốn mươi bảy công cụ quan sát thị trường crypto, xếp theo việc
   chúng làm chứ không theo thứ tự ai nổi hơn ai.

   ── VÌ SAO KHÔNG PHẢI MỘT TRANG BOOKMARK ──────────────
   Một lưới 47 ô link là bookmark đẹp, và bookmark thì trình duyệt
   nào cũng có sẵn. Thứ một danh sách link không nói được, mà chỗ
   này phải nói, là BỐN việc:

     1. công cụ đó nhìn cái gì (giá? ví? hợp đồng?)
     2. nó đòi quyền gì ở ví bạn — xem thang `tang` bên dưới
     3. tin được tới đâu, và ai kiểm chứng
     4. hỏi câu nào thì mở nó

   ── THANG QUYỀN VÍ — trục quan trọng nhất ─────────────
     0  chỉ đọc dữ liệu công khai        không chạm ví
     1  dán địa chỉ ví công khai vào ô tìm   vẫn không chạm ví
     2  nối ví, ký đăng nhập             chữ ký, chưa chuyển tiền
     3  duyệt chi / hoán đổi / bắc cầu   TIỀN THẬT RỜI VÍ

   Ranh giới thật nằm giữa 2 và 3. "Trang web có thật" và "thao tác
   trên đó an toàn" là hai câu khác nhau hoàn toàn — Whales Market
   là sàn có thật và đang chạy, nhưng mua một suất phân bổ trước
   TGE trên đó gánh cùng lúc rủi ro đối tác, rủi ro định giá, rủi
   ro thanh khoản và rủi ro hợp đồng.

   ── LUẬT KHÔNG CÓ NGOẠI LỆ ────────────────────────────
   KHÔNG công cụ nào trong danh sách này cần seed phrase hay khoá
   riêng tư của bạn. Ai hỏi tới, dừng ngay — người có seed phrase
   là người sở hữu tài sản, không có cách nào rút lại.

   ── `rui` KHÔNG PHẢI ĐIỂM ĐẠO ĐỨC ─────────────────────
   Nó đo mức thiệt hại nếu mọi thứ diễn ra tệ nhất, chứ không đo
   công cụ đó tử tế hay không. Một trang đọc dữ liệu tuyệt vời và
   một cây cầu nối hoàn toàn hợp pháp nằm ở hai mức khác nhau, vì
   sai lầm trên cái sau lấy mất tiền còn trên cái trước thì không.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var LOP = [
    { ma: "gia", ten: "Giá & thị trường", y: "Giá, khối lượng, biểu đồ, thanh khoản. Lớp ai cũng bắt đầu, và cũng là lớp nói ít nhất về nguyên nhân." },
    { ma: "onchain", ten: "On-chain thô", y: "Dữ liệu đọc thẳng từ blockchain: dòng vốn, chu kỳ, hành vi nắm giữ. Chậm hơn giá, nhưng nói được vì sao." },
    { ma: "vi", ten: "Ví & cá voi", y: "Gắn nhãn địa chỉ, lần theo tiền của tổ chức và tay to. Nhãn là suy đoán từ lịch sử, không phải danh tính đã xác minh." },
    { ma: "giao-thuc", ten: "Giao thức & DeFi", y: "TVL, phí, doanh thu, cầu nối, Layer 2. Đây là lớp Hộ Bộ đứng lên để dựng số của chính nó." },
    { ma: "von", ten: "Vốn & dự án", y: "Ai rót tiền cho ai, vòng gọi vốn, mở khoá token. Nhìn được tiền chuyên nghiệp đang chuẩn bị đi đâu." },
    { ma: "tin", ten: "Tin & tự sự", y: "Cộng đồng đang nói gì, tự sự nào đang nổi. Lớp nhiễu nhất, và cũng là lớp đi trước giá xa nhất." },
    { ma: "an-ninh", ten: "An ninh & pháp chứng", y: "Soi hợp đồng, mô phỏng giao dịch trước khi gửi, gom cụm ví. Dùng trước khi mất tiền chứ không phải sau." },
    { ma: "thuc-thi", ten: "Thực thi", y: "Chạm tiền thật: hoán đổi, bắc cầu, mua bán suất. Mọi thứ ở đây là tầng 3." },
    { ma: "tien-ich", ten: "Tiện ích & bot", y: "Báo giá, báo ví, tra cứu mạng. Nhỏ nhưng đúng lúc thì hữu dụng." }
  ];

  /* tang: 0–3 theo thang quyền ví ở đầu file
     rui:  thap | vua | cao      — thiệt hại nếu mọi chuyện đi sai
     tin:  cao | vua | chua-ro   — mức bằng chứng độc lập
     api:  co | mot-phan | khong
     tien: free | freemium | tra-phi */
  var TOOL = [
    /* ── giá & thị trường ──────────────────────────────── */
    { ma: "coingecko", ten: "CoinGecko", url: "https://www.coingecko.com", lop: "gia", tang: 0, rui: "thap", tin: "cao", api: "co", tien: "freemium",
      viec: "Giá, vốn hoá, khối lượng của hàng chục nghìn tài sản.",
      hoi: "Đồng này đang bao nhiêu, vốn hoá thế nào?" },
    { ma: "coinmarketcap", ten: "CoinMarketCap", url: "https://coinmarketcap.com", lop: "gia", tang: 0, rui: "thap", tin: "cao", api: "co", tien: "freemium",
      viec: "Cùng việc với CoinGecko, khác cách xếp hạng và khác nguồn niêm yết.",
      hoi: "Bảng xếp hạng vốn hoá đang thế nào?" },
    { ma: "tradingview", ten: "TradingView", url: "https://www.tradingview.com", lop: "gia", tang: 0, rui: "thap", tin: "cao", api: "mot-phan", tien: "freemium",
      viec: "Biểu đồ và chỉ báo kỹ thuật, không riêng crypto. Có ngôn ngữ viết chỉ báo riêng.",
      hoi: "Đồ thị đang ở đâu so với các mốc kỹ thuật?" },
    { ma: "dexscreener", ten: "DEX Screener", url: "https://dexscreener.com", lop: "gia", tang: 0, rui: "vua", tin: "cao", api: "co", tien: "free",
      viec: "Cặp giao dịch mới trên các sàn phi tập trung, gần như tức thời.",
      hoi: "Token mới nào vừa có thanh khoản?",
      luu: "Trang này tự niêm yết MỌI token có hồ thanh khoản và có giao dịch. Xuất hiện ở đây KHÔNG phải chứng nhận an toàn — token lừa đảo cũng lên bảng y như nhau. Công cụ đáng tin; thứ bên trong nó thì không." },
    { ma: "dextools", ten: "DEXTools", url: "https://www.dextools.io", lop: "gia", tang: 3, rui: "vua", tin: "cao", api: "co", tien: "freemium",
      viec: "Phân tích cặp DEX, thanh khoản, dữ liệu giao dịch — và có cả chức năng đổi token.",
      hoi: "Cặp này thanh khoản ra sao, ai đang mua?",
      luu: "Cùng cảnh báo như DEX Screener. Thêm một tầng nữa: từ lúc bấm nối ví để đổi token là đã sang tầng 3." },
    { ma: "birdeye", ten: "Birdeye", url: "https://birdeye.so", lop: "gia", tang: 3, rui: "vua", tin: "cao", api: "co", tien: "freemium",
      viec: "Giá, OHLCV, thanh khoản, ví nắm giữ — mạnh nhất ở Solana, nay đã nhiều chuỗi.",
      hoi: "Token này trên Solana có ai đang gom không?",
      luu: "Dữ liệu tốt là một chuyện, giao dịch là chuyện khác. Bấm nối ví là đổi từ lớp đọc sang lớp thực thi, và mức rủi ro đổi theo." },
    { ma: "dropstab", ten: "DropsTab", url: "https://dropstab.com", lop: "gia", tang: 0, rui: "thap", tin: "vua", api: "mot-phan", tien: "freemium",
      viec: "Theo dõi danh mục, lịch sự kiện, dữ liệu token.",
      hoi: "Sắp có sự kiện gì với đồng này?" },

    /* ── on-chain thô ──────────────────────────────────── */
    { ma: "dune", ten: "Dune", url: "https://dune.com", lop: "onchain", tang: 0, rui: "thap", tin: "cao", api: "co", tien: "freemium",
      viec: "SQL trên dữ liệu blockchain đã chuẩn hoá, hơn 100 chuỗi. Tự viết truy vấn, tự dựng bảng.",
      hoi: "Trong 30 ngày có bao nhiêu ví mới? Giao thức nào tăng người dùng?",
      luu: "Bảng do người khác dựng KHÔNG bảo đảm logic của bảng đó đúng. Dữ liệu nền thì chuẩn; phép cộng bên trên nó là của tác giả bảng, và bảng sai vẫn hiện ra rất đẹp." },
    { ma: "artemis", ten: "Artemis", url: "https://artemis.xyz", lop: "onchain", tang: 0, rui: "thap", tin: "cao", api: "mot-phan", tien: "freemium",
      viec: "So sánh các chuỗi theo địa chỉ hoạt động, giao dịch, doanh thu.",
      hoi: "Chuỗi nào thật sự có người dùng, không chỉ có TVL?" },
    { ma: "glassnode", ten: "Glassnode", url: "https://glassnode.com", lop: "onchain", tang: 0, rui: "thap", tin: "cao", api: "co", tien: "freemium",
      viec: "Chỉ số chu kỳ cho Bitcoin và Ethereum: MVRV, SOPR, vốn hoá thực, phân tách người giữ dài và ngắn hạn.",
      hoi: "Chu kỳ đang ở đoạn nào?" },
    { ma: "cryptoquant", ten: "CryptoQuant", url: "https://cryptoquant.com", lop: "onchain", tang: 0, rui: "thap", tin: "cao", api: "co", tien: "freemium",
      viec: "Dòng vào/ra sàn, dự trữ sàn, dòng thợ đào, tỷ lệ cá voi, lãi suất tài trợ, thanh lý.",
      hoi: "Có lượng lớn coin vừa chuyển lên sàn không?",
      luu: "Dòng vào sàn tăng là một BIẾN RỦI RO, không phải một kết luận. Đọc thành \"sắp sập\" là tự thêm vào dữ liệu thứ nó không nói." },
    { ma: "santiment", ten: "Santiment", url: "https://santiment.net", lop: "onchain", tang: 0, rui: "thap", tin: "vua", api: "co", tien: "freemium",
      viec: "Ghép dữ liệu on-chain với tín hiệu mạng xã hội và hành vi nhà phát triển.",
      hoi: "Đám đông đang hưng phấn hay đang chán?" },

    /* ── ví & cá voi ───────────────────────────────────── */
    { ma: "nansen", ten: "Nansen", url: "https://nansen.ai", lop: "vi", tang: 1, rui: "thap", tin: "cao", api: "co", tien: "tra-phi",
      viec: "Gắn nhãn hàng trăm triệu địa chỉ: quỹ, sàn, cá voi, tay giao dịch giỏi. Có bảng xếp hạng Smart Money.",
      hoi: "Ai đang mua token này?",
      luu: "\"Smart Money\" là một PHÂN LOẠI DỰA TRÊN QUÁ KHỨ — lãi đã thực hiện, tỷ lệ thắng, lịch sử giao dịch. Nó không phải lời tiên tri, và nhãn hôm nay không ràng buộc hành vi ngày mai." },
    { ma: "arkham", ten: "Arkham", url: "https://arkm.com", lop: "vi", tang: 1, rui: "thap", tin: "cao", api: "mot-phan", tien: "freemium",
      viec: "Pháp chứng blockchain: gom cụm ví, gắn với tổ chức, vẽ mạng lưới chuyển tiền.",
      hoi: "Số tiền này đi từ đâu tới đâu, ai đứng sau?" },
    { ma: "cielo", ten: "Cielo", url: "https://cielo.finance", lop: "vi", tang: 3, rui: "cao", tin: "vua", api: "co", tien: "freemium",
      viec: "Theo dõi ví theo thời gian thực, báo động khi ví bạn dõi có động tĩnh.",
      hoi: "Ví tôi đang theo vừa làm gì?",
      luu: "Phần theo dõi là tầng 1. Phần sao chép giao dịch là tầng 3 — bạn giao quyền quyết định cho hành vi của một người lạ." },
    { ma: "debank", ten: "DeBank", url: "https://debank.com", lop: "vi", tang: 2, rui: "vua", tin: "cao", api: "mot-phan", tien: "freemium",
      viec: "Xem toàn bộ danh mục DeFi của một ví trên nhiều chuỗi, kể cả vị thế đang mở.",
      hoi: "Ví này đang giữ gì và nợ gì?" },
    { ma: "zapper", ten: "Zapper", url: "https://zapper.xyz", lop: "vi", tang: 2, rui: "vua", tin: "cao", api: "co", tien: "freemium",
      viec: "Bảng danh mục và lịch sử giao dịch đã diễn giải cho người đọc.",
      hoi: "Ví này đã làm gì trong tháng qua?" },

    /* ── giao thức & DeFi ──────────────────────────────── */
    { ma: "defillama", ten: "DefiLlama", url: "https://defillama.com", lop: "giao-thuc", tang: 0, rui: "thap", tin: "cao", api: "co", tien: "free",
      viec: "TVL, phí, doanh thu, khối lượng DEX, stablecoin, lợi suất, cầu nối — hàng nghìn giao thức, hàng trăm chuỗi, phương pháp tính công khai.",
      hoi: "Tiền đang nằm ở đâu?",
      loi: "Toàn bộ số liệu của chính cung Hộ Bộ này lấy từ đây, qua API công khai không cần khoá." },
    { ma: "l2beat", ten: "L2BEAT", url: "https://l2beat.com", lop: "giao-thuc", tang: 0, rui: "thap", tin: "cao", api: "mot-phan", tien: "free",
      viec: "Hồ sơ từng Layer 2: thang tự trị, hệ chứng minh, năm chiều rủi ro, tài sản đang giữ.",
      hoi: "Layer 2 này ai còn giữ quyền tắt máy?",
      loi: "Đô Sát Viện trong kinh đô này là bản Việt hoá của L2BEAT." },
    { ma: "dappradar", ten: "DappRadar", url: "https://dappradar.com", lop: "giao-thuc", tang: 0, rui: "thap", tin: "vua", api: "co", tien: "freemium",
      viec: "Xếp hạng ứng dụng phi tập trung theo người dùng, khối lượng, giao dịch.",
      hoi: "Ứng dụng nào đang có người dùng thật?" },
    { ma: "eigenphi", ten: "EigenPhi", url: "https://eigenphi.io", lop: "giao-thuc", tang: 0, rui: "thap", tin: "vua", api: "mot-phan", tien: "freemium",
      viec: "Mổ xẻ MEV: chạy trước, kẹp lệnh, chênh lệch giá, thanh lý.",
      hoi: "Lệnh của tôi có bị kẹp không?" },
    { ma: "revert", ten: "Revert Finance", url: "https://revert.finance", lop: "giao-thuc", tang: 3, rui: "cao", tin: "vua", api: "khong", tien: "freemium",
      viec: "Phân tích và tự động hoá vị thế cung cấp thanh khoản.",
      hoi: "Vị thế LP của tôi lãi thật hay chỉ hoà vốn sau tổn thất tạm thời?",
      luu: "Phần phân tích chỉ đọc. Phần tự động hoá đòi quyền chạm vào vị thế — tầng 3." },

    /* ── vốn & dự án ───────────────────────────────────── */
    { ma: "cryptorank", ten: "CryptoRank", url: "https://cryptorank.io", lop: "von", tang: 0, rui: "thap", tin: "vua", api: "co", tien: "freemium",
      viec: "Cơ sở dữ liệu gọi vốn, lịch mở khoá token, hồ sơ quỹ đầu tư.",
      hoi: "Ai đầu tư vào dự án này, bao giờ mở khoá?" },
    { ma: "messari", ten: "Messari", url: "https://messari.io", lop: "von", tang: 0, rui: "thap", tin: "cao", api: "co", tien: "freemium",
      viec: "Nghiên cứu và dữ liệu chuẩn hoá cho hàng chục nghìn tài sản.",
      hoi: "Dự án này thật sự làm gì và kiếm tiền bằng gì?" },
    { ma: "crunchbase", ten: "Crunchbase", url: "https://www.crunchbase.com", lop: "von", tang: 0, rui: "thap", tin: "cao", api: "co", tien: "tra-phi",
      viec: "Dữ liệu gọi vốn của công ty nói chung, không riêng crypto.",
      hoi: "Công ty đứng sau dự án này gọi được bao nhiêu?" },
    { ma: "cypherhunter", ten: "CypherHunter", url: "https://www.cypherhunter.com", lop: "von", tang: 0, rui: "thap", tin: "vua", api: "khong", tien: "free",
      viec: "Bản đồ quan hệ dự án — nhà đầu tư — con người trong crypto.",
      hoi: "Những dự án này có chung ai đứng sau không?" },
    { ma: "icoanalytics", ten: "ICO Analytics", url: "https://icoanalytics.org", lop: "von", tang: 0, rui: "thap", tin: "vua", api: "khong", tien: "free",
      viec: "Thống kê đợt mở bán và ra mắt token.",
      hoi: "Tháng này có đợt mở bán nào đáng chú ý?" },
    { ma: "cryptofundraising", ten: "Crypto Fundraising", url: "https://crypto-fundraising.info", lop: "von", tang: 0, rui: "thap", tin: "vua", api: "khong", tien: "free",
      viec: "Tổng hợp vòng gọi vốn theo tuần, theo ngành, theo quỹ.",
      hoi: "Tiền của quỹ đang chảy vào ngành nào?" },

    /* ── tin & tự sự ───────────────────────────────────── */
    { ma: "cryptopanic", ten: "CryptoPanic", url: "https://cryptopanic.com", lop: "tin", tang: 0, rui: "thap", tin: "vua", api: "co", tien: "freemium",
      viec: "Tổng hợp tin từ nhiều nguồn, có bộ lọc theo đồng.",
      hoi: "Vừa có tin gì về đồng này?" },
    { ma: "delphi", ten: "Delphi Digital", url: "https://delphidigital.io", lop: "tin", tang: 0, rui: "thap", tin: "cao", api: "khong", tien: "tra-phi",
      viec: "Nghiên cứu chuyên sâu cho nhà đầu tư và người xây dựng.",
      hoi: "Luận điểm đầy đủ về ngành này là gì?" },
    { ma: "bankless", ten: "Bankless", url: "https://www.bankless.com", lop: "tin", tang: 0, rui: "thap", tin: "vua", api: "khong", tien: "freemium",
      viec: "Bản tin và podcast theo hướng biên tập, thiên về hệ Ethereum.",
      hoi: "Tuần này có gì đáng đọc?" },
    { ma: "chaincatcher", ten: "ChainCatcher", url: "https://www.chaincatcher.com", lop: "tin", tang: 0, rui: "thap", tin: "vua", api: "khong", tien: "free",
      viec: "Tin và phân tích crypto tiếng Trung, thường sớm hơn báo tiếng Anh ở tin châu Á.",
      hoi: "Thị trường châu Á đang bàn gì?" },
    { ma: "moni", ten: "Moni", url: "https://discover.getmoni.io", lop: "tin", tang: 0, rui: "thap", tin: "vua", api: "co", tien: "freemium",
      viec: "Chấm điểm mạng xã hội của dự án: ai theo dõi, chất lượng người theo dõi, tốc độ tăng.",
      hoi: "Dự án này có sự chú ý thật hay chỉ mua người theo dõi?" },
    { ma: "dexu", ten: "Dexu", url: "https://dexu.ai", lop: "tin", tang: 0, rui: "vua", tin: "chua-ro", api: "khong", tien: "freemium",
      viec: "Công cụ tổng hợp tự sự và tín hiệu, có phần dùng mô hình ngôn ngữ.",
      hoi: "Tự sự nào đang nổi lên?",
      luu: "Chưa đủ bằng chứng độc lập để xếp cùng nhóm với Glassnode hay Nansen. Dùng để lấy ý tưởng, đừng dùng làm căn cứ." },
    { ma: "rayo", ten: "Rayo", url: "https://rayo.gg", lop: "tin", tang: 0, rui: "vua", tin: "vua", api: "khong", tien: "free",
      viec: "Khám phá dự án Web3 do cộng đồng biên soạn. Trước đây tên là The Dapp List.",
      hoi: "Trong ngách này có những dự án nào?",
      luu: "Chính Rayo nói rõ một phần nội dung do người đóng góp gửi lên và CÓ THỂ CHƯA ĐƯỢC XÁC MINH. Nền tảng hợp pháp không đồng nghĩa mọi dự án được liệt kê đều an toàn — đây là hai câu khác nhau." },
    { ma: "tokleo", ten: "Tokleo", url: "https://tokleo.com", lop: "tin", tang: 0, rui: "thap", tin: "vua", api: "khong", tien: "freemium",
      viec: "Phân tích thời gian thực cho các hồ Meteora DLMM trên Solana: TVL, khối lượng, phí, rủi ro.",
      hoi: "Hồ DLMM này có đáng vào không?",
      luu: "Ảnh gốc lan truyền ghi công cụ này là \"Token Launch Analytics\" của @KalindroDB. MÔ TẢ ĐÓ SAI. KalindroDB là tài khoản của người xây Tokleo, còn Tokleo thì chuyên về hồ Meteora DLMM — hẹp hơn và cụ thể hơn hẳn. Chi tiết này đáng giữ vì nó nhắc: một tấm ảnh tổng hợp không phải là danh mục đã được kiểm chứng." },
    { ma: "vestlab", ten: "VestLab", url: "https://vestlab.io", lop: "tin", tang: 0, rui: "vua", tin: "chua-ro", api: "khong", tien: "freemium",
      viec: "Công cụ theo dõi vesting và phân bổ token.",
      hoi: "Token này mở khoá theo lịch nào?",
      luu: "Chưa tìm được bằng chứng độc lập đủ mạnh để nâng lên nhóm tin cậy cao. Đối chiếu chéo trước khi dùng số của nó." },

    /* ── an ninh & pháp chứng ──────────────────────────── */
    { ma: "blocksec", ten: "BlockSec · Phalcon", url: "https://blocksec.com", lop: "an-ninh", tang: 0, rui: "thap", tin: "cao", api: "co", tien: "freemium",
      viec: "Giám sát an ninh, mô phỏng và gỡ lỗi giao dịch, phát hiện tấn công, lần theo dòng tiền bị lấy, tuân thủ.",
      hoi: "Giao dịch này thật sự làm gì bên trong?",
      luu: "Ảnh gốc ghi gọn là \"Smart Contract Tracker\" — thiếu hẳn. Phần mô phỏng và giám sát tấn công mới là chỗ mạnh nhất." },
    { ma: "tenderly", ten: "Tenderly", url: "https://tenderly.co", lop: "an-ninh", tang: 0, rui: "thap", tin: "cao", api: "co", tien: "freemium",
      viec: "Mô phỏng giao dịch TRƯỚC khi gửi lên mạng: token nào đi, token nào về, hợp đồng gọi gì, có bị hoàn không.",
      hoi: "Nếu tôi ký cái này thì chuyện gì xảy ra?",
      loi: "Với bot tự động thì đây gần như bắt buộc: mô phỏng trước, thực thi sau. Rẻ hơn vô cùng so với học bằng tiền thật." },
    { ma: "bubblemaps", ten: "Bubblemaps", url: "https://bubblemaps.io", lop: "an-ninh", tang: 0, rui: "thap", tin: "cao", api: "mot-phan", tien: "freemium",
      viec: "Vẽ phân bố token thành cụm bong bóng, làm lộ các ví liên quan nhau và mức tập trung.",
      hoi: "Token này có bị vài ví liên thông nắm phần lớn không?",
      luu: "Nó CUNG CẤP BẰNG CHỨNG để điều tra, không phải máy phán quyết lừa đảo. Cụm ví liên thông là dấu hiệu đáng đào tiếp, không phải kết luận." },

    /* ── thực thi ──────────────────────────────────────── */
    { ma: "whales-market", ten: "Whales Market", url: "https://whales.market", lop: "thuc-thi", tang: 3, rui: "cao", tin: "vua", api: "khong", tien: "free",
      viec: "Sàn mua bán suất phân bổ và token trước niêm yết, giao dịch ngoài sàn có ký quỹ hợp đồng.",
      hoi: "Suất airdrop này bán trước được giá bao nhiêu?",
      luu: "Nền tảng có thật và đang chạy — nhưng \"có thật\" khác \"an toàn\". Mua trước TGE gánh cùng lúc: rủi ro đối tác, rủi ro dự án không ra token, rủi ro định giá, rủi ro thanh khoản, rủi ro tất toán và rủi ro hợp đồng. Đây là mục KHÔNG bao giờ nên xếp cùng mức rủi ro với CoinGecko." },
    { ma: "cointool", ten: "CoinTool", url: "https://ct.app", lop: "thuc-thi", tang: 3, rui: "cao", tin: "vua", api: "khong", tien: "freemium",
      viec: "Bộ tiện ích on-chain: tạo ví hàng loạt, thao tác theo lô, công cụ token và NFT, gọi hợp đồng.",
      hoi: "Làm sao chạy một thao tác cho nhiều ví cùng lúc?",
      luu: "Đã ĐỔI TÊN MIỀN sang ct.app. Hợp pháp, nhưng quyền tương tác ví rất mạnh — đừng thử bằng ví đang giữ nhiều tiền." },
    { ma: "chaineye", ten: "ChainEye", url: "https://chaineye.tools", lop: "thuc-thi", tang: 0, rui: "thap", tin: "vua", api: "khong", tien: "free",
      viec: "Bộ công cụ đa chuỗi: so sánh phí cầu nối, tra RPC, tra gas.",
      hoi: "Bắc cầu sang chuỗi này đường nào rẻ nhất?" },
    { ma: "minibridge", ten: "MiniBridge", url: "https://minibridge.chaineye.tools", lop: "thuc-thi", tang: 3, rui: "cao", tin: "vua", api: "khong", tien: "free",
      viec: "Cầu nối cho các khoản chuyển nhỏ giữa các chuỗi.",
      hoi: "Chuyển nhanh một ít tiền sang chuỗi khác bằng gì?",
      luu: "Phần SO SÁNH của ChainEye chỉ đọc, rủi ro thấp. Phần BẮC CẦU là tài sản rời ví bạn qua một hợp đồng — hai việc khác hẳn nhau dù cùng một nhà làm." },
    { ma: "chainlist", ten: "ChainList", url: "https://chainlist.org", lop: "thuc-thi", tang: 2, rui: "vua", tin: "cao", api: "khong", tien: "free",
      viec: "Danh sách Chain ID, Network ID và RPC để thêm mạng vào ví.",
      hoi: "Thêm mạng này vào ví thì điền thông số gì?",
      luu: "Vì nó liên quan tới cấu hình ví nên phải CHẮC CHẮN ĐÚNG TRANG. Đừng tra Google rồi bấm vào quảng cáo đầu tiên — đó là kiểu tấn công rẻ nhất và hiệu quả nhất nhắm vào lớp này." },

    /* ── tiện ích & bot ────────────────────────────────── */
    { ma: "etherdrops", ten: "EtherDrops Bot", url: "https://dropstab.com/products/drops-bot", lop: "tien-ich", tang: 1, rui: "vua", tin: "vua", api: "khong", tien: "freemium",
      viec: "Bot Telegram báo giá và báo động tĩnh của ví. Nay thuộc hệ DropsTab.",
      hoi: "Ví này vừa chuyển tiền, báo cho tôi ngay được không?",
      luu: "Bot Telegram GIẢ mạo tên bot thật là chuyện phổ biến. Vào bot từ đường dẫn trên trang chính thức, đừng từ kết quả tìm kiếm trong Telegram." },
    { ma: "notslava", ten: "NotSlava", url: "https://t.me/notslava_bot", lop: "tien-ich", tang: 1, rui: "vua", tin: "chua-ro", api: "khong", tien: "freemium",
      viec: "Bot tiện ích theo dõi ví, phổ biến trong một số cộng đồng nói tiếng Nga.",
      hoi: "Theo dõi nhanh một ví bằng Telegram?",
      luu: "Có dấu vết sử dụng thật, nhưng bằng chứng độc lập yếu hơn hẳn các tên như Glassnode hay Nansen. Đừng cho nó nhiều hơn mức một bot đọc dữ liệu công khai." }
  ];

  window.HOBU_NGUON = { LOP: LOP, TOOL: TOOL };
})();
