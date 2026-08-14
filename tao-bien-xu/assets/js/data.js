/* ═══════════════════════════════════════════════════════
   TẠO BIỆN XỨ — nội dung công xưởng AI.

   VIẾT TAY, không tự sinh. Đây là bản thiết kế, không phải số
   liệu quét về — nên không có script build và không nằm trong
   danh sách file bot ghi đè. Sửa thẳng file này.

   Nguồn: bản phác "Công xưởng AI" của người dùng. Việc ở đây là
   PHÂN LOẠI và LÀM RÕ: bản phác cho tên 18 máy và một mẫu spec
   10 trường (áp cho S004), phần còn lại là mô tả rời. File này
   áp đủ 10 trường cho cả 18 máy, xếp chúng vào 4 khu theo dòng
   chảy công việc, và ghi rõ chỗ nào là suy ra chứ không có
   trong bản phác.

   ── BA THỨ ĐỪNG TRỘN (bản phác nhấn mạnh, giữ nguyên) ──
     MÁY        thực hiện một chức năng
     DÂY CHUYỀN thứ tự các máy phải chạy
     TỔ         mang nhiệm vụ và điều khiển máy
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  /* ── 4 tầng ──────────────────────────────────────────── */
  var TANG = [
    { ma: "t1", so: "I", ten: "Bộ não", mau: "#E0793B",
      gom: "Foundation model",
      y: "Claude · GPT · Grok · model nội bộ. Chỉ là động cơ — thay được, không phải cả nhà máy." },
    { ma: "t2", so: "II", ten: "Tính cách & trí nhớ", mau: "#C9A227",
      gom: "Personality + Memory",
      y: "Cùng một động cơ, đổi tính cách thì ra một kiểu nhân viên khác. Trí nhớ biến “mỗi lần bật lên là người mới” thành “người làm lâu năm trong xưởng”." },
    { ma: "t3", so: "III", ten: "Máy & dây chuyền", mau: "#3F9D6D",
      gom: "Skills + Routines + Agents",
      y: "Kỹ năng là máy, quy trình là băng chuyền, tổ là người vận hành. Đây là chỗ tri thức vận hành thật sự nằm." },
    { ma: "t4", so: "IV", ten: "Thực thi & kiểm soát", mau: "#5A8DD6",
      gom: "Tools + Computer + Approval",
      y: "Không có dụng cụ thì AI chỉ biết nghĩ. Không có cửa duyệt thì nó biến suy nghĩ thành hành động thật mà không ai chặn." }
  ];

  /* ── 4 khu theo dòng chảy ────────────────────────────── */
  var KHU = [
    { ma: "k1", ten: "Khu tiếp nhận", mau: "#E0793B",
      y: "Việc vào xưởng, được phân loại, và bị soát quyền trước khi tốn một token nào." },
    { ma: "k2", ten: "Khu điều độ", mau: "#C9A227",
      y: "Lắp ngữ cảnh, chia việc lớn thành bước, rồi giao mỗi bước cho đúng tổ và đúng động cơ." },
    { ma: "k3", ten: "Khu nền tảng", mau: "#3F9D6D",
      y: "Sáu kho dùng chung: động cơ, tính cách, trí nhớ, tổ, dụng cụ, mặt bằng. Không tự chạy — các khu kia gọi tới." },
    { ma: "k4", ten: "Khu kiểm & giao", mau: "#5A8DD6",
      y: "Không có gì ra khỏi xưởng mà chưa qua kiểm. Và vòng học lại đóng ở đây." }
  ];

  /* ── 18 máy ──────────────────────────────────────────────
     Mỗi máy đủ 10 trường theo mẫu trong bản phác:
     tên · mục đích · vào · ra · luật · dụng cụ · lỗi ·
     chuyển bước · khi nào hỏi người · nhật ký ghi gì.

     `treo` = máy này có thể giữ việc lại chờ người.
     `vong` = máy này đẩy ngược về máy nào (vòng tuần hoàn). */
  var MAY = [
    {
      id: "M01", khu: "k1", ten: "Cửa nhận việc", en: "Job Intake",
      tom: "Chỗ duy nhất việc được phép vào xưởng.",
      boi: "Nếu việc vào từ mười chỗ khác nhau thì không đếm được, không truy được, và không chặn được. Một cửa duy nhất là điều kiện để mọi thứ phía sau có nghĩa.",
      vao: "Câu lệnh của người · lịch chạy tự động · sự kiện từ hệ thống khác",
      ra: "Một JOB có mã số, thời điểm, người yêu cầu, và nội dung thô",
      luat: [
        "Mọi việc đều thành JOB có mã — kể cả việc một câu",
        "Không xử lý gì ở đây, chỉ ghi nhận và cấp số",
        "Giữ nguyên văn yêu cầu gốc, đừng diễn giải sớm"
      ],
      cu: ["form", "webhook", "cron", "email"],
      loi: "Yêu cầu rỗng · thiếu người chịu trách nhiệm · vượt hạn ngạch",
      chuyen: "Luôn sang M02",
      hoi: "Không",
      log: "job_id · nguồn · người yêu cầu · nguyên văn · thời điểm"
    },
    {
      id: "M02", khu: "k1", ten: "Máy phân loại việc", en: "Job Classifier",
      tom: "Đây là loại việc gì?",
      boi: "Phân loại sai thì mọi bước sau sai theo: chọn nhầm động cơ, nhầm tổ, nhầm mức duyệt. Đây là máy rẻ nhất mà ảnh hưởng lớn nhất.",
      vao: "JOB thô",
      ra: "JOB có nhãn loại + độ khó ước lượng + mức rủi ro",
      luat: [
        "Sáu loại: nghiên cứu · dựng · viết · vận hành · điều tra · sửa lỗi",
        "Không chắc thì gắn nhãn “chưa rõ” chứ đừng đoán bừa",
        "Rủi ro chấm riêng, không suy từ độ khó — việc dễ vẫn có thể nguy hiểm"
      ],
      cu: ["model nhỏ", "bảng luật"],
      loi: "Việc lai nhiều loại · mô tả quá mơ hồ để phân",
      chuyen: "Sang M03. Nhãn “chưa rõ” thì hỏi lại người trước.",
      hoi: "Khi không phân được loại sau hai lần thử",
      log: "loại · độ tin của phân loại · rủi ro"
    },
    {
      id: "M03", khu: "k1", ten: "Cổng kiểm quyền", en: "Authority Check",
      tom: "AI có được làm việc này không?",
      boi: "Đây là chỗ bản phác nói kỹ nhất và cũng là chỗ hay bị bỏ. Kiểm quyền TRƯỚC khi chạy thì rẻ; kiểm sau khi đã gửi email thật thì không rút lại được.",
      vao: "JOB đã phân loại",
      ra: "JOB kèm mức duyệt (0–3) và danh sách hành động bị cấm",
      luat: [
        "Bốn mức: 0 tự làm · 1 tự làm và ghi log · 2 chuẩn bị rồi chờ duyệt · 3 cấm",
        "Mức lấy theo hành động NẶNG NHẤT mà việc có thể chạm tới",
        "Không có mức thì mặc định là 2, không phải 0"
      ],
      cu: ["bảng quyền", "sổ chính sách"],
      loi: "Việc chạm hành động chưa có trong bảng quyền",
      chuyen: "Mức 0–2 sang M04. Mức 3 dừng và trả lời người.",
      hoi: "Khi gặp hành động chưa xếp mức",
      log: "mức duyệt · hành động bị cấm · luật nào áp"
    },
    {
      id: "M04", khu: "k2", ten: "Máy lắp ngữ cảnh", en: "Context Assembler",
      tom: "Gom đúng thứ cần biết, và chỉ thứ cần biết.",
      boi: "Nhồi hết mọi thứ vào ngữ cảnh vừa đắt vừa làm model lạc. Máy này quyết định lấy gì từ năm kho trí nhớ.",
      vao: "JOB + mã dự án",
      ra: "Gói ngữ cảnh: tính cách + trí nhớ liên quan + luật + dữ liệu",
      luat: [
        "Lấy theo liên quan, không lấy theo “có sẵn”",
        "Bài học cũ ưu tiên hơn dữ liệu cũ",
        "Ghi rõ đã lấy từ đâu, để sau truy được vì sao model nghĩ vậy"
      ],
      cu: ["M09 kho trí nhớ", "M08 tính cách", "tìm kiếm ngữ nghĩa"],
      loi: "Ngữ cảnh vượt hạn mức · mâu thuẫn giữa hai bài học cũ",
      chuyen: "Sang M05",
      hoi: "Khi hai bài học cũ mâu thuẫn nhau",
      log: "đã lấy mảnh nào · tổng token · mảnh nào bị cắt"
    },
    {
      id: "M05", khu: "k2", ten: "Máy lập kế hoạch", en: "Planner",
      tom: "Chia mục tiêu lớn thành các bước chạy được.",
      boi: "Không có bước thì không kiểm được giữa chừng, không biết đang ở đâu, và hỏng thì phải làm lại từ đầu.",
      vao: "JOB + gói ngữ cảnh",
      ra: "Danh sách bước, mỗi bước có đầu vào/đầu ra rõ",
      luat: [
        "Mỗi bước phải kiểm được độc lập",
        "Có dây chuyền sẵn khớp thì dùng lại, đừng bịa kế hoạch mới",
        "Bước nào chạm hành động thật thì tách riêng, không gộp"
      ],
      cu: ["model mạnh", "kho dây chuyền"],
      loi: "Không chia nhỏ được · kế hoạch quá 20 bước",
      chuyen: "Sang M06",
      hoi: "Kế hoạch có bước mức 2 trở lên thì cho người xem trước",
      log: "số bước · dùng lại dây chuyền nào · ước lượng chi phí"
    },
    {
      id: "M06", khu: "k2", ten: "Máy điều phối", en: "Router",
      tom: "Bước nào — tổ nào — máy nào — động cơ nào.",
      boi: "Đây là chỗ biến kế hoạch thành phân công. Cũng là chỗ tiết kiệm nhiều nhất: việc rẻ mà giao cho động cơ đắt là đốt tiền đều đặn.",
      vao: "Danh sách bước",
      ra: "Mỗi bước gắn: tổ + kỹ năng + động cơ + mặt bằng chạy",
      luat: [
        "Giao theo thế mạnh, không giao theo mặc định",
        "Bước lặp lại và rẻ thì đẩy xuống model nhỏ",
        "Tổ chỉ nhận được bước nằm trong quyền của tổ đó"
      ],
      cu: ["M07 chọn động cơ", "M10 sổ tổ", "M11 kho dụng cụ"],
      loi: "Không tổ nào đủ quyền · không động cơ nào phù hợp",
      chuyen: "Vào ba dây: nghiên cứu · dựng · kiểm",
      hoi: "Không",
      log: "phân công từng bước · lý do chọn động cơ"
    },
    {
      id: "M07", khu: "k3", ten: "Bộ chọn động cơ", en: "Model Gateway",
      tom: "Đổi model mà không phải xây lại xưởng.",
      boi: "Đây là ý quan trọng nhất của cả bản thiết kế: đừng khoá vào một hãng. Trí nhớ, kỹ năng và quy trình là của xưởng; model chỉ là thợ có thể thay.",
      vao: "Loại bước + ràng buộc (chi phí, độ trễ, độ bí mật)",
      ra: "Một model cụ thể + tham số",
      luat: [
        "Việc suy luận khó → model mạnh nhất đang có",
        "Việc lặp lại, rẻ → model nhỏ hoặc chạy nội bộ",
        "Dữ liệu nhạy cảm → chỉ model chạy nội bộ",
        "Model hỏng → tự chuyển sang model dự phòng, ghi log"
      ],
      cu: ["API các hãng", "model nội bộ"],
      loi: "Hết hạn mức · model ngừng phục vụ · quá thời gian chờ",
      chuyen: "Trả động cơ cho M06",
      hoi: "Khi buộc phải gửi dữ liệu nhạy cảm ra ngoài",
      log: "model · token vào/ra · chi phí · độ trễ · có phải bản dự phòng không"
    },
    {
      id: "M08", khu: "k3", ten: "Phòng tính cách", en: "Personality Engine",
      tom: "Cùng một động cơ, khác cách làm việc.",
      boi: "Tính cách không phải giọng văn. Nó quy định thứ tự ưu tiên khi phải chọn: nhanh hay chắc, gọn hay đủ, kết luận hay để ngỏ.",
      vao: "Vai của bước",
      ra: "Hồ sơ tính cách nạp vào ngữ cảnh",
      luat: [
        "Nghiên cứu: tách FACT và INFERENCE, không kết luận khi thiếu chứng cứ",
        "Dựng: chạy được trước, đơn giản trước, có test",
        "Kiểm: mặc định không tin, đi tìm chỗ sai và bằng chứng phản bác"
      ],
      cu: ["kho hồ sơ tính cách"],
      loi: "Vai chưa có hồ sơ tính cách",
      chuyen: "Trả hồ sơ cho M04",
      hoi: "Không",
      log: "hồ sơ nào · phiên bản mấy"
    },
    {
      id: "M09", khu: "k3", ten: "Kho trí nhớ", en: "Memory System",
      tom: "Năm ngăn, không phải một cục.",
      boi: "Trộn chung năm loại trí nhớ là lý do trí nhớ AI thường vô dụng: chuyện riêng của một job cũ trồi lên giữa một job không liên quan.",
      vao: "Sự kiện, quyết định, bài học, sở thích",
      ra: "Mảnh trí nhớ có nhãn và thời hạn",
      luat: [
        "Năm ngăn: người dùng · dự án · job đang chạy · bài học · quyết định đã chốt",
        "Trí nhớ job chết khi job xong; bài học thì sống lâu",
        "Bài học phải ghi kèm việc đã xảy ra, không ghi luật suông",
        "Không lưu bí mật vào ngăn dùng chung"
      ],
      cu: ["kho vector", "cơ sở dữ liệu", "file"],
      loi: "Hai bài học mâu thuẫn · trí nhớ phình quá hạn",
      chuyen: "Trả mảnh cho M04",
      hoi: "Khi ghi đè một quyết định đã chốt",
      log: "đọc/ghi mảnh nào · ngăn nào"
    },
    {
      id: "M10", khu: "k3", ten: "Sổ tổ thợ", en: "Agent Registry",
      tom: "Ai làm nghề gì, được cầm dụng cụ nào.",
      boi: "Một chatbot biết tất cả thì không kiểm soát được. Chia thành tổ có nghề và có quyền riêng thì hỏng chỗ nào biết chỗ đó.",
      vao: "Yêu cầu một vai",
      ra: "Hồ sơ tổ: model + kỹ năng + dụng cụ + quyền đọc/ghi/xoá",
      luat: [
        "Mỗi tổ có quyền tối thiểu đủ làm việc của mình",
        "Tổ nghiên cứu không có quyền ghi",
        "Tổ kiểm chỉ đọc — không sửa được thứ mình đang chấm"
      ],
      cu: ["sổ đăng ký tổ"],
      loi: "Không tổ nào có kỹ năng cần · tổ bị treo quyền",
      chuyen: "Trả hồ sơ tổ cho M06",
      hoi: "Khi phải cấp thêm quyền cho một tổ",
      log: "tổ nào nhận bước nào"
    },
    {
      id: "M11", khu: "k3", ten: "Kho dụng cụ", en: "Tool Registry",
      tom: "Cánh tay nối ra thế giới ngoài.",
      boi: "Không dụng cụ thì AI chỉ biết nghĩ. Nhưng phát dụng cụ bừa thì một tổ đọc web lại xoá được cơ sở dữ liệu.",
      vao: "Yêu cầu dụng cụ từ một tổ",
      ra: "Quyền dùng dụng cụ, có hạn mức và thời hạn",
      luat: [
        "Phát theo tổ, không phát theo job",
        "Dụng cụ ghi/xoá luôn kèm hạn mức",
        "Mọi lần gọi dụng cụ đều ghi log, không có ngoại lệ"
      ],
      cu: ["trình duyệt", "shell", "API", "MCP", "cơ sở dữ liệu", "hệ tệp"],
      loi: "Dụng cụ hỏng · vượt hạn mức · thiếu khoá",
      chuyen: "Trả quyền cho M12",
      hoi: "Khi cấp dụng cụ có quyền xoá",
      log: "dụng cụ · tham số · kết quả · thời gian"
    },
    {
      id: "M12", khu: "k3", ten: "Mặt bằng thực thi", en: "Sandbox Manager",
      tom: "Nơi máy móc thật sự chạy.",
      boi: "Tách mặt bằng là cách rẻ nhất để một job hỏng không kéo theo job khác. Cũng là chỗ duy nhất giới hạn được tài nguyên thật.",
      vao: "Bước cần chạy + dụng cụ đã cấp",
      ra: "Kết quả chạy + hiện vật sinh ra",
      luat: [
        "Mỗi job một hộp cách ly, xong thì huỷ",
        "Hộp không có khoá thật trừ khi bước đó cần",
        "Có giới hạn thời gian, bộ nhớ, và lưu lượng mạng"
      ],
      cu: ["container", "máy ảo", "phiên trình duyệt"],
      loi: "Quá giờ · hết bộ nhớ · mạng chặn",
      chuyen: "Sang M13",
      hoi: "Khi bước cần khoá thật của hệ thống ngoài",
      log: "hộp nào · tài nguyên dùng · mã thoát"
    },
    {
      id: "M13", khu: "k4", ten: "Máy kiểm chất lượng", en: "Quality Gate",
      tom: "Không có gì đi thẳng ra ngoài.",
      boi: "Đây là chỗ vòng tuần hoàn đóng lại. Kiểm mà không đẩy ngược được thì chỉ là báo cáo; đẩy ngược được mới là dây chuyền.",
      vao: "Kết quả từ M12",
      ra: "ĐẠT · SỬA LẠI · TRẢ VỀ",
      luat: [
        "Sáu phép: đúng định dạng · có chứng cứ · không lỗi · không bịa · test qua · không phạm chính sách",
        "Trượt phép nào thì trả về đúng bước sinh ra lỗi, không trả về đầu dây",
        "Trả về quá ba lần thì dừng và hỏi người"
      ],
      cu: ["bộ test", "đối chiếu nguồn", "soát chính sách"],
      loi: "Không kiểm được vì thiếu tiêu chí",
      chuyen: "ĐẠT sang M14. SỬA LẠI quay về M12.",
      vong: "M12",
      hoi: "Khi trả về lần thứ ba",
      log: "phép nào trượt · lần trả về thứ mấy"
    },
    {
      id: "M14", khu: "k4", ten: "Cổng người duyệt", en: "Approval Gate",
      tom: "Chỗ con người còn giữ chìa khoá.",
      boi: "Ranh giới giữa “trợ lý” và “hệ thống tự chạy” nằm đúng ở đây. Không có cổng này thì mọi lớp trên chỉ là trang trí.",
      vao: "Kết quả đã ĐẠT + mức duyệt từ M03",
      ra: "Cho phép thực thi · hoặc trả lại kèm ghi chú",
      luat: [
        "Mức 0 đi thẳng · mức 1 đi thẳng và ghi log · mức 2 dừng chờ người · mức 3 không bao giờ tự chạy",
        "Chờ quá hạn thì huỷ, không mặc định cho qua",
        "Ghi chú của người được đưa thẳng vào M18 làm bài học"
      ],
      cu: ["hàng chờ duyệt", "thông báo"],
      loi: "Không ai duyệt trong hạn · người duyệt không đủ quyền",
      chuyen: "Duyệt thì sang M15. Trả lại thì về M12.",
      vong: "M12",
      treo: true,
      hoi: "Chính nó là chỗ hỏi",
      log: "ai duyệt · lúc nào · ghi chú gì"
    },
    {
      id: "M15", khu: "k4", ten: "Máy thực thi thật", en: "Commit Engine",
      tom: "Tách CHUẨN BỊ khỏi THỰC HIỆN.",
      boi: "Cả bản thiết kế xoay quanh một ranh giới: soạn email không phải gửi email. Tách hai việc đó ra thì AI không biến suy nghĩ thành hành động không rút lại được.",
      vao: "Hành động đã được duyệt",
      ra: "Hành động đã thực hiện + biên nhận",
      luat: [
        "Chỉ nhận đầu vào đã qua M14, không có đường tắt",
        "Việc nào hoàn tác được thì chuẩn bị sẵn đường hoàn tác trước khi chạy",
        "Chạy một lần — trùng mã thì bỏ qua, không chạy lại"
      ],
      cu: ["API ghi", "git", "gửi thư", "triển khai"],
      loi: "Thực thi hỏng nửa chừng · hệ thống ngoài từ chối",
      chuyen: "Sang M16",
      hoi: "Khi hành động không hoàn tác được",
      log: "hành động · biên nhận · hoàn tác được không"
    },
    {
      id: "M16", khu: "k4", ten: "Kho thành phẩm", en: "Artifact Store",
      tom: "Thành phẩm phải biết mình từ đâu ra.",
      boi: "Một báo cáo không biết ai tạo, theo dây chuyền nào, từ nguồn nào thì sáu tháng sau không dùng lại được.",
      vao: "Kết quả đã thực thi",
      ra: "Hiện vật có phiên bản và lai lịch đầy đủ",
      luat: [
        "Mỗi hiện vật ghi: ai tạo · lúc nào · dây chuyền nào · phiên bản mấy · nguồn nào · đã duyệt chưa",
        "Không ghi đè — ra bản mới",
        "Hiện vật chưa duyệt phải đánh dấu rõ là bản nháp"
      ],
      cu: ["kho tệp", "git", "cơ sở dữ liệu"],
      loi: "Trùng phiên bản · thiếu lai lịch",
      chuyen: "Sang M17",
      hoi: "Không",
      log: "mã hiện vật · phiên bản · kích thước"
    },
    {
      id: "M17", khu: "k4", ten: "Phòng điều khiển", en: "Observability",
      tom: "Nhìn thấy xưởng đang làm gì, kẹt ở đâu.",
      boi: "Không có phòng này thì mọi thứ trên chỉ là niềm tin. Có nó thì trả lời được: tốn bao nhiêu, chậm ở máy nào, tổ nào hay gây lỗi.",
      vao: "Log từ mọi máy",
      ra: "Dòng thời gian mỗi job + số liệu gộp",
      luat: [
        "Mọi máy ghi cùng một khuôn: job · máy · vào · ra · thời gian · chi phí",
        "Việc đang chạy phải thấy được ngay, không đợi job xong",
        "Giữ log đủ lâu để truy ngược một quyết định"
      ],
      cu: ["log", "số liệu", "bảng theo dõi"],
      loi: "Mất log · đồng hồ lệch giữa các máy",
      chuyen: "Sang M18",
      hoi: "Không",
      log: "chính nó là nhật ký"
    },
    {
      id: "M18", khu: "k4", ten: "Xưởng học lại", en: "Learning Engine",
      tom: "So việc AI làm với chỗ người sửa, rút thành luật.",
      boi: "Đây là thứ biến công cụ thành nhân viên. Không có máy này thì mỗi lần sửa của người chỉ sống trong một đoạn chat rồi mất.",
      vao: "Kết quả AI + bản người đã sửa + ghi chú lúc duyệt",
      ra: "BÀI HỌC có mã, kèm đề nghị sửa máy nào",
      luat: [
        "Chỉ rút bài học khi có khác biệt thật giữa bản AI và bản người",
        "Bài học phải chỉ đích danh máy hoặc kỹ năng bị ảnh hưởng",
        "Bài học nào cũng ở trạng thái CHỜ NGƯỜI DUYỆT trước khi có hiệu lực",
        "Có hiệu lực thì kỹ năng lên một phiên bản"
      ],
      cu: ["so sánh bản", "M09 kho trí nhớ"],
      loi: "Không tìm được khác biệt · bài học mâu thuẫn luật cũ",
      chuyen: "Đẩy ngược về M09 · kho kỹ năng · kho dây chuyền",
      vong: "M09",
      treo: true,
      hoi: "Mọi bài học đều phải người duyệt",
      log: "mã bài học · ảnh hưởng máy nào · đã duyệt chưa"
    }
  ];

  /* ── kỹ năng: mỗi cái một máy chuyên dụng ────────────── */
  var KY_NANG = [
    { id: "S01", ten: "Tra cứu web", vao: "câu hỏi", ra: "danh sách nguồn",
      y: "Ưu tiên nguồn gốc. Wikipedia dùng để dò đường, không dùng làm chứng cứ cuối." },
    { id: "S02", ten: "Đọc tài liệu", vao: "PDF · trang web", ra: "văn bản có cấu trúc",
      y: "Giữ số trang để trích dẫn ngược lại được." },
    { id: "S03", ten: "Bóc thực thể", vao: "văn bản", ra: "người · tổ chức · ngày · số",
      y: "Không suy diễn quan hệ ở bước này, chỉ bóc thứ có mặt." },
    { id: "S04", ten: "Kiểm chứng tuyên bố", vao: "một tuyên bố", ra: "ĐÃ KIỂM · CHƯA KIỂM · MÂU THUẪN · KHÔNG RÕ",
      y: "Máy duy nhất bản phác viết đủ spec. Cấm tuyệt đối: tự sửa tuyên bố gốc cho khớp chứng cứ." },
    { id: "S05", ten: "Viết mã", vao: "yêu cầu", ra: "mã + test",
      y: "Không có test thì coi như chưa xong." },
    { id: "S06", ten: "Chạy test", vao: "mã", ra: "đạt/trượt + log",
      y: "Trượt là kết quả hợp lệ, không phải lỗi của máy." },
    { id: "S07", ten: "Dựng báo cáo", vao: "dữ kiện đã kiểm", ra: "báo cáo",
      y: "Mỗi khẳng định phải kèm nguồn hoặc nhãn suy luận." }
  ];

  /* ── dây chuyền ──────────────────────────────────────── */
  var DAY = [
    {
      id: "R001", ten: "Điều tra một công ty",
      y: "Dây chuyền mẫu trong bản phác. Điểm đáng chú ý: kiểm chứng nằm TRƯỚC khi dựng báo cáo, nên báo cáo không bao giờ chứa tuyên bố chưa kiểm.",
      buoc: [
        ["S01", "Thu thập thông tin cơ bản"],
        ["S03", "Bóc thực thể"],
        ["S01", "Tìm chủ sở hữu hưởng lợi"],
        ["S01", "Tìm hội đồng quản trị"],
        ["S01", "Tìm liên hệ tài chính"],
        ["S04", "Kiểm chứng từng tuyên bố"],
        ["S07", "Dựng báo cáo"],
        ["—", "Tổ kiểm chấm"],
        ["—", "Người duyệt"]
      ]
    },
    {
      id: "R002", ten: "Dựng một ứng dụng",
      y: "Suy ra từ bản phác (mục Builder → code → Unit Test → Integration Test → Reviewer). Vòng sửa nằm giữa test và mã, không kéo về đầu dây.",
      buoc: [
        ["—", "Chốt phạm vi"],
        ["S05", "Viết mã"],
        ["S06", "Chạy test đơn vị"],
        ["S06", "Chạy test tích hợp"],
        ["—", "Tổ kiểm đọc mã"],
        ["—", "Người duyệt"],
        ["—", "Gộp và triển khai"]
      ]
    },
    {
      id: "R003", ten: "Rút bài học sau một job",
      y: "Dây chuyền của chính M18. Chạy sau mỗi job xong, và là thứ khiến xưởng khá lên theo thời gian thay vì đứng yên.",
      buoc: [
        ["—", "Lấy bản AI và bản người đã sửa"],
        ["—", "So khác biệt"],
        ["—", "Rút thành luật"],
        ["—", "Chỉ đích danh máy bị ảnh hưởng"],
        ["—", "Người duyệt bài học"],
        ["—", "Nâng phiên bản kỹ năng"]
      ]
    }
  ];

  /* ── tổ thợ ──────────────────────────────────────────── */
  var TO = [
    { id: "A00", ten: "Quản đốc", vai: "Nhận việc, chia bước, giao tổ, gom kết quả",
      may: "model mạnh nhất", kn: [], doc: true, ghi: false, xoa: false,
      y: "Không tự làm việc chuyên môn. Việc của quản đốc là phân công và chịu trách nhiệm." },
    { id: "A01", ten: "Tổ nghiên cứu", vai: "Tìm và thu thập",
      may: "model mạnh về tìm kiếm", kn: ["S01", "S02", "S03"], doc: true, ghi: false, xoa: false,
      y: "Cố ý KHÔNG có quyền ghi. Tổ tìm tin mà sửa được dữ liệu là mất đường truy nguyên." },
    { id: "A02", ten: "Tổ chứng cứ", vai: "Đối chiếu nguồn, chấm độ chắc",
      may: "model suy luận", kn: ["S04"], doc: true, ghi: false, xoa: false,
      y: "Tách khỏi tổ nghiên cứu có chủ đích: người đi tìm tin không nên là người chấm tin mình tìm." },
    { id: "A03", ten: "Tổ dựng", vai: "Viết mã, dựng sản phẩm",
      may: "model mạnh về mã", kn: ["S05", "S06"], doc: true, ghi: true, xoa: false,
      y: "Có quyền ghi nhưng không có quyền xoá. Xoá luôn phải qua cửa duyệt." },
    { id: "A04", ten: "Tổ kiểm", vai: "Tìm chỗ sai trước khi ra khỏi xưởng",
      may: "model mạnh nhất", kn: ["S06"], doc: true, ghi: false, xoa: false,
      y: "Chỉ đọc. Tổ chấm mà sửa được thứ mình chấm thì không còn là chấm." },
    { id: "A05", ten: "Tổ vận hành", vai: "Thực thi hành động đã duyệt",
      may: "model nhỏ", kn: [], doc: true, ghi: true, xoa: true,
      y: "Tổ duy nhất có quyền xoá, và chỉ nhận việc đã qua M14." }
  ];

  /* ── bốn mức duyệt ───────────────────────────────────── */
  var MUC = [
    { m: 0, ten: "Tự làm", mau: "#3F9D6D",
      y: "Việc đọc, việc tổng hợp, việc không để lại dấu vết ở ngoài.",
      vd: ["Đọc tệp", "Tra web", "Tóm tắt tài liệu"] },
    { m: 1, ten: "Tự làm + ghi log", mau: "#C9A227",
      y: "Có tạo ra thứ gì đó, nhưng còn nằm trong xưởng.",
      vd: ["Soạn báo cáo nháp", "Sinh mã chưa gộp", "Ghi trí nhớ dự án"] },
    { m: 2, ten: "Chuẩn bị rồi chờ duyệt", mau: "#E0793B",
      y: "Chạm ra thế giới thật. AI chuẩn bị đầy đủ nhưng dừng lại.",
      vd: ["Gửi thư", "Gộp mã vào nhánh chính", "Đăng công khai", "Sửa dữ liệu thật"] },
    { m: 3, ten: "Không bao giờ tự làm", mau: "#C0392B",
      y: "Không có đường tắt nào, kể cả khi người dùng bảo cứ làm đi.",
      vd: ["Chuyển tiền", "Xoá dữ liệu gốc", "Cấp quyền mới", "Ký thay người"] }
  ];

  /* ── lộ trình dựng ───────────────────────────────────── */
  var CHANG = [
    { v: "V1", ten: "Xưởng tối thiểu", y: "Đừng dựng 100 máy ngay. Dựng đủ để một việc thật chạy hết vòng.",
      viec: ["1 động cơ", "1 tính cách", "trí nhớ cơ bản", "3–5 kỹ năng lõi",
             "1 dây chuyền thật sự hữu ích", "2 tổ", "2–3 dụng cụ", "bảng mức duyệt"] },
    { v: "V2", ten: "Bắt đầu vận hành", y: "Cho chạy việc thật rồi xem chỗ nào hỏng — đừng đoán trước.",
      viec: ["chạy việc thật", "ghi log", "xem chỗ nào hỏng", "tách thêm kỹ năng",
             "sửa dây chuyền", "thêm luật trí nhớ"] },
    { v: "V3", ten: "Thành công xưởng", y: "Chỉ tới đây mới cần bộ máy đầy đủ.",
      viec: ["nhiều dây chuyền", "nhiều tổ", "phân quyền", "lịch chạy tự động",
             "bảng theo dõi", "đánh phiên bản kỹ năng và dây chuyền"] }
  ];

  /* ── thư mục hồ sơ ───────────────────────────────────── */
  var THU_MUC = [
    ["00_constitution", "nguyên tắc · quyền hạn · an toàn"],
    ["01_models", "khai báo từng động cơ"],
    ["02_personalities", "hồ sơ tính cách"],
    ["03_memory", "người dùng · dự án · bài học · quyết định"],
    ["04_skills", "mỗi kỹ năng một thư mục có spec"],
    ["05_routines", "mỗi dây chuyền một thư mục"],
    ["06_agents", "hồ sơ từng tổ"],
    ["07_tools", "khai báo dụng cụ và hạn mức"],
    ["08_computers", "các mặt bằng chạy"],
    ["09_workflows", "ghép dây chuyền thành luồng lớn"],
    ["10_approval", "luật duyệt và hàng chờ"],
    ["11_jobs", "job đã và đang chạy"],
    ["12_outputs", "kho thành phẩm"],
    ["13_logs", "nhật ký"],
    ["14_learning", "bài học và đề nghị nâng cấp"]
  ];

  /* ── ví dụ định tuyến model (M07) ────────────────────────
     Bảng viết tay, dùng cho phần mô phỏng. KHÔNG gọi API thật —
     xem ghi chú trong app.js về lý do. */
  var DONG_CO = [
    { ma: "claude", ten: "Claude", mau: "#D97757", manh: ["mã", "văn bản dài", "bám quy trình"] },
    { ma: "gpt", ten: "GPT", mau: "#10A37F", manh: ["suy luận", "đa năng", "gọi công cụ"] },
    { ma: "grok", ten: "Grok", mau: "#8B93A8", manh: ["tin thời sự", "tìm kiếm mạng xã hội"] },
    { ma: "noibo", ten: "Model nội bộ", mau: "#7C6BB5", manh: ["việc rẻ lặp lại", "dữ liệu nhạy cảm"] }
  ];

  var VIEC_MAU = [
    { ten: "Điều tra một công ty", loai: "điều tra", muc: 1, day: "R001",
      buoc: [
        { m: "S01", d: "grok", ly: "cần tin mới và nguồn thời sự" },
        { m: "S03", d: "noibo", ly: "bóc thực thể là việc lặp lại, rẻ" },
        { m: "S04", d: "gpt", ly: "đối chiếu nguồn cần suy luận" },
        { m: "S07", d: "claude", ly: "viết dài, bám khuôn báo cáo" }
      ] },
    { ten: "Dựng một trang web tĩnh", loai: "dựng", muc: 2, day: "R002",
      buoc: [
        { m: "S05", d: "claude", ly: "viết mã và bám quy ước sẵn có" },
        { m: "S06", d: "noibo", ly: "chạy test không cần model mạnh" },
        { m: "—", d: "gpt", ly: "tổ kiểm dùng động cơ khác tổ dựng, để không tự khen mình" }
      ] },
    { ten: "Tóm tắt 40 tài liệu nội bộ", loai: "nghiên cứu", muc: 1, day: "—",
      buoc: [
        { m: "S02", d: "noibo", ly: "dữ liệu nội bộ — bắt buộc chạy tại chỗ" },
        { m: "S07", d: "noibo", ly: "vẫn là dữ liệu nhạy cảm, không được ra ngoài" }
      ] },
    { ten: "Gửi thư báo giá cho khách", loai: "vận hành", muc: 2, day: "—",
      buoc: [
        { m: "S07", d: "claude", ly: "soạn thư theo giọng đã chốt" },
        { m: "—", d: "—", ly: "M15 tách CHUẨN BỊ khỏi GỬI — dừng ở cổng duyệt" }
      ] },
    { ten: "Chuyển tiền cho nhà cung cấp", loai: "vận hành", muc: 3, day: "—",
      buoc: [
        { m: "—", d: "—", ly: "mức 3 — M03 chặn ngay tại cổng kiểm quyền, không chạy bước nào" }
      ] },
    { ten: "Sửa một lỗi trong mã", loai: "sửa lỗi", muc: 1, day: "R002",
      buoc: [
        { m: "S05", d: "claude", ly: "đọc mã sẵn có rồi vá" },
        { m: "S06", d: "noibo", ly: "chạy lại bộ test" }
      ] }
  ];

  /* ── sơ đồ toàn nhà máy ──────────────────────────────────
     Đây là bản đồ MỘT TRANG của cả xưởng — thứ bản phác vẽ ở mục
     "BÂY GIỜ NHÌN TOÀN BỘ NHÀ MÁY TRÊN MỘT SƠ ĐỒ".

     Khác Sàn máy ở chỗ: Sàn máy bày 18 máy theo KHU và cho chạy mô
     phỏng — nó nói xưởng đang làm gì. Sơ đồ này nói xưởng ĐƯỢC NỐI
     RA SAO: việc đi đường nào, rẽ ở đâu, và quay lại chỗ nào.

     Ba chi tiết chỉ sơ đồ này mới thấy, Sàn máy không bày được:
       · M04 được NẠP từ bên hông (trí nhớ + tính cách), không phải
         nhận từ máy trước
       · sau M06 việc TÁCH thành ba dây song song rồi mới gộp lại
       · M14 là chỗ RẼ NHÁNH thật: mức 0–1 đi thẳng, mức 2 dừng chờ
         người rồi mới nhập lại dòng

     `may` trỏ sang hồ sơ máy để bấm vào đọc được đủ 10 trường. */
  var SO_DO = [
    { k: "nguoi", ten: "Bạn", phu: "Human Owner",
      y: "Người giao việc — và người giữ chìa khoá ở cửa duyệt phía dưới." },
    { k: "may", may: "M01" },
    { k: "may", may: "M02" },
    { k: "may", may: "M03" },
    { k: "may", may: "M04",
      nap: [
        { may: "M09", ten: "Trí nhớ", phu: "5 ngăn" },
        { may: "M08", ten: "Tính cách", phu: "theo vai" }
      ] },
    { k: "may", may: "M05" },
    { k: "may", may: "M06" },
    { k: "chia", nhan: "Tách ba dây song song",
      o: [
        { to: "A01", ten: "Tổ nghiên cứu", phu: "tìm và thu thập" },
        { to: "A03", ten: "Tổ dựng", phu: "viết mã, dựng sản phẩm" },
        { to: "A04", ten: "Tổ kiểm", phu: "tìm chỗ sai" }
      ],
      /* Hai máy làm nên bước tách này nhưng KHÔNG có ô riêng trong sơ đồ
         gốc — chúng là kho được gọi tới, không phải trạm việc đi qua.
         Ghi ra đây để không ai tưởng sơ đồ bỏ sót chúng. */
      qua: ["M10", "M07"],
      y: "Ba tổ chạy song song trên cùng một job, mỗi tổ một quyền riêng. Sổ tổ (M10) quyết định ai được nhận bước nào, còn bộ chọn động cơ (M07) giao mỗi dây một model khác nhau — cố ý, để tổ kiểm không dùng chung động cơ với tổ dựng." },
    { k: "gop", nhan: "Gộp lại" },
    { k: "kho", ten: "Kho kỹ năng", phu: "S01 · S02 · S03 …", di: "#/to",
      y: "Tổ không tự làm — tổ cầm máy. Mỗi kỹ năng là một máy chuyên dụng." },
    { k: "may", may: "M11" },
    { k: "may", may: "M12" },
    { k: "may", may: "M13" },
    { k: "quyet", may: "M14",
      khong: "Mức 0–1 · đi thẳng",
      co: "Mức 2 · dừng chờ người",
      y: "Chỗ rẽ duy nhất trong cả sơ đồ. Mức 3 thì không tới được đây — M03 đã chặn từ đầu dây." },
    { k: "may", may: "M15" },
    { k: "may", may: "M16" },
    { k: "may", may: "M17" },
    { k: "may", may: "M18" },
    { k: "toa", nhan: "Đẩy ngược vào ba kho",
      o: [
        { ten: "Trí nhớ", phu: "thêm bài học", may: "M09" },
        { ten: "Kỹ năng", phu: "lên phiên bản", di: "#/to" },
        { ten: "Dây chuyền", phu: "sửa thứ tự bước", di: "#/day" }
      ],
      y: "Vòng khép kín. Không có mũi tên quay ngược này thì đây chỉ là một đường ống, và xưởng sẽ giỏi y như ngày đầu mãi mãi." }
  ];

  window.XUONG = {
    SO_DO: SO_DO,
    TANG: TANG, KHU: KHU, MAY: MAY, KY_NANG: KY_NANG, DAY: DAY,
    TO: TO, MUC: MUC, CHANG: CHANG, THU_MUC: THU_MUC,
    DONG_CO: DONG_CO, VIEC_MAU: VIEC_MAU
  };
})();
