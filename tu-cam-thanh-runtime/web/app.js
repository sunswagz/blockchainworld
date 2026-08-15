/* ═══════════════════════════════════════════════════════════════════
   CLAUDE TRADER — Trung tâm chỉ huy

   Ba tầng: bot ĐANG LÀM GÌ → ĐANG NGHĨ GÌ → ĐANG HỌC GÌ.

   Luật xuyên suốt: ô nào không có nguồn dữ liệu thì gọi `chuaCo()` —
   nói rõ thiếu gì và cần gì để bật. KHÔNG bao giờ điền số cho đầy
   layout. Một bảng điều khiển nói dối tệ hơn hẳn một bảng còn trống:
   ô trống thì người ta đi tìm, số giả thì người ta tin.
   ═══════════════════════════════════════════════════════════════════ */
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
};

const NAV = [
  { tang: 1, ten: "Chỉ huy",     y: "Bot đang làm gì", muc: [
    { id: "tong-quan",       ten: "Tổng quan",        ic: "tongQuan" },
    { id: "vi-the",          ten: "Vị thế",           ic: "viThe", dem: () => (S?.account?.positions || []).length },
    { id: "rui-ro",          ten: "Rủi ro",           ic: "ruiRo", dem: () => (S?.risk?.breakers || []).length, nong: true },
  ]},
  { tang: 2, ten: "Trí tuệ",     y: "Bot đang nghĩ gì", muc: [
    { id: "nao-thi-truong",  ten: "Bộ não thị trường", ic: "naoTt" },
    { id: "nao-claude",      ten: "Bộ não Claude",     ic: "naoAi" },
    { id: "quan-sat-trader", ten: "Quan sát trader",   ic: "trader", trong: true },
    { id: "the-gioi",        ten: "Dòng chảy thế giới",ic: "theGioi", trong: true },
  ]},
  { tang: 3, ten: "Tiến hoá",    y: "Bot đang học gì", muc: [
    { id: "chien-luoc",      ten: "Chiến lược",       ic: "chienLuoc" },
    { id: "hoc",             ten: "Học",              ic: "hoc", dem: () => (J?.lessons || []).length },
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
  hn.className = "huy " + (S.brain?.mode === "claude" ? "ai" : "");

  const t = S.brain?.today || {}, cap = S.brain?.budgetUsd || 0;
  const ht = el("huyTien");
  ht.textContent = `$${(t.usd || 0).toFixed(4)} / $${cap} · ${t.calls || 0} lượt`;
  ht.className = "huy " + (S.brain?.blocked ? "dut" : (t.usd || 0) > cap * 0.7 ? "nhac" : "");

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

  let pq = `<h3>Risk Engine</h3>`;
  if (!d) pq += '<div class="mo" style="font-size:12px">chưa thẩm định lượt nào</div>';
  else if (d.approved) pq += hang("phán quyết", "CHO QUA", "len") + hang("RR", num(d.rr)) +
    hang("rủi ro", tien(d.position?.riskAmount));
  else if (d.action === "NO_TRADE") pq += '<div class="nhac" style="font-size:12px">Bộ não chủ động đứng ngoài — đây là một quyết định.</div>';
  else pq += `<div class="xuong" style="font-size:12px;font-weight:600;margin-bottom:6px">CHẶN</div>` +
    (d.rejections || []).map((r) => `<div style="font-size:11.5px;color:var(--fg-3);padding:2px 0">× ${esc(r)}</div>`).join("");
  el("aiPhanQuyet").innerHTML = pq;
}

/* ── TẦNG 1 · TỔNG QUAN ────────────────────────────────────────── */
function veTongQuan() {
  if (!S) return;
  const a = S.account || {}, r = S.risk || {};
  const dung = r.halted, ngat = (r.breakers || []).length;

  el("tqTrangThai").innerHTML = `<div class="luoi c4">
    ${oSo("Hệ thống", S.dataSource?.live ? "TỐT" : "DỮ LIỆU GIẢ",
        S.dataSource?.live ? "len" : "xuong", S.dataSource?.name || "")}
    ${oSo("Giao dịch", dung ? "ĐÃ DỪNG" : S.paused ? "TẠM DỪNG" : ngat ? "BỊ CHẶN" : "HOẠT ĐỘNG",
        dung ? "xuong" : S.paused || ngat ? "nhac" : "len", dung || (r.breakers || [])[0] || "")}
    ${oSo("Chế độ rủi ro", ngat ? "HẠN CHẾ" : "BÌNH THƯỜNG", ngat ? "nhac" : "", S.spotOnly ? "spot · chỉ LONG" : "")}
    ${oSo("Chế độ thị trường", S.regime?.primary || "—", "lam", "chất lượng " + (S.regime?.quality || "—"))}
  </div>`;

  const lai = (a.equityMarked ?? 0) - (S.risk?.limits?.startingEquity ?? 0);
  const trienKhai = (a.positions || []).reduce((s, p) => s + (p.riskAmount || 0), 0);
  const tranRui = (a.equityMarked || 1) * (r.limits?.maxRiskPerTradePct || 0.5) / 100;

  el("tqTaiKhoan").innerHTML = `<div class="luoi c4">
    ${oSo("Vốn", tien(a.equityMarked), "", S.venue === "testnet" ? "đọc từ sàn" : "sàn giấy")}
    ${oSo("Hôm nay", tien(a.todayPnl), dau(a.todayPnl))}
    ${oSo("Drawdown", pct(a.drawdownPct), a.drawdownPct > (r.limits?.maxDrawdownPct || 10) * 0.6 ? "nhac" : "",
        "đỉnh " + tien(a.peakEquity))}
    ${oSo("Vị thế mở", (a.positions || []).length, "", `rủi ro đang đặt ${tien(trienKhai)}`)}
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
  const thang = td.filter((t) => (t.pnl || 0) > 0).length;
  const thua = td.filter((t) => (t.pnl || 0) < 0).length;

  el("tqHomNay").innerHTML = `<div class="luoi c4">
    ${oSo("Lệnh", td.length)}
    ${oSo("Thắng / Thua", `${thang} / ${thua}`, "", "kết quả")}
    ${oSo("Quyết định tốt", tot, tot ? "len" : "mo", "chất lượng, không phải tiền")}
    ${oSo("Quyết định tồi", xau, xau ? "xuong" : "mo", "đây mới là thứ phải sửa")}
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
      </div>
      <div class="tieu-muc" style="margin-top:16px">Vì sao vẫn còn giữ</div>
      ${check.map(([ten, ok, gt]) =>
        `<div class="hang"><span>${esc(ten)}</span><b class="${ok ? "len" : "nhac"}">${ok ? "✓" : "!"} ${esc(gt ?? "—")}</b></div>`).join("")}
      <div class="hang"><span>lệnh thoát do sàn giữ</span><b class="${v.ocoOrderListId ? "len" : "xuong"}">${
        v.ocoOrderListId ? "✓ OCO " + v.ocoOrderListId : "✗ KHÔNG CÓ — không ai canh"}</b></div>
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

  el("nttNoi").innerHTML = `
    <div class="nao">
      <div class="kinh nao-o tren im"><h4>Vĩ mô</h4>
        <div class="d"><span>DXY</span><span class="mo">—</span></div>
        <div class="d"><span>lợi suất</span><span class="mo">—</span></div>
        <div class="d"><span>dầu</span><span class="mo">—</span></div></div>

      <div class="kinh nao-o trai im"><h4>On-chain</h4>
        <div class="d"><span>dòng vào sàn</span><span class="mo">—</span></div>
        <div class="d"><span>ví cá voi</span><span class="mo">—</span></div>
        <div class="d"><span>stablecoin</span><span class="mo">—</span></div></div>

      <div class="nao-loi">
        <div class="cap">${esc(S?.symbol || "—")}</div>
        <div class="gia">${num(S?.price)}</div>
        <div class="rg">${esc(S?.regime?.primary || "—")}</div>
      </div>

      <div class="kinh nao-o phai im"><h4>Phái sinh</h4>
        <div class="d"><span>funding</span><span class="mo">—</span></div>
        <div class="d"><span>open interest</span><span class="mo">—</span></div>
        <div class="d"><span>vùng thanh lý</span><span class="mo">—</span></div></div>

      <div class="kinh nao-o duoi"><h4>Kỹ thuật · có dữ liệu thật</h4>
        <div class="d"><span>EMA</span><span>${esc(p.emaStack || "—")}</span></div>
        <div class="d"><span>RSI(14)</span><span>${num(p.rsi14, 1)}</span></div>
        <div class="d"><span>ADX</span><span>${num(p.adx, 1)}</span></div>
        <div class="d"><span>Volume</span><span>×${num(p.volumeRatio)}</span></div></div>
    </div>

    <div class="tieu-muc">Trạng thái thị trường</div>
    <div class="luoi c2">
      <div class="kinh the">
        ${thanhDo("Xu hướng", p.adx != null ? `${num(trend, 0)}%` : "chưa có", trend, "")}
        ${thanhDo("Động lượng", p.rsi14 != null ? `${num(momentum, 0)}%` : "chưa có", momentum, "")}
        ${thanhDo("Biến động", p.atrRatioVsMedian != null ? `${num(volat, 0)}%` : "chưa có", volat, "tim")}
        ${thanhDo("Thanh khoản", "chưa có nguồn", null)}
        ${thanhDo("Vĩ mô", "chưa có nguồn", null)}
        ${thanhDo("Trader giỏi", "chưa có nguồn", null)}
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

    <div style="margin-top:12px">${chuaCo("Vĩ mô · On-chain · Phái sinh",
      "Ba ô mờ ở trên cần nguồn dữ liệu mà M0 chưa nối. Chúng để trống thật chứ không điền số cho đủ hình — " +
      "một sơ đồ đẹp với ba ô bịa thì tệ hơn hẳn một sơ đồ thiếu ba ô.",
      ["<b>Vĩ mô</b> — DXY, lợi suất trái phiếu, dầu: cần nguồn như FRED hoặc Yahoo Finance",
       "<b>On-chain</b> — dòng vào sàn, ví cá voi, cung stablecoin: cần Glassnode/Nansen hoặc node riêng",
       "<b>Phái sinh</b> — funding, open interest, bản đồ thanh lý: cần API futures; M0 chạy <code>spot</code> nên chưa có"])}</div>`;
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

/* ── TẦNG 2 · hai phòng chưa có nguồn ──────────────────────────── */
function veQuanSatTrader() {
  el("qstNoi").innerHTML = chuaCo("Đài quan sát trader",
    "Phòng này để bot học từ những trader giỏi trên các sàn khác: ai đang LONG/SHORT, ai có điểm số cao, " +
    "phong cách nào hợp chế độ thị trường nào — rồi Claude rút ra bài học từ hành vi của họ. " +
    "M0 chưa nối nguồn nào, nên ở đây trống thật.",
    ["API vị thế công khai của <b>Hyperliquid</b> (có sẵn, dễ nhất để bắt đầu)",
     "<b>OKX</b> / <b>dYdX</b> / <b>Aster</b> — copy-trading hoặc leaderboard công khai",
     "Một bộ chấm điểm trader: ROI 90 ngày, max drawdown, số lệnh, độ ổn định — để tách <i>giỏi</i> khỏi <i>may</i>",
     "Một tầng gộp: từ N vị thế lẻ thành một con số “64% đang LONG”, kèm khoảng tin cậy"]) +
    `<div class="kinh the" style="margin-top:12px"><h3>Cảnh báo thiết kế</h3>
     <p style="margin:0;font-size:12.5px;color:var(--fg-3);line-height:1.7">
     Đây là phòng dễ tự lừa mình nhất. Một trader có ROI +38% trong 90 ngày có thể chỉ là người vào đúng một
     sóng, và sao chép họ ở chế độ thị trường khác là mua lại đúng rủi ro đã trả cho họ. Nếu dựng phòng này,
     phải chấm điểm theo <b>chế độ thị trường</b>, không chấm theo tổng ROI — nếu không nó thành một máy
     khuếch đại đám đông.</p></div>`;
}

function veTheGioi() {
  el("tgNoi").innerHTML = chuaCo("Dòng chảy thế giới",
    "Phòng này biến tin tức thành <b>dữ liệu có cấu trúc</b>: một sự kiện FED thành " +
    "<code>{category, region, affected_assets, surprise, direction, confidence, horizon}</code>, rồi vẽ thành chuỗi nhân quả " +
    "<i>FED → lãi suất → USD → tài sản rủi ro → BTC</i>. M0 chưa có bước này.",
    ["Nguồn tin: RSS/API tài chính, hoặc <code>web_search</code> qua Claude Code Action",
     "Một lượt Claude biến tin thành JSON có schema — <b>không</b> cho model ghi thẳng vào file trang",
     "Bảng lịch sự kiện (FOMC, CPI, NFP) để đặt cờ <code>event_risk</code> trước giờ công bố",
     "Ghi rõ đây là <b>chuỗi nhân quả CÓ THỂ</b>, không phải chân lý — và lưu lại để hậu kiểm xem nó có đúng không"]) +
    `<div class="kinh the" style="margin-top:12px"><h3>Chỗ này tốn tiền nhất</h3>
     <p style="margin:0;font-size:12.5px;color:var(--fg-3);line-height:1.7">
     Đo được rồi: bản quét tin của Đài Quan Trắc trong repo này từng tốn <b>1,4 USD một lượt</b> vì
     <code>web_search</code> kéo nguyên nội dung trang vào ngữ cảnh, nhân số chủ đề — ở nhịp 4 lượt/ngày là
     ~170 USD/tháng và đã phải tắt lịch. Nếu dựng phòng này thì <b>bắt đầu từ trần chi phí</b>, không phải từ
     tính năng.</p></div>`;
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

    <div class="tieu-muc">Challenger · thách đấu</div>
    ${chuaCo("Champion / Challenger",
      "Cơ chế tiến hoá: Claude đề xuất một thay đổi (ví dụ <i>ATR stop 1.5 → 1.8</i>), thay đổi đó chạy như " +
      "<b>Challenger</b> qua backtest → walk-forward → ngoài mẫu → paper → shadow, và chỉ được lên thay " +
      "Champion khi thắng trên dữ liệu <b>chưa từng thấy</b>. M0 chưa có bước nào trong chuỗi đó.",
      ["<b>Backtest / replay</b> trên nến lịch sử — <b>đây phải là mốc kế tiếp</b>, trước mọi tính năng khác",
       "Tách dữ liệu trong mẫu / ngoài mẫu, và walk-forward để không tự chấm điểm mình trên chính dữ liệu đã tinh chỉnh",
       "Sổ đăng ký chiến lược có phiên bản, để biết lệnh nào chạy bằng bản nào",
       "Một cửa duyệt: <code>[ BACKTEST ]</code> chứ không phải <code>[ ÁP DỤNG THẲNG ]</code>"])}
    <div class="kinh the" style="margin-top:12px"><h3>Vì sao backtest phải đi trước</h3>
      <p style="margin:0;font-size:12.5px;color:var(--fg-3);line-height:1.7">
      Hiện tại <b>không có cách nào biết một thay đổi là tốt hơn hay chỉ là khác đi</b>. Thêm chiến lược,
      thêm chỉ báo, thêm nguồn dữ liệu lúc này đều là đoán. Đổi chiến lược sau mỗi lệnh thua là đường cong
      sát thủ: hệ thống đuổi theo nhiễu, mọi thay đổi đều được biện minh bằng lệnh gần nhất, và không phiên
      bản nào sống đủ lâu để biết nó tốt hay xấu.</p></div>`;
}

/* ── TẦNG 3 · HỌC ──────────────────────────────────────────────── */
const VONG_DOI = ["PHÁT HIỆN", "BACKTEST", "KIỂM CHỨNG", "CHALLENGER", "LÊN CHẠY"];

function veHoc() {
  const ls = J?.lessons || [];
  const doi = ls.filter((l) => l.change_strategy).length;

  el("hocNoi").innerHTML = `
    <div class="luoi c4">
      ${oSo("Lệnh đã hậu kiểm", ls.length)}
      ${oSo("Quyết định tốt", ls.filter((l) => (l.classification || "").startsWith("GOOD_TRADE")).length, "len")}
      ${oSo("Quyết định tồi", ls.filter((l) => (l.classification || "").startsWith("BAD_TRADE")).length, "xuong")}
      ${oSo("Đề nghị đổi chiến lược", doi, doi ? "nhac" : "mo", "cửa hẹp — cần mẫu lặp lại")}
    </div>

    <div class="tieu-muc">Bài học</div>
    ${ls.length ? ls.slice().reverse().map((l) => {
      const c = l.classification || "";
      const k = c.startsWith("BAD_TRADE") ? "xau" : c.includes("BAD_OUTCOME") ? "canh" : "tot";
      const buoc = l.change_strategy ? 1 : 0;
      return `<div class="kinh the" style="margin-bottom:10px">
        <h3><span class="${k === "xau" ? "xuong" : k === "canh" ? "nhac" : "len"}">${esc(c)}</span>
          <span class="cuoi">${esc(l.regime || "—")} · ${l.rMultiple ?? "—"}R · ${esc(l.exitReason || "")}</span></h3>
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
      </div>`;
    }).join("") : `<div class="trong">Chưa có bài học nào — bài học chỉ sinh ra sau khi một lệnh đóng lại.</div>`}`;
}

/* ── TẦNG 3 · NHẬT KÝ ──────────────────────────────────────────── */
function veNhatKy() {
  const td = (J?.trades || []).slice().reverse();
  const ls = J?.lessons || [];
  const perf = (J?.performance || {}).overall || {};

  el("nkNoi").innerHTML = `
    <div class="luoi c4">
      ${oSo("Tổng lệnh", perf.count ?? 0)}
      ${oSo("Tỉ lệ thắng", perf.winRate != null ? perf.winRate + "%" : "—")}
      ${oSo("Kỳ vọng", perf.expectancyR != null ? perf.expectancyR + "R" : "—",
          (perf.expectancyR ?? 0) > 0 ? "len" : (perf.expectancyR ?? 0) < 0 ? "xuong" : "")}
      ${oSo("Tổng lãi/lỗ", tien(perf.totalPnl), dau(perf.totalPnl))}
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
  "tong-quan": veTongQuan, "vi-the": veViThe, "rui-ro": veRuiRo,
  "nao-thi-truong": veNaoThiTruong, "nao-claude": veNaoClaude,
  "quan-sat-trader": veQuanSatTrader, "the-gioi": veTheGioi,
  "chien-luoc": veChienLuoc, "hoc": veHoc, "nhat-ky": veNhatKy,
  "chat": () => {},
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
]).then(([s, j]) => {
  S = s; J = j;
  dungBen();
  moPhong(phongDangMo);
  document.body.dataset.sanSang = "1";   // dấu để headless biết đã render xong
});

if (THAM_SO.get("nosse") !== "1") {
  noiSSE();
  setInterval(veMach, 700);
  setInterval(taiNhatKy, 20000);
}
})();
