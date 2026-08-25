/* ═══════════════════════════════════════════════════════
   Sinh context tri thức cho từng cung.

   Chạy:  node knowledge-os/sinh.mjs             sinh cho mọi cung có ánh xạ phòng
          node knowledge-os/sinh.mjs ho-bo       chỉ một cung
          node knowledge-os/sinh.mjs --thu       xem sẽ ghi gì, KHÔNG ghi

   Ghi ra:  <cung>/assets/js/v/tri-thuc.js

   ── VÌ SAO KHÔNG COPY CẢ GÓI VÀO CUNG ─────────────────
   Gói lõi là 48 concept, 34 quan hệ, 10 chương, 12 cầu nối — vài
   trăm KB và còn phình. Không cung nào cần quá bảy khái niệm. Bơm
   cả gói vào trang là bắt điện thoại tải một thư viện để hiện sáu
   dòng chữ.

   Nên gói lõi ở NGUỒN, và mỗi cung nhận một lát cắt nhỏ đúng phần
   của nó. Gói lõi không nằm trong `HALLS` của scripts/build-dist.mjs
   nên nó tự ở ngoài dist/ — không lên Pages, không lên IPFS.

   ── FILE SINH RA LÀ SINH TAY, PHẢI COMMIT ─────────────
   Cùng loại với `hoang-thanh/assets/js/data.js` và ba lát cắt của
   ba runtime Python: máy sinh, nhưng KHÔNG có workflow nào chạy nó,
   nên người chạy phải commit kết quả. Đừng thêm nó vào
   scripts/node/ — một node khai nhịp mà không workflow nào gọi thì
   Bảng vận hành sẽ mãi báo "đến hạn" cho thứ không bao giờ chạy.

   Đường ghi nằm ở `assets/js/v/`, nhánh MẠNG-TRƯỚC của mọi sw.js,
   nên sửa nó KHÔNG cần nâng CACHE_VERSION.

   ── KHÔNG GHI KHI DỮ LIỆU CHƯA QUA KIỂM ───────────────
   Bước đầu tiên là chạy kiem.mjs. Dữ liệu sai mà vẫn ghi thì lỗi
   không dừng ở file JSON: nó thành chữ trên trang người ta đọc, và
   một câu giải nghĩa sai trông y hệt một câu đúng. Cùng lý do
   scripts/build-scan.mjs không cho model ghi thẳng scan.js.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync, statSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const GOI = dirname(fileURLToPath(import.meta.url));
const REPO = join(GOI, "..");
const json = async (p) => JSON.parse(await readFile(join(GOI, p), "utf8"));

const cho = process.argv.slice(2).filter((a) => !a.startsWith("--"));
const THU = process.argv.includes("--thu");

/* ── 1. kiểm trước, ghi sau ───────────────────────────── */
try {
  execFileSync(process.execPath, [join(GOI, "kiem.mjs"), "--im"], { stdio: "inherit" });
} catch {
  console.error("\n✗ Dữ liệu chưa qua kiểm — KHÔNG ghi gì cả.");
  console.error("  Sửa xong rồi chạy lại: node knowledge-os/kiem.mjs");
  process.exit(1);
}

const C = await json("data/concepts/core.json");
const R = await json("data/relations/core.json");
const B = await json("data/bridges/repo.json");
const K = await json("data/bridges/capital-os.json");
const SACH = await json("data/sources/bitcoin-standard.json");
const C26 = await json("data/2026/concepts.json");
const R26 = await json("data/2026/relations.json");

const BANG = new Map([...C, ...C26].map((x) => [x.id, x]));

