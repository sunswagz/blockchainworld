/* ═══════════════════════════════════════════════════════════════
   MẮT XÍCH THIẾU: biến một kỹ năng trên kệ thành một CÂY THƯỚC.

       node scripts/thuoc-moi.mjs de-bai            ra đề cho model
       node scripts/thuoc-moi.mjs cong              cổng chặn
       node scripts/thuoc-moi.mjs cong --cung ho-bo  (chỉ soi một cung, để thử)

   ─── VÌ SAO CẦN, KHI DÂY CHUYỀN ĐÃ GẦN ĐỦ ───

   Dây chuyền hiện có đã dài: `do-kho` mỗi tuần lục 3.696 kỹ năng của
   Tàng Thư Các, bỏ cái đã khai thác, ghi ứng viên vào
   `factory/kho-de-xuat.json`; `themUngVienMoi` ghép hai cái đầu bảng
   vào đuôi danh sách kỹ năng của đề bài; model đọc rồi vá giao diện.

   Thiếu đúng MỘT khâu: không có gì biến một kỹ năng thành THƯỚC.
   Kỹ năng mới chỉ thành ý tưởng vá, còn bộ thước chỉ đổi khi có
   người ngồi sửa `tien-hoa.mjs`. Hệ quả đo được ngày 02/09/2026:
   mười hai cung đều 16/16 hoặc 17/17, 26 lượt tiến hoá gần nhất đều
   là "16/16 → 16/16", và bản ghi cuối tự khai — "mọi thước đã đạt,
   nên vá một chỗ không thước nào đo".

   Vòng lặp biết đi về phía một cái đích. Không khâu nào SINH ra đích
   mới. Đó là khoảng trống kiến trúc, không phải giới hạn của model.

   ─── VÌ SAO CỔNG NÀY PHẢI NGHIÊM HƠN MỌI CỔNG KHÁC ───

   Cho model tự thêm thước là cho nó tự ra đề thi cho chính nó. Ba
   cửa dưới đây là chỗ chặn đúng cái đó, và cửa 4 là cửa quan trọng
   nhất — nó sinh ra từ một tai nạn CÓ THẬT đã ghi trong CLAUDE.md:
   máy thang chữ chèn một khối `:root` mới, phép đo tương phản khi ấy
   chỉ đọc khối `:root` ĐẦU TIÊN nên chuyển sang "không đo được", và
   Đô Sát Viện đi từ 10/11 xuống 10/10 — mẫu số tụt một, ĐIỂM VẪN
   ĐẸP, không dòng nào kêu.

   Nghĩa là: thêm một thước có thể làm một thước khác biến mất trong
   im lặng. Nên cửa 4 đòi phán quyết của MỌI thước cũ, trên MỌI cung,
   phải y nguyên từng cái một.

   ─── ĐIỀU CỔNG NÀY KHÔNG CANH ĐƯỢC, KHAI THẲNG ───

   Nó canh được rằng thước mới CHẠY ĐƯỢC, PHÂN BIỆT ĐƯỢC, và KHÔNG
   phá thước cũ. Nó KHÔNG canh được thước ấy có đo đúng thứ đáng đo
   không — một thước đếm số dấu chấm phẩy cũng qua cả bốn cửa. Chỗ
   ấy là việc của người duyệt, và đó là lý do node này chỉ đề xuất
   một bản vá chứ không tự nhập vào `main`.
   ═══════════════════════════════════════════════════════════════ */

import {
  readFileSync, writeFileSync, existsSync, rmSync,
} from "node:fs";
import { execFileSync } from "node:child_process";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { dsTrang } from "./vong-xoay.mjs";

const NOI = dirname(fileURLToPath(import.meta.url));
const ROOT = join(NOI, "..");
const DO = join(NOI, "tien-hoa.mjs");
const TRUOC = join(NOI, ".thuoc-truoc.mjs"); /* bản HEAD, dựng tạm */

const [, , LENH] = process.argv;
const co_ = (t) => {
  const i = process.argv.indexOf("--" + t);
  return i > 0 ? process.argv[i + 1] : null;
};

