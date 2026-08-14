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
