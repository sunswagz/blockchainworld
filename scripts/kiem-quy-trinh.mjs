/* ═══════════════════════════════════════════════════════
   Kiểm CLAUDE.md có còn khớp với repo thật không.

   Chạy: npm run kiem

   CLAUDE.md nói nhiều thứ "phải khớp với nhau" — bảng cổng, danh
   sách file bot tự sinh, danh sách cung trong build-dist và trong
   paths của hai workflow. Không có gì bắt chúng khớp cả; chúng lệch
   dần, và LỆCH THÌ KHÔNG AI BÁO.

   Mỗi lỗi ở đây đều từng xảy ra thật, hoặc suýt xảy ra:
     · thiếu cung trong paths → push xong không workflow nào chạy,
       site vẫn bản cũ, không lỗi nào báo
     · thiếu cung trong bảng cổng → phiên sau đoán bừa, tranh cổng
     · danh sách file bot tự sinh thiếu → phiên khác sửa tay đúng
       file bot ghi, conflict lúc gộp
     · cung mới chưa được cung cũ trỏ sang → dựng xong mà không có
       đường vào

   Mã thoát khác 0 nếu có lỗi, để cắm vào CI sau này nếu muốn.
   ═══════════════════════════════════════════════════════ */

import { readFile, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { NGUON, nguongCua, tuoi } from "./tuoi-du-lieu.mjs";
import { docMangTruoc, laMangTruoc, docShell } from "./mang-truoc.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const doc = (p) => readFile(join(ROOT, p), "utf8");

const loi = [];
const canhBao = [];
const bao = (m) => loi.push(m);
const nhac = (m) => canhBao.push(m);

/* ── cung thật trên đĩa ───────────────────────────────
   Một thư mục là cung khi và chỉ khi nó có index.html riêng. */
const BO_QUA = new Set(["assets", "scripts", "dist", "node_modules", ".git", ".github", ".claude"]);
const cung = [];
for (const ten of await readdir(ROOT)) {
  if (BO_QUA.has(ten) || ten.startsWith(".")) continue;
  if (existsSync(join(ROOT, ten, "index.html"))) cung.push(ten);
}
cung.sort();

const CLAUDE = await doc("CLAUDE.md");

/* ── 0. bản CLAUDE.md tại chỗ có cũ hơn origin/main không ──
   Worktree nhánh từ origin/main LÚC TẠO rồi đứng yên. Phiên mở từ
   worktree cũ đang đọc luật của tuần trước mà không biết.

   Bảy phép kiểm dưới đây so tài liệu CỤC BỘ với repo CỤC BỘ, nên
   worktree cũ có cả hai đều cũ mà khớp nhau sẽ in ✓ — xanh trong khi
   phiên đó làm theo luật đã bị thay. Đúng kiểu "bước xanh vĩnh viễn"
   mà CLAUDE.md cảnh báo ở mục Hoàng Thành. Đã xảy ra thật: một
   worktree tạo lúc repo còn năm cung vẫn báo ✓ sau khi main lên sáu.

   Đếm commit chạm CLAUDE.md có ở origin/main mà KHÔNG có ở đây.
   Không so nội dung hai bản: nhánh tại chỗ có thể đang sửa chính
   CLAUDE.md, khác nội dung mà là mới hơn chứ không cũ — báo nó lỗi
   thời thì chính người đang vá lại bị chặn.

   Đọc ref có sẵn trên đĩa, KHÔNG tự ra mạng: `npm run kiem` phải chạy
   được khi mất mạng. Muốn số liệu tươi thì `git fetch -q` trước, đúng
   thứ tự trong mục "Trước khi bắt đầu".

   Đây là lớp thứ hai, không phải lớp duy nhất: hook pre-commit nhắc
   phiên đang chạy dở mà không nhớ chạy lệnh này. Hook chỉ nhắc và luôn
   thoát 0; chỗ này thoát 1 để chặn được và cắm CI được. */
if (!process.argv.includes("--offline")) {
  const git = (...a) =>
    execFileSync("git", a, { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
  try {
    const so = Number(git("rev-list", "--count", "HEAD..origin/main", "--", "CLAUDE.md"));
    if (so > 0) {
      bao(
        `CLAUDE.md ở đây CŨ HƠN origin/main ${so} commit — bạn đang theo luật lỗi thời.\n` +
        "        Xem đã đổi gì: git diff HEAD origin/main -- CLAUDE.md\n" +
        "        Bắt kịp      : git merge --ff-only origin/main\n" +
        "        Bỏ qua       : npm run kiem -- --offline"
      );
    }
  } catch {
    nhac("Không so được CLAUDE.md với origin/main (chưa `git fetch`, hoặc không có remote).");
  }
}

/* ── 1. danh sách cung ở đầu CLAUDE.md ────────────── */
for (const c of cung) {
  if (!new RegExp("(^|\\s)" + c + "/", "m").test(CLAUDE)) {
    bao(`CLAUDE.md chưa nhắc cung "${c}/" ở danh sách đầu file`);
  }
}

/* ── 2. bảng cổng ─────────────────────────────────── */
const cong = new Map();
for (const m of CLAUDE.matchAll(/^ {4}(\d{4}) {2}(\S+)/gm)) {
  const [, so, ten] = m;
  if (cong.has(so)) bao(`Bảng cổng: ${so} bị cấp cho cả "${cong.get(so)}" và "${ten}"`);
  cong.set(so, ten);
}
const tenCong = new Set([...cong.values()]);
for (const c of cung) {
  if (!tenCong.has(c)) bao(`Bảng cổng thiếu cung "${c}" — phiên sau sẽ đoán bừa và tranh cổng`);
}
for (const [so] of cong) {
  const n = Number(so);
  if (n < 5173 || n > 5199) nhac(`Cổng ${so} nằm ngoài dải 5173–5199 dành cho repo này`);
}

/* ── 3. danh sách file bot tự sinh khớp `git add` ─── */
/* CLAUDE.md liệt kê đường dẫn bot ghi đè. Nếu workflow add thêm
   đường dẫn mà tài liệu không ghi, phiên khác sẽ sửa tay đúng chỗ
   đó và chắc chắn conflict lúc gộp. */
/* Từ 20/08 workflow KHÔNG còn chép tay khối `git add` nữa — nó gọi
   `nha-may.mjs duong-ra`, sinh từ `ra` của node. Nên phép này thôi
   đọc YAML: nó hỏi thẳng sổ đăng ký.

   Ba nơi phải khớp đã còn hai, và nơi còn lại đối chiếu với NGUỒN
   chứ không với một bản chép. Cái vẫn phải canh là CLAUDE.md: tài
   liệu mà thiếu một đường thì phiên khác sẽ sửa tay đúng file bot
   ghi đè, và mất việc lúc gộp. */
{
  const wf = ".github/workflows/refresh-data.yml";
  if (!existsSync(join(ROOT, wf))) bao(`Thiếu workflow ${wf}`);
  else {
    const t = await doc(wf);
    if (!t.includes("nha-may.mjs duong-ra"))
      bao(`refresh-data.yml không còn gọi "nha-may.mjs duong-ra" — khối git add đã bị chép tay lại?`);
  }
  let NM = null;
  try { NM = await import("./nha-may.mjs"); } catch { /* phép 8c báo rồi */ }
  if (NM && typeof NM.duongRa === "function") {
    /* Chỉ soi đường của node, không soi ba file sổ — chúng là của
       chính nhà máy và CLAUDE.md đã mô tả riêng ở mục sổ đăng ký. */
    const soSo = new Set([NM.DUONG_TRANG_THAI, NM.DUONG_CHIEU, NM.DUONG_SO]);
    for (const d of NM.duongRa()) {
      if (soSo.has(d)) continue;
      if (!CLAUDE.includes(d))
        bao(`sổ đăng ký khai bot ghi "${d}" nhưng CLAUDE.md không liệt kê — mục "File do workflow tự sinh" bị thiếu`);
    }
  }
}

/* ── 4. build-dist HALLS ──────────────────────────── */
const bd = await doc("scripts/build-dist.mjs");
const mHalls = bd.match(/const HALLS = \[([^\]]*)\]/);
if (!mHalls) bao("build-dist.mjs: không tìm thấy mảng HALLS");
else {
  const halls = [...mHalls[1].matchAll(/"([^"]+)"/g)].map((m) => m[1]);
  for (const c of cung) if (!halls.includes(c)) bao(`build-dist.mjs HALLS thiếu "${c}" — cung này sẽ không vào dist/`);
  for (const h of halls) if (!cung.includes(h)) bao(`build-dist.mjs HALLS có "${h}" nhưng trên đĩa không có thư mục đó`);
}

/* ── 5. sửa một cung thì Pages có dựng lại không ────
   Trước đây phép này bắt mọi cung phải có mặt trong `paths:` của hai
   workflow deploy. Nhưng danh sách cho phép chính LÀ cái bẫy: thêm
   cung mà quên thêm dòng thì push xong không workflow nào chạy.

   deploy-pages.yml giờ dùng `paths-ignore` — mặc định mọi thứ đều
   deploy, chỉ trừ file rõ ràng không phải của trang. Nên phép kiểm
   cũng đổi: không soi cơ chế nữa, soi TÍNH CHẤT — đẩy một file trong
   `<cung>/` thì Pages có dựng lại không.

   Cách đó đúng với cả hai lược đồ, nên đổi cách cấu hình sau này
   không phải viết lại phép kiểm. */
{
  const wf = ".github/workflows/deploy-pages.yml";
  if (!existsSync(join(ROOT, wf))) bao(`Thiếu ${wf}`);
  else {
    const t = await doc(wf);
    const khoi = (ten) => {
      const m = t.match(new RegExp("^\\s*" + ten + ":\\s*\\n((?:\\s*-\\s*\"[^\"]*\"\\s*\\n)+)", "m"));
      return m ? [...m[1].matchAll(/"([^"]+)"/g)].map((x) => x[1]) : null;
    };
    const chophep = khoi("paths");
    const loaitru = khoi("paths-ignore") || [];

    for (const c of cung) {
      const mau = `${c}/index.html`;
      if (chophep && !chophep.some((p) => p === mau || p === `${c}/**`)) {
        bao(`deploy-pages.yml: danh sách "paths" bỏ sót "${c}/" — sửa cung đó xong sẽ KHÔNG deploy, và không có lỗi nào báo`);
      }
      const bi = loaitru.find((p) => p === `${c}/**` || p === mau || p === `${c}/`);
      if (bi) {
        bao(`deploy-pages.yml: "paths-ignore" có "${bi}" — cung "${c}" bị loại khỏi deploy`);
      }
    }
    if (!chophep && !loaitru.length) {
      nhac("deploy-pages.yml: không có paths lẫn paths-ignore — mọi push đều dựng lại Pages");
    }
  }
}

/* ── 5b. IPFS không được pin theo mỗi push ──────────
   Gói Pinata free là 1 GB. Bản site đo ngày 14/08 đã 21,8 MB / 462
   file, và còn tăng theo số cung. Pin mỗi push là hết hạn mức —
   đã hỏng liên tục 20 lượt liền từ 13/08 vì đúng lý do đó.

   IPFS ở đây là bản lưu bất biến, không phải đường chạy chính, nên
   pin theo TAG phát hành hoặc bấm tay. Phép kiểm này giữ cho không
   ai vô tình cắm lại `on: push` với branches. */
{
  const wf = ".github/workflows/deploy-ipfs.yml";
  if (!existsSync(join(ROOT, wf))) bao(`Thiếu ${wf}`);
  else {
    const t = await doc(wf);
    const on = t.split(/\npermissions:/)[0];
    if (/\n\s*push:\s*\n\s*branches:/.test(on)) {
      bao(`${wf.split("/").pop()}: đang pin theo mỗi push vào branch — gói Pinata free không chịu nổi.\n` +
        "        Chỉ nên pin theo tag (`tags: [\"v*\"]`) hoặc bấm tay workflow_dispatch.");
    }
  }
}

/* ── 6. sw.js gốc để yên phạm vi từng cung ────────── */
const sw = await doc("sw.js");
for (const c of cung) {
  if (!sw.includes(`/${c}/`)) {
    bao(`sw.js (Cổng Thành) thiếu dòng bỏ qua "/${c}/" — service worker cổng sẽ tranh phục vụ file của cung đó`);
  }
}

/* ── 7. mỗi cung trỏ sang mọi cung khác ───────────── */
for (const c of cung) {
  const f = join(c, "assets", "js", "halls.js");
  if (!existsSync(join(ROOT, f))) { nhac(`${c}: chưa có assets/js/halls.js (cung mới chưa dựng xong?)`); continue; }
  const t = await doc(f);
  for (const k of cung) {
    if (k === c) continue;
    if (!t.includes(`../${k}/`)) bao(`${c}/assets/js/halls.js chưa có lối sang "${k}"`);
  }
}

/* ── 8. thẻ ở Cổng Thành ──────────────────────────── */
const goc = await doc("index.html");
for (const c of cung) {
  if (!goc.includes(`"${c}/"`)) bao(`index.html (Cổng Thành) chưa có thẻ dẫn vào "${c}"`);
}

/* ── 8b. script sinh dữ liệu ghi ra ngoài phạm vi git add ──
   Phép 3 soi chiều "add gì thì phải khai trong tài liệu". Chiều
   ngược lại mới là chiều nguy hiểm: **script GHI vào đâu mà add
   không phủ** thì file sinh ra rồi mất, và không lỗi nào báo.

   Đã dính thật, hai chỗ cùng lúc: build-l2beat.mjs và
   build-congbo.mjs tải logo về `assets/logos/`, còn `git add` chỉ
   phủ `assets/js/`. Hệ quả: `logos.js` được commit và trỏ tới ảnh
   chưa bao giờ được commit. Chưa nổ vì lần thêm logo gần nhất làm
   bằng tay — sẽ nổ đúng lần L2BEAT thêm một dự án mới.

   Đọc mã bằng regex nên chỉ bắt được khuôn `const X = join(ROOT, …)`
   rồi `writeFile(join(X, …))`. Khuôn khác thì bỏ qua chứ không đoán:
   phép kiểm báo nhầm còn tệ hơn phép kiểm thiếu. */
const NGUON_GHI = [
  ["build-live.mjs", ".github/workflows/refresh-data.yml"],
  ["build-l2beat.mjs", ".github/workflows/refresh-data.yml"],
  ["build-congbo.mjs", ".github/workflows/refresh-data.yml"],
  ["build-tangthu.mjs", ".github/workflows/refresh-data.yml"],
  ["pin-snapshot.mjs", ".github/workflows/refresh-data.yml"],
  ["build-scan.mjs", ".github/workflows/refresh-data.yml"]
];

/* Phạm vi add giờ SINH ra từ sổ đăng ký, không còn nằm trong YAML —
   nên hỏi sổ, đừng đọc lại YAML. Một nguồn, không có bản chép nào
   để mà lệch. */
async function phamViAdd(wf) {
  if (!existsSync(join(ROOT, wf))) return null;
  try {
    const NM = await import("./nha-may.mjs");
    if (typeof NM.duongRa !== "function") return null;
    /* Lấy CẢ đường chưa có file: phép này soi "script ghi vào đâu",
       và một node chưa chạy lần nào vẫn phải được phủ. */
    const ds = new Set([NM.DUONG_TRANG_THAI, NM.DUONG_CHIEU, NM.DUONG_SO]);
    for (const n of NM.NODE) for (const d of n.ra || []) if (d) ds.add(d);
    return [...ds];
  } catch { return null; }
}

const camAdd = {};
for (const [, wf] of NGUON_GHI) if (!(wf in camAdd)) camAdd[wf] = await phamViAdd(wf);

for (const [tep, wf] of NGUON_GHI) {
  if (!existsSync(join(ROOT, "scripts", tep))) continue;
  const pv = camAdd[wf];
  if (!pv) { nhac(`${wf}: không đọc được khối "git add" để soi đường ghi`); continue; }

  const s = await doc(join("scripts", tep));
  const bien = {};
  for (const m of s.matchAll(/const (\w+) = join\(ROOT,\s*([^)]*)\)/g)) {
    bien[m[1]] = m[2].split(",").map((x) => x.trim().replace(/^["']|["']$/g, "")).join("/");
  }

  const duong = new Set();
  // writeFile(join(BIEN, "a", "b")) — phần nào là biến thì cắt, giữ tiền tố chắc chắn
  for (const m of s.matchAll(/writeFile\(\s*join\((\w+)\s*,\s*([^)]*)\)/g)) {
    const goc = bien[m[1]];
    if (!goc) continue;
    const phan = [];
    for (const p of m[2].split(",").map((x) => x.trim())) {
      if (!/^["']/.test(p)) break;                 // gặp biến thì dừng
      phan.push(p.replace(/^["']|["']$/g, ""));
    }
    duong.add(phan.length ? goc + "/" + phan.join("/") : goc + "/");
  }
  // writeFile(BIEN, …)
  for (const m of s.matchAll(/writeFile\(\s*(\w+)\s*,/g)) {
    if (bien[m[1]]) duong.add(bien[m[1]]);
  }

  for (const d of duong) {
    const phu = pv.some((p) => {
      const pp = p.replace(/\/$/, "");
      return d === p || d === pp || d.startsWith(pp + "/");
    });
    if (!phu) {
      bao(`scripts/${tep} ghi vào "${d}" nhưng ${wf.split("/").pop()} không add đường đó\n` +
        "        → file sinh ra rồi mất sau mỗi lượt bot, và không lỗi nào báo.");
    }
  }
}

/* ── 8c. sổ nhà máy khớp với workflow thật không ──────
   Từ khi nhịp chạy nằm ở NODE trong scripts/nha-may.mjs, sổ đó là
   nguồn sự thật cho ba thứ vốn rời nhau: node nào chạy, bao lâu một
   lượt, và nó ghi ra file nào. Sức mạnh ấy đi kèm ba cách hỏng mới,
   cả ba đều IM LẶNG — không lỗi, không đỏ, chỉ là dữ liệu ngừng mới:

     · node có nhịp nhưng không workflow nào gọi tới  → không bao giờ chạy
     · node ghi ra file mà `git add` không phủ        → chạy rồi mất
     · registry.json lệch NODE                        → tài liệu nói dối

   Phép kiểm này soi cả ba. */
{
  let NM = null;
  try { NM = await import("./nha-may.mjs"); }
  catch (e) { bao(`scripts/nha-may.mjs không nạp được — ${e.message}`); }

  if (NM) {
    const wfs = [".github/workflows/refresh-data.yml"];
    const noiDung = {};
    for (const w of wfs) if (existsSync(join(ROOT, w))) noiDung[w] = await doc(w);

    for (const n of NM.NODE) {
      /* Node "tay" và "theo" cố ý không có workflow nào gọi — bỏ qua.
         Hoàng Thành lấy nguồn ngoài repo nên Actions không quét được;
         giao hàng thì chạy theo commit chứ không theo nhịp. */
      if (!n.nhip) continue;

      const chay = Object.keys(noiDung).filter((w) => noiDung[w].includes(`,${n.ma},`));
      if (!chay.length) {
        bao(`node "${n.ma}" khai nhịp ${n.nhip} giờ nhưng KHÔNG workflow nào gọi tới nó\n` +
          "        → Bảng vận hành sẽ mãi báo 'đến hạn' cho một node không bao giờ chạy.");
        continue;
      }

      /* CỐ Ý không còn soi "`ra` của node có được `git add` phủ không".
         Từ 20/08 khối add SINH RA từ chính `ra`, nên phép ấy thành
         vòng tự so với mình: không bao giờ đỏ được nữa.

         Một phép kiểm không thể đỏ thì tệ hơn không có phép nào — nó
         vẫn in dấu ✓ và người đọc tưởng có ai đó đang canh.

         Chiều nguy hiểm vẫn được canh, ở phép 8b: script GHI vào đâu
         mà `ra` không khai. Đó mới là chỗ file sinh ra rồi mất. */
    }

    /* registry.json phải là bản chiếu đúng của NODE. Nó được commit để
       Claude Code Action đọc được trong runner, nên nó CÓ THỂ lệch —
       và một sổ đăng ký nói sai thì mọi thứ đọc nó đều sai theo. */
    const pSo = join(ROOT, NM.DUONG_SO);
    if (!existsSync(pSo)) {
      bao(`Thiếu ${NM.DUONG_SO} — chạy: node scripts/nha-may.mjs so-dang-ky`);
    } else {
      const tren = JSON.parse(await doc(NM.DUONG_SO));
      if (JSON.stringify(tren.node) !== JSON.stringify(NM.NODE)) {
        bao(`${NM.DUONG_SO} lệch với NODE trong scripts/nha-may.mjs\n` +
          "        → chạy: node scripts/nha-may.mjs so-dang-ky");
      }
    }

    /* Hai danh sách cùng nói về một tập nguồn dữ liệu, ở hai file khác
       nhau. Không có phép kiểm này thì thêm một cung mới vào một bên mà
       quên bên kia là chuyện sẽ xảy ra, và hậu quả im: hoặc nguồn mới
       không ai canh độ tươi, hoặc nó không bao giờ được lên lịch. */
    const maNode = new Set(NM.NODE.filter((n) => n.cung).map((n) => n.cung));
    for (const g of NGUON) {
      const c = g.duong.split("/")[0];
      if (!maNode.has(c)) {
        nhac(`nguồn "${g.nhan}" (${c}) có trong tuoi-du-lieu.mjs nhưng không có node ` +
          "nào trong nha-may.mjs — nó không được lên lịch bao giờ.");
      }
    }
  }
}

/* ── 9. bot còn sống không ────────────────────────────
   Bảy phép trên soi repo có tự khớp với tài liệu không. Không
   phép nào soi được thứ đã xảy ra thật ngày 13–14/08/2026:
   repo khớp hoàn hảo, tài liệu đúng từng chữ, mà đường ống bot
   chết hơn một ngày — bước đóng dấu Pinata ngã kéo cả job, rồi
   job đụng trần 10 phút. Bước commit chưa lần nào chạy tới,
   site đứng im, và KHÔNG CÓ LỖI NÀO NỔI LÊN.

   build-dist.mjs có in "⚠" nhưng nó không thoát khác 0, và
   `npm run dist` không nằm trong danh sách lệnh đầu phiên. Nên
   phép kiểm có mà không tới được mắt ai.

   Nhắc chứ không báo lỗi: bot chết không phải lỗi của phiên
   đang mở, và không được chặn họ làm cung của mình. Nhưng nó
   in ở đầu mỗi phiên, nên không thể chết âm thầm cả ngày nữa. */
for (const n of NGUON) {
  /* Nguồn đang tắt có chủ ý: nhắc một dòng bình thản để còn nhớ mà
     bật lại, chứ đừng báo "có gì đó gãy" cho thứ không gãy. */
  if (n.tamDung) { nhac(`${n.nhan}: TẠM DỪNG — ${n.tamDung}`); continue; }
  const t = await tuoi(ROOT, n.duong);
  if (!t.co) {
    if (n.botSinh) nhac(`${n.nhan}: chưa sinh lần nào, hoặc thiếu dấu thời gian (${n.duong})`);
    continue;
  }
  const nguong = nguongCua(n);
  if (n.botSinh && t.ngay > nguong) {
    nhac(
      `${n.nhan}: sinh cách đây ${t.ngay.toFixed(1)} ngày — quá ${nguong} ngày là có gì đó gãy.\n` +
      "        Xem: https://github.com/sunswagz/blockchainworld/actions"
    );
  }
}

/* ── 9. CACHE_VERSION có theo kịp file trong SHELL không ──
   Mỗi sw.js liệt kê một mảng SHELL và phục vụ chúng theo lối
   CACHE-TRƯỚC. Sửa một file trong SHELL mà không nâng
   CACHE_VERSION thì máy đã cài app cứ dùng bản cũ trong cache.

   Hỏng kiểu này khó lần ra nhất trong repo: không có lỗi mạng,
   không có 404, HTML mới ghép CSS cũ nên chỉ thấy GIAO DIỆN VỠ.
   Đã dính thật: xếp lại thứ bậc Cổng Thành, đổi portal.css,
   quên nâng v4 → v5, và icon SVG mất luật cỡ nên phình kín màn hình.

   Cách kiểm: so commit cuối của sw.js với commit cuối của từng
   file nó khai trong SHELL. */
function commitCuoi(p) {
  try {
    return execFileSync("git", ["log", "-1", "--format=%ct", "--", p],
      { cwd: ROOT, encoding: "utf8" }).trim();
  } catch { return ""; }
}

/* Đường do bot ghi, gom từ `ra` của mọi node. Chỉ dùng để quyết định
   khi nào "không đọc được khai báo mạng-trước" là chuyện đáng nói —
   một cung tĩnh hoàn toàn thì không có đường mạng-trước nào là bình
   thường, còn một cung có file bot trong SHELL thì câu trả lời đó
   quyết định người dùng thấy bản mới hay bản cũ. */
let duongBot = [];
try {
  const NM2 = await import("./nha-may.mjs");
  duongBot = NM2.NODE.flatMap((n) => n.ra || []);
} catch { /* nha-may.mjs hỏng thì mục 8c đã báo rồi, không báo hai lần */ }

for (const c of ["."].concat(cung)) {
  const swP = c === "." ? "sw.js" : `${c}/sw.js`;
  if (!existsSync(join(ROOT, swP))) continue;
  const sw = await doc(swP);
  if (!/CACHE_VERSION\s*=/.test(sw)) continue;

  const tSw = Number(commitCuoi(swP) || 0);
  if (!tSw) continue;                       // chưa commit lần nào — bỏ qua

  /* File được phục vụ MẠNG-TRƯỚC thì không cần nâng version: service
     worker đi lấy bản mới mỗi lần, cache chỉ là lưới đỡ lúc mất mạng.
     Bốn cung lấy số từ API để data.js ở nhánh đó và bot ghi 4 lượt/ngày
     — bắt nâng version mỗi lượt là biến phép kiểm thành tiếng ồn.

     Nhận diện nằm ở scripts/mang-truoc.mjs, dùng chung với `npm run nang`
     — trước đây cùng một regex bị chép ở cả hai file. (sw.js gốc cũng
     dùng khuôn này để BỎ QUA đường của từng cung, nhưng SHELL của nó
     không chứa đường nào như vậy nên không có chuyện miễn trừ nhầm.) */
  const { duong: mangTruoc, docDuoc } = docMangTruoc(sw);
  /* docShell — một chỗ duy nhất, xem scripts/mang-truoc.mjs. Regex cũ ở
     đây neo đầu dòng nên bỏ qua đường thứ hai trở đi trên cùng một dòng.
     dai-quan-trac viết hai đường một dòng, nên bang.js và nen.js — 30 KB —
     vô hình với cả bốn script chép cùng regex này. */
  const shell = docShell(sw).duong;

  /* Không đọc được khai báo thì NÓI RA, đừng buộc tội. Rút ra không
     đường nào có thể vì cung ấy thật sự không có file mạng-trước,
     cũng có thể vì nó khai bằng một dạng bộ kiểm chưa biết — hai
     chuyện khác hẳn nhau. Chỉ lên tiếng khi câu trả lời THỰC SỰ quan
     trọng, tức là khi trong SHELL có file do bot ghi: cung tĩnh hoàn
     toàn thì không đường mạng-trước nào là bình thường. */
  if (!docDuoc) {
    const botTrongShell = shell.filter((f) => {
      const p = c === "." ? f : `${c}/${f}`;
      return duongBot.some((d) => p === d || p.startsWith(d));
    });
    if (botTrongShell.length) {
      bao(`${swP}: không đọc được khai báo mạng-trước, mà SHELL có ` +
        `${botTrongShell.length} file do bot ghi — ${botTrongShell.slice(0, 3).join(", ")}\n` +
        `        Bộ kiểm KHÔNG kết luận gì về CACHE_VERSION của cung này.\n` +
        `        Thêm dạng khai báo đó vào scripts/mang-truoc.mjs.`);
    }
    continue;
  }

  const tre = [];
  for (const f of shell) {
    if (laMangTruoc(mangTruoc, f)) continue;
    const p = c === "." ? f : `${c}/${f}`;
    if (!existsSync(join(ROOT, p))) continue;
    const t = Number(commitCuoi(p) || 0);
    if (t > tSw) tre.push(f);
  }
  if (tre.length) {
    bao(`${swP}: CACHE_VERSION chưa nâng, nhưng ${tre.length} file trong SHELL ` +
      `mới hơn — ${tre.slice(0, 4).join(", ")}${tre.length > 4 ? "…" : ""}\n` +
      `        Máy đã cài app sẽ nhận bản CŨ của những file đó (giao diện vỡ, không báo lỗi).`);
  }
}

/* ── 10. node nào ngã nhiều lượt liền ───────────────
   Sổ nhà máy ghi `chuoiLoi` cho mỗi node, và Bảng vận hành hiện nó.
   Nhưng cả hai chỉ tới được người ĐI TÌM. Một node chết không làm
   Actions đỏ — workflow vẫn xanh vì bước đó `continue-on-error`, và
   lượt sau lại chạy, lại ngã, lại ghi sổ.

   Đã xảy ra thật: `tien-hoa-dqt` khai `--model claude-haiku-4-5`, một
   id KHÔNG tồn tại (Haiku 4.5 là `claude-haiku-4-5-20251001`). Bước
   gọi model chết sau 2 giây, chín lượt liền, `lucOk: null` — chưa
   thành công lần nào kể từ khi dựng. Chín ngày, không dòng nào nổi
   lên chỗ người ta nhìn.

   Nhắc chứ không báo lỗi, cùng lý do với mục dữ liệu cũ: node chết
   không phải lỗi của phiên đang mở. Nhưng in ở đầu mỗi phiên thì nó
   không chết âm thầm được nữa. */
{
  const p = join(ROOT, "factory", "state.json");
  if (existsSync(p)) {
    try {
      const s = JSON.parse(await doc("factory/state.json"));
      const n = s.node || s;
      for (const [ma, v] of Object.entries(n)) {
        if (!v || typeof v !== "object" || !v.chuoiLoi || v.chuoiLoi < 3) continue;
        nhac(`node "${ma}": ngã ${v.chuoiLoi} lượt liền` +
          (v.lucOk ? `, lần chạy được cuối là ${String(v.lucOk).slice(0, 10)}` : ", CHƯA thành công lần nào") +
          (v.chuThich ? `\n        ghi sổ: ${v.chuThich}` : ""));
      }
    } catch { nhac("factory/state.json không đọc được — không soi được node nào đang ngã."); }
  }
}

/* ── 11. lớp tri thức có còn khớp repo không ─────────
   `knowledge-os/kiem.mjs` đọc mã phòng THẲNG từ mã nguồn từng cung,
   nên nó là thứ duy nhất phát hiện được chuyện này: một cung thêm
   phòng mới, và lớp giải nghĩa im lặng vắng mặt ở đó.

   Nhưng chuông chỉ kêu khi có người bấm. Trước khi cắm vào đây, không
   có gì bấm nó — `npm run kiem` chạy đầu mỗi phiên mà không hề gọi
   tới, nên drift nằm im tới lúc ai đó nhớ ra. Đã có thật: Thị Bạc Ty
   thêm phòng `trung-uong` và lớp tri thức không hay biết.

   Gọi bằng tiến trình con để bộ kiểm của gói giữ được mã thoát riêng,
   và để `kiem` này không phải biết gì về cấu trúc dữ liệu bên đó. */
{
  const p = join(ROOT, "knowledge-os", "kiem.mjs");
  if (existsSync(p)) {
    try {
      execFileSync(process.execPath, [p, "--im"], { cwd: ROOT, encoding: "utf8", stdio: "pipe" });
    } catch (e) {
      const ra = String(e.stdout || "") + String(e.stderr || "");
      const dong = ra.split("\n").filter((x) => x.trim().startsWith("✗")).slice(0, 3);
      bao("lớp tri thức lệch với repo — chạy: npm run tri-thuc-kiem\n" +
        dong.map((x) => "        " + x.trim()).join("\n"));
    }
  }
}

/* ── PHÉP: NGÂN SÁCH THỜI GIAN CỦA LƯỢT CHẠY ──────────
   Trước đây workflow tự canh bằng MỘT KHỐI CỘNG TAY:

     #   5 + 3 + 2 + 5 + 14 + 3 + 2   (lấy số liệu + đóng dấu)
     # + 2 + 15 + 2                   (ra đề · quét · dựng)
     #   = 75  <  80

   Khối đó đã lệch HAI LẦN. Lần đầu 20/08 (thêm Thái Bộc Tự, quên
   cộng, tổng thật 72 > trần job 70). Lần hai lộ ra hôm nay: khai
   75, cộng thật 236, trần job đã bị nâng lên 130 mà khối cộng
   không ai đụng. Một con số phải cộng tay mỗi lần thêm bước thì
   sớm muộn cũng thành trang trí — đúng như dòng cảnh báo nằm ngay
   trên chính nó.

   Bỏ luôn cách cộng đó, vì ngoài chuyện lệch nó còn SAI VỀ CHẤT:
   `timeout-minutes` của một bước là VAN AN TOÀN, không phải ước
   lượng. Cộng các van lại rồi so với trần job là so hai đại lượng
   khác loại — muốn tổng đó nhỏ hơn trần job thì phải siết van
   xuống sát thời gian chạy thật, tức là biến van thành thứ hay nổ
   oan.

   Cái đáng canh là thời gian chạy THẬT, và sổ nhà máy đã ghi sẵn
   (`--giay` mỗi node). Nên phép này hỏi ba câu đo được:

     1. Bước nào có việc mà KHÔNG có van?  (một bước treo là cả
        lượt treo tới trần job)
     2. Cộng giây thật của MỌI node có vượt trần job không? Đây là
        lượt xấu nhất và nó xảy ra THẬT mỗi ngày: nhịp 6·12·24·168
        đều chia hết cho lượt gióng hàng, nên có một lượt trong
        ngày mọi node cùng đến hạn.
     3. Node nào đang chạy sát van của chính nó? Sát van là sắp nổ,
        và nó sẽ nổ vào lúc mạng chậm chứ không phải lúc ta đang
        nhìn.

   Số liệu là một mẫu gần nhất mỗi node, không phải p100 — nên
   ngưỡng để rộng (gấp ba) chứ không bắt sát. */
{
  const wf = ".github/workflows/refresh-data.yml";
  if (existsSync(join(ROOT, wf))) {
    const L = (await doc(wf)).split("\n");
    let tranJob = 0;
    const buoc = [];
    let cur = null;
    for (const l of L) {
      let m;
      if ((m = l.match(/^    timeout-minutes:\s*(\d+)/))) tranJob = +m[1];
      if ((m = l.match(/^      - name:\s*(.+?)\s*$/))) {
        if (cur) buoc.push(cur);
        cur = { ten: m[1], tran: null, id: null, viec: false };
      }
      if (!cur) continue;
      if ((m = l.match(/^        timeout-minutes:\s*(\d+)/))) cur.tran = +m[1];
      if ((m = l.match(/^        id:\s*n-(.+?)\s*$/))) cur.id = m[1];
      if (/^        (run|uses):/.test(l)) cur.viec = true;
    }
    if (cur) buoc.push(cur);

    /* 0. khối cộng tay không được sống lại */
    const congTay = L.filter((l) => /^\s*#\s*=\s*\d+\s*<\s*\d+/.test(l));
    if (congTay.length)
      bao(
        `refresh-data.yml lại có khối cộng trần bước bằng tay ("${congTay[0].trim()}").\n` +
        `        Con số đó đã lệch hai lần. Ngân sách lượt chạy do phép này canh bằng\n` +
        `        giây THẬT trong factory/state.json — xoá khối cộng tay đi.`
      );

    /* 1. bước có việc mà không có van */
    const hoBuoc = buoc.filter((b) => b.viec && b.tran === null && !/^Ghi sổ|^Bấm giờ|^Đánh dấu|^Chiếu sổ/.test(b.ten));
    for (const b of hoBuoc)
      bao(`bước "${b.ten}" trong refresh-data.yml có việc nhưng KHÔNG khai timeout-minutes — treo là cả lượt treo tới trần job ${tranJob} phút`);

    /* 2 + 3. đối chiếu với giây chạy thật */
    let so = null;
    try { so = JSON.parse(await doc("factory/state.json")); } catch { /* chưa có sổ */ }
    if (so?.node && tranJob) {
      const giayTong = Object.values(so.node).reduce((a, n) => a + (n.giay || 0), 0);
      const phut = giayTong / 60;
      if (phut * 3 > tranJob)
        bao(
          `lượt xấu nhất (mọi node cùng đến hạn) chạy thật ${phut.toFixed(1)} phút, trần job ${tranJob} phút —\n` +
          `        còn chưa tới ba lần đệm. Nâng trần job, hoặc giãn nhịp node nặng nhất.`
        );
      else
        nhac(`ngân sách lượt: ${phut.toFixed(1)} phút chạy thật / ${tranJob} phút trần job (đệm ${(tranJob / phut).toFixed(1)}×)`);

      const wfT = L.join(String.fromCharCode(10));
      const nhieuBuoc = [];
      for (const b of buoc) {
        if (!b.id || b.tran === null) continue;
        const g = so.node[b.id]?.giay;
        if (typeof g !== "number" || !g) continue;
        const donBuoc = wfT.includes("GIAY: ${{ steps.n-" + b.id + ".outputs.giay }}");
        if (!donBuoc) { nhieuBuoc.push(b.id); continue; }
        const tyLe = g / (b.tran * 60);
        if (tyLe > 0.6)
          nhac(`node "${b.id}" chạy ${g}s, van của nó là ${b.tran} phút — dùng hết ${(tyLe * 100).toFixed(0)}% van, sắp nổ khi mạng chậm`);
      }
      /* KHAI RA CÁI KHÔNG CANH ĐƯỢC — im lặng bỏ qua thì lần sau
         người đọc tưởng mọi node đều đã được soi van. */
      if (nhieuBuoc.length)
        nhac(`không soi được van của ${nhieuBuoc.length} node đo-nhiều-bước (${nhieuBuoc.join(", ")}) — ` +
             `giây của chúng là tổng cả nhóm bước, không so được với van của một bước`);
    }
  }
}

/* ── 12. chỗ đè im lặng trong CSS ─────────────────────
   Cùng ngữ cảnh, cùng selector, cùng thuộc tính, khác giá trị, ở hai
   khối khác nhau: một trong hai đang chết và người viết nó không hay.

   Cắm vào đây vì lớp lỗi này MỞ RỘNG THEO SỐ CUNG. `knowledge-os`
   sinh widget mang tiền tố `tt-` cho mười một cung, nên mỗi lớp mới
   là mười một chỗ có thể đụng tên với lớp sẵn có của cung. Đã đụng
   thật: Đài Quan Trắc dùng `tt-` cho "trạng thái", widget dùng `tt-`
   cho "tri thức", và số cấp độ — chữ to nhất trên dải — bị vẽ 10,5px
   thay vì 27px ở mọi trang, không lỗi nào báo. Tìm ra nó là do may.

   NHẮC chứ không báo lỗi: CSS của cung khác không phải việc của phiên
   đang mở, và chặn họ vì chuyện đó là đúng thứ luật worktree sinh ra
   để tránh. Nhưng in ở đầu mỗi phiên thì không ai nằm im được nữa. */
{
  const p = join(ROOT, "scripts", "de-im-lang.mjs");
  if (existsSync(p)) {
    try {
      execFileSync(process.execPath, [p], { cwd: ROOT, encoding: "utf8", stdio: "pipe" });
    } catch (e) {
      const ra = String(e.stdout || "") + String(e.stderr || "");
      const dong = ra.split("\n").filter((x) => /chỗ đè$/.test(x.trim()));
      nhac(`${dong.length} tệp CSS có chỗ đè im lặng — chạy: npm run de-im-lang\n` +
        dong.slice(0, 4).map((x) => "        · " + x.trim()).join("\n"));
    }
  }
}

/* ── phép: lớp CSS không ai dùng ───────────────────
   Cùng lối NHẮC như phép trên, và cùng lý do. Khác một điều đáng
   nói: phép này là PHỎNG ĐOÁN, không phải phép đo — lớp CSS không
   được ai GỌI, nó chỉ khớp hoặc không. Nên nó nới về phía an toàn
   và vẫn có thể kêu oan ở tên lớp trùng khoá dữ liệu (`.ng` gặp
   `ng:"2026-08-28"`) hay trùng chữ tiếng Việt (`.dem`, `.hang`).

   Đo ngày 02/09: 45 ứng viên trên 12 cung, trong đó 40 được một
   phép ĐỘC LẬP (đếm thô toàn bộ HTML+JS) xác nhận bằng 0. Nhóm
   `hs-*` chết ở CẢ HAI cung kham-thien-giam và thai-boc-tu — một
   khối chép qua rồi không ai dùng ở cả hai nơi. */
{
  const p = join(ROOT, "scripts", "lop-chet.mjs");
  const NL = String.fromCharCode(10);
  if (existsSync(p)) {
    try {
      execFileSync(process.execPath, [p], { cwd: ROOT, encoding: "utf8", stdio: "pipe" });
    } catch (e) {
      const ra = String(e.stdout || "") + String(e.stderr || "");
      const dong = ra.split(NL).filter((x) => /lớp không token nào chạm tới/.test(x));
      if (dong.length)
        nhac(dong.length + " cung có lớp CSS không ai dùng — chạy: npm run lop-chet" + NL +
          dong.slice(0, 4).map((x) => "        · " + x.trim()).join(NL));
    }
  }
}

/* ── phép: cổng chặn nạp dữ liệu tự sinh ──────────
   Cổng nằm ở .claude/hooks/, ngoài tầm mắt của phép kiểm khác vì
   .claude bị BO_QUA. Nhưng nó là thứ giữ cho phiên không bị 16 MB
   dữ liệu tự sinh làm nghẽn, nên phải có người canh nó. */
{
  const NL = String.fromCharCode(10);
  const CAN = [
    ".claude/hooks/chan-doc-du-lieu.mjs",
    ".claude/hooks/du-lieu-cam.json",
    ".claude/hooks/thu-chan-doc.mjs",
    ".claude/settings.json",
  ];
  const thieu = CAN.filter((f) => !existsSync(join(ROOT, f)));
  if (thieu.length) {
    bao(
      "cổng chặn nạp dữ liệu tự sinh thiếu mảnh: " + thieu.join(", ") +
        " — không còn gì chặn `cat` đổ 16 MB dữ liệu vào ngữ cảnh",
    );
  } else {
    const t = await doc(".claude/settings.json");
    if (!t.includes("chan-doc-du-lieu.mjs")) {
      bao(".claude/settings.json không còn gọi hook chan-doc-du-lieu.mjs");
    }
    if (!t.includes("permissions")) {
      bao(".claude/settings.json không còn khối permissions.deny");
    }
    const { spawnSync } = await import("node:child_process");
    const r = spawnSync(
      process.execPath,
      [join(ROOT, ".claude/hooks/thu-chan-doc.mjs")],
      { encoding: "utf8" },
    );
    if (r.status !== 0) {
      const dong = (r.stdout || "").trim().split(NL).filter(Boolean);
      bao(
        "bộ kiểm cổng chặn dữ liệu KHÔNG qua — chạy: " +
          "node .claude/hooks/thu-chan-doc.mjs" + NL +
          dong.slice(0, 8).map((x) => "        · " + x.trim()).join(NL),
      );
    }
  }
}

/* ── 13. ảnh khai mà không có trên đĩa ────────────────
   `build-l2beat.mjs` và `build-congbo.mjs` TẢI ảnh về `assets/logos/`
   rồi ghi `logos.js` trỏ tới chúng. `git add` không phủ thư mục ảnh
   thì bảng tra được commit còn ảnh thì không — trang hiện ô vỡ, và
   không lỗi nào báo: không 404 trong log build, Actions vẫn xanh.

   Mục "File do workflow tự sinh" trong CLAUDE.md đã mô tả đúng lớp lỗi
   này bằng văn xuôi, kèm cả câu "sẽ nổ đúng lần L2BEAT thêm dự án
   mới". Lời cảnh báo trong văn xuôi chỉ cứu được người vừa đọc đúng
   đoạn ấy; đây là bản chạy được của nó.

   NHẮC chứ không báo lỗi, cùng lý do với phép kiểm chỗ-đè: ảnh do bot
   ghi, nên phiên đang mở không phải người gây ra và không đáng bị chặn
   vì chuyện đó. */
{
  const p = join(ROOT, "scripts", "kiem-anh.mjs");
  if (existsSync(p)) {
    try {
      execFileSync(process.execPath, [p], { cwd: ROOT, encoding: "utf8", stdio: "pipe" });
    } catch (e) {
      const ra = String(e.stdout || "") + String(e.stderr || "");
      const dong = ra.split("\n").filter((x) => x.trim().startsWith("✗"));
      nhac(`ảnh khai mà thiếu trên đĩa — chạy: npm run kiem-anh\n` +
        dong.slice(0, 2).map((x) => "        " + x.trim()).join("\n"));
    }
  }
}

/* ── PHÉP: MỘT CUNG KHÔNG ĐƯỢC NẰM Ở HAI VÒNG TIẾN HOÁ ──
   `VONG_XOAY` trong scripts/tien-hoa.mjs là danh sách cung dùng
   CHUNG một node xoay vòng, mỗi ngày một cung. Cung nào được cấp
   vòng RIÊNG thì phải gỡ khỏi danh sách đó.

   Quên gỡ là mỗi tuần có một ngày cung ấy bị hai model sửa trong
   cùng một lượt, không biết nhau: model thứ hai đo phiếu SAU khi
   model thứ nhất đã sửa, nên "không được xấu đi" so với một mốc gốc
   đã dịch. Hai bản vá chồng lên nhau và cổng chặn vẫn xanh.

   Không đọc YAML để đoán — hỏi thẳng chuỗi `de-bai <cung>` mà mỗi
   vòng riêng đều phải gọi. */
{
  const wf = ".github/workflows/refresh-data.yml";
  if (existsSync(join(ROOT, wf))) {
    const t = await doc(wf);
    /* Đọc từ scripts/vong-xoay.mjs, KHÔNG từ tien-hoa.mjs: file kia
       gọi `thoat("Thiếu lệnh")` ngay ở đầu khi không có tham số, nên
       import nó là giết cả bộ kiểm. Đã dính đúng một lần. */
    let VX = null;
    try { VX = await import("./vong-xoay.mjs"); } catch { /* chưa có file */ }
    const xoay = VX && Array.isArray(VX.VONG_XOAY) ? VX.VONG_XOAY : null;
    if (xoay) {
      for (const c of xoay) {
        if (t.includes(`tien-hoa.mjs de-bai ${c}`))
          bao(`cung "${c}" vừa nằm trong VONG_XOAY vừa có vòng tiến hoá RIÊNG trong workflow —\n` +
              `        mỗi tuần một ngày nó bị hai model sửa trong cùng một lượt.\n` +
              `        Gỡ nó khỏi VONG_XOAY ở scripts/tien-hoa.mjs.`);
        /* `cong-thanh` là BÍ DANH của trang gốc, không phải thư mục —
           xem đầu scripts/vong-xoay.mjs. Đo nó bằng ROOT/index.html
           chứ không phải ROOT/cong-thanh/index.html, không thì phép
           canh này báo oan đúng ngày Cổng Thành được nối vào vòng. */
        const ten = c === "cong-thanh" ? "index.html" : `${c}/index.html`;
        if (!existsSync(join(ROOT, ten)))
          bao(`VONG_XOAY khai cung "${c}" nhưng không có ${ten} — node xoay sẽ ngã vào ngày tới lượt nó`);
      }

      /* Chiều ngược lại: cung KHÔNG thuộc vòng nào thì không bao giờ
         tiến hoá, và không có gì báo. Đây là hình dạng của một cung
         vừa được thêm — người thêm nhớ bảy chỗ trong CLAUDE.md,
         nhưng vòng tiến hoá không nằm trong bảy chỗ đó.

         `nhac` chứ không `bao`: có thể là cố ý (một cung tĩnh hoàn
         toàn, hoặc đang dựng dở). Nhưng phải NÓI RA — im lặng ở đây
         nghĩa là cung ấy đứng yên nhiều tháng mà mọi bảng đều xanh. */
      const coVongRieng = (c) => t.includes(`tien-hoa.mjs de-bai ${c}`);
      const boRoi = cung.filter((c) => !xoay.includes(c) && !coVongRieng(c));
      if (boRoi.length)
        nhac(`${boRoi.length} cung không thuộc vòng tiến hoá nào (${boRoi.join(", ")}) — ` +
             `chúng chỉ tiến khi có người ngồi vào sửa. Thêm vào VONG_XOAY ở scripts/vong-xoay.mjs, ` +
             `hoặc cấp vòng riêng.`);
    }
  }
}

/* ── PHÉP: CỔNG THÀNH PHẢI NẰM TRONG VÒNG ──────────────
   Trước 02/09/2026 khối này là một BẢN CHÉP TAY: `tien-hoa.mjs` dựng
   đường theo `<cung>/…` nên không trỏ vào gốc repo được, và trang đầu
   tiên người ta thấy là trang duy nhất không thước nào chạm tới. Nên
   năm luật đọc-được-bằng-chuỗi bị chép lại ở đây.

   Nay bộ thước nhận `cong-thanh` làm bí danh cho gốc và chấm đủ 17
   thước cho nó, kể cả những thước động mà bản chép không làm được.
   Giữ cả hai là nuôi hai bản sao của cùng một luật, rồi chúng lệch —
   đúng bài học `scripts/mang-truoc.mjs`. Nên phần chép đã GỠ, và việc
   còn lại của khối này là canh chỗ NỐI: bộ thước chấm được không có
   nghĩa là có ai gọi nó.

   Hai chỗ nối, hỏng chỗ nào cũng đưa Cổng Thành về đúng tình trạng
   cũ — chấm được mà không ai chấm, và không dòng nào báo. */
{
  if (existsSync(join(ROOT, "index.html"))) {
    let VX = null;
    try { VX = await import("./vong-xoay.mjs"); } catch { /* chưa có file */ }
    if (VX && Array.isArray(VX.VONG_XOAY) && !VX.VONG_XOAY.includes("cong-thanh"))
      bao(`Cổng Thành (index.html ở gốc) không nằm trong VONG_XOAY — nó chỉ tiến khi có\n` +
          `        người ngồi vào sửa, trong khi mười hai cung tiến mỗi ngày hoặc mỗi tuần.\n` +
          `        Thêm "cong-thanh" vào scripts/vong-xoay.mjs.`);

    const pt = await doc("scripts/phieu-toan-thanh.mjs").catch(() => "");
    if (pt && !pt.includes('"cong-thanh"'))
      bao(`scripts/phieu-toan-thanh.mjs không chấm Cổng Thành — phiếu toàn thành liệt kê cung\n` +
          `        bằng "thư mục có index.html", mà gốc repo không phải thư mục con nào.\n` +
          `        factory/phieu.json sẽ khai 12 cung và im lặng bỏ trang gốc.`);
  }
}

/* ── PHÉP: THẺ HTML PHẢI CÂN, CẢ 13 TRANG ──────────────
   Trình duyệt vá HTML hỏng rất giỏi, nên một trang thiếu thẻ mở vẫn
   hiện ra bình thường và không ai biết. Đo 29/08: `kinh-thanh` có
   `</body>` ở dòng cuối mà KHÔNG có `<body>` — thiếu suốt từ đầu.

   Hậu quả không chỉ là "HTML sai": thước "đường nhảy qua thanh bên"
   cắt trang từ `indexOf("<body")`, và với cung đó nó nhận −1 rồi soi
   nhầm cả phần <head>. Một thẻ thiếu làm lệch giả định của phép đo
   khác, và đó là kiểu hỏng lan mà không ai lần ra.

   Đặt ở ĐÂY chứ không trong bộ thước tiến hoá là có chủ ý: bảng thẻ
   rỗng dưới đây phải nuôi bằng tay, và một phép đo tự nuôi-bằng-tay
   mà đi chặn vòng tự động thì lần nó sai sẽ chặn cả bản vá đúng.
   Ở bộ kiểm thì nó chỉ làm phiền người đọc, và người đọc sửa được.

   Bỏ <script> trước khi đếm: bên trong là JS, mọi dấu < đều không
   phải thẻ. */
{
  const RONG = new Set(["br", "img", "input", "meta", "link", "hr", "path", "circle",
    "rect", "line", "polyline", "polygon", "use", "source", "area", "col", "embed",
    "track", "wbr", "ellipse", "stop", "base", "param"]);
  const trang = ["index.html", ...cung.map((c) => `${c}/index.html`)];
  for (const f of trang) {
    if (!existsSync(join(ROOT, f))) continue;
    const s = (await doc(f))
      .replace(/<!--[\s\S]*?-->/g, "")
      .replace(/<script[\s\S]*?<\/script>/g, "");
    const chong = [];
    const loi = [];
    for (const m of s.matchAll(/<(\/?)([a-zA-Z][\w-]*)([^>]*)>/g)) {
      const [, dong, ten, attr] = m;
      const t = ten.toLowerCase();
      if (t === "!doctype" || RONG.has(t) || attr.trim().endsWith("/")) continue;
      if (!dong) chong.push(t);
      else {
        const x = chong.pop();
        if (x !== t) loi.push(`</${t}> khi đang mở <${x ?? "không có gì"}>`);
      }
    }
    if (loi.length || chong.length)
      bao(`${f}: thẻ không cân — ${loi.slice(0, 2).join(" · ") || ""}` +
          (chong.length ? `${loi.length ? " · " : ""}còn mở: ${chong.join(", ")}` : "") +
          `\n        Trình duyệt vá được nên trang vẫn hiện, nhưng phép đo khác thì lệch theo.`);
  }
}

/* ── PHÉP: ĐƯỜNG ĐIỀU HƯỚNG PHẢI TRỎ VÀO CHỖ CÓ THẬT ───
   Mỗi cung mang một `assets/js/halls.js` do `npm run halls` sinh, và
   trong đó là 12 đường sang 12 cung. Cộng cả lưới trên Cổng Thành là
   156 đường; đổi tên hay bỏ một cung mà quên sinh lại là gãy đồng
   loạt 13 trang, và không có gì báo — `npm run live` chỉ soi TÀI
   NGUYÊN (script, css, ảnh), không soi liên kết trang.

   Soi trên ĐĨA chứ không gọi mạng: phép này phải chạy được trước khi
   đẩy, và một cung mới ở nhánh chưa gộp thì trên site chưa có. */
{
  const duongCung = (u) => u.replace(/^\.\.\//, "").replace(/\/$/, "");
  let tong = 0;
  for (const c of cung) {
    const p = join(ROOT, c, "assets", "js", "halls.js");
    if (!existsSync(p)) continue;
    const s = await doc(`${c}/assets/js/halls.js`);
    const hrefs = [...s.matchAll(/href:\s*"([^"]+)"/g)].map((m) => m[1]);
    tong += hrefs.length;
    const hong = hrefs.filter((u) => {
      if (/^https?:/.test(u)) return false;
      const t = duongCung(u);
      return t !== "" && !existsSync(join(ROOT, t, "index.html")) && !existsSync(join(ROOT, t));
    });
    if (hong.length)
      bao(`${c}/assets/js/halls.js trỏ vào ${hong.length} chỗ không có: ${hong.join(", ")}\n` +
          `        Chạy \`npm run halls\` để sinh lại cả 12 file.`);
  }
  if (existsSync(join(ROOT, "index.html"))) {
    const h = await doc("index.html");
    const hong = [...h.matchAll(/<a class="hall" href="([^"]+)"/g)]
      .map((m) => m[1])
      .filter((u) => !/^https?:/.test(u) && !existsSync(join(ROOT, duongCung(u), "index.html")));
    if (hong.length)
      bao(`index.html ở gốc trỏ vào ${hong.length} cung không có: ${hong.join(", ")}`);
  }
  if (tong) nhac(`điều hướng: ${tong} đường trong halls.js của ${cung.length} cung, tất cả trỏ vào chỗ có thật`);
}

/* ── PHÉP: BƯỚC GỌI MODEL PHẢI CÓ continue-on-error ────
   Model là phần DUY NHẤT của xưởng hỏng được vì lý do ngoài repo:
   hết quota, mạng chập, API đổi. Nên nó phải là phần không bao giờ
   kéo theo ai. Thiếu `continue-on-error: true` thì một lượt tiến hoá
   hỏng làm ĐỎ cả job và bỏ luôn bước deploy — tức là dữ liệu của
   mười hai cung đứng lại vì một bản vá giao diện không chạy được.

   Đã trả giá thật: lượt 10:10Z ngày 29/08. Tám bước
   claude-code-action trong workflow đều có dòng ấy; bước thứ chín
   tôi vừa thêm thì không, và nó ngã sau 15 giây vì hết quota, kéo
   theo cả pipeline. Tám lần đúng không ngăn được lần thứ chín —
   nên luật này phải là phép canh, không phải thói quen. */
{
  const wf = ".github/workflows/refresh-data.yml";
  if (existsSync(join(ROOT, wf))) {
    const L = (await doc(wf)).split("\n");
    /* Gom theo KHỐI bước, không quét dòng rời: `uses` có thể đứng
       trước hay sau `continue-on-error` trong cùng một bước. */
    const thieu = [];
    let khoi = [], tenKhoi = null;
    const xet = () => {
      if (!tenKhoi) return;
      const t = khoi.join("\n");
      if (/uses:\s*anthropics\/claude-code-action/.test(t) &&
          !/continue-on-error:\s*true/.test(t)) thieu.push(tenKhoi);
    };
    for (const l of L) {
      const m = l.match(/^      - name:\s*(.+?)\s*$/);
      if (m) { xet(); tenKhoi = m[1]; khoi = []; continue; }
      if (tenKhoi) khoi.push(l);
    }
    xet();
    for (const t of thieu)
      bao(`bước "${t}" gọi claude-code-action nhưng THIẾU continue-on-error: true —\n` +
          `        model hỏng vì hết quota sẽ làm đỏ cả job và bỏ luôn bước deploy.`);
  }
}

/* ── PHÉP: ĐƯỜNG ỐNG LÀM ĐIỀU KIỆN PHẢI CÓ pipefail ────
   GitHub chạy `run:` không khai `shell:` bằng `bash -e {0}` — KHÔNG
   có pipefail (phải khai `shell: bash` mới có). Nên trong

       if node … cong … 2>&1 | tee "$LOG"; then

   mã thoát lấy của `tee`, luôn bằng 0, và nhánh THEN luôn chạy.
   Cổng chặn in "NHẬN" kể cả khi phép đo bên trong vừa thoát 1.

   Đây không phải lo xa. Lượt 02/09 11:24: factory/tien-hoa.jsonl ghi
   `ho-bo 16/16→15/16 tra-lai`, còn chú giải của CHÍNH lượt đó ghi
   "Vòng tiến hoá Hộ Bộ: NHẬN" — node biết nó trượt, workflow không
   nghe thấy, bản vá lên thẳng site và không hoàn nguyên gì. Cả bảy
   cổng chặn đều dính cùng một dòng, tức là chốt "không được xấu đi"
   — thứ cả vòng tự tiến hoá dựa vào để dám cho model tự gộp — đã là
   trang trí từ đầu.

   Chỉ soi đường ống DÙNG LÀM ĐIỀU KIỆN. Một `| tee` đứng riêng không
   cần pipefail, và bắt cả những chỗ ấy là kêu oan ở mười bảy chỗ vô
   hại. */
{
  const wf = ".github/workflows/refresh-data.yml";
  if (existsSync(join(ROOT, wf))) {
    const L = (await doc(wf)).split("\n");
    /* Khai `defaults.run.shell: bash` ở cấp workflow là đủ cho MỌI
       bước — GitHub đổi sang `bash --noprofile --norc -eo pipefail`.
       Có dòng ấy thì phép này im. */
    const coDefaults = /^defaults:\s*$[\s\S]{0,120}?^\s+shell:\s*bash\s*$/m.test(L.join("\n"));
    /* MỌI `| tee`, không chỉ cái nằm trong `if`. Bản đầu của phép này
       chỉ soi đường ống dùng làm ĐIỀU KIỆN, và loại trừ ấy sai: bước
       `node scripts/pin-snapshot.mjs 2>&1 | tee "$LOG"` không có `if`
       nào, nhưng mã thoát của nó là thứ GitHub dùng để chấm bước
       success hay failure — rồi bước ghi sổ đọc đúng cái đó. Đo hôm
       phát hiện: 18 trên 25 bước dùng `| tee` đang nuốt mã thoát,
       gần như toàn bộ đường lấy và dựng số liệu.

       BỎ DÒNG CHÚ THÍCH trước khi tìm, và tìm đúng CÂU LỆNH chứ không
       tìm chữ. Bản đầu dò `/pipefail/` trên nguyên khối, mà chính khối
       chú thích giải thích lỗi có chữ ấy bốn lần — nên nó luôn thấy
       "có" và chưa bao giờ kêu, kể cả khi tôi cố tình gỡ câu lệnh ra
       để thử. Một phép canh chưa từng thấy mình đỏ thì chưa biết nó
       canh gì. */
    const daBao = new Set();
    for (let i = 0; i < L.length && !coDefaults; i++) {
      /* Bỏ dòng chú thích NGAY Ở KHÂU DÒ, không chỉ lúc kiểm pipefail:
         khối chú thích giải thích lỗi này có chữ `| tee` trong đó, và
         nó tự khớp chính mình rồi in ra một "bước" ở dòng 1. Lần thứ
         năm trong hai ngày một phép đo bị chú thích của nó đánh lừa. */
      if (/^\s*#/.test(L[i]) || !/\|\s*tee\b/.test(L[i])) continue;
      let j = i;
      while (j > 0 && !/^\s+run: \|/.test(L[j])) j--;
      if (daBao.has(j)) continue;
      const than = L.slice(j, i + 1).filter((x) => !/^\s*#/.test(x)).join("\n");
      if (/^\s*set\s+-o\s+pipefail\b/m.test(than)) continue;
      daBao.add(j);
      /* Tên bước cho dễ tìm: ngược lên từ `run:` tới `- name:` ở ĐÚNG
         mức thụt của bước (6 dấu cách). Không chốt mức thì nó vớ phải
         `name:` của cả workflow ở dòng 1 và in ra một cái tên vô nghĩa. */
      let t = j; while (t > 0 && !/^ {6}- name:/.test(L[t])) t--;
      const tenBuoc = t > 0 ? L[t].replace(/^\s*- name:\s*/, "").slice(0, 52) : `dòng ${j + 1}`;
      bao(`bước "${tenBuoc}" dùng \`| tee\` mà khối lệnh\n` +
          `        không có \`set -o pipefail\` — mã thoát lấy của tee (luôn 0), nên script ngã\n` +
          `        mà bước vẫn "success" và sổ nhà máy vẫn ghi ket: ok. Cách gọn nhất là khai\n` +
          `        \`defaults: run: shell: bash\` một lần ở đầu workflow.`);
    }
  }
}

/* ── kết quả ──────────────────────────────────────── */
console.log(`Cung tìm thấy trên đĩa: ${cung.length} — ${cung.join(", ")}\n`);

if (canhBao.length) {
  console.log("Nhắc:");
  for (const m of canhBao) console.log("  · " + m);
  console.log();
}

if (!loi.length) {
  console.log("✓ CLAUDE.md khớp với repo. Không có lệch nào.");
  process.exit(0);
}

console.log(`✗ ${loi.length} chỗ lệch:\n`);
for (const m of loi) console.log("  ✗ " + m);
console.log("\nSửa xong nhớ chạy lại. Mục nào thuộc CLAUDE.md thì xem phần");
console.log('"Khi phát hiện lỗi trong chính file này" để biết cách vá.');
process.exit(1);