/* MƯỜI BA trang, không phải mười hai. Bản đầu tự đếm "thư mục có
   index.html NGAY tại gốc nó" — đúng cho mười hai cung, nhưng Cổng
   Thành nằm ở GỐC repo nên không thư mục nào chứa nó, và nó rơi ra
   ngoài trong im lặng.

   Ở đây cái giá của việc rơi ra là lớn nhất trong repo: đây là cổng
   canh việc SỬA BỘ THƯỚC. Trang nào không có trong `CUNG` thì cửa
   "không lật kết luận thước cũ" không soi nó — nghĩa là một thước mới
   có thể làm hỏng đúng trang gốc mà cổng vẫn xanh, và trang gốc là
   trang đầu tiên người ta thấy.

   `dsTrang` trong scripts/vong-xoay.mjs là chỗ DUY NHẤT trả lời câu
   "trang nào bị thước chấm". `phieu-toan-thanh.mjs` cũng hỏi nó. Hai
   chỗ tự đếm riêng là hai cơ hội sót, và lần trước đã sót thật. */
const CUNG = co_("cung") ? [co_("cung")] : dsTrang(ROOT);

/* Mã của mọi thước, đọc thẳng từ mã nguồn bộ đo. Không giữ bản chép:
   bản chép sẽ lệch, và lệch ở đây nghĩa là cổng canh nhầm tập. */
