/* ═══════════════════════════════════════════════════════
   Tử Cấm Thành — giao diện.

   Đọc `window.TU_CAM_THANH` do runtime ghi ra. KHÔNG fetch, KHÔNG
   gọi API, không có khoá nào ở đây: trang này là GitHub Pages công
   khai. Muốn số liệu tươi thì chạy runtime ở máy rồi commit lát cắt.

   Chưa có lát cắt nào thì trang vẫn phải đọc được — phần kiến trúc
   và sơ đồ luôn hiện, chỉ các ô số là trống. Một cung mới nối vào mà
   trắng trang thì người xem tưởng hỏng.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var D = window.TU_CAM_THANH || null;
  var co = !!(D && D.generatedAt && D.gia);

  /* ── tiện ích ──────────────────────────────────────── */
  function esc(s) {
    return String(s === null || s === undefined ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function so(v, n) {
    if (v === null || v === undefined || isNaN(v)) return "—";
    return Number(v).toLocaleString("vi-VN", { minimumFractionDigits: n === undefined ? 2 : n,
                                               maximumFractionDigits: n === undefined ? 2 : n });
  }
  function tien(v) {
    if (v === null || v === undefined || isNaN(v)) return "—";
    return (v < 0 ? "−$" : "$") + so(Math.abs(v));
  }
  function dau(v) { return v > 0 ? "len" : v < 0 ? "xuong" : ""; }
  function ngay(iso) {
    if (!iso) return "—";
    var d = new Date(iso);
    if (isNaN(d)) return "—";
    function p(n) { return n < 10 ? "0" + n : "" + n; }
    return p(d.getDate()) + "/" + p(d.getMonth() + 1) + "/" + d.getFullYear() +
           " " + p(d.getHours()) + ":" + p(d.getMinutes());
  }
  function cachDay(iso) {
    if (!iso) return null;
    var ms = Date.now() - new Date(iso).getTime();
    if (isNaN(ms) || ms < 0) return null;
    var phut = Math.floor(ms / 60000);
    if (phut < 60) return phut + " phút trước";
    var gio = Math.floor(phut / 60);
    if (gio < 24) return gio + " giờ trước";
    return Math.floor(gio / 24) + " ngày trước";
  }
  function el(id) { return document.getElementById(id); }
  function hang(k, v, cls) {
    return '<div class="hang"><span>' + esc(k) + '</span><b class="' + (cls || "") + '">' + esc(v) + "</b></div>";
  }
  function o(nhan, giatri, cls, phu) {
    return '<div class="o"><i>' + esc(nhan) + '</i><b class="' + (cls || "") + '">' + esc(giatri) + "</b>" +
           (phu ? "<small>" + esc(phu) + "</small>" : "") + "</div>";
  }
  function trong(msg) { return '<div class="trong">' + esc(msg) + "</div>"; }

  /* ── dải trạng thái ────────────────────────────────── */
  function veDai() {
    var host = el("dai");
    if (!co) {
      host.innerHTML = '<span class="vien tinh">chưa có lát cắt nào</span>' +
        '<span class="day"></span><span class="vien">chạy runtime rồi commit assets/js/v/phien.js</span>';
      el("dinhPhu").textContent = "chưa có dữ liệu";
      return;
    }
    var nguonThat = D.nguon && D.nguon.live;
    var bn = D.boNao || {};
    var cu = cachDay(D.generatedAt);

    host.innerHTML =
      '<span class="vien ' + (nguonThat ? "song" : "dut") + '">' +
        (nguonThat ? "nguồn thật · " + esc(D.nguon.name) : "⚠ nến tổng hợp — đừng tin số") + "</span>" +
      '<span class="vien">' + esc(D.cap) + " · " + esc((D.khung && D.khung.primary) || "") +
        "+" + esc((D.khung && D.khung.context) || "") + "</span>" +
      '<span class="vien ' + (bn.cheDo === "claude" ? "song" : "tinh") + '">bộ não ' + esc(bn.cheDo || "—") +
        (bn.model ? " · " + esc(bn.model) : "") + "</span>" +
      (D.rui_ro && D.rui_ro.dungHan ? '<span class="vien dut">ĐÃ DỪNG · ' + esc(D.rui_ro.dungHan) + "</span>" : "") +
      (D.tamDung ? '<span class="vien tinh">tạm dừng</span>' : "") +
      '<span class="day"></span>' +
      '<span class="vien">lát cắt ' + esc(ngay(D.generatedAt)) + (cu ? " · " + esc(cu) : "") + "</span>";

    el("dinhPhu").textContent = D.cap + " · " + so(D.gia) + " · " + ((D.cheDo && D.cheDo.primary) || "—");
  }

  /* ── ô số phiên ────────────────────────────────────── */
  function vePhien() {
    var host = el("oPhien");
    if (!co) {
      host.innerHTML = trong("Chưa có phiên nào được ghi. Chạy runtime ở máy — xem mục “Cách chạy” bên dưới.");
      return;
    }
    var tk = D.taiKhoan || {};
    var cd = D.cheDo || {};
    var lai = (tk.von || 0) - (tk.vonBanDau || 0);
    var laiPct = tk.vonBanDau ? (lai / tk.vonBanDau) * 100 : 0;

    host.innerHTML = '<div class="o-so">' +
      o("giá", so(D.gia), "son") +
      o("chế độ thị trường", cd.primary || "—", "", cd.quality ? "chất lượng " + cd.quality : "") +
      o("vốn", tien(tk.von), dau(lai), "ban đầu " + tien(tk.vonBanDau)) +
      o("lãi/lỗ tích luỹ", tien(lai), dau(lai), so(laiPct) + "%") +
      o("lãi/lỗ hôm nay", tien(tk.laiLoHomNay), dau(tk.laiLoHomNay)) +
      o("drawdown", so(tk.drawdownPct) + "%",
        tk.drawdownPct > 0 ? "nhac" : "", "đỉnh " + tien(tk.dinhVon)) +
      o("lệnh đã đóng", tk.soLenhDaDong === undefined ? "—" : tk.soLenhDaDong) +
      o("vị thế đang mở", (tk.viThe || []).length) +
      o("vòng đã chạy", D.vong === undefined ? "—" : D.vong) +
      o("chi phí model hôm nay",
        D.boNao && D.boNao.homNay ? "$" + Number(D.boNao.homNay.usd || 0).toFixed(4) : "—",
        "", D.boNao && D.boNao.homNay ? (D.boNao.homNay.calls || 0) + " lượt · trần $" + (D.boNao.hanMucUsd || 0) : "") +
    "</div>";
  }

  /* ── sơ đồ dữ liệu ─────────────────────────────────── */
  function veSoDo() {
    var pq = D && D.phanQuyet;
    var ld = D && D.luanDiem;
    var tk = (D && D.taiKhoan) || {};
    var cd = (D && D.cheDo) || {};
    var f = D && D.thiTruong && D.khung ? D.thiTruong[D.khung.primary] : null;

    var chan = pq && !pq.approved && pq.action !== "NO_TRADE";

    var nut = [
      ["Thế giới", "giá · khối lượng · thời gian", false],
      ["Market Data Engine",
        co ? (D.nguon.name + (D.nguon.live ? "" : "  ⚠ TỔNG HỢP") + " · " + so(D.gia)) : "—", co],
      ["Feature Factory",
        f ? ("EMA " + f.emaStack + " · RSI " + f.rsi14 + " · ADX " + f.adx + " · ATR% " + f.atrPct) : "—", !!f],
      ["Market State → Regime",
        cd.primary ? (cd.primary + " · chất lượng " + cd.quality +
          (cd.flags && cd.flags.length ? " · " + cd.flags.join(",") : "")) : "—", !!cd.primary],
      ["__DOI__",
        ["Memory Engine", "episodic · semantic · procedural · performance",
         "Claude Brain", D.boNao ? (D.boNao.cheDo + " · " + (D.boNao.soKyNang || 0) + " kỹ năng") : "—"]],
      ["Trade Thesis",
        ld ? (ld.action + " · tin cậy " + so(ld.confidence, 2) + " · " + ld.strategy) : "chưa có luận điểm nào", !!ld],
      ["Risk Engine  (Python thuần — có quyền phủ quyết)",
        !pq ? "chưa thẩm định lượt nào"
          : pq.approved ? ("CHO QUA · RR " + so(pq.rr) + " · rủi ro " + tien(pq.position && pq.position.riskAmount))
          : pq.action === "NO_TRADE" ? "NO_TRADE — bộ não chủ động đứng ngoài"
          : "CHẶN · " + (pq.rejections || []).join(" | "),
        !!pq, chan],
      ["Execution  (sàn giấy)",
        (tk.viThe || []).length ? ((tk.viThe.length) + " vị thế mở · P&L mở " + tien(tk.laiLoMo))
                                : "không có vị thế mở", !!co],
      ["Trade Journal", (tk.soLenhDaDong || 0) + " lệnh đã đóng", (tk.soLenhDaDong || 0) > 0],
      ["Post-Mortem → Lesson Memory",
        (D && D.baiHoc || []).length ? ((D.baiHoc.length) + " bài học đã lưu")
                                     : "quyết định ≠ kết quả", (D && D.baiHoc || []).length > 0]
    ];

    var h = "";
    nut.forEach(function (n, i) {
      if (i) h += '<div class="mui"></div>';
      if (n[0] === "__DOI__") {
        h += '<div class="doi">' +
          '<div class="nut"><i>' + esc(n[1][0]) + "</i><b>" + esc(n[1][1]) + "</b></div>" +
          '<div class="nut' + (D && D.boNao ? " hot" : "") + '"><i>' + esc(n[1][2]) + "</i><b>" + esc(n[1][3]) + "</b></div>" +
        "</div>";
        return;
      }
      h += '<div class="nut' + (n[2] ? " hot" : "") + (n[3] ? " chan" : "") + '">' +
             "<i>" + esc(n[0]) + "</i><b>" + esc(n[1]) + "</b></div>";
    });
    h += '<div class="mui"></div><div class="nut" style="border-style:dashed">' +
         "<i>↺ quay lại Memory Engine</i><b>bài học của vòng này là ngữ cảnh của vòng sau</b></div>";
    el("soDo").innerHTML = h;
  }

  /* ── luận điểm ─────────────────────────────────────── */
  function veLuanDiem() {
    var host = el("oLuanDiem");
    var t = D && D.luanDiem;
    if (!t) {
      host.innerHTML = trong("Chưa có luận điểm nào. Bộ não chỉ thức khi có nến mới đóng, khi chế độ thị trường đổi, hoặc khi bấm tay ở buồng lái.");
      return;
    }
    var cls = t.action === "LONG" ? "len" : t.action === "SHORT" ? "xuong" : "nhac";
    var h = '<div class="luoi">' +
      '<div class="the"><h3>quyết định</h3>' +
        hang("hành động", t.action, cls) +
        hang("độ tin cậy", so(t.confidence, 2)) +
        hang("bộ não đọc chế độ", t.regime_read) +
        hang("bộ phân loại nói", t.regimeFromClassifier) +
        hang("chiến lược", t.strategy) +
        hang("rủi ro sự kiện", t.event_risk) +
      "</div>" +
      '<div class="the"><h3>mức giá</h3>' +
        hang("vùng vào", (t.entry_zone || []).map(function (x) { return so(x); }).join(" – ") || "—") +
        hang("vô hiệu hoá (SL)", so(t.invalidation)) +
        hang("mục tiêu", (t.targets || []).map(function (x) { return so(x); }).join(" · ") || "—") +
        hang("rủi ro đề xuất", (t.suggested_risk_pct || 0) + "%") +
        (t.invalidation_logic ? '<p style="margin:9px 0 0;font-size:12.5px;color:var(--fg-3);line-height:1.6">' +
          esc(t.invalidation_logic) + "</p>" : "") +
      "</div></div>";

    if (t.scenarios && t.scenarios.length) {
      h += '<h2 class="tieu" style="margin-top:18px">kịch bản</h2><div class="luoi">' +
        t.scenarios.map(function (s) {
          return '<div class="the"><h3>' + esc(s.name) + " — " + Math.round((s.probability || 0) * 100) + "%</h3>" +
            '<p style="margin:0;font-size:13px;color:var(--fg-2);line-height:1.6">' + esc(s.description) + "</p></div>";
        }).join("") + "</div>";
    }
    if (t.reasoning) {
      h += '<h2 class="tieu" style="margin-top:18px">lập luận</h2>' +
        '<div class="the" style="white-space:pre-wrap;font-size:13.5px;color:var(--fg-2);line-height:1.7">' +
        esc(t.reasoning) + "</div>";
    }
    if (t.reason_codes && t.reason_codes.length) {
      h += '<div class="the mono" style="margin-top:10px;font-size:11.5px;color:var(--fg-3)">' +
        esc(t.reason_codes.join(" · ")) + "</div>";
    }
    host.innerHTML = h;
  }

  /* ── rủi ro & vị thế ───────────────────────────────── */
  function veRuiRo() {
    var host = el("oRuiRo");
    var r = (D && D.rui_ro) || {};
    var gh = r.gioiHan || {};
    var tk = (D && D.taiKhoan) || {};
    var pq = D && D.phanQuyet;
    var h = "";

    if (r.dungHan) {
      h += '<div class="the" style="border-color:var(--do);margin-bottom:12px">' +
        '<h3 style="color:var(--do)">đã dừng</h3><div class="mono xuong">' + esc(r.dungHan) + "</div></div>";
    }
    if ((r.ngatMach || []).length) {
      h += '<div class="the" style="border-color:var(--vang);margin-bottom:12px"><h3 style="color:var(--vang)">ngắt mạch đang bật</h3>' +
        r.ngatMach.map(function (b) { return '<div class="mono nhac" style="font-size:11.5px">• ' + esc(b) + "</div>"; }).join("") +
        "</div>";
    }

    h += '<div class="luoi">' +
      '<div class="the"><h3>giới hạn cứng</h3>' +
        hang("rủi ro mỗi lệnh", (gh.maxRiskPerTradePct === undefined ? "—" : gh.maxRiskPerTradePct + "%")) +
        hang("RR tối thiểu (sau phí)", gh.minRR === undefined ? "—" : gh.minRR) +
        hang("tin cậy tối thiểu", gh.minConfidence === undefined ? "—" : gh.minConfidence) +
        hang("khoảng stop", gh.minStopAtr === undefined ? "—" : gh.minStopAtr + "–" + gh.maxStopAtr + " × ATR") +
        hang("trần lỗ ngày", gh.maxDailyLossPct === undefined ? "—" : gh.maxDailyLossPct + "%") +
        hang("kill switch drawdown", gh.maxDrawdownPct === undefined ? "—" : gh.maxDrawdownPct + "%") +
        hang("vị thế mở tối đa", gh.maxOpenPositions === undefined ? "—" : gh.maxOpenPositions) +
      "</div>" +
      '<div class="the"><h3>tài khoản</h3>' +
        hang("vốn (đã đánh dấu)", tien(tk.von)) +
        hang("vốn thực hiện", tien(tk.vonThucHien)) +
        hang("P&L mở", tien(tk.laiLoMo), dau(tk.laiLoMo)) +
        hang("P&L hôm nay", tien(tk.laiLoHomNay), dau(tk.laiLoHomNay)) +
        hang("đỉnh vốn", tien(tk.dinhVon)) +
        hang("drawdown", (tk.drawdownPct === undefined ? "—" : tk.drawdownPct + "%")) +
      "</div>" +
      (pq ? '<div class="the"><h3>phán quyết gần nhất</h3>' +
        hang("kết quả", pq.approved ? "CHO QUA" : pq.action === "NO_TRADE" ? "NO_TRADE" : "CHẶN",
             pq.approved ? "len" : pq.action === "NO_TRADE" ? "nhac" : "xuong") +
        hang("RR", so(pq.rr)) +
        hang("ghi chú", pq.note || "—") +
        (pq.rejections || []).map(function (x) {
          return '<div class="mono xuong" style="font-size:11px;margin-top:3px">• ' + esc(x) + "</div>";
        }).join("") +
      "</div>" : "") +
    "</div>";

    h += '<h2 class="tieu" style="margin-top:18px">vị thế đang mở</h2>';
    if ((tk.viThe || []).length) {
      h += '<div class="cuon"><table><thead><tr><th>chiều</th><th>vào</th><th>SL</th><th>TP1</th>' +
        "<th>khối lượng</th><th>rủi ro</th><th>P&L</th><th>R</th></tr></thead><tbody>" +
        tk.viThe.map(function (p) {
          return "<tr><td class=\"" + (p.side === "LONG" ? "len" : "xuong") + "\">" + esc(p.side) + "</td>" +
            "<td>" + so(p.entry) + "</td><td>" + so(p.stopLoss) + "</td>" +
            "<td>" + so(p.targets && p.targets[0]) + "</td>" +
            "<td>" + Number(p.qty || 0).toFixed(6) + "</td><td>" + tien(p.riskAmount) + "</td>" +
            '<td class="' + dau(p.unrealizedPnl) + '">' + tien(p.unrealizedPnl) + "</td>" +
            '<td class="' + dau(p.unrealizedR) + '">' + (p.unrealizedR === undefined ? "—" : p.unrealizedR) + "</td></tr>";
        }).join("") + "</tbody></table></div>";
    } else {
      h += trong("Không có vị thế nào đang mở.");
    }
    host.innerHTML = h;
  }

  /* ── nhật ký & bài học ─────────────────────────────── */
  function veNhatKy() {
    var host = el("oNhatKy");
    var tk = (D && D.thongKe) || {};
    var gd = (D && D.giaoDich) || [];
    var bh = (D && D.baiHoc) || [];
    var h = "";

    function ke(x) {
      if (!x || !x.count) return "chưa có dữ liệu";
      return x.count + " lệnh · thắng " + x.winRate + "% · kỳ vọng " + x.expectancyR + "R · " + tien(x.totalPnl);
    }
    h += '<div class="luoi">' +
      '<div class="the"><h3>tổng thể</h3><div class="mono" style="font-size:12.5px;color:var(--fg-2)">' +
        esc(ke(tk.overall)) + "</div></div>" +
      Object.keys(tk.byRegime || {}).map(function (k) {
        return '<div class="the"><h3>chế độ ' + esc(k) + "</h3>" +
          '<div class="mono" style="font-size:12.5px;color:var(--fg-2)">' + esc(ke(tk.byRegime[k])) + "</div></div>";
      }).join("") + "</div>";

    h += '<h2 class="tieu" style="margin-top:18px">giao dịch gần đây</h2>';
    if (gd.length) {
      h += '<div class="cuon"><table><thead><tr><th>thời điểm</th><th>chiều</th><th>chế độ</th>' +
        "<th>vào</th><th>ra</th><th>lý do thoát</th><th>P&L</th><th>R</th></tr></thead><tbody>" +
        gd.slice().reverse().map(function (t) {
          return "<tr><td>" + esc(ngay(t.closedAt || t.openedAt)) + "</td>" +
            '<td class="' + (t.side === "LONG" ? "len" : "xuong") + '">' + esc(t.side) + "</td>" +
            "<td>" + esc(t.regimeAtEntry || "—") + "</td><td>" + so(t.entry) + "</td><td>" + so(t.exit) + "</td>" +
            "<td>" + esc(t.exitReason || "—") + "</td>" +
            '<td class="' + dau(t.pnl) + '">' + tien(t.pnl) + "</td>" +
            '<td class="' + dau(t.rMultiple) + '">' + (t.rMultiple === undefined ? "—" : t.rMultiple) + "</td></tr>";
        }).join("") + "</tbody></table></div>";
    } else {
      h += trong("Chưa có giao dịch nào đóng.");
    }

    h += '<h2 class="tieu" style="margin-top:18px">bài học (semantic memory)</h2>';
    if (bh.length) {
      h += bh.slice().reverse().map(function (l) {
        var c = l.classification || "";
        var k = c.indexOf("BAD_TRADE") === 0 ? "xau" : c.indexOf("BAD_OUTCOME") !== -1 ? "canh" : "tot";
        return '<div class="bai ' + k + '"><div class="dinh">' + esc(c) + " · " + esc(l.regime || "—") +
          " · " + (l.rMultiple === undefined ? "—" : l.rMultiple) + "R" +
          (l.change_strategy ? ' · <span class="nhac">ĐỀ NGHỊ ĐỔI CHIẾN LƯỢC</span>' : "") +
          "</div><p>" + esc(l.lesson) + "</p></div>";
      }).join("");
    } else {
      h += trong("Chưa có bài học nào — bài học chỉ sinh ra sau khi một lệnh đóng lại.");
    }
    host.innerHTML = h;
  }

  /* ── thanh bên trên máy hẹp ────────────────────────── */
  function benMo() {
    var nut = el("benMoNut"), ben = el("ben");
    if (!nut || !ben) return;
    nut.addEventListener("click", function () {
      ben.dataset.mo = ben.dataset.mo === "1" ? "0" : "1";
    });
    ben.addEventListener("click", function (e) {
      if (e.target.closest("a")) ben.dataset.mo = "0";
    });
  }

  veDai();
  vePhien();
  veSoDo();
  veLuanDiem();
  veRuiRo();
  veNhatKy();
  benMo();
})();
