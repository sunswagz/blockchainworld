/* ═══════════════════════════════════════════════════════
   THÁI BỘC TỰ — đoàn tàu blockchain và các khớp nối.

   Chạy: npm run thaiboc   (hoặc node scripts/build-thaiboc.mjs)
   Ghi:  thai-boc-tu/assets/js/v/doan-tau.js

   ── CUNG NÀY ĐO CÁI GÌ, VÀ KHÔNG ĐO CÁI GÌ ────────────
   Hộ Bộ đã trả lời "tiền đang ở đâu". Cung này trả lời một câu
   khác hẳn: "ai đang dựa vào ai, và chỗ nào gãy thì kéo theo cái
   gì". Nên thứ đáng giá ở đây không phải TVL — mà là ĐỘ TẬP TRUNG
   và ĐƯỜNG LUI.

   Con số lõi: một giao thức khai đúng MỘT oracle là một giao thức
   không có nguồn giá dự phòng. Cộng TVL của nhóm đó lại thì ra
   "bao nhiêu vốn đang treo trên một khớp nối duy nhất" — thứ mà
   bảng vốn hoá không bao giờ nói ra.

   ── MỖI TOA MỘT THƯỚC, VÀ PHẢI NÓI RÕ THƯỚC NÀO ───────
   Đây là chỗ dễ nói dối nhất của cả cung, nên viết rõ:

   TVL không phải thước đo được cho cả 18 toa. Nền tảng (toa 01)
   đo bằng TVL của CHUỖI, không phải của giao thức. Tiền ổn định
   (toa 04) đo bằng LƯỢNG LƯU HÀNH — TVL của mấy nhà phát hành chỉ
   vài trăm triệu trong khi lượng lưu hành là hàng trăm tỷ, lấy
   nhầm thước là sai hai bậc độ lớn.

   Còn meme, game, AI, danh tính thì TVL gần bằng 0 — và điều đó
   KHÔNG có nghĩa chúng vô giá trị. Nó có nghĩa là thước này không
   đo được chúng: chẳng ai khoá vốn vào một meme coin để nó chạy.
   Nên những toa đó được đánh dấu `khong-do-duoc` và hiện "—", chứ
   TUYỆT ĐỐI không hiện 0. Một ô trống nói "chưa đo được"; một số 0
   nói "đo được và bằng không". Trộn hai câu đó là kiểu nói dối khó
   phát hiện nhất trên một bảng điều khiển.

   (Và đó tự nó là một phát hiện: mấy toa bị đốt trước trong thang
   Runaway đúng là mấy toa mà TVL không đo nổi — vì không có vốn
   khoá nào phụ thuộc vào chúng.)

   ── PHẦN DƯ ĐƯỢC BÀY RA, KHÔNG GIẤU ───────────────────
   DefiLlama có hơn 100 category, thang của tài liệu có 18 toa.
   Ánh xạ nào cũng còn dư. Phần dư được cộng lại và hiện thành một
   dòng riêng thay vì nhét bừa vào toa gần nhất — nhét bừa thì bảng
   đẹp hơn và sai đi mà không ai biết.

   ── KHÔNG CÓ KHOÁ NÀO ─────────────────────────────────
   Ba nguồn dưới đây đều công khai. Đó là điều kiện để node này
   chạy trong Actions mà không thêm secret nào vào repo.

   Ba đường DefiLlama khác đã sau tường phí (402): /oracles,
   /forks, /overview/derivatives. Đừng dựng lại chúng bằng số bịa —
   quan hệ oracle ở đây tự tính từ /protocols, chi tiết hơn hẳn một
   bảng tổng đã gộp sẵn, vì còn biết được giao thức nào KHÔNG khai
   nguồn dự phòng.

   ── HỎNG THÌ GIỮ BẢN CŨ ───────────────────────────────
   Hai nguồn LÕI mà ngã thì thoát 1 và KHÔNG ghi gì. Ghi đè bằng
   bảng trống thì người xem đọc thành "đoàn tàu không còn toa nào".
   ═══════════════════════════════════════════════════════ */

