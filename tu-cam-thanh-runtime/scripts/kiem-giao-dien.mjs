/* Kiểm giao diện: mọi trường web/app.js ĐỌC đều phải có thật trong API.
 *
 *     node scripts/kiem-giao-dien.mjs        (runtime phải đang chạy)
 *
 * Đây là chỗ hỏng dễ nhất và im lặng nhất của một dashboard: đổi tên một
 * trường ở backend, frontend đọc ra `undefined`, và giao diện hiện "—" hoặc
 * "NaN" ở đúng ô mà người dùng tin nhất. Không có lỗi nào trong console,
 * không có test nào đỏ.
 *
 * Danh sách dưới đây phải sửa cùng lúc với app.js. Nếu thấy nó lệch, đó
 * chính là thứ phép kiểm này sinh ra để bắt.
 */

const CONG = process.env.PORT || 5182;
const goc = `http://127.0.0.1:${CONG}`;

/* Đường dẫn app.js đọc. `?` = được phép null nhưng KHÓA phải tồn tại. */
const CAN_STATE = [
  "symbol", "price", "ticks", "paused", "mode", "venue", "spotOnly",
  "timeframes.primary", "timeframes.context",
  "dataSource.name", "dataSource.live",
  "regime?.primary", "regime?.quality", "regime?.reasons", "regime?.flags",
  "marketState?.timeframes",
  "thesis?", "decision?",
  "account.equity", "account.equityMarked", "account.availableQuote",
  "account.peakEquity", "account.todayPnl", "account.drawdownPct",
  "account.positions", "account.closedCount",
  "risk.halted?", "risk.breakers", "risk.limits.startingEquity",
  "risk.limits.maxRiskPerTradePct", "risk.limits.maxDailyLossPct",
  "risk.limits.maxDrawdownPct", "risk.limits.minRR", "risk.limits.minConfidence",
  "risk.limits.minStopAtr", "risk.limits.maxStopAtr", "risk.limits.maxOpenPositions",
  "brain.mode", "brain.model", "brain.today.usd", "brain.today.calls",
  "brain.budgetUsd", "brain.blocked?",
];

const CAN_JOURNAL = [
  "trades", "lessons", "theses",
  "performance.overall", "performance.byRegime", "performance.byStrategy",
];

/* Feature khung chính mà phòng "bộ não thị trường" và "vị thế" đọc. */
const CAN_FEATURE = [
  "emaStack", "rsi14", "adx", "volumeRatio", "atrPct", "atrRatioVsMedian",
  "structure", "macdHist", "macdHistSlope", "volatility",
];

let sai = 0;
const bao = (m) => { console.log("  SAI  " + m); sai++; };
const ok = (m) => console.log("  OK   " + m);

function lay(obj, duong) {
  const cho = duong.replace(/\?/g, "");
  return cho.split(".").reduce((o, k) => (o == null ? undefined : o[k]), obj);
}

function soat(obj, ds, ten) {
  const thieu = [];
  for (const d of ds) {
    const chonull = d.includes("?");
    const v = lay(obj, d);
    if (v === undefined) thieu.push(d);
    else if (v === null && !chonull) thieu.push(d + " (null mà không được phép)");
  }
  if (thieu.length) { thieu.forEach((t) => bao(`${ten}: thiếu ${t}`)); }
  else ok(`${ten}: đủ ${ds.length} trường`);
}

const res = await fetch(`${goc}/api/state`).catch(() => null);
if (!res || !res.ok) {
  console.log(`\n  SAI  không gọi được ${goc}/api/state — runtime chưa chạy?`);
  process.exit(1);
}
const S = await res.json();
const J = await (await fetch(`${goc}/api/journal`)).json();

console.log("\n[1] /api/state");
soat(S, CAN_STATE, "state");

console.log("\n[2] feature khung chính");
const f = S.marketState?.timeframes?.[S.timeframes?.primary];
if (!f) bao(`không có feature cho khung ${S.timeframes?.primary}`);
else soat(f, CAN_FEATURE, `feature ${S.timeframes.primary}`);

console.log("\n[3] /api/journal");
soat(J, CAN_JOURNAL, "journal");

console.log("\n[4] hình dạng mảng");
for (const [ten, v] of [["trades", J.trades], ["lessons", J.lessons], ["theses", J.theses],
                        ["positions", S.account.positions], ["breakers", S.risk.breakers]]) {
  Array.isArray(v) ? ok(`${ten} là mảng (${v.length})`) : bao(`${ten} KHÔNG phải mảng`);
}

console.log("\n[5] trường của phần tử (nếu có dữ liệu)");
const KIEM_PHAN_TU = [
  ["trade", J.trades?.[0], ["id", "side", "entry", "pnl", "rMultiple", "exitReason", "regimeAtEntry"]],
  ["lesson", J.lessons?.[0], ["classification", "lesson", "change_strategy", "regime_appropriate",
                              "entry_valid", "size_valid", "stop_placement_valid", "tradeId"]],
  ["thesis", J.theses?.[0], ["action", "confidence", "regime_read", "strategy", "source", "at"]],
  ["position", S.account.positions?.[0], ["side", "entry", "stopLoss", "targets", "qty", "riskAmount"]],
];
for (const [ten, mau, truong] of KIEM_PHAN_TU) {
  if (!mau) { console.log(`  —    ${ten}: chưa có dữ liệu để kiểm`); continue; }
  const thieu = truong.filter((t) => mau[t] === undefined);
  thieu.length ? bao(`${ten}: thiếu ${thieu.join(", ")}`) : ok(`${ten}: đủ ${truong.length} trường`);
}

console.log("\n[6] /api/candles — biểu đồ");
const C = await (await fetch(`${goc}/api/candles`)).json();
if (!C.ready) bao("candles: chưa sẵn sàng (vòng lặp chưa chạy lượt nào?)");
else {
  soat(C, ["symbol", "price", "primary", "timeframes", "overlay"], "candles");
  const tf = C.timeframes?.[C.primary] || [];
  Array.isArray(tf) && tf.length ? ok(`nến khung ${C.primary}: ${tf.length}`)
    : bao(`không có nến cho khung ${C.primary}`);
  if (tf[0]) {
    const thieu = ["t", "o", "h", "l", "c", "v", "closed"].filter((k) => tf[0][k] === undefined);
    thieu.length ? bao(`nến thiếu ${thieu.join(", ")}`) : ok("nến đủ 7 trường OHLCV");
  }
  soat(C.overlay, ["ema20?", "ema50?", "ema200?", "support", "resistance",
                   "entryZone?", "stopLoss?", "targets", "positions"], "overlay");
}

console.log("\n[7] /api/skills — kho kỹ năng");
const K = await (await fetch(`${goc}/api/skills`)).json();
soat(K, ["skills", "tong"], "skills");
if (K.skills?.[0]) {
  const thieu = ["ma", "tieuDe", "moTa", "soDong", "soKyTu"].filter((k) => K.skills[0][k] === undefined);
  thieu.length ? bao(`kỹ năng thiếu ${thieu.join(", ")}`) : ok(`kỹ năng đủ 5 trường (${K.tong} kỹ năng)`);
} else bao("không đọc được kỹ năng nào — skills/ trống?");

console.log("\n" + "=".repeat(58));
if (sai) { console.log(`  ${sai} chỗ lệch giữa app.js và API.`); process.exit(1); }
console.log("  GIAO DIỆN ĐỌC ĐƯỢC MỌI TRƯỜNG NÓ CẦN.");
console.log("=".repeat(58));
