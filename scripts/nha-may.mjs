/* ═══════════════════════════════════════════════════════
   LÕI NHÀ MÁY — sổ đăng ký node + sổ ghi lượt chạy.

   Trước file này, "nhịp chạy" của hệ sinh thái nằm rải ở ba chỗ
   không chỗ nào biết chỗ nào:

     · cron trong .github/workflows/*.yml   — chạy lúc mấy giờ
     · thứ tự các bước trong workflow        — chạy cái gì
     · scripts/tuoi-du-lieu.mjs              — bao lâu thì coi là cũ

   Ba chỗ đó phải khớp nhau nhưng không có gì bắt chúng khớp. Đổi
   nhịp một cung là sửa tay cả ba, và sót một chỗ thì hệ quả im
   lặng: bot vẫn chạy, `npm run kiem` vẫn xanh, chỉ có số liệu là
   sai nhịp — đúng loại hỏng mà cả CLAUDE.md sinh ra để chặn.

   Giờ nhịp nằm ở NODE bên dưới, một chỗ. cron trong workflow chỉ
   còn là TRẦN — "cứ 6 giờ ngó một lần xem có gì đến hạn không" —
   còn ĐẾN HẠN HAY CHƯA thì hỏi file này. Hệ quả: đổi nhịp một
   cung là sửa đúng một con số, không đụng YAML.

   ── BA VIỆC FILE NÀY LÀM ──────────────────────────────
     sổ đăng ký   NODE + factory/registry.json   (ai chạy, nhịp nào)
     sổ ghi       factory/state.json             (lượt vừa rồi ra sao)
     chiếu        tao-bien-xu/assets/js/v/van-hanh.js
                  → Tạo Biện Xứ đọc file này để hiện Bảng vận hành

   ── LỆNH ──────────────────────────────────────────────
     node scripts/nha-may.mjs so-dang-ky   sinh lại factory/registry.json
     node scripts/nha-may.mjs den-han      in các node đến hạn (workflow đọc)
     node scripts/nha-may.mjs ghi <ma> <ok|loi|bo-qua> [--giay N] [--ghi "..."]
     node scripts/nha-may.mjs chieu        sinh van-hanh.js cho webapp
     node scripts/nha-may.mjs bang         in bảng cho người đọc

   ── THÊM MỘT NODE ─────────────────────────────────────
   Thêm một khối vào NODE. Nếu node ghi ra file thì MỌI đường dẫn
   nó `writeFile` phải nằm trong `ra`, và `npm run kiem` sẽ bắt
   `ra` phải khớp với `git add` trong workflow lẫn danh sách "File
   do workflow tự sinh" trong CLAUDE.md. Đó là cái bẫy đã cắn hai
   lần (thư mục logo bị sót → ảnh vỡ trên site, không lỗi nào báo).
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { CUNG } from "./cung.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

export const DUONG_SO = "factory/registry.json";
export const DUONG_TRANG_THAI = "factory/state.json";
export const DUONG_CHIEU = "tao-bien-xu/assets/js/v/van-hanh.js";

/* Nhật ký giữ bao nhiêu dòng. 200 ≈ hai tuần ở nhịp 6 giờ với
   9 node — đủ để nhìn ra một node hỏng lặp lại, chưa đủ to để
   file thành gánh nặng (mỗi dòng ~110 byte → ~22 KB). */
const TRAN_NHAT_KY = 200;

/* ═══════════════ SỔ ĐĂNG KÝ ═══════════════

   `tram` là máy nào trong 18 máy của Tạo Biện Xứ chịu trách nhiệm
   cho node này. Không phải trang trí: Bảng vận hành dùng nó để nối
   lượt chạy THẬT vào đúng ô trên Sơ đồ nhà máy, nên mô hình 18 máy
   thôi mô tả một xưởng tưởng tượng.

     che: "script" — chạy bằng node script, xác định, không tốn model
          "claude" — cần phán đoán, gọi model, TỐN TIỀN hoặc TỐN QUOTA
          "tay"    — người chạy ở máy mình (nguồn nằm ngoài repo)
          "theo"   — không có nhịp riêng, chạy khi thứ khác đổi

     nhip: số giờ giữa hai lượt. 0 = không tự chạy bao giờ.
           Đây là SỐ THẬT quyết định node có chạy hay không —
           cron trong workflow chỉ là trần. */
