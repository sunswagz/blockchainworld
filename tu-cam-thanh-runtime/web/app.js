/* ═══════════════════════════════════════════════════════════════════
   CLAUDE TRADER — Trung tâm chỉ huy

   Ba tầng: bot ĐANG LÀM GÌ → ĐANG NGHĨ GÌ → ĐANG HỌC GÌ.

   Luật xuyên suốt: ô nào không có nguồn dữ liệu thì gọi `chuaCo()` —
   nói rõ thiếu gì và cần gì để bật. KHÔNG bao giờ điền số cho đầy
   layout. Một bảng điều khiển nói dối tệ hơn hẳn một bảng còn trống:
   ô trống thì người ta đi tìm, số giả thì người ta tin.
   ═══════════════════════════════════════════════════════════════════ */
import { veNen } from "/chart.js";

(() => {
"use strict";

const $ = (s) => document.querySelector(s);
const el = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;" }[c]));
const num = (v, n = 2) => (v == null || Number.isNaN(v) ? "—"
  : Number(v).toLocaleString("vi-VN", { minimumFractionDigits: n, maximumFractionDigits: n }));
const tien = (v) => (v == null ? "—" : (v < 0 ? "−$" : "$") + num(Math.abs(v)));
const dau = (v) => (v > 0 ? "len" : v < 0 ? "xuong" : "");
const pct = (v, n = 2) => (v == null ? "—" : num(v, n) + "%");
const gio = (iso) => { const d = new Date(iso); return isNaN(d) ? "—"
  : String(d.getHours()).padStart(2,"0") + ":" + String(d.getMinutes()).padStart(2,"0"); };
const clamp = (v, a = 0, b = 100) => Math.max(a, Math.min(b, v));

let S = null;     // /api/state
let J = null;     // /api/journal
let C = null;     // /api/candles
let K = null;     // /api/skills
let W = null;     // /api/the-gioi — phái sinh, vĩ mô, tâm lý, tin tức
let khungBieuDo = null;   // khung đang xem trên biểu đồ
const NONG = new Map();

/* ── mảnh dùng lại ─────────────────────────────────────────────── */
const hang = (k, v, cls = "") => `<div class="hang"><span>${esc(k)}</span><b class="${cls}">${esc(v)}</b></div>`;

const oSo = (nhan, gt, cls = "", phu = "") =>
  `<div class="kinh the"><h3>${esc(nhan)}</h3><div class="so-lon ${cls}">${esc(gt)}</div>` +
  (phu ? `<div class="phu-nho">${esc(phu)}</div>` : "") + `</div>`;

function thanhDo(nhan, gtHienThi, phanTram, cls = "", nguongPct = null) {
  const co = phanTram != null;
  return `<div class="do">
    <div class="do-nhan"><span>${esc(nhan)}</span><b class="${co ? cls : "mo"}">${esc(gtHienThi)}</b></div>
    <div class="do-rai ${co ? "" : "chua"}">
      ${co ? `<div class="do-day ${cls}" style="width:${clamp(phanTram)}%"></div>` : ""}
      ${nguongPct != null ? `<div class="do-nguong" style="left:${clamp(nguongPct)}%"></div>` : ""}
    </div></div>`;
}

/** Ô chưa có nguồn. Nói rõ thiếu gì — đây là thứ thay cho số giả. */
function chuaCo(tieu, giaiThich, canGi = []) {
  return `<div class="chua-co">
    <div class="nhan">chưa có nguồn dữ liệu</div>
    <h4>${esc(tieu)}</h4>
    <p>${giaiThich}</p>
    ${canGi.length ? `<ul>${canGi.map((c) => `<li>${c}</li>`).join("")}</ul>` : ""}
  </div>`;
}

/* ── biểu đồ nến ───────────────────────────────────────────────── */
function khoiBieuDo(id, cao = 300) {
  const khung = Object.keys(C?.timeframes || {});
  const tf = khungBieuDo && khung.includes(khungBieuDo) ? khungBieuDo : (C?.primary || khung[0]);
  if (!C?.ready || !khung.length) {
    return `<div class="trong">Chưa có nến — chờ vòng lặp chạy lượt đầu.</div>`;
  }
  return `<div class="kinh the" style="padding:12px 14px">
    <h3>${esc(C.symbol)} · ${esc(tf)}
      <span class="cuoi">${khung.map((k) =>
        `<button class="nut-tf ${k === tf ? "on" : ""}" data-tf="${k}">${k}</button>`).join("")}</span></h3>
    <canvas id="${id}" style="width:100%;height:${cao}px;display:block"></canvas>
    <div class="chu-thich">
      <span><i style="background:var(--cyan)"></i>EMA20</span>
      <span><i style="background:var(--violet)"></i>EMA50</span>
      <span><i style="background:var(--fg-4)"></i>EMA200</span>
      <span><i style="background:var(--green)"></i>hỗ trợ · TP</span>
      <span><i style="background:var(--red)"></i>kháng cự · SL</span>
      <span><i style="background:var(--amber)"></i>vùng vào</span>
      <span class="mo">nến mờ = chưa đóng</span>
    </div></div>`;
}

function veBieuDoVao(id, cao) {
  const cv = el(id);
  if (!cv || !C?.ready) return;
  const khung = Object.keys(C.timeframes);
  const tf = khungBieuDo && khung.includes(khungBieuDo) ? khungBieuDo : C.primary;
  cv.style.height = cao + "px";
  veNen(cv, { nen: C.timeframes[tf], overlay: C.overlay }, { symbol: C.symbol, tf });
  document.querySelectorAll(".nut-tf").forEach((b) => b.onclick = () => { khungBieuDo = b.dataset.tf; ve(); });
}

/* ── thanh bên ba tầng ─────────────────────────────────────────── */
const IC = {
  tongQuan: '<path d="M3 13h8V3H3zM13 21h8V11h-8zM3 21h8v-6H3zM13 9h8V3h-8z"/>',
  viThe:    '<path d="M3 3v18h18"/><path d="M7 15l4-5 3 3 5-7"/>',
  ruiRo:    '<path d="M12 3l8 3.5v5c0 4.6-3.2 8.4-8 9.5-4.8-1.1-8-4.9-8-9.5v-5z"/><path d="M12 9v4M12 16h.01"/>',
  naoTt:    '<circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="9"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3"/>',
  naoAi:    '<path d="M9 3a3 3 0 0 0-3 3v1a3 3 0 0 0 0 6v1a3 3 0 0 0 3 3h1V3zM15 3a3 3 0 0 1 3 3v1a3 3 0 0 1 0 6v1a3 3 0 0 1-3 3h-1V3z"/>',
  trader:   '<circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0 1 12 0"/><circle cx="17" cy="10" r="2.2"/><path d="M15 20a4.5 4.5 0 0 1 6.5-4"/>',
  theGioi:  '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/>',
  chienLuoc:'<path d="M9 3h6l-1 5h4l-8 13 2-8H7z"/>',
  hoc:      '<path d="M12 4 2 9l10 5 10-5z"/><path d="M6 11.5V17c0 1.7 2.7 3 6 3s6-1.3 6-3v-5.5"/>',
  nhatKy:   '<path d="M5 4h11l3 3v13H5z"/><path d="M8 9h8M8 13h8M8 17h5"/>',
  chat:     '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.4A8 8 0 1 1 21 12z"/>',
  bieuDo:   '<path d="M3 21V3M3 21h18"/><rect x="6" y="11" width="3" height="7"/><rect x="11" y="6" width="3" height="12"/><rect x="16" y="9" width="3" height="9"/>',
  triNho:   '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 4v16M15 4v16M4 9h16M4 15h16"/>',
  kyNang:   '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H10v16H5.5A1.5 1.5 0 0 1 4 18.5z"/><path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H14v16h4.5a1.5 1.5 0 0 0 1.5-1.5z"/>',
  huanLuyen:'<path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><circle cx="12" cy="12" r="4"/><path d="M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/>',
  heThong:  '<rect x="3" y="4" width="18" height="7" rx="1.5"/><rect x="3" y="13" width="18" height="7" rx="1.5"/><path d="M7 7.5h.01M7 16.5h.01"/>',
};

const NAV = [
  { tang: 1, ten: "Chỉ huy",     y: "Bot đang làm gì", muc: [
    { id: "tong-quan",       ten: "Tổng quan",        ic: "tongQuan" },
    { id: "thi-truong",      ten: "Thị trường",       ic: "bieuDo" },
    { id: "vi-the",          ten: "Vị thế",           ic: "viThe", dem: () => (S?.account?.positions || []).length },
    { id: "rui-ro",          ten: "Rủi ro",           ic: "ruiRo", dem: () => (S?.risk?.breakers || []).length, nong: true },
    { id: "he-thong",        ten: "Hệ thống",         ic: "heThong",
      dem: () => (TC?.bat ? "tự bật" : null) },
  ]},
  { tang: 2, ten: "Trí tuệ",     y: "Bot đang nghĩ gì", muc: [
    { id: "nao-thi-truong",  ten: "Bộ não thị trường", ic: "naoTt" },
    { id: "nao-claude",      ten: "Bộ não Claude",     ic: "naoAi" },
    // Hai phòng này từng mang nhãn "chưa có" vì không có nguồn. Giờ có rồi —
    // nhãn phải mất theo, nếu không nó thành lời nói dối đúng chiều ngược lại.
    { id: "quan-sat-trader", ten: "Quan sát trader",   ic: "trader",
      dem: () => (W?.phaiSinh?.co ? null : "chưa có") },
    { id: "the-gioi",        ten: "Dòng chảy thế giới",ic: "theGioi",
      dem: () => (W?.suKien?.co ? W.suKien.soBai : "chưa có") },
  ]},
  { tang: 3, ten: "Tiến hoá",    y: "Bot đang học gì", muc: [
    { id: "chien-luoc",      ten: "Chiến lược",       ic: "chienLuoc" },
    { id: "huan-luyen",      ten: "Phòng huấn luyện", ic: "huanLuyen",
      dem: () => (HL?.trangThai === "đang chạy" ? HL.phanTram + "%" : null), nong: true },
    { id: "hoc",             ten: "Học",              ic: "hoc", dem: () => (J?.lessons || []).length },
    { id: "tri-nho",         ten: "Trí nhớ",          ic: "triNho" },
    { id: "ky-nang",         ten: "Kho kỹ năng",      ic: "kyNang", dem: () => K?.tong ?? null },
    { id: "nhat-ky",         ten: "Nhật ký",          ic: "nhatKy", dem: () => (J?.trades || []).length },
    { id: "chat",            ten: "Hỏi bộ não",       ic: "chat" },
  ]},
];

let phongDangMo = "tong-quan";

function dungBen() {
  el("ben").innerHTML = NAV.map((t) => `
    <div class="tang">
      <div class="tang-nhan"><span class="so">${t.tang}</span>${esc(t.ten)}</div>
      <div class="tang-y">${esc(t.y)}</div>
      ${t.muc.map((m) => {
        const d = m.dem ? m.dem() : null;
        return `<button class="muc ${m.id === phongDangMo ? "on" : ""} ${m.trong ? "trong-nguon" : ""}" data-p="${m.id}">
          <span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
            stroke-linecap="round" stroke-linejoin="round">${IC[m.ic]}</svg></span>
          <span>${esc(m.ten)}</span>
          ${m.trong ? '<span class="dem">chưa có</span>'
            : d ? `<span class="dem ${m.nong && d ? "nong" : ""}">${d}</span>` : ""}
        </button>`;
      }).join("")}
    </div>`).join("");

  el("ben").querySelectorAll(".muc").forEach((b) => b.onclick = () => moPhong(b.dataset.p));
}

function moPhong(id) {
  phongDangMo = id;
  document.querySelectorAll(".phong").forEach((p) => p.classList.toggle("on", p.dataset.p === id));
  el("ben").querySelectorAll(".muc").forEach((m) => m.classList.toggle("on", m.dataset.p === id));
  ve();
}

/* ── mạch dữ liệu ──────────────────────────────────────────────── */
const MACH = [
  { id: "data",     ten: "DỮ LIỆU" },
  { id: "features", ten: "PHÂN TÍCH" },
  { id: "regime",   ten: "CHẾ ĐỘ" },
  { id: "brain",    ten: "QUYẾT ĐỊNH" },
  { id: "risk",     ten: "RỦI RO" },
  { id: "exec",     ten: "VÀO LỆNH" },
  { id: "journal",  ten: "GHI SỔ" },
  { id: "memory",   ten: "HỌC" },
];

function dungMach() {
  const m = el("mach");
  m.innerHTML = '<span class="mach-nhan">Vòng lặp AI</span>' +
    MACH.map((n, i) => (i ? `<span class="mach-noi" id="noi-${n.id}"></span>` : "") +
      `<span class="mach-o" id="mo-${n.id}"><span class="ch"></span>${n.ten}</span>`).join("") +
    '<span class="mach-noi"></span><span class="mach-o" style="color:var(--fg-4)">↺ TRÍ NHỚ</span>';
}

function veMach() {
  const now = Date.now();
  const chan = S?.decision && !S.decision.approved && S.decision.action !== "NO_TRADE";
  MACH.forEach((n, i) => {
    const o = el("mo-" + n.id);
    if (!o) return;
    const hot = NONG.get(n.id) > now;
    o.classList.toggle("hot", !!hot && !(n.id === "risk" && chan));
    o.classList.toggle("chan", n.id === "risk" && !!chan);
    if (i) { const noi = el("noi-" + n.id); if (noi) noi.classList.toggle("chay", !!hot); }
  });
}

/* ── thanh đỉnh ────────────────────────────────────────────────── */
function veDinh() {
  if (!S) return;
  const song = S.dataSource?.live;
  el("chamSong").classList.toggle("dut", !song);

  const p = S.marketState?.timeframes?.[S.timeframes?.primary] || {};
  el("giaDai").innerHTML =
    `<div class="gia-o"><i>${esc(S.symbol || "")}</i><b>${num(S.price)}</b>
      <s class="${dau(p.macdHist)}">${p.emaStack === "BULLISH_ALIGNED" ? "▲" : p.emaStack === "BEARISH_ALIGNED" ? "▼" : "◆"}</s></div>` +
    `<div class="gia-o"><i>CHẾ ĐỘ</i><b class="${S.regime?.primary?.includes("UP") ? "len" : S.regime?.primary?.includes("DOWN") ? "xuong" : "nhac"}">${esc(S.regime?.primary || "—")}</b></div>` +
    `<div class="gia-o"><i>ATR</i><b>${pct(p.atrPct, 3)}</b></div>` +
    `<div class="gia-o"><i>NGUỒN</i><b class="${song ? "len" : "xuong"}">${esc(S.dataSource?.name || "—")}</b></div>`;

  const hs = el("huySan"), tn = S.venue === "testnet";
  hs.textContent = tn ? "SÀN TESTNET · khớp thật" : "SÀN GIẤY · nội bộ";
  hs.className = "huy " + (tn ? "ok" : "nhac");

  const hc = el("huyCheDo");
  const dung = S.risk?.halted, ngat = (S.risk?.breakers || []).length;
  hc.textContent = dung ? "ĐÃ DỪNG" : S.paused ? "TẠM DỪNG" : ngat ? "AN TOÀN" : "ĐANG CHẠY";
  hc.className = "huy " + (dung ? "dut" : S.paused || ngat ? "nhac" : "ok");

  const hn = el("huyNao");
  hn.textContent = "bộ não " + (S.brain?.mode === "claude" ? S.brain.model : "mock");
  hn.className = "huy " + (["claude", "cli"].includes(S.brain?.mode) ? "ai" : "");

  // Ở chế độ `cli` KHÔNG có đồng nào — bot chạy bằng quota gói tháng. Hiện
  // "$2,09 / $5" ở đó là một con số đúng về mặt số học và sai về mặt sự thật:
  // nó là chi phí TƯƠNG ĐƯƠNG nếu gọi qua API, không phải tiền đã tiêu.
  // Thứ thật sự có trần ở chế độ này là SỐ LƯỢT, nên số lượt phải đứng trước.
  const t = S.brain?.today || {}, cap = S.brain?.budgetUsd || 0;
  const tranLuot = S.brain?.maxCalls || 0;
  const ht = el("huyTien");
  const laCli = S.brain?.mode === "cli";
  ht.textContent = laCli
    ? `${t.calls || 0}/${tranLuot} lượt · quota gói (≈$${(t.usd || 0).toFixed(2)} nếu tính qua API)`
    : `$${(t.usd || 0).toFixed(4)} / $${cap} · ${t.calls || 0} lượt`;
  const gan = laCli
    ? tranLuot && (t.calls || 0) > tranLuot * 0.7
    : cap && (t.usd || 0) > cap * 0.7;
  ht.className = "huy " + (S.brain?.blocked ? "dut" : gan ? "nhac" : "");

  el("btDung").textContent = S.paused ? "Chạy lại" : "Tạm dừng";
}

/* ── cột phải ──────────────────────────────────────────────────── */
function vePhai() {
  const th = S?.thesis, d = S?.decision;
  const hd = th?.action || "—";
  const cls = hd === "LONG" ? "long" : hd === "SHORT" ? "short" : "cho";
  const c = th?.confidence ?? 0;
  const chuvi = 2 * Math.PI * 34;

  el("aiQuyet").innerHTML = `
    <div class="hd ${cls}">${esc(hd === "NO_TRADE" ? "KHÔNG VÀO" : hd)}</div>
    <div class="nn">${esc(th?.strategy || "chưa có luận điểm")}</div>
    <div class="vong-tin">
      <svg width="78" height="78">
        <circle cx="39" cy="39" r="34" fill="none" stroke="rgba(125,158,200,.12)" stroke-width="6"/>
        <circle cx="39" cy="39" r="34" fill="none" stroke="var(--violet)" stroke-width="6" stroke-linecap="round"
          stroke-dasharray="${chuvi}" stroke-dashoffset="${chuvi * (1 - c)}"/>
      </svg>
      <div class="so">${Math.round(c * 100)}%</div>
    </div>
    <div class="nn">độ tin cậy</div>`;

  el("aiNgu").innerHTML = `<h3>Bối cảnh</h3>` +
    hang("chế độ", S?.regime?.primary || "—") +
    hang("chất lượng", S?.regime?.quality || "—") +
    hang("brain đọc", th?.regime_read || "—") +
    hang("rủi ro sự kiện", th?.event_risk || "—") +
    hang("vòng đã chạy", S?.ticks ?? "—");

  const mg = S?.marketState?.timeframes?.[S?.timeframes?.primary]?.mauGia;
  el("aiMauGia") && (el("aiMauGia").innerHTML = !mg?.co
    ? `<h3>Mẫu giá</h3><div class="mo" style="font-size:12px">không mẫu nào xác nhận ở nến này</div>`
    : `<h3>Mẫu giá</h3>` +
      (mg.mauThuan ? `<div class="nhac" style="font-size:11.5px;margin-bottom:6px">
        Hai mẫu NGƯỢC HƯỚNG cùng xác nhận — hình học đang mâu thuẫn, đây là lúc đứng ngoài
        chứ không phải lúc lấy trung bình.</div>` : "") +
      mg.mau.map((m) => hang(`${esc(m.ten)} · ${esc(m.loai)}`,
        `${esc(m.huong)} · RR ${m.rr ?? "—"}`,
        m.huong === "LONG" ? "len" : "xuong")).join(""));

  let pq = `<h3>Risk Engine</h3>`;
  if (!d) pq += '<div class="mo" style="font-size:12px">chưa thẩm định lượt nào</div>';
  else if (d.approved) pq += hang("phán quyết", "CHO QUA", "len") + hang("RR", num(d.rr)) +
    hang("rủi ro", tien(d.position?.riskAmount)) +
    (d.position?.riskBase != null
      ? hang(d.position.riskBaseIsCash ? "…% của tiền mua được" : "…% của vốn",
             `${num(d.position.riskPct, 2)}% × ${tien(d.position.riskBase)}`)
      : "");
  else if (d.action === "NO_TRADE") pq += dungNgoai();
  else pq += `<div class="xuong" style="font-size:12px;font-weight:600;margin-bottom:6px">CHẶN</div>` +
    (d.rejections || []).map((r) => `<div style="font-size:11.5px;color:var(--fg-3);padding:2px 0">× ${esc(r)}</div>`).join("");
  el("aiPhanQuyet").innerHTML = pq;
}

/* Đứng ngoài MỘT lượt và đứng ngoài MƯỜI TÁM lượt là hai chuyện khác nhau, và
   bảng cũ nói đúng một câu cho cả hai: "đây là một quyết định". Câu ấy đúng ở
   lượt thứ nhất và ru ngủ ở lượt thứ mười tám.

   Đứng ngoài liên tục vì bằng chứng ÂM về chính chế độ đang chạy là một thế bí
   tự khoá: không vào lệnh ⇒ không có dữ liệu mới ⇒ bằng chứng âm đứng nguyên ⇒
   không vào lệnh. Nó không tự kết thúc, và bảng phải nói ra chỗ đó thay vì để
   người xem chờ một thứ sẽ không tới.

   Ngưỡng 12 khớp `Runtime.DUNG_IM_LIEN_TIEP` và `ban-giao.DUNG_IM_LIEN_TIEP`. */
const DUNG_IM = 12;

function dungNgoai() {
  const n = S?.chuoiDungNgoai || 0;
  if (n < DUNG_IM)
    return '<div class="nhac" style="font-size:12px">Bộ não chủ động đứng ngoài — '
         + (n > 1 ? `lượt thứ ${n} liên tiếp. ` : "")
         + "đây là một quyết định.</div>";
  return `<div class="xuong" style="font-size:12px;font-weight:600;margin-bottom:6px">ĐỨNG IM ${n} LƯỢT LIÊN TIẾP</div>`
       + '<div class="nhac" style="font-size:11.5px;line-height:1.5">Đứng ngoài vẫn là '
       + "quyết định đúng nếu bằng chứng âm. Nhưng nó đã đúng lâu tới mức tự khoá: "
       + "không vào lệnh nghĩa là không có dữ liệu mới, nên bằng chứng âm đứng "
       + "nguyên. <b>Cái chờ này không tự kết thúc</b> — thứ phải đổi là chiến lược "
       + 'hoặc chợ, không phải thời gian.</div>';
}
/* ── TẦNG 1 · TỔNG QUAN ────────────────────────────────────────── */
function veTongQuan() {
  if (!S) return;
  const a = S.account || {}, r = S.risk || {};
  const dung = r.halted, ngat = (r.breakers || []).length;

  el("tqTrangThai").innerHTML = `<div class="luoi c3">
    ${oSo("Hệ thống", S.dataSource?.live ? "TỐT" : "DỮ LIỆU GIẢ",
        S.dataSource?.live ? "len" : "xuong", S.dataSource?.name || "")}
    ${oSo("Giao dịch", dung ? "ĐÃ DỪNG" : S.paused ? "TẠM DỪNG" : ngat ? "BỊ CHẶN" : "HOẠT ĐỘNG",
        dung ? "xuong" : S.paused || ngat ? "nhac" : "len", dung || (r.breakers || [])[0] || "")}
    ${oSo("Chế độ rủi ro", ngat ? "HẠN CHẾ" : "BÌNH THƯỜNG", ngat ? "nhac" : "", S.spotOnly ? "spot · chỉ LONG" : "")}
    ${oSo("Chế độ thị trường", S.regime?.primary || "—", "lam", "chất lượng " + (S.regime?.quality || "—"))}
    ${oSo("Tin cậy của bot", S.thesis ? Math.round((S.thesis.confidence || 0) * 100) + "%" : "—", "tim",
        S.thesis ? S.thesis.strategy : "chưa có luận điểm")}
    ${oSo("Bộ não", S.brain?.mode === "claude" ? "CLAUDE" : "MOCK",
        S.brain?.mode === "claude" ? "tim" : "nhac",
        S.brain?.mode === "claude" ? S.brain.model : "suy luận bằng luật, không tốn tiền")}
  </div>`;

  // Biểu đồ ngay trên màn đầu — đúng như bố cục HOME trong bản thiết kế.
  el("tqBieuDo").innerHTML = khoiBieuDo("cvTongQuan", 260);
  veBieuDoVao("cvTongQuan", 260);

  const lai = (a.equityMarked ?? 0) - (S.risk?.limits?.startingEquity ?? 0);
  const trienKhai = (a.positions || []).reduce((s, p) => s + (p.riskAmount || 0), 0);
  const tranRui = (a.equityMarked || 1) * (r.limits?.maxRiskPerTradePct || 0.5) / 100;

  // P&L 7 ngày tính từ nhật ký — dailyPnl chỉ giữ theo ngày UTC, cộng lại là ra.
  const bayNgay = new Date(Date.now() - 7 * 864e5).toISOString().slice(0, 10);
  const tuan = Object.entries(a.dailyPnl || {})
    .filter(([d]) => d >= bayNgay).reduce((s, [, v]) => s + v, 0);
  const von0 = r.limits?.startingEquity || 0;
  const rrDatPct = a.equityMarked ? (trienKhai / a.equityMarked) * 100 : 0;
  const muaDuocPct = a.equityMarked ? (a.availableQuote / a.equityMarked) * 100 : null;

  el("tqTaiKhoan").innerHTML = `<div class="luoi c4">
    ${oSo("Vốn", tien(a.equityMarked), "", S.venue === "testnet" ? "đọc từ sàn" : "sàn giấy")}
    ${oSo("Hôm nay", tien(a.todayPnl), dau(a.todayPnl),
        a.equityMarked ? pct((a.todayPnl / a.equityMarked) * 100) : "")}
    ${oSo("7 ngày", tien(tuan), dau(tuan),
        a.equityMarked ? pct((tuan / a.equityMarked) * 100) : "")}
    ${oSo("Drawdown", pct(a.drawdownPct), a.drawdownPct > (r.limits?.maxDrawdownPct || 10) * 0.6 ? "nhac" : "",
        "đỉnh " + tien(a.peakEquity))}
    ${oSo("Vị thế mở", (a.positions || []).length, "", `trần ${r.limits?.maxOpenPositions ?? "—"}`)}
    ${oSo("Rủi ro đang đặt", pct(rrDatPct), rrDatPct > (r.limits?.maxRiskPerTradePct || 0.5) ? "nhac" : "",
        tien(trienKhai))}
    ${oSo("Vốn còn mua được", muaDuocPct == null ? "—" : pct(muaDuocPct), "", tien(a.availableQuote))}
    ${oSo("So với vốn ban đầu", von0 ? tien(a.equityMarked - von0) : "—",
        dau(a.equityMarked - von0), von0 ? "gốc " + tien(von0) : "")}
  </div>
  <div class="luoi c2" style="margin-top:12px">
    <div class="kinh the"><h3>Sức chứa<span class="cuoi">đã dùng / trần</span></h3>
      ${thanhDo(`Rủi ro đang đặt · trần ${tien(tranRui)}`,
          `${tien(trienKhai)} / ${pct(r.limits?.maxRiskPerTradePct)}`,
          tranRui ? (trienKhai / tranRui) * 100 : 0, "tim")}
      ${thanhDo(`Vị thế mở · trần ${r.limits?.maxOpenPositions ?? "—"}`,
          `${(a.positions || []).length} / ${r.limits?.maxOpenPositions ?? "—"}`,
          r.limits?.maxOpenPositions ? ((a.positions || []).length / r.limits.maxOpenPositions) * 100 : 0, "")}
      ${thanhDo("Tiền mua được trên tổng vốn", `${tien(a.availableQuote)} / ${tien(a.equityMarked)}`,
          a.equityMarked ? (a.availableQuote / a.equityMarked) * 100 : null, "")}
      <p style="margin:8px 0 0;font-size:11px;color:var(--fg-4);line-height:1.55">
        Thanh đầy nghĩa là đã chạm trần, không phải "tốt". Hàng cuối thấp là bình thường khi
        tài khoản giữ cả coin lẫn tiền — vốn lớn nhưng chỉ mua được bằng phần tiền mặt.</p>
    </div>
    <div class="kinh the"><h3>Sàn</h3>
      ${hang("nơi khớp", S.venue === "testnet" ? "Binance Spot Testnet" : "mô phỏng nội bộ")}
      ${hang("cặp", S.symbol)}
      ${hang("khung", `${S.timeframes?.primary} + ${S.timeframes?.context}`)}
      ${hang("chỉ LONG", S.spotOnly ? "có (spot)" : "không")}
      ${hang("lệnh đã đóng", a.closedCount ?? 0)}
    </div>
  </div>`;

  // GOOD/BAD decision — thứ quan trọng hơn lãi/lỗ
  const ls = J?.lessons || [];
  const homNay = new Date().toISOString().slice(0, 10);
  const hn = ls.filter((l) => (l.at || "").slice(0, 10) === homNay);
  const tot = hn.filter((l) => (l.classification || "").startsWith("GOOD_TRADE")).length;
  const xau = hn.filter((l) => (l.classification || "").startsWith("BAD_TRADE")).length;
  const td = (J?.trades || []).filter((t) => (t.closedAt || "").slice(0, 10) === homNay);
  // Hoà vốn: |PnL| nhỏ hơn 2% số tiền đã đặt rủi ro. Lấy đúng 0 thì gần như
  // không bao giờ khớp — phí luôn để lại vài xu lẻ.
  const hoa = td.filter((t) => Math.abs(t.pnl || 0) < (t.riskAmount || 1) * 0.02).length;
  const thang = td.filter((t) => (t.pnl || 0) > 0 && !(Math.abs(t.pnl) < (t.riskAmount || 1) * 0.02)).length;
  const thua = td.filter((t) => (t.pnl || 0) < 0 && !(Math.abs(t.pnl) < (t.riskAmount || 1) * 0.02)).length;
  const doiCl = hn.filter((l) => l.change_strategy).length;

  el("tqHomNay").innerHTML = `<div class="luoi c4">
    ${oSo("Lệnh", td.length)}
    ${oSo("Thắng / Thua / Hoà", `${thang} / ${thua} / ${hoa}`, "", "kết quả")}
    ${oSo("Quyết định tốt", tot, tot ? "len" : "mo", "chất lượng, không phải tiền")}
    ${oSo("Quyết định tồi", xau, xau ? "xuong" : "mo", "đây mới là thứ phải sửa")}
    ${oSo("Bài học hôm nay", hn.length, hn.length ? "tim" : "mo", "sinh sau mỗi lệnh đóng")}
    ${oSo("Chiến lược bị đổi", doiCl, doiCl ? "nhac" : "mo", "cửa hẹp — cần mẫu lặp lại")}
  </div>
  <div class="kinh the" style="margin-top:12px">
    <h3>Vì sao tách hai hàng này<span class="cuoi">quyết định ≠ kết quả</span></h3>
    <p style="margin:0;font-size:12.5px;color:var(--fg-3);line-height:1.7">
      Một lệnh <b>lãi</b> vẫn có thể là quyết định ngu, và một lệnh <b>lỗ</b> đúng quy trình vẫn là quyết định tốt.
      Học theo tiền lãi/lỗ thay vì theo chất lượng quyết định thì cuối cùng sẽ học ra cờ bạc — và nó học rất nhanh,
      vì phần thưởng đến ngay.
    </p>
  </div>`;
}

/* ── TẦNG 1 · VỊ THẾ ───────────────────────────────────────────── */
function veViThe() {
  const a = S?.account || {}, vt = a.positions || [];
  if (!vt.length) {
    el("vtNoi").innerHTML = `<div class="trong">Không có vị thế nào đang mở.<br>
      <span style="color:var(--fg-3)">Phần lớn thời gian thị trường không đưa ra gì đáng vào — đó là trạng thái bình thường.</span></div>`;
    return;
  }
  const p = S.marketState?.timeframes?.[S.timeframes?.primary] || {};
  const ctx = S.marketState?.timeframes?.[S.timeframes?.context] || {};

  el("vtNoi").innerHTML = vt.map((v) => {
    const r = v.unrealizedR ?? 0;
    const tienDo = v.targets?.[0] && v.entry
      ? clamp(((S.price - v.entry) / (v.targets[0] - v.entry)) * 100) : 0;
    const check = [
      ["Cấu trúc khung lớn", ctx.emaStack === "BULLISH_ALIGNED", ctx.emaStack],
      ["Cấu trúc khung chính", p.structure === "UPTREND", p.structure],
      ["Động lượng", (p.macdHistSlope ?? 0) > 0, "MACD " + (p.macdHistSlope > 0 ? "tăng" : "giảm")],
      ["Sức xu hướng", (p.adx ?? 0) >= 22, "ADX " + num(p.adx, 1)],
      ["Biến động", p.volatility === "NORMAL", p.volatility],
    ];
    return `<div class="kinh the" style="margin-bottom:12px">
      <h3>${esc(v.symbol || S.symbol)} · ${esc(v.side)}<span class="cuoi">${esc(v.strategy || "")}</span></h3>
      <div class="luoi c4" style="margin-bottom:12px">
        <div><div class="phu-nho">vào</div><div class="so-vua">${num(v.entry)}</div></div>
        <div><div class="phu-nho">hiện tại</div><div class="so-vua">${num(S.price)}</div></div>
        <div><div class="phu-nho">lãi/lỗ</div><div class="so-vua ${dau(v.unrealizedPnl)}">${tien(v.unrealizedPnl)}</div></div>
        <div><div class="phu-nho">R</div><div class="so-vua ${dau(r)}">${r > 0 ? "+" : ""}${num(r)}R</div></div>
      </div>
      ${thanhDo(`SL ${num(v.stopLoss)} → TP ${num(v.targets?.[0])}`, num(S.price), tienDo, r >= 0 ? "" : "dut")}
      <div class="luoi c3" style="margin-top:12px">
        ${hang("khối lượng", Number(v.qty).toFixed(6))}
        ${hang("rủi ro", tien(v.riskAmount))}
        ${hang("RR kế hoạch", v.rr ?? "—")}
        ${v.riskBase != null
          ? hang(v.riskBaseIsCash ? "mẫu số rủi ro" : "mẫu số rủi ro (vốn)", tien(v.riskBase))
          : hang("mẫu số rủi ro", "— (lệnh mở trước khi sửa)")}
      </div>
      <div class="tieu-muc" style="margin-top:16px">Vì sao vẫn còn giữ</div>
      ${check.map(([ten, ok, gt]) =>
        `<div class="hang"><span>${esc(ten)}</span><b class="${ok ? "len" : "nhac"}">${ok ? "✓" : "!"} ${esc(gt ?? "—")}</b></div>`).join("")}
      <div class="hang"><span>lệnh thoát do sàn giữ</span><b class="${v.ocoOrderListId ? "len" : "xuong"}">${
        v.ocoOrderListId ? "✓ OCO " + v.ocoOrderListId : "✗ KHÔNG CÓ — không ai canh"}</b></div>

      <div class="tieu-muc" style="margin-top:16px">Mục tiêu</div>
      ${(v.targets || []).map((t, i) => {
        const cham = S.price >= t;
        return `<div class="hang"><span>TP${i + 1} · ${num(t)}</span><b class="${cham ? "len" : ""}">${
          cham ? "✓ ĐÃ CHẠM" : i === 0 ? "ĐANG CHỜ" : "CHƯA TỚI"}</b></div>`;
      }).join("")}
      ${(v.targets || []).length < 2 ? `<div class="phu-nho" style="margin-top:6px">
        M0 chỉ dùng MỘT mục tiêu và thoát toàn bộ. Chốt từng phần (TP1/TP2/runner) và dời SL về hoà vốn
        là mốc sau — thêm bây giờ là thêm nhánh chưa có nhật ký nào kiểm chứng.</div>` : ""}

      <div class="luoi c2" style="margin-top:14px">
        <div class="kinh the" style="background:var(--glass-2)">
          <h3>Claude</h3><div class="so-vua tim">${esc(S.thesis?.action === "NO_TRADE" ? "GIỮ" : S.thesis?.action || "GIỮ")}</div>
          <div class="phu-nho">${esc(S.thesis?.strategy || "")}</div></div>
        <div class="kinh the" style="background:var(--glass-2)">
          <h3>Risk Engine</h3><div class="so-vua ${S.risk?.halted ? "xuong" : (S.risk?.breakers || []).length ? "nhac" : "len"}">${
            S.risk?.halted ? "ĐÃ DỪNG" : (S.risk?.breakers || []).length ? "HẠN CHẾ" : "CHO GIỮ"}</div>
          <div class="phu-nho">${esc((S.risk?.breakers || [])[0] || "trong hạn mức")}</div></div>
      </div>
    </div>`;
  }).join("");
}

/* ── TẦNG 1 · RỦI RO ───────────────────────────────────────────── */
function veRuiRo() {
  const r = S?.risk || {}, a = S?.account || {}, L = r.limits || {};
  const trienKhai = (a.positions || []).reduce((s, p) => s + (p.riskAmount || 0), 0);
  const rrPct = a.equityMarked ? (trienKhai / a.equityMarked) * 100 : 0;
  const loHomNay = Math.max(0, -(a.todayPnl || 0));
  const loPct = a.equityMarked ? (loHomNay / a.equityMarked) * 100 : 0;

  el("rrNoi").innerHTML = `
    ${r.halted ? `<div class="kinh the" style="border-color:rgba(248,113,113,.4);margin-bottom:12px">
      <h3 style="color:var(--red)">Đã dừng</h3><div class="xuong mono" style="font-size:12.5px">${esc(r.halted)}</div></div>` : ""}
    ${(r.breakers || []).length ? `<div class="kinh the" style="border-color:rgba(251,191,36,.35);margin-bottom:12px">
      <h3 style="color:var(--amber)">Ngắt mạch đang bật</h3>
      ${r.breakers.map((b) => `<div class="nhac mono" style="font-size:11.5px;padding:2px 0">• ${esc(b)}</div>`).join("")}</div>` : ""}

    <div class="luoi c2">
      <div class="kinh the"><h3>Mức dùng so với trần</h3>
        ${thanhDo("Rủi ro danh mục", `${num(rrPct)} / ${L.maxRiskPerTradePct}%`,
            L.maxRiskPerTradePct ? (rrPct / L.maxRiskPerTradePct) * 100 : 0,
            rrPct > L.maxRiskPerTradePct ? "dut" : "")}
        ${thanhDo("Lỗ trong ngày", `${num(loPct)} / ${L.maxDailyLossPct}%`,
            L.maxDailyLossPct ? (loPct / L.maxDailyLossPct) * 100 : 0,
            loPct > L.maxDailyLossPct * 0.7 ? "nhac" : "")}
        ${thanhDo("Drawdown", `${num(a.drawdownPct)} / ${L.maxDrawdownPct}%`,
            L.maxDrawdownPct ? ((a.drawdownPct || 0) / L.maxDrawdownPct) * 100 : 0,
            (a.drawdownPct || 0) > L.maxDrawdownPct * 0.6 ? "dut" : "")}
        ${thanhDo("Vị thế mở", `${(a.positions || []).length} / ${L.maxOpenPositions}`,
            L.maxOpenPositions ? ((a.positions || []).length / L.maxOpenPositions) * 100 : 0, "tim")}
      </div>

      <div class="kinh the"><h3>Công tắc cứng<span class="cuoi">Claude không đổi được</span></h3>
        ${[["Rủi ro / lệnh", L.maxRiskPerTradePct + "%"],
           ["Lỗ ngày tối đa", L.maxDailyLossPct + "%"],
           ["Drawdown tối đa", L.maxDrawdownPct + "%"],
           ["RR tối thiểu (sau phí)", L.minRR],
           ["Tin cậy tối thiểu", L.minConfidence],
           ["Khoảng stop", `${L.minStopAtr}–${L.maxStopAtr} × ATR`],
           ["Vị thế đồng thời", L.maxOpenPositions],
           ["Chỉ LONG (spot)", S?.spotOnly ? "BẬT" : "TẮT"]].map(([t, v]) =>
          `<div class="tac"><span class="khoa"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg></span>
           <span class="ten">${esc(t)}</span><span class="gt">${esc(v)}</span></div>`).join("")}
        <button class="nut-dung ${r.halted ? "dang-dung" : ""}" id="btKill">
          ${r.halted ? "GỠ KILL SWITCH" : "DỪNG TOÀN BỘ BOT"}
        </button>
      </div>
    </div>

    <div class="kinh the" style="margin-top:12px">
      <h3>Vì sao Claude không cầm chìa khoá két</h3>
      <p style="margin:0;font-size:12.5px;color:var(--fg-3);line-height:1.7">
        Bộ não được phép phân tích, dựng kịch bản, đề xuất lệnh và điểm vô hiệu hoá. Nó <b>không</b> có đường nào
        bỏ stop loss, tăng size, tăng đòn bẩy hay vượt drawdown — Risk Engine là Python thuần, không gọi model,
        và nó <b>tính lại kích thước vị thế từ đầu</b>. <code>confidence 0.99</code> chỉ dùng để TỪ CHỐI,
        không bao giờ dùng để nới thêm rủi ro.
      </p>
    </div>`;

  const bk = el("btKill");
  if (bk) bk.onclick = () => dieuKhien(S?.risk?.halted ? "unkill" : "kill");
}

/* ── TẦNG 2 · BỘ NÃO THỊ TRƯỜNG ────────────────────────────────── */
function veNaoThiTruong() {
  const p = S?.marketState?.timeframes?.[S?.timeframes?.primary] || {};
  const ctx = S?.marketState?.timeframes?.[S?.timeframes?.context] || {};

  // Chuyển feature thật thành thang 0–100. Ô nào không có nguồn thì để null.
  const trend = p.adx == null ? null
    : clamp((p.adx / 40) * 100) * (p.emaStack === "MIXED" ? 0.55 : 1);
  const momentum = p.rsi14 == null ? null : clamp(Math.abs(p.rsi14 - 50) * 2.6);
  const volat = p.atrRatioVsMedian == null ? null : clamp(p.atrRatioVsMedian * 55);

  /* TỔNG HỢP — nói rõ nó dựa trên MẤY nguồn. Ba trên sáu ô có dữ liệu, nên
     một dòng "BULLISH · TIN CẬY CAO" ở đây sẽ là tự tin quá mức so với thứ
     thực sự đo được. Ghi luôn số nguồn thay vì giấu. */
  const G = W?.phaiSinh, V = W?.viMo;
  const coVimo = !!V?.co, coPs = !!G?.co;

  // Thang 0–100 cho hai ô mới. Vĩ mô: khẩu vị rủi ro quanh mốc 50.
  const viMoDo = !coVimo ? null : clamp(50 + (V.khauVi?.diem ?? 0) * 25);
  // "Trader giỏi": lệch khỏi cân bằng của nhóm ký quỹ lớn, KHÔNG phải tỉ lệ thô.
  const tlTop = G?.topTrader?.tyLe;
  const traderDo = tlTop == null ? null : clamp((tlTop / (1 + tlTop)) * 100);

  const soNguon = 3 + (coVimo ? 1 : 0) + (coPs ? 1 : 0);
  const huong = p.emaStack === "BULLISH_ALIGNED" ? { chu: "THIÊN TĂNG", cls: "len" }
    : p.emaStack === "BEARISH_ALIGNED" ? { chu: "THIÊN GIẢM", cls: "xuong" }
    : { chu: "KHÔNG RÕ HƯỚNG", cls: "nhac" };
  const manh = (p.adx ?? 0) >= 25 ? "mạnh" : (p.adx ?? 0) >= 18 ? "vừa" : "yếu";
  const tongHop = {
    chu: `${huong.chu} · lực ${manh}`,
    cls: huong.cls,
    y: `dựa trên ${soNguon}/6 nguồn (kỹ thuật${coVimo ? " · vĩ mô" : ""}${coPs ? " · phái sinh" : ""}). ` +
       `On-chain chưa nối${!coVimo || !coPs ? ", và một số nguồn ngoài chưa lấy được" : ""} — ` +
       `dòng này là tổng hợp của phần đo được, không phải một kết luận đầy đủ.`,
  };

  const fund = G?.fundingNamHoa;
  el("nttNoi").innerHTML = `
    <div class="nao">
      <div class="kinh nao-o tren ${coVimo ? "" : "im"}"><h4>Vĩ mô${coVimo ? "" : " · chưa lấy được"}</h4>
        ${["DXY", "US10Y", "DAU"].map((k) => {
          const m = V?.muc?.[k];
          return `<div class="d"><span>${k === "US10Y" ? "lợi suất" : k === "DAU" ? "dầu" : "DXY"}</span>${
            m ? `<span>${num(m.gia, 2)} <b class="${dau(m.doiPct)}">${m.doiPct > 0 ? "+" : ""}${num(m.doiPct, 1)}%</b></span>`
              : '<span class="mo">—</span>'}</div>`;
        }).join("")}</div>

      <div class="kinh nao-o trai im"><h4>On-chain · chưa nối</h4>
        <div class="d"><span>dòng vào sàn</span><span class="mo">—</span></div>
        <div class="d"><span>ví cá voi</span><span class="mo">—</span></div>
        <div class="d"><span>stablecoin</span><span class="mo">—</span></div></div>

      <div class="nao-loi">
        <div class="cap">${esc(S?.symbol || "—")}</div>
        <div class="gia">${num(S?.price)}</div>
        <div class="rg">${esc(S?.regime?.primary || "—")}</div>
      </div>

      <div class="kinh nao-o phai ${coPs ? "" : "im"}"><h4>Phái sinh${coPs ? "" : " · chưa lấy được"}</h4>
        <div class="d"><span>funding</span>${fund == null ? '<span class="mo">—</span>'
          : `<span class="${fund > 15 ? "xuong" : fund < 0 ? "len" : ""}">${num(fund, 1)}%/năm</span>`}</div>
        <div class="d"><span>open interest</span>${G?.openInterestUsd == null ? '<span class="mo">—</span>'
          : `<span>$${num(G.openInterestUsd / 1e9, 2)} tỷ <b class="${dau(G.oiDoi24hPct)}">${
              G.oiDoi24hPct > 0 ? "+" : ""}${num(G.oiDoi24hPct, 1)}%</b></span>`}</div>
        <div class="d"><span>vùng thanh lý</span><span class="mo">— cần dữ liệu trả phí</span></div></div>

      <div class="kinh nao-o duoi"><h4>Kỹ thuật · có dữ liệu thật</h4>
        <div class="d"><span>EMA</span><span>${esc(p.emaStack || "—")}</span></div>
        <div class="d"><span>RSI(14)</span><span>${num(p.rsi14, 1)}</span></div>
        <div class="d"><span>ADX</span><span>${num(p.adx, 1)}</span></div>
        <div class="d"><span>Volume</span><span>×${num(p.volumeRatio)}</span></div></div>
    </div>

    ${fund != null && fund > 20 ? `<div class="canh-bao">Funding ${num(fund, 1)}%/năm —
      phe long đang trả rất đắt để giữ vị thế. Trạng thái này thường đi trước những cú quét dài.</div>` : ""}

    <div class="tieu-muc">Trạng thái thị trường</div>
    <div class="luoi c2">
      <div class="kinh the">
        ${thanhDo("Xu hướng", p.adx != null ? `${num(trend, 0)}%` : "chưa có", trend, "")}
        ${thanhDo("Động lượng", p.rsi14 != null ? `${num(momentum, 0)}%` : "chưa có", momentum, "")}
        ${thanhDo("Biến động", p.atrRatioVsMedian != null ? `${num(volat, 0)}%` : "chưa có", volat, "tim")}
        ${thanhDo("Thanh khoản", "chưa có nguồn", null)}
        ${thanhDo("Vĩ mô · khẩu vị rủi ro", coVimo ? esc(V.khauVi.nhan) : "chưa có", viMoDo,
          (V?.khauVi?.diem ?? 0) > 0 ? "len" : "xuong", 50)}
        ${thanhDo("Trader lớn đang LONG", traderDo != null ? `${num(traderDo, 1)}%` : "chưa có",
          traderDo, "", 50)}
        <div style="margin-top:14px;padding-top:12px;border-top:1px solid var(--line)">
          <div class="phu-nho">TỔNG HỢP</div>
          <div class="so-vua ${tongHop.cls}" style="margin-top:3px">${esc(tongHop.chu)}</div>
          <div class="phu-nho" style="margin-top:5px">${esc(tongHop.y)}</div>
        </div>
      </div>
      <div class="kinh the"><h3>Vì sao bộ phân loại nói vậy</h3>
        ${(S?.regime?.reasons || []).map((r) => `<div style="font-size:12.5px;color:var(--fg-2);padding:4px 0;display:flex;gap:8px">
          <span class="lam">▸</span><span>${esc(r)}</span></div>`).join("") || '<div class="mo">—</div>'}
        <div class="tieu-muc" style="margin-top:14px">Hai khung</div>
        ${hang(S?.timeframes?.primary || "chính", `${p.emaStack} · ${p.structure}`)}
        ${hang(S?.timeframes?.context || "lớn", `${ctx.emaStack} · ${ctx.structure}`)}
        ${hang("mâu thuẫn khung", (S?.regime?.flags || []).includes("MTF_CONFLICT") ? "CÓ — lý do đứng ngoài" : "không",
            (S?.regime?.flags || []).includes("MTF_CONFLICT") ? "nhac" : "len")}
      </div>
    </div>

    <div style="margin-top:12px">${chuaCo("On-chain — ô duy nhất còn trống",
      "Vĩ mô và phái sinh đã nối xong bằng nguồn công khai miễn phí, không cần khoá. " +
      "On-chain thì chưa, và nó trống thật chứ không điền số cho đủ hình.",
      ["<b>Dòng vào/ra sàn, ví cá voi, cung stablecoin</b> — cần Glassnode/Nansen (trả phí) hoặc tự chạy node",
       "Đây là ô đắt nhất trong bốn ô, và cũng là ô ít cấp bách nhất: ba ô kia đã đủ để bộ não có bối cảnh",
       "Ghi chú về <b>phái sinh</b>: funding và open interest lấy từ Binance Futures công khai. " +
       "Runtime vẫn chạy <code>spot</code> — dữ liệu futures dùng để ĐỌC trạng thái đòn bẩy của thị trường, " +
       "không phải để giao dịch futures"])}</div>`;
}

/* ── TẦNG 2 · BỘ NÃO CLAUDE ────────────────────────────────────── */
function veNaoClaude() {
  const t = S?.thesis, d = S?.decision;
  if (!t) {
    el("ncNoi").innerHTML = `<div class="trong">Chưa có luận điểm nào.<br>
      <span style="color:var(--fg-3)">Bộ não chỉ thức khi có nến mới đóng, khi chế độ thị trường đổi, hoặc khi bạn bấm “Phân tích ngay”.</span></div>`;
    return;
  }
  const mau = ["", "tim", "nhac"];
  el("ncNoi").innerHTML = `
    <div class="luoi c2">
      <div class="kinh the"><h3>Luận điểm hiện tại<span class="cuoi">${esc(t.source || "")}</span></h3>
        <p style="margin:0 0 10px;font-size:13px;line-height:1.7;color:var(--fg-2)">${esc(t.market_summary || "")}</p>
        ${hang("chế độ brain đọc", t.regime_read)}
        ${hang("bộ phân loại nói", t.regimeFromClassifier)}
        ${hang("chiến lược", t.strategy)}
        ${hang("rủi ro sự kiện", t.event_risk)}
      </div>
      <div class="kinh the"><h3>Mức giá đề xuất</h3>
        ${hang("vùng vào", (t.entry_zone || []).map((x) => num(x)).join(" – ") || "—")}
        ${hang("vô hiệu hoá (SL)", num(t.invalidation))}
        ${hang("mục tiêu", (t.targets || []).map((x) => num(x)).join(" · ") || "—")}
        ${hang("rủi ro đề xuất", (t.suggested_risk_pct ?? 0) + "%")}
        <p style="margin:9px 0 0;font-size:11.5px;color:var(--fg-3);line-height:1.6">${esc(t.invalidation_logic || "")}</p>
      </div>
    </div>

    <div class="tieu-muc">Kịch bản</div>
    <div class="kinh the">
      ${(t.scenarios || []).map((s, i) => `<div class="kb">
        <div class="kb-dinh"><b>${esc(s.name)}</b><s>${Math.round((s.probability || 0) * 100)}%</s></div>
        <div class="do-rai"><div class="do-day ${mau[i % 3]}" style="width:${(s.probability || 0) * 100}%"></div></div>
        <div class="kb-mo">${esc(s.description)}</div>
      </div>`).join("") || '<div class="mo">—</div>'}
      <p style="margin:12px 0 0;font-size:11.5px;color:var(--fg-4);line-height:1.6">
        Bộ não không dự đoán một mức giá. Nó gán xác suất cho các kịch bản — và <b>NO_TRADE là một quyết định đúng</b>,
        không phải một lần bỏ lỡ.</p>
    </div>

    ${d && !d.approved && d.action !== "NO_TRADE" ? `
      <div class="tieu-muc">Vì sao KHÔNG vào lệnh ngay</div>
      <div class="vi-sao">
        <h4>Risk Engine chặn</h4>
        ${(d.rejections || []).map((r) => `<div>${esc(r)}</div>`).join("")}
      </div>` : ""}
    ${d && d.action === "NO_TRADE" ? `
      <div class="tieu-muc">Vì sao KHÔNG vào lệnh</div>
      <div class="vi-sao" style="border-left-color:var(--cyan);background:rgba(34,211,238,.05)">
        <h4 style="color:var(--cyan)">Bộ não chủ động đứng ngoài</h4>
        <div style="color:var(--fg-2)">${esc(t.reasoning || "")}</div>
      </div>` : ""}

    <div class="tieu-muc">Lập luận đầy đủ</div>
    <div class="kinh the" style="white-space:pre-wrap;font-size:13px;line-height:1.75;color:var(--fg-2)">${esc(t.reasoning || "—")}</div>
    <div class="kinh the mono" style="margin-top:10px;font-size:11px;color:var(--fg-3)">${esc((t.reason_codes || []).join("  ·  ")) || "—"}</div>`;
}

/* ── TẦNG 1 · HỆ THỐNG ─────────────────────────────────────────── */
let TC = null;          // /api/tu-chay
let CL = null;          // /api/chien-luoc
let QS = null;          // /api/quan-sat

function veHeThong() {
  const n = el("htNoi");
  if (!TC) { n.innerHTML = `<div class="trong">Đang đọc trạng thái hệ thống…</div>`; return; }

  const bat = !!TC.bat;
  n.innerHTML = `
    <div class="kinh the cong-tac">
      <div class="ct-trai">
        <h3 style="margin:0 0 4px">Tự chạy khi đăng nhập Windows</h3>
        <p style="margin:0;font-size:12.5px;line-height:1.7;color:var(--fg-2)">
          ${bat
            ? "Đang <b class='len'>BẬT</b>. Bật máy và đăng nhập là runtime tự lên, không cần bấm gì."
            : "Đang <b>TẮT</b>. Runtime chỉ chạy khi bạn bấm lối tắt <b>Tử Cấm Thành</b> ngoài desktop."}
        </p>
        ${TC.coThe ? "" : `<p class="phu-nho" style="margin-top:8px;color:var(--amber)">
          Không bật được ở máy này: ${esc(TC.viSao || "")}</p>`}
      </div>
      <button class="ct-nut ${bat ? "on" : ""}" id="htTuChay" ${TC.coThe ? "" : "disabled"}
        role="switch" aria-checked="${bat}" title="${bat ? "Tắt tự chạy" : "Bật tự chạy"}">
        <span class="ct-num"></span></button>
    </div>

    <div class="kinh the" style="margin-top:12px">
      <p style="margin:0;font-size:12.5px;line-height:1.8;color:var(--fg-2)">
      <b>Mặc định là TẮT, và đó là mặc định đúng.</b> Trên một máy nhiều người
      dùng chung, một cỗ máy đặt lệnh tự khởi động là thứ không ai xin phép — người
      ngồi vào máy sau bạn không biết nó đang chạy, không biết nó đang giữ vị thế nào.</p>
      <p style="margin:10px 0 0;font-size:12.5px;line-height:1.8;color:var(--fg-3)">
      Bật nó ở máy riêng của bạn thì hợp lý. Còn trên VPS thì <b>đừng dùng công tắc này</b>:
      Linux tự chạy bằng <code>systemd</code>, và nó khởi động theo MÁY chứ không theo
      phiên đăng nhập — đúng thứ một con bot chạy 24/7 cần.</p>
    </div>

    <div class="tieu-muc">Runtime đang chạy ở đâu</div>
    <div class="kinh the">
      ${hang("thư mục", TC.goc || "—")}
      ${hang("python", TC.python || "—")}
      ${hang("hệ điều hành", TC.heDieuHanh === "nt" ? "Windows" : (TC.heDieuHanh || "—"))}
      ${TC.duong ? hang("lối tắt tự chạy", TC.duong) : ""}
      ${hang("cổng", location.port || "80")}
      ${hang("sàn", S?.mode === "testnet" ? "Binance Spot Testnet — lệnh thật, tiền giả"
                  : "sàn giấy nội bộ — không có lệnh nào ra sàn",
             S?.mode === "testnet" ? "nhac" : "")}
      ${hang("chỉ LONG", S?.spotOnly ? "có — spot không short được" : "không")}
      ${hang("số vòng đã chạy", S?.ticks ?? "—")}
    </div>

    <div class="tieu-muc">Tắt runtime</div>
    <div class="kinh the">
      <p style="margin:0 0 12px;font-size:12.5px;line-height:1.8;color:var(--fg-2)">
      Đóng trình duyệt <b>không</b> tắt bot — nó chạy ngầm, không cửa sổ nào.
      Nút dưới đây tắt hẳn tiến trình và báo bộ giám sát đừng dựng lại.</p>
      <div class="hang">
        <span>Lệnh đang mở trên sàn</span>
        <b class="${(S?.account?.positions || []).length ? "nhac" : ""}">${(S?.account?.positions || []).length}</b>
      </div>
      <p style="margin:8px 0 12px;font-size:11.5px;line-height:1.7;color:var(--fg-3)">
      ${(S?.account?.positions || []).length
        ? "Cắt lỗ và chốt lời của các vị thế này đã đặt <b>trên sàn</b> dưới dạng lệnh OCO, nên chúng vẫn hiệu lực khi runtime tắt. Thứ mất đi là việc theo dõi và hậu kiểm."
        : "Không có vị thế nào đang mở."}</p>
      <div class="nut-hang">
        <button class="nut nguy" id="htDungHan">Tắt hẳn runtime</button>
        <button class="nut" id="htTamDung">${S?.paused ? "Chạy tiếp" : "Tạm dừng vòng lặp"}</button>
      </div>
      <p class="phu-nho" style="margin-top:10px">
      <b>Tạm dừng</b> giữ tiến trình sống, chỉ ngừng ra quyết định — bấm lại là chạy tiếp.
      <b>Tắt hẳn</b> thì phải bấm lối tắt ngoài desktop để bật lại.</p>
    </div>`;

  const nut = el("htTuChay");
  if (nut && TC.coThe) nut.onclick = () => datTuChay(!bat);
  el("htTamDung").onclick = () => dieuKhien(S?.paused ? "resume" : "pause");
  el("htDungHan").onclick = async () => {
    if (!confirm("Tắt hẳn runtime?\n\nVòng lặp dừng, bot ngừng theo dõi thị trường.\n" +
                 "Lệnh OCO đã đặt trên sàn vẫn còn hiệu lực.\n\n" +
                 "Bật lại bằng lối tắt Tử Cấm Thành ngoài desktop.")) return;
    try { await fetch("/api/dung-han", { method: "POST" }); } catch (e) { /* nó tự thoát */ }
    el("htNoi").innerHTML = `<div class="trong">Đã gửi lệnh tắt.<br>
      <span style="color:var(--fg-3)">Bật lại bằng lối tắt <b>Tử Cấm Thành</b> ngoài desktop.</span></div>`;
  };
}

async function datTuChay(bat) {
  try {
    const r = await fetch("/api/tu-chay", { method: "POST",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify({ bat }) });
    TC = await r.json();
    if (TC.ok === false && TC.loi) alert("Không đổi được: " + TC.loi);
  } catch (e) { alert("Không gọi được runtime: " + e.message); }
  dungBen(); veHeThong();
}

/* ── TẦNG 2 · ĐÀI QUAN SÁT TRADER ──────────────────────────────── */
/* Nguồn: tỉ lệ vị thế công khai của Binance Futures. Miễn phí, không khoá.
   Điều quan trọng nhất ở phòng này là ĐỌC ĐÚNG CHIỀU — xem ghi chú dưới. */
function veQuanSatTrader() {
  const G = W?.phaiSinh;
  const dai = veDaiQuanSat();
  if (!G?.co) {
    el("qstNoi").innerHTML = dai + khoiTheGioiChoLay("Tỉ lệ vị thế toàn sàn");
    noiNutQuanSat();
    return;
  }
  const nhomLs = (ten, g, y) => {
    if (!g || g.tyLe == null) return "";
    const lg = g.long != null ? g.long * 100 : (g.tyLe / (1 + g.tyLe)) * 100;
    const doi = g.doi12h;
    return `<div class="kinh the"><h3>${esc(ten)}
        <span class="cuoi ${doi > 0 ? "len" : doi < 0 ? "xuong" : "mo"}">${
          doi == null ? "" : (doi > 0 ? "▲" : doi < 0 ? "▼" : "") + " " + num(Math.abs(doi), 3) + " / 12h"}</span></h3>
      <div class="so-lon ${lg > 55 ? "len" : lg < 45 ? "xuong" : ""}">${num(lg, 1)}% LONG</div>
      <div class="do-rai" style="margin:8px 0 6px"><div class="do-day len" style="width:${clamp(lg)}%"></div></div>
      <div class="hang"><span>tỉ lệ long/short</span><b>${num(g.tyLe, 3)}</b></div>
      <div class="phu-nho" style="margin-top:6px">${y}</div></div>`;
  };

  el("qstNoi").innerHTML = dai + `
    <div class="luoi c3">
      ${nhomLs("Trader lớn (top)", G.topTrader,
        "Nhóm tài khoản ký quỹ lớn nhất sàn — gần nhất với ý “trader giỏi”.")}
      ${nhomLs("Toàn sàn", G.toanSan,
        "Mọi tài khoản, đếm theo đầu người. Đây là ĐÁM ĐÔNG.")}
      ${nhomLs("Lệnh chủ động (taker)", G.taker,
        "Ai đang chịu trả giá để vào ngay — dòng tiền nóng, không phải vị thế đang giữ.")}
    </div>

    <div class="tieu-muc">Chênh lệch giữa trader lớn và đám đông</div>
    ${(() => {
      const a = G.topTrader?.tyLe, b = G.toanSan?.tyLe;
      if (a == null || b == null) return `<div class="trong">Chưa đủ hai nhóm để so.</div>`;
      const ch = a - b;
      const manh = Math.abs(ch) > 0.5;
      return `<div class="kinh the">
        <div class="so-vua ${ch > 0 ? "len" : "xuong"}">${ch > 0 ? "+" : "−"}${num(Math.abs(ch), 3)}</div>
        <p style="margin:8px 0 0;font-size:12.5px;line-height:1.7;color:var(--fg-2)">
        Trader lớn đang ${ch > 0 ? "<b>nghiêng LONG hơn</b>" : "<b>nghiêng SHORT hơn</b>"} đám đông
        ${manh ? "một cách rõ rệt" : "một chút"}. ${manh
          ? "Chênh lệch rõ thường đáng chú ý hơn con số tuyệt đối của từng nhóm."
          : "Chênh lệch nhỏ — nhiều khả năng chỉ là nhiễu, đừng đọc thành tín hiệu."}</p></div>`;
    })()}

    <div class="tieu-muc">Đọc phòng này thế nào</div>
    <div class="kinh the">
      <p style="margin:0 0 10px;font-size:12.5px;line-height:1.7;color:var(--fg-2)">
      <b>Đây là phòng dễ tự lừa mình nhất, và cái bẫy nằm ở chiều đọc.</b>
      Tỉ lệ toàn sàn là chỉ báo <b>ngược</b> nhiều hơn là chỉ báo thuận: khi 80% tài khoản cùng LONG thì
      phía còn lại để đẩy giá lên đã cạn. Nó đếm theo <i>đầu người</i>, nên một nghìn tài khoản 100 đô
      nặng bằng một nghìn tài khoản một triệu đô.</p>
      <p style="margin:0 0 10px;font-size:12.5px;line-height:1.7;color:var(--fg-2)">
      Nhóm trader lớn có ích hơn, nhưng vẫn không phải mệnh lệnh: họ có thể đang phòng hộ cho một vị thế
      giao ngay mà mình không nhìn thấy, và họ chịu đựng được mức sụt giảm mà tài khoản này không chịu nổi.</p>
      <p style="margin:0;font-size:12.5px;line-height:1.7;color:var(--fg-3)">
      Vì vậy ở đây <b>không</b> có nút “sao chép”. Những con số này là bối cảnh cho bộ não, không phải tín
      hiệu vào lệnh. Chấm điểm trader theo tổng ROI rồi bắt chước là mua lại đúng rủi ro đã sinh ra ROI đó —
      và trên dữ liệu tổng hợp thế này thì còn chẳng tách được <i>giỏi</i> khỏi <i>may</i>.</p>
    </div>
    ${nguonNho(G.nguon, W.luc)}`;
  noiNutQuanSat();
}

/** Nút chạy phễu + nhịp hỏi tiến độ. */
let qsNhip = null;
function noiNutQuanSat() {
  const b = el("qsChay");
  if (b) b.onclick = async () => {
    await fetch("/api/quan-sat", { method: "POST",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify({ moiNhom: 8 }) });
    if (!qsNhip) qsNhip = setInterval(async () => {
      await taiQuanSat();
      if (QS?.trangThai !== "đang chạy") { clearInterval(qsNhip); qsNhip = null; }
      if (phongDangMo === "quan-sat-trader") veQuanSatTrader();
    }, 2000);
    await taiQuanSat(); veQuanSatTrader();
  };
}

/** ĐÀI QUAN SÁT — nghiên cứu trader thật, KHÔNG sao chép họ. */
function veDaiQuanSat() {
  const k = QS?.kho;
  const T = QS?.traders || [];
  const chay = QS?.trangThai === "đang chạy";

  const dinh = `<div class="tieu-muc">Đài quan sát trader · Hyperliquid + OKX</div>
    <div class="kinh the">
      <p style="margin:0 0 10px;font-size:12.5px;line-height:1.8;color:var(--fg-2)">
      Đây là <b>trader-research</b>, không phải copy-trading. Không có nút "sao chép" ở đâu cả:
      đầu ra là những mẫu hành vi lặp lại, và mẫu đó vẫn phải đi qua backtest rồi cửa duyệt
      champion như mọi ý tưởng khác.</p>
      <div class="nut-hang">
        <button class="nut ${k?.co ? "" : "chinh"}" id="qsChay" ${chay ? "disabled" : ""}>
          ${k?.co ? "Chạy lại phễu" : "Chạy phễu quan sát"}</button>
      </div>
      ${chay ? `<div style="margin-top:10px">
        <div class="do-nhan"><span>${esc(QS.viec || "")}</span><b>${QS.phanTram}%</b></div>
        <div class="do-rai"><div class="do-day" style="width:${clamp(QS.phanTram)}%"></div></div>
      </div>` : ""}
      ${QS?.loi ? `<div class="canh-bao" style="margin-top:10px">${esc(QS.loi)}</div>` : ""}
    </div>`;

  if (!k?.co) return dinh + `<div class="trong" style="margin-top:12px">
    Chưa dựng hồ sơ nào. Phễu lọc từ <b>41.794 trader</b> Hyperliquid xuống vài chục hồ sơ sâu —
    mất khoảng 2 phút.</div>`;

  const nhom = (n, ten) => {
    const g = T.filter((t) => t.nhom === n);
    if (!g.length) return "";
    const tb = (f) => { const v = g.map(f).filter((x) => x != null && !isNaN(x));
      return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null; };
    return `<tr><td>${ten}</td><td>${g.length}</td>
      <td class="mono">${num(tb((t) => t.diem.diem), 1)}</td>
      <td class="mono">${num(tb((t) => Number(t.toanThoi?.roi) * 100), 0)}%</td>
      <td class="mono">${num(tb((t) => t.hoSo?.giuTrungVi_gio), 1)}h</td>
      <td class="mono">${num(tb((t) => t.hoSo?.tyLeThang), 1)}%</td>
      <td class="mono">${num(tb((t) => t.hoSo?.soLanThanhLy), 2)}</td></tr>`;
  };

  return dinh + `
    <div class="luoi c4" style="margin-top:12px">
      ${oTk("Hồ sơ đã dựng", k.soTrader, "", `lọc từ ${(k.tongLeaderboard || 0).toLocaleString("vi-VN")} ứng viên`)}
      ${oTk("MASTER + ELITE", (k.theoHang?.MASTER || 0) + (k.theoHang?.ELITE || 0), "len",
        "điểm ≥80 — <b>không</b> xếp theo PnL")}
      ${oTk("Nghi ăn may", k.soNghiNgoAnMay, k.soNghiNgoAnMay ? "nhac" : "",
        "thành tích dồn vào một lệnh, mẫu quá nhỏ, hoặc từng bị thanh lý")}
      ${oTk("Nhóm đang lỗ", k.theoNhom?.dangLo || 0, "",
        "lấy <b>có chủ ý</b> — chống thiên lệch kẻ sống sót")}
    </div>

    <div class="tieu-muc">Ba nhóm so với nhau</div>
    <div class="kinh the" style="overflow-x:auto"><table class="bang">
      <tr><th>nhóm</th><th>n</th><th>điểm</th><th>ROI</th><th>giữ</th><th>thắng</th><th>thanh lý</th></tr>
      ${nhom("dinh", "đỉnh")}${nhom("giua", "giữa")}${nhom("dangLo", "đang lỗ")}
    </table>
    <p style="margin:10px 0 0;font-size:12.5px;line-height:1.8;color:var(--fg-2)">
    Nhóm giữa thường <b>thắng nhiều hơn</b> nhóm đỉnh mà kiếm ít hơn hẳn — họ cắt lãi non.
    Đây đúng là bài học cả hệ thống này đang dạy, nhưng lần này nó đến từ hành vi trader thật
    chứ không phải từ lý thuyết. Nhóm đang lỗ thì giữ lệnh rất ngắn và bị thanh lý nhiều nhất.</p>
    </div>

    <div class="tieu-muc">${Math.min(10, T.length)} hồ sơ điểm cao nhất</div>
    <div class="kinh the" style="overflow-x:auto"><table class="bang">
      <tr><th>điểm</th><th>hạng</th><th>nhóm</th><th>địa chỉ</th><th>ROI</th><th>lệnh</th>
          <th>giữ</th><th>thắng</th><th>1 lệnh</th><th>phủ</th></tr>
      ${T.slice(0, 10).map((t) => {
        const h = t.hoSo || {};
        return `<tr>
          <td class="mono ${t.diem.diem >= 80 ? "len" : ""}">${t.diem.diem}</td>
          <td>${esc(t.diem.hang)}</td><td>${esc(t.nhom)}</td>
          <td class="mono">${esc((t.diaChi || "").slice(0, 10))}…</td>
          <td class="mono">${num(Number(t.toanThoi?.roi) * 100, 0)}%</td>
          <td>${h.soLenh ?? "—"}</td>
          <td class="mono">${num(h.giuTrungVi_gio, 1)}h</td>
          <td class="mono">${num(h.tyLeThang, 1)}%</td>
          <td class="mono ${h.phanTramLaiTuLenhLonNhat > 50 ? "xuong" : ""}">${num(h.phanTramLaiTuLenhLonNhat, 0)}%</td>
          <td class="mono">${t.diem.doPhu}%</td></tr>`;
      }).join("")}
    </table>
    <div class="phu-nho" style="margin-top:8px">
      Cột <b>1 lệnh</b> là phần trăm tổng lãi đến từ một lệnh duy nhất — trên 50% nghĩa là
      thành tích đến từ một cú, không phải một nghề. Cột <b>phủ</b> là bao nhiêu phần trọng số
      điểm thật sự đo được; phần chưa đo không bị cho điểm 0, vì cho 0 là phạt người mình
      chưa buồn đo.</div>
    </div>

    <div class="tieu-muc">Chưa đo được</div>
    <div class="kinh the"><p style="margin:0;font-size:12.5px;line-height:1.8;color:var(--fg-3)">
      <b>Đa dạng chế độ thị trường</b> (5% trọng số) cần ghép từng lệnh với chế độ thị trường tại
      đúng thời điểm đó — mà chế độ hiện chỉ tính cho BTCUSDT, còn trader Hyperliquid vào lệnh
      trên hàng chục coin. Để trống thay vì bịa: bịa ở đây sẽ nghiêng bảng xếp hạng theo một
      chiều không ai kiểm được.<br><br>
      <b>Binance leaderboard</b> trả 404 ở cả hai endpoint — đo tại máy này, đúng như tài liệu
      thiết kế đã ngờ. Nguồn đó bị bỏ chứ không cào lén.</p></div>`;
}

/* ── TẦNG 2 · DÒNG CHẢY THẾ GIỚI ───────────────────────────────── */
function veTheGioi() {
  if (!W?.co) { el("tgNoi").innerHTML = khoiTheGioiChoLay("Dòng chảy thế giới"); return; }
  const V = W.viMo, T = W.tamLy, SK = W.suKien;

  const oViMo = (ma) => {
    const m = V?.muc?.[ma];
    if (!m) return `<div class="kinh the"><h3>${esc(ma)}</h3><div class="so-lon mo">—</div>
      <div class="phu-nho">chưa lấy được</div></div>`;
    return `<div class="kinh the"><h3>${esc(ma)}<span class="cuoi">${esc(m.ten)}</span></h3>
      <div class="so-lon">${num(m.gia, 2)}</div>
      <div class="so-vua ${dau(m.doiPct)}" style="font-size:14px">${m.doiPct > 0 ? "+" : ""}${num(m.doiPct)}%</div></div>`;
  };

  const fg = T?.co ? T.gt : null;
  const fgCls = fg == null ? "mo" : fg < 25 ? "xuong" : fg < 45 ? "nhac" : fg > 75 ? "xuong" : "len";

  el("tgNoi").innerHTML = `
    <div class="tieu-muc">Vĩ mô · Yahoo Finance</div>
    <div class="luoi c5">${["DXY", "US10Y", "DAU", "SP500", "VANG"].map(oViMo).join("")}</div>

    <div class="luoi c2" style="margin-top:12px">
      <div class="kinh the"><h3>Khẩu vị rủi ro</h3>
        <div class="so-vua ${V?.khauVi?.nhan === "RISK_ON" ? "len" : V?.khauVi?.nhan === "RISK_OFF" ? "xuong" : "nhac"}">
          ${esc(V?.khauVi?.nhan || "—")}</div>
        <div class="phu-nho" style="margin-top:6px">điểm ${num(V?.khauVi?.diem)} · từ ${V?.khauVi?.soChiSo ?? 0} chỉ số</div>
        <p style="margin:8px 0 0;font-size:11.5px;color:var(--fg-3);line-height:1.6">
          ${esc(V?.khauVi?.ghiChu || "")}</p></div>

      <div class="kinh the"><h3>Sợ hãi / Tham lam<span class="cuoi">alternative.me</span></h3>
        <div class="so-lon ${fgCls}">${fg ?? "—"}</div>
        <div class="so-vua" style="font-size:14px">${esc(T?.nhan || "")}</div>
        ${T?.chuoi ? `<div class="do-rai" style="margin-top:10px">
          <div class="do-day ${fgCls}" style="width:${clamp(fg)}%"></div>
          <div class="do-nguong" style="left:50%"></div></div>
          <div class="phu-nho" style="margin-top:6px">8 ngày: ${T.chuoi.join(" → ")}
          ${T.doi7ngay != null ? ` · <b class="${dau(T.doi7ngay)}">${T.doi7ngay > 0 ? "+" : ""}${T.doi7ngay}</b>` : ""}</div>` : ""}
      </div>
    </div>

    <div class="tieu-muc">Tin theo chủ đề${SK?.co ? ` · ${SK.soFeed}/${SK.tongFeed} feed · ${SK.soBai} bài` : ""}</div>
    ${SK?.co ? SK.chuDe.map((c) => `
      <div class="kinh the" style="margin-bottom:10px">
        <h3>${esc(c.ma.replace(/_/g, " "))}
          <span class="cuoi">${c.soBai} bài · ảnh hưởng: ${c.anhHuong.join(", ")}</span></h3>
        ${c.soBai ? c.bai.map((b) => `<div class="tin-bai">
            <a href="${esc(b.url || "#")}" target="_blank" rel="noopener">${esc(b.tieuDe)}</a>
            <div class="tin-phu"><span>${esc(b.nguon)}</span>
              <span class="khop" title="từ khoá đã khớp">${esc(b.khop || "")}</span></div>
          </div>`).join("")
          : `<div class="mo" style="font-size:12px">Chưa có tin nào khớp chủ đề này trong 3 ngày.
             Rỗng ở đây nghĩa là <i>không có tin</i>, không phải <i>hỏng</i>.</div>`}
      </div>`).join("") : `<div class="trong">Chưa lấy được tin.</div>`}

    ${SK?.khac?.length ? `<div class="tieu-muc">Không thuộc chủ đề nào</div>
      <div class="kinh the">${SK.khac.map((b) => `<div class="tin-bai">
        <a href="${esc(b.url || "#")}" target="_blank" rel="noopener">${esc(b.tieuDe)}</a>
        <div class="tin-phu"><span>${esc(b.nguon)}</span></div></div>`).join("")}
        <div class="phu-nho" style="margin-top:8px">Giữ lại có chủ đích: thị trường vẫn có thể động vì
        một lý do chưa nằm trong danh sách từ khoá. Bỏ hẳn thì đúng lúc đó phòng này im lặng.</div></div>` : ""}

    <div class="tieu-muc">Giới hạn của phòng này</div>
    <div class="kinh the"><p style="margin:0;font-size:12.5px;line-height:1.7;color:var(--fg-3)">
      Đây mới là <b>thu thập và phân loại</b>, chưa phải chuỗi nhân quả. Mỗi bài mang theo từ khoá đã khớp
      (ô xám bên phải) nên xếp sai là nhìn ra ngay — đó là lý do dùng từ khoá thay vì để một model gán nhãn:
      model rẻ hơn nhưng lúc nó gán sai thì không ai truy được.
      Bước <i>FED → lãi suất → USD → BTC</i> cần một lượt gọi model có schema, và
      <b>phải bắt đầu từ trần chi phí</b>: bản quét tin của Đài Quan Trắc trong repo này từng tốn
      <b>1,4 USD một lượt</b> vì <code>web_search</code> kéo nguyên trang vào ngữ cảnh — ~170 USD/tháng ở
      nhịp 4 lượt/ngày, và đã phải tắt lịch. RSS ở đây thì <b>không tốn gì</b>.</p></div>
    ${nguonNho(SK?.nguon, W.luc)}`;
}

/* Ô chờ chung cho các phòng ăn dữ liệu ngoài. */
function khoiTheGioiChoLay(ten) {
  const dang = W?.dangLay;
  return `<div class="trong">${esc(ten)} — ${dang ? "đang lấy dữ liệu…" : "chưa có dữ liệu."}<br>
    <span style="color:var(--fg-3)">Luồng nguồn ngoài chạy riêng, nhịp 15 phút, không nằm trong vòng giao dịch.
    Lượt đầu mất vài giây sau khi runtime khởi động.</span></div>`;
}

function nguonNho(ten, luc) {
  if (!ten) return "";
  const t = luc ? new Date(luc * 1000) : null;
  return `<div class="phu-nho" style="margin-top:10px;text-align:right">nguồn: ${esc(ten)}${
    t ? " · lấy lúc " + String(t.getHours()).padStart(2, "0") + ":" + String(t.getMinutes()).padStart(2, "0") : ""}</div>`;
}

/* ── TẦNG 3 · CHIẾN LƯỢC ───────────────────────────────────────── */
function veChienLuoc() {
  const perf = J?.performance || {};
  const cl = perf.byStrategy || {};
  const ten = Object.keys(cl);

  el("clNoi").innerHTML = `
    <div class="tieu-muc">Champion · đang chạy</div>
    ${ten.length ? `<div class="luoi c2">${ten.map((k) => {
      const s = cl[k];
      return `<div class="kinh the"><h3>${esc(k)}<span class="cuoi">${s.count} lệnh</span></h3>
        ${hang("tỉ lệ thắng", s.winRate != null ? s.winRate + "%" : "—")}
        ${hang("kỳ vọng", s.expectancyR != null ? s.expectancyR + "R" : "—")}
        ${hang("tổng lãi/lỗ", tien(s.totalPnl), dau(s.totalPnl))}
        ${hang("R trung bình thắng", s.avgWinR ?? "—")}
        ${hang("R trung bình thua", s.avgLossR ?? "—")}
        ${hang("R xấu nhất", s.maxLossR ?? "—", "xuong")}</div>`;
    }).join("")}</div>` : `<div class="trong">Chưa có lệnh nào đóng — chưa có gì để thống kê.</div>`}

    ${CL ? veSoChienLuoc() : `<div class="tieu-muc">Challenger</div>
      <div class="trong">Đang đọc sổ chiến lược…</div>`}`;

  const nut = el("clDanhGia");
  if (nut) nut.onclick = () => hlBatDau("danh-gia", { khoa: nut.dataset.khoa });
  document.querySelectorAll("[data-duyet]").forEach((b) => b.onclick = async () => {
    const r = await (await fetch("/api/chien-luoc", { method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ viec: "duyet", khoa: b.dataset.duyet }) })).json();
    if (!r.ok) alert("Chưa lên được:\n\n" + (r.lyDo || [r.vi_sao || r.viSao]).join("\n"));
    await taiChienLuoc(); veChienLuoc();
  });
}

