/* ═══════════════════════════════════════════════════════
   Kiểm Knowledge OS — dữ liệu có tự khớp, và có khớp với REPO THẬT
   không.

   Chạy:  node knowledge-os/kiem.mjs
          node knowledge-os/kiem.mjs --im     (chỉ in khi có lỗi)

   Gói này là source-of-truth cho mấy cung, nên một dòng sai ở đây
   không nằm yên trong file JSON: nó được `sinh.mjs` bơm thẳng vào
   trang mà người ta đọc. Mọi phép dưới đây đều canh một kiểu hỏng
   IM LẶNG — thứ không ném lỗi, chỉ nói sai.

   ── HAI CHUYỆN PHÉP KIỂM NÀY CANH ─────────────────────
   1. RANH GIỚI NGUỒN. Ba lớp không được lẫn: sách nói gì (book),
      repo đo được gì (repo), và SUNSWaGz suy ra gì (analysis).
      Lẫn một lần là từ đó về sau không tách lại được, vì không ai
      biết dòng nào vốn thuộc lớp nào. Xem docs/SOURCE_POLICY.md.
   2. MÃ PHÒNG CÓ THẬT KHÔNG. Ánh xạ tới một mã toa/phòng không tồn
      tại thì trang vẫn mở bình thường và lặng lẽ không hiện gì —
      đúng cái bẫy mà thai-boc-tu/assets/js/toa.js đã ghi biển báo.
      Nên chỗ này đọc mã phòng từ CHÍNH mã nguồn của cung, không
      chép lại danh sách.
   ═══════════════════════════════════════════════════════ */