export const NODE = [
  {
    ma: "kinh-thanh", ten: "Số liệu Kinh Thành", cung: "kinh-thanh",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-live.mjs",
    ra: ["kinh-thanh/assets/js/data/live.js",
         "kinh-thanh/assets/js/data/provenance.js",
         "kinh-thanh/assets/data/history.json"],
    y: "TVL và số on-chain 9 quốc gia L1, lấy từ DefiLlama."
  },
  {
    ma: "do-sat-vien", ten: "Bảng xét Đô Sát Viện", cung: "do-sat-vien",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-l2beat.mjs",
    ra: ["do-sat-vien/assets/js/data.js", "do-sat-vien/assets/logos/"],
    y: "Xếp hạng Layer 2 theo L2BEAT, kèm logo tải về."
  },
  {
    ma: "cong-bo", ten: "Đồ nghề Công Bộ", cung: "cong-bo",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-congbo.mjs",
    ra: ["cong-bo/assets/js/data.js", "cong-bo/assets/js/logos.js",
         "cong-bo/assets/js/v/nhat-ky.js", "cong-bo/assets/logos/"],
    y: "Bộ công cụ onchain. Nguồn có một phần là host staging của L2BEAT nên hay ngã."
  },
  {
    ma: "ho-bo", ten: "Dòng tiền Hộ Bộ", cung: "ho-bo",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-hobu.mjs",
    ra: ["ho-bo/assets/js/v/dong-tien.js"],
    y: "Mười một đường DefiLlama công khai (TVL, phí, DEX, stablecoin, vụ mất tiền, " +
       "lợi suất) cộng lịch sử 20 chuỗi, gộp thành một file. KHÔNG gọi AI, không khoá nào."
  },
  {
    ma: "thai-boc-tu", ten: "Đoàn tàu Thái Bộc Tự", cung: "thai-boc-tu",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-thaiboc.mjs",
    ra: ["thai-boc-tu/assets/js/v/doan-tau.js"],
    y: "Ba đường DefiLlama công khai. Không gọi AI, không khoá nào. Việc nặng nhất " +
       "làm ở đây chứ không ở trình duyệt: xếp hơn 8.000 giao thức vào 18 toa và " +
       "dựng quan hệ phụ thuộc oracle từ khai báo của từng cái."
  },
  /* Thái Bộc Tự có HAI node, và tách đôi là có chủ ý — cùng lý do
     cặp node của Đài Quan Trắc, nhưng tách theo NGUỒN chứ không theo
     "cần model hay không":

       thai-boc-tu            DefiLlama → tiền đang nằm ở đâu
       thai-boc-tu-cong-truong  GitHub   → ai đang xây cái gì

     GitHub chạm hạn mức thì bảng đoàn tàu vẫn cập nhật, và DefiLlama
     ngã thì bảng công trường vẫn cập nhật. Gộp một node là để một
     nguồn ngã kéo cả hai bảng đứng im. */
  {
    ma: "thai-boc-tu-cong-truong", ten: "Công trường Thái Bộc Tự", cung: "thai-boc-tu",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-congtruong.mjs",
    ra: ["thai-boc-tu/assets/js/v/cong-truong.js"],
    y: "Hỏi GitHub 14 kho mã và lịch sử đề xuất ERC/EIP: nút thắt nào còn " +
       "người xây, chuẩn nào vừa mở. Dùng GITHUB_TOKEN Actions tự cấp — không " +
       "thêm secret nào, không gọi AI."
  },
  {
    ma: "thai-boc-tu-tin", ten: "Tin tức Thái Bộc Tự", cung: "thai-boc-tu",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-tintuc.mjs",
    ra: ["thai-boc-tu/assets/js/v/tin-tuc.js"],
    y: "Sáu nguồn RSS công khai (CoinDesk, Cointelegraph, Decrypt, Bitcoin Magazine, " +
       "blog Ethereum Foundation, Vitalik). Gắn nhãn toa bằng từ khoá. Ảnh TRỎ THẲNG " +
       "sang CDN toà soạn, không tải về repo. Không khoá nào, không gọi AI."
  },
  {
    ma: "tang-thu-cac", ten: "Kho skill Tàng Thư Các", cung: "tang-thu-cac",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-tangthu.mjs",
    ra: ["tang-thu-cac/assets/js/data.js", "tang-thu-cac/assets/data/"],
    y: "Quét kho Claude Skills trên GitHub. Bước chậm nhất — có lượt 532 giây."
  },
  /* Đài Quan Trắc có HAI node, và cặp này là ví dụ rõ nhất trong repo
     cho luật "đo được thì đừng để model đoán":

       quan-trac-do    ba nguồn số, so ngưỡng số học → miễn phí, xác định
       dai-quan-trac   đọc tin rồi viết một câu    → cần phán đoán, tốn tiền

     Cùng một cung, cùng một câu hỏi ("tình hình có căng không"), nhưng
     phần trả lời được bằng số thì đã tách hẳn ra khỏi phần cần model.
     Nhờ vậy khi lịch quét AI phải tắt vì tiền — đã xảy ra 14/08 — cung
     vẫn còn đèn xanh/vàng/đỏ chạy đều 4 lượt/ngày. */
  {
    ma: "quan-trac-do", ten: "Bảng cảnh báo Quan Trắc", cung: "dai-quan-trac",
    tram: "M12", che: "script", nhip: 6,
    lenh: "node scripts/build-quantrac.mjs",
    ra: ["dai-quan-trac/assets/js/do.js", "dai-quan-trac/assets/js/tq/do.js"],
    y: "Bốn nguồn miễn phí không cần khoá (Yahoo Finance, open.er-api, " +
       "Federal Register, GDELT), so ngưỡng số học rồi tự đặt đèn. KHÔNG gọi AI. " +
       "Đo cho CẢ HAI chủ thể; bảng đo cái gì nằm ở DODAC trong data.js của cung."
  },
  {
    ma: "dai-quan-trac", ten: "Bản quét Đài Quan Trắc", cung: "dai-quan-trac",
    tram: "M07", che: "claude", nhip: 12,
    lenh: "claude-code-action + node scripts/build-scan.mjs",
    ra: ["dai-quan-trac/assets/js/scan.js", "dai-quan-trac/assets/js/tq/scan.js"],
    y: "Việc DUY NHẤT trong xưởng thật sự cần phán đoán: đọc tin 7 ngày " +
       "rồi viết một câu tiếng Việt + phân loại xanh/vàng/đỏ. " +
       "Trả bằng quota gói, không còn khoá API."
  },
  {
    ma: "dong-tin", ten: "Dòng tin Đài Quan Trắc", cung: "dai-quan-trac",
    tram: "M08", che: "claude", nhip: 12,
    lenh: "claude-code-action + node scripts/build-dong-tin.mjs",
    ra: ["dai-quan-trac/assets/js/tin.js"],
    y: "Lấy bài từ 11 nguồn RSS đã chọn tay, chấm điểm liên quan theo " +
       "từng chủ thể, rồi để model viết một đoạn suy luận móc bài vào " +
       "mắt xích nào của mạch truyền dẫn. Khối lượng CHẶN ĐƯỢC: 6 bài " +
       "× 3 chủ thể, tiêu đề và tóm tắt có sẵn nên không phải kéo cả " +
       "trang web vào ngữ cảnh như bản quét."
  },
  {
    ma: "dong-dau", ten: "Đóng dấu bản số liệu",
    tram: "M16", che: "script", nhip: 6,
    lenh: "node scripts/pin-snapshot.mjs",
    ra: [],
    y: "Pin bản số liệu 1,8 KB lên IPFS. Tự bỏ qua nếu sha256 trùng bản trước."
  },
  {
    ma: "bao-cao", ten: "Báo cáo sức khoẻ xưởng",
    tram: "M18", che: "claude", nhip: 24,
    lenh: "anthropics/claude-code-action",
    ra: ["factory/bao-cao.md"],
    y: "Claude Code Action đọc state.json rồi viết vài dòng tiếng Việt: " +
       "node nào đang ốm, ốm từ bao giờ, nên xem chỗ nào trước."
  },
  {
    ma: "hoang-thanh", ten: "Rừng văn hoá Hoàng Thành", cung: "hoang-thanh",
    tram: "M12", che: "tay", nhip: 0,
    lenh: "npm run hoangthanh",
    ra: ["hoang-thanh/assets/js/data.js", "hoang-thanh/assets/js/v/"],
    y: "Nguồn nằm NGOÀI repo (sunswagz-hub/08_world_culture_forest) nên " +
       "Actions không quét được. Chạy tay rồi commit là cách duy nhất."
  },
  {
    ma: "tu-cam-thanh", ten: "Phiên Tử Cấm Thành", cung: "tu-cam-thanh",
    tram: "M12", che: "tay", nhip: 0,
    lenh: "cd tu-cam-thanh-runtime && python -m trader.snapshot",
    ra: ["tu-cam-thanh/assets/js/v/phien.js"],
    y: "Runtime là tiến trình Python chạy dài, cần ANTHROPIC_API_KEY và quyền " +
       "ghi đĩa — Actions không chạy được. Chạy tay rồi commit lát cắt, cùng " +
       "kiểu Hoàng Thành."
  },
  {
    ma: "giao-hang", ten: "Giao hàng lên Pages",
    tram: "M16", che: "theo", nhip: 0,
    lenh: ".github/workflows/deploy-pages.yml",
    ra: [],
    y: "Không có nhịp riêng — chạy khi có commit số liệu. 27/27 lượt thành công."
  }
];