/** Sổ champion/challenger — phần đáng đọc nhất là LÝ DO BỊ CHẶN. */
function veSoChienLuoc() {
  const c = CL.champion || {};
  const ds = CL.challengers || [];
  const kq = c.ketQua;

  const oKq = (t, nhan) => !t ? `<div class="mo">${nhan}: chưa đo</div>` : `
    <div class="hang"><span>${nhan}</span><b class="${t.kyVongR > 0 ? "len" : "xuong"}">${
      t.kyVongR == null ? "—" : (t.kyVongR > 0 ? "+" : "") + num(t.kyVongR, 3) + "R"
    } · ${t.so} lệnh · sụt ${num(t.sutGiamToiDaPct, 1)}%</b></div>`;

  return `
    <div class="tieu-muc">Champion đang giữ ngôi</div>
    <div class="kinh the">
      <h3>${esc(c.ten || "—")}<span class="cuoi">${esc(c.ma || "")} · bản ${c.phienBan}</span></h3>
      ${hang("tham số", Object.keys(c.tham || {}).length
        ? Object.entries(c.tham).map(([k, v]) => `${k}=${v}`).join(" · ") : "mặc định")}
      ${oKq(kq, "ngoài mẫu")}
      <div class="phu-nho" style="margin-top:6px">giữ ngôi từ ${esc((c.tuLuc || "").slice(0, 16).replace("T", " "))}</div>
    </div>

    <div class="tieu-muc">Challenger · ${ds.length} đang chờ</div>
    ${ds.length ? ds.map((x) => {
      const p = x.phanQuyet;
      return `<div class="kinh the bai-hoc" data-nang="${p ? (p.qua ? "thap" : "cao") : "vua"}" style="margin-bottom:10px">
        <h3>${esc(x.ten)}<span class="cuoi">${esc(x.ma)} · ${esc(x.trangThai)}</span></h3>
        ${x.ghiChu ? `<p style="margin:0 0 8px;font-size:12.5px;color:var(--fg-2)">${esc(x.ghiChu)}</p>` : ""}
        ${oKq(x.ketQua, "ngoài mẫu")}
        ${x.ketQua?.khopTroi != null ? hang("khớp trội", num(x.ketQua.khopTroi, 3) + "R",
          x.ketQua.khopTroi > 0.35 ? "xuong" : "len") : ""}
        ${p ? `<div style="margin-top:10px;padding-top:10px;border-top:1px solid var(--line)">
          <div class="so-vua ${p.qua ? "len" : "xuong"}" style="font-size:14px">${
            p.qua ? "ĐỦ ĐIỀU KIỆN LÊN CHAMPION" : "BỊ CHẶN"}</div>
          ${p.lyDo.map((l) => `<div style="font-size:12px;color:var(--fg-2);padding:4px 0;display:flex;gap:8px">
            <span class="xuong">✗</span><span>${esc(l)}</span></div>`).join("")}
        </div>` : `<div class="phu-nho" style="margin-top:8px">chưa đo — bấm nút dưới</div>`}
        <div class="nut-hang" style="margin-top:10px">
          <button class="nut" id="clDanhGia" data-khoa="${esc(x.khoa)}">Đo lại</button>
          <button class="nut ${p?.qua ? "chinh" : ""}" data-duyet="${esc(x.khoa)}">Cho lên champion</button>
        </div>
      </div>`;
    }).join("") : `<div class="trong">Không có challenger nào đang chờ.</div>`}

    ${CL.lichSu?.length ? `<div class="tieu-muc">Lịch sử thay ngôi</div>
      <div class="kinh the">${CL.lichSu.slice().reverse().map((h) =>
        hang(`${esc(h.thay)} → ${esc(h.bang)}`, esc((h.luc || "").slice(0, 16).replace("T", " ")))).join("")}
      <div class="phu-nho" style="margin-top:8px">Ghi lại để truy được lệnh nào chạy bằng bản nào.</div></div>` : ""}

    <div class="tieu-muc">Cửa duyệt — năm điều kiện, không có đường vòng</div>
    <div class="kinh the">
      <p style="margin:0 0 10px;font-size:12.5px;line-height:1.8;color:var(--fg-2)">
      Không có tầng này thì "cải tiến" là một từ không kiểm chứng được: đổi tham số, thấy số đẹp hơn,
      áp dụng. Mà số đẹp hơn thì <b>luôn</b> tìm được nếu dò đủ lâu — đó là cực trị của nhiễu.
      Đường cong sát thủ bắt đầu đúng từ chỗ đó, và nó không bao giờ trông giống một sai lầm
      khi đang xảy ra.</p>
      <ol style="margin:0;padding-left:20px;font-size:12.5px;line-height:1.9;color:var(--fg-2)">
        <li>Đủ mẫu ngoài mẫu — dưới ${CL.champion?.ketQua ? 20 : 20} lệnh thì mọi con số là nhiễu</li>
        <li>Kỳ vọng ngoài mẫu <b>vượt</b> champion, so trên cùng đoạn dữ liệu</li>
        <li>Kỳ vọng ngoài mẫu phải <b>dương</b> — thắng một champion đang lỗ thì vẫn là lỗ</li>
        <li>Khớp trội dưới ngưỡng — đẹp trong mẫu rồi rơi ngoài mẫu là ảo giác</li>
        <li>Sụt giảm không tệ hơn nhiều — kỳ vọng nhỉnh hơn mà chịu đau gấp đôi thì không phải cải tiến</li>
      </ol>
      <p style="margin:10px 0 0;font-size:12.5px;line-height:1.8;color:var(--fg-3)">
      Không có tham số <code>--force</code>, không có cờ bỏ qua. Muốn cho lên khi chưa qua cửa thì phải
      sửa ngưỡng trong mã, và việc đó để lại dấu vết trong git.</p>
    </div>

    ${CL.triNhoChayLai?.so ? `<div class="tieu-muc">Trí nhớ đúc từ lịch sử</div>
      <div class="kinh the">
        ${hang("bài học từ chạy lại", CL.triNhoChayLai.so)}
        ${hang("rút từ mẫu lặp lại", CL.triNhoChayLai.soDoiChienLuoc, "nhac")}
        ${(CL.triNhoChayLai.ketLuan || []).map((k) =>
          `<p style="margin:8px 0 0;font-size:12.5px;line-height:1.7;color:var(--fg-1)">${esc(k)}</p>`).join("")}
        <div class="phu-nho" style="margin-top:8px">Giữ ở kho <b>riêng</b>, không trộn vào bài học từ lệnh thật:
        lệnh mô phỏng khớp đúng giá đặt và không có nhảy giá qua stop, nên chúng đúng về <b>cấu trúc</b>
        và sai về <b>độ lớn</b>.</div>
      </div>` : ""}`;
}

