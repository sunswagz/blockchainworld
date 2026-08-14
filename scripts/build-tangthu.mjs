/* ═══════════════════════════════════════════════════════
   Sinh dữ liệu cho Tàng Thư Các — kho tra cứu Claude Skills.

   Chạy tay:      npm run tangthu
   Chạy tự động:  .github/workflows/refresh-data.yml

   ── LẤY GÌ, TỪ ĐÂU ────────────────────────────────────
   1. Xếp hạng kho ← api.github.com/search/repositories
        BỐN truy vấn gộp lại, cộng danh sách LUON_CO gọi thẳng.
        Một thẻ là không đủ: obra/superpowers (271k sao) gắn thẻ
        `skills` chứ không phải `claude-skills`, còn mattpocock/skills
        và garrytan/gstack thì KHÔNG gắn thẻ nào — không truy vấn
        topic nào tìm ra chúng được.
   2. Danh mục skill ← với mỗi kho hàng đầu, gọi git/trees?recursive=1
        (MỘT lời gọi lấy cả cây) rồi lọc mọi file SKILL.md.
   3. Nội dung skill ← raw.githubusercontent.com
        Đọc frontmatter YAML: name + description.
        raw.* là CDN, KHÔNG tính vào hạn mức API — nên phần nặng
        nhất lại là phần rẻ nhất.

   ── HẠN MỨC ───────────────────────────────────────────
   Không có token: 60 lượt/giờ mỗi IP. Có GITHUB_TOKEN trong
   Actions: 1.000 lượt/giờ mỗi repo. Personal access token cá nhân
   (miễn phí): 5.000 lượt/giờ. Script tự dùng token nếu thấy biến
   môi trường,
   và dừng quét thêm kho khi hạn mức xuống thấp thay vì đâm đầu
   vào lỗi 403.

   ── VÌ SAO KHÔNG DỊCH TAY HẾT ─────────────────────────
   17 skill chính thức của Anthropic được dịch và diễn giải tay
   trong cong-bo... không, trong tang-thu-cac/assets/js/glossary.js.
   Skill cộng đồng thì hàng trăm cái, không dịch tay nổi — nên
   phân nhóm tự động và GIỮ NGUYÊN mô tả tiếng Anh, đánh dấu rõ
   là chưa dịch tay. Bịa mô tả tiếng Việt cho skill mình chưa đọc
   còn tệ hơn là để nguyên bản.
   ═══════════════════════════════════════════════════════ */