/* ── 2. nhãn nguồn ────────────────────────────────────
   Đây là chỗ ranh giới nguồn đi từ dữ liệu ra tới màn hình. Bốn
   nhãn, không gộp lại được:

     sach      tác giả mô tả, có chương/trang tra lại được
     tacGia    luận điểm riêng của tác giả — đọc như một lập trường
     phanTich  SUNSWaGz suy ra, sách không nói gì về chuyện này
     repo      đo được từ chính repo/runtime này, năm 2026

   Gộp "tacGia" vào "sach" là biến một lập trường thành sự thật.
   Gộp "phanTich" vào "sach" là mượn uy tín của sách cho suy luận
   của mình. Cả hai đều là nói dối mà không câu nào sai ngữ pháp. */
const NHAN_STANCE = { source: "sach", author_claim: "tacGia", analysis: "phanTich", repo: "repo" };
const NHAN_NGUON = { book: "sach", analysis: "phanTich", repo: "repo", web: "web" };

function goiKhaiNiem(x) {
  const o = {
    en: x.label_en,
    vi: x.label_vi,
    loai: x.kind,
    nghia: x.definition_vi,
    goc: NHAN_STANCE[x.stance] || x.stance
  };
  if (x.source_chapters?.length) o.chuong = x.source_chapters;
  if (x.source_pages?.length) o.trang = x.source_pages;
  if (x.source_ref) o.nguon = x.source_ref;
  return o;
}

function goiQuanHe(x) {
  const o = {
    tu: x.from,
    loai: x.relation,
    den: x.to,
    vi: x.reason_vi,
    goc: NHAN_NGUON[x.source_type] || x.source_type,
    tin: x.confidence
  };
  if (x.chapters?.length) o.chuong = x.chapters;
  if (x.pages?.length) o.trang = x.pages;
  if (x.source_ref) o.nguon = x.source_ref;
  return o;
}

/* ── 3. một lát cắt ───────────────────────────────────── */
function latCat(h) {
  /* Tập khái niệm của cung = khái niệm mức cung + mọi khái niệm của
     từng phòng. Không lấy thêm hàng xóm một bậc: lát cắt phình lên
     thì nó thành cả gói, mà cả gói là thứ vừa cố tránh. */
  const ids = new Set(h.concepts || []);
  for (const p of h.rooms || []) for (const i of p.concepts) ids.add(i);

  /* Quan hệ sách: chỉ giữ cái có CẢ HAI đầu trong lát cắt. Một
     quan hệ trỏ ra ngoài là một dòng chữ nhắc tới khái niệm mà
     trang không có định nghĩa — người đọc gặp một cái tên trần. */
  const quanHe = R.filter((x) => ids.has(x.from) && ids.has(x.to)).map(goiQuanHe);

  /* Lớp 2026 nối VÀO lát cắt: giữ quan hệ nào có đầu `den` nằm
     trong tập, rồi kéo theo concept 2026 ở đầu `tu`. Đây là chỗ
     duy nhất lát cắt được phép mọc thêm khái niệm, và khái niệm
     mọc thêm luôn mang nhãn "repo" chứ không bao giờ nhãn "sach". */
  const lop2026 = R26.filter((x) => ids.has(x.to)).map(goiQuanHe);
  const id26 = new Set(lop2026.map((x) => x.tu));

  const khaiNiem = {};
  for (const i of [...ids, ...id26]) {
    const x = BANG.get(i);
    if (x) khaiNiem[i] = goiKhaiNiem(x);
  }

  /* Vai vốn nào chạm tới lát cắt này. Capital OS là lớp phân tích,
     nên nó đi kèm nhãn riêng chứ không lẫn vào khái niệm sách.

     Ngưỡng HAI khái niệm chung, không phải một: `counterparty_risk`
     có mặt trong sáu trong bảy vai, nên chạm-một-cái là mọi cung
     đều hiện đủ bảy vai. Một danh sách luôn đầy đủ thì không phân
     biệt được cung nào với cung nào — nó chiếm chỗ mà không nói gì. */
  const vaiVon = K.roles
    .map((r) => ({
      ma: r.id,
      ten: r.label_vi,
      khaiNiem: r.concepts.filter((i) => ids.has(i)),
      heThong: r.systems || []
    }))
    .filter((r) => r.khaiNiem.length >= 2)
    .sort((a, b) => b.khaiNiem.length - a.khaiNiem.length);

  return {
    sinhLuc: new Date().toISOString(),
    goi: "knowledge-os",
    cung: h.hall,
    vai: h.role_vi,
    y: h.example_vi,
    phong: (h.rooms || []).map((p) => ({ ma: p.id, ten: p.name_vi, y: p.note_vi, khaiNiem: p.concepts })),
    khaiNiem,
    quanHe,
    lop2026,
    vaiVon,
    nguon: {
      sach: { ten: SACH.title_vi + " (" + SACH.title + ")", tacGia: SACH.author, nam: 2018, canhBao: SACH.bias_note },
      ranhGioi:
        "Nhãn `goc` trên mỗi mục: sach = tác giả mô tả · tacGia = lập trường riêng của tác giả · " +
        "phanTich = SUNSWaGz suy ra · repo = đo được từ repo/runtime năm 2026. " +
        "Ánh xạ khái niệm sang toa/phòng của cung là phân tích, sách không nói gì về repo này."
    }
  };
}

