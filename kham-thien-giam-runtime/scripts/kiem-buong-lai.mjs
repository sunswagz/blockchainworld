/* Vẽ THẬT mọi ô của buồng lái, trên một mẫu dựng tay. Không cần mạng,
   không cần runtime đang chạy, không cần trình duyệt.
 *
 *     node scripts/kiem-buong-lai.mjs
 *     node scripts/kiem-buong-lai.mjs --song      (lấy từ máy đang chạy)
 *     node scripts/kiem-buong-lai.mjs --in chi-huy
 *
 * VÌ SAO CẦN: `node --check` chỉ đọc cú pháp. Loại lỗi đắt nhất của một
 * trang như thế này lại đúng cú pháp — đọc một trường không tồn tại rồi
 * ném, và cả buồng lái trắng trang. Máy vẫn giao dịch bình thường, chỉ
 * người vận hành là mù. Ba lỗi thật đã bị bắt bằng đúng phép kiểm này:
 *
 *   · dùng hàm định dạng CHÊNH LỆCH cho một mức giá, nên "1,0¢" hiện ra
 *     thành "+1,0¢" và đọc thành một thay đổi;
 *   · bày giá lấy từ THANG CHỜ như thể là báo giá thật — đúng cái việc
 *     mà cả cỗ máy bên dưới được dựng để từ chối làm;
 *   · chặn theo `thangCho` thay vì `dungDuoc`, giấu mất báo giá thật của
 *     bên token còn lại.
 *
 * Mẫu là dựng TAY chứ không phải ảnh chụp máy đang chạy: ảnh chụp chỉ có
 * trạng thái tình cờ lúc chụp, còn mẫu tay thì giữ được đủ các trường
 * hợp khó và không đổi theo chợ.
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const GOC = join(dirname(fileURLToPath(import.meta.url)), "..");
const doi = process.argv.slice(2);
const co = (t) => doi.includes(t);
const IN = doi.includes("--in") ? doi[doi.indexOf("--in") + 1] : null;

function Nut(ten) {
  return {
    tagName: ten, children: [], _txt: "", style: {}, dataset: {}, hidden: false,
    classList: {
      _s: new Set(),
      add(...c) { c.forEach((x) => x && this._s.add(x)); },
      toggle(c, v) { v ? this._s.add(c) : this._s.delete(c); },
      contains(c) { return this._s.has(c); },
    },
    appendChild(c) { this.children.push(c); return c; },
    // Canvas giả: mọi lệnh vẽ đều được đếm. Không có nó thì `veNhietDo`
    // thoát sớm ở nhánh "không có ngữ cảnh" và phần vẽ — chỗ dễ sai
    // nhất — không bao giờ được chạy trong bộ kiểm.
    getContext() {
      const d = { _n: 0 };
      const noop = () => { d._n++; };
      for (const k of ["fillRect", "beginPath", "moveTo", "lineTo", "stroke",
                       "setLineDash", "clearRect", "arc", "fill", "closePath"]) {
        d[k] = noop;
      }
      globalThis._veCount = (globalThis._veCount || 0) + 0;
      this._ctx = d;
      return d;
    },
    addEventListener() {}, closest() { return null; },
    querySelectorAll() { return []; },
    set textContent(v) { this._txt = String(v); this.children = []; },
    get textContent() { return this._txt; },
    set innerHTML(v) { this._txt = String(v); },
    get innerHTML() { return this._txt; },
  };
}

const kho = {};
globalThis.document = {
  createElement: Nut,
  createDocumentFragment: () => Nut("#frag"),
  getElementById: (id) => kho[id] || (kho[id] = Nut("div")),
  querySelectorAll: () => [],
  addEventListener: () => {},
};
globalThis.fetch = () => Promise.resolve({ json: () => Promise.resolve({}) });
globalThis.setInterval = () => 0;
globalThis.setTimeout = () => 0;

async function layTrangThai() {
  if (!co("--song")) {
    return JSON.parse(readFileSync(join(GOC, "scripts/mau-buong-lai.json"), "utf8"));
  }
  const r = await fetch("http://localhost:5186/api/trang-thai");
  return r.json();
}

// Mở cái nắp của IIFE để lấy được bảng VE và biến T.
const ma = readFileSync(join(GOC, "web/app.js"), "utf8").replace(
  "})();",
  "  globalThis._VE = VE; globalThis._datT = (d) => { T = d; }; globalThis._ghiLich = ghiLich;\n})();"
);

const T = await layTrangThai();
const nap = new Function(ma);
nap();
globalThis._datT(T);

// Dựng một quãng lịch sử để ô Áp Lực Sổ có gì mà vẽ. Lát 0-11 là báo giá
// thật bám quanh giữa; lát 12-19 chuyển thành THANG CHỜ trải cả dải — đúng
// hai trạng thái mà nhiệt đồ sinh ra để phân biệt.
for (let i = 0; i < 20; i++) {
  const thang = i >= 12;
  const giua = 0.5 + Math.sin(i / 3) * 0.06;
  const muc = (nen, huong) =>
    thang
      ? Array.from({ length: 60 }, (_, k) => ({ gia: (k + 1) / 100, luong: 900 + k }))
      : Array.from({ length: 4 }, (_, k) => ({
          gia: Math.round((nen + huong * k * 0.01) * 100) / 100,
          luong: 400 + k * 260,
        }));
  const ban = JSON.parse(JSON.stringify(T));
  for (const m of ban.thiTruong) {
    if (!m.theo) continue;
    m.so = m.so || {};
    m.so.UP = {
      bestBid: thang ? 0.01 : giua - 0.005,
      bestAsk: thang ? 0.99 : giua + 0.005,
      thangCho: thang,
      bid: muc(giua - 0.005, -1),
      ask: muc(giua + 0.005, +1),
    };
  }
  globalThis._ghiLich(ban);
}

function dem(x) {
  return 1 + (x.children || []).reduce((a, c) => a + dem(c), 0);
}
function inRa(x, d) {
  const t = (x._txt || "").trim();
  const c = [...(x.classList?._s ?? [])].join(".");
  if (t) console.log("  ".repeat(d) + (c ? `[${c}] ` : "") + t);
  else if (c) console.log("  ".repeat(d) + `[${c}]`);
  (x.children || []).forEach((y) => inRa(y, d + 1));
}

console.log(`\n  Buồng lái — ${co("--song") ? "máy đang chạy" : "mẫu dựng tay"}\n`);
let loi = 0, xong = 0, tongNut = 0;
for (const [ten, fn] of Object.entries(globalThis._VE)) {
  try {
    const r = fn();
    const n = dem(r);
    tongNut += n;
    // Một ô vẽ ra đúng 1 nút là một ô RỖNG — cú pháp đúng, không ném, và
    // cũng không nói gì. Đó vẫn là hỏng, chỉ là hỏng lặng lẽ.
    const rong = n <= 1;
    console.log(`  ${rong ? "TRỐNG" : "OK   "} ${ten.padEnd(12)} ${String(n).padStart(4)} nút`);
    if (rong) loi++; else xong++;
    if (IN === ten) inRa(r, 2);
  } catch (e) {
    console.log(`  LỖI   ${ten.padEnd(12)} ${e.message}`);
    console.log(e.stack.split("\n").slice(1, 4).join("\n"));
    loi++;
  }
}
console.log(`\n  ${xong}/${xong + loi} ô vẽ được · ${tongNut} nút\n`);
process.exit(loi ? 1 : 0);
