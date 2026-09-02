/* ═══════════════════════════════════════════════════════
   HƯỚNG — thứ duy nhất trong xưởng KHÔNG sinh bản vá.

       node scripts/huong.mjs          ghi factory/huong.json
       node scripts/huong.mjs --in     chỉ in ra

   ── VÌ SAO CÓ FILE NÀY ────────────────────────────────
   Bảy vòng tiến hoá đang chạy đều là vòng SỬA. Thước hỏi "có gì
   hỏng không"; hỏng thì vá xong là hết, và khi phiếu đã đầy thì
   model chỉ còn được bảo "tìm một chỗ không thước nào đo". Nó làm
   được — sổ tiến hoá chứng minh — nhưng đó là phán đoán trong
   PHẠM VI MỘT TRANG. Không cơ chế nào hỏi "cả cái này nên thành
   cái gì tiếp".

   Đó là chỗ hệ phải nhờ người, và người dùng đã nói thẳng ra.

   ── NÓ LÀM ĐƯỢC NỬA NÀO, VÀ KHÔNG LÀM ĐƯỢC NỬA NÀO ────
   Hướng có hai nửa:

     "thiếu gì · lệch gì · phí gì"            SUY RA ĐƯỢC từ repo
     "cái này ĐỂ LÀM GÌ, gì quan trọng nhất"  KHÔNG suy ra được

   File này làm nửa đầu cho tử tế rồi giao nửa sau. Nó thu hẹp từ
   mọi khả năng xuống vài lựa chọn CÓ SỐ ĐẾM KÈM. Người chọn.

   Đổi "AI cần người định hướng" thành "AI dọn bàn, người chọn" là
   một bước thật. Giả vờ nó tự chọn được thì chỉ ra thêm việc, vì
   một hướng không ai kiểm là một hướng không ai theo.

   ── LUẬT: MỖI ĐỀ XUẤT PHẢI ĐẾM ĐƯỢC ───────────────────
   Không dòng nào trong file ra được phép là ý kiến. Mỗi mục kèm
   một con số lấy từ repo và một lệnh để bác nó. Không có luật ấy
   thì đây là máy sinh ý tưởng — mà ý tưởng thì không thiếu; thứ
   thiếu là ý tưởng có bằng chứng.

   ── VÀ NÓ CÓ THỂ SAI ──────────────────────────────────
   Báo cáo Opus ngày 01/09 khai `tri-thuc` "CẦN KIỂM" vì `lucDoi`
   là null. Kiểm thật: sinh lại 11 lát cắt ra 0 file đổi — cổng
   chặn của `tri-thuc-tien-hoa` đã sinh lại ở lớp 2 nên node kia
   không còn việc. Báo động nhầm, và nhầm theo lối rất thuyết
   phục. Nên mỗi mục ở đây mang `kiemBang`.
   ═══════════════════════════════════════════════════════ */

