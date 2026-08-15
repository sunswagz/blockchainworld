/* ═══════════════════════════════════════════════════════
   HỘ BỘ — dòng tiền blockchain.

   Chạy: npm run hobu       (hoặc node scripts/build-hobu.mjs)
   Ghi:  ho-bo/assets/js/v/dong-tien.js

   ── VÌ SAO CHỈ MỘT FILE RA ────────────────────────────
   Mọi thứ cung cần đều nằm trong đúng một file, và file đó nằm
   dưới `assets/js/v/` — nhánh MẠNG-TRƯỚC của sw.js. Bot ghi 4
   lượt/ngày; để nó ở nhánh cache-trước là máy đã cài app giữ số
   của hôm qua tới lần nâng CACHE_VERSION kế tiếp, tức một bảng
   điều khiển nói dối. Đúng cái bẫy đã cắn logos.js của Công Bộ.

   ── VÌ SAO KHÔNG TỰ LƯU LỊCH SỬ ───────────────────────
   Cám dỗ đầu tiên là ghi thêm một `lich-su.json` để tính xu
   hướng giữa hai lượt. Không cần: DefiLlama đã trả nguyên chuỗi
   thời gian (`historicalChainTvl`, `stablecoincharts`), nên xu
   hướng đọc thẳng từ nguồn. Một file ra thì `ra` của node, dòng
   `git add` trong workflow và danh sách trong CLAUDE.md đều chỉ
   có một dòng — ba chỗ khó lệch nhau hơn hẳn.

   ── KHÔNG CÓ KHOÁ NÀO ─────────────────────────────────
   Tất cả nguồn dưới đây đều công khai, không cần khoá. Đó là
   điều kiện để node này chạy được trong Actions mà không thêm
   một secret nào vào repo — xem mục "Repo này KHÔNG dùng
   ANTHROPIC_API_KEY nữa" trong CLAUDE.md.

   Ba đường DefiLlama từng dùng được nay đã sau tường phí (trả
   402): /raises (gọi vốn), /emissions (lịch mở khoá), /bridges
   (dòng cầu nối). Đừng dựng lại ba phòng đó bằng số bịa — cung
   này chỉ bày thứ đo được.

   ── HỎNG THÌ GIỮ BẢN CŨ ───────────────────────────────
   Nguồn nào cũng có thể ngã. Bốn nguồn LÕI mà ngã thì thoát 1 và
   KHÔNG ghi gì — bản cũ còn nguyên trên site. Ghi đè bằng bảng
   trống thì người xem đọc thành "thị trường không có gì", tệ hơn
   hẳn một bảng cũ có ghi ngày.
   ═══════════════════════════════════════════════════════ */

