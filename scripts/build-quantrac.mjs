/* ═══════════════════════════════════════════════════════
   ĐO cho Đài Quan Trắc — tự đặt đèn cho bảng cảnh báo sớm.

   Chạy: node scripts/build-quantrac.mjs
   Ghi:  dai-quan-trac/assets/js/do.js       (Việt Nam)
         dai-quan-trac/assets/js/tq/do.js    (Trung Quốc)

   ── VÌ SAO KHÔNG GỌI AI Ở ĐÂY ──────────────────────────
   Bản quét (scripts/build-scan.mjs) gọi model. Bảng đo thì không,
   và lý do quan trọng hơn tiền: file scan.js đóng dấu tên model vào
   output — nghĩa là kết quả PHỤ THUỘC model nào chạy. Đổi model là
   đổi kết luận mà không ai biết. Một ngưỡng số học thì cùng một con
   số luôn cho cùng một màu, năm này qua năm khác, kiểm toán ngược
   được.

   Trí tuệ ở đây nằm trong NGƯỠNG, viết một lần bằng phán đoán của
   người, chứ không phải đoán lại mỗi 6 giờ.

   ── NGƯỠNG NAY NẰM Ở CUNG, KHÔNG NẰM Ở ĐÂY ─────────────
   Trước đây "đo cái gì, ngưỡng bao nhiêu" viết cứng trong chính
   file này. Hệ quả: thêm một đồng hồ cho một cung là phải sửa
   script của cả xưởng — đúng thứ luật worktree muốn tránh.

   Nay bảng khai nằm ở `DODAC` trong data.js của từng chủ thể, và
   script này chỉ còn là BỘ CHẠY. Cùng khuôn build-scan.mjs đã dùng
   với THEATERS. Thêm một đồng hồ = sửa một dòng trong cung.

   ── BỐN NGUỒN, ĐỀU MIỄN PHÍ VÀ KHÔNG CẦN KHOÁ ──────────
   Đã thử thật trước khi viết, không lấy từ trí nhớ:
     · yahoo   — Yahoo Finance chart. Trả kèm ~64 phiên lịch sử,
                 nên sparkline có sẵn, không phải tự tích luỹ.
     · erapi   — open.er-api.com. MỘT lượt gọi trả MỌI đồng tiền,
                 nên USD/VND và USD/CNY dùng chung một phản hồi.
     · fedreg  — Federal Register API, đếm văn bản theo từ khoá.
     · gdelt   — GDELT timelinetone, sắc thái tin theo truy vấn.

   Đã loại sau khi thử: stooq (chặn, trả HTML), Frankfurter (không
   có VND), EIA và FRED (miễn phí nhưng đòi đăng ký khoá).

   ── ĐỒNG HỒ NÀO KHÔNG TỰ ĐO ĐƯỢC ───────────────────────
   Việt Nam: ngân hàng, bất động sản, kênh sàn — không có nguồn
   miễn phí đủ tin.

   Trung Quốc: CẢ MƯỜI HAI đồng hồ. Chúng đo thu địa phương, LGFV,
   "tam bảo", thanh lọc cán bộ, chuỗi mệnh lệnh — không nguồn công
   khai nào có. Nên bản khai của Trung Quốc chỉ có SỐ ĐO NỀN
   (`gg:null`), và giao diện phải nói rõ chúng không phải đồng hồ
   chính. Bịa một proxy yếu rồi gắn nhãn "tự đo" còn tệ hơn để
   trống: người đọc sẽ tin một con số không đáng tin.
   ═══════════════════════════════════════════════════════ */

