/* ═══════════════════════════════════════════════════════
   Sinh dữ liệu cho Hoàng Thành — rừng 15 nền văn hoá thần truyền.

   Chạy tay:  npm run hoangthanh

   ── VÌ SAO KHÔNG CHẠY TRONG GITHUB ACTIONS ────────────
   Bốn cung kia lấy số từ API công khai nên workflow chạy được.
   Cung này thì KHÔNG: nguồn là thư mục sunswagz-hub nằm NGOÀI
   repo, trên máy người dùng. Actions checkout repo này ra máy
   ảo thì không có thư mục đó, nên không có gì để quét.

   Hệ quả: chạy tay ở máy có nguồn, rồi commit file sinh ra.
   Đừng thêm bước này vào refresh-data.yml — nó sẽ luôn thấy
   thiếu nguồn và (theo nhánh dưới đây) không làm gì cả.

   ── HAI NGUỒN, HAI VAI ────────────────────────────────
   1. <nền>/*-roadmap.html  ← XƯƠNG SỐNG
        Roadmap do chính Builder dựng: nguyên (epoch) → pha
        (phase) → chương, kèm trạng thái done/locked. Đây là
        KẾ HOẠCH ĐẦY ĐỦ, gồm cả chương chưa viết.
   2. <nền>/chapters/NNN-*.md  ← NỘI DUNG
        Chương đã tinh luyện. Ghép vào roadmap theo số chương.

   Vì sao lấy roadmap làm gốc chứ không phải thư mục chapters:
   chỉ roadmap mới biết chương CHƯA viết. Hy Lạp 198/416 và
   Bắc Âu 0/382 — không đọc roadmap thì hai nền này trông như
   đã xong, và mục "đã làm được gì" trở thành vô nghĩa.
   Đã đối chiếu: số thẻ `chapter done` khớp đúng số file .md ở
   cả 15 nền, nên hai nguồn đang đồng bộ.

   ── HAI KHUÔN CHƯƠNG KHÁC NHAU ────────────────────────
   Phần lớn nền dùng khuôn Chancellor có đánh số section:
       ## 1. Chapter Identity … ## 11. Chapter Legacy …
   Riêng Trung Hoa dùng khuôn Hub Principle gọn hơn:
       # Chapter NNN — Tên
       **HP-NNN: nguyên lý tiếng Anh**
       *bản tiếng Việt*
       - [FACT] …  - Cross-Link: Ch.x, Ch.y
   Script đọc được cả hai; bài học lấy từ `Hub Lesson`
   (khuôn Chancellor) hoặc dòng HP- tiếng Việt (khuôn Trung Hoa).

   ── GHI RA GÌ ─────────────────────────────────────────
   hoang-thanh/assets/js/data.js      ~250 KB, nạp sẵn
       mục lục: 15 nền, nguyên/pha, tiến độ, bài học, mô-típ.
   hoang-thanh/assets/js/v/<ma>.js    600 KB–1,5 MB, nạp khi mở
       toàn văn chương của MỘT nền.

   Chia hai tầng vì tổng nội dung ~15 MB — nhét hết vào một file
   thì mở app lần đầu phải tải 15 MB để đọc một chương. Thư mục
   assets/js/v/ được build-dist.mjs và sw.js hiểu là "nạp theo
   yêu cầu", không nạp sẵn vào bộ nhớ offline.

   ── VIẾT TAY, KHÔNG SUY RA TỪ DỮ LIỆU ─────────────────
   · VAN_HOA: tên tiếng Việt, màu, dòng phụ.
   · MO_TIF: các mô-típ so sánh xuyên văn hoá. Định nghĩa là
     viết tay; việc GẮN chương vào mô-típ là máy dò từ khoá
     trong tiêu đề, nên có sót và có dư — app nói rõ như vậy
     chứ không trình bày như kết luận học thuật.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir, readdir, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const RA = join(ROOT, "hoang-thanh", "assets", "js");

/* Nguồn nằm ngoài repo — cạnh kinh-thanh-app, trong sunswagz-hub.
   Đổi chỗ để nguồn thì đặt biến môi trường RUNG_NGUON. */