/* ── 4. ghi ───────────────────────────────────────────── */
const DAU =
  "/* TỰ SINH bởi knowledge-os/sinh.mjs — đừng sửa tay.\n" +
  "   Nguồn: knowledge-os/data/. Sửa dữ liệu ở đó rồi sinh lại:\n" +
  "       node knowledge-os/sinh.mjs %CUNG%\n" +
  "\n" +
  "   SINH TAY, PHẢI COMMIT — không workflow nào chạy lệnh này.\n" +
  "   Nằm ở assets/js/v/ nên đi nhánh MẠNG-TRƯỚC: KHÔNG cần nâng\n" +
  "   CACHE_VERSION khi file này đổi. */\n";

const dsCung = B.hall_mappings.filter((h) => h.rooms?.length);
const lam = cho.length ? dsCung.filter((h) => cho.includes(h.hall)) : dsCung;

if (cho.length) {
  const la = new Set(dsCung.map((h) => h.hall));
  for (const c of cho) {
    if (!la.has(c)) {
      console.error(`✗ "${c}" chưa có ánh xạ phòng trong data/bridges/repo.json.`);
      console.error(`  Cung đang có ánh xạ: ${[...la].join(", ")}`);
      process.exit(2);
    }
  }
}

let n = 0;
for (const h of lam) {
  const thu = join(REPO, h.hall, "assets", "js", "v");
  if (!existsSync(join(REPO, h.hall, "index.html"))) {
    console.error(`✗ ${h.hall}: không phải cung trên đĩa — bỏ qua.`);
    continue;
  }
  const duong = join(thu, "tri-thuc.js");
  const d = latCat(h);
  const noi = DAU.replace("%CUNG%", h.hall) + "window.TRI_THUC = " + JSON.stringify(d) + ";\n";

  if (THU) {
    console.log(
      `· ${h.hall}/assets/js/v/tri-thuc.js — ${(noi.length / 1024).toFixed(1)} KB · ` +
      `${Object.keys(d.khaiNiem).length} khái niệm · ${d.quanHe.length} quan hệ · ` +
      `${d.lop2026.length} nối 2026 · ${d.phong.length} phòng · ${d.vaiVon.length} vai vốn`
    );
    continue;
  }

  await mkdir(thu, { recursive: true });
  await writeFile(duong, noi);
  n++;
  console.log(
    `✓ ${h.hall}/assets/js/v/tri-thuc.js — ${(statSync(duong).size / 1024).toFixed(1)} KB · ` +
    `${Object.keys(d.khaiNiem).length} khái niệm · ${d.quanHe.length} quan hệ · ${d.lop2026.length} nối 2026`
  );
}

if (THU) console.log("\n(--thu: chưa ghi gì.)");
else console.log(`\n${n} file. Nhớ commit — không workflow nào ghi hộ.`);
