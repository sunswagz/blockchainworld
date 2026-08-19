/* ═══════════════════════════════════════════════════════
   SỔ 18 TOA — VIẾT TAY, sửa như mã nguồn.

   File này giữ phần CHỮ: tên toa, trách nhiệm, thứ tự bị đốt, và
   cửa nối sang cung khác. Phần SỐ nằm ở `assets/js/v/doan-tau.js`
   do bot sinh 4 lượt/ngày. Hai file khớp nhau bằng mã toa `t01`…
   `t18`; app.js báo thẳng ra màn hình nếu một bên có mã mà bên kia
   không có, chứ không lặng lẽ bỏ qua.

   ── RANH GIỚI PHẢI GIỮ ────────────────────────────────
   Ánh xạ "category nào thuộc toa nào" KHÔNG nằm ở đây. Nó nằm ở
   `scripts/build-thaiboc.mjs`, một chỗ duy nhất, vì bot cần nó để
   cộng số. Chép sang đây là tạo bản sao thứ hai của cùng một sự
   thật, và bản sao thứ hai luôn là bản lệch.

   ── THỨ TỰ BỊ ĐỐT LÀ MỘT LUẬN, KHÔNG PHẢI MỘT SỐ ĐO ───
   `songSot` xếp từ 1 (trụ lại lâu nhất) tới 18 (bị bỏ trước nhất).
   Đây là suy luận theo thứ tự phụ thuộc: cái gì phải có trước để
   cái kia tồn tại được. Nó KHÔNG phải dự báo giá, và không đo được
   bằng bất cứ API nào — nên trong giao diện nó luôn hiện dưới nhãn
   "luận", tách hẳn khỏi các con số đo được.

   Cách đọc một hạng: "bỏ toa này thì phần còn lại của đoàn tàu có
   chạy tiếp được không?" Bỏ meme thì settlement vẫn chạy, khối vẫn
   được tạo, tài sản vẫn chuyển. Bỏ settlement thì không còn gì cả.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  window.THAIBOC_TOA = {

    /* Cửa nối sang cung khác. Chỉ để ở đây những tuyến ĐÃ KIỂM là
       có thật — liên kết sâu tới một mã phòng không tồn tại thì
       trình duyệt vẫn mở trang và im lặng rơi về phòng mặc định,
       tức là hỏng mà không báo. Cung nào chưa xác minh được mã
       phòng thì trỏ thẳng vào gốc cung. */
    /* `goc` là mã CUNG thật. Năm cửa "hb-*" đều dẫn về Hộ Bộ, chỉ
       khác phòng — nên đếm số khoá của bảng này ra 13 và gọi đó là
       "13 cung" là sai. Có `goc` thì đếm cung phân biệt được với
       đếm cửa, và hai con số đó không bao giờ lẫn nhau nữa. */
    CUNG: {
      "kinh-thanh":    { goc: "kinh-thanh",    ten: "Kinh Thành",    duong: "../kinh-thanh/" },
      "do-sat-vien":   { goc: "do-sat-vien",   ten: "Đô Sát Viện",   duong: "../do-sat-vien/" },
      "cong-bo":       { goc: "cong-bo",       ten: "Công Bộ",       duong: "../cong-bo/" },
      "tang-thu-cac":  { goc: "tang-thu-cac",  ten: "Tàng Thư Các",  duong: "../tang-thu-cac/" },
      "tao-bien-xu":   { goc: "tao-bien-xu",   ten: "Tạo Biện Xứ",   duong: "../tao-bien-xu/#/van-hanh" },
      "tu-cam-thanh":  { goc: "tu-cam-thanh",  ten: "Tử Cấm Thành",  duong: "../tu-cam-thanh/" },
      "dai-quan-trac": { goc: "dai-quan-trac", ten: "Đài Quan Trắc", duong: "../dai-quan-trac/" },
      "hoang-thanh":   { goc: "hoang-thanh",   ten: "Hoàng Thành",   duong: "../hoang-thanh/" },
      "hb-tien-cho":   { goc: "ho-bo", ten: "Hộ Bộ · Tiền Chờ",   duong: "../ho-bo/#/tien-cho" },
      "hb-dong-tien":  { goc: "ho-bo", ten: "Hộ Bộ · Dòng Tiền",  duong: "../ho-bo/#/dong-tien" },
      "hb-nhom":       { goc: "ho-bo", ten: "Hộ Bộ · Nhóm Ngành", duong: "../ho-bo/#/nhom-nganh" },
      "hb-loi-suat":   { goc: "ho-bo", ten: "Hộ Bộ · Lợi Suất",   duong: "../ho-bo/#/loi-suat" },
      "hb-an-ninh":    { goc: "ho-bo", ten: "Hộ Bộ · An Ninh",    duong: "../ho-bo/#/an-ninh" }
    },

    TOA: [
      {
        ma: "t01", so: "01", ten: "Nền tảng & thanh toán cuối", songSot: 1,
        lat: "Mặt đất để xây thành phố.",
        nguoi: ["ETH", "SOL", "BNB", "ADA", "AVAX", "TRX", "SUI", "TON", "NEAR", "APT", "HBAR", "XLM"],
        lam: "Giữ trạng thái tài sản và kết sổ giao dịch mà không cần một sổ cái trung tâm nào.",
        vao: "điện, phần cứng, người vận hành nút, tài sản đặt cọc",
        ra: "quyền sở hữu chứng minh được · thanh toán cuối · môi trường chạy hợp đồng",
        dua: ["hạ tầng vật lý", "an ninh kinh tế của toa 08"],
        nuoi: ["toàn bộ 17 toa còn lại"],
        y: "Toa cuối cùng. Mọi thứ khác đứng trên nó; nó không đứng trên thứ gì trong đoàn tàu này. " +
           "Không có nghĩa mọi L1 hiện nay đều sống — phần lớn có thể biến mất, và cuộc thanh lọc " +
           "đó diễn ra ngay BÊN TRONG toa này chứ không phải giữa toa này với toa khác.",
        cung: ["kinh-thanh"]
      },
      {
        ma: "t02", so: "02", ten: "Mở rộng & thực thi", songSot: 5,
        lat: "Tăng số làn đường của blockchain.",
        nguoi: ["ARB", "OP", "STRK", "ZK", "MNT", "POL", "METIS", "IMX", "BLAST", "SCR"],
        lam: "Gom giao dịch, hạ chi phí, tăng thông lượng — trong khi vẫn dựa vào lớp nền bên dưới cho một phần bảo mật.",
        vao: "chuỗi nền, người sắp xếp giao dịch, hệ chứng minh",
        ra: "giao dịch rẻ hơn và nhanh hơn",
        dua: ["toa 01 để kết sổ", "toa 03 để bắc cầu tài sản sang"],
        nuoi: ["ứng dụng cần phí thấp: game, thanh toán nhỏ, giao dịch tần suất cao"],
        y: "Đây là bộ tăng tốc, không phải bộ máy. Mất nó thì mọi thứ đắt hơn và chậm hơn, " +
           "nhưng chuỗi nền vẫn kết sổ. Đúng cảnh trong phim: bỏ tiện nghi, giữ thứ khiến " +
           "đoàn tàu còn là đoàn tàu.",
        cung: ["do-sat-vien"]
      },
      {
        ma: "t03", so: "03", ten: "Oracle & liên chuỗi", songSot: 4,
        lat: "Hệ thần kinh và khớp nối giữa các toa.",
        nguoi: ["LINK", "PYTH", "ZRO", "AXL", "W", "QNT", "API3", "BAND", "TRB", "UMA"],
        lam: "Đưa dữ liệu ngoài chuỗi vào trong chuỗi, và chuyển tài sản/thông điệp giữa các chuỗi.",
        vao: "giá từ sàn, dữ liệu thật, người vận hành nút oracle",
        ra: "một con số mà hợp đồng thông minh dám tin",
        dua: ["nguồn dữ liệu ngoài", "chính các chuỗi nó phục vụ"],
        nuoi: ["toa 06 tín dụng", "toa 07 phái sinh", "toa 09 RWA", "toa 04 tiền ổn định"],
        y: "Toa có hệ số lan truyền lớn nhất so với kích thước của nó. Vốn hoá một dự án oracle " +
           "không nói lên bao nhiêu tiền đang treo trên nó — phòng Khớp Nối trong cung này đo " +
           "đúng khoảng cách đó. Mất oracle thì một chuỗi đơn lẻ vẫn đồng thuận và vẫn chuyển " +
           "được tài sản gốc; nhưng mọi thứ cần biết giá thì mù.",
        cung: ["cong-bo"]
      },
      {
        ma: "t04", so: "04", ten: "Tiền ổn định", songSot: 2,
        lat: "Tiền mặt chạy trong đoàn tàu.",
        nguoi: ["USDT", "USDC", "USDS", "DAI", "USDe", "FDUSD", "PYUSD", "FRAX", "GHO", "crvUSD"],
        lam: "Giữ một đơn vị tính toán ổn định để mọi toa khác định giá, thế chấp và kết sổ theo nó.",
        vao: "tài sản dự trữ, nhà phát hành, kênh đổi ra tiền pháp định",
        ra: "vốn lưu động on-chain",
        dua: ["toa 01 làm đường ray kết sổ", "hệ thống ngân hàng ngoài chuỗi"],
        nuoi: ["toa 05, 06, 07, 09, 10 — gần như mọi hoạt động tài chính"],
        y: "Toa áp chót. Một nền kinh tế có thể mất phái sinh, tín dụng, RWA mà vẫn còn lý do " +
           "tồn tại cho tiền ổn định. Nhưng bản thân nó vẫn phải đứng trên một đường ray kết sổ, " +
           "nên nó chưa phải toa cuối. Đo bằng LƯỢNG LƯU HÀNH chứ không phải TVL của nhà phát hành — " +
           "hai con số đó lệch nhau hai bậc độ lớn.",
        cung: ["hb-tien-cho"]
      },
      {
        ma: "t05", so: "05", ten: "Thanh khoản & chợ", songSot: 3,
        lat: "Chợ đầu mối.",
        nguoi: ["UNI", "JUP", "CAKE", "CRV", "RAY", "SUSHI", "BAL", "COW", "1INCH", "OSMO"],
        lam: "Đổi tài sản A lấy tài sản B, và trong lúc làm việc đó thì phát hiện ra giá.",
        vao: "vốn của người cung cấp thanh khoản, nhu cầu giao dịch",
        ra: "giá tham chiếu · khả năng thoát khỏi một vị thế",
        dua: ["toa 04 làm cặp đối ứng", "toa 01 để kết sổ"],
        nuoi: ["toa 06 định giá tài sản thế chấp", "toa 07 tính giá đánh dấu", "toa 09"],
        y: "Không có toa này thì tài sản vẫn tồn tại nhưng khó đổi. Mất thanh khoản là mất " +
           "phát hiện giá, mà mất phát hiện giá thì tín dụng, phái sinh và RWA cùng lúc mất oxy. " +
           "Một trong ba toa sống dai nhất.",
        cung: ["hb-dong-tien"]
      },
      {
        ma: "t06", so: "06", ten: "Tín dụng & cho vay", songSot: 7,
        lat: "Ngân hàng tín dụng của đoàn tàu.",
        nguoi: ["AAVE", "COMP", "MORPHO", "SYRUP", "EUL", "XVS", "GFI", "CPOOL", "TRU", "MPL"],
        lam: "Biến vốn nhàn rỗi thành vốn đang làm việc, thông qua tài sản thế chấp.",
        vao: "vốn gửi vào, tài sản thế chấp, giá từ oracle",
        ra: "đòn bẩy · lợi suất cho người gửi",
        dua: ["toa 03 để định giá thế chấp", "toa 05 để thanh lý", "toa 04 làm đơn vị vay"],
        nuoi: ["toa 07", "mọi chiến lược dùng đòn bẩy"],
        y: "Bắt đầu thực sự đau. Nhưng tín dụng nằm PHÍA TRÊN những thứ cơ bản hơn: phải có vốn, " +
           "thế chấp, thanh khoản và giá thì mới có tín dụng. Hết nhiên liệu thì tín dụng cháy " +
           "trước, còn vốn thì vẫn tồn tại.",
        cung: ["hb-loi-suat"]
      },
      {
        ma: "t07", so: "07", ten: "Phái sinh & thị trường rủi ro", songSot: 13,
        lat: "Nơi mua bán rủi ro và kỳ vọng tương lai.",
        nguoi: ["HYPE", "DYDX", "GMX", "SNX", "DRIFT", "AEVO", "PERP", "GNS", "RDNT"],
        lam: "Tạo ra vị thế lớn hơn vốn thật, và cho phép chuyển rủi ro từ người này sang người khác.",
        vao: "tài sản cơ sở, giá đánh dấu, ký quỹ",
        ra: "đòn bẩy · phòng hộ · khuếch đại biến động",
        dua: ["toa 05 để có giá", "toa 03 để có giá đánh dấu", "toa 04 làm ký quỹ"],
        nuoi: ["không toa nào — đây là tầng trên cùng của tháp tài chính"],
        y: "Toa khuếch đại: nó không tạo thêm tài sản cơ sở, chỉ tạo thêm quyền đòi. Phải có tài " +
           "sản trước rồi mới có phái sinh của tài sản, nên tháo ngược hệ thống thì nó rơi trước " +
           "thị trường giao ngay. Giống toa không tạo ra than nhưng khiến đoàn tàu chạy nhanh hơn.",
        cung: ["tu-cam-thanh"]
      },
      {
        ma: "t08", so: "08", ten: "Đặt cọc & tái đặt cọc", songSot: 12,
        lat: "Động cơ tạo an ninh kinh tế.",
        nguoi: ["LDO", "RPL", "JTO", "EIGEN", "ETHFI", "REZ", "SSV", "ANKR", "SWELL"],
        lam: "Biến vốn thành an ninh cho mạng lưới, rồi biến vốn đã khoá đó thành thanh khoản trở lại.",
        vao: "tài sản gốc của chuỗi, người xác thực",
        ra: "an ninh kinh tế · chứng chỉ đặt cọc có thanh khoản",
        dua: ["toa 01 — không có chuỗi thì không có gì để bảo vệ"],
        nuoi: ["toa 01 (an ninh)", "toa 05, 06 (chứng chỉ dùng làm thế chấp)"],
        y: "Điểm đặc biệt: TÁI đặt cọc chết trước đặt cọc gốc. Khi hệ thống tháo bớt phức tạp thì " +
           "các tầng chồng lên nhau — tái đặt cọc có thanh khoản, tái đặt cọc, chứng chỉ đặt cọc — " +
           "rụng dần từ trên xuống, còn phần đặt cọc gốc thì hoà trở lại vào toa 01 thay vì tồn " +
           "tại như một nền kinh tế token riêng.",
        cung: ["hb-nhom"]
      },
      {
        ma: "t09", so: "09", ten: "Tài sản thế giới thật", songSot: 8,
        lat: "Chỗ đoàn tàu blockchain móc vào đoàn tàu kinh tế thật.",
        nguoi: ["ONDO", "CFG", "POLYX", "XDC", "PLUME", "CHEX", "OM", "PRO", "RIO", "GFI"],
        lam: "Đưa trái phiếu, tín dụng, bất động sản và cổ phần lên chuỗi dưới dạng token.",
        vao: "tài sản thật, người giữ hộ, cấu trúc pháp lý, oracle",
        ra: "công cụ tài chính đã token hoá",
        dua: ["toà án và luật ngoài chuỗi", "người giữ hộ", "toa 03", "toa 04"],
        nuoi: ["toa 06 (thế chấp chất lượng cao)", "toa 05"],
        y: "Toa mạnh nhưng có một điểm yếu Runaway rất rõ: nó cần thế giới bên ngoài. Chuỗi mắt " +
           "xích dài — kho bạc, người giữ hộ, pháp lý, token hoá, chuỗi, oracle, tiền ổn định, " +
           "chợ, ví — và đứt một khâu là cả đường chảy ngừng. Đây cũng là lý do RWA không thể là " +
           "toa cuối: khi cầu nối với tài chính truyền thống gặp khủng hoảng, một tài sản tiền tệ " +
           "thuần on-chain còn khả năng tồn tại độc lập hơn.",
        cung: ["hb-nhom"]
      },
      {
        ma: "t10", so: "10", ten: "Thanh toán & chuyển giá trị", songSot: 6,
        lat: "Chuyển giá trị từ A sang B.",
        nguoi: ["XRP", "XLM", "LTC", "BCH", "XNO", "CELO", "DASH", "XEC", "TEL", "ACH"],
        lam: "Đưa giá trị đi xa, nhanh, rẻ — và đó là trọng tâm chứ không phải một tính năng phụ.",
        vao: "mạng lưới, thanh khoản hai đầu, kênh đổi tiền pháp định",
        ra: "giá trị đã tới tay người nhận",
        dua: ["toa 01 hoặc mạng riêng của chính nó"],
        nuoi: ["người dùng cuối", "kiều hối", "thương mại"],
        y: "Đã rất sát lõi. Nhưng một mạng kết sổ tiền tệ như Bitcoin TỰ NÓ đã chuyển được giá " +
           "trị, nên mạng thanh toán chuyên biệt vẫn có thể mất mà kết sổ tiền tệ chưa chết. " +
           "Một mạng hoàn toàn có thể vừa là L1 vừa là đường thanh toán — đây đúng là trường hợp " +
           "cần phân biệt trách nhiệm chính với trách nhiệm phụ.",
        cung: ["kinh-thanh"]
      },
      {
        ma: "t11", so: "11", ten: "DePIN · máy móc & tài nguyên", songSot: 9,
        lat: "Cơ sở vật chất của nền kinh tế số.",
        nguoi: ["FIL", "AR", "HNT", "AKT", "RENDER", "IOTX", "AIOZ", "GRASS", "IO", "FLUX", "DIMO"],
        lam: "Dùng phần thưởng token để điều phối tài nguyên VẬT LÝ: lưu trữ, tính toán, GPU, sóng, cảm biến.",
        vao: "phần cứng thật, điện, người vận hành",
        ra: "dung lượng lưu trữ · năng lực tính toán · vùng phủ sóng",
        dua: ["toa 01 để trả công", "nhu cầu thật từ người mua"],
        nuoi: ["toa 12 (AI cần compute)", "ứng dụng cần lưu trữ"],
        y: "Từ đây các toa khó đốt hơn nhiều, vì chúng đại diện cho tài nguyên THẬT. Nhưng một " +
           "blockchain tiền tệ vẫn tồn tại được nếu nó không điều phối GPU hay sóng — nên vẫn " +
           "tháo được. TVL không đo được toa này: chẳng ai khoá vốn vào một mạng lưu trữ để nó " +
           "chạy, thứ đo đúng là dung lượng và doanh thu dịch vụ.",
        cung: ["tao-bien-xu"]
      },
      {
        ma: "t12", so: "12", ten: "AI · dữ liệu & tác tử", songSot: 16,
        lat: "Người lao động máy sắp trèo lên tàu.",
        nguoi: ["TAO", "FET", "VIRTUAL", "OLAS", "KAITO", "GRT", "PHALA", "ORAI", "AIXBT"],
        lam: "Cho tác tử phần mềm một cái ví, một danh tính và khả năng tự mua bán dịch vụ.",
        vao: "compute, dữ liệu, mô hình, ví",
        ra: "quyết định tự động · dịch vụ bán được",
        dua: ["toa 11 để có compute", "toa 01 để thanh toán", "toa 13 để có danh tính"],
        nuoi: ["chưa nuôi toa nào ở quy mô đáng kể — còn là phôi thai"],
        y: "Cần tách một ngoại lệ lớn: hạ tầng AI thật, compute thật, dữ liệu thật có thể rất " +
           "quan trọng và sống lâu hơn vị trí trung bình của toa. Nhưng hàng loạt token kể chuyện " +
           "về AI thì có thể bị đốt trước khi hạ tầng tài chính cốt lõi bị đụng tới. Ví cho tác " +
           "tử thì đã có; hiến pháp kinh tế cho tác tử thì chưa.",
        cung: ["tao-bien-xu", "tang-thu-cac"]
      },
      {
        ma: "t13", so: "13", ten: "Danh tính & xã hội", songSot: 15,
        lat: "Chuỗi biết 'tài sản nào', còn cần biết 'ai'.",
        nguoi: ["WLD", "ENS", "MASK", "CYBER", "GAL", "ID", "RSS3", "LIT", "KEY", "CVC"],
        lam: "Trả lời ai, tác tử nào, chứng chỉ nào, quyền gì, danh tiếng gì — mà không phải phơi hết đời tư.",
        vao: "bằng chứng, chứng chỉ, đồ thị quan hệ",
        ra: "một khẳng định kiểm chứng được về một chủ thể",
        dua: ["toa 01", "mật mã zero-knowledge"],
        nuoi: ["toa 06 (tín dụng không cần thế chấp quá mức)", "toa 12 (tác tử cần chứng chỉ)"],
        y: "Rất quan trọng với một nền kinh tế trưởng thành, nhưng khi đoàn tàu vào chế độ sinh " +
           "tồn thì 'tôi là ai, danh tiếng tôi thế nào' đều đứng sau 'tiền của tôi ở đâu, có " +
           "chuyển được không, kết sổ còn chạy không'. Nên nó tiếp tục bị giảm tải.",
        cung: ["tang-thu-cac"]
      },
      {
        ma: "t14", so: "14", ten: "Riêng tư", songSot: 10,
        lat: "Không phải mọi blockchain đều nên lộ toàn bộ dữ liệu.",
        nguoi: ["XMR", "ZEC", "SCRT", "ROSE", "DUSK", "NYM", "FIRO", "ZANO"],
        lam: "Cho phép giao dịch, trạng thái và tính toán diễn ra mà không phơi ra công khai.",
        vao: "mật mã, người dùng cần kín",
        ra: "giao dịch riêng tư · tính toán bảo mật",
        dua: ["toa 01, hoặc mạng riêng của chính nó"],
        nuoi: ["doanh nghiệp không thể chạy chuỗi cung ứng công khai"],
        y: "Riêng tư là tiện ích thật, nhưng lớp riêng tư không phải điều kiện bắt buộc để kết " +
           "sổ công khai tồn tại. Một ngoại lệ rất lớn là XMR: nó gần một đoàn tàu tiền tệ độc " +
           "lập hơn là một toa riêng tư — và đó đúng là lý do phải xếp theo trách nhiệm của từng " +
           "tài sản chứ không thể giết cả một nhóm cùng một lúc.",
        cung: ["cong-bo"]
      },
      {
        ma: "t15", so: "15", ten: "Game · NFT · metaverse", songSot: 17,
        lat: "Ứng dụng của blockchain, không phải điều kiện để nó tồn tại.",
        nguoi: ["RON", "GALA", "AXS", "SAND", "MANA", "BEAM", "ILV", "PRIME", "YGG", "PIXEL"],
        lam: "Đưa quyền sở hữu, vật phẩm và nền kinh tế người chơi lên chuỗi.",
        vao: "người chơi, nội dung, chuỗi rẻ",
        ra: "tài sản trong game có thể bán ra ngoài",
        dua: ["toa 02 để phí đủ rẻ", "toa 05 để đổi ra tiền"],
        nuoi: ["không toa nào"],
        y: "Nếu chúng biến mất thì BTC vẫn chạy, ETH vẫn chạy, USDC vẫn chuyển, chợ vẫn đổi, " +
           "cho vay vẫn chạy. Tháo được. NFT chỉ là một nguyên thuỷ bên trong toa này chứ không " +
           "nhất thiết là toàn bộ toa.",
        cung: ["hoang-thanh"]
      },
      {
        ma: "t16", so: "16", ten: "Meme · văn hoá & chú ý", songSot: 18,
        lat: "Toa bán thứ không ai gọi là hạ tầng.",
        nguoi: ["DOGE", "SHIB", "PEPE", "BONK", "WIF", "FLOKI", "PENGU", "BRETT", "SPX"],
        lam: "Định lượng sự chú ý, cộng đồng và đồng thuận xã hội thành một tài sản giao dịch được.",
        vao: "sự chú ý, cộng đồng, câu chuyện",
        ra: "thanh khoản đầu cơ · người dùng mới bước vào hệ",
        dua: ["toa 05 để giao dịch", "toa 02 để phí rẻ"],
        nuoi: ["không toa nào — nhưng nó kéo người mới vào cả đoàn tàu"],
        y: "Bị đốt đầu tiên, và điều đó KHÔNG có nghĩa mọi meme coin chết trước mọi dự án khác. " +
           "Ý ở đây là CHỨC NĂNG 'tài sản chú ý' là thứ hệ thống có thể bỏ mà kết sổ vẫn chạy, " +
           "khối vẫn được tạo, tài sản vẫn chuyển được. Trong bảng xếp theo trách nhiệm thì meme " +
           "không phải 'coin vô dụng' — nó là một loại tài sản có trách nhiệm rõ ràng, chỉ là " +
           "trách nhiệm đó bỏ được trước nhất.",
        cung: ["dai-quan-trac"]
      },
      {
        ma: "t17", so: "17", ten: "Cửa vốn & sàn", songSot: 14,
        lat: "Cổng giữa tiền pháp định và vốn crypto.",
        nguoi: ["BNB", "OKB", "BGB", "CRO", "LEO", "KCS", "GT", "MX"],
        lam: "Nhận tiền pháp định vào, đưa vốn crypto ra, và giữ hộ phần lớn số đó.",
        vao: "người dùng, ngân hàng, giấy phép",
        ra: "vốn đã vào được trong hệ · thanh khoản tập trung",
        dua: ["hệ thống ngân hàng", "luật pháp từng nước"],
        nuoi: ["toàn bộ đoàn tàu, ở khâu nạp vốn"],
        y: "Lưu ý phân biệt: TOKEN sàn khác với CHỨC NĂNG sàn. Token ưu đãi — giảm phí, hạng VIP, " +
           "bệ phóng — không phải cấu kiện tối thiểu của blockchain, nên hạng sống sót ở đây nói " +
           "về token. Còn bản thân cửa vốn thì rất khó bỏ. BNB là ngoại lệ vì nó còn gắn với một " +
           "chuỗi, nên không thể đánh giá nó chỉ như một token sàn.",
        cung: ["hb-an-ninh"]
      },
      {
        ma: "t18", so: "18", ten: "Kinh tế Bitcoin · BTCFi", songSot: 11,
        lat: "Toa quay ngược trở lại đầu tàu.",
        nguoi: ["STX", "CORE", "BABY", "MERL", "SOLV", "ORDI", "SATS", "RUNE"],
        lam: "Mở rộng khả năng sử dụng BTC ra ngoài chức năng chuyển BTC cơ bản.",
        vao: "BTC, cầu nối, chuỗi phụ",
        ra: "lợi suất trên BTC · ứng dụng trên hệ Bitcoin",
        dua: ["Bitcoin", "cầu nối — tức toa 03"],
        nuoi: ["người giữ BTC muốn BTC làm việc"],
        y: "Nằm sát đầu tàu về mặt câu chuyện, nhưng Bitcoin KHÔNG cần cho vay BTC, lợi suất BTC, " +
           "Ordinals hay Runes để bản thân nó tiếp tục tồn tại. Nên trong kịch bản Runaway, BTCFi " +
           "cháy còn BTC vẫn chạy.",
        cung: ["kinh-thanh"]
      }
    ],

    /* ═══════════ THANG TIẾN HOÁ ═══════════
       Đây là ĐÁNH GIÁ KIẾN TRÚC lấy từ tài liệu nguồn, KHÔNG phải
       số đo và không có API nào chấm được. Giao diện phải hiện nó
       dưới nhãn "luận" — một thanh phần trăm trông y hệt một phép
       đo, và đó chính là lý do phải nói rõ nó không phải phép đo. */
    THANG: [
      { so: "1",  ten: "Tiền & thanh toán cuối",       muc: 90, y: "Bitcoin, Ethereum và nhiều L1 đã chứng minh giữ được trạng thái tài sản mà không cần một sổ cái trung tâm." },
      { so: "2",  ten: "Thị trường vốn on-chain",      muc: 80, y: "Chợ, cho vay, thế chấp, phái sinh, quản lý tài sản đều đã có bản chạy được." },
      { so: "3",  ten: "RWA & DePIN · thế giới thật",  muc: 50, y: "Cánh cửa giữa hai đoàn tàu đã mở, nhưng mới là một cửa nhỏ." },
      { so: "4",  ten: "Kinh tế tác tử AI",            muc: 25, y: "Ví, thanh toán và chuẩn danh tính cho tác tử đã bắt đầu có; trách nhiệm pháp lý thì chưa." },
      { so: "5",  ten: "Kinh tế máy móc",              muc: 10, y: "Từng mảnh DePIN đã chạy, nhưng chưa có một tầng chung để hàng tỷ máy tự mua bán với nhau." },
      { so: "6",  ten: "Công ty → giao thức",          muc: 10, y: "Một số chức năng của công ty đã thành mã, phần lớn thì chưa." },
      { so: "7",  ten: "Nhà nước → giao thức công",    muc: 5,  y: "Kho bạc công on-chain còn là thử nghiệm lẻ." },
      { so: "8",  ten: "Kinh tế tự điều chỉnh",        muc: 1,  y: "Đã có phản xạ cục bộ — thanh lý, chênh lệch giá, đấu giá. Chưa có tầng nhìn toàn hệ." },
      { so: "9",  ten: "Kinh tế tự tiến hoá",          muc: 0,  y: "Gần như còn ở mức nghiên cứu và giả thuyết." },
      { so: "10", ten: "Cơ thể kinh tế hành tinh",     muc: 0,  y: "Viễn cảnh dài hạn." }
    ],

    /* Những khớp nối tài liệu chỉ ra là CÒN THIẾU. Không đo được,
       nên đứng riêng như một danh sách việc chưa làm chứ không trộn
       vào bảng số. */
    THIEU: [
      { ten: "Tầng trạng thái thế giới", y: "Chuỗi biết rất rõ ví A có bao nhiêu ETH, và biết rất kém nhà máy A đang sản xuất bao nhiêu." },
      { ten: "Oracle cho thứ khó đo",    y: "Giá BTC/USD thì dễ. 'Nhà máy đã xây xong 87% chưa' thì khó hơn rất nhiều — và hợp đồng càng hoàn hảo thì càng thực thi sai một cách hoàn hảo khi đầu vào sai." },
      { ten: "Danh tính giữ được riêng tư", y: "Cần phân biệt người, công ty, máy, tác tử — mà không biến chuỗi công khai thành nơi phơi toàn bộ đời tư." },
      { ten: "Ví đủ dễ cho mọi người",   y: "Cụm 12 từ, gas, nonce, cầu nối, đổi mạng — không thể là điều kiện để tham gia một nền kinh tế." },
      { ten: "Thanh khoản thống nhất",   y: "Cùng một đồng USDC bị chia thành nhiều đảo trên nhiều chuỗi." },
      { ten: "Trạng thái pháp lý = trạng thái on-chain", y: "Token nói ví A sở hữu 1% toà nhà; toà án có nói vậy không lại là chuyện khác." },
      { ten: "Tín dụng không cần thế chấp quá mức", y: "Kinh tế thật chạy bằng dòng tiền tương lai và danh tiếng, không chỉ bằng tài sản đã có." },
      { ten: "Tư cách kinh tế cho tác tử", y: "Tác tử gây thiệt hại thì ai chịu, tác tử vay tiền thì ai bảo lãnh — ví thì đã có, luật thì chưa." },
      { ten: "Thực thi ở thế giới vật lý", y: "Hợp đồng chuyển token rất giỏi, xây cầu và sửa máy thì không." },
      { ten: "Tầng xử lý tranh chấp",    y: "Mã nghĩ theo đúng–sai; đời sống đầy nhầm lẫn, ép buộc, thừa kế, bất khả kháng." },
      { ten: "Ai đặt hàm mục tiêu",      y: "Tối đa hoá GDP, bình đẳng, tự do hay giảm phát thải sẽ ra bốn phương án khác nhau — và máy không tự chọn được." },
      { ten: "Cỗ máy giữ thăng bằng",    y: "Hệ thống có phản xạ cục bộ nhưng chưa có chỗ nào nhìn thấy chính nó đang tiến tới mất kiểm soát." }
    ]
  };
})();
