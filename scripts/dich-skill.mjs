/* ═══════════════════════════════════════════════════════
   Dịch mô tả skill cộng đồng sang tiếng Việt.

   Chạy:  ANTHROPIC_API_KEY=sk-... node scripts/dich-skill.mjs
   Xem trước, không gọi API:  node scripts/dich-skill.mjs --thu

   ── VÌ SAO DỊCH MÁY Ở ĐÂY LÀ HỢP LỆ ──
   Luật của cung này là "đừng bịa mô tả tiếng Việt cho skill chưa
   đọc kỹ". Dịch máy KHÔNG vi phạm luật đó: mô tả gốc nằm ngay
   trong lời nhắc, mô hình dịch cái đang đọc chứ không bịa cái
   không có. Bịa là sinh nội dung không có nguồn; đây là chuyển
   ngữ một nguồn cụ thể.

   ── NHƯNG KHÔNG DỊCH MỤC "VỚI HỆ THỐNG CỦA BẠN" ──
   Mục `ban` của bản dịch tay trả lời "skill này giúp gì cho hệ
   thống bảy cung, CLAUDE.md, hook pre-commit của BẠN". Không có
   thông tin đó trong mô tả gốc, nên máy sinh ra chỉ có thể là
   bịa. Bản máy cố ý THIẾU mục đó. Thiếu thành thật hơn đầy giả.

   ── VÌ SAO BATCH API ──
   Việc này không gấp: 2.859 skill, chạy một lần, xong thì thôi.
   Batch giảm 50% giá và cho tới 100.000 yêu cầu mỗi mẻ. Đo trên
   dữ liệu thật: ~2,66M token vào + 0,54M ra → Haiku 4.5 qua
   Batch khoảng 2,7 USD cho toàn bộ. Rẻ hơn hai lượt quét Đài
   Quan Trắc.

   ── VÌ SAO KHÔNG DÙNG SDK ──
   Cả repo không có node_modules; mọi script chạy bằng fetch trần.
   Batch API là REST đơn giản, kéo thêm một phụ thuộc chỉ để gọi
   ba endpoint là đổi cả tính chất của repo lấy vài dòng tiện.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const KB = join(ROOT, "tang-thu-cac", "assets", "data", "kb");
const DICH = join(ROOT, "tang-thu-cac", "assets", "data", "dich");

const THU = process.argv.includes("--thu");
const KEY = process.env.ANTHROPIC_API_KEY || "";

/* Haiku 4.5 — 1 USD/M vào, 5 USD/M ra, giảm nửa qua Batch.
   Việc ở đây là "đọc một mô tả tiếng Anh rồi viết lại bằng tiếng
   Việt theo bốn ô cố định". Đó là việc của Haiku; dùng Opus cho
   nó là lấy dao mổ trâu — và bài học hôm 14/08 đủ đắt rồi. */
const MODEL = process.env.TT_MODEL || "claude-haiku-4-5";
const GIA = { "claude-haiku-4-5": [1, 5], "claude-sonnet-5": [2, 10] };

const log = (...a) => console.log(...a);

/* ── lời dẫn ────────────────────────────────────────────
   Giữ NGẮN có chủ ý. Ngưỡng lưu đệm của Haiku 4.5 là 4.096
   token — nhồi lời dẫn cho đủ dài để được lưu đệm thì tốn hơn
   là cứ gửi một lời dẫn ngắn 2.859 lần. Đã tính cả hai chiều. */
const DAN = `Bạn dịch mô tả kỹ thuật của Claude Code skill sang tiếng Việt.

Trả về JSON theo đúng lược đồ. Quy tắc:
- tom: MỘT câu, skill này là cái gì. Tiếng Việt tự nhiên, không dịch cứng.
- lam: 2-4 việc cụ thể nó làm được, mỗi việc một mệnh đề ngắn.
- khi: một câu, khi nào Claude tự bật skill này lên.

Giữ nguyên tên riêng và thuật ngữ không có từ tiếng Việt phổ biến
(MCP, hook, commit, API, repo, agent, skill, plugin, token, webhook).
Đừng dịch tên skill. Đừng thêm thông tin không có trong mô tả gốc —
mô tả nghèo thì viết ngắn, đừng đắp thêm cho dài.`;

