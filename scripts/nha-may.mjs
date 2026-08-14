/* ═══════════════════════════════════════════════════════
   LÕI NHÀ MÁY — sổ đăng ký node + sổ ghi lượt chạy.

   Trước file này, "nhịp chạy" của hệ sinh thái nằm rải ở ba chỗ
   không chỗ nào biết chỗ nào:

     · cron trong .github/workflows/*.yml   — chạy lúc mấy giờ
     · thứ tự các bước trong workflow        — chạy cái gì
     · scripts/tuoi-du-lieu.mjs              — bao lâu thì coi là cũ

   Ba chỗ đó phải khớp nhau nhưng không có gì bắt chúng khớp. Đổi
   nhịp một cung là sửa tay cả ba, và sót một chỗ thì hệ quả im
   lặng: bot vẫn chạy, `npm run kiem` vẫn xanh, chỉ có số liệu là
   sai nhịp — đúng loại hỏng mà cả CLAUDE.md sinh ra để chặn.

   Giờ nhịp nằm ở NODE bên dưới, một chỗ. cron trong workflow chỉ
   còn là TRẦN — "cứ 6 giờ ngó một lần xem có gì đến hạn không" —
   còn ĐẾN HẠN HAY CHƯA thì hỏi file này. Hệ quả: đổi nhịp một
   cung là sửa đúng một con số, không đụng YAML.

   ── BA VIỆC FILE NÀY LÀM ──────────────────────────────
     sổ đăng ký   NODE + factory/registry.json   (ai chạy, nhịp nào)
     sổ ghi       factory/state.json             (lượt vừa rồi ra sao)
     chiếu        tao-bien-xu/assets/js/v/van-hanh.js
                  → Tạo Biện Xứ đọc file này để hiện Bảng vận hành

   ── LỆNH ──────────────────────────────────────────────
     node scripts/nha-may.mjs so-dang-ky   sinh lại factory/registry.json
     node scripts/nha-may.mjs den-han      in các node đến hạn (workflow đọc)
     node scripts/nha-may.mjs ghi <ma> <ok|loi|bo-qua> [--giay N] [--ghi "..."]
     node scripts/nha-may.mjs chieu        sinh van-hanh.js cho webapp
     node scripts/nha-may.mjs bang         in bảng cho người đọc

   ── THÊM MỘT NODE ─────────────────────────────────────
   Thêm một khối vào NODE. Nếu node ghi ra file thì MỌI đường dẫn
   nó `writeFile` phải nằm trong `ra`, và `npm run kiem` sẽ bắt
   `ra` phải khớp với `git add` trong workflow lẫn danh sách "File
   do workflow tự sinh" trong CLAUDE.md. Đó là cái bẫy đã cắn hai
   lần (thư mục logo bị sót → ảnh vỡ trên site, không lỗi nào báo).
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { CUNG } from "./cung.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

export const DUONG_SO = "factory/registry.json";
export const DUONG_TRANG_THAI = "factory/state.json";
export const DUONG_CHIEU = "tao-bien-xu/assets/js/v/van-hanh.js";

/* Nhật ký giữ bao nhiêu dòng. 200 ≈ hai tuần ở nhịp 6 giờ với
   9 node — đủ để nhìn ra một node hỏng lặp lại, chưa đủ to để
   file thành gánh nặng (mỗi dòng ~110 byte → ~22 KB). */
const TRAN_NHAT_KY = 200;

/* ═══════════════ SỔ ĐĂNG KÝ ═══════════════

   `tram` là máy nào trong 18 máy của Tạo Biện Xứ chịu trách nhiệm
   cho node này. Không phải trang trí: Bảng vận hành dùng nó để nối
   lượt chạy THẬT vào đúng ô trên Sơ đồ nhà máy, nên mô hình 18 máy
   thôi mô tả một xưởng tưởng tượng.

     che: "script" — chạy bằng node script, xác định, không tốn model
          "claude" — cần phán đoán, gọi model, TỐN TIỀN hoặc TỐN QUOTA
          "tay"    — người chạy ở máy mình (nguồn nằm ngoài repo)
          "theo"   — không có nhịp riêng, chạy khi thứ khác đổi

     nhip: số giờ giữa hai lượt. 0 = không tự chạy bao giờ.
           Đây là SỐ THẬT quyết định node có chạy hay không —
           cron trong workflow chỉ là trần. */