import { writeFile, readFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { CHU_THE, docChuThe } from "./dqt-chuthe.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const APP = join(ROOT, "dai-quan-trac");

const log = (...a) => console.log(...a);
const warn = (...a) => console.error("  ⚠", ...a);

/* Chỉ số nghịch: giá trị THẤP mới là xấu, lúc đó hai biên đảo vai. */
function dat(k, v) {
  if (v == null || !Number.isFinite(v) || k.g == null) return "n";
  if (k.nghich) return v >= k.g ? "g" : v <= k.r ? "r" : "y";
  return v <= k.g ? "g" : v >= k.r ? "r" : "y";
}

/* ── LẤY SỐ ───────────────────────────────────────────── */
const UA = { "user-agent": "dai-quan-trac-databot", accept: "*/*" };
const nghi = (ms) => new Promise((r) => setTimeout(r, ms));

/* Thử 3 lần, nghỉ 2s rồi 5s. GDELT chập chờn thật — cùng một URL
   lần đầu tắc, lần sau trả 8 KB JSON bình thường. Không có vòng
   này thì đồng hồ sắc thái hỏng ngẫu nhiên vài lượt mỗi ngày và
   trông như nguồn đã chết. */
async function nap(url, kieu = "json") {
  let cuoi;
  for (let lan = 1; lan <= 3; lan++) {
    try {
      const r = await fetch(url, { headers: UA, signal: AbortSignal.timeout(30000) });
      /* 429 là ĐỦ RỒI, không phải trục trặc: thử lại chỉ làm sâu
         thêm hình phạt. Ngã ngay, giữ số đo lượt trước. */
      if (r.status === 429) throw new Error("bị chặn tạm thời (429) — giữ số cũ");
      if (!r.ok) throw new Error("HTTP " + r.status);
      return kieu === "json" ? r.json() : r.text();
    } catch (e) {
      cuoi = e;
      if (/429/.test(e.message)) break;
      if (lan < 3) await nghi(lan * 2000 + 1000);
    }
  }
  throw cuoi;
}

/* open.er-api trả MỌI đồng tiền trong một lượt. Gọi một lần rồi
   dùng lại cho mọi chủ thể — thêm nước thứ ba cũng không tốn thêm
   lượt gọi nào. */
let TIEN = null;
let daGoiGdelt = false;
async function bangTien() {
  if (!TIEN) TIEN = nap("https://open.er-api.com/v6/latest/USD");
  return TIEN;
}

/* Bốn bộ lấy số. Bản khai chỉ chọn `nguon` và `ma`, không biết gì
   về URL — nên đổi nhà cung cấp là sửa đúng ở đây, một chỗ. */
const LAY = {
  async yahoo(ma) {
    const j = await nap("https://query1.finance.yahoo.com/v8/finance/chart/" +
      encodeURIComponent(ma) + "?range=3mo&interval=1d");
    if (j.chart?.error) throw new Error(j.chart.error.description || "yahoo error");
    const c = (j.chart.result[0].indicators.quote[0].close || []).filter((x) => x != null);
    if (!c.length) throw new Error("chuỗi rỗng");
    const l = c.map((x) => Math.round(x * 100) / 100);
    return { lich: l, so: l[l.length - 1] };
  },
  async erapi(ma) {
    const j = await bangTien();
    const v = j?.rates?.[ma];
    if (!Number.isFinite(v)) throw new Error("không có " + ma + " trong phản hồi");
    /* Nguồn này chỉ cho giá hiện tại — chuỗi tự tích luỹ, xem gopLich(). */
    return { so: v >= 1000 ? Math.round(v) : Math.round(v * 10000) / 10000, lich: null };
  },
  async fedreg(ma) {
    const tu = new Date(Date.now() - 30 * 864e5).toISOString().slice(0, 10);
    const j = await nap("https://www.federalregister.gov/api/v1/documents.json" +
      "?conditions%5Bterm%5D=" + encodeURIComponent(ma) +
      "&conditions%5Bpublication_date%5D%5Bgte%5D=" + tu +
      "&per_page=1&fields%5B%5D=publication_date");
    if (!Number.isFinite(j?.count)) throw new Error("không đọc được số đếm");
    return { so: j.count, lich: null };
  },
  async gdelt(ma) {
    /* GDELT chặn khi hai lượt gọi sát nhau — lộ ra đúng lúc thêm chủ
       thể thứ hai, vì trước đó cả xưởng chỉ gọi nó một lần. Nghỉ giữa
       các lượt rẻ hơn nhiều so với mất một phép đo. */
    if (daGoiGdelt) await nghi(15000);
    daGoiGdelt = true;
    const j = await nap("https://api.gdeltproject.org/api/v2/doc/doc?query=" +
      encodeURIComponent(ma) + "&mode=timelinetone&format=json&timespan=90d");
    const d = (j.timeline?.[0]?.data || []).map((x) => x.value).filter(Number.isFinite);
    if (!d.length) throw new Error("chuỗi rỗng");
    const l = d.map((x) => Math.round(x * 100) / 100);
    return { lich: l, so: l[l.length - 1] };
  }
};

const TEN_NGUON = {
  yahoo: (ma) => "Yahoo Finance · " + ma,
  erapi: (ma) => "open.er-api.com · USD/" + ma,
  fedreg: (ma) => "Federal Register API · “" + ma + "”",
  gdelt: (ma) => "GDELT timelinetone · “" + ma + "”"
};

/* Đổi phần trăm so với N phiên trước — nói nhiều hơn giá trị tuyệt đối. */
function doi(lich, n) {
  if (!lich || lich.length <= n) return null;
  const a = lich[lich.length - 1 - n], b = lich[lich.length - 1];
  if (!a) return null;
  return Math.round(((b - a) / a) * 1000) / 10;
}

/* Mỗi phép đo hỏng độc lập: một nguồn chết không được làm mất
   những nguồn đã lấy xong. */
async function thu(ten, fn) {
  try { const v = await fn(); log("  ✓ " + ten); return v; }
  catch (e) { warn(ten + ": " + e.message); return null; }
}

/* Nguồn không cho lịch sử thì tự tích luỹ: đọc bản cũ, nối thêm
   điểm mới, cắt còn 90. Không có bước này thì sparkline của tỷ giá
   vĩnh viễn là một chấm. */
async function docCu(duong, bien) {
  if (!existsSync(duong)) return {};
  try {
    const t = await readFile(duong, "utf8");
    const m = t.match(new RegExp("window\\." + bien + "\\s*=\\s*([\\s\\S]*?);\\s*$"));
    return m ? JSON.parse(m[1]).do || {} : {};
  } catch { return {}; }
}
function gopLich(cu, moi, so) {
  if (moi) return moi.slice(-90);
  const l = (cu && cu.lich) ? cu.lich.slice() : [];
  if (so != null && l[l.length - 1] !== so) l.push(so);
  return l.slice(-90);
}

/* ── CHẠY ─────────────────────────────────────────────── */
let tongDo = 0, hongHet = true;

for (const ct of CHU_THE) {
  log("\n═══ " + ct.ten + " ═══");

  let khai;
  try {
    khai = (await docChuThe(APP, ct)).DODAC;
  } catch (e) {
    warn("không đọc được bản khai: " + e.message);
    continue;
  }
  if (!Array.isArray(khai) || !khai.length) {
    log("  (chưa khai phép đo nào — bỏ qua)");
    continue;
  }

  const RA = join(APP, ...ct.doRa);
  const cu = await docCu(RA, ct.doBien);
  const ra = {};

  for (const k of khai) {
    const lay = LAY[k.nguon];
    if (!lay) { warn(k.nhan + ": nguồn “" + k.nguon + "” chưa có bộ lấy"); continue; }
    const v = await thu(k.nhan, () => lay(k.ma));
    if (!v) {
      /* Giữ nguyên số đo cũ thay vì xoá — mất mạng một lượt không
         được làm bảng trống trơn. Nhưng đánh dấu để giao diện nói
         thật là số này cũ. */
      if (cu[k.id]) { ra[k.id] = { ...cu[k.id], oi: true }; log("    (giữ số đo lượt trước)"); }
      continue;
    }
    const lich = gopLich(cu[k.id], v.lich, v.so);
    ra[k.id] = {
      nhan: k.nhan, so: v.so, dv: k.dv,
      nguon: (TEN_NGUON[k.nguon] || (() => k.nguon))(k.ma),
      ghi: k.ghi || null,
      muc: dat(k, v.so), lich,
      doi7: doi(lich, 7), doi30: doi(lich, 30),
      nguong: k.g == null ? null : { g: k.g, r: k.r, nghich: !!k.nghich, can: k.can },
      luc: new Date().toISOString()
    };
  }

  if (!Object.keys(ra).length) {
    warn(ct.ten + ": không đo được gì cả — KHÔNG ghi đè file cũ.");
    continue;
  }
  hongHet = false;

  const out = {
    generatedAt: new Date().toISOString(),
    /* Ghi rõ để giao diện đừng bịa: đây là danh sách CÓ nguồn tự
       động. Những đồng hồ khác vẫn phải đặt tay. */
    tuDo: Object.keys(ra),
    do: ra
  };
  await mkdir(dirname(RA), { recursive: true });
  await writeFile(RA,
    "/* TỰ SINH — scripts/build-quantrac.mjs. Đừng sửa tay. */\n" +
    "window." + ct.doBien + " = " + JSON.stringify(out, null, 1) + ";\n", "utf8");

  log("");
  for (const [, d] of Object.entries(ra)) {
    const den = { g: "XANH", y: "VÀNG", r: "ĐỎ", n: "—" }[d.muc];
    const dd = d.doi7 == null ? "" : "  (" + (d.doi7 > 0 ? "+" : "") + d.doi7 + "% / 7 phiên)";
    log("  " + d.nhan.padEnd(34) + String(d.so).padStart(9) + " " + (d.dv || "") +
        "  → " + den + dd + (d.oi ? "  [số cũ]" : ""));
  }
  tongDo += Object.keys(ra).length;
  log("  → " + ct.doRa.join("/") + " · " + Object.keys(ra).length + " phép đo");
}

/* Hỏng một nước thì vẫn ghi nước kia; hỏng CẢ HAI mới là sự cố. */
if (hongHet) {
  console.error("\n✗ Không chủ thể nào đo được — không ghi đè gì.");
  process.exit(1);
}
log("\n✓ tổng " + tongDo + " phép đo trên " + CHU_THE.length + " chủ thể");
