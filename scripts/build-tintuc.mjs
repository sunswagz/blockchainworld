/* ═══════════════════════════════════════════════════════
   THÁI BỘC TỰ · TIN TỨC — thế giới bên ngoài đang nói gì.

   Chạy: npm run tintuc  (hoặc node scripts/build-tintuc.mjs)
   Ghi:  thai-boc-tu/assets/js/v/tin-tuc.js

   ── VÌ SAO CÓ MỤC NÀY TRONG MỘT CUNG ĐO PHỤ THUỘC ─────
   Bảng đoàn tàu trả lời "cấu trúc thế nào", công trường trả lời
   "ai đang xây". Còn thiếu "hôm nay có chuyện gì" — và quan trọng
   hơn: chuyện đó rơi vào TOA NÀO.

   Nên mỗi bài ở đây được gắn nhãn toa bằng từ khoá. Một tin về
   Tether không nằm lơ lửng trong mục tin; nó nằm ở toa 04, cạnh
   con số 308 tỷ lưu hành và tỷ lệ tập trung 59%. Đó là cả lý do
   mục này thuộc về cung này chứ không phải một trang tin thường.

   ── ẢNH: TRỎ THẲNG, KHÔNG TẢI VỀ ──────────────────────
   Cân nhắc thật, và ghi lại để đừng ai đảo ngược mà không biết giá:

   TẢI VỀ giữ ảnh vĩnh viễn và không phiền người xem. Nhưng bot chạy
   4 lượt/ngày × ~30 bài, ảnh tin tức 100–400 KB mỗi cái, và git giữ
   MỌI phiên bản mãi mãi. Vài tháng là lịch sử repo phình hơn cả
   site. Bản site đã 21,8 MB và Pinata free chỉ 1 GB — xem mục
   "IPFS pin theo tag" trong CLAUDE.md.

   TRỎ THẲNG không tốn byte nào của repo. Giá phải trả: trình duyệt
   người xem gọi tới CDN của từng toà soạn, nên IP của họ lộ ra ở
   đó. Trang này vốn đã tải phông từ Google Fonts nên không phải
   loại việc mới, nhưng vẫn phải nói rõ ở chân trang chứ không lặng
   lẽ làm.

   Hệ quả phải giữ: `<img>` trong app.js luôn có `referrerpolicy`
   là no-referrer, `loading="lazy"`, và `onerror` ẩn hẳn khung ảnh.
   Thiếu onerror thì một ảnh 404 để lại cái icon vỡ — xấu hơn hẳn
   không có ảnh.

   ── CHỈ NGUỒN CÓ TÊN, VÀ LUÔN DẪN NGƯỢC ───────────────
   Sáu nguồn dưới đây đều là toà soạn hoặc blog chính thức có tên
   thật. Không lấy tin tổng hợp lại của bên thứ ba, không lấy nguồn
   ẩn danh. Mỗi bài LUÔN hiện tên nguồn và bấm được sang bài gốc —
   cung này không viết lại tin của ai, nó chỉ chỉ đường.

   Hai nguồn đã thử và KHÔNG dùng được, đừng mất công thử lại:
   theblock.co trả 403 cho mọi client tự động, a16zcrypto.com/feed
   trả 404.

   ── HỎNG MỘT NGUỒN KHÔNG PHẢI HỎNG CẢ MỤC ─────────────
   Mỗi nguồn ngã riêng. Còn ít nhất một nguồn có bài thì vẫn ghi;
   TẤT CẢ cùng ngã thì thoát 1 và giữ bản cũ. Bảng tin trống bị đọc
   thành "thế giới không có tin gì", đúng kiểu nói dối mà cả cung
   này tránh.
   ═══════════════════════════════════════════════════════ */