export const NODE = [
  {
    ma: "kinh-thanh", ten: "Số liệu Kinh Thành", cung: "kinh-thanh",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-live.mjs",
    ra: ["kinh-thanh/assets/js/data/live.js",
         "kinh-thanh/assets/js/data/provenance.js",
         "kinh-thanh/assets/data/history.json"],
    y: "TVL và số on-chain 9 quốc gia L1, lấy từ DefiLlama."
  },
  {
    ma: "do-sat-vien", ten: "Bảng xét Đô Sát Viện", cung: "do-sat-vien",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-l2beat.mjs",
    ra: ["do-sat-vien/assets/js/data.js", "do-sat-vien/assets/logos/"],
    y: "Xếp hạng Layer 2 theo L2BEAT, kèm logo tải về."
  },
  {
    ma: "cong-bo", ten: "Đồ nghề Công Bộ", cung: "cong-bo",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-congbo.mjs",
    ra: ["cong-bo/assets/js/data.js", "cong-bo/assets/js/logos.js",
         "cong-bo/assets/js/v/nhat-ky.js", "cong-bo/assets/logos/"],
    y: "Bộ công cụ onchain. Nguồn có một phần là host staging của L2BEAT nên hay ngã."
  },
  {
    ma: "tang-thu-cac", ten: "Kho skill Tàng Thư Các", cung: "tang-thu-cac",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-tangthu.mjs",
    ra: ["tang-thu-cac/assets/js/data.js", "tang-thu-cac/assets/data/"],
    y: "Quét kho Claude Skills trên GitHub. Bước chậm nhất — có lượt 532 giây."
  },
  /* Đài Quan Trắc có HAI node, và cặp này là ví dụ rõ nhất trong repo
     cho luật "đo được thì đừng để model đoán":

       quan-trac-do    ba nguồn số, so ngưỡng số học → miễn phí, xác định
       dai-quan-trac   đọc tin rồi viết một câu    → cần phán đoán, tốn tiền

     Cùng một cung, cùng một câu hỏi ("tình hình có căng không"), nhưng
     phần trả lời được bằng số thì đã tách hẳn ra khỏi phần cần model.
     Nhờ vậy khi lịch quét AI phải tắt vì tiền — đã xảy ra 14/08 — cung
     vẫn còn đèn xanh/vàng/đỏ chạy đều 4 lượt/ngày. */
  {
    ma: "quan-trac-do", ten: "Bảng cảnh báo Quan Trắc", cung: "dai-quan-trac",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-quantrac.mjs",
    ra: ["dai-quan-trac/assets/js/do.js"],
    y: "Ba nguồn miễn phí không cần khoá (Yahoo Finance, open.er-api, GDELT), " +
       "so ngưỡng số học rồi tự đặt đèn. KHÔNG gọi AI."
  },
  {
    ma: "dai-quan-trac", ten: "Bản quét Đài Quan Trắc", cung: "dai-quan-trac",
    tram: "M07", che: "claude", nhip: 24,
    lenh: "node scripts/build-scan.mjs",
    ra: ["dai-quan-trac/assets/js/scan.js"],
    y: "Việc DUY NHẤT trong xưởng thật sự cần phán đoán: đọc tin 7 ngày " +
       "rồi viết một câu tiếng Việt + phân loại xanh/vàng/đỏ."
  },
  {
    ma: "dong-dau", ten: "Đóng dấu bản số liệu",
    tram: "M16", che: "script", nhip: 6,
    lenh: "node scripts/pin-snapshot.mjs",
    ra: [],
    y: "Pin bản số liệu 1,8 KB lên IPFS. Tự bỏ qua nếu sha256 trùng bản trước."
  },
  {
    ma: "bao-cao", ten: "Báo cáo sức khoẻ xưởng",
    tram: "M18", che: "claude", nhip: 24,
    lenh: "anthropics/claude-code-action",
    ra: ["factory/bao-cao.md"],
    y: "Claude Code Action đọc state.json rồi viết vài dòng tiếng Việt: " +
       "node nào đang ốm, ốm từ bao giờ, nên xem chỗ nào trước."
  },
  {
    ma: "hoang-thanh", ten: "Rừng văn hoá Hoàng Thành", cung: "hoang-thanh",
    tram: "M12", che: "tay", nhip: 0,
    lenh: "npm run hoangthanh",
    ra: ["hoang-thanh/assets/js/data.js", "hoang-thanh/assets/js/v/"],
    y: "Nguồn nằm NGOÀI repo (sunswagz-hub/08_world_culture_forest) nên " +
       "Actions không quét được. Chạy tay rồi commit là cách duy nhất."
  },
  {
    ma: "giao-hang", ten: "Giao hàng lên Pages",
    tram: "M16", che: "theo", nhip: 0,
    lenh: ".github/workflows/deploy-pages.yml",
    ra: [],
    y: "Không có nhịp riêng — chạy khi có commit số liệu. 27/27 lượt thành công."
  }
];

