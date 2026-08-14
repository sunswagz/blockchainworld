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
/* Không token: 60 lượt/giờ. Trừ 4 truy vấn tìm kiếm và ~8 lượt nạp
   thẳng, còn dư nhiều cho 14 lượt lấy cây repo. Có token thì thoải mái. */
const SO_KHO_QUET = Number(process.env.TT_SO_KHO || (TOKEN ? 40 : 14));
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

log(TOKEN ? "· có token — hạn mức 1.000/giờ (GITHUB_TOKEN) hoặc 5.000/giờ (token cá nhân)"
          : "· KHÔNG có token — hạn mức 60/giờ mỗi IP, quét ít kho thôi");

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
const daQuet = new Set();   /* kho thật sự quét trong lần chạy này */
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
const demNhom = dsSkill.reduce((m, s) => { m[s.nhom] = (m[s.nhom] || 0) + 1; return m; }, {});
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
const naySkill = new Map(dsSkill.map((x) => [x.id, x]));

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
  tongSkill: dsSkill.length,
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
LS.moc.push({ luc: nowSec, sao: saoNay, soSkill: dsSkill.length, soKho: kho.length });
LS.moc = LS.moc.slice(-GIU_MOC);

/* ── xu hướng: so với mốc gần nhất ở mỗi khoảng ── */
/* Chọn mốc CŨ NHẤT còn nằm trong cửa sổ, để "24 giờ" thật sự là
   quãng dài nhất ≤ 24 giờ chứ không phải mốc vừa ghi 6 giờ trước. */
function mocGan(giay) {
  const dich = nowSec - giay;
  let chon = null;
  for (const m of LS.moc) {
    if (m.luc > nowSec - 60) continue;          /* bỏ mốc vừa ghi */
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
  soKhoQuet: new Set(dsSkill.map((x) => x.kho)).size,
  soKhoLuotNay: quetDuoc,
  soKhoHong: quetHong,
  demNhom,
  xuHuong,
  doiGanNhat: LS.doi.slice(0, 12),
  kho,
  skills: dsSkill
};

const js = `/* ═══════════════════════════════════════════════════════
   TỰ SINH bởi scripts/build-tangthu.mjs — ĐỪNG SỬA TAY.
   Nguồn: ${out.nguon}
   Lấy lúc: ${out.generatedAt}
   ${dsSkill.length} skill từ ${out.soKhoQuet} kho · bảng xếp hạng ${kho.length} kho
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
