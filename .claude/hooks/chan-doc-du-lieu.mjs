/* ═══════════════════════════════════════════════════════════════
   Cổng chặn đọc dữ liệu tự sinh của Tàng Thư Các.

   Vì sao cần: rule `Read(...)` trong permissions.deny chỉ chặn tool
   Read. Một lệnh `cat` chạy qua Bash đi cửa khác và vẫn đổ 2 MB
   data.js vào ngữ cảnh. File này bịt cửa đó.

   Chạy như hook PreToolUse, matcher "Bash|PowerShell". Nhận JSON
   của lượt gọi tool trên stdin, soi chuỗi lệnh, và nếu thấy có
   đường dẫn dữ liệu thì trả quyết định "deny" — Claude Code huỷ
   lượt gọi TRƯỚC khi shell chạy.

   ─── VÌ SAO LÀ DANH SÁCH CHO PHÉP, KHÔNG PHẢI DANH SÁCH CẤM ───

   Bản đầu cấm theo động từ: cat, head, grep... Đo thử 13 đường
   vòng thì 12 đi lọt — sed, awk, perl, python -c, node -e, jq,
   base64, cut, tr, `< redirect`, git diff. Danh sách cấm luôn
   thiếu, vì kẻ đọc file không nhất thiết tên là cat.

   Nên luật lật ngược: hễ chuỗi lệnh có nhắc tới đường dẫn dữ liệu
   thì CẤM, trừ khi mọi đầu lệnh trong chuỗi đều nằm trong nhóm
   CHI_DO — nhóm chỉ đo đạc chứ không đổ nội dung ra. Công cụ lạ,
   script tự viết, ngôn ngữ script: chặn mặc định.

   ─── ĐIỀU NÓ KHÔNG CANH ĐƯỢC, KHAI THẲNG ───

   1. Lệnh không nhắc tên đường dẫn thì cổng này mù. Ví dụ
      `node scripts/build-dich-tom.mjs` đọc data.js bên trong —
      đúng và cần thiết, cứ chạy. Nhưng một script tuỳ ý cũng có
      thể đọc rồi in ra, mà cổng không thấy.
   2. Đường dẫn dựng động (biến shell, ghép chuỗi) thì không khớp.
   3. Nó chặn LỆNH SHELL. Tool Read đã có permissions.deny lo;
      các tool khác (Grep, Glob) không nằm trong tầm file này.

   ─── LUẬT KHI SỬA FILE NÀY ───

   Tuyệt đối không gõ ký tự gạch ngược vào đây. File được ghi qua
   heredoc của shell và gạch ngược bị nuốt mất một lớp — bản đầu
   tiên chết cú pháp đúng vì thế, mà script chết thì IM LẶNG cho
   lệnh chạy qua. Mọi biểu thức chính quy vì vậy dựng bằng
   new RegExp(chuỗi), dấu chấm viết [.], gạch ngược lấy từ
   String.fromCharCode(92).
   ═══════════════════════════════════════════════════════════════ */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const GACH_NGUOC = String.fromCharCode(92);

/* Khoảng trắng: dấu cách hoặc tab. Dựng bằng mã ký tự vì lý do nêu
   ở đầu file. */
const TRANG = new RegExp("[ " + String.fromCharCode(9) + "]+");

/* Đường dẫn dữ liệu KHÔNG nằm trong mã. Chúng khai ở
   du-lieu-cam.json cạnh file này — thêm một cung là thêm một mục ở
   đó, không phải sửa rồi test lại cả cái khoá.

   Khai báo hỏng thì cổng CHẶN TẤT CẢ chứ không âm thầm chạy tiếp:
   một cái khoá không biết mình canh gì thì không được phép nói cho
   qua. Sửa lại JSON là hết chặn. */
const NOI = dirname(fileURLToPath(import.meta.url));
let KHAI = null;
let LOI_KHAI = null;
try {
  KHAI = JSON.parse(readFileSync(join(NOI, "du-lieu-cam.json"), "utf8"));
  if (!Array.isArray(KHAI.cam) || !KHAI.cam.length) {
    throw new Error("thiếu mảng cam, hoặc mảng rỗng");
  }
  for (const m of KHAI.cam) {
    if (!Array.isArray(m.duong) || !m.duong.length) {
      throw new Error("mục " + (m.cung || "?") + " thiếu mảng duong");
    }
  }
} catch (e) {
  LOI_KHAI = e.message;
}

/* Mỗi đường dẫn thành một phép so khớp không phân biệt hoa thường. */
const DUONG = LOI_KHAI
  ? []
  : KHAI.cam.flatMap((m) =>
      m.duong.map((d) => ({
        cung: m.cung,
        sinh_boi: m.sinh_boi,
        khop: new RegExp(d.split(".").join("[.]"), "i"),
      })),
    );

/* Nhóm CHI_DO: đo đạc, liệt kê, quản lý file — không đổ nội dung.
   So khớp sau khi hạ chữ thường. Thêm tên vào đây là nới cổng,
   nên chỉ thêm khi chắc lệnh đó không in được nội dung file. */
const CHI_DO = new Set([
  "ls", "dir", "find", "stat", "du", "wc", "file", "tree",
  "basename", "dirname", "realpath", "readlink", "pwd", "cd",
  "echo", "printf", "mkdir", "test", "[", "true", ":",
  "get-childitem", "gci", "test-path", "measure-object",
  "resolve-path", "split-path", "join-path", "get-item",
]);

/* Từ khoá cú pháp: KHÔNG phải lệnh, phải bước QUA nó rồi mới soi
   lệnh thật đứng sau. Cho thẳng vào nhóm chỉ-đo là sai — `do cat
   $f` sẽ lọt vì chữ đầu khúc là `do`. Đúng chuyện đã xảy ra. */