const LUOC_DO = {
  type: "object",
  properties: {
    tom: { type: "string" },
    lam: { type: "array", items: { type: "string" } },
    khi: { type: "string" }
  },
  required: ["tom", "lam", "khi"],
  additionalProperties: false
};

async function api(duong, tuyChon = {}) {
  const r = await fetch("https://api.anthropic.com" + duong, {
    ...tuyChon,
    headers: {
      "x-api-key": KEY,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
      ...(tuyChon.headers || {})
    }
  });
  if (!r.ok) throw new Error(`HTTP ${r.status} — ${(await r.text()).slice(0, 300)}`);
  return r;
}

/* ── gom skill cần dịch ───────────────────────────────── */
const dataJs = await readFile(join(ROOT, "tang-thu-cac/assets/js/data.js"), "utf8");
const TT = JSON.parse(dataJs.match(/window\.TT_DATA\s*=\s*([\s\S]*);\s*$/)[1]);

/* Hai kho chính chủ đã dịch TAY, đủ bốn mục kể cả "ban".
   Đừng để bản máy đè lên bản tay — bản tay hơn hẳn. */
const DA_DICH_TAY = new Set(["anthropics/skills", "anthropics/claude-plugins-official"]);

/* Bản dịch máy đã có từ lần chạy trước: chạy lại chỉ dịch phần
   mới. Không có phần này thì mỗi lần chạy lại trả tiền lại từ
   đầu cho 2.859 skill không đổi gì. */
const daCo = new Set();
if (existsSync(DICH)) {
  for (const f of await readdir(DICH)) {
    try {
      const j = JSON.parse(await readFile(join(DICH, f), "utf8"));
      for (const id of Object.keys(j.skills || {})) daCo.add(id);
    } catch { /* file hỏng — coi như chưa có, dịch lại */ }
  }
}

const canDich = (TT.skills || []).filter(
  (s) => !DA_DICH_TAY.has(s.kho) && !daCo.has(s.id)
);

log(`Tổng skill        : ${(TT.skills || []).length}`);
log(`Đã dịch tay       : ${(TT.skills || []).filter((s) => DA_DICH_TAY.has(s.kho)).length}`);
log(`Đã dịch máy trước : ${daCo.size}`);
log(`CẦN DỊCH LẦN NÀY  : ${canDich.length}`);

if (!canDich.length) { log("\nKhông có gì để dịch."); process.exit(0); }

/* ── ước giá trước khi tiêu ─────────────────────────────
   In ra TRƯỚC khi gọi, kể cả khi không ở chế độ thử: tiêu tiền
   của người khác thì phải nói trước bao nhiêu. */
const tokDan = Math.round(DAN.length / 3.5);
let tokVao = 0;
for (const s of canDich) tokVao += tokDan + Math.round(((s.ten || "") + (s.moTa || "")).length / 3.5) + 40;
const tokRa = canDich.length * 190;
const [gv, gr] = GIA[MODEL] || GIA["claude-haiku-4-5"];
const tien = ((tokVao / 1e6) * gv + (tokRa / 1e6) * gr) / 2;   /* Batch −50% */
log(`\nMô hình           : ${MODEL}`);
log(`Ước token         : ${(tokVao / 1e6).toFixed(2)}M vào · ${(tokRa / 1e6).toFixed(2)}M ra`);
log(`ƯỚC CHI PHÍ       : ~${tien.toFixed(2)} USD (đã tính giảm 50% của Batch)`);

if (THU) { log("\n--thu: dừng ở đây, không gọi API."); process.exit(0); }
if (!KEY) { console.error("\n✗ Thiếu ANTHROPIC_API_KEY."); process.exit(1); }

/* ── gửi mẻ ─────────────────────────────────────────────
   Batch tối đa 100.000 yêu cầu; 2.859 lọt gọn một mẻ. */