/* ── TẦNG 3 · PHÒNG HUẤN LUYỆN ─────────────────────────────────── */
/* Phòng duy nhất trong cả app có nút LÀM một việc nặng, nên nó cũng là phòng
   duy nhất phải tự vẽ lại theo tiến độ. Mọi phòng khác chỉ hiển thị. */
let HL = null;          // /api/hoc
let hlNhip = null;      // đồng hồ hỏi tiến độ
/* Mã mức độ để ASCII ở phía runtime, chữ có dấu chỉ nằm ở đây. Móc CSS hay so
   sánh chuỗi vào tiếng Việt có dấu là móc vào dạng chuẩn hoá Unicode — NFC và
   NFD trông giống hệt nhau mà không khớp nhau. */
const NANG = { cao: "cao", vua: "vừa", thap: "thấp" };
const hlTham = { stopAtr: 1.5, demTp: 1.05, adxToiThieu: 0, chanBienDongCao: false,
                 boQuaKill: false, toiDaNenGiu: 48 };

function ngay(ms) {
  const d = new Date(ms);
  return isNaN(d) ? "—" : d.toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric" });
}

/** Thẻ một con số thống kê, kèm cách đọc. */
function oTk(nhan, gt, cls, y) {
  return `<div class="kinh the"><h3>${esc(nhan)}</h3>
    <div class="so-lon ${cls || ""}">${gt}</div>
    ${y ? `<div class="phu-nho" style="margin-top:4px">${y}</div>` : ""}</div>`;
}

