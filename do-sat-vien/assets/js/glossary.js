/* ═══════════════════════════════════════════════════════
   Bảng chú giải — dịch và giải nghĩa mọi nhãn của L2BEAT.

   Đây là phần đáng giá nhất của cung này. L2BEAT ghi rất chính
   xác nhưng cực kỳ cô đọng: "Fraud proofs (INT)" hay "Cannot
   withdraw" đúng về kỹ thuật mà không nói cho người đọc biết
   điều đó nghĩa là gì với tài sản của họ.

   Mỗi nhãn ở đây có ba phần:
     nhan  — tên tiếng Việt ngắn, để hiện trong bảng
     y     — nghĩa là gì, một câu
     vn    — hệ quả với người gửi tiền vào, nói thẳng

   Nhãn nào L2BEAT thêm mới mà chưa dịch thì app hiện nguyên bản
   tiếng Anh chứ không bịa — xem hàm tra() ở app.js.
   ═══════════════════════════════════════════════════════ */
window.DSV_VI = {

  /* ── thang tự trị ─────────────────────────────────── */
  thang: {
    "Stage 0": {
      nhan: "Thang 0",
      y: "Thành phố còn do đội ngũ dựng nó điều hành. Họ có thể nâng cấp hợp đồng gần như tức thì.",
      vn: "Tiền của bạn phụ thuộc vào việc đội đó tiếp tục tử tế và tiếp tục tồn tại. Chưa có bảo đảm kỹ thuật nào cho việc bạn rút được nếu họ biến mất."
    },
    "Stage 1": {
      nhan: "Thang 1",
      y: "Đã có cơ chế chứng minh gian lận hoặc bằng chứng hợp lệ chạy thật, cùng một hội đồng an ninh giám sát.",
      vn: "Bạn rút được tài sản về Ethereum kể cả khi đội vận hành ngừng làm việc — nhưng hội đồng an ninh vẫn có quyền can thiệp nhanh."
    },
    "Stage 2": {
      nhan: "Thang 2",
      y: "Hợp đồng tự cai trị. Đội ngũ không còn quyền nâng cấp nhanh; mọi thay đổi phải qua thời gian chờ đủ dài.",
      vn: "Mức tự trị cao nhất hiện có. Bạn luôn có thời gian rời đi trước khi bất kỳ thay đổi nào có hiệu lực."
    },
    "Not applicable": {
      nhan: "Không xếp thang",
      y: "Không phải rollup theo định nghĩa của L2BEAT, nên thang Stage không áp dụng.",
      vn: "Thường là sidechain hoặc chuỗi có mô hình bảo mật riêng — an toàn của nó không kế thừa từ Ethereum, phải xét theo cách khác."
    }
  },

  /* ── dạng kỹ thuật ────────────────────────────────── */
  dang: {
    "Optimistic Rollup": {
      nhan: "Rollup lạc quan",
      y: "Mặc định tin kết quả là đúng, ai phát hiện sai thì nộp bằng chứng gian lận trong thời hạn khiếu nại.",
      vn: "Rút về Ethereum thường phải chờ hết hạn khiếu nại — quãng bảy ngày ở phần lớn thiết kế."
    },
    "ZK Rollup": {
      nhan: "Rollup chứng minh",
      y: "Mỗi lô giao dịch kèm một bằng chứng toán học chứng tỏ kết quả đúng, kiểm ngay trên Ethereum.",
      vn: "Không cần chờ khiếu nại: bằng chứng được chấp nhận là rút được. Đổi lại chi phí tính toán cao hơn."
    },
    "Validium": {
      nhan: "Validium",
      y: "Có bằng chứng toán học như ZK Rollup, nhưng dữ liệu giao dịch KHÔNG đăng lên Ethereum.",
      vn: "Rẻ hơn nhiều, nhưng nếu nhóm giữ dữ liệu không đưa ra thì bạn không dựng lại được số dư để mà rút."
    },
    "Optimium": {
      nhan: "Optimium",
      y: "Như rollup lạc quan nhưng dữ liệu cũng để ngoài Ethereum.",
      vn: "Gộp cả hai điểm yếu: vừa phải chờ khiếu nại, vừa phụ thuộc bên ngoài giữ dữ liệu."
    },
    "Other": {
      nhan: "Dạng khác",
      y: "Không rơi vào bốn dạng trên — sidechain, chuỗi lai, hoặc kiến trúc riêng. Đây là ô L2BEAT gộp sẵn, và hiện phần lớn thành phố nằm ở đây, nên nhãn này không nói được gì nhiều.",
      vn: "Phải đọc từng dòng rủi ro bên dưới, không suy ra được từ nhãn dạng."
    }
  },

  /* ── loại tầng ────────────────────────────────────── */
  loai: { layer2: "Tầng 2 — nằm trên Ethereum", layer3: "Tầng 3 — nằm trên một tầng 2 khác" },

  /* ── năm chiều rủi ro ─────────────────────────────── */
  chieu: {
    "Sequencer Failure": {
      nhan: "Người xếp lịch ngừng việc",
      y: "Sequencer là bên quyết định thứ tự giao dịch. Nếu nó ngừng hoặc từ chối phục vụ bạn thì sao?"
    },
    "State Validation": {
      nhan: "Ai kiểm chứng sổ sách",
      y: "Điều gì bảo đảm kết quả tính toán mà thành phố công bố là đúng?"
    },
    "Data Availability": {
      nhan: "Dữ liệu cất ở đâu",
      y: "Dữ liệu để dựng lại số dư của mọi người nằm chỗ nào, và ai bảo đảm nó luôn lấy được?"
    },
    "Exit Window": {
      nhan: "Cửa thoát khi bị nâng cấp",
      y: "Khi đội ngũ đổi hợp đồng, bạn có bao nhiêu thời gian để rút tiền ra trước khi thay đổi có hiệu lực?"
    },
    "Proposer Failure": {
      nhan: "Người chốt sổ ngừng việc",
      y: "Proposer là bên gửi kết quả lên Ethereum. Nếu nó ngừng thì tiền của bạn có kẹt lại không?"
    }
  },

  /* ── 29 giá trị rủi ro ────────────────────────────── */
  gia: {
    /* Sequencer Failure */
    "Self sequence":              { nhan: "Tự xếp lịch được", y: "Sequencer ngừng thì bạn tự gửi giao dịch thẳng lên Ethereum để buộc nó được ghi nhận." },
    "No mechanism":               { nhan: "Không có cơ chế", y: "Không có đường nào buộc giao dịch của bạn được ghi nhận nếu sequencer từ chối. Bạn phụ thuộc hoàn toàn vào thiện chí của nó." },
    "Enqueue via L1":             { nhan: "Xếp hàng qua Ethereum", y: "Bạn đẩy được giao dịch vào hàng đợi từ Ethereum, nhưng sequencer vẫn là bên quyết định lúc nào xử lý." },
    "Force via L1":               { nhan: "Ép qua Ethereum", y: "Bạn buộc được giao dịch phải chạy thông qua Ethereum, không cần sequencer đồng ý." },
    "Log via L1":                 { nhan: "Ghi nhận qua Ethereum", y: "Chỉ ghi lại được yêu cầu trên Ethereum; việc thực thi vẫn nằm ở sequencer." },
    "Decentralized Sequencer Set":{ nhan: "Nhiều bên xếp lịch", y: "Không phải một bên duy nhất mà cả một nhóm luân phiên — một bên hỏng thì bên khác thay." },

    /* State Validation */
    "Fraud proofs (INT)":         { nhan: "Chứng minh gian lận (nội bộ)", y: "Có cơ chế tố cáo kết quả sai, nhưng chỉ một nhóm được phép tố cáo, không phải bất kỳ ai." },
    "Fraud proofs (1R, ZK)":      { nhan: "Chứng minh gian lận (một vòng, ZK)", y: "Ai cũng tố cáo được, và tranh chấp giải quyết trong một giao dịch duy nhất nhờ bằng chứng ZK." },
    "None":                       { nhan: "Không có", y: "Không có cơ chế nào kiểm chứng kết quả. Phải tin bên vận hành công bố đúng." },
    "Validity proofs":            { nhan: "Bằng chứng hợp lệ", y: "Mỗi lô kèm bằng chứng toán học, Ethereum kiểm trước khi chấp nhận." },
    "Validity proofs (ST, SN)":   { nhan: "Bằng chứng hợp lệ (STARK + SNARK)", y: "Dùng cả hai loại bằng chứng lồng nhau để vừa nhanh vừa rẻ khi kiểm trên Ethereum." },
    "Validity proofs (SN)":       { nhan: "Bằng chứng hợp lệ (SNARK)", y: "Bằng chứng dạng SNARK, gọn và rẻ để kiểm trên Ethereum." },
    "Validity proofs (ST)":       { nhan: "Bằng chứng hợp lệ (STARK)", y: "Bằng chứng dạng STARK, không cần nghi lễ khởi tạo tin cậy." },
    "TEE attestations":           { nhan: "Chứng thực từ chip bảo mật", y: "Dựa vào vùng thực thi tin cậy trong phần cứng. Bạn phải tin nhà sản xuất chip, không phải tin toán học." },

    /* Data Availability */
    "Onchain":                    { nhan: "Trên Ethereum", y: "Dữ liệu đăng thẳng lên Ethereum. Ai cũng dựng lại được số dư của mình mà không xin phép ai." },
    "Onchain (SD)":               { nhan: "Trên Ethereum (rút gọn)", y: "Đăng lên Ethereum nhưng ở dạng nén, đủ để dựng lại trạng thái." },
    "External":                   { nhan: "Để bên ngoài", y: "Dữ liệu nằm ngoài Ethereum. Bên giữ không đưa ra thì bạn không chứng minh được mình có bao nhiêu." },
    "External (DAC)":             { nhan: "Để bên ngoài (uỷ ban)", y: "Một uỷ ban được chỉ định giữ dữ liệu. An toàn của bạn bằng đúng độ trung thực của uỷ ban đó." },
    "PoS network":                { nhan: "Mạng đặt cọc riêng", y: "Một mạng riêng có đặt cọc giữ dữ liệu — có tiền thế chấp nếu gian dối, nhưng vẫn không phải Ethereum." },
    "Self custodied":             { nhan: "Tự giữ", y: "Người dùng tự giữ dữ liệu của mình. Mất là không ai dựng lại hộ được." },

    /* Exit Window */
    "∞":                          { nhan: "Không giới hạn", y: "Hợp đồng không nâng cấp nhanh được, nên bạn luôn có thời gian rời đi." },
    "Not applicable":             { nhan: "Không áp dụng", y: "Mô hình của chuỗi này không có khái niệm cửa sổ thoát." },

    /* Proposer Failure */
    "Cannot withdraw":            { nhan: "Không rút được", y: "Proposer ngừng việc là tài sản kẹt lại cho tới khi nó chạy lại. Đây là rủi ro thường bị bỏ qua nhất." },
    "Self propose":               { nhan: "Tự chốt sổ được", y: "Proposer ngừng thì bạn tự gửi kết quả lên Ethereum để rút tiền ra." },
    "Self Propose":               { nhan: "Tự chốt sổ được", y: "Proposer ngừng thì bạn tự gửi kết quả lên Ethereum để rút tiền ra." },
    "Replace proposer":           { nhan: "Thay người chốt sổ", y: "Có cơ chế thay proposer khác nếu bên đang giữ vai trò ngừng việc." },
    "Use escape hatch":           { nhan: "Dùng cửa thoát hiểm", y: "Có lối thoát khẩn cấp để rút tài sản mà không cần proposer." },
    "Security Council minority":  { nhan: "Thiểu số hội đồng an ninh", y: "Một nhóm nhỏ trong hội đồng an ninh có thể đứng ra chốt sổ thay." }
  },

  /* ── giá trị trùng chữ nhưng khác nghĩa theo từng chiều ──
     L2BEAT dùng lại cùng một chuỗi cho nhiều chiều rủi ro.
     "None" ở State Validation nghĩa là không ai kiểm chứng sổ
     sách; "None" ở Exit Window nghĩa là không có thời gian rút
     trước khi nâng cấp có hiệu lực — hai chuyện hoàn toàn khác.
     Bảng này tra TRƯỚC `gia`; không có thì mới rơi về `gia`. */
  giaTheoChieu: {
    "Exit Window": {
      "None": {
        nhan: "Không có",
        y: "Nâng cấp có hiệu lực ngay, không có khoảng thời gian nào để bạn rút tài sản ra trước."
      }
    }
  },

  /* ── stack xây dựng ───────────────────────────────── */
  stack: {
    "OP Stack": "Bản vẽ của Optimism — nhiều thành phố cùng dùng nên nâng cấp chảy xuống tất cả, và lỗi cũng vậy.",
    "Arbitrum": "Bản vẽ của Arbitrum, chứng minh gian lận nhiều vòng.",
    "ZK Stack": "Bản vẽ của Matter Labs cho chuỗi ZK.",
    "Agglayer CDK": "Bộ dựng chuỗi của Polygon, nối vào lớp tổng hợp chung.",
    "SN Stack": "Bản vẽ của Starknet.",
    "StarkEx": "Động cơ StarkEx của StarkWare, dùng cho ứng dụng chuyên biệt.",
    "OVM": "Máy ảo đời đầu của Optimism.",
    "Taiko": "Kiến trúc riêng của Taiko, mô phỏng sát Ethereum.",
    "Cartesi Rollups": "Kiến trúc Cartesi, chạy được cả môi trường Linux bên trong."
  },

  /* ── cảm quan rủi ro ──────────────────────────────── */
  camQuan: { good: "tốt", warning: "cần lưu ý", bad: "đáng ngại", neutral: "trung tính", UnderReview: "đang xem xét" }
};
