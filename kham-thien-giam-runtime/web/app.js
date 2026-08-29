/* Buồng lái Khâm Thiên Giám.

   Luật của giao diện này, và nó khác hẳn mấy dashboard "quant lab" mà tài
   liệu mổ xẻ: KHÔNG ô nào được vẽ khi chưa có số. Chưa có thì nói "chưa có".

   Một ô hiện 0 khi thực ra là "chưa đo" là một ô nói dối, và nó nói dối theo
   đúng chiều làm người ta yên tâm. */
(function () {
  "use strict";

  var T = null;          // trạng thái mới nhất
  var O = "tat-ca";      // trang đang mở (nay là cấp CHUYÊN MỤC)
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
  function gia(v) {
    if (v == null || !isFinite(v)) return "—";
    return (v * 100).toFixed(1) + "¢";
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
    // Vỏ cuộn ngang. Không có nó, bảng nào rộng hơn ô sẽ bị CẮT CỤT — mất
    // hẳn cột cuối mà không một dấu hiệu nào. Đã xảy ra thật với bảng tồn
    // kho: cột "giá cặp" biến mất trong khi nó là cột đáng đọc nhất.
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
    var vo = el("div", "bang-vo");
    vo.appendChild(t);
    return vo;
  }

  /* ── ĐÀI CHIÊM ────────────────────────────────────────────────── */
  function veDaiChiem() {
    var g = document.createDocumentFragment();
    var tt = khungDeVe();
    if (!tt.length) { g.appendChild(chuaCo("Chưa theo market nào. Bật một khung trong `config.json` "
        + "(`thiTruong[].theo = true`) rồi khởi động lại runtime.")); return g; }

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
    khungDeVe().forEach(function (m) {
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
    if (!co) {
      var mm = khungHienTai();
      g.appendChild(chuaCo("chưa nhận được sổ lệnh cho " +
        (mm ? mm.ma : "khung nào") + " — dòng sống có thể vừa nối lại, " +
        "hoặc khung này chưa mở cửa đặt cược."));
    }
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
      o._than.appendChild(chuaCo("Chưa cân được cơ hội nào lượt này. Bảng này chỉ có mục khi sổ "
        + "đang yết giá THẬT và mô hình đủ mẫu σ — xem dòng CHỢ ở thẻ chỉ huy "
        + "để biết đang vướng cái nào."));
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
      o2._than.appendChild(chuaCo("Chưa có vị thế nào. Kho chỉ có hàng sau lần khớp đầu tiên; "
        + "trước đó mọi cột ở đây đều bằng 0 một cách đúng đắn."));
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

    // NẮN LẠI — chỗ hở cuối của vòng học vừa khép. Đặt ngay dưới bảng
    // hiệu chỉnh vì nó đọc chính bảng đó: đo được lệch thì phải sửa lệch,
    // không thì đo để làm gì.
    var nl = T.nanLai || {};
    var on = oKhung("Nắn lại", nl.dungDuoc
      ? nl.tongMau + " mẫu · giảm chấn " + nl.heSoGiamChan
      : "chưa nắn");
    if (!nl.dungDuoc) {
      on._than.appendChild(chuaCo(
        "Chưa nắn. Cần đủ mẫu kết toán trước khi sửa mô hình theo sổ — " +
        "nắn trên vài chục lượt là học thuộc tiếng ồn rồi đem tiếng ồn đi cược."));
    } else {
      var ln = el("div", "luoi3");
      ln.appendChild(chi("Sai số trước", so(nl.saiTruoc * 100, 2) + " điểm",
        "mô hình thô", "xuong"));
      ln.appendChild(chi("Sai số sau", so(nl.saiSau * 100, 2) + " điểm",
        "sau khi nắn", "len"));
      ln.appendChild(chi("Cải thiện", so(nl.caiThien * 100, 2) + " điểm",
        nl.soMoc + " mốc", "len"));
      on._than.appendChild(ln);
      on._than.appendChild(el("div", "ghi",
        "Bảng trên đo được mô hình bị NÉN VỀ 50% — nói 34% thì thật 13,5%, " +
        "nói 75% thì thật 93%. Phép nắn kéo giãn lại. Nó làm TĂNG lợi thế " +
        "thô chứ không chỉ làm đẹp số: mô hình nén thì tự kéo ước lượng về " +
        "gần giá chợ, và lợi thế teo đúng ở những lần nó tự tin nhất."));
      on._than.appendChild(el("div", "ghi",
        "Giảm chấn " + nl.heSoGiamChan + " vì sổ chỉ lưu TỔNG theo ô nên " +
        "chưa kiểm được ngoài mẫu. Từ nay ghi thêm từng cặp thô; đủ rồi " +
        "mới nói chuyện bỏ giảm chấn. Trần dịch chuyển " +
        so(nl.doiToiDa * 100, 0) + " điểm — khớp hỏng thì cùng lắm lệch chừng ấy."));
    }
    g.appendChild(on);

    var o2 = oKhung("Kết quả", tk.n ? tk.n + " market đã kết toán" : null);
    if (tk.chuaCo || !tk.n) {
      o2._than.appendChild(chuaCo("Chưa market nào kết toán. Mỗi khung 5 phút kết toán một lần sau "
        + "khi hết hạn — con số này chỉ đứng yên khi máy không với tới được sàn."));
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
      // Câu cảnh báo lấy TỪ DỮ LIỆU (`so.dong_canh_bao`), không chép
      // lại ở đây. Bản trước dựng đúng câu ấy bằng JavaScript trong khi
      // Python đã có sẵn một bản — hai bản của một câu thì sớm muộn lệch
      // nhau, và câu này là thứ chặn người đọc hiểu sai con số nguy hiểm
      // nhất trong cả hệ: tỉ lệ thắng.
      if (tk.canhBao) {
        var p = el("p", "ghi");
        p.appendChild(el("b", "xuong", "Đuôi lệch: "));
        p.appendChild(document.createTextNode(tk.canhBao));
        o2._than.appendChild(p);
      }
    }
    g.appendChild(o2);

    var b = T.bang || {};
    // Một con số thì đưa lên ĐẦU khối, đừng nhét vào lưới ba cột. Một ô
    // số đơn độc trong lưới sẽ giãn hết bề ngang với đệm dày — chiếm chỗ
    // như sáu ô mà nói đúng một điều.
    var o3 = oKhung("Băng ghi",
      (b.bat ? "đang ghi" : "TẮT") + " · " +
      (b.soKhung || 0).toLocaleString("vi-VN") + " khung");
    // Báo cáo ĐỌC. Khối trên chỉ nói chuyện GHI, nên trước bản này hai
    // file băng hỏng nằm trên đĩa mà buồng lái vẫn xanh — con số đã được
    // tính rất kỹ trong `BaoCaoDoc` rồi vứt đi.
    // Nút nằm ở MÉP dải vặn: cái mép đang quyết định, không phải dữ liệu.
    // Đã cắn thật — `bienDongCuaSoGiay` có mép trên bằng đúng giá trị đang
    // dùng, nên mọi lượt tiến hoá kết luận "giữ nguyên" nghe như dữ liệu
    // đã nói, thật ra là cái lồng đã nói.
    var mep = T.nutOMep || [];
    if (mep.length) {
      o3._than.appendChild(el("div", "canh",
        mep.length + " nút đang nằm ở MÉP dải vặn — mép đang quyết định, "
        + "không phải dữ liệu: "
        + mep.map(function (x) {
            return x.duong + " = " + x.giaTri + " (mép " + x.ben + " của ["
              + x.thap + ", " + x.cao + "])";
          }).join(" · ")));
    }
    var bd = b.doc;
    if (!bd) {
      // CHƯA ĐO và SẠCH là hai chuyện. Đừng vẽ đèn xanh cho một phép đo
      // chưa từng chạy.
      o3._than.appendChild(el("div", "ghi",
        "Chưa lượt quét băng đầy đủ nào chạy trong phiên này, nên chưa biết "
        + "băng lành hay hỏng. Chạy lại hoặc mở /api/bang thì có số."));
    } else {
      var hong = (bd.soFileHong || 0) > 0;
      var d = el("div", hong ? "canh" : "ghi");
      d.appendChild(el("span", null,
        bd.soFile + " file · " + (bd.soKhung || 0).toLocaleString("vi-VN")
        + " khung đọc được · " + (bd.soFileCutDuoi || 0) + " cụt đuôi"));
      if (hong) {
        // "cụt đuôi" là bình thường sau mỗi lần tắt máy; "đứt giữa" mới là
        // mất dữ liệu. Gộp hai thứ lại thì đèn đỏ vĩnh viễn, rồi người ta
        // thôi nhìn nó — kể cả lần nó đúng.
        d.appendChild(el("div", null,
          "ĐỨT GIỮA " + bd.soFileHong + " file, nhảy qua "
          + (bd.soByteBoQua || 0).toLocaleString("vi-VN") + " byte: "
          + (bd.fileHong || []).join(", ")));
      }
      d.appendChild(el("div", "mo", "đo lúc " + String(bd.luc || "")));
      o3._than.appendChild(d);
    }
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
    // Ví NGÃ phải hiện trước, không thì "trống" đọc thành "chưa tới lượt"
    // trong khi thật ra mọi ví đều hỏng — đúng hình dạng lỗi đã giấu
    // `KeyError: gamma` mấy tiếng.
    var nga = v.nga || {};
    var tenNga = Object.keys(nga);
    if (tenNga.length) {
      o._than.appendChild(el("div", "canh",
        tenNga.length + " ví NGÃ lượt quét vừa rồi — " +
        tenNga.slice(0, 3).map(function (t) { return t + ": " + nga[t]; })
          .join(" · ")));
    }
    if (!v.vi || !v.vi.length) {
      o._than.appendChild(chuaCo(tenNga.length
        ? "Trống vì MỌI ví đều ngã, không phải vì chưa tới lượt. Xem dòng trên."
        : "Chưa quét ví nào. Lượt quét cách nhau 30 phút, nên trống ở đây "
          + "chỉ có nghĩa là chưa tới lượt."));
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
      // Dòng lặp được GỘP ở `kham/bus.py`. Không in số lần thì một câu
      // kêu 78 lần trông y hệt một câu kêu đúng một lần — và chênh giữa
      // hai cái ấy chính là thứ người đọc cần.
      if (e.soLan > 1) {
        r.appendChild(el("span", "lap", "×" + e.soLan
          + (e.tuLuc ? " từ " + String(e.tuLuc).slice(11, 19) : "")));
      }
      d.appendChild(r);
    });
    if (!(T.nhatKy || []).length) d.appendChild(chuaCo("Chưa có dòng nào. Nhật ký ghi từ lúc runtime khởi động, "
        + "nên trống nghĩa là vừa bật chưa lâu."));
    o._than.style.padding = "0";
    o._than.appendChild(d);
    g.appendChild(o);

    /* LÀN NGÃ — đặt TRƯỚC sức khoẻ nguồn vì nó nặng hơn.

       Một lỗi gõ một chữ trong `nguon.tim_theo_slug` từng ném KeyError ở
       làn tìm khung và giết trọn mỗi vòng lặp, suốt nhiều giờ: không ghi
       băng, không kết toán, không lượt tiến hoá nào. Mà bảng vẫn đếm
       `vòng 21590` và vẫn xanh — một cỗ máy chết trông y hệt một cỗ máy
       đang chạy. Ô này là để lần sau nhìn là thấy. */
    var ln = T.lanNga || {};
    var tenLan = Object.keys(ln);
    if (tenLan.length) {
      var oL = oKhung("Làn ngã trong vòng vừa rồi",
        tenLan.length + " làn không chạy được");
      oL._than.appendChild(bang(
        ["làn", "ngã vì"],
        tenLan.map(function (k) {
          return [{ v: k, cls: "t xuong" }, { v: ln[k], cls: "t mo" }];
        })));
      oL._than.appendChild(chuaCo("Các làn KHÁC vẫn chạy — vòng lặp không "
        + "còn chết cả cụm vì một làn. Nhưng làn nào ở đây thì việc của nó "
        + "hôm nay KHÔNG xảy ra: tìm khung ngã là không có cơ hội nào, ghi "
        + "băng ngã là mất dữ liệu đào tạo, tiến hoá ngã là hôm nay không "
        + "học được gì."));
      g.appendChild(oL);
    }

    var n = T.nguon || {};
    var dr = T.duongRa || {};
    var o2 = oKhung("Sức khoẻ nguồn",
      (dr.coProxy ? "qua proxy · " : "") + (dr.moTa || "—"));
    var ks = Object.keys(n);
    if (!ks.length) o2._than.appendChild(chuaCo("Chưa gọi nguồn nào. Bảng này lấp đầy sau nhịp đầu tiên; "
        + "trống quá một phút là dấu hiệu vòng chạy không quay."));
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

  /* ── ĐÀI CHỈ HUY ──────────────────────────────────────────────────
     Một market = MỘT tấm, đọc từ trên xuống là ra quyết định.

     Bảy ô kia mỗi ô là một động cơ, và đó là cách người DỰNG máy nghĩ.
     Người VẬN HÀNH máy thì cần biết "ngay bây giờ, market này, nên làm
     gì" — mà muốn trả lời câu đó bằng bảy ô thì phải bấm bốn tab rồi tự
     nhớ số trong đầu. Tấm này gom đúng đường đi của một quyết định:

         còn bao lâu → đáng giá bao nhiêu → chợ hỏi bao nhiêu
         → ăn được bao nhiêu → đang mang gì → và VÌ VẬY nên làm gì

     Dòng QUYẾT ĐỊNH không nghĩ hộ máy. Nó chỉ đọc lại kết luận máy đã
     có — cầu dao, cửa khung, sàng cơ hội — thành một câu. Nếu nó nói
     khác với các ô bên dưới thì đó là lỗi của tấm này, không phải máy.  */

  function nhipConLai(el, denMs) {
    el.dataset.den = denMs;
    el._ve = function () {
      var s = Math.max(0, (Number(el.dataset.den) - Date.now()) / 1000);
      var p = Math.floor(s / 60), g = Math.floor(s % 60);
      el.textContent = p + ":" + (g < 10 ? "0" : "") + g;
      el.classList.toggle("gap", s <= 30);
    };
    el._ve();
  }

  function hang(nhan, noi) {
    var d = el("div", "hang");
    d.appendChild(el("div", "hnhan", nhan));
    var v = el("div", "hgt");
    (Array.isArray(noi) ? noi : [noi]).forEach(function (x) {
      if (x == null) return;
      v.appendChild(typeof x === "string" ? el("span", "", x) : x);
    });
    d.appendChild(v);
    return d;
  }

  function manh(t, lop) { return el("span", "manh " + (lop || ""), t); }
  function sotv(t, lop) { return el("span", "so " + (lop || ""), t); }

  /* Câu quyết định — đọc lại kết luận của máy, không tự nghĩ thêm. */
  function quyetDinh(m, coHoiTot) {
    var r = T.risk || {}, k = m.khung || {}, c = m.cap || {};
    if (r.ngatKhanCap)
      return { t: "ĐỨNG NGOÀI", v: "cầu dao đang ngắt — " + (r.lyDoNgat || ""), l: "xuong" };
    if (T.tamDung)
      return { t: "ĐỨNG NGOÀI", v: "máy đang tạm dừng", l: "canh" };
    if (k.slug && !k.datCuocDuoc)
      return { t: "ĐỨNG NGOÀI", v: "ngoài cửa đặt cược — đang " + (k.nhan || "?"), l: "mo" };
    if (c.ma && !c.dungDuoc)
      return { t: "ĐỨNG NGOÀI", v: c.lyDo || "sổ chưa dùng được", l: "mo" };
    if (coHoiTot)
      return {
        t: "MUA " + coHoiTot.ben,
        v: (tenChienThuat(coHoiTot.ct) || coHoiTot.ct) + " · ròng " +
           cent(coHoiTot.net) + " · sức chứa " + so(coHoiTot.sucChua, 0) + " cổ",
        l: "len"
      };
    var coMa = (T.coHoi || []).filter(function (x) { return x.ma === m.ma; });
    if (coMa.length)
      return { t: "ĐỨNG NGOÀI", v: "có chênh nhưng không mục nào qua sàng", l: "canh" };
    return { t: "ĐỨNG NGOÀI", v: "chưa thấy cơ hội nào", l: "mo" };
  }

  function tenChienThuat(ma) {
    var c = (T.chienThuat || []).filter(function (x) { return x.ma === ma; })[0];
    return c ? c.ten : null;
  }

  /* ── CHỌN KHUNG ───────────────────────────────────────────────────
     Bốn khung xếp dọc, mỗi thẻ chiếm trọn bề ngang, là cách bày phí chỗ
     nhất có thể: mỗi dòng chỉ dùng chừng một phần tư bề rộng, ba phần tư
     còn lại trống trơn. Và vì thẻ dài nên khung thứ hai đã nằm ngoài màn
     hình — muốn so BTC với ETH thì phải cuộn, tức là phải NHỚ.

     Nay một thẻ hẹp, chọn khung bằng nút. Chỗ dôi ra bên phải để cho các
     khối gập mở ra CẠNH thẻ chứ không phải bên dưới.

     Hàng nút chọn cố ý hiện cả giai đoạn và số giây còn lại của TỪNG
     khung, không chỉ mỗi tên. Chọn mù thì người ta phải bấm từng cái để
     biết cái nào đang trong cửa đặt cược — đúng thứ mà một hàng nút sinh
     ra để khỏi phải làm.                                                */

  var KHUNG = null;                 // mã khung đang xem

  function khungDangTheo() {
    return (T.thiTruong || []).filter(function (x) { return x.theo; });
  }

  function khungHienTai() {
    var ds = khungDangTheo();
    if (!ds.length) return null;
    var m = ds.filter(function (x) { return x.ma === KHUNG; })[0];
    // Khung đang chọn biến mất (đổi cấu hình, hết theo dõi) thì rơi về
    // cái đầu chứ không để trang trống — trống thì trông như hỏng.
    return m || ds[0];
  }

  function veHangChon() {
    var ds = khungDangTheo();
    var h = el("div", "chon-khung");
    ds.forEach(function (m) {
      var k = m.khung || {};
      var b = el("button", "ck" + (m === khungHienTai() ? " chon" : ""));
      b.appendChild(el("b", "", m.ma.replace("_5M", "")));
      var p = el("i", "");
      if (k.datCuocDuoc && k.conLaiGiay != null) {
        var s = Math.max(0, Math.round(k.conLaiGiay));
        p.textContent = Math.floor(s / 60) + ":" + (s % 60 < 10 ? "0" : "") + (s % 60);
        p.className = "dat";
      } else {
        p.textContent = k.nhan || "—";
      }
      b.appendChild(p);
      // Chấm trạng thái: đứng ngoài vì cầu dao/cửa/sổ thì thấy ngay ở đây,
      // khỏi phải bấm vào từng khung mới biết cái nào đang làm việc được.
      var c = (m.cap || {}).dungDuoc ? "ok" : "khong";
      b.appendChild(el("span", "cham " + c));
      b.addEventListener("click", function () { KHUNG = m.ma; ve(); });
      h.appendChild(b);
    });
    return h;
  }

  /* Ô CHI TIẾT theo khung đang chọn; ô TOÀN DANH MỤC thì không.

     Ba ô Đài Chiêm / Sổ Lệnh / Áp Lực Sổ trước đây xếp cả bốn khung
     chồng lên nhau, nên mỗi ô dài gấp bốn và khung thứ hai đã trôi khỏi
     màn hình. Nay chúng bám theo đúng cái nút bạn vừa bấm ở thẻ chỉ huy
     — một lần chọn, mọi ô chi tiết theo.

     Cân Lợi, Kho Đối và Bản Đồ thì KHÔNG bám. Giá trị của ba ô đó chính
     là nhìn cả rổ cùng lúc: một bảng cơ hội chỉ có một khung thì không
     xếp hạng được với gì, và một kho hàng chỉ hiện một khung thì giấu
     mất đúng thứ đáng sợ nhất — bốn khung cùng nghiêng một phía.        */
  function khungDeVe() {
    var m = khungHienTai();
    return m ? [m] : [];
  }

  var SAU = {};              // ô nào đang mở phần sâu, nhớ qua các lần vẽ

  /* Dải ĐỘ TRỄ — một con số cho cả hệ, nên nó đứng trên mọi market.

     Đây là con số mà cả một dòng bot được dựng quanh nó, và được kể lại
     rất khác nhau: một bài lan truyền nói 2.700ms, nghiên cứu OpenMarket
     đo 347ms. Ta không tin bên nào — ta đo, và đo kèm đối chứng ngẫu
     nhiên, vì chờ "giá dịch 0,4 xu" từ một mốc bất kỳ thì bao giờ cũng
     chờ được. Không có đối chứng thì ô này chỉ là một số đẹp. */
  function veDaiTre() {
    var t = T.doTre || {}, n = T.dongNen || {};
    var o = el("div", "tre");

    var trai = el("div", "tre-trai");
    trai.appendChild(el("div", "tre-nhan", "ĐỘ TRỄ ĐO ĐƯỢC"));
    if (t.trungViMs == null) {
      trai.appendChild(el("div", "tre-so mo", "—"));
    } else {
      var v = el("div", "tre-so");
      v.appendChild(el("b", "", so(t.trungViMs, 0)));
      v.appendChild(el("i", "", "ms"));
      trai.appendChild(v);
      if (t.p25Ms != null) {
        trai.appendChild(el("div", "tre-phu",
          so(t.p25Ms, 0) + "–" + so(t.p75Ms, 0) + " ms (tứ phân vị)"));
      }
    }
    o.appendChild(trai);

    var phai = el("div", "tre-phai");
    phai.appendChild(hang("Mẫu", [
      sotv((t.n || 0) + " cú động"),
      manh("phản ứng"), sotv((t.soPhanUng || 0) + " · " + pc(t.tyLePhanUng || 0, 0))
    ]));
    var dc = t.doiChung || {};
    phai.appendChild(hang("Đối chứng", [
      dc.trungViMs == null ? manh("chưa có", "chua")
        : sotv(so(dc.trungViMs, 0) + " ms"),
      manh("mốc rút ngẫu nhiên, cùng quãng")
    ]));
    phai.appendChild(hang("Dòng nền", [
      manh(n.dangNoi ? "Binance WebSocket đã nối" : "CHƯA nối", n.dangNoi ? "len" : "xuong"),
      sotv((n.tinNhan || 0) + " tin"),
      manh("sàn phân giải " + so(t.sanPhanGiaiMs, 0) + " ms")
    ]));
    o.appendChild(phai);

    var kl = el("p", "tre-kl");
    var xau = (t.ketLuan || "").indexOf("tiếng ồn") >= 0;
    kl.className = "tre-kl " + (xau ? "xuong" : (t.trungViMs != null ? "len" : "mo"));
    kl.textContent = t.ketLuan || "chưa đo";
    o.appendChild(kl);
    return o;
  }

  function veChiHuy() {
    var g = document.createDocumentFragment();
    var tt = khungDangTheo();
    if (!tt.length) { g.appendChild(chuaCo("Chưa theo market nào. Bật một khung trong `config.json` "
        + "(`thiTruong[].theo = true`) rồi khởi động lại runtime.")); return g; }
    g.appendChild(veHangChon());

    [khungHienTai()].forEach(function (m) {
      var k = m.khung || {}, q = m.gia, s = m.so || {}, c = m.cap || {};
      var o = el("section", "ch");

      /* ── đỉnh: tên · giai đoạn · ĐỒNG HỒ ─────────────────────── */
      var d = el("div", "ch-dinh");
      d.appendChild(el("b", "", m.ma));
      if (k.nhan) d.appendChild(el("span", "gd gd-" + (k.giaiDoan || ""), k.nhan));
      // Động cơ nào định giá market này. Khi có nhiều họ market thì đây là
      // câu hỏi đầu tiên lúc một con số trông lạ: sai số, hay là mình đang
      // đọc kết quả của một mô hình khác với mô hình mình tưởng?
      if (m.dongCo) {
        var hs = (T.dongCo || []).filter(function (x) { return x.ma === m.dongCo; })[0];
        var dc = el("span", "dcm", hs ? hs.ten : m.dongCo);
        dc.title = hs ? hs.mota : m.dongCo;
        d.appendChild(dc);
      }
      // Đồng hồ ĐỔI MỐC theo giai đoạn, vì hai giai đoạn hỏi hai câu khác
      // nhau. Trong cửa đặt cược, câu hỏi là "còn bao lâu để vào lệnh".
      // Qua cửa rồi thì `conLaiGiay` bằng 0 mãi mãi, và một số 0 đỏ đứng
      // yên chẳng nói gì; lúc đó câu hỏi đúng là "còn bao lâu tới kết toán".
      //
      // Dùng thẳng mốc tuyệt đối của sàn được, vì buồng lái chỉ chạy trên
      // localhost — trang và runtime dùng CHUNG một đồng hồ máy.
      var oh = el("div", "ch-ho");
      if (k.datCuocDuoc && k.conLaiGiay != null) {
        oh.appendChild(el("i", "", "còn đặt được"));
        var dh = el("b", "dhho");
        nhipConLai(dh, Date.now() + k.conLaiGiay * 1000);
        oh.appendChild(dh);
      } else if (k.endMs) {
        oh.appendChild(el("i", "", "còn tới kết toán"));
        var dh2 = el("b", "dhho cho");
        nhipConLai(dh2, k.endMs);
        oh.appendChild(dh2);
      } else oh.appendChild(el("i", "", "chưa rõ khung"));
      d.appendChild(oh);
      o.appendChild(d);

      /* thanh vòng đời — thứ mà market 5 phút cần nhất */
      if (k.troiQuaPct != null) {
        var vd = el("div", "vdoi");
        var ch = el("div", "vdoi-c"); ch.style.width = Math.min(100, k.troiQuaPct) + "%";
        vd.appendChild(ch);
        o.appendChild(vd);
      }

      var b = el("div", "ch-than");

      /* ── tham chiếu ───────────────────────────────────────────── */
      if (m.giaNen != null || (q && q.z != null)) {
        b.appendChild(hang("Tham chiếu", [
          m.giaNen != null ? sotv("$" + so(m.giaNen, 2)) : null,
          q ? manh("z " + (q.z >= 0 ? "+" : "") + so(q.z, 2)) : null,
          q ? manh("σ " + (q.sigmaGiay * 1e5).toFixed(2) + "e-5/giây") : null
        ]));
      }

      /* ── giá trị thật ─────────────────────────────────────────── */
      if (!q) {
        b.appendChild(hang("Giá trị thật", manh("chưa đủ mẫu để ước lượng σ", "chua")));
      } else {
        b.appendChild(hang("Giá trị thật", [
          sotv("UP " + pc(q.pUp), q.roRang ? "saoc" : "mo"),
          sotv("DOWN " + pc(q.pDown), "mo"),
          manh("± " + so(q.batDinh * 100, 1) + " điểm"),
          q.roRang ? null : manh("mô hình tự nhận KHÔNG rõ ràng", "canh")
        ]));
      }

      /* ── chợ ──────────────────────────────────────────────────── */
      // Thang chờ thì KHÔNG hiện giá. Một dải lệnh trải 0,001→0,999 vẫn
      // có "best ask", và con số đó vẫn ra số — nhưng nó không phải báo
      // giá của ai cả. Bày nó ở dòng CHỢ là làm đúng cái việc mà cả cỗ
      // máy bên dưới được dựng để từ chối làm.
      // Cổng đúng là `dungDuoc`, KHÔNG phải `thangCho`. Hai cờ này ở cấp
      // cặp đều là phép HOẶC của hai token, nên chúng nói hai chuyện khác
      // hẳn nhau: `thangCho` = một trong hai bên là thang, `dungDuoc` =
      // một trong hai bên dùng được. Một cặp có thể vừa có thang ở bên
      // này vừa có báo giá thật ở bên kia — và đó là trường hợp THƯỜNG,
      // không phải ngoại lệ. Chặn nhầm sang `thangCho` là giấu mất báo
      // giá thật của bên còn lại.
      if (!c.dungDuoc) {
        b.appendChild(hang("Chợ", manh(c.lyDo || "sổ chưa dùng được", "canh")));
      } else {
        var cho = [];
        ["UP", "DOWN"].forEach(function (ben) {
          var x = s[ben];
          if (!x) return;
          if (x.thangCho) { cho.push(manh(ben + " thang chờ", "canh")); return; }
          if (x.bestAsk != null) cho.push(sotv(ben + " hỏi " + gia(x.bestAsk)));
          if (x.spread != null) cho.push(manh("spread " + gia(x.spread)));
        });
        b.appendChild(hang("Chợ", cho.length ? cho : manh("chưa có báo giá", "chua")));
      }

      /* giá cặp — và nói thẳng khi nó ở SAI phía của $1 */
      if (c.tongGiaMua != null && c.dungDuoc) {
        var duoi1 = c.tongGiaMua < 1;
        b.appendChild(hang("Giá cặp", [
          sotv(gia(c.tongGiaMua), duoi1 ? "len" : "xuong"),
          manh(duoi1
            ? "dưới $1 — mua đủ cặp là khoá lãi"
            : "TRÊN $1 — mua đủ cặp là khoá LỖ, không phải cơ hội",
            duoi1 ? "len" : "xuong")
        ]));
      }

      /* ── lợi thế ăn được ──────────────────────────────────────── */
      var ch2 = (T.coHoi || []).filter(function (x) { return x.ma === m.ma; });
      var tot = ch2.filter(function (x) { return x.dangLam; })
                   .sort(function (a, z) { return z.net - a.net; })[0];
      var hien = tot || ch2.sort(function (a, z) { return z.net - a.net; })[0];
      if (!hien) {
        b.appendChild(hang("Lợi thế", manh("không mục nào", "chua")));
      } else {
        b.appendChild(hang("Lợi thế " + hien.ben, [
          manh("thô"), sotv(cent(hien.gross)),
          manh("ròng"), sotv(cent(hien.net), hien.net > 0 ? "len" : "xuong"),
          hien.dangLam ? null : manh("KHÔNG qua sàng", "canh")
        ]));
        b.appendChild(hang("", [
          manh("sức chứa"), sotv(so(hien.sucChua, 0) + " cổ"),
          manh("khớp"), sotv(pc(hien.xacSuatKhop)),
          manh("nửa đời"), sotv(so(hien.nuaDoiMs, 0) + "ms")
        ]));
      }

      /* ── tồn kho ──────────────────────────────────────────────── */
      var v = ((T.kho || {}).viThe || []).filter(function (x) { return x.ma === m.ma; })[0];
      if (!v || (!v.coUp && !v.coDown)) {
        b.appendChild(hang("Tồn kho", manh("chưa có vị thế", "chua")));
      } else {
        b.appendChild(hang("Tồn kho", [
          sotv("UP " + so(v.coUp, 0)), sotv("DOWN " + so(v.coDown, 0)),
          manh("cặp"), sotv(so(v.daGhepCap, 0)),
          manh("lệch"), sotv((v.dinhHuong >= 0 ? "+" : "") + so(v.dinhHuong, 0)),
          v.giaCap != null ? manh("giá cặp " + gia(v.giaCap),
            v.capKhoaLo ? "xuong" : "len") : null
        ]));
        if (v.chuaPhongHoUsd > 0) {
          b.appendChild(hang("", manh(
            "chưa phòng hộ " + usd(v.chuaPhongHoUsd) + " · chờ " +
            so(v.choLauNhatMs / 1000, 0) + "s — đây LÀ vị thế định hướng, " +
            "chưa phải cặp khoá", "canh")));
        }
        // `quyetChan` được tính mỗi vòng và gửi cả lên ảnh chụp công
        // khai, mà trước bản này KHÔNG nơi nào vẽ ra — một phép tính đi
        // suốt đường ống rồi chết ở cuối. Hiện nó ra, kèm nhãn LỜI
        // KHUYÊN: bot không tự làm việc này, và người đọc phải biết thế.
        var qc = (T.quyetChan || {})[v.ma];
        if (qc && qc.loi) {
          b.appendChild(hang("", manh(
            "khuyên: " + qc.loi + (qc.ben ? " " + qc.ben : "") +
            (qc.soCo ? " " + so(qc.soCo, 0) + " cổ" : "") +
            " — LỜI KHUYÊN, bot KHÔNG tự làm" +
            (qc.lyDo && qc.lyDo.length ? " (" + qc.lyDo.join("; ") + ")" : ""),
            "mo")));
        }
      }

      /* ── rủi ro ───────────────────────────────────────────────── */
      var r = T.risk || {};
      var tenCu = null, cu = 0;
      Object.keys(T.nguon || {}).forEach(function (n) {
        var t = (T.nguon[n] || {}).tuoiMs || 0;
        if (t > cu) { cu = t; tenCu = n; }
      });
      b.appendChild(hang("Rủi ro", [
        manh("vốn"), sotv(usd(r.von)),
        manh("lỗ ngày"), sotv(usd(r.loNgayUsd) + "/" + usd(r.tranLoNgayUsd),
          r.loNgayUsd >= r.tranLoNgayUsd * 0.8 ? "xuong" : ""),
        manh("cũ nhất " + (tenCu || "—")),
        sotv(so(cu / 1000, 1) + "s", cu > 60000 ? "canh" : "len")
      ]));

      /* ── quyết định ───────────────────────────────────────────── */
      var qd = quyetDinh(m, tot);
      var oq = el("div", "qd qd-" + qd.l);
      oq.appendChild(el("b", "", qd.t));
      oq.appendChild(el("span", "", qd.v));
      b.appendChild(oq);

      /* ── sâu hơn ──────────────────────────────────────────────── */
      var nut = el("button", "sau-nut", "Sâu hơn ▾");
      var sau = el("div", "sau");
      //  dựng lại cả trang mỗi 2 giây. Không nhớ trạng thái thì
      // nút này tự đóng ngay khi người ta vừa mở ra đọc — một lỗi chỉ
      // lộ khi dùng thật, không lộ khi xem ảnh chụp.
      sau.hidden = !SAU[m.ma];
      nut.addEventListener("click", function () {
        sau.hidden = !sau.hidden;
        SAU[m.ma] = !sau.hidden;
        nut.textContent = sau.hidden ? "Sâu hơn ▾" : "Thu lại ▴";
        if (!sau._daVe) { sau.appendChild(veSauHon(m)); sau._daVe = true; }
      });
      b.appendChild(nut); b.appendChild(sau);

      o.appendChild(b);
      g.appendChild(o);
    });
    return g;
  }

  /* Phần sâu — đúng những thứ tệp gọi là ADVANCED. Không hiện mặc định,
     vì chín trên mười lần người mở buồng lái chỉ cần bảy dòng phía trên. */
  function veSauHon(m) {
    var g = document.createDocumentFragment();
    var q = m.gia, s = m.so || {}, c = m.cap || {};

    if (q) {
      var l = el("div", "luoi3");
      l.appendChild(chi("Rủi ro nhảy", so(q.ruiRoNhay * 100, 1) + " điểm",
        "tham số " + so(q.batDinhThamSo * 100, 1), q.ruiRoNhay > 0.12 ? "xuong" : "mo"));
      l.appendChild(chi("τ", so(q.tauGiay, 0) + "s", q.tauDungSan ? "đã kẹp về sàn" : null,
        q.tauDungSan ? "canh" : ""));
      l.appendChild(chi("Làm phẳng", q.daMatPhang ? "CÓ" : "không",
        q.daMatPhang ? "công thức trần cho 0/1" : null, q.daMatPhang ? "canh" : "mo"));
      g.appendChild(l);
    }

    if (c.lechSoiGuong != null) {
      g.appendChild(el("div", "ghi",
        "Lệch soi gương " + so(c.lechSoiGuong, 6) + " — mua UP ≡ bán DOWN, nên hai " +
        "sổ phải soi gương qua 0,5. Số này lệch nhiều là một trong hai sổ đã cũ."));
    }

    ["UP", "DOWN"].forEach(function (ben) {
      var x = s[ben];
      if (!x) return;
      var r = el("div", "ghi");
      r.innerHTML = "<b>" + ben + "</b> · vi giá " + cent(x.viGia) +
        " · lệch " + so(x.lech, 3) +
        (x.doSau ? " · sâu " + x.doSau.map(function (y) { return so(y, 0); }).join(" / ") : "") +
        (x.thangCho ? " · <b>thang chờ</b>, chưa phải báo giá" : "");
      g.appendChild(r);
    });

    var gt = q && q.giaiTrinh;
    if (gt && gt.chiTiet && gt.chiTiet.length) {
      g.appendChild(el("div", "ghi",
        "Tín hiệu phụ — gộp " + gt.soHo + " họ, không phải " +
        gt.chiTiet.length + " bằng chứng độc lập:"));
      g.appendChild(bang(
        ["tín hiệu", "họ", { t: "thô", num: 1 }, { t: "trọng số", num: 1 }, { t: "góp", num: 1 }],
        gt.chiTiet.map(function (x) {
          return [{ v: x.ten, cls: "t" }, { v: x.ho, cls: "t" },
                  { v: (x.tho >= 0 ? "+" : "") + so(x.tho, 3), cls: "num" },
                  { v: "×" + so(x.trongSo, 2), cls: "num" },
                  { v: (x.gop >= 0 ? "+" : "") + so(x.gop, 3), cls: "num" }];
        })));
    }
    return g;
  }

  /* ── BẢN ĐỒ ───────────────────────────────────────────────────────
     Đây là bản có nghĩa của thứ mà các dashboard kia gọi là "Edge
     Matrix" hay "force graph": so mỗi khung với CHÍNH giá trị thật của
     nó, không bao giờ so giá thô giữa hai khung. BTC 5m ở 68¢ và BTC
     15m ở 54¢ không nói lên điều gì — hai khung khác mốc, khác thời
     gian còn lại, khác chân trời biến động.                            */
  function veBanDo() {
    var g = document.createDocumentFragment();
    var d = T.doThi || {};
    var o = oKhung("Bản đồ khung", d.soNut ? d.soNut + " nút" : null);

    if (!d.nut || !d.nut.length) {
      o._than.appendChild(chuaCo("Chưa có khung nào để so. Bản đồ cần ít nhất hai khung định giá "
        + "được cùng lúc — một khung thì không có gì để so với gì."));
      g.appendChild(o); return g;
    }

    if (d.canhBaoDongPha) {
      var w = el("p", "ghi canh");
      w.innerHTML = "<b>Cả rổ đang nghiêng một phía.</b> " + d.canhBaoDongPha +
        " — khi mọi khung cùng lệch một hướng thì lời giải thích đơn giản " +
        "nhất là MÔ HÌNH đang lệch, không phải cả chợ cùng sai.";
      o._than.appendChild(w);
    }

    o._than.appendChild(bang(
      ["khung", "nhóm", { t: "còn (s)", num: 1 }, { t: "thật", num: 1 },
       { t: "chợ", num: 1 }, { t: "lệch", num: 1 }, { t: "z riêng", num: 1 }],
      d.nut.slice().sort(function (a, b) { return Math.abs(b.z) - Math.abs(a.z); })
        .map(function (n) {
          return [{ v: n.ma, cls: "t" }, { v: n.nhom, cls: "t" },
                  { v: so(n.conLaiGiay, 0), cls: "num" },
                  { v: pc(n.fairUp), cls: "num" },
                  { v: n.giaChoUp == null ? "—" : cent(n.giaChoUp), cls: "num" },
                  { v: cent(n.lech), cls: "num " + huong(n.lech) },
                  { v: (n.z >= 0 ? "+" : "") + so(n.z, 2), cls: "num" }];
        })));

    o._than.appendChild(el("div", "ghi",
      "Cột z riêng = lệch chia cho bất định của CHÍNH khung đó. Đó là lý " +
      "do cột này so được với nhau còn cột giá chợ thì không: một khung " +
      "còn 20 giây và một khung còn 800 giây không cùng thước đo."));

    if (d.zTrungBinh != null) {
      o._than.appendChild(el("div", "ghi",
        "z trung bình " + so(d.zTrungBinh, 2) + " — con số này ở xa 0 nghĩa " +
        "là mô hình đang lệch có hệ thống so với chợ, và đó là tin về mô " +
        "hình trước khi là tin về cơ hội."));
    }
    g.appendChild(o);
    return g;
  }

  /* ── KẾT TOÁN ─────────────────────────────────────────────────────
     Vòng học chỉ khép khi biết kết quả THẬT. Ô này là chỗ duy nhất
     trong buồng lái nói được "mô hình đoán đúng hay sai", nên nó cũng
     là chỗ duy nhất chứng minh cả cỗ máy có đang học hay không.        */
  function veKetToan() {
    var g = document.createDocumentFragment();
    var kt = T.ketToan || {}, vd = T.voDich || {}, th = T.tienHoa || {};

    var kq = T.soKetQua || {};
    var o = oKhung("Kết toán", (kt.daKetToan || 0) + " xong · " +
      (kt.dangCho || 0) + " chờ" +
      (kq.soSlug ? " · sổ kết quả " + kq.soSlug + " khung" : ""));
    if (kq.soSlug) {
      o._than.appendChild(el("div", "ghi",
        "Sổ kết quả có " + kq.soSlug + " khung (" + kq.soUp + " UP / " +
        kq.soDown + " DOWN" + (kq.soBatDong ? ", " + kq.soBatDong +
        " BẤT ĐỒNG" : "") + "). Đây là thứ cho phép chạy lại CHẤM ĐƯỢC " +
        "điểm — băng ghi khung hình lúc nó đang diễn ra nên không thể tự " +
        "chứa kết quả, và trước khi có sổ này thì cỗ máy chạy lại chưa " +
        "từng chấm được một khung nào."));
      // NGUỒN của sự thật, không chỉ số lượng. 100% `tu-tinh` nghĩa là
      // mọi điểm Brier, mọi điểm kỹ năng, cả vòng tiến hoá đều đứng trên
      // một sự thật do chính mình tính ra — chưa dòng nào sàn xác nhận.
      if (kq.soTheoSan != null) {
        var het = kq.soTheoSan === 0;
        o._than.appendChild(el("div", het ? "canh" : "ghi",
          "Nguồn: " + kq.soTheoSan + " do SÀN xác nhận · " +
          (kq.soTuTinh || 0) + " tự tính từ giá Binance." +
          (het ? " CHƯA MỘT DÒNG NÀO được sàn xác nhận — mọi điểm chấm "
               + "đứng trên sự thật do chính mình tính ra. Phép tính ấy đơn "
               + "giản và gần như chắc đúng, nhưng 'gần như chắc đúng' "
               + "không phải 'đã đối chiếu'." : "")));
      }
    }
    if (kt.soBatDong) {
      var w = el("p", "ghi xuong");
      w.innerHTML = "<b>" + kt.soBatDong + " lần hai nguồn BẤT ĐỒNG.</b> " +
        "Kết quả đọc bằng hai đường độc lập — outcomePrices của sàn và tự " +
        "tính từ nến Binance. Bất đồng tăng nghĩa là một giả định đang sai, " +
        "và nhờ đọc hai đường nên nó lộ ra ở đây chứ không lộ thành tiền.";
      o._than.appendChild(w);
    } else {
      o._than.appendChild(el("div", "ghi",
        "Hai nguồn đọc kết quả chưa lần nào bất đồng. Đọc bằng hai đường " +
        "độc lập là để một giả định sai lộ ra thành con số này, không lộ " +
        "thành tiền."));
    }

    if (kt.cho && kt.cho.length) {
      o._than.appendChild(bang(
        ["đang chờ", { t: "còn (s)", num: 1 }, { t: "đã đoán", num: 1 }, { t: "hỏi", num: 1 }],
        kt.cho.map(function (x) {
          return [{ v: x.slug.replace(/^.*?-5m-/, ""), cls: "t" },
                  { v: so(x.conMs / 1000, 0), cls: "num" },
                  { v: pc(x.pDuDoan), cls: "num" },
                  { v: x.soLanHoi, cls: "num" }];
        })));
    }
    if (kt.ganDay && kt.ganDay.length) {
      o._than.appendChild(bang(
        ["đã xong", "kết quả", { t: "đã đoán", num: 1 }, "có vị thế"],
        kt.ganDay.slice(0, 12).map(function (x) {
          return [{ v: x.ma + " " + (x.luc || "").slice(11, 16), cls: "t" },
                  { v: x.upThang ? "UP" : "DOWN", cls: "t " + (x.upThang ? "len" : "xuong") },
                  { v: pc(x.pDuDoan), cls: "num" },
                  { v: x.coViThe ? "có" : "không", cls: "t mo" }];
        })));
      o._than.appendChild(el("div", "ghi",
        "Mọi khung đều được ghi sổ, kể cả khung KHÔNG có vị thế. Chỉ chấm " +
        "những khung mình có tiền là tự chọn mẫu — hiệu chỉnh sẽ đẹp lên " +
        "mà không phải vì mô hình khá hơn."));
    }
    g.appendChild(o);

    /* Vô địch / thách đấu */
    var o2 = oKhung("Vô địch · thách đấu",
      (vd.hoSo && vd.hoSo.length) ? vd.hoSo.length + " hồ sơ" : null);
    var ng = vd.nguong || {};
    o2._than.appendChild(el("div", "ghi",
      "Bốn cửa đặt TRƯỚC khi nhìn số: tối thiểu " + (ng.toiThieuMau || "—") +
      " mẫu, phải hơn đương kim " + (ng.bienVuot || "—") + " lần, và đuôi " +
      "không tệ hơn " + (ng.duoiToiDa || "—") + " lần. Không có cờ ép qua."));
    if (!vd.hoSo || !vd.hoSo.length) {
      o2._than.appendChild(chuaCo(
        "Chưa có thách đấu nào. Cần đủ mẫu kết toán trước khi so hai bộ " +
        "tham số — so trên vài chục lượt là so tiếng ồn."));
    } else {
      o2._than.appendChild(bang(
        ["chiến thuật", { t: "mẫu", num: 1 }, { t: "kỳ vọng", num: 1 }, "trạng thái"],
        vd.hoSo.map(function (h) {
          return [{ v: h.ma || "?", cls: "t" },
                  { v: h.mau == null ? "—" : h.mau, cls: "num" },
                  { v: h.kyVong == null ? "—" : so(h.kyVong, 4), cls: "num" },
                  { v: h.trangThai || "—", cls: "t" }];
        })));
    }
    g.appendChild(o2);

    /* Vòng tiến hoá */
    var dd = th.duong || {}, gn = th.ganNhat || {};
    var o3 = oKhung("Vòng tiến hoá", th.bat ? "bật · sau " +
      String(th.gioUTC).padStart(2, "0") + ":00 UTC mỗi ngày" : "tắt");
    var l = el("div", "luoi3");
    l.appendChild(chi("Lượt", dd.soLuot != null ? dd.soLuot : "—", "đã chạy"));
    l.appendChild(chi("Nhận", dd.soLanNhan != null ? dd.soLanNhan : "—",
      "qua cổng", dd.soLanNhan ? "len" : "mo"));
    l.appendChild(chi("Trả lại", dd.soLanTraLai != null ? dd.soLanTraLai : "—",
      "cổng chặn", "mo"));
    l.appendChild(chi("Đứng yên", dd.soLanDungYen != null ? dd.soLanDungYen : "—",
      "không bệnh nào vượt ngưỡng", "mo"));
    o3._than.appendChild(l);
    if (th.ngayDaChay) {
      o3._than.appendChild(el("div", "ghi", "Lượt gần nhất " + th.ngayDaChay +
        (gn.tomTat ? " — " + gn.tomTat : "") + "."));
    }
    o3._than.appendChild(el("div", "ghi",
      "Ba kết cục đều hợp lệ. TRẢ LẠI nghĩa là cổng làm đúng việc của nó; " +
      "ĐỨNG YÊN nghĩa là chưa bệnh nào đủ nặng để đáng vặn. Một vòng nhận " +
      "mọi đề xuất là một vòng không có cổng."));
    g.appendChild(o3);
    return g;
  }

  /* ── ÁP LỰC SỔ ────────────────────────────────────────────────────
     Nhiệt đồ sổ lệnh theo thời gian. Đây là bản CÓ DỮ LIỆU THẬT của thứ
     mà các dashboard kia đặt tên "book membrane" hay "pressure field".

     Một thang giá đứng yên chỉ nói được sổ ĐANG thế nào. Cái đắt hơn là
     sổ ĐANG ĐỔI thế nào: tường dày rồi biến mất, báo giá đứng im trong
     lúc giá nền chạy, thanh khoản rút sạch trước giờ kết toán. Ba thứ
     đó chỉ hiện ra khi xếp nhiều lát sổ cạnh nhau theo trục thời gian.

     Trục dọc là CẢ dải 0→1, cố ý. Nhờ vậy thang chờ tự lộ ra bằng mắt:
     một báo giá thật là một vệt hẹp bám quanh giữa, còn thang chờ là
     một cột phủ kín từ đáy lên đỉnh. Không cần đọc số cũng thấy.

     Lịch sử gom NGAY TRONG TRANG, từ lúc mở. Không đọc băng của runtime
     — băng là để chạy lại và kết toán, và nối buồng lái vào đó sẽ biến
     một trang chỉ-để-xem thành một đường phụ thuộc nữa. Đổi lại: đóng
     tab là mất, và ô này nói thẳng điều đó chứ không giả vờ có sẵn.     */

  var LICH = {};                    // ma → [{t, bid, ask, giua}], mới ở cuối
  var LICH_TOI_DA = 180;            // 180 × 2s ≈ 6 phút, hơn một khung 5m

  function ghiLich(d) {
    (d.thiTruong || []).forEach(function (m) {
      if (!m.theo) return;
      var s = (m.so || {}).UP;
      if (!s) return;
      var a = LICH[m.ma] || (LICH[m.ma] = []);
      a.push({
        t: Date.now(),
        bid: (s.bid || []).map(function (x) { return [x.gia, x.luong]; }),
        ask: (s.ask || []).map(function (x) { return [x.gia, x.luong]; }),
        giua: (s.bestBid != null && s.bestAsk != null)
          ? (s.bestBid + s.bestAsk) / 2 : null,
        thang: !!s.thangCho
      });
      if (a.length > LICH_TOI_DA) a.splice(0, a.length - LICH_TOI_DA);
    });
  }

  var CAO = 132, ROW = 100;         // 100 hàng, mỗi hàng 1 xu
  var RONG_COT = 3;

  function veNhietDo(lich) {
    var c = document.createElement("canvas");
    // Rộng theo SỐ LÁT ĐANG CÓ, không theo sức chứa tối đa. Bản đầu lấy
    // `LICH_TOI_DA * RONG_COT` rồi vẽ dồn về mép phải, nên lúc mới mở
    // trang có 28 lát mà canvas rộng cho 180 — bốn phần năm là khoảng
    // trống, và nó trông y hệt "không có dữ liệu".
    c.width = lich.length * RONG_COT;   // vừa khít, không chừa mép trống
    c.height = CAO;
    c.className = "nhiet";
    // Bộ kiểm chạy trong DOM giả, không có ngữ cảnh vẽ. Bỏ qua phần vẽ
    // chứ đừng ném — mất một biểu đồ thì vẫn đọc được cả trang.
    var g = c.getContext && c.getContext("2d");
    if (!g) return c;

    g.fillStyle = "#07090D";
    g.fillRect(0, 0, c.width, c.height);

    // Chuẩn hoá theo lượng LỚN NHẤT đang thấy. Thang tuyệt đối thì một
    // tường 50.000 cổ sẽ dìm mọi thứ còn lại xuống đen thui.
    var max = 0;
    lich.forEach(function (l) {
      l.bid.concat(l.ask).forEach(function (m) { if (m[1] > max) max = m[1]; });
    });
    if (max <= 0) return c;
    var lgMax = Math.log1p(max);

    var x0 = 0;                 // canvas vừa khít nên vẽ từ mép trái
    lich.forEach(function (l, i) {
      var x = x0 + i * RONG_COT;
      function cham(muc, r, gg, b) {
        muc.forEach(function (m) {
          var hang = Math.min(ROW - 1, Math.max(0, Math.floor(m[0] * ROW)));
          var y = CAO - (hang + 1) * (CAO / ROW);
          var a = Math.log1p(m[1]) / lgMax;
          g.fillStyle = "rgba(" + r + "," + gg + "," + b + "," + (0.12 + a * 0.88) + ")";
          g.fillRect(x, y, RONG_COT, CAO / ROW);
        });
      }
      cham(l.bid, 78, 203, 142);     // mua — xanh lá
      cham(l.ask, 232, 99, 90);      // bán — đỏ
    });

    // Vạch giữa. Vẽ SAU để không bị thang giá đè mất.
    g.strokeStyle = "rgba(127,178,232,.85)";
    g.lineWidth = 1.2;
    g.beginPath();
    var daBatDau = false;
    lich.forEach(function (l, i) {
      if (l.giua == null) { daBatDau = false; return; }
      var x = x0 + i * RONG_COT + RONG_COT / 2;
      var y = CAO - l.giua * CAO;
      if (daBatDau) g.lineTo(x, y); else { g.moveTo(x, y); daBatDau = true; }
    });
    g.stroke();

    // Mốc 50¢ — biên giới của một thị trường nhị phân.
    g.strokeStyle = "rgba(133,146,166,.35)";
    g.setLineDash([3, 4]); g.lineWidth = 1;
    g.beginPath(); g.moveTo(0, CAO / 2); g.lineTo(c.width, CAO / 2); g.stroke();
    g.setLineDash([]);
    return c;
  }

  function veApLuc() {
    var g = document.createDocumentFragment();
    var tt = khungDeVe();
    if (!tt.length) { g.appendChild(chuaCo("Chưa theo market nào. Bật một khung trong `config.json` "
        + "(`thiTruong[].theo = true`) rồi khởi động lại runtime.")); return g; }

    tt.forEach(function (m) {
      var lich = LICH[m.ma] || [];
      var o = oKhung("Áp lực sổ · " + m.ma,
        lich.length ? lich.length + " lát · " +
          so((lich[lich.length - 1].t - lich[0].t) / 1000, 0) + "s" : null);

      if (lich.length < 3) {
        o._than.appendChild(chuaCo(
          "Đang gom lát cắt. Ô này dựng lịch sử NGAY TRONG TRANG từ lúc " +
          "bạn mở, mỗi 2 giây một lát — nên vài chục giây nữa mới có hình, " +
          "và đóng tab là mất. Cố ý không đọc băng của runtime: băng để " +
          "chạy lại và kết toán, nối buồng lái vào đó là thêm một đường " +
          "phụ thuộc cho một trang chỉ để xem."));
        g.appendChild(o); return;
      }

      var boc = el("div", "nhiet-boc");
      boc.appendChild(veNhietDo(lich));
      var truc = el("div", "nhiet-truc");
      ["100¢", "75¢", "50¢", "25¢", "0¢"].forEach(function (t) {
        truc.appendChild(el("span", "", t));
      });
      boc.appendChild(truc);
      o._than.appendChild(boc);

      var soThang = lich.filter(function (l) { return l.thang; }).length;
      var pctThang = soThang / lich.length;
      o._than.appendChild(el("div", "ghi",
        "Xanh lá = lệnh mua, đỏ = lệnh bán, đậm theo lượng (thang log). " +
        "Vạch xanh dương = giữa hai giá tốt nhất. Trục dọc là CẢ dải 0→1."));

      if (pctThang > 0.02) {
        var w = el("p", "ghi canh");
        w.innerHTML = "<b>" + pc(pctThang, 0) + " số lát là thang chờ.</b> " +
          "Nhìn hình sẽ thấy chúng ngay: một cột phủ kín từ đáy lên đỉnh. " +
          "Báo giá thật là một vệt hẹp bám quanh vạch giữa. Đó là lý do " +
          "trục dọc để cả dải chứ không cắt quanh giá — cắt đi thì thang " +
          "chờ trông y hệt một sổ dày.";
        o._than.appendChild(w);
      } else {
        o._than.appendChild(el("div", "ghi",
          "Không lát nào là thang chờ trong quãng này — sổ đang yết giá thật."));
      }
      g.appendChild(o);
    });
    return g;
  }

  /* ── MỘT TRANG ────────────────────────────────────────────────────
     Mười hai ô cũ đều phục vụ đúng MỘT họ market. Chúng nằm cạnh nhau
     trên một thanh tab, nên nhìn thì tưởng là mười hai thứ ngang hàng —
     trong khi thật ra chúng là mười hai lát cắt của cùng một thứ.

     Chuyện đó không sao khi chỉ có crypto. Nó vỡ ngay khi có họ thứ hai:
     thời tiết cũng cần sổ lệnh, cũng cần cân lợi, cũng cần kho đối, cũng
     cần kết toán. Hai mươi bốn tab. Rồi ba mươi sáu.

     Nên thanh trên cùng phải là cấp CHUYÊN MỤC, không phải cấp ô. Mỗi
     chuyên mục là MỘT trang cuộn, các ô thành khối gập được trong đó.

     Ba luật của trang này:

     1. Thứ luôn mở là thứ trả lời được câu "ngay bây giờ nên làm gì" —
        độ trễ của cả hệ, rồi một tấm cho mỗi market. Đúng những gì người
        vận hành cần khi liếc màn hình một cái.
     2. Mọi khối khác gập lại, và **chỉ VẼ khi đang mở**. Trang tự dựng
        lại mỗi 2 giây; vẽ cả mười khối mỗi lần là trả giá cho thứ không
        ai nhìn.
     3. Trạng thái gập nhớ ngoài DOM. Không nhớ thì nó tự đóng ngay khi
        người ta vừa mở ra đọc — lỗi chỉ lộ khi dùng thật.                */


  /* MỌI Ô ĐỀU MỞ. Không còn cơ chế gập.

     Gập chỉ đáng khi trang dài hơn thứ người ta cần nhìn. Ở một buồng
     lái thì ngược lại: mỗi ô là một mặt của cùng một câu hỏi, và thứ
     phải bấm mới thấy là thứ trên thực tế không được nhìn.

     Việc còn lại là xếp cho mỗi ô đúng bề ngang nó CẦN, chứ không phải
     bề ngang nó được phát. `rong: 1` = trọn hàng, và mỗi lần dùng đều
     có lý do riêng ghi ngay cạnh.                                      */
  var O_LIST = [
    // Thứ tự đọc theo CỘT: trên xuống ở cột một, rồi sang cột hai. Nên
    // xếp theo mức thường xuyên phải liếc, không theo nhóm chủ đề.
    { ma: "dai-chiem", ten: "Đài Chiêm", phu: "mô hình định giá", theoKhung: 1 },
    { ma: "so-lenh", ten: "Sổ Lệnh", phu: "sổ L2 hai bên", theoKhung: 1 },
    { ma: "can-loi", ten: "Cân Lợi", phu: "lợi thế sau mọi khoản trừ", caRo: 1 },
    { ma: "ap-luc", ten: "Áp Lực Sổ", phu: "nhiệt đồ theo thời gian", theoKhung: 1 },
    { ma: "kho-doi", ten: "Kho Đối", phu: "tồn kho, cặp, chân lẻ", caRo: 1 },
    { ma: "ban-do", ten: "Bản Đồ", phu: "so các khung với nhau", caRo: 1 },
    { ma: "chien-thuat", ten: "Chiến Thuật", phu: "sáu ngón, bật tắt được" },
    { ma: "truong-thi", ten: "Trường Thi", phu: "hiệu chỉnh, kỳ vọng, đuôi" },
    { ma: "ket-toan", ten: "Kết Toán", phu: "vòng học, vô địch, tiến hoá" },
    { ma: "quan-vi", ten: "Đài Quan Ví", phu: "ví khác đang làm gì" },
    { ma: "nhat-ky", ten: "Nhật Ký", phu: "dòng sự kiện, sức khoẻ nguồn" },
  ];


  function veOMo(k) {
    var o = el("section", "gop mo");
    o.id = "o-" + k.ma;
    var d = el("div", "gop-dinh tinh");
    d.appendChild(el("span", "gop-ten", k.ten));
    d.appendChild(el("span", "gop-phu", k.phu));
    if (k.theoKhung) {
      var m = khungHienTai();
      d.appendChild(el("span", "gop-pham vi-khung", m ? m.ma : "—"));
    } else if (k.caRo) {
      d.appendChild(el("span", "gop-pham vi-ro", "cả rổ"));
    }
    o.appendChild(d);
    var b = el("div", "gop-than");
    try { b.appendChild(VE[k.ma]()); } catch (e) { b.appendChild(oLoi(e, k.ma)); }
    o.appendChild(b);
    return o;
  }

  /* Thanh nhảy nhanh. Mọi ô đều mở nên trang dài — nhưng dài mà đi tới
     được ngay thì khác hẳn dài mà phải cuộn tìm. Đây là thứ THAY cho cơ
     chế gập: gập giấu nội dung đi để trang ngắn lại; thanh này giữ nội
     dung và rút ngắn ĐƯỜNG ĐI. */
  /* ── XẾP CỘT ──────────────────────────────────────────────────────
     CSS `columns` cân theo TỔNG chiều cao của cả khối, và với mười một ô
     cao thấp rất khác nhau thì nó ra những cách chia rất lệch: có lúc cả
     Trường Thi lẫn Nhật Ký dồn vào cột một, hai cột còn lại trống trơn
     suốt cả đoạn. Phép cân ấy không sai — nó tối ưu đúng thứ nó được
     giao, chỉ là thứ đó không phải thứ mình muốn.

     Nên tự xếp: dồn từng ô vào cột đang THẤP NHẤT. Đây là phép tham lam
     kinh điển cho bài toán này, và nó đủ tốt vì các ô không chênh nhau
     quá xa.

     Muốn xếp thì phải biết ô cao bao nhiêu, mà biết được thì phải vẽ
     xong. Nên: vẽ xong ĐO, cất số đo lại, lần vẽ sau dùng. Trang tự dựng
     lại mỗi 2 giây nên nó hội tụ sau đúng một nhịp — và số đo luôn là
     của nội dung thật, không phải của một bảng ước lượng viết cứng rồi
     lệch dần theo thời gian.

     Lần vẽ đầu tiên chưa có gì để đo, dùng `CAO_UOC` bên dưới. Sai vài
     trăm pixel ở nhịp đầu thì không ai kịp thấy.                        */

  var CAO_O = {};                   // ma → chiều cao đo được lần vẽ trước

  // Ước lượng thô cho nhịp đầu, theo lượng nội dung mỗi ô thường có.
  var CAO_UOC = {
    "dai-chiem": 380, "so-lenh": 420, "can-loi": 200, "ap-luc": 280,
    "kho-doi": 520, "ban-do": 320, "chien-thuat": 680, "truong-thi": 660,
    "ket-toan": 540, "quan-vi": 170, "nhat-ky": 660
  };

  function soCot() {
    var w = (typeof window !== "undefined" && window.innerWidth) || 1600;
    // Ngưỡng tính cả cột trái (~440px) cộng khoảng cách. Dưới 1120 thì
    // lưới đã xếp lại một cột nên chỗ này chỉ còn một cột luôn.
    if (w < 1120) return 1;
    if (w < 1620) return 2;
    return 3;
  }

  function _cao(k) { return (CAO_O[k.ma] || CAO_UOC[k.ma] || 300) + 10; }

  function xepCot(ds, n) {
    var cot = [], cao = [];
    for (var i = 0; i < n; i++) { cot.push([]); cao.push(0); }
    function thap() {
      var j = 0;
      for (var i = 1; i < n; i++) if (cao[i] < cao[j]) j = i;
      return j;
    }
    function dat(j, k) { cot[j].push(k); cao[j] += _cao(k); }

    // GHIM n ô đầu, mỗi cột một ô. Hàng trên cùng phải là những ô đọc
    // nhiều nhất — mô hình nói gì, chợ đang thế nào, ăn được bao nhiêu —
    // chứ không phải ô nào tình cờ hợp phép xếp.
    ds.slice(0, n).forEach(function (k, i) { dat(i, k); });

    // Còn lại: CAO TRƯỚC, thấp sau. Xếp theo thứ tự đọc thì ô cao nhất
    // hay rơi vào cuối và dồn hết vào một cột — đo được: lệch 1,43 lần.
    // Đặt ô to trước rồi lấy ô nhỏ lấp khe thì còn 1,08.
    ds.slice(n).slice().sort(function (a, b) { return _cao(b) - _cao(a); })
      .forEach(function (k) { dat(thap(), k); });

    // Trong mỗi cột, xếp lại theo thứ tự đọc gốc. Cân bằng là việc của
    // phép xếp; thứ tự đọc là việc của người đọc, đừng đánh đổi.
    cot.forEach(function (c) {
      c.sort(function (a, b) { return ds.indexOf(a) - ds.indexOf(b); });
    });
    return cot;
  }

  /* Đo sau khi vẽ. Không có `offsetHeight` (bộ kiểm chạy DOM giả) thì bỏ
     qua — xếp theo ước lượng vẫn ra một trang đọc được. */
  function doCaoCacO() {
    O_LIST.forEach(function (k) {
      var e = document.getElementById("o-" + k.ma);
      var h = e && e.offsetHeight;
      if (h) CAO_O[k.ma] = h;
    });
  }

  function veThanhNhay() {
    var h = el("nav", "nhay");
    O_LIST.forEach(function (k) {
      var b = el("button", "nhay-nut", k.ten);
      b.addEventListener("click", function () {
        var t = document.getElementById("o-" + k.ma);
        if (t && t.scrollIntoView) t.scrollIntoView({ behavior: "smooth", block: "start" });
      });
      h.appendChild(b);
    });
    return h;
  }

  function veTatCa() {
    var g = document.createDocumentFragment();

    // Độ trễ là con số của CẢ HỆ, không của riêng khung nào — nên nó nằm
    // trên cùng, trọn bề ngang, ngoài lưới hai cột.
    g.appendChild(veDaiTre());

    // Hai cột: thẻ chỉ huy hẹp bên trái, các khối mở ra BÊN CẠNH nó chứ
    // không phải bên dưới. Trước đây thẻ chiếm trọn bề ngang nên ba phần
    // tư màn hình bỏ trống, mà khối mở ra thì lại bị đẩy xuống dưới tầm
    // nhìn — vừa phí chỗ vừa phải cuộn.
    var luoi = el("div", "luoi-chinh");

    var trai = el("div", "cot-trai");
    trai.appendChild(veChiHuy());
    luoi.appendChild(trai);

    var phai = el("div", "cot-phai");
    phai.appendChild(veThanhNhay());
    var mo = el("div", "luon-mo");
    xepCot(O_LIST, soCot()).forEach(function (ds) {
      var c = el("div", "cot-m");
      ds.forEach(function (k) { c.appendChild(veOMo(k)); });
      mo.appendChild(c);
    });
    phai.appendChild(mo);
    luoi.appendChild(phai);

    g.appendChild(luoi);
    return g;
  }

  /* Thanh chuyên mục. Hôm nay đúng một mục vì mọi động cơ đều thuộc nhóm
     `crypto`. Dựng sẵn theo NHÓM chứ không viết cứng chữ "Crypto": thêm
     động cơ thời tiết là nó tự mọc thêm một mục, không phải sửa ở đây. */
  function veThanhChuyenMuc() {
    var thanh = document.getElementById("cm");
    if (!thanh) return;
    var nhom = {};
    (T.dongCo || []).forEach(function (h) {
      nhom[h.nhom] = (nhom[h.nhom] || 0) + 1;
    });
    var dem = {};
    (T.thiTruong || []).forEach(function (m) {
      if (!m.theo) return;
      var hs = (T.dongCo || []).filter(function (x) { return x.ma === m.dongCo; })[0];
      var n = hs ? hs.nhom : "?";
      dem[n] = (dem[n] || 0) + 1;
    });
    var ten = Object.keys(nhom).sort();
    if (thanh._ky === ten.join(",") + "|" + JSON.stringify(dem)) return;
    thanh._ky = ten.join(",") + "|" + JSON.stringify(dem);
    thanh.textContent = "";
    ten.forEach(function (n) {
      var b = el("button", "cm-nut" + (n === "crypto" ? " chon" : ""));
      b.appendChild(el("b", "", n === "crypto" ? "Crypto" : n));
      b.appendChild(el("i", "", (dem[n] || 0) + " khung · " +
                                nhom[n] + " động cơ"));
      thanh.appendChild(b);
    });
  }

  /* ── vẽ ───────────────────────────────────────────────────────── */
  var VE = {
    "tat-ca": veTatCa, "chi-huy": veChiHuy, "dai-chiem": veDaiChiem, "so-lenh": veSoLenh,
    "can-loi": veCanLoi, "kho-doi": veKhoDoi, "ap-luc": veApLuc,
    "ban-do": veBanDo,
    "chien-thuat": veChienThuat, "truong-thi": veTruongThi,
    "ket-toan": veKetToan, "quan-vi": veQuanVi, "nhat-ky": veNhatKy
  };

  /* Một buồng lái trắng trang KHÔNG được phép im lặng.

     `ve()` xoá thân trang rồi mới vẽ. Nếu hàm vẽ ném giữa chừng thì thân
     trang ở lại RỖNG, và vì lỗi bị `.catch` phía dưới nuốt nên không còn
     dấu vết nào — trang trắng, không thông báo, không dòng nào trong bảng
     điều khiển. Người vận hành thấy y hệt "máy chết", trong khi máy vẫn
     đang giao dịch bình thường.

     Ba đổi thay để chuyện đó không lặp lại:
       1. Cập nhật phần đỉnh TRƯỚC — đồng hồ và chế độ không bao giờ kẹt
          ở "—" chỉ vì một ô nào đó vẽ hỏng.
       2. Bọc phần vẽ trong try/catch, và HIỆN lỗi ra chính chỗ đáng lẽ
          là nội dung.
       3. Chỉ xoá thân trang khi đã dựng xong phần thay thế.                */
  function veDinh() {
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
  }

  // Tách dòng bằng hàm riêng: viết thẳng ký tự xuống dòng trong chuỗi
  // JS là chỗ rất dễ vỡ khi file được sinh ra bởi script khác.
  function _dong(s, n) {
    return s.split(String.fromCharCode(10)).slice(0, n)
            .join(String.fromCharCode(10));
  }

  function oLoi(e, o) {
    var d = el("div", "loi-ve");
    d.appendChild(el("b", "", "Ô “" + o + "” vẽ hỏng"));
    d.appendChild(el("p", "", String((e && e.message) || e)));
    var s = el("pre", "", _dong(String((e && e.stack) || ""), 6));
    d.appendChild(s);
    d.appendChild(el("p", "mo",
      "Máy vẫn chạy — chỉ ô này hỏng. Các ô khác vẫn bấm sang được, và " +
      "`node scripts/kiem-buong-lai.mjs --song` dựng lại đúng lỗi này ở " +
      "dòng lệnh."));
    return d;
  }

  function ve() {
    if (!T) return;
    try { veDinh(); veThanhChuyenMuc(); }
    catch (e) { /* đỉnh hỏng không được chặn thân */ }

    var moi;
    try {
      moi = (VE[O] || veTatCa)();
    } catch (e) {
      moi = oLoi(e, O);
    }
    than.textContent = "";
    than.appendChild(moi);
    // Đo NGAY SAU khi gắn vào trang — trước đó phần tử chưa có chiều cao.
    try { doCaoCacO(); } catch (e) { /* DOM giả không đo được, không sao */ }

    var bc = document.getElementById("bangCanh");
    var r = T.risk || {};
    // MÙ NGUỒN phải kêu to hơn cả cầu dao, vì nó dễ bị đọc nhầm thành
    // "chợ đang yên". Khi Gamma không với tới được, mọi khung đều rơi vào
    // "không thấy khung nào có tiền tố …" — một câu nghe hoàn toàn bình
    // thường. Máy đã mù suốt nhiều giờ mà bảng vẫn trông như một phiên
    // vắng khách.
    var mu = [];
    Object.keys(T.nguon || {}).forEach(function (n) {
      var v = T.nguon[n] || {};
      if ((v.soLoi || 0) >= 3 && !v.tongLuot) mu.push(n);
    });
    if (mu.length) {
      var v0 = T.nguon[mu[0]] || {};
      bc.textContent = "MÁY ĐANG MÙ — không với tới được " + mu.join(", ") +
        " (" + (v0.loiCuoi || "?") + "). Mọi khung bị bỏ qua vì KHÔNG CÓ " +
        "dữ liệu, không phải vì chợ yên. Kiểm đường mạng tới sàn trước khi " +
        "nghi mô hình.";
      bc.hidden = false;
    } else if (r.ngatKhanCap) {
      bc.textContent = "CẦU DAO ĐANG NGẮT — " + (r.lyDoNgat || "") +
        ". Mọi lệnh bị chặn cho tới khi mở lại bằng tay.";
      bc.hidden = false;
    } else bc.hidden = true;
  }

  function tai() {
    return fetch("/api/trang-thai", { cache: "no-store" })
      .then(function (r) { return r.json(); })
      .then(function (d) { T = d; ghiLich(d); ve(); })
      .catch(function (e) {
        // KHÔNG nuốt. Một buồng lái không nói được là nó đang mù thì tệ
        // hơn một buồng lái báo lỗi.
        var bc = document.getElementById("bangCanh");
        bc.textContent = "Không đọc được trạng thái từ runtime — " +
          ((e && e.message) || e) + ". Máy có thể vẫn đang chạy; đây là " +
          "trang không lấy được dữ liệu.";
        bc.hidden = false;
      });
  }

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

  // Đồng hồ đếm ngược phải chạy MƯỢT. Nhịp nạp là 2 giây, nên nếu để đồng
  // hồ nhảy theo nhịp đó thì với market 5 phút nó giật thấy rõ, và đúng ở
  // giây cuối — lúc con số ấy quan trọng nhất. Mỗi lần nạp cho một MỐC KẾT
  // THÚC tuyệt đối; giữa hai lần nạp thì trang tự trừ dần lấy.
  setInterval(function () {
    [].forEach.call(document.querySelectorAll(".dhho"), function (e) {
      if (e._ve) e._ve();
    });
  }, 250);
})();
