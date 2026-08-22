/* ═══════════════════════════════════════════════════════
   Sao lưu những thứ GitHub KHÔNG giữ.  Chạy: npm run sao-luu

   `git clone` mang được ~95% dự án. Phần còn lại nằm ngoài git
   và không tái tạo được:

     *-runtime/data/     băng ghi, chay-nen.py tích 24/7 theo nhịp
                         30 giây. Vi cấu trúc thị trường quá khứ
                         KHÔNG tải lại được. README Thị Bạc Ty:
                         "Thiếu băng thì mọi lần vặn ngưỡng đều là
                         đổi số cho vui."
     *-runtime/.env      khoá API và khoá ví — tiền thật
     skills/traders/     kỹ năng trader đã học
     ~/.claude/          hook, skill riêng, agent, lệnh, settings
     ~/.claude.json      danh sách project, cấu hình MCP

   Ba thứ đầu chỉ tồn tại trên MỘT máy. Máy hỏng là mất, và mất
   trong im lặng — không lỗi nào báo, chỉ là lần sau vặn ngưỡng
   thì không còn gì để hậu kiểm.

   ── CHỖ NGUY HIỂM NHẤT CỦA SCRIPT NÀY ────────────────
   Gói sinh ra CHỨA KHOÁ VÍ. Repo này là PUBLIC, và CLAUDE.md
   đã cảnh báo `git add -A` nuốt trọn thứ chưa theo dõi. Gói
   nằm trong cây làm việc + một lần `git add -A` = khoá ví lên
   GitHub công khai, không rút lại được.
   Nên script TỪ CHỐI ghi vào bất kỳ kho git nào, kể cả kho khác.
   ═══════════════════════════════════════════════════════ */

import { readdir, mkdir, copyFile, stat, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir, hostname } from "node:os";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const NHA = homedir();

const args = process.argv.slice(2);
const co = (t) => args.includes(t);
const giaTri = (t) => { const i = args.indexOf(t); return i < 0 ? null : args[i + 1]; };

const THU = co("--thu");
const DU = co("--du");
const DE = co("--de");
const PHUC_HOI = giaTri("--phuc-hoi");

if (co("--giup") || co("-h")) {
  console.log(`
  node scripts/sao-luu.mjs                 sao lưu vào ../sao-luu-blockchainworld/<ngày>
  node scripts/sao-luu.mjs --thu           chỉ liệt kê và đo cỡ, KHÔNG chép
  node scripts/sao-luu.mjs --ra <đường>    chọn chỗ chứa khác
  node scripts/sao-luu.mjs --du            gói cả ~/.claude/projects (lịch sử hội thoại, rất nặng)
  node scripts/sao-luu.mjs --phuc-hoi <gói>   chép ngược từ gói về máy này
  node scripts/sao-luu.mjs --phuc-hoi <gói> --de   ...và ĐÈ file đã có
`);
  process.exit(0);
}

/* ── Những thứ trong ~/.claude KHÔNG gói ──────────────
   projects/ là bản ghi từng lượt hội thoại — hàng trăm MB và
   dựng lại được bằng cách... không cần dựng lại.
   .credentials.json thì cố ý bỏ: chép khoá đăng nhập sang máy
   mới rủi ro hơn hẳn việc gõ `claude` rồi /login một lần. */
const BO_QUA_CLAUDE = new Set([
  "projects", ".credentials.json", "todos", "statsig",
  "shell-snapshots", "file-history", "ide", "logs", "downloads",
]);
if (DU) BO_QUA_CLAUDE.delete("projects");

/* ── Băng ghi có thể KHÔNG nằm trong thư mục runtime ──
   Cả ba config.py đều đọc biến môi trường trước:
     DATA_DIR = Path(os.environ.get("TBT_DATA_DIR") or (ROOT / "data"))
   Đoán bừa "runtime/data" là gói nhầm thư mục rỗng rồi tưởng
   đã sao lưu xong — đúng kiểu hỏng im lặng mà script này sinh
   ra để chặn. */
