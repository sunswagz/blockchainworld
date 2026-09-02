/* ═══════════════════════════════════════════════════════
   PHIẾU TOÀN THÀNH — chấm mọi cung, một bảng.

       node scripts/phieu-toan-thanh.mjs          ghi factory/phieu.json
       node scripts/phieu-toan-thanh.mjs --in     chỉ in ra, không ghi

   ── VÌ SAO CÓ FILE NÀY ────────────────────────────────
   `scripts/tien-hoa.mjs do <cung>` chấm được MỌI cung, nhưng chỉ
   BỐN cung có vòng tiến hoá gọi tới nó. Tám cung còn lại chưa từng
   được chấm trong một lượt bot nào — điểm của chúng chỉ hiện ra khi
   có người ngồi gõ lệnh, tức là gần như không bao giờ.

   Đo ngày 29/08, và chính vì thế mà không ai biết: Kinh Thành 11/13,
   Khâm Thiên Giám 8/13. Không phải chúng mới hỏng — chúng vẫn vậy
   suốt, chỉ là không có thước nào chỉ vào.

   Node này KHÔNG gọi model (`che: "script"`). Nó chỉ chạy lại phép
   đo đã có cho cả mười hai cung rồi ghi một file. Thấy được vấn đề
   là việc rẻ; sửa mới là việc đắt, và sửa vẫn là việc của vòng tiến
   hoá hoặc của người.

   ── KHÔNG DỰNG THÊM MỘT BỘ ĐO THỨ HAI ─────────────────
   File này gọi thẳng `tien-hoa.mjs do <cung> --ghi` qua tiến trình
   con. Chép phép đo sang đây thì hai bản sẽ lệch, và lệch thì không
   ai báo — đúng cái bẫy mà `scripts/mang-truoc.mjs` và
   `scripts/tuoi-du-lieu.mjs` sinh ra để gỡ.

   Chạy tiến trình con còn một cái lợi nữa: `do` dựng DOM giả rồi nạp
   app.js của cung. Mười hai cung nạp trong CÙNG một tiến trình là
   mười hai lần ghi đè `global.window`, và cung nào ngã sẽ kéo theo
   cả bảng.
   ═══════════════════════════════════════════════════════ */

import { execFileSync } from "node:child_process";
import { writeFileSync, readFileSync, existsSync, readdirSync, mkdirSync, rmSync } from "node:fs";
import { join, dirname } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const CHI_IN = process.argv.includes("--in");
const RA = join(ROOT, "factory", "phieu.json");

/* Cùng phép nhận diện cung với kiem-quy-trinh.mjs: thư mục có
   index.html NGAY tại gốc nó. Ba runtime Python chỉ có
   web/index.html ở tầng hai nên không lọt vào. */
const cung = readdirSync(ROOT, { withFileTypes: true })
  .filter((d) => d.isDirectory() && !d.name.startsWith(".") && d.name !== "node_modules")
  .map((d) => d.name)
  .filter((n) => existsSync(join(ROOT, n, "index.html")))
  .sort();

/* Cổng Thành không lọt vào phép trên vì mã của nó ở NGAY gốc repo,
   không trong một thư mục con. Nó là trang đầu tiên người ta thấy và
   là trang duy nhất phiếu này bỏ sót suốt — `tien-hoa.mjs` nhận
   `cong-thanh` làm bí danh cho gốc, nên chỉ cần gọi tên nó ra.

   Thêm vào ĐÂY chứ không nới phép nhận diện ở trên: nới ra thì
   `dist/`, `knowledge-os/` và ba runtime Python cũng có cửa lọt vào,
   mà cả bốn đều cố ý không phải cung. */
if (existsSync(join(ROOT, "index.html"))) cung.push("cong-thanh");

