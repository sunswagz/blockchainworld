/* ═══════════════════════════════════════════════════════
   Chú giải Tàng Thư Các.

   Đây là file quan trọng nhất của cung này, và là file duy nhất
   KHÔNG tự sinh.

   Mô tả gốc của skill viết cho MÁY đọc — nó trả lời "khi nào thì
   agent nên tự bật skill này". Người đọc lại cần biết chuyện khác:
   nó làm được gì, và nó giúp ĐƯỢC GÌ CHO MÌNH.

   Nên mỗi skill chính thức ở đây có bốn phần:
     tom    — một câu, nó là cái gì
     lam    — làm được những việc cụ thể nào (danh sách)
     khi    — khi nào Claude tự bật nó lên
     ban    — với hệ thống của BẠN (webapp tĩnh, PWA nhiều cung,
              GitHub Actions, Việt hoá, dữ liệu blockchain) thì
              dùng vào việc gì. Đây là phần không kho nào khác có.

   Bản dịch khoá theo ĐÚNG kho anthropics/skills, không tra theo tên:
   tên trùng giữa các kho rất thường, và skill cùng tên ở kho khác làm
   việc khác. Mọi skill còn lại giữ nguyên bản gốc — bịa mô tả tiếng
   Việt cho skill mình chưa đọc còn tệ hơn để nguyên bản.
   ═══════════════════════════════════════════════════════ */
