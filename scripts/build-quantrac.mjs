/* ═══════════════════════════════════════════════════════
   ĐO cho Đài Quan Trắc — tự đặt đèn cho bảng cảnh báo sớm.

   Chạy: node scripts/build-quantrac.mjs
   Ghi:  dai-quan-trac/assets/js/do.js

   ── VÌ SAO KHÔNG GỌI AI Ở ĐÂY ──────────────────────────
   Bản quét cũ (scripts/build-scan.mjs) gọi Claude + web_search,
   đo được là ~1,4 USD một lượt, ~170 USD/tháng ở nhịp 4 lượt/ngày.
   Đó là lý do nó bị tắt lịch 14/08/2026.

   Nhưng tiền chỉ là lý do thứ hai. Lý do thứ nhất: file scan.js
   đóng dấu `"model": "claude-opus-5"` vào output — nghĩa là kết
   quả PHỤ THUỘC model nào chạy. Đổi model là đổi kết luận mà
   không ai biết. Một ngưỡng số học thì cùng một con số luôn cho
   cùng một màu, năm này qua năm khác, và kiểm toán ngược được.

   Trí tuệ ở đây nằm trong NGƯỠNG, viết một lần bằng phán đoán
   của người, chứ không phải đoán lại mỗi 6 giờ.

   ── BA NGUỒN, ĐỀU MIỄN PHÍ VÀ KHÔNG CẦN KHOÁ ───────────
   Đã thử thật trước khi viết, không lấy từ trí nhớ:
     · Yahoo Finance chart  — Brent, US 10Y, chỉ số USD.
       Trả kèm ~64 phiên lịch sử, nên sparkline có sẵn,
       không phải tự tích luỹ dần.
     · open.er-api.com      — USD/VND.
     · GDELT timelinetone   — sắc thái tin về kinh tế Việt Nam.

   Đã loại sau khi thử: stooq (chặn, trả HTML), Frankfurter
   (không có VND), EIA và FRED (miễn phí nhưng đòi đăng ký khoá).

   ── ĐỒNG HỒ NÀO KHÔNG TỰ ĐO ĐƯỢC ───────────────────────
   Ngân hàng, bất động sản, kênh sàn: không có nguồn miễn phí
   đủ tin. Chúng ở lại chế độ ĐẶT TAY, và giao diện phải nói rõ
   điều đó. Bịa một proxy yếu rồi gắn nhãn "tự đo" còn tệ hơn
   để trống: người đọc sẽ tin một con số không đáng tin.
   ═══════════════════════════════════════════════════════ */

