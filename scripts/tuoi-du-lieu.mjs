/* ═══════════════════════════════════════════════════════
   Độ tươi của các file dữ liệu tự sinh — một nguồn sự thật.

   Dùng bởi hai chỗ, với hai mục đích khác nhau:
     · build-dist.mjs — in ra để người dựng bản nhìn
     · kiem-quy-trinh.mjs — nhắc ở đầu phiên làm việc

   Để chung ở đây vì ngưỡng "mấy ngày là cũ" và cách đọc dấu
   thời gian phải giống nhau ở cả hai. Chép làm hai bản thì
   chúng lệch, và lệch thì không ai báo — đúng thứ cả bộ kiểm
   này sinh ra để chặn.

   Vì sao cần: 13–14/08/2026 đường ống bot chết hơn một ngày
   (bước đóng dấu Pinata ngã kéo cả job, rồi job hết giờ 10
   phút). build-dist.mjs có in "⚠" nhưng nó không thoát khác 0
   và không ai chạy `npm run dist` mỗi phiên, nên không ai
   thấy. Site đứng im, không có lỗi nào nổi lên.
   ═══════════════════════════════════════════════════════ */

import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";

/* Bot chạy 4 lượt/ngày, tức cách nhau 6 giờ. Quá 1 ngày nghĩa là
   BỐN lượt liên tiếp không ghi được gì — không còn là trục trặc
   nhất thời nữa.

   Ngưỡng cũ ở build-dist.mjs là 2 ngày. Quá lỏng: nó đợi tám lượt
   hỏng liên tiếp mới hé răng, mà đợt chết 13–14/08 vừa rồi kéo dài
   hơn một ngày và vẫn chưa chạm ngưỡng đó. */
export const NGAY_TOI_DA = 1;

/* Ngưỡng riêng cho nguồn có nhịp khác. Từ khi nhịp chạy nằm ở
   `nhip` của từng node trong scripts/nha-may.mjs, "1 ngày" thôi
   đúng cho mọi nguồn: node nhịp 24 giờ thì vừa chạy xong đã gần
   chạm ngưỡng 1 ngày, và mỗi phiên lại thấy một cảnh báo cho thứ
   đang chạy đúng hẹn. Cảnh báo báo nhầm mãi thì bị bỏ qua, kéo
   theo cả lần nó đúng — nên nguồn nào nhịp thưa thì khai `nguong`. */
export const nguongCua = (n) => n.nguong ?? NGAY_TOI_DA;

/* botSinh: false = sinh bằng tay, cũ là bình thường, đừng nhắc.
   Hoàng Thành lấy nguồn từ thư mục NGOÀI repo nên Actions không
   quét được — xem mục "Hoàng Thành là ngoại lệ" trong CLAUDE.md.

   tamDung: nguồn DO BOT sinh nhưng lịch đang tắt có chủ ý. Khác hẳn
   botSinh:false — chỗ kia cũ là bản chất, chỗ này cũ là hậu quả của
   một quyết định và sẽ phải bật lại.

   Vì sao không dùng luôn botSinh:false cho tiện: nó sẽ im hẳn, và im
   hẳn thì sáu tháng nữa không ai nhớ có một nguồn đang tắt. Còn để
   nguyên botSinh:true thì mỗi phiên lại thấy một cảnh báo "có gì đó
   gãy" cho một thứ không gãy — mà cảnh báo báo nhầm mãi sẽ bị bỏ qua,
   kéo theo cả lần nó đúng. Nên có trạng thái thứ ba: nhắc một dòng
   bình thản, đúng bằng sự thật. */
export const NGUON = [
  { nhan: "số liệu Kinh Thành",      duong: "kinh-thanh/assets/js/data/live.js", botSinh: true },
  /* Bật lại 14/08/2026 sau khi vặn ba núm chi phí (haiku thay opus,
     max_uses 3, nhịp 24 giờ thay 6). Nhịp 24 giờ nên ngưỡng riêng —
     dùng NGAY_TOI_DA=1 chung thì nó bị báo cũ ngay sau mỗi lượt. */
  { nhan: "bản quét Quan Trắc",      duong: "dai-quan-trac/assets/js/scan.js",   botSinh: true,
    nguong: 2 },
  { nhan: "bảng cảnh báo Quan Trắc", duong: "dai-quan-trac/assets/js/do.js",     botSinh: true },
  { nhan: "bảng xét Đô Sát Viện",    duong: "do-sat-vien/assets/js/data.js",     botSinh: true },
  { nhan: "đồ nghề Công Bộ",         duong: "cong-bo/assets/js/data.js",         botSinh: true },
  { nhan: "dòng tiền Hộ Bộ",         duong: "ho-bo/assets/js/v/dong-tien.js",    botSinh: true },
  { nhan: "kho skill Tàng Thư Các",  duong: "tang-thu-cac/assets/js/data.js",    botSinh: true },
  { nhan: "đoàn tàu Thái Bộc Tự",    duong: "thai-boc-tu/assets/js/v/doan-tau.js", botSinh: true },
  { nhan: "công trường Thái Bộc Tự", duong: "thai-boc-tu/assets/js/v/cong-truong.js", botSinh: true },
  { nhan: "rừng văn hoá Hoàng Thành", duong: "hoang-thanh/assets/js/data.js",    botSinh: false },
  /* Cùng lý do Hoàng Thành: runtime giao dịch cần khoá API và một tiến trình
     chạy dài, Actions không làm được. Sinh tay ở máy rồi commit — nên cũ là
     bình thường, không được kèm ⚠. */
  { nhan: "phiên Tử Cấm Thành",      duong: "tu-cam-thanh/assets/js/v/phien.js", botSinh: false }
];

/* Dấu thời gian viết cả hai kiểu tuỳ script sinh ra nó:
   `"generatedAt":"…"` và `"generatedAt": "…"`. Thiếu \s* là
   sót đúng một nửa số file mà vẫn chạy êm. */
const RE = /"generatedAt"\s*:\s*"([^"]+)"/;

/* Trả { co, ngay } — co=false khi chưa chạy lần nào hoặc file
   không có dấu thời gian. Không ném lỗi: gọi ở đầu phiên, hỏng
   một file không được làm chết cả bộ kiểm. */
export async function tuoi(goc, duong) {
  const p = join(goc, duong);
  if (!existsSync(p)) return { co: false };
  let m;
  try { m = RE.exec(await readFile(p, "utf8")); } catch { return { co: false }; }
  if (!m) return { co: false };
  const t = new Date(m[1]).getTime();
  if (!Number.isFinite(t)) return { co: false };
  return { co: true, ngay: (Date.now() - t) / 864e5, luc: m[1] };
}