function veThongKeChay(tk) {
  const kv = tk.kyVongR;
  return `<div class="luoi c4">
    ${oTk("Kỳ vọng mỗi lệnh", kv == null ? "—" : (kv > 0 ? "+" : "") + num(kv, 3) + "R",
      kv == null ? "mo" : kv > 0 ? "len" : "xuong",
      "<b>Con số quan trọng nhất.</b> Dương thì có cửa, âm thì thắng nhiều đến mấy cũng là chết chậm.")}
    ${oTk("Tỉ lệ thắng", tk.tyLeThang == null ? "—" : num(tk.tyLeThang, 1) + "%", "",
      `${tk.soThang}/${tk.so} lệnh. Một mình nó <b>không</b> nói lên điều gì — chốt lãi non là đẩy được lên 90%.`)}
    ${oTk("Sụt giảm sâu nhất", num(tk.sutGiamToiDaPct, 1) + "%", tk.sutGiamToiDaPct > 15 ? "xuong" : "",
      "Con số quyết định mức risk chịu được, không phải kỳ vọng.")}
    ${oTk("Thua liền dài nhất", tk.chuoiThuaDaiNhat + " lệnh", tk.chuoiThuaDaiNhat >= 6 ? "nhac" : "",
      "Hỏi thật: chuỗi này ở mức risk hiện tại có ngồi yên được không?")}
  </div>
  <div class="luoi c4" style="margin-top:10px">
    ${oTk("Số lệnh", tk.so, "", "Dưới 30 lệnh thì mọi con số trên đây đều là nhiễu.")}
    ${oTk("Hệ số lợi nhuận", tk.heSoLoiNhuan ?? "—", tk.heSoLoiNhuan > 1 ? "len" : "xuong", "tổng lãi ÷ tổng lỗ")}
    ${oTk("R thắng / R thua", `${tk.trungBinhThangR ?? "—"} / ${tk.trungBinhThuaR ?? "—"}`, "",
      "Thua trung bình luôn xấu hơn −1R vì còn phí lần thoát.")}
    ${oTk("Vốn cuối", tien(tk.vonCuoi), dau(tk.loiNhuanPct),
      `${tk.loiNhuanPct > 0 ? "+" : ""}${num(tk.loiNhuanPct)}% · giữ TB ${tk.trungBinhNenGiu} nến`)}
  </div>
  ${tk.theoLyDoThoat ? `<div class="kinh the" style="margin-top:10px"><h3>Thoát lệnh vì</h3>
    <div class="luoi c3">
      ${hang("chạm mục tiêu", tk.theoLyDoThoat.TP ?? 0, "len")}
      ${hang("chạm cắt lỗ", tk.theoLyDoThoat.SL ?? 0, "xuong")}
      ${hang("hết hạn giữ", tk.theoLyDoThoat.HET_HAN ?? 0, "nhac")}
    </div></div>` : ""}`;
}

