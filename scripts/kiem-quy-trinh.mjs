/* ═══════════════════════════════════════════════════════
   Kiểm CLAUDE.md có còn khớp với repo thật không.

   Chạy: npm run kiem

   CLAUDE.md nói nhiều thứ "phải khớp với nhau" — bảng cổng, danh
   sách file bot tự sinh, danh sách cung trong build-dist và trong
   paths của hai workflow. Không có gì bắt chúng khớp cả; chúng lệch
   dần, và LỆCH THÌ KHÔNG AI BÁO.

   Mỗi lỗi ở đây đều từng xảy ra thật, hoặc suýt xảy ra:
     · thiếu cung trong paths → push xong không workflow nào chạy,
       site vẫn bản cũ, không lỗi nào báo
     · thiếu cung trong bảng cổng → phiên sau đoán bừa, tranh cổng
     · danh sách file bot tự sinh thiếu → phiên khác sửa tay đúng
       file bot ghi, conflict lúc gộp
     · cung mới chưa được cung cũ trỏ sang → dựng xong mà không có
       đường vào

   Mã thoát khác 0 nếu có lỗi, để cắm vào CI sau này nếu muốn.
   ═══════════════════════════════════════════════════════ */

import { readFile, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { NGUON, NGAY_TOI_DA, tuoi } from "./tuoi-du-lieu.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const doc = (p) => readFile(join(ROOT, p), "utf8");

const loi = [];
const canhBao = [];
const bao = (m) => loi.push(m);
const nhac = (m) => canhBao.push(m);

/* ── cung thật trên đĩa ───────────────────────────────
   Một thư mục là cung khi và chỉ khi nó có index.html riêng. */
const BO_QUA = new Set(["assets", "scripts", "dist", "node_modules", ".git", ".github", ".claude"]);
const cung = [];
for (const ten of await readdir(ROOT)) {
  if (BO_QUA.has(ten) || ten.startsWith(".")) continue;
  if (existsSync(join(ROOT, ten, "index.html"))) cung.push(ten);
}
cung.sort();

const CLAUDE = await doc("CLAUDE.md");

/* ── 0. bản CLAUDE.md tại chỗ có cũ hơn origin/main không ──
   Worktree nhánh từ origin/main LÚC TẠO rồi đứng yên. Phiên mở từ
   worktree cũ đang đọc luật của tuần trước mà không biết.

   Bảy phép kiểm dưới đây so tài liệu CỤC BỘ với repo CỤC BỘ, nên
   worktree cũ có cả hai đều cũ mà khớp nhau sẽ in ✓ — xanh trong khi
   phiên đó làm theo luật đã bị thay. Đúng kiểu "bước xanh vĩnh viễn"
   mà CLAUDE.md cảnh báo ở mục Hoàng Thành. Đã xảy ra thật: một
   worktree tạo lúc repo còn năm cung vẫn báo ✓ sau khi main lên sáu.

   Đếm commit chạm CLAUDE.md có ở origin/main mà KHÔNG có ở đây.
   Không so nội dung hai bản: nhánh tại chỗ có thể đang sửa chính
   CLAUDE.md, khác nội dung mà là mới hơn chứ không cũ — báo nó lỗi
   thời thì chính người đang vá lại bị chặn.

   Đọc ref có sẵn trên đĩa, KHÔNG tự ra mạng: `npm run kiem` phải chạy
   được khi mất mạng. Muốn số liệu tươi thì `git fetch -q` trước, đúng
   thứ tự trong mục "Trước khi bắt đầu".

   Đây là lớp thứ hai, không phải lớp duy nhất: hook pre-commit nhắc
   phiên đang chạy dở mà không nhớ chạy lệnh này. Hook chỉ nhắc và luôn
   thoát 0; chỗ này thoát 1 để chặn được và cắm CI được. */
if (!process.argv.includes("--offline")) {
  const git = (...a) =>
    execFileSync("git", a, { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
  try {
    const so = Number(git("rev-list", "--count", "HEAD..origin/main", "--", "CLAUDE.md"));
    if (so > 0) {
      bao(
        `CLAUDE.md ở đây CŨ HƠN origin/main ${so} commit — bạn đang theo luật lỗi thời.\n` +
        "        Xem đã đổi gì: git diff HEAD origin/main -- CLAUDE.md\n" +
        "        Bắt kịp      : git merge --ff-only origin/main\n" +
        "        Bỏ qua       : npm run kiem -- --offline"
      );
    }
  } catch {
    nhac("Không so được CLAUDE.md với origin/main (chưa `git fetch`, hoặc không có remote).");
  }
}

/* ── 1. danh sách cung ở đầu CLAUDE.md ────────────── */
for (const c of cung) {
  if (!new RegExp("(^|\\s)" + c + "/", "m").test(CLAUDE)) {
    bao(`CLAUDE.md chưa nhắc cung "${c}/" ở danh sách đầu file`);
  }
}

/* ── 2. bảng cổng ─────────────────────────────────── */
const cong = new Map();
for (const m of CLAUDE.matchAll(/^ {4}(\d{4}) {2}(\S+)/gm)) {
  const [, so, ten] = m;
  if (cong.has(so)) bao(`Bảng cổng: ${so} bị cấp cho cả "${cong.get(so)}" và "${ten}"`);
  cong.set(so, ten);
}
const tenCong = new Set([...cong.values()]);
for (const c of cung) {
  if (!tenCong.has(c)) bao(`Bảng cổng thiếu cung "${c}" — phiên sau sẽ đoán bừa và tranh cổng`);
}
for (const [so] of cong) {
  const n = Number(so);
  if (n < 5173 || n > 5199) nhac(`Cổng ${so} nằm ngoài dải 5173–5199 dành cho repo này`);
}

/* ── 3. danh sách file bot tự sinh khớp `git add` ─── */
/* CLAUDE.md liệt kê đường dẫn bot ghi đè. Nếu workflow add thêm
   đường dẫn mà tài liệu không ghi, phiên khác sẽ sửa tay đúng chỗ
   đó và chắc chắn conflict lúc gộp. */
for (const [wf, ten] of [
  [".github/workflows/refresh-data.yml", "refresh-data.yml"],
  [".github/workflows/scan-observatory.yml", "scan-observatory.yml"]
]) {
  if (!existsSync(join(ROOT, wf))) { bao(`Thiếu workflow ${wf}`); continue; }
  const t = await doc(wf);
  const khoi = t.match(/git add ([\s\S]*?)\n\s*(?:if |git )/);
  if (!khoi) { nhac(`${ten}: không đọc được khối "git add" để đối chiếu`); continue; }
  const duong = khoi[1]
    .split(/\\?\n/).map((x) => x.trim()).filter(Boolean)
    .filter((x) => !x.startsWith("#"));
  for (const d of duong) {
    if (!CLAUDE.includes(d)) {
      bao(`${ten} ghi "${d}" nhưng CLAUDE.md không liệt kê — mục "File do workflow tự sinh" bị thiếu`);
    }
  }
}

/* ── 4. build-dist HALLS ──────────────────────────── */
const bd = await doc("scripts/build-dist.mjs");
const mHalls = bd.match(/const HALLS = \[([^\]]*)\]/);
if (!mHalls) bao("build-dist.mjs: không tìm thấy mảng HALLS");
else {
  const halls = [...mHalls[1].matchAll(/"([^"]+)"/g)].map((m) => m[1]);
  for (const c of cung) if (!halls.includes(c)) bao(`build-dist.mjs HALLS thiếu "${c}" — cung này sẽ không vào dist/`);
  for (const h of halls) if (!cung.includes(h)) bao(`build-dist.mjs HALLS có "${h}" nhưng trên đĩa không có thư mục đó`);
}

/* ── 5. paths của hai workflow deploy ─────────────── */
for (const wf of [".github/workflows/deploy-pages.yml", ".github/workflows/deploy-ipfs.yml"]) {
  if (!existsSync(join(ROOT, wf))) { bao(`Thiếu ${wf}`); continue; }
  const t = await doc(wf);
  for (const c of cung) {
    if (!t.includes(`"${c}/**"`)) {
      bao(`${wf.split("/").pop()}: paths thiếu "${c}/**" — sửa cung đó xong sẽ KHÔNG deploy, và không có lỗi nào báo`);
    }
  }
}

/* ── 6. sw.js gốc để yên phạm vi từng cung ────────── */
const sw = await doc("sw.js");
for (const c of cung) {
  if (!sw.includes(`/${c}/`)) {
    bao(`sw.js (Cổng Thành) thiếu dòng bỏ qua "/${c}/" — service worker cổng sẽ tranh phục vụ file của cung đó`);
  }
}

/* ── 7. mỗi cung trỏ sang mọi cung khác ───────────── */
for (const c of cung) {
  const f = join(c, "assets", "js", "halls.js");
  if (!existsSync(join(ROOT, f))) { nhac(`${c}: chưa có assets/js/halls.js (cung mới chưa dựng xong?)`); continue; }
  const t = await doc(f);
  for (const k of cung) {
    if (k === c) continue;
    if (!t.includes(`../${k}/`)) bao(`${c}/assets/js/halls.js chưa có lối sang "${k}"`);
  }
}

/* ── 8. thẻ ở Cổng Thành ──────────────────────────── */
const goc = await doc("index.html");
for (const c of cung) {
  if (!goc.includes(`"${c}/"`)) bao(`index.html (Cổng Thành) chưa có thẻ dẫn vào "${c}"`);
}

/* ── 8b. script sinh dữ liệu ghi ra ngoài phạm vi git add ──
   Phép 3 soi chiều "add gì thì phải khai trong tài liệu". Chiều
   ngược lại mới là chiều nguy hiểm: **script GHI vào đâu mà add
   không phủ** thì file sinh ra rồi mất, và không lỗi nào báo.

   Đã dính thật, hai chỗ cùng lúc: build-l2beat.mjs và
   build-congbo.mjs tải logo về `assets/logos/`, còn `git add` chỉ
   phủ `assets/js/`. Hệ quả: `logos.js` được commit và trỏ tới ảnh
   chưa bao giờ được commit. Chưa nổ vì lần thêm logo gần nhất làm
   bằng tay — sẽ nổ đúng lần L2BEAT thêm một dự án mới.

   Đọc mã bằng regex nên chỉ bắt được khuôn `const X = join(ROOT, …)`
   rồi `writeFile(join(X, …))`. Khuôn khác thì bỏ qua chứ không đoán:
   phép kiểm báo nhầm còn tệ hơn phép kiểm thiếu. */
const NGUON_GHI = [
  ["build-live.mjs", ".github/workflows/refresh-data.yml"],
  ["build-l2beat.mjs", ".github/workflows/refresh-data.yml"],
  ["build-congbo.mjs", ".github/workflows/refresh-data.yml"],
  ["build-tangthu.mjs", ".github/workflows/refresh-data.yml"],
  ["pin-snapshot.mjs", ".github/workflows/refresh-data.yml"],
  ["build-scan.mjs", ".github/workflows/scan-observatory.yml"]
];

async function phamViAdd(wf) {
  if (!existsSync(join(ROOT, wf))) return null;
  const t = await doc(wf);
  const m = t.match(/git add ([\s\S]*?)\n\s*(?:if |git )/);
  if (!m) return null;
  return m[1].split(/\\?\n/).map((x) => x.trim())
    .filter(Boolean).filter((x) => !x.startsWith("#"));
}

const camAdd = {};
for (const [, wf] of NGUON_GHI) if (!(wf in camAdd)) camAdd[wf] = await phamViAdd(wf);

for (const [tep, wf] of NGUON_GHI) {
  if (!existsSync(join(ROOT, "scripts", tep))) continue;
  const pv = camAdd[wf];
  if (!pv) { nhac(`${wf}: không đọc được khối "git add" để soi đường ghi`); continue; }

  const s = await doc(join("scripts", tep));
  const bien = {};
  for (const m of s.matchAll(/const (\w+) = join\(ROOT,\s*([^)]*)\)/g)) {
    bien[m[1]] = m[2].split(",").map((x) => x.trim().replace(/^["']|["']$/g, "")).join("/");
  }

  const duong = new Set();
  // writeFile(join(BIEN, "a", "b")) — phần nào là biến thì cắt, giữ tiền tố chắc chắn
  for (const m of s.matchAll(/writeFile\(\s*join\((\w+)\s*,\s*([^)]*)\)/g)) {
    const goc = bien[m[1]];
    if (!goc) continue;
    const phan = [];
    for (const p of m[2].split(",").map((x) => x.trim())) {
      if (!/^["']/.test(p)) break;                 // gặp biến thì dừng
      phan.push(p.replace(/^["']|["']$/g, ""));
    }
    duong.add(phan.length ? goc + "/" + phan.join("/") : goc + "/");
  }
  // writeFile(BIEN, …)
  for (const m of s.matchAll(/writeFile\(\s*(\w+)\s*,/g)) {
    if (bien[m[1]]) duong.add(bien[m[1]]);
  }

  for (const d of duong) {
    const phu = pv.some((p) => {
      const pp = p.replace(/\/$/, "");
      return d === p || d === pp || d.startsWith(pp + "/");
    });
    if (!phu) {
      bao(`scripts/${tep} ghi vào "${d}" nhưng ${wf.split("/").pop()} không add đường đó\n` +
        "        → file sinh ra rồi mất sau mỗi lượt bot, và không lỗi nào báo.");
    }
  }
}

/* ── 9. bot còn sống không ────────────────────────────
   Bảy phép trên soi repo có tự khớp với tài liệu không. Không
   phép nào soi được thứ đã xảy ra thật ngày 13–14/08/2026:
   repo khớp hoàn hảo, tài liệu đúng từng chữ, mà đường ống bot
   chết hơn một ngày — bước đóng dấu Pinata ngã kéo cả job, rồi
   job đụng trần 10 phút. Bước commit chưa lần nào chạy tới,
   site đứng im, và KHÔNG CÓ LỖI NÀO NỔI LÊN.

   build-dist.mjs có in "⚠" nhưng nó không thoát khác 0, và
   `npm run dist` không nằm trong danh sách lệnh đầu phiên. Nên
   phép kiểm có mà không tới được mắt ai.

   Nhắc chứ không báo lỗi: bot chết không phải lỗi của phiên
   đang mở, và không được chặn họ làm cung của mình. Nhưng nó
   in ở đầu mỗi phiên, nên không thể chết âm thầm cả ngày nữa. */
for (const n of NGUON) {
  /* Nguồn đang tắt có chủ ý: nhắc một dòng bình thản để còn nhớ mà
     bật lại, chứ đừng báo "có gì đó gãy" cho thứ không gãy. */
  if (n.tamDung) { nhac(`${n.nhan}: TẠM DỪNG — ${n.tamDung}`); continue; }
  const t = await tuoi(ROOT, n.duong);
  if (!t.co) {
    if (n.botSinh) nhac(`${n.nhan}: chưa sinh lần nào, hoặc thiếu dấu thời gian (${n.duong})`);
    continue;
  }
  if (n.botSinh && t.ngay > NGAY_TOI_DA) {
    nhac(
      `${n.nhan}: sinh cách đây ${t.ngay.toFixed(1)} ngày — bot chạy 4 lượt/ngày, quá ${NGAY_TOI_DA} ngày là có gì đó gãy.\n` +
      "        Xem: https://github.com/sunswagz/blockchainworld/actions"
    );
  }
}

/* ── 9. CACHE_VERSION có theo kịp file trong SHELL không ──
   Mỗi sw.js liệt kê một mảng SHELL và phục vụ chúng theo lối
   CACHE-TRƯỚC. Sửa một file trong SHELL mà không nâng
   CACHE_VERSION thì máy đã cài app cứ dùng bản cũ trong cache.

   Hỏng kiểu này khó lần ra nhất trong repo: không có lỗi mạng,
   không có 404, HTML mới ghép CSS cũ nên chỉ thấy GIAO DIỆN VỠ.
   Đã dính thật: xếp lại thứ bậc Cổng Thành, đổi portal.css,
   quên nâng v4 → v5, và icon SVG mất luật cỡ nên phình kín màn hình.

   Cách kiểm: so commit cuối của sw.js với commit cuối của từng
   file nó khai trong SHELL. */
function commitCuoi(p) {
  try {
    return execFileSync("git", ["log", "-1", "--format=%ct", "--", p],
      { cwd: ROOT, encoding: "utf8" }).trim();
  } catch { return ""; }
}

for (const c of ["."].concat(cung)) {
  const swP = c === "." ? "sw.js" : `${c}/sw.js`;
  if (!existsSync(join(ROOT, swP))) continue;
  const sw = await doc(swP);
  if (!/CACHE_VERSION\s*=/.test(sw)) continue;

  const tSw = Number(commitCuoi(swP) || 0);
  if (!tSw) continue;                       // chưa commit lần nào — bỏ qua

  /* File được phục vụ MẠNG-TRƯỚC thì không cần nâng version: service
     worker đi lấy bản mới mỗi lần, cache chỉ là lưới đỡ lúc mất mạng.
     Bốn cung lấy số từ API để data.js ở nhánh đó và bot ghi 4 lượt/ngày
     — bắt nâng version mỗi lượt là biến phép kiểm thành tiếng ồn.

     Nhận diện bằng các chuỗi trong `url.pathname.indexOf("…")` của chính
     sw.js đó. (sw.js gốc cũng dùng khuôn này để BỎ QUA đường của từng
     cung, nhưng SHELL của nó không chứa đường nào như vậy nên không có
     chuyện miễn trừ nhầm.) */
  const mangTruoc = [...sw.matchAll(/indexOf\(\s*"([^"]+)"\s*\)/g)].map((m) => m[1]);
  const shell = [...sw.matchAll(/^\s*"\.\/([^"]+)"/gm)].map((m) => m[1]);
  const tre = [];
  for (const f of shell) {
    if (mangTruoc.some((p) => ("/" + f).indexOf(p) !== -1)) continue;
    const p = c === "." ? f : `${c}/${f}`;
    if (!existsSync(join(ROOT, p))) continue;
    const t = Number(commitCuoi(p) || 0);
    if (t > tSw) tre.push(f);
  }
  if (tre.length) {
    bao(`${swP}: CACHE_VERSION chưa nâng, nhưng ${tre.length} file trong SHELL ` +
      `mới hơn — ${tre.slice(0, 4).join(", ")}${tre.length > 4 ? "…" : ""}\n` +
      `        Máy đã cài app sẽ nhận bản CŨ của những file đó (giao diện vỡ, không báo lỗi).`);
  }
}

/* ── kết quả ──────────────────────────────────────── */
console.log(`Cung tìm thấy trên đĩa: ${cung.length} — ${cung.join(", ")}\n`);

if (canhBao.length) {
  console.log("Nhắc:");
  for (const m of canhBao) console.log("  · " + m);
  console.log();
}

if (!loi.length) {
  console.log("✓ CLAUDE.md khớp với repo. Không có lệch nào.");
  process.exit(0);
}

console.log(`✗ ${loi.length} chỗ lệch:\n`);
for (const m of loi) console.log("  ✗ " + m);
console.log("\nSửa xong nhớ chạy lại. Mục nào thuộc CLAUDE.md thì xem phần");
console.log('"Khi phát hiện lỗi trong chính file này" để biết cách vá.');
process.exit(1);
