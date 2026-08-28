/* ═══════════════════════════════════════════════════════
   THANG — gom số rải rác của MỘT cung về một thang.

   Hai thang, cùng một phép:

     · thang CHỮ    cỡ font-size            → --t-0 … --t-N
     · thang CÁCH   padding / margin / gap  → --k-0 … --k-N

   Hai thước trong scripts/tien-hoa.mjs đếm đúng hai chuyện đó, và
   cả hai đều dịch từ skill trên kệ `.claude/skills/`:

     `thang-chu`  ← frontend-design (anthropics/skills)
                    "set a clear type scale"
     `thang-cach` ← design-system (affaan-m/ECC)

   Đo ngày 28/08: 11 trên 12 cung trượt thang chữ (16–34 cỡ), 4 cung
   trượt thang cách. Đo xong mà không có đường sửa thì thước chỉ là
   một lời chê lặp lại mỗi ngày — nên có file này.

       node scripts/thang.mjs <cung>          sửa thật, cả hai thang
       node scripts/thang.mjs <cung> --thu    xem sẽ đổi gì, chưa ghi
       node scripts/thang.mjs <cung> --chu    chỉ thang chữ
       node scripts/thang.mjs <cung> --cach   chỉ thang khoảng cách
       node scripts/thang.mjs --tat-ca --thu  soi cả 12 cung một lượt

   ── VÌ SAO LÀ MÁY, KHÔNG PHẢI SỬA TAY ────────────────────────
   Repo này có 2–4 phiên chạy song song, mỗi phiên một cung, và luật
   là "chỉ sửa thư mục cung mình". Một phiên đi sửa CSS của 11 cung
   khác là đúng thứ luật đó sinh ra để chặn — lúc viết file này có
   16 worktree đang mở, bảy trong số đó giữ chính những cung cần sửa.

   Nên đi lối `npm run halls` đã đi: máy sinh, mỗi cung chạy một lệnh
   cho cung của mình, không ai phải sửa tay trong nhà người khác.

   ── THANG DỰNG TỪ CHÍNH CUNG ĐÓ, KHÔNG ÁP THANG CUNG KHÁC ────
   Cung 54 phòng và cung 5 phòng không cần cùng một thang. Máy gom số
   của CHÍNH cung đang sửa thành cụm, rồi lấy số DÙNG NHIỀU NHẤT
   trong mỗi cụm làm nấc — nhờ vậy số phổ biến đứng yên, chỉ những số
   lẻ dùng một hai lần mới bị kéo về.

   Cửa sổ gom nới dần cho tới khi còn đủ ít nấc, nên nó luôn báo ra
   "số dịch nhiều nhất bao nhiêu phần trăm". Con số đó là thứ người
   duyệt cần nhìn: 4% ở 12px là nửa pixel, mắt không thấy; 20% thì
   phải xem lại.
   ═══════════════════════════════════════════════════════ */

import { readFileSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { join, dirname, basename } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const CO = (t) => process.argv.includes("--" + t);
const THU = CO("thu");
const TAT_CA = CO("tat-ca");
const CUNG = process.argv.slice(2).find((a) => !a.startsWith("--"));
/* Không khai gì thì chạy cả hai. */
const LAM_CHU = CO("chu") || !(CO("chu") || CO("cach"));
const LAM_CACH = CO("cach") || !(CO("chu") || CO("cach"));

/* Ngưỡng khớp với hai thước trong tien-hoa.mjs, nhưng nhắm THẤP hơn:
   gom về sát ngưỡng thì lần sau thêm một cỡ là trượt lại ngay. */
const DICH = {
  chu:  { tran: 10, bien: "--t-", nhan: "chữ" },
  cach: { tran: 16, bien: "--k-", nhan: "cách" }
};

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

/* Bỏ chú thích trước khi ĐẾM. Một câu văn nhắc "padding: 12px cho vừa
   vạch" không phải một giá trị thật — cùng cái bẫy đã làm thước
   `hieu-ung` phạt Đài Quan Trắc vì chính câu chú thích kể chuyện đã
   gỡ hiệu ứng đó. Nhưng SỬA thì sửa trên bản gốc, nên hai bản này
   phải đi riêng. */
const boChuThich = (s) => s.replace(/\/\*[\s\S]*?\*\//g, " ");

/* ── Gom cụm ───────────────────────────────────────────────
   CHẶN THEO MỨC ĐỔI, không chặn theo số nấc. Bản đầu làm ngược: ép
   xuống 16 nấc bằng mọi giá, và khoảng cách phải dịch 10–15% — ở
   padding 40px là 6px, mắt thấy rõ. Cỡ chữ thì may mà tự rơi vào
   3,8–6,6% nên không lộ; khoảng cách thì lộ ngay.

   Nay: nới cửa sổ gom đến chừng nào MỌI số còn dịch dưới NGAN, rồi
   lấy cửa sổ rộng nhất còn đạt. Số nấc là thứ rơi ra, không phải thứ
   đặt trước. Gom xong mà vẫn nhiều nấc hơn ngưỡng của thước thì nói
   thẳng ra, chứ đừng đổi bừa cho vừa một con số. */
const NGAN = 0.06;

/* Thang thật của một hệ thiết kế hiếm khi quá chừng này nấc. */
const THAT_SU_LA_THANG = 12;

function gom(co, w) {
  const cum = [];
  let hien = [];
  for (const v of co) {
    if (!hien.length) { hien = [v]; continue; }
    if (v / hien[0] <= 1 + w) hien.push(v);
    else { cum.push(hien); hien = [v]; }
  }
  if (hien.length) cum.push(hien);
  return cum;
}

function dungThang(dem) {
  const co = [...dem.keys()].sort((a, b) => a - b);
  let tot = null;
  for (let w = 0; w <= 0.6; w += 0.005) {
    const nac = gom(co, w).map((c) => {
      let dai = c[0], nhieu = -1;
      for (const v of c) {
        const n = dem.get(v);
        if (n > nhieu) { nhieu = n; dai = v; }
      }
      if (c.filter((v) => dem.get(v) === nhieu).length > 1) dai = c[Math.floor(c.length / 2)];
      return { cu: c, moi: Math.round(dai * 10) / 10 };
    });
    let dich = 0;
    for (const n of nac) for (const v of n.cu) dich = Math.max(dich, Math.abs(n.moi - v) / v);
    if (dich > NGAN) break;
    tot = { nac, dichToiDa: dich };
  }
  return tot;
}

/* ── Hai cách nhặt số ──────────────────────────────────── */
const RE_CHU = /font-size:\s*([\d.]+)px/g;
/* `[^;}:]*` dừng trước dấu hai chấm, nên bắt được `padding-left`,
   `row-gap`, `margin-inline-start` mà không nuốt sang khai báo sau. */
const RE_CACH = /(?:padding|margin|gap)[^;}:]*:\s*([^;}]+)/g;

