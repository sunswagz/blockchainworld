/* ═══════════════════════════════════════════════════════
   Đẩy dist/ lên IPFS qua Pinata.

   Chạy: npm run pin
   Cần:  PINATA_JWT   (bắt buộc)
         PINATA_GATEWAY  (tuỳ chọn, ví dụ mycdn.mypinata.cloud)

   Dùng fetch + FormData có sẵn của Node 20 — không cài gói nào,
   không dùng action của bên thứ ba. Toàn bộ chỗ chạm vào token
   nằm gọn trong file này, đọc hết trong một phút.
   ═══════════════════════════════════════════════════════ */

import { readFile, readdir, stat, appendFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DIST = join(ROOT, "dist");
const FOLDER = "kinh-thanh";

const JWT = process.env.PINATA_JWT;
if (!JWT) {
  console.error("Thiếu PINATA_JWT.\n" +
    "  · Cục bộ:  $env:PINATA_JWT=\"...\"; npm run pin\n" +
    "  · CI:      Settings → Secrets and variables → Actions → New repository secret");
  process.exit(1);
}
if (!existsSync(DIST)) {
  console.error("Chưa có dist/ — chạy `npm run dist` trước.");
  process.exit(1);
}

async function walk(dir, out = []) {
  for (const name of await readdir(dir)) {
    const p = join(dir, name);
    const s = await stat(p);
    if (s.isDirectory()) await walk(p, out);
    else out.push(p);
  }
  return out;
}

const files = await walk(DIST);
const form = new FormData();
let bytes = 0;

for (const f of files) {
  const buf = await readFile(f);
  bytes += buf.length;
  const rel = relative(DIST, f).split("\\").join("/");
  // Pinata dựng lại cây thư mục từ chính tên file có kèm đường dẫn
  form.append("file", new Blob([buf]), `${FOLDER}/${rel}`);
}

form.append("pinataMetadata", JSON.stringify({
  name: FOLDER,
  keyvalues: { app: "kinh-thanh", pinnedAt: new Date().toISOString() }
}));
// cidVersion 1 → CID dạng bafy…, dùng được cho gateway theo tên miền con
form.append("pinataOptions", JSON.stringify({ cidVersion: 1 }));

console.log(`Đang đẩy ${files.length} file · ${(bytes / 1024).toFixed(0)} KB lên Pinata…`);

const res = await fetch("https://api.pinata.cloud/pinning/pinFileToIPFS", {
  method: "POST",
  headers: { Authorization: "Bearer " + JWT },
  body: form
});

const text = await res.text();
if (!res.ok) {
  console.error(`Pinata trả về HTTP ${res.status}\n${text.slice(0, 500)}`);
  process.exit(1);
}

let out;
try { out = JSON.parse(text); } catch {
  console.error("Không đọc được phản hồi của Pinata:\n" + text.slice(0, 500));
  process.exit(1);
}

const cid = out.IpfsHash;
console.log(`\n✓ CID  ${cid}`);
console.log(`  kích thước đã pin: ${(Number(out.PinSize || bytes) / 1024).toFixed(0)} KB`);
console.log("\nMở thử:");
console.log(`  https://${cid}.ipfs.dweb.link/`);
console.log(`  https://ipfs.io/ipfs/${cid}/`);
if (process.env.PINATA_GATEWAY) {
  console.log(`  https://${process.env.PINATA_GATEWAY}/ipfs/${cid}/`);
}
console.log("\nĐể tên miền ENS trỏ vào bản này, đặt contenthash thành:");
console.log(`  ipfs://${cid}`);

/* nhả CID ra cho các bước sau của GitHub Actions */
if (process.env.GITHUB_OUTPUT) await appendFile(process.env.GITHUB_OUTPUT, `cid=${cid}\n`);
if (process.env.GITHUB_STEP_SUMMARY) {
  await appendFile(process.env.GITHUB_STEP_SUMMARY,
    `### Đã đẩy lên IPFS\n\n` +
    `\`\`\`\n${cid}\n\`\`\`\n\n` +
    `- [dweb.link](https://${cid}.ipfs.dweb.link/)\n` +
    `- [ipfs.io](https://ipfs.io/ipfs/${cid}/)\n\n` +
    `Đặt ENS contenthash: \`ipfs://${cid}\`\n`);
}
