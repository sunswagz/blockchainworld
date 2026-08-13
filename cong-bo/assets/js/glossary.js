/* ═══════════════════════════════════════════════════════
   Chú giải Công Bộ — dịch và giải nghĩa.

   Cùng lối với Đô Sát Viện: mỗi mục có tên tiếng Việt, một câu
   nói nó là gì, và một câu nói nó dùng để làm gì cho người đọc.

   Sửa tay được. Đây là file duy nhất trong cung này không tự sinh.
   ═══════════════════════════════════════════════════════ */
window.CB_VI = {

  soHamSan: 29,

  /* ── ba công cụ ───────────────────────────────────── */
  muc: {
    "giai-ma": {
      ten: "Giải mã lời gọi",
      y: "Dán vào chuỗi calldata của một giao dịch, trả về tên hàm và từng tham số đã đọc ra nghĩa.",
      vn: "Khi xem một giao dịch trên Etherscan mà chỉ thấy một dãy hex dài, đây là chỗ dịch nó ra tiếng người: hàm nào đang được gọi, gửi cho ai, bao nhiêu. Chạy hẳn trong máy bạn — không gửi dữ liệu đi đâu, trừ khi phải tra tên hàm lạ."
    },
    "nhat-ky": {
      ten: "Nhật ký đổi thay",
      y: "Hợp đồng on-chain của các dự án Layer 2 vừa bị đổi những gì, trong 30 ngày gần nhất.",
      vn: "Đây là chỗ thấy trước khi báo chí kịp viết. Một tham số bảo mật bị sửa, một địa chỉ quản trị bị thay — tất cả hiện ở đây dưới dạng diff, ngay khi máy quét của L2BEAT phát hiện."
    },
    "kinh-lup": {
      ten: "Kính lúp hồ sơ",
      y: "Dự án nào đã dựng đủ hồ sơ, dự án nào còn bỏ trống hạng mục nào.",
      vn: "Một dự án thiếu nhiều hạng mục không có nghĩa là nó tệ — nghĩa là chưa ai soi kỹ nó. Với người gửi tiền, chỗ chưa ai soi mới đáng ngại hơn chỗ đã soi và thấy điểm yếu."
    },
    "xuong-huy-hieu": {
      ten: "Xưởng huy hiệu",
      y: "Xếp logo của các dự án thành một tấm, lọc theo tầng và trạng thái, rồi tải về dạng PNG.",
      vn: "Dùng khi cần một tấm ảnh gộp logo cho bài viết hay slide. Chạy hẳn trong máy bạn: 198 logo đã tải sẵn về repo nên không gọi mạng lần nào."
    },
    "di-noi-khac": {
      ten: "Đi nơi khác",
      y: "Bốn mục trong danh sách của tools.l2beat.com thật ra là liên kết trỏ sang ứng dụng khác, không phải công cụ nằm trong trang đó.",
      vn: "Liệt kê ra đây cho đủ, kèm ghi chú vì sao không dựng lại được — chứ không giả vờ là chúng không tồn tại."
    }
  },

  /* ── 11 hạng mục hồ sơ ────────────────────────────── */
  hangMuc: {
    hopDong:      { ten: "Hợp đồng", y: "danh sách hợp đồng đã được máy quét tự dựng" },
    quyenHan:     { ten: "Quyền hạn", y: "ai nắm quyền gì, cũng do máy quét tự dựng" },
    chiPhi:       { ten: "Chi phí", y: "đã đo được chi phí vận hành chưa" },
    doSong:       { ten: "Độ sống", y: "đã theo dõi nhịp gửi lô và cập nhật trạng thái chưa" },
    cotMoc:       { ten: "Cột mốc", y: "đã ghi các mốc lịch sử của dự án chưa" },
    benVanHanh:   { ten: "Bên vận hành", y: "đã mô tả ai đang chạy chuỗi này chưa" },
    rutTien:      { ten: "Đường rút tiền", y: "đã mô tả cách rút tài sản về Ethereum chưa" },
    luuYKhac:     { ten: "Lưu ý khác", y: "những điểm riêng chưa xếp vào đâu được" },
    dungTrangThai:{ ten: "Cách dựng trạng thái", y: "đã mô tả cách dựng lại sổ sách từ dữ liệu chưa" },
    kiemChung:    { ten: "Kiểm chứng trạng thái", y: "đã mô tả ai bảo đảm sổ sách đúng chưa" },
    nangCap:      { ten: "Nâng cấp và quản trị", y: "đã mô tả ai đổi được hợp đồng, và mất bao lâu chưa" }
  },

  /* Ghi chú nguồn — nói thẳng chỗ mong manh thay vì để người dùng
     tự phát hiện lúc trang trống trơn. */
  ghiChuNguon: "Nhật ký đổi thay lấy từ um-prod.l2beat.com; kính lúp hồ sơ lấy từ fe-stag.l2beat.com — fe-stag là host staging của L2BEAT, không phải bản chính thức, nên có thể đổi hoặc tắt bất cứ lúc nào."
};
