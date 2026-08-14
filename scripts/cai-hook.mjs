/* ═══════════════════════════════════════════════════════
   Cài hook nhắc dùng chung.  Chạy: npm run hook

   Mọi worktree dùng CHUNG một thư mục .git/hooks (worktree
   chỉ có file .git trỏ về .git/worktrees/<tên>, còn hooks thì
   không tách). Nên hook cài một lần là mọi phiên đều chạm —
   kể cả phiên đang mở dở, vốn không có cách nào nhắn tới.

   Không đè hook có sẵn: nếu đã có pre-commit khác thì dừng và
   báo, để người dùng tự quyết.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, chmod, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const NGUON = join(ROOT, "scripts", "hooks", "pre-commit");

const git = (...a) =>
  execFileSync("git", a, { cwd: ROOT, encoding: "utf8" }).trim();

/* Thư mục hooks thật — hỏi git, đừng đoán ".git/hooks": kho có
   thể đặt core.hooksPath sang chỗ khác, đoán là cài vào chỗ
   không ai chạy rồi tưởng đã xong. */
let dich;
try {
  dich = git("rev-parse", "--git-path", "hooks");
} catch {
  console.error("Không phải kho git — không cài được hook.");
  process.exit(1);
}
if (!dich.match(/^[A-Za-z]:|^\//)) dich = join(ROOT, dich);

const tep = join(dich, "pre-commit");
const moi = await readFile(NGUON, "utf8");

if (existsSync(tep)) {
  const cu = await readFile(tep, "utf8");
  if (cu === moi) {
    console.log("Hook đã cài sẵn và đúng bản mới nhất:\n  " + tep);
    process.exit(0);
  }
  if (!cu.includes("nhắc trước khi commit")) {
    console.error("Đã có pre-commit KHÁC ở:\n  " + tep);
    console.error("Không đè. Xem file đó rồi tự quyết có gộp hay không.");
    process.exit(1);
  }
}

await mkdir(dich, { recursive: true });
await writeFile(tep, moi, "utf8");
try { await chmod(tep, 0o755); } catch { /* Windows không cần */ }

console.log("✓ Đã cài hook nhắc:\n  " + tep);
console.log("\nDùng chung cho mọi worktree:");
for (const d of git("worktree", "list").split("\n")) console.log("  " + d);
console.log("\nHook chỉ NHẮC, không chặn commit. Gỡ:  rm \"" + tep + "\"");
