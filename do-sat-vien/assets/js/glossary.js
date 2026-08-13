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
  camQuan: { good: "tốt", warning: "cần lưu ý", bad: "đáng ngại", neutral: "trung tính", UnderReview: "đang xem xét" },

  /* ── ba tab của L2BEAT ────────────────────────────── */
  /* Đây là cách L2BEAT chia bảng chính, và cũng là lý do thứ hạng
     nhìn khác nhau: tab mặc định của họ là Rollup, không tính
     Hyperliquid hay Polygon PoS. */
  tab: {
    rollup: {
      nhan: "Rollup",
      y: "Đăng dữ liệu giao dịch lên thẳng Ethereum, và có cơ chế chứng minh kết quả — bằng chứng hợp lệ hoặc chứng minh gian lận.",
      vn: "Nhóm an toàn nhất trong ba nhóm: dữ liệu công khai trên Ethereum nên ai cũng dựng lại được số dư của mình mà không cần xin phép ai."
    },
    validium: {
      nhan: "Validium & Optimium",
      y: "Có cơ chế chứng minh kết quả như rollup, nhưng dữ liệu giao dịch KHÔNG đăng lên Ethereum mà giữ ở nơi khác.",
      vn: "Rẻ hơn nhiều, đổi lại: nhóm giữ dữ liệu không đưa ra thì bạn không dựng lại được số dư để mà rút."
    },
    khac: {
      nhan: "Dạng khác",
      y: "Không đạt định nghĩa rollup hay validium của L2BEAT — sidechain, chuỗi tầng 3, chuỗi có mô hình bảo mật riêng.",
      vn: "An toàn của nhóm này không kế thừa từ Ethereum, phải xét theo cách khác. Nhóm này đông nhất."
    }
  },

  /* ── hệ chứng minh ────────────────────────────────── */
  heCM: {
    "Optimistic": {
      nhan: "Lạc quan",
      y: "Mặc định tin kết quả là đúng. Ai phát hiện sai thì nộp bằng chứng gian lận trong thời hạn khiếu nại.",
      vn: "Rút về Ethereum thường phải chờ hết hạn khiếu nại — quãng bảy ngày ở phần lớn thiết kế."
    },
    "Validity": {
      nhan: "Bằng chứng hợp lệ",
      y: "Mỗi lô giao dịch kèm một bằng chứng toán học chứng tỏ kết quả đúng, Ethereum kiểm trước khi chấp nhận.",
      vn: "Không cần chờ khiếu nại: bằng chứng được chấp nhận là rút được. Đổi lại chi phí tính toán cao hơn."
    }
  },

  /* giao thức tranh chấp — chỉ có nghĩa với hệ lạc quan */
  giaoThuc: {
    "Single-step": {
      nhan: "Một bước",
      y: "Tranh chấp giải quyết trong một giao dịch duy nhất: nộp bằng chứng là xong."
    },
    "Interactive": {
      nhan: "Nhiều vòng",
      y: "Hai bên đối chất qua lại nhiều vòng để thu hẹp dần điểm bất đồng, rồi mới phân xử trên Ethereum. Rẻ hơn nhưng kéo dài hơn."
    }
  },

  /* ── nhãn phụ ─────────────────────────────────────── */
  nhan: {
    thangSau: "Còn thiếu gì để lên thang sau",
    tvsTong: "Tài sản đang giữ",
    uops: "Thao tác/giây (24h)",
    khongUops: "chưa đo",
    baoDong: "đang có bất thường",
    xemXet: "đang xem xét",
    layer3: "tầng 3"
  },

  /* Ghi chú đối chiếu — con số này KHÔNG khớp với tiêu đề của
     L2BEAT và đã truy ra lý do, nên nói thẳng thay vì để người
     đọc tự nghi ngờ mình đọc nhầm. */
  ghiChuTong: "L2BEAT ở tiêu đề trang chỉ cộng các chuỗi tầng 2. Bảng này cộng cả tầng 3 nên tổng cao hơn — phần chênh gần như toàn bộ là Hyperliquid, một chuỗi tầng 3."
};