import { readFile, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const GOI = dirname(fileURLToPath(import.meta.url));
const REPO = join(GOI, "..");

const doc = (p) => readFile(join(GOI, p), "utf8");
const json = async (p) => JSON.parse(await doc(p));

const loi = [];
const nhac = [];
const bao = (m) => loi.push(m);
const luu = (m) => nhac.push(m);

/* ── nạp ─────────────────────────────────────────────── */
const C = await json("data/concepts/core.json");
const R = await json("data/relations/core.json");
const B = await json("data/bridges/repo.json");
const K = await json("data/bridges/capital-os.json");
const SACH = await json("data/sources/bitcoin-standard.json");
const CHI = await json("data/chapters/index.json");
const TUDIEN = await json("data/glossary/en-vi.json");
const C26 = await json("data/2026/concepts.json");
const R26 = await json("data/2026/relations.json");

const idSach = new Set(C.map((x) => x.id));
const id26 = new Set(C26.map((x) => x.id));
const idAll = new Set([...idSach, ...id26]);

const STANCE = new Set(["source", "author_claim", "analysis", "repo"]);
const NGUON_LOAI = new Set(["book", "repo", "web", "analysis"]);
const TIN = new Set(["high", "medium", "low"]);
/* Lớp 2026 chỉ được mang mấy loại này. Không phải quy ước cho đẹp:
   chúng nói rõ quan hệ với sách là gì — nối dài, chống lại, hay
   củng cố — nên không ai đọc nhầm một quan sát 2026 thành lời tác
   giả. Handoff đòi supports/challenges/extends; "carries" thêm vào
   cho quan hệ mang rủi ro, cùng nhóm nghĩa. */
const LOAI_2026 = new Set(["supports", "challenges", "extends", "carries"]);

/* Biên trang của từng chương, đọc từ sổ nguồn. Dùng để bắt locator
   bịa: một concept khai chương 3 mà trang 200 là đang trỏ vào chỗ
   khác hẳn, và không có gì báo. */
const BIEN = new Map();
for (const [so, , tu, den] of SACH.chapter_boundaries) BIEN.set(so, [tu, den]);
const TRANG_CUOI = SACH.pages;

/* ── 1. concept lớp sách ──────────────────────────────── */
{
  const thay = new Set();
  for (const x of C) {
    const ten = x.id || "(không id)";
    if (!x.id || !/^[a-z][a-z0-9_]*$/.test(x.id))
      bao(`concept "${ten}": id phải dạng chữ_thường_gạch_dưới`);
    if (thay.has(x.id)) bao(`concept "${ten}": id trùng — bản sau sẽ che bản trước`);
    thay.add(x.id);

    for (const f of ["label_en", "label_vi", "kind", "definition_vi"])
      if (!x[f]) bao(`concept "${ten}": thiếu ${f}`);

    if (!STANCE.has(x.stance))
      bao(`concept "${ten}": stance "${x.stance}" ngoài bảng ${[...STANCE].join("/")}`);

    /* Điều 2 của SOURCE_POLICY: cái gì nhận là của sách thì phải
       chỉ được ra chương và trang. Không có locator thì câu đó
       không kiểm lại được, mà không kiểm lại được thì nó là ý kiến
       của người nhập chứ không phải nội dung sách. */
    const cuaSach = x.stance === "source" || x.stance === "author_claim";
    if (cuaSach) {
      if (!x.source_chapters?.length) bao(`concept "${ten}": stance=${x.stance} mà không có source_chapters`);
      if (!x.source_pages?.length) bao(`concept "${ten}": stance=${x.stance} mà không có source_pages`);
    } else if (x.source_chapters?.length || x.source_pages?.length) {
      /* Chiều ngược lại nguy hiểm hơn: gắn chương/trang cho một
         suy luận của mình là biến phân tích thành lời tác giả, và
         người đọc sau không có cách nào phân biệt. */
      bao(`concept "${ten}": stance=${x.stance} nhưng mang chương/trang của sách — ` +
        "đó là gán phân tích thành lời tác giả (SOURCE_POLICY điều 6)");
    }

    for (const ch of x.source_chapters || [])
      if (!BIEN.has(ch)) bao(`concept "${ten}": chương ${ch} không có trong sổ nguồn`);
    for (const tr of x.source_pages || []) {
      if (tr < 1 || tr > TRANG_CUOI) { bao(`concept "${ten}": trang ${tr} ngoài sách (1–${TRANG_CUOI})`); continue; }
      const hop = (x.source_chapters || []).some((ch) => {
        const b = BIEN.get(ch);
        return b && tr >= b[0] && tr <= b[1];
      });
      if (!hop) bao(`concept "${ten}": trang ${tr} không nằm trong chương nào nó khai ` +
        `(${(x.source_chapters || []).join(", ") || "không khai chương"})`);
    }
  }
}

/* ── 2. quan hệ lớp sách ──────────────────────────────── */
for (const x of R) {
  const ten = `${x.from} -${x.relation}-> ${x.to}`;
  if (!idSach.has(x.from)) bao(`quan hệ ${ten}: "from" mồ côi`);
  if (!idSach.has(x.to)) bao(`quan hệ ${ten}: "to" mồ côi`);
  if (!x.relation) bao(`quan hệ ${ten}: thiếu động từ quan hệ`);
  if (!x.reason_vi) bao(`quan hệ ${ten}: thiếu reason_vi — quan hệ không nói vì sao là quan hệ không kiểm được`);
  if (!NGUON_LOAI.has(x.source_type)) bao(`quan hệ ${ten}: source_type "${x.source_type}" ngoài bảng`);
  if (!TIN.has(x.confidence)) bao(`quan hệ ${ten}: confidence "${x.confidence}" ngoài bảng ${[...TIN].join("/")}`);

  if (x.source_type === "book") {
    if (!x.chapters?.length || !x.pages?.length)
      bao(`quan hệ ${ten}: source_type=book mà thiếu chapters/pages`);
    for (const tr of x.pages || [])
      if (tr < 1 || tr > TRANG_CUOI) bao(`quan hệ ${ten}: trang ${tr} ngoài sách`);
  } else if (x.chapters?.length || x.pages?.length) {
    bao(`quan hệ ${ten}: source_type=${x.source_type} mà vẫn mang chương/trang sách`);
  } else if (!x.source_ref) {
    bao(`quan hệ ${ten}: source_type=${x.source_type} thì phải có source_ref chỉ ra nguồn riêng`);
  }
}

/* ── 3. lớp 2026 — TÁCH HẲN, không được đè lên sách ────
   Handoff nói thẳng: đừng sửa dữ liệu sách để "cập nhật" nó. Sách
   viết năm 2018 và nó đứng yên ở đó; thứ đổi là thế giới. Trộn hai
   lớp là mất luôn khả năng nói "chỗ này tác giả sai" — vì không
   còn bản gốc để so. */
{
  for (const x of C26) {
    const ten = x.id || "(không id)";
    if (idSach.has(x.id))
      bao(`concept 2026 "${ten}": trùng id với lớp sách — lớp 2026 nối thêm, không ghi đè`);
    if (!["repo", "analysis", "web"].includes(x.stance))
      bao(`concept 2026 "${ten}": stance phải là repo/analysis/web, không bao giờ là source`);
    if (!x.source_ref) bao(`concept 2026 "${ten}": thiếu source_ref — quan sát không chỉ được nguồn là tin đồn`);
    if (x.source_chapters?.length || x.source_pages?.length)
      bao(`concept 2026 "${ten}": mang chương/trang sách — sách 2018 không nói về chuyện của 2026`);
    if (!x.definition_vi) bao(`concept 2026 "${ten}": thiếu definition_vi`);
  }
  for (const x of R26) {
    const ten = `${x.from} -${x.relation}-> ${x.to}`;
    if (!id26.has(x.from)) bao(`quan hệ 2026 ${ten}: "from" phải là concept của lớp 2026`);
    if (!idAll.has(x.to)) bao(`quan hệ 2026 ${ten}: "to" mồ côi`);
    if (!LOAI_2026.has(x.relation))
      bao(`quan hệ 2026 ${ten}: loại "${x.relation}" ngoài ${[...LOAI_2026].join("/")}`);
    if (x.source_type === "book")
      bao(`quan hệ 2026 ${ten}: source_type=book — không được lấy sách làm bằng chứng cho dữ kiện 2026 (SOURCE_POLICY điều 4)`);
    if (!x.source_ref) bao(`quan hệ 2026 ${ten}: thiếu source_ref`);
    if (!TIN.has(x.confidence)) bao(`quan hệ 2026 ${ten}: confidence "${x.confidence}" ngoài bảng`);
    if (!x.reason_vi) bao(`quan hệ 2026 ${ten}: thiếu reason_vi`);
  }
}

/* ── 4. chương ────────────────────────────────────────── */
{
  const soChuong = new Set();
  for (const c of CHI) {
    if (soChuong.has(c.chapter)) bao(`chương ${c.chapter}: khai hai lần trong index.json`);
    soChuong.add(c.chapter);
    const b = BIEN.get(c.chapter);
    if (!b) { bao(`chương ${c.chapter}: không có trong sổ nguồn bitcoin-standard.json`); continue; }
    if (c.pages[0] !== b[0] || c.pages[1] !== b[1])
      bao(`chương ${c.chapter}: index.json nói trang ${c.pages.join("–")} còn sổ nguồn nói ${b.join("–")}`);
    for (const i of c.concepts || [])
      if (!idSach.has(i)) bao(`chương ${c.chapter}: trỏ tới concept "${i}" không có`);
    for (const p of c.points || [])
      if (p.page < b[0] || p.page > b[1])
        bao(`chương ${c.chapter}: điểm ở trang ${p.page} nằm ngoài chương (${b.join("–")})`);
    const f = `data/chapters/${c.id}.json`;
    if (!existsSync(join(GOI, f))) bao(`chương ${c.chapter}: thiếu file ${f}`);
  }
  for (const [so] of BIEN) if (!soChuong.has(so)) luu(`chương ${so} có trong sổ nguồn nhưng chưa có mục trong index.json`);
}

/* ── 5. từ điển ───────────────────────────────────────── */
for (const [en, v] of Object.entries(TUDIEN)) {
  if (!v.id) { bao(`từ điển "${en}": thiếu id`); continue; }
  if (!idAll.has(v.id)) bao(`từ điển "${en}" trỏ tới concept "${v.id}" không có`);
  if (!v.vi) bao(`từ điển "${en}": thiếu bản tiếng Việt`);
}

/* ── 6. cầu nối repo phải trỏ vào CUNG CÓ THẬT ─────────
   Một thư mục là cung khi và chỉ khi nó có index.html ngay tại gốc
   — cùng định nghĩa với scripts/kiem-quy-trinh.mjs, để hai bộ kiểm
   không bao giờ đếm ra hai con số khác nhau. */
const cung = [];
for (const ten of await readdir(REPO)) {
  if (ten.startsWith(".") || ten === "node_modules") continue;
  if (existsSync(join(REPO, ten, "index.html"))) cung.push(ten);
}
cung.sort();

/* Mã phòng đọc thẳng từ mã nguồn của cung. Chép danh sách sang đây
   là tạo bản sao thứ hai của cùng một sự thật, và bản thứ hai luôn
   là bản lệch — luật đã ghi trong CLAUDE.md, ở đây chỉ áp vào chỗ
   mới. Cung nào chưa đọc được thì NÓI RA là không kết luận được,
   đừng buộc tội. */
async function maPhong(ten) {
  if (ten === "thai-boc-tu") {
    const t = await readFile(join(REPO, "thai-boc-tu/assets/js/toa.js"), "utf8");
    const ds = [...t.matchAll(/ma:\s*"(t\d\d)"/g)].map((m) => m[1]);
    return ds.length ? new Set(ds) : null;
  }
  if (ten === "ho-bo") {
    const t = await readFile(join(REPO, "ho-bo/assets/js/app.js"), "utf8");
    const khoi = t.match(/var PHONG = \[([\s\S]*?)\n {2}\];/);
    if (!khoi) return null;
    const ds = [...khoi[1].matchAll(/ma:\s*"([a-z-]+)"/g)].map((m) => m[1]);
    return ds.length ? new Set(ds) : null;
  }
  if (ten === "thi-bac-ty") {
    const t = await readFile(join(REPO, "thi-bac-ty/index.html"), "utf8");
    const ds = [...t.matchAll(/<section class="o[^"]*" id="([a-z-]+)"/g)].map((m) => m[1]);
    return ds.length ? new Set(ds) : null;
  }
  return null;
}

{
  const thay = new Set();
  for (const h of B.hall_mappings) {
    if (thay.has(h.hall)) bao(`cầu nối repo: cung "${h.hall}" khai hai lần`);
    thay.add(h.hall);
    if (!cung.includes(h.hall))
      bao(`cầu nối repo: "${h.hall}" không phải cung trên đĩa (không có index.html ở gốc thư mục)`);
    if (!h.role_vi || !h.example_vi) bao(`cầu nối repo "${h.hall}": thiếu role_vi/example_vi`);
    for (const i of h.concepts || [])
      if (!idAll.has(i)) bao(`cầu nối repo "${h.hall}": concept "${i}" không có`);

    if (!h.rooms) continue;
    const that = await maPhong(h.hall);
    if (!that) {
      luu(`cầu nối repo "${h.hall}": không đọc được mã phòng từ mã nguồn cung — ` +
        "bộ kiểm KHÔNG kết luận gì về ánh xạ phòng của cung này.");
    }
    const maThay = new Set();
    for (const p of h.rooms) {
      if (maThay.has(p.id)) bao(`cầu nối repo "${h.hall}": phòng "${p.id}" khai hai lần`);
      maThay.add(p.id);
      if (that && !that.has(p.id))
        bao(`cầu nối repo "${h.hall}": phòng "${p.id}" KHÔNG có trong mã nguồn cung\n` +
          `        → trang vẫn mở bình thường và lặng lẽ không hiện gì. Mã có thật: ${[...that].join(", ")}`);
      if (!p.concepts?.length) bao(`cầu nối repo "${h.hall}/${p.id}": không nối concept nào`);
      if (!p.note_vi) bao(`cầu nối repo "${h.hall}/${p.id}": thiếu note_vi — ánh xạ không giải nghĩa thì vô dụng`);
      for (const i of p.concepts || [])
        if (!idAll.has(i)) bao(`cầu nối repo "${h.hall}/${p.id}": concept "${i}" không có`);
    }
    if (that) {
      const sot = [...that].filter((m) => !maThay.has(m));
      if (sot.length) luu(`${h.hall}: còn ${sot.length}/${that.size} phòng chưa ánh xạ — ${sot.join(", ")}`);
    }
  }
  if (B.stance !== "analysis")
    bao("cầu nối repo: thiếu stance=analysis ở đầu file — ánh xạ sách→cung là suy luận của SUNSWaGz, không phải lời tác giả");
  for (const c of cung) if (!thay.has(c)) luu(`cung "${c}" chưa có cầu nối nào trong repo.json`);
}

/* ── 7. Capital OS ────────────────────────────────────── */
{
  const thay = new Set();
  for (const r of K.roles) {
    if (thay.has(r.id)) bao(`Capital OS: vai "${r.id}" khai hai lần`);
    thay.add(r.id);
    if (!r.label_vi) bao(`Capital OS "${r.id}": thiếu label_vi`);
    for (const i of r.concepts || [])
      if (!idAll.has(i)) bao(`Capital OS "${r.id}": concept "${i}" không có`);
  }
}

/* ── 8. HỢP ĐỒNG V1 ───────────────────────────────────
   Mấy dòng dưới đây là thứ handoff đòi phải xong ở V1. Không có
   phép kiểm này thì một lượt sửa dữ liệu sau có thể gỡ chúng ra mà
   không ai hay: dữ liệu vẫn hợp lệ, validator vẫn xanh, chỉ có
   trang là bớt đi một mẩu giải nghĩa và không ai để ý. */
const HOP_DONG = [
  ["thai-boc-tu", "t01", ["consensus", "final_settlement"]],
  ["thai-boc-tu", "t04", ["medium_of_exchange", "unit_of_account"]],
  ["thai-boc-tu", "t05", ["salability", "price_signal"]],
  ["thai-boc-tu", "t06", ["capital_market", "interest_rate"]],
  ["ho-bo", "tien-cho", ["medium_of_exchange", "unit_of_account", "counterparty_risk"]],
  ["ho-bo", "loi-suat", ["interest_rate", "counterparty_risk"]],
  ["thi-bac-ty", "co-hoi", ["interest_rate", "capital_market", "price_signal"]]
];
for (const [c, p, phai] of HOP_DONG) {
  const h = B.hall_mappings.find((x) => x.hall === c);
  const ph = h?.rooms?.find((x) => x.id === p);
  if (!ph) { bao(`hợp đồng V1: thiếu ánh xạ ${c}/${p}`); continue; }
  const thieu = phai.filter((i) => !ph.concepts.includes(i));
  if (thieu.length) bao(`hợp đồng V1 ${c}/${p}: thiếu ${thieu.join(", ")}`);
}

/* ── 9. lát cắt đã sinh có tới được trang không ────────
   Ba cách hỏng, cả ba IM LẶNG — không lỗi, không đỏ, chỉ là trang
   thiếu mất một mẩu mà không ai để ý:

     · sinh ra file nhưng index.html không nạp  → file nằm chết trên đĩa
     · index.html nạp nhưng file chưa sinh      → 404 trong console, trang vẫn chạy
     · file sinh từ bản dữ liệu cũ hơn dữ liệu  → trang nói theo bản cũ

   Cách thứ hai là cách khó thấy nhất: service worker đi nhánh
   MẠNG-TRƯỚC cho `assets/js/v/`, gặp 404 thì rơi về cache, và cache
   rỗng thì `window.TRI_THUC` là undefined — mọi hàm vẽ đều có nhánh
   thoát êm, nên trang trông hoàn toàn bình thường. */
{
  const { statSync } = await import("node:fs");
  let moiNhat = 0;
  for (const f of ["data/concepts/core.json", "data/relations/core.json",
    "data/bridges/repo.json", "data/bridges/capital-os.json",
    "data/2026/concepts.json", "data/2026/relations.json"]) {
    try { moiNhat = Math.max(moiNhat, statSync(join(GOI, f)).mtimeMs); } catch { /* phép khác báo rồi */ }
  }

  for (const h of B.hall_mappings) {
    if (!h.rooms?.length) continue;
    const ra = join(REPO, h.hall, "assets", "js", "v", "tri-thuc.js");
    const trang = join(REPO, h.hall, "index.html");
    const coFile = existsSync(ra);
    const nap = existsSync(trang) &&
      (await readFile(trang, "utf8")).includes("assets/js/v/tri-thuc.js");

    if (!coFile && !nap) {
      luu(`${h.hall}: đã ánh xạ ${h.rooms.length} phòng nhưng chưa sinh lát cắt — ` +
        `chạy: node knowledge-os/sinh.mjs ${h.hall}`);
      continue;
    }
    if (!coFile)
      bao(`${h.hall}/index.html nạp assets/js/v/tri-thuc.js nhưng file KHÔNG có\n` +
        `        → 404 im lặng: sw.js rơi về cache rỗng, window.TRI_THUC là undefined,\n` +
        `          mọi hàm vẽ thoát êm, và trang trông hoàn toàn bình thường.\n` +
        `        Sinh: node knowledge-os/sinh.mjs ${h.hall}`);
    else if (!nap)
      bao(`${h.hall}/assets/js/v/tri-thuc.js đã sinh nhưng index.html KHÔNG nạp nó\n` +
        "        → file nằm chết trên đĩa, và không có lỗi nào báo.");
    else if (statSync(ra).mtimeMs + 1000 < moiNhat)
      luu(`${h.hall}: lát cắt sinh TRƯỚC lần sửa dữ liệu gần nhất — ` +
        `chạy lại: node knowledge-os/sinh.mjs ${h.hall}`);
  }
}

/* ── 10. concept mồ côi ───────────────────────────────
   Nhắc chứ không báo lỗi: một concept chưa nối vào đâu là việc
   chưa làm xong, không phải dữ liệu sai. */
{
  const dung = new Set();
  for (const x of R) { dung.add(x.from); dung.add(x.to); }
  for (const x of R26) { dung.add(x.from); dung.add(x.to); }
  for (const h of B.hall_mappings) {
    for (const i of h.concepts || []) dung.add(i);
    for (const p of h.rooms || []) for (const i of p.concepts) dung.add(i);
  }
  for (const r of K.roles) for (const i of r.concepts) dung.add(i);
  for (const c of CHI) for (const i of c.concepts || []) dung.add(i);
  const moCoi = C.filter((x) => !dung.has(x.id)).map((x) => x.id);
  if (moCoi.length) luu(`${moCoi.length} concept chưa nối vào đâu: ${moCoi.slice(0, 8).join(", ")}${moCoi.length > 8 ? "…" : ""}`);
}

/* ── kết quả ──────────────────────────────────────────── */
const im = process.argv.includes("--im");
const soPhong = B.hall_mappings.reduce((n, h) => n + (h.rooms?.length || 0), 0);

if (!im || loi.length) {
  console.log(
    `Knowledge OS · ${C.length} concept sách · ${R.length} quan hệ sách · ` +
    `${C26.length} concept 2026 · ${R26.length} quan hệ 2026\n` +
    `                ${CHI.length} chương · ${B.hall_mappings.length} cầu nối cung · ` +
    `${soPhong} phòng · ${K.roles.length} vai vốn\n`
  );
}

if (nhac.length && !im) {
  console.log("Nhắc:");
  for (const m of nhac) console.log("  · " + m);
  console.log();
}

if (!loi.length) {
  if (!im) console.log("✓ Dữ liệu tự khớp, và khớp với repo thật.");
  process.exit(0);
}

console.log(`✗ ${loi.length} chỗ sai:\n`);
for (const m of loi) console.log("  ✗ " + m);
console.log("\nLuật ranh giới nguồn nằm ở knowledge-os/docs/SOURCE_POLICY.md.");
process.exit(1);
