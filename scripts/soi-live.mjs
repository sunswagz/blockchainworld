/* ═══════════════════════════════════════════════════════
   SOI LIVE — mọi tài nguyên trên bản ĐANG CHẠY có tải được không.

   Chạy: npm run live          (soi cả 13 trang)
         npm run live thai-boc-tu   (một cung)

   ── VÌ SAO CẦN, KHI ĐÃ CÓ CỔNG CHẶN ──────────────────────────
   Cổng chặn và phiếu đo chỉ soi FILE TRONG REPO. Chúng không biết
   hai chuyện, và cả hai chỉ lộ ra sau khi deploy:

     1. `build-dist.mjs` có chép file đó lên Pages không. Thêm một
        thư mục assets mới mà quên dạy build-dist là trang chạy hoàn
        hảo ở máy và thiếu tài nguyên trên site.
     2. Đường dẫn có đúng khi phục vụ dưới /blockchainworld/<cung>/
        không. Một `/assets/…` mở đầu bằng gạch chéo trỏ về gốc
        DOMAIN, không phải gốc repo — ở máy `npm start` thì đúng, ở
        Pages thì 404.

   Đây là phép DÒ SAU KHI GIAO, không phải cổng chặn: nó không ngăn
   được bản hỏng đi lên, chỉ nói cho biết ngay trong lượt ấy. Muốn
   ngăn thì phải dựng thật một bản Pages trước khi đẩy, mà đó là một
   cỗ máy khác hẳn.

   Đo ngày 29/08: 177 tài nguyên trên 13 trang, không cái nào gãy.
   Ghi lại con số đó để lần sau ai chạy còn biết "0 gãy" là bình
   thường chứ không phải phép soi hỏng.
   ═══════════════════════════════════════════════════════ */

const GOC = "https://sunswagz.github.io/blockchainworld/";

/* "" là Cổng Thành ở gốc. Danh sách cứng chứ không đọc đĩa: phép
   này soi bản ĐANG CHẠY, và cung mới thêm ở nhánh chưa gộp thì trên
   site chưa có — đọc đĩa là tự chuốc một dòng đỏ vô nghĩa. */
const CUNG = ["", "cong-bo", "dai-quan-trac", "do-sat-vien", "ho-bo", "hoang-thanh",
  "kham-thien-giam", "kinh-thanh", "tang-thu-cac", "tao-bien-xu", "thai-boc-tu",
  "thi-bac-ty", "tu-cam-thanh"];

const RE = [
  [/<script[^>]+src="([^"]+)"/g, "script"],
  [/<link[^>]+href="([^"]+)"[^>]*>/g, "link"],
  [/<img[^>]+src="([^"]+)"/g, "img"],
];

const loc = process.argv[2];
const ds = loc ? CUNG.filter((c) => c === loc) : CUNG;
if (loc && !ds.length) {
  console.error(`"${loc}" không có trên site. Có: ${CUNG.filter(Boolean).join(", ")}`);
  process.exit(2);
}

let tongGay = 0, tongTep = 0;
for (const c of ds) {
  const base = GOC + (c ? c + "/" : "");
  let html;
  try {
    const r = await fetch(base, { cache: "no-store" });
    if (!r.ok) { console.log(`  ✗ ${(c || "(cổng thành)").padEnd(17)} trang chính ${r.status}`); tongGay++; continue; }
    html = await r.text();
  } catch (e) { console.log(`  ✗ ${(c || "(cổng thành)").padEnd(17)} ${e.message}`); tongGay++; continue; }

  const duong = new Set();
  for (const [re, loai] of RE)
    for (const m of html.matchAll(re)) {
      const u = m[1];
      if (/^(data:|https?:|#|mailto:)/.test(u)) continue;
      /* <link> còn dùng cho preconnect, alternate, canonical… — những
         cái đó không tải tệp nào của ta. Chỉ soi bốn rel thật sự kéo
         tài nguyên về. */
      if (loai === "link" && !/rel="(stylesheet|manifest|icon|apple-touch-icon)"/.test(m[0])) continue;
      duong.add(u);
    }

  const gay = [];
  for (const u of duong) {
    /* GET chứ không HEAD: GitHub Pages trả 405 cho HEAD ở vài đường,
       và một phép soi báo 405 cho tệp lành là phép soi không ai tin. */
    try {
      const r = await fetch(new URL(u, base).href, { cache: "no-store" });
      if (!r.ok) gay.push(`${u} → ${r.status}`);
    } catch (e) { gay.push(`${u} → ${e.message.slice(0, 30)}`); }
  }
  tongGay += gay.length;
  tongTep += duong.size;
  console.log(`  ${gay.length ? "✗" : "✓"} ${(c || "(cổng thành)").padEnd(17)}${String(duong.size).padStart(3)} tài nguyên` +
    (gay.length ? `  · GÃY: ${gay.join(" | ")}` : ""));
}

console.log(tongGay
  ? `\n✗ ${tongGay} tài nguyên gãy trên ${tongTep} đã soi`
  : `\n✓ ${tongTep} tài nguyên, không cái nào gãy`);
process.exit(tongGay ? 1 : 0);