const bang = (thuMuc, bien) =>
  process.env[bien] ? resolve(process.env[bien]) : join(ROOT, thuMuc, "data");

const MUC = [
  { ten: "runtime/tu-cam-thanh/data",     tu: bang("tu-cam-thanh-runtime", "TCT_DATA_DIR"),
    ve: bang("tu-cam-thanh-runtime", "TCT_DATA_DIR"),     mo: "băng ghi Tử Cấm Thành" },
  { ten: "runtime/kham-thien-giam/data",  tu: bang("kham-thien-giam-runtime", "KTG_DATA_DIR"),
    ve: bang("kham-thien-giam-runtime", "KTG_DATA_DIR"),  mo: "băng ghi Khâm Thiên Giám" },
  { ten: "runtime/thi-bac-ty/data",       tu: bang("thi-bac-ty-runtime", "TBT_DATA_DIR"),
    ve: bang("thi-bac-ty-runtime", "TBT_DATA_DIR"),       mo: "băng ghi Thị Bạc Ty" },

  { ten: "runtime/tu-cam-thanh/.env",     tu: join(ROOT, "tu-cam-thanh-runtime", ".env"),
    ve: join(ROOT, "tu-cam-thanh-runtime", ".env"),       mo: "khoá Tử Cấm Thành", khoa: true },
  { ten: "runtime/kham-thien-giam/.env",  tu: join(ROOT, "kham-thien-giam-runtime", ".env"),
    ve: join(ROOT, "kham-thien-giam-runtime", ".env"),    mo: "khoá Khâm Thiên Giám (có khoá ví)", khoa: true },
  { ten: "runtime/thi-bac-ty/.env",       tu: join(ROOT, "thi-bac-ty-runtime", ".env"),
    ve: join(ROOT, "thi-bac-ty-runtime", ".env"),         mo: "khoá Thị Bạc Ty", khoa: true },

  { ten: "runtime/tu-cam-thanh/skills-traders", tu: join(ROOT, "tu-cam-thanh-runtime", "skills", "traders"),
    ve: join(ROOT, "tu-cam-thanh-runtime", "skills", "traders"), mo: "kỹ năng trader đã học" },

  { ten: "claude/thu-muc", tu: join(NHA, ".claude"), ve: join(NHA, ".claude"),
    bo: BO_QUA_CLAUDE, mo: "hook, skill riêng, agent, lệnh, settings" },
  { ten: "claude/claude.json", tu: join(NHA, ".claude.json"), ve: join(NHA, ".claude.json"),
    mo: "danh sách project, cấu hình MCP", khoa: true },
];

/* ── Chép đệ quy bằng tay ─────────────────────────────
   fs.cp có sẵn nhưng còn gắn nhãn thử nghiệm ở Node 18, mà
   package.json chỉ đòi >=18. Tự đi cây thì không phụ thuộc
   phiên bản, và đây cũng là lối repo đang theo: "ít phụ thuộc,
   đừng thêm thứ có thể cài hỏng". */
async function chep(tu, ve, bo, dem = { tep: 0, cd: 0 }) {
  const t = await stat(tu);
  if (t.isDirectory()) {
    await mkdir(ve, { recursive: true });
    for (const ten of await readdir(tu)) {
      if (bo?.has(ten)) continue;
      await chep(join(tu, ten), join(ve, ten), null, dem);
    }
  } else {
    await mkdir(dirname(ve), { recursive: true });
    await copyFile(tu, ve);
    dem.tep++; dem.cd += t.size;
  }
  return dem;
}

async function do_(p, bo, dem = { tep: 0, cd: 0 }) {
  const t = await stat(p);
  if (t.isDirectory()) {
    for (const ten of await readdir(p)) {
      if (bo?.has(ten)) continue;
      await do_(join(p, ten), null, dem);
    }
  } else { dem.tep++; dem.cd += t.size; }
  return dem;
}

const cỡ = (n) =>
  n < 1024 ? n + " B"
  : n < 1048576 ? (n / 1024).toFixed(1) + " KB"
  : n < 1073741824 ? (n / 1048576).toFixed(1) + " MB"
  : (n / 1073741824).toFixed(2) + " GB";