import { writeFile, mkdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const RA = join(ROOT, "ho-bo", "assets", "js", "v", "dong-tien.js");

/* Số chuỗi được lấy nguyên chuỗi thời gian. Mỗi chuỗi là một lời
   gọi riêng, nên con số này là đánh đổi thẳng giữa độ rộng bảng
   và thời gian chạy. 20 chuỗi ≈ 20 lời gọi ≈ 12 giây. */
const SO_CHUOI = 20;
/* Số ngày giữ lại cho đường nến nhỏ trong bảng. 90 điểm/chuỗi ×
   20 chuỗi ≈ 1.800 số ≈ 14 KB sau khi làm tròn. */
const NGAY_NEN = 90;

const nguon = [];
const log = (...a) => console.log(...a);

/* ── lấy dữ liệu ─────────────────────────────────────────
   Thử ba lần, giãn dần. Ghi lại mọi lượt vào sổ `nguon` để trang
   có thể tự khai nó đang đứng trên nguồn nào — một bảng số không
   nói được nó lấy số ở đâu thì không kiểm chứng được. */
async function lay(nhan, url, { batBuoc = false } = {}) {
  for (let lan = 1; lan <= 3; lan++) {
    try {
      const c = new AbortController();
      const hen = setTimeout(() => c.abort(), 60_000);
      const r = await fetch(url, {
        signal: c.signal,
        headers: { accept: "application/json", "user-agent": "blockchainworld-hobu/1.0" }
      });
      clearTimeout(hen);
      if (!r.ok) throw new Error("HTTP " + r.status);
      const j = await r.json();
      nguon.push({ nhan, url: url.split("?")[0], ok: true });
      return j;
    } catch (e) {
      if (lan === 3) {
        nguon.push({ nhan, url: url.split("?")[0], ok: false, loi: String(e.message || e).slice(0, 80) });
        if (batBuoc) throw new Error(`nguồn lõi "${nhan}" ngã: ${e.message}`);
        log(`  ⚠ ${nhan}: ${e.message} — bỏ qua, phần này sẽ trống`);
        return null;
      }
      await new Promise((s) => setTimeout(s, lan * 1500));
    }
  }
  return null;
}

/* ── tiện ──────────────────────────────────────────────── */
const so = (x) => (Number.isFinite(x) ? x : 0);
const lam = (x, n = 2) => (Number.isFinite(x) ? Number(x.toFixed(n)) : null);
/* Đổi % giữa hai mốc. Mẫu số 0 thì trả null chứ đừng trả 0: "không
   đổi" và "không biết" là hai chuyện khác nhau, và trang vẽ chúng
   khác nhau. */
const pt = (moi, cu) => (Number.isFinite(moi) && Number.isFinite(cu) && cu > 0 ? lam(((moi - cu) / cu) * 100) : null);

/* Chuẩn hoá tên chuỗi để ghép ba bảng khác nhau về cùng một khoá.
   /v2/chains trả "OP Mainnet", stablecoinchains trả "Optimism",
   còn breakdown của phí trả "optimism". Không có bảng bí danh này
   thì ba cột đó lệch hàng mà không có gì báo — cột phí của Base
   rơi vào dòng BSC chẳng hạn. */
const BI_DANH = {
  "op mainnet": "optimism", op: "optimism", "optimism mainnet": "optimism",
  bsc: "binance", "bnb chain": "binance", "bnb smart chain": "binance", binance: "binance",
  avax: "avalanche", avalanche: "avalanche",
  "arbitrum one": "arbitrum", arbitrum: "arbitrum",
  "polygon pos": "polygon", matic: "polygon",
  "zksync era": "zksync", "era": "zksync",
  "ethereum mainnet": "ethereum",
  xdai: "gnosis",
  "hyperliquid l1": "hyperliquid", hyperevm: "hyperliquid"
};
function khoa(ten) {
  const t = String(ten || "").trim().toLowerCase();
  return BI_DANH[t] || t.replace(/\s+/g, "");
}

/* Cộng breakdown24h của mọi giao thức về từng chuỗi.
   DefiLlama có endpoint riêng cho mỗi chuỗi (/overview/fees/base…)
   nhưng đó là 20 lời gọi thêm cho thứ đã nằm sẵn trong bảng vừa
   tải. Cộng tại chỗ rẻ hơn hẳn. */
function congTheoChuoi(bang) {
  const gom = {};
  for (const p of (bang && bang.protocols) || []) {
    const bd = p.breakdown24h;
    if (!bd) continue;
    for (const [ch, v] of Object.entries(bd)) {
      let t = 0;
      if (typeof v === "number") t = v;
      else if (v && typeof v === "object") for (const x of Object.values(v)) t += so(Number(x));
      if (!t) continue;
      const k = khoa(ch);
      gom[k] = (gom[k] || 0) + t;
    }
  }
  return gom;
}

/* Chuỗi thời gian → giá trị cách đây N ngày. Mảng của DefiLlama là
   [{date: giây, tvl}] tăng dần, một điểm mỗi ngày — nhưng có chuỗi
   thiếu ngày, nên tìm theo MỐC THỜI GIAN chứ đừng đếm lùi chỉ số. */
function truoc(chuoi, ngay, khoaGiaTri = "tvl") {
  if (!Array.isArray(chuoi) || !chuoi.length) return null;
  const cuoi = chuoi[chuoi.length - 1];
  const moc = so(Number(cuoi.date)) - ngay * 86400;
  let tot = null;
  for (const d of chuoi) {
    const t = so(Number(d.date));
    if (t <= moc + 43200) tot = d;
    else break;
  }
  if (!tot) return null;
  const v = tot[khoaGiaTri];
  return Number.isFinite(Number(v)) ? Number(v) : null;
}
const cuoiCua = (chuoi, k = "tvl") => {
  if (!Array.isArray(chuoi) || !chuoi.length) return null;
  const v = chuoi[chuoi.length - 1][k];
  return Number.isFinite(Number(v)) ? Number(v) : null;
};

/* ═══════════════ LẤY SỐ ═══════════════ */
log("Hộ Bộ — lấy số liệu dòng tiền…\n");
const t0 = Date.now();

/* Bốn nguồn LÕI: thiếu bất kỳ cái nào thì cả trang mất nghĩa, nên
   chúng ném lỗi thay vì trả null. Số còn lại là phần bày thêm. */
const [chains, lsTong, chainStable, stables] = await Promise.all([
  lay("chuỗi · TVL hiện tại", "https://api.llama.fi/v2/chains", { batBuoc: true }),
  lay("chuỗi · TVL theo ngày", "https://api.llama.fi/v2/historicalChainTvl", { batBuoc: true }),
  lay("stablecoin theo chuỗi", "https://stablecoins.llama.fi/stablecoinchains", { batBuoc: true }),
  lay("stablecoin · phát hành", "https://stablecoins.llama.fi/stablecoins?includePrices=true", { batBuoc: true })
]);

const [lsStable, protocols, phi, dex, hacks, giaMajor] = await Promise.all([
  lay("stablecoin theo ngày", "https://stablecoins.llama.fi/stablecoincharts/all"),
  lay("giao thức · TVL", "https://api.llama.fi/protocols"),
  lay("phí & doanh thu", "https://api.llama.fi/overview/fees?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"),
  lay("khối lượng DEX", "https://api.llama.fi/overview/dexs?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"),
  lay("vụ mất tiền", "https://api.llama.fi/hacks"),
  lay("giá tham chiếu", "https://coins.llama.fi/prices/current/coingecko:bitcoin,coingecko:ethereum")
]);
const pools = await lay("lợi suất", "https://yields.llama.fi/pools");

/* ── các chuỗi lớn + lịch sử riêng ─────────────────────── */
const topChuoi = (chains || [])
  .filter((c) => so(c.tvl) > 0 && c.name)
  .sort((a, b) => b.tvl - a.tvl)
  .slice(0, SO_CHUOI);

const lsChuoi = {};
for (const c of topChuoi) {
  const j = await lay(`lịch sử ${c.name}`, `https://api.llama.fi/v2/historicalChainTvl/${encodeURIComponent(c.name)}`);
  if (j) lsChuoi[c.name] = j;
}

/* ═══════════════ DỰNG ═══════════════ */

/* ── tổng toàn thị trường ──────────────────────────────── */
const tvlNay = cuoiCua(lsTong) ?? (chains || []).reduce((n, c) => n + so(c.tvl), 0);
const tvl1d = truoc(lsTong, 1), tvl7d = truoc(lsTong, 7), tvl30d = truoc(lsTong, 30);

const stableNay = cuoiCua(lsStable, "totalCirculatingUSD")?.peggedUSD
  ?? (() => {
    const c = lsStable && lsStable.length ? lsStable[lsStable.length - 1] : null;
    return c && c.totalCirculatingUSD ? so(c.totalCirculatingUSD.peggedUSD) : null;
  })();
function stableTruoc(n) {
  if (!Array.isArray(lsStable) || !lsStable.length) return null;
  const cuoi = lsStable[lsStable.length - 1];
  const moc = so(Number(cuoi.date)) - n * 86400;
  let tot = null;
  for (const d of lsStable) { if (so(Number(d.date)) <= moc + 43200) tot = d; else break; }
  return tot && tot.totalCirculatingUSD ? so(tot.totalCirculatingUSD.peggedUSD) : null;
}
const stableTong = Number.isFinite(stableNay) ? stableNay
  : (lsStable && lsStable.length ? so(lsStable[lsStable.length - 1].totalCirculatingUSD?.peggedUSD) : null);

const phiChuoi = congTheoChuoi(phi);
const dexChuoi = congTheoChuoi(dex);

const tong = {
  tvl: lam(tvlNay, 0),
  tvl_d1: pt(tvlNay, tvl1d), tvl_d7: pt(tvlNay, tvl7d), tvl_d30: pt(tvlNay, tvl30d),
  stable: lam(stableTong, 0),
  stable_d7: pt(stableTong, stableTruoc(7)), stable_d30: pt(stableTong, stableTruoc(30)),
  dex_24h: lam(so(dex && dex.total24h), 0),
  dex_d1: lam(Number(dex && dex.change_1d)),
  dex_7d7d: lam(Number(dex && dex.change_7dover7d)),
  phi_24h: lam(so(phi && phi.total24h), 0),
  phi_d1: lam(Number(phi && phi.change_1d)),
  phi_7d7d: lam(Number(phi && phi.change_7dover7d)),
  btc: lam(so(giaMajor?.coins?.["coingecko:bitcoin"]?.price), 0),
  eth: lam(so(giaMajor?.coins?.["coingecko:ethereum"]?.price), 0)
};

/* Đường nến của tổng TVL và tổng stablecoin — 180 ngày, lấy cách
   ngày để file không phình. */
function nen(chuoi, k = "tvl", ngay = NGAY_NEN, buoc = 2) {
  if (!Array.isArray(chuoi)) return [];
  const cat = chuoi.slice(-ngay);
  const ra = [];
  for (let i = 0; i < cat.length; i += buoc) {
    const d = cat[i];
    let v = d[k];
    if (v && typeof v === "object") v = v.peggedUSD;
    if (Number.isFinite(Number(v))) ra.push(Number(Number(v).toPrecision(6)));
  }
  return ra;
}
tong.nen_tvl = nen(lsTong, "tvl", 180, 2);
tong.nen_stable = nen(lsStable, "totalCirculatingUSD", 180, 2);

/* ── bảng chuỗi ────────────────────────────────────────── */
const stableTheoChuoi = {};
for (const s of chainStable || []) {
  const v = s.totalCirculatingUSD;
  let t = 0;
  if (v && typeof v === "object") for (const x of Object.values(v)) t += so(Number(x));
  if (t) stableTheoChuoi[khoa(s.name)] = t;
}

const chuoi = topChuoi.map((c) => {
  const ls = lsChuoi[c.name];
  const k = khoa(c.name);
  const stb = stableTheoChuoi[k] ?? null;
  return {
    ten: c.name,
    ma: c.tokenSymbol || null,
    tvl: lam(so(c.tvl), 0),
    d1: pt(so(c.tvl), truoc(ls, 1)),
    d7: pt(so(c.tvl), truoc(ls, 7)),
    d30: pt(so(c.tvl), truoc(ls, 30)),
    stable: stb === null ? null : lam(stb, 0),
    /* Stablecoin trên chuỗi CHIA CHO TVL của chuỗi, tính bằng LẦN.
       Ban đầu chỗ này viết là phần trăm và ra những con số vô nghĩa
       — Tron 1.927%, Ethereum 358%. Không phải lỗi phép chia: TVL
       của DefiLlama là tài sản khoá trong các giao thức, còn
       stablecoin lưu hành nằm ngoài cái đó, nên tỷ lệ vượt 100% là
       chuyện bình thường chứ không phải bất thường.

       Đọc bằng "lần" thì con số lại nói đúng một điều đáng nghe:
       Tron 19× nghĩa là chuỗi đó gần như chỉ để chuyển USDT chứ
       hầu như không có DeFi; Base 1,1× nghĩa là tiền tới đó là để
       làm việc ngay. */
    tyle: stb && so(c.tvl) > 0 ? lam(stb / so(c.tvl), 1) : null,
    phi24h: phiChuoi[k] ? lam(phiChuoi[k], 0) : null,
    dex24h: dexChuoi[k] ? lam(dexChuoi[k], 0) : null,
    nen: nen(ls, "tvl", NGAY_NEN, 1)
  };
});

/* ── nhóm ngành ────────────────────────────────────────────
   BỎ HẲN nhóm `CEX`. Nó là dự trữ ví sàn tập trung — 250 tỷ đô,
   gấp ba TVL của toàn bộ phần còn lại — và nó không phải vốn nằm
   trong hợp đồng on-chain. Để nguyên thì biểu đồ nhóm ngành chỉ
   còn một cột và mọi ngành thật bị ép thành vạch mờ dưới đáy.

   Cũng vì cùng lý do đó mà TỔNG các nhóm KHÔNG bằng TVL tổng ở
   trên: DefiLlama khử trùng lặp khi cộng TVL theo chuỗi (một đồng
   ETH vừa stake vừa đem thế chấp chỉ tính một lần), còn cộng theo
   nhóm thì không. Trang phải nói rõ chuyện này chứ đừng để người
   đọc tự trừ hai con số rồi tưởng có cái sai. */
const BO_NHOM = new Set(["CEX"]);
const nhomGom = {};
/* Dựng lại TVL cách đây N ngày từ mức hiện tại và % đã đổi.
   `c <= -100` là dữ liệu hỏng (giảm hơn 100% thì gốc phải âm) —
   trả null để giao thức đó rơi khỏi cả tử lẫn mẫu. */
const truocDo = (tvl, c) => (Number.isFinite(c) && c > -99.9 ? tvl / (1 + c / 100) : null);
for (const p of protocols || []) {
  if (!p.category || BO_NHOM.has(p.category) || !Number.isFinite(p.tvl) || p.tvl <= 0) continue;
  const g = (nhomGom[p.category] ||= { ten: p.category, tvl: 0, so: 0, n7: 0, c7: 0, n1: 0, c1: 0 });
  g.tvl += p.tvl; g.so++;
  /* CỘNG VỐN RỒI MỚI CHIA, chứ không lấy trung bình các phần trăm.
     Hai cách nghe như nhau và ra kết quả khác hẳn nhau.

     Bản đầu tiên lấy trung bình % có trọng số theo TVL và ra "Dexs
     +47,4% trong 7 ngày" cho một tuần bình lặng. Thủ phạm là Jupiter
     Lend DEX: TVL 6 triệu đô, nhưng +74.493% vì tuần trước nó mới có
     8 nghìn đô. Trọng số theo TVL không đỡ nổi — vô cực nhân một số
     nhỏ vẫn là số to, và một mình nó đóng 44,6 trong 47,4 điểm.

     Cộng vốn thì chuyện đó tự tan: giao thức ấy thêm 6 triệu vào cột
     "nay" và 8 nghìn vào cột "tuần trước", đẩy cả nhóm đúng +0,05%.
     Đó cũng là con số người ta thật sự muốn biết — "vốn của cả ngành
     này tuần rồi tăng hay giảm bao nhiêu" — chứ không phải "giao
     thức trung bình của ngành này đổi bao nhiêu phần trăm". */
  const t7 = truocDo(p.tvl, p.change_7d);
  if (t7 !== null) { g.n7 += p.tvl; g.c7 += t7; }
  const t1 = truocDo(p.tvl, p.change_1d);
  if (t1 !== null) { g.n1 += p.tvl; g.c1 += t1; }
}
const nhom = Object.values(nhomGom)
  .sort((a, b) => b.tvl - a.tvl)
  .slice(0, 16)
  .map((g) => ({
    ten: g.ten, tvl: lam(g.tvl, 0), so: g.so,
    d1: pt(g.n1, g.c1), d7: pt(g.n7, g.c7)
  }));

/* ── ma trận chuỗi × nhóm ngành ────────────────────────────
   Đây là thứ dựng nên Bản đồ dòng tiền, và nó là dữ liệu THẬT chứ
   không phải sơ đồ vẽ tay: mỗi giao thức khai TVL của nó trên từng
   chuỗi trong `chainTvls`, mà bản thân nó thì thuộc một nhóm ngành.
   Cộng lại là ra "trên chuỗi này, vốn đang nằm ở những ngành nào".

   ── HAI CON SỐ, HAI PHÉP ĐO — ĐỪNG ÉP CHÚNG BẰNG NHAU ──
   Tổng của bản đồ này LỚN HƠN TVL chuỗi ở bảng Kho Bạc, và chênh
   không đều: Ethereum 3,4× · Solana 2,8× · Bitcoin 7,5×. Đã thử
   trừ hai khoá `-doublecounted` và `-liquidstaking` như DefiLlama
   làm — bản API này không trả hai khoá đó, trừ xong y nguyên.

   Nhưng cả hai con số đều đúng, chúng chỉ đo hai thứ:

     TVL chuỗi     phía CHUỖI — một đô chỉ được đếm một lần
     bản đồ này    phía GIAO THỨC — một đô đi qua mấy giao thức
                   thì được đếm mấy lần

   Một đồng ETH đem stake ở Lido rồi lấy stETH thế chấp ở Aave là
   một đô nằm ở hai chỗ, và câu "ngành nào đang giữ vốn" thì phải
   đếm cả hai. Bitcoin chênh 7,5× vì 21 tỷ BTC đang nằm trong các
   cầu nối kiểu WBTC — có thật, chỉ là không thuộc DeFi *trên*
   Bitcoin.

   Nên bản đồ vẽ theo TỶ TRỌNG trong từng chuỗi và tự khai tổng
   riêng của nó. Ép hai phép đo về một số là chọn một con số sai
   để hai bảng trông hợp nhau. */
const CAT_PHU = new Set(["borrowed", "staking", "pool2", "treasury", "vesting", "offers", "doublecounted", "liquidstaking"]);
const topLuoi = topChuoi.slice(0, 9);
const tenNhomTop = nhom.slice(0, 8).map((n) => n.ten);

/* `chainTvls` gọi tên chuỗi khác /v2/chains: BSC ở đó là "Binance".
   Đối chiếu thẳng theo tên thì BSC — chuỗi lớn thứ hai — biến mất
   khỏi bản đồ, và mất im lặng: bản đồ vẫn vẽ đẹp, chỉ thiếu một
   cột. Nên ghép qua `khoa()`, cùng bảng bí danh dùng cho cột phí. */
const khoaTop = new Map(topLuoi.map((c) => [khoa(c.name), c.name]));

/* Map lồng Map, KHÔNG phải object khoá bằng chuỗi ghép. Ghép hai
   tên rồi tách lại là hỏng ngay dòng đầu: có chuỗi tên "OP Mainnet"
   và có nhóm tên "Liquid Staking", nên tách theo dấu cách thì "OP"
   thành tên chuỗi còn "Mainnet" thành tên nhóm. */
const oLuoi = new Map();
for (const p of protocols || []) {
  if (!p.category || BO_NHOM.has(p.category) || !p.chainTvls) continue;
  const nh = tenNhomTop.includes(p.category) ? p.category : "Khác";
  for (const [k, v] of Object.entries(p.chainTvls)) {
    if (k.includes("-") || CAT_PHU.has(k.toLowerCase())) continue;
    const t = Number(v);
    if (!Number.isFinite(t) || t <= 0) continue;
    const ten = khoaTop.get(khoa(k));
    if (!ten) continue;
    if (!oLuoi.has(ten)) oLuoi.set(ten, new Map());
    const hang = oLuoi.get(ten);
    hang.set(nh, (hang.get(nh) || 0) + t);
  }
}
const luoi = [];
for (const [ch, hang] of oLuoi) {
  for (const [nh, v] of hang) if (v > 5e6) luoi.push({ chuoi: ch, nhom: nh, tvl: lam(v, 0) });
}
luoi.sort((a, b) => b.tvl - a.tvl);

/* ── giao thức chuyển động mạnh ────────────────────────── */
const loc = (protocols || []).filter(
  (p) => Number.isFinite(p.tvl) && p.tvl >= 50e6 && Number.isFinite(p.change_7d) && Math.abs(p.change_7d) < 400
);
const gonGiaoThuc = (p) => ({
  ten: p.name, nhom: p.category || null, chuoi: p.chain || null,
  tvl: lam(p.tvl, 0), d1: lam(p.change_1d), d7: lam(p.change_7d), slug: p.slug || null
});
const giaoThuc = {
  len: [...loc].sort((a, b) => b.change_7d - a.change_7d).slice(0, 14).map(gonGiaoThuc),
  xuong: [...loc].sort((a, b) => a.change_7d - b.change_7d).slice(0, 14).map(gonGiaoThuc)
};

/* ── stablecoin và độ neo giá ──────────────────────────── */
const stable = ((stables && stables.peggedAssets) || [])
  .map((s) => {
    const cir = so(s.circulating?.peggedUSD ?? s.circulating?.peggedVAR ?? 0);
    const tuan = so(s.circulatingPrevWeek?.peggedUSD ?? s.circulatingPrevWeek?.peggedVAR ?? 0);
    const thang = so(s.circulatingPrevMonth?.peggedUSD ?? s.circulatingPrevMonth?.peggedVAR ?? 0);
    return {
      ten: s.name, ma: s.symbol, loai: s.pegMechanism || null, neo: s.pegType || null,
      cung: lam(cir, 0), d7: pt(cir, tuan), d30: pt(cir, thang),
      gia: Number.isFinite(Number(s.price)) ? lam(Number(s.price), 4) : null,
      /* Chỉ tính lệch neo cho đồng neo theo USD. Đồng neo vàng hay
         euro mà so với 1,00 thì lệch vài chục phần trăm và bảng cảnh
         báo đỏ rực vì một phép so sai đơn vị. */
      lech: s.pegType === "peggedUSD" && Number.isFinite(Number(s.price))
        ? lam((Number(s.price) - 1) * 100, 2) : null,
      /* TÍCH LÃI, không phải mất neo. USYC và USDY là trái phiếu kho
         bạc token hoá: giá token tự bò lên trên 1 đô vì lãi cộng dồn
         vào chính token, đúng như thiết kế.

         Bản đầu tiên của script này chấm USDY +14,15% là "mất neo
         nghiêm trọng" và bật đèn ĐỎ cho toàn thị trường trong một
         ngày hoàn toàn bình thường. Nếu để nguyên, cảnh báo đó sẽ đỏ
         mãi mãi — và một đèn đỏ vĩnh viễn thì dạy người ta bỏ qua
         đèn đỏ, kể cả lần nó đúng.

         Nên đèn chỉ đọc lệch XUỐNG. Đó cũng là chiều duy nhất đáng
         sợ: stablecoin rẻ hơn 1 đô nghĩa là thị trường nghi ngờ khả
         năng đổi lại; đắt hơn 1 đô chưa bao giờ làm ai mất tiền. */
      tich: s.pegType === "peggedUSD" && Number.isFinite(Number(s.price)) && Number(s.price) > 1.02
    };
  })
  .filter((s) => so(s.cung) > 0)
  .sort((a, b) => b.cung - a.cung)
  .slice(0, 14);

/* ── vụ mất tiền ───────────────────────────────────────── */
const nay = Date.now() / 1000;
const loi = (hacks || [])
  .filter((h) => so(h.date) > nay - 730 * 86400)
  .sort((a, b) => b.date - a.date)
  .slice(0, 40)
  .map((h) => ({
    ten: h.name,
    ngay: new Date(so(h.date) * 1000).toISOString().slice(0, 10),
    mat: lam(so(h.amount), 0),
    cach: h.technique || null,
    loai: h.targetType || h.classification || null,
    chuoi: Array.isArray(h.chain) ? h.chain.slice(0, 3).join(", ") : (h.chain || null),
    nguon: h.source || null
  }));
const mat30 = (hacks || [])
  .filter((h) => so(h.date) > nay - 30 * 86400)
  .reduce((n, h) => n + so(h.amount), 0);
const mat365 = (hacks || [])
  .filter((h) => so(h.date) > nay - 365 * 86400)
  .reduce((n, h) => n + so(h.amount), 0);

/* ── lợi suất ──────────────────────────────────────────── */
/* Ba lớp lọc, mỗi lớp chặn một kiểu số đẹp mà vô nghĩa:
     tvlUsd ≥ 3 triệu   — hồ nhỏ thì APY nhảy theo một lệnh swap
     apy ≤ 150%         — trên mức đó gần như luôn là thưởng token
                          đang xả, không phải lợi suất giữ được
     apy > 0            — hồ chết vẫn nằm trong bảng với apy 0 */
const loiSuat = (Array.isArray(pools?.data) ? pools.data : Array.isArray(pools) ? pools : [])
  .filter((p) => so(p.tvlUsd) >= 3e6 && so(p.apy) > 0 && so(p.apy) <= 150)
  .sort((a, b) => b.apy - a.apy)
  .slice(0, 70)
  .map((p) => ({
    ho: p.symbol, duAn: p.project, chuoi: p.chain,
    tvl: lam(so(p.tvlUsd), 0),
    apy: lam(so(p.apy)), goc: lam(so(p.apyBase)), thuong: lam(so(p.apyReward)),
    on: p.stablecoin === true,
    il: p.ilRisk || null,
    /* sigma = độ lệch chuẩn của APY 30 ngày. Con số này mới phân
       biệt được "8% đều đặn" với "8% trung bình của một đường
       răng cưa" — hai thứ hiện lên bảng giống hệt nhau nếu chỉ
       nhìn cột APY. */
    dao: Number.isFinite(Number(p.sigma)) ? lam(Number(p.sigma), 3) : null
  }));

/* ═══════════════ CHẾ ĐỘ THỊ TRƯỜNG ═══════════════
   Sáu thành phần, mỗi cái cho một điểm trong [-1, +1], rồi lấy
   trung bình các thành phần ĐO ĐƯỢC (thiếu nguồn thì bỏ khỏi mẫu
   số, không tính là 0 — 0 nghĩa là "trung tính", còn thiếu nghĩa
   là "không biết", và gộp hai thứ đó lại là nói dối bằng số).

   Vì sao bày cả sáu thành phần ra trang: một cái kim chỉ 68/100
   không nói được gì và không cãi lại được. Bày ra thì người đọc
   thấy nó đứng trên cái gì và tự bất đồng được với cách chấm. */
function dai(x, thap, cao) {
  if (!Number.isFinite(x)) return null;
  if (cao === thap) return 0;
  return Math.max(-1, Math.min(1, ((x - thap) / (cao - thap)) * 2 - 1));
}
/* Chỉ đo lệch XUỐNG, và chỉ trên các đồng lớn — xem ghi chú `tich`
   ở phần stablecoin bên trên để biết vì sao chiều lên bị bỏ. */
const lechXuong = (s) => (s.lech !== null && s.lech < 0 ? -s.lech : 0);
const lechToiDa = stable
  .filter((s) => so(s.cung) > 1e9)
  .reduce((m, s) => Math.max(m, lechXuong(s)), 0);
const rong = (() => {
  const co = chuoi.filter((c) => c.d7 !== null);
  if (!co.length) return null;
  return co.filter((c) => c.d7 > 0).length / co.length;
})();

const THANH_PHAN = [
  { ma: "stable30", ten: "Vốn khô 30 ngày", y: "Tổng stablecoin đang lưu hành. Tăng là tiền mới vào chờ, giảm là tiền rút khỏi hệ.", gt: tong.stable_d30, don: "%", diem: dai(tong.stable_d30, -3, 3) },
  { ma: "tvl30", ten: "TVL 30 ngày", y: "Tổng tài sản đang khoá trong các giao thức.", gt: tong.tvl_d30, don: "%", diem: dai(tong.tvl_d30, -12, 12) },
  { ma: "tvl7", ten: "TVL 7 ngày", y: "Cùng chỉ số, nhìn gần hơn — bắt được chỗ đổi chiều sớm.", gt: tong.tvl_d7, don: "%", diem: dai(tong.tvl_d7, -6, 6) },
  { ma: "dex", ten: "Khối lượng DEX", y: "Tuần này so tuần trước. Đo mức chịu giao dịch, không phải mức giá.", gt: tong.dex_7d7d, don: "%", diem: dai(tong.dex_7d7d, -25, 25) },
  { ma: "rong", ten: "Độ rộng", y: "Bao nhiêu phần các chuỗi lớn tăng TVL trong 7 ngày. Một chuỗi kéo cả bảng thì độ rộng thấp.", gt: rong === null ? null : lam(rong * 100, 0), don: "%", diem: dai(rong === null ? null : rong * 100, 20, 80) },
  { ma: "neo", ten: "Sức khoẻ neo giá", y: "Mức chiết khấu sâu nhất so với mệnh giá trong các stablecoin trên 1 tỷ đô. Chỉ đọc chiều giảm — đắt hơn 1 đô chưa bao giờ làm ai mất tiền.", gt: lechToiDa ? lam(lechToiDa, 2) : 0, don: "%", diem: dai(-lechToiDa, -1, 0) }
];
const coDiem = THANH_PHAN.filter((t) => t.diem !== null);
const diemTho = coDiem.length ? coDiem.reduce((n, t) => n + t.diem, 0) / coDiem.length : 0;
const diem = Math.round(((diemTho + 1) / 2) * 100);
const NHAN = [
  [22, "Rất phòng thủ", "Tiền đang rút khỏi hệ trên nhiều mặt cùng lúc."],
  [42, "Phòng thủ", "Nghiêng về rút vốn, nhưng chưa đồng loạt."],
  [58, "Trung tính", "Vào và ra gần bằng nhau — chưa có chiều rõ."],
  [78, "Ưa rủi ro", "Vốn đang chảy vào và lan ra nhiều chuỗi."],
  [101, "Rất ưa rủi ro", "Vốn vào mạnh và đều — cũng là lúc dễ trả giá đắt cho một sai lầm."]
];
const nhanChon = NHAN.find(([n]) => diem < n) || NHAN[NHAN.length - 1];
const cheDo = {
  diem,
  nhan: nhanChon[1],
  y: nhanChon[2],
  do: coDiem.length,
  tong: THANH_PHAN.length,
  thanhPhan: THANH_PHAN.map((t) => ({ ...t, diem: t.diem === null ? null : lam(t.diem, 2) }))
};

/* ═══════════════ BẢNG CẢNH BÁO ═══════════════
   Toàn bộ là SO NGƯỠNG SỐ HỌC, không gọi model — cùng lối với
   scripts/build-quantrac.mjs. Chỗ nào số trả lời được thì đừng
   trả tiền cho model trả lời, và cũng đừng để nó đoán.

   Mỗi cảnh báo mang theo con số đã dùng để chấm, nên đọc được
   ngược lại: không đồng ý với ngưỡng thì vẫn thấy dữ liệu thô. */
const canhBao = [];
const bao = (ma, ten, muc, so_, y) => canhBao.push({ ma, ten, muc, so: so_, y });

const lechNang = stable.filter((s) => so(s.cung) > 5e8 && lechXuong(s) >= 0.5);
bao("neo", "Neo giá stablecoin", lechToiDa >= 2 ? "r" : lechToiDa >= 0.5 ? "y" : "g",
  lechToiDa ? `chiết khấu tối đa ${lam(lechToiDa, 2)}%` : "trong ngưỡng",
  lechNang.length
    ? `Đang giao dịch dưới mệnh giá: ${lechNang.map((s) => `${s.ma} ${s.lech}%`).join(", ")}.`
    : "Không đồng lớn nào bị chiết khấu quá 0,5% so với mệnh giá. Đèn này chỉ đọc chiều GIẢM — token tích lãi như USYC, USDY vượt 1 đô là đúng thiết kế, không phải mất neo.");

bao("rut", "Stablecoin rút khỏi hệ",
  tong.stable_d7 !== null && tong.stable_d7 <= -3 ? "r" : tong.stable_d7 !== null && tong.stable_d7 <= -1 ? "y" : "g",
  tong.stable_d7 === null ? "chưa đo được" : `${tong.stable_d7 > 0 ? "+" : ""}${tong.stable_d7}% / 7 ngày`,
  "Tổng cung stablecoin co lại nghĩa là tiền rời hệ thật, không phải xoay giữa các tài sản.");

bao("tvl", "Tài sản khoá sụt nhanh",
  tong.tvl_d7 !== null && tong.tvl_d7 <= -15 ? "r" : tong.tvl_d7 !== null && tong.tvl_d7 <= -8 ? "y" : "g",
  tong.tvl_d7 === null ? "chưa đo được" : `${tong.tvl_d7 > 0 ? "+" : ""}${tong.tvl_d7}% / 7 ngày`,
  "TVL sụt vừa có thể do giá tài sản giảm, vừa có thể do người ta rút. Đọc kèm cột stablecoin để tách hai chuyện.");

const chayMau = chuoi.filter((c) => c.d7 !== null && c.d7 <= -15);
bao("chuoi", "Chuỗi đang chảy máu vốn", chayMau.length >= 4 ? "r" : chayMau.length >= 1 ? "y" : "g",
  `${chayMau.length} / ${chuoi.length} chuỗi`,
  chayMau.length ? `Giảm trên 15% trong 7 ngày: ${chayMau.map((c) => `${c.ten} ${c.d7}%`).join(", ")}.`
    : "Không chuỗi lớn nào mất quá 15% TVL trong tuần.");

bao("hack", "Tiền mất vì tấn công", mat30 >= 200e6 ? "r" : mat30 >= 50e6 ? "y" : "g",
  `${lam(mat30 / 1e6, 1)} triệu $ / 30 ngày`,
  `Cộng 12 tháng: ${lam(mat365 / 1e6, 0)} triệu $. Nguồn là bảng vụ việc của DefiLlama, chỉ gồm vụ đã xác nhận.`);

const top1 = chuoi[0];
const phanTop1 = top1 && tong.tvl ? (top1.tvl / tong.tvl) * 100 : null;
bao("tap-trung", "Tập trung vào một chuỗi",
  phanTop1 !== null && phanTop1 >= 65 ? "y" : "g",
  phanTop1 === null ? "chưa đo được" : `${top1.ten} giữ ${lam(phanTop1, 1)}%`,
  "Không phải lỗi — nhưng vốn dồn một chỗ thì một sự cố ở đó là sự cố của cả thị trường.");

bao("phi", "Phí trả cho hạ tầng",
  tong.phi_7d7d !== null && tong.phi_7d7d <= -35 ? "y" : "g",
  tong.phi_7d7d === null ? "chưa đo được" : `${tong.phi_7d7d > 0 ? "+" : ""}${tong.phi_7d7d}% tuần/tuần`,
  "Phí là thứ người dùng thật sự trả. Phí co nhanh hơn TVL nghĩa là hoạt động nguội trước khi vốn kịp rút.");

/* ═══════════════ GHI ═══════════════ */
const gio = new Date();
const hai = (n) => String(n).padStart(2, "0");
const ngayVN = `${hai(gio.getUTCDate())}/${hai(gio.getUTCMonth() + 1)}/${gio.getUTCFullYear()}`;
const tomTat = `${chuoi.length} chuỗi · TVL ${lam(so(tong.tvl) / 1e9, 1)} tỷ $`;

/* Thứ tự khoá ở đây KHÔNG tuỳ tiện: assets/js/portal.js của Cổng
   Thành chỉ đọc 900 byte đầu file rồi huỷ dòng tải, nên
   `generatedAt`, `date` và `tomTat` phải nằm trong khúc đó. Đẩy
   chúng xuống dưới là thẻ Hộ Bộ ở Cổng Thành mất ngày cập nhật mà
   không có lỗi nào báo. */
const goi = {
  generatedAt: gio.toISOString(),
  date: ngayVN,
  tomTat,
  cheDo, tong, chuoi, nhom, luoi, giaoThuc, stable, loiSuat, loi, canhBao,
  mat30: lam(mat30, 0), mat365: lam(mat365, 0),
  nguon
};

const dau = `/* TỰ SINH bởi scripts/build-hobu.mjs — đừng sửa tay.
   Nguồn: DefiLlama (TVL, phí, DEX, stablecoin, vụ mất tiền, lợi suất).
   Nhánh MẠNG-TRƯỚC của sw.js, nên KHÔNG cần nâng CACHE_VERSION. */
`;
await mkdir(dirname(RA), { recursive: true });
await writeFile(RA, dau + "window.HOBU = " + JSON.stringify(goi) + ";\n", "utf8");

const kb = (Buffer.byteLength(dau + JSON.stringify(goi)) / 1024).toFixed(0);
log(`\n✓ ho-bo/assets/js/v/dong-tien.js · ${kb} KB · ${((Date.now() - t0) / 1000).toFixed(1)}s`);
log(`  chế độ ${diem}/100 (${cheDo.nhan}) · ${chuoi.length} chuỗi · ${nhom.length} nhóm · ${stable.length} stablecoin`);
log(`  ${loiSuat.length} hồ lợi suất · ${loi.length} vụ mất tiền · ${canhBao.filter((c) => c.muc !== "g").length}/${canhBao.length} đèn không xanh`);
const nga = nguon.filter((n) => !n.ok);
if (nga.length) log(`  ⚠ ${nga.length} nguồn ngã: ${nga.map((n) => n.nhan).join(", ")}`);