import { readFileSync, writeFileSync, existsSync, readdirSync, statSync, mkdirSync } from "node:fs";
import { join, dirname, extname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const CHI_IN = process.argv.includes("--in");
const RA = join(ROOT, "factory", "huong.json");
const doc = (p) => readFileSync(p, "utf8");
const co = (p) => existsSync(p);

const cung = readdirSync(ROOT, { withFileTypes: true })
  .filter((d) => d.isDirectory() && !d.name.startsWith(".") && d.name !== "node_modules")
  .map((d) => d.name).filter((n) => co(join(ROOT, n, "index.html"))).sort();

function quet(d, ra = []) {
  for (const n of readdirSync(d)) {
    const p = join(d, n);
    statSync(p).isDirectory() ? quet(p, ra) : ra.push(p);
  }
  return ra;
}

/* Đọc một lần, dùng lại — quét 12 cung bốn lượt thì chậm gấp bốn
   mà không thêm được gì. */
const kho = {};
for (const c of cung) {
  const html = doc(join(ROOT, c, "index.html"));
  const dCss = join(ROOT, c, "assets", "css");
  const css = co(dCss)
    ? readdirSync(dCss).filter((f) => f.endsWith(".css")).map((f) => doc(join(dCss, f))).join("\n") : "";
  const fileJs = quet(join(ROOT, c)).filter((f) => extname(f) === ".js");
  const js = fileJs.map((f) => doc(f)).join("\n");
  /* `jsNguoi` bỏ các file MÁY SINH. Dùng nó khi câu hỏi là "có người
     viết mã đọc thứ này không"; dùng `js` khi câu hỏi là "mã chạy
     trên trang có làm được việc này không". Trộn hai câu hỏi vào
     một chuỗi là chỗ tín hiệu 3 đã im lặng oan. */
  const MAY_SINH = /(van-hanh|tri-thuc|halls)\.js$|[\\/]v[\\/]/;
  const jsNguoi = fileJs.filter((f) => !MAY_SINH.test(f)).map((f) => doc(f)).join("\n");
  kho[c] = { html, css, js, jsNguoi };
}

const dat = [];

/* ══ TÍN HIỆU 1 · model chọn gì khi nó được tự do ══════
   Sổ tiến hoá ghi `daLam` — lời model tự khai. Khi phiếu đã đầy nó
   phải tự tìm việc, và việc nó tìm là thứ nó THẤY khi đọc trang.
   Cùng một lớp hiện lại ở nhiều cung, do nhiều lượt độc lập, thì
   không còn là ngẫu nhiên. */
const LOP = {
  "thứ bậc thông tin sai": ["thứ bậc", "tiêu đề", "cỡ chữ", "in hoa", "nhỏ hơn"],
  "trạng thái trống và điều khiển khuất": ["trống", "vô hình", "khuất", "ngăn kéo", "không thấy"],
  "con số không tự nói nghĩa": ["giải thích", "nghĩa là", "truy ngược", "đơn vị", "để làm gì"],
  "bàn phím và tiêu điểm": ["tiêu điểm", "bàn phím", "focus"]
};
if (co(join(ROOT, "factory", "tien-hoa.jsonl"))) {
  const nk = doc(join(ROOT, "factory", "tien-hoa.jsonl")).trim().split("\n")
    .map((l) => { try { return JSON.parse(l); } catch { return null; } })
    .filter((x) => x && x.daLam);
  const dem = {};
  for (const x of nk) {
    const van = String(x.daLam).toLowerCase();
    for (const [lop, tu] of Object.entries(LOP))
      if (tu.some((t) => van.includes(t))) (dem[lop] = dem[lop] || new Set()).add(x.cung);
  }
  for (const [lop, s] of Object.entries(dem)) {
    /* Một cung là chuyện riêng của cung ấy; HAI cung trở lên mới là
       một lớp. Ngưỡng này giữ cho tín hiệu khỏi thành tiếng ồn. */
    if (s.size < 2) continue;
    dat.push({
      tin: "model tự chọn", huong: lop, soCung: s.size,
      vi: `${s.size} cung khác nhau (${[...s].join(" ")}) trên ${nk.length} lượt có ghi việc — ` +
          "model tự tìm ra lớp này khi mọi thước đã đạt",
      kiemBang: "xem factory/tien-hoa.jsonl, trường daLam"
    });
  }
}

/* ══ TÍN HIỆU 2 · năng lực LỆCH giữa các cung ══════════
   Cùng một hệ, mười hai cung. Cung nào có một năng lực mà phần lớn
   cung khác không có thì đó là một đường ĐÃ CÓ NGƯỜI ĐI, khác hẳn
   một ý tưởng chưa ai thử.

   Đây là khuôn `bo-qua` tổng quát hoá: thêm một thước cho đường
   nhảy qua thanh bên thì 10 cung còn lại được vá trong 25 phút. */
const NANG_LUC = {
  "ngăn chi tiết để truy ngược con số": (k) => /role="dialog"|aria-modal/.test(k.html),
  "ô tìm kiếm": (k) => /type="search"/.test(k.html) || /placeholder="[^"]*[Tt]ìm/.test(k.html + k.js),
  "sao chép hoặc xuất dữ liệu": (k) => /clipboard|download|toBlob|csv/i.test(k.js),
  "kiểu in ra giấy": (k) => /@media print/.test(k.css)
};
for (const [ten, hoi] of Object.entries(NANG_LUC)) {
  const thieu = cung.filter((c) => { try { return !hoi(kho[c]); } catch { return true; } });
  const coBn = cung.length - thieu.length;
  /* Chỉ đề xuất khi VÀI cung đã có — đó là bằng chứng đường ấy đi
     được. Không cung nào có thì là ý tưởng, và ý tưởng không thuộc
     file này. */
  if (coBn >= 2 && thieu.length >= 3) {
    dat.push({
      tin: "lệch giữa các cung", huong: ten, soCung: thieu.length,
      vi: `${coBn}/${cung.length} cung đã có, ${thieu.length} cung chưa: ${thieu.join(" ")}`,
      kiemBang: "node scripts/huong.mjs --in"
    });
  }
}