/* ── Ràng buộc kiểm ngay lúc nạp module ───────────────────
   Đặt ở đây chứ không ở kiem-quy-trinh.mjs là có chủ ý: mọi thứ
   dùng sổ đăng ký (workflow, bộ soát, lệnh chiếu) đều phải import
   file này, nên không có đường nào chạy được với một sổ sai. Để
   phép kiểm ở nơi khác thì nó chỉ chặn người nhớ chạy nó. */
{
  const maCung = new Set(CUNG.map((c) => c.ma));
  const thay = new Set();
  for (const n of NODE) {
    if (thay.has(n.ma)) throw new Error(`nha-may: node trùng mã "${n.ma}"`);
    thay.add(n.ma);
    if (n.cung && !maCung.has(n.cung))
      throw new Error(`nha-may: node "${n.ma}" trỏ tới cung không có thật "${n.cung}"`);
    if (!/^M\d\d$/.test(n.tram))
      throw new Error(`nha-may: node "${n.ma}" có trạm sai dạng "${n.tram}"`);
    if (!["script", "claude", "tay", "theo"].includes(n.che))
      throw new Error(`nha-may: node "${n.ma}" có chế độ lạ "${n.che}"`);
  }
}

export const nodeTheoMa = Object.fromEntries(NODE.map((n) => [n.ma, n]));

/* ═══════════════ SỔ GHI ═══════════════ */

const RONG = { generatedAt: null, lan: 0, node: {}, nk: [] };

export async function docTrangThai() {
  const p = join(ROOT, DUONG_TRANG_THAI);
  if (!existsSync(p)) return structuredClone(RONG);
  try {
    const t = JSON.parse(await readFile(p, "utf8"));
    /* File hỏng hoặc thiếu trường thì coi như chưa có, đừng ném:
       nó được đọc trong workflow, và một file JSON lỗi không được
       phép làm chết lượt cập nhật số liệu. */
    return { ...structuredClone(RONG), ...t, node: t.node || {}, nk: t.nk || [] };
  } catch { return structuredClone(RONG); }
}

async function ghiTrangThai(t) {
  await mkdir(join(ROOT, "factory"), { recursive: true });
  await writeFile(join(ROOT, DUONG_TRANG_THAI), JSON.stringify(t, null, 2) + "\n");
}

/* Node đã đổi file nào chưa — hỏi git, đừng tin script tự khai.
   Script có thể ghi ra nội dung y hệt (API trả cùng số), lúc đó
   "chạy xong" là đúng nhưng "có gì mới" là sai. Phân biệt hai
   thứ đó mới thấy được node đang chạy nhưng nguồn đã chết. */
function coDoi(ra) {
  const duong = (ra || []).filter(Boolean);
  if (!duong.length) return false;
  try {
    const o = execFileSync("git", ["status", "--porcelain", "--", ...duong],
      { cwd: ROOT, encoding: "utf8" });
    return o.trim().length > 0;
  } catch { return false; }
}

/* ═══════════════ M02 · MÁY PHÂN LOẠI ═══════════════

   Sổ tới giờ chỉ ghi được `ok` hay `loi`. Mà "ngã" không phải một
   bệnh — nó là bốn bệnh khác nhau, chữa ở bốn chỗ khác nhau:

     nguon-nga   API bên kia timeout / 5xx / đứt kết nối.
                 → không phải lỗi của ta. Chờ, hoặc đổi nguồn.
     han-muc     429, rate limit, quota.
                 → cần khoá riêng hoặc giãn nhịp. KHÔNG phải chờ.
     khoa-sai    401/403.
                 → secret hết hạn. Chờ bao lâu cũng không tự khỏi.
     loi-ma      SyntaxError/TypeError… trong chính script của ta.
                 → phải sửa code, không liên quan gì tới nguồn.

   Phân biệt được bốn thứ đó là khác biệt giữa "Tàng Thư Các đỏ" và
   "Tàng Thư Các chạm hạn mức GitHub, cần PAT" — cái sau nói thẳng
   phải làm gì.

   Khớp chuỗi, không gọi model. Thứ tự quan trọng: hạn mức và khoá
   sai đều là mã 4xx nên phải soi trước `nguon-nga`; lỗi mã soi cuối
   vì tên lỗi JS có thể xuất hiện trong nội dung trang mà nguồn trả về. */
