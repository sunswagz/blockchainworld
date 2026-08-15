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

  /* ── Kho chính chủ THỨ HAI ────────────────────────────
     anthropics/claude-plugins-official: 25 skill, cũng của Anthropic
     nhưng nằm kho khác nên trước nay không có bản Việt nào.

     Khoá theo KHO rồi mới tới tên, đúng luật đã ghi ở đầu file: tên
     trùng giữa các kho là chuyện thường, tra theo tên là có ngày một
     skill mượn bản dịch của skill khác hẳn.

     Vì sao chỉ tới đây mà không dịch tiếp: 2.901 skill thì dịch tay
     không nổi, còn dịch máy phải gọi model — tức tốn tiền thật. Và
     bịa mô tả tiếng Việt cho skill chưa đọc kỹ còn tệ hơn để nguyên
     bản gốc. 42 skill chính chủ là ranh giới đọc hết được. */
  dichKho: {
    "anthropics/claude-plugins-official": {

      /* ── Bộ dựng plugin cho Claude Code ── */
      "skill-development": {
        tom: "Hướng dẫn viết một skill mới cho Claude Code cho đúng chuẩn.",
        lam: ["Dựng khung thư mục skill", "Viết mô tả sao cho Claude tự bật đúng lúc",
              "Chia nội dung theo lớp để không nhồi hết vào một file", "Đóng skill vào plugin"],
        khi: "Bạn bảo \"tạo một skill\", \"viết skill mới\", hoặc hỏi cách sắp xếp nội dung skill.",
        ban: "Đây là skill để tự làm ra skill. Hệ của bạn có bảy cung với quy trình riêng — quy trình gộp về main, luật hook, cách thêm cung mới — toàn thứ đang nằm trong CLAUDE.md dạng chữ. Gói chúng thành skill thì phiên nào cũng theo được mà không phải đọc lại 400 dòng."
      },
      "plugin-structure": {
        tom: "Cách bố trí một plugin Claude Code: thư mục nào chứa gì, plugin.json khai ra sao.",
        lam: ["Dựng khung plugin từ đầu", "Sắp xếp commands / agents / skills / hooks",
              "Viết plugin.json", "Dùng ${CLAUDE_PLUGIN_ROOT} để đường dẫn không vỡ khi đổi máy"],
        khi: "Bạn bảo \"tạo plugin\", \"dựng khung plugin\", hoặc hỏi cấu trúc thư mục plugin.",
        ban: "Nếu sau này bạn muốn đóng gói cả bộ quy trình blockchainworld — kiểm quy trình, nâng version, sinh halls — thành một thứ cài được cho dự án khác, thì đây là khuôn."
      },
      "command-development": {
        tom: "Viết lệnh gạch chéo riêng, kiểu /kiem hay /gop.",
        lam: ["Khai lệnh bằng file markdown", "Nhận tham số truyền vào",
              "Nhúng tham chiếu tới file khác", "Xếp lệnh theo nhóm"],
        khi: "Bạn bảo \"tạo slash command\", \"thêm lệnh\", hoặc hỏi cách truyền tham số cho lệnh.",
        ban: "Repo của bạn đã có bốn lệnh npm hay dùng: kiem, nang, halls, dist. Biến chúng thành lệnh gạch chéo thì gõ /kiem là xong, không phải nhớ tên script."
      },
      "agent-development": {
        tom: "Viết agent con — một Claude phụ có chỉ dẫn riêng, bộ công cụ riêng.",
        lam: ["Viết frontmatter cho agent", "Đặt mô tả \"khi nào dùng\" cho đúng",
              "Chọn bộ công cụ agent được phép dùng", "Thiết kế lời dẫn hệ thống"],
        khi: "Bạn bảo \"tạo agent\", \"viết subagent\", hoặc hỏi về công cụ và màu của agent.",
        ban: "Hợp với việc lặp lại mà tách bạch được — ví dụ một agent chỉ chuyên đọc SKILL.md rồi viết bản Việt bốn phần, đúng việc đang làm dở ở đây."
      },
      "hook-development": {
        tom: "Viết hook để Claude Code tự chạy gì đó trước hoặc sau mỗi thao tác.",
        lam: ["Bắt sự kiện PreToolUse / PostToolUse / Stop", "Chặn thao tác không hợp lệ",
              "Chạy kiểm tra tự động sau mỗi lần sửa file", "Khai hook trong settings.json"],
        khi: "Bạn bảo \"tạo hook\", \"chặn thao tác X\", hoặc muốn tự động hoá theo sự kiện.",
        ban: "Bạn đã có một hook rồi — pre-commit nhắc khi CLAUDE.md cũ hoặc đang dàn file bot sinh. Nhưng đó là hook của git. Hook Claude Code chạm được sớm hơn: chặn ngay lúc phiên định `git add -A`, thay vì nhắc sau khi đã lỡ."
      },
      "plugin-settings": {
        tom: "Cho plugin có cấu hình riêng theo từng người dùng, từng dự án.",
        lam: ["Đọc file .local.md", "Bóc frontmatter YAML làm cấu hình",
              "Giữ trạng thái riêng cho từng dự án", "Tách cài đặt chung với cài đặt dự án"],
        khi: "Bạn hỏi cách lưu cấu hình plugin, hoặc muốn plugin đổi hành vi theo dự án.",
        ban: "Đúng bài toán cổng localhost của bạn: mỗi cung một cổng, hiện đang chép tay trong bảng ở CLAUDE.md. Cấu hình theo dự án thì bảng đó tự đọc được."
      },
      "mcp-integration": {
        tom: "Nối một máy chủ MCP vào plugin để Claude dùng được dịch vụ ngoài.",
        lam: ["Khai máy chủ trong .mcp.json", "Chọn kiểu kết nối (stdio, HTTP, SSE)",
              "Truyền biến môi trường vào máy chủ", "Hiểu quy tắc đặt tên công cụ MCP"],
        khi: "Bạn bảo \"thêm MCP server\", \"nối dịch vụ ngoài\", hoặc nhắc tới .mcp.json.",
        ban: "Nếu muốn Claude đọc thẳng số liệu Actions hay Pinata thay vì bạn đưa ảnh chụp màn hình, thì lối đi là ở đây."
      },

      /* ── Dựng MCP ── */
      "build-mcp-server": {
        tom: "Dựng một máy chủ MCP từ đầu, đi qua năm chặng từ hỏi nhu cầu tới bàn giao.",
        lam: ["Hỏi rõ ca sử dụng trước khi viết dòng nào", "Chọn mô hình triển khai",
              "Chọn kiểu thiết kế công cụ", "Chọn khung, rồi dựng khung sườn"],
        khi: "Bạn bảo \"dựng MCP server\", \"bọc một API cho Claude\", \"đưa công cụ cho Claude dùng\".",
        ban: "Cách chuẩn để đưa dữ liệu ngoài vào Claude. Khác hẳn kiểu Đài Quan Trắc hiện tại — chỗ đó gọi model trong Actions rồi ghi ra file tĩnh, còn MCP là nối trực tiếp lúc đang làm việc."
      },
      "build-mcp-app": {
        tom: "Thêm giao diện thật vào máy chủ MCP — biểu mẫu, bảng chọn, bảng điều khiển hiện ngay trong khung chat.",
        lam: ["Dựng widget giao diện cho công cụ MCP", "Phân biệt khi nào cần widget, khi nào chữ là đủ",
              "Gắn widget vào công cụ", "Chọn giữa hai kiểu triển khai"],
        khi: "Bạn muốn công cụ MCP hiện ra giao diện bấm được chứ không chỉ trả về chữ.",
        ban: "Cùng một tay nghề với việc dựng các cung: HTML tĩnh, tự chứa, không khung nào. Khác chỗ nó sống trong khung chat thay vì một trang riêng."
      },
      "build-mcpb": {
        tom: "Đóng gói máy chủ MCP thành một file .mcpb cài được.",
        lam: ["Gói cả bản chạy Node hoặc Python vào trong", "Viết manifest",
              "Dựng đường ống đóng gói", "Hiểu rõ: MCPB KHÔNG có hộp cát"],
        khi: "Bạn muốn phát hành một máy chủ MCP chạy tại máy cho người khác cài.",
        ban: "Chỗ cần đọc kỹ nhất là câu \"không có hộp cát\": người cài file .mcpb tin bạn hoàn toàn. Cùng thứ cảnh giác mà Tàng Thư Các đang gắn cờ cho skill lạ."
      },

      /* ── Chăm sóc chính Claude Code ── */
      "claude-md-improver": {
        tom: "Soi và sửa các file CLAUDE.md trong kho.",
        lam: ["Quét tìm mọi CLAUDE.md", "Chấm chất lượng theo khuôn mẫu",
              "Xuất báo cáo", "Sửa thẳng những chỗ dở"],
        khi: "Bạn bảo \"kiểm tra CLAUDE.md\", \"cải thiện CLAUDE.md\".",
        ban: "CLAUDE.md của bạn đã hơn 400 dòng và được vá liên tục bởi nhiều phiên song song. Đây là thứ soi giúp — nhưng nhớ: nó chấm theo khuôn chung, còn `npm run kiem` của bạn kiểm thứ khác hẳn là tài liệu có KHỚP với repo thật không. Hai việc bù nhau, không thay nhau."
      },
      "claude-automation-recommender": {
        tom: "Đọc cả kho rồi gợi ý nên tự động hoá chỗ nào bằng hook, agent, skill hay MCP.",
        lam: ["Phân tích mã nguồn", "Chỉ ra việc lặp đáng tự động hoá",
              "Gợi ý đúng loại công cụ cho từng việc", "Kèm mẹo cấu hình"],
        khi: "Bạn hỏi \"nên tự động hoá gì\", hoặc muốn tối ưu cách dùng Claude Code.",
        ban: "Chạy nó trên blockchainworld xem có thấy việc lặp nào bạn với tôi chưa nhận ra không. Riêng chuyện nâng CACHE_VERSION và sinh halls.js thì đã tự động rồi."
      },
      "claude-security": {
        tom: "Bàn tiếp nhận rà soát an ninh: quét cả kho, quét phần thay đổi, hoặc đề xuất bản vá.",
        lam: ["Quét toàn bộ mã nguồn", "Quét riêng phần khác biệt của nhánh hoặc một PR",
              "Biến phát hiện thành bản vá cụ thể", "Nhớ những phát hiện đã xử lý"],
        khi: "Bạn bảo \"rà soát bảo mật\", \"quét bản thay đổi này\".",
        ban: "Đáng chạy trước mỗi lần gộp về main. Bạn đã lộ hai khoá trong phiên này — khoá Anthropic dán vào khung chat và khoá Pinata; cả hai đều chết. Rà tự động không đỡ được chuyện dán vào chat, nhưng đỡ được chuyện khoá lọt vào mã."
      },
      "receipts": {
        tom: "Dựng báo cáo bạn đã dùng Claude Code vào những gì, từ nhật ký phiên trên máy.",
        lam: ["Đào dữ liệu từ transcript ở máy", "Chọn khoảng thời gian",
              "Viết báo cáo tác động", "Lưu ra markdown"],
        khi: "Bạn muốn tổng kết đã dùng Claude Code làm được gì, tốn bao nhiêu.",
        ban: "Trả lời đúng câu bạn hỏi hôm nay — tiền đi đâu. Khác chỗ: nó đọc nhật ký phiên ở máy, còn hoá đơn Đài Quan Trắc thì nằm ở bảng điều khiển Anthropic."
      },
      "session-report": {
        tom: "Dựng trang HTML xem được về mức dùng của các phiên: token, bộ nhớ đệm, agent con, skill.",
        lam: ["Đọc transcript trong ~/.claude/projects", "Thống kê token và cache",
              "Chỉ ra lời nhắc tốn kém nhất", "Xuất ra trang xem được"],
        khi: "Bạn muốn nhìn cụ thể phiên nào tốn gì.",
        ban: "Phiên này rất dài. Chạy nó để thấy chỗ nào ngốn token nhất — thường là đọc lại file lớn nhiều lần."
      },

      /* ── Dựng thứ xem được ── */
      "project-artifact": {
        tom: "Dựng và phát hành một trang trạng thái dự án, chia tab.",
        lam: ["Trang tổng quan kèm tiêu chí thành công", "Chuỗi các luồng việc",
              "Việc kế tiếp, rủi ro, bối cảnh", "Cập nhật theo phần đổi chứ không viết lại"],
        khi: "Dự án lớn tới mức một bản cập nhật không chứa hết.",
        ban: "Blockchainworld đã bảy cung, nhiều phiên song song, một nhà máy dữ liệu. Đúng cỡ cần một trang trạng thái. Điểm hay nhất là \"cập nhật theo phần đổi\" — cùng nguyên tắc với nhật ký cập nhật của Tàng Thư Các."
      },
      "playground": {
        tom: "Dựng trang HTML một file cho người ta vặn thử bằng nút bấm rồi chép ra lời nhắc.",
        lam: ["Tự chứa trong một file", "Có nút vặn và xem trước trực tiếp",
              "Xuất ra lời nhắc chép được", "Quản lý trạng thái theo khuôn sẵn"],
        khi: "Bạn muốn ai đó thử một thứ bằng cách vặn nút thay vì đọc tài liệu.",
        ban: "Đúng phong cách bảy cung của bạn: một file, không khung, chạy offline. Dùng được để làm chỗ vặn thử các tham số của Đài Quan Trắc chẳng hạn."
      },
      "math-olympiad": {
        tom: "Giải toán thi đấu (IMO, Putnam, USAMO, AIME) kèm khâu phản biện để bắt lỗi mà tự kiểm không thấy.",
        lam: ["Giải bài olympic", "Kiểm chứng bằng cách phản biện chính lời giải",
              "Chọn cách tiếp cận theo dạng bài", "Xử lý riêng bài đáp số"],
        khi: "Bạn đưa một bài toán thi đấu hoặc nhờ kiểm một chứng minh.",
        ban: "Không liên quan blockchainworld, nhưng ý tưởng thì có: \"kiểm bằng phản biện thay vì tự kiểm\" chính là thứ đã bắt được mấy lỗi hôm nay — như con số 25 lượt/kho tôi suýt tin."
      },

      /* ── Kênh nhắn tin ── */
      "configure": {
        tom: "Cấu hình kênh Telegram: lưu token bot và đặt luật ai được nhắn tới.",
        lam: ["Lưu token bot", "Xem lại chính sách truy cập", "Kiểm tra trạng thái kênh"],
        khi: "Bạn dán token bot Telegram, hoặc hỏi \"ai nhắn tới tôi được\".",
        ban: "Cẩn thận: skill này nhận token. Tàng Thư Các gắn cờ đọc-bí-mật cho nó là đúng. Và nhớ bài học hôm nay — dán token vào khung chat là mất token."
      },
      "access": {
        tom: "Quản lý ai được dùng kênh iMessage: duyệt ghép đôi, sửa danh sách trắng, đặt luật nhóm.",
        lam: ["Duyệt yêu cầu ghép đôi", "Sửa danh sách được phép",
              "Đặt chính sách nhắn riêng và nhắn nhóm", "Xem ai đang được phép"],
        khi: "Bạn bảo \"duyệt người này\", \"ai đang được phép\", hoặc muốn đổi luật kênh iMessage.",
        ban: "Chỉ dùng khi bạn mở kênh iMessage. Đáng chú ý ở chỗ nó là ví dụ về skill quản trị quyền — thứ nên đọc kỹ trước khi cài."
      },

      /* ── Phần cứng ── */
      "m5-onboard": {
        tom: "Đưa một thiết bị M5Stack ESP32 mới cắm vào từ số không tới chạy được.",
        lam: ["Nhận thiết bị qua cổng USB", "Nạp firmware UIFlow 2.0",
              "Cài bộ ứng dụng MicroPython", "Tránh sẵn những bẫy đã biết"],
        khi: "Bạn vừa cắm một thiết bị M5Stack (Cardputer, Core, Stick) vào máy.",
        ban: "Chỉ dùng nếu bạn nghịch phần cứng. Không dính gì tới bảy cung."
      },
      "cardputer-buddy": {
        tom: "Sửa và đẩy tiếp ứng dụng MicroPython trên Cardputer sau khi đã cài xong.",
        lam: ["Thêm ứng dụng mới", "Đẩy một file .py đã đổi mà không nạp lại cả bộ",
              "Dùng bộ công cụ vòng lặp phát triển"],
        khi: "Thiết bị đã cài rồi và bạn muốn sửa tiếp ứng dụng trên đó.",
        ban: "Đi kèm m5-onboard. Chỉ dùng khi nghịch phần cứng."
      },

      /* ── Còn lại ── */
      "writing-hookify-rules": {
        tom: "Viết luật cho hookify — cách khai hook bằng file luật thay vì viết mã.",
        lam: ["Viết file luật đúng khuôn", "Chọn đúng loại sự kiện",
              "Viết mẫu khớp cho chuẩn", "Soạn nội dung thông báo"],
        khi: "Bạn bảo \"tạo luật hookify\", hoặc hỏi cú pháp luật hookify.",
        ban: "Nhẹ hơn hook-development: khai bằng luật thay vì viết mã. Hợp với những luật nhỏ kiểu \"đừng add -A\"."
      },
      "example-skill": {
        tom: "Skill mẫu — bản khuôn để xem một skill đúng chuẩn trông thế nào.",
        lam: ["Cho xem khung thư mục skill", "Cho xem các tuỳ chọn frontmatter",
              "Ví dụ cách viết mô tả cho hiệu quả"],
        khi: "Bạn bảo \"cho xem khuôn skill\", \"minh hoạ định dạng skill\".",
        ban: "Đọc cùng skill-development. Đây là bản mẫu để chép, kia là bản hướng dẫn."
      },
      "example-command": {
        tom: "Lệnh mẫu — minh hoạ các tuỳ chọn frontmatter và cách bố trí skills/<tên>/SKILL.md.",
        lam: ["Cho xem cách nhận tham số", "Liệt kê tuỳ chọn frontmatter", "Ví dụ dùng thật"],
        khi: "Bạn muốn xem một lệnh gạch chéo mẫu.",
        ban: "Bản mẫu để chép khi làm lệnh riêng cho repo, kiểu /kiem hay /gop."
      }
    }
  },

  ghiChuNguon: "Danh mục dò bằng bốn truy vấn tìm kiếm gộp lại, cộng 10 kho gọi thẳng theo danh sách. Bản dịch tay áp cho HAI kho chính chủ — anthropics/skills (17 skill) và anthropics/claude-plugins-official (25 skill) — khoá theo đúng kho chứ không tra theo tên skill, vì tên trùng giữa các kho rất thường. 2.859 skill cộng đồng còn lại giữ nguyên mô tả gốc tiếng Anh: dịch tay không nổi, mà dịch máy thì phải gọi model, và bịa mô tả cho skill chưa đọc kỹ còn tệ hơn để nguyên bản."
};
