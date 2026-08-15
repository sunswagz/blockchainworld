/* Dashboard. Client thuần: không tính toán gì, chỉ hiển thị thứ runtime phát ra.
   Đóng tab không ảnh hưởng giao dịch; mở hai tab không nhân đôi thứ gì. */

const $ = (s) => document.querySelector(s);
const fmt = (v, n = 2) =>
  v === null || v === undefined || Number.isNaN(v) ? "—"
  : Number(v).toLocaleString("vi-VN", { minimumFractionDigits: n, maximumFractionDigits: n });
const money = (v) => (v === null || v === undefined ? "—" : (v < 0 ? "-$" : "$") + fmt(Math.abs(v)));
const sgn = (v) => (v > 0 ? "pos" : v < 0 ? "neg" : "");
const esc = (s) => String(s ?? "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

let STATE = null;
const HOT = new Map();   // stage -> hết hạn sáng (ms)

/* ── SƠ ĐỒ DỮ LIỆU ─────────────────────────────────────────────────────── */
const NODES = [
  { id: "world",   stage: null,       title: "Thế giới",                   get: () => "giá · khối lượng · thời gian" },
  { id: "data",    stage: "data",     title: "Market Data Engine",         get: (s) => s?.dataSource ? `${s.dataSource.name}${s.dataSource.live ? "" : "  ⚠ DỮ LIỆU TỔNG HỢP"} · ${fmt(s.price)}` : "—" },
  { id: "feat",    stage: "features", title: "Feature Factory",            get: (s) => { const p = tf(s); return p ? `EMA ${p.emaStack} · RSI ${p.rsi14} · MACD ${p.macdHist} · ATR% ${p.atrPct}` : "—"; } },
  { id: "regime",  stage: "regime",   title: "Market State → Regime",      get: (s) => s?.regime ? `${s.regime.primary} · ADX ${s.regime.adx} · chất lượng ${s.regime.quality}${s.regime.flags?.length ? " · " + s.regime.flags.join(",") : ""}` : "—" },
  { split: [
    { id: "mem",   stage: "memory",   title: "Memory Engine",              get: () => "episodic · semantic · procedural · performance" },
    { id: "brain", stage: "brain",    title: "Claude Brain",               get: (s) => s?.brain ? `${s.brain.mode} · ${s.brain.model} · $${(s.brain.today?.usd ?? 0).toFixed(4)} hôm nay` : "—" },
  ]},
  { id: "thesis",  stage: null,       title: "Trade Thesis",               get: (s) => s?.thesis ? `${s.thesis.action} · tin cậy ${fmt(s.thesis.confidence, 2)} · ${s.thesis.strategy}` : "chưa có luận điểm nào" },
  { id: "risk",    stage: "risk",     title: "Risk Engine  (Python thuần — có quyền phủ quyết)",
                                      get: (s) => { const d = s?.decision; if (!d) return "chưa thẩm định lượt nào";
                                        if (d.approved) return `CHO QUA · RR ${fmt(d.rr)} · rủi ro $${fmt(d.position?.riskAmount)} (${d.position?.riskPct}%)`;
                                        if (d.action === "NO_TRADE") return "NO_TRADE — brain chủ động đứng ngoài";
                                        return "CHẶN · " + (d.rejections || []).join(" | "); },
                                      bad: (s) => s?.decision && !s.decision.approved && s.decision.action !== "NO_TRADE" },
  { id: "exec",    stage: "exec",     title: "Execution  (sàn giấy)",      get: (s) => { const n = s?.account?.positions?.length || 0;
                                        return n ? `${n} vị thế mở · P&L mở ${money(s.account.openPnl)}` : "không có vị thế mở"; } },
  { id: "journal", stage: "journal",  title: "Trade Journal",              get: (s) => `${s?.account?.closedCount ?? 0} lệnh đã đóng` },
  { id: "post",    stage: "memory",   title: "Post-Mortem → Lesson Memory", get: () => "quyết định ≠ kết quả — học theo chất lượng quyết định" },
];

function tf(s) { return s?.marketState?.timeframes?.[s?.timeframes?.primary]; }

function buildFlow() {
  const box = $("#flow");
  box.innerHTML = "";
  const mk = (n) => `<div class="node" id="n-${n.id}"><div class="nt">${n.title}</div><div class="nv" id="nv-${n.id}">—</div></div>`;
  NODES.forEach((n, i) => {
    if (i) box.insertAdjacentHTML("beforeend", '<div class="arrow"></div>');
    box.insertAdjacentHTML("beforeend", n.split
      ? `<div class="split">${n.split.map(mk).join("")}</div>`
      : mk(n));
  });
  box.insertAdjacentHTML("beforeend",
    '<div class="arrow"></div><div class="node" style="border-style:dashed"><div class="nt">↺ quay lại Memory Engine</div>' +
    '<div class="nv">bài học của vòng này là ngữ cảnh của vòng sau</div></div>');
}

function paintFlow() {
  const now = Date.now();
  const each = (n) => {
    const el = document.getElementById("n-" + n.id);
    const v = document.getElementById("nv-" + n.id);
    if (!el) return;
    if (v) v.textContent = n.get(STATE) ?? "—";
    const hot = n.stage && HOT.get(n.stage) > now;
    el.classList.toggle("hot", !!hot);
    el.classList.toggle("bad", !!(n.bad && n.bad(STATE)));
  };
  NODES.forEach((n) => (n.split ? n.split.forEach(each) : each(n)));
}

/* ── THANH TRÊN ────────────────────────────────────────────────────────── */
function paintHeader() {
  const s = STATE; if (!s) return;
  $("#sym").textContent = s.symbol;
  $("#price").textContent = fmt(s.price);
  $("#regime").textContent = s.regime?.primary ?? "—";
  const a = s.account || {};
  $("#equity").textContent = money(a.equityMarked ?? a.equity);
  const t = $("#pnlToday");
  t.textContent = money(a.todayPnl); t.className = sgn(a.todayPnl);
  const d = $("#dd");
  d.textContent = (a.drawdownPct ?? 0).toFixed(2) + "%";
  d.className = a.drawdownPct > (s.risk?.limits?.maxDrawdownPct ?? 10) * 0.6 ? "neg" : "";

  const sb = $("#srcBadge"), live = s.dataSource?.live;
  sb.textContent = "nguồn " + (s.dataSource?.name ?? "—");
  sb.className = "badge " + (live ? "ok" : "bad");

  const bb = $("#brainBadge"), bm = s.brain?.mode;
  bb.textContent = "brain " + (bm ?? "—") + (s.paused ? " · TẠM DỪNG" : "");
  bb.className = "badge " + (bm === "claude" ? "ok" : "warn");

  const cb = $("#costBadge"), used = s.brain?.today?.usd ?? 0, cap = s.brain?.budgetUsd ?? 0;
  cb.textContent = `$${used.toFixed(4)} / $${cap} · ${s.brain?.today?.calls ?? 0} lượt`;
  cb.className = "badge " + (s.brain?.blocked ? "bad" : used > cap * 0.7 ? "warn" : "");

  $("#btnPause").textContent = s.paused ? "Chạy lại" : "Tạm dừng";
  $("#btnKill").textContent = s.risk?.halted ? "Gỡ kill switch" : "Kill switch";
  $("#chatMode").textContent = bm === "claude" ? s.brain.model : "mock — chưa có API key";
}

/* ── CÁC TAB ───────────────────────────────────────────────────────────── */
const kv = (k, v, cls = "") => `<div class="kv"><span>${esc(k)}</span><b class="${cls}">${esc(v)}</b></div>`;

function paintState() {
  const s = STATE; if (!s?.marketState) return;
  const tfs = s.marketState.timeframes;
  $("#v-state").innerHTML = `<div class="grid">` + Object.entries(tfs).map(([name, f]) => `
    <div class="card"><h4>khung ${name}</h4>
      ${kv("giá", fmt(f.price))}
      ${kv("EMA stack", f.emaStack)}
      ${kv("cấu trúc", f.structure)}
      ${kv("RSI(14)", `${f.rsi14} (${f.rsiSlope > 0 ? "↑" : f.rsiSlope < 0 ? "↓" : "→"})`)}
      ${kv("MACD hist", f.macdHist)}
      ${kv("ADX", `${f.adx}  +DI ${f.plusDI} / -DI ${f.minusDI}`)}
      ${kv("ATR", `${fmt(f.atr)}  (${f.atrPct}%)`)}
      ${kv("biến động", `${f.volatility} · ×${f.atrRatioVsMedian} trung vị`)}
      ${kv("Bollinger", `rộng ${f.bbWidthPct}% · vị trí ${f.bbPosition}`)}
      ${kv("volume", "×" + f.volumeRatio)}
      ${kv("biên 20 nến", `${fmt(f.range20Low)} … ${fmt(f.range20High)}`)}
      ${kv("kháng cự", (f.resistance || []).map((z) => fmt(z.price)).join(" · ") || "—")}
      ${kv("hỗ trợ", (f.support || []).map((z) => fmt(z.price)).join(" · ") || "—")}
    </div>`).join("") + `
    <div class="card"><h4>chế độ thị trường</h4>
      ${kv("chính", s.regime?.primary)}
      ${kv("chất lượng", s.regime?.quality)}
      ${kv("cờ", (s.regime?.flags || []).join(", ") || "không")}
      ${kv("xu hướng khung lớn", s.regime?.contextTrend ?? "—")}
      <div style="margin-top:8px;color:var(--muted);font-size:11.5px;line-height:1.6">
        ${(s.regime?.reasons || []).map((r) => "• " + esc(r)).join("<br>")}
      </div>
    </div></div>`;
}

function paintThesis() {
  const t = STATE?.thesis;
  if (!t) { $("#v-thesis").innerHTML = '<div class="empty">Chưa có luận điểm nào. Bấm “Phân tích ngay” để đánh thức brain.</div>'; return; }
  $("#v-thesis").innerHTML = `
    <div class="grid">
      <div class="card"><h4>quyết định</h4>
        ${kv("hành động", t.action, t.action === "LONG" ? "pos" : t.action === "SHORT" ? "neg" : "warn")}
        ${kv("độ tin cậy", fmt(t.confidence, 2))}
        ${kv("brain đọc regime", t.regime_read)}
        ${kv("bộ phân loại nói", t.regimeFromClassifier)}
        ${kv("chiến lược", t.strategy)}
        ${kv("rủi ro sự kiện", t.event_risk)}
        ${kv("nguồn", t.source)}
      </div>
      <div class="card"><h4>mức giá</h4>
        ${kv("vùng vào", (t.entry_zone || []).map((x) => fmt(x)).join(" – ") || "—")}
        ${kv("vô hiệu hoá (SL)", fmt(t.invalidation))}
        ${kv("mục tiêu", (t.targets || []).map((x) => fmt(x)).join(" · ") || "—")}
        ${kv("risk đề xuất", (t.suggested_risk_pct ?? 0) + "%")}
        <div style="margin-top:8px;color:var(--muted);font-size:11.5px">${esc(t.invalidation_logic || "")}</div>
      </div>
    </div>
    <h3 class="sec">kịch bản</h3>
    <div class="grid">${(t.scenarios || []).map((sc) => `
      <div class="card"><h4>${esc(sc.name)} — ${Math.round((sc.probability || 0) * 100)}%</h4>
      <div style="color:var(--muted);font-size:12px">${esc(sc.description)}</div></div>`).join("")}</div>
    <h3 class="sec">lập luận</h3>
    <div class="card" style="white-space:pre-wrap;color:var(--muted);font-size:12.5px;line-height:1.7">${esc(t.reasoning)}</div>
    <h3 class="sec">mã lý do</h3>
    <div class="card mono" style="font-size:11.5px;color:var(--muted)">${(t.reason_codes || []).join(" · ") || "—"}</div>`;
}

function paintRisk() {
  const s = STATE; if (!s) return;
  const r = s.risk || {}, a = s.account || {}, d = s.decision;
  const brk = r.breakers || [];
  $("#v-risk").innerHTML = `
    ${r.halted ? `<div class="card" style="border-color:#5e2626;margin-bottom:14px"><h4 style="color:var(--red)">đã dừng</h4><div class="neg mono">${esc(r.halted)}</div></div>` : ""}
    ${brk.length ? `<div class="card" style="border-color:#5c4715;margin-bottom:14px"><h4 style="color:var(--amber)">ngắt mạch đang bật</h4>${brk.map((b) => `<div class="warn mono" style="font-size:11.5px">• ${esc(b)}</div>`).join("")}</div>` : ""}
    <div class="grid">
      <div class="card"><h4>giới hạn cứng</h4>
        ${kv("rủi ro / lệnh", r.limits?.maxRiskPerTradePct + "%")}
        ${kv("RR tối thiểu", r.limits?.minRR)}
        ${kv("tin cậy tối thiểu", r.limits?.minConfidence)}
        ${kv("stop trong khoảng", `${r.limits?.minStopAtr}–${r.limits?.maxStopAtr} × ATR`)}
        ${kv("trần lỗ ngày", r.limits?.maxDailyLossPct + "%")}
        ${kv("kill switch drawdown", r.limits?.maxDrawdownPct + "%")}
        ${kv("vị thế tối đa", r.limits?.maxOpenPositions)}
      </div>
      <div class="card"><h4>tài khoản</h4>
        ${kv("vốn (đã đánh dấu)", money(a.equityMarked))}
        ${kv("vốn thực hiện", money(a.equity))}
        ${kv("P&L mở", money(a.openPnl), sgn(a.openPnl))}
        ${kv("P&L hôm nay", money(a.todayPnl), sgn(a.todayPnl))}
        ${kv("đỉnh vốn", money(a.peakEquity))}
        ${kv("drawdown", (a.drawdownPct ?? 0) + "%")}
        ${kv("lệnh đã đóng", a.closedCount ?? 0)}
      </div>
      ${d ? `<div class="card"><h4>phán quyết gần nhất</h4>
        ${kv("kết quả", d.approved ? "CHO QUA" : d.action === "NO_TRADE" ? "NO_TRADE" : "CHẶN", d.approved ? "pos" : d.action === "NO_TRADE" ? "warn" : "neg")}
        ${kv("RR", fmt(d.rr))}
        ${kv("ghi chú", d.note || "—")}
        ${(d.rejections || []).map((x) => `<div class="neg mono" style="font-size:11px;margin-top:3px">• ${esc(x)}</div>`).join("")}
      </div>` : ""}
    </div>
    <h3 class="sec">vị thế đang mở</h3>
    ${(a.positions || []).length ? `<table><thead><tr>
      <th>chiều</th><th>vào</th><th>SL</th><th>TP1</th><th>KL</th><th>rủi ro</th><th>P&L</th><th>R</th></tr></thead><tbody>
      ${a.positions.map((p) => `<tr>
        <td class="${p.side === "LONG" ? "pos" : "neg"}">${p.side}</td>
        <td>${fmt(p.entry)}</td><td>${fmt(p.stopLoss)}</td><td>${fmt(p.targets?.[0])}</td>
        <td>${Number(p.qty).toFixed(6)}</td><td>${money(p.riskAmount)}</td>
        <td class="${sgn(p.unrealizedPnl)}">${money(p.unrealizedPnl)}</td>
        <td class="${sgn(p.unrealizedR)}">${p.unrealizedR ?? "—"}</td></tr>`).join("")}
      </tbody></table>` : '<div class="empty">Không có vị thế nào đang mở.</div>'}`;
}

async function paintJournal() {
  const j = await (await fetch("/api/journal")).json();
  const p = j.performance || {};
  const st = (x) => x && x.count ? `${x.count} lệnh · thắng ${x.winRate}% · kỳ vọng ${x.expectancyR}R · ${money(x.totalPnl)}` : "chưa có dữ liệu";
  $("#v-journal").innerHTML = `
    <div class="grid">
      <div class="card"><h4>tổng thể</h4><div class="mono" style="font-size:12px;color:var(--muted)">${st(p.overall)}</div></div>
      ${Object.entries(p.byRegime || {}).map(([k, v]) => `<div class="card"><h4>regime ${esc(k)}</h4>
        <div class="mono" style="font-size:12px;color:var(--muted)">${st(v)}</div></div>`).join("")}
    </div>
    <h3 class="sec">giao dịch gần đây</h3>
    ${j.trades?.length ? `<table><thead><tr><th>thời điểm</th><th>chiều</th><th>regime</th><th>vào</th><th>ra</th><th>lý do</th><th>P&L</th><th>R</th></tr></thead><tbody>
      ${j.trades.map((t) => `<tr><td>${esc((t.closedAt || t.openedAt || "").slice(5, 16).replace("T", " "))}</td>
        <td class="${t.side === "LONG" ? "pos" : "neg"}">${t.side}</td><td>${esc(t.regimeAtEntry || "—")}</td>
        <td>${fmt(t.entry)}</td><td>${fmt(t.exit)}</td><td>${esc(t.exitReason || "—")}</td>
        <td class="${sgn(t.pnl)}">${money(t.pnl)}</td><td class="${sgn(t.rMultiple)}">${t.rMultiple ?? "—"}</td></tr>`).join("")}
      </tbody></table>` : '<div class="empty">Chưa có giao dịch nào đóng.</div>'}
    <h3 class="sec">bài học (semantic memory)</h3>
    ${j.lessons?.length ? j.lessons.map((l) => `<div class="card" style="margin-bottom:9px">
        <h4>${esc(l.classification)} · ${esc(l.regime || "—")} · ${l.rMultiple ?? "—"}R
          ${l.change_strategy ? '<span class="warn"> · ĐỀ NGHỊ ĐỔI CHIẾN LƯỢC</span>' : ""}</h4>
        <div style="color:var(--muted);font-size:12.5px;line-height:1.6">${esc(l.lesson)}</div></div>`).join("")
      : '<div class="empty">Chưa có bài học nào — bài học chỉ sinh ra sau khi một lệnh đóng.</div>'}`;
}

const PAINT = { flow: paintFlow, state: paintState, thesis: paintThesis, risk: paintRisk, journal: paintJournal };
let activeView = "flow";

function repaint() {
  paintHeader();
  paintFlow();
  (PAINT[activeView] || (() => {}))();
}

/* ── DÒNG SỰ KIỆN + SSE ────────────────────────────────────────────────── */
function pushEvent(ev) {
  HOT.set(ev.stage, Date.now() + 2600);
  const log = $("#log");
  const stick = log.scrollTop + log.clientHeight >= log.scrollHeight - 30;
  const div = document.createElement("div");
  div.className = "ev " + ev.stage;
  div.innerHTML = `<time>${esc(ev.ts.slice(11, 19))}</time><span class="stg">${esc(ev.stage)}</span>` +
                  `<span class="typ">${esc(ev.type)}</span><span class="txt">${esc(ev.msg || "")}</span>`;
  log.appendChild(div);
  while (log.children.length > 400) log.removeChild(log.firstChild);
  if (stick) log.scrollTop = log.scrollHeight;
}

function connect() {
  const es = new EventSource("/api/stream");
  es.addEventListener("bus", (e) => { pushEvent(JSON.parse(e.data)); paintFlow(); });
  es.addEventListener("state", (e) => { STATE = JSON.parse(e.data); repaint(); });
  es.onerror = () => { /* EventSource tự kết nối lại */ };
}

/* ── CHAT ──────────────────────────────────────────────────────────────── */
const history = [];

function bubble(role, text = "") {
  const wrap = document.createElement("div");
  wrap.className = "msg " + (role === "user" ? "user" : "bot");
  wrap.innerHTML = `<div class="who">${role === "user" ? "bạn" : "bộ não"}</div><div class="bubble"></div>`;
  wrap.querySelector(".bubble").textContent = text;
  $("#msgs").appendChild(wrap);
  $("#msgs").scrollTop = $("#msgs").scrollHeight;
  return wrap.querySelector(".bubble");
}

async function send(text) {
  if (!text.trim()) return;
  $("#input").value = "";
  bubble("user", text);
  history.push({ role: "user", content: text });
  const out = bubble("bot", "…");
  let acc = "";

  const res = await fetch("/api/chat", {
    method: "POST", headers: { "content-type": "application/json" },
    body: JSON.stringify({ messages: history }),
  });
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const parts = buf.split("\n\n");
    buf = parts.pop();
    for (const p of parts) {
      const line = p.split("\n").find((l) => l.startsWith("data: "));
      if (!line) continue;
      const obj = JSON.parse(line.slice(6));
      if (obj.delta) {
        acc += obj.delta;
        out.textContent = acc;
        $("#msgs").scrollTop = $("#msgs").scrollHeight;
      }
    }
  }
  history.push({ role: "assistant", content: acc || "(rỗng)" });
}

