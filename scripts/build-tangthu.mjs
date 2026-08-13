/* ═══════════════════════════════════════════════════════
   Sinh dữ liệu cho Tàng Thư Các — kho tra cứu Claude Skills.

   Chạy tay:      npm run tangthu
   Chạy tự động:  .github/workflows/refresh-data.yml

   ── LẤY GÌ, TỪ ĐÂU ────────────────────────────────────
   1. Xếp hạng kho ← api.github.com/search/repositories
        q=topic:claude-skills, sắp theo sao.
   2. Danh mục skill ← với mỗi kho hàng đầu, gọi git/trees?recursive=1
        (MỘT lời gọi lấy cả cây) rồi lọc mọi file SKILL.md.
   3. Nội dung skill ← raw.githubusercontent.com
        Đọc frontmatter YAML: name + description.
        raw.* là CDN, KHÔNG tính vào hạn mức API — nên phần nặng
        nhất lại là phần rẻ nhất.

   ── HẠN MỨC ───────────────────────────────────────────
   Không có token: 60 lượt/giờ. Trong Actions có GITHUB_TOKEN:
   5.000 lượt/giờ. Script tự dùng token nếu thấy biến môi trường,
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
const SO_KHO_QUET = Number(process.env.TT_SO_KHO || (TOKEN ? 40 : 6));
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

log(TOKEN ? "· có GITHUB_TOKEN — hạn mức 5.000/giờ" : "· KHÔNG có GITHUB_TOKEN — hạn mức 60/giờ, quét ít kho thôi");

/* Kho LUÔN nạp thẳng, không trông vào kết quả tìm kiếm.
   anthropics/skills gắn thẻ `agent-skills` chứ không phải
   `claude-skills`, nên nó KHÔNG lọt vào tìm theo topic — mà đây
   lại đúng là nguồn chính thức và là nhóm duy nhất được dịch tay.
   Lần đầu tôi quên chỗ này và ra bảng 0 skill chính thức. */
const LUON_CO = ["anthropics/skills"];

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
let kho = null;
try {
  const j = await gh("https://api.github.com/search/repositories" +
    "?q=topic:claude-skills&sort=stars&order=desc&per_page=" + SO_KHO_HANG);
  if (!j.items || !j.items.length) throw new Error("không có items");
  kho = j.items.map((r) => ({
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
  log(`✓ xếp hạng  ${kho.length} kho · tổng ${j.total_count} kho gắn thẻ claude-skills`);
} catch (e) {
  warn("Không lấy được xếp hạng kho — " + e.message);
  kho = cu?.kho || null;
  if (kho) warn("Giữ bản trước (" + kho.length + " kho).");
}

if (!kho) {
  console.error("Không có xếp hạng kho và cũng không có bản cũ — không ghi đè.");
  process.exit(1);
}

/* nạp thẳng những kho bắt buộc mà tìm kiếm không trả về */
for (const ten of LUON_CO) {
  if (kho.some((k) => k.id.toLowerCase() === ten.toLowerCase())) continue;
  try {
    kho.unshift(gonRepo(await gh("https://api.github.com/repos/" + ten)));
    log(`✓ nạp thẳng ${ten} (tìm theo topic không trả về kho này)`);
  } catch (e) {
    warn(`Không nạp được ${ten} — ${e.message}`);
  }
}

/* ── 2. quét SKILL.md ──────────────────────────────── */
/* anthropics/skills luôn quét đầu tiên dù sao có thể thấp hơn kho
   khác: đây là nguồn chính thức và là nhóm duy nhất được dịch tay. */
const thuTu = [...kho].sort((a, b) => (b.chinhChu ? 1 : 0) - (a.chinhChu ? 1 : 0));
const canQuet = thuTu.slice(0, SO_KHO_QUET);

const skills = [];
let quetDuoc = 0, quetHong = 0;

for (const r of canQuet) {
  if (conLuot != null && conLuot < 5) {
    warn(`Dừng quét sớm: hạn mức còn ${conLuot} lượt. Đã quét ${quetDuoc}/${canQuet.length} kho.`);
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

  let lay = 0;
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
    lay++;
  }
  quetDuoc++;
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

/* ── đóng gói ──────────────────────────────────────── */
const now = new Date();
const pad = (n) => String(n).padStart(2, "0");
const dsSkill = skills.length ? skills : (cu?.skills || []);
const demNhom = dsSkill.reduce((m, s) => { m[s.nhom] = (m[s.nhom] || 0) + 1; return m; }, {});

const out = {
  generatedAt: now.toISOString(),
  date: `${pad(now.getUTCDate())}/${pad(now.getUTCMonth() + 1)}/${now.getUTCFullYear()}`,
  nguon: "api.github.com — topic:claude-skills + git/trees + raw SKILL.md",
  coToken: !!TOKEN,
  soKhoQuet: quetDuoc,
  soKhoHong: quetHong,
  demNhom,
  kho,
  skills: dsSkill
};

const js = `/* ═══════════════════════════════════════════════════════
   TỰ SINH bởi scripts/build-tangthu.mjs — ĐỪNG SỬA TAY.
   Nguồn: ${out.nguon}
   Lấy lúc: ${out.generatedAt}
   ${dsSkill.length} skill từ ${quetDuoc} kho · bảng xếp hạng ${kho.length} kho
   ═══════════════════════════════════════════════════════ */
window.TT_DATA = ${JSON.stringify(out)};
`;
await mkdir(DIR, { recursive: true });
await writeFile(join(DIR, "data.js"), js, "utf8");

/* ── thống kê ──────────────────────────────────────── */
const show = (o) => Object.entries(o).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}=${v}`).join("  ");
log(`\n  ${dsSkill.length} skill · ${dsSkill.filter((s) => s.chinhChu).length} chính thức của Anthropic`);
log("  nhóm  :", show(demNhom));
log("  kho   :", `quét ${quetDuoc}, hỏng ${quetHong}, xếp hạng ${kho.length}`);
log(`  còn   : ${conLuot ?? "?"} lượt gọi API`);
log(`\n✓ đã ghi tang-thu-cac/assets/js/data.js · ${(js.length / 1024).toFixed(0)} KB`);
