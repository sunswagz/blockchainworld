/* ═══════════════════════════════════════════════════════════════
   Bộ kiểm của cổng chan-doc-du-lieu.

   Chạy:  node .claude/hooks/thu-chan-doc.mjs
   Về 0 nếu mọi ca đúng, về 1 nếu có ca sai.

   Vì sao là một FILE chứ không phải vài lệnh shell gõ tay: các ca
   thử buộc phải chứa đường dẫn dữ liệu, mà chính cổng này chặn mọi
   lệnh shell nhắc tới đường dẫn đó — bộ thử gõ tay tự chặn chính
   nó. Nằm trong file thì lệnh chạy chỉ là `node ...thu-chan-doc.mjs`,
   không nhắc đường dẫn nào, nên đi lọt hợp lệ.

   Sửa cổng xong thì chạy lại file này. Thêm một cung vào
   du-lieu-cam.json cũng nên thêm vài ca vào đây.
   ═══════════════════════════════════════════════════════════════ */

import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const NOI = dirname(fileURLToPath(import.meta.url));
const CONG = join(NOI, "chan-doc-du-lieu.mjs");

/* mong: "chan" = cổng phải từ chối, "qua" = cổng phải im lặng cho qua */
const CA = [
  // ── đọc thẳng, đủ kiểu công cụ ────────────────────────────────
  ["chan", "cat tang-thu-cac/assets/js/data.js", "cat"],
  ["chan", "sed -n 1,400p tang-thu-cac/assets/js/data.js", "sed"],
  ["chan", "awk NR<300 tang-thu-cac/assets/js/data.js", "awk"],
  ["chan", "perl -ne print tang-thu-cac/assets/data/x.json", "perl"],
  ["chan", 'python -c open("tang-thu-cac/assets/js/data.js")', "python -c"],
  ["chan", 'node -e fs.readFileSync("tang-thu-cac/assets/js/data.js")', "node -e"],
  ["chan", "jq . tang-thu-cac/assets/data/dich-tom.json", "jq"],
  ["chan", "base64 tang-thu-cac/assets/js/data.js", "base64"],
  ["chan", "xxd tang-thu-cac/assets/js/data.js", "xxd"],
  ["chan", "cut -c1-500 tang-thu-cac/assets/js/data.js", "cut"],
  ["chan", "grep -c x tang-thu-cac/assets/data/lich-su.json", "grep"],
  ["chan", "head -5 tang-thu-cac/assets/data/lich-su.json", "head"],

  // ── đường vòng: núp sau cú pháp shell ─────────────────────────
  ["chan", "tr -d x < tang-thu-cac/assets/js/data.js", "redirect vào lệnh"],
  [
    "chan",
    "while read l; do echo $l; done < tang-thu-cac/assets/js/data.js",
    "redirect vào vòng lặp",
  ],
  ["chan", "echo $(cat tang-thu-cac/assets/js/data.js)", "núp sau $( )"],
  ["chan", "ls x; cat tang-thu-cac/assets/js/data.js", "núp sau dấu ;"],
  [
    "chan",
    "cd tang-thu-cac/assets/data && cat lich-su.json",
    "cd rồi gọi tên ngắn",
  ],
  [
    "chan",
    "for f in hoang-thanh/assets/js/v/*.js; do cat $f; done",
    "vòng lặp có cat bên trong",
  ],

  // ── git: lệnh con nào in được nội dung file ───────────────────
  ["chan", "git show HEAD:tang-thu-cac/assets/js/data.js", "git show"],
  ["chan", "git diff -- tang-thu-cac/assets/data/lich-su.json", "git diff"],
  ["chan", "git log -p tang-thu-cac/assets/js/data.js", "git log -p"],

  // ── ba cung khai sau ──────────────────────────────────────────
  ["chan", "head -5 hoang-thanh/assets/js/v/an-do.js", "hoang-thanh v/"],
  ["chan", "cat hoang-thanh/assets/js/data.js", "hoang-thanh data.js"],
  ["chan", "cat do-sat-vien/assets/js/data.js", "do-sat-vien"],
  ["chan", "cat cong-bo/assets/js/v/nhat-ky.js", "cong-bo nhat-ky"],

  // ── đo đạc: phải chạy được, nếu không thì không ai đếm nổi ────
  ["qua", "find tang-thu-cac/assets/data -type f | wc -l", "find | wc"],
  ["qua", "ls -la tang-thu-cac/assets/data/kb", "ls"],
  ["qua", "du -sh tang-thu-cac/assets/data", "du"],
  ["qua", "stat -c%s tang-thu-cac/assets/js/data.js", "stat"],
  ["qua", "ls hoang-thanh/assets/js/v | wc -l", "ls | wc"],

  // ── git an toàn ───────────────────────────────────────────────
  ["qua", "git ls-files tang-thu-cac/assets/data | wc -l", "git ls-files"],
  ["qua", "git check-ignore -q tang-thu-cac/assets/js/data.js", "git check-ignore"],
  ["qua", "git add tang-thu-cac/assets/data", "git add"],
  ["qua", "git status --short", "git status"],

  // ── cú pháp shell bọc quanh lệnh đo đạc ───────────────────────
  [
    "qua",
    "for p in tang-thu-cac/assets/js/data.js; do stat -c%s $p; done",
    "for ... do ... done",
  ],
  [
    "qua",
    "if git check-ignore -q tang-thu-cac/assets/js/data.js; then echo co; else echo khong; fi",
    "if ... then ... else ... fi",
  ],
  [
    "qua",
    "git count-objects -vH | grep -E 'size-pack|count:'",
    "dấu | nằm trong nháy",
  ],

  // ── file viết tay của chính các cung bị khai ──────────────────
  ["qua", "cat tang-thu-cac/assets/js/glossary.js", "glossary.js viết tay"],
  ["qua", "cat hoang-thanh/assets/js/app.js", "app.js viết tay"],
  ["qua", "cat tang-thu-cac/index.html", "index.html"],

  // ── script sinh: đọc được, và chạy được ───────────────────────
  ["qua", "cat scripts/build-hoangthanh.mjs", "đọc script sinh"],
  ["qua", "node scripts/build-tangthu.mjs", "chạy script sinh"],

  // ── cung CHƯA khai: không được lan phạm vi ────────────────────
  ["qua", "head -20 ho-bo/assets/js/v/dong-tien.js", "ho-bo chưa khai"],
  ["qua", "cat thai-boc-tu/assets/js/v/doan-tau.js", "thai-boc-tu chưa khai"],

  // ── lệnh thường ngày, không dính dáng ─────────────────────────
  ["qua", "git log --oneline -5", "git log"],
  ["qua", "grep -rn abc scripts/", "grep trong scripts"],
  ["qua", "npm run kiem", "npm"],
];