const BUOC_QUA = new Set([
  "do", "then", "else", "elif", "fi", "done", "esac",
  "while", "until", "if", "time", "command", "exec",
  "builtin", "env", "nohup", "sudo",
]);

/* Khúc mở đầu một cấu trúc: cả khúc là danh sách dữ liệu, không
   chứa lệnh nào. `for f in <đường dẫn>` là khai biến, không đọc. */
const KHUC_KHUNG = new Set(["for", "select", "case", "in"]);

/* git in được nội dung file (show, diff, log -p, cat-file), nên
   chỉ cho qua những lệnh con không in. */
const GIT_CHI_DO = new Set([
  "status", "add", "ls-files", "check-ignore", "rm", "mv",
  "restore", "checkout", "stash", "clean", "commit", "push",
  "count-objects", "rev-parse", "branch", "remote", "config",
]);

/* Chỗ tách khúc: mọi thứ có thể bắt đầu một lệnh mới, kể cả
   $( và dấu huyền, để `echo $(cat data.js)` không núp sau echo. */
const TACH = new RegExp(
  "[|;&" + String.fromCharCode(10) + "]+|[$][(]|[(]|[)]|`|[{]|[}]",
  "g",
);

/* Thay mọi đoạn trong dấu nháy bằng một chữ Q, TRƯỚC khi tách khúc.
   Vì sao: dấu | ; & nằm bên trong dấu nháy là văn bản, không phải
   chỗ ngắt lệnh. Không làm bước này thì grep -E 'a|b' bị cắt đôi
   và nửa sau thành một đầu lệnh ma. Nội dung trong nháy không cần
   giữ: phép dò đường dẫn đã chạy trên chuỗi gốc rồi. */
function boNhay(s) {
  const NHAY_DON = String.fromCharCode(39);
  const NHAY_KEP = String.fromCharCode(34);
  let ra = "";
  let dang = null;
  for (const ch of s) {
    if (dang) {
      if (ch === dang) {
        dang = null;
        ra += "Q";
      }
    } else if (ch === NHAY_DON || ch === NHAY_KEP) {
      dang = ch;
    } else {
      ra += ch;
    }
  }
  if (dang) ra += "Q";
  return ra;
}

/* Một chỗ duy nhất dựng câu trả lời chặn. */
function chan(ly_do) {
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: ly_do,
      },
      systemMessage: "⛔ chan-doc-du-lieu đã chặn một lệnh.",
    }),
  );
  process.exit(0);
}

let vao = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (d) => (vao += d));
process.stdin.on("end", () => {
  let lenh = "";
  try {
    const j = JSON.parse(vao);
    lenh = (j && j.tool_input && j.tool_input.command) || "";
  } catch {
    /* Không đọc nổi JSON thì soi thẳng chuỗi thô — thà chặn nhầm
       còn hơn để lọt. */
    lenh = vao;
  }

  const chuoi = String(lenh).split(GACH_NGUOC).join("/");

  /* Khai báo hỏng: chặn tất, kèm cách sửa. */
  if (LOI_KHAI) {
    chan(
      "Cổng chan-doc-du-lieu tự khoá: file khai báo " +
        "du-lieu-cam.json cạnh nó đọc không được (" + LOI_KHAI +
        "). Một cái khoá không biết mình canh gì thì không được " +
        "phép nói cho qua. Sửa lại JSON đó là hết chặn.",
    );
  }

  /* Không nhắc tới dữ liệu thì không phải việc của cổng này. */
  const trung = DUONG.find((d) => d.khop.test(chuoi));
  if (!trung) {
    process.exit(0);
  }
  /* Có nhắc tới. Giờ soi từng khúc: đầu lệnh nào lạ thì chặn. */
  const la = [];
  for (const khuc of boNhay(chuoi).split(TACH)) {
    const tu = khuc.trim().split(TRANG).filter(Boolean);
    if (!tu.length) continue;
    /* Bước qua từ khoá, tiền tố kiểu FOO=bar, và mảnh vụn dấu câu,
       để tìm ĐẦU LỆNH thật của khúc này. */
    if (KHUC_KHUNG.has(tu[0].toLowerCase())) continue;
    let k = 0;
    while (k < tu.length) {
      const t = tu[k].toLowerCase();
      if (BUOC_QUA.has(t)) { k += 1; continue; }
      if (!/[a-z0-9]/.test(t)) { k += 1; continue; }
      if (t.includes("=") && !t.startsWith("-")) { k += 1; continue; }
      break;
    }
    if (k >= tu.length) continue;
    const dau = tu[k].toLowerCase();
    if (dau === "git") {
      const con = (tu.slice(k + 1).find((t) => !t.startsWith("-")) || "").toLowerCase();
      if (!GIT_CHI_DO.has(con)) la.push("git " + (con || "?"));
      continue;
    }
    if (!CHI_DO.has(dau)) la.push(dau);
  }

  if (la.length) {
    chan(
      "Chặn bởi hook chan-doc-du-lieu: lệnh này chạm vào file dữ liệu " +
        "tự sinh của cung " + trung.cung + ", qua lệnh không thuộc " +
        "nhóm chỉ-đo: " + la.join(", ") + ". Chúng bị cấm nạp vào " +
        "ngữ cảnh. Đo đạc thì dùng ls/find/wc/du/stat. Cần biết cấu " +
        "trúc thì đọc script sinh ra chúng" +
        (trung.sinh_boi ? " (" + trung.sinh_boi + ")" : "") +
        ", hoặc hỏi người dùng.",
    );
  }

  process.exit(0);
});
