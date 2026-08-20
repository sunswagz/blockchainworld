/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — xuong

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của CHÍNH nhà máy — không thuộc cung nào.
   Đóng dấu bản số liệu, báo cáo sức khoẻ, giao hàng. */

export const NODE = [
  {
    ma: "dong-dau", ten: "Đóng dấu bản số liệu",
    tram: "M16", che: "script", nhip: 6,
    lenh: "node scripts/pin-snapshot.mjs",
    ra: [],
    y: "Pin bản số liệu 1,8 KB lên IPFS. Tự bỏ qua nếu sha256 trùng bản trước."
  },
  {
    ma: "bao-cao", ten: "Báo cáo sức khoẻ xưởng",
    tram: "M18", che: "claude", nhip: 24,
    lenh: "anthropics/claude-code-action",
    ra: ["factory/bao-cao.md"],
    y: "Claude Code Action đọc state.json rồi viết vài dòng tiếng Việt: " +
       "node nào đang ốm, ốm từ bao giờ, nên xem chỗ nào trước."
  },
  {
    ma: "giao-hang", ten: "Giao hàng lên Pages",
    tram: "M16", che: "theo", nhip: 0,
    lenh: ".github/workflows/deploy-pages.yml",
    ra: [],
    y: "Không có nhịp riêng — chạy khi có commit số liệu. 27/27 lượt thành công."
  }
];
