/* ═══════════════════════════════════════════════════════
   Hộ chiếu — bạn đang là công dân của những nước nào.

   Đọc số dư gốc trên các chuỗi EVM bằng RPC công cộng.
   Không thư viện, không backend, không API key, không gas.

   Hai thao tác duy nhất chạm tới ví:
     · eth_requestAccounts  — xin địa chỉ
     · personal_sign        — ký một câu chữ
   KHÔNG BAO GIỜ gọi eth_sendTransaction. App này không tiêu
   tiền của bạn, và không có đường nào để làm việc đó.

   File tự chèn nút của mình vào thanh bên, giống pwa.js —
   không cần móc nào trong app.js.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  /* Sáu chuỗi EVM có mặt trên bản đồ. `go` là đích nhảy tới
     khi bấm vào dòng — nối thẳng hộ chiếu với bản đồ. */
  var CHAINS = [
    { n: "Ethereum",     sym: "ETH",  go: "eth",           kind: "country",
      rpc: "https://ethereum-rpc.publicnode.com" },
    { n: "BNB Chain",    sym: "BNB",  go: "bnb",           kind: "country",
      rpc: "https://bsc-rpc.publicnode.com" },
    { n: "Avalanche",    sym: "AVAX", go: "avax",          kind: "country",
      rpc: "https://avalanche-c-chain-rpc.publicnode.com" },
    { n: "Base",         sym: "ETH",  go: "eth/base",      kind: "city",
      rpc: "https://base-rpc.publicnode.com" },
    { n: "Arbitrum One", sym: "ETH",  go: "eth/arbitrum-one", kind: "city",
      rpc: "https://arbitrum-one-rpc.publicnode.com" },
    { n: "Optimism",     sym: "ETH",  go: "eth/optimism",  kind: "city",
      rpc: "https://optimism-rpc.publicnode.com" }
  ];

  /* Sáu nước còn lại trên bản đồ không dùng địa chỉ EVM.
     Nói thẳng ra chứ không lặng lẽ bỏ qua. */
  var NON_EVM = "Solana, Sui, Near, TON, Cosmos, Polkadot";

  var LS_KEY = "kt.passport";

  function el(t, c) { var e = document.createElement(t); if (c) e.className = c; return e; }
  function isAddr(s) { return /^0x[0-9a-fA-F]{40}$/.test(String(s || "").trim()); }
  function shortAddr(a) { return a.slice(0, 6) + "…" + a.slice(-4); }

  /* wei (hex) → chuỗi thập phân, không dùng Number để khỏi mất chính xác */
  function fromWei(hex) {
    var wei = BigInt(hex || "0x0");
    var whole = wei / 1000000000000000000n;
    var frac = (wei % 1000000000000000000n).toString().padStart(18, "0").slice(0, 4);
    return whole.toString() + "." + frac;
  }

  function rpc(url, method, params) {
    return fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: method, params: params }),
      signal: AbortSignal.timeout(15000)
    }).then(function (r) { return r.json(); }).then(function (j) {
      if (j.error) throw new Error(j.error.message);
      return j.result;
    });
  }

  /* ── giao diện ────────────────────────────────────────── */
  var panel = null, scrim = null, addr = null;

  function close() {
    if (panel) panel.dataset.open = "0";
    if (scrim) scrim.dataset.open = "0";
  }

  function build() {
    scrim = el("div", "pp-scrim");
    scrim.addEventListener("click", close);
    document.body.appendChild(scrim);

    panel = el("aside", "pp");
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Hộ chiếu");
    document.body.appendChild(panel);

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && panel.dataset.open === "1") close();
    });
  }

  function open() {
    if (!panel) build();
    render();
    panel.dataset.open = "1";
    scrim.dataset.open = "1";
  }

  function render() {
    panel.innerHTML = "";

    var top = el("div", "pp-top");
    var h = el("h2"); h.textContent = "Hộ chiếu";
    top.appendChild(h);
    var x = el("button", "pp-x"); x.type = "button"; x.setAttribute("aria-label", "Đóng");
    x.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="2.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
    x.addEventListener("click", close);
    top.appendChild(x);
    panel.appendChild(top);

    var body = el("div", "pp-body");
    panel.appendChild(body);

    if (!addr) { renderConnect(body); return; }

    var who = el("div", "pp-who");
    who.innerHTML = '<span class="k">Địa chỉ</span><span class="v mono">' + shortAddr(addr) + '</span>';
    var chg = el("button", "pp-link"); chg.type = "button"; chg.textContent = "đổi";
    chg.addEventListener("click", function () { addr = null; render(); });
    who.appendChild(chg);
    body.appendChild(who);

    var list = el("div", "pp-list");
    body.appendChild(list);

    var summary = el("p", "pp-sum");
    summary.textContent = "Đang đọc số dư trên " + CHAINS.length + " chuỗi…";
    body.appendChild(summary);

    var rows = {};
    CHAINS.forEach(function (c) {
      var r = el("button", "pp-row"); r.type = "button";
      r.dataset.kind = c.kind;
      r.innerHTML = '<span class="nm">' + c.n + '</span><span class="bal">…</span>';
      r.addEventListener("click", function () { window.location.hash = c.go; close(); });
      list.appendChild(r);
      rows[c.n] = r;
    });

    var done = 0, citizen = 0;
    CHAINS.forEach(function (c) {
      rpc(c.rpc, "eth_getBalance", [addr, "latest"]).then(function (hex) {
        var v = fromWei(hex);
        rows[c.n].querySelector(".bal").textContent = v + " " + c.sym;
        if (BigInt(hex || "0x0") > 0n) { rows[c.n].dataset.has = "1"; citizen++; }
      }).catch(function () {
        rows[c.n].querySelector(".bal").textContent = "không đọc được";
        rows[c.n].dataset.err = "1";
      }).finally(function () {
        if (++done === CHAINS.length) {
          summary.textContent = citizen
            ? "Bạn đang có mặt ở " + citizen + "/" + CHAINS.length + " nơi trên bản đồ này."
            : "Địa chỉ này chưa có số dư gốc ở nơi nào trong sáu chuỗi trên.";
        }
      });
    });

    var note = el("p", "pp-note");
    note.textContent = "Chưa đọc được: " + NON_EVM + " — sáu nước này không dùng địa chỉ EVM, " +
      "cần ví riêng của từng hệ.";
    body.appendChild(note);

    renderSign(body);
  }

  function renderConnect(body) {
    var p = el("p", "pp-lead");
    p.textContent = "Xem bạn đang là công dân của những nước nào trên bản đồ. " +
      "Chỉ đọc số dư, không ký gì và không tiêu gì.";
    body.appendChild(p);

    if (window.ethereum) {
      var b = el("button", "pp-btn"); b.type = "button";
      b.textContent = "Kết nối ví";
      b.addEventListener("click", function () {
        b.disabled = true; b.textContent = "đang chờ ví…";
        window.ethereum.request({ method: "eth_requestAccounts" }).then(function (accs) {
          if (accs && accs[0]) { addr = accs[0]; render(); }
          else { b.disabled = false; b.textContent = "Kết nối ví"; }
        }).catch(function () {
          b.disabled = false; b.textContent = "Kết nối ví";
        });
      });
      body.appendChild(b);
      var or = el("div", "pp-or"); or.textContent = "hoặc";
      body.appendChild(or);
    } else {
      var nw = el("p", "pp-note");
      nw.textContent = "Không thấy ví trong trình duyệt này. Vẫn xem được bằng cách dán địa chỉ.";
      body.appendChild(nw);
    }

    var row = el("div", "pp-input");
    var i = el("input");
    i.type = "text";
    i.placeholder = "0x…";
    i.spellcheck = false;
    i.autocomplete = "off";
    var go = el("button"); go.type = "button"; go.textContent = "Xem";
    function submit() {
      var v = i.value.trim();
      if (!isAddr(v)) { i.dataset.bad = "1"; return; }
      addr = v; render();
    }
    i.addEventListener("input", function () { delete i.dataset.bad; });
    i.addEventListener("keydown", function (e) { if (e.key === "Enter") submit(); });
    go.addEventListener("click", submit);
    row.appendChild(i); row.appendChild(go);
    body.appendChild(row);
  }

  /* ── ký bản số liệu ───────────────────────────────────── */
  function renderSign(body) {
    var P = (window.KT_DATA && window.KT_DATA.PROV) || null;
    if (!P || !P.sha256) return;

    var w = el("div", "pp-sign");
    var h = el("h3"); h.textContent = "Ký bản số liệu";
    w.appendChild(h);

    var p = el("p");
    p.textContent = "Bản số liệu ngày " + P.date + " đã có CID nên không sửa được. " +
      "Ký thêm bằng ví thì nó còn chứng minh được là của bạn. Chữ ký nằm ngoài chuỗi — không tốn gas.";
    w.appendChild(p);

    var saved = null;
    try { saved = JSON.parse(localStorage.getItem(LS_KEY) || "null"); } catch (e) {}

    if (saved && saved.sha256 === P.sha256) {
      var ok = el("div", "pp-signed");
      ok.innerHTML = '<span class="k">Đã ký</span><span class="v mono">' +
        saved.sig.slice(0, 20) + '…</span>';
      var cp = el("button", "pp-link"); cp.type = "button"; cp.textContent = "chép";
      cp.addEventListener("click", function () {
        navigator.clipboard.writeText(JSON.stringify(saved, null, 2));
        cp.textContent = "đã chép";
        setTimeout(function () { cp.textContent = "chép"; }, 1500);
      });
      ok.appendChild(cp);
      w.appendChild(ok);
    } else if (window.ethereum && addr) {
      var b = el("button", "pp-btn small"); b.type = "button";
      b.textContent = "Ký bằng ví";
      b.addEventListener("click", function () {
        var msg = "Kinh Thanh — ban so lieu " + P.date + "\n" +
          "sha256: " + P.sha256 + "\n" +
          "cid: " + P.cid + "\n" +
          "Toi xac nhan da xem ban so lieu nay.";
        b.disabled = true; b.textContent = "đang chờ ví…";
        window.ethereum.request({ method: "personal_sign", params: [msg, addr] })
          .then(function (sig) {
            var rec = { addr: addr, sha256: P.sha256, cid: P.cid, date: P.date, msg: msg, sig: sig, at: new Date().toISOString() };
            try { localStorage.setItem(LS_KEY, JSON.stringify(rec)); } catch (e) {}
            render();
          })
          .catch(function () { b.disabled = false; b.textContent = "Ký bằng ví"; });
      });
      w.appendChild(b);
    } else {
      var n = el("p", "pp-note");
      n.textContent = "Cần ví trong trình duyệt để ký. Dán địa chỉ thì chỉ xem được, không ký được.";
      w.appendChild(n);
    }

    body.appendChild(w);
  }

  /* ── nút trong thanh bên ──────────────────────────────── */
  function mountButton() {
    var foot = document.querySelector(".nav-foot");
    if (!foot) return;
    var b = el("button", "passport-btn");
    b.type = "button";
    b.title = "Hộ chiếu — bạn là công dân nước nào";
    b.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" ' +
      'stroke-linecap="round" stroke-linejoin="round">' +
      '<rect x="4.5" y="2.8" width="15" height="18.4" rx="2.2"/>' +
      '<circle cx="12" cy="10" r="3.1"/><path d="M8.6 17.4h6.8"/></svg>' +
      '<span>Hộ chiếu</span>';
    b.addEventListener("click", open);
    foot.parentNode.insertBefore(b, foot);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountButton);
  } else {
    mountButton();
  }

  window.KT_PASSPORT = { open: open };
})();
