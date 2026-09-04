/* Thị Bạc Ty — cung tĩnh.
 *
 * Đọc `window.CANG_PHI` do `thi-bac-ty-runtime/bac/snapshot.py` ghi ra. Không
 * gọi mạng, không nút nào đặt lệnh — cung QUAN SÁT, runtime ĐIỀU KHIỂN.
 *
 * Luật của cả file: **chưa có lát cắt thì phải NÓI RA**. Trang hiện bảng
 * trống với mọi đèn xanh là kiểu hỏng tệ nhất một bảng điều khiển có thể có —
 * nó không sai, nó im lặng, và người xem không phân biệt được với "thị trường
 * hôm nay không có gì".
 */
(function () {
  "use strict";

  var D = window.CANG_PHI || null;

  function $(s) { return document.querySelector(s); }
  function el(t, c, x) {
    var e = document.createElement(t);
    if (c) e.className = c;
    if (x != null) e.textContent = x;
    return e;
  }
  function so(v, n, hau) {
    if (v == null || (typeof v === "number" && !isFinite(v))) return "—";
    return Number(v).toFixed(n == null ? 2 : n) + (hau || "");
  }
  function dau(v, n) {
    if (v == null || !isFinite(v)) return "—";
    return (v >= 0 ? "+" : "") + Number(v).toFixed(n == null ? 2 : n);
  }
  function lop(v) { return v == null ? "nhat" : (v >= 0 ? "duong" : "am"); }
  function gio(g) {
    if (g == null) return "—";
    if (g < 60) return Math.round(g) + " giây";
    if (g < 3600) return (g / 60).toFixed(1) + " phút";
    if (g < 86400) return (g / 3600).toFixed(1) + " giờ";
    return (g / 86400).toFixed(1) + " ngày";
  }

  function bang(cot, hang) {
    var w = el("div", "cuon"), t = el("table"), th = el("thead"), tr = el("tr");
    cot.forEach(function (c) { tr.appendChild(el("th", c.trai ? "trai" : null, c.t)); });
    th.appendChild(tr); t.appendChild(th);
    var tb = el("tbody");
    hang.forEach(function (h) {
      var r = el("tr");
      h.forEach(function (o) {
        var td = el("td", o.c || null, o.t);
        if (o.title) td.title = o.title;
        r.appendChild(td);
      });
      tb.appendChild(r);
    });
    t.appendChild(tb); w.appendChild(t);
    return w;
  }

  function giai(t) { return el("p", "giai", t); }

  function trong(nhan) {
    var d = document.createDocumentFragment();
    d.appendChild(el("p", "trong", nhan));
    return d;
  }

  /* ── chưa có lát cắt ────────────────────────────────────────────── */
  function chua_co() {
    var c = $("#canh-tinh");
    c.hidden = false;
    c.className = "canh-tinh nang";
    c.textContent =
      "CHƯA CÓ LÁT CẮT NÀO. File assets/js/v/cang-phi.js chưa được sinh, nên "
      + "mọi bảng dưới đây trống vì THIẾU DỮ LIỆU — không phải vì thị trường "
      + "không có chênh lệch. Sinh bằng: cd thi-bac-ty-runtime && python -m bac.snapshot";

    ["#oCoHoi", "#oViSao", "#oBaoGia", "#oCang"].forEach(function (s) {
      $(s).replaceChildren(trong("chưa có dữ liệu — xem dải cảnh báo ở trên"));
    });
    $("#dauSo").replaceChildren(el("span", "vien xau", "chưa có lát cắt"));
    $("#chanNhac").textContent =
      "Cung tĩnh này chỉ đọc một file đã commit. Nó không gọi sàn nào.";
  }

  /* ── đỉnh trang ─────────────────────────────────────────────────── */
  function ve_dinh() {
    var s = $("#dauSo"), ds = [];
    ds.push(["lát cắt " + (D.date || "—"), ""]);
    ds.push(["chế độ " + (D.che || "—"), D.che === "quan-sat" ? "" : "canh"]);
    var song = (D.cang || []).filter(function (c) { return c.songSot; }).length;
    var tong = (D.cang || []).length;
    ds.push([song + "/" + tong + " cảng", song === tong ? "on" : "xau"]);
    ds.push([(D.soDuyet || 0) + " cặp qua cửa", (D.soDuyet || 0) ? "on" : ""]);
    s.replaceChildren.apply(s, ds.map(function (x) {
      return el("span", "vien" + (x[1] ? " " + x[1] : ""), x[0]);
    }));
  }

  function ve_canh() {
    var c = $("#canh-tinh"), ds = [];
    var chet = (D.cang || []).filter(function (x) { return !x.songSot; });
    if (chet.length)
      ds.push("MÙ MỘT MẮT lúc chụp: " + chet.map(function (x) { return x.ten; }).join(", ")
              + " chưa lấy được dữ liệu lần nào — bảng dưới thiếu cảng.");
    if (D.loiVongCuoi) ds.push("vòng quét gần nhất lỗi: " + D.loiVongCuoi);

    var dh = D.dongHo || {};
    if (!dh.daDo)
      ds.push("lúc chụp CHƯA đo được lệch đồng hồ — phép đếm mốc trong lát "
              + "cắt này chạy trên giờ MÁY, không phải giờ sàn.");
    else if (dh.dangKeu)
      ds.push("đồng hồ máy lệch " + dh.lechGiay.toFixed(0) + "s so với sàn "
              + "lúc chụp (đã bù khi đếm mốc).");

    // Lát cắt cũ: số liệu funding hết hạn rất nhanh, một lát cắt tuần trước
    // nói về một thế giới đã qua. Nói thẳng tuổi của nó.
    var tuoi = null;
    if (D.generatedAt) {
      var t = Date.parse(D.generatedAt);
      if (!isNaN(t)) tuoi = (Date.now() - t) / 1000;
    }
    if (tuoi != null && tuoi > 86400)
      ds.push("lát cắt đã " + gio(tuoi) + " tuổi — funding đổi theo giờ, "
              + "nên đây là ảnh của một thế giới đã qua.");

    if (!ds.length) { c.hidden = true; return; }
    c.hidden = false;
    c.className = "canh-tinh" + (chet.length ? " nang" : "");
    c.textContent = ds.join("  ·  ");
  }

  /* ── cơ hội ─────────────────────────────────────────────────────── */
  function ve_co_hoi() {
    var ds = D.coHoi || [], n = $("#oCoHoi");
    if (!ds.length) {
      n.replaceChildren(trong(
        "lát cắt này chưa cân được cặp nào — cần ít nhất hai cảng cùng trả về "
        + "một mã thì mới ghép được một cặp"));
      return;
    }

    var f = document.createDocumentFragment();

    var l = el("div", "luoi");
    [["cặp đã cân", ds.length],
     ["qua cửa rủi ro", D.soDuyet || 0],
     ["cửa sổ giữ giả định", so(D.giuGio, 0) + " giờ"],
     ["mã theo dõi", (D.ma || []).length]
    ].forEach(function (x) {
      var d = el("div", "so");
      d.appendChild(el("div", "n", String(x[1])));
      d.appendChild(el("div", "t", x[0]));
      l.appendChild(d);
    });
    f.appendChild(l);

    f.appendChild(bang(
      [{ t: "Mã", trai: 1 }, { t: "LONG", trai: 1 }, { t: "SHORT", trai: 1 },
       { t: "gross bps/ngày" }, { t: "mốc L+S" }, { t: "thu bps" },
       { t: "phí bps" }, { t: "NET bps" }, { t: "lệch mark" },
       { t: "cửa", trai: 1 }, { t: "vì sao", trai: 1 }],
      ds.map(function (c) {
        var km = (c.soMocLong || 0) + (c.soMocShort || 0);
        return [
          { t: c.ma, c: "trai" },
          { t: c.sanLong, c: "trai" },
          { t: c.sanShort, c: "trai" },
          { t: dau(c.grossBpsNgay) },
          { t: (c.soMocLong || 0) + "+" + (c.soMocShort || 0),
            c: km ? null : "am",
            title: km ? "" : "không mốc kết toán nào rơi vào cửa sổ giữ" },
          { t: dau(c.thuBps), c: lop(c.thuBps) },
          { t: so(c.phiBps), c: "nhat" },
          { t: dau(c.netBps), c: lop(c.netBps) },
          { t: c.lechMarkBps == null ? "—" : so(c.lechMarkBps, 1),
            c: c.lechMarkBps == null ? "am" : "nhat" },
          { t: c.duyet ? "QUA" : "chặn", c: c.duyet ? "qua" : "chan" },
          { t: (c.lyDo || []).join(" · ") || "—", c: "vi" }
        ];
      })));

    f.appendChild(giai(
      "Cột NET là CHẶN TRÊN: funding thực thu trừ phí và trượt giá, nhưng "
      + "CHƯA trừ bốn khoản — vay coin, chuyển vốn giữa sàn, rủi ro basis lúc "
      + "thoát, và vốn bị khoá. Lát cắt mang theo `phiConThieu` để nói rõ. "
      + "Trong các con số đang có thì đây vẫn là thứ duy nhất đáng "
      + "xếp hạng. Cột gross chỉ là chênh lệch thô đã chuẩn hoá, chưa trừ gì. "
      + "Cột 'mốc L+S' bằng 0+0 nghĩa là giữ hết cửa sổ mà thu đúng bằng "
      + "không, dù gross trông vẫn to — xem mục Hai phép tính."));
    n.replaceChildren(f);
  }

  function ve_vi_sao() {
    var vs = D.viSaoTuChoi || {}, k = Object.keys(vs), n = $("#oViSao");
    if (!k.length) {
      n.replaceChildren(trong("không cặp nào bị chặn trong lát cắt này"));
      return;
    }
    k.sort(function (a, b) { return vs[b] - vs[a]; });
    var f = document.createDocumentFragment();
    f.appendChild(bang(
      [{ t: "Cửa", trai: 1 }, { t: "số cặp" }],
      k.map(function (x) { return [{ t: x, c: "trai" }, { t: String(vs[x]) }]; })));
    f.appendChild(giai(
      "Bảng cơ hội trống mà không có bảng này thì người xem đọc thành \"thị "
      + "trường hôm nay không có gì\". Thường sự thật là: có chênh lệch, "
      + "nhưng phí ăn hết — và đó là hai kết luận rất khác nhau."));
    n.replaceChildren(f);
  }

  function ve_bao_gia() {
    var ds = (D.baoGia || []).slice(), n = $("#oBaoGia");
    if (!ds.length) {
      n.replaceChildren(trong("lát cắt này không có báo giá nào"));
      return;
    }
    ds.sort(function (a, b) {
      return a.ma === b.ma ? (b.moiNgayBps - a.moiNgayBps) : (a.ma < b.ma ? -1 : 1);
    });
    var f = document.createDocumentFragment();
    f.appendChild(bang(
      [{ t: "Mã", trai: 1 }, { t: "Cảng", trai: 1 }, { t: "rate / chu kỳ" },
       { t: "chu kỳ" }, { t: "bps/ngày" }, { t: "mark" }, { t: "tuổi" },
       { t: "ghi chú", trai: 1 }],
      ds.map(function (q) {
        return [
          { t: q.ma, c: "trai" },
          { t: q.san, c: "trai" },
          { t: (q.rate * 100).toFixed(5) + "%" },
          { t: so(q.intervalGio, 0) + "h" + (q.intervalSuyRa ? " ?" : ""),
            c: q.intervalSuyRa ? "am" : null,
            title: q.intervalSuyRa ? "chu kỳ phải ĐOÁN — sàn không công bố" : "" },
          { t: dau(q.moiNgayBps), c: lop(q.moiNgayBps) },
          { t: q.markPx == null ? "—" : so(q.markPx, 4),
            c: q.markPx == null ? "am" : null },
          { t: q.tuoiGiay == null ? "—" : gio(q.tuoiGiay), c: "nhat" },
          { t: q.ghiChu || "", c: "vi" }
        ];
      })));
    f.appendChild(giai(
      "Cột 'rate / chu kỳ' là con số sàn công bố; 'bps/ngày' là sau khi chia "
      + "cho chu kỳ thật rồi quy về ngày. So hai cảng bằng cột đầu là sai — "
      + "0,08%/8h nhỏ hơn 0,015%/1h, dù nhìn số thô thì ngược lại."));
    n.replaceChildren(f);
  }

  function ve_cang() {
    var ds = D.cang || [], n = $("#oCang");
    if (!ds.length) { n.replaceChildren(trong("không có cảng nào")); return; }
    var f = document.createDocumentFragment();
    f.appendChild(bang(
      [{ t: "Cảng", trai: 1 }, { t: "trạng thái", trai: 1 }, { t: "lượt hỏi" },
       { t: "lỗi" }, { t: "trễ TB" }, { t: "phí taker" }, { t: "trượt giá" },
       { t: "lỗi cuối", trai: 1 }],
      ds.map(function (c) {
        var p = (D.phiSan || {})[c.ten] || {};
        return [
          { t: c.ten, c: "trai" },
          { t: c.songSot ? "sống" : "CHƯA BAO GIỜ",
            c: c.songSot ? "qua" : "am" },
          { t: String(c.tongLuot == null ? "—" : c.tongLuot) },
          { t: String(c.soLoi == null ? "—" : c.soLoi),
            c: c.soLoi ? "am" : "nhat" },
          { t: so(c.treTrungBinhMs, 0) + " ms" },
          { t: so(p.phiTakerBps, 1) + " bps" },
          { t: so(p.truotGiaBps, 1) + " bps" },
          { t: c.loiCuoi || "", c: "vi" }
        ];
      })));
    f.appendChild(giai(
      "Phí và trượt giá là THAM SỐ trong config.json của runtime, không phải "
      + "số đo được từ sàn. Đặt quá thấp là tự vẽ ra lợi nhuận không có thật. "
      + "— Đồng hồ lúc chụp: "
      + ((D.dongHo || {}).daDo
          ? "máy chậm hơn sàn " + so(D.dongHo.lechGiay, 1)
            + " giây, đo từ " + D.dongHo.soMau + " sàn, đã bù khi đếm mốc."
          : "CHƯA đo được.")));
    n.replaceChildren(f);
  }

  function ve_chan() {
    var t = [];
    if (D.tomTat) t.push(D.tomTat);
    if (D.vong != null) t.push("vòng quét thứ " + D.vong);
    if (D.chayDuocGiay != null) t.push("runtime chạy được " + gio(D.chayDuocGiay));
    if (D.so && D.so.soLuot) t.push(D.so.soLuot + " lượt quét đã ghi sổ");
    $("#chanNhac").textContent =
      t.join(" · ") + (t.length ? ". " : "") + (D.loiNhac || "");
  }

  /* ── lớp tri thức nền ───────────────────────────────────────────────
   *
   * Đọc `window.TRI_THUC` do `knowledge-os/sinh.mjs` ghi ra — file đó mang
   * CẢ dữ liệu lẫn hàm vẽ, nên khuôn HTML giống hệt tám cung kia và chỉ
   * sửa ở một chỗ. Nó KHÔNG đụng vào con số nào: funding, NET, mốc, phí
   * đều tính y như cũ; việc duy nhất của nó là nói mỗi bảng đang đo VIỆC
   * KINH TẾ nào, và mỗi câu giải nghĩa đến từ đâu.
   *
   * Lớp này độc lập với lát cắt runtime, nên nó vẽ cả khi CHƯA có
   * `cang-phi.js` — không có số vẫn còn giải nghĩa để đọc.
   */
  var TT = window.TRI_THUC || null;

  function ve_tri_thuc() {
    if (!TT || !TT.gan || !TT.phong) return;
    TT.phong.forEach(function (p) {
      /* Mã phòng đã đổi thì `getElementById` trả null — im lặng bỏ qua,
         đừng vẽ bừa vào thẻ khác. `knowledge-os/kiem.mjs` mới là chỗ
         báo chuyện đó, và nó báo lúc sinh chứ không lúc chạy. */
      TT.gan(p.ma, document.getElementById(p.ma));
    });
  }

  /* Một dòng ở chân trang nói lát cắt tri thức đến từ đâu. Không có nó
     thì người đọc không biết mấy câu giải nghĩa trên kia là của ai — mà
     "của ai" chính là thứ cả lớp này canh.

     Gọi SAU cùng, không gọi chung với `ve_tri_thuc()`: cả `ve_chan()`
     lẫn `chua_co()` đều GÁN `textContent` cho `#chanNhac`, nên nối
     trước là bị xoá sạch mà không có lỗi nào báo. */
  function ve_tri_thuc_chan() {
    var n = $("#chanNhac");
    if (!TT || !TT.chan || !n) return;
    n.appendChild(el("span", "tt-chan-dong", TT.chan()));
  }

  /* ── Trung Ương: CHÍN ty, không phải một ────────────────────────── */
  function ve_trung_uong() {
    var T = D.trungUong;
    var host = $("#trungUong");
    if (!host) return;
    if (!T || !T.co) {
      host.appendChild(giai(
        "Lát cắt này chưa mang tóm tắt Trung Ương"
        + (T && T.vi ? " (" + T.vi + ")" : "") + "."));
      return;
    }

    host.appendChild(giai(
      "Trang này là cửa sổ nhìn vào ty chênh funding. Bảng dưới nói phần "
      + "còn lại của cỗ máy đang làm gì — " + (T.soTy || 0) + " ty, "
      + "và tám trong số đó không xuất hiện ở bất kỳ ô nào khác trên trang."));

    /* chế độ từng ty */
    host.appendChild(bang(
      [{ t: "ty", trai: true }, { t: "họ", trai: true },
       { t: "chế độ", trai: true }, { t: "vì sao", trai: true }],
      (T.ty || []).map(function (x) {
        return [{ t: x.ma || "?", c: "trai" },
                { t: x.ho || "?", c: "trai" },
                { t: x.che || "?", c: "trai " + (x.che === "THAT" ? "duong"
                    : x.che === "GIAY" ? "nhat" : "am") },
                { t: (x.vi || "").slice(0, 64), c: "trai giai" }];
      })));
    host.appendChild(giai(
      "QUAN_SAT nghĩa là ty ấy quét được nhưng vốn hiện có chưa tới ngưỡng "
      + "kinh tế của nó — nó TỪ CHỐI xin vốn thay vì xin một nửa. GIAY là "
      + "đủ vốn nhưng chỉ ghi sổ giấy: lớp đặt lệnh thật KHÔNG tồn tại "
      + "trong runtime này."));

    /* phễu theo họ */
    var ph = T.pheuTheoHo || [];
    if (ph.length) {
      host.appendChild(el("h3", null, "Phễu theo họ"));
      host.appendChild(bang(
        [{ t: "họ", trai: true }, { t: "cơ hội thô" }, { t: "qua cổng ty" },
         { t: "qua Rủi Ro Tổng" }, { t: "được cấp vốn" }],
        ph.map(function (x) {
          return [{ t: x.ho, c: "trai" },
                  { t: so(x.coHoiTho, 0) },
                  { t: so(x.quaCongTy, 0) },
                  { t: so(x.quaRuiRoTong, 0) },
                  { t: so(x.daCapVon, 0) }];
        })));
      host.appendChild(giai(
        "Cột đầu trừ cột cuối chính là số cơ hội bị TỪ CHỐI. Một cỗ máy "
        + "từ chối giỏi quan trọng hơn một cỗ máy phát hiện nhiều — bảng "
        + "này đáng đọc từ phải sang trái."));
    }

    /* hiến pháp + sổ engine */
    var hp = T.hienPhap || {}, dc = T.dongCoChuaCo || {};
    var d = el("div", hp.soViPham ? "loi-o" : null);
    d.appendChild(el("p", hp.soViPham ? "am" : "qua",
      "Hiến pháp: " + (hp.soDieu || 0) + " điều · "
      + (hp.soCanhDuoc || 0) + " canh được bằng máy · "
      + (hp.soViPham || 0) + " vi phạm"));
    if ((hp.khongCanhDuoc || []).length) {
      d.appendChild(el("p", "vi", "KHÔNG canh được ("
        + (hp.soKhongCanhDuoc || 0) + "): "
        + (hp.khongCanhDuoc || []).join(", ")));
    }
    if (dc.soDongCo) {
      d.appendChild(el("p", "giai",
        "Engine chưa dựng: " + dc.soDongCo + " · CHẶN " + dc.soChan
        + " · quét được nhưng chưa dựng " + dc.soQuetDuoc
        + " · ĐÃ DỰNG " + dc.soDaDung
        + ((dc.theoTrangThai && dc.theoTrangThai.CHAN || []).length
            ? " — còn chặn: " + dc.theoTrangThai.CHAN.join(", ") : "")));
    }
    host.appendChild(d);
    host.appendChild(giai(
      "Một hiến pháp mà điều nào cũng trông như đang có hiệu lực thì tệ "
      + "hơn không có, nên số điều KHÔNG canh được cũng hiện ở đây. "
      + (T.loiNhac || "")));
  }

  /* ── Bể thanh khoản V3 — lát cắt THỨ HAI, file riêng ────────────────
   *
   * Đọc `window.BE_THANH_KHOAN` do `lp_v3/lat_cat.py` ghi. Độc lập với
   * `D`: vẽ cả khi chưa có `cang-phi.js`, và thiếu file thì NÓI RA —
   * một ô trống ở đây đọc thành «không có pool nào đáng vào».
   */
  var B = window.BE_THANH_KHOAN || null;
  var TEN_HD = { VAO: "VÀO", GIU: "GIỮ", CHO: "CHỜ", RUT: "RÚT",
                 NOI_RONG: "NỚI DẢI", THU_HEP: "THU HẸP", DOI_DAI: "ĐỔI DẢI" };
  function bps(v) {
    if (v == null || !isFinite(v)) return "—";
    return (v >= 0 ? "+" : "") + Math.round(v) + " bps";
  }
  function ve_be_thanh_khoan() {
    var n = $("#oBeThanhKhoan");
    if (!n) return;
    if (!B) {
      n.replaceChildren(trong(
        "CHƯA CÓ LÁT CẮT bể thanh khoản — assets/js/v/be-thanh-khoan.js chưa "
        + "được sinh. Sinh bằng: cd thi-bac-ty-runtime && python -m bac.snapshot"));
      return;
    }
    var f = document.createDocumentFragment();
    var ph = B.phien || {}, th = B.thuong || {}, hd = B.tomTatHanhDong || {};
    var l = el("div", "luoi");
    [["lát cắt", B.lucVn || B.date || "—"],
     ["phiên Mỹ lúc chụp", ph.trangThai || "—"],
     ["thưởng còn", th.conGio == null ? "—" : Math.round(th.conGio) + " giờ"],
     ["pool VÀO được", (hd.VAO || []).length],
     ["vị thế đang giữ", (B.viThe || []).length]
    ].forEach(function (x) {
      var d = el("div", "so");
      d.appendChild(el("div", "n", String(x[1])));
      d.appendChild(el("div", "t", x[0]));
      l.appendChild(d);
    });
    f.appendChild(l);
    if ((B.nguonMu || []).length)
      f.appendChild(giai("Nguồn đang mù lúc chụp: " + B.nguonMu.join(" · ")));
    if (th.kiemCheo) f.appendChild(giai(th.kiemCheo));

    f.appendChild(bang(
      [{ t: "Pool", trai: 1 }, { t: "hành động", trai: 1 }, { t: "luật", trai: 1 },
       { t: "giá" }, { t: "σ" }, { t: "dải đề xuất" }, { t: "P(văng)" },
       { t: "phí/LVR" }, { t: "NET/cửa sổ" }, { t: "vì sao", trai: 1 }],
      (B.pool || []).map(function (p) {
        var dd = p.dai || {};
        return [
          { t: p.kyHieu, c: "trai" },
          { t: TEN_HD[p.hanhDong] || p.hanhDong || "—",
            c: "trai " + (p.hanhDong === "VAO" ? "qua" : p.biChan ? "chan" : "") },
          { t: p.luat || "", c: "trai nhat" },
          { t: p.gia == null ? "—" : so(p.gia, 2) + " " + (p.nguonGia || ""),
            c: p.gia == null ? "am" : null },
          { t: p.sigma == null ? "—" : so(p.sigma * 100, 0, "%") + "/" + (p.soPhien || 0),
            c: p.sigma == null ? "am" : null },
          { t: dd.Pa == null ? "—" : so(dd.Pa, 2) + "–" + so(dd.Pb, 2)
               + " (±" + so(dd.rongPct, 1) + "%)" },
          { t: dd.pVang == null ? "—" : "≤ " + so(dd.pVang * 100, 0, "%") },
          { t: dd.tiLePhiTrenLvr == null ? "—" : so(dd.tiLePhiTrenLvr, 2) },
          { t: bps(dd.netBps), c: lop(dd.netBps) },
          { t: p.lyDo || "", c: "vi" }
        ];
      })));
    f.appendChild(giai(
      "Ty thứ mười của Thị Bạc Ty. Khác ty AMM ở trên: nó nhận cặp BIẾN "
      + "ĐỘNG (cổ phiếu token hoá so với USDG trên X Layer), nhưng chỉ khi "
      + "đo được σ — có σ thì tổn thất vô thường, LVR và xác suất văng dải "
      + "đều là phép tính. Không có σ thì nó nói KHÔNG, y như ty kia. "
      + "Giả định đang dùng: " + (B.giaDinh || []).join(" | ")));

    var bh = B.baiHoc;
    if (bh && (bh.duMau || []).length) {
      f.appendChild(el("h3", null, "Bài học đủ mẫu"));
      var u = el("div", "viec-1");
      bh.duMau.forEach(function (c) { u.appendChild(el("p", "giai", "★ " + c)); });
      f.appendChild(u);
    } else {
      var kn = B.kinhNghiem || {};
      f.appendChild(giai("Sổ kinh nghiệm: " + (kn.soQuyetDinh || 0) + " quyết định "
        + "đã ghi, " + (kn.soKetCuc || 0) + " đã chấm — chưa có bài học đủ mẫu. "
        + "Cầu tuyết lăn theo từng cửa sổ giữ; trang này chỉ hiện những bài đã "
        + "vượt ngưỡng n ≥ 5 và độ tin ≥ 2."));
    }
    n.replaceChildren(f);
  }

  function ve() {
    ve_tri_thuc();
    try { ve_be_thanh_khoan(); }
    catch (e) {
      var nb = $("#oBeThanhKhoan");
      if (nb) nb.replaceChildren(trong("Ô bể thanh khoản vẽ hỏng: " + (e && e.message || e)));
    }
    if (!D) { chua_co(); ve_tri_thuc_chan(); return; }
    // Dựng từng ô trong try riêng: một ô hỏng không được kéo theo cả trang,
    // và chỗ hỏng phải HIỆN ra chứ không để lại một khoảng trắng.
    [["đỉnh", ve_dinh], ["cảnh báo", ve_canh],
     ["trung ương", ve_trung_uong], ["cơ hội", ve_co_hoi],
     ["vì sao", ve_vi_sao], ["báo giá", ve_bao_gia], ["cảng", ve_cang],
     ["chân trang", ve_chan]
    ].forEach(function (x) {
      try { x[1](); }
      catch (e) {
        var c = $("#canh-tinh");
        c.hidden = false;
        c.className = "canh-tinh nang";
        c.textContent = "Ô «" + x[0] + "» vẽ hỏng: " + (e && e.message || e)
          + " — lát cắt vẫn còn nguyên trong assets/js/v/cang-phi.js.";
      }
    });
    ve_tri_thuc_chan();
  }

  /* ── thanh bên trên máy hẹp ─────────────────────────────────────── */
  var ben = $("#ben"), nut = $("#benNut");
  if (nut) nut.addEventListener("click", function () {
    ben.setAttribute("data-mo", ben.getAttribute("data-mo") === "1" ? "0" : "1");
  });
  document.addEventListener("click", function (e) {
    if (window.innerWidth > 900) return;
    if (e.target.closest("#ben a")) ben.setAttribute("data-mo", "0");
    else if (!e.target.closest("#ben") && !e.target.closest("#benNut"))
      ben.setAttribute("data-mo", "0");
  });

  /* ── thanh bên: đang đọc mục nào ────────────────────────────────
   *
   * Cung này là MỘT trang dài bảy mục, thanh bên dính theo suốt. Không
   * có dấu "đang ở đây" thì thanh bên chỉ là một danh sách liên kết,
   * không phải bản đồ: cuộn tới giữa bảng cơ hội rồi thì phải cuộn
   * ngược lên tìm tiêu đề mới biết mình đang đọc bảng nào — mà bảng
   * cơ hội và bảng báo giá có cột trông rất giống nhau.
   *
   * `aria-current` chứ không chỉ đổi màu: người đi bằng trình đọc màn
   * hình cũng cần câu trả lời ấy, và họ là người cần nó nhất.
   *
   * Chỉ lấy `.bnhom .bmuc` — halls.js cũng dựng `.bmuc` trong #cungNav
   * cho danh sách chuyển cung, và những mục đó trỏ ra ngoài trang.
   */
  var mucBen = [].slice.call(document.querySelectorAll(".bnhom .bmuc[href^='#']"));
  var dichBen = mucBen.map(function (a) {
    return document.getElementById(a.getAttribute("href").slice(1));
  });

  function danh_dau_muc() {
    if (!mucBen.length) return;
    var dang = 0;
    for (var i = 0; i < dichBen.length; i++) {
      var d = dichBen[i];
      if (d && d.getBoundingClientRect().top <= 96) dang = i;
    }
    /* Cuộn hết trang thì mục CUỐI phải sáng, dù đỉnh nó chưa qua vạch:
       mục cuối thấp hơn màn hình thì không bao giờ chạm tới vạch ấy,
       và thanh bên sẽ mãi chỉ vào mục áp chót. */
    if (window.innerHeight + (window.scrollY || 0)
        >= document.documentElement.scrollHeight - 4)
      dang = mucBen.length - 1;
    mucBen.forEach(function (a, k) {
      if (k === dang) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
  }

  var choNhip = 0;
  window.addEventListener("scroll", function () {
    if (choNhip) return;
    choNhip = 1;
    requestAnimationFrame(function () { choNhip = 0; danh_dau_muc(); });
  }, { passive: true });
  window.addEventListener("resize", danh_dau_muc);

  ve();
  /* Sau ve(): chiều cao mỗi mục chỉ có thật khi bảng đã dựng xong. */
  danh_dau_muc();
})();