const PHAN_LOAI = [
  ["han-muc",   /\b429\b|rate.?limit|quota|too many requests|hạn mức|secondary rate/i],
  ["khoa-sai",  /\b40[13]\b|unauthorized|forbidden|bad credentials|invalid token/i],
  ["nguon-nga", /\b5\d\d\b|etimedout|enotfound|econnreset|econnrefused|socket hang up|fetch failed|network|timeout/i],
  ["loi-ma",    /\b(syntaxerror|typeerror|referenceerror|rangeerror)\b|cannot read propert/i]
];

export function phanLoai(noiDung) {
  if (!noiDung || !noiDung.trim()) return null;
  /* Chỉ soi phần đuôi: log dài thì phần đầu là những lượt gọi ĐÃ
     THÀNH CÔNG, và một chữ "429" trong đó (đã lùi giờ chờ rồi chạy
     tiếp được) sẽ dán nhãn sai cho cả lượt. Thứ giết nó nằm ở cuối. */
  const duoi = noiDung.slice(-4000);
  for (const [ten, re] of PHAN_LOAI) if (re.test(duoi)) return ten;
  return "chua-ro";
}

export async function ghi(ma, ket, { giay = null, chuThich = "", log = null } = {}) {
  const n = nodeTheoMa[ma];
  if (!n) throw new Error(`nha-may: không có node "${ma}"`);
  if (!["ok", "loi", "bo-qua"].includes(ket))
    throw new Error(`nha-may: kết quả lạ "${ket}" (ok | loi | bo-qua)`);

  const t = await docTrangThai();
  const luc = new Date().toISOString();
  const doi = ket === "ok" ? coDoi(n.ra) : false;

  const truoc = t.node[ma] || {};
  /* Chuỗi lỗi liên tiếp — thứ đáng báo động, khác hẳn một lượt ngã.
     Nguồn mạng ngã một lượt là chuyện thường; ngã bốn lượt liền là
     nguồn đã chết và không ai biết. */
  const chuoiLoi = ket === "loi" ? (truoc.chuoiLoi || 0) + 1 : 0;

  /* Chỉ phân loại lượt NGÃ. Lượt ok mà log có chữ "429" là chuyện
     bình thường — script lùi giờ chờ rồi chạy tiếp được. */
  let vi = null;
  if (ket === "loi" && log) {
    try { vi = phanLoai(readFileSync(join(ROOT, log), "utf8")); }
    catch { try { vi = phanLoai(readFileSync(log, "utf8")); } catch { vi = null; } }
  }

  t.node[ma] = {
    luc, ket, giay, doi, chuThich,
    chuoiLoi, vi,
    lucOk: ket === "ok" ? luc : truoc.lucOk || null,
    lucDoi: doi ? luc : truoc.lucDoi || null
  };
  t.nk.unshift({ luc, ma, ket, giay, doi, chuThich, vi });
  if (t.nk.length > TRAN_NHAT_KY) t.nk.length = TRAN_NHAT_KY;
  t.lan = (t.lan || 0) + 1;
  t.generatedAt = luc;
  await ghiTrangThai(t);
  return t.node[ma];
}

/* ═══════════════ ĐẾN HẠN ═══════════════

   Một node đến hạn khi: có nhịp (>0), và lần chạy được ghi gần
   nhất đã cách đây >= nhịp. Chưa chạy lần nào cũng là đến hạn.

   Trừ hao 10 phút: cron của GitHub trôi vài phút mỗi lượt, nên
   một node nhịp 6 giờ chạy lúc 12:19 sẽ bị coi là "mới 5h58" ở
   lượt 18:17 và bị bỏ qua — rồi lượt sau lại lệch tiếp. Không
   trừ hao thì nhịp 6 giờ trên thực tế thành 12 giờ.

   ── NGÃ THÌ THỬ LẠI NGAY LƯỢT SAU ─────────────────────────
   `ghi` đóng dấu thời gian cho MỌI lượt, kể cả lượt ngã. Nên
   trước đây một node ngã bị coi là "vừa chạy xong" và phải đợi
   hết nhịp mới tới lượt. Hệ quả đo được: bản quét Đài Quan Trắc
   ngã lúc 13:14 ngày 15/08 với nhịp 12 giờ, và lượt thử lại kế
   tiếp rơi vào 06:17 hôm sau — mười bảy tiếng cung ấy đứng im vì
   một lượt hỏng, trong khi nhà máy vẫn thức dậy ba lần ở giữa.

   Xưởng tự chạy thì phải tự lành. Node ngã đến hạn ngay lượt
   thức dậy kế tiếp.

   NHƯNG chỉ ba lượt đầu. Ngã 3 lượt liên tiếp là hỏng thật, không
   phải trục trặc thoáng qua — lúc đó thử lại mỗi 6 giờ chỉ đốt
   quota (`dai-quan-trac` và `bao-cao` đều gọi model) mà không sửa
   được gì. Từ lượt thứ tư trở đi nó quay về nhịp thường, và việc
   đánh thức người thì đã có `canh-bao` lo — nó mở issue đúng ở
   ngưỡng `chuoiLoi >= 2`. */
const TRU_HAO_PHUT = 10;
const THU_LAI_TOI_DA = 3;

export function denHan(trangThai, bayGio = Date.now()) {
  const ra = [];
  for (const n of NODE) {
    if (!n.nhip) continue;
    const t = trangThai.node[n.ma];
    if (!t || !t.luc) { ra.push(n.ma); continue; }
    if (t.ket === "loi" && (t.chuoiLoi || 0) < THU_LAI_TOI_DA) { ra.push(n.ma); continue; }
    const gioQua = (bayGio - new Date(t.luc).getTime()) / 36e5;
    if (gioQua >= n.nhip - TRU_HAO_PHUT / 60) ra.push(n.ma);
  }
  return ra;
}