/* ═══════════════════════════════════════════════════════
   BỔ SUNG CHO CÁC MỤC NGOÀI TỔNG QUAN

   Gộp thêm vào hai bảng lớn ở trên thay vì chèn vào giữa chúng —
   dễ đọc diff hơn, và thêm mục mới sau này chỉ việc nối xuống dưới.

   L2BEAT gọi cùng một chiều bằng hai cách viết tuỳ trang
   ("committeeSecurity" ở trang rủi ro DA, "Committee security" ở
   trang tổng quan DA), nên khai cả hai — rẻ hơn nhiều so với chuẩn
   hoá khoá lúc build rồi lỡ sót một chỗ.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";
  var VI = window.DSV_VI;
  if (!VI) return;

  /* ── chiều rủi ro của lớp dữ liệu sẵn có ── */
  var CHIEU = {
    committeeSecurity: {
      nhan: "An toàn của hội đồng",
      y: "Bao nhiêu thành viên phải thông đồng thì mới giấu được dữ liệu, và họ có công khai danh tính không?"
    },
    economicSecurity: {
      nhan: "Bảo chứng kinh tế",
      y: "Có tài sản nào bị tịch thu nếu bên giữ dữ liệu giở trò không? Không có nghĩa là họ phá luật mà chẳng mất gì."
    },
    fraudDetection: {
      nhan: "Phát hiện gian lận",
      y: "Có cơ chế tự phát hiện việc giấu dữ liệu, hay phải có người tự tải toàn bộ về mới biết?"
    },
    upgradeability: {
      nhan: "Khả năng nâng cấp",
      y: "Hợp đồng có sửa được không, và sửa xong bao lâu mới có hiệu lực?"
    },
    relayerFailure: {
      nhan: "Bên chuyển tiếp ngừng việc",
      y: "Nếu bên đưa dữ liệu qua cầu ngừng làm việc thì còn đường nào khác không?"
    }
  };
  var HOA = {
    committeeSecurity: "Committee security",
    economicSecurity: "Economic security",
    fraudDetection: "Fraud detection",
    upgradeability: "Upgradeability",
    relayerFailure: "Relayer failure"
  };
  for (var c in CHIEU) if (Object.prototype.hasOwnProperty.call(CHIEU, c)) {
    VI.chieu[c] = CHIEU[c];
    VI.chieu[HOA[c]] = CHIEU[c];
  }
  VI.chieu["DA Layer"] = {
    nhan: "Lớp dữ liệu",
    y: "Dữ liệu để dựng lại số dư nằm ở đâu, và ai bảo đảm nó luôn lấy được?"
  };
  VI.chieu["DA Bridge"] = {
    nhan: "Cầu dữ liệu",
    y: "Ethereum tin vào đâu để biết dữ liệu đã thật sự được đăng?"
  };

  /* ── giá trị mới ── */
  var G = {
    "Permissioned":        { nhan: "Phải xin phép", y: "Chỉ những bên được duyệt mới vào hội đồng được." },
    "Validator set":       { nhan: "Tập người xác thực", y: "Chính tập người xác thực của chuỗi đứng ra giữ dữ liệu." },
    "TEE-based":           { nhan: "Dựa vào chip bảo mật", y: "Bảo đảm đến từ vùng thực thi tin cậy trong phần cứng — phải tin nhà sản xuất chip." },
    "Public committee":    { nhan: "Hội đồng công khai", y: "Danh tính thành viên công khai, nên còn có ràng buộc danh tiếng." },
    "Staked assets":       { nhan: "Có tài sản đặt cọc", y: "Có tiền thế chấp bị tịch thu nếu giấu dữ liệu." },
    "No slashing":         { nhan: "Không bị tịch thu", y: "Có đặt cọc nhưng không có cơ chế tịch thu — nên thực chất không mất gì khi phá luật." },
    "DA Challenges":       { nhan: "Có cơ chế khiếu nại", y: "Ai cũng thách thức được việc dữ liệu bị giấu, và bên giấu sẽ mất tiền." },
    "DAS":                 { nhan: "Lấy mẫu dữ liệu", y: "Các nút lấy mẫu ngẫu nhiên để phát hiện dữ liệu bị giấu mà không phải tải hết." },

    "No delay":            { nhan: "Sửa là có hiệu lực ngay", y: "Không có khoảng chờ nào để bạn kịp rút ra trước." },
    "Immutable":           { nhan: "Không sửa được", y: "Hợp đồng đã đóng băng, không ai đổi được nữa." },
    "Governance":          { nhan: "Qua bỏ phiếu quản trị", y: "Phải chờ một cuộc bỏ phiếu mới thay được." },

    "Self-verify":         { nhan: "Tự kiểm chứng", y: "Nút đầy đủ tải hết dữ liệu về và tự kiểm, không tin ai cả." },
    "Enshrined":           { nhan: "Gắn thẳng vào chuỗi", y: "Cầu dữ liệu là một phần của chính Ethereum, không phải hợp đồng riêng." },
    "Self-attested":       { nhan: "Tự khai", y: "Chính bên đăng dữ liệu là bên xác nhận đã đăng — không ai kiểm chéo." },
    "Self Custodied":      { nhan: "Tự giữ", y: "Dữ liệu do chính dự án giữ, không gửi ra lớp nào khác." },
    "Self custodied":      { nhan: "Tự giữ", y: "Dữ liệu do chính dự án giữ, không gửi ra lớp nào khác." },
    "DAC":                 { nhan: "Hội đồng dữ liệu", y: "Một nhóm được chỉ định giữ dữ liệu và ký xác nhận." },

    "Transaction data":    { nhan: "Dữ liệu giao dịch", y: "Đăng nguyên giao dịch, dựng lại được toàn bộ trạng thái." },
    "State diffs":         { nhan: "Chênh lệch trạng thái", y: "Chỉ đăng phần thay đổi, gọn hơn nhưng khó dựng lại lịch sử đầy đủ." },
    "Balance proofs":      { nhan: "Bằng chứng số dư", y: "Chỉ đủ để chứng minh số dư, không đủ dựng lại toàn bộ chuỗi." },

    "Intent framework":    { nhan: "Khung ý định", y: "Bạn nêu thứ mình muốn, một bên trung gian lo phần thực hiện." },
    "Intent framework (OIF)": { nhan: "Khung ý định (OIF)", y: "Khung ý định theo chuẩn mở OIF." },
    "Liquidity network":   { nhan: "Mạng thanh khoản", y: "Bên trung gian ứng tiền sẵn ở đầu bên kia rồi đòi lại sau." },
    "Gas refuel":          { nhan: "Tiếp phí giao dịch", y: "Chỉ để chuyển một ít tiền trả phí sang chuỗi mới." },
    "Resolver cancellation": { nhan: "Bên thực hiện phải huỷ", y: "Muốn lấy lại tiền thì phải trông vào chính bên đã nhận đơn đi huỷ giúp." },
    "Slow-fill fallback":  { nhan: "Đường chậm dự phòng", y: "Không ai nhận đơn thì vẫn có đường chậm hơn để tiền tới nơi." },
    "Request refund":      { nhan: "Tự xin hoàn tiền", y: "Bạn chủ động yêu cầu hoàn, không phải chờ ai." },
    "Order cancellation":  { nhan: "Tự huỷ đơn", y: "Bạn tự huỷ được đơn để lấy tiền về." },
    "Timeout refund":      { nhan: "Hết giờ tự hoàn", y: "Quá hạn mà chưa xong thì tiền tự quay về." },
    "Self-relay":          { nhan: "Tự chuyển tiếp", y: "Bạn tự đứng ra đưa dữ liệu qua, không cần bên trung gian." },
    "Whitelist / NFT":     { nhan: "Danh sách trắng / NFT", y: "Chỉ bên trong danh sách hoặc có NFT mới được nhận đơn." },
    "Permissionless":      { nhan: "Ai cũng tham gia được", y: "Không cần xin phép ai để nhận đơn." },
    "Internal":            { nhan: "Nội bộ", y: "Do chính dự án đảm nhận, không mở cho bên ngoài." },
    "Internal (sidechain)": { nhan: "Nội bộ (chuỗi bên)", y: "Thanh toán chạy trên một chuỗi riêng của dự án." },
    "HTLC-like":           { nhan: "Kiểu khoá thời gian", y: "Hai bên khoá tiền bằng một bí mật chung và mốc hết hạn." },
    "Optimistic":          { nhan: "Lạc quan", y: "Mặc định coi là đúng, có thời hạn để ai đó phản đối." },
    "Celer SGN":           { nhan: "Qua mạng Celer SGN", y: "Thông điệp đi qua mạng người bảo lãnh của Celer." },
    "deBridge messaging":  { nhan: "Nhắn tin qua deBridge", y: "Hai chuỗi nói chuyện với nhau bằng lớp thông điệp của deBridge." },
    "Wormhole messaging":  { nhan: "Nhắn tin qua Wormhole", y: "Hai chuỗi nói chuyện với nhau bằng lớp thông điệp của Wormhole." },
    "LayerZero messaging": { nhan: "Nhắn tin qua LayerZero", y: "Hai chuỗi nói chuyện với nhau bằng lớp thông điệp của LayerZero." },
    "OIF settlement":      { nhan: "Thanh toán theo chuẩn OIF", y: "Dùng cơ chế thanh toán của chuẩn mở OIF." },

    "Open":                { nhan: "Mở", y: "Ai đủ điều kiện cũng tham gia tạo khối được." },
    "Closed and capped":   { nhan: "Đóng và giới hạn", y: "Chỉ một số bên định sẵn, và có trần số lượng." },
    "Sampled committees":  { nhan: "Hội đồng bốc ngẫu nhiên", y: "Mỗi kỳ bốc ngẫu nhiên một nhóm từ tập người xếp lịch." },
    "Single proposer rotation": { nhan: "Một người đề xuất, luân phiên", y: "Mỗi lượt một bên, xoay vòng theo thứ tự." },
    "Span producers":      { nhan: "Nhóm theo đoạn", y: "Một nhóm phụ trách liên tiếp nhiều khối trong một đoạn." },

    "Reproducible":        { nhan: "Dựng lại được", y: "Ai cũng biên dịch lại mạch từ mã nguồn và đối chiếu được." },
    "Partially reproducible": { nhan: "Dựng lại được một phần", y: "Chỉ một phần mạch đối chiếu lại được, phần còn lại phải tin." },

    "Infinite":            { nhan: "Vô hạn", y: "Không có nâng cấp nào ép được bạn, muốn rút lúc nào cũng kịp." },
    "∞":              { nhan: "Vô hạn", y: "Không có nâng cấp nào ép được bạn, muốn rút lúc nào cũng kịp." },
    "Unknown":             { nhan: "Chưa rõ", y: "L2BEAT chưa xác định được." },
    "Under Review":        { nhan: "Đang xem xét", y: "L2BEAT đang rà soát lại, chưa chốt đánh giá." },
    "Exits only":          { nhan: "Chỉ cho việc rút", y: "Chỉ kiểm chứng phần rút tiền, phần còn lại không kiểm." },
    "Fraud proofs (!)":    { nhan: "Chứng minh gian lận (có cảnh báo)", y: "Có cơ chế tố cáo nhưng L2BEAT đánh dấu là còn khiếm khuyết." }
  };
  for (var k in G) if (Object.prototype.hasOwnProperty.call(G, k) && !VI.gia[k]) VI.gia[k] = G[k];

  /* "None" đổi nghĩa theo từng chiều — cùng cơ chế với Exit Window
     ở trên, xem ghi chú tại giaTheoChieu. */
  function haiCach(camel, hoa, bang) {
    VI.giaTheoChieu[camel] = bang;
    VI.giaTheoChieu[hoa] = bang;
  }
  haiCach("economicSecurity", "Economic security", {
    "None": { nhan: "Không có", y: "Không có tài sản nào bị tịch thu nếu bên giữ dữ liệu giở trò." }
  });
  haiCach("fraudDetection", "Fraud detection", {
    "None": { nhan: "Không có", y: "Không có cơ chế phát hiện; chỉ biết khi có người tự tải toàn bộ dữ liệu về đối chiếu." }
  });
  haiCach("committeeSecurity", "Committee security", {
    "None": { nhan: "Không có", y: "Không có hội đồng nào đứng ra bảo đảm dữ liệu." }
  });
  haiCach("relayerFailure", "Relayer failure", {
    "No mechanism": { nhan: "Không có lối thoát", y: "Bên chuyển tiếp ngừng là dữ liệu không qua cầu được nữa." }
  });

  /* ── tên các mục trên thanh bên ── */
  VI.muc = {
    "tong-quan":      { ten: "Tổng quan", y: "Toàn bộ thành phố Layer 2 xếp theo tài sản đang giữ." },
    "rui-ro":         { ten: "Tổng hợp", y: "Năm chiều rủi ro của mọi thành phố đặt cạnh nhau." },
    "kiem-chung":     { ten: "Kiểm chứng trạng thái", y: "Ai bảo đảm sổ sách thành phố công bố là đúng — và bằng cách nào." },
    "du-lieu":        { ten: "Dữ liệu sẵn có", y: "Dữ liệu để dựng lại số dư của bạn đang nằm ở đâu." },
    "xep-thu-tu":     { ten: "Xếp thứ tự giao dịch", y: "Ai quyết định giao dịch nào vào trước, và có ai chen vào được không." },
    "hoat-dong":      { ten: "Hoạt động", y: "Thành phố nào thật sự đông người dùng, đo bằng thao tác mỗi giây." },
    "do-song":        { ten: "Độ sống", y: "Bao lâu thành phố mới gửi một lô giao dịch và một bản cập nhật lên Ethereum." },
    "luu-tru":        { ten: "Đã ngừng hoạt động", y: "Những thành phố đã đóng cửa — giữ lại để đối chiếu." },
    "lt-tong-quan":   { ten: "Tổng quan", y: "Các giao thức nối chuỗi này với chuỗi kia." },
    "lt-khung-token": { ten: "Khung token", y: "Chuẩn để một token đi lại giữa nhiều chuỗi mà vẫn là một." },
    "lt-cau-y-dinh":  { ten: "Cầu ý định", y: "Bạn nêu thứ mình muốn, bên khác lo phần chạy qua chuỗi." },
    "rieng-tu":       { ten: "Quyền riêng tư", y: "Các giao thức che giấu dòng tiền, và mức độ tin cậy chúng đòi hỏi." },
    "dl-tong-quan":   { ten: "Tổng quan", y: "Các lớp giữ dữ liệu cho thành phố Layer 2." },
    "dl-rui-ro":      { ten: "Rủi ro", y: "Điều gì xảy ra nếu lớp giữ dữ liệu giấu dữ liệu đi." },
    "dl-thong-luong": { ten: "Thông lượng", y: "Mỗi lớp đang tải bao nhiêu dữ liệu, và còn dư bao nhiêu chỗ." },
    "dl-do-song":     { ten: "Độ sống", y: "Lớp dữ liệu có đang chạy đều không." },
    "dl-luu-tru":     { ten: "Đã ngừng", y: "Những lớp dữ liệu không còn dùng nữa." },
    "zk":             { ten: "Danh mục ZK", y: "Các cỗ máy sinh bằng chứng toán học, và ai đang dùng chúng." },
    "st-arbitrum-orbit": { ten: "Arbitrum Orbit", y: "Họ chuỗi dựng trên bản vẽ Arbitrum." },
    "st-elastic":     { ten: "The Elastic Network", y: "Họ chuỗi dựng trên ZK Stack của Matter Labs." },
    "st-superchain":  { ten: "Superchain", y: "Họ chuỗi dựng trên OP Stack của Optimism." },
    "st-agglayer":    { ten: "Agglayer", y: "Họ chuỗi nối vào lớp tổng hợp của Polygon." },
    "tu-dien":        { ten: "Từ điển", y: "Toàn bộ thuật ngữ L2BEAT dùng, kèm định nghĩa gốc." }
  };
})();