function maThuoc(nguon) {
  return [...nguon.matchAll(/cham\(\s*"([a-z0-9-]+)"/g)].map((m) => m[1]);
}

function phieu(duongBoDo, cung) {
  const ra = join(NOI, ".phieu-tam.json");
  try {
    execFileSync(process.execPath, [duongBoDo, "do", cung, "--ghi", ra], {
      cwd: ROOT,
      stdio: "ignore",
    });
    const j = JSON.parse(readFileSync(ra, "utf8"));
    rmSync(ra, { force: true });
    return j;
  } catch (e) {
    rmSync(ra, { force: true });
    return { loi: String(e.message || e).slice(0, 120) };
  }
}

function banHead() {
  const noi = execFileSync("git", ["show", "HEAD:scripts/tien-hoa.mjs"], {
    cwd: ROOT,
    encoding: "utf8",
    maxBuffer: 32 * 1024 * 1024,
  });
  writeFileSync(TRUOC, noi, "utf8");
  return noi;
}

/* ── ĐỀ BÀI ─────────────────────────────────────────────────── */

if (LENH === "de-bai") {
  const nguon = readFileSync(DO, "utf8");
  const daCo = maThuoc(nguon);

  let deXuat = [];
  const p = join(ROOT, "factory", "kho-de-xuat.json");
  if (existsSync(p)) {
    try {
      const d = JSON.parse(readFileSync(p, "utf8"));
      deXuat = (d.deXuat || []).slice(0, 6);
    } catch { /* kho hỏng thì đề bài vẫn ra được, chỉ nghèo hơn */ }
  }

  const bang = CUNG.map((c) => {
    const ph = phieu(DO, c);
    return ph.loi ? `${c}: KHÔNG CHẤM ĐƯỢC` : `${c}: ${ph.dat}/${ph.tong}`;
  });

  console.log(`Thêm ĐÚNG MỘT cây thước mới vào scripts/tien-hoa.mjs.

Điểm hiện tại của mười ba trang (mười hai cung + Cổng Thành):
  ${bang.join("\n  ")}

Gần hết đã kịch trần. Thước hiện có (${daCo.length}):
  ${daCo.join(" · ")}

Kỹ năng chưa khai thác, do do-kho lấy về từ Tàng Thư Các:
  ${deXuat.map((x) => "- " + (x.ten || x.id)).join("\n  ") || "- (kho trống)"}

LUẬT:
1. Thêm đúng một lời gọi cham("<mã>", "<tên>", <đạt>, "<chi tiết>")
   trong hàm do_(). Không sửa, không xoá thước nào đang có.
2. Thước phải PHÂN BIỆT được: ít nhất một cung trượt VÀ ít nhất một
   cung đạt. Thước mà mọi cung đều đạt thì không mở dư địa nào;
   thước mà mọi cung đều trượt thì nhiều phần là đo sai.
3. Ưu tiên thước đo ĐỘ PHỦ ("đã làm tới đâu") hơn thước đo LỖI
   ("có gì hỏng không"). Thước lỗi sửa xong là xanh vĩnh viễn rồi
   bão hoà — đúng chỗ hệ này đang mắc. Thước phủ có mẫu số lớn lên
   theo trang nên không bao giờ cạn việc.
4. Ngưỡng phải hiệu chuẩn từ số ĐO ĐƯỢC trên cả 13 trang, và viết rõ
   trong chú thích vì sao là số đó. Đừng bốc số.
5. Cắt chú thích trước khi dò chuỗi thô (dùng biến cssMa có sẵn),
   nếu không thì một câu giải thích bị tính là chính thứ nó tả.

Xong thì cổng chặn tự chạy: node scripts/thuoc-moi.mjs cong`);
  process.exit(0);
}

/* ── CỔNG CHẶN ──────────────────────────────────────────────── */

if (LENH === "cong") {
  const loi = [];
  const nhac = [];

  /* Cửa 1 — chạy được. */
  try {
    execFileSync(process.execPath, ["--check", DO], { stdio: "ignore" });
  } catch {
    console.log("✗ TRẢ LẠI: scripts/tien-hoa.mjs không còn hợp cú pháp.");
    process.exit(1);
  }

  const sau = readFileSync(DO, "utf8");
  const truocNguon = banHead();
  const maTruoc = maThuoc(truocNguon);
  const maSau = maThuoc(sau);

  /* Cửa 2 — thêm đúng một, không xoá cái nào. */
  const mat = maTruoc.filter((m) => !maSau.includes(m));
  const them = maSau.filter((m) => !maTruoc.includes(m));
  if (mat.length) loi.push(`xoá mất thước: ${mat.join(", ")}`);
  if (them.length !== 1) {
    loi.push(
      them.length === 0
        ? "không thêm thước nào"
        : `thêm ${them.length} thước cùng lúc (${them.join(", ")}) — mỗi lượt một cây, để còn biết cây nào gây ra chuyện gì`,
    );
  }

  if (loi.length) {
    rmSync(TRUOC, { force: true });
    console.log("✗ TRẢ LẠI\n  · " + loi.join("\n  · "));
    process.exit(1);
  }

  const maMoi = them[0];
  console.log(`Thước mới: ${maMoi}\nSoi ${CUNG.length} cung...\n`);

  /* Cửa 3 và 4 — chạy cả hai bản trên mọi cung. */
  let sốTrượt = 0;
  let sốĐạt = 0;
  let sốKhôngĐo = 0;
  for (const c of CUNG) {
    const a = phieu(TRUOC, c);
    const b = phieu(DO, c);
    if (a.loi || b.loi) {
      loi.push(`${c}: không chấm được (${a.loi || b.loi})`);
      continue;
    }
    const cuA = new Map(a.diem.map((d) => [d.ma, d.dat]));
    const cuB = new Map(b.diem.map((d) => [d.ma, d.dat]));

    /* Cửa 4: phán quyết của MỌI thước cũ phải y nguyên. */
    for (const m of maTruoc) {
      if (cuA.get(m) !== cuB.get(m)) {
        loi.push(
          `${c}: thước CŨ "${m}" đổi phán quyết (${cuA.get(m)} → ${cuB.get(m)}) — thêm thước không được làm đổi thước khác`,
        );
      }
    }

    const v = cuB.get(maMoi);
    if (v === true) sốĐạt += 1;
    else if (v === false) sốTrượt += 1;
    else sốKhôngĐo += 1;
    console.log(
      `  ${c.padEnd(18)} ${a.dat}/${a.tong} → ${b.dat}/${b.tong}   ${maMoi}: ${v === null || v === undefined ? "không đo được" : v ? "đạt" : "TRƯỢT"}`,
    );
  }
  rmSync(TRUOC, { force: true });

  /* Cửa 3: phải phân biệt được. */
  if (sốTrượt === 0) {
    loi.push(
      `thước mới không cung nào trượt (${sốĐạt} đạt, ${sốKhôngĐo} không đo được) — không mở dư địa nào, vòng tiến hoá vẫn không có việc`,
    );
  }
  if (sốĐạt === 0 && sốTrượt > 0) {
    nhac.push(
      `mọi cung đều trượt (${sốTrượt}/${CUNG.length}) — có thể đúng, nhưng cũng là dấu hiệu quen thuộc của một thước đo sai. Người duyệt xem kỹ chỗ này.`,
    );
  }
  if (sốKhôngĐo > CUNG.length / 2) {
    nhac.push(
      `${sốKhôngĐo}/${CUNG.length} cung "không đo được" — thước gần như không chạm tới ai`,
    );
  }

  console.log();
  for (const n of nhac) console.log("  ⚠ " + n);
  if (loi.length) {
    console.log("\n✗ TRẢ LẠI\n  · " + loi.join("\n  · "));
    process.exit(1);
  }
  console.log(
    `\n✓ NHẬN — ${maMoi}: ${sốTrượt} cung trượt, ${sốĐạt} đạt. Dư địa mở ra ${sốTrượt} lượt tiến hoá.`,
  );

  /* `--ghi <file>`: viết TỜ TRÌNH thay vì để bản vá nằm lại trong cây.

     Đây là chỗ node này khác mọi vòng tiến hoá khác, và khác có chủ ý.
     Vòng giao diện cho model sửa CSS của cung rồi commit thẳng — sai
     thì thấy ngay trên trang. Còn đây model sửa chính CÂY THƯỚC, tức
     là sửa cái định nghĩa "thế nào là tốt hơn". Cổng trên canh được
     thước mới chạy được, phân biệt được, không phá thước cũ — nhưng
     KHÔNG canh được nó có đo đúng thứ đáng đo không.

     Nên bot dừng ở tờ trình. Bước commit của workflow chỉ mang file
     này về, rồi trả `scripts/tien-hoa.mjs` lại nguyên trạng. Người
     đọc tờ trình, thấy đúng thì áp bản vá — một lệnh. Chỗ nghẽn "phải
     tự nghĩ ra hướng" biến mất; chỗ neo "người quyết đâu là tốt hơn"
     vẫn còn. */
  const raTrinh = co_("ghi");
  if (raTrinh) {
    let vaPatch = "";
    try {
      vaPatch = execFileSync("git", ["diff", "--", "scripts/tien-hoa.mjs"], {
        cwd: ROOT, encoding: "utf8", maxBuffer: 16 * 1024 * 1024,
      });
    } catch { vaPatch = "(không lấy được diff)"; }

    const luc = new Date().toISOString();
    writeFileSync(
      join(ROOT, raTrinh),
      `# Tờ trình: thước mới \`${maMoi}\`\n\n` +
        `Sinh lúc ${luc} bởi \`scripts/thuoc-moi.mjs cong\`.\n\n` +
        `Cổng đã kiểm bốn cửa: chạy được · thêm đúng một thước · phân biệt được ` +
        `(${sốTrượt} cung trượt, ${sốĐạt} đạt) · không thước cũ nào đổi phán quyết.\n\n` +
        `**Cổng KHÔNG kiểm được thước này có đo đúng thứ đáng đo không.** ` +
        `Đó là việc của người đọc tờ trình.\n\n` +
        `## Áp bản vá\n\n` +
        "```\ngit apply factory/thuoc-de-xuat.patch\nnpm run kiem\n```\n\n" +
        `## Bản vá\n\n` +
        "```diff\n" + vaPatch + "```\n",
      "utf8",
    );
    console.log(`  tờ trình đã ghi: ${raTrinh}`);
  }
  process.exit(0);
}

console.error(`Lệnh lạ "${LENH || ""}". Có: de-bai · cong`);
process.exit(1);