const NGUON = process.env.RUNG_NGUON ||
  join(ROOT, "..", "sunswagz-hub", "08_world_culture_forest");

/* ── viết tay: 15 nền văn hoá ───────────────────────────
   Thứ tự ở đây là thứ tự hiện trong app: Đông Á → Nam/Tây Á →
   Địa Trung Hải → Bắc Âu → châu Mỹ → châu Phi → Đại Dương. */
const VAN_HOA = [
  { thu: "vietnamese-civilization",          ma: "viet",       ten: "Việt Nam",   phu: "Hồng Bàng · Đại Việt",           mau: "#C0392B" },
  { thu: "chinese-traditional-civilization", ma: "hoa",        ten: "Trung Hoa",  phu: "Bàn Cổ · Tam Hoàng Ngũ Đế",      mau: "#B8860B" },
  { thu: "japanese-civilization",            ma: "nhat",       ten: "Nhật Bản",   phu: "Kojiki · Thần đạo",              mau: "#8E44AD" },
  { thu: "korean-civilization",              ma: "trieu-tien", ten: "Triều Tiên", phu: "Dangun · Gojoseon",              mau: "#2E86C1" },
  { thu: "indian-civilization",              ma: "an-do",      ten: "Ấn Độ",      phu: "Vệ Đà · Mahabharata",            mau: "#D35400" },
  { thu: "persian-civilization",             ma: "ba-tu",      ten: "Ba Tư",      phu: "Zarathustra · Achaemenid",       mau: "#16A085" },
  { thu: "mesopotamian-civilization",        ma: "luong-ha",   ten: "Lưỡng Hà",   phu: "Sumer · Gilgamesh",              mau: "#8D6E63" },
  { thu: "egyptian-civilization",            ma: "ai-cap",     ten: "Ai Cập",     phu: "Ra · Osiris · Ma'at",            mau: "#C9A227" },
  { thu: "greek-civilization",               ma: "hy-lap",     ten: "Hy Lạp",     phu: "Titan · Olympus · Polis",        mau: "#2E8B62" },
  { thu: "roman-civilization",               ma: "la-ma",      ten: "La Mã",      phu: "Romulus · Cộng hoà · Đế chế",    mau: "#A93226" },
  { thu: "norse-civilization",               ma: "bac-au",     ten: "Bắc Âu",     phu: "Ginnungagap · Ragnarök",         mau: "#5D8AA8" },
  { thu: "mayan-civilization",               ma: "maya",       ten: "Maya",       phu: "Popol Vuh · Anh hùng song sinh", mau: "#1E8449" },
  { thu: "inca-civilization",                ma: "inca",       ten: "Inca",       phu: "Viracocha · Tawantinsuyu",       mau: "#CA6F1E" },
  { thu: "african-civilizations",            ma: "chau-phi",   ten: "Châu Phi",   phu: "Yoruba · Dogon · Akan",          mau: "#7D3C0A" },
  { thu: "oceania-civilizations",            ma: "dai-duong",  ten: "Đại Dương",  phu: "Polynesia · Thời Mộng",          mau: "#1F6FB2" }
];

/* ── viết tay: mô-típ so sánh xuyên văn hoá ─────────────
   Đây là phần "dòng chảy" — thứ chỉ thấy khi đặt 15 rừng cạnh
   nhau. Máy dò từ khoá trong TIÊU ĐỀ chương, không dò toàn văn:
   toàn văn nhắc tên thần ở khắp nơi, dò cả bài thì mô-típ nào
   cũng khớp mọi chương và bảng so sánh mất hết ý nghĩa. */