function veHuanLuyen() {
  const n = el("hlNoi");
  const ss = HL?.sanSang;

  if (!HL) { n.innerHTML = `<div class="trong">Đang hỏi trạng thái phòng huấn luyện…</div>`; return; }

  if (ss && !ss.coNen) {
    n.innerHTML = `<div class="trong">Chưa có nến lịch sử để chạy lại.<br>
      <span style="color:var(--fg-3)">Chạy lệnh này một lần rồi mở lại phòng:</span>
      <div class="ma-lenh">${esc(ss.goiY)}</div></div>`;
    return;
  }

  const chay = HL.trangThai === "đang chạy";
  const kq = HL.ketQua;

  const oTham = (khoa, nhan, buoc, y) => `<label class="tham">
    <span>${esc(nhan)}</span>
    <input type="number" step="${buoc}" value="${hlTham[khoa]}" data-tham="${khoa}" ${chay ? "disabled" : ""}>
    <i>${esc(y)}</i></label>`;

  n.innerHTML = `
    <div class="kinh the">
      <h3>Dữ liệu<span class="cuoi">${esc(ss?.symbol || "")}</span></h3>
      <div class="luoi c3">
        ${hang("nến", Object.entries(ss?.soNen || {}).map(([k, v]) => `${k}: ${v}`).join(" · "))}
        ${hang("khoảng", `${ngay(ss?.tu)} → ${ngay(ss?.den)}`)}
        ${hang("chuỗi tín hiệu", ss?.coChuoiSan ? "đã dựng sẵn — chạy tức thì" : "chưa dựng — lượt đầu ~6 phút",
          ss?.coChuoiSan ? "len" : "nhac")}
      </div>
    </div>

    <div class="tieu-muc">Tham số chiến lược</div>
    <div class="kinh the">
      <div class="luoi c4">
        ${oTham("stopAtr", "SL cách giá (×ATR)", "0.1", "hẹp thì chết vì nhiễu, rộng thì một lệnh nuốt cả tuần")}
        ${oTham("demTp", "Đệm mục tiêu (×)", "0.05", "1.0 = đặt TP sát mức RR tối thiểu")}
        ${oTham("adxToiThieu", "ADX tối thiểu", "1", "0 = không lọc thêm")}
        ${oTham("toiDaNenGiu", "Giữ tối đa (nến)", "1", "quá hạn thì thoát ở giá đóng cửa")}
      </div>
      <div class="hang" style="margin-top:10px">
        <span>Bỏ qua lệnh khi biến động cao</span>
        <input type="checkbox" data-tham="chanBienDongCao" ${hlTham.chanBienDongCao ? "checked" : ""} ${chay ? "disabled" : ""}>
      </div>
      <div class="hang">
        <span>Tắt ngắt mạch để đo hết đoạn <i style="color:var(--fg-4)">(đo lợi thế thô, KHÔNG phải cách chạy thật)</i></span>
        <input type="checkbox" data-tham="boQuaKill" ${hlTham.boQuaKill ? "checked" : ""} ${chay ? "disabled" : ""}>
      </div>
      <div class="nut-hang" style="margin-top:12px">
        <button class="nut chinh" id="hlChay" ${chay ? "disabled" : ""}>Chạy lại lịch sử</button>
        <button class="nut" id="hlQuet" ${chay ? "disabled" : ""}>Dò tham số (${
          Object.values(ss?.luoiMacDinh || {}).reduce((a, b) => a * b.length, 1)} tổ hợp)</button>
      </div>
      ${chay ? `<div style="margin-top:12px">
        <div class="do-nhan"><span>${esc(HL.viec || "")}</span><b>${HL.phanTram}%</b></div>
        <div class="do-rai"><div class="do-day" style="width:${clamp(HL.phanTram)}%"></div></div>
      </div>` : ""}
      ${HL.loi ? `<div class="canh-bao" style="margin-top:10px">${esc(HL.loi)}</div>` : ""}
    </div>

    ${kq ? (HL.viec === "quet" ? veKetQuaQuet(kq) : veKetQuaChay(kq)) : `
      <div class="trong" style="margin-top:12px">Chưa chạy lượt nào.<br>
      <span style="color:var(--fg-3)">“Chạy lại” đo bộ tham số đang đặt ở trên.
      “Dò tham số” thử tất cả tổ hợp, chọn trên phần dữ liệu đầu rồi chấm điểm trên phần cuối chưa từng đụng tới.</span></div>`}`;

  n.querySelectorAll("[data-tham]").forEach((i) => {
    i.onchange = () => {
      hlTham[i.dataset.tham] = i.type === "checkbox" ? i.checked : Number(i.value);
    };
  });
  const bam = (id, viec) => { const b = el(id); if (b) b.onclick = () => hlBatDau(viec); };
  bam("hlChay", "chay-lai");
  bam("hlQuet", "quet");
}

