/* ═══════════════════════════════════════════════════════
   SỔ ĐĂNG KÝ CHỦ THỂ — Đài Quan Trắc

   Hai script của cung này (build-quantrac.mjs và build-scan.mjs)
   đều phải biết "có những nước nào, dữ liệu nằm đâu, ghi ra đâu".
   Để ở một chỗ chứ không chép hai bản: hai bản sao thì sẽ lệch,
   và cái lệch đó im lặng — bot vẫn chạy xanh, chỉ có một nước là
   không được cập nhật.

   Thêm nước thứ ba: thêm một khối ở đây, xong. Không script nào
   phải sửa, vì cả hai đều đọc bảng này.
   ═══════════════════════════════════════════════════════ */

import { readFile } from "node:fs/promises";
import { join } from "node:path";
import vm from "node:vm";

export const CHU_THE = [
  {
    id: "vn", ten: "Việt Nam",
    data: ["assets", "js", "data.js"], bien: "DQT_DATA",
    doRa: ["assets", "js", "do.js"], doBien: "DQT_DO",
    scanRa: ["assets", "js", "scan.js"], scanBien: "DQT_SCAN",
    boiCanh: "tác động tới KINH TẾ VIỆT NAM — giá cả, tỷ giá, việc làm, đơn hàng"
  },
  {
    id: "tq", ten: "Trung Quốc",
    data: ["assets", "js", "tq", "data.js"], bien: "DQT_TQ",
    doRa: ["assets", "js", "tq", "do.js"], doBien: "DQT_TQ_DO",
    scanRa: ["assets", "js", "tq", "scan.js"], scanBien: "DQT_TQ_SCAN",
    /* Bối cảnh KHÁC HẲN Việt Nam, và đây là chỗ dễ sai nhất: một cú
       sốc kinh tế KHÔNG trực tiếp đe doạ chế độ. Nó phải chuyển hoá
       thành xung đột phân phối trong nội bộ trước đã. Viết `tac_dong`
       theo khuôn Việt Nam ở đây là hỏng đúng phần cốt lõi. */
    boiCanh: "tác động tới KHẢ NĂNG GIỮ QUYỀN LỰC của ĐCSTQ — đường truyền là " +
             "cú sốc → thu ngân sách → khả năng nuôi bộ máy → thống nhất tầng lãnh đạo"
  }
];

/* Đọc dữ liệu của một chủ thể bằng cách CHẠY THẬT file trình duyệt
   trong sandbox. Nhờ vậy không có bản sao nào của danh sách chiến
   trường hay bảng ngưỡng nằm trong scripts/ — sửa data.js là lượt
   chạy sau tự có. */
export async function docChuThe(APP, ct) {
  const src = await readFile(join(APP, ...ct.data), "utf8");
  const hop = { window: {} };
  vm.createContext(hop);
  vm.runInContext(src, hop, { timeout: 5000 });
  const d = hop.window[ct.bien];
  if (!d) throw new Error(`không đọc được ${ct.bien} trong ${ct.data.join("/")}`);
  return d;
}