function nhat(van, loai) {
  const dem = new Map();
  for (const v of van.values()) {
    const sach = boChuThich(v);
    if (loai === "chu") {
      for (const m of sach.matchAll(RE_CHU)) {
        const px = Number(m[1]);
        if (px > 0) dem.set(px, (dem.get(px) || 0) + 1);
      }
    } else {
      for (const m of sach.matchAll(RE_CACH))
        /* KHÔNG nhận số đứng sau dấu trừ hay dấu chấm: `-4px` mà thay
           thành `-var(--k-1)` là CSS hỏng, còn `1.5px` thì `5px` chỉ
           là một mẩu của nó. */
        for (const g of m[1].matchAll(/(^|[^-\w.])(\d+)px\b/g)) {
          const px = Number(g[2]);
          if (px > 0) dem.set(px, (dem.get(px) || 0) + 1);
        }
    }
  }
  return dem;
}

function doCung(cung, loai) {
  const fs_ = fileCss(cung);
  if (!fs_.length) return { bo: "không có assets/css/*.css" };
  const van = new Map(fs_.map((f) => [f, readFileSync(f, "utf8")]));
  const { tran, bien } = DICH[loai];

  if ([...van.values()].some((v) => new RegExp(bien + "0\\s*:").test(v)))
    return { bo: `đã có thang ${DICH[loai].nhan} (${bien}0)` };

  const dem = nhat(van, loai);
  if (dem.size === 0) return { bo: `không số px nào cho thang ${DICH[loai].nhan}` };
  if (dem.size <= tran) return { bo: `${dem.size} số, đã dưới ngưỡng ${tran}` };

  const t = dungThang(dem);
  if (!t) return { bo: `${dem.size} số, không gom được nấc nào dưới mức đổi ${(NGAN*100).toFixed(0)}%` };
  /* Gom mà không bớt được nấc nào thì đây chỉ là phép ĐỔI TÊN. Hai
     thước trong tien-hoa.mjs nay đếm cả nấc `--t-*`/`--k-*`, nên đổi
     tên không làm điểm lên — nó chỉ đẻ ra một diff to. Dừng, và nói
     rõ là dừng vì lý do gì. */
  if (t.nac.length >= dem.size)
    return { bo: `${dem.size} số, gom trong mức đổi ${(NGAN * 100).toFixed(0)}% không bớt được nấc nào — ` +
      `đổi tên suông không giúp gì, cần mắt người` };
  return { van, dem, loai, ...t };
}