import { writeFile, mkdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const RA = join(ROOT, "thai-boc-tu", "assets", "js", "v", "doan-tau.js");

/* ═══════════ ÁNH XẠ CATEGORY → 18 TOA ═══════════
   Đây là chỗ DUY NHẤT giữ ánh xạ. File `toa.js` bên cung chỉ giữ
   phần chữ (tên toa, luận, thứ tự bị đốt) và khớp lại bằng mã toa.
   Muốn đổi một category thuộc toa nào thì sửa ở ĐÂY, không sửa hai
   chỗ. Mỗi toa xuất ra kèm `catGoc` nên người xem truy ngược được
   con số về đúng những category đã cộng vào nó. */
const XEP = {
  t01: ["Chain"],
  t02: ["Canonical Bridge", "MEV", "Block Builders"],
  t03: ["Oracle", "Bridge", "Cross Chain Bridge", "Bridge Aggregator",
        "Bridge Aggregators", "DOR"],
  t04: ["Stablecoin Issuer", "Algo-Stables", "Dual-Token Stablecoin",
        "Partially Algorithmic Stablecoin", "Stablecoin Wrapper",
        "Reserve Currency", "CDP", "CDP Manager"],
  t05: ["Dexs", "DEX Aggregator", "Liquidity Manager", "Liquidity Automation",
        "OTC Marketplace", "Yield", "Yield Aggregator", "Farm"],
  t06: ["Lending", "RWA Lending", "Uncollateralized Lending", "NFT Lending",
        "Collateral Markets", "Collateral Management", "Secondary Debt Markets",
        "Risk Curators", "Onchain Capital Allocator", "Indexes", "Treasury Manager"],
  t07: ["Derivatives", "Options", "Options Vault", "Exotic Options", "Synthetics",
        "Interest Rate Derivatives", "Prediction Market", "Basis Trading",
        "Leveraged Farming", "Insurance", "Liquidations"],
  t08: ["Liquid Staking", "Staking Pool", "Restaking", "Liquid Restaking",
        "Staking Rental"],
  t09: ["RWA"],
  t10: ["Payments", "Crypto Card Issuer"],
  t11: ["DePIN", "Video Infrastructure", "Mining Pools", "Gamified Mining"],
  t12: ["AI Agents", "Decentralized AI"],
  t13: ["Identity & Reputation", "Domains", "SoFi"],
  t14: ["Privacy"],
  t15: ["Gaming", "NFT Marketplace", "NftFi", "NFT Automated Strategies",
        "NFT Launchpad", "Luck Games", "Yield Lottery", "Physical TCG"],
  t16: ["Meme", "Ponzi", "Volume Boosting"],
  t17: ["CEX", "CeDeFi", "Launchpad", "Trading App", "Telegram Bot", "Wallets",
        "Portfolio Tracker", "Coins Tracker", "Interface", "DCA Tools"],
  t18: ["Restaked BTC", "Anchor BTC", "Decentralized BTC"]
};

/* Toa nào KHÔNG đo được bằng TVL giao thức — xem khối đầu file. */
const THUOC = {
  t01: "tvl-chuoi",
  t04: "luu-hanh",
  t11: "khong-do-duoc",
  t12: "khong-do-duoc",
  t13: "khong-do-duoc",
  t15: "khong-do-duoc",
  t16: "khong-do-duoc"
};

const CAT2TOA = {};
for (const [ma, ds] of Object.entries(XEP)) for (const c of ds) CAT2TOA[c] = ma;

/* ═══════════ LẤY NGUỒN ═══════════ */
const nguon = [];
async function lay(nhan, url, thu) {
  const batBuoc = thu && thu.batBuoc;
  try {
    const r = await fetch(url, {
      headers: { "user-agent": "blockchainworld/thai-boc-tu (+https://sunswagz.github.io/blockchainworld/)" },
      signal: AbortSignal.timeout(60000)
    });
    if (!r.ok) throw new Error("HTTP " + r.status);
    const j = await r.json();
    nguon.push({ nhan, ok: true });
    console.log("  ✓ " + nhan);
    return j;
  } catch (e) {
    nguon.push({ nhan, ok: false });
    console.error("  ✗ " + nhan + " — " + e.message);
    if (batBuoc) {
      console.error("\nNguồn LÕI ngã. Không ghi gì, giữ nguyên bản cũ trên site.");
      process.exit(1);
    }
    return null;
  }
}

console.log("Thái Bộc Tự — lấy nguồn:");
const giaoThuc = await lay("giao thức · TVL, chuỗi, oracle",
  "https://api.llama.fi/protocols", { batBuoc: true });
const chuoi = await lay("chuỗi · TVL hiện tại",
  "https://api.llama.fi/v2/chains", { batBuoc: true });
const stable = await lay("stablecoin · lượng lưu hành",
  "https://stablecoins.llama.fi/stablecoins?includePrices=true");

/* ═══════════ TÍNH ═══════════ */
const soHoac = (v) => (typeof v === "number" && isFinite(v) ? v : 0);

/* Tên oracle một giao thức khai — gộp cả hai trường DefiLlama dùng.
   `oracles` là bản cũ, `oraclesBreakdown` là bản mới có kèm vai trò;
   giao thức có thể khai ở một trong hai, nên phải hợp cả hai lại. */
function oracleCua(p) {
  return new Set([
    ...(p.oracles || []),
    ...((p.oraclesBreakdown || []).map((o) => o && o.name).filter(Boolean))
  ]);
}

/* ── các toa ── */
const gom = {};
for (const ma of Object.keys(XEP)) gom[ma] = { tvl: 0, n: 0, top: [], cat: new Set() };
const du = { tvl: 0, n: 0, cat: new Set() };

for (const p of giaoThuc) {
  const cat = p.category;
  const ma = cat ? CAT2TOA[cat] : null;
  const tvl = soHoac(p.tvl);
  if (!ma) { du.tvl += tvl; du.n++; if (cat) du.cat.add(cat); continue; }
  const g = gom[ma];
  g.tvl += tvl; g.n++; g.cat.add(cat);
  g.top.push({ ten: p.name, tvl, chuoi: (p.chains || []).length });
}

/* TVL toàn chuỗi — thước đúng cho toa 01 */
const tvlChuoi = chuoi.reduce((s, c) => s + soHoac(c.tvl), 0);

/* Lượng stablecoin lưu hành — thước đúng cho toa 04. Nguồn này
   KHÔNG bắt buộc, nên ngã thì để null và toa 04 hiện "—" chứ không
   tụt xuống dùng TVL nhà phát hành: hai con số đó lệch nhau hai bậc
   độ lớn, đổi thước giữa chừng là bảng nói dối. */
let luuHanh = null;
if (stable && Array.isArray(stable.peggedAssets)) {
  luuHanh = stable.peggedAssets.reduce(
    (s, x) => s + soHoac(x.circulating && x.circulating.peggedUSD), 0);
}

/* Bảng xếp hạng theo ĐÚNG thước của từng toa. Toa nền phải xếp theo
   chuỗi, toa tiền ổn định phải xếp theo từng stablecoin — lấy bảng
   giao thức cho hai toa đó là bày một con số đo bằng thước này bên
   cạnh một tỷ lệ tính bằng thước khác. Đã suýt để lọt: toa 01 hiện
   78 tỷ (TVL toàn chuỗi) mà "lớn nhất giữ 84%" lại là thị phần
   trong nhóm category "Chain", hai chuyện không liên quan nhau. */
const topChuoi = chuoi
  .map((c) => ({ ten: c.name, tvl: soHoac(c.tvl), chuoi: null }))
  .sort((a, b) => b.tvl - a.tvl);

const topStable = (stable && Array.isArray(stable.peggedAssets) ? stable.peggedAssets : [])
  .map((x) => ({
    ten: x.symbol || x.name,
    tvl: soHoac(x.circulating && x.circulating.peggedUSD),
    chuoi: null
  }))
  .sort((a, b) => b.tvl - a.tvl);

/* Độ tập trung: thị phần của cái lớn nhất trong toa, tính trên cùng
   thước với con số hiển thị. Một toa mà một cái chiếm 80% thì "toa"
   đó thực chất là một cái — và cái đó gãy là cả toa gãy. Đây mới là
   thứ bảng vốn hoá không nói. */
const toa = Object.keys(XEP).map((ma) => {
  const g = gom[ma];
  g.top.sort((a, b) => b.tvl - a.tvl);
  const thuoc = THUOC[ma] || "tvl-giao-thuc";

  let tvl = g.tvl, top = g.top, topNhan = "Giao thức";
  if (thuoc === "tvl-chuoi") { tvl = tvlChuoi; top = topChuoi; topNhan = "Chuỗi"; }
  else if (thuoc === "luu-hanh") { tvl = luuHanh; top = topStable; topNhan = "Stablecoin"; }
  else if (thuoc === "khong-do-duoc") tvl = null;

  const tapTrung = tvl != null && tvl > 0 && top.length ? top[0].tvl / tvl : null;
  return {
    ma, thuoc, tvl, topNhan,
    tvlGiaoThuc: g.tvl,
    soGiaoThuc: g.n,
    tapTrung,
    tapTrungTen: tapTrung != null ? top[0].ten : null,
    top: top.slice(0, 6).map((t) => ({ ten: t.ten, tvl: t.tvl, chuoi: t.chuoi })),
    catGoc: [...g.cat].sort()
  };
});

/* ── khớp nối oracle ── */
const oc = {};
for (const p of giaoThuc) {
  const ten = oracleCua(p);
  if (!ten.size) continue;
  const tvl = soHoac(p.tvl);
  const rieng = ten.size === 1;
  for (const t of ten) {
    oc[t] = oc[t] || { ten: t, tvl: 0, n: 0, tvlRieng: 0, nRieng: 0, top: [] };
    oc[t].tvl += tvl; oc[t].n++;
    if (rieng) { oc[t].tvlRieng += tvl; oc[t].nRieng++; }
    oc[t].top.push({ ten: p.name, tvl, rieng });
  }
}
const oracle = Object.values(oc)
  .sort((a, b) => b.tvl - a.tvl)
  .slice(0, 14)
  .map((o) => {
    o.top.sort((a, b) => b.tvl - a.tvl);
    return {
      ten: o.ten, tvl: o.tvl, soGiaoThuc: o.n,
      tvlRieng: o.tvlRieng, soRieng: o.nRieng,
      top: o.top.slice(0, 5)
    };
  });

/* Đường lui: bao nhiêu vốn treo trên ĐÚNG MỘT oracle. */
let motTvl = 0, motN = 0, nhieuTvl = 0, nhieuN = 0;
for (const p of giaoThuc) {
  const ten = oracleCua(p);
  if (!ten.size) continue;
  const tvl = soHoac(p.tvl);
  if (ten.size === 1) { motTvl += tvl; motN++; } else { nhieuTvl += tvl; nhieuN++; }
}

/* ── khớp nối chuỗi ── */
const ch = {};
for (const p of giaoThuc) {
  for (const c of p.chains || []) {
    ch[c] = ch[c] || { ten: c, n: 0 };
    ch[c].n++;
  }
}
const tvlTheoChuoi = {};
for (const c of chuoi) tvlTheoChuoi[c.name] = soHoac(c.tvl);
const khopChuoi = Object.values(ch)
  .sort((a, b) => b.n - a.n)
  .slice(0, 16)
  .map((c) => ({
    ten: c.ten,
    soGiaoThuc: c.n,
    tvl: tvlTheoChuoi[c.ten] != null ? tvlTheoChuoi[c.ten] : null
  }));

/* Trải chuỗi: giao thức đứng trên một chuỗi duy nhất thì chuỗi đó
   ngã là nó ngã theo. Đứng trên nhiều chuỗi thì còn đường lui. */
let motChuoiN = 0, nhieuChuoiN = 0, motChuoiTvl = 0, nhieuChuoiTvl = 0;
for (const p of giaoThuc) {
  const n = (p.chains || []).length;
  if (!n) continue;
  const tvl = soHoac(p.tvl);
  if (n === 1) { motChuoiN++; motChuoiTvl += tvl; }
  else { nhieuChuoiN++; nhieuChuoiTvl += tvl; }
}

const now = new Date();
const tyLeLui = motTvl + nhieuTvl > 0 ? motTvl / (motTvl + nhieuTvl) : null;

/* `date` và `tomTat` PHẢI nằm ngay đầu object. Thẻ của cung này ở
   Cổng Thành chỉ tải 900 byte đầu file rồi huỷ dòng tải — đẩy hai
   khoá này xuống sau mảng `toa` là thẻ mất ngày cập nhật, và mất
   im lặng. Cùng bẫy đã ghi ở build-hobu.mjs. */
const data = {
  generatedAt: now.toISOString(),
  date: now.toISOString().slice(0, 10).split("-").reverse().join("/"),
  tomTat: (tyLeLui == null ? "—" : (tyLeLui * 100).toFixed(0) + "%") +
    " vốn treo một khớp",
  nguon,
  tong: {
    soGiaoThuc: giaoThuc.length,
    soCategory: new Set(giaoThuc.map((p) => p.category).filter(Boolean)).size,
    soChuoi: chuoi.length,
    tvlGiaoThuc: giaoThuc.reduce((s, p) => s + soHoac(p.tvl), 0),
    tvlChuoi,
    luuHanhStable: luuHanh
  },
  toa,
  du: { tvl: du.tvl, soGiaoThuc: du.n, cat: [...du.cat].sort() },
  oracle,
  duongLui: { motTvl, motN, nhieuTvl, nhieuN, tyLe: tyLeLui },
  khopChuoi,
  traiChuoi: { motN: motChuoiN, motTvl: motChuoiTvl, nhieuN: nhieuChuoiN, nhieuTvl: nhieuChuoiTvl }
};

await mkdir(dirname(RA), { recursive: true });
await writeFile(RA,
  "/* TỰ SINH — đừng sửa tay. Nguồn: scripts/build-thaiboc.mjs\n" +
  "   Sinh lúc " + data.generatedAt + " */\n" +
  "window.THAIBOC = " + JSON.stringify(data) + ";\n", "utf8");

const kb = (JSON.stringify(data).length / 1024).toFixed(1);
console.log("\n✓ Ghi " + RA.replace(ROOT, ".") + "  (" + kb + " KB)");
console.log("  " + data.tong.soGiaoThuc + " giao thức · " + data.tong.soCategory +
  " category → 18 toa, dư " + data.du.cat.length + " category");
if (data.duongLui.tyLe != null) {
  console.log("  đường lui: " + (data.duongLui.tyLe * 100).toFixed(1) +
    "% vốn có khai oracle đang treo trên đúng một oracle");
}
