/* ═══════════════════════════════════════════════════════
   THÁI BỘC TỰ · CÔNG TRƯỜNG — thế giới đang xây tới đâu.

   Chạy: npm run congtruong  (hoặc node scripts/build-congtruong.mjs)
   Ghi:  thai-boc-tu/assets/js/v/cong-truong.js

   ── VÌ SAO TÁCH KHỎI build-thaiboc.mjs ────────────────
   Khác nguồn, khác nhịp hỏng. `build-thaiboc.mjs` hỏi DefiLlama về
   TIỀN; file này hỏi GitHub về NGƯỜI ĐANG LÀM. GitHub chạm hạn mức
   thì bảng đoàn tàu vẫn phải cập nhật được, và ngược lại. Gộp một
   node là một nguồn ngã kéo cả hai bảng đứng im.

   ── “REALTIME” Ở ĐÂY NGHĨA LÀ GÌ ──────────────────────
   Nói thẳng để không ai hiểu nhầm: trang này là trang TĨNH trên
   GitHub Pages. Nó không gọi API lúc bạn mở — làm vậy thì mỗi người
   xem đốt hạn mức 60 lượt/giờ của chính IP họ, và trang treo theo
   độ trễ của GitHub.

   Nên “cập nhật liên tục” ở đây = bot chạy 4 lượt/ngày rồi ghi
   xuống file tĩnh, và giao diện LUÔN hiện con số “dữ liệu cũ bao
   nhiêu giờ”. Một trang nói rõ mình cũ 5 giờ thì trung thực hơn hẳn
   một trang tự xưng realtime mà không ai kiểm được.

   ── KHOÁ: DÙNG GITHUB_TOKEN CÓ SẴN, KHÔNG THÊM SECRET ─
   Trong Actions, `GITHUB_TOKEN` được cấp tự động cho mỗi lượt chạy:
   5.000 lượt/giờ, không tốn tiền, KHÔNG phải thêm secret nào vào
   repo. Chạy ở máy mà không có token thì rơi về 60 lượt/giờ — vẫn
   đủ cho một lượt (file này tốn ~32 lượt), chỉ đừng chạy hai lần
   liên tiếp.

   Đây KHÔNG mâu thuẫn với mục "Repo này không dùng ANTHROPIC_API_KEY
   nữa" trong CLAUDE.md: luật đó nói về khoá TÍNH TIỀN THEO TOKEN của
   model. `GITHUB_TOKEN` là khoá đọc kho công khai, do chính Actions
   cấp và hết hạn khi lượt chạy kết thúc.

   ── VÌ SAO ĐỌC COMMIT CHỨ KHÔNG ĐỌC “TRẠNG THÁI CHUẨN” ─
   Cám dỗ đầu tiên là đọc trường `status:` trong từng file ERC để
   biết chuẩn nào Draft/Review/Final. Làm vậy tốn một lượt gọi MỖI
   chuẩn — hơn 800 chuẩn là hơn 800 lượt, và phần lớn không đổi gì
   trong nhiều tháng.

   Lịch sử commit của thư mục ERCS trả về đúng thứ cần trong MỘT
   lượt: ai vừa đề xuất gì, ai vừa đẩy chuẩn nào sang Last Call.
   Dòng "Update ERC-5516: Move to last call" nói nhiều hơn một bảng
   trạng thái tĩnh.

   ── NÚT THẮT KHÔNG CÓ KHO LÀ CÓ CHỦ Ý ─────────────────
   Bốn nút — pháp lý on-chain, thực thi vật lý, ai đặt hàm mục tiêu,
   cỗ máy giữ thăng bằng — cố ý để TRỐNG. Không phải quên.

   Đó là phát hiện chính của cả phòng này: những nút có công trường
   đều là nút KỸ THUẬT, còn nút pháp lý, quản trị và vật lý thì
   không có kho mã nào để trỏ tới. Gán bừa một kho cho đủ bộ là xoá
   mất đúng cái mà bảng này tồn tại để cho thấy.

   ── HỎNG THÌ GIỮ BẢN CŨ ───────────────────────────────
   Nguồn LÕI (lịch sử ERC) ngã thì thoát 1 và KHÔNG ghi gì. Từng kho
   lẻ ngã thì chỉ kho đó thiếu, đánh dấu `ok:false` và bày ra.
   ═══════════════════════════════════════════════════════ */

