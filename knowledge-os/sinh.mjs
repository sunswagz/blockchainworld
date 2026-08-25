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

   ── PHẦN VẼ CŨNG SINH RA TỪ ĐÂY ───────────────────────
   File sinh ra mang CẢ dữ liệu lẫn hàm vẽ. Chín cung dùng chung một
   khuôn HTML, nên viết chín bản là chín chỗ để lệch nhau — và bản
   thứ chín bao giờ cũng là bản quên sửa.

   Đây đúng lối `scripts/build-halls.mjs` đã đi: một khai báo ở
   `scripts/cung.mjs`, sinh ra `halls.js` cho MỌI cung. Cung chỉ cần
   một dòng:

       than.innerHTML = veGiHetPhong() + (TT ? TT.ve(maPhong) : "");

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

/* ── 4. phần vẽ, chung cho mọi cung ───────────────────
   ES5 thuần, không phụ thuộc gì ngoài `document`. Chín cung dùng
   đúng khuôn này nên lớp CSS trùng tên ở cả chín — mỗi cung chỉ
   khai màu bằng biến bảng màu của chính nó.

   `gan()` dùng insertBefore chứ không insertAdjacentElement/HTML:
   cả hai chạy trên trình duyệt, nhưng DOM giả của
   scripts/tien-hoa.mjs chỉ có insertBefore — và cổng chặn của vòng
   tiến hoá chấm bằng DOM giả đó, nên dùng API nó không có là tự
   chấm trượt một cung hoàn toàn lành. Đã cắn một lần. */
