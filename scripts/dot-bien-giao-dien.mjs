/* ═══════════════════════════════════════════════════════
   ĐỘT BIẾN GIAO DIỆN — đo TRẦN của bộ thước, không đo cung.

       node scripts/dot-bien-giao-dien.mjs <cung>
       node scripts/dot-bien-giao-dien.mjs <cung> --song   chỉ in con SỐNG

   ── CÂU HỎI NÓ TRẢ LỜI ───────────────────────────────────────
   Một cung 17/17 KHÔNG có nghĩa là nó đẹp. Nó có nghĩa là mười bảy
   câu hỏi đã được trả lời hết. Câu còn lại — và là câu đắt hơn —
   là *mười bảy câu ấy phủ được bao nhiêu phần của cái đáng hỏi*.

   Cách duy nhất trả lời được: CỐ Ý làm hỏng một thứ, rồi xem có
   thước nào kêu không.

     con CHẾT  = có thước bắt được  → chiều ấy đang được canh
     con SỐNG  = không ai kêu       → CHIỀU MÙ, và nó có TÊN

   Danh sách con sống chính là bản đồ chỗ hệ thống không nhìn thấy.
   Nó khác hẳn một danh sách từ khoá rút từ kho skill: mỗi con ở đây
   là một hỏng hóc CỤ THỂ, mô tả được bằng tiếng Việt, và kiểm lại
   được bằng mắt trên trang thật.

   (Một công cụ trước đó thử tìm chiều mù bằng cách đếm tần suất từ
   trong mô tả 3.702 skill. Nó ra 1.226 "chiều trống" gồm `user`,
   `building`, `create` — rác. Đã bỏ. Bài học: chiều mù phải tìm bằng
   cách CHỌC vào hệ thống, không tìm bằng cách đọc từ điển.)

   ── LUẬT TỰ CHỨNG, CHÉP TỪ BÀI HỌC KHÂM THIÊN GIÁM ───────────
   `quet-dot-bien.py` của Khâm Thiên Giám từng chạy trong lúc một lệnh
   `git rebase --autostash` cất rồi trả file giữa chừng. Nhiều lượt
   chấm chạy trên một file KHÔNG phải file bộ quét tưởng, và chiều
   lệch là chiều NGUY: file mang đột biến của lượt trước thì phiếu đỏ,
   con đang xét bị đếm là CHẾT — tức tai nạn làm phiếu ĐẸP LÊN.

   Nên ở đây, mỗi lần ghi xong là ĐỌC LẠI đĩa và đối chiếu từng byte;
   khác thì dừng hẳn. Và mỗi lần trả file về cũng đối chiếu lại lần
   nữa. Lời dặn trong văn xuôi không giữ được gì — bên kia đã có sẵn
   dòng "ĐỪNG chạy git trong lúc quét" ở đầu file và vẫn dính.

   ── VÌ SAO KHÔNG DÙNG ĐỘT BIẾN NGẪU NHIÊN ────────────────────
   Đổi bừa một ký tự trong CSS phần lớn cho ra CSS hỏng cú pháp —
   trình duyệt bỏ qua rule ấy, và "bỏ qua một rule" không phải một
   hỏng hóc người dùng gặp. Mỗi con ở đây là một hỏng hóc CÓ THẬT,
   khai rõ nó làm gì với người đọc trang.
   ═══════════════════════════════════════════════════════ */

import { readFileSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const CHI_SONG = process.argv.includes("--song");
const CUNG = process.argv.slice(2).find((a) => !a.startsWith("--"));

if (!CUNG || !existsSync(join(ROOT, CUNG, "index.html"))) {
  console.error("Dùng: node scripts/dot-bien-giao-dien.mjs <cung> [--song]");
  process.exit(2);
}

const P_HTML = join(ROOT, CUNG, "index.html");
const THU_CSS = join(ROOT, CUNG, "assets", "css");
const FS_CSS = existsSync(THU_CSS)
  ? readdirSync(THU_CSS).filter((f) => f.endsWith(".css")).map((f) => join(THU_CSS, f))
  : [];
const P_CSS = FS_CSS.find((p) => p.endsWith("app.css")) || FS_CSS[0];
if (!P_CSS) { console.error(`${CUNG}: không có CSS.`); process.exit(2); }

/* ── HƯỚNG ĐÃ ĐÓNG ───────────────────────────────────────────
   Kết quả ÂM đáng giữ đúng bằng kết quả dương: chúng ngăn một phiên
   sau làm lại trọn vẹn một chuỗi thí nghiệm đã thất bại. Lối này chép
   từ Khâm Thiên Giám, nơi mười hai hướng đã đóng được ghi lại kèm con
   số — và nhờ đó không ai đi lại.

   Mỗi mục phải nói ĐO ĐƯỢC GÌ, không chỉ nói "không được". */
const DA_DONG = [
  {
    huong: "tìm chiều mù bằng cách đếm tần suất từ trong kho skill",
    luc: "02/09/2026",
    ketQua: "1.226 chiều trống trên 712 skill giao diện, và đọc vào thì " +
      "toàn `user`, `building`, `create`, `data` — từ tiếng Anh phổ " +
      "thông, không phải chiều đo được. Công cụ đã bỏ.",
    vaSao: "Bước từ một skill sang một phép canh là bước NGỮ NGHĨA. So " +
      "chuỗi làm không nổi; phải CHỌC vào hệ thống rồi xem ai kêu, " +
      "hoặc phải có model đọc hiểu skill.",
  },
  {
    huong: "đột biến NGẪU NHIÊN trên CSS (đổi bừa một ký tự)",
    luc: "02/09/2026",
    ketQua: "phần lớn cho ra CSS hỏng cú pháp; trình duyệt bỏ qua rule ấy.",
    vaSao: "\"Trình duyệt bỏ qua một rule\" không phải hỏng hóc người " +
      "dùng gặp, nên con chết hay sống đều không nói gì về bộ thước. " +
      "Mỗi con ở đây phải là một hỏng hóc CÓ THẬT, tả được bằng lời.",
  },
];

/* ── các con ─────────────────────────────────────────────────
   `ap` nhận nội dung gốc, trả về nội dung đã đột biến — hoặc null khi
   cung này không có chỗ để áp (không phải lỗi, chỉ là không áp được).
   `canh` là mã thước ta MONG nó kêu; null nghĩa là chưa biết thước nào
   canh chuyện này, và đó chính là thứ đang đi tìm. */
const CON = [
  {
    ten: "màu chữ trùng nền",
    vi: "chữ thành vô hình — chạm đúng thứ WCAG gọi là tương phản",
    tep: "css", canh: "tuong-phan",
    ap: (t) => {
      const m = t.match(/(--(?:ink|fg|text)[\w-]*)\s*:\s*(#[0-9a-fA-F]{3,8})/);
      const n = t.match(/(--(?:bg|nen|paper)[\w-]*)\s*:\s*(#[0-9a-fA-F]{3,8})/);
      return m && n ? t.replace(m[0], `${m[1]}:${n[2]}`) : null;
    },
  },
  {
    ten: "bỏ aria-hidden của một svg",
    vi: "trình đọc màn hình đọc ra một mớ toạ độ giữa câu",
    tep: "html", canh: "nhan",
    ap: (t) => (t.includes(' aria-hidden="true"')
      ? t.replace(' aria-hidden="true"', "") : null),
  },
  {
    ten: "bỏ cỡ nội tại của một svg",
    vi: "CSS cũ còn kẹt là icon phình kín màn hình",
    tep: "html", canh: "svg-co",
    ap: (t) => {
      const m = t.match(/<svg([^>]*?)\swidth="\d+"\sheight="\d+"/);
      return m ? t.replace(m[0], `<svg${m[1]}`) : null;
    },
  },
  {
    ten: "thêm một cỡ chữ lẻ",
    vi: "thang chữ rạn thêm một nấc không ai dùng lại",
    tep: "css", canh: "thang-chu",
    ap: (t) => t + "\n.db-thu-nghiem{font-size:13.7px}\n",
  },
  {
    ten: "transition chạm bố cục",
    vi: "trình duyệt phải tính lại layout mỗi khung hình",
    tep: "css", canh: "hieu-ung",
    ap: (t) => t + "\n.db-thu-nghiem-2{transition:top .3s ease,height .3s ease}\n",
  },
  {
    ten: "bỏ :focus-visible",
    vi: "đi bằng bàn phím không biết mình đang đứng ở đâu",
    tep: "css", canh: "tieu-diem",
    ap: (t) => (t.includes(":focus-visible")
      ? t.replace(/:focus-visible/g, ":focus-KHONG-CO") : null),
  },
  {
    ten: "nhân đôi một id",
    vi: "getElementById trả thẻ đầu, phần còn lại thành vô hình với JS",
    tep: "html", canh: "id-trung",
    ap: (t) => {
      const m = t.match(/\sid="([\w-]+)"/);
      return m ? t.replace("</body>", `<div id="${m[1]}"></div>\n</body>`) : null;
    },
  },
  {
    ten: "mặt số mất tabular-nums",
    vi: "mỗi lượt cập nhật là cả bảng số nhảy ngang",
    tep: "css", canh: "so-cot",
    ap: (t) => t + "\n.db-bang-so td{font-family:var(--mono);font-size:12px}\n",
  },

  /* ── từ đây là những con CHƯA BIẾT có thước nào canh ────────
     Mỗi con là một hỏng hóc thật, người dùng gặp được. Con nào SỐNG
     là một chiều hệ thống đang mù. */
  {
    ten: "dòng chữ dài không giới hạn",
    vi: "trên màn rộng, một dòng chạy hết 2000px — mắt lạc dòng khi xuống hàng",
    tep: "css", canh: null,
    ap: (t) => (/max-width\s*:\s*\d+/.test(t)
      ? t.replace(/max-width\s*:\s*\d+(\.\d+)?(px|rem|ch|em)/g, "max-width:99999px") : null),
  },
  {
    ten: "line-height về 1",
    vi: "chữ dính nhau, đọc một đoạn dài thành mệt",
    tep: "css", canh: null,
    ap: (t) => t.replace(/line-height\s*:\s*1\.[0-9]+/g, "line-height:1"),
  },
  {
    ten: "bảng mất overflow ngang",
    vi: "trên điện thoại bảng tràn ra ngoài, cả TRANG cuộn ngang",
    tep: "css", canh: null,
    ap: (t) => (/overflow-x\s*:\s*auto/.test(t)
      ? t.replace(/overflow-x\s*:\s*auto/g, "overflow-x:visible") : null),
  },
  {
    ten: "h1 mất thứ bậc",
    vi: "tiêu đề to nhất trang bằng cỡ chữ thân bài — mắt hết chỗ neo",
    tep: "css", canh: null,
    ap: (t) => (/(^|\})\s*h1\s*\{/.test(t)
      ? t + "\nh1{font-size:1rem;font-weight:400}\n" : null),
  },
  {
    ten: "vùng bấm nhỏ hơn 24px",
    vi: "ngón tay bấm trượt — WCAG 2.2 đặt sàn 24×24 cho đích bấm",
    tep: "css", canh: null,
    ap: (t) => t + "\n.db-nut-nho{min-height:12px;height:12px;padding:0}\n",
  },
  {
    ten: "bỏ prefers-reduced-motion",
    vi: "người say chuyển động không tắt được hiệu ứng",
    tep: "css", canh: null,
    ap: (t) => (t.includes("prefers-reduced-motion")
      ? t.replace(/prefers-reduced-motion/g, "prefers-KHONG-CO") : null),
  },
  {
    ten: "bỏ lang của trang",
    vi: "trình đọc màn hình đọc tiếng Việt bằng giọng tiếng Anh",
    tep: "html", canh: null,
    ap: (t) => (/<html[^>]*\slang="/.test(t)
      ? t.replace(/(<html[^>]*)\slang="[^"]*"/, "$1") : null),
  },
  {
    ten: "ảnh mất alt",
    vi: "trình đọc màn hình đọc tên tệp, hoặc không đọc gì",
    tep: "html", canh: null,
    ap: (t) => (/<img[^>]*\salt="/.test(t)
      ? t.replace(/(<img[^>]*)\salt="[^"]*"/, "$1") : null),
  },
  {
    ten: "bỏ thẻ title",
    vi: "tab trình duyệt và kết quả tìm kiếm mất tên",
    tep: "html", canh: null,
    ap: (t) => (/<title>/.test(t) ? t.replace(/<title>[\s\S]*?<\/title>/, "") : null),
  },
  {
    ten: "bỏ meta viewport",
    vi: "điện thoại vẽ trang ở cỡ desktop rồi thu nhỏ — chữ bé li ti",
    tep: "html", canh: null,
    ap: (t) => (/<meta[^>]*name="viewport"/.test(t)
      ? t.replace(/<meta[^>]*name="viewport"[^>]*>/, "") : null),
  },
];

/* ── chạy ────────────────────────────────────────────────────
   Đọc bản gốc MỘT lần rồi giữ trong bộ nhớ. Mọi lần trả file đều trả
   về đúng bản này, và đối chiếu lại — xem "luật tự chứng" ở đầu file. */
const GOC = { css: readFileSync(P_CSS, "utf8"), html: readFileSync(P_HTML, "utf8") };
const DUONG = { css: P_CSS, html: P_HTML };

function ghiVaChung(loai, noi) {
  writeFileSync(DUONG[loai], noi);
  if (readFileSync(DUONG[loai], "utf8") !== noi) {
    console.error("\n✗ DỪNG: ghi xong đọc lại thấy KHÁC. Có tiến trình khác đang");
    console.error("  đụng cây làm việc (git, trình soạn thảo, một phiên song song).");
    console.error("  Mọi con chấm sau đây sẽ nói dối — xem luật tự chứng ở đầu file.");
    traHet();
    process.exit(8);
  }
}

function traHet() {
  for (const loai of ["css", "html"]) {
    writeFileSync(DUONG[loai], GOC[loai]);
    if (readFileSync(DUONG[loai], "utf8") !== GOC[loai]) {
      console.error(`✗ KHÔNG trả được ${DUONG[loai]} về bản gốc. Chạy: git checkout -- ${CUNG}/`);
    }
  }
}

function chamPhieu() {
  try {
    const ra = execFileSync(process.execPath,
      [join(ROOT, "scripts", "tien-hoa.mjs"), "do", CUNG],
      { encoding: "utf8", stdio: "pipe" });
    const m = ra.match(/Phiếu đo [\w-]+: (\d+)\/(\d+)/);
    if (!m) return null;
    return { dat: +m[1], tong: +m[2], truot: [...ra.matchAll(/✗ (.+?)\s{2,}/g)].map((x) => x[1].trim()) };
  } catch { return null; }
}

const nen = chamPhieu();
if (!nen) { console.error("Không chấm được phiếu gốc."); process.exit(2); }

console.log(`\n${CUNG} — phiếu gốc ${nen.dat}/${nen.tong}\n`);
console.log(`Thả ${CON.length} con đột biến, mỗi con là một hỏng hóc CÓ THẬT.\n`);

const ketQua = [];
for (const con of CON) {
  const moi = con.ap(GOC[con.tep]);
  if (moi === null || moi === GOC[con.tep]) {
    ketQua.push({ ...con, trangThai: "khong-ap-duoc" });
    continue;
  }
  let p = null;
  try {
    ghiVaChung(con.tep, moi);
    p = chamPhieu();
  } finally {
    traHet();
  }
  /* Phiếu tụt = có thước bắt được. Mẫu số đổi cũng tính là bắt được:
     một thước chuyển sang "không đo được" vì đột biến cũng là phản ứng. */
  const chet = p && (p.dat < nen.dat || p.tong !== nen.tong);
  ketQua.push({
    ...con,
    trangThai: chet ? "chet" : "song",
    thuocKeu: chet && p ? p.truot.filter((x) => !nen.truot.includes(x)) : [],
  });
}

const chet = ketQua.filter((x) => x.trangThai === "chet");
const song = ketQua.filter((x) => x.trangThai === "song");
const boQua = ketQua.filter((x) => x.trangThai === "khong-ap-duoc");

if (!CHI_SONG && chet.length) {
  console.log(`── CHẾT (${chet.length}) — có thước bắt được ──`);
  for (const c of chet) {
    console.log(`   ✓ ${c.ten}`);
    if (c.thuocKeu.length) console.log(`       thước kêu: ${c.thuocKeu.join(" · ")}`);
    else if (c.canh) console.log(`       (mẫu số đổi — thước "${c.canh}" chuyển sang không đo được)`);
  }
  console.log();
}

console.log(`── SỐNG (${song.length}) — KHÔNG thước nào kêu ──`);
if (!song.length) console.log("   (không con nào sống — bộ thước phủ hết tập con này)\n");
for (const c of song) {
  console.log(`   ✗ ${c.ten}`);
  console.log(`       ${c.vi}`);
  if (c.canh) console.log(`       ⚠ thước "${c.canh}" LẼ RA phải bắt được con này — thước đang hỏng`);
}

if (boQua.length && !CHI_SONG) {
  console.log(`\n── không áp được (${boQua.length}) ──`);
  console.log("   Cung này không có chỗ để thả con ấy vào. Không phải lỗi.");
  for (const c of boQua) console.log(`   · ${c.ten}`);
}

const hong = song.filter((x) => x.canh);
console.log(`\n${chet.length} chết · ${song.length} sống · ${boQua.length} không áp được`);
if (hong.length) {
  console.log(`\n⚠ ${hong.length} con SỐNG mà lẽ ra phải chết — đó là THƯỚC HỎNG, không phải`);
  console.log("  chiều mù. Sửa thước trước, vì một thước hỏng làm cả phiếu nói dối.");
}
/* ── ghi sổ ──────────────────────────────────────────────────
   `--ghi` đổ kết quả ra factory/chieu-mu.json. Sổ ấy là thứ NỐI bộ
   quét này với vòng tiến hoá: tỉ lệ con bị bắt là một thước ĐỘ PHỦ
   cho chính bộ thước.

   Vì sao độ phủ là loại thước khác hẳn mười chín thước kia: chúng đều
   hỏi "cung có gì hỏng không", nên hỏng thì sửa, sửa xong là xanh
   VĨNH VIỄN — mười hai cung 16/16 suốt từ 01/09 là vậy. Độ phủ hỏi
   "bộ thước có mù chỗ nào không", và nó KHÔNG bão hoà: thêm một con
   đột biến mới là tỉ lệ tụt ngay, đúng như thêm một khái niệm sách
   làm thước `phan-quyet-2026` của knowledge-os tụt.

   Sổ giữ cả DANH SÁCH con sống, có tên và có mô tả hỏng-cái-gì. Đó là
   đề bài cho ai đi thêm thước — khác hẳn một con số trần trụi. */
if (process.argv.includes("--ghi")) {
  const p = join(ROOT, "factory", "chieu-mu.json");
  let so = { ghiChu: "SINH TỰ ĐỘNG bởi scripts/dot-bien-giao-dien.mjs. Đây là ĐỀ XUẤT, không phải phép canh.", cung: {} };
  if (existsSync(p)) { try { so = JSON.parse(readFileSync(p, "utf8")); } catch { /* hỏng thì dựng lại */ } }
  so.luc = new Date().toISOString();
  so.cung[CUNG] = {
    luc: so.luc,
    phieu: `${nen.dat}/${nen.tong}`,
    apDuoc: chet.length + song.length,
    batDuoc: chet.length,
    doPhu: chet.length + song.length ? +(chet.length / (chet.length + song.length)).toFixed(3) : null,
    thuocHong: song.filter((x) => x.canh).map((x) => ({ con: x.ten, thuoc: x.canh })),
    chieuMu: song.filter((x) => !x.canh).map((x) => ({ ten: x.ten, vi: x.vi })),
  };
  so.daDong = DA_DONG;
  /* Tổng hợp lại từ ĐẦU mỗi lần, đừng cộng dồn: cung bị xoá khỏi sổ
     mà con số tổng vẫn nhớ nó thì sổ nói dối. */
  const ds = Object.values(so.cung);
  so.tong = {
    soCungDaQuet: ds.length,
    batDuoc: ds.reduce((n, x) => n + x.batDuoc, 0),
    apDuoc: ds.reduce((n, x) => n + x.apDuoc, 0),
  };
  so.tong.doPhu = so.tong.apDuoc ? +(so.tong.batDuoc / so.tong.apDuoc).toFixed(3) : null;
  writeFileSync(p, JSON.stringify(so, null, 2) + "\n");
  console.log(`\n✓ Đã ghi factory/chieu-mu.json — độ phủ toàn xưởng ` +
    `${so.tong.batDuoc}/${so.tong.apDuoc} (${Math.round(so.tong.doPhu * 100)}%) trên ${so.tong.soCungDaQuet} cung.`);
}

console.log("\nMỗi con SỐNG là một chiều hệ thống đang mù, và nó có TÊN — khác hẳn");
console.log("một danh sách từ khoá. Đó là bản đồ để quyết thước nào đáng thêm.");