/* ── Ràng buộc kiểm ngay lúc nạp module ───────────────────
   Đặt ở đây chứ không ở kiem-quy-trinh.mjs là có chủ ý: mọi thứ
   dùng sổ đăng ký (workflow, bộ soát, lệnh chiếu) đều phải import
   file này, nên không có đường nào chạy được với một sổ sai. Để
   phép kiểm ở nơi khác thì nó chỉ chặn người nhớ chạy nó. */
{
  const maCung = new Set(CUNG.map((c) => c.ma));
  const thay = new Set();
  for (const n of NODE) {
    if (thay.has(n.ma)) throw new Error(`nha-may: node trùng mã "${n.ma}"`);
    thay.add(n.ma);
    if (n.cung && !maCung.has(n.cung))
      throw new Error(`nha-may: node "${n.ma}" trỏ tới cung không có thật "${n.cung}"`);
    if (!/^M\d\d$/.test(n.tram))
      throw new Error(`nha-may: node "${n.ma}" có trạm sai dạng "${n.tram}"`);
    if (!["script", "claude", "tay", "theo"].includes(n.che))
      throw new Error(`nha-may: node "${n.ma}" có chế độ lạ "${n.che}"`);
  }
}

export const nodeTheoMa = Object.fromEntries(NODE.map((n) => [n.ma, n]));

/* ═══════════════ SỔ GHI ═══════════════ */

const RONG = { generatedAt: null, lan: 0, node: {}, nk: [] };

export async function docTrangThai() {
  const p = join(ROOT, DUONG_TRANG_THAI);
  if (!existsSync(p)) return structuredClone(RONG);
  try {
    const t = JSON.parse(await readFile(p, "utf8"));
    /* File hỏng hoặc thiếu trường thì coi như chưa có, đừng ném:
       nó được đọc trong workflow, và một file JSON lỗi không được
       phép làm chết lượt cập nhật số liệu. */
    return { ...structuredClone(RONG), ...t, node: t.node || {}, nk: t.nk || [] };
  } catch { return structuredClone(RONG); }
}

async function ghiTrangThai(t) {
  await mkdir(join(ROOT, "factory"), { recursive: true });
  await writeFile(join(ROOT, DUONG_TRANG_THAI), JSON.stringify(t, null, 2) + "\n");
}

/* Node đã đổi file nào chưa — hỏi git, đừng tin script tự khai.
   Script có thể ghi ra nội dung y hệt (API trả cùng số), lúc đó
   "chạy xong" là đúng nhưng "có gì mới" là sai. Phân biệt hai
   thứ đó mới thấy được node đang chạy nhưng nguồn đã chết. */
function coDoi(ra) {
  const duong = (ra || []).filter(Boolean);
  if (!duong.length) return false;
  try {
    const o = execFileSync("git", ["status", "--porcelain", "--", ...duong],
      { cwd: ROOT, encoding: "utf8" });
    return o.trim().length > 0;
  } catch { return false; }
}

