/* ═══════════════════════════════════════════════════════
   THANG CHỮ — gom cỡ chữ rải rác của một cung về một thang.

   Thước `thang-chu` trong scripts/tien-hoa.mjs (dịch từ skill
   `frontend-design`, kho anthropics/skills: "set a clear type scale")
   đo được 11 trên 12 cung đang trượt, cỡ rời rạc từ 16 tới 34. Đo
   xong mà không có đường sửa thì thước ấy chỉ là một lời chê lặp lại
   mỗi ngày — nên có file này.

       node scripts/thang-chu.mjs <cung>          sửa thật
       node scripts/thang-chu.mjs <cung> --thu    xem sẽ đổi gì, chưa ghi
       node scripts/thang-chu.mjs --tat-ca --thu  soi cả 12 cung một lượt

   ── VÌ SAO LÀ MÁY, KHÔNG PHẢI SỬA TAY ────────────────────────
   Repo này có 2–4 phiên chạy song song, mỗi phiên một cung, và luật
   là "chỉ sửa thư mục cung mình". Một phiên đi sửa CSS của 11 cung
   khác là đúng thứ luật đó sinh ra để chặn — lúc viết file này có
   16 worktree đang mở, bảy trong số đó giữ chính những cung cần sửa.

   Nên đi lối `npm run halls` đã đi: máy sinh, mỗi cung chạy một lệnh
   cho cung của mình, không ai phải sửa tay trong nhà người khác.

   ── THANG DỰNG TỪ CHÍNH CUNG ĐÓ, KHÔNG ÁP THANG CỦA HỘ BỘ ────
   Cung 54 phòng và cung 5 phòng không cần cùng một thang. Máy này
   gom cỡ của CHÍNH cung đang sửa thành cụm, rồi lấy cỡ DÙNG NHIỀU
   NHẤT trong mỗi cụm làm nấc — nhờ vậy cỡ phổ biến đứng yên, chỉ
   những cỡ lẻ dùng một hai lần mới bị kéo về.

   Cửa sổ gom nới dần từ 4% cho tới khi còn ≤12 nấc, nên nó luôn báo
   ra "cỡ dịch nhiều nhất là bao nhiêu phần trăm". Con số đó là thứ
   người duyệt cần nhìn: 4% ở 12px là nửa pixel, mắt không thấy;
   20% thì phải xem lại.
   ═══════════════════════════════════════════════════════ */

import { readFileSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { join, dirname, basename } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const THU = process.argv.includes("--thu");
const TAT_CA = process.argv.includes("--tat-ca");
const CUNG = process.argv.slice(2).find((a) => !a.startsWith("--"));

const TRAN_NAC = 12;   /* cùng ngưỡng với thước trong tien-hoa.mjs */

/* Cung = thư mục có index.html NGAY tại gốc nó. Cùng phép nhận diện
   với kiem-quy-trinh.mjs — chép một phép nhận diện khác đi là sớm
   muộn hai bên nói hai chuyện. */
function moiCung() {
  return readdirSync(ROOT, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith(".") && d.name !== "node_modules")
    .map((d) => d.name)
    .filter((n) => existsSync(join(ROOT, n, "index.html")))
    .sort();
}

function fileCss(cung) {
  const thu = join(ROOT, cung, "assets", "css");
  if (!existsSync(thu)) return [];
  return readdirSync(thu).filter((f) => f.endsWith(".css")).map((f) => join(thu, f));
}

/* ── Gom cụm ─────────────────────────────────────────────
   Trả { nac: [{ cu: [...], moi }], cuaSo, dichToiDa } hoặc null nếu
   không cách nào xuống được ≤ TRAN_NAC (chưa gặp cung nào như vậy). */
function dungThang(dem) {
  const co = [...dem.keys()].sort((a, b) => a - b);
  for (let w = 0.04; w <= 0.6; w += 0.01) {
    const cum = [];
    let hien = [];
    for (const v of co) {
      if (!hien.length) { hien = [v]; continue; }
      if (v / hien[0] <= 1 + w) hien.push(v);
      else { cum.push(hien); hien = [v]; }
    }
    if (hien.length) cum.push(hien);
    if (cum.length > TRAN_NAC) continue;

    const nac = cum.map((c) => {
      /* Đại diện = cỡ dùng nhiều nhất trong cụm. Hoà thì lấy cỡ ở
         giữa, để không kéo cả cụm về một đầu. */
      let tot = c[0], nhieu = -1;
      for (const v of c) {
        const n = dem.get(v);
        if (n > nhieu) { nhieu = n; tot = v; }
      }
      if (c.filter((v) => dem.get(v) === nhieu).length > 1) tot = c[Math.floor(c.length / 2)];
      return { cu: c, moi: Math.round(tot * 10) / 10 };
    });
    let dich = 0;
    for (const n of nac) for (const v of n.cu) dich = Math.max(dich, Math.abs(n.moi - v) / v);
    return { nac, cuaSo: w, dichToiDa: dich };
  }
  return null;
}

function doCung(cung) {
  const fs_ = fileCss(cung);
  if (!fs_.length) return { cung, bo: "không có assets/css/*.css" };

  const van = new Map(fs_.map((f) => [f, readFileSync(f, "utf8")]));
  const dem = new Map();
  for (const v of van.values())
    for (const m of v.matchAll(/font-size:\s*([\d.]+)px/g)) {
      const px = Number(m[1]);
      dem.set(px, (dem.get(px) || 0) + 1);
    }

  if ([...van.values()].some((v) => /--t-0\s*:/.test(v)))
    return { cung, bo: "đã có thang (--t-0) — không đụng lại" };
  if (dem.size === 0) return { cung, bo: "không cỡ px nào — có thể đã dùng rem/em" };
  if (dem.size <= TRAN_NAC) return { cung, bo: `${dem.size} cỡ, đã dưới ngưỡng ${TRAN_NAC}` };

  const t = dungThang(dem);
  if (!t) return { cung, bo: `${dem.size} cỡ, gom mãi không xuống được ${TRAN_NAC} nấc` };
  return { cung, van, dem, ...t };
}

function viet(kq) {
  const { cung, van, dem, nac, dichToiDa } = kq;

  /* Nấc xếp từ nhỏ lên lớn: --t-0 là nhỏ nhất. */
  const ten = new Map();
  nac.forEach((n, i) => { for (const v of n.cu) ten.set(v, `--t-${i}`); });

  const khai = nac.map((n, i) => `--t-${i}:${n.moi}px;`);
  const dong = [];
  for (let i = 0; i < khai.length; i += 4) dong.push("  " + khai.slice(i, i + 4).join("  "));

  const khoi =
`
/* ── THANG CHỮ ─────────────────────────────────────────
   Sinh bởi scripts/thang-chu.mjs từ chính cỡ chữ của cung này:
   ${dem.size} cỡ px rời rạc gom thành ${nac.length} nấc, cỡ dịch nhiều nhất
   ${(dichToiDa * 100).toFixed(1)}%. Nấc lấy cỡ DÙNG NHIỀU NHẤT của mỗi cụm, nên cỡ
   phổ biến đứng yên và chỉ cỡ lẻ bị kéo về.

   Thêm cỡ mới thì thêm NẤC, đừng viết px thẳng vào rule — thước
   \`thang-chu\` trong scripts/tien-hoa.mjs đếm đúng chuyện đó. */
:root{
${dong.join("\n")}
}
`;

  /* Chèn NGAY SAU khối :root đầu tiên — cạnh các biến khác, nhưng
     KHÔNG chen lên trước chúng.

     Bản đầu chèn trước, và nó làm hỏng phép đo tương phản trong
     scripts/tien-hoa.mjs: phép ấy khi đó chỉ đọc khối :root ĐẦU TIÊN,
     nên khối thang chữ (toàn px, không màu nào) chen lên trước là nó
     báo "không ghép được cặp nào". Thử trên do-sat-vien ra 10/11 →
     10/10: mẫu số tụt một mà điểm vẫn đẹp, tức là mất một phép kiểm
     mà không dòng nào kêu.

     `doMau` nay đọc mọi khối :root nên đã hết hỏng ở đầu kia. Vẫn
     chèn sau, vì bộ đo sau này có thể lại giả định khối đầu là khối
     màu, và một công cụ sinh mã thì không nên đi thử vận may đó. */
  const chinh = [...van.keys()].find((f) => basename(f) === "app.css") || [...van.keys()][0];
  let v = van.get(chinh);
  const m = /:root\s*\{[\s\S]*?\}/.exec(v);
  const sau = m ? m.index + m[0].length : -1;
  v = sau >= 0 ? v.slice(0, sau) + "\n" + khoi.trimStart() + v.slice(sau) : khoi + v;
  van.set(chinh, v);

  let doi = 0;
  for (const [f, noi] of van) {
    van.set(f, noi.replace(/font-size:\s*([\d.]+)px/g, (all, px) => {
      const t = ten.get(Number(px));
      if (!t) return all;
      doi++; return `font-size:var(${t})`;
    }));
  }

  if (!THU) for (const [f, noi] of van) writeFileSync(f, noi);
  return { doi, nac: nac.length };
}

/* ═══════════════ CHẠY ═══════════════ */
const ds = TAT_CA ? moiCung() : (CUNG ? [CUNG] : []);
if (!ds.length) {
  console.error("Dùng: node scripts/thang-chu.mjs <cung> [--thu]   ·   --tat-ca --thu");
  process.exit(1);
}
if (TAT_CA && !THU) {
  console.error("--tat-ca chỉ chạy cùng --thu. Sửa thật thì sửa TỪNG cung, ở worktree của cung đó:\n" +
    "16 worktree có thể đang mở, và ghi đè CSS của cung người khác đang sửa dở là mất việc của họ.");
  process.exit(1);
}

let canSua = 0;
for (const c of ds) {
  const kq = doCung(c);
  if (kq.bo) { console.log(`  ·  ${c.padEnd(18)} ${kq.bo}`); continue; }
  canSua++;
  const r = viet(kq);
  console.log(`  ${THU ? "?" : "✓"}  ${c.padEnd(18)} ${kq.dem.size} cỡ → ${r.nac} nấc · ` +
    `${r.doi} khai báo · dịch nhiều nhất ${(kq.dichToiDa * 100).toFixed(1)}%`);
  if (THU) {
    for (const [i, n] of kq.nac.entries())
      console.log(`        --t-${String(i).padEnd(2)} ${String(n.moi + "px").padEnd(8)} ← ${n.cu.join(" ")}`);
  }
}
if (THU) console.log(`\n${canSua} cung sẽ đổi. Bỏ --thu để ghi thật, và chỉ chạy cho cung của phiên mình.`);
else if (canSua) console.log(`\nChạy \`node scripts/tien-hoa.mjs do <cung>\` để soát lại, rồi \`npm run nang\`.`);
