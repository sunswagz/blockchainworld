/* ═══════════════════════════════════════════════════════════════
   KHÂM THIÊN GIÁM — giao diện cung tĩnh.

   Hai nguồn, cố ý tách nhau:

     window.PHONG      sổ bảy phòng, VIẾT TAY (assets/js/phong.js)
     window.DAI_CHIEM  lát cắt runtime, SINH TAY (assets/js/v/dai-chiem.js)

   Trang này KHÔNG gọi API nào. Nó không có khoá, không có server, và
   không đặt được lệnh nào — đúng như cả repo quy định: khoá không bao
   giờ ra tới trình duyệt.

   LUẬT VẼ: ô nào chưa có số thì nói là chưa có, không vẽ số 0. Cung này
   giảng về một cỗ máy mà điểm hay của nó là không tự tin quá những gì
   đo được; một giao diện vẽ số 0 cho chỗ chưa đo là phản lại chính điều
   nó đang giảng.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var PHONG = window.PHONG || [];
  var TT = window.TRI_THUC || null;
  var LC = window.DAI_CHIEM || null;

  /* Hộp NỘI DUNG, không phải `<main>`. Hai thẻ ấy từng cùng mang id
     "than", và khi đó dòng dọn nền trong tuyen() xoá cả đỉnh trang,
     ô cảnh báo và chân trang — xem chú thích dài ở index.html. */
  var noiDung = document.getElementById("noiDung");
  var tieu = document.getElementById("tieu");
  var benMuc = document.getElementById("benMuc");

  /* ── tiện ─────────────────────────────────────────────────── */
  function el(t, c, x) {
    var e = document.createElement(t);
    if (c) e.className = c;
    if (x != null) e.textContent = x;
    return e;
  }
  function html(t, c, h) {
    var e = document.createElement(t);
    if (c) e.className = c;
    if (h != null) e.innerHTML = h;
    return e;
  }
  function so(v, n) {
    return (v == null || !isFinite(v)) ? "—" : Number(v).toFixed(n == null ? 2 : n);
  }
  function cent(v, n) {
    if (v == null || !isFinite(v)) return "—";
    return (v >= 0 ? "+" : "") + (v * 100).toFixed(n == null ? 2 : n) + "¢";
  }
  function pc(v, n) {
    return (v == null || !isFinite(v)) ? "—" : (v * 100).toFixed(n == null ? 1 : n) + "%";
  }

  /* ── nhãn NGUỒN của một khối số ───────────────────────────────
     Luật 2 bắt thứ ĐO ĐƯỢC và thứ LUẬN RA đừng bao giờ trông giống
     nhau. Trong cung này chúng đang trông giống hệt: "+9,00¢ lợi thế
     thô" của máy VWAP và "1 vòng đã chạy" của lát cắt runtime cùng là
     chữ máy, cùng cỡ, cùng đậu trên một thẻ .khoi không khác một
     pixel. Cái thứ nhất là một sổ lệnh DỰNG SẴN để giảng cơ chế; cái
     thứ hai là con số một tiến trình thật đã ghi ra rồi commit. Đọc
     nhầm chiều nào cũng hỏng, và hỏng nặng ở đúng cung này: tưởng ví
     dụ là thành tích giao dịch, hoặc ngược lại tưởng số đo thật cũng
     chỉ là minh hoạ.

     Chỗ duy nhất phân biệt hai thứ ấy tới giờ là một đoạn văn dưới
     CHÂN TRANG — đúng thứ "một câu chú thích ai cũng lướt qua" mà
     chú thích luật 2 trong app.css đã nói thẳng là không đủ. Nhãn
     dưới đây đưa nó lên đỉnh từng khối, nơi con số đang nằm.

     CHỮ đứng trước, màu chỉ đi kèm — luật 3. Và cả ba màu đều là màu
     đã khai ở :root và đã dùng chỗ khác, nên sàn tương phản không
     thêm cặp nào phải đo lại. Cố ý KHÔNG dùng --len/--xuong: xanh và
     đỏ trong cung này nghĩa là lợi thế dương/âm, mượn chúng cho
     "đo được / ví dụ" là gán một lời khen vào một câu nói về nguồn.

     Ba nhãn chứ không hai, và cái thứ ba là chỗ suýt nói sai: đường
     cong phí KHÔNG phải ví dụ. Nó vẽ đúng biểu phí Polymarket đang
     áp — maker 0, taker theo giá — nên dán "SỐ VÍ DỤ" lên nó là hạ
     một luật của sàn xuống thành một con số bịa ra để giảng bài. Thà
     thêm một nhãn còn hơn xếp sai một khối. */
  var VI_DU = { chu: "SỐ VÍ DỤ", k: "tim" };
  var DO_DUOC = { chu: "SỐ ĐO", k: "tien" };
  var CONG_THUC = { chu: "CÔNG THỨC SÀN", k: "lam" };
  var CHUA_DO = { chu: "CHƯA CÓ SỐ ĐO", k: "" };

  function khoi(ten, phu, nguon) {
    var k = el("section", "khoi");
    var d = el("div", "khoi-dinh");
    d.appendChild(el("h2", null, ten));
    if (nguon) {
      var n = el("span", "the", nguon.chu);
      n.dataset.k = nguon.k;
      n.dataset.nguon = "1";
      d.appendChild(n);
    }
    if (phu) d.appendChild(el("span", "n", phu));
    k.appendChild(d);
    var t = el("div", "khoi-than");
    k.appendChild(t);
    k._than = t;
    k._dinh = d;
    return k;
  }

  /* ── vẽ một đoạn giảng ────────────────────────────────────── */
  function veDoan(d) {
    var o = el("div", "doan");
    if (d.canh) o.dataset.canh = "1";
    if (d.h) o.appendChild(el("h3", null, d.h));
    if (d.p) o.appendChild(html("p", null, d.p));

    if (d.cong) o.appendChild(el("pre", "cong", d.cong.join("\n")));

    if (d.bang) {
      var t = el("table", "kyhieu"), tb = el("tbody");
      d.bang.forEach(function (r) {
        var tr = el("tr");
        tr.appendChild(el("td", null, r[0]));
        tr.appendChild(html("td", null, r[1]));
        tb.appendChild(tr);
      });
      t.appendChild(tb);
      o.appendChild(t);
    }

    if (d.p2) o.appendChild(html("p", null, d.p2));
    if (d.cong2) o.appendChild(el("pre", "cong", d.cong2.join("\n")));

    if (d.ds) {
      var u = el("ul");
      d.ds.forEach(function (x) { u.appendChild(html("li", null, x)); });
      o.appendChild(u);
    }
    if (d.ds2) {
      var c = el("div", "chips");
      d.ds2.forEach(function (x) { c.appendChild(el("span", null, x)); });
      o.appendChild(c);
    }
    if (d.p3) o.appendChild(html("p", null, d.p3));

    if (d.nhan) {
      d.nhan.forEach(function (n) {
        var v = el("div", "nhanvi");
        v.appendChild(el("h4", null, n.t));
        var dl = el("dl");
        var dt1 = el("dt", null, "nói được"); dt1.dataset.k = "co";
        dl.appendChild(dt1); dl.appendChild(html("dd", null, n.co));
        var dt2 = el("dt", null, "không nói được"); dt2.dataset.k = "khong";
        dl.appendChild(dt2); dl.appendChild(html("dd", null, n.khong));
        v.appendChild(dl);
        o.appendChild(v);
      });
    }

    if (d.lotrinh) {
      var lt = el("table", "lotrinh"), lb = el("tbody");
      d.lotrinh.forEach(function (r, i) {
        var tr = el("tr");
        if (i === d.lotrinh.length - 1) tr.dataset.cuoi = "1";
        tr.appendChild(el("td", "p", r[0]));
        tr.appendChild(el("td", "v", r[1]));
        tr.appendChild(el("td", "c", r[2]));
        lb.appendChild(tr);
      });
      lt.appendChild(lb);
      o.appendChild(lt);
      if (d.p) { /* p đã vẽ ở trên */ }
    }
    return o;
  }

  /* ── máy tính VWAP — sổ lệnh thật của phép kiểm ───────────── */
  var SO_MAU = [
    { gia: 0.46, luong: 80 },
    { gia: 0.48, luong: 200 },
    { gia: 0.50, luong: 400 },
    { gia: 0.53, luong: 1000 }
  ];
  var FAIR = 0.55;

  function tinhVwap(q) {
    var con = q, tien = 0, khop = 0, muc = 0, cham = SO_MAU[0].gia;
    for (var i = 0; i < SO_MAU.length && con > 1e-9; i++) {
      var lay = Math.min(con, SO_MAU[i].luong);
      tien += lay * SO_MAU[i].gia;
      khop += lay; con -= lay; cham = SO_MAU[i].gia; muc++;
    }
    return { khop: khop, vwap: khop > 0 ? tien / khop : 0, muc: muc, cham: cham,
             dayDu: con <= 1e-9 };
  }

  function veMayVwap() {
    var k = khoi("Thử đi qua sổ", "kéo để đổi khối lượng", VI_DU);
    var w = el("div", "vwap-o");

    // cột trái: sổ lệnh
    var trai = el("div");
    trai.appendChild(html("div", "chips", "<span>ASK &mdash; bên bán</span>"));
    var maxL = 1000;
    var hangs = SO_MAU.slice().reverse().map(function (m) {
      var d = el("div", "so-muc");
      var t = el("div", "thanh");
      // Bề rộng nằm ở CSS (62%); ở đây chỉ đặt tỷ lệ. Xem .so-muc .thanh.
      t.style.transform = "scaleX(" + (m.luong / maxL) + ")";
      d.appendChild(t);
      d.appendChild(el("div", "g", (m.gia * 100).toFixed(0) + "¢"));
      d.appendChild(el("div", "l", m.luong.toLocaleString("vi-VN") + " cổ"));
      d._gia = m.gia;
      trai.appendChild(d);
      return d;
    });
    w.appendChild(trai);

    // cột phải: điều khiển + kết quả
    var phai = el("div");
    var dieu = el("div", "vwap-dieu");
    var lab = el("label", null, "Muốn mua: 280 cổ");
    var rng = document.createElement("input");
    rng.type = "range"; rng.min = "20"; rng.max = "1680"; rng.step = "20"; rng.value = "280";
    dieu.appendChild(lab); dieu.appendChild(rng);
    phai.appendChild(dieu);

    var oso = el("div", "vwap-so");
    var oBest = el("div"), oVwap = el("div"), oEdge = el("div"), oMuc = el("div");
    [["Best ask", oBest], ["VWAP thật", oVwap], ["Lợi thế thô", oEdge], ["Đi qua", oMuc]]
      .forEach(function (p) {
        p[1].appendChild(el("b", null, p[0]));
        /* Giữ thẳng thẻ giá trị thay vì querySelector(".v") mỗi lượt kéo
           thanh trượt — cùng kết quả, và cap() không còn phải biết tên lớp. */
        p[1]._v = el("div", "v", "—");
        p[1].appendChild(p[1]._v);
        oso.appendChild(p[1]);
      });

    /* Trạng thái lợi thế viết BẰNG CHỮ, ngay dưới con số.

       Trước bản này ba mức — dày / mỏng / âm — khác nhau ĐÚNG một sắc
       độ chữ (--len / --canh / --xuong), và con số in bằng toFixed nên
       số dương còn không mang dấu +. Ai không phân biệt được xanh với
       đỏ đọc "8.46¢" y hệt "0.42¢": cùng một chuỗi ký tự, khác nhau
       chỉ ở màu. Đó là luật 3 hỏng ngay tại ô mà cả phòng dẫn tới —
       và hỏng trong im lặng, vì trên màn hình của người viết nó vẫn
       xanh đỏ rất rõ.

       Hai dấu hiệu thêm vào, không dấu nào là màu:
         · dấu +/− của cent(), cùng lối với thác trừ ngay bên dưới;
         · một dòng chữ nói ra NGƯỠNG. 2¢ vốn chỉ nằm trong mã, nên
           người kéo thanh trượt thấy màu nhảy mà không biết nó nhảy
           ở đâu và vì sao. */
    var oTt = el("span", "tt");
    oEdge.appendChild(oTt);
    phai.appendChild(oso);
    var ghi = html("p", null, "");
    ghi.style.cssText = "margin:12px 0 0;font-size:12.6px;color:var(--fg-3);line-height:1.66";
    phai.appendChild(ghi);
    w.appendChild(phai);

    function cap() {
      var q = Number(rng.value);
      var r = tinhVwap(q);
      lab.textContent = "Muốn mua: " + q.toLocaleString("vi-VN") + " cổ";
      oBest._v.textContent = "46,0¢";
      oVwap._v.textContent = (r.vwap * 100).toFixed(2) + "¢";
      var e = FAIR - r.vwap;
      oEdge._v.textContent = cent(e);
      /* Màu nằm ở CSS theo data-muc, không rắc inline nữa: một chỗ đặt
         màu thì một chỗ đó cũng là chỗ ghi được vì sao có ba mức. */
      var muc = e > 0.02 ? "day" : (e > 0 ? "mong" : "am");
      oEdge.dataset.muc = muc;
      oTt.textContent = muc === "day" ? "dày hơn ngưỡng 2¢"
        : muc === "mong" ? "mỏng, dưới ngưỡng 2¢"
        : "âm, không đáng vào";
      oMuc._v.textContent = r.muc + " mức";
      hangs.forEach(function (h) { h.dataset.an = h._gia <= r.cham + 1e-9 ? "1" : "0"; });
      ghi.innerHTML = r.dayDu
        ? ("Mô hình định giá <b>55,0¢</b>. Phép trừ ai cũng làm là " +
           "<code>55,0 − 46,0 = 9,0¢</code>. Giá thật cho " + q.toLocaleString("vi-VN") +
           " cổ là <b>" + (r.vwap * 100).toFixed(2) + "¢</b>, nên lợi thế thô còn <b>" +
           (e * 100).toFixed(2) + "¢</b> — và đó vẫn là <i>trước</i> phí, trượt giá, " +
           "bất định mô hình và biên an toàn.")
        : ("Cả sổ chỉ có 1.680 cổ. Muốn " + q.toLocaleString("vi-VN") +
           " cổ thì <b>không đủ hàng</b> — sổ mỏng là một trạng thái có thật, " +
           "và Risk Engine cần thấy nó chứ không phải một con số làm tròn.");
    }
    rng.addEventListener("input", cap);
    cap();

    k._than.appendChild(w);
    return k;
  }

  /* ── thác trừ năm khoản ───────────────────────────────────── */
  function veThac() {
    var k = khoi("Thác trừ", "lô 680 cổ, sổ lệnh ở trên", VI_DU);
    var r = tinhVwap(680);
    var phi = 0.02 * Math.min(r.vwap, 1 - r.vwap);
    var truot = 8 / 10000;
    var bd = 0.02, at = 0.008;
    var net = (FAIR - r.vwap) - phi - truot - bd - at;

    var t = el("div", "thac");
    function hang(ten, gt, k2) {
      var h = el("div", "hang");
      if (k2) h.dataset.k = k2;
      h.appendChild(el("div", "ten", ten));
      h.appendChild(el("div", "sl", gt));
      t.appendChild(h);
    }
    hang("fair value (mô hình)", (FAIR * 100).toFixed(2) + "¢");
    hang("− VWAP thật cho 680 cổ", (r.vwap * 100).toFixed(2) + "¢", "tru");
    hang("= lợi thế thô", cent(FAIR - r.vwap));
    hang("− phí taker", (phi * 100).toFixed(2) + "¢", "tru");
    hang("− trượt giá", (truot * 100).toFixed(2) + "¢", "tru");
    hang("− bất định mô hình", (bd * 100).toFixed(2) + "¢", "tru");
    hang("− biên an toàn", (at * 100).toFixed(2) + "¢", "tru");
    hang("NET EXECUTABLE EDGE", cent(net), "tong");
    k._than.appendChild(t);
    k._than.appendChild(html("p", null,
      "<span style='font-size:12.6px;color:var(--fg-3);line-height:1.66;display:block;" +
      "margin-top:12px'>Từ <b style='color:var(--fg-2)'>9,00¢</b> trên bảng điều khiển " +
      "xuống <b style='color:var(--fg-2)'>" + (net * 100).toFixed(2) + "¢</b> ăn được. " +
      "Bỏ bất kỳ khoản trừ nào cũng ra một con số đẹp hơn và sai hơn.</span>"));
    return k;
  }

  /* ── đường cong phí ───────────────────────────────────────── */
  function veDuongPhi() {
    var k = khoi("Phí taker theo giá", "maker = 0", CONG_THUC);
    var W = 560, H = 150, P = 26;
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("width", "100%");
    svg.style.cssText = "max-width:560px;height:auto;display:block";

    function X(p) { return P + p * (W - 2 * P); }
    function Y(f) { return H - P - (f / 0.01) * (H - 2 * P); }

    var d = "";
    for (var i = 0; i <= 100; i++) {
      var p = i / 100, f = 0.02 * Math.min(p, 1 - p);
      d += (i ? "L" : "M") + X(p).toFixed(1) + " " + Y(f).toFixed(1);
    }
    var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", d);
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", "#7FB2E8");
    path.setAttribute("stroke-width", "2");
    svg.appendChild(path);

    var truc = document.createElementNS("http://www.w3.org/2000/svg", "path");
    truc.setAttribute("d", "M" + P + " " + (H - P) + "H" + (W - P));
    truc.setAttribute("stroke", "#1E2634");
    truc.setAttribute("stroke-width", "1.5");
    svg.appendChild(truc);

    [[0, "0¢"], [0.5, "50¢"], [0.987, "98,7¢"]].forEach(function (m) {
      var g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      var c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      var f = 0.02 * Math.min(m[0], 1 - m[0]);
      c.setAttribute("cx", X(m[0])); c.setAttribute("cy", Y(f));
      c.setAttribute("r", "3.5"); c.setAttribute("fill", "#E8A33D");
      g.appendChild(c);
      var tx = document.createElementNS("http://www.w3.org/2000/svg", "text");
      tx.setAttribute("x", X(m[0])); tx.setAttribute("y", Y(f) - 9);
      tx.setAttribute("fill", "#A9B6C7"); tx.setAttribute("font-size", "11");
      tx.setAttribute("text-anchor", "middle");
      tx.setAttribute("font-family", "JetBrains Mono,monospace");
      tx.textContent = m[1] + " → " + (f * 100).toFixed(2) + "¢";
      g.appendChild(tx);
      svg.appendChild(g);
    });

    k._than.appendChild(svg);
    k._than.appendChild(html("p", null,
      "<span style='font-size:12.6px;color:var(--fg-3);line-height:1.66;display:block;" +
      "margin-top:10px'>Phí cao nhất ở giữa bảng giá, về gần 0 ở hai đầu. Điều đó có " +
      "hệ quả rất thực tế: ngón <b style='color:var(--fg-2)'>cận kết quả</b> mua ở " +
      "98,7¢ gần như không mất phí — nhưng đó cũng đúng chỗ rủi ro đuôi lớn nhất. " +
      "Rẻ về phí không có nghĩa là rẻ về rủi ro.</span>"));
    return k;
  }

  /* ── đường tiến hoá ───────────────────────────────────────── */
  function veDuongTienHoa() {
    var th = (LC && LC.tienHoa) || null;
    /* Nhãn phải hỏi ĐÚNG câu mà nhánh trống ở dưới hỏi, không thì có
       ngày khối in "SỐ ĐO" ở đỉnh rồi ngay dưới nói "chưa chạy lượt
       nào" — hai câu ngược nhau trên cùng một thẻ. */
    var coLuot = !!(th && th.duong && th.duong.soLuot);
    var k = khoi("Đường tiến hoá", th && th.bat ? ("mỗi ngày, sau " +
      String(th.gioUTC).padStart(2, "0") + ":00 UTC") : "đang tắt",
      coLuot ? DO_DUOC : CHUA_DO);

    if (!coLuot) {
      k._than.appendChild(html("div", "latcat-trong",
        "<b>Chưa chạy lượt tiến hoá nào.</b><br>Vòng chạy mỗi ngày một lượt " +
        "trong runtime ở máy. Chưa có lượt nào thì ô này để trống — " +
        "<b>không vẽ số 0</b>, vì 0 là một con số còn “chưa đo” thì không."));
      return k;
    }

    var d = th.duong;
    var l = el("div", "luoi-so");
    function oso(nhan, to, duoi, lop) {
      var o = el("div", "o-so");
      o.appendChild(el("div", "nhan", nhan));
      o.appendChild(el("div", "to " + (lop || ""), to));
      if (duoi) o.appendChild(el("div", "duoi", duoi));
      l.appendChild(o);
    }
    oso("Đã chạy", String(d.soLuot) + " lượt");
    oso("Nhận", String(d.soLanNhan), "tham số đổi thật",
      d.soLanNhan > 0 ? "len" : "");
    oso("Trả lại", String(d.soLanTraLai), "cổng làm đúng việc");
    oso("Đứng yên", String(d.soLanDungYen), "không bệnh nào vượt ngưỡng");
    oso("Tổng cải thiện",
      d.tongCaiThien == null ? "chưa đo" : cent(d.tongCaiThien, 4),
      "kỳ vọng mỗi lệnh",
      d.tongCaiThien == null ? "mo" : (d.tongCaiThien > 0 ? "len" : "xuong"));
    k._than.appendChild(l);

    if (d.chuoi && d.chuoi.length) {
      var t = el("table", "lotrinh"), tb = el("tbody");
      d.chuoi.slice(-8).forEach(function (x) {
        var tr = el("tr");
        tr.appendChild(el("td", "p", (x.luc || "").slice(5, 10)));
        tr.appendChild(el("td", "v",
          so(x.truoc, 5) + "  →  " + so(x.sau, 5)));
        var hieu = (x.sau || 0) - (x.truoc || 0);
        var td = el("td", "c", (hieu >= 0 ? "+" : "") + so(hieu, 5));
        td.style.color = hieu > 0 ? "var(--len)" : "var(--xuong)";
        tr.appendChild(td);
        tb.appendChild(tr);
      });
      t.appendChild(tb);
      k._than.appendChild(el("div", "ghi", "Kỳ vọng mỗi lệnh, trước → sau:"));
      k._than.appendChild(t);
    }

    var gn = th.ganNhat;
    if (gn) {
      k._than.appendChild(html("p", null,
        "<span style='font-size:12.6px;color:var(--fg-3);line-height:1.66;" +
        "display:block;margin-top:12px'><b>Lượt gần nhất:</b> " +
        (gn.ghiChu || "") + "</span>"));
    }
    return k;
  }

  /* TUỔI của lát cắt — thứ trang này chưa bao giờ nói ra.

     Lát cắt mang sẵn `generatedAt` (ISO, có giờ phút giây) từ ngày đầu,
     và trang chỉ hiện `date` — mỗi ngày. Nên một lát cắt ghi bảy tiếng
     trước và một lát cắt ghi ba mươi giây trước đọc ra y hệt nhau, còn
     một lát cắt cũ SÁU NGÀY thì bắt người đọc tự lấy hôm nay trừ đi.

     Đây là cùng một cái bệnh với `dichvu/trang-thai.ps1` bên runtime:
     in mười dòng nhật ký cũ hai mươi giờ như thể tin mới. Ở đây nó nặng
     hơn một bậc vì đây là mặt CÔNG KHAI — người đọc không có cách nào
     kiểm chứng, họ chỉ có những gì trang nói.

     Chữ đứng trước, màu đi kèm — luật 3. Và ngưỡng đặt ở 24 giờ chứ
     không phải 1 giờ: runtime chạy ở máy riêng và lát cắt phải COMMIT
     tay mới lên site, nên vài giờ là bình thường, không phải sự cố. Một
     cảnh báo nhảy lúc mọi thứ đang đúng thì lần nó đúng cũng không ai
     nhìn — luật đã ghi ở `BaoCaoDoc` bên runtime. */
  function tuoiLatCat() {
    if (!LC || !LC.generatedAt) return null;
    var t = Date.parse(LC.generatedAt);
    if (!isFinite(t)) return null;
    var gio = (Date.now() - t) / 3600000;
    if (gio < 0) return null;          // đồng hồ máy đọc lệch, đừng đoán
    var chu;
    if (gio < 1) chu = Math.max(1, Math.round(gio * 60)) + " phút trước";
    else if (gio < 48) chu = Math.round(gio) + " giờ trước";
    else chu = Math.round(gio / 24) + " ngày trước";
    return { gio: gio, chu: chu, cu: gio >= 24 };
  }

  /* ── lát cắt runtime ──────────────────────────────────────── */
  function veLatCat() {
    /* Không có lát cắt thì bỏ luôn phụ đề "chưa có": nhãn CHƯA CÓ SỐ ĐO
       đã nói đúng câu đó ở chỗ dễ thấy hơn, và nói hai lần cạnh nhau
       làm người đọc đi tìm khác biệt giữa hai câu vốn không khác gì. */
    var tuoi = tuoiLatCat();
    var phu = null;
    if (LC) {
      phu = "ghi " + (LC.date || "—");
      if (tuoi) phu += " · " + tuoi.chu + (tuoi.cu ? " — ĐÃ CŨ" : "");
    }
    var k = khoi("Lát cắt runtime", phu, LC ? DO_DUOC : CHUA_DO);
    if (!LC) {
      k._than.appendChild(html("div", "latcat-trong",
        "<b>Chưa có lát cắt nào.</b><br>Runtime Python chạy ở máy riêng, ghi trạng " +
        "thái ra file rồi commit. GitHub Actions không chạy được nó — cần một tiến " +
        "trình dài và có thể cần khoá ví.<br><br>" +
        "Sinh bằng tay:<br><code class='ma'>python -m kham.snapshot</code>"));
      return k;
    }

    var l = el("div", "luoi-so");
    /* Tham số `lop` — cùng hợp đồng với oso() ở veDuongTienHoa, cố ý
       giống hệt: hai lưới số của cung này phải nói "chưa có" theo cùng
       một lối, không thì người đọc phải học quy ước ấy hai lần. */
    function oso(nhan, to, duoi, lop) {
      var o = el("div", "o-so");
      o.appendChild(el("div", "nhan", nhan));
      o.appendChild(el("div", "to " + (lop || ""), to));
      if (duoi) o.appendChild(el("div", "duoi", duoi));
      l.appendChild(o);
    }
    /* Luật 1: chưa có số thì nói là chưa có. `x || 0` vẽ số 0 cho một ô
       chưa hề đo — đúng thứ luật 1 cấm, và nó hỏng trong im lặng: "chạy
       được 0 vòng" với "lát cắt không mang theo số vòng nào" là hai
       chuyện khác hẳn, mà cả hai đều in ra cùng một chữ "0". Trả null
       cho chỗ chưa có rồi để người gọi chọn chữ; số 0 đo được thật thì
       vẫn ra "0", vì 0 khác null. */
    function demSo(v) {
      return (v == null || !isFinite(v)) ? null : Number(v).toLocaleString("vi-VN");
    }
    var tk = LC.thongKe || {}, r = LC.risk || {}, hc = LC.hieuChinh || {};
    oso("Chế độ", LC.che === "that" ? "TIỀN THẬT" : (LC.che === "giay" ? "Sổ giấy" : "Quan sát"),
      "khai: " + (LC.cheKhai || "—"));
    var vong = demSo(LC.vong);
    oso("Vòng đã chạy", vong == null ? "chưa có" : vong,
      LC.chayDuocGiay ? Math.round(LC.chayDuocGiay) + " giây" : null,
      vong == null ? "mo" : "");
    var khung = demSo((LC.bang || {}).soKhung);
    oso("Băng đã ghi", khung == null ? "chưa có" : khung + " khung", null,
      khung == null ? "mo" : "");
    var mau = demSo(hc.tongMau);
    oso("Mẫu hiệu chỉnh", mau == null ? "chưa có" : mau,
      hc.duDeDungKelly ? "Kelly mở" : "Kelly còn khoá",
      mau == null ? "mo" : "");
    oso("Market kết toán", tk.n ? tk.n.toLocaleString("vi-VN") : "chưa có",
      tk.n ? ("kỳ vọng " + so(tk.kyVong, 4) + "$/lệnh") : null,
      tk.n ? "" : "mo");
    oso("Cầu dao", r.ngatKhanCap ? "ĐANG NGẮT" : "đóng", r.lyDoNgat || null);
    k._than.appendChild(l);

    /* ── danh sách BỎ QUA ────────────────────────────────────
       Trước bản này nó là hai vạch hổ phách KHÔNG TÊN, đậu ngay dưới
       lưới sáu ô. Người đọc lần đầu hiểu thành "máy đang hỏng" — và
       hiểu ngược đúng điều cung này giảng: đó là cỗ máy TỪ CHỐI vào
       lệnh vì chưa đủ mẫu ước lượng σ, tức nó đang làm đúng việc. Một
       trạng thái lành mạnh mà trông như một lỗi thì tệ hơn không hiện
       gì, vì nó dạy sai chứ không chỉ dạy thiếu.

       Vạch GIỮ NGUYÊN màu hổ phách: theo bảng màu khai ở đầu app.css,
       hổ phách nghĩa là "đáng chú ý, chưa nguy" — đúng nghĩa cần ở đây.
       Thứ thiếu chưa bao giờ là màu, mà là cái tên. Thêm tên vào cũng
       là thêm dấu hiệu thứ hai cho cả cụm (luật 3): trước đó nghĩa của
       cụm nằm trần trong sắc hổ phách.

       Rỗng thì NÓI là rỗng — nhưng chỉ khi lát cắt CÓ mang khoá
       `boQua`. Không mang là CHƯA ĐO, và luật 1 cấm biến chưa-đo thành
       0; nên nhánh đó không vẽ gì cả, thay vì vẽ một con số 0 không ai
       đo được. Số 0 đo được thật thì vẫn in ra "0 market", vì 0 khác
       null — cùng lối demSo() đã đi ở lưới trên. */
    var bq = LC.boQua;
    if (bq && typeof bq === "object") {
      var mas = Object.keys(bq);
      var cap = el("div", "boqua-d");
      /* h3 thật, không phải một dòng chữ in đậm: khối này đã là h2
         ("Lát cắt runtime") nên đây đúng là cấp ba, và trình đọc màn
         hình nhảy được tới nó thay vì phải nghe hết lưới sáu ô. */
      cap.appendChild(el("h3", null, "Bỏ qua lượt này"));
      /* Số đếm đi CHỮ MÁY, câu giải thích đi chữ thường — luật 2, ngay
         cạnh nhau trên một dòng nên khác biệt ấy đọc ra được. */
      cap.appendChild(el("span", "dem", mas.length + " market"));
      cap.appendChild(el("span", "y", mas.length
        ? "máy từ chối vào lệnh, lý do ghi ngay dưới"
        : "đo được là không có — khác với chưa đo"));
      k._than.appendChild(cap);
      mas.forEach(function (ma) {
        k._than.appendChild(html("div", "boqua", "<b>" + ma + "</b> — " + bq[ma]));
      });
    }

    k._than.appendChild(html("p", null,
      "<span style='font-size:12.6px;color:var(--fg-3);line-height:1.66;display:block'>" +
      (LC.loiNhac || "") + "</span>"));
    return k;
  }

  /* ── vẽ một phòng ─────────────────────────────────────────── */
  /* Trả về MẢNG nút, không phải DocumentFragment. Người gọi gắn
     từng nút — cùng kết quả trên trình duyệt, một dòng ở `tuyen`.

     Lý do đổi: cổng chặn tiến hoá chạy cả cung trong một DOM giả
     dựng bằng tay, và DOM ấy không có `createDocumentFragment`.
     Dòng đầu của hàm này ném, nên CẢ TÁM phòng bị chấm là vẽ ra 0
     ký tự trong khi trình duyệt vẽ đủ. Một cung lành bị phán oan
     thì phiếu đo hết nói được điều gì, và bảy thước còn lại cũng
     mất nghĩa theo: "không rò undefined" và "ít ô trống" đều xanh
     chỉ vì chúng đang soi một trang trống.

     ĐÃ CẮN THẬT, và đây là bản vá: lượt đổi sang mảng chỉ sửa được
     một nửa hợp đồng. Hai chỗ còn gọi `appendChild` trên mảng —
     `g.appendChild(k2)` cuối hàm này, và `than.appendChild(vePhong(p))`
     ở `tuyen`. DOM giả của cổng chặn nhận bừa mọi thứ vào `children`
     nên nó chỉ chấm hụt; TRÌNH DUYỆT THẬT ném TypeError, và trang
     công khai trắng CẢ TÁM phòng suốt từ 22/08. Nên nhớ khi đổi kiểu
     trả về: `g` là mảng thì mọi lối vào là `push`, và người gọi phải
     gắn từng nút — cổng chặn KHÔNG bắt hộ lỗi này. */
  function vePhong(p) {
    var g = [];

    if (p.tom) {
      g.push(html("p", "giaithich", p.tom));
    }

    if (p.ma === "dai-chiem") g.push(veLatCat());

    (p.doan || []).forEach(function (d) {
      var k = khoi(d.h || "—");
      var o = veDoan(Object.assign({}, d, { h: null }));
      /* Khối cảnh báo: MÀU KHÔNG BAO GIỜ ĐI MỘT MÌNH.
         Dấu hiệu thứ hai vốn là "! " trước h3 (xem app.css), nhưng
         ở đây tiêu đề được nâng lên đầu khối rồi veDoan gọi với
         h:null — trong .doan không còn h3 nào để gắn, nên dấu ấy
         chưa từng hiện. Còn lại đúng một lằn màu, tức là thông tin
         nằm trần trong màu. Nhãn chữ dưới đây nằm ở chỗ chắc chắn
         có, và đọc được cả khi không phân biệt được màu. */
      if (d.canh) {
        k.dataset.canh = "1";
        var nhanCanh = el("span", "the", "CẢNH BÁO");
        nhanCanh.dataset.k = "canh";
        k._dinh.appendChild(nhanCanh);
      }
      k._than.appendChild(o);
      g.push(k);
    });

    if (p.demo === "vwap") { g.push(veMayVwap()); g.push(veThac()); }
    if (p.demo === "phi") g.push(veDuongPhi());
    if (p.demo === "tienhoa") g.push(veDuongTienHoa());

    /* Lớp tri thức nền — knowledge-os/sinh.mjs ghi ra
       assets/js/v/tri-thuc.js, mang cả dữ liệu lẫn hàm vẽ nên khuôn
       giống hệt mọi cung khác. Nó KHÔNG đụng con số nào; việc duy nhất
       là nói phòng này đang đo VIỆC KINH TẾ gì, và mỗi câu đến từ đâu.
       Phòng chưa ánh xạ thì `them` trả false và không đẩy gì vào `g`. */
    if (TT && TT.them) {
      var oTT = el("div");
      if (TT.them(oTT, p.ma)) g.push(oTT);
    }

    if (p.ngon) {
      var k2 = khoi("Sáu ngón", p.ngon.length + " chiến thuật");
      var w = el("div", "ngon");
      p.ngon.forEach(function (n, i) {
        var o = el("div", "ngon-o");
        o.appendChild(el("div", "stt", "NGÓN " + (i + 1)));
        o.appendChild(el("h3", null, n.t));
        o.appendChild(html("div", "d", n.d));
        o.appendChild(html("div", "r", n.r));
        w.appendChild(o);
      });
      k2._than.appendChild(w);
      g.push(k2);
    }
    return g;
  }

  /* ── thanh bên ────────────────────────────────────────────── */
  function veBen() {
    benMuc.appendChild(el("div", "blab", "Các phòng"));
    PHONG.forEach(function (p) {
      var a = document.createElement("a");
      a.className = "bmuc";
      a.href = "#/" + p.ma;
      a.innerHTML =
        '<span class="bic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' + p.icon +
        '</svg></span><span class="bten">' + p.ten + '</span>';
      a.dataset.ma = p.ma;
      benMuc.appendChild(a);
    });
  }

  /* ── tuyến ────────────────────────────────────────────────── */
  function tuyen() {
    var ma = (location.hash || "").replace(/^#\/?/, "") || PHONG[0].ma;
    var p = PHONG.filter(function (x) { return x.ma === ma; })[0] || PHONG[0];

    tieu.textContent = p.ten;
    document.title = "Khâm Thiên Giám · " + p.ten;
    /* Chỉ dọn hộp nội dung. Trỏ nhầm sang `<main>` là mỗi lần đổi
       phòng lại xoá luôn đỉnh trang, ô #canhBao và chân trang. */
    noiDung.textContent = "";
    /* vePhong trả về MẢNG, nên gắn TỪNG nút. `appendChild(mảng)` ném
       TypeError trên trình duyệt thật — và ném ở đây thì cả phòng
       trắng, không riêng một khối. */
    vePhong(p).forEach(function (nut) { noiDung.appendChild(nut); });

    [].forEach.call(benMuc.querySelectorAll(".bmuc"), function (a) {
      if (a.dataset.ma === p.ma) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
    document.getElementById("ben").dataset.mo = "0";
    window.scrollTo(0, 0);
  }

  /* ── khởi ─────────────────────────────────────────────────── */
  veBen();
  window.addEventListener("hashchange", tuyen);
  tuyen();

  var ngay = document.getElementById("ngay");
  if (LC && LC.date) {
    var _t = tuoiLatCat();
    ngay.textContent = "lát cắt " + LC.date + (_t ? " · " + _t.chu : "");
    if (_t && _t.cu) ngay.dataset.cu = "1";
  } else ngay.textContent = "chưa có lát cắt";

  /* ── MÁY CÓ ĐANG NHÌN THẤY GÌ KHÔNG ──────────────────────────
     Ô `#canhBao` có sẵn trong HTML và CSS từ đầu nhưng **chưa hề có
     dòng JS nào đổ chữ vào** — một chỗ báo động chưa bao giờ báo.

     Nó cần thiết vì lát cắt có thể vừa TƯƠI vừa MÙ cùng lúc: ngày
     28/08/2026 đường mạng ở máy này chặn `*.polymarket.com` ở tầng TLS,
     nên runtime không đọc nổi một market nào, và lát cắt ghi ra đúng
     "0/0 cơ hội qua sàng". Không có dòng dưới đây thì trang công khai
     đọc y hệt một phiên chợ vắng — trong khi sự thật là cỗ máy đang bịt
     mắt. Hai chuyện ấy phải KHÁC NHAU trên màn hình.

     Đọc từ `LC.nguon` chứ không tự đoán: runtime đã đếm sẵn `soLoi` và
     `tongLuot` cho từng nguồn. `tongLuot === 0` mà `soLoi > 0` nghĩa là
     CHƯA LẦN NÀO đọc được — nặng hơn hẳn "có đọc được nhưng đang lỗi". */
  (function veCanhNguon() {
    var o = document.getElementById("canhBao");
    if (!o || !LC || !LC.nguon) return;
    var chuaBaoGio = [], dangLoi = [];
    Object.keys(LC.nguon).forEach(function (k) {
      var n = LC.nguon[k] || {};
      if (!n.soLoi) return;
      (n.tongLuot ? dangLoi : chuaBaoGio).push(k);
    });
    if (!chuaBaoGio.length && !dangLoi.length) return;
    var c = [];
    if (chuaBaoGio.length)
      c.push("KHÔNG với tới được " + chuaBaoGio.join(", ")
             + " — chưa lần nào đọc được trong lượt ghi lát cắt này.");
    if (dangLoi.length)
      c.push("Đang lỗi: " + dangLoi.join(", ") + ".");
    c.push("Nên mọi con số «0» ở dưới KHÔNG có nghĩa là thị "
           + "trường vắng; nó có nghĩa là máy không nhìn thấy gì.");
    var n0 = LC.nguon[(chuaBaoGio[0] || dangLoi[0])] || {};
    if (n0.loiCuoi) c.push("Lỗi cuối: " + n0.loiCuoi);
    o.textContent = "MÁY ĐANG MÙ · " + c.join(" ");
    o.hidden = false;
  })();

  var che = document.getElementById("cheDo");
  if (LC && LC.che) {
    che.hidden = false;
    che.dataset.c = LC.che;
    che.textContent = LC.che === "that" ? "tiền thật" :
      (LC.che === "giay" ? "sổ giấy" : "quan sát");
  }

  document.getElementById("benMoNut").addEventListener("click", function () {
    var b = document.getElementById("ben");
    b.dataset.mo = b.dataset.mo === "1" ? "0" : "1";
  });

  // ngăn hồ sơ chưa dùng ở bản này, nhưng khung đã sẵn cho lần sau
  var scrim = document.getElementById("scrim");
  var hoso = document.getElementById("hoso");
  function dongHoSo() {
    scrim.dataset.open = "0";
    hoso.dataset.open = "0";
    hoso.setAttribute("aria-hidden", "true");
  }
  scrim.addEventListener("click", dongHoSo);
  document.getElementById("hosoDong").addEventListener("click", dongHoSo);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") dongHoSo();
  });
})();