export async function ghi(ma, ket, { giay = null, chuThich = "" } = {}) {
  const n = nodeTheoMa[ma];
  if (!n) throw new Error(`nha-may: không có node "${ma}"`);
  if (!["ok", "loi", "bo-qua"].includes(ket))
    throw new Error(`nha-may: kết quả lạ "${ket}" (ok | loi | bo-qua)`);

  const t = await docTrangThai();
  const luc = new Date().toISOString();
  const doi = ket === "ok" ? coDoi(n.ra) : false;

  const truoc = t.node[ma] || {};
  /* Chuỗi lỗi liên tiếp — thứ đáng báo động, khác hẳn một lượt ngã.
     Nguồn mạng ngã một lượt là chuyện thường; ngã bốn lượt liền là
     nguồn đã chết và không ai biết. */
  const chuoiLoi = ket === "loi" ? (truoc.chuoiLoi || 0) + 1 : 0;

  t.node[ma] = {
    luc, ket, giay, doi, chuThich,
    chuoiLoi,
    lucOk: ket === "ok" ? luc : truoc.lucOk || null,
    lucDoi: doi ? luc : truoc.lucDoi || null
  };
  t.nk.unshift({ luc, ma, ket, giay, doi, chuThich });
  if (t.nk.length > TRAN_NHAT_KY) t.nk.length = TRAN_NHAT_KY;
  t.lan = (t.lan || 0) + 1;
  t.generatedAt = luc;
  await ghiTrangThai(t);
  return t.node[ma];
}

/* ═══════════════ ĐẾN HẠN ═══════════════

   Một node đến hạn khi: có nhịp (>0), và lần chạy được ghi gần
   nhất đã cách đây >= nhịp. Chưa chạy lần nào cũng là đến hạn.

   Trừ hao 10 phút: cron của GitHub trôi vài phút mỗi lượt, nên
   một node nhịp 6 giờ chạy lúc 12:19 sẽ bị coi là "mới 5h58" ở
   lượt 18:17 và bị bỏ qua — rồi lượt sau lại lệch tiếp. Không
   trừ hao thì nhịp 6 giờ trên thực tế thành 12 giờ. */
const TRU_HAO_PHUT = 10;

export function denHan(trangThai, bayGio = Date.now()) {
  const ra = [];
  for (const n of NODE) {
    if (!n.nhip) continue;
    const t = trangThai.node[n.ma];
    if (!t || !t.luc) { ra.push(n.ma); continue; }
    const gioQua = (bayGio - new Date(t.luc).getTime()) / 36e5;
    if (gioQua >= n.nhip - TRU_HAO_PHUT / 60) ra.push(n.ma);
  }
  return ra;
}

/* ═══════════════ CHIẾU RA WEBAPP ═══════════════

   Sinh tao-bien-xu/assets/js/v/van-hanh.js — file DUY NHẤT nối
   nhà máy thật với Tạo Biện Xứ.

   Vì sao là file .js trong assets/js/v/ chứ không phải fetch
   factory/state.json: thư mục v/ đã là quy ước sẵn của repo cho
   "nạp khi cần" — build-dist.mjs biết chép nó, sw.js đã có nhánh
   mạng-trước cho nó, và `npm run kiem` đã miễn nó khỏi luật nâng
   CACHE_VERSION. Dùng lại quy ước cũ thì không sinh thêm luật mới;
   fetch một file JSON ở gốc repo thì phải dạy cả ba chỗ đó một
   đường dẫn ngoại lệ. */
