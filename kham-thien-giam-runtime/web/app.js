/* Buồng lái Khâm Thiên Giám.

   Luật của giao diện này, và nó khác hẳn mấy dashboard "quant lab" mà tài
   liệu mổ xẻ: KHÔNG ô nào được vẽ khi chưa có số. Chưa có thì nói "chưa có".

   Một ô hiện 0 khi thực ra là "chưa đo" là một ô nói dối, và nó nói dối theo
   đúng chiều làm người ta yên tâm. */
(function () {
  "use strict";

  var T = null;          // trạng thái mới nhất
  var O = "dai-chiem";   // ô đang mở
  var than = document.getElementById("than");

  /* ── tiện ─────────────────────────────────────────────────────── */
  function el(t, c, x) {
    var e = document.createElement(t);
    if (c) e.className = c;
    if (x != null) e.textContent = x;
    return e;
  }
  function so(v, n) {
    if (v == null || !isFinite(v)) return "—";
    return Number(v).toFixed(n == null ? 2 : n);
  }
  function pc(v, n) {
    if (v == null || !isFinite(v)) return "—";
    return (v * 100).toFixed(n == null ? 1 : n) + "%";
  }
  function usd(v) {
    if (v == null || !isFinite(v)) return "—";
    return (v < 0 ? "-$" : "$") + Math.abs(v).toFixed(2);
  }
  function cent(v) {
    if (v == null || !isFinite(v)) return "—";
    return (v >= 0 ? "+" : "") + (v * 100).toFixed(2) + "¢";
  }
  function huong(v) { return v == null ? "mo" : (v > 0 ? "len" : (v < 0 ? "xuong" : "mo")); }

  function oKhung(ten, phu) {
    var o = el("section", "o");
    var d = el("div", "o-dinh");
    d.appendChild(el("h2", null, ten));
    if (phu) d.appendChild(el("span", "phu", phu));
    o.appendChild(d);
    var t = el("div", "o-than");
    o.appendChild(t);
    o._than = t;
    return o;
  }
  function chi(nhan, giaTri, ghi, lop) {
    var c = el("div", "chi");
    c.appendChild(el("b", null, nhan));
    c.appendChild(el("div", "v " + (lop || ""), giaTri));
    if (ghi) c.appendChild(el("div", "g", ghi));
    return c;
  }
  function chuaCo(msg) { return el("p", "chua", msg || "chưa có dữ liệu"); }

  function bang(cot, hang) {
    var t = el("table"), th = el("thead"), tr = el("tr");
    cot.forEach(function (c) {
      var e = el("th", null, typeof c === "string" ? c : c.t);
      if (typeof c === "object" && c.num) e.className = "num";
      tr.appendChild(e);
    });
    th.appendChild(tr); t.appendChild(th);
    var tb = el("tbody");
    hang.forEach(function (h) {
      var r = el("tr");
      h.forEach(function (o) {
        var td = el("td", (o && o.cls) || "");
        if (o && o.el) td.appendChild(o.el);
        else td.textContent = (o && o.v != null) ? o.v : (o == null ? "—" : o);
        r.appendChild(td);
      });
      tb.appendChild(r);
    });
    t.appendChild(tb);
    return t;
  }

  /* ── ĐÀI CHIÊM ────────────────────────────────────────────────── */
  function veDaiChiem() {
    var g = document.createDocumentFragment();
    var tt = (T.thiTruong || []).filter(function (x) { return x.theo; });
    if (!tt.length) { g.appendChild(chuaCo("chưa theo market nào")); return g; }

    tt.forEach(function (m) {
      var o = oKhung("Đài Chiêm · " + m.ma, m.gia ? null : "chưa đủ mẫu biến động");
      if (!m.gia) {
        o._than.appendChild(chuaCo(
          "Chưa đủ mẫu giá để ước lượng σ. Mô hình cố ý KHÔNG đoán khi thiếu " +
          "nguyên liệu — trả 0,5 ở đây trông như một câu trả lời và sẽ lặng lẽ " +
          "chảy vào phép tính lợi thế."));
        g.appendChild(o); return;
      }
      var q = m.gia, s = m.so || {};
      var chợUp = (s.UP && s.UP.bestAsk != null) ? s.UP.bestAsk : null;

      var l = el("div", "luoi3");
      l.appendChild(chi("Mô hình P(UP)", pc(q.pUp), "±" + so(q.batDinh * 100, 1) + " điểm",
        q.roRang ? "saoc" : "mo"));
      l.appendChild(chi("Chợ hỏi UP", chợUp == null ? "—" : so(chợUp * 100, 1) + "¢",
        s.UP ? "spread " + so((s.UP.spread || 0) * 100, 1) + "¢" : null));
      l.appendChild(chi("Chênh thô", chợUp == null ? "—" : cent(q.pUp - chợUp),
        "chưa trừ gì cả", huong(chợUp == null ? null : q.pUp - chợUp)));
      l.appendChild(chi("Còn lại", so(q.tauGiay, 0) + "s",
        q.tauDungSan ? "τ đã kẹp về sàn" : null, q.tauDungSan ? "canh" : ""));
      l.appendChild(chi("z", (q.z >= 0 ? "+" : "") + so(q.z, 2),
        "σ " + (q.sigmaGiay * 1e5).toFixed(2) + "e-5/giây"));
      l.appendChild(chi("Rủi ro nhảy", so(q.ruiRoNhay * 100, 1) + " điểm",
        "tham số " + so(q.batDinhThamSo * 100, 1),
        q.ruiRoNhay > 0.12 ? "xuong" : "mo"));
      o._than.appendChild(l);

      if (!q.roRang) {
        var c = el("p", "ghi");
        c.innerHTML = "<b>Mô hình tự nhận là KHÔNG rõ ràng.</b> Bất định (±" +
          so(q.batDinh * 100, 1) + " điểm) lớn hơn khoảng cách từ P tới 50%, " +
          "nghĩa là nó đang nói \"tôi không biết\" bằng một con số trông như đang biết.";
        o._than.appendChild(c);
      }
      if (q.daMatPhang) {
        var p = el("p", "ghi");
        p.innerHTML = "<b>Đã làm phẳng ở cận kết quả.</b> Công thức trần cho ra " +
          "0 hoặc 1; không outcome nào đáng giá đúng 0 hay đúng 1 khi một tick " +
          "vẫn lật được kết quả.";
        o._than.appendChild(p);
      }

      // giải trình tín hiệu
      var gt = q.giaiTrinh;
      if (gt && gt.chiTiet && gt.chiTiet.length) {
        var h = gt.chiTiet.map(function (c) {
          return [{ v: c.ten, cls: "t" }, { v: c.ho, cls: "t" },
                   { v: (c.tho >= 0 ? "+" : "") + so(c.tho, 3), cls: "num" },
                   { v: "×" + so(c.trongSo, 2), cls: "num" },
                   { v: (c.gop >= 0 ? "+" : "") + so(c.gop, 3), cls: "num" }];
        });
        o._than.appendChild(el("div", "ghi",
          "Tín hiệu phụ — gộp " + gt.soHo + " họ, không phải " +
          gt.chiTiet.length + " bằng chứng độc lập:"));
        o._than.appendChild(bang(
          ["tín hiệu", "họ", { t: "thô", num: 1 }, { t: "trọng số", num: 1 },
           { t: "góp", num: 1 }], h));
      }
      g.appendChild(o);
    });
    return g;
  }

  /* ── SỔ LỆNH ──────────────────────────────────────────────────── */
  function veSoLenh() {
    var g = document.createDocumentFragment();
    var co = false;
    (T.thiTruong || []).forEach(function (m) {
      if (!m.so) return;
      co = true;
      var o = oKhung("Sổ lệnh · " + m.ma);
      var w = el("div", "book");
      ["UP", "DOWN"].forEach(function (ben) {
        var s = m.so[ben];
        if (!s) return;
        var col = el("div");
        col.appendChild(el("div", "ghi", ben + " — best " +
          so((s.bestBid || 0) * 100, 1) + "¢ / " + so((s.bestAsk || 0) * 100, 1) +
          "¢ · lệch " + (s.lech == null ? "—" : (s.lech >= 0 ? "+" : "") + so(s.lech, 3)) +
          " · vi giá " + so((s.viGia || 0) * 100, 2) + "¢"));
        var max = 0;
        (s.ask || []).concat(s.bid || []).forEach(function (x) { max = Math.max(max, x.luong); });
        (s.ask || []).slice().reverse().forEach(function (x) { col.appendChild(veMuc(x, max, "a")); });
        col.appendChild(el("div", "ghi", "── spread " + so(((s.spread) || 0) * 100, 2) + "¢ ──"));
        (s.bid || []).forEach(function (x) { col.appendChild(veMuc(x, max, "b")); });
        w.appendChild(col);
      });
      o._than.appendChild(w);
      g.appendChild(o);
    });
    if (!co) g.appendChild(chuaCo("chưa nhận được sổ lệnh nào"));
    return g;
  }
  function veMuc(x, max, k) {
    var d = el("div", "muc " + k);
    var t = el("div", "thanh");
    t.style.width = max > 0 ? (x.luong / max * 100) + "%" : "0";
    d.appendChild(t);
    d.appendChild(el("div", "g", (x.gia * 100).toFixed(1) + "¢"));
    d.appendChild(el("div", "l", Math.round(x.luong).toLocaleString("vi-VN")));
    return d;
  }

  /* ── CÂN LỢI ──────────────────────────────────────────────────── */
  function veCanLoi() {
    var g = document.createDocumentFragment();
    var ch = T.coHoi || [];
    var o = oKhung("Cân Lợi · net executable edge",
      ch.length ? ch.filter(function (c) { return c.dangLam; }).length + "/" + ch.length + " qua sàng" : null);

    if (!ch.length) {
      o._than.appendChild(chuaCo("chưa cân được cơ hội nào lượt này"));
      g.appendChild(o);
      return g;
    }
    var h = ch.map(function (c) {
      return [
        { v: c.ma, cls: "t" }, { v: c.ben, cls: "t" }, { v: c.ct, cls: "t" },
        { v: so(c.fair * 100, 1) + "¢", cls: "num" },
        { v: so(c.vwap * 100, 1) + "¢", cls: "num" },
        { v: cent(c.gross), cls: "num " + huong(c.gross) },
        { v: "−" + so(c.phi * 100, 2), cls: "num mo" },
        { v: "−" + so(c.batDinh * 100, 2), cls: "num mo" },
        { v: cent(c.net), cls: "num " + huong(c.net) },
        { v: Math.round(c.sucChua), cls: "num" },
        { v: pc(c.xacSuatKhop, 0), cls: "num" },
        { v: Math.round(c.nuaDoiMs) + "ms", cls: "num" },
        { el: nhan(c.dangLam ? "qua" : "loại", c.dangLam ? "ok" : "no") }
      ];
    });
    o._than.appendChild(bang(
      ["market", "bên", "chiến thuật", { t: "fair", num: 1 }, { t: "vwap", num: 1 },
       { t: "gross", num: 1 }, { t: "phí", num: 1 }, { t: "b.định", num: 1 },
       { t: "NET", num: 1 }, { t: "sức chứa", num: 1 }, { t: "khớp", num: 1 },
       { t: "nửa đời", num: 1 }, ""], h));
    o._than.appendChild(el("div", "ghi",
      "gross là chênh giữa fair và VWAP — chưa phải lợi thế. NET đã trừ phí, " +
      "trượt giá, bất định mô hình và biên an toàn. Chỉ NET mới là alpha."));
    g.appendChild(o);
    return g;
  }
  function nhan(x, c) { return el("span", "nhan " + (c || ""), x); }

  /* ── KHO ĐỐI ──────────────────────────────────────────────────── */
  function veKhoDoi() {
    var g = document.createDocumentFragment();
    var k = T.kho || {}, r = T.risk || {};

    var o1 = oKhung("Vốn và cầu dao");
    var l = el("div", "luoi3");
    l.appendChild(chi("Vốn sổ sách", usd(r.von), "khởi điểm " + usd(r.vonBanDau),
      huong(r.von - r.vonBanDau)));
    l.appendChild(chi("Sụt vốn", so(r.sutVonPct, 2) + "%",
      "trần " + so(r.tranSutVonPct != null ? r.tranSutVonPct : 10, 0) + "%",
      r.sutVonPct > 5 ? "canh" : "mo"));
    l.appendChild(chi("Lỗ hôm nay", usd(r.loNgayUsd), "trần " + usd(r.tranLoNgayUsd),
      r.loNgayUsd > 0 ? "xuong" : "mo"));
    l.appendChild(chi("Nằm trần một chân", usd(k.tongChuaPhongHoUsd),
      "rủi ro THẬT, đang chạy đồng hồ",
      (k.tongChuaPhongHoUsd || 0) > 0 ? "canh" : "mo"));
    l.appendChild(chi("Lỗ đã khoá trong cặp", usd(k.tongLoKhoaUsd),
      "cặp trên 1,00$", (k.tongLoKhoaUsd || 0) > 0 ? "xuong" : "mo"));
    l.appendChild(chi("Phơi nhiễm gộp", usd(k.phoiNhiemGop),
      "sau khi tính tương quan chéo"));
    o1._than.appendChild(l);
    if (r.ngatKhanCap) {
      var w = el("p", "ghi");
      w.innerHTML = "<b class='xuong'>CẦU DAO ĐANG NGẮT:</b> " + (r.lyDoNgat || "");
      o1._than.appendChild(w);
    }
    g.appendChild(o1);

    var vt = k.viThe || [];
    var o2 = oKhung("Tồn kho ba phần");
    if (!vt.length) {
      o2._than.appendChild(chuaCo("chưa có vị thế nào"));
    } else {
      o2._than.appendChild(bang(
        ["market", { t: "UP", num: 1 }, { t: "DOWN", num: 1 },
         { t: "đã ghép cặp", num: 1 }, { t: "định hướng", num: 1 },
         { t: "giá cặp", num: 1 }, { t: "chưa phòng hộ", num: 1 },
         { t: "chờ", num: 1 }, ""],
        vt.map(function (v) {
          return [
            { v: v.ma, cls: "t" },
            { v: Math.round(v.coUp) + " @" + so(v.giaVonUp * 100, 1) + "¢", cls: "num" },
            { v: Math.round(v.coDown) + " @" + so(v.giaVonDown * 100, 1) + "¢", cls: "num" },
            { v: Math.round(v.daGhepCap), cls: "num" },
            { v: (v.dinhHuong > 0 ? "+" : "") + Math.round(v.dinhHuong), cls: "num " + huong(v.dinhHuong) },
            { v: v.giaCap == null ? "—" : "$" + so(v.giaCap, 4), cls: "num " + (v.capKhoaLo ? "xuong" : "len") },
            { v: usd(v.chuaPhongHoUsd), cls: "num" },
            { v: v.choLauNhatMs > 0 ? Math.round(v.choLauNhatMs / 1000) + "s" : "—", cls: "num" },
            { el: v.capKhoaLo ? nhan("khoá lỗ " + usd(v.loKhoaUsd), "no") : nhan("ổn", "ok") }
          ];
        })));
      o2._than.appendChild(el("div", "ghi",
        "Giá cặp trên $1,00 nghĩa là phần \"đã phòng hộ\" đang khoá sẵn một " +
        "khoản lỗ. Phần định hướng phải gỡ đủ chừng đó trước khi cả vị thế hoà — " +
        "nên bảng này khoe GIÁ CẶP chứ không khoe \"đã phòng hộ bao nhiêu %\"."));
    }
    g.appendChild(o2);
    return g;
  }

  /* ── CHIẾN THUẬT ──────────────────────────────────────────────── */
  function veChienThuat() {
    var g = document.createDocumentFragment();
    var o = oKhung("Sáu ngón nghề", "cắm vào cùng một nền máy");
    (T.chienThuat || []).forEach(function (c) {
      var d = el("div", "ct");
      d.dataset.bat = c.bat ? "1" : "0";
      var cong = el("div", "cong");
      cong.addEventListener("click", function () {
        fetch("/api/chien-thuat/" + c.ma, { method: "POST" }).then(tai);
      });
      d.appendChild(cong);
      var x = el("div");
      x.appendChild(el("b", null, c.ten));
      x.appendChild(el("i", null, c.mota));
      d.appendChild(x);
      o._than.appendChild(d);
    });
    g.appendChild(o);

    var lenh = T.lenh || {};
    var o2 = oKhung("Lệnh", lenh.duong ? "đường: " + lenh.duong : null);
    var l = el("div", "luoi3");
    l.appendChild(chi("Tổng lệnh", String(lenh.tongLenh || 0)));
    l.appendChild(chi("Đã khớp", String(lenh.daKhop || 0)));
    l.appendChild(chi("Đang chờ", String(lenh.dangCho || 0), "lệnh maker"));
    l.appendChild(chi("Tổng phí", usd(lenh.tongPhiUsd)));
    o2._than.appendChild(l);
    if (lenh.cuaDangDong && lenh.cuaDangDong.length) {
      var p = el("p", "ghi");
      p.innerHTML = "<b>Cửa lệnh thật đang đóng:</b><br>· " +
        lenh.cuaDangDong.join("<br>· ");
      o2._than.appendChild(p);
    }
    g.appendChild(o2);
    return g;
  }

  /* ── TRƯỜNG THI ───────────────────────────────────────────────── */
  function veTruongThi() {
    var g = document.createDocumentFragment();
    var h = T.hieuChinh || {}, tk = T.thongKe || {};

    var o = oKhung("Hiệu chỉnh", h.tongMau + " mẫu · Kelly " +
      (h.duDeDungKelly ? "MỞ" : "khoá"));
    if (!h.tongMau) {
      o._than.appendChild(chuaCo(
        "Chưa có market nào kết toán để đối chiếu. Kelly bị khoá cho tới khi " +
        "đủ mẫu — dùng Kelly trên một xác suất chưa ai kiểm là khuếch đại " +
        "chính sai lầm của mô hình."));
    } else {
      (h.bang || []).forEach(function (r) {
        if (!r.n) return;
        var d = el("div", "hc");
        d.appendChild(el("div", "o1", r.o + "%"));
        var t = el("div", "thanh");
        var du = el("div", "du"); du.style.width = (r.duDoan * 100) + "%";
        var th = el("div", "that"); th.style.left = (r.thucTe * 100) + "%";
        t.appendChild(du); t.appendChild(th);
        d.appendChild(t);
        d.appendChild(el("div", "o1", "n=" + r.n));
        d.appendChild(el("div", "o1 " + huong(r.lech),
          (r.lech >= 0 ? "+" : "") + so(r.lech * 100, 1)));
        o._than.appendChild(d);
      });
      o._than.appendChild(el("div", "ghi",
        "Vệt xanh nhạt = mô hình dự đoán. Vạch xanh lá = thực tế. Hai cái " +
        "trùng nhau thì mô hình đáng tin. Sai số trung bình: " +
        (h.saiSoTB == null ? "—" : so(h.saiSoTB * 100, 2) + " điểm")));
    }
    g.appendChild(o);

    var o2 = oKhung("Kết quả", tk.n ? tk.n + " market đã kết toán" : null);
    if (tk.chuaCo || !tk.n) {
      o2._than.appendChild(chuaCo("chưa market nào kết toán"));
    } else {
      var l = el("div", "luoi3");
      l.appendChild(chi("Tỉ lệ thắng", pc(tk.tiLeThang),
        tk.soThang + " thắng / " + tk.soThua + " thua"));
      l.appendChild(chi("Kỳ vọng", usd(tk.kyVong), "mỗi lệnh", huong(tk.kyVong)));
      l.appendChild(chi("Tổng lãi lỗ", usd(tk.tongLaiLo), null, huong(tk.tongLaiLo)));
      l.appendChild(chi("Thua lớn nhất", usd(tk.thuaLonNhat), null, "xuong"));
      l.appendChild(chi("Xoá bao nhiêu lần thắng",
        tk.xoaBaoNhieuLanThang == null ? "—" : so(tk.xoaBaoNhieuLanThang, 0) + " lần",
        "một lần thua lớn nhất", tk.canhBaoDuoi ? "xuong" : "mo"));
      l.appendChild(chi("Đuôi 5%", usd(tk.duoi5pct), "trung bình 5% tệ nhất", "xuong"));
      o2._than.appendChild(l);
      if (tk.canhBaoDuoi) {
        var p = el("p", "ghi");
        p.innerHTML = "<b class='xuong'>Đuôi lệch:</b> tỉ lệ thắng " +
          pc(tk.tiLeThang) + " nhưng MỘT lần thua lớn nhất xoá " +
          so(tk.xoaBaoNhieuLanThang, 0) + " lần thắng. Tỉ lệ thắng ở đây " +
          "không nói lên điều gì về an toàn.";
        o2._than.appendChild(p);
      }
    }
    g.appendChild(o2);

    var b = T.bang || {};
    var o3 = oKhung("Băng ghi", b.bat ? "đang ghi" : "TẮT");
    o3._than.appendChild(el("div", "luoi3")).appendChild(
      chi("Khung đã ghi", (b.soKhung || 0).toLocaleString("vi-VN"),
        "P0 — phải làm trước mô hình"));
    o3._than.appendChild(el("div", "ghi",
      "Không lưu sổ lệnh và tick ngay từ đầu thì ba tháng nữa dù muốn nghiên " +
      "cứu cũng không có ký ức nào để chạy lại. Mô hình viết sau lúc nào cũng " +
      "được; dữ liệu thì không quay lại."));
    g.appendChild(o3);
    return g;
  }

  /* ── ĐÀI QUAN VÍ ──────────────────────────────────────────────── */
  function veQuanVi() {
    var g = document.createDocumentFragment();
    var v = T.vi || {};
    var o = oKhung("Đài Quan Ví", v.soVi ? v.soVi + " ví" : "chưa quét");
    if (!v.vi || !v.vi.length) {
      o._than.appendChild(chuaCo("chưa quét ví nào — lượt quét cách nhau 30 phút"));
    } else {
      o._than.appendChild(bang(
        ["ví", { t: "lệnh", num: 1 }, { t: "market", num: 1 },
         { t: "cả hai chiều", num: 1 }, { t: "cận kết quả", num: 1 },
         { t: "giá vào TB", num: 1 }, "nhãn"],
        v.vi.map(function (h) {
          var n = el("div");
          (h.nhan || []).forEach(function (x) {
            n.appendChild(nhan(x.ten, "sao"));
            n.appendChild(document.createTextNode(" "));
          });
          if (!(h.nhan || []).length) n.textContent = "—";
          return [
            { v: h.ten, cls: "t" },
            { v: (h.soLenh || 0).toLocaleString("vi-VN"), cls: "num" },
            { v: h.soMarket, cls: "num" },
            { v: pc(h.tiLeCaHaiChieu, 0), cls: "num" },
            { v: pc(h.tiLeCanKetQua, 0), cls: "num" },
            { v: so((h.giaVaoTrungBinh || 0) * 100, 1) + "¢", cls: "num" },
            { el: n }
          ];
        })));
    }
    var p = el("p", "ghi");
    p.innerHTML = "<b>Giới hạn không vượt qua được:</b> " + (v.gioiHan ||
      "Đặt/huỷ lệnh diễn ra off-chain, nên chỉ thấy được các lần KHỚP.");
    o._than.appendChild(p);
    g.appendChild(o);
    return g;
  }

  /* ── NHẬT KÝ ──────────────────────────────────────────────────── */
  function veNhatKy() {
    var g = document.createDocumentFragment();
    var o = oKhung("Nhật ký");
    var d = el("div", "nk");
    (T.nhatKy || []).slice().reverse().forEach(function (e) {
      var r = el("div");
      r.dataset.l = e.loai;
      r.appendChild(el("span", "t", (e.luc || "").slice(11, 23)));
      r.appendChild(el("span", null, e.muc));
      d.appendChild(r);
    });
    if (!(T.nhatKy || []).length) d.appendChild(chuaCo("chưa có dòng nào"));
    o._than.style.padding = "0";
    o._than.appendChild(d);
    g.appendChild(o);

    var n = T.nguon || {};
    var o2 = oKhung("Sức khoẻ nguồn");
    var ks = Object.keys(n);
    if (!ks.length) o2._than.appendChild(chuaCo("chưa gọi nguồn nào"));
    else o2._than.appendChild(bang(
      ["nguồn", { t: "tuổi", num: 1 }, { t: "lượt", num: 1 },
       { t: "lỗi liên tiếp", num: 1 }, "lỗi cuối"],
      ks.map(function (k) {
        var x = n[k];
        return [{ v: k, cls: "t" },
          { v: isFinite(x.tuoiMs) ? Math.round(x.tuoiMs) + "ms" : "chưa", cls: "num" },
          { v: x.tongLuot, cls: "num" },
          { v: x.soLoi, cls: "num " + (x.soLoi >= 3 ? "xuong" : "mo") },
          { v: x.loiCuoi || "—", cls: "t mo" }];
      })));
    g.appendChild(o2);
    return g;
  }

  /* ── vẽ ───────────────────────────────────────────────────────── */
  var VE = {
    "dai-chiem": veDaiChiem, "so-lenh": veSoLenh, "can-loi": veCanLoi,
    "kho-doi": veKhoDoi, "chien-thuat": veChienThuat,
    "truong-thi": veTruongThi, "quan-vi": veQuanVi, "nhat-ky": veNhatKy
  };

  function ve() {
    if (!T) return;
    than.textContent = "";
    than.appendChild((VE[O] || veDaiChiem)());

    var c = document.getElementById("cheDo");
    c.textContent = T.che === "that" ? "TIỀN THẬT" :
      (T.che === "giay" ? "sổ giấy" : "quan sát");
    c.dataset.c = T.che;

    document.getElementById("dongHo").textContent =
      "vòng " + T.vong + " · " + Math.round(T.chayDuocGiay) + "s";
    document.getElementById("vongDem").textContent =
      "vòng " + T.vong + " · băng " + ((T.bang || {}).soKhung || 0) + " khung";
    document.getElementById("nutDung").textContent =
      T.tamDung ? "Chạy tiếp" : "Tạm dừng";
    document.getElementById("nutDung").classList.toggle("dang", !!T.tamDung);

    var bc = document.getElementById("bangCanh");
    var r = T.risk || {};
    if (r.ngatKhanCap) {
      bc.textContent = "CẦU DAO ĐANG NGẮT — " + (r.lyDoNgat || "") +
        ". Mọi lệnh bị chặn cho tới khi mở lại bằng tay.";
      bc.hidden = false;
    } else bc.hidden = true;
  }

  function tai() {
    return fetch("/api/trang-thai", { cache: "no-store" })
      .then(function (r) { return r.json(); })
      .then(function (d) { T = d; ve(); })
      .catch(function () {});
  }

  document.getElementById("tab").addEventListener("click", function (e) {
    var b = e.target.closest("button[data-o]");
    if (!b) return;
    O = b.dataset.o;
    [].forEach.call(this.children, function (x) { x.classList.toggle("chon", x === b); });
    ve();
  });

  document.getElementById("nutDung").addEventListener("click", function () {
    fetch("/api/tam-dung", { method: "POST" }).then(tai);
  });
  document.getElementById("nutDao").addEventListener("click", function () {
    var dangNgat = T && T.risk && T.risk.ngatKhanCap;
    fetch("/api/cau-dao?mo=" + (dangNgat ? "true" : "false"), { method: "POST" }).then(tai);
  });
  document.getElementById("nutLat").addEventListener("click", function () {
    var b = this;
    b.textContent = "đang ghi…";
    fetch("/api/lat-cat", { method: "POST" })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        b.textContent = d.daGhi ? "đã ghi ✓" : "không tìm thấy cung";
        setTimeout(function () { b.textContent = "Ghi lát cắt"; }, 2400);
      });
  });

  tai();
  setInterval(tai, 2000);
})();
