/* ═══════════════════════════════════════════════════════
   Hiển thị dấu đóng của bản số liệu.

   Dữ liệu: window.KT_DATA.PROV, sinh bởi scripts/pin-snapshot.mjs.
   Móc: một dòng có rào trong openRanking() của app.js.

   Ý nghĩa với người đọc: những con số trong bảng này không phải
   "tin thì tin" — chúng có một CID, và CID chính là hash của nội
   dung. Ba tháng nữa mở lại CID đó, nếu ra đúng bộ số này thì
   không ai sửa được lịch sử.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var P = (window.KT_DATA && window.KT_DATA.PROV) || null;
  if (!P || !P.cid) return;

  var GATEWAY = "https://ipfs.io/ipfs/";

  function el(t, c) { var e = document.createElement(t); if (c) e.className = c; return e; }
  function short(s, head, tail) {
    if (!s || s.length <= head + tail + 1) return s || "";
    return s.slice(0, head) + "…" + s.slice(-tail);
  }

  function section(host) {
    var w = el("div", "prov");

    var h = el("h3");
    h.textContent = "Bản số liệu này đóng dấu được";
    w.appendChild(h);

    var p = el("p", "prov-lead");
    p.textContent = "Bộ số ngày " + P.date + " đã được lưu lên IPFS thành một bản bất biến. " +
      "CID bên dưới chính là dấu vân tay của nội dung — đổi một chữ số là ra CID khác. " +
      "Mở lại link đó bất cứ lúc nào để đối chiếu xem hôm nay bảng này nói gì.";
    w.appendChild(p);

    var rows = el("div", "prov-rows");

    var a = el("a", "prov-row");
    a.href = GATEWAY + P.cid;
    a.target = "_blank";
    a.rel = "noopener";
    a.innerHTML = '<span class="k">CID</span><span class="v mono">' + short(P.cid, 14, 8) + '</span>' +
      '<span class="go">mở ↗</span>';
    a.title = P.cid;
    rows.appendChild(a);

    var s = el("div", "prov-row");
    s.innerHTML = '<span class="k">SHA-256</span><span class="v mono">' + short(P.sha256, 12, 8) + '</span>' +
      '<span class="go">' + (P.bytes || 0) + ' byte</span>';
    s.title = P.sha256;
    rows.appendChild(s);

    var c = el("div", "prov-row");
    c.innerHTML = '<span class="k">Đã lưu</span><span class="v">' + P.count +
      (P.count > 1 ? " bản" : " bản") + '</span><span class="go">mỗi 6 giờ một lần</span>';
    rows.appendChild(c);

    w.appendChild(rows);

    var f = el("p", "prov-foot");
    if (P.anchored) {
      f.innerHTML = "Đã neo lên Base: <code>" + short(P.anchored, 12, 8) + "</code>";
    } else {
      f.textContent = "Chưa neo lên chuỗi. Khi neo, thứ ghi lên Base chỉ là 32 byte SHA-256 ở trên — " +
        "phần nội dung vẫn nằm trên IPFS, nên chi phí gần như không đáng kể.";
    }
    w.appendChild(f);

    host.appendChild(w);
  }

  window.KT_PROV = { section: section, data: P };
})();
