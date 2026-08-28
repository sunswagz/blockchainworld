/* ═══════════════════════════════════════════════════════
   PHIẾU ĐO TRI THỨC — và cổng chặn cho vòng tiến hoá.

   Chạy:
     node knowledge-os/do.mjs                  phiếu đo, thuần số học
     node knowledge-os/do.mjs --ghi <file>     cất phiếu làm MỐC GỐC
     node knowledge-os/do.mjs de-bai           ra đề cho model
     node knowledge-os/do.mjs cong --so <file> CỔNG CHẶN: nhận hay trả lại

   ── VÌ SAO CÓ FILE NÀY, KHI ĐÃ CÓ kiem.mjs ────────────
   `kiem.mjs` trả ĐÚNG hoặc SAI. Đó là validator, và validator đủ để
   chặn dữ liệu hỏng — nhưng KHÔNG đủ để tiến hoá.

   Tiến hoá cần một con SỐ so được giữa hai lượt. "Hợp lệ" hôm nay
   giống hệt "hợp lệ" hôm qua, nên một vòng chỉ có validator thì
   không bao giờ biết mình có khá lên không; nó chỉ biết mình chưa
   gãy. Vòng tiến hoá giao diện của repo chạy được đúng vì nó có
   `tien-hoa.mjs do` cho ra 7 thước bằng số TRƯỚC, rồi mới có cổng
   chặn so hai phiếu.

   File này là bản tương ứng cho lớp tri thức. Cùng hình dạng, cùng
   luật: mọi thước phải TỰ ĐO ĐƯỢC. Thứ nào cần người đọc mới chấm
   được thì không thuộc về đây — đưa nó vào là biến phiếu thành ý
   kiến, mà ý kiến thì không so được giữa hai lượt.

   ── THƯỚC ĐO CÁI GÌ, VÀ KHÔNG ĐO CÁI GÌ ───────────────
   Nó đo **độ phủ và độ truy ngược được** của lớp tri thức. Nó KHÔNG
   đo "giải nghĩa hay hay dở" — không có phép toán nào chấm được câu
   đó, và giả vờ chấm được là tự nói dối bằng số.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync, statSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const GOI = dirname(fileURLToPath(import.meta.url));
const REPO = join(GOI, "..");
const json = async (p) => JSON.parse(await readFile(join(GOI, p), "utf8"));
const doc = (p) => readFile(p, "utf8");

const LENH = process.argv[2] && !process.argv[2].startsWith("--") ? process.argv[2] : "do";
const co_ = (ten) => {
  const i = process.argv.indexOf("--" + ten);
  return i === -1 || i === process.argv.length - 1 ? null : process.argv[i + 1];
};

/* ── nạp ─────────────────────────────────────────────── */
const C = await json("data/concepts/core.json");
const R = await json("data/relations/core.json");
const B = await json("data/bridges/repo.json");
const K = await json("data/bridges/capital-os.json");
const CHI = await json("data/chapters/index.json");
const C26 = await json("data/2026/concepts.json");
const R26 = await json("data/2026/relations.json");

/* Mã phòng thật của từng cung — dùng lại BẢNG của kiem.mjs chứ không
   chép. Chép là hai bản sao của cùng một sự thật, và bản thứ hai
   luôn là bản lệch; đó là luật xuyên suốt repo này. */
const { DOC_PHONG, docMaPhong } = await import("./ma-phong.mjs");