function veKetQuaChay(kq) {
  const tk = kq.thongKe, d = kq.dungSom;
  return `
    ${d ? `<div class="canh-bao" style="margin-top:12px">
      <b>Dừng sớm ở ${ngay(d.luc)}</b> — ${esc(d.lyDo)}.
      Chỉ đo được ${d.phanTramDaXet}% đoạn dữ liệu (bỏ dở ${d.soNenBoDo} nến).
      Ngắt mạch là chốt cứng, đúng như bản chạy thật. Muốn đo hết đoạn thì bật
      “tắt ngắt mạch” ở trên — nhưng đó là đo lợi thế thô, không phải cách hệ thống hành xử.
    </div>` : ""}

    <div class="tieu-muc">Kết quả${kq.nguonChuoi ? ` · chuỗi tín hiệu từ ${esc(kq.nguonChuoi)}` : ""}</div>
    ${tk.so === 0 ? `<div class="trong">Không lệnh nào qua được Risk Engine.</div>` : veThongKeChay(tk)}

    ${kq.baiHoc?.length ? `<div class="tieu-muc">Bài học đúc ra</div>
      ${kq.baiHoc.map((b) => `<div class="kinh the bai-hoc" data-nang="${esc(b.nang)}" style="margin-bottom:10px">
        <h3>${esc(b.muc.replace(/_/g, " "))}<span class="cuoi">${esc(NANG[b.nang] || b.nang)}</span></h3>
        <p style="margin:0 0 8px;font-size:13px;line-height:1.7;color:var(--fg-1)">${esc(b.cau)}</p>
        <div class="hang"><span>số liệu</span><b class="mono">${esc(b.so)}</b></div>
        <p style="margin:8px 0 0;font-size:12.5px;line-height:1.7;color:var(--fg-2)">
          <b style="color:var(--amber)">Làm gì:</b> ${esc(b.lam)}</p>
      </div>`).join("")}` : ""}

    ${Object.keys(kq.theoRegime || {}).length ? `<div class="tieu-muc">Theo chế độ thị trường</div>
      <div class="kinh the"><table class="bang">
        <tr><th>chế độ</th><th>lệnh</th><th>thắng</th><th>R trung bình</th></tr>
        ${Object.entries(kq.theoRegime).sort((a, b) => b[1].so - a[1].so).map(([k, v]) =>
          `<tr><td>${esc(k)}</td><td>${v.so}</td><td>${num(v.tyLeThang, 1)}%</td>
           <td class="${v.trungBinhR > 0 ? "len" : "xuong"}">${v.trungBinhR > 0 ? "+" : ""}${num(v.trungBinhR, 3)}R</td></tr>`).join("")}
      </table>
      <div class="phu-nho" style="margin-top:8px">Dòng dưới 5 lệnh chỉ là nhiễu — đừng rút kết luận từ chúng.</div></div>` : ""}

    ${Object.keys(kq.tuChoi || {}).length ? `<div class="tieu-muc">Vì sao bị chặn</div>
      <div class="kinh the">${Object.entries(kq.tuChoi).map(([k, v]) =>
        hang(k.replace(/_/g, " "), v)).join("")}
      <div class="phu-nho" style="margin-top:8px">Bị chặn nhiều không hẳn xấu — Risk Engine đứng chắn là
      việc của nó. Nhưng nếu một lý do chiếm gần hết thì đó là chỗ nới sẽ đổi được nhiều nhất.</div></div>` : ""}

    ${kq.lenh?.length ? `<div class="tieu-muc">${kq.lenh.length} lệnh gần nhất</div>
      <div class="kinh the" style="overflow-x:auto"><table class="bang">
        <tr><th>lúc</th><th>phía</th><th>vào</th><th>SL</th><th>TP</th><th>ra</th><th>vì</th><th>nến</th><th>R</th><th>vốn</th></tr>
        ${kq.lenh.slice().reverse().map((t) => `<tr>
          <td class="mono">${ngay(t.t)}</td>
          <td class="${t.side === "LONG" ? "len" : "xuong"}">${t.side}</td>
          <td class="mono">${num(t.entry)}</td><td class="mono">${num(t.sl)}</td>
          <td class="mono">${num(t.tp)}</td><td class="mono">${num(t.exit)}</td>
          <td><span class="the-nho ${t.lyDo === "TP" ? "len" : t.lyDo === "SL" ? "xuong" : "nhac"}">${t.lyDo}</span></td>
          <td>${t.soNenGiu}</td>
          <td class="mono ${t.R > 0 ? "len" : "xuong"}">${t.R > 0 ? "+" : ""}${num(t.R, 2)}</td>
          <td class="mono">${num(t.von, 0)}</td></tr>`).join("")}
      </table></div>` : ""}`;
}