/* ═══════════════ CHIẾU RA WEBAPP ═══════════════

   Sinh tao-bien-xu/assets/js/v/van-hanh.js — file DUY NHẤT nối
   nhà máy thật với Tạo Biện Xứ.

   Vì sao là file .js trong assets/js/v/ chứ không phải fetch
   factory/state.json: thư mục v/ đã là quy ước sẵn của repo cho
   "nạp khi cần" — build-dist.mjs biết chép nó, sw.js đã có nhánh
   mạng-trước cho nó, và `npm run kiem` đã miễn nó khỏi luật nâng
   CACHE_VERSION. Dùng lại quy ước cũ thì không sinh thêm luật mới;
   fetch một file JSON ở gốc repo thì phải dạy cả ba chỗ đó một
   đường dẫn ngoại lệ. */
/* Node nào chạy trong workflow nào. Để Ở ĐÂY chứ không để trong
   app.js: một cái bảng như thế nằm trong trình duyệt thì không có
   gì bắt nó khớp với .github/workflows/, và nó sẽ lệch âm thầm
   đúng vào ngày người ta cần bấm nút nhất.

   Mặc định là refresh-data.yml; chỉ khai ngoại lệ. `che: "tay"`
   không có workflow nào cả — nút bấm cho nó là lời nói dối. */
const REPO = "sunswagz/blockchainworld";
const WF_MAC_DINH = "refresh-data.yml";
const WF_RIENG = {
  "giao-hang": "deploy-pages.yml"
};

export async function chieu() {
  const t = await docTrangThai();
  const cungTheoMa = Object.fromEntries(CUNG.map((c) => [c.ma, c]));

  const node = NODE.map((n) => {
    const s = t.node[n.ma] || {};
    return {
      ma: n.ma, ten: n.ten, y: n.y, tram: n.tram, che: n.che, nhip: n.nhip,
      lenh: n.lenh, ra: n.ra,
      cung: n.cung || null,
      cungTen: n.cung ? cungTheoMa[n.cung].ten : null,
      wf: n.che === "tay" ? null : (WF_RIENG[n.ma] || WF_MAC_DINH),
      luc: s.luc || null, ket: s.ket || null, giay: s.giay ?? null,
      doi: !!s.doi, chuThich: s.chuThich || "", vi: s.vi || null,
      chuoiLoi: s.chuoiLoi || 0,
      lucOk: s.lucOk || null, lucDoi: s.lucDoi || null
      /* CỐ Ý không chiếu sẵn "đang đến hạn" vào đây, dù tính được.
         Hai lý do, cả hai đều quan trọng:

         1. Nó phụ thuộc ĐỒNG HỒ LÚC CHIẾU. Chiếu nó vào file nghĩa
            là mỗi lượt bot sinh ra một file khác lượt trước dù không
            node nào chạy — và thế là một commit rác mỗi 6 giờ, mãi
            mãi. File này chỉ được đổi khi TRẠNG THÁI đổi.
         2. Trình duyệt tự tính chính xác hơn: nó có `nhip` và `luc`,
            và nó biết BÂY GIỜ là mấy giờ. Chiếu sẵn thì con số đông
            cứng ở thời điểm bot chạy và sai dần suốt 6 tiếng sau. */
    };
  });

  const noiDung =
    "/* SINH TỰ ĐỘNG bởi scripts/nha-may.mjs — ĐỪNG SỬA TAY.\n" +
    "   Đây là bản chiếu của factory/state.json sang thứ trình duyệt đọc được.\n" +
    "   Sửa tay thì lượt bot kế tiếp ghi đè, không báo gì. */\n" +
    "window.VAN_HANH = " + JSON.stringify({
      generatedAt: t.generatedAt, lan: t.lan, repo: REPO,
      node, nk: t.nk.slice(0, 60)
    }, null, 1) + ";\n";

  await mkdir(join(ROOT, "tao-bien-xu/assets/js/v"), { recursive: true });
  await writeFile(join(ROOT, DUONG_CHIEU), noiDung);
  return node.length;
}

/* ═══════════════ MỒI SỔ ═══════════════

   Sổ trống thì Bảng vận hành mở ra chỉ có chữ "chưa chạy lần nào"
   cho tới lượt bot đầu tiên — mà lượt đó có thể là 6 giờ nữa.

   Nhưng sự thật thì đã có sẵn: mỗi file dữ liệu tự sinh đều mang
   dấu `generatedAt` bên trong, và đó CHÍNH LÀ lúc node ấy chạy
   xong lần cuối. `tuoi-du-lieu.mjs` đã đọc dấu đó từ lâu để nhắc
   dữ liệu cũ. Nên mồi sổ không phải bịa số — nó là đọc lại một sự
   thật đang nằm sẵn trong repo mà chưa ai gom về một chỗ.

   Chỉ chạy một lần, lúc dựng. Sau đó `ghi` là nguồn duy nhất. */
export async function moSo() {
  const t = await docTrangThai();
  const RE = /"generatedAt"\s*:\s*"([^"]+)"/;
  let mo = 0;
  for (const n of NODE) {
    if (t.node[n.ma]) continue;
    let luc = null;
    for (const d of n.ra || []) {
      if (d.endsWith("/")) continue;
      const p = join(ROOT, d);
      if (!existsSync(p)) continue;
      const m = RE.exec(await readFile(p, "utf8"));
      if (!m) continue;
      const ms = new Date(m[1]).getTime();
      if (!Number.isFinite(ms)) continue;
      if (!luc || ms > new Date(luc).getTime()) luc = m[1];
    }
    if (!luc) continue;
    const chuThich = "mồi từ dấu generatedAt sẵn có trong file";
    t.node[n.ma] = {
      luc, ket: "ok", giay: null, doi: false, chuThich,
      chuoiLoi: 0, lucOk: luc, lucDoi: luc
    };
    /* Ghi cả vào nhật ký, không chỉ vào trạng thái. Bỏ qua thì Bảng
       vận hành mở ra có 9 thẻ node đầy số nhưng khối "Nhật ký lượt
       chạy" trống trơn — trông như một nửa trang bị hỏng, trong khi
       những lượt ấy có thật và giờ chạy của chúng cũng có thật. */
    t.nk.push({ luc, ma: n.ma, ket: "ok", giay: null, doi: false, chuThich });
    mo++;
  }
  if (mo) {
    t.nk.sort((a, b) => new Date(b.luc) - new Date(a.luc));
    if (t.nk.length > TRAN_NHAT_KY) t.nk.length = TRAN_NHAT_KY;
    t.generatedAt = t.generatedAt || new Date().toISOString();
    await ghiTrangThai(t);
  }
  return mo;
}

