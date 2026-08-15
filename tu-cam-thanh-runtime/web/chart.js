/* ═══════════════════════════════════════════════════════════════════
   Biểu đồ nến — canvas thuần, không thư viện.

   Vì sao không dùng lightweight-charts hay TradingView: trang này phải chạy
   được offline và không kéo script từ CDN nào. Vẽ nến là hình học đơn giản;
   thứ khó là phần LỚP PHỦ, mà thư viện ngoài cũng không làm hộ được.

   Lớp phủ mới là điểm chính. Một biểu đồ nến trần không nói được điều đáng
   nói nhất: **bot đang nhìn chỗ nào trên đó**. Nên vẽ kèm EMA, vùng hỗ trợ/
   kháng cự, và các mức của luận điểm hiện tại (vùng vào, stop, mục tiêu) —
   để nhìn một phát là thấy vì sao nó nói "chưa đủ RR".
   ═══════════════════════════════════════════════════════════════════ */

export function veNen(canvas, du_lieu, opt = {}) {
  const nen = du_lieu.nen || [];
  const ov = du_lieu.overlay || {};
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.clientWidth, H = canvas.clientHeight;
  if (!W || !H || !nen.length) return;

  canvas.width = W * dpr; canvas.height = H * dpr;
  const g = canvas.getContext("2d");
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.clearRect(0, 0, W, H);

  const L = 4, R = 74, T = 10, B = 22;          // chừa lề phải cho thang giá
  const w = W - L - R, h = H - T - B;

  // Biên giá phải gồm cả mức của luận điểm, nếu không stop/mục tiêu nằm
  // ngoài khung và người xem tưởng bot đặt lệnh ở đâu đó vô hình.
  let lo = Math.min(...nen.map((c) => c.l));
  let hi = Math.max(...nen.map((c) => c.h));
  const them = [ov.stopLoss, ...(ov.targets || []), ...(ov.entryZone || []),
                ...(ov.positions || []).flatMap((p) => [p.entry, p.stopLoss, ...(p.targets || [])])]
    .filter((x) => typeof x === "number");
  for (const v of them) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
  const dem = (hi - lo) * 0.06 || 1;
  lo -= dem; hi += dem;

  const y = (p) => T + h - ((p - lo) / (hi - lo)) * h;
  const bw = Math.max(1.5, (w / nen.length) * 0.62);
  const x = (i) => L + (i + 0.5) * (w / nen.length);

  const css = getComputedStyle(document.documentElement);
  const mau = (n, fb) => (css.getPropertyValue(n) || fb).trim();
  const LUC = mau("--green", "#4ade80"), DO = mau("--red", "#f87171");
  const LAM = mau("--cyan", "#22d3ee"), TIM = mau("--violet", "#a78bfa");
  const AM = mau("--amber", "#fbbf24"), MO = mau("--fg-4", "#3d4a5e");

  // ── lưới + thang giá ────────────────────────────────────────────
  g.font = "10px ui-monospace,Menlo,Consolas,monospace";
  g.textBaseline = "middle";
  for (let i = 0; i <= 4; i++) {
    const p = lo + ((hi - lo) * i) / 4, yy = y(p);
    g.strokeStyle = "rgba(125,158,200,.07)";
    g.beginPath(); g.moveTo(L, yy); g.lineTo(L + w, yy); g.stroke();
    g.fillStyle = MO;
    g.fillText(p.toLocaleString("vi-VN", { maximumFractionDigits: 0 }), L + w + 6, yy);
  }

  // ── EMA ─────────────────────────────────────────────────────────
  // Chỉ có GIÁ TRỊ HIỆN TẠI của EMA (feature đo ở nến cuối), không có cả
  // chuỗi — nên vẽ thành đường ngang đứt, và ghi rõ đó là mức hiện tại.
  const emas = [["EMA20", ov.ema20, LAM], ["EMA50", ov.ema50, TIM], ["EMA200", ov.ema200, MO]];
  g.setLineDash([3, 4]); g.lineWidth = 1;
  for (const [ten, v, c] of emas) {
    if (typeof v !== "number") continue;
    g.strokeStyle = c; g.globalAlpha = .55;
    g.beginPath(); g.moveTo(L, y(v)); g.lineTo(L + w, y(v)); g.stroke();
    g.globalAlpha = 1; g.fillStyle = c;
    g.fillText(ten, L + 3, y(v) - 7);
  }
  g.setLineDash([]);

  // ── hỗ trợ / kháng cự ───────────────────────────────────────────
  g.globalAlpha = .3; g.lineWidth = 1;
  for (const p of (ov.support || [])) { g.strokeStyle = LUC; g.beginPath(); g.moveTo(L, y(p)); g.lineTo(L + w, y(p)); g.stroke(); }
  for (const p of (ov.resistance || [])) { g.strokeStyle = DO; g.beginPath(); g.moveTo(L, y(p)); g.lineTo(L + w, y(p)); g.stroke(); }
  g.globalAlpha = 1;

  // ── nến ─────────────────────────────────────────────────────────
  nen.forEach((c, i) => {
    const len = c.c >= c.o;
    g.strokeStyle = g.fillStyle = len ? LUC : DO;
    g.globalAlpha = c.closed === false ? .55 : 1;      // nến chưa đóng mờ đi
    g.lineWidth = 1;
    g.beginPath(); g.moveTo(x(i), y(c.h)); g.lineTo(x(i), y(c.l)); g.stroke();
    const yo = y(c.o), yc = y(c.c);
    g.fillRect(x(i) - bw / 2, Math.min(yo, yc), bw, Math.max(1, Math.abs(yc - yo)));
  });
  g.globalAlpha = 1;

  // ── mức của luận điểm / vị thế ──────────────────────────────────
  const veMuc = (p, c, nhan) => {
    if (typeof p !== "number") return;
    g.strokeStyle = c; g.lineWidth = 1.4; g.setLineDash([6, 3]);
    g.beginPath(); g.moveTo(L, y(p)); g.lineTo(L + w, y(p)); g.stroke();
    g.setLineDash([]);
    const tw = g.measureText(nhan).width + 8;
    g.fillStyle = c; g.globalAlpha = .16;
    g.fillRect(L + w - tw, y(p) - 8, tw, 16);
    g.globalAlpha = 1; g.fillStyle = c;
    g.fillText(nhan, L + w - tw + 4, y(p));
  };

  if (ov.entryZone?.length === 2) {
    g.fillStyle = AM; g.globalAlpha = .1;
    g.fillRect(L, y(Math.max(...ov.entryZone)), w, Math.abs(y(ov.entryZone[0]) - y(ov.entryZone[1])) || 2);
    g.globalAlpha = 1;
  }
  veMuc(ov.stopLoss, DO, "SL");
  (ov.targets || []).forEach((t, i) => veMuc(t, LUC, "TP" + (i + 1)));
  (ov.positions || []).forEach((p) => {
    veMuc(p.entry, LAM, "VÀO");
    veMuc(p.stopLoss, DO, "SL");
    (p.targets || []).forEach((t, i) => veMuc(t, LUC, "TP" + (i + 1)));
  });

  // ── giá hiện tại ────────────────────────────────────────────────
  const gia = nen[nen.length - 1].c;
  g.strokeStyle = "rgba(233,238,247,.5)"; g.lineWidth = 1; g.setLineDash([2, 3]);
  g.beginPath(); g.moveTo(L, y(gia)); g.lineTo(L + w, y(gia)); g.stroke();
  g.setLineDash([]);
  const s = gia.toLocaleString("vi-VN", { maximumFractionDigits: 2 });
  g.fillStyle = "#e9eef7"; g.fillRect(L + w + 2, y(gia) - 8, R - 4, 16);
  g.fillStyle = "#0b0f17"; g.fillText(s, L + w + 6, y(gia));

  // ── nhãn khung + số nến ─────────────────────────────────────────
  g.fillStyle = MO;
  g.fillText(`${opt.symbol || ""} · ${opt.tf || ""} · ${nen.length} nến`, L + 2, H - 9);
}