const yeuCau = canDich.map((s) => ({
  custom_id: Buffer.from(s.id).toString("base64url").slice(0, 60),
  params: {
    model: MODEL,
    max_tokens: 600,
    system: DAN,
    output_config: { format: { type: "json_schema", schema: LUOC_DO } },
    messages: [{
      role: "user",
      content: `Tên skill: ${s.ten}\nNhóm: ${s.nhom}\nKho: ${s.kho}\n\nMô tả gốc:\n${s.moTa}`
    }]
  }
}));

/* custom_id phải tra ngược ra id skill; base64url có thể bị cắt
   ở 60 ký tự nên giữ bảng tra thay vì giải mã ngược. */
const tra = new Map(yeuCau.map((y, i) => [y.custom_id, canDich[i].id]));

log(`\nGửi mẻ ${yeuCau.length} yêu cầu…`);
const me = await (await api("/v1/messages/batches", {
  method: "POST", body: JSON.stringify({ requests: yeuCau })
})).json();
log(`  mẻ ${me.id} — ${me.processing_status}`);

/* ── chờ ────────────────────────────────────────────────
   Batch thường xong trong một giờ, tối đa 24. Hỏi mỗi 30 giây. */
let xong = me;
while (xong.processing_status !== "ended") {
  await new Promise((r) => setTimeout(r, 30000));
  xong = await (await api(`/v1/messages/batches/${me.id}`)).json();
  const c = xong.request_counts || {};
  log(`  ${xong.processing_status} — xong ${c.succeeded || 0}, hỏng ${c.errored || 0}, còn ${c.processing || 0}`);
}

/* ── đọc kết quả ────────────────────────────────────────
   Kết quả trả về JSONL và KHÔNG theo thứ tự gửi — phải tra theo
   custom_id, tuyệt đối không theo vị trí. */
const vanBan = await (await api(`/v1/messages/batches/${me.id}/results`)).text();
const theoKho = new Map();
let ok = 0, hong = 0;

for (const dong of vanBan.split("\n")) {
  if (!dong.trim()) continue;
  let r; try { r = JSON.parse(dong); } catch { continue; }
  const id = tra.get(r.custom_id);
  if (!id || r.result?.type !== "succeeded") { hong++; continue; }
  const khoi = (r.result.message.content || []).find((b) => b.type === "text");
  if (!khoi) { hong++; continue; }
  let d; try { d = JSON.parse(khoi.text); } catch { hong++; continue; }
  if (!d.tom || !Array.isArray(d.lam)) { hong++; continue; }

  const kho = id.split("/").slice(0, 2).join("/");
  if (!theoKho.has(kho)) theoKho.set(kho, {});
  /* KHÔNG có `ban` — xem đầu file. */
  theoKho.get(kho)[id] = { tom: d.tom, lam: d.lam.slice(0, 4), khi: d.khi || "", may: 1 };
  ok++;
}

log(`\nDịch được ${ok} · hỏng ${hong}`);

/* ── ghi, gộp với bản cũ ────────────────────────────────
   Gộp chứ không đè: chạy lần sau chỉ dịch phần mới, nếu ghi đè
   thì mọi bản dịch cũ của kho đó biến mất. */
await mkdir(DICH, { recursive: true });
for (const [kho, moi] of theoKho) {
  const ten = kho.replace(/\//g, "__").replace(/[^A-Za-z0-9_.-]/g, "_") + ".json";
  const p = join(DICH, ten);
  let cu = {};
  if (existsSync(p)) { try { cu = JSON.parse(await readFile(p, "utf8")).skills || {}; } catch {} }
  await writeFile(p, JSON.stringify({ kho, luc: new Date().toISOString(), skills: { ...cu, ...moi } }), "utf8");
}
log(`Ghi ${theoKho.size} file vào tang-thu-cac/assets/data/dich/`);
log(`\nChi phí thật xem ở console.anthropic.com — ước ban đầu là ~${tien.toFixed(2)} USD.`);
