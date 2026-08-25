/* ═══════════════════════════════════════════════════════
   HOÀNG THÀNH — giao diện.

   Không khung, không gói phụ thuộc. Định tuyến bằng hash:

     #/rung              lưới 15 nền
     #/nen/<ma>          roadmap một nền: nguyên → pha → chương
     #/nen/<ma>/<số>     mở thẳng một chương
     #/dong-chay         mô-típ lặp lại xuyên 15 nền
     #/bai-hoc           bài học đúc kết theo từng nguyên
     #/xu-huong          truyền thống nhường chỗ cho sự kiện

   ── BA TẦNG DỮ LIỆU, NẠP KHÁC LÚC ─────────────────────
   data.js      nạp sẵn      ~270 KB  mục lục, nguyên/pha, tiến độ
   v/_tim.js    khi gõ tìm   ~280 KB  số + tiêu đề mọi chương
   v/<ma>.js    khi mở nền   0,6–1,5 MB toàn văn của MỘT nền

   Tổng toàn văn là ~15 MB. Nạp sẵn hết thì mở app lần đầu phải
   tải 15 MB chỉ để đọc một chương, nên chia ra như trên. Mở nền
   nào thì nặng đúng nền đó, và service worker giữ lại cho lần sau.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var R = window.RUNG;
  var G = (window.RUNG_GIAI || { NHAN: {}, GIAI: {}, TU: {} });
  var NHAN = G.NHAN, GIAI = G.GIAI;

  var than = document.getElementById("than");
  var tieu = document.getElementById("tieu");
  var oTim = document.getElementById("q");
  var canhBao = document.getElementById("canhBao");

  if (!R || !R.vh) {
    canhBao.hidden = false;
    canhBao.textContent = "Chưa có dữ liệu. Chạy `npm run hoangthanh` ở máy có thư mục nguồn.";
    return;
  }

  var vhTheoMa = {};
  R.vh.forEach(function (v) { vhTheoMa[v.ma] = v; });

  /* ── tiện dựng DOM ──────────────────────────────────── */
  function el(tag, lop, chu) {
    var e = document.createElement(tag);
    if (lop) e.className = lop;
    if (chu != null) e.textContent = chu;
    return e;
  }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function so3(n) { return String(n).padStart(3, "0"); }
  function pct(a, b) { return b ? Math.round((a / b) * 100) : 0; }

  function khongDau(s) {
    return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "")
      .replace(/đ/g, "d").replace(/Đ/g, "D").toLowerCase();
  }

  /* ── nạp file theo yêu cầu ──────────────────────────── */
  var kho = {};      // ma → { chuong: [...], theoId: {} }
  var dangNap = {};  // ma → [callback]

  window.RUNG_NAP = function (goi) {
    var theoId = {};
    goi.chuong.forEach(function (c) { theoId[c.id] = c; });
    kho[goi.ma] = { chuong: goi.chuong, theoId: theoId };
    (dangNap[goi.ma] || []).forEach(function (f) { f(kho[goi.ma]); });
    delete dangNap[goi.ma];
  };

  function napNen(ma, xong) {
    if (kho[ma]) return xong(kho[ma]);
    if (dangNap[ma]) return dangNap[ma].push(xong);
    dangNap[ma] = [xong];
    var s = document.createElement("script");
    s.src = "assets/js/v/" + ma + ".js";
    s.onerror = function () {
      (dangNap[ma] || []).forEach(function (f) { f(null); });
      delete dangNap[ma];
    };
    document.head.appendChild(s);
  }

  var timKho = null, timDang = null;
  window.RUNG_TIM_NAP = function (d) {
    timKho = d;
    (timDang || []).forEach(function (f) { f(d); });
    timDang = null;
  };
  function napTim(xong) {
    if (timKho) return xong(timKho);
    if (timDang) return timDang.push(xong);
    timDang = [xong];
    var s = document.createElement("script");
    s.src = "assets/js/v/_tim.js";
    s.onerror = function () { (timDang || []).forEach(function (f) { f(null); }); timDang = null; };
    document.head.appendChild(s);
  }

  /* ═══════════════════════════════════════════════════════
     Dựng markdown → HTML.

     Chỉ đủ những gì các chương thật sự dùng: tiêu đề, đoạn,
     danh sách, bảng, trích dẫn, đậm/nghiêng/mã, đường kẻ, và
     nhãn [FACT] [TRADITION] … được tô riêng để quét mắt.

     Escape TRƯỚC, định dạng SAU — và mã nội dòng được rút ra
     giữ chỗ trước khi chạy đậm/nghiêng, nếu không thì dấu * và
     _ nằm trong mã bị hiểu nhầm thành định dạng.
     ═══════════════════════════════════════════════════════ */

  var TEN_NHAN = Object.keys(NHAN);

  function noiDong(s) {
    var ma = [];
    // rút mã nội dòng ra trước
    s = s.replace(/`([^`]+)`/g, function (_, m) {
      ma.push(m); return "\u0000" + (ma.length - 1) + "\u0000";
    });

    s = esc(s);

    // nhãn độ chắc chắn — dài trước ngắn, để "PRIMARY SOURCE"
    // không bị "SOURCE" cắt trước
    TEN_NHAN.slice().sort(function (a, b) { return b.length - a.length; })
      .forEach(function (t) {
        var re = new RegExp("\\[" + t.replace(/ /g, "\\s+") + "\\]", "g");
        s = s.replace(re, '<span class="nh ' + NHAN[t].lop + '" title="' +
          esc(NHAN[t].ten + " — " + NHAN[t].giai) + '">' + esc(NHAN[t].ten) + "</span>");
      });

    s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>");
    s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>');

    s = s.replace(/\u0000(\d+)\u0000/g, function (_, i) {
      return "<code>" + esc(ma[Number(i)]) + "</code>";
    });
    return s;
  }

  function dungMd(md) {
    var dong = md.replace(/\r\n/g, "\n").split("\n");
    var ra = [], i = 0;

    function bang(bd) {
      // cần dòng phân cách kiểu |---|---|
      if (bd + 1 >= dong.length || !/^\s*\|?[\s:-]*-[\s|:-]*$/.test(dong[bd + 1])) return null;
      var o = ["<div class=\"md-bang\"><table>"], j = bd;
      function o1(l) {
        return l.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(function (x) { return x.trim(); });
      }
      o.push("<thead><tr>" + o1(dong[j]).map(function (c) {
        return "<th>" + noiDong(c) + "</th>";
      }).join("") + "</tr></thead><tbody>");
      j += 2;
      for (; j < dong.length && /\|/.test(dong[j]) && dong[j].trim(); j++) {
        o.push("<tr>" + o1(dong[j]).map(function (c) {
          return "<td>" + noiDong(c) + "</td>";
        }).join("") + "</tr>");
      }
      o.push("</tbody></table></div>");
      return { html: o.join(""), den: j };
    }

    while (i < dong.length) {
      var l = dong[i];

      if (!l.trim()) { i++; continue; }

      var h = /^(#{1,6})\s+(.*)$/.exec(l);
      if (h) {
        var n = Math.min(h[1].length, 3);
        ra.push("<h" + n + ">" + noiDong(h[2]) + "</h" + n + ">");
        i++; continue;
      }

      if (/^\s*([-*_])\s*\1\s*\1[\s\-*_]*$/.test(l)) { ra.push("<hr>"); i++; continue; }

      if (/\|/.test(l) && l.trim().indexOf("|") !== -1) {
        var b = bang(i);
        if (b) { ra.push(b.html); i = b.den; continue; }
      }

      if (/^\s*>/.test(l)) {
        var q = [];
        for (; i < dong.length && /^\s*>/.test(dong[i]); i++) q.push(dong[i].replace(/^\s*>\s?/, ""));
        ra.push("<blockquote>" + dungMd(q.join("\n")) + "</blockquote>");
        continue;
      }

      var ds = /^\s*([-*+]|\d+[.)])\s+/.exec(l);
      if (ds) {
        var soThuTu = /\d/.test(ds[1]);
        var muc = [];
        while (i < dong.length) {
          var m2 = /^\s*(?:[-*+]|\d+[.)])\s+(.*)$/.exec(dong[i]);
          if (!m2) break;
          var noi = [m2[1]];
          i++;
          // dòng tiếp nối thụt vào
          while (i < dong.length && /^\s{2,}\S/.test(dong[i]) &&
                 !/^\s*(?:[-*+]|\d+[.)])\s+/.test(dong[i])) {
            noi.push(dong[i].trim()); i++;
          }
          muc.push("<li>" + noiDong(noi.join(" ")) + "</li>");
        }
        var t = soThuTu ? "ol" : "ul";
        ra.push("<" + t + ">" + muc.join("") + "</" + t + ">");
        continue;
      }

      // đoạn văn
      var doan = [];
      while (i < dong.length && dong[i].trim() &&
             !/^(#{1,6})\s/.test(dong[i]) && !/^\s*>/.test(dong[i]) &&
             !/^\s*(?:[-*+]|\d+[.)])\s+/.test(dong[i]) &&
             !/^\s*([-*_])\s*\1\s*\1[\s\-*_]*$/.test(dong[i])) {
        doan.push(dong[i]); i++;
      }
      if (doan.length) ra.push("<p>" + noiDong(doan.join(" ")) + "</p>");
    }
    return ra.join("");
  }

  /* ═══════════════ thanh bên ═══════════════ */

  var MUC = [
    { hash: "#/rung", ten: "Rừng văn hoá",
      icon: '<path d="M12 2 5 12h4l-4 8h14l-4-8h4z"/>' },
    { hash: "#/dong-chay", ten: "Dòng chảy",
      icon: '<path d="M3 7c3-3 6 3 9 0s6-3 9 0"/><path d="M3 13c3-3 6 3 9 0s6-3 9 0"/><path d="M3 19c3-3 6 3 9 0s6-3 9 0"/>' },
    { hash: "#/bai-hoc", ten: "Bài học đúc kết",
      icon: '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H19v16H5.5A1.5 1.5 0 0 1 4 18.5z"/><path d="M9 8h6M9 12h6"/>' },
    { hash: "#/xu-huong", ten: "Thần thoại → lịch sử",
      icon: '<path d="M3 20h18"/><path d="m4 16 5-5 4 3 6-7"/>' }
  ];

  function svg(p, sw) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="' +
      (sw || 1.7) + '" stroke-linecap="round" stroke-linejoin="round">' + p + "</svg>";
  }

  function dungBen() {
    var host = document.getElementById("benMuc");
    host.innerHTML = "";

    var l1 = el("div", "blab", "Trong cung");
    host.appendChild(l1);
    MUC.forEach(function (m) {
      var a = el("a", "bmuc");
      a.href = m.hash;
      a.dataset.hash = m.hash;
      a.innerHTML = '<span class="bic">' + svg(m.icon) + '</span><span class="bten">' +
        esc(m.ten) + "</span>";
      host.appendChild(a);
    });

    var l2 = el("div", "blab", "Mười lăm nền");
    host.appendChild(l2);
    R.vh.forEach(function (v) {
      var a = el("a", "bmuc");
      a.href = "#/nen/" + v.ma;
      a.dataset.hash = "#/nen/" + v.ma;
      a.style.setProperty("--m", v.mau);
      a.title = v.ten + " — " + v.xong + "/" + v.keHoach + " chương";
      a.innerHTML = '<span class="bcham"></span><span class="bten">' + esc(v.ten) +
        '</span><span class="bn">' + v.xong + "</span>";
      host.appendChild(a);
    });
  }

  function sangMuc(hash) {
    document.querySelectorAll("#benMuc .bmuc").forEach(function (a) {
      var h = a.dataset.hash;
      if (h === hash || (h.indexOf("#/nen/") === 0 && hash.indexOf(h) === 0)) {
        a.setAttribute("aria-current", "page");
      } else {
        a.removeAttribute("aria-current");
      }
    });
  }

  /* ═══════════════ trang: rừng 15 nền ═══════════════ */

  function trangRung() {
    tieu.textContent = "Rừng văn hoá";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML = GIAI.rung;
    than.appendChild(gt);

    var t = R.tong;
    var tom = el("div", "tomtat");
    [
      [t.vanHoa, "nền văn hoá", "Mỗi nền một roadmap độc lập."],
      [t.xong.toLocaleString("vi-VN"), "chương đã viết",
        "Trên " + t.keHoach.toLocaleString("vi-VN") + " chương trong kế hoạch — " +
        pct(t.xong, t.keHoach) + "%."],
      [t.nguyen, "nguyên", t.pha + " pha. Nguyên là thời đại, pha là chặng trong thời đại."],
      [(t.kb / 1024).toFixed(1) + " MB", "toàn văn",
        "Nạp theo từng nền, không nạp sẵn cả rừng."]
    ].forEach(function (o) {
      var d = el("div", "tt-o");
      d.innerHTML = "<span>" + esc(o[1]) + "</span><b>" + esc(o[0]) + "</b><i>" + esc(o[2]) + "</i>";
      tom.appendChild(d);
    });
    than.appendChild(tom);

    var luoi = el("div", "rung");
    R.vh.forEach(function (v) {
      var a = el("a", "nen");
      a.href = "#/nen/" + v.ma;
      a.style.setProperty("--m", v.mau);
      var p = pct(v.xong, v.keHoach);
      var the = "";
      if (v.xong === 0) the = '<span class="the the-thieu">chưa tinh luyện chương nào</span>';
      else if (v.xong < v.keHoach) the = '<span class="the the-thieu">còn ' + (v.keHoach - v.xong) + " chương</span>";
      else the = '<span class="the the-xong">đủ kế hoạch</span>';
      if (v.scout) the += '<span class="the">' + v.scout + " báo cáo Scout</span>";
      if (v.ngoai) the += '<span class="the the-vang">+' + v.ngoai + " ngoài roadmap</span>";

      a.innerHTML =
        '<div class="nen-dinh">' +
          '<div class="nen-ten"><h3>' + esc(v.ten) + "</h3><em>" + esc(v.phu) + "</em></div>" +
          '<div class="nen-chu">' + esc(v.chu || "") + "</div>" +
        "</div>" +
        '<div class="nen-than">' +
          '<div class="nen-so"><b>' + v.xong + '</b><span>/ ' + v.keHoach + " chương</span>" +
            '<span class="pt">' + p + "%</span></div>" +
          '<div class="thanh"><i style="width:' + p + '%"></i></div>' +
          '<div class="nen-chan">' + the + "</div>" +
        "</div>";
      luoi.appendChild(a);
    });
    than.appendChild(luoi);
  }

  /* ═══════════════ trang: roadmap một nền ═══════════════ */

  function trangNen(ma, moId) {
    var v = vhTheoMa[ma];
    if (!v) return trangRung();

    tieu.textContent = v.ten;
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML = GIAI.nen +
      ' <span class="vn"><b>' + esc(v.ten) + "</b> — " + esc(v.phu) + ". " +
      v.xong + "/" + v.keHoach + " chương (" + pct(v.xong, v.keHoach) + "%), " +
      v.nguyen.length + " nguyên." +
      (v.xong < v.keHoach
        ? " Phần chưa viết nằm ở các nguyên cuối — xem ô mờ bên dưới."
        : "") +
      "</span>";
    than.appendChild(gt);

    var boc = el("div");
    than.appendChild(boc);

    v.nguyen.forEach(function (ng) {
      var kh = el("section", "nguyen");
      var dinh = el("div", "ng-dinh");
      dinh.innerHTML =
        '<div class="ng-so">' + esc(ng.laMa) + "</div>" +
        '<div class="ng-tin"><h2>' + esc(ng.ten || "—") + "</h2>" +
          (ng.thoi ? "<em>" + esc(ng.thoi) + "</em>" : "") + "</div>" +
        (ng.chu ? '<div class="ng-chu">' + esc(ng.chu) + "</div>" : "") +
        '<div class="ng-tien"><b>' + ng.xong + "/" + ng.n + "</b><span>chương</span></div>";
      kh.appendChild(dinh);

      ng.pha.forEach(function (p, iPha) {
        if (p.ten) kh.appendChild(el("div", "pha-nhan", p.ten));
        var luoi = el("div", "luoi-ch");
        luoi.dataset.ng = ng.laMa;
        luoi.dataset.ph = String(iPha);
        kh.appendChild(luoi);
      });

      boc.appendChild(kh);
    });

    // chương nằm trong file nặng — nạp rồi mới đổ vào lưới
    var dangEl = el("div", "dang", "Đang nạp " + v.kb + " KB nội dung của " + v.ten + "…");
    boc.appendChild(dangEl);

    napNen(ma, function (d) {
      dangEl.remove();
      if (!d) {
        var loi = el("p", "canhbao", "Không nạp được nội dung của " + v.ten + ". Thử tải lại trang.");
        boc.insertBefore(loi, boc.firstChild);
        return;
      }
      var luois = boc.querySelectorAll(".luoi-ch");
      var theo = {};
      luois.forEach(function (g) { theo[g.dataset.ng + "|" + g.dataset.ph] = g; });

      d.chuong.forEach(function (c) {
        var g = theo[c.ng + "|" + c.ph];
        if (!g) return;
        g.appendChild(oChuong(v, c));
      });

      if (moId != null) moChuong(v, moId);
    });
  }

  function oChuong(v, c) {
    var co = c.md != null;
    var e;
    if (co) {
      e = el("a", "ch ch-xong");
      e.href = "#/nen/" + v.ma + "/" + c.id;
    } else {
      e = el("div", "ch ch-khoa");
      e.title = "Chương này nằm trong kế hoạch nhưng chưa được tinh luyện.";
    }
    e.style.setProperty("--m", v.mau);
    e.innerHTML =
      '<div class="ch-tt">' + (co ? "✅" : "🔒") + "</div>" +
      (c.chu ? '<div class="ch-chu">' + esc(c.chu) + "</div>" : "") +
      '<div class="ch-so">Chương ' + so3(c.id) + "</div>" +
      '<span class="ch-ten">' + esc(c.ten || "—") + "</span>";
    return e;
  }

  /* ═══════════════ ngăn kéo: đọc một chương ═══════════════ */

  var hoso = document.getElementById("hoso");
  var scrim = document.getElementById("scrim");
  var hosoTren = document.getElementById("hosoTren");
  var hosoTen = document.getElementById("hosoTen");
  var hosoTag = document.getElementById("hosoTag");
  var hosoBody = document.getElementById("hosoBody");
  var hosoChan = document.getElementById("hosoChan");

  function dongHoso() {
    hoso.dataset.open = "0";
    scrim.dataset.open = "0";
    var h = location.hash.split("/");
    if (h.length > 3) location.hash = h.slice(0, 3).join("/");
  }
  document.getElementById("hosoDong").addEventListener("click", dongHoso);
  scrim.addEventListener("click", dongHoso);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && hoso.dataset.open === "1") dongHoso();
  });

  function moChuong(v, id) {
    var d = kho[v.ma];
    if (!d) return napNen(v.ma, function () { moChuong(v, id); });
    var c = d.theoId[id];
    if (!c) return;

    var ng = null;
    for (var i = 0; i < v.nguyen.length; i++) if (v.nguyen[i].laMa === c.ng) ng = v.nguyen[i];
    var pha = ng && ng.pha[c.ph] ? ng.pha[c.ph].ten : null;

    hosoTren.textContent = v.ten + " · Chương " + so3(c.id) +
      (ng ? " · Nguyên " + ng.laMa : "");
    hosoTen.textContent = c.ten || "—";

    hosoTag.innerHTML = "";
    var cham = el("span", "cham");
    cham.style.setProperty("--m", v.mau);
    cham.innerHTML = "<i></i>" + esc(ng ? (ng.ten || ng.laMa) : "");
    hosoTag.appendChild(cham);
    if (pha) hosoTag.appendChild(el("span", "the", pha));
    if (c.loai) hosoTag.appendChild(el("span", "the", c.loai));

    // đếm nhãn độ chắc chắn
    Object.keys(NHAN).forEach(function (t) {
      var n = c.nhan && c.nhan[t];
      if (!n) return;
      var s = el("span", "the");
      s.style.background = "transparent";
      s.style.color = NHAN[t].mau;
      s.style.border = "1px solid " + NHAN[t].mau + "55";
      s.textContent = NHAN[t].ten + " " + n;
      s.title = NHAN[t].giai;
      hosoTag.appendChild(s);
    });

    hosoBody.innerHTML = "";
    if (c.md == null) {
      var t = el("div", "thieu");
      t.innerHTML = "<b>Chương này chưa được tinh luyện.</b>" +
        "Nó có trong roadmap của " + esc(v.ten) + " nên vẫn hiện ra ở đây, nhưng " +
        "file nội dung <code>chapters/" + so3(c.id) + "-….md</code> chưa tồn tại. " +
        "Roadmap giữ chỗ sẵn để biết còn thiếu gì.";
      hosoBody.appendChild(t);
    } else {
      var b = el("div", "md");
      b.innerHTML = dungMd(c.md);
      hosoBody.appendChild(b);
    }
    hosoBody.scrollTop = 0;

    // chân: chương trước/sau + các chương được dẫn tới
    hosoChan.innerHTML = "";
    var ds = d.chuong, vt = -1;
    for (var k = 0; k < ds.length; k++) if (ds[k].id === c.id) vt = k;
    if (vt > 0) hosoChan.appendChild(nutCh(v, ds[vt - 1], "← "));
    if (vt >= 0 && vt < ds.length - 1) hosoChan.appendChild(nutCh(v, ds[vt + 1], "", " →"));

    var noi = (c.cheo || []).filter(function (x) { return d.theoId[x]; }).slice(0, 6);
    if (noi.length) {
      var g = el("span", "goiy", "Dẫn tới: ");
      noi.forEach(function (x, j) {
        var a = el("a");
        a.href = "#/nen/" + v.ma + "/" + x;
        a.textContent = "Ch." + so3(x);
        a.title = d.theoId[x].ten || "";
        g.appendChild(a);
        if (j < noi.length - 1) g.appendChild(document.createTextNode(", "));
      });
      hosoChan.appendChild(g);
    }

    hoso.dataset.open = "1";
    scrim.dataset.open = "1";
  }

  function nutCh(v, c, truoc, sau) {
    var a = el("a", "nut-phu");
    a.href = "#/nen/" + v.ma + "/" + c.id;
    a.textContent = (truoc || "") + "Ch." + so3(c.id) + (sau || "");
    a.title = c.ten || "";
    return a;
  }

  /* ═══════════════ trang: dòng chảy (mô-típ) ═══════════════ */

  function trangDongChay() {
    tieu.textContent = "Dòng chảy";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML = GIAI.dongchay +
      ' <span class="vn"><b>Cách đọc bảng này:</b> mỗi mô-típ là một câu hỏi mà nhiều ' +
      "nền cùng phải trả lời. Số bên phải là số nền có chương khớp. Danh sách mô-típ do " +
      "người viết tay; việc gắn chương vào mô-típ là máy dò từ khoá trong tiêu đề chương, " +
      "nên có sót và có dư — dùng làm lối gợi ý đọc chéo, đừng dùng làm bằng chứng.</span>";
    than.appendChild(gt);

    var kh = el("section", "khoi");
    var dinh = el("div", "khoi-dinh");
    dinh.innerHTML = "<h2>Mô-típ lặp lại</h2><span class=\"khoi-n\">" +
      R.motif.length + " mô-típ · " + R.tong.vanHoa + " nền</span>";
    kh.appendChild(dinh);

    R.motif.forEach(function (m) {
      var o = el("div", "motif");
      var d = el("div", "motif-dinh");
      d.innerHTML = "<h3>" + esc(m.ten) + '</h3><span class="motif-n">' +
        m.phu + "/" + R.tong.vanHoa + " nền</span>";
      o.appendChild(d);
      o.appendChild(el("p", "motif-hoi", m.hoi));

      var day = el("div", "motif-day");
      m.theo.forEach(function (t) {
        var v = vhTheoMa[t.vh];
        if (!v) return;
        var a = el("a", "motif-nen");
        a.href = "#/nen/" + v.ma + "/" + t.ch[0].id;
        a.style.setProperty("--m", v.mau);
        a.title = t.ch.map(function (c) { return "Ch." + so3(c.id) + " " + c.ten; }).join("\n");
        a.innerHTML = "<i></i><b>" + esc(v.ten) + "</b><span>" + t.n + "</span>";
        day.appendChild(a);
      });
      o.appendChild(day);
      kh.appendChild(o);
    });
    than.appendChild(kh);
  }

  /* ═══════════════ trang: bài học đúc kết ═══════════════ */

  function trangBaiHoc() {
    tieu.textContent = "Bài học đúc kết";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML = GIAI.baihoc;
    than.appendChild(gt);

    R.vh.forEach(function (v) {
      if (!v.hoc || !v.hoc.length) return;
      var kh = el("section", "khoi");
      var dinh = el("div", "khoi-dinh");
      dinh.innerHTML = "<h2>" + esc(v.ten) + '</h2><span class="khoi-n">' +
        v.hoc.length + " nguyên có bài học</span>";
      dinh.style.borderTop = "3px solid " + v.mau;
      kh.appendChild(dinh);

      v.hoc.forEach(function (h) {
        var o = el("div", "hoc");
        var a = el("a", "hoc-trai");
        a.href = "#/nen/" + v.ma + "/" + h.id;
        a.innerHTML = '<div class="hoc-ng">' + esc(h.ng) + '</div><span class="hoc-ch">Ch.' +
          so3(h.id) + "</span>";
        o.appendChild(a);

        var p = el("div", "hoc-phai");
        p.innerHTML =
          (h.ngTen ? '<div class="hoc-nen">' + esc(h.ngTen) + "</div>" : "") +
          '<div class="hoc-dinh"><b>' + esc(h.ten || "") + "</b>" +
          '<span class="hoc-dan">' + h.dan + " chương khác dẫn tới</span></div>" +
          '<p class="hoc-loi">' + noiDong(h.loi) + "</p>";
        o.appendChild(p);
        kh.appendChild(o);
      });
      than.appendChild(kh);
    });
  }

  /* ═══════════════ trang: xu hướng nhãn ═══════════════ */

  function trangXuHuong() {
    tieu.textContent = "Thần thoại → lịch sử";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML = GIAI.xuhuong;
    than.appendChild(gt);

    var thu = ["TRADITION", "SCHOLARLY INTERPRETATION", "OPEN QUESTION", "PRIMARY SOURCE", "FACT"];

    R.vh.forEach(function (v) {
      var co = v.xu.filter(function (x) { return x.tong > 0; });
      if (!co.length) return;

      var kh = el("section", "khoi");
      var dinh = el("div", "khoi-dinh");
      var d0 = co[0], dn = co[co.length - 1];
      var f0 = pct(d0.nhan.FACT, d0.tong), fn = pct(dn.nhan.FACT, dn.tong);
      dinh.innerHTML = "<h2>" + esc(v.ten) + '</h2><span class="khoi-n">Sự kiện: ' +
        f0 + "% ở nguyên " + d0.ng + " → " + fn + "% ở nguyên " + dn.ng + "</span>";
      dinh.style.borderTop = "3px solid " + v.mau;
      kh.appendChild(dinh);

      var cg = el("div", "chugiai");
      thu.forEach(function (t) {
        var s = el("span");
        s.innerHTML = '<i style="background:' + NHAN[t].mau + '"></i>' + esc(NHAN[t].ten);
        s.title = NHAN[t].giai;
        cg.appendChild(s);
      });
      kh.appendChild(cg);

      co.forEach(function (x) {
        var h = el("div", "xu-hang");
        var dai = thu.map(function (t) {
          var w = (x.nhan[t] / x.tong) * 100;
          return w > 0 ? '<i style="width:' + w.toFixed(2) + "%;background:" + NHAN[t].mau + '" title="' +
            esc(NHAN[t].ten + ": " + x.nhan[t]) + '"></i>' : "";
        }).join("");
        h.innerHTML =
          '<div class="xu-ng">' + esc(x.ng) + "</div>" +
          '<div class="xu-ten">' + esc(x.ngTen || "") + "</div>" +
          '<div class="xu-dai">' + dai + "</div>" +
          '<div class="xu-so">' + x.tong + " nhãn</div>";
        kh.appendChild(h);
      });
      than.appendChild(kh);
    });
  }

  /* ═══════════════ tìm ═══════════════ */

  var timTre = null;
  oTim.addEventListener("input", function () {
    clearTimeout(timTre);
    timTre = setTimeout(function () {
      var q = oTim.value.trim();
      if (!q) { dinhTuyen(); return; }
      chayTim(q);
    }, 160);
  });

  function chayTim(q) {
    tieu.textContent = "Tìm";
    than.innerHTML = "";
    than.appendChild(el("div", "dang", "Đang tìm…"));

    napTim(function (d) {
      than.innerHTML = "";
      if (!d) {
        than.appendChild(el("div", "trong", "Không nạp được chỉ mục tìm."));
        return;
      }
      var k = khongDau(q);
      var ra = [];
      d.forEach(function (nen) {
        var v = vhTheoMa[nen.ma];
        if (!v) return;
        nen.ch.forEach(function (c) {
          if (khongDau(c[1]).indexOf(k) !== -1 || String(c[0]) === q) {
            ra.push({ v: v, id: c[0], ten: c[1], co: c[2], ng: c[3] });
          }
        });
      });

      var gt = el("div", "giaithich");
      gt.innerHTML = "<b>" + ra.length.toLocaleString("vi-VN") + "</b> chương khớp “" +
        esc(q) + "” trên tổng " + R.tong.keHoach.toLocaleString("vi-VN") +
        " chương của cả 15 nền. Tìm theo tiêu đề chương, không dấu cũng được.";
      than.appendChild(gt);

      if (!ra.length) {
        than.appendChild(el("div", "trong", "Không có chương nào khớp."));
        return;
      }

      var kh = el("section", "khoi");
      ra.slice(0, 300).forEach(function (x) {
        var a = el("a", "kq");
        a.href = "#/nen/" + x.v.ma + (x.co ? "/" + x.id : "");
        a.style.setProperty("--m", x.v.mau);
        a.innerHTML =
          '<div class="kq-dinh">' +
            '<span class="kq-nen"><i></i>' + esc(x.v.ten) + "</span>" +
            '<span class="kq-so">Ch.' + so3(x.id) + "</span>" +
            '<span class="kq-ten">' + esc(x.ten) + "</span>" +
            '<span class="kq-ng">' + (x.co ? "nguyên " + esc(x.ng) : "chưa viết") + "</span>" +
          "</div>";
        kh.appendChild(a);
      });
      than.appendChild(kh);
      if (ra.length > 300) {
        than.appendChild(el("div", "trong", "Còn " + (ra.length - 300) +
          " kết quả nữa — gõ thêm chữ để thu hẹp."));
      }
    });
  }

  /* ═══════════════ định tuyến ═══════════════ */

  /* Lớp tri thức nền — knowledge-os/sinh.mjs ghi ra
     assets/js/v/tri-thuc.js, mang cả dữ liệu lẫn hàm vẽ nên khuôn giống
     hệt mọi cung khác. Nó KHÔNG đụng dữ liệu văn hoá nào.

     Cung này cần nhãn nguồn hơn mọi cung khác: sách viết về Bitcoin và
     kinh tế học Áo, còn đây là mười lăm nền văn hoá. Nối hai thứ mà
     không nói rõ đâu là suy luận thì thành áp một cuốn sách lên thần
     thoại — nên mọi dòng ở đây đều đeo nhãn, và ánh xạ mang nhãn
     "phân tích" chứ không bao giờ nhãn "sách".

     Bọc `dinhTuyen` chứ không sửa từng nhánh: hàm gốc có sáu đường ra,
     và nối ở một chỗ sau khi nó chạy xong là một chỗ phải nhớ thay vì
     sáu. `them()` tự gỡ khối cũ nên vẽ lại cùng tuyến không chồng khối. */
  function dinhTuyen() {
    dinhTuyenNoiDung();
    var TT = window.TRI_THUC;
    if (TT && TT.them) {
      TT.them(than, (location.hash || "#/rung").replace(/^#\/?/, "").split("/")[0]);
    }
  }

  function dinhTuyenNoiDung() {
    var h = location.hash || "#/rung";
    var p = h.replace(/^#\/?/, "").split("/");

    if (hoso.dataset.open === "1" && !(p[0] === "nen" && p[2])) {
      hoso.dataset.open = "0";
      scrim.dataset.open = "0";
    }

    sangMuc("#/" + p.slice(0, 2).join("/"));
    document.getElementById("ben").dataset.mo = "0";

    if (p[0] === "nen" && p[1]) {
      var moId = p[2] ? Number(p[2]) : null;
      // đang ở đúng nền rồi thì chỉ mở/đóng chương, không dựng lại roadmap
      if (than.dataset.nen === p[1]) {
        if (moId != null) moChuong(vhTheoMa[p[1]], moId);
        return;
      }
      than.dataset.nen = p[1];
      trangNen(p[1], moId);
      return;
    }

    than.dataset.nen = "";
    if (p[0] === "dong-chay") return trangDongChay();
    if (p[0] === "bai-hoc") return trangBaiHoc();
    if (p[0] === "xu-huong") return trangXuHuong();
    trangRung();
  }

  window.addEventListener("hashchange", function () {
    if (oTim.value.trim()) oTim.value = "";
    dinhTuyen();
  });

  document.getElementById("benMoNut").addEventListener("click", function () {
    var b = document.getElementById("ben");
    b.dataset.mo = b.dataset.mo === "1" ? "0" : "1";
  });

  /* ═══════════════ khởi động ═══════════════ */

  document.getElementById("ngay").textContent = "cập nhật " + R.date;
  dungBen();
  dinhTuyen();
})();