export async function chieu() {
  const t = await docTrangThai();
  const cungTheoMa = Object.fromEntries(CUNG.map((c) => [c.ma, c]));

  const node = NODE.map((n) => {
    const s = t.node[n.ma] || {};
    return {
      ma: n.ma, ten: n.ten, y: n.y, tram: n.tram, che: n.che, nhip: n.nhip,
      lenh: n.lenh, ra: n.ra,
      cung: n.cung || null,
      cungTen: n.cung ? cungTheoMa[n.cung].ten : null,
      luc: s.luc || null, ket: s.ket || null, giay: s.giay ?? null,
      doi: !!s.doi, chuThich: s.chuThich || "",
      chuoiLoi: s.chuoiLoi || 0,
      lucOk: s.lucOk || null, lucDoi: s.lucDoi || null
      /* CỐ Ý không chiếu sẵn "đang đến hạn" vào đây, dù tính được.
         Hai lý do, cả hai đều quan trọng:

         1. Nó phụ thuộc ĐỒNG HỒ LÚC CHIẾU. Chiếu nó vào file nghĩa
            là mỗi lượt bot sinh ra một file khác lượt trước dù không
            node nào chạy — và thế là một commit rác mỗi 6 giờ, mãi
            mãi. File này chỉ được đổi khi TRẠNG THÁI đổi.
         2. Trình duyệt tự tính chính xác hơn: nó có `nhip` và `luc`,
            và nó biết BÂY GIỜ là mấy giờ. Chiếu sẵn thì con số đông
            cứng ở thời điểm bot chạy và sai dần suốt 6 tiếng sau. */
    };
  });

  const noiDung =
    "/* SINH TỰ ĐỘNG bởi scripts/nha-may.mjs — ĐỪNG SỬA TAY.\n" +
    "   Đây là bản chiếu của factory/state.json sang thứ trình duyệt đọc được.\n" +
    "   Sửa tay thì lượt bot kế tiếp ghi đè, không báo gì. */\n" +
    "window.VAN_HANH = " + JSON.stringify({
      generatedAt: t.generatedAt, lan: t.lan, node, nk: t.nk.slice(0, 60)
    }, null, 1) + ";\n";

  await mkdir(join(ROOT, "tao-bien-xu/assets/js/v"), { recursive: true });
  await writeFile(join(ROOT, DUONG_CHIEU), noiDung);
  return node.length;
}

/* ═══════════════ MỒI SỔ ═══════════════

   Sổ trống thì Bảng vận hành mở ra chỉ có chữ "chưa chạy lần nào"
   cho tới lượt bot đầu tiên — mà lượt đó có thể là 6 giờ nữa.

   Nhưng sự thật thì đã có sẵn: mỗi file dữ liệu tự sinh đều mang
   dấu `generatedAt` bên trong, và đó CHÍNH LÀ lúc node ấy chạy
   xong lần cuối. `tuoi-du-lieu.mjs` đã đọc dấu đó từ lâu để nhắc
   dữ liệu cũ. Nên mồi sổ không phải bịa số — nó là đọc lại một sự
   thật đang nằm sẵn trong repo mà chưa ai gom về một chỗ.

   Chỉ chạy một lần, lúc dựng. Sau đó `ghi` là nguồn duy nhất. */
export async function moSo() {
  const t = await docTrangThai();
  const RE = /"generatedAt"\s*:\s*"([^"]+)"/;
  let mo = 0;
  for (const n of NODE) {
    if (t.node[n.ma]) continue;
    let luc = null;
    for (const d of n.ra || []) {
      if (d.endsWith("/")) continue;
      const p = join(ROOT, d);
      if (!existsSync(p)) continue;
      const m = RE.exec(await readFile(p, "utf8"));
      if (!m) continue;
      const ms = new Date(m[1]).getTime();
      if (!Number.isFinite(ms)) continue;
      if (!luc || ms > new Date(luc).getTime()) luc = m[1];
    }
    if (!luc) continue;
    const chuThich = "mồi từ dấu generatedAt sẵn có trong file";
    t.node[n.ma] = {
      luc, ket: "ok", giay: null, doi: false, chuThich,
      chuoiLoi: 0, lucOk: luc, lucDoi: luc
    };
    /* Ghi cả vào nhật ký, không chỉ vào trạng thái. Bỏ qua thì Bảng
       vận hành mở ra có 9 thẻ node đầy số nhưng khối "Nhật ký lượt
       chạy" trống trơn — trông như một nửa trang bị hỏng, trong khi
       những lượt ấy có thật và giờ chạy của chúng cũng có thật. */
    t.nk.push({ luc, ma: n.ma, ket: "ok", giay: null, doi: false, chuThich });
    mo++;
  }
  if (mo) {
    t.nk.sort((a, b) => new Date(b.luc) - new Date(a.luc));
    if (t.nk.length > TRAN_NHAT_KY) t.nk.length = TRAN_NHAT_KY;
    t.generatedAt = t.generatedAt || new Date().toISOString();
    await ghiTrangThai(t);
  }
  return mo;
}