/* ── đo ──────────────────────────────────────────────── */
async function do_() {
  const diem = [];
  const cham = (ma, ten, dat, y, n) => diem.push({ ma, ten, dat, y, ...(typeof n === "number" ? { n } : {}) });

  const idSach = new Set(C.map((x) => x.id));
  const id26 = new Set(C26.map((x) => x.id));

  /* 1. PHỦ PHÒNG — mỗi phòng có thật phải ĐƯỢC ÁNH XẠ hoặc ĐƯỢC KHAI
        BỎ QUA kèm lý do. Phòng lửng lơ là chỗ lớp tri thức im lặng
        vắng mặt, và im lặng thì không ai đi tìm. */
  let tongPhong = 0, daPhu = 0;
  const conThieu = [];
  for (const h of B.hall_mappings) {
    const that = await docMaPhong(REPO, h.hall);
    if (!that) continue;                       // không đọc được thì không chấm
    const co = new Set([...(h.rooms || []).map((p) => p.id),
                        ...(h.rooms_skipped || []).map((p) => p.id)]);
    for (const m of that) {
      tongPhong++;
      if (co.has(m)) daPhu++;
      else conThieu.push(h.hall + "/" + m);
    }
  }
  cham("phu-phong", "Mọi phòng có thật đều đã xử",
    tongPhong > 0 && daPhu === tongPhong,
    `${daPhu}/${tongPhong} phòng` + (conThieu.length ? ` · còn: ${conThieu.slice(0, 5).join(", ")}` : ""));

  /* 2. KHÁI NIỆM MỒ CÔI — concept không nối vào quan hệ, cầu nối hay
        chương nào là một mục không bao giờ tới được mắt ai. */
  const dung = new Set();
  for (const x of R) { dung.add(x.from); dung.add(x.to); }
  for (const x of R26) { dung.add(x.from); dung.add(x.to); }
  for (const h of B.hall_mappings) {
    for (const i of h.concepts || []) dung.add(i);
    for (const p of h.rooms || []) for (const i of p.concepts) dung.add(i);
  }
  for (const r of K.roles) for (const i of r.concepts) dung.add(i);
  for (const c of CHI) for (const i of c.concepts || []) dung.add(i);
  const moCoi = C.filter((x) => !dung.has(x.id)).map((x) => x.id);
  cham("mo-coi", "Không khái niệm nào mồ côi", moCoi.length === 0,
    `${moCoi.length}/${C.length} chưa nối` + (moCoi.length ? ` · ${moCoi.slice(0, 5).join(", ")}` : ""));

  /* 3. TRUY NGƯỢC ĐƯỢC — mỗi luận điểm của sách phải chỉ được ra
        chương và trang. Không có locator thì câu đó không kiểm lại
        được, và không kiểm lại được thì nó là ý kiến của người nhập. */
  const sachCanLoc = C.filter((x) => x.stance === "source" || x.stance === "author_claim");
  const thieuLoc = sachCanLoc.filter((x) => !x.source_chapters?.length || !x.source_pages?.length);
  const qhSach = R.filter((x) => x.source_type === "book");
  const qhThieu = qhSach.filter((x) => !x.chapters?.length || !x.pages?.length);
  const tongLoc = sachCanLoc.length + qhSach.length;
  const soThieu = thieuLoc.length + qhThieu.length;
  cham("truy-nguoc", "Luận điểm sách đều tra lại được", soThieu === 0,
    `${tongLoc - soThieu}/${tongLoc} có chương+trang` + (soThieu ? ` · thiếu ${soThieu}` : ""));

  /* 4. LÁT CẮT CÒN TƯƠI — dữ liệu sửa rồi mà chưa sinh lại thì trang
        đang nói theo bản cũ, và không lỗi nào báo.

        Đo bằng NỘI DUNG, không bằng dấu thời gian. Bản đầu so mtime và
        nó SAI theo một kiểu khó thấy: từ khi `sinh.mjs` bỏ qua file
        không đổi, mtime của lát cắt đứng yên mãi, nên mọi lần sửa dữ
        liệu — kể cả lần không ảnh hưởng cung nào — đều làm thước này
        đỏ vĩnh viễn. Một thước không bao giờ xanh lại được thì người
        ta thôi đọc nó.

        `sinh.mjs --kiem` dựng đúng nội dung mà nó SẼ ghi rồi so với
        file trên đĩa. Một nguồn cho hai việc, không có bản chép nào để
        mà lệch. */
  let cuCung = [];
  try {
    cuCung = execFileSync(process.execPath, [join(GOI, "sinh.mjs"), "--kiem"],
      { encoding: "utf8" }).trim().split("\n").filter(Boolean);
  } catch {
    cuCung = ["(không chạy được sinh.mjs --kiem)"];
  }
  cham("lat-cat-tuoi", "Lát cắt khớp với dữ liệu hiện tại", cuCung.length === 0,
    cuCung.length ? `${cuCung.length} cung lệch: ${cuCung.slice(0, 4).join(", ")}` : "cả 11 cung đều khớp");

  /* 5. TRANG CÓ NẠP — sinh ra mà index.html không nạp thì file nằm
        chết trên đĩa; nạp mà chưa sinh thì 404 im lặng. */
  let lech = [];
  for (const h of B.hall_mappings) {
    if (!h.rooms?.length) continue;
    const ra = join(REPO, h.hall, "assets", "js", "v", "tri-thuc.js");
    const trang = join(REPO, h.hall, "index.html");
    const nap = existsSync(trang) && (await doc(trang)).includes("assets/js/v/tri-thuc.js");
    if (existsSync(ra) !== nap) lech.push(h.hall);
  }
  cham("trang-nap", "Cung nào sinh lát cắt thì trang nạp lát cắt", lech.length === 0,
    lech.length ? `${lech.length} cung lệch: ${lech.join(", ")}` : "khớp cả 11 cung");

  /* 6. LỚP 2026 CÓ TỚI ĐƯỢC TRANG — một quan sát 2026 chỉ có ích khi
        nó nối vào một khái niệm đang nằm trong lát cắt của cung nào
        đó. Nối vào chỗ không cung nào dùng là viết cho ngăn kéo. */
  const trongLatCat = new Set();
  for (const h of B.hall_mappings) {
    if (!h.rooms?.length) continue;
    for (const i of h.concepts || []) trongLatCat.add(i);
    for (const p of h.rooms) for (const i of p.concepts) trongLatCat.add(i);
  }
  const c26Cam = new Set(R26.filter((r) => trongLatCat.has(r.to)).map((r) => r.from));
  const c26Treo = [...id26].filter((i) => !c26Cam.has(i));
  cham("lop-2026-toi-trang", "Khái niệm 2026 đều tới được một trang", c26Treo.length === 0,
    `${id26.size - c26Treo.length}/${id26.size} có đường ra trang` +
    (c26Treo.length ? ` · treo: ${c26Treo.slice(0, 4).join(", ")}` : ""));

  /* 7. NGUỒN CỦA LỚP REPO CHỈ ĐƯỢC RA ĐƯỜNG CÓ THẬT — đây là lớp
        DUY NHẤT vòng tiến hoá được phép chạm, nên nó phải là lớp bị
        canh chặt nhất. Một `source_ref` trỏ vào đường không tồn tại
        là một trích dẫn bịa mà vẫn qua được mọi phép kiểm khác. */
  /* Đuôi file xếp DÀI TRƯỚC NGẮN: `js` đứng trước `json` thì
     `ch10-questions.json` khớp thành `ch10-questions.js`, và bộ đo tự
     báo một đường bịa không có thật. Đã cắn ngay lượt chạy đầu tiên. */
  const coDuong = (s) => {
    const ds = String(s || "").match(/[\w./-]+\.(json|mjs|js|py|md)|[a-z-]+\/[a-z0-9/-]+/g) || [];
    return ds.filter((d) => /[/.]/.test(d)).map((d) => d.replace(/^\.\//, ""));
  };
  /* Hai gốc: đường của cung tính từ gốc repo, đường của chính gói tính
     từ knowledge-os/. Chỉ soi một gốc là báo oan nửa số dòng. */
  const coThat = (d) => existsSync(join(REPO, d)) || existsSync(join(GOI, d));
  const bia = [];
  for (const x of [...C26, ...R26]) {
    if (x.source_type === "web") continue;                 // nguồn ngoài, không soi đĩa
    for (const d of coDuong(x.source_ref)) {
      if (!coThat(d)) bia.push((x.id || x.from) + " → " + d);
    }
  }
  cham("nguon-co-that", "Nguồn lớp repo trỏ vào đường có thật", bia.length === 0,
    bia.length ? `${bia.length} đường không tồn tại: ${bia.slice(0, 3).join(", ")}` : "mọi đường đều có trên đĩa");

  /* 8. PHÁN QUYẾT 2026 — sách viết năm 2018. Một khái niệm sách không
        có dòng nào nói "từ đó tới nay chuyện gì đã xảy ra với nó" thì
        lớp 2026 chưa chạm tới nó, và trang chỉ nói được nửa câu.

        VÌ SAO CÓ THƯỚC NÀY, và nói thẳng: bảy thước kia đều hỏi "có
        gì hỏng không". Hỏng thì sửa xong là hết, nên chúng cùng xanh
        và ở nguyên đó. Vòng tiến hoá tri thức đọc `de-bai` từ chính
        phiếu này, nên bảy thước xanh nghĩa là `yeu=0`, nghĩa là model
        KHÔNG BAO GIỜ được gọi. Vòng đã dựng xong mà nằm im — thứ tệ
        hơn một vòng chưa dựng, vì nhìn vào sổ thì nó có vẻ đang chạy.

        Nên thước này hỏi chuyện khác: lớp 2026 đã PHỦ tới đâu. Nó là
        thước duy nhất trong bảy — nay tám — mà làm việc mới thì mới
        nhích lên được.

        MỐC LÀ MỘT NỬA, KHÔNG PHẢI TẤT CẢ, và có lý do. Trong 48 khái
        niệm sách có những cái thuần định nghĩa (`economic_value`,
        `unit_of_account`) mà 2018→2026 thật sự không có tin gì. Đòi
        đủ 48 là dựng một thước không bao giờ xanh nổi, đúng cái hỏng
        mà repo này đã ghi lại nhiều lần. Một nửa thì tới được, và tới
        rồi thì thước đứng lại chứ không đòi thêm.

        KHÔNG có danh sách khai-bỏ-qua ở đây, khác thước "phủ phòng",
        và khác có chủ ý: danh sách ấy sẽ nằm trong lớp 2026 hoặc lớp
        cầu nối — hai lớp model ĐƯỢC PHÉP sửa. Cho model tự khai miễn
        trừ là cho nó tự chấm mình đạt mà không làm gì. */
  const noi26 = new Set();
  for (const r of R26) { noi26.add(r.from); noi26.add(r.to); }
  const daPhanQuyet = C.filter((x) => noi26.has(x.id));
  const MOC = Math.ceil(C.length / 2);
  cham("phan-quyet-2026", "Khái niệm sách có phán quyết 2026",
    daPhanQuyet.length >= MOC,
    `${daPhanQuyet.length}/${C.length} · mốc ${MOC}` +
    (daPhanQuyet.length >= MOC ? "" :
      ` · còn thiếu ${MOC - daPhanQuyet.length}, ví dụ: ` +
      C.filter((x) => !noi26.has(x.id)).slice(0, 3).map((x) => x.id).join(", ")),
    daPhanQuyet.length);

  return {
    luc: new Date().toISOString(),
    dat: diem.filter((d) => d.dat === true).length,
    tong: diem.filter((d) => d.dat !== null).length,
    diem,
    so: {
      concept: C.length, quanHe: R.length, concept26: C26.length, quanHe26: R26.length,
      cauNoi: B.hall_mappings.length, phong: tongPhong,
      phongDaAnhXa: B.hall_mappings.reduce((n, h) => n + (h.rooms?.length || 0), 0)
    }
  };
}

/* ── in ──────────────────────────────────────────────── */
function in_(p) {
  console.log(`Phiếu đo tri thức: ${p.dat}/${p.tong} đạt\n`);
  for (const d of p.diem) {
    console.log(`  ${d.dat === null ? "·" : d.dat ? "✓" : "✗"} ${d.ten.padEnd(38)} ${d.y}`);
  }
  console.log(`\n  ${p.so.concept} khái niệm sách · ${p.so.quanHe} quan hệ · ` +
    `${p.so.concept26} khái niệm 2026 · ${p.so.phongDaAnhXa}/${p.so.phong} phòng đã ánh xạ`);
}

/* ── validator phải qua trước, luôn ──────────────────── */
function kiemQua() {
  try {
    execFileSync(process.execPath, [join(GOI, "kiem.mjs"), "--im"], { stdio: "pipe" });
    return true;
  } catch (e) {
    process.stdout.write(String(e.stdout || "") + String(e.stderr || ""));
    return false;
  }
}

/* ═══════════════ LỆNH ═══════════════ */
if (LENH === "do") {
  const p = await do_();
  const raGhi = co_("ghi");
  if (raGhi) {
    await mkdir(dirname(raGhi), { recursive: true });
    await writeFile(raGhi, JSON.stringify(p, null, 2) + "\n", "utf8");
  }
  in_(p);
  process.exit(0);
}

if (LENH === "de-bai") {
  /* Đề bài cho model. CỐ Ý chỉ đưa những gì nó được phép sửa: lớp
     phân tích (cầu nối) và lớp 2026. Lớp SÁCH không nằm trong đề —
     nó cần người có PDF trong tay, và một model đoán một số trang
     nằm đúng khoảng chương thì qua được mọi phép kiểm mà vẫn là
     trích dẫn bịa. */
  const p = await do_();
  const yeu = p.diem.filter((x) => !x.dat);

  const chuaAnhXa = [];
  for (const h of B.hall_mappings) {
    const that = await docMaPhong(REPO, h.hall);
    if (!that) continue;
    const co = new Set([...(h.rooms || []).map((x) => x.id),
                        ...(h.rooms_skipped || []).map((x) => x.id)]);
    const con = [...that].filter((m) => !co.has(m));
    if (con.length) chuaAnhXa.push({ cung: h.hall, phong: con });
  }

  const de = {
    luc: new Date().toISOString(),
    phieu: p,
    yeu: yeu.map((x) => ({ ma: x.ma, ten: x.ten, y: x.y })),
    chuaAnhXa,
    khaiNiemDungDuoc: C.map((x) => ({ id: x.id, vi: x.label_vi, nghia: x.definition_vi })),
    duocSua: ["knowledge-os/data/bridges/repo.json", "knowledge-os/data/2026/concepts.json",
              "knowledge-os/data/2026/relations.json"],
    camSua: ["knowledge-os/data/concepts/core.json", "knowledge-os/data/relations/core.json",
             "knowledge-os/data/chapters/", "knowledge-os/data/sources/"],
    luat: [
      "Chỉ dùng id khái niệm CÓ SẴN trong khaiNiemDungDuoc — đừng bịa id mới ở lớp sách.",
      "Mã phòng phải nằm trong chuaAnhXa; mã khác là mã không có thật.",
      "Mỗi phòng thêm vào phải có note_vi giải nghĩa, không được chép lại tên phòng.",
      "Phòng không mang nội dung kinh tế thì khai rooms_skipped kèm why_vi, đừng nhồi cho đủ.",
      "Khái niệm 2026 phải có source_ref trỏ vào đường CÓ THẬT trong repo.",
      "Không đụng lớp sách. Không thêm chương/trang cho bất cứ thứ gì."
    ]
  };
  const ra = join(GOI, "data", "de-bai-tien-hoa.json");
  await writeFile(ra, JSON.stringify(de, null, 2) + "\n", "utf8");
  const raFile = co_("ra");
  if (raFile) await writeFile(raFile, `yeu=${yeu.length}\nt0=${Math.floor(Date.now() / 1000)}\n`, { flag: "a" });
  console.log(`::notice::Phiếu đo tri thức: ${p.dat}/${p.tong} đạt · ${yeu.length} điểm yếu` +
    (yeu.length ? ` · trượt: ${yeu.map((x) => x.ten).join(", ")}` : ""));
  process.exit(0);
}

if (LENH === "cong") {
  /* CỔNG CHẶN — ba lớp:
       1. validator phải qua       (dữ liệu không được hỏng)
       2. sinh lại phải chạy được  (lát cắt phải dựng được từ dữ liệu mới)
       3. phiếu không được tụt     (bản vá phải tiến, hoặc ít nhất giữ)

     THỨ TỰ NÀY LÀ BẮT BUỘC, và bản đầu xếp sai. Bản đầu chấm phiếu
     trước rồi mới sinh lại, "cho rẻ trước, đắt sau". Nhưng thước
     `lat-cat-tuoi` hỏi "lát cắt có khớp dữ liệu hiện tại không" — mà
     ngay sau khi model sửa dữ liệu thì câu trả lời LUÔN là không, cho
     tới khi sinh lại. Nên phiếu tụt ở lớp 2 và MỌI bản vá hợp lệ đều
     bị trả lại: một lượt Opus mỗi ngày, vĩnh viễn, không lượt nào
     được nhận, và sổ ghi "loi" mà không ai đọc ra vì sao.

     Đúng cái bẫy đã giết vòng Đài Quan Trắc chín lượt liền: so với một
     trạng thái mà chính các bước trước đó đã làm bẩn.

     Bộ thử `thu-cong.mjs` bắt được nó ngay lượt chạy đầu tiên. Nếu ai
     đổi lại thứ tự "cho rẻ trước", kịch bản 1 sẽ đỏ. */
  if (!kiemQua()) {
    console.log("✗ Cổng chặn: validator KHÔNG qua — trả lại.");
    process.exit(1);
  }


  try {
    execFileSync(process.execPath, [join(GOI, "sinh.mjs")], { stdio: "pipe" });
  } catch (e) {
    console.log("✗ Cổng chặn: sinh lát cắt HỎNG — trả lại.");
    process.stdout.write(String(e.stdout || "").slice(0, 600));
    process.exit(1);
  }

  const p = await do_();
  const soFile = co_("so");
  let goc = null;
  if (soFile && existsSync(soFile)) goc = JSON.parse(await doc(soFile));

  if (goc) {
    if (p.dat < goc.dat) {
      console.log(`✗ Cổng chặn: phiếu TỤT ${goc.dat}/${goc.tong} → ${p.dat}/${p.tong} — trả lại.`);
      for (const d of p.diem) {
        const cu = goc.diem.find((x) => x.ma === d.ma);
        if (cu && cu.dat && !d.dat) console.log(`    vỡ: ${d.ten} — ${d.y}`);
      }
      process.exit(1);
    }

    /* Thước CÓ SỐ thì số cũng không được tụt, không chỉ đếm ô xanh.
       Thước "phán quyết 2026" đi từ 12 lên mốc 24, nên trong suốt quãng
       ấy nó vẫn ĐỎ — và đếm ô xanh thì 12→7 với 12→20 đều là "giữ
       nguyên 7/8", đều qua cổng. Tức là model xoá năm quan hệ rồi thêm
       một cái cũng được nhận, và lượt sau lại được ra đúng đề ấy.
       Thước có số mà cổng không đọc số thì phần thang đo ở giữa hai
       đầu là vô nghĩa. */
    for (const d of p.diem) {
      if (typeof d.n !== "number") continue;
      const cu = goc.diem.find((x) => x.ma === d.ma);
      if (cu && typeof cu.n === "number" && d.n < cu.n) {
        console.log(`✗ Cổng chặn: "${d.ten}" TỤT ${cu.n} → ${d.n} — trả lại.`);
        process.exit(1);
      }
    }
  }

  console.log(`✓ Cổng chặn: tri thức qua cả ba phép` +
    (goc ? `\n  phiếu đo ${goc.dat}/${goc.tong} → ${p.dat}/${p.tong}` +
      (p.dat > goc.dat ? "  = TIẾN" : "  = giữ nguyên") : ""));
  process.exit(0);
}

console.error(`Lệnh lạ "${LENH}". Có: do · de-bai · cong`);
process.exit(2);