export async function soDangKy() {
  const so = {
    generatedAt: new Date().toISOString(),
    ghiChu: "SINH TỰ ĐỘNG từ NODE trong scripts/nha-may.mjs — đừng sửa tay.",
    node: NODE
  };
  await mkdir(join(ROOT, "factory"), { recursive: true });
  await writeFile(join(ROOT, DUONG_SO), JSON.stringify(so, null, 2) + "\n");
  return NODE.length;
}

/* ═══════════════ M15 · MÁY KIỂM ═══════════════

   Sơ đồ xưởng ghi "không có gì ra khỏi xưởng mà chưa qua kiểm".
   Thực tế thì chưa có bước kiểm nào: script chạy xong, `git add`
   gom hết, commit, đẩy lên Pages. Script thoát 0 mà ghi ra file
   cụt là chuyện im lặng hoàn toàn — và nó ĐÃ xảy ra ở dạng khác
   (logos.js trỏ tới ảnh chưa commit).

   Ba phép soi, xếp theo thứ tự bắt được nhiều lỗi nhất:

     1. CÒN ĐỌC ĐƯỢC KHÔNG. JSON thì parse, JS thì cho qua bộ phân
        tích cú pháp (`new Function` chỉ biên dịch, không chạy). Bắt
        được file ghi dở vì tiến trình bị cắt giữa chừng.
     2. CÓ ĐỘT NGỘT TEO KHÔNG. Nhỏ hơn một nửa bản đang nằm trong
        HEAD là dấu hiệu cụt kinh điển: API trả 200 kèm mảng rỗng,
        script vẫn ghi, vẫn thoát 0. Không phép nào khác bắt được.
     3. THƯ MỤC CÓ RỖNG KHÔNG. Thư mục logo rỗng nghĩa là ảnh chưa
        tải về, mà data.js thì đã trỏ tới chúng.

   CHỈ soi file mà LƯỢT NÀY vừa đổi — hỏi git, không soi tất. Soi
   tất thì một file cũ hỏng từ đời nào sẽ bị trả lại mỗi lượt, và
   node "chạy tay" như Hoàng Thành bị phán oan dù nó không hề chạy.

   Hỏng thì TRẢ LẠI BẢN CŨ chứ không bỏ trắng: bản cũ tuy cũ nhưng
   đọc được, còn bản mới thì làm vỡ trang. Rồi ghi node là `loi` —
   node ấy đến hạn sớm, lượt sau tự thử lại. */
const NGUONG_TEO = 0.5;

function batByte(duong) {
  try {
    return execFileSync("git", ["show", `HEAD:${duong}`],
      { cwd: ROOT, maxBuffer: 256 * 1024 * 1024 }).length;
  } catch { return null; }   /* chưa từng có trong HEAD — lần đầu sinh */
}

function soiMotFile(duong) {
  const p = join(ROOT, duong);
  if (!existsSync(p)) return "không thấy file";
  const noi = readFileSync(p, "utf8");
  if (!noi.trim()) return "file rỗng";

  if (duong.endsWith(".json")) {
    try { JSON.parse(noi); } catch (e) { return `JSON hỏng: ${e.message.slice(0, 80)}`; }
  } else if (duong.endsWith(".js")) {
    try { new Function(noi); } catch (e) { return `JS hỏng cú pháp: ${e.message.slice(0, 80)}`; }
  }

  const cu = batByte(duong);
  if (cu && noi.length < cu * NGUONG_TEO)
    return `teo đột ngột: ${noi.length} byte, bản cũ ${cu} byte`;

  return null;
}

export async function kiemHang() {
  /* Chỉ những đường dẫn lượt này vừa đụng. */
  const moiDuong = [];
  for (const n of NODE) for (const d of n.ra || []) moiDuong.push([n, d]);
  if (!moiDuong.length) return { hong: [], soi: 0 };

  let doi = "";
  try {
    doi = execFileSync("git", ["status", "--porcelain", "--",
      ...new Set(moiDuong.map(([, d]) => d))], { cwd: ROOT, encoding: "utf8" });
  } catch { return { hong: [], soi: 0 }; }

  const daDoi = new Set(
    doi.split("\n").map((d) => d.slice(3).trim().replace(/^"|"$/g, "")).filter(Boolean)
  );
  if (!daDoi.size) return { hong: [], soi: 0 };

  const hong = [];
  let soi = 0;
  for (const [n, d] of moiDuong) {
    if (d.endsWith("/")) {
      /* Thư mục: đủ khi có ít nhất một file lượt này vừa ghi. */
      if (![...daDoi].some((x) => x.startsWith(d))) continue;
      soi++;
      const p = join(ROOT, d);
      if (!existsSync(p) || !readdirSync(p).length)
        hong.push({ ma: n.ma, ten: n.ten, duong: d, vi: "thư mục rỗng" });
      continue;
    }
    if (!daDoi.has(d)) continue;
    soi++;
    const vi = soiMotFile(d);
    if (vi) hong.push({ ma: n.ma, ten: n.ten, duong: d, vi });
  }

  for (const h of hong) {
    try {
      execFileSync("git", ["checkout", "HEAD", "--", h.duong], { cwd: ROOT });
      h.traLai = true;
    } catch { h.traLai = false; }
  }

  /* Ghi sau khi trả lại, để `coDoi` nhìn thấy đúng sự thật: file đã
     về bản cũ nên node này KHÔNG mang lại gì mới cho lượt này. */
  for (const ma of new Set(hong.map((h) => h.ma))) {
    const vi = hong.filter((h) => h.ma === ma).map((h) => `${h.duong} — ${h.vi}`).join("; ");
    await ghi(ma, "loi", { chuThich: `kiểm không qua: ${vi}`.slice(0, 300) });
  }

  return { hong, soi };
}