import { writeFile, mkdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const RA = join(ROOT, "thai-boc-tu", "assets", "js", "v", "tin-tuc.js");

const NGUON = [
  { ma: "coindesk", ten: "CoinDesk", url: "https://www.coindesk.com/arc/outboundfeeds/rss/" },
  { ma: "cointelegraph", ten: "Cointelegraph", url: "https://cointelegraph.com/rss" },
  { ma: "decrypt", ten: "Decrypt", url: "https://decrypt.co/feed" },
  { ma: "bitcoinmag", ten: "Bitcoin Magazine", url: "https://bitcoinmagazine.com/feed" },
  { ma: "ethfound", ten: "Ethereum Foundation", url: "https://blog.ethereum.org/en/feed.xml" },
  { ma: "vitalik", ten: "Vitalik Buterin", url: "https://vitalik.eth.limo/feed.xml" }
];

/* ═══════════ GẮN BÀI VÀO TOA ═══════════
   Từ khoá thường, khớp không phân biệt hoa thường trên tiêu đề +
   tóm tắt. Thứ tự trong mảng là thứ tự ƯU TIÊN: bài khớp nhiều toa
   thì lấy toa đứng trước.

   Vì sao xếp hạ tầng trước ứng dụng: một bài "Aave triển khai trên
   Base" khớp cả t02 (Base) lẫn t06 (Aave), và điều đáng nói của nó
   là tín dụng chứ không phải mở rộng. Nên toa hẹp đứng trước toa
   rộng, chứ không phải toa quan trọng đứng trước.

   Không khớp gì thì để null — mục "chưa xếp toa" ở giao diện. Đừng
   ép mọi bài vào một toa: gắn sai còn tệ hơn không gắn, vì người
   đọc sẽ tin cái nhãn. */
const NHAN = [
  { toa: "t16", tu: ["meme coin", "memecoin", "dogecoin", " doge", "shiba", "pepe", "bonk", "fartcoin"] },
  { toa: "t12", tu: ["ai agent", "agentic", "artificial intelligence", " ai ", "machine learning", "erc-8004"] },
  { toa: "t09", tu: ["rwa", "real-world asset", "real world asset", "tokenized treasur", "tokenization", "tokenised"] },
  { toa: "t08", tu: ["restaking", "liquid staking", "eigenlayer", "lido", "staking", "validator"] },
  { toa: "t03", tu: ["oracle", "chainlink", "pyth", "cross-chain", "bridge", "interoperab"] },
  { toa: "t04", tu: ["stablecoin", "tether", "usdt", "usdc", "circle", "depeg", "dai "] },
  { toa: "t07", tu: ["perpetual", "derivative", "futures", "options", "leverage", "hyperliquid", "liquidat"] },
  { toa: "t06", tu: ["lending", "borrow", "aave", "compound", "morpho", "collateral", "credit"] },
  { toa: "t05", tu: ["uniswap", "dex ", "liquidity", "amm", "swap", "curve finance"] },
  { toa: "t14", tu: ["privacy", "zero-knowledge", "zk-", "monero", "zcash", "anonym", "mixer"] },
  { toa: "t13", tu: ["identity", "worldcoin", " ens ", "did ", "reputation", "passport"] },
  { toa: "t11", tu: ["depin", "filecoin", "helium", "render network", "storage network", "gpu"] },
  { toa: "t15", tu: ["nft", "gaming", "metaverse", "play-to-earn", "opensea"] },
  { toa: "t10", tu: ["payment", "ripple", " xrp", "remittance", "cross-border", "settlement rail"] },
  { toa: "t18", tu: ["ordinals", "runes", "btcfi", "bitcoin layer", "stacks", "babylon"] },
  { toa: "t17", tu: ["binance", "coinbase", "kraken", "okx", "bybit", "exchange", " etf", "custody"] },
  { toa: "t02", tu: ["layer 2", "layer-2", " l2 ", "rollup", "arbitrum", "optimism", "zksync", "starknet", "base network", "scaling"] },
  { toa: "t01", tu: ["ethereum", "solana", "bitcoin", "avalanche", "cardano", "layer 1", " l1 ", "hard fork", "upgrade", "consensus"] }
];

function gan(chu) {
  const s = " " + String(chu || "").toLowerCase().replace(/\s+/g, " ") + " ";
  for (const n of NHAN) for (const t of n.tu) if (s.indexOf(t) !== -1) return n.toa;
  return null;
}

/* ═══════════ ĐỌC RSS / ATOM ═══════════
   Viết tay chứ không kéo thư viện: repo này cố ý không có
   node_modules, và thứ cần ở đây chỉ là bốn trường trên mỗi mục.

   Không dùng bộ phân tích XML đầy đủ vì không cần — nhưng cũng
   KHÔNG dựa vào regex để hiểu cấu trúc lồng nhau. Cách làm: cắt
   theo thẻ mục (<item> hoặc <entry>), rồi trong từng mảnh mới lấy
   trường. Mảnh đã cắt thì không còn lồng nhau nữa. */
function goHtml(s) {
  return String(s || "")
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&").replace(/&lt;/gi, "<").replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, '"').replace(/&#0?39;|&apos;/gi, "'")
    .replace(/&#8217;|&rsquo;/gi, "’").replace(/&#8216;|&lsquo;/gi, "‘")
    .replace(/&#8220;|&ldquo;/gi, "“").replace(/&#8221;|&rdquo;/gi, "”")
    .replace(/&#8230;|&hellip;/gi, "…").replace(/&#8211;|&ndash;/gi, "–")
    .replace(/&#8212;|&mdash;/gi, "—")
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)))
    .replace(/\s+/g, " ")
    .trim();
}

function lay(manh, ten) {
  const m = manh.match(new RegExp("<" + ten + "(?:\\s[^>]*)?>([\\s\\S]*?)</" + ten + ">", "i"));
  return m ? goHtml(m[1]) : null;
}

/* Ảnh: ba chỗ khác nhau tuỳ toà soạn, thử lần lượt. Chỉ nhận https
   — ảnh http trên trang https bị trình duyệt chặn, và một khung ảnh
   bị chặn trông y hệt một khung ảnh hỏng. */
function layAnh(manh) {
  const thu = [
    /<media:content[^>]*\surl=["']([^"']+)["']/i,
    /<media:thumbnail[^>]*\surl=["']([^"']+)["']/i,
    /<enclosure[^>]*\surl=["']([^"']+)["'][^>]*type=["']image/i,
    /<enclosure[^>]*type=["']image[^>]*\surl=["']([^"']+)["']/i,
    /<img[^>]+src=["']([^"']+)["']/i
  ];
  for (const r of thu) {
    const m = manh.match(r);
    if (m && /^https:\/\//i.test(m[1])) return m[1].replace(/&amp;/g, "&");
  }
  return null;
}

function layLink(manh) {
  const a = manh.match(/<link[^>]*\shref=["']([^"']+)["']/i);   /* Atom */
  if (a) return a[1];
  const b = manh.match(/<link(?:\s[^>]*)?>([\s\S]*?)<\/link>/i); /* RSS  */
  if (b) return goHtml(b[1]);
  return null;
}

function docFeed(xml, ng) {
  const manh = xml.split(/<item(?:\s[^>]*)?>/i).slice(1)
    .map((x) => x.split(/<\/item>/i)[0]);
  const manh2 = manh.length ? manh
    : xml.split(/<entry(?:\s[^>]*)?>/i).slice(1).map((x) => x.split(/<\/entry>/i)[0]);

  const ra = [];
  for (const m of manh2) {
    const tieuDe = lay(m, "title");
    const link = layLink(m);
    if (!tieuDe || !link || !/^https?:\/\//i.test(link)) continue;
    const ngay = lay(m, "pubDate") || lay(m, "published") || lay(m, "updated") || null;
    const t = ngay ? new Date(ngay).getTime() : NaN;
    const tom = (lay(m, "description") || lay(m, "summary") || "").slice(0, 260);
    ra.push({
      tieuDe: tieuDe.slice(0, 180),
      link,
      nguon: ng.ten,
      nguonMa: ng.ma,
      ngay: isFinite(t) ? new Date(t).toISOString() : null,
      tom: tom || null,
      anh: layAnh(m),
      toa: gan(tieuDe + " " + tom)
    });
  }
  return ra;
}

/* ═══════════ LẤY ═══════════ */
const soNguon = [];
async function tai(ng) {
  try {
    const r = await fetch(ng.url, {
      headers: {
        accept: "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
        "user-agent": "Mozilla/5.0 (compatible; blockchainworld/1.0; +https://sunswagz.github.io/blockchainworld/)"
      },
      redirect: "follow",
      signal: AbortSignal.timeout(45000)
    });
    if (!r.ok) throw new Error("HTTP " + r.status);
    const xml = await r.text();
    const bai = docFeed(xml, ng);
    if (!bai.length) throw new Error("không đọc được mục nào");
    soNguon.push({ nhan: ng.ten, ok: true, so: bai.length });
    console.log("  ✓ " + ng.ten.padEnd(20) + bai.length + " bài");
    return bai;
  } catch (e) {
    soNguon.push({ nhan: ng.ten, ok: false, so: 0 });
    console.error("  ✗ " + ng.ten.padEnd(20) + e.message);
    return [];
  }
}

console.log("Thái Bộc Tự · Tin tức — đọc " + NGUON.length + " nguồn:");
const tatCa = (await Promise.all(NGUON.map(tai))).flat();

if (!tatCa.length) {
  console.error("\nKHÔNG nguồn nào cho bài nào. Không ghi gì, giữ nguyên bản cũ.");
  process.exit(1);
}

/* Trùng bài: hai toà soạn đưa lại cùng một link, hoặc một feed lặp.
   Khoá theo link đã bỏ tham số theo dõi, rồi thêm khoá tiêu đề. */
const thay = new Set();
const bai = [];
for (const b of tatCa.sort((a, c) => (a.ngay || "") < (c.ngay || "") ? 1 : -1)) {
  const k1 = b.link.split("?")[0].replace(/\/$/, "").toLowerCase();
  const k2 = b.tieuDe.toLowerCase().replace(/[^a-z0-9]+/g, "").slice(0, 60);
  if (thay.has(k1) || thay.has(k2)) continue;
  thay.add(k1); thay.add(k2);
  bai.push(b);
}

/* Trần mỗi nguồn. Không có nó thì ba trang tin ra bài hàng giờ
   chiếm sạch 30 chỗ, còn hai nguồn GỐC — blog Ethereum Foundation
   và Vitalik — không bao giờ lọt, dù đó đúng là hai nguồn đáng đọc
   nhất khi có bài. Đo thật trước khi thêm: 9/9/9/3/0/0.

   Trần đặt ở 8 chứ không thấp hơn: hạ quá thì mục tin mất tính
   "hôm nay có gì", mà đó vẫn là việc chính của nó. */
const TRAN_NGUON = 8;
const dem = {};
const gioiHan = [];
for (const b of bai) {
  dem[b.nguonMa] = (dem[b.nguonMa] || 0) + 1;
  if (dem[b.nguonMa] > TRAN_NGUON) continue;
  gioiHan.push(b);
  if (gioiHan.length >= 30) break;
}
const theoToa = {};
for (const b of gioiHan) if (b.toa) theoToa[b.toa] = (theoToa[b.toa] || 0) + 1;

const now = new Date();
const data = {
  generatedAt: now.toISOString(),
  date: now.toISOString().slice(0, 10).split("-").reverse().join("/"),
  tomTat: gioiHan.length + " bài · " + soNguon.filter((n) => n.ok).length + "/" + NGUON.length + " nguồn",
  nguon: soNguon,
  tong: {
    soBai: gioiHan.length,
    soCoAnh: gioiHan.filter((b) => b.anh).length,
    soXepToa: gioiHan.filter((b) => b.toa).length,
    theoToa
  },
  bai: gioiHan
};

await mkdir(dirname(RA), { recursive: true });
await writeFile(RA,
  "/* TỰ SINH — đừng sửa tay. Nguồn: scripts/build-tintuc.mjs\n" +
  "   Sinh lúc " + data.generatedAt + " */\n" +
  "window.THAIBOC_TIN = " + JSON.stringify(data) + ";\n", "utf8");

console.log("\n✓ Ghi " + RA.replace(ROOT, ".") +
  "  (" + (JSON.stringify(data).length / 1024).toFixed(1) + " KB)");
console.log("  " + data.tong.soBai + " bài · " + data.tong.soCoAnh + " có ảnh · " +
  data.tong.soXepToa + " xếp được vào toa");