/* ── Chỗ chứa có nằm trong kho git nào không ──────────
   Đi ngược lên tận gốc ổ đĩa. Chặn cả kho KHÁC chứ không chỉ
   kho này: gói có khoá ví, lọt vào kho nào cũng là hỏng. */
function trongKhoGit(p) {
  let d = resolve(p);
  for (;;) {
    if (existsSync(join(d, ".git"))) return d;
    const cha = dirname(d);
    if (cha === d) return null;
    d = cha;
  }
}

/* ═══════════════ PHỤC HỒI ═══════════════ */
if (PHUC_HOI) {
  const goi = resolve(PHUC_HOI);
  if (!existsSync(goi)) {
    console.error(`Không thấy gói: ${goi}`);
    process.exit(1);
  }
  console.log(`Phục hồi từ: ${goi}\n`);
  let cham = 0;
  for (const m of MUC) {
    const tu = join(goi, m.ten);
    if (!existsSync(tu)) { console.log(`  –  ${m.ten}  (không có trong gói)`); continue; }
    if (existsSync(m.ve) && !DE) {
      console.log(`  ⚠  ${m.ten}\n     đã có ở ${m.ve} — bỏ qua. Muốn đè thì thêm --de`);
      cham++; continue;
    }
    const d = await chep(tu, m.ve, null);
    console.log(`  ✓  ${m.ten}  →  ${m.ve}   (${d.tep} tệp, ${cỡ(d.cd)})`);
  }
  console.log(`\nXong.${cham ? `  ${cham} mục bị bỏ qua vì đã có sẵn.` : ""}`);
  console.log("Kiểm lại:  npm run kiem   và   cd thi-bac-ty-runtime && python scripts/selftest.py");
  process.exit(0);
}

/* ═══════════════ SAO LƯU ═══════════════ */
const gio = new Date().toISOString().slice(0, 16).replace("T", "_").replace(":", "h");
const macDinh = join(resolve(ROOT, ".."), "sao-luu-blockchainworld", gio);
const DICH = resolve(giaTri("--ra") || macDinh);

if (!THU) {
  const kho = trongKhoGit(DICH);
  if (kho) {
    console.error(
      `TỪ CHỐI: chỗ chứa nằm trong một kho git.\n` +
      `  chỗ chứa : ${DICH}\n` +
      `  kho git  : ${kho}\n\n` +
      `Gói này chứa khoá ví và khoá API. Một lần \`git add -A\` là chúng lên\n` +
      `remote, và nếu remote công khai thì không rút lại được.\n` +
      `Chọn chỗ ngoài mọi kho git:  --ra D:/sao-luu-blockchainworld`);
    process.exit(1);
  }
}

console.log(`Kho    : ${ROOT}`);
console.log(THU ? "Chế độ : THỬ — không chép gì\n" : `Chỗ chứa: ${DICH}\n`);

const so = [];
let tongTep = 0, tongCd = 0, thieu = 0;

for (const m of MUC) {
  if (!existsSync(m.tu)) {
    console.log(`  –  ${m.ten.padEnd(34)} không có trên máy này  (${m.mo})`);
    thieu++;
    continue;
  }
  const d = THU ? await do_(m.tu, m.bo) : await chep(m.tu, join(DICH, m.ten), m.bo);
  tongTep += d.tep; tongCd += d.cd;
  so.push({ ...m, tep: d.tep, cd: d.cd });
  console.log(`  ${THU ? "·" : "✓"}  ${m.ten.padEnd(34)} ${String(d.tep).padStart(6)} tệp  ${cỡ(d.cd).padStart(10)}   ${m.mo}`);
}

console.log(`\n  tổng: ${tongTep} tệp, ${cỡ(tongCd)}` + (thieu ? `   (${thieu} mục không có trên máy này)` : ""));

/* ── Thứ KHÔNG nằm trong gói này ──────────────────────
   Commit chưa push cũng mất cùng máy, mà gói không cứu được —
   chúng nằm trong .git của từng worktree. Nên báo, đừng im. */