function veKetQuaQuet(q) {
  const tn = q.totNhat;
  const bang = (q.bang || []).filter((b) => b.duMau)
    .sort((a, b) => (b.kyVongR ?? -9) - (a.kyVongR ?? -9)).slice(0, 12);

  return `
    <div class="tieu-muc">Kết luận</div>
    <div class="kinh the ket-luan">
      <p style="margin:0;font-size:14px;line-height:1.8;color:var(--fg-1)">${esc(q.ketLuan)}</p>
      <div class="phu-nho" style="margin-top:10px">
        ${q.soToHop} tổ hợp · ${q.giay}s · cắt trong/ngoài mẫu tại nến ${q.mocCat}/${q.tongNen}
        ${q.boQuaKill ? " · ngắt mạch đã tắt để so được các tổ hợp với nhau" : ""}</div>
    </div>

    ${tn ? `<div class="tieu-muc">Bộ tốt nhất trong mẫu, chấm điểm ngoài mẫu</div>
      <div class="kinh the">
        <div class="mono" style="font-size:13px;margin-bottom:12px;color:var(--amber)">${
          Object.entries(tn.bo).map(([k, v]) => `${k}=${v}`).join("  ·  ")}</div>
        <div class="luoi c3">
          ${oTk("Trong mẫu", (tn.trongMau.kyVongR > 0 ? "+" : "") + num(tn.trongMau.kyVongR, 3) + "R",
            tn.trongMau.kyVongR > 0 ? "len" : "xuong",
            `${tn.trongMau.so} lệnh · thắng ${num(tn.trongMau.tyLeThang, 1)}% — <b>đây là phần đã dùng để CHỌN</b>, nên nó luôn đẹp`)}
          ${oTk("Ngoài mẫu", tn.ngoaiMau.kyVongR == null ? "—"
              : (tn.ngoaiMau.kyVongR > 0 ? "+" : "") + num(tn.ngoaiMau.kyVongR, 3) + "R",
            tn.ngoaiMau.kyVongR > 0 ? "len" : "xuong",
            `${tn.ngoaiMau.so} lệnh · thắng ${num(tn.ngoaiMau.tyLeThang, 1)}% — <b>chỉ con số này mới có nghĩa</b>`)}
          ${oTk("Khớp trội", tn.khopTroi == null ? "—" : num(tn.khopTroi, 3) + "R",
            tn.khopTroi > 0.2 ? "xuong" : "len",
            "Phần kỳ vọng bốc hơi khi ra khỏi dữ liệu đã dùng để chọn. Càng lớn càng là ảo giác.")}
        </div>
      </div>` : ""}

    <div class="tieu-muc">Bảng dò · sắp theo kỳ vọng TRONG mẫu</div>
    <div class="kinh the" style="overflow-x:auto">
      ${bang.length ? `<table class="bang">
        <tr><th>SL ×ATR</th><th>đệm TP</th><th>ADX ≥</th><th>chặn b.động</th>
            <th>lệnh</th><th>thắng</th><th>kỳ vọng</th><th>sụt</th></tr>
        ${bang.map((b, i) => `<tr class="${i === 0 ? "dau" : ""}">
          <td class="mono">${b.bo.stopAtr}</td><td class="mono">${b.bo.demTp}</td>
          <td class="mono">${b.bo.adxToiThieu || "—"}</td><td>${b.bo.chanBienDongCao ? "có" : "—"}</td>
          <td>${b.so}</td><td>${num(b.tyLeThang, 1)}%</td>
          <td class="mono ${b.kyVongR > 0 ? "len" : "xuong"}">${b.kyVongR > 0 ? "+" : ""}${num(b.kyVongR, 3)}R</td>
          <td>${num(b.sutGiamToiDaPct, 1)}%</td></tr>`).join("")}
      </table>` : `<div class="trong">Không tổ hợp nào vào đủ ${q.toiThieuLenh} lệnh.</div>`}
    </div>

    <div class="tieu-muc">Vì sao bảng này không phải danh sách để chọn</div>
    <div class="kinh the"><p style="margin:0;font-size:12.5px;line-height:1.8;color:var(--fg-2)">
      Dòng đầu bảng <b>luôn</b> đẹp. Nó đẹp kể cả khi chiến lược hoàn toàn vô dụng — dò càng nhiều tổ hợp
      thì con số đứng đầu càng cao, vì đó là cực trị của nhiễu chứ không phải lợi thế.
      Đó là lý do dữ liệu bị cắt đôi: bảng này chọn trên phần đầu, rồi bộ thắng bị đem ra chấm lại trên phần
      cuối mà nó <b>chưa từng thấy</b>. Chỉ con số ngoài mẫu mới đáng tin, và
      <b>“khớp trội” chính là khoảng cách giữa cái mình tưởng và cái có thật.</b></p>
      <p style="margin:10px 0 0;font-size:12.5px;line-height:1.8;color:var(--fg-3)">
      Ngay cả khi ngoài mẫu vẫn dương: một đoạn sáu tháng chỉ chứa vài chế độ thị trường.
      Bước kế tiếp đúng đắn không phải áp dụng luôn, mà là chạy lại trên đoạn khác và trên cặp khác.</p></div>`;
}

async function hlBatDau(viec, phu = {}) {
  const than = viec === "danh-gia" ? { viec, ...phu }
    : viec === "quet"
    ? { viec, tyLeTrongMau: 0.7 }
    : { viec, tham: { stopAtr: hlTham.stopAtr, demTp: hlTham.demTp,
                      adxToiThieu: hlTham.adxToiThieu, chanBienDongCao: hlTham.chanBienDongCao },
        boQuaKill: hlTham.boQuaKill, toiDaNenGiu: hlTham.toiDaNenGiu };
  try {
    await fetch("/api/hoc", { method: "POST", headers: { "Content-Type": "application/json" },
                              body: JSON.stringify(than) });
  } catch (e) { /* hỏi tiến độ ngay sau đây sẽ lộ ra lỗi */ }
  taiHoc();
  hlBatNhip();
}

function hlBatNhip() {
  if (hlNhip) return;
  hlNhip = setInterval(async () => {
    await taiHoc();
    if (HL?.trangThai !== "đang chạy") { clearInterval(hlNhip); hlNhip = null; await taiChienLuoc(); }
    if (phongDangMo === "huan-luyen") veHuanLuyen();
  }, 1200);
}

async function taiHoc() {
  try { HL = await (await fetch("/api/hoc")).json(); } catch (e) { /* giữ bản cũ */ }
}

/* ── TẦNG 3 · HỌC ──────────────────────────────────────────────── */
const VONG_DOI = ["PHÁT HIỆN", "BACKTEST", "KIỂM CHỨNG", "CHALLENGER", "LÊN CHẠY"];

function veHoc() {
  const ls = J?.lessons || [];
  const doi = ls.filter((l) => l.change_strategy).length;

  const homNay = new Date().toISOString().slice(0, 10);
  const hnLs = ls.filter((l) => (l.at || "").slice(0, 10) === homNay);

  el("hocNoi").innerHTML = `
    <div class="kinh the" style="margin-bottom:12px"><h3>Hôm nay</h3>
      <div class="luoi c4">
        ${hang("lệnh đã soi lại", hnLs.length)}
        ${hang("lỗi tìm ra", hnLs.filter((l) => l.thesis_was_wrong || !l.entry_valid || !l.stop_placement_valid).length)}
        ${hang("bài học mới", hnLs.length)}
        ${hang("chiến lược bị đổi", hnLs.filter((l) => l.change_strategy).length)}
      </div></div>
    <div class="luoi c4">
      ${oSo("Lệnh đã hậu kiểm", ls.length)}
      ${oSo("Quyết định tốt", ls.filter((l) => (l.classification || "").startsWith("GOOD_TRADE")).length, "len")}
      ${oSo("Quyết định tồi", ls.filter((l) => (l.classification || "").startsWith("BAD_TRADE")).length, "xuong")}
      ${oSo("Đề nghị đổi chiến lược", doi, doi ? "nhac" : "mo", "cửa hẹp — cần mẫu lặp lại")}
    </div>
    <div class="luoi c4" style="margin-top:12px">
      ${oSo("Phát hiện đã chưng", (J?.phatHien || []).length, "", "từ chạy lại · lệnh thật · trader ngoài · champion")}
      ${oSo("Bằng chứng mạnh", (J?.phatHien || []).filter((x) => x.doTin === "CAO").length, "len", "cỡ mẫu ≥ 3× ngưỡng nguồn")}
      ${oSo("Chế độ bị ngắt", (J?.phatHien || []).filter((x) =>
          x.nguon === "chay-lai" && x.doTin === "CAO" && (x.so?.kyVongR ?? 0) <= -0.25 && (x.mau || 0) >= 30
        ).length, "xuong", "cầu dao: đo ra lỗ đều thì không vào lệnh nữa")}
      ${oSo("Mẫu lớn nhất", Math.max(0, ...(J?.phatHien || []).map((x) => x.mau || 0)), "", "so với 8 lệnh thật")}
    </div>

    <div class="tieu-muc">Phát hiện — gộp từ MỌI kho đo</div>
    ${(() => {
      const pd = J?.phatHien || [];
      if (!pd.length) return `<div class="trong">Lò chưng cất chưa chạy lần nào. Chạy tay: <b class="mono">python scripts/chung-cat.py</b></div>`;
      // Xếp theo bằng chứng, giống hệt thứ tự bộ não đọc. Bảng xếp một kiểu còn
      // bộ não đọc kiểu khác thì người xem không đối chiếu được hai bên.
      const hang3 = { "CAO": 0, "VỪA": 1, "THẤP": 2 };
      const NGUON = {
        "chien-luoc": ["chiến lược đang chạy", "len"],
        "chay-lai": ["chạy lại lịch sử", "nhac"],
        "so-that": ["lệnh thật", "len"],
        "dai-quan-sat": ["trader ngoài", "mo"],
      };
      return pd.slice().sort((a, b) =>
        (hang3[a.doTin] ?? 3) - (hang3[b.doTin] ?? 3) || (b.mau || 0) - (a.mau || 0)
      ).map((x) => {
        const [ten, cls] = NGUON[x.nguon] || [x.nguon, "mo"];
        return `<div class="kinh the" style="margin-bottom:10px">
          <h3><span class="${cls}">${esc(ten)}</span>
            <span class="cuoi">${esc(x.doTin)} · mẫu ${x.mau}${x.cheDo ? " · " + esc(x.cheDo) : ""}</span></h3>
          <p style="margin:0;font-size:13px;line-height:1.7;color:var(--fg-2)">${esc(x.cau)}</p>
        </div>`;
      }).join("");
    })()}

    <div class="tieu-muc">Bài học</div>
    ${ls.length ? ls.slice().reverse().map((l) => {
      const c = l.classification || "";
      const k = c.startsWith("BAD_TRADE") ? "xau" : c.includes("BAD_OUTCOME") ? "canh" : "tot";
      const buoc = l.change_strategy ? 1 : 0;
      return `<div class="kinh the" style="margin-bottom:10px">
        <h3><span class="${k === "xau" ? "xuong" : k === "canh" ? "nhac" : "len"}">${esc(c)}</span>
          <span class="cuoi">${l.soatLai ? '<span class="nhac">đã soát lại</span> · ' : ""}${esc(l.regime || "—")} · ${l.rMultiple ?? "—"}R · ${esc(l.exitReason || "")}</span></h3>
        <p style="margin:0 0 10px;font-size:13px;line-height:1.7;color:var(--fg-2)">${esc(l.lesson)}</p>
        <div class="luoi c4" style="gap:6px;margin-bottom:10px">
          ${[["chế độ hợp", l.regime_appropriate], ["điểm vào hợp lệ", l.entry_valid],
             ["size hợp lệ", l.size_valid], ["stop đặt đúng", l.stop_placement_valid]].map(([t, v]) =>
            `<div class="hang" style="border:0;padding:2px 0"><span>${t}</span><b class="${v ? "len" : "xuong"}">${v ? "✓" : "✗"}</b></div>`).join("")}
        </div>
        <div class="doi">${VONG_DOI.map((b, i) =>
          (i ? '<span class="doi-n"></span>' : "") +
          `<span class="doi-b ${i < buoc ? "qua" : i === buoc ? "hien" : ""}">${b}</span>`).join("")}</div>
        ${l.change_strategy ? "" : `<div style="font-size:11px;color:var(--fg-4);margin-top:6px">
          Dừng ở “phát hiện”: một lệnh không đủ cớ để đổi chiến lược. Cần mẫu lặp lại qua nhiều lệnh.</div>`}
        ${l.soatLai ? `<div style="font-size:11px;color:var(--fg-4);margin-top:6px">
          Bài học này được hậu kiểm LẠI khi sổ đã dài hơn. Bản đúc lần đầu — lúc chưa tồn tại “mức cược thường” để so — vẫn còn nguyên trong <b class="mono">lessons.jsonl</b>.</div>` : ""}
      </div>`;
    }).join("") : `<div class="trong">Chưa có bài học nào — bài học chỉ sinh ra sau khi một lệnh đóng lại.</div>`}`;
}

/* ── TẦNG 1 · THỊ TRƯỜNG ───────────────────────────────────────── */
function veThiTruong() {
  const p = S?.marketState?.timeframes?.[S?.timeframes?.primary] || {};
  el("ttNoi").innerHTML = khoiBieuDo("cvThiTruong", 420) + `
    <div class="luoi c2" style="margin-top:12px">
      <div class="kinh the"><h3>Vùng giá bộ não đang nhìn</h3>
        ${hang("kháng cự", (p.resistance || []).map((z) => `${num(z.price)} (${z.touches}×)`).join("  ·  ") || "—", "xuong")}
        ${hang("giá hiện tại", num(S?.price), "lam")}
        ${hang("hỗ trợ", (p.support || []).map((z) => `${num(z.price)} (${z.touches}×)`).join("  ·  ") || "—", "len")}
        ${hang("biên 20 nến", `${num(p.range20Low)} … ${num(p.range20High)}`)}
        ${hang("cách đỉnh biên", pct(p.distToRange20HighPct))}
        ${hang("cách đáy biên", pct(p.distToRange20LowPct))}
      </div>
      <div class="kinh the"><h3>Chỉ báo · khung ${esc(S?.timeframes?.primary || "")}</h3>
        ${hang("EMA 20 / 50 / 200", `${num(p.ema20)} · ${num(p.ema50)} · ${num(p.ema200)}`)}
        ${hang("xếp EMA", p.emaStack)}
        ${hang("RSI(14)", `${num(p.rsi14, 1)} (${p.rsiSlope > 0 ? "↑" : p.rsiSlope < 0 ? "↓" : "→"})`)}
        ${hang("MACD hist", `${num(p.macdHist)} (${p.macdHistSlope > 0 ? "↑" : "↓"})`)}
        ${hang("ADX / +DI / −DI", `${num(p.adx, 1)} · ${num(p.plusDI, 1)} · ${num(p.minusDI, 1)}`)}
        ${hang("ATR", `${num(p.atr)} (${pct(p.atrPct, 3)}) · ×${num(p.atrRatioVsMedian)} trung vị`)}
        ${hang("Bollinger", `rộng ${pct(p.bbWidthPct)} · vị trí ${num(p.bbPosition)}`)}
        ${hang("volume", "×" + num(p.volumeRatio))}
        ${hang("cấu trúc", p.structure)}
      </div>
    </div>
    <div style="margin-top:12px">${chuaCo("Chỉ một cặp",
      "Bản thiết kế có BTC · ETH · SOL trên thanh đỉnh. M0 chạy <b>một cặp duy nhất</b> " +
      `(<code>${esc(S?.symbol || "")}</code>) — thêm cặp không chỉ là thêm dòng cấu hình.`,
      ["Vòng lặp phải chạy song song nhiều cặp mà không nhân số lượt gọi model lên theo",
       "Risk Engine phải biết <b>tương quan</b>: 3 lệnh long BTC/ETH/SOL là một lệnh lớn đội lốt phân tán",
       "Trần rủi ro phải tính trên toàn danh mục, không phải từng cặp riêng"])}</div>`;
  veBieuDoVao("cvThiTruong", 420);
}