export async function soDangKy() {
  const so = {
    generatedAt: new Date().toISOString(),
    ghiChu: "SINH TỰ ĐỘNG từ NODE trong scripts/nha-may.mjs — đừng sửa tay.",
    node: NODE
  };
  await mkdir(join(ROOT, "factory"), { recursive: true });
  await writeFile(join(ROOT, DUONG_SO), JSON.stringify(so, null, 2) + "\n");
  return NODE.length;
}

/* ═══════════════ DÒNG LỆNH ═══════════════ */

function doiSo(argv, ten, mac) {
  const i = argv.indexOf("--" + ten);
  return i === -1 || i === argv.length - 1 ? mac : argv[i + 1];
}

/* So bằng đuôi đường dẫn chứ không so `import.meta.url` với
   `file://${argv[1]}` — trên Windows ổ D: thành `file:///D:/…` (ba
   gạch, ổ đĩa hoa) nên phép so chuỗi đó KHÔNG BAO GIỜ đúng, và cả
   khối lệnh dưới đây im lặng không chạy. */
if ((process.argv[1] || "").replace(/\\/g, "/").endsWith("scripts/nha-may.mjs")) {
  const [, , lenh, ...rest] = process.argv;
  const t = await docTrangThai();

  if (lenh === "so-dang-ky") {
    console.log(`Sổ đăng ký: ${await soDangKy()} node → ${DUONG_SO}`);

  } else if (lenh === "den-han") {
    /* In một dòng, phân cách bằng dấu phẩy có bọc — workflow dùng
       `contains(..., ',kinh-thanh,')` nên phải có phẩy hai đầu, không
       thì "cong-bo" khớp nhầm với "cong-bo-x" nếu sau này có node đó. */
    const han = process.env.NHA_MAY_EP === "1" ? NODE.filter((n) => n.nhip).map((n) => n.ma)
                                               : denHan(t);
    console.log("," + han.join(",") + ",");

  } else if (lenh === "ghi") {
    const [ma, ket] = rest;
    const giayRaw = doiSo(rest, "giay", null);
    const kq = await ghi(ma, ket, {
      giay: giayRaw == null ? null : Number(giayRaw),
      chuThich: doiSo(rest, "ghi", "")
    });
    console.log(`${ma}: ${kq.ket}` + (kq.giay != null ? ` ${kq.giay}s` : "") +
      (kq.doi ? " · có thay đổi" : " · không đổi") +
      (kq.chuoiLoi > 1 ? ` · NGÃ ${kq.chuoiLoi} LƯỢT LIỀN` : ""));

  } else if (lenh === "mo-so") {
    console.log(`Mồi sổ: ${await moSo()} node lấy được lượt chạy cuối từ file sẵn có`);

  } else if (lenh === "chieu") {
    console.log(`Chiếu: ${await chieu()} node → ${DUONG_CHIEU}`);

  } else if (lenh === "bang") {
    const han = new Set(denHan(t));
    const gio = (l) => l ? ((Date.now() - new Date(l).getTime()) / 36e5).toFixed(1) + "h" : "—";
    console.log(`\nNhà máy — ${t.lan || 0} lượt đã ghi` +
      (t.generatedAt ? `, mới nhất ${t.generatedAt}` : ", chưa chạy lần nào") + "\n");
    console.log("  node            trạm chế độ nhịp  lượt cuối  kết quả   đến hạn");
    for (const n of NODE) {
      const s = t.node[n.ma] || {};
      console.log("  " + n.ma.padEnd(15) + n.tram.padEnd(5) +
        n.che.padEnd(7) + String(n.nhip || "—").padEnd(6) +
        gio(s.luc).padEnd(11) +
        (s.ket || "—").padEnd(10) +
        (n.nhip ? (han.has(n.ma) ? "CÓ" : "chưa") : "—") +
        (s.chuoiLoi > 1 ? `   ← ngã ${s.chuoiLoi} lượt liền` : ""));
    }
    console.log("");

  } else {
    console.log("Lệnh: so-dang-ky | mo-so | den-han | ghi <ma> <ok|loi|bo-qua> | chieu | bang");
    process.exit(1);
  }
}