/* ═══════════════ CHẨN ĐOÁN ═══════════════

   Phần "học lại" của xưởng cho tới nay dừng ở chỗ VIẾT: M18 sinh
   factory/bao-cao.md rồi hết. Không có gì đọc nó, không có gì hành
   động theo nó. Một vòng học mà không ai đọc thì chỉ là một cái log
   dài thêm mỗi ngày.

   Chỗ này là nửa còn lại: đọc sổ, quyết định node nào đang ốm, và
   trả về một danh sách máy dùng được. Không gọi model — mọi thứ ở
   đây là so số với ngưỡng, đúng tinh thần build-quantrac.mjs.

   Ba mức, tách ra vì hai mức đầu đáng gọi người dậy còn mức ba thì
   không:

     nga      ngã >= 2 lượt liền. Một lượt ngã là chuyện thường của
              nguồn mạng; hai lượt liền là đã thành nếp.
     tre      quá 2 lần nhịp mà chưa chạy. Nghĩa là workflow không
              gọi tới nó, chứ không phải nó chạy rồi hỏng — hai bệnh
              khác nhau, chữa ở hai chỗ khác nhau.
     dung-im  chạy được, kết quả ok, nhưng nội dung không đổi suốt
              8 lần nhịp. Đây là kiểu hỏng khó thấy nhất: node xanh,
              bảng xanh, mà nguồn phía sau đã chết từ lâu.

   `dung-im` CỐ Ý không tự mở việc. Có dữ liệu đứng im một cách hợp
   lệ (logo không đổi hàng tháng là chuyện bình thường), nên để nó
   gọi người dậy thì chỉ vài hôm là không ai thèm nhìn cảnh báo nữa.
   Nó được liệt kê trong thân việc, để người đọc tự phán. */
const NGUONG_NGA = 2;
const NGUONG_TRE = 2;      /* lần nhịp */
const NGUONG_DUNG_IM = 8;  /* lần nhịp */

export function chanDoan(trangThai, bayGio = Date.now()) {
  const ra = [];
  for (const n of NODE) {
    const s = trangThai.node[n.ma];
    if (!s) continue;
    const gioQua = s.luc ? (bayGio - new Date(s.luc).getTime()) / 36e5 : null;

    if ((s.chuoiLoi || 0) >= NGUONG_NGA) {
      ra.push({ ma: n.ma, ten: n.ten, muc: "nga", nang: true,
        y: `ngã ${s.chuoiLoi} lượt liền` + (s.vi ? `, vì \`${s.vi}\`` : "") +
           `, lượt cuối ${s.luc}` });
      continue;
    }
    if (n.nhip && gioQua != null && gioQua > n.nhip * NGUONG_TRE) {
      ra.push({ ma: n.ma, ten: n.ten, muc: "tre", nang: true,
        y: `trễ ${gioQua.toFixed(1)} giờ, trong khi nhịp là ${n.nhip} giờ` });
      continue;
    }
    if (n.nhip && s.ket === "ok" && s.lucDoi) {
      const gioIm = (bayGio - new Date(s.lucDoi).getTime()) / 36e5;
      if (gioIm > n.nhip * NGUONG_DUNG_IM)
        ra.push({ ma: n.ma, ten: n.ten, muc: "dung-im", nang: false,
          y: `chạy đều nhưng nội dung không đổi ${gioIm.toFixed(0)} giờ` });
    }
  }
  return ra;
}

/* ═══════════════ CẢNH BÁO RA NGOÀI ═══════════════

   Vì sao là GitHub Issue chứ không phải thêm một file trong repo:
   file thì phải có người mở repo ra mới thấy, mà lúc xưởng ốm thì
   thường chẳng ai mở. Issue tự đẩy thông báo về hộp thư.

   MỘT việc duy nhất, sửa đi sửa lại — không mở việc mới mỗi lượt.
   Nhịp 4 lượt/ngày mà mỗi lượt một issue thì một tuần có 28 việc
   nói cùng một chuyện, và người ta tắt thông báo. Nên: có bệnh thì
   mở (hoặc cập nhật thân việc, hoặc mở lại nếu đã đóng); hết bệnh
   thì tự đóng kèm một dòng nói vì sao đóng.

   Thiếu `gh` hoặc thiếu khoá thì IN RA rồi thôi, không ném. Chạy ở
   máy để xem xưởng có ốm không là việc hợp lệ, và nó không được
   phép đòi hỏi thứ chỉ có trên runner. */
const TIEU_DE_VIEC = "Nhà máy: có node đang ốm";

function gh(args) {
  return execFileSync("gh", args, { cwd: ROOT, encoding: "utf8" }).trim();
}

export async function canhBao({ that = true } = {}) {
  const t = await docTrangThai();
  const benh = chanDoan(t);
  const nang = benh.filter((b) => b.nang);

  const than =
    (nang.length
      ? nang.map((b) => `- **${b.ten}** (\`${b.ma}\`) — ${b.y}`).join("\n")
      : "Không có node nào đang ốm.") +
    (benh.some((b) => !b.nang)
      ? "\n\nNgờ, chưa chắc là bệnh:\n" +
        benh.filter((b) => !b.nang).map((b) => `- ${b.ten} (\`${b.ma}\`) — ${b.y}`).join("\n")
      : "") +
    `\n\nSổ ghi: \`factory/state.json\` · Báo cáo: \`factory/bao-cao.md\`` +
    `\nBảng vận hành: https://sunswagz.github.io/blockchainworld/tao-bien-xu/#van-hanh` +
    `\n\n<sub>Việc này do \`nha-may.mjs canh-bao\` giữ, cập nhật mỗi lượt. Đừng sửa tay thân việc.</sub>`;

  if (!that) return { benh, nang, than };

  let ds = [];
  try {
    ds = JSON.parse(gh(["issue", "list", "--state", "all", "--limit", "30",
      "--json", "number,title,state"]));
  } catch {
    console.log("canh-bao: không gọi được `gh` (thiếu lệnh hoặc thiếu khoá) — chỉ in ra.");
    console.log(than);
    return { benh, nang, than };
  }

  const viec = ds.find((v) => v.title === TIEU_DE_VIEC);

  if (nang.length) {
    if (!viec) {
      gh(["issue", "create", "--title", TIEU_DE_VIEC, "--body", than]);
      console.log(`canh-bao: mở việc mới — ${nang.length} node ốm`);
    } else {
      gh(["issue", "edit", String(viec.number), "--body", than]);
      if (viec.state !== "OPEN") gh(["issue", "reopen", String(viec.number)]);
      console.log(`canh-bao: cập nhật việc #${viec.number} — ${nang.length} node ốm`);
    }
  } else if (viec && viec.state === "OPEN") {
    gh(["issue", "close", String(viec.number),
      "--comment", "Hết node ốm — xưởng tự đóng việc này."]);
    console.log(`canh-bao: đóng việc #${viec.number} — không còn node nào ốm`);
  } else {
    console.log("canh-bao: không có node nào ốm, không có việc nào cần mở.");
  }
  return { benh, nang, than };
}