window.TT_VI = {

  /* ── ba màn hình ──────────────────────────────────── */
  muc: {
    "tong-quan": {
      ten: "Tổng quan",
      y: "Toàn bộ skill chia theo nhóm việc — nhìn một cái là biết có những loại đồ nghề gì.",
      vn: "Bắt đầu từ đây nếu bạn chưa biết mình cần gì. Mỗi ô là một nhóm việc, bấm vào để xem skill trong nhóm."
    },
    "danh-muc": {
      ten: "Danh mục skill",
      y: "Tra từng skill: nó làm gì, khi nào Claude tự bật, và cách cài. Bản trùng đã gộp, mỗi skill chỉ còn một mục.",
      vn: "17 skill trong kho anthropics/skills được dịch và diễn giải tay vì tôi đã đọc từng SKILL.md. Mọi skill còn lại — kể cả skill do Anthropic sở hữu ở kho khác — giữ nguyên bản gốc và có đánh dấu."
    },
    "xu-huong": {
      ten: "Xu hướng",
      y: "Kho nào đang tăng sao nhanh nhất trong 24 giờ, 7 ngày, 30 ngày.",
      vn: "GitHub KHÔNG cho biết một kho có bao nhiêu sao trong quá khứ — chỉ có số hiện tại. Nên Tàng Thư Các tự ghi một mốc mỗi lần cập nhật rồi lấy hiệu. Nghĩa là bảng này rỗng lúc đầu và đầy dần theo thời gian: 24 giờ có sau một ngày, 30 ngày có sau một tháng."
    },
    "lich-su": {
      ten: "Lịch sử cập nhật",
      y: "Mỗi lần cập nhật đã thêm hay bớt kho nào, skill nào.",
      vn: "Chỉ ghi những lần CÓ thay đổi thật. Lần chạy nào cũng ghi một dòng thì nhật ký thành rác, phải lội qua hàng chục dòng trống mới thấy cái đáng xem."
    },
    "xep-hang": {
      ten: "Xếp hạng kho",
      y: "Các kho skill trên GitHub, sắp theo số sao, kèm số skill quét được.",
      vn: "Dò bằng bốn truy vấn gộp lại cộng danh sách gọi thẳng — một thẻ là không đủ, vì kho lớn nhất hệ sinh thái (obra/superpowers) không gắn thẻ claude-skills, còn mattpocock/skills và garrytan/gstack thì không gắn thẻ nào. Số sao là của cả kho, không phải của từng skill."
    }
  },

  /* ── nhóm việc ────────────────────────────────────── */
  nhom: {
    "giao-dien":  { ten: "Giao diện & thiết kế", mau: "#8B7FE8", y: "Dựng UI, chọn màu, làm hình, làm artifact." },
    "tai-lieu":   { ten: "Tài liệu",             mau: "#3DBB69", y: "Đọc và tạo PDF, Word, Excel, PowerPoint." },
    "lap-trinh":  { ten: "Lập trình & công cụ",  mau: "#4C9AFF", y: "Viết mã, gọi API, dựng MCP, tạo skill mới." },
    "kiem-thu":   { ten: "Kiểm thử & rà soát",   mau: "#F0B429", y: "Chạy thử, bắt lỗi, soi bảo mật." },
    "du-lieu":    { ten: "Dữ liệu & phân tích",  mau: "#FF46A2", y: "Xử lý số liệu, vẽ biểu đồ, truy vấn." },
    "ha-tang":    { ten: "Hạ tầng & vận hành",   mau: "#00B8D9", y: "Triển khai, Docker, CI/CD, máy chủ." },
    "giao-tiep":  { ten: "Giao tiếp & nội dung", mau: "#FF8B00", y: "Viết thư, bài đăng, thông báo nội bộ." },
    "nghien-cuu": { ten: "Nghiên cứu",           mau: "#6554C0", y: "Tra cứu, đọc tài liệu khoa học, tổng hợp." },
    "khac":       { ten: "Chưa xếp nhóm",        mau: "#7A7A88", y: "Máy chưa nhận ra thuộc nhóm nào — đọc mô tả gốc." }
  },

  /* ── 17 skill của kho anthropics/skills, dịch tay ─── */
  skill: {
    "pdf": {
      tom: "Làm mọi việc với file PDF.",
      lam: ["Đọc và bóc chữ, bảng ra khỏi PDF", "Gộp nhiều PDF thành một, hoặc tách ra",
            "Xoay trang, đóng dấu mờ, mã hoá / giải mã", "Điền biểu mẫu PDF",
            "OCR bản scan để tìm kiếm được chữ trong đó"],
      khi: "Bạn nhắc tới một file .pdf, hoặc bảo tạo ra một file PDF.",
      ban: "Xuất báo cáo từ Đô Sát Viện hay Đài Quan Trắc ra PDF để lưu hoặc gửi đi. Cũng dùng để đọc ngược lại whitepaper của các dự án blockchain rồi bóc số ra."
    },
    "docx": {
      tom: "Làm việc với file Word.",
      lam: ["Tạo văn bản Word mới", "Đọc và sửa file .docx có sẵn", "Giữ định dạng, bảng biểu, kiểu chữ"],
      khi: "Có file .docx trong câu chuyện, hoặc bạn bảo soạn một văn bản Word.",
      ban: "Ít dùng cho hệ thống web tĩnh này, trừ khi cần xuất tài liệu bàn giao hoặc bản mô tả dự án cho người khác đọc."
    },
    "xlsx": {
      tom: "Làm việc với bảng tính Excel.",
      lam: ["Tạo bảng tính mới có công thức", "Đọc và sửa file .xlsx", "Xử lý nhiều sheet, định dạng ô"],
      khi: "Bảng tính là đầu vào hoặc đầu ra chính của việc bạn nhờ.",
      ban: "Đối chiếu số liệu: xuất bảng xét Layer 2 ra Excel để tự lọc và tính thêm, thay vì phải sửa app."
    },
    "pptx": {
      tom: "Làm việc với PowerPoint.",
      lam: ["Tạo bộ slide mới", "Đọc và sửa file .pptx", "Đặt bố cục, hình, biểu đồ vào slide"],
      khi: "Có file .pptx hoặc .potx dính vào việc, dù chỉ là đọc.",
      ban: "Khi cần trình bày hệ thống bốn cung này cho ai đó — dựng slide từ chính số liệu đang có."
    },
    "doc-coauthoring": {
      tom: "Cùng viết tài liệu theo quy trình có bước rõ ràng.",
      lam: ["Hỏi rõ mục đích và người đọc trước khi viết", "Dựng dàn ý rồi mới viết chi tiết",
            "Sửa theo góp ý qua nhiều vòng"],
      khi: "Bạn muốn viết một tài liệu dài mà chưa rõ nên bắt đầu từ đâu.",
      ban: "Viết README cho từng cung, hoặc ghi lại quyết định kiến trúc — đúng loại việc mà viết một mạch thì rối, có quy trình thì gọn."
    },
    "frontend-design": {
      tom: "Hướng dẫn thiết kế giao diện có chủ ý, không rơi vào mặc định nhàn nhạt.",
      lam: ["Chọn bảng màu và kiểu chữ có tính cách", "Dựng hệ thống khoảng cách, tỉ lệ nhất quán",
            "Tránh những mẫu giao diện AI hay lặp lại"],
      khi: "Bạn nhờ dựng giao diện mới hoặc sửa lại giao diện cũ cho đẹp hơn.",
      ban: "Rất hợp. Bốn cung đang có bốn bảng màu riêng — skill này là thứ giữ cho chúng khác nhau có lý do chứ không phải ngẫu nhiên."
    },
    "canvas-design": {
      tom: "Vẽ hình đẹp xuất ra .png và .pdf theo nguyên tắc thiết kế.",
      lam: ["Dựng poster, sơ đồ, hình minh hoạ", "Bố cục theo lưới và tỉ lệ", "Xuất ra ảnh hoặc PDF in được"],
      khi: "Bạn cần một tấm hình chứ không phải một trang web.",
      ban: "Làm ảnh bìa cho từng cung, hoặc sơ đồ giải thích mô hình Cổng Thành → các cung."
    },
    "theme-factory": {
      tom: "Khoác một bộ chủ đề đồng nhất lên artifact.",
      lam: ["Sinh bảng màu sáng/tối đồng bộ", "Áp cùng một chủ đề cho slide, tài liệu, trang web"],
      khi: "Bạn muốn nhiều thứ khác nhau trông như một bộ.",
      ban: "Nếu sau này muốn bốn cung trông đồng bộ hơn, đây là chỗ bắt đầu — thay vì sửa tay bốn file app.css."
    },
    "brand-guidelines": {
      tom: "Áp bộ nhận diện chính thức của Anthropic.",
      lam: ["Dùng đúng màu và font thương hiệu Anthropic"],
      khi: "Làm thứ gì đó mang nhận diện của Anthropic.",
      ban: "Gần như không dùng — hệ thống của bạn có nhận diện riêng (SUNSWaGz), không phải của Anthropic."
    },
    "web-artifacts-builder": {
      tom: "Bộ đồ nghề dựng artifact HTML nhiều thành phần cho claude.ai.",
      lam: ["Dựng trang HTML phức tạp chạy trong artifact", "Ghép nhiều thành phần trong một file"],
      khi: "Bạn nhờ làm một artifact web nhiều phần trên claude.ai.",
      ban: "Khác đường với hệ thống này: bạn xuất bản lên GitHub Pages chứ không phải artifact. Chỉ hữu ích khi cần dựng bản nháp nhanh để xem trước."
    },
    "algorithmic-art": {
      tom: "Vẽ tranh bằng thuật toán với p5.js.",
      lam: ["Sinh hình theo quy luật với hạt ngẫu nhiên cố định", "Làm hình tương tác chạy trong trình duyệt"],
      khi: "Bạn muốn hình sinh ra từ mã chứ không phải vẽ tay.",
      ban: "Có thể làm hình nền hoặc hoạ tiết riêng cho Cổng Thành. Nhưng nhớ: p5.js là thư viện ngoài, mà các cung đang cố ý không dùng thư viện nào."
    },
    "slack-gif-creator": {
      tom: "Làm ảnh động GIF tối ưu cho Slack.",
      lam: ["Sinh GIF đúng giới hạn kích thước của Slack"],
      khi: "Bạn cần một GIF để đăng lên Slack.",
      ban: "Không dùng — hệ thống này không dính tới Slack."
    },
    "internal-comms": {
      tom: "Viết các loại thông báo nội bộ.",
      lam: ["Soạn thông báo, cập nhật tiến độ, ghi chú họp"],
      khi: "Bạn cần viết thư hay thông báo cho đồng nghiệp.",
      ban: "Ít dùng — hệ thống này hiện chỉ mình bạn dùng, chưa có ai để thông báo."
    },
    "mcp-builder": {
      tom: "Hướng dẫn dựng máy chủ MCP chất lượng tốt.",
      lam: ["Dựng MCP server bằng Python (FastMCP) hoặc Node/TypeScript",
            "Thiết kế tool sao cho model dùng đúng", "Nối API bên ngoài vào cho agent gọi được"],
      khi: "Bạn muốn cho agent gọi được một dịch vụ bên ngoài.",
      ban: "Đây là bước tiếp theo tự nhiên của hệ thống này. Ví dụ: dựng một MCP đọc thẳng dữ liệu bốn cung, để hỏi 'Base đang giữ bao nhiêu' mà không phải mở trang."
    },
    "claude-api": {
      tom: "Sổ tra cứu Claude API và SDK Anthropic.",
      lam: ["Tra mã model, giá, giới hạn", "Cách dùng streaming, tool use, prompt caching",
            "Cách chuyển đổi giữa các đời model"],
      khi: "Bạn hỏi về model, giá, hoặc viết mã gọi Claude API.",
      ban: "Rất hợp. Đài Quan Trắc gọi Claude trong GitHub Actions — mọi lần sửa `build-scan.mjs` đều nên tra sổ này trước, nhất là phần giá và mã model."
    },
    "skill-creator": {
      tom: "Tạo skill mới, sửa skill cũ, và đo xem skill có chạy tốt không.",
      lam: ["Dựng bộ khung một skill đúng chuẩn", "Sửa và cải thiện skill có sẵn",
            "Kiểm xem skill có được kích hoạt đúng lúc không"],
      khi: "Bạn muốn tự viết một skill.",
      ban: "Đúng thứ bạn cần nếu muốn biến những quy tắc riêng của hệ thống này thành skill — ví dụ 'thêm một cung mới' với bảy bước, hoặc quy tắc không để khoá API ra trình duyệt."
    },
    "webapp-testing": {
      tom: "Chạy thử và soi web app đang chạy trên máy, bằng Playwright.",
      lam: ["Bấm và điền vào trang như người thật", "Chụp màn hình trình duyệt",
            "Đọc log console và lỗi mạng", "Tự quản lý vòng đời máy chủ khi test"],
      khi: "Bạn muốn kiểm chứng một thay đổi có thật sự chạy trong trình duyệt hay không.",
      ban: "Chính là việc tôi vẫn làm tay suốt: mở trình duyệt thật, quét 23 mục của Đô Sát Viện, đọc console, chụp ảnh. Skill này gói việc đó lại thành quy trình sẵn."
    }
  },

  /* ── nhãn phụ ─────────────────────────────────────── */
  nhan: {
    chinhChu: "chính thức",
    chuaDich: "nguyên bản gốc",
    trungTen: "cùng tên, khác nội dung",
    khongMoTa: "không có mô tả"
  },

  ghiChuNguon: "Danh mục dò bằng bốn truy vấn tìm kiếm gộp lại, cộng 10 kho gọi thẳng theo danh sách. Bản dịch tay chỉ áp cho kho anthropics/skills, khoá theo đúng kho chứ không tra theo tên skill — tên trùng giữa các kho rất thường."
};
