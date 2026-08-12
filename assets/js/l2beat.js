/* ═══════════════════════════════════════════════════════
   Hồ sơ tự trị của thành phố — dữ liệu từ L2BEAT.

   Dữ liệu nằm trong live.js (window.KT_DATA.L2BEAT), do
   scripts/build-live.mjs sinh ra mỗi 6 giờ.

   app.js gọi vào đây qua hai móc, cả hai đều có rào
   `if (window.KT_L2B)`. Xoá file này đi thì app chạy y như cũ,
   chỉ mất huy hiệu và khối hồ sơ.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var DATA = (window.KT_DATA && window.KT_DATA.L2BEAT) || null;
  if (!DATA) return;

  /* phải trùng norm() trong app.js, nếu không tra không ra khoá */
  function norm(s) {
    return String(s).toLowerCase().normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d");
  }

  function find(name) { return DATA[norm(name)] || null; }

  function el(t, c) { var e = document.createElement(t); if (c) e.className = c; return e; }

  function usd(v) {
    if (v == null) return "—";
    if (v >= 1e9) return "$" + (v / 1e9).toFixed(v / 1e9 >= 10 ? 1 : 2) + "b";
    if (v >= 1e6) return "$" + (v / 1e6).toFixed(v / 1e6 >= 100 ? 0 : 1) + "m";
    return "$" + Math.round(v / 1e3) + "k";
  }

  /* Stage 0/1/2 là thang tự trị của L2BEAT. Dịch sang lời của bản đồ này:
     thành phố còn phụ thuộc bao nhiêu vào đội ngũ dựng ra nó. */
  var STAGE_VI = {
    "Stage 0": "Còn phụ thuộc đội vận hành: họ có thể nâng cấp tức thì, dân chưa có đường thoát bảo đảm.",
    "Stage 1": "Đã có chứng minh gian lận và hội đồng an ninh. Dân rút được tài sản kể cả khi đội vận hành ngừng.",
    "Stage 2": "Tự trị gần như hoàn toàn: hợp đồng cai trị, đội ngũ không can thiệp nhanh được nữa."
  };

  /* nhãn rủi ro của L2BEAT → tiếng Việt, đặt theo phép ví kinh thành */
  var RISK_VI = {
    "Sequencer Failure": "Người xếp lịch ngừng việc",
    "State Validation":  "Ai kiểm chứng sổ sách",
    "Data Availability": "Dữ liệu cất ở đâu",
    "Exit Window":       "Cửa thoát khi bị nâng cấp",
    "Proposer Failure":  "Người chốt sổ ngừng việc"
  };

  /* ── móc 1: huy hiệu trên thẻ thành phố ở bản đồ ─────── */
  function badge(card, item, ctx) {
    if (!ctx || ctx.kind !== "l2" || !item || item.more) return;
    var d = find(item.n);
    if (!d || !d.stage || d.stage.indexOf("Stage") !== 0) return;
    var b = el("span", "l2b-tag");
    b.dataset.stage = d.stage.slice(-1);
    b.textContent = "S" + d.stage.slice(-1);
    b.title = d.stage + " · " + (STAGE_VI[d.stage] || "");
    card.appendChild(b);
  }

  /* ── móc 2: khối hồ sơ trong trang thành phố ─────────── */
  function section(frame, cityName, parentId) {
    var d = find(cityName);

    if (!d) {
      // Không có dữ liệu không phải lỗi — với nước không phải Ethereum
      // thì đó chính là một thông tin: L2BEAT không đo loại này.
      if (parentId && parentId !== "eth") {
        var note = el("div", "city-sect l2b-none");
        note.innerHTML =
          '<div class="l2b-none-in"><b>L2BEAT không chấm thành phố này.</b> ' +
          'Thang Stage 0/1/2 chỉ dùng cho lớp mở rộng của Ethereum — nơi thành phố ' +
          'phải chứng minh dân rút được tài sản về nước mẹ kể cả khi đội vận hành biến mất. ' +
          'Mô hình ở đây khác hẳn, nên không có thang chung để so.</div>';
        frame.appendChild(note);
      }
      return;
    }

    var sec = el("div", "city-sect l2b");

    var head = el("div", "l2b-head");
    var left = el("div", "l2b-stage");
    var st = el("span", "l2b-tag big");
    if (d.stage && d.stage.indexOf("Stage") === 0) {
      st.dataset.stage = d.stage.slice(-1);
      st.textContent = d.stage;
    } else {
      st.dataset.stage = "n";
      st.textContent = "Chưa xếp thang";
    }
    left.appendChild(st);
    var kind = el("span", "l2b-kind");
    kind.textContent = [d.category, (d.providers || [])[0]].filter(Boolean).join(" · ");
    left.appendChild(kind);
    head.appendChild(left);

    var num = el("div", "l2b-num");
    num.innerHTML = '<b>' + usd(d.tvs) + '</b><span>tài sản đang giữ' +
      (typeof d.change7d === "number"
        ? ' · <i data-dir="' + (d.change7d >= 0 ? "up" : "down") + '">' +
          (d.change7d >= 0 ? "+" : "") + (d.change7d * 100).toFixed(1) + '% / 7 ngày</i>'
        : "") + '</span>';
    head.appendChild(num);
    sec.appendChild(head);

    if (d.stage && STAGE_VI[d.stage]) {
      var exp = el("p", "l2b-exp");
      exp.textContent = STAGE_VI[d.stage];
      sec.appendChild(exp);
    }

    var grid = el("div", "l2b-risks");
    (d.risks || []).forEach(function (r) {
      var row = el("div", "l2b-risk");
      row.dataset.sent = r.s || "neutral";
      if (r.d) row.title = r.d; // mô tả gốc của L2BEAT, tiếng Anh
      var n = el("span", "rn");
      n.textContent = RISK_VI[r.n] || r.n;
      var v = el("span", "rv");
      v.textContent = r.v;
      row.appendChild(n);
      row.appendChild(v);
      grid.appendChild(row);
    });
    sec.appendChild(grid);

    var src = el("div", "l2b-src");
    src.innerHTML = 'Số liệu và đánh giá rủi ro: <a href="https://l2beat.com/scaling/projects/' +
      encodeURIComponent(d.slug) + '" target="_blank" rel="noopener">L2BEAT · ' +
      (d.name || cityName) + '</a>. Di chuột vào từng dòng để xem giải thích gốc.';
    sec.appendChild(src);

    frame.appendChild(sec);
  }

  window.KT_L2B = { find: find, badge: badge, section: section };
})();
