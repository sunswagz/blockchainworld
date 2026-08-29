/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ NODE — tang-thu-cac

   scripts/nha-may.mjs đọc CẢ thư mục này rồi gộp lại thành mảng
   NODE. Một cung một file là có lý do: trước đây mọi cung khai
   chung một mảng trong nha-may.mjs, nên hai phiên thêm hai cung
   là hai người sửa cùng vài dòng — xung đột mỗi lần, không trừ
   lần nào. Tách ra thì git không có gì để mà đụng.

   Trường bắt buộc: ma · ten · tram · che · nhip · lenh · ra · y
   Xem đầu scripts/nha-may.mjs để biết ý nghĩa từng trường.
   ═══════════════════════════════════════════════════════ */

/* Node của cung tang-thu-cac.
   Sửa nhịp, thêm hay bỏ node của cung này thì sửa ĐÚNG file này —
   không phiên nào khác phải chạm vào, nên không ai xung đột với ai. */

export const NODE = [
  {
    ma: "tang-thu-cac", ten: "Kho skill Tàng Thư Các", cung: "tang-thu-cac",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-tangthu.mjs",
    /* KHÔNG khai cả `assets/data/`. Thư mục đó còn chứa `dich/` —
       bản dịch tiếng Việt VIẾT TAY cho skill cộng đồng, bot không hề
       ghi. Khai rộng thì `git add` nuốt luôn bản dịch dở của người
       đang sửa; đã cắn thật, xem dacf631. Khối `git add` trong
       workflow từng thu hẹp đúng còn sổ này thì chưa — nay `git add`
       sinh ra TỪ sổ, nên chỗ hẹp phải nằm ở đây mới có tác dụng. */
    ra: ["tang-thu-cac/assets/js/data.js",
         "tang-thu-cac/assets/data/lich-su.json",
         "tang-thu-cac/assets/data/kb/"],
    y: "Quét kho Claude Skills trên GitHub. Bước chậm nhất, và PHÌNH THEO KHO: 532 giây khi viết dòng này, 684 giây ngày 29/08. Van đã nới 14 → 20 phút."
  },
  /* M11 · Kho dụng cụ. Tàng Thư Các quét 3.656 skill rồi để đó — repo
     không có `.claude/skills/` nên KHÔNG phiên nào, kể cả bot, gọi
     được cái nào. Node này nối chỗ đứt: chọn skill đầu bảng theo
     nhóm, tải SKILL.md về kệ, ghi sổ xuất xứ kèm sha256.

     Nhịp 24 chứ không 6: catalogue chỉ đổi khi `tang-thu-cac` chạy,
     mà kệ dụng cụ thì không cần bám theo từng lượt của nó. */
  {
    ma: "nhap-skill", ten: "Nhập skill vào kệ", cung: "tang-thu-cac",
    tram: "M11", che: "script", nhip: 24,
    lenh: "node scripts/nhap-skill.mjs",
    ra: [".claude/skills/", "factory/skills.json"],
    y: "Chọn skill đầu bảng theo nhóm rồi tải SKILL.md vào .claude/skills/. " +
       "CHỈ lấy chỉ dẫn, không lấy script chạy được của người lạ."
  },
];