const VE = `
(function () {
  "use strict";
  var T = window.TRI_THUC;
  if (!T) return;

  var TEN = { sach: "sách", tacGia: "tác giả", phanTich: "phân tích", repo: "repo", web: "web" };
  var GIAI = {
    sach: "Tác giả mô tả — tra lại được bằng chương/trang",
    tacGia: "Lập trường riêng của tác giả, không phải sự thật đo được",
    phanTich: "SUNSWaGz suy ra — sách không nói gì về chuyện này",
    repo: "Đo được từ repo/runtime này, năm 2026",
    web: "Nguồn ngoài"
  };

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function chip(g) {
    return '<i class="tt-g" data-g="' + esc(g) + '" title="' + esc(GIAI[g] || "") + '">' +
      esc(TEN[g] || g) + "</i>";
  }
  function viTri(k) {
    if (!k.chuong || !k.chuong.length) return k.nguon || "";
    return "ch." + k.chuong.join(",") + (k.trang && k.trang.length ? " tr." + k.trang.join(",") : "");
  }
  function timPhong(ma) {
    var ds = T.phong || [], i;
    for (i = 0; i < ds.length; i++) if (ds[i].ma === ma) return ds[i];
    return null;
  }

  /* Trả về chuỗi HTML cho một phòng, hoặc "" nếu phòng chưa ánh xạ.
     Chưa ánh xạ thì KHÔNG vẽ khung rỗng: một khung có tiêu đề mà
     không có nội dung đọc ra là "chỗ này hỏng", chứ không phải
     "chỗ này chưa làm". */
  function ve(ma) {
    var p = timPhong(ma);
    if (!p) return "";

    var the = "", i, k, vt;
    for (i = 0; i < p.khaiNiem.length; i++) {
      k = T.khaiNiem[p.khaiNiem[i]];
      if (!k) continue;
      vt = viTri(k);
      the += '<div class="tt-k"><div class="tt-kd"><b>' + esc(k.vi) + "</b>" + chip(k.goc) +
        (vt ? '<span class="tt-vt">' + esc(vt) + "</span>" : "") + "</div><p>" + esc(k.nghia) + "</p></div>";
    }

    /* Lớp 2018→2026 vẽ RIÊNG dưới một tiêu đề riêng. Trộn nó vào
       lưới trên là đúng cái nhầm mà cả lớp này dựng ra để chặn. */
    var noi = "", ds = T.lop2026 || [], r, tu, den;
    for (i = 0; i < ds.length; i++) {
      r = ds[i];
      if (p.khaiNiem.indexOf(r.den) === -1) continue;
      tu = T.khaiNiem[r.tu]; den = T.khaiNiem[r.den];
      noi += "<p><b>" + esc(tu ? tu.vi : r.tu) + "</b>" + chip(r.goc) +
        '<span class="tt-loai">' + esc(r.loai) + "</span><b>" + esc(den ? den.vi : r.den) + "</b>" +
        '<span class="tt-tin">tin ' + esc(r.tin) + "</span>" +
        '<span class="tt-vi">' + esc(r.vi) + "</span></p>";
    }

    return '<section class="tt"><h3 class="tt-d">Vấn đề kinh tế gốc' +
      '<span class="tt-n">' + p.khaiNiem.length + " khái niệm</span></h3>" +
      '<p class="tt-y">' + esc(p.y) + "</p>" +
      (the ? '<div class="tt-luoi">' + the + "</div>" : "") +
      (noi ? '<div class="tt-26"><h4>2018 → 2026</h4>' + noi + "</div>" : "") +
      '<p class="tt-chan">Nền: «' + esc(T.nguon.sach.ten) + "» (" + esc(T.nguon.sach.tacGia) + ", " +
      esc(T.nguon.sach.nam) + "). Ánh xạ khái niệm sang phòng là <b>phân tích</b> của SUNSWaGz — " +
      "sách không nói gì về repo này. Sinh từ <code>knowledge-os/</code>.</p></section>";
  }

  /* Nối vào CUỐI thẻ chứa nội dung phòng. Dùng cho cung vẽ lại cả
     thân theo tuyến (\`than.innerHTML = ...\`).

     appendChild chứ KHÔNG \`host.innerHTML += ...\`: cộng chuỗi là
     phân tích lại toàn bộ cây con, và mọi listener đã gắn vào thẻ
     con bên trong đều rụng — hỏng im lặng, không lỗi nào báo, chỉ
     là bấm vào không ăn nữa. */
  function them(host, ma) {
    var s = ve(ma);
    if (!s || !host) return false;
    /* Gỡ khối cũ trước khi nối khối mới. Cung nào vẽ lại CÙNG một
       tuyến hai lần — điều hướng sâu, mở ngăn kéo, bấm lại đúng mục
       đang đứng — sẽ gọi lại chỗ này, và hai khối chồng nhau trông
       hệt như một trang dài chứ không giống lỗi. */
    var cu = host.querySelector ? host.querySelector(".tt-hop") : null;
    if (cu && cu.remove) cu.remove();
    var w = document.createElement("div");
    w.className = "tt-hop";
    w.innerHTML = s;
    host.appendChild(w);
    return true;
  }

  /* Chèn vào ngay sau <h2> của một thẻ đã có sẵn trong index.html.
     Dùng cho cung dựng trang tĩnh chứ không vẽ lại theo tuyến. */
  function gan(ma, muc) {
    var s = ve(ma);
    if (!s || !muc) return false;
    var w = document.createElement("div");
    w.className = "tt-hop";
    w.innerHTML = s;
    var h = muc.querySelector ? muc.querySelector("h2") : null;
    muc.insertBefore(w, h && h.nextSibling ? h.nextSibling : null);
    return true;
  }

  /* Một dòng nói lát cắt tri thức đến từ đâu, để nối vào chân trang.
     Gọi SAU khi cung đã vẽ xong chân trang của nó: phần lớn cung GÁN
     textContent cho thẻ đó, nên nối trước là bị xoá sạch mà không có
     lỗi nào báo. */
  function chan() {
    return " Lớp giải nghĩa: knowledge-os, nền là «" + T.nguon.sach.ten + "» (" +
      T.nguon.sach.tacGia + ", " + T.nguon.sach.nam +
      "). Nhãn nguồn trên từng dòng: sách · tác giả · phân tích · repo.";
  }

  T.ve = ve;
  T.them = them;
  T.gan = gan;
  T.chan = chan;
  T.co = function (ma) { return !!timPhong(ma); };
})();
`;

/* ── 5. ghi ───────────────────────────────────────────── */
const DAU =
  "/* TỰ SINH bởi knowledge-os/sinh.mjs — đừng sửa tay.\n" +
  "   Nguồn: knowledge-os/data/. Sửa dữ liệu ở đó rồi sinh lại:\n" +
  "       node knowledge-os/sinh.mjs %CUNG%\n" +
  "\n" +
  "   Mang CẢ dữ liệu lẫn phần vẽ — khuôn HTML chung cho mọi cung,\n" +
  "   viết một lần trong sinh.mjs. Cung gọi TRI_THUC.ve(maPhong).\n" +
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
  const noi = DAU.replace("%CUNG%", h.hall) + "window.TRI_THUC = " + JSON.stringify(d) + ";\n" + VE;

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
    `✓ ${h.hall.padEnd(16)} ${(statSync(duong).size / 1024).toFixed(1).padStart(5)} KB · ` +
    `${String(d.phong.length).padStart(2)} phòng · ${String(Object.keys(d.khaiNiem).length).padStart(2)} khái niệm · ` +
    `${String(d.quanHe.length).padStart(2)} quan hệ · ${String(d.lop2026.length).padStart(2)} nối 2026`
  );
}

if (THU) console.log("\n(--thu: chưa ghi gì.)");
else console.log(`\n${n} file. Nhớ commit — không workflow nào ghi hộ.`);