import { writeFile, mkdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const RA = join(ROOT, "thai-boc-tu", "assets", "js", "v", "cong-truong.js");

/* ═══════════ NÚT THẮT NÀO CÓ CÔNG TRƯỜNG NÀO ═══════════
   `nut` khớp với mã trong THIEU của thai-boc-tu/assets/js/toa.js.
   Phần chữ (tên nút, vì sao nó là nút thắt) nằm bên đó; ở đây chỉ
   giữ ánh xạ sang kho mã, vì builder cần nó để đi hỏi.

   Thêm một kho thì hỏi đúng một câu: kho này có thật sự là nơi
   NÚT ĐÓ đang được xây không? Nếu chỉ “liên quan” thì đừng thêm —
   bảng này đo công trường, không đo mức độ liên quan. */
const KHO = [
  { nut: "n01", chu: "smartcontractkit", ten: "chainlink",
    y: "Oracle lớn nhất — đường đưa dữ liệu ngoài vào trong chuỗi." },
  { nut: "n01", chu: "pyth-network", ten: "pyth-crosschain",
    y: "Oracle đẩy giá tần suất cao, mô hình khác Chainlink." },
  { nut: "n02", chu: "UMAprotocol", ten: "protocol",
    y: "Oracle lạc quan: dùng tranh chấp và đặt cọc để trả lời câu hỏi không có sẵn nguồn giá." },
  { nut: "n03", chu: "semaphore-protocol", ten: "semaphore",
    y: "Chứng minh mình thuộc một nhóm mà không lộ mình là ai." },
  { nut: "n03", chu: "AztecProtocol", ten: "aztec-packages",
    y: "Chuỗi riêng tư theo mặc định — trạng thái kín nhưng vẫn kiểm chứng được." },
  { nut: "n04", chu: "eth-infinitism", ten: "account-abstraction",
    y: "ERC-4337: ví thành hợp đồng, bỏ được cụm 12 từ và tiền gas." },
  { nut: "n05", chu: "circlefin", ten: "evm-cctp-contracts",
    y: "Đốt USDC ở chuỗi nguồn, đúc USDC gốc ở chuỗi đích — thay vì tài sản bọc." },
  { nut: "n07", chu: "morpho-org", ten: "morpho-blue",
    y: "Hạ tầng cho vay tách bạch, nền để dựng thị trường tín dụng khác kiểu thế chấp quá mức." },
  { nut: "n08", chu: "ethereum", ten: "ERCs",
    y: "Nơi ERC-8004 (tác tử không cần tin cậy) và các chuẩn tác tử khác được bàn." },
  { nut: "n08", chu: "coinbase", ten: "agentkit",
    y: "Bộ đồ nghề cho tác tử tự giữ ví và tự trả tiền." },
  { nut: "n09", chu: "akash-network", ten: "node",
    y: "Chợ compute phi tập trung — một mảnh của kinh tế máy móc." },
  { nut: "n09", chu: "Layr-Labs", ten: "eigenlayer-contracts",
    y: "Cho thuê lại an ninh kinh tế để dịch vụ máy móc mượn được lòng tin." },
  { nut: "n11", chu: "kleros", ten: "kleros-v2",
    y: "Toà phi tập trung: bồi thẩm đoàn có đặt cọc xử tranh chấp." },
  { nut: "n12", chu: "ethereum", ten: "consensus-specs",
    y: "Đặc tả lớp đồng thuận — chống kiểm duyệt, đa dạng client, lộ trình hậu lượng tử." }
];

/* ═══════════ LẤY NGUỒN ═══════════ */
const TOKEN = process.env.GITHUB_TOKEN || process.env.GH_TOKEN || "";
const nguon = [];
let chamTran = false;

async function gh(nhan, duong, thu) {
  const batBuoc = thu && thu.batBuoc;
  const im = thu && thu.im;
  try {
    const dau = {
      accept: "application/vnd.github+json",
      "x-github-api-version": "2022-11-28",
      "user-agent": "blockchainworld/thai-boc-tu (+https://sunswagz.github.io/blockchainworld/)"
    };
    if (TOKEN) dau.authorization = "Bearer " + TOKEN;
    const r = await fetch("https://api.github.com" + duong, {
      headers: dau, signal: AbortSignal.timeout(45000)
    });
    if (r.status === 403 || r.status === 429) {
      chamTran = true;
      throw new Error("chạm hạn mức GitHub (" + r.status + ")");
    }
    if (!r.ok) throw new Error("HTTP " + r.status);
    const j = await r.json();
    if (!im) { nguon.push({ nhan, ok: true }); console.log("  ✓ " + nhan); }
    return j;
  } catch (e) {
    if (!im) { nguon.push({ nhan, ok: false }); console.error("  ✗ " + nhan + " — " + e.message); }
    if (batBuoc) {
      console.error("\nNguồn LÕI ngã. Không ghi gì, giữ nguyên bản cũ trên site.");
      process.exit(1);
    }
    return null;
  }
}

console.log("Thái Bộc Tự · Công Trường — hỏi GitHub" +
  (TOKEN ? " (có token, 5.000 lượt/giờ)" : " (KHÔNG token, 60 lượt/giờ)") + ":");

/* ── kỹ sư vừa đề xuất gì ── */
const ercCommit = await gh("lịch sử đề xuất ERC",
  "/repos/ethereum/ERCs/commits?path=ERCS&per_page=40", { batBuoc: true });
const eipCommit = await gh("lịch sử đề xuất EIP",
  "/repos/ethereum/EIPs/commits?path=EIPS&per_page=25");

/* ── từng công trường ── */
const kho = [];
for (const k of KHO) {
  const duong = "/repos/" + k.chu + "/" + k.ten;
  const r = await gh("kho " + k.chu + "/" + k.ten, duong, { im: true });
  if (!r) { kho.push({ ...k, ok: false }); continue; }
  const c = await gh("commit " + k.ten, duong + "/commits?per_page=1", { im: true });
  const c0 = Array.isArray(c) && c[0] ? c[0] : null;
  kho.push({
    nut: k.nut, chu: k.chu, ten: k.ten, y: k.y, ok: true,
    sao: r.stargazers_count,
    mo: r.description || null,
    ngonNgu: r.language || null,
    viecMo: r.open_issues_count,
    day: r.pushed_at || null,
    commit: c0
      ? {
          ngay: c0.commit && c0.commit.author ? c0.commit.author.date : null,
          thongDiep: c0.commit ? String(c0.commit.message || "").split("\n")[0].slice(0, 150) : null
        }
      : null
  });
}
const soNga = kho.filter((k) => !k.ok).length;
nguon.push({ nhan: KHO.length + " kho mã theo dõi", ok: soNga === 0 });
console.log((soNga ? "  ✗ " : "  ✓ ") + (KHO.length - soNga) + "/" + KHO.length + " kho lấy được");

/* ═══════════ TÍNH ═══════════ */
const now = new Date();
const NGAY = 86400000;
const tuoiNgay = (iso) => {
  if (!iso) return null;
  const t = new Date(iso).getTime();
  return isFinite(t) ? (now.getTime() - t) / NGAY : null;
};

/* Trạng thái một công trường. Ngưỡng đặt theo nhịp thật của kho mã
   hạ tầng: 30 ngày không ai đụng vào một đặc tả đang sống là bất
   thường; quá 180 ngày thì gần như chắc chắn đã nguội. */
function trangThaiKho(k) {
  if (!k.ok) return "khong-hoi-duoc";
  const d = tuoiNgay((k.commit && k.commit.ngay) || k.day);
  if (d == null) return "khong-ro";
  if (d <= 30) return "dang-xay";
  if (d <= 180) return "cham";
  return "nguoi";
}
for (const k of kho) k.trangThai = trangThaiKho(k);

/* Gộp về từng nút thắt. Nút không có kho nào thì `soKho: 0` — và
   đó là dòng đáng đọc nhất của bảng. */
const maNut = [...new Set(KHO.map((k) => k.nut))];
const nut = maNut.map((ma) => {
  const ds = kho.filter((k) => k.nut === ma);
  const song = ds.filter((k) => k.trangThai === "dang-xay").length;
  const ngay = ds
    .map((k) => (k.commit && k.commit.ngay) || k.day)
    .filter(Boolean)
    .sort()
    .pop() || null;
  return { ma, soKho: ds.length, soDangXay: song, moiNhat: ngay };
});

/* Đề xuất: lọc ra dòng thật sự nói về một chuẩn, bỏ commit sửa
   website/cấu hình — chúng làm nhiễu đúng phần người đọc quan tâm. */
function locDeXuat(ds, kho) {
  if (!Array.isArray(ds)) return [];
  return ds
    .map((c) => ({
      ngay: c.commit && c.commit.author ? c.commit.author.date : null,
      tieuDe: c.commit ? String(c.commit.message || "").split("\n")[0].trim() : "",
      kho
    }))
    .filter((x) => x.ngay && /\b(ERC|EIP)[-\s]?\d+|Add (ERC|EIP)\b/i.test(x.tieuDe))
    .map((x) => ({ ...x, tieuDe: x.tieuDe.replace(/\s*\(#\d+\)\s*$/, "").slice(0, 130) }));
}
const deXuat = [...locDeXuat(ercCommit, "ERC"), ...locDeXuat(eipCommit, "EIP")]
  .sort((a, b) => (a.ngay < b.ngay ? 1 : -1))
  .slice(0, 24);

const soDangXay = kho.filter((k) => k.trangThai === "dang-xay").length;
const soNutTrong = 0; /* tính ở trình duyệt: THIEU có nút nào không nằm trong `nut` */

const data = {
  generatedAt: now.toISOString(),
  date: now.toISOString().slice(0, 10).split("-").reverse().join("/"),
  tomTat: soDangXay + "/" + kho.length + " công trường còn động",
  nguon,
  chamTran,
  tong: {
    soKho: kho.length,
    soDangXay,
    soDeXuat: deXuat.length,
    coToken: !!TOKEN
  },
  nut,
  kho,
  deXuat
};

await mkdir(dirname(RA), { recursive: true });
await writeFile(RA,
  "/* TỰ SINH — đừng sửa tay. Nguồn: scripts/build-congtruong.mjs\n" +
  "   Sinh lúc " + data.generatedAt + " */\n" +
  "window.THAIBOC_CT = " + JSON.stringify(data) + ";\n", "utf8");

console.log("\n✓ Ghi " + RA.replace(ROOT, ".") +
  "  (" + (JSON.stringify(data).length / 1024).toFixed(1) + " KB)");
console.log("  " + soDangXay + "/" + kho.length + " công trường có commit trong 30 ngày");
console.log("  " + deXuat.length + " dòng đề xuất chuẩn gần đây");
if (chamTran) console.log("  ⚠ có lúc chạm hạn mức GitHub — vài kho có thể thiếu");
