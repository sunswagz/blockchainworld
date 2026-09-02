/* ═══════════════════════════════════════════════════════
   CỔNG CHẶN CHO THƯỚC MỚI — xét một bản sửa BỘ THƯỚC.

       node scripts/thuoc-moi.mjs moc --ghi <file>   chụp thước hiện có
       node scripts/thuoc-moi.mjs cong --so <file>   xét bản sửa
       node scripts/thuoc-moi.mjs tu-kiem            tự kiểm, không mạng

   ── VÌ SAO CÓ FILE NÀY ────────────────────────────────
   Tám vòng tiến hoá đang chạy đều là vòng SỬA TRANG. Đề bài của
   chúng nói rõ: "Chỉ sửa trong ba file này" — index.html, app.css,
   app.js của đúng một cung. `scripts/tien-hoa.mjs`, nơi các thước
   sống, KHÔNG nằm trong ba file đó.

   Nghĩa là hệ này tối ưu được theo một cái thước cố định, nhưng
   không tự nới được cái thước ấy. Đó không phải giới hạn của model —
   đó là một RANH GIỚI QUYỀN, và nó được dựng có lý do: một cái máy
   vừa bị chấm vừa được sửa thước chấm mình thì con số nó khoe không
   còn nghĩa gì.

   Nhưng cái giá của ranh giới ấy đo được, và đã tới lúc trả:

     · 22 lượt tiến hoá liên tiếp (30/08 → 02/09) ghi "16/16 → 16/16"
     · `factory/kho-da-dung.json` đứng im từ 28/08 — lần cuối có
       NGƯỜI dịch skill thành thước
     · phiếu toàn thành đọc 198/198, tròn, và tròn vì thước hết chỗ
       đo chứ không phải vì trang đã tốt

   Thêm ĐÚNG MỘT thước bằng tay ngày 02/09 (`mot-main`) bắt ngay được
   `kinh-thanh` thiếu thẻ <main> — thiếu từ đầu, không ai báo. Nút
   thắt nằm ở bộ thước, không nằm ở model.

   ── CỔNG NÀY LÀM GÌ ───────────────────────────────────
   Nới ranh giới thì phải có cổng khác, vì chốt cũ không dùng được ở
   đây. Chốt cũ là "điểm không được tụt" — mà thêm một thước thì điểm
   tụt là chuyện ĐÚNG. Ngược lại, gỡ một thước đang trượt làm điểm
   ĐẸP LÊN, và chốt cũ khen nó.

   Sáu phép dưới đây hỏi một câu khác: bản sửa này có làm bộ thước
   NHÌN ĐƯỢC NHIỀU HƠN không.

     1. nạp được          bộ thước ngã thì mọi phiếu sau là rác
     2. không mất thước    mọi mã cũ phải còn — chặn xoá và đổi tên
     3. đúng một thước mới  một bước, như mọi vòng khác
     4. thước mới phải BẮT ĐƯỢC gì   trượt ở ít nhất một trang
     5. không lật thước cũ  không mã cũ nào đổi kết luận ở bất kỳ
                            trang nào, cả hai chiều
     6. tất định           đo hai lần ra một kết quả

   Phép 4 và phép 5 là phần đáng kể, và cả hai đều đến từ vết xe đã
   đổ trong repo này:

   · Phép 4 — repo tự ghi trong `tien-hoa.mjs`: "thêm một thước xanh
     sẵn khắp nơi là thêm một dấu ✓ không canh gì". Một thước đạt ở
     cả mười ba trang ngay ngày đầu thì hoặc nó đo thứ không ai sai,
     hoặc regex của nó hỏng. Thước SVG từng xanh giả ở cả mười hai
     cung suốt nhiều tuần vì một ký tự lọt vào regex.

   · Phép 5 chặn kiểu gian tinh vi nhất, và là kiểu DUY NHẤT mà một
     máy tối ưu điểm sẽ tự tìm ra: đừng sửa trang, hãy nới thước.
     Không có phép này thì `soCo <= 12` thành `soCo <= 40` là mọi
     cung lên điểm, cổng cũ khen "↑ tiến", và cả hệ đo tự tan trong
     im lặng. Trang KHÔNG đổi trong lượt này, nên mọi thay đổi kết
     luận đều là do bộ thước — không có nhánh nào khác để đổ.

   Nói thẳng cái nó KHÔNG khoá: thước mới có ĐÁNG đo hay không.
   Một thước đếm số dấu phẩy trong HTML sẽ qua sạch sáu phép. Cổng
   này chỉ khoá được "thước này có thật và có nhìn thấy gì không";
   "có đáng nhìn không" vẫn là câu của người đọc diff.
   ═══════════════════════════════════════════════════════ */