const git = (...a) => {
  try { return execFileSync("git", a, { cwd: ROOT, encoding: "utf8" }).trim(); }
  catch { return ""; }
};
const chuaPush = git("log", "--branches", "--not", "--remotes", "--oneline");
const chuaCommit = git("status", "--short");

if (chuaPush || chuaCommit) {
  console.log("\n  ⚠  GÓI NÀY KHÔNG CHỨA:");
  if (chuaPush)
    console.log(`     ${chuaPush.split("\n").length} commit chưa push:\n` +
      chuaPush.split("\n").slice(0, 5).map((l) => "        " + l).join("\n"));
  if (chuaCommit)
    console.log(`     ${chuaCommit.split("\n").length} file chưa commit trong cây này`);
  console.log("     → push hết trước khi rời máy, gói này không cứu được chúng.");
}

const wt = git("worktree", "list");
if (wt.split("\n").length > 1)
  console.log(`\n  ⚠  Máy này có ${wt.split("\n").length} worktree — kiểm TỪNG cái:\n` +
    wt.split("\n").map((l) => "        " + l).join("\n"));

if (THU) {
  console.log("\nĐây mới là bản thử. Chép thật:  npm run sao-luu");
  process.exit(0);
}

/* ── Sổ tay đi kèm gói ────────────────────────────────
   Băng ghi chỉ có nghĩa khi biết nó ghép với bản code nào —
   ngưỡng đổi thì băng cũ vẫn đọc được nhưng kết luận thì không
   so được. Nên đóng dấu commit vào gói. */
const soTay = `# Gói sao lưu blockchainworld

    ngày   : ${new Date().toISOString()}
    máy    : ${hostname()}
    kho    : ${ROOT}
    commit : ${git("rev-parse", "HEAD") || "(không đọc được)"}
    nhánh  : ${git("rev-parse", "--abbrev-ref", "HEAD") || "(không đọc được)"}

## ⚠ GÓI NÀY CHỨA KHOÁ

\`.env\` của ba runtime có khoá API và **khoá ví Polymarket — tiền thật**.
\`claude.json\` có cấu hình MCP, có thể kèm token.

- Đừng để gói này vào bất kỳ thư mục nào có \`.git\`
- Đừng gửi qua email, chat, hay cloud drive không mã hoá
- Ổ ngoài, hoặc file nén có mật khẩu

## Trong gói

${so.map((m) => `- \`${m.ten}\` — ${m.mo}  (${m.tep} tệp, ${cỡ(m.cd)})`).join("\n")}

## Phục hồi trên máy mới

    git clone https://github.com/sunswagz/blockchainworld
    cd blockchainworld
    node scripts/sao-luu.mjs --phuc-hoi <đường-dẫn-gói-này>

Không cần \`npm install\` — repo không có phụ thuộc npm nào.
Cần Node ≥ 18. Ba runtime cần Python và \`pip install -r requirements.txt\`.

Kiểm sau khi phục hồi:

    npm run kiem
    cd thi-bac-ty-runtime && python scripts/selftest.py

## Gói này KHÔNG chứa

- Commit chưa push — push trước khi rời máy
- \`~/.claude/projects/\` (lịch sử hội thoại)${DU ? " — LẦN NÀY CÓ, vì chạy với --du" : " — dùng --du nếu muốn"}
- \`~/.claude/.credentials.json\` — cố ý; máy mới chạy \`claude\` rồi \`/login\`
- Nguồn Hoàng Thành ngoài repo — chép tay thư mục \`sunswagz-hub\`
- \`node_modules/\`, \`.venv/\`, \`dist/\` — dựng lại được
`;

await writeFile(join(DICH, "SO-TAY.md"), soTay);

console.log(`\nXong: ${DICH}`);
console.log(`Đọc SO-TAY.md trong gói để biết cách phục hồi.`);
console.log(`\n⚠  Gói chứa khoá ví. Ổ ngoài hoặc file nén có mật khẩu — đừng cloud drive trần.`);