function viet(cung, kq) {
  const { van, dem, nac, dichToiDa, loai } = kq;
  const { bien, nhan } = DICH[loai];

  const ten = new Map();
  nac.forEach((n, i) => { for (const v of n.cu) ten.set(v, `${bien}${i}`); });

  const khai = nac.map((n, i) => `${bien}${i}:${n.moi}px;`);
  const dong = [];
  for (let i = 0; i < khai.length; i += 4) dong.push("  " + khai.slice(i, i + 4).join("  "));

  const khoi =
`
/* ── THANG ${nhan.toUpperCase()} ─────────────────────────────────────
   Sinh bởi scripts/thang.mjs từ chính số của cung này: ${dem.size} giá trị
   px rời rạc gom thành ${nac.length} nấc, số dịch nhiều nhất ${(dichToiDa * 100).toFixed(1)}%.
   Nấc lấy số DÙNG NHIỀU NHẤT của mỗi cụm, nên số phổ biến đứng yên
   và chỉ số lẻ bị kéo về.

   Thêm giá trị mới thì thêm NẤC, đừng viết px thẳng vào rule. */
:root{
${dong.join("\n")}
}
`;

  /* Chèn NGAY SAU khối :root đầu tiên — cạnh các biến khác, nhưng
     KHÔNG chen lên trước chúng.

     Bản đầu chèn trước, và nó làm hỏng phép đo tương phản: phép ấy
     khi đó chỉ đọc khối :root ĐẦU TIÊN, nên khối thang (toàn px,
     không màu nào) chen lên trước là nó báo "không ghép được cặp
     nào". Thử trên do-sat-vien ra 10/11 → 10/10: mẫu số tụt một mà
     điểm vẫn đẹp, tức mất một phép kiểm mà không dòng nào kêu.

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
    let ra;
    if (loai === "chu") {
      ra = noi.replace(/font-size:\s*([\d.]+)px/g, (all, px) => {
        const t = ten.get(Number(px));
        if (!t) return all;
        doi++; return `font-size:var(${t})`;
      });
    } else {
      ra = noi.replace(RE_CACH, (all, gt) => {
        const moi = gt.replace(/(^|[^-\w.])(\d+)px\b/g, (mm, tr, so) => {
          const t = ten.get(Number(so));
          if (!t) return mm;
          doi++; return `${tr}var(${t})`;
        });
        return all.slice(0, all.length - gt.length) + moi;
      });
    }
    van.set(f, ra);
  }

  if (!THU) for (const [f, noi] of van) writeFileSync(f, noi);
  return { doi, nac: nac.length };
}

/* ═══════════════ CHẠY ═══════════════ */
const ds = TAT_CA ? moiCung() : (CUNG ? [CUNG] : []);
if (!ds.length) {
  console.error("Dùng: node scripts/thang.mjs <cung> [--thu] [--chu|--cach]   ·   --tat-ca --thu");
  process.exit(1);
}
if (TAT_CA && !THU) {
  console.error("--tat-ca chỉ chạy cùng --thu. Sửa thật thì sửa TỪNG cung, ở worktree của cung đó:\n" +
    "16 worktree có thể đang mở, và ghi đè CSS của cung người khác đang sửa dở là mất việc của họ.");
  process.exit(1);
}

let canSua = 0;
for (const c of ds) {
  for (const loai of ["chu", "cach"]) {
    if (loai === "chu" && !LAM_CHU) continue;
    if (loai === "cach" && !LAM_CACH) continue;
    /* Đọc lại từ đĩa mỗi lượt: lượt `chu` đã ghi thì lượt `cach` phải
       thấy bản mới, không thì nó ghi đè mất thang vừa dựng. */
    const kq = doCung(c, loai);
    const nh = DICH[loai].nhan;
    if (kq.bo) { console.log(`  ·  ${c.padEnd(17)} ${nh.padEnd(5)} ${kq.bo}`); continue; }
    canSua++;
    const r = viet(c, kq);
    console.log(`  ${THU ? "?" : "✓"}  ${c.padEnd(17)} ${nh.padEnd(5)} ${kq.dem.size} số → ${r.nac} nấc · ` +
      `${r.doi} khai báo · dịch nhiều nhất ${(kq.dichToiDa * 100).toFixed(1)}%`);
    /* Nói thẳng khi máy chỉ DỌN chứ chưa THIẾT KẾ. Gom trong mức đổi
       an toàn có lúc chỉ bớt được vài nấc, và một thang 23 nấc thì
       vẫn chưa phải một thang — nó chỉ là 23 con số đã có tên. Không
       in dòng này ra thì người chạy lệnh dễ tưởng xong việc, và cái
       máy hoá thành máy làm đẹp phiếu đo. */
    if (r.nac > THAT_SU_LA_THANG)
      console.log(`        ⚠ ${r.nac} nấc vẫn nhiều hơn một thang thật (≤${THAT_SU_LA_THANG}). ` +
        `Máy chỉ dọn được tới mức đổi ${(NGAN * 100).toFixed(0)}%; gom tiếp là đổi bố cục, cần mắt người.`);
    if (THU) for (const [i, n] of kq.nac.entries())
      console.log(`        ${DICH[loai].bien}${String(i).padEnd(2)} ${String(n.moi + "px").padEnd(8)} ← ${n.cu.join(" ")}`);
    /* Ở chế độ --thu không ghi gì, nên lượt sau vẫn đọc bản cũ — đúng
       ý: --thu phải cho thấy tình trạng HIỆN TẠI của cả hai thang. */
  }
}
if (THU) console.log(`\n${canSua} lượt sẽ đổi. Bỏ --thu để ghi thật, và chỉ chạy cho cung của phiên mình.`);
else if (canSua) console.log(`\nChạy \`node scripts/tien-hoa.mjs do <cung>\` để soát lại, rồi \`npm run nang\`.`);