const MO_TIF = [
  { ma: "hon-mang", ten: "Khởi nguyên từ hỗn mang",
    hoi: "Trước khi có trời đất thì có gì?",
    tu: ["hỗn mang", "hỗn độn", "hondon", "chaos", "khoảng trống", "nguyên sơ", "khai thiên",
         "sáng thế", "ginnungagap", "vực thẳm", "before creation", "trước khai thiên"] },
  { ma: "tach-troi-dat", ten: "Tách trời khỏi đất",
    hoi: "Ai đã đẩy trời lên cao?",
    tu: ["mở trời", "opens heaven", "tách trời", "trời đất", "heaven and earth", "bàn cổ", "pangu",
         "nâng trời", "chống trời", "cột trời", "gánh bầu trời", "atlas", "lập địa"] },
  { ma: "tao-nguoi", ten: "Nặn ra con người",
    hoi: "Con người được làm từ gì — đất, ngô, hay máu thần?",
    tu: ["tạo ra con người", "creates humans", "nặn người", "tạo hình con người", "sinh ra loài người",
         "loài người", "con người đầu tiên", "người mẹ đầu tiên", "thân thể và linh hồn", "tạo người"] },
  { ma: "hong-thuy", ten: "Đại hồng thuỷ",
    hoi: "Vì sao gần như mọi nền văn hoá đều nhớ một trận lụt xoá sạch?",
    tu: ["hồng thuỷ", "hồng thủy", "đại lụt", "trận lụt", "flood", "deluge", "utnapishtim",
         "nạn lụt", "trị thuỷ", "trị thủy", "sơn tinh thuỷ tinh", "sơn tinh thủy tinh"] },
  { ma: "lua-tri-thuc", ten: "Lửa và tri thức bị đánh cắp",
    hoi: "Ai dám lấy thứ của thần trao cho người?",
    tu: ["prometheus", "ngọn lửa", "toại nhân", "suiren", "tạo chữ", "phát minh chữ", "chữ viết",
         "knotted cords", "bát quái", "bagua", "trao cho loài người", "thương hiệt"] },
  { ma: "xuong-coi-chet", ten: "Xuống cõi chết rồi trở về",
    hoi: "Vì sao anh hùng nào cũng phải đi qua cái chết một lần?",
    tu: ["âm phủ", "cõi chết", "cõi âm", "địa ngục", "duat", "xibalba", "hades", "underworld",
         "xuống âm phủ", "phục sinh", "hồi sinh", "tái sinh", "yomi", "niflheim", "cõi sau cái chết"] },
  { ma: "phan-xet", ten: "Phán xét linh hồn",
    hoi: "Sau khi chết thì bị cân đo bằng thước nào?",
    tu: ["phán xét", "cân trái tim", "trái tim và lông vũ", "ma'at", "maat", "chinvat",
         "toà án", "nghiệp", "karma", "luân hồi"] },
  { ma: "cay-the-gioi", ten: "Cây thế giới và trục vũ trụ",
    hoi: "Cái gì nối ba tầng trời — đất — cõi dưới?",
    tu: ["cây thế giới", "yggdrasil", "trục vũ trụ", "cây vũ trụ", "world tree", "núi thiêng",
         "ba cõi", "tam giới", "uku pacha", "hanan pacha", "tam tài"] },
  { ma: "song-sinh", ten: "Cặp song sinh dựng nước",
    hoi: "Vì sao nhiều nước khởi đầu bằng hai anh em?",
    tu: ["song sinh", "sinh đôi", "hai anh em", "romulus", "remus", "hunahpu", "xbalanque",
         "anh hùng song sinh", "bốn anh em", "ayar"] },
  { ma: "vua-thieng", ten: "Vua nhận mệnh trời",
    hoi: "Quyền cai trị được biện minh bằng gì?",
    tu: ["mệnh trời", "mandate of heaven", "thiên mệnh", "vương quyền", "hoàng quyền",
         "vua đầu tiên", "lập quốc", "dựng nước", "quốc hiệu", "thiên giáng", "sapa inca"] },
  { ma: "tan-the", ten: "Tận thế và tái tạo",
    hoi: "Thế giới kết thúc rồi có bắt đầu lại không?",
    tu: ["tận thế", "ragnarök", "ragnarok", "frashokereti", "saoshyant", "cứu thế",
         "kết thúc thế giới", "tái tạo", "mặt trời thứ năm", "long count", "chu kỳ vũ trụ"] },
  { ma: "to-tien", ten: "Thờ tổ tiên",
    hoi: "Người chết còn giữ vai trò gì trong làng?",
    tu: ["tổ tiên", "thờ cúng", "ancestor", "giỗ tổ", "đền thờ", "miếu", "tổ phụ",
         "thuỷ tổ", "thủy tổ", "tổ tiên thiêng"] }
];

