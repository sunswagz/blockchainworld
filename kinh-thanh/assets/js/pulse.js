/* ═══════════════════════════════════════════════════════
   Nhịp tim realtime — số khối nhảy trực tiếp cho nước đang xem.

   Dùng eth_subscribe("newHeads") qua WebSocket RPC công cộng.
   Không khoá, không thư viện, không backend.

   Ba nguyên tắc để không ngốn pin điện thoại:
     · chỉ mở MỘT kết nối, cho đúng nước đang xem
     · tab ẩn đi thì ngắt; quay lại thì nối tiếp
     · mạng hỏng thì thử lại giãn dần, tối đa 30 giây

   Chỉ ba nước EVM có nhịp: Ethereum, BNB Chain, Avalanche.
   Sáu nước còn lại dùng giao thức khác — nói thẳng ra chứ không
   để ô trống khó hiểu.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var WSS = {
    eth:  { url: "wss://ethereum-rpc.publicnode.com",          nhip: "~12 giây một khối" },
    bnb:  { url: "wss://bsc-rpc.publicnode.com",               nhip: "~0,75 giây một khối" },
    avax: { url: "wss://avalanche-c-chain-rpc.publicnode.com", nhip: "~2 giây một khối" }
  };

  var NO_PULSE = {
    sol: "Solana", sui: "Sui", near: "Near",
    ton: "TON", atom: "Cosmos", dot: "Polkadot"
  };

  var ws = null, chain = null, retry = 0, timer = null, blocks = 0, since = 0;

  function el(t, c) { var e = document.createElement(t); if (c) e.className = c; return e; }

  function strip() {
    var hero = document.querySelector(".hero");
    if (!hero) return null;
    var s = hero.querySelector(".pulse");
    if (!s) {
      s = el("div", "pulse");
      s.innerHTML =
        '<span class="dot"></span>' +
        '<span class="lab">nhịp tim</span>' +
        '<span class="num">—</span>' +
        '<span class="meta"></span>';
      hero.appendChild(s);
    }
    return s;
  }

  function set(state, num, meta) {
    var s = strip();
    if (!s) return;
    s.dataset.state = state;
    if (num != null) s.querySelector(".num").textContent = num;
    s.querySelector(".meta").textContent = meta || "";
  }

  function stop() {
    if (timer) { clearTimeout(timer); timer = null; }
    if (ws) {
      try { ws.onclose = null; ws.close(); } catch (e) {}
      ws = null;
    }
  }

  function connect(id) {
    stop();
    var cfg = WSS[id];
    if (!cfg) return;
    blocks = 0;
    since = Date.now();
    set("wait", "—", "đang nối…");

    try { ws = new WebSocket(cfg.url); } catch (e) { return schedule(id); }

    ws.onopen = function () {
      retry = 0;
      ws.send(JSON.stringify({ jsonrpc: "2.0", id: 1, method: "eth_subscribe", params: ["newHeads"] }));
    };

    ws.onmessage = function (e) {
      var m;
      try { m = JSON.parse(e.data); } catch (err) { return; }
      if (m.method !== "eth_subscription" || !m.params || !m.params.result) return;
      var n = parseInt(m.params.result.number, 16);
      if (!isFinite(n)) return;
      blocks++;
      set("live", n.toLocaleString("vi-VN"), cfg.nhip);
      var s = strip();
      if (s) {
        // nháy một cái mỗi khối mới
        s.classList.remove("beat");
        void s.offsetWidth;
        s.classList.add("beat");
      }
    };

    ws.onclose = function () { schedule(id); };
    ws.onerror = function () { try { ws.close(); } catch (e) {} };
  }

  function schedule(id) {
    if (document.hidden) return;
    retry++;
    var wait = Math.min(1000 * Math.pow(2, retry - 1), 30000);
    set("wait", null, "mất kết nối — thử lại sau " + Math.round(wait / 1000) + "s");
    timer = setTimeout(function () { connect(id); }, wait);
  }

  /* ── theo dõi nước đang xem ─────────────────────────── */
  function currentId() {
    var raw = (location.hash || "").slice(1).split("/")[0];
    return raw || "eth";
  }

  function sync() {
    var id = currentId();
    if (id === chain) return;
    chain = id;
    retry = 0;

    if (WSS[id]) { connect(id); return; }

    stop();
    var s = strip();
    if (!s) return;
    if (NO_PULSE[id]) {
      set("off", "—", NO_PULSE[id] + " dùng giao thức riêng, chưa nối nhịp");
    } else {
      s.remove();
    }
  }

  window.addEventListener("hashchange", sync);

  /* tab ẩn thì ngắt cho đỡ tốn pin, hiện lại thì nối tiếp */
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) { stop(); set("wait", null, "tạm dừng"); }
    else if (WSS[chain]) { retry = 0; connect(chain); }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", sync);
  } else {
    sync();
  }
})();