/* ═══════════════ DÒNG LỆNH ═══════════════ */

function doiSo(argv, ten, mac) {
  const i = argv.indexOf("--" + ten);
  return i === -1 || i === argv.length - 1 ? mac : argv[i + 1];
}

/* So bằng đuôi đường dẫn chứ không so `import.meta.url` với
   `file://${argv[1]}` — trên Windows ổ D: thành `file:///D:/…` (ba
   gạch, ổ đĩa hoa) nên phép so chuỗi đó KHÔNG BAO GIỜ đúng, và cả
   khối lệnh dưới đây im lặng không chạy. */
if ((process.argv[1] || "").replace(/\\/g, "/").endsWith("scripts/nha-may.mjs")) {
  const [, , lenh, ...rest] = process.argv;
  const t = await docTrangThai();

  if (lenh === "so-dang-ky") {
    console.log(`Sổ đăng ký: ${await soDangKy()} node → ${DUONG_SO}`);

  } else if (lenh === "den-han") {
    /* In một dòng, phân cách bằng dấu phẩy có bọc — workflow dùng
       `contains(..., ',kinh-thanh,')` nên phải có phẩy hai đầu, không
       thì "cong-bo" khớp nhầm với "cong-bo-x" nếu sau này có node đó. */
    const han = process.env.NHA_MAY_EP === "1" ? NODE.filter((n) => n.nhip).map((n) => n.ma)
                                               : denHan(t);
    console.log("," + han.join(",") + ",");

  } else if (lenh === "ghi") {
    const [ma, ket] = rest;
    const giayRaw = doiSo(rest, "giay", null);
    const kq = await ghi(ma, ket, {
      giay: giayRaw == null ? null : Number(giayRaw),
      chuThich: doiSo(rest, "ghi", ""),
      log: doiSo(rest, "log", null)
    });
    console.log(`${ma}: ${kq.ket}` + (kq.giay != null ? ` ${kq.giay}s` : "") +
      (kq.doi ? " · có thay đổi" : " · không đổi") +
      (kq.vi ? ` · vì: ${kq.vi}` : "") +
      (kq.chuoiLoi > 1 ? ` · NGÃ ${kq.chuoiLoi} LƯỢT LIỀN` : ""));

  } else if (lenh === "mo-so") {
    console.log(`Mồi sổ: ${await moSo()} node lấy được lượt chạy cuối từ file sẵn có`);

  } else if (lenh === "chieu") {
    console.log(`Chiếu: ${await chieu()} node → ${DUONG_CHIEU}`);

  } else if (lenh === "kiem-hang") {
    const { hong, soi } = await kiemHang();
    if (!soi) {
      console.log("Kiểm hàng: lượt này không đổi file nào — không có gì để soi.");
    } else if (!hong.length) {
      console.log(`Kiểm hàng: soi ${soi} đường dẫn, tất cả đạt.`);
    } else {
      console.log(`Kiểm hàng: soi ${soi} đường dẫn, ${hong.length} KHÔNG ĐẠT:`);
      for (const h of hong)
        console.log(`  · ${h.duong} — ${h.vi}` + (h.traLai ? " (đã trả lại bản cũ)" : " (KHÔNG trả lại được)"));
      /* Không thoát 1: hàng hỏng đã bị chặn lại và node đã bị ghi
         `loi`, nên lượt này vẫn nên commit những node lành. Ngã ở
         đây là ném đi cả mẻ vì một món. */
    }

  } else if (lenh === "canh-bao") {
    /* `--thu` để xem thân việc mà không đụng gì trên GitHub. */
    const kq = await canhBao({ that: !rest.includes("--thu") });
    if (rest.includes("--thu")) console.log(kq.than);

  } else if (lenh === "bang") {
    const han = new Set(denHan(t));
    const gio = (l) => l ? ((Date.now() - new Date(l).getTime()) / 36e5).toFixed(1) + "h" : "—";
    console.log(`\nNhà máy — ${t.lan || 0} lượt đã ghi` +
      (t.generatedAt ? `, mới nhất ${t.generatedAt}` : ", chưa chạy lần nào") + "\n");
    console.log("  node            trạm chế độ nhịp  lượt cuối  kết quả   đến hạn");
    for (const n of NODE) {
      const s = t.node[n.ma] || {};
      console.log("  " + n.ma.padEnd(15) + n.tram.padEnd(5) +
        n.che.padEnd(7) + String(n.nhip || "—").padEnd(6) +
        gio(s.luc).padEnd(11) +
        (s.ket || "—").padEnd(10) +
        (n.nhip ? (han.has(n.ma) ? "CÓ" : "chưa") : "—") +
        (s.chuoiLoi > 1 ? `   ← ngã ${s.chuoiLoi} lượt liền` : ""));
    }
    console.log("");

  } else {
    console.log("Lệnh: so-dang-ky | mo-so | den-han | ghi <ma> <ok|loi|bo-qua> | kiem-hang | chieu | canh-bao [--thu] | bang");
    process.exit(1);
  }
}