/* ── tiện ─────────────────────────────────────────────── */
const log = (...a) => console.log(...a);
const LA_MA = { I: 1, II: 2, III: 3, IV: 4, V: 5, VI: 6, VII: 7, VIII: 8, IX: 9, X: 10,
                XI: 11, XII: 12, XIII: 13, XIV: 14, XV: 15, XVI: 16, XVII: 17, XVIII: 18,
                XIX: 19, XX: 20 };
const NHAN = ["FACT", "PRIMARY SOURCE", "TRADITION", "SCHOLARLY INTERPRETATION", "OPEN QUESTION"];

function khongDau(s) {
  return s.normalize("NFD").replace(/[̀-ͯ]/g, "")
    .replace(/đ/g, "d").replace(/Đ/g, "D").toLowerCase();
}

function goHtml(s) {
  return s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&")
    .replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
}

/* ── đọc roadmap.html → nguyên → pha → chương ──────────── */
function docRoadmap(html) {
  const nguyen = [];

  // Cắt theo từng khối <div class="epoch">
  const khoi = html.split(/<div class="epoch">/).slice(1);
  for (const k of khoi) {
    const so = /<div class="epoch-num">([\s\S]*?)<\/div>/.exec(k);
    const ten = /<div class="epoch-name">([\s\S]*?)<\/div>/.exec(k);
    const thoi = /<div class="epoch-time">([\s\S]*?)<\/div>/.exec(k);
    const chu = /<div class="epoch-hanzi">([\s\S]*?)<\/div>/.exec(k);
    const laMa = so ? goHtml(so[1]) : "?";

    const ng = {
      laMa, so: LA_MA[laMa] || 99,
      ten: ten ? goHtml(ten[1]) : null,
      thoi: thoi ? goHtml(thoi[1]) : null,
      chu: chu ? goHtml(chu[1]) : null,
      pha: []
    };

    /* Trong một nguyên: các nhãn pha xen kẽ các lưới chương.
       Cắt theo phase-label, mảnh đầu (trước nhãn đầu tiên) là
       phần header — bỏ, trừ khi nó đã chứa chương (nguyên không
       chia pha). */
    const manh = k.split(/<div class="phase-label">/);
    const day = [];
    if (/class="chapter[ "]/.test(manh[0])) day.push({ ten: null, html: manh[0] });
    for (const m of manh.slice(1)) {
      const c = /^([\s\S]*?)<\/div>([\s\S]*)$/.exec(m);
      if (c) day.push({ ten: goHtml(c[1]) || null, html: c[2] });
    }

    for (const d of day) {
      const pha = { ten: d.ten, chuong: [] };
      for (const m of d.html.matchAll(/<div class="chapter ([a-z]+)">([\s\S]*?)(?=<div class="chapter |<\/div><\/div>|$)/g)) {
        const tt = m[1];
        const than = m[2];
        const id = /<div class="chapter-id">[^<]*?(\d+)\s*<\/div>/.exec(than);
        const tn = /<div class="chapter-title">([\s\S]*?)<\/div>/.exec(than);
        const hz = /<div class="chapter-hanzi">([\s\S]*?)<\/div>/.exec(than);
        if (!id) continue;
        pha.chuong.push({
          id: Number(id[1]),
          ten: tn ? goHtml(tn[1]) : null,
          chu: hz ? goHtml(hz[1]) : null,
          tt
        });
      }
      if (pha.chuong.length) ng.pha.push(pha);
    }

    if (ng.pha.length) nguyen.push(ng);
  }

  nguyen.sort((a, b) => a.so - b.so);
  return nguyen;
}

/* ── cắt section ───────────────────────────────────────
   Lấy theo SỐ thứ tự thì hỏng: 16 chương Trung Hoa còn dùng
   Protocol v4, ở đó `## 11.` là "Certainty Map" chứ không phải
   "Chapter Legacy" như v5 — lấy nhầm thì bài học đúc kết ra
   một bảng nhãn độ chắc chắn. Nên cắt cả bài thành các section
   rồi tra theo TÊN tiêu đề. */
function catMuc(md) {
  const ra = [];
  const rx = /^##\s*(?:[\d]+(?:[-–]\d+)?\.)?\s*(.+?)\s*$/gm;
  let m, truoc = null;
  while ((m = rx.exec(md))) {
    if (truoc) truoc.than = md.slice(truoc.tu, m.index).trim();
    truoc = { ten: m[1], tu: m.index + m[0].length };
    ra.push(truoc);
  }
  if (truoc) truoc.than = md.slice(truoc.tu).trim();
  return ra;
}

function timMuc(mucs, re) {
  const m = mucs.find((x) => re.test(x.ten));
  return m ? m.than : null;
}

/* Bảng markdown và danh sách nhãn không phải câu đúc kết. */
function laVanXuoi(s) {
  if (!s) return false;
  if (/^\s*\|/.test(s)) return false;
  if ((s.match(/\|/g) || []).length >= 4) return false;
  return s.replace(/\s+/g, " ").trim().length > 40;
}

/* ── đọc một file chương ──────────────────────────────── */
function docChuong(tep, md) {
  const c = { tep, kb: Buffer.byteLength(md, "utf8"), md };

  const h1 = /^#\s*Chapter\s+(\d+)\s*[·:.—–-]\s*(.+)$/m.exec(md);
  if (h1) { c.id = Number(h1[1]); c.tenMd = h1[2].trim(); }
  if (c.id == null) {
    const m = /^(\d+)/.exec(tep);
    if (m) c.id = Number(m[1]);
  }

  const mucs = catMuc(md);
  const id1 = timMuc(mucs, /Chapter Identity/i) || "";
  const ty = /\*\*Type:\*\*\s*([^\n·]*)/.exec(id1);
  c.loai = ty ? ty[1].trim().replace(/\s+/g, " ") : null;
  const st = /\*\*Status:\*\*\s*([^\n]*)/.exec(id1);
  c.tt = st ? st[1].trim() : null;

  // nhãn độ chắc chắn — đếm trên toàn văn
  c.nhan = {};
  for (const n of NHAN) {
    const m = md.match(new RegExp("\\[" + n.replace(/ /g, "\\s+") + "\\]", "g"));
    if (m) c.nhan[n] = m.length;
  }

  // chương được nhắc tới: "Ch.012", "Ch.042, 058"
  const cheo = new Set();
  for (const m of md.matchAll(/Ch\.\s*\d{1,3}(?:\s*,\s*\d{1,3})*/g)) {
    for (const so of m[0].matchAll(/\d{1,3}/g)) {
      const n = Number(so[0]);
      if (n !== c.id) cheo.add(n);
    }
  }
  c.cheo = [...cheo].sort((a, b) => a - b);

  /* bài học — thử lần lượt, lấy cái đầu tiên ra văn xuôi:
     1. "**Hub Lesson:**" — khuôn Chancellor v5, rõ ràng nhất
     2. dòng *tiếng Việt* ngay dưới **HP-NNN: …** — khuôn Trung Hoa
     3. đoạn đầu của section có tên …Legacy — v4 lẫn v5 đều có */
  const ung = [];
  const hl = /\*\*Hub Lesson:\*\*\s*([\s\S]+?)(?=\n\n|$)/.exec(md);
  if (hl) ung.push(hl[1]);
  const hp = /^\*\*HP-\d+:[\s\S]*?\*\*\s*\n\s*\*([^*][\s\S]*?)\*\s*$/m.exec(md);
  if (hp) ung.push(hp[1]);
  /* Đoạn mở section Legacy đôi khi là một câu hỏi in đậm làm tiêu
     đề phụ ("**Tại sao chapter này quan trọng?**") — bỏ qua, lấy
     đoạn văn xuôi thật đứng sau nó. */
  const lg = timMuc(mucs, /Legacy/i);
  if (lg) for (const d of lg.split(/\n\s*\n/)) {
    if (/^\*\*[^*]*\*\*$/.test(d.trim())) continue;
    ung.push(d);
    break;
  }

  for (const u of ung) {
    if (laVanXuoi(u)) { c.hoc = u.replace(/\s+/g, " ").trim(); break; }
  }
  return c;
}

/* ── quét một nền ─────────────────────────────────────── */
async function quet(vh) {
  const thu = join(NGUON, vh.thu);
  if (!existsSync(thu)) return null;

  let tepRm = null;
  for (const f of await readdir(thu)) if (/roadmap\.html$/i.test(f)) { tepRm = f; break; }
  if (!tepRm) { log("  ⚠ " + vh.thu + ": không có roadmap.html — bỏ qua"); return null; }

  const nguyen = docRoadmap(await readFile(join(thu, tepRm), "utf8"));

  // nội dung chương
  const noi = new Map();
  let ngoai = 0;
  const thuCh = join(thu, "chapters");
  if (existsSync(thuCh)) {
    for (const t of (await readdir(thuCh)).sort()) {
      if (!t.endsWith(".md")) continue;
      const md = (await readFile(join(thuCh, t), "utf8")).replace(/\r\n/g, "\n");
      const c = docChuong(t, md);
      if (c.id != null) noi.set(c.id, c);
    }
    // chương nằm ngoài phạm vi roadmap (thư mục con `_ngoai-…`)
    for (const d of await readdir(thuCh, { withFileTypes: true })) {
      if (!d.isDirectory()) continue;
      ngoai += (await readdir(join(thuCh, d.name))).filter((f) => f.endsWith(".md")).length;
    }
  }

  let scout = 0;
  const thuSc = join(thu, "scout");
  if (existsSync(thuSc)) scout = (await readdir(thuSc)).filter((f) => f.endsWith(".md")).length;

  return { ...vh, tepRm, nguyen, noi, ngoai, scout,
           chu: nguyen.length ? nguyen[0].chu : null };
}

/* ── xu hướng: tỉ lệ nhãn theo từng nguyên ──────────────
   Càng về các nguyên sau, [TRADITION] càng nhường chỗ cho
   [FACT] — thần thoại chuyển dần thành lịch sử có bằng chứng.
   Đây là thứ chỉ đọc được khi gộp cả nghìn chương lại. */
function xuHuong(v) {
  return v.nguyen.map((ng) => {
    const d = { FACT: 0, TRADITION: 0, "SCHOLARLY INTERPRETATION": 0, "OPEN QUESTION": 0, "PRIMARY SOURCE": 0 };
    let n = 0, xong = 0;
    for (const p of ng.pha) for (const ch of p.chuong) {
      n++;
      const c = v.noi.get(ch.id);
      if (!c) continue;
      xong++;
      for (const k of NHAN) d[k] += c.nhan[k] || 0;
    }
    const tong = NHAN.reduce((s, k) => s + d[k], 0);
    return { ng: ng.laMa, ngTen: ng.ten, n, xong, tong, nhan: d };
  });
}

/* ── đúc kết: mỗi nguyên một chương tiêu biểu ────────────
   Tiêu biểu = có bài học viết ra VÀ được nhiều chương khác
   nhắc tới nhất. Chương bị nhắc nhiều là chương mà các chương
   khác phải dựa vào mới giải thích được chính mình. */
function ducKet(v) {
  const vao = new Map();
  for (const c of v.noi.values()) for (const k of c.cheo) vao.set(k, (vao.get(k) || 0) + 1);

  const ra = [];
  for (const ng of v.nguyen) {
    const ung = [];
    for (const p of ng.pha) for (const ch of p.chuong) {
      const c = v.noi.get(ch.id);
      if (c && c.hoc) ung.push({ ch, c });
    }
    if (!ung.length) continue;
    ung.sort((a, b) => (vao.get(b.ch.id) || 0) - (vao.get(a.ch.id) || 0) || a.ch.id - b.ch.id);
    const { ch, c } = ung[0];
    ra.push({
      ng: ng.laMa, ngTen: ng.ten, id: ch.id, ten: ch.ten,
      dan: vao.get(ch.id) || 0,
      loi: c.hoc.length > 460 ? c.hoc.slice(0, 457).replace(/\s+\S*$/, "") + "…" : c.hoc
    });
  }
  return ra;
}

/* ── khớp mô-típ theo từ khoá trong tiêu đề ────────────── */
function khopMoTif(vs) {
  return MO_TIF.map((m) => {
    const tuKhoa = m.tu.map(khongDau);
    const theo = [];
    for (const v of vs) {
      const hit = [];
      for (const ng of v.nguyen) for (const p of ng.pha) for (const ch of p.chuong) {
        const t = khongDau(ch.ten || "");
        if (tuKhoa.some((k) => t.includes(k))) {
          hit.push({ id: ch.id, ten: ch.ten, co: v.noi.has(ch.id) ? 1 : 0 });
        }
      }
      if (hit.length) theo.push({ vh: v.ma, ch: hit.slice(0, 8), n: hit.length });
    }
    return { ma: m.ma, ten: m.ten, hoi: m.hoi, theo, phu: theo.length };
  }).sort((a, b) => b.phu - a.phu);
}

/* ═══════════════ chạy ═══════════════ */

if (!existsSync(NGUON)) {
  log("Không thấy nguồn: " + NGUON);
  log("Giữ nguyên dữ liệu đã sinh lần trước. Đặt RUNG_NGUON nếu nguồn ở chỗ khác.");
  process.exit(0);
}

log("Nguồn: " + NGUON + "\n");
log("  nền           chương  kế hoạch  nguyên  pha  scout   toàn văn");

const vs = [];
for (const vh of VAN_HOA) {
  const v = await quet(vh);
  if (!v) { log("  ⚠ thiếu " + vh.thu); continue; }

  v.keHoach = v.nguyen.reduce((s, ng) => s + ng.pha.reduce((t, p) => t + p.chuong.length, 0), 0);
  v.soPha = v.nguyen.reduce((s, ng) => s + ng.pha.length, 0);
  v.xong = 0; v.kb = 0;
  for (const ng of v.nguyen) for (const p of ng.pha) for (const ch of p.chuong) {
    const c = v.noi.get(ch.id);
    if (c) { v.xong++; v.kb += c.kb; }
  }
  v.hoc = ducKet(v);
  v.xu = xuHuong(v);
  vs.push(v);

  log("  " + v.ten.padEnd(11) + String(v.xong).padStart(7) + String(v.keHoach).padStart(10) +
    String(v.nguyen.length).padStart(8) + String(v.soPha).padStart(5) +
    String(v.scout).padStart(7) + (v.kb / 1024).toFixed(0).padStart(8) + " KB" +
    (v.xong < v.keHoach ? "   ← còn " + (v.keHoach - v.xong) : "") +
    (v.ngoai ? "   (+" + v.ngoai + " ngoài roadmap)" : ""));
}

if (!vs.length) { console.error("Không quét được nền nào."); process.exit(1); }

const motif = khopMoTif(vs);
const gio = new Date();
const p2 = (n) => String(n).padStart(2, "0");

const mucLuc = {
  generatedAt: gio.toISOString(),
  date: p2(gio.getUTCDate()) + "/" + p2(gio.getUTCMonth() + 1) + "/" + gio.getUTCFullYear(),
  nguon: "sunswagz-hub/08_world_culture_forest",
  tong: {
    vanHoa: vs.length,
    xong: vs.reduce((s, v) => s + v.xong, 0),
    keHoach: vs.reduce((s, v) => s + v.keHoach, 0),
    nguyen: vs.reduce((s, v) => s + v.nguyen.length, 0),
    pha: vs.reduce((s, v) => s + v.soPha, 0),
    scout: vs.reduce((s, v) => s + v.scout, 0),
    ngoai: vs.reduce((s, v) => s + v.ngoai, 0),
    kb: Math.round(vs.reduce((s, v) => s + v.kb, 0) / 1024)
  },
  vh: vs.map((v) => ({
    ma: v.ma, ten: v.ten, phu: v.phu, mau: v.mau, thu: v.thu, chu: v.chu,
    xong: v.xong, keHoach: v.keHoach, scout: v.scout, ngoai: v.ngoai,
    kb: Math.round(v.kb / 1024), roadmap: v.tepRm,
    nguyen: v.nguyen.map((ng) => ({
      laMa: ng.laMa, so: ng.so, ten: ng.ten, thoi: ng.thoi, chu: ng.chu,
      n: ng.pha.reduce((s, p) => s + p.chuong.length, 0),
      xong: ng.pha.reduce((s, p) => s + p.chuong.filter((c) => v.noi.has(c.id)).length, 0),
      tu: Math.min(...ng.pha.flatMap((p) => p.chuong.map((c) => c.id))),
      den: Math.max(...ng.pha.flatMap((p) => p.chuong.map((c) => c.id))),
      pha: ng.pha.map((p) => ({
        ten: p.ten, n: p.chuong.length,
        xong: p.chuong.filter((c) => v.noi.has(c.id)).length,
        tu: p.chuong[0].id, den: p.chuong[p.chuong.length - 1].id
      }))
    })),
    hoc: v.hoc,
    xu: v.xu
  })),
  motif
};

await mkdir(join(RA, "v"), { recursive: true });
const dau = "/* TỰ SINH — đừng sửa tay. Nguồn: scripts/build-hoangthanh.mjs */\n";

await writeFile(join(RA, "data.js"),
  dau + "window.RUNG = " + JSON.stringify(mucLuc, null, 1) + ";\n", "utf8");

/* Chỉ mục tìm — chỉ số chương + tiêu đề + cờ "đã có nội dung".
   Tách riêng vì tìm kiếm phải chạy trên CẢ 15 nền, mà nạp cả 15
   file toàn văn thì mất 15 MB. Nạp file này lúc người dùng gõ
   chữ đầu tiên, không nạp lúc mở app. */
const tim = vs.map((v) => ({
  ma: v.ma,
  ch: v.nguyen.flatMap((ng) =>
    ng.pha.flatMap((p) => p.chuong.map((c) => [c.id, c.ten, v.noi.has(c.id) ? 1 : 0, ng.laMa])))
}));
await writeFile(join(RA, "v", "_tim.js"),
  dau + "window.RUNG_TIM_NAP && window.RUNG_TIM_NAP(" + JSON.stringify(tim) + ");\n", "utf8");

for (const v of vs) {
  const chuong = [];
  for (const ng of v.nguyen) {
    for (let i = 0; i < ng.pha.length; i++) {
      for (const ch of ng.pha[i].chuong) {
        const c = v.noi.get(ch.id);
        chuong.push({
          id: ch.id, ten: ch.ten, chu: ch.chu, tt: ch.tt,
          ng: ng.laMa, ph: i,
          loai: c ? c.loai : null, cheo: c ? c.cheo : [],
          nhan: c ? c.nhan : {}, kb: c ? c.kb : 0,
          md: c ? c.md : null
        });
      }
    }
  }
  await writeFile(join(RA, "v", v.ma + ".js"),
    dau + "window.RUNG_NAP && window.RUNG_NAP(" +
    JSON.stringify({ ma: v.ma, chuong }) + ");\n", "utf8");
}

const t = mucLuc.tong;
log("\n✓ data.js · " + (Buffer.byteLength(JSON.stringify(mucLuc)) / 1024).toFixed(0) + " KB");
log("✓ v/*.js  · " + vs.length + " tệp · " + t.kb + " KB toàn văn");
log("  " + t.vanHoa + " nền · " + t.xong + "/" + t.keHoach + " chương (" +
  ((t.xong / t.keHoach) * 100).toFixed(1) + "%) · " + t.nguyen + " nguyên · " + t.pha + " pha");
log("  " + motif.filter((m) => m.phu > 1).length + "/" + motif.length +
  " mô-típ bắt được ở từ hai nền trở lên");