import { writeFile, mkdir, readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DIR = join(ROOT, "tang-thu-cac", "assets", "js");

const TOKEN = process.env.GITHUB_TOKEN || process.env.GH_TOKEN || "";

/* MỖI KHO TỐN ĐÚNG MỘT LƯỢT API — đo thật, không suy đoán:
   quét 5 kho liên tiếp thì hạn mức đi 31→30→29→28→27.

   Lý do nằm ở chỗ chia việc: mỗi kho chỉ cần một lời gọi
   `git/trees?recursive=1` để lấy toàn bộ cây file; còn nội dung
   từng SKILL.md thì lấy qua raw.githubusercontent.com — CDN, KHÔNG
   tính vào hạn mức. Nên phần nặng nhất lại là phần miễn phí, và một
   kho 400 skill tốn y hệt một kho 1 skill: một lượt.

   Trước khi vào vòng quét còn tốn cỡ 15 lượt cố định: 4 truy vấn
   tìm kiếm cộng khoảng 10 lượt nạp thẳng danh sách kho gieo sẵn.
   Cộng thêm ít dự phòng cho lần thử lại khi mạng chập. */
const LUOT_CO_DINH = 20;

/* Số kho quét suy từ hạn mức CÒN LẠI thật, đọc lúc chạy (doTran).

   Bản cũ ghi cứng 40 khi có token, và tôi từng tưởng đó là hệ quả
   của hạn mức. Không phải: với 1 lượt/kho thì GITHUB_TOKEN
   (1.000/giờ) thừa sức quét cả 66 kho. Con số 40 chỉ là một mức
   thủ cựu viết tay, và nó im lặng bỏ sót 26 kho — bảng vẫn ra
   bình thường, không có gì báo là còn thiếu.

   Đặt TT_SO_KHO để ép một con số cụ thể (dùng khi thử ở máy). */
let SO_KHO_QUET = Number(process.env.TT_SO_KHO || 0);
const SO_KHO_HANG = 60;          /* giữ bao nhiêu kho trong bảng xếp hạng */
const MAX_SKILL_MOI_KHO = 400;   /* kho gom hàng nghìn skill thì cắt bớt */

const log = (...a) => console.log(...a);
const warn = (...a) => console.error("  ⚠", ...a);
const nghi = (ms) => new Promise((r) => setTimeout(r, ms));

const HEAD = {
  accept: "application/vnd.github+json",
  "user-agent": "tang-thu-cac-databot",
  ...(TOKEN ? { authorization: "Bearer " + TOKEN } : {})
};

let conLuot = null;
let tranLuot = null;

/* Hỏi thẳng GitHub trần hạn mức là bao nhiêu, thay vì suy từ "có
   token hay không". Ba mức rất khác nhau — 60 (không token), 1.000
   (GITHUB_TOKEN trong Actions), 5.000 (token cá nhân) — và chỉ nhìn
   biến môi trường thì không phân biệt được hai mức sau, vì cả hai
   đều chỉ là một chuỗi ký tự.

   /rate_limit KHÔNG tính vào hạn mức, nên phép hỏi này miễn phí.
   Hỏng thì không sao: rơi về mức đoán cũ và chạy tiếp. */
async function doTran() {
  try {
    const r = await fetch("https://api.github.com/rate_limit", { headers: HEAD });
    if (!r.ok) return;
    const j = await r.json();
    const c = j?.resources?.core;
    if (!c) return;
    tranLuot = Number(c.limit);
    conLuot = Number(c.remaining);
  } catch { /* mạng hỏng — cứ chạy, gh() sẽ tự đọc header sau */ }
}

async function gh(url) {
  for (let lan = 1; lan <= 3; lan++) {
    try {
      const r = await fetch(url, { headers: HEAD });
      const cl = r.headers.get("x-ratelimit-remaining");
      if (cl != null) conLuot = Number(cl);
      if (r.status === 403 || r.status === 429) {
        throw new Error("hết hạn mức (còn " + conLuot + ")");
      }
      if (!r.ok) throw new Error("HTTP " + r.status);
      return await r.json();
    } catch (e) {
      if (lan === 3) throw e;
      await nghi(lan * 3000);
    }
  }
}

async function raw(url) {
  const r = await fetch(url, { headers: { "user-agent": "tang-thu-cac-databot" } });
  if (!r.ok) throw new Error("HTTP " + r.status);
  return await r.text();
}

/* ── frontmatter YAML rất đơn giản, không kéo thư viện ──
   Chỉ cần name + description. Description hay trải nhiều dòng
   nên phải gộp các dòng thụt vào tiếp theo. */
function bocFrontmatter(md) {
  if (!md.startsWith("---")) return null;
  const het = md.indexOf("\n---", 3);
  if (het === -1) return null;
  const than = md.slice(3, het);
  const ra = {};
  let khoa = null;
  for (const dong of than.split("\n")) {
    const m = dong.match(/^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$/);
    if (m) {
      khoa = m[1];
      let v = m[2].trim();
      /* YAML block scalar: `description: |-` rồi nội dung thụt vào
         dòng dưới. Không bỏ dấu này thì mô tả bắt đầu bằng "|-". */
      if (/^[|>][-+]?$/.test(v)) v = "";
      ra[khoa] = v.replace(/^["']|["']$/g, "");
    } else if (khoa && /^\s+\S/.test(dong)) {
      ra[khoa] = (ra[khoa] ? ra[khoa] + " " : "") + dong.trim();
    }
  }
  return ra;
}

/* ── phân nhóm việc tự động ────────────────────────────
   Bắt theo từ khoá trong tên + mô tả. Không khớp gì thì vào
   "khac" chứ không đoán bừa — nhóm sai còn khó chịu hơn không
   phân nhóm. */
/* Thứ tự QUAN TRỌNG: cái hẹp đứng trước cái rộng. "canvas-design"
   có chữ ".pdf" trong mô tả nên nếu để tai-lieu trước giao-dien thì
   nó bị xếp thành công cụ tài liệu. Và xét TÊN trước MÔ TẢ, vì tên
   nói đúng việc của skill hơn — mô tả hay nhắc tới thứ nó xuất ra. */
const NHOM = [
  ["kiem-thu", /\b(test|testing|qa|playwright|e2e|lint|audit|debug)\b/i],
  ["giao-dien", /\b(design|ui|ux|frontend|css|theme|brand|canvas|artifact|animation|logo|colou?r|typography|layout|visual|art)\b/i],
  ["tai-lieu", /\b(pdf|docx?|xlsx?|pptx?|spreadsheet|powerpoint|word|excel|document|report|slide|presentation)\b/i],
  ["du-lieu", /\b(data|chart|graph|analytics|sql|database|csv|dataset|scrape|scraping)\b/i],
  ["ha-tang", /\b(deploy|docker|kubernetes|ci\/cd|infra|server|cloud|aws|terraform|workflow|action)\b/i],
  ["giao-tiep", /\b(slack|email|comms|communication|blog|social|marketing|meeting|notion)\b/i],
  ["nghien-cuu", /\b(research|paper|academic|science|scientific)\b/i],
  ["lap-trinh", /\b(code|coding|refactor|api|sdk|mcp|plugin|skill|library|framework|typescript|python|rust|git)\b/i]
];
function phanNhom(ten, mota) {
  for (const [ma, re] of NHOM) if (re.test(ten || "")) return ma;
  for (const [ma, re] of NHOM) if (re.test(mota || "")) return ma;
  return "khac";
}

/* ── bản cũ, để vá khi nguồn hỏng ──────────────────── */
async function docCu() {
  const f = join(DIR, "data.js");
  if (!existsSync(f)) return null;
  try {
    const t = await readFile(f, "utf8");
    const m = t.match(/window\.TT_DATA\s*=\s*([\s\S]*);\s*$/);
    return m ? JSON.parse(m[1]) : null;
  } catch { return null; }
}
const cu = await docCu();

await doTran();

/* Đặt ngân sách kho theo trần THẬT. Không hỏi được trần thì rơi về
   mức đoán cũ — thà quét ít còn hơn đâm vào 403 giữa chừng. */
if (!SO_KHO_QUET) {
  SO_KHO_QUET = conLuot != null
    ? Math.max(6, conLuot - LUOT_CO_DINH)
    : (TOKEN ? 40 : 14);          /* không hỏi được trần → mức đoán cũ */
}

if (tranLuot) {
  const loai = tranLuot >= 15000 ? "Enterprise Cloud"
             : tranLuot >= 5000 ? "token cá nhân"
             : tranLuot >= 1000 ? "GITHUB_TOKEN trong Actions"
             : "không có token";
  log(`· hạn mức thật: ${tranLuot}/giờ (${loai}) — còn ${conLuot} lượt`);
  log(`  → đủ chỗ cho tối đa ${SO_KHO_QUET} kho (1 lượt/kho)`);
} else {
  log(TOKEN ? "· có token, nhưng không hỏi được trần — tạm quét " + SO_KHO_QUET + " kho"
            : "· KHÔNG có token — hạn mức 60/giờ mỗi IP, quét ít kho thôi");
}

/* Kho LUÔN nạp thẳng, không trông vào kết quả tìm kiếm.
   anthropics/skills gắn thẻ `agent-skills` chứ không phải
   `claude-skills`, nên nó KHÔNG lọt vào tìm theo topic — mà đây
   lại đúng là nguồn chính thức và là nhóm duy nhất được dịch tay.
   Lần đầu tôi quên chỗ này và ra bảng 0 skill chính thức. */
const LUON_CO = [
  /* Kho lớn mà KHÔNG tìm theo thẻ nào ra được — phải gọi thẳng.
     Nhớ: mattpocock/skills và garrytan/gstack không gắn một thẻ nào,
     nên không có truy vấn topic nào cứu được chúng. */
  "anthropics/skills",
  "obra/superpowers",
  "mattpocock/skills",
  "garrytan/gstack",
  "addyosmani/agent-skills",
  "nextlevelbuilder/ui-ux-pro-max-skill",
  "Egonex-AI/Understand-Anything",
  "FullStackFang/career-ops",
  /* Leonxlnx viết bằng chữ L THƯỜNG, không phải chữ i HOA. Hai ký tự
     này trông y hệt nhau ở phần lớn phông chữ; bản danh sách tôi nhận
     được ghi "LeonxInx" và nó 404. */
  "Leonxlnx/taste-skill",
  "mvanhorn/last30days-skill"
];

function gonRepo(r) {
  return {
    id: r.full_name,
    chu: r.owner?.login || null,
    ten: r.name,
    moTa: r.description || null,
    sao: r.stargazers_count,
    fork: r.forks_count,
    nhanh: r.default_branch || "main",
    doiLuc: r.pushed_at || r.updated_at,
    ngonNgu: r.language || null,
    topics: r.topics || [],
    chinhChu: r.owner?.login === "anthropics"
  };
}

/* ── 1. xếp hạng kho ───────────────────────────────── */
/* Nhiều truy vấn thay vì một. Tìm kiếm của GitHub giới hạn 10
   lượt/phút khi không có token, nên nghỉ giữa các truy vấn. */
const TRUY_VAN = [
  "topic:claude-skills",
  "topic:agent-skills",
  "topic:claude-code topic:skills",
  "skills in:name claude in:description"
];

let kho = null;
try {
  const gom = new Map();
  for (const q of TRUY_VAN) {
    let j;
    try {
      j = await gh("https://api.github.com/search/repositories?q=" +
        encodeURIComponent(q) + "&sort=stars&order=desc&per_page=" + SO_KHO_HANG);
    } catch (e) {
      warn(`truy vấn "${q}" lỗi: ${e.message}`);
      await nghi(7000);
      continue;
    }
    let moi = 0;
    for (const r of j.items || []) {
      if (gom.has(r.full_name)) continue;
      gom.set(r.full_name, r);
      moi++;
    }
    log(`  tìm "${q}" → ${(j.items || []).length} kết quả, ${moi} kho mới`);
    await nghi(7000);   /* tìm kiếm không token: 10 lượt/phút */
  }
  if (!gom.size) throw new Error("không truy vấn nào trả về kho");
  kho = [...gom.values()].map((r) => ({
    id: r.full_name,
    chu: r.owner?.login || null,
    ten: r.name,
    moTa: r.description || null,
    sao: r.stargazers_count,
    fork: r.forks_count,
    nhanh: r.default_branch || "main",
    doiLuc: r.pushed_at || r.updated_at,
    ngonNgu: r.language || null,
    topics: r.topics || [],
    chinhChu: r.owner?.login === "anthropics"
  }));
  kho.sort((a, b) => b.sao - a.sao);
  kho = kho.slice(0, SO_KHO_HANG);
  log(`✓ xếp hạng  ${kho.length} kho, gộp từ ${TRUY_VAN.length} truy vấn`);
} catch (e) {
  warn("Không lấy được xếp hạng kho — " + e.message);
  kho = cu?.kho || null;
  if (kho) warn("Giữ bản trước (" + kho.length + " kho).");
}

if (!kho) {
  console.error("Không có xếp hạng kho và cũng không có bản cũ — không ghi đè.");
  process.exit(1);
}

let hongNapThang = 0;

/* nạp thẳng những kho bắt buộc mà tìm kiếm không trả về */
for (const ten of LUON_CO) {
  if (kho.some((k) => k.id.toLowerCase() === ten.toLowerCase())) continue;
  try {
    kho.unshift(gonRepo(await gh("https://api.github.com/repos/" + ten)));
    log(`✓ nạp thẳng ${ten} (tìm theo topic không trả về kho này)`);
  } catch (e) {
    /* Không gọi được thì lấy lại từ bản trước thay vì để kho biến mất
       khỏi bảng. Hết hạn mức là chuyện thường khi chạy tay, mà bảng
       xếp hạng tụt mất mấy kho lớn thì rất khó nhận ra. */
    const truoc = (cu?.kho || []).find((k) => k.id.toLowerCase() === ten.toLowerCase());
    if (truoc) {
      kho.unshift(truoc);
      warn(`${ten}: ${e.message} — dùng lại bản trước`);
    } else {
      warn(`Không nạp được ${ten} — ${e.message}`);
      hongNapThang++;
    }
  }
}

/* Thư mục ngôn ngữ trong đường dẫn — bản dịch của cùng một skill.
   Giữ bản gốc, không giữ bản dịch làm bản chuẩn. */
/* Mã ngôn ngữ có thể kèm mã vùng: ja-JP, ko-KR, pt-BR, zh-Hans…
   Bản đầu chỉ liệt kê mã trần nên docs/ja-JP/ lọt lưới và được chọn
   làm bản chính — lệnh cài trỏ vào bản tiếng Nhật. */
const RE_NGON_NGU =
  /(^|\/)(es|vi|zh|ja|ko|fr|de|pt|ru|it|tr|id|th|hi|ar|nl|pl|sv|uk|cs|ro|el|he|fa|bn|ms)(-[a-z]{2,4})?(\/|$)/i;

/* Thư mục "gương" cho từng công cụ agent. Thứ tự = mức ưu tiên;
   không nằm trong danh sách thì coi như vị trí chính. */
const THU_TU_GUONG = [".claude/", ".agents/", ".cursor/", ".kiro/", ".codex/", ".windsurf/"];

function diemDuong(p) {
  let d = 0;
  if (RE_NGON_NGU.test(p)) d += 100;                       /* bản dịch: xuống hạng mạnh */
  if (/(^|\/)docs(\/|$)/i.test(p)) d += 40;                /* trong docs/: bản phụ, không phải chỗ chính */
  for (let i = 0; i < THU_TU_GUONG.length; i++) {
    if (p.indexOf(THU_TU_GUONG[i]) !== -1) { d += 10 + i; break; }
  }
  d += p.split("/").length;                                /* nông hơn thì tốt hơn */
  return d;
}
/* ── BẢNG TUA + HỒ SƠ AN TOÀN ────────────────────────
   Skill không phải app để quay màn hình — nó là bản hướng dẫn cho
   agent. Nên "trailer" phải dựng từ chính cấu trúc bài viết: các đề
   mục là các chặng, khối lệnh là hành động cụ thể.

   Toàn bộ phần này KHÔNG tốn thêm một lượt tải nào: `md` đã nằm sẵn
   trong tay ở vòng quét, trước nay chỉ bóc frontmatter rồi vứt thân.

   ── Vì sao chỉ quét cờ trong KHỐI LỆNH ──
   Quét cả văn xuôi thì một câu như "đừng bao giờ commit API_KEY của
   bạn" sẽ bị gắn cờ "chạm tới bí mật" — tức là câu CẢNH BÁO người
   đọc lại làm skill trông nguy hiểm. Cờ báo nhầm thì người ta bỏ qua
   cờ, kéo theo cả lần nó đúng. Nên chỉ soi nơi có hành vi thật: khối
   ``` và mã nội dòng.

   ── Giới hạn phải nói thẳng ──
   Đây là quét TĨNH: nó chỉ thấy thứ được viết ra. Skill là chỉ dẫn
   cho agent, mà agent có thể làm việc không nằm nguyên văn trong
   file. Nên nhãn đúng là "chỗ cần đọc kỹ", KHÔNG BAO GIỜ là "đã an
   toàn". Không skill nào được gắn dấu tick xanh. */

const CO_RUI_RO = [
  { ma: "macode", nang: 3, noi: "tải mã từ mạng rồi chạy thẳng",
    re: /\b(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(ba|z|fi)?sh\b/i },
  { ma: "quantri", nang: 3, noi: "chạy quyền quản trị (sudo)", re: /\bsudo\s+\S/ },
  { ma: "xoa", nang: 3, noi: "xoá đệ quy hoặc ép xoá", re: /\brm\s+-[a-z]*[rf]/ },
  { ma: "bimat", nang: 3, noi: "đọc khoá, mật khẩu hoặc biến bí mật",
    re: /(~\/\.ssh|\/\.aws\/|\.env\b|\bcredentials\b|[A-Z][A-Z0-9_]*(API_KEY|SECRET|TOKEN|PASSWORD))/ },
  { ma: "daymang", nang: 2, noi: "ghi ra kho từ xa (không thu hồi được)",
    re: /\b(git\s+push|gh\s+(pr|release|repo|gist)\s+create)\b/ },
  { ma: "caidat", nang: 2, noi: "cài phần mềm vào máy bạn",
    re: /\b(pip3?\s+install|npm\s+(i|install|exec)\b|npx\s|yarn\s+add|brew\s+install|apt(-get)?\s+install|cargo\s+install|go\s+install)/ },
  { ma: "mang", nang: 1, noi: "gọi ra mạng",
    re: /\b(curl|wget)\b|\bfetch\(|\brequests\.(get|post)\b|\burllib\b/ },
  { ma: "quyen", nang: 1, noi: "đổi quyền tệp", re: /\bchmod\b|\bchown\b/ }
];

/* Đuôi file coi là CHẠY ĐƯỢC. Skill kèm mã chạy được thì không còn
   thuần hướng dẫn nữa — đó là khác biệt lớn nhất về mức độ tin cậy,
   nên tách hẳn ra chứ không gộp vào danh sách file chung. */
const DUOI_CHAY = /\.(sh|bash|zsh|py|js|mjs|cjs|ts|rb|pl|ps1|bat|cmd|exe)$/i;

function batMa(md) {
  let ma = "";
  for (const m of md.matchAll(/```[^\n]*\n([\s\S]*?)```/g)) ma += m[1] + "\n";
  for (const m of md.matchAll(/`([^`\n]{2,200})`/g)) ma += m[1] + "\n";
  return ma;
}

function boTrailer(md, thuMuc, fm, duongTrongCay) {
  /* Chặng = đề mục. Bỏ đề mục cấp 1 vì nó thường chỉ lặp lại tên
     skill. Cắt 12 chặng: dài hơn thì không còn là "tua nhanh" nữa. */
  const buoc = [];
  for (const m of md.matchAll(/^(#{2,3})\s+(.+?)\s*$/gm)) {
    if (buoc.length >= 12) break;
    const t = m[2].replace(/[*_`#]/g, "").trim();
    if (t) buoc.push({ c: m[1].length - 1, t: t.slice(0, 72) });
  }

  /* Khối lệnh: giữ ngôn ngữ và dòng đầu có nghĩa, để thấy ngay nó
     định làm gì mà không phải mở cả file. */
  const lenh = [];
  for (const m of md.matchAll(/```(\w*)[^\n]*\n([\s\S]*?)```/g)) {
    if (lenh.length >= 6) break;
    const dong = m[2].split("\n").map((x) => x.trim())
      .filter((x) => x && !x.startsWith("#"))[0];
    if (dong) lenh.push({ ng: (m[1] || "?").slice(0, 12), d: dong.slice(0, 110) });
  }

  const ma = batMa(md);
  const co = [];
  for (const c of CO_RUI_RO) if (c.re.test(ma)) co.push({ ma: c.ma, n: c.nang, t: c.noi });

  /* File kèm theo, lấy từ cây repo đã tải — không thêm lượt gọi nào. */
  const tien = thuMuc + "/";
  const kem = [], chay = [];
  let soTep = 0;                 /* ĐẾM THẬT, trước khi cắt danh sách */
  for (const p of duongTrongCay) {
    if (!p.startsWith(tien) || p === thuMuc + "/SKILL.md") continue;
    soTep++;
    const ten = p.slice(tien.length);
    if (DUOI_CHAY.test(ten)) chay.push(ten);
    /* Danh sách tên thì cắt cho nhẹ, nhưng số đếm phải là số thật:
       báo "24 tệp" khi thực ra là "cắt ở 24" là nói sai — và sai
       giống hệt nhau ở mọi skill lớn, nên rất khó nhận ra. */
    if (ten.length > 90 || kem.length >= 24) continue;
    kem.push(ten);
  }

  const congCu = fm["allowed-tools"] || fm.allowed_tools || null;

  return {
    dai: md.length,
    buoc,
    lenh,
    co,
    soTep,
    kem: kem.slice(0, 24),
    chay: chay.slice(0, 12),
    congCu: congCu ? String(congCu).slice(0, 200) : null
  };
}

/* ── 2. quét SKILL.md ──────────────────────────────── */
/* anthropics/skills luôn quét đầu tiên dù sao có thể thấp hơn kho
   khác: đây là nguồn chính thức và là nhóm duy nhất được dịch tay. */
/* Ưu tiên quét: kho chính thức trước, rồi tới MỌI kho trong LUON_CO,
   rồi mới tới phần còn lại theo sao. Nếu chỉ ưu tiên chinhChu thì kho
   gieo sẵn nào được tìm kiếm trả về (nên không phải "nạp thẳng") sẽ
   nằm đúng thứ hạng sao của nó và rơi ra ngoài giới hạn quét — đã xảy
   ra với Leonxlnx/taste-skill: vào được bảng mà không được quét. */
const uuTien = new Set(LUON_CO.map((x) => x.toLowerCase()));
const diem = (k) => (k.chinhChu ? 2 : 0) + (uuTien.has(k.id.toLowerCase()) ? 1 : 0);
const thuTu = [...kho].sort((a, b) => diem(b) - diem(a));
const canQuet = thuTu.slice(0, SO_KHO_QUET);

const skills = [];
const trailer = [];         /* bảng tua, ghi ra file riêng theo kho */
const daQuet = new Set();   /* kho thật sự quét trong lần chạy này */
let quetDuoc = 0, quetHong = 0;

/* Ràng buộc thật không phải hạn mức API mà là THỜI GIAN: mỗi kho chỉ
   tốn 1 lượt API nhưng phải tải hàng trăm file SKILL.md qua CDN, và
   thời gian dao động rất mạnh theo độ lớn của kho (đo được: 151s,
   309s, 532s cho 40 kho).

   Từ khi ngân sách kho suy theo hạn mức, số kho quét nhảy từ 40 lên
   cả 66 — và 66 kho ở nhịp xấu nhất là ~880s, vượt trần 14 phút của
   bước trong refresh-data.yml. Bị cắt giữa chừng thì KHÔNG ghi được
   gì cả: script chỉ ghi file ở cuối, nên cả lượt thành công cốc.

   Nên tự dừng TRƯỚC hạn, ghi lại những gì đã quét, rồi để lượt sau
   quét tiếp. Thà 50 kho có kết quả còn hơn 66 kho bị giết. Đổi trần
   ở workflow thì đổi luôn con số này — để thấp hơn vài phút. */
const HAN_GIAY = Number(process.env.TT_HAN_GIAY || 11 * 60);
const batDau = Date.now();

for (const r of canQuet) {
  if (conLuot != null && conLuot < 5) {
    warn(`Dừng quét sớm: hạn mức còn ${conLuot} lượt. Đã quét ${quetDuoc}/${canQuet.length} kho.`);
    break;
  }
  const troi = Math.round((Date.now() - batDau) / 1000);
  if (troi > HAN_GIAY) {
    warn(`Dừng quét sớm: đã chạy ${troi}s, quá hạn ${HAN_GIAY}s. ` +
      `Đã quét ${quetDuoc}/${canQuet.length} kho — phần còn lại để lượt sau.`);
    break;
  }
  let cay;
  try {
    cay = await gh(`https://api.github.com/repos/${r.id}/git/trees/${encodeURIComponent(r.nhanh)}?recursive=1`);
  } catch (e) {
    warn(`${r.id}: ${e.message}`);
    quetHong++;
    continue;
  }
  const ds = (cay.tree || []).filter((x) => /(^|\/)SKILL\.md$/i.test(x.path));
  if (cay.truncated) warn(`${r.id}: cây file bị GitHub cắt bớt — có thể sót skill.`);
  /* Danh sách đường dẫn dùng cho phần "file kèm theo" của bảng tua.
     Chỉ lấy blob: cây còn có cả node thư mục, kể chúng vào thì skill
     nào cũng như kèm thêm mấy file ma. */
  const duongTrongCay = (cay.tree || [])
    .filter((x) => x.type === "blob").map((x) => x.path);

  let lay = 0;
  /* Sắp theo chất lượng đường dẫn TRƯỚC khi cắt: kho lớn có gần 900
     file và cây trả theo thứ tự chữ cái, nên `docs/<ngôn ngữ>/` đứng
     trước `skills/`. Cắt thẳng 400 đầu là mất sạch bản gốc. */
  ds.sort((a, b) => diemDuong(a.path) - diemDuong(b.path));

  for (const f of ds.slice(0, MAX_SKILL_MOI_KHO)) {
    /* template/SKILL.md là mẫu trống, không phải skill thật */
    if (/^template\//i.test(f.path)) continue;
    let md;
    try {
      md = await raw(`https://raw.githubusercontent.com/${r.id}/${r.nhanh}/${f.path.split("/").map(encodeURIComponent).join("/")}`);
    } catch { continue; }
    const fm = bocFrontmatter(md);
    if (!fm || !fm.name || !fm.description) continue;

    const thuMuc = f.path.replace(/\/SKILL\.md$/i, "");
    skills.push({
      id: r.id + "/" + thuMuc,
      ten: String(fm.name).slice(0, 80),
      moTa: String(fm.description).replace(/\s+/g, " ").trim().slice(0, 900),
      kho: r.id,
      duong: thuMuc,
      chinhChu: !!r.chinhChu,
      nhom: phanNhom(fm.name, fm.description),
      sao: r.sao,
      giayPhep: fm.license ? String(fm.license).slice(0, 90) : null
    });
    /* Bảng tua để RIÊNG, không nhét vào data.js: data.js đã 1,5 MB và
       nằm trong SHELL nên mọi người tải ngay từ lần mở đầu. Nhồi thêm
       ~1 MB bảng tua là bắt cả những người không bao giờ mở chi tiết
       skill phải trả giá. Tách theo kho, tải khi cần. */
    trailer.push({ id: r.id + "/" + thuMuc, ...boTrailer(md, thuMuc, fm, duongTrongCay) });
    lay++;
  }
  quetDuoc++;
  daQuet.add(r.id);
  log(`  · ${r.id.padEnd(40)} ${String(lay).padStart(4)} skill  (còn ${conLuot ?? "?"} lượt)`);
  await nghi(150);
}

/* trùng tên giữa các kho là chuyện thường — giữ hết, nhưng đánh dấu */
const demTen = {};
skills.forEach((s) => { demTen[s.ten] = (demTen[s.ten] || 0) + 1; });
skills.forEach((s) => { s.trung = demTen[s.ten] > 1; });

skills.sort((a, b) => (b.chinhChu ? 1 : 0) - (a.chinhChu ? 1 : 0) || b.sao - a.sao ||
  String(a.ten).localeCompare(String(b.ten)));

if (!skills.length && cu?.skills?.length) {
  warn("Không quét được skill nào — giữ nguyên danh mục bản trước.");
}

/* ── không để lần chạy suy giảm thu nhỏ bảng ──────── */
if ((hongNapThang || !quetDuoc) && cu?.kho?.length) {
  const dangCo = new Set(kho.map((k) => k.id.toLowerCase()));
  let buLai = 0;
  for (const k of cu.kho) {
    if (dangCo.has(k.id.toLowerCase())) continue;
    kho.push(k);
    buLai++;
  }
  if (buLai) {
    kho.sort((a, b) => b.sao - a.sao);
    warn(`Lần chạy này suy giảm — bù ${buLai} kho từ bản trước để bảng không tụt.`);
  }
}


/* ══════════════════════════════════════════════════════
   GỘP BẢN TRÙNG
   ══════════════════════════════════════════════════════ */



/* Bản nào làm bản chuẩn: kho chính thức trước, rồi sao cao,
   rồi đường dẫn "gốc" nhất, rồi mô tả đầy đủ hơn. */
function chonChuan(v) {
  return v.slice().sort((a, b) => {
    const ka = a.kho === "anthropics/skills" ? 0 : (a.chinhChu ? 1 : 2);
    const kb = b.kho === "anthropics/skills" ? 0 : (b.chinhChu ? 1 : 2);
    if (ka !== kb) return ka - kb;
    if (b.sao !== a.sao) return b.sao - a.sao;
    const da = diemDuong(a.duong), db = diemDuong(b.duong);
    if (da !== db) return da - db;
    return String(b.moTa).length - String(a.moTa).length;
  })[0];
}

function noiDung(x) {
  return String(x || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim().slice(0, 240);
}

function gopTrung(ds) {
  const truocKhiGop = ds.length;

  /* bước 1: cùng kho + cùng tên */
  const b1 = new Map();
  for (const x of ds) {
    const k = x.kho + "|" + x.ten.toLowerCase();
    if (!b1.has(k)) b1.set(k, []);
    b1.get(k).push(x);
  }
  let boB1 = 0;
  const sau1 = [];
  for (const v of b1.values()) {
    const c = chonChuan(v);
    if (v.length > 1) {
      boB1 += v.length - 1;
      c.banSao = v.filter((x) => x !== c).map((x) => ({ kho: x.kho, duong: x.duong }));
    }
    sau1.push(c);
  }

  /* bước 2: khác kho, cùng tên VÀ cùng nội dung */
  const b2 = new Map();
  for (const x of sau1) {
    const k = x.ten.toLowerCase() + "|" + noiDung(x.moTa);
    if (!b2.has(k)) b2.set(k, []);
    b2.get(k).push(x);
  }
  let boB2 = 0;
  const sau2 = [];
  for (const v of b2.values()) {
    const c = chonChuan(v);
    if (v.length > 1) {
      boB2 += v.length - 1;
      c.banSao = (c.banSao || []).concat(
        v.filter((x) => x !== c).map((x) => ({ kho: x.kho, duong: x.duong }))
      );
    }
    sau2.push(c);
  }

  /* Còn trùng TÊN sau khi gộp = skill khác nhau cùng tên. Đánh dấu để
     giao diện nói đúng chuyện đó, thay vì để người đọc tưởng lỗi. */
  const demTen = {};
  for (const x of sau2) demTen[x.ten] = (demTen[x.ten] || 0) + 1;
  for (const x of sau2) {
    x.trungTen = demTen[x.ten] > 1;
    x.soBanSao = (x.banSao || []).length;
    if (x.banSao && x.banSao.length > 8) x.banSao = x.banSao.slice(0, 8);
    delete x.trung;
  }

  log(`  gộp trùng: ${truocKhiGop} → ${sau2.length} skill ` +
    `(cùng kho ${boB1} bản, chép chéo ${boB2} bản)`);
  const conTrung = Object.values(demTen).filter((n) => n > 1).length;
  if (conTrung) log(`             giữ ${conTrung} tên trùng — skill khác nhau, không gộp`);
  return sau2;
}

/* ── đóng gói ──────────────────────────────────────── */
const now = new Date();
const pad = (n) => String(n).padStart(2, "0");
/* Gộp thay vì thay thế: skill vừa quét, cộng skill cũ của những kho
   lần này KHÔNG đụng tới. Thay thế toàn bộ thì quét 6 kho là mất sạch
   danh mục của 20 kho lần trước. */
const cuTheoKho = new Map();
for (const x of cu?.skills || []) {
  if (daQuet.has(x.kho)) continue;      /* kho này vừa quét lại — dùng bản mới */
  cuTheoKho.set(x.id, x);
}
const dsSkill = skills.length || cuTheoKho.size
  ? [...skills, ...cuTheoKho.values()].sort(
      (a, b) => (b.chinhChu ? 1 : 0) - (a.chinhChu ? 1 : 0) || b.sao - a.sao ||
        String(a.ten).localeCompare(String(b.ten)))
  : (cu?.skills || []);
if (cuTheoKho.size) {
  log(`  gộp     : ${skills.length} skill vừa quét + ${cuTheoKho.size} giữ lại từ ${new Set([...cuTheoKho.values()].map((x) => x.kho)).size} kho chưa quét lượt này`);
}
const dsGon = gopTrung(dsSkill);
const demNhom = dsGon.reduce((m, s) => { m[s.nhom] = (m[s.nhom] || 0) + 1; return m; }, {});
/* ══════════════════════════════════════════════════════
   LỊCH SỬ MỐC · XU HƯỚNG · NHẬT KÝ ĐỔI
   ══════════════════════════════════════════════════════ */
const FLS = join(ROOT, "tang-thu-cac", "assets", "data", "lich-su.json");
const GIU_MOC = 130;   /* 130 mốc × 6 giờ ≈ 32 ngày */
const GIU_DOI = 80;

async function docLichSu() {
  if (!existsSync(FLS)) return { khoIdx: [], moc: [], doi: [] };
  try {
    const j = JSON.parse(await readFile(FLS, "utf8"));
    return { khoIdx: j.khoIdx || [], moc: j.moc || [], doi: j.doi || [] };
  } catch { return { khoIdx: [], moc: [], doi: [] }; }
}
const LS = await docLichSu();

/* Bảng chỉ mục kho dùng chung cho mọi mốc: mỗi mốc chỉ lưu MẢNG SỐ
   xếp theo khoIdx. Lưu cả tên kho trong từng mốc thì 130 mốc thành
   ~300 KB; lưu theo chỉ mục còn ~60 KB. */
for (const k of kho) if (!LS.khoIdx.includes(k.id)) LS.khoIdx.push(k.id);
const viTri = new Map(LS.khoIdx.map((id, i) => [id, i]));

const nowSec = Math.floor(Date.now() / 1000);
const saoNay = new Array(LS.khoIdx.length).fill(null);
for (const k of kho) saoNay[viTri.get(k.id)] = k.sao;

/* ── nhật ký đổi so với lần chạy trước ── */
const truocKho = new Set((cu?.kho || []).map((k) => k.id));
const nayKho = new Set(kho.map((k) => k.id));
const truocSkill = new Map((cu?.skills || []).map((x) => [x.id, x]));
const naySkill = new Map(dsGon.map((x) => [x.id, x]));

const doiLan = {
  luc: nowSec,
  khoThem: [...nayKho].filter((x) => !truocKho.has(x)),
  khoBot: [...truocKho].filter((x) => !nayKho.has(x)),
  skillThem: [...naySkill.keys()].filter((x) => !truocSkill.has(x))
    .slice(0, 60).map((id) => ({ id, ten: naySkill.get(id).ten, kho: naySkill.get(id).kho })),
  soSkillThem: [...naySkill.keys()].filter((x) => !truocSkill.has(x)).length,
  skillBot: [...truocSkill.keys()].filter((x) => !naySkill.has(x))
    .slice(0, 60).map((id) => ({ id, ten: truocSkill.get(id).ten, kho: truocSkill.get(id).kho })),
  soSkillBot: [...truocSkill.keys()].filter((x) => !naySkill.has(x)).length,
  tongSkill: dsGon.length,
  tongKho: kho.length,
  suyGiam: !!(hongNapThang || !quetDuoc)
};

/* Chỉ ghi vào nhật ký khi CÓ đổi thật. Lần chạy nào cũng ghi một dòng
   "không có gì đổi" thì nhật ký thành rác, người đọc phải lội qua
   hàng chục dòng trống mới thấy thay đổi thật. */
const coDoi = doiLan.khoThem.length || doiLan.khoBot.length ||
  doiLan.soSkillThem || doiLan.soSkillBot;
if (coDoi) {
  LS.doi.unshift(doiLan);
  LS.doi = LS.doi.slice(0, GIU_DOI);
}

/* ── mốc ── */
LS.moc.push({ luc: nowSec, sao: saoNay, soSkill: dsGon.length, soKho: kho.length });
LS.moc = LS.moc.slice(-GIU_MOC);

/* ── xu hướng: so với mốc gần nhất ở mỗi khoảng ── */
/* Chọn mốc CŨ NHẤT còn nằm trong cửa sổ, để "24 giờ" thật sự là
   quãng dài nhất ≤ 24 giờ chứ không phải mốc vừa ghi 6 giờ trước. */
/* Mốc phải NẰM TRONG cửa sổ VÀ đủ già — ít nhất một nửa tuổi cửa sổ.
   Không có ràng buộc "đủ già" thì một mốc ghi 12 phút trước cũng lọt
   vào cửa sổ 30 ngày, và chênh lệch 12 phút bị dán nhãn "xu hướng 30
   ngày". Thà báo chưa đủ dữ liệu còn hơn nói sai. */
const TUOI_TOI_THIEU = 0.5;

function mocGan(giay) {
  const dich = nowSec - giay;
  const canGia = nowSec - giay * TUOI_TOI_THIEU;
  let chon = null;
  for (const m of LS.moc) {
    if (m.luc > canGia) continue;               /* quá mới, chưa đại diện cho cửa sổ */
    if (m.luc >= dich && (!chon || m.luc < chon.luc)) chon = m;
  }
  return chon;
}

function tinhXu(giay) {
  const m = mocGan(giay);
  if (!m) return { du: false, tuoiGio: null, muc: [] };
  const muc = [];
  for (const k of kho) {
    const i = viTri.get(k.id);
    const truoc = m.sao[i];
    if (truoc == null || typeof k.sao !== "number") continue;
    const d = k.sao - truoc;
    if (d === 0) continue;
    muc.push({ id: k.id, sao: k.sao, them: d, pt: truoc ? d / truoc : null });
  }
  muc.sort((a, b) => b.them - a.them);
  return {
    du: true,
    tuoiGio: Math.round((nowSec - m.luc) / 360) / 10,
    soSkillTruoc: m.soSkill,
    soKhoTruoc: m.soKho,
    muc: muc.slice(0, 25)
  };
}

const xuHuong = {
  "24h": tinhXu(24 * 3600),
  "7d": tinhXu(7 * 86400),
  "30d": tinhXu(30 * 86400),
  soMoc: LS.moc.length,
  mocDau: LS.moc.length ? LS.moc[0].luc : null
};

await mkdir(dirname(FLS), { recursive: true });
await writeFile(FLS, JSON.stringify({ khoIdx: LS.khoIdx, moc: LS.moc, doi: LS.doi }), "utf8");
log(`  lịch sử : ${LS.moc.length} mốc · ${LS.doi.length} lần đổi đã ghi` +
  (coDoi ? ` (lần này: +${doiLan.khoThem.length} kho, +${doiLan.soSkillThem} skill)` : " (lần này không đổi)"));
for (const [ten, x] of [["24h", xuHuong["24h"]], ["7d", xuHuong["7d"]], ["30d", xuHuong["30d"]]]) {
  log(`  xu ${ten.padEnd(4)}: ` + (x.du
    ? `${x.muc.length} kho đổi sao (mốc cách ${x.tuoiGio} giờ)`
    : "chưa đủ mốc — cần thêm thời gian tích luỹ"));
}



const out = {
  generatedAt: now.toISOString(),
  date: `${pad(now.getUTCDate())}/${pad(now.getUTCMonth() + 1)}/${now.getUTCFullYear()}`,
  nguon: "api.github.com — topic:claude-skills + git/trees + raw SKILL.md",
  coToken: !!TOKEN,
  /* Giữ lại số kho của bản trước khi lần này quét được 0 — nếu không,
     tiêu đề ghi "1054 skill từ 0 kho", tự mâu thuẫn ngay trong một dòng. */
  /* Số kho có mặt trong danh mục, không phải số kho quét lượt này —
     quét theo đợt thì hai con số khác nhau, và người đọc quan tâm
     danh mục đang phủ bao nhiêu kho. */
  soKhoQuet: new Set(dsGon.map((x) => x.kho)).size,
  soKhoLuotNay: quetDuoc,
  soKhoHong: quetHong,
  demNhom,
  xuHuong,
  doiGanNhat: LS.doi.slice(0, 12),
  kho,
  skills: dsGon
};

const js = `/* ═══════════════════════════════════════════════════════
   TỰ SINH bởi scripts/build-tangthu.mjs — ĐỪNG SỬA TAY.
   Nguồn: ${out.nguon}
   Lấy lúc: ${out.generatedAt}
   ${dsGon.length} skill từ ${out.soKhoQuet} kho · bảng xếp hạng ${kho.length} kho
   ═══════════════════════════════════════════════════════ */
window.TT_DATA = ${JSON.stringify(out)};
`;
await mkdir(DIR, { recursive: true });
await writeFile(join(DIR, "data.js"), js, "utf8");

/* ── bảng tua: một file mỗi kho, tải khi cần ──────────
   Chỉ ghi lại kho THẬT SỰ quét lần này. Kho không quét thì file cũ
   của nó nằm nguyên trên đĩa — cùng luật với guard gộp-từ-bản-cũ ở
   trên, để một lượt chạy ngắn (hết giờ, hết hạn mức) không xoá sạch
   công của những lượt trước.

   Tên file thay "/" bằng "__": tên kho là `chu/kho`, để nguyên thì
   thành thư mục lồng, mà thư mục lồng lại không nằm trong `git add`
   của workflow. */
const KB = join(ROOT, "tang-thu-cac", "assets", "data", "kb");
await mkdir(KB, { recursive: true });

const theoKho = new Map();
for (const t of trailer) {
  const kho = t.id.split("/").slice(0, 2).join("/");
  if (!theoKho.has(kho)) theoKho.set(kho, []);
  theoKho.get(kho).push(t);
}
let soFile = 0, soByte = 0;
for (const [kho, ds] of theoKho) {
  const ten = kho.replace(/\//g, "__").replace(/[^A-Za-z0-9_.-]/g, "_") + ".json";
  const noi = JSON.stringify({ kho, luc: now.toISOString(), skills: ds });
  await writeFile(join(KB, ten), noi, "utf8");
  soFile++; soByte += noi.length;
}
log(`  bảng tua: ${trailer.length} skill · ${soFile} file · ${(soByte / 1024).toFixed(0)} KB (tải khi mở skill)`);

/* ── thống kê ──────────────────────────────────────── */
const show = (o) => Object.entries(o).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}=${v}`).join("  ");
log(`\n  ${dsGon.length} skill · ${dsGon.filter((s) => s.chinhChu).length} chính thức của Anthropic`);
log("  nhóm  :", show(demNhom));
log("  kho   :", `quét ${quetDuoc}, hỏng ${quetHong}, xếp hạng ${kho.length}`);
log(`  còn   : ${conLuot ?? "?"} lượt gọi API`);
log(`\n✓ đã ghi tang-thu-cac/assets/js/data.js · ${(js.length / 1024).toFixed(0)} KB`);