function hoi(lenh) {
  const vao = JSON.stringify({
    tool_name: "Bash",
    tool_input: { command: lenh },
  });
  const r = spawnSync(process.execPath, [CONG], { input: vao, encoding: "utf8" });
  if (r.status !== 0) return "loi:" + (r.stderr || "").split("\n")[0];
  const ra = (r.stdout || "").trim();
  if (!ra) return "qua";
  try {
    return JSON.parse(ra).hookSpecificOutput.permissionDecision === "deny"
      ? "chan"
      : "la:" + ra.slice(0, 60);
  } catch {
    return "la:" + ra.slice(0, 60);
  }
}

let dung = 0;
const sai = [];
for (const [mong, lenh, nhan] of CA) {
  const duoc = hoi(lenh);
  if (duoc === mong) dung += 1;
  else sai.push({ nhan, lenh, mong, duoc });
}

console.log("Bộ kiểm cổng chan-doc-du-lieu");
console.log("  " + dung + " đúng / " + CA.length + " ca");
if (sai.length) {
  console.log("");
  for (const s of sai) {
    console.log("  SAI  " + s.nhan);
    console.log("       lệnh : " + s.lenh);
    console.log("       cần  : " + s.mong + "   được: " + s.duoc);
  }
  process.exit(1);
}
console.log("  trọn vẹn");