/* ── TẦNG 3 · TRÍ NHỚ ──────────────────────────────────────────── */
function veTriNho() {
  const t = J?.trades || [], l = J?.lessons || [], perf = J?.performance || {};
  const theoRegime = Object.entries(perf.byRegime || {});

  el("tnNoi").innerHTML = `<div class="luoi c2">
    <div class="kinh the"><h3>1 · Episodic<span class="cuoi">từng giao dịch</span></h3>
      <div class="so-lon">${t.length}</div>
      <div class="phu-nho">bản ghi nguyên trạng: giá vào/ra, chế độ lúc vào, lý do thoát, R thu được.
      Đây là thứ mọi loại trí nhớ khác được tính ra từ đó.</div>
      <div class="hang" style="margin-top:8px"><span>file</span><b class="mono">data/trades.jsonl</b></div></div>

    <div class="kinh the"><h3>2 · Semantic<span class="cuoi">bài học đã hậu kiểm</span></h3>
      <div class="so-lon ${l.length ? "tim" : ""}">${l.length}</div>
      <div class="phu-nho">không phải bản tóm tắt giao dịch — là kết luận sau khi trả lời bảy câu hỏi,
      trong đó câu quan trọng nhất là “luận điểm có sai không, hay chỉ là một lần thua bình thường”.</div>
      <div class="hang" style="margin-top:8px"><span>file</span><b class="mono">data/lessons.jsonl</b></div></div>

    <div class="kinh the"><h3>3 · Procedural<span class="cuoi">kỹ năng &amp; luật</span></h3>
      <div class="so-lon">${K?.tong ?? "—"}</div>
      <div class="phu-nho">kho kỹ năng trên đĩa + các trần cứng trong <code>config.json</code>.
      Sửa được mà không phải deploy lại, và đọc git log của nó là thấy bot đã học thêm những gì.</div>
      <div class="hang" style="margin-top:8px"><span>nơi giữ</span><b class="mono">skills/ · config.json</b></div></div>

    <div class="kinh the"><h3>4 · Performance<span class="cuoi">cái gì hiệu quả ở đâu</span></h3>
      <div class="so-lon">${theoRegime.length}</div>
      <div class="phu-nho">thống kê cắt theo <b>chế độ thị trường</b> — vì không có chiến lược nào
      tốt cho mọi thị trường, và một tỉ lệ thắng gộp chung che mất đúng điều đó.</div>
      ${theoRegime.map(([k, v]) => hang(k, v.count ? `${v.count} lệnh · ${v.winRate}% · ${v.expectancyR}R` : "chưa có")).join("")}
    </div></div>

    <div class="tieu-muc">Truy hồi — thứ làm trí nhớ có ích</div>
    <div class="kinh the">
      <p style="margin:0 0 10px;font-size:12.5px;color:var(--fg-3);line-height:1.7">
      Trí nhớ chỉ có giá trị nếu được lấy ra <b>đúng lúc</b>. Mỗi lượt phân tích, hệ thống lọc theo chế độ
      thị trường hiện tại trước, rồi mới tới bài học chung — nhét cả nghìn bài học vào mỗi prompt thì vừa
      đắt vừa loãng, và bài học đúng chìm nghỉm giữa bài học lạc đề.</p>
      ${hang("chế độ hiện tại", S?.regime?.key || "—", "lam")}
      ${hang("bài học hợp chế độ này", l.filter((x) => x.regimeKey === S?.regime?.key).length)}
      ${hang("bài học cùng chế độ chính", l.filter((x) => x.regime === S?.regime?.primary).length)}
      ${hang("bài học đòi đổi chiến lược", l.filter((x) => x.change_strategy).length, "nhac")}
    </div>`;
}

/* ── TẦNG 3 · KHO KỸ NĂNG ──────────────────────────────────────── */
function veKyNang() {
  if (!K) { el("knNoi").innerHTML = '<div class="trong">Đang đọc kho kỹ năng…</div>'; return; }
  el("knNoi").innerHTML = `
    <div class="luoi c4">
      ${oSo("Kỹ năng", K.tong, "tim")}
      ${oSo("Tổng dòng", (K.skills || []).reduce((s, x) => s + x.soDong, 0))}
      ${oSo("Nạp vào prompt", S?.brain?.skillsLoaded ?? "—", "", "được cache theo prefix")}
      ${oSo("Bộ não", S?.brain?.mode === "claude" ? "CLAUDE" : "MOCK",
          S?.brain?.mode === "claude" ? "tim" : "nhac", S?.brain?.mode === "claude" ? "" : "kỹ năng chỉ dùng khi gọi model thật")}
    </div>
    <div class="kinh the" style="margin-top:12px">
      <h3>Vì sao kỹ năng nằm ngoài code</h3>
      <p style="margin:0;font-size:12.5px;color:var(--fg-3);line-height:1.7">
      Bộ não không nhét mọi kiến thức vào một prompt khổng lồ. Kho kỹ năng nằm ở <code>skills/</code>,
      nạp vào phần <b>ổn định</b> của system prompt nên được prompt-caching trả về rẻ; dữ liệu biến thiên
      (giá, chỉ báo) đi trong message. Sửa một kỹ năng không phải deploy lại gì cả.</p>
    </div>
    <div class="tieu-muc">Danh sách</div>
    ${(K.skills || []).map((s) => `<div class="kinh the" style="margin-bottom:9px">
      <h3>${esc(s.tieuDe)}<span class="cuoi mono">${s.soDong} dòng · ${(s.soKyTu / 1024).toFixed(1)} KB</span></h3>
      <div style="font-size:12.5px;color:var(--fg-3);line-height:1.6">${esc(s.moTa)}</div>
      <div class="hang" style="margin-top:6px"><span>đường dẫn</span><b class="mono">skills/${esc(s.ma)}/SKILL.md</b></div>
    </div>`).join("") || '<div class="trong">Không tìm thấy kỹ năng nào.</div>'}`;
}

/* ── TẦNG 3 · NHẬT KÝ ──────────────────────────────────────────── */
function veNhatKy() {
  const td = (J?.trades || []).slice().reverse();
  const ls = J?.lessons || [];
  const perf = (J?.performance || {}).overall || {};

  el("nkNoi").innerHTML = `
    ${perf.canhBao ? `<div class="canh-bao" style="margin-bottom:12px">
      <b>Hai con số đang lệch dấu.</b> ${esc(perf.canhBao)}</div>` : ""}
    <div class="luoi c4">
      ${oSo("Tổng lệnh", perf.count ?? 0)}
      ${oSo("Tỉ lệ thắng", perf.winRate != null ? perf.winRate + "%" : "—", "",
          "một mình nó không nói lên gì — đọc kèm R thắng/thua")}
      ${oSo("Kỳ vọng mỗi lệnh",
          perf.expectancyUsd != null ? tien(perf.expectancyUsd) : "—",
          dau(perf.expectancyUsd),
          perf.expectancyR != null
            ? `${perf.expectancyR > 0 ? "+" : ""}${perf.expectancyR}R · ` +
              (perf.riskDeu === false
                ? "<b class='nhac'>rủi ro KHÔNG đều</b> nên R không so được"
                : "rủi ro đều nên R so được")
            : "")}
      ${oSo("Tổng lãi/lỗ", tien(perf.totalPnl), dau(perf.totalPnl),
          perf.riskCv != null ? `độ lệch rủi ro ${num(perf.riskCv, 2)}` : "")}
    </div>

    <div class="tieu-muc">Dòng thời gian</div>
    ${td.length ? `<div class="kinh the">${td.slice(0, 25).map((t) => {
      const l = ls.find((x) => x.tradeId === t.id);
      const c = l?.classification || "";
      const k = c.startsWith("BAD_TRADE") ? "xau" : c.includes("BAD_OUTCOME") ? "canh" : c ? "tot" : "";
      return `<div class="dong ${k}">
        <div class="gio">${gio(t.closedAt || t.openedAt)}</div>
        <div class="vach"></div>
        <div class="noi">
          <b>${esc(t.symbol || "")} ${esc(t.side)} đóng · <span class="${dau(t.pnl)}">${tien(t.pnl)} (${t.rMultiple ?? "—"}R)</span></b>
          <p>vào ${num(t.entry)} → ra ${num(t.exit)} · ${esc(t.exitReason || "")} · chế độ ${esc(t.regimeAtEntry || "—")}
          ${c ? `<br>hậu kiểm: <b class="${k === "xau" ? "xuong" : k === "canh" ? "nhac" : "len"}">${esc(c)}</b>` : ""}
          ${l?.lesson ? `<br>${esc(l.lesson.slice(0, 160))}` : ""}</p>
        </div></div>`;
    }).join("")}</div>` : `<div class="trong">Chưa có giao dịch nào đóng.</div>`}

    <div class="tieu-muc">Mọi luận điểm, kể cả cái bị chặn</div>
    ${(J?.theses || []).length ? `<div class="cuon"><table><thead><tr>
      <th>lúc</th><th>hành động</th><th>tin cậy</th><th>chế độ</th><th>chiến lược</th><th>nguồn</th></tr></thead><tbody>
      ${J.theses.slice(0, 25).map((t) => `<tr>
        <td>${gio(t.at)}</td>
        <td class="${t.action === "LONG" ? "len" : t.action === "SHORT" ? "xuong" : "nhac"}">${esc(t.action)}</td>
        <td>${num(t.confidence, 2)}</td><td>${esc(t.regime_read || "—")}</td>
        <td>${esc(t.strategy || "—")}</td><td>${esc(t.source || "—")}</td></tr>`).join("")}
      </tbody></table></div>` : `<div class="trong">Chưa có luận điểm nào.</div>`}`;
}

/* ── vẽ theo phòng đang mở ─────────────────────────────────────── */
const VE = {
  "tong-quan": veTongQuan, "thi-truong": veThiTruong, "vi-the": veViThe, "rui-ro": veRuiRo,
  "he-thong": veHeThong,
  "nao-thi-truong": veNaoThiTruong, "nao-claude": veNaoClaude,
  "quan-sat-trader": veQuanSatTrader, "the-gioi": veTheGioi,
  "chien-luoc": veChienLuoc, "huan-luyen": veHuanLuyen, "hoc": veHoc,
  "tri-nho": veTriNho, "ky-nang": veKyNang,
  "nhat-ky": veNhatKy, "chat": () => {},
};

function ve() {
  if (!S) return;
  veDinh(); vePhai(); veMach();
  // Lỗi render phải HIỆN RA. Nuốt vào console là phòng trắng trơn mà người
  // dùng tưởng "chưa có dữ liệu" — sai kiểu tệ nhất, vì nó không giục ai sửa.
  try {
    (VE[phongDangMo] || (() => {}))();
  } catch (e) {
    console.error(phongDangMo, e);
    const p = document.querySelector(`.phong[data-p="${phongDangMo}"]`);
    const noi = p && p.querySelector('[id]:not(.phong-dinh *)');
    if (noi) noi.innerHTML = `<div class="chua-co" style="border-color:rgba(248,113,113,.4)">
      <div class="nhan" style="color:var(--red)">lỗi giao diện</div>
      <h4>Phòng "${esc(phongDangMo)}" không dựng được</h4>
      <p class="mono" style="color:var(--red)">${esc(e.message)}</p>
      <p>Đây là lỗi của giao diện, không phải của runtime — vòng lặp giao dịch vẫn chạy.
      Mở Console của trình duyệt để xem vết đầy đủ.</p></div>`;
  }
  el("ben").querySelectorAll(".muc").forEach((b) => {
    const m = NAV.flatMap((t) => t.muc).find((x) => x.id === b.dataset.p);
    const d = m?.dem ? m.dem() : null;
    const s = b.querySelector(".dem");
    if (s && d != null && !m.trong) { s.textContent = d; s.classList.toggle("nong", !!(m.nong && d)); }
  });
}

/* ── dòng sự kiện + SSE ────────────────────────────────────────── */
function themSuKien(e) {
  NONG.set(e.stage, Date.now() + 2600);
  const box = el("suKien");
  const dinh = box.scrollTop + box.clientHeight >= box.scrollHeight - 25;
  const d = document.createElement("div");
  const mau = { risk: "nhac", exec: "len", brain: "tim", memory: "tim", system: "mo", data: "lam" }[e.stage] || "";
  d.innerHTML = `<span style="color:var(--fg-4)">${e.ts.slice(11, 19)}</span> ` +
    `<span class="${mau}">${esc(e.stage)}</span> <span style="color:var(--fg-3)">${esc(e.msg || e.type)}</span>`;
  box.appendChild(d);
  while (box.children.length > 160) box.removeChild(box.firstChild);
  if (dinh) box.scrollTop = box.scrollHeight;
  veMach();
}

function noiSSE() {
  const es = new EventSource("/api/stream");
  es.addEventListener("bus", (e) => themSuKien(JSON.parse(e.data)));
  es.addEventListener("state", (e) => { S = JSON.parse(e.data); ve(); });
}

async function taiNhatKy() {
  try { J = await (await fetch("/api/journal")).json(); ve(); } catch {}
}

async function taiNen() {
  try { C = await (await fetch("/api/candles")).json(); ve(); } catch {}
}

async function taiQuanSat() {
  try { QS = await (await fetch("/api/quan-sat?day_du=1")).json(); } catch (e) { /* giữ bản cũ */ }
}

async function taiChienLuoc() {
  try { CL = await (await fetch("/api/chien-luoc")).json(); } catch (e) { /* giữ bản cũ */ }
}

async function taiTheGioi() {
  try { W = await (await fetch("/api/the-gioi")).json(); ve(); } catch {}
}

/* ── điều khiển ────────────────────────────────────────────────── */
const dieuKhien = (h) => fetch("/api/control", {
  method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ action: h }),
});

/* ── chat ──────────────────────────────────────────────────────── */
const lichSu = [];
function bong(vai, chu = "") {
  const w = document.createElement("div");
  w.className = "tin " + (vai === "user" ? "toi" : "bot");
  w.innerHTML = `<div class="ai">${vai === "user" ? "bạn" : "bộ não"}</div><div class="bong"></div>`;
  w.querySelector(".bong").textContent = chu;
  el("chatCuon").appendChild(w);
  el("chatCuon").scrollTop = el("chatCuon").scrollHeight;
  return w.querySelector(".bong");
}

async function gui(chu) {
  if (!chu.trim()) return;
  el("chatO").value = "";
  bong("user", chu);
  lichSu.push({ role: "user", content: chu });
  const ra = bong("bot", "…");
  let acc = "";
  const res = await fetch("/api/chat", {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ messages: lichSu }),
  });
  const rd = res.body.getReader(), dec = new TextDecoder();
  let buf = "";
  for (;;) {
    const { done, value } = await rd.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const ps = buf.split("\n\n"); buf = ps.pop();
    for (const p of ps) {
      const line = p.split("\n").find((l) => l.startsWith("data: "));
      if (!line) continue;
      const o = JSON.parse(line.slice(6));
      if (o.delta) { acc += o.delta; ra.textContent = acc; el("chatCuon").scrollTop = el("chatCuon").scrollHeight; }
    }
  }
  lichSu.push({ role: "assistant", content: acc || "(rỗng)" });
}

/* ── nối dây ───────────────────────────────────────────────────── */
dungBen(); dungMach();
el("btPhanTich").onclick = () => dieuKhien("analyze");
el("btDung").onclick = () => dieuKhien(S?.paused ? "resume" : "pause");
el("btDatLai").onclick = () => { if (confirm("Đặt lại sổ vị thế?\nNhật ký và bài học vẫn giữ nguyên.\nSố dư testnet KHÔNG nạp lại được.")) dieuKhien("reset"); };
el("chatGui").onclick = () => gui(el("chatO").value);
el("chatO").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); gui(el("chatO").value); }
});
document.querySelectorAll(".goi-y button").forEach((b) => b.onclick = () => { moPhong("chat"); gui(b.dataset.h); });

/* ?phong=<id> mở thẳng một phòng; ?nosse=1 tắt luồng thời gian thực.
   Cờ nosse để chụp/kiểm bằng trình duyệt headless: EventSource giữ kết nối
   mở nên trang không bao giờ "load xong" và headless treo vô hạn. */
const THAM_SO = new URLSearchParams(location.search);
const phongYeuCau = THAM_SO.get("phong");
if (phongYeuCau && VE[phongYeuCau]) phongDangMo = phongYeuCau;

Promise.all([
  fetch("/api/state").then((r) => r.json()),
  fetch("/api/journal").then((r) => r.json()),
  fetch("/api/candles").then((r) => r.json()).catch(() => null),
  fetch("/api/skills").then((r) => r.json()).catch(() => null),
  fetch("/api/the-gioi").then((r) => r.json()).catch(() => null),
  fetch("/api/hoc").then((r) => r.json()).catch(() => null),
  fetch("/api/tu-chay").then((r) => r.json()).catch(() => null),
  fetch("/api/chien-luoc").then((r) => r.json()).catch(() => null),
  fetch("/api/quan-sat?day_du=1").then((r) => r.json()).catch(() => null),
]).then(([s, j, c, k, w, h, tc, cl, qs]) => {
  S = s; J = j; C = c; K = k; W = w; HL = h; TC = tc; CL = cl; QS = qs;
  dungBen();
  moPhong(phongDangMo);
  document.body.dataset.sanSang = "1";   // dấu để headless biết đã render xong
  // Một phiên huấn luyện có thể đang chạy từ trước khi mở tab này — nối lại
  // thanh tiến độ thay vì hiện như chưa chạy gì.
  if (HL?.trangThai === "đang chạy") hlBatNhip();
});

// Vẽ lại biểu đồ khi đổi kích thước cửa sổ — canvas không tự co giãn.
let hoanResize;
window.addEventListener("resize", () => {
  clearTimeout(hoanResize);
  hoanResize = setTimeout(ve, 180);
});

if (THAM_SO.get("nosse") !== "1") {
  noiSSE();
  setInterval(veMach, 700);
  setInterval(taiNhatKy, 20000);
  setInterval(taiNen, 15000);
  // Nguồn ngoài tự tươi lại mỗi 15 phút ở runtime, nên hỏi mỗi 2 phút là thừa
  // đủ. Hỏi dày hơn chỉ chép lại đúng một bản trong bộ nhớ máy chủ.
  setInterval(taiTheGioi, 120000);
}
})();