/* Mỗi cung một tiến trình, và mỗi tiến trình một trần giờ. Cung nào
   treo thì mất đúng cung đó chứ không mất cả bảng — cùng lối `do` đã
   đi với DOM giả (HAN_GIAY = 45 trong tien-hoa.mjs). */
const HAN_MS = 150000;

const bang = [];
for (const c of cung) {
  const tam = join(tmpdir(), "phieu-" + c + "-" + process.pid + ".json");
  try {
    execFileSync(process.execPath,
      [join(ROOT, "scripts", "tien-hoa.mjs"), "do", c, "--ghi", tam],
      { cwd: ROOT, encoding: "utf8", timeout: HAN_MS, stdio: "ignore" });
    const p = JSON.parse(readFileSync(tam, "utf8"));
    const xau = (p.diem || []).filter((d) => d.dat === false);
    const truot = xau.map((d) => d.ma);
    /* CHÉP CẢ LỜI GIẢI THÍCH, không chỉ mã thước.

       Bản đầu chỉ ghi mã, và lượt bot 29/08 03:47 ghi "ve" cho 11 trên
       12 cung — trong khi ở máy cả 12 đều đạt. Có một khác biệt thật
       giữa Actions và máy, mà phiếu không mang theo một chữ nào để lần
       ra nó. Một bảng điểm nói "hỏng" mà không nói "hỏng thế nào" thì
       chỉ chuyển được nỗi lo, không chuyển được việc. */
    const truotVi = xau.map((d) => ({ thuoc: d.ma, vi: String(d.y || "").slice(0, 200) }));
    bang.push({ cung: c, dat: p.dat, tong: p.tong, khongDo: p.khongDo, truot, truotVi });
    console.log("  " + (truot.length ? "·" : "✓") + " " + c.padEnd(17) + " " + p.dat + "/" + p.tong +
      (truot.length ? "  trượt: " + truot.join(" ") : "  đủ"));
    for (const t of truotVi) console.log("        " + t.thuoc.padEnd(12) + t.vi.slice(0, 88));
  } catch (e) {
    const vi = String(e.message || e).slice(0, 120);
    bang.push({ cung: c, loi: vi });
    console.log("  ✗ " + c.padEnd(17) + " không chấm được: " + vi.slice(0, 70));
  } finally {
    try { rmSync(tam, { force: true }); } catch { /* rác tạm, không đáng ngã vì nó */ }
  }
}

const xong = bang.filter((b) => b.tong);
const tongDat = xong.reduce((n, b) => n + b.dat, 0);
const tongThuoc = xong.reduce((n, b) => n + b.tong, 0);

/* Thước nào đang trượt ở NHIỀU cung nhất — đó mới là việc đáng làm
   trước, và nó chỉ thấy được khi nhìn cả mười hai cung một lượt.
   Nhìn từng cung thì mỗi lỗi trông như chuyện riêng của cung đó. */
const demTruot = {};
for (const b of xong) for (const t of b.truot) demTruot[t] = (demTruot[t] || 0) + 1;
const nong = Object.entries(demTruot).sort((a, b) => b[1] - a[1]);

console.log("\n  " + tongDat + "/" + tongThuoc + " thước đạt trên " + xong.length + " cung" +
  (nong.length ? "\n  trượt nhiều nhất: " +
    nong.slice(0, 4).map(([t, n]) => t + " (" + n + " cung)").join(" · ") : ""));

if (!CHI_IN) {
  mkdirSync(dirname(RA), { recursive: true });
  writeFileSync(RA, JSON.stringify({
    generatedAt: new Date().toISOString(),
    ghiChu: "SINH TỰ ĐỘNG bởi scripts/phieu-toan-thanh.mjs. Đừng sửa tay.",
    tongDat, tongThuoc, soCung: xong.length,
    truotNhieuNhat: nong.map(([thuoc, soCung]) => ({ thuoc, soCung })),
    cung: bang
  }, null, 2) + "\n", "utf8");
  console.log("  → factory/phieu.json");
}