import { execFileSync } from "node:child_process";
import { writeFileSync, readFileSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { join, dirname } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { dsTrang } from "./vong-xoay.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const LENH = process.argv[2];
const co_ = (ten) => {
  const i = process.argv.indexOf("--" + ten);
  return i === -1 || i === process.argv.length - 1 ? null : process.argv[i + 1];
};

/* Cùng trần giờ với phieu-toan-thanh.mjs, cùng lý do: một trang treo
   thì mất đúng trang đó chứ không mất cả bảng. */
const HAN_MS = 150000;

/* Chấm cả mười ba trang, trả về { trang: { <ten>: { <ma>: dat } } }.
   `dat` giữ nguyên ba trạng thái true / false / null — null là KHÔNG
   ĐO ĐƯỢC, và gộp nó vào false ở đây sẽ làm phép 5 báo oan mỗi khi
   một trang đổi từ "không có ô nhập nào" sang "có". */
function chamHet() {
  const trang = {};
  const nga = [];
  for (const c of dsTrang(ROOT)) {
    const tam = join(tmpdir(), "thuoc-moi-" + c + "-" + process.pid + ".json");
    try {
      execFileSync(process.execPath,
        [join(ROOT, "scripts", "tien-hoa.mjs"), "do", c, "--ghi", tam],
        { cwd: ROOT, encoding: "utf8", timeout: HAN_MS, stdio: "ignore" });
      const p = JSON.parse(readFileSync(tam, "utf8"));
      const m = {};
      for (const d of p.diem || []) m[d.ma] = d.dat;
      trang[c] = m;
    } catch (e) {
      nga.push(c + ": " + String(e.message || e).slice(0, 100));
    } finally {
      try { rmSync(tam, { force: true }); } catch { /* rác tạm */ }
    }
  }
  return { trang, nga };
}

const maCua = (t) => [...new Set(Object.values(t).flatMap((m) => Object.keys(m)))].sort();

/* ═══════════ chụp mốc ═══════════ */
if (LENH === "moc") {
  const ra = co_("ghi");
  if (!ra) { console.error("Thiếu --ghi <file>."); process.exit(2); }
  const { trang, nga } = chamHet();
  /* Ngã lúc CHỤP MỐC là chặn ngay, không phải cảnh báo. Mốc thiếu một
     trang thì phép 5 không soi được trang ấy, và bản sửa nào làm hỏng
     đúng trang đó sẽ đi lọt — một cổng chặn có lỗ thầm lặng thì tệ hơn
     không có cổng, vì người ta tin nó. */
  if (nga.length) {
    console.error("✗ Không chấm được " + nga.length + " trang, mốc không dùng được:\n" +
      nga.map((x) => "   " + x).join("\n"));
    process.exit(1);
  }
  mkdirSync(dirname(ra), { recursive: true });
  writeFileSync(ra, JSON.stringify({ luc: new Date().toISOString(), trang }, null, 1) + "\n", "utf8");
  const ma = maCua(trang);
  console.log(`Mốc: ${ma.length} thước × ${Object.keys(trang).length} trang → ${ra}`);
  process.exit(0);
}

/* ═══════════ cổng chặn ═══════════ */
if (LENH === "cong") {
  const moc = co_("so");
  if (!moc || !existsSync(moc)) { console.error("Thiếu --so <file mốc>."); process.exit(2); }
  const cu = JSON.parse(readFileSync(moc, "utf8"));
  const loi = [];

  /* ── 1. nạp được ──────────────────────────────────────── */
  try {
    execFileSync(process.execPath, ["--check", join(ROOT, "scripts", "tien-hoa.mjs")], { stdio: "pipe" });
  } catch (e) {
    console.log("✗ CỔNG THƯỚC — bộ thước không nạp được:\n   " +
      String(e.stderr || e).slice(0, 300));
    process.exit(1);
  }

  const { trang: moi, nga } = chamHet();
  for (const x of nga) loi.push("không chấm được " + x);

  const maCu = maCua(cu.trang);
  const maMoi = maCua(moi);

  /* ── 2. không mất thước ───────────────────────────────── */
  const mat = maCu.filter((m) => !maMoi.includes(m));
  if (mat.length) loi.push(`MẤT ${mat.length} thước: ${mat.join(", ")} — xoá hoặc đổi tên đều không được`);

  /* ── 3. đúng một thước mới ────────────────────────────── */
  const them = maMoi.filter((m) => !maCu.includes(m));
  if (them.length === 0) loi.push("KHÔNG thêm thước nào — lượt này không có gì để nhận");
  else if (them.length > 1) loi.push(`thêm ${them.length} thước cùng lúc (${them.join(", ")}) — mỗi lượt MỘT bước`);

  /* ── 4. thước mới phải bắt được gì ────────────────────── */
  for (const m of them) {
    const ketLuan = Object.entries(moi).map(([c, d]) => [c, d[m]]);
    const truot = ketLuan.filter(([, d]) => d === false).map(([c]) => c);
    const doDuoc = ketLuan.filter(([, d]) => d !== null && d !== undefined);
    if (!doDuoc.length) {
      loi.push(`thước "${m}" KHÔNG ĐO ĐƯỢC ở cả ${ketLuan.length} trang — nó chưa đo gì cả`);
    } else if (!truot.length) {
      loi.push(`thước "${m}" đạt ở cả ${doDuoc.length} trang đo được — ` +
        `một thước xanh sẵn khắp nơi là một dấu ✓ không canh gì. ` +
        `Hoặc nó đo thứ không ai sai, hoặc phép dò của nó hỏng.`);
    } else {
      console.log(`  thước mới "${m}" bắt được ${truot.length} trang: ${truot.join(" ")}`);
    }
  }

  /* ── 5. không lật thước cũ ────────────────────────────── */
  const lat = [];
  for (const c of Object.keys(moi)) {
    if (!cu.trang[c]) { loi.push(`trang "${c}" không có trong mốc — chụp lại mốc trước khi xét`); continue; }
    for (const m of maCu) {
      const a = cu.trang[c][m], b = moi[c][m];
      if (a === b) continue;
      lat.push(`${c}/${m}: ${a} → ${b}`);
    }
  }
  if (lat.length) {
    loi.push(`LẬT ${lat.length} kết luận của thước CŨ, mà lượt này không sửa trang nào:\n` +
      lat.slice(0, 8).map((x) => "        " + x).join("\n") +
      (lat.length > 8 ? `\n        … và ${lat.length - 8} chỗ nữa` : "") +
      "\n        false→true là NỚI thước cho dễ đạt; true→false là làm hỏng thước cũ.");
  }

  /* ── 6. tất định ──────────────────────────────────────── */
  const lai = chamHet();
  const khacNhau = [];
  for (const c of Object.keys(moi)) {
    for (const m of Object.keys(moi[c])) {
      if (lai.trang[c] && lai.trang[c][m] !== moi[c][m]) khacNhau.push(`${c}/${m}`);
    }
  }
  if (khacNhau.length)
    loi.push(`KHÔNG TẤT ĐỊNH — đo hai lần khác nhau ở ${khacNhau.length} chỗ: ${khacNhau.slice(0, 5).join(", ")}`);

  const soDat = (t) => Object.values(t).flatMap((m) => Object.values(m)).filter((d) => d === true).length;
  const soThuoc = (t) => Object.values(t).flatMap((m) => Object.values(m)).filter((d) => d !== null && d !== undefined).length;

  if (loi.length) {
    console.log("✗ CỔNG THƯỚC — " + loi.length + " lỗi:\n" + loi.map((x) => "   " + x).join("\n"));
    process.exit(1);
  }
  console.log(`✓ Cổng thước: nhận "${them[0]}" · ` +
    `${maCu.length} → ${maMoi.length} thước · ` +
    `phiếu ${soDat(cu.trang)}/${soThuoc(cu.trang)} → ${soDat(moi)}/${soThuoc(moi)}`);
  process.exit(0);
}

/* ═══════════ tự kiểm ═══════════
   Sáu phép trên KHÔNG chạy được thử bằng tay: mỗi lượt là 13 tiến
   trình con và vài phút. Nên phần quyết định — logic so hai bảng —
   tách khỏi phần đo, và tự kiểm bơm bảng giả vào đúng phần ấy.

   Vì sao bắt buộc phải có: cổng chặn là mã KHÔNG BAO GIỜ chạy đúng
   đường trong lúc mọi thứ lành. Nó chỉ chạy khi có bản sửa xấu, tức
   là đúng lúc không ai ngồi xem. Một cổng chặn hỏng thì im lặng cho
   qua, và ta chỉ biết sau khi đã mất thứ nó phải giữ. */
if (LENH === "tu-kiem") {
  let dat = 0, truot = 0;
  const ca = (ten, that) => { that ? dat++ : (truot++, console.log("  ✗ " + ten)); };

  const goc = { trang: { a: { x: true, y: false }, b: { x: true, y: true } } };

  /* maCua gom mã từ MỌI trang, không chỉ trang đầu — trang đầu có thể
     thiếu một thước ở trạng thái "không đo được". */
  ca("maCua gom đủ mã", JSON.stringify(maCua(goc.trang)) === '["x","y"]');
  ca("maCua gom cả mã chỉ có ở trang sau",
    JSON.stringify(maCua({ a: { x: true }, b: { x: true, z: false } })) === '["x","z"]');

  /* Bảng giả cho từng ca, chạy qua đúng các phép so trong nhánh
     `cong` ở trên — chép logic thì hai bản lệch, nên ở đây chỉ dựng
     dữ liệu và gọi lại chính các phép ấy qua hàm nhỏ dưới. */
  const xet = (moi) => {
    const maCu = maCua(goc.trang), maMoi = maCua(moi);
    const l = [];
    const mat = maCu.filter((m) => !maMoi.includes(m));
    if (mat.length) l.push("mat");
    const them = maMoi.filter((m) => !maCu.includes(m));
    if (them.length === 0) l.push("khong-them");
    else if (them.length > 1) l.push("them-nhieu");
    for (const m of them) {
      const kl = Object.values(moi).map((d) => d[m]);
      const doDuoc = kl.filter((d) => d !== null && d !== undefined);
      if (!doDuoc.length) l.push("khong-do-duoc");
      else if (!kl.some((d) => d === false)) l.push("xanh-san");
    }
    for (const c of Object.keys(moi))
      for (const m of maCu)
        if (goc.trang[c] && goc.trang[c][m] !== moi[c][m]) l.push("lat");
    return l;
  };

  ca("nhận thước mới có bắt được lỗi",
    xet({ a: { x: true, y: false, z: false }, b: { x: true, y: true, z: true } }).length === 0);
  ca("chặn thước mới xanh sẵn mọi trang",
    xet({ a: { x: true, y: false, z: true }, b: { x: true, y: true, z: true } }).includes("xanh-san"));
  ca("chặn thước mới không đo được ở đâu cả",
    xet({ a: { x: true, y: false, z: null }, b: { x: true, y: true, z: null } }).includes("khong-do-duoc"));
  ca("chặn xoá thước cũ",
    xet({ a: { x: true, z: false }, b: { x: true, z: true } }).includes("mat"));
  ca("chặn lượt không thêm gì",
    xet({ a: { x: true, y: false }, b: { x: true, y: true } }).includes("khong-them"));
  ca("chặn thêm hai thước cùng lúc",
    xet({ a: { x: true, y: false, z: false, w: false }, b: { x: true, y: true, z: true, w: true } })
      .includes("them-nhieu"));
  /* Ca quan trọng nhất: NỚI một thước cũ cho dễ đạt. Trang không đổi,
     nên y ở trang a chỉ có thể đi từ false lên true nếu thước bị nới. */
  ca("chặn NỚI thước cũ (false→true)",
    xet({ a: { x: true, y: true, z: false }, b: { x: true, y: true, z: true } }).includes("lat"));
  ca("chặn làm HỎNG thước cũ (true→false)",
    xet({ a: { x: false, y: false, z: false }, b: { x: true, y: true, z: true } }).includes("lat"));
  /* Ba trạng thái phải phân biệt: null KHÔNG phải false. Gộp lại thì
     mỗi trang đổi từ "không có ô nhập nào" sang "có" là bị gọi là lật. */
  ca("null khác false", (null === false) === false);

  console.log(`\n${dat}/${dat + truot} ca đạt`);
  process.exit(truot ? 1 : 0);
}

console.error("Lệnh lạ. Có: moc --ghi <file> · cong --so <file> · tu-kiem");
process.exit(2);
