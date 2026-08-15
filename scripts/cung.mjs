/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ CUNG — một chỗ duy nhất.

   Trước đây mỗi cung tự giữ một bản chép danh sách các cung khác
   trong `assets/js/halls.js`. Với N cung thì đó là N bản chép của
   cùng một sự thật, và thêm một cung là sửa tay N file.

   Ở 7 cung đã là 6 lần sửa lặp lại mỗi lần thêm. Với một hoàng
   thành nhiều bộ nhiều ban thì con số đó chỉ có tăng, và mỗi lần
   sửa tay là một cơ hội sót — sót thì cung mới thành ngõ cụt ở
   đúng cung bị sót, không ai thấy vì các cung khác vẫn nối được.

   Giờ: sửa ở đây, chạy `npm run halls`, cả N file tự sinh lại.

   ── THÊM CUNG MỚI ─────────────────────────────────────
   Thêm một khối vào CUNG bên dưới, rồi:

       npm run halls      sinh lại halls.js của mọi cung
       npm run kiem       soát xem còn thiếu chỗ nào

   Thứ tự trong mảng là thứ tự hiện trong thanh bên. Đang xếp
   theo đúng thứ bậc kinh đô như ở Cổng Thành: vòng ngoài → vòng
   trong → các nha môn.
   ═══════════════════════════════════════════════════════ */

export const CUNG = [
  {
    ma: "kinh-thanh",
    ten: "Kinh Thành",
    note: "9 quốc gia L1",
    icon: '<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2"/>' +
          '<path d="M12 3.4c2.4 2.4 3.6 5.3 3.6 8.6s-1.2 6.2-3.6 8.6c-2.4-2.4-3.6-5.3-3.6-8.6S9.6 5.8 12 3.4Z"/>'
  },
  {
    ma: "hoang-thanh",
    ten: "Hoàng Thành",
    note: "15 nền văn hoá",
    icon: '<path d="M3 21h18M5 21V10l7-5.5L19 10v11"/><path d="M9.5 21v-5.5h5V21"/>'
  },
  {
    ma: "tu-cam-thanh",
    ten: "Tử Cấm Thành",
    note: "lõi giao dịch",
    icon: '<path d="M2.5 21h19"/><path d="M4.5 21V9.5h15V21"/><path d="M3 9.5 12 4l9 5.5"/>' +
          '<path d="M10.2 21v-5a1.8 1.8 0 0 1 3.6 0v5"/><path d="M7 21v-3.2a1.2 1.2 0 0 1 2.4 0V21"/>' +
          '<path d="M14.6 21v-3.2a1.2 1.2 0 0 1 2.4 0V21"/>'
  },
  {
    ma: "tao-bien-xu",
    ten: "Tạo Biện Xứ",
    note: "công xưởng AI",
    icon: '<path d="M3 21h18M5 21V11l4-3v13M13 21V6l6-3v18"/><path d="M8 15h.01M16 12h.01"/>'
  },
  {
    ma: "cong-bo",
    ten: "Công Bộ",
    note: "bộ đồ nghề",
    icon: '<path d="M14.5 5.5a4 4 0 0 0 5 5l-9.5 9.5a2.1 2.1 0 0 1-3-3z"/>' +
          '<path d="M14.5 5.5 17 3l4 4-2.5 2.5"/>'
  },
  {
    ma: "ho-bo",
    ten: "Hộ Bộ",
    note: "dòng tiền blockchain",
    icon: '<ellipse cx="12" cy="6" rx="7.5" ry="2.8"/>' +
          '<path d="M4.5 6v4.4c0 1.55 3.36 2.8 7.5 2.8s7.5-1.25 7.5-2.8V6"/>' +
          '<path d="M4.5 10.4v4.4c0 1.55 3.36 2.8 7.5 2.8s7.5-1.25 7.5-2.8v-4.4"/>' +
          '<path d="M4.5 14.8v3.2c0 1.55 3.36 2.8 7.5 2.8s7.5-1.25 7.5-2.8v-3.2"/>'
  },
  {
    ma: "do-sat-vien",
    ten: "Đô Sát Viện",
    note: "bảng xét Layer 2",
    icon: '<path d="M3.5 20.5h17"/><path d="M4.5 16.8h7.2v3.7H4.5z"/>' +
          '<path d="M7 12.4h7.2v4.4H7z"/><path d="M9.5 8h7.2v4.4H9.5z"/>'
  },
  {
    ma: "dai-quan-trac",
    ten: "Đài Quan Trắc",
    note: "địa chính trị",
    icon: '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.2"/>' +
          '<path d="M12 12l6-3.6"/><circle cx="12" cy="12" r="1.3" fill="currentColor"/>'
  },
  {
    ma: "tang-thu-cac",
    ten: "Tàng Thư Các",
    note: "kho Claude Skills",
    icon: '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H10v16H5.5A1.5 1.5 0 0 1 4 18.5z"/>' +
          '<path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H14v16h4.5a1.5 1.5 0 0 0 1.5-1.5z"/>'
  }
];

/* Cổng Thành không phải cung — nó là cửa ngõ, luôn đứng cuối danh sách. */
export const CONG_THANH = {
  ma: "",
  ten: "Cổng Thành",
  note: "cửa ngõ",
  icon: '<path d="M2.5 21h19"/><path d="M4 21V7.5h3.2M19.8 7.5H23V21"/>' +
        '<path d="M8.5 21v-8a3.5 3.5 0 0 1 7 0v8"/><path d="M7 7.5 12 3l5 4.5"/>'
};