/* ══ TÍN HIỆU 3 · xưởng sinh ra mà không trang nào đọc ══
   Một file sinh mỗi ngày mà không ai đọc là một lượt chạy đổi lấy
   số không. Loại lãng phí này không kêu: node vẫn `ok`, sổ vẫn
   xanh, thứ duy nhất thiếu là người xem. */
const RA_XUONG = ["bao-cao.md", "phieu.json", "kho-de-xuat.json", "huong.json"];

/* TRỪ `van-hanh.js` RA. Nó là bản chiếu của sổ đăng ký, nên MỌI
   đường khai trong `ra` của mọi node đều hiện ở đó THEO CẤU TẠO —
   kể cả đường chưa ai đọc nội dung bao giờ.

   Bản đầu không trừ, và nó im lặng đúng chỗ đáng kêu: ba file
   `bao-cao.md`, `phieu.json`, `kho-de-xuat.json` "được đọc" chỉ vì
   tên chúng nằm trong bảng chiếu. Kiểm thật thì trong cả 12 cung
   chỉ `sw.js` có `fetch`, và đó là ống service worker — không
   trang nào nạp nội dung ba file ấy.

   Bài học chung với thước `bo-qua` và `kiem-anh`: dò bằng chuỗi
   thô thì một cái TÊN bị tính là chính THỨ nó gọi tên. */
const moiTrang = cung.map((c) => kho[c].html + kho[c].jsNguoi).join("\n");
const khongAiDoc = RA_XUONG.filter((f) => co(join(ROOT, "factory", f)) && !moiTrang.includes(f));
if (khongAiDoc.length) {
  dat.push({
    tin: "sinh ra mà không ai đọc", huong: "đưa phân tích của xưởng lên site",
    soCung: khongAiDoc.length,
    vi: `${khongAiDoc.length} file xưởng sinh mà không trang nào đọc: ${khongAiDoc.join(" ")}`,
    kiemBang: "grep -rl bao-cao.md */assets/js/ */index.html"
  });
}

/* ══ TÍN HIỆU 4 · node chạy mà chưa từng đổi được gì ════
   `lucDoi` null nghĩa là chưa lượt nào ghi ra thay đổi. Có thể là
   node thừa, có thể là hỏng câm — hai chuyện khác hẳn nhau, và
   phân biệt được thì phải mở ra xem. Nên đây là câu HỎI, không
   phải lời kết tội: chính mục này đã báo nhầm một lần. */
if (co(join(ROOT, "factory", "state.json"))) {
  const st = JSON.parse(doc(join(ROOT, "factory", "state.json")));
  const im = Object.entries(st.node || {}).filter(([, v]) => v.luc && !v.lucDoi && v.ket === "ok");
  if (im.length) {
    dat.push({
      tin: "chạy mà chưa đổi gì", huong: "xem lại node không sinh ra thay đổi nào",
      soCung: im.length,
      vi: `${im.length} node: ${im.map(([m]) => m).join(" ")} — thừa, hay hỏng câm? Phải mở ra xem`,
      kiemBang: "node scripts/nha-may.mjs bang"
    });
  }
}

/* ══ XẾP HẠNG ═════════════════════════════════════════
   Theo SỐ CUNG chịu ảnh hưởng, không theo cảm giác quan trọng.
   Một thứ tự dở mà kiểm được còn hơn một thứ tự hay mà không ai
   bác được. */
dat.sort((a, b) => b.soCung - a.soCung);

console.log(`HƯỚNG — ${dat.length} đề xuất, xếp theo số cung chịu ảnh hưởng\n`);
dat.forEach((d, i) => {
  console.log(`${i + 1}. [${d.tin}] ${d.huong}`);
  console.log(`   ${d.vi}`);
  console.log(`   kiểm: ${d.kiemBang}\n`);
});
console.log("Đây là ĐỀ XUẤT, không phải quyết định. Nửa còn lại — cái này ĐỂ LÀM GÌ,");
console.log("gì quan trọng nhất — không suy ra được từ repo, và đó là phần của người.");

if (!CHI_IN) {
  mkdirSync(dirname(RA), { recursive: true });
  writeFileSync(RA, JSON.stringify({
    generatedAt: new Date().toISOString(),
    ghiChu: "SINH TỰ ĐỘNG bởi scripts/huong.mjs. ĐỀ XUẤT có bằng chứng, KHÔNG phải quyết định.",
    soCung: cung.length, deXuat: dat
  }, null, 2) + "\n", "utf8");
  console.log("\n→ factory/huong.json");
}