import { writeFile, readFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const RA = join(ROOT, "dai-quan-trac", "assets", "js", "do.js");

const log = (...a) => console.log(...a);
const warn = (...a) => console.error("  ⚠", ...a);

/* ── NGƯỠNG ─────────────────────────────────────────────
   Đây là phần duy nhất mang phán đoán, nên để tách hẳn ra và
   ghi rõ căn cứ. Sửa ngưỡng là sửa ở đây, một chỗ.

   Quy ước: `g` là biên trên của vùng XANH, `r` là biên dưới của
   vùng ĐỎ, ở giữa là VÀNG. `nghich:true` cho chỉ số mà THẤP mới
   là xấu (sắc thái tin), lúc đó hai biên đảo vai. */
const NGUONG = {
  nangluong: {
    g: 75, r: 90,
    can: "EIA dự báo Brent trung bình ~85 USD/thùng quý III/2026. Trên 90 là vượt vùng dự báo; dưới 75 là về lại mức trước xung đột."
  },
  tygia: {
    g: 25500, r: 26500,
    can: "Đặt quanh vùng tỷ giá đang giao dịch. Vượt 26.500 là mức chưa từng thấy kéo dài, đủ để gây áp lực nhập khẩu và nợ ngoại tệ."
  },
  laisuat: {
    g: 4.0, r: 4.75,
    can: "Lợi suất trái phiếu Mỹ 10 năm — lực ép TỪ NGOÀI lên lãi suất và tỷ giá Việt Nam, không phải lãi suất điều hành trong nước. Trên 4,75% là vùng siết mạnh dòng vốn khỏi thị trường mới nổi."
  },
  niemtin: {
    g: 1.9, r: 1.4, nghich: true,
    can: "Sắc thái tin GDELT không có mốc 0 tự nhiên cho mục đích này, nên ngưỡng đặt theo PHÂN PHỐI QUAN SÁT 90 ngày: trung vị 1,91 · phần tư dưới 1,61 · thấp nhất 0,83. Trên trung vị là xanh, rơi xuống phần tư dưới là đỏ."
  }
};

/* Chỉ số nghịch: giá trị thấp mới là xấu. */
function dat(id, v) {
  const n = NGUONG[id];
  if (!n || v == null || !Number.isFinite(v)) return "n";
  if (n.nghich) return v >= n.g ? "g" : v <= n.r ? "r" : "y";
  return v <= n.g ? "g" : v >= n.r ? "r" : "y";
}

/* ── LẤY SỐ ───────────────────────────────────────────── */
const UA = { "user-agent": "dai-quan-trac-databot", accept: "*/*" };

const nghi = (ms) => new Promise((r) => setTimeout(r, ms));

/* Thử 3 lần, nghỉ 2s rồi 5s. GDELT chập chờn thật — cùng một URL
   lần đầu tắc, lần sau trả 8 KB JSON bình thường. Không có vòng
   này thì đồng hồ niềm tin hỏng ngẫu nhiên vài lượt mỗi ngày và
   trông như nguồn đã chết.

   Tổng chờ xấu nhất: 3×30s tải + 7s nghỉ ≈ 1,6 phút cho một nguồn.
   Trần bước trong workflow phải lớn hơn tổng đó nhân số nguồn. */
async function nap(url, kieu = "json") {
  let cuoi;
  for (let lan = 1; lan <= 3; lan++) {
    try {
      const r = await fetch(url, { headers: UA, signal: AbortSignal.timeout(30000) });
      /* 429 là ĐỦ RỒI, không phải trục trặc: thử lại chỉ làm sâu
         thêm hình phạt. Ngã ngay, giữ số đo lượt trước.
         (GDELT chặn khá gắt — lúc phát triển gọi vài chục lượt là
         chạm, còn nhịp thật 4 lượt/ngày thì không tới gần.) */
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

/* Yahoo trả cả chuỗi lịch sử — dùng luôn làm sparkline. */
async function yahoo(sym) {
  const j = await nap("https://query1.finance.yahoo.com/v8/finance/chart/" +
    encodeURIComponent(sym) + "?range=3mo&interval=1d");
  if (j.chart?.error) throw new Error(j.chart.error.description || "yahoo error");
  const c = (j.chart.result[0].indicators.quote[0].close || []).filter(x => x != null);
  if (!c.length) throw new Error("chuỗi rỗng");
  return c.map(x => Math.round(x * 100) / 100);
}

/* Đổi phần trăm so với N phiên trước — thứ nói nhiều hơn giá trị tuyệt đối. */
function doi(lich, n) {
  if (!lich || lich.length <= n) return null;
  const a = lich[lich.length - 1 - n], b = lich[lich.length - 1];
  if (!a) return null;
  return Math.round(((b - a) / a) * 1000) / 10;
}

/* Mỗi phép đo hỏng độc lập: một nguồn chết không được làm mất
   những nguồn đã lấy xong. Cùng lý do với continue-on-error của
   từng bước trong refresh-data.yml. */
async function thu(ten, fn) {
  try { const v = await fn(); log("  ✓ " + ten); return v; }
  catch (e) { warn(ten + ": " + e.message); return null; }
}

const phep = [
  {
    id: "nangluong", nhan: "Dầu Brent", dv: "USD/thùng",
    nguon: "Yahoo Finance · BZ=F",
    lay: async () => { const l = await yahoo("BZ=F"); return { lich: l, so: l[l.length - 1] }; }
  },
  {
    id: "laisuat", nhan: "Lợi suất TPCP Mỹ 10 năm", dv: "%",
    nguon: "Yahoo Finance · ^TNX",
    ghi: "Lực ép từ ngoài lên lãi suất trong nước, không phải lãi suất điều hành của NHNN.",
    lay: async () => { const l = await yahoo("^TNX"); return { lich: l, so: l[l.length - 1] }; }
  },
  {
    id: "tygia", nhan: "USD/VND", dv: "đồng",
    nguon: "open.er-api.com",
    lay: async () => {
      const j = await nap("https://open.er-api.com/v6/latest/USD");
      const v = j?.rates?.VND;
      if (!Number.isFinite(v)) throw new Error("không có VND trong phản hồi");
      /* Nguồn này chỉ cho giá hiện tại, không cho lịch sử — nên
         chuỗi phải tự tích luỹ qua các lượt chạy, xem gopLich(). */
      return { so: Math.round(v), lich: null };
    }
  },
  {
    id: "niemtin", nhan: "Sắc thái tin về kinh tế VN", dv: "điểm GDELT",
    nguon: "GDELT · timelinetone",
    ghi: "Chỉ báo THAY THẾ, không phải đo niềm tin trực tiếp. Nó đo giọng của báo chí quốc tế, và giọng báo không đồng nghĩa với hành vi người gửi tiền.",
    lay: async () => {
      const j = await nap("https://api.gdeltproject.org/api/v2/doc/doc?query=" +
        encodeURIComponent("Vietnam economy") + "&mode=timelinetone&format=json&timespan=90d");
      const d = (j.timeline?.[0]?.data || []).map(x => x.value).filter(Number.isFinite);
      if (!d.length) throw new Error("chuỗi rỗng");
      const l = d.map(x => Math.round(x * 100) / 100);
      return { lich: l, so: l[l.length - 1] };
    }
  }
];

/* Nguồn không cho lịch sử thì tự tích luỹ: đọc bản cũ, nối thêm
   điểm mới, cắt còn 90. Không có bước này thì sparkline của tỷ
   giá vĩnh viễn là một chấm. */
async function docCu() {
  if (!existsSync(RA)) return {};
  try {
    const t = await readFile(RA, "utf8");
    const m = t.match(/window\.DQT_DO\s*=\s*([\s\S]*?);\s*$/);
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
log("Đo cho Đài Quan Trắc\n");
const cu = await docCu();
const ra = {};

for (const p of phep) {
  const v = await thu(p.nhan, p.lay);
  if (!v) {
    /* Giữ nguyên số đo cũ thay vì xoá — mất mạng một lượt không
       được làm bảng trống trơn. Nhưng đánh dấu để giao diện nói
       thật là số này cũ. */
    if (cu[p.id]) { ra[p.id] = { ...cu[p.id], oi: true }; log("    (giữ số đo lượt trước)"); }
    continue;
  }
  const lich = gopLich(cu[p.id], v.lich, v.so);
  const n = NGUONG[p.id];
  ra[p.id] = {
    nhan: p.nhan, so: v.so, dv: p.dv, nguon: p.nguon, ghi: p.ghi || null,
    muc: dat(p.id, v.so), lich,
    doi7: doi(lich, 7), doi30: doi(lich, 30),
    nguong: n ? { g: n.g, r: n.r, nghich: !!n.nghich, can: n.can } : null,
    luc: new Date().toISOString()
  };
}

if (!Object.keys(ra).length) {
  console.error("\n✗ Không đo được gì cả — KHÔNG ghi đè file cũ.");
  process.exit(1);
}

const out = {
  generatedAt: new Date().toISOString(),
  /* Ghi rõ để giao diện đừng bịa: đây là danh sách đồng hồ CÓ
     nguồn tự động. Những đồng hồ khác vẫn phải đặt tay. */
  tuDo: Object.keys(ra),
  do: ra
};

await mkdir(dirname(RA), { recursive: true });
await writeFile(RA,
  "/* TỰ SINH — scripts/build-quantrac.mjs. Đừng sửa tay. */\n" +
  "window.DQT_DO = " + JSON.stringify(out, null, 1) + ";\n", "utf8");

log("");
for (const [id, d] of Object.entries(ra)) {
  const den = { g: "XANH", y: "VÀNG", r: "ĐỎ", n: "—" }[d.muc];
  const dd = d.doi7 == null ? "" : "  (" + (d.doi7 > 0 ? "+" : "") + d.doi7 + "% / 7 phiên)";
  log("  " + d.nhan.padEnd(30) + String(d.so).padStart(9) + " " + (d.dv || "") +
      "  → " + den + dd + (d.oi ? "  [số cũ]" : ""));
}
log("\n✓ ghi " + Object.keys(ra).length + " phép đo → dai-quan-trac/assets/js/do.js");