/* ── NỐI DÂY ───────────────────────────────────────────────────────────── */
document.querySelectorAll(".tab").forEach((t) => t.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach((x) => x.classList.remove("on"));
  document.querySelectorAll(".view").forEach((x) => x.classList.remove("on"));
  t.classList.add("on");
  activeView = t.dataset.v;
  $("#v-" + activeView).classList.add("on");
  repaint();
}));

const ctl = (action) => fetch("/api/control", {
  method: "POST", headers: { "content-type": "application/json" },
  body: JSON.stringify({ action }),
});

$("#btnAnalyze").onclick = () => ctl("analyze");
$("#btnPause").onclick = () => ctl(STATE?.paused ? "resume" : "pause");
$("#btnKill").onclick = () => ctl(STATE?.risk?.halted ? "unkill" : "kill");
$("#btnReset").onclick = () => { if (confirm("Đặt lại tài khoản paper về vốn ban đầu?\nNhật ký giao dịch và bài học vẫn giữ nguyên.")) ctl("reset"); };
$("#send").onclick = () => send($("#input").value);
$("#input").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send($("#input").value); }
});
document.querySelectorAll(".suggest button").forEach((b) => b.onclick = () => send(b.dataset.q));

buildFlow();
fetch("/api/state").then((r) => r.json()).then((s) => { STATE = s; repaint(); });
connect();
setInterval(paintFlow, 700);
