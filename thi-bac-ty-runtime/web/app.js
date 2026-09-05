/* Buồng lái Thị Bạc Ty — TRUNG ƯƠNG.
 *
 * Luật kiến trúc thông tin của file này, và nó là lý do buồng lái được viết
 * lại: **`localhost:5188/` không thuộc về bất kỳ ty nào.** Trước đây trang
 * gốc là bảng chẩn đoán của riêng ty chênh funding — bps, mốc L+S, lệch
 * mark — và người mở nó ra phải giải mã mới biết máy có ổn không. Một động
 * cơ trong mười ba chiếm cửa vào của cả bộ máy.
 *
 * Ba tầng, và trang gốc chỉ được ở tầng MỘT:
 *
 *   tầng 1  máy có ổn không · tiền ở đâu · lời lỗ · ai đang chạy
 *   tầng 2  vì sao — cơ hội, phân bổ, nguồn dữ liệu
 *   tầng 3  mổ máy — bps thô, lệch mark, RPC, log        ← `/dong-co/...`
 *
 * Luật thứ hai, giữ từ bản cũ: **trang trắng không được phép im lặng.**
 * Dựng xong phần thay thế RỒI mới thay; vẽ hỏng thì HIỆN lỗi ra đúng chỗ
 * đáng lẽ là nội dung, kèm câu "máy VẪN đang chạy".
 *
 * Luật thứ ba: **màu là trạng thái.** Sáu màu trạng thái không dùng vào
 * việc gì khác — nếu không thì mắt học sai, và một cái thẻ xanh vì nó đẹp
 * sẽ đọc như một cái thẻ xanh vì nó khoẻ.
 */
(function () {
  "use strict";

  var S = null, DANG_TAI = false, NHAT_KY = null, LOI_NHAT_KY = "";

  /* ── tiện ─────────────────────────────────────────────────────── */
  function $(s) { return document.querySelector(s); }
  function el(t, c, x) {
    var e = document.createElement(t);
    if (c) e.className = c;
    if (x != null) e.textContent = x;
    return e;
  }
  function tien(v, hau) {
    if (v == null) return "—";
    var s = "$" + Math.abs(v).toLocaleString("vi-VN",
      { minimumFractionDigits: hau == null ? 2 : hau,
        maximumFractionDigits: hau == null ? 2 : hau });
    return (v < 0 ? "−" : "") + s;
  }
  function so(v, hau) {
    if (v == null) return "—";
    return Number(v).toLocaleString("vi-VN",
      { minimumFractionDigits: hau || 0, maximumFractionDigits: hau || 0 });
  }
  function phan(v, hau) { return v == null ? "—" : (v >= 0 ? "+" : "−")
    + Math.abs(v).toFixed(hau == null ? 2 : hau) + "%"; }
  function gio(g) {
    if (g == null) return "—";
    if (g < 60) return Math.round(g) + "s";
    if (g < 3600) return Math.round(g / 60) + "m";
    var h = Math.floor(g / 3600), m = Math.round((g % 3600) / 60);
    return h + "h" + (m ? String(m).padStart(2, "0") : "");
  }
  function khoi(ten, giaiTren) {
    var k = el("section", "khoi");
    if (ten) k.appendChild(el("h2", null, ten));
    if (giaiTren) k.appendChild(el("p", "giai-tren", giaiTren));
    return k;
  }
  function hop(tieu, phai) {
    var h = el("div", "hop"), d = el("header");
    d.appendChild(el("h3", null, tieu));
    if (phai) d.appendChild(phai);
    h.appendChild(d);
    var n = el("div", "noi");
    h.appendChild(n);
    h.noi = n;
    return h;
  }
  function oSo(ten, gt, duoi, lop, nho) {
    var o = el("div", "o-so");
    o.appendChild(el("span", "ten", ten));
    o.appendChild(el("span", "gt" + (nho ? " nho" : "") + (lop ? " " + lop : ""), gt));
    if (duoi) o.appendChild(el("span", "duoi", duoi));
    return o;
  }
  function bang(cot, hang) {
    var w = el("div", "cuon"), t = el("table"), h = el("thead"), r = el("tr");
    cot.forEach(function (c) { r.appendChild(el("th", c.n ? "n" : null, c.t)); });
    h.appendChild(r); t.appendChild(h);
    var b = el("tbody");
    hang.forEach(function (x) {
      var tr = el("tr");
      x.forEach(function (o) {
        var td = el("td", o.c || null);
        if (o.el) td.appendChild(o.el); else td.textContent = o.t;
        tr.appendChild(td);
      });
      b.appendChild(tr);
    });
    t.appendChild(b); w.appendChild(t);
    return w;
  }
  function giai(t) { return el("p", "giai", t); }

  /* ── SÁU TRẠNG THÁI — bảng dịch duy nhất ──────────────────────────
   * Backend nói `GIAY`/`QUAN_SAT`; sổ engine nói `CHAN`/`DA_DUNG`. Người
   * dùng không nên phải học hai từ điển, nên chúng quy về MỘT hệ sáu
   * trạng thái, và mỗi trạng thái có đúng một màu.                    */
  var TT = {
    LIVE:    { ten: "Tiền thật",   giai: "đang đặt lệnh thật" },
    PAPER:   { ten: "Sổ giấy",     giai: "đủ vốn, nhưng chỉ ghi sổ — chưa có lớp ký lệnh" },
    OBSERVE: { ten: "Quan sát",    giai: "quét được, nhưng vốn chưa tới ngưỡng kinh tế của nó" },
    BLOCKED: { ten: "Bị chặn",     giai: "thiếu hạ tầng, chưa dựng được" },
    FAULT:   { ten: "Đang lỗi",    giai: "lượt quét gần nhất ném lỗi" },
    OFF:     { ten: "Đã tắt",      giai: "không chạy trong vòng này" }
  };
  function cot(tt) {
    var c = el("span", "cot " + tt, (TT[tt] || {}).ten || tt);
    c.title = (TT[tt] || {}).giai || "";
    return c;
  }

  /* ── ĐỘNG CƠ: gộp ty đang chạy + engine chưa dựng ─────────────────
   * Mười ba luồng của bản đồ, một danh sách. Chín ty có thật đọc từ
   * `trungUong`; ba engine còn chặn đọc từ sổ `dongCoChuaCo`; Router là
   * hạ tầng nên nó KHÔNG nằm ở đây — nó không xin vốn.               */
  var TEN_DEP = {
    "perpetual.funding_spread.v1": ["Chênh funding perp", "so bốn sàn perp, thu tại mốc kết toán"],
    "basis.cash_carry.v1":         ["Cash-and-carry", "mua giao ngay, bán khống perp cùng sàn"],
    "options.put_call_parity.v1":  ["Ngang giá quyền chọn", "đẳng thức call/put trên Deribit"],
    "lending.rate_rotation.v1":    ["Xoay lãi cho vay", "chuyển vốn giữa thị trường cho vay"],
    "yield.pendle_pt.v1":          ["Lãi cố định Pendle", "PT khoá tới ngày đáo hạn"],
    "stablecoin.cross_venue.v1":   ["Chênh stablecoin", "lệch giá giữa hai sàn giao ngay"],
    "dex.round_trip.v1":           ["Vòng đổi DEX", "đổi A→B→A trên cùng một chuỗi"],
    "amm.fee_farming.v1":          ["Cấp thanh khoản AMM", "phí AMM, chỉ nhận cặp neo nhau"],
    "amm.v3_range.v1":             ["Bể thanh khoản V3", "dải giá trên cặp biến động, chỉ khi đo được σ — trang riêng: /be-thanh-khoan"],
    "prediction.polymarket.v1":    ["Thị trường tiên đoán", "đọc từ Khâm Thiên Giám, không định giá lại"]
  };
  var TEN_CHAN = {
    "thanh-ly":   ["Săn thanh lý", "mua tài sản thế chấp giá chiết khấu"],
    "jit":        ["Thanh khoản JIT", "bơm thanh khoản đúng một block"],
    "mev":        ["Tìm kiếm MEV", "chênh lệch nguyên tử trong một block"],
    "dex-arb":    ["Chênh lệch DEX", ""],
    "lp-v3":      ["Cấp thanh khoản", ""],
    "quyen-chon": ["Quyền chọn", ""]
  };

  function dsDongCo() {
    var t = (S && S.trungUong) || {}, ra = [];
    var theoMa = {};
    (t.ty || []).forEach(function (x) { theoMa[x.ma] = x; });
    (t.cheTy || []).forEach(function (c) {
      var n = theoMa[c.ma] || {}, tt;
      if (n.loiCuoi) tt = "FAULT";
      else if (c.che === "THAT") tt = "LIVE";
      else if (c.che === "GIAY") tt = "PAPER";
      else tt = "OBSERVE";
      var d = TEN_DEP[c.ma] || [c.ma, ""];
      ra.push({
        ma: c.ma, ten: d[0], mo: d[1], ho: c.ho, tt: tt, dung: true,
        soQuet: n.soLuotQuet, soCoHoi: n.soCoHoi, soQua: n.soQuaCongTy,
        soTrinh: n.soTrinh, loi: n.loiCuoi,
        soBiTuChoi: n.soBiTuChoi, soMaBiBo: n.soMaBiBo,
        soMaThieuCau: n.soMaThieuCau,
        lyDoCongTy: n.lyDoTuChoi,
        nguong: c.vonToiThieuUsd, tran: c.tranMotCoHoiUsd, vi: c.vi
      });
    });
    var dc = (S && S.dongCoChuaCo) || {}, chan = (dc.theoTrangThai || {}).CHAN || [];
    chan.forEach(function (ma) {
      var d = TEN_CHAN[ma] || [ma, ""];
      ra.push({ ma: ma, ten: d[0], mo: d[1], ho: "—", tt: "BLOCKED", dung: false });
    });
    return ra;
  }

  /* ── VIỆC CẦN NGƯỜI ───────────────────────────────────────────────
   * Hệ này cố ý giữ người trong vòng kiểm soát, nên phải có một chỗ nói
   * thẳng "cái gì đang chờ tôi". Không có việc gì cũng phải nói ra —
   * im lặng đọc thành "chưa kiểm tra".                                */
  function dsViec() {
    var t = (S && S.trungUong) || {}, ra = [];
    var cd = t.cauDao || {};
    (cd.lyDo || []).forEach(function (l) {
      ra.push({
        nang: true, ten: "Cầu dao NGẮT · " + l.ma, mo: l.moTa,
        lam: l.tuMo ? "Tự đóng lại khi điều kiện hết — không cần ai."
                    : "Phải có NGƯỜI đóng lại: máy không phân biệt được "
                      + "«sự cố đã qua» với «sự cố vẫn còn nhưng tín hiệu tạm im»."
      });
    });
    (t.vonNgoai || []).forEach(function (v) {
      if (!v.docDuoc) ra.push({
        nang: true, ten: "Không đọc được vốn ngoài · " + v.ten,
        mo: v.vi || "", lam: "NAV đang thiếu một phần chưa biết bao nhiêu."
      });
    });
    (t.ty || []).forEach(function (x) {
      if (x.loiCuoi) ra.push({
        nang: true, ten: "Ty ném lỗi · " + x.ma, mo: String(x.loiCuoi),
        lam: "Ty này không nộp được tờ trình nào trong vòng vừa rồi."
      });
    });
    var lt = t.lechTien || {};
    if (lt.khop === false) ra.push({
      nang: true,
      ten: "Sổ tiền LỆCH danh mục · " + tien(lt.lechUsd, 6),
      mo: lt.vi || "",
      lam: "Có đường dịch tiền KHÔNG đi qua `_ghi_tien`, nên sổ cái thiếu "
           + "mất nó. Mọi con số lãi lỗ đọc từ sổ đang sai đúng khoản ấy."
    });
    var kt3 = t.keToan || {};
    if (kt3.soKhongCoKeToan) ra.push({
      nang: false,
      ten: "Vốn KHÔNG được kế toán · " + kt3.soKhongCoKeToan + " vị thế · "
           + tien(kt3.vonKhongDuocKeToanUsd, 0),
      mo: "Ty của những vị thế này chưa cài `ke_toan()`, nên lãi lỗ của "
          + "phần vốn ấy KHÔNG được biết — không phải bằng 0.",
      lam: "Cài `ke_toan()` cho ty ấy, hoặc đừng cấp vốn cho nó nữa. NAV "
           + "hiện đang thiếu một khoản chưa biết bao nhiêu."
    });
    (kt3.loi || []).forEach(function (m) {
      ra.push({ nang: true, ten: "Kế toán vị thế ném lỗi", mo: String(m),
                lam: "Vị thế ấy không được cộng lãi lỗ vòng này." });
    });
    var ds = t.doiSoatViThe || {};
    if (ds.lech) ra.push({
      nang: !!ds.canNguoi,
      ten: "Vị thế mồ côi · " + (ds.soConMoCoi || 0) + " tờ"
           + (ds.vonMoCoiUsd == null ? "" : " · " + tien(ds.vonMoCoiUsd)),
      mo: "Sổ đăng ký ghi là ĐANG MỞ, danh mục không giữ chân nào — nên vốn "
          + "ấy nằm ngoài mọi phép tính trần.",
      lam: ds.canNguoi
        ? "Lớp thực thi chạy TIỀN THẬT: phải đối soát với sàn rồi đóng tay. "
          + "Máy không tự đóng."
        : "Bấm «Đối soát vị thế» ở thanh dưới — vị thế mô phỏng, đóng ở sổ "
          + "kèm bút toán là ghi đúng cái đã xảy ra."
    });
    var nc = (S && S.nguonCau) || {};
    if (nc.dangNghi) ra.push({
      nang: false, ten: "Nguồn cầu nối đang nghỉ vì hạn mức",
      mo: "Còn " + Math.round((nc.conNghiGiay || 0) / 60) + " phút · đã dính 429 "
          + (nc.soLan429 || 0) + " lần",
      lam: "Mọi tuyến liên chuỗi MỜ tới lúc ấy; các ty giữ nguyên khai báo phí còn thiếu."
    });
    var r = (S && S.router) || {};
    (r.chuoiCoGasNhungThieuGia || []).forEach(function (c) {
      ra.push({ nang: false, ten: "Chuỗi " + c + " đọc được gas nhưng thiếu giá token gốc",
                mo: "Mọi tuyến qua chuỗi này đang mờ.",
                lam: "Thêm token trả gas vào danh sách quét." });
    });
    if (S && S.loiVongCuoi) ra.push({
      nang: true, ten: "Vòng gần nhất có lỗi", mo: String(S.loiVongCuoi), lam: ""
    });
    return ra;
  }

  /* ══════════════════ TRANG: TRUNG TÂM ══════════════════════════ */
  function ve_trung_tam() {
    var f = document.createDocumentFragment();
    var t = (S && S.trungUong) || {}, dm = t.danhMuc || {}, hn = t.hieuNang || {};
    var cd = t.cauDao || {}, lat = t.latCatVong || {}, dc = dsDongCo();

    /* — BÂY GIỜ: một câu, đọc trước mọi con số —
     * Bảng số nói "bao nhiêu"; câu này nói "đang xảy ra chuyện gì". Người
     * mở buồng lái ra lúc 2 giờ sáng cần câu thứ hai trước. */
    f.appendChild(cauBayGio(t, lat, dc));

    /* — tám câu hỏi, năm ô — */
    var k1 = khoi("Tám câu hỏi, mười giây");
    var d1 = el("div", "day-so");
    d1.appendChild(oSo("Tổng vốn (NAV)", tien(dm.navUsd),
      dm.ngoaiDayDu ? "đã gồm vốn ngoài · đầy đủ" : "⚠ THIẾU vốn ngoài",
      dm.ngoaiDayDu ? null : "am"));
    d1.appendChild(oSo("Vốn đang dùng", tien(dm.daCamKetUsd),
      so((dm.tiLeDungVon || 0) * 100, 1) + "% NAV · " + (dm.soViThe || 0) + " vị thế"));
    d1.appendChild(oSo("Tiền rảnh", tien(dm.tienMatUsd), "chưa cam kết cho cơ hội nào"));
    var laiLo = hn.duDeKetLuan
      ? oSo("Lời / lỗ", phan(hn.laiLoPhanTram), "từ đầu · đã đủ dữ liệu",
            (hn.laiLoPhanTram || 0) >= 0 ? "duong" : "am")
      : oSo("Lời / lỗ", "chưa kết luận", (hn.vi || "").slice(0, 64), "nhat", true);
    d1.appendChild(laiLo);
    d1.appendChild(oSo("Cầu dao", cd.dangNgat ? "ĐANG NGẮT" : "Đóng",
      cd.dangNgat ? (cd.lyDo || []).map(function (l) { return l.ma; }).join(", ")
                  : "đã ngắt " + (cd.soLanNgat || 0) + " lần từ đầu",
      cd.dangNgat ? "am" : "duong", true));
    k1.appendChild(d1);
    f.appendChild(k1);

    /* — hai cột: máy đang làm gì · việc cần người — */
    var k2 = el("div", "hai-cot");
    k2.style.marginBottom = "26px";

    var hMach = hop("Cỗ máy đang làm gì", el("span", "so-nho",
      "vòng " + (S.vong || "—")));
    hMach.noi.appendChild(veMach(lat, cd, dc));
    hMach.noi.appendChild(giai(
      "Vòng chạy mỗi " + (S.nhipGiay || 30) + " giây. Cầu dao đứng TRƯỚC phân bổ "
      + "— chặn trước khi cam kết đồng nào, không phải sau."));
    k2.appendChild(hMach);

    var viec = dsViec();
    var hViec = hop("Cần tôi xử lý", el("span", "so-nho",
      viec.length ? viec.length + " việc" : "không có"));
    var dv = el("div", "viec");
    if (!viec.length) {
      dv.appendChild(el("div", "viec-khong",
        "Không có việc nào đang chờ người. Máy tự chạy được."));
    } else {
      viec.forEach(function (v) {
        var b = el("div", "viec-1" + (v.nang ? "" : " nhe"));
        b.appendChild(el("b", null, v.ten));
        if (v.mo) b.appendChild(el("span", null, v.mo));
        if (v.lam) b.appendChild(el("span", null, v.lam));
        dv.appendChild(b);
      });
    }
    hViec.noi.appendChild(dv);
    k2.appendChild(hViec);
    f.appendChild(k2);

    /* — mười ba động cơ — */
    var k3 = khoi("Mười ba động cơ",
      "Chín ty đang chạy, ba engine còn chặn vì thiếu dữ liệu không công khai, "
      + "và một hạ tầng (Router chuyển vốn) không nằm ở đây vì nó không xin vốn.");
    k3.appendChild(veLuoiDongCo(dc));
    f.appendChild(k3);

    /* — vốn ở đâu · cơ hội thành tiền — */
    var k4 = el("div", "hai-cot");
    k4.style.marginBottom = "26px";
    var hVon = hop("Vốn đang ở đâu", el("a", "so-nho", "xem đủ →"));
    hVon.querySelector("a").href = "/von";
    hVon.querySelector("a").setAttribute("data-lien", "");
    hVon.noi.appendChild(veCayVon(dm));
    k4.appendChild(hVon);

    var hPheu = hop("Cơ hội → tiền", el("span", "so-nho", "từ đầu"));
    hPheu.noi.appendChild(vePheu(t.pheuDayDu || {}));
    k4.appendChild(hPheu);
    f.appendChild(k4);

    /* — hoạt động gần đây — */
    var k5 = khoi("Hoạt động gần đây");
    k5.appendChild(veNhatKyNgan());
    f.appendChild(k5);
    return f;
  }

  /* Câu tường thuật. Dựng từ dữ liệu chứ không phải một câu cố định —
   * một câu cố định thì đọc lần thứ hai đã thành trang trí, và trang trí
   * ở buồng lái là thứ che mất chỗ đáng lẽ nói điều gì đó. */
  function cauBayGio(t, lat, dc) {
    var cd = t.cauDao || {}, dm = t.danhMuc || {};
    var tho = 0;
    (t.ty || []).forEach(function (x) { tho += x.soCoHoi || 0; });
    var chay = dc.filter(function (x) { return x.dung; }).length;
    var loi = dc.filter(function (x) { return x.tt === "FAULT"; }).length;

    var c = [];
    c.push("Vòng " + (S.vong != null ? S.vong : "—") + ", nhịp "
           + (S.nhipGiay || 30) + " giây: " + chay + " động cơ vừa quét xong "
           + "và cân " + so(tho) + " cơ hội, "
           + so(lat.soToTrinhNhan || 0) + " tờ trình lên tới Trung Ương.");
    if (loi) c.push(loi + " động cơ đang NÉM LỖI.");
    if (cd.dangNgat) {
      c.push("Cầu dao ĐANG NGẮT ("
             + (cd.lyDo || []).map(function (l) { return l.ma; }).join(", ")
             + ") nên không đồng nào được cam kết trong vòng này — máy vẫn "
             + "quét, vẫn ghi nhận, chỉ không tiêu tiền.");
    } else if (lat.phanBo && lat.phanBo.soCap) {
      c.push("Phân Bổ vừa cấp " + tien(lat.phanBo.tongCapUsd) + " qua "
             + lat.phanBo.soCap + " lần, xét lại trần sau mỗi lần.");
    } else {
      c.push("Cầu dao đóng và không tờ nào được cấp vốn — trần chặn trước "
             + "khi tiền cạn, không phải vì hết tiền.");
    }
    c.push("Tiền rảnh " + tien(dm.tienMatUsd) + " trên NAV " + tien(dm.navUsd)
           + (dm.ngoaiDayDu ? "." : ", và NAV đang THIẾU phần vốn ngoài "
              + "chưa đọc được."));

    var d = el("p", "bay-gio");
    d.appendChild(el("b", null, "BÂY GIỜ"));
    d.appendChild(el("span", null, c.join(" ")));
    return d;
  }

  /* mạch: chín chặng, chặng đang chặn thì đỏ */
  function veMach(lat, cd, dc) {
    var ngat = !!cd.dangNgat;
    var pb = lat.phanBo || {};
    var soChay = lat.soTyChay != null ? lat.soTyChay : (dc || []).filter(
      function (x) { return x.dung; }).length;
    var chang = [
      { ten: "Quét", phu: "chín ty đọc nguồn công khai", dem: soChay + " ty" },
      { ten: "Cổng ty", phu: "mỗi ty tự loại cơ hội của mình",
        dem: (lat.soToTrinhNhan != null ? lat.soToTrinhNhan : "—") + " tờ trình" },
      { ten: "Sổ đăng ký", phu: "ghi nhận, bỏ trùng theo dấu vân",
        dem: (lat.soGhiNhan != null ? lat.soGhiNhan : "—") + " ghi · "
             + (lat.soBoTrung || 0) + " trùng" },
      { ten: "Vốn ngoài → NAV", phu: "đọc cỗ máy khác TRƯỚC khi tính trần", dem: "" },
      { ten: "Cầu dao", phu: ngat ? (cd.lyDo || []).map(function (l) { return l.ma; }).join(", ")
                                  : "không có điều kiện nào bật",
        dem: ngat ? "NGẮT" : "đóng", chan: ngat },
      { ten: "Rủi ro tổng → Phân bổ", phu: "cấp TUẦN TỰ, xét lại trần sau mỗi lần",
        dem: tien(pb.tongCapUsd) + " · " + (pb.soCap || 0) + " lần" },
      { ten: "Thực thi", phu: "mô phỏng — lớp ký lệnh chưa tồn tại",
        dem: (lat.soThucThi || 0) + " lệnh" },
      { ten: "Sổ cái", phu: "chỉ-thêm, sửa bằng bút toán đảo",
        dem: so(((S.trungUong || {}).soCai || {}).soButToan) + " bút toán" }
    ];
    var m = el("div", "mach");
    chang.forEach(function (c, i) {
      var d = el("div", "chang " + (c.chan ? "chan" : "xong"));
      d.appendChild(el("span", "cham", String(i + 1)));
      var g = el("div");
      g.appendChild(el("div", "ten", c.ten));
      g.appendChild(el("div", "phu", c.phu));
      d.appendChild(g);
      d.appendChild(el("span", "dem", c.dem));
      m.appendChild(d);
    });
    return m;
  }

  function veLuoiDongCo(dc) {
    var l = el("div", "luoi-dc");
    dc.forEach(function (x) {
      var a = el("a", "the-dc");
      a.href = "/dong-co/" + x.ma;
      a.setAttribute("data-lien", "");
      a.dataset.tt = x.tt;
      a.appendChild(cot(x.tt));
      a.appendChild(el("div", "ten-dc", x.ten));
      /* Thẻ nói MỘT câu. Câu đầy đủ của backend dài tới mức lặp sáu lần
         thì thành một bức tường chữ, và tường chữ thì không ai đọc — nên
         nó xuống `title`, còn thẻ giữ đúng phần người ta cần liếc. */
      var lam = el("div", "lam", x.dung ? lamGon(x)
        : "Chưa dựng được — " + (x.mo || "thiếu hạ tầng"));
      if (x.vi) lam.title = x.vi;
      a.appendChild(lam);
      var n = el("div", "day-nho");
      if (x.dung) {
        n.appendChild(nho("quét", so(x.soQuet)));
        n.appendChild(nho("cơ hội", so(x.soCoHoi)));
        n.appendChild(nho("qua cổng", so(x.soQua)));
        n.appendChild(nho("ngưỡng", tien(x.nguong, 0)));
      } else {
        n.appendChild(nho("vốn", "$0"));
        n.appendChild(nho("vị thế", "0"));
      }
      a.appendChild(n);
      l.appendChild(a);
    });
    return l;
  }
  function lamGon(x) {
    if (x.tt === "FAULT") return "Lượt quét gần nhất ném lỗi — xem chi tiết.";
    if (x.tt === "OBSERVE")
      return "Cần " + tien(x.nguong, 0) + " · vốn hiện chỉ rót được "
             + tien(x.tran, 0) + ". Nó TỪ CHỐI xin một nửa.";
    if (x.tt === "PAPER")
      return (x.mo || "") + " — đủ vốn, nhưng chỉ ghi sổ giấy.";
    return x.mo || "";
  }

  function nho(t, v) {
    var s = el("span", null, t + " ");
    s.appendChild(el("b", null, v));
    return s;
  }

  function veCayVon(dm) {
    var c = el("div", "cay");
    function canh(ten, gt, con) {
      var d = el("div", "canh-cay" + (con ? " con" : ""));
      d.appendChild(el("span", null, ten));
      d.appendChild(el("span", "tien", gt));
      c.appendChild(d);
    }
    canh("TỔNG NAV", tien(dm.navUsd));
    canh("tự quản", tien(dm.tuQuanUsd), true);
    canh("vốn ngoài (cỗ máy khác)", tien(dm.ngoaiUsd)
      + (dm.ngoaiDayDu ? "" : " ⚠"), true);
    canh("Tiền rảnh", tien(dm.tienMatUsd));
    canh("Đã cam kết", tien(dm.daCamKetUsd));
    var pn = dm.phoiNhiemCang || {};
    var ten = Object.keys(pn);
    if (ten.length) {
      ten.forEach(function (k) { canh(k, tien(pn[k]), true); });
    } else {
      var d = el("div", "canh-cay con");
      d.appendChild(el("span", null,
        "chưa vị thế nào mở, nên chưa có phơi nhiễm theo cảng"));
      d.appendChild(el("span", "tien", "—"));
      c.appendChild(d);
    }
    return c;
  }

  function vePheu(p) {
    var nac = p.nac || [];
    if (!nac.length) return giai("chưa có số liệu phễu");
    var lon = Math.max.apply(null, nac.map(function (n) { return n.so || 0; })) || 1;
    var d = el("div", "pheu");
    nac.forEach(function (n, i) {
      var r = el("div", "nac" + (i === nac.length - 1 ? " cuoi" : ""));
      r.appendChild(el("span", "ten", nhanNac(n.ten)));
      var t = el("span", "thanh"), b = el("i");
      /* thang LOGARIT: vẽ tuyến tính thì mọi nấc sau nấc đầu thành một
         vạch không nhìn thấy, và cái không nhìn thấy được thì không ai đọc. */
      b.style.width = (n.so > 0
        ? Math.max(2, Math.log10(n.so + 1) / Math.log10(lon + 1) * 100) : 0) + "%";
      t.appendChild(b); r.appendChild(t);
      var e = el("span", "dem", so(n.so));
      e.appendChild(el("span", null, ((n.tiLe || 0) * 100).toFixed(
        (n.tiLe || 0) < 0.001 ? 5 : 2) + "%"));
      r.appendChild(e);
      d.appendChild(r);
    });
    var w = el("div");
    w.appendChild(d);
    w.appendChild(giai("Thang LOGARIT. Đọc từ PHẢI sang TRÁI: cột đầu trừ cột "
      + "cuối là số cơ hội bị TỪ CHỐI — và từ chối giỏi quan trọng hơn phát "
      + "hiện nhiều."));
    /* VÌ SAO, không chỉ BAO NHIÊU. Một họ có 2115 cơ hội mà không được đồng
       nào: «cổng ty quá chặt» và «hết chỗ vì trần vị thế» trông giống hệt
       nhau nếu chỉ nhìn con số 0 — mà hai cái ấy sửa bằng hai việc khác
       hẳn. */
    var ho = (p.theoHo || []).filter(function (h) {
      return (h.lyDoTuChoi || []).length;
    });
    if (ho.length) {
      var kl = el("div", "vi-sao-tu-choi");
      kl.appendChild(el("h4", null, "Vì sao bị từ chối — theo họ"));
      ho.forEach(function (h) {
        var r = el("div", "viec-1 nhe");
        r.appendChild(el("b", null, h.ho + " · " + so(h.coHoiTho)
          + " cơ hội thô → " + so(h.daCapVon) + " lần được cấp vốn"));
        var phu = 0;
        h.lyDoTuChoi.forEach(function (x) {
          phu += x.so || 0;
          r.appendChild(el("span", null, "× " + so(x.so) + "  " + x.lyDo
            + (x.soCauKhac > 1 ? "   (gộp " + so(x.soCauKhac) + " câu)" : "")));
        });
        /* Mẫu số, vì không có nó thì mấy dòng trên đọc như «đây là tất
           cả». Đo 30/08: năm mã đứng đầu của họ tín dụng phủ 1.561 trên
           2.305 lần từ chối — hai phần ba, không phải tất cả. */
        if (h.soTuChoi) {
          r.appendChild(el("span", "nhat", "— mấy mã trên phủ " + so(phu)
            + "/" + so(h.soTuChoi) + " lần từ chối"));
        }
        kl.appendChild(r);
      });
      w.appendChild(kl);
      w.appendChild(giai("Gộp theo MÃ, không theo CÂU. Câu có SỐ nhúng bên "
        + "trong (`khoá vốn 2455 giờ`), nên gộp theo câu thì MỘT nguyên nhân "
        + "vỡ thành hàng chục dòng đếm 2–3 lần, và cái đang chặn 90% số cơ "
        + "hội biến mất khỏi bảng. Đo 30/08: 2.527 lần từ chối, 306 câu, "
        + "đúng 5 mã."));
    }
    return w;
  }
  function nhanNac(t) {
    return ({ coHoiTho: "Cơ hội thô", quaCongTy: "Qua cổng ty",
              DUYET_RUI_RO: "Qua Rủi Ro Tổng", DA_CAP_VON: "Đã cấp vốn",
              DA_MO: "Đã mở vị thế", DA_DONG: "Đã đóng" })[t] || t;
  }

  function veNhatKyNgan() {
    var d = el("div", "nhat-ky");
    var dong = (NHAT_KY && NHAT_KY.dong) || [];
    if (!dong.length) {
      d.appendChild(giai(LOI_NHAT_KY
        ? "KHÔNG đọc được nhật ký: " + LOI_NHAT_KY
          + " — máy vẫn chạy, chỉ ô này mù."
        : "nhật ký còn trống"));
      return d;
    }
    dong.slice(-12).reverse().forEach(function (x) {
      var r = el("div", "dong-nk " + (x.loai === "canh" ? "canh"
        : x.loai === "loi" ? "loi" : ""));
      var t = el("time", null, String(x.luc || "").slice(11, 19));
      r.appendChild(t);
      r.appendChild(el("span", null, x.muc || ""));
      d.appendChild(r);
    });
    return d;
  }

  /* ══════════════════ TRANG: ĐỘNG CƠ ════════════════════════════ */
  function ve_dong_co() {
    var f = document.createDocumentFragment();
    var dc = dsDongCo();
    var k = khoi("Mười ba động cơ",
      "Trạng thái quy về SÁU, và mỗi trạng thái một màu cố định. "
      + "Bấm vào một thẻ để mở tầng chi tiết của động cơ ấy.");
    k.appendChild(veLuoiDongCo(dc));
    f.appendChild(k);

    var k2 = khoi("Sáu trạng thái nghĩa là gì");
    var h = [];
    Object.keys(TT).forEach(function (t) {
      h.push([{ el: cot(t) }, { t: TT[t].giai },
              { t: String(dc.filter(function (x) { return x.tt === t; }).length), c: "n" }]);
    });
    k2.appendChild(bang([{ t: "Trạng thái" }, { t: "Nghĩa là" },
                         { t: "Bao nhiêu", n: true }], h));
    f.appendChild(k2);

    var d = (S && S.dongCoChuaCo) || {};
    if (d.loiNhac) {
      var k3 = khoi("Vì sao ba engine còn chặn");
      k3.appendChild(giai(d.loiNhac));
      k3.appendChild(giai("Đọc đủ kèm từng điều kiện: "
        + "curl -s localhost:" + (location.port || "5188")
        + "/api/dong-co-chua-co?day_du=true"));
      f.appendChild(k3);
    }
    return f;
  }

  /* ══════════════════ TRANG: VỐN ════════════════════════════════ */
  function ve_von() {
    var f = document.createDocumentFragment();
    var t = (S && S.trungUong) || {}, dm = t.danhMuc || {};
    var k = khoi("Bản đồ vốn", dm.loiNhac || "");
    var d = el("div", "day-so");
    d.appendChild(oSo("NAV", tien(dm.navUsd),
      dm.navLaVonGoc ? "vẫn bằng vốn gốc" : "đã đổi so với vốn gốc"));
    d.appendChild(oSo("Tự quản", tien(dm.tuQuanUsd), "phần Thị Bạc Ty quản"));
    d.appendChild(oSo("Vốn ngoài", tien(dm.ngoaiUsd),
      dm.ngoaiDayDu ? "đọc được đầy đủ" : "⚠ CHƯA đầy đủ",
      dm.ngoaiDayDu ? null : "am"));
    d.appendChild(oSo("Tỉ lệ dùng vốn", so((dm.tiLeDungVon || 0) * 100, 1) + "%",
      (dm.soViThe || 0) + " vị thế đang mở"));
    k.appendChild(d);
    f.appendChild(k);

    /* VỐN KHẢ DỤNG NẰM KHÔNG. Mẫu số là vốn khả dụng — NAV trừ dự trữ —
       chứ không phải NAV. Dự trữ là một lựa chọn có chủ ý; tính nó vào
       phần «nằm không» là buộc tội cỗ máy vì chính luật ta đặt ra.

       Đo làn thật 30/08: dùng vốn 56% trên NAV, nghe không tệ. Cùng con
       số ấy trên phần KHẢ DỤNG là 70%, và 30% còn lại — 239.071 USD —
       đang ăn 0%. Lợi suất 4,30%/năm trên vốn đang dùng, quy về NAV còn
       2,41%. Gần một nửa lợi suất mất ở chỗ này. */
    var vr = t.vonRanh || {};
    if (vr.khaDungUsd != null) {
      var kvr = khoi("Vốn khả dụng có đang làm việc không",
        "Dự trữ đã trừ ra rồi. Phần còn lại mà vẫn nằm im thì không ai "
        + "chọn cả — nó chỉ đơn giản là không vào được chỗ nào.");
      var dvr = el("div", "day-so");
      dvr.appendChild(oSo("Khả dụng", tien(vr.khaDungUsd, 0),
        "NAV trừ dự trữ " + so((vr.tiLeDuTru || 0) * 100, 0) + "%"));
      dvr.appendChild(oSo("Đang làm việc", tien(vr.dangDungUsd, 0),
        vr.tiLeRanhTrenKhaDung == null ? "—"
          : so((1 - vr.tiLeRanhTrenKhaDung) * 100, 1) + "% phần khả dụng"));
      dvr.appendChild(oSo("NẰM KHÔNG", tien(vr.ranhNgoaiDuTruUsd, 0),
        vr.tiLeRanhTrenKhaDung == null ? "chưa chia được"
          : so(vr.tiLeRanhTrenKhaDung * 100, 1) + "% phần khả dụng · ăn 0%",
        (vr.tiLeRanhTrenKhaDung || 0) >= 0.25 ? "am" : "nhat"));
      dvr.appendChild(oSo("Lợi suất trên vốn DÙNG",
        vr.loiSuatTrenVonDungPhanTram == null ? "—"
          : phan(vr.loiSuatTrenVonDungPhanTram),
        "gia quyền theo VỐN-GIỜ, không phải trung bình các ty"));
      dvr.appendChild(oSo("Quy về NAV",
        vr.loiSuatQuyVeNavPhanTram == null ? "—"
          : phan(vr.loiSuatQuyVeNavPhanTram),
        vr.loiSuatNeuLapDayPhanTram == null ? "—"
          : "lấp đầy phần khả dụng thì tới "
            + phan(vr.loiSuatNeuLapDayPhanTram)));
      kvr.appendChild(dvr);
      if (vr.soTyChuaDoDuocLoiSuat) {
        kvr.appendChild(giai(vr.soTyChuaDoDuocLoiSuat + " ty chưa đo được "
          + "lợi suất nên KHÔNG nằm trong hai con số trên — chúng bị bỏ "
          + "khỏi cả tử lẫn mẫu, không bị coi là 0%."));
      }
      kvr.appendChild(giai("Con số «lấp đầy» là TRẦN TRÊN của phần đang bỏ "
        + "lỡ, không phải số sẽ thu được: phần nằm không thường nằm không "
        + "vì những cơ hội còn lại tệ hơn, hoặc vì một trần đang chặn "
        + "trước khi tiền cạn. Xem phễu để biết trần nào."));
      /* GHẾ, chứ không TIỀN. Câu trên nói «hoặc vì một trần đang chặn» mà
         không nói trần nào — và trần ấy đo được. Đo làn thật 30/08: ghế
         đầy 120/120 trong khi 222.757 USD nằm ngoài dự trữ ăn 0%, trung
         vị một ghế giữ 1.136 USD trên phần chia công bằng 6.666. Thứ khan
         hiếm là CHỖ NGỒI. Ba ô này để câu hỏi ấy hỏi được — chúng KHÔNG
         khuyên nâng trần: vị thế nhỏ vì sức chứa pool nhỏ là sự thật của
         thị trường, và chỗ cân là quyết định của chủ. */
      var gv = t.gheVaVon || {};
      if (gv.soGhe && gv.soDangDung != null) {
        var dgv = el("div", "day-so");
        dgv.appendChild(oSo("Ghế đã dùng",
          so(gv.soDangDung) + " / " + so(gv.soGhe),
          gv.tiLeGheDay == null ? "—"
            : so(gv.tiLeGheDay * 100, 0) + "% · `phanBo.toiDaSoViThe`",
          (gv.tiLeGheDay || 0) >= 0.95 ? "am" : "nhat"));
        dgv.appendChild(oSo("Một ghế giữ (trung vị)",
          gv.vonTrungViMotGheUsd == null ? "—"
            : tien(gv.vonTrungViMotGheUsd, 0),
          gv.phanChiaMoiGheUsd == null ? "—"
            : "phần chia công bằng " + tien(gv.phanChiaMoiGheUsd, 0)));
        if (gv.soGheBe != null) {
          dgv.appendChild(oSo("Ghế BÉ",
            so(gv.soGheBe) + " ghế",
            "dưới " + tien(gv.nguongGheBeUsd, 0) + " · cộng lại "
              + tien(gv.vonTrongGheBeUsd, 0)
              + (gv.tiLeVonTrongGheBe == null ? ""
                 : " (" + so(gv.tiLeVonTrongGheBe * 100, 1) + "% vốn dùng)"),
            (gv.soDangDung && gv.soGheBe / gv.soDangDung >= 0.5)
              ? "am" : "nhat"));
        }
        kvr.appendChild(dgv);
        var _bt = Object.keys(gv.gheBeTheoTy || {});
        if (_bt.length) {
          kvr.appendChild(giai("Ghế bé thuộc về: " + _bt.map(function (k) {
            return (TEN_DEP[k] || [k])[0] + " " + gv.gheBeTheoTy[k];
          }).join(" · ") + ". Vị thế nhỏ vì SỨC CHỨA nhỏ là sự thật của "
            + "thị trường, không phải lỗi cấu hình — và trần ghế cũng có "
            + "lý của nó. Chỗ cân giữa hai điều ấy là quyết định của chủ."));
        }
      }
      f.appendChild(kvr);
    }

    var k2 = khoi("Vốn ở cỗ máy khác",
      "Thị Bạc Ty KHÔNG quản phần này, nhưng phải THẤY nó — nếu không thì mọi "
      + "trần tính theo NAV đều rộng hơn sự thật.");
    var ng = (dm.ngoai || []).concat(t.vonNgoai || []).filter(function (x, i, a) {
      return a.findIndex(function (y) { return y.ten === x.ten; }) === i;
    });
    k2.appendChild(bang(
      [{ t: "Nguồn" }, { t: "Đọc được" }, { t: "Chế độ" },
       { t: "Đã cam kết", n: true }, { t: "Tiền mặt", n: true }, { t: "Vị thế", n: true }],
      ng.map(function (v) {
        return [{ t: v.ten },
                { el: cot(v.docDuoc ? "PAPER" : "FAULT") },
                { t: v.che || "—" },
                { t: tien(v.daCamKetUsd), c: "n" },
                { t: tien(v.tienMatUsd), c: "n" },
                { t: String(v.soViThe != null ? v.soViThe : "—"), c: "n" }];
      })));
    f.appendChild(k2);

    var k3 = khoi("Phơi nhiễm theo lát cắt");
    var pn = [["Theo cảng", dm.phoiNhiemCang], ["Theo chuỗi", dm.phoiNhiemChuoi],
              ["Theo ty", dm.phoiNhiemTy], ["Ròng theo tài sản", dm.phoiNhiemRong],
              ["Thô theo tài sản", dm.phoiNhiemTho]];
    var co = false;
    pn.forEach(function (p) {
      var m = p[1] || {}, ks = Object.keys(m);
      if (!ks.length) return;
      co = true;
      var h = hop(p[0]);
      h.noi.appendChild(bang([{ t: "Chỗ" }, { t: "USD", n: true }],
        ks.map(function (k) { return [{ t: k }, { t: tien(m[k]), c: "n" }]; })));
      k3.appendChild(h);
    });
    if (!co) k3.appendChild(giai(
      "Chưa vị thế nào mở, nên mọi lát cắt phơi nhiễm đều rỗng. Đây là RỖNG "
      + "ĐO ĐƯỢC, khác hẳn rỗng vì không nhìn thấy."));
    f.appendChild(k3);
    return f;
  }

  /* ══════════════════ TRANG: VỊ THẾ ═════════════════════════════
   * Trang này tồn tại vì HAI sổ nói về cùng một thứ mà có thể lệch nhau,
   * và trước 28/08/2026 không chỗ nào trong buồng lái đặt chúng cạnh nhau:
   *
   *   DANH MỤC     dựng trong RAM → khởi động lại là quên
   *   SỔ ĐĂNG KÝ   nằm trên đĩa   → nó nhớ
   *
   * Lệch ấy đã có thật: 4 tờ đứng DA_MO với 500 USD đã cấp, trong khi
   * danh mục báo 0 vị thế và 0 đã cam kết. Xem `doi_soat_vi_the.py`.       */
  function ve_vi_the() {
    var f = document.createDocumentFragment();
    var t = (S && S.trungUong) || {}, dm = t.danhMuc || {};
    var ds = t.doiSoatViThe || {}, sdk = t.soDangKy || {};
    /* Bản đối soát LÚC KHỞI ĐỘNG giữ riêng: `doiSoatViThe` là lượt đo của
       vòng gần nhất, và nó ghi đè sau một nhịp. Chỉ đọc nó thì "vừa đóng
       4 tờ mồ côi, 500 USD" sống được 30 giây rồi biến mất. */
    var dk = t.doiSoatKhoiDong || {};
    var tr = sdk.theoTrangThai || {}, ph = sdk.pheu || {};

    var k = khoi("Vị thế đang mở",
      "Hai sổ nói về cùng một thứ. DANH MỤC là thứ mọi trần rủi ro tính "
      + "theo; SỔ ĐĂNG KÝ là thứ sống sót qua mỗi lần khởi động lại. Chúng "
      + "phải khớp — và ô «Mồ côi» là chỗ nói ra khi không.");
    var d = el("div", "day-so");
    d.appendChild(oSo("Danh mục đang giữ", so(dm.soViThe),
      tien(dm.daCamKetUsd) + " đã cam kết"));
    d.appendChild(oSo("Sổ ghi là ĐANG MỞ", so(tr.DA_MO || 0),
      "đã đóng " + so(ph.DA_DONG || 0) + " từ đầu"));
    var con = ds.soConMoCoi || 0;
    var daDong = (ds.daDong || []).length || (dk.daDong || []).length;
    var dsHien = (ds.daDong || []).length ? ds : dk;
    d.appendChild(oSo("Mồ côi", so(con),
      con ? "sổ mở · danh mục không giữ"
          : (daDong ? "lúc khởi động đã dọn " + daDong + " tờ"
                    : "hai sổ khớp nhau"),
      con ? "am" : "duong"));
    d.appendChild(oSo("Vốn mồ côi",
      con ? (ds.vonMoCoiUsd == null ? "KHÔNG đo được" : tien(ds.vonMoCoiUsd))
          : "—",
      con ? "nằm ngoài mọi phép tính trần" : "không có",
      con ? "am" : "nhat", ds.vonMoCoiUsd == null));
    k.appendChild(d);
    if (ds.vi) k.appendChild(giai(ds.vi));
    f.appendChild(k);

    if (!ds.lech && daDong) {
      var kx = khoi("Lúc khởi động, máy đã dọn một chỗ lệch");
      var bx = el("div", "viec-1 nhe");
      bx.appendChild(el("b", null, "Đã đóng " + daDong
        + " tờ mồ côi ở sổ"
        + (dsHien.vonDaDongUsd ? " · " + tien(dsHien.vonDaDongUsd) : "")
        + ", kèm bút toán"));
      bx.appendChild(el("span", null,
        "Chúng mở từ trước lần khởi động này. Vị thế MÔ PHỎNG không sống "
        + "qua được một lần restart — danh mục dựng lại rỗng — nên đóng "
        + "chúng ở sổ là ghi đúng cái đã xảy ra, không phải xoá dấu vết."));
      bx.appendChild(el("span", null,
        "Sổ cái nhận một bút toán DONG_VI_THE và một HOAN_VON cho mỗi tờ, "
        + "nên vẫn truy nguyên được."));
      kx.appendChild(bx);
      f.appendChild(kx);
    }

    if (ds.lech) {
      var k0 = khoi("Lệch — và vì sao nó im lặng");
      var b = el("div", "viec-1");
      b.appendChild(el("b", null, ds.canNguoi
        ? "PHẢI CÓ NGƯỜI: lớp thực thi chạy tiền thật"
        : "Vốn đã cam kết đang nằm ngoài phép tính trần"));
      b.appendChild(el("span", null,
        "Danh mục dựng lại rỗng sau mỗi lần khởi động, còn sổ đăng ký thì "
        + "nhớ. Nên phần vốn ĐÃ TIÊU biến khỏi mẫu số, và tiền rảnh trông "
        + "rộng hơn sự thật — cùng họ với «không đọc được vốn ngoài», chỉ "
        + "ngược chiều."));
      b.appendChild(el("span", null, ds.canNguoi
        ? "Máy KHÔNG tự đóng: vị thế tiền thật vẫn ở trên sàn sau khi "
          + "runtime chết, và tự đóng ở sổ là bịa ra một lần đóng chưa từng "
          + "xảy ra. Đối soát với sàn rồi đóng tay."
        : "Đây là vị thế MÔ PHỎNG — chưa từng tồn tại ngoài RAM. Bấm «Đối "
          + "soát vị thế» ở thanh dưới để đóng chúng ở sổ, kèm bút toán."));
      k0.appendChild(b);
      f.appendChild(k0);

      var k1 = khoi("Bốn cột, và cột «vốn đã cấp» đọc từ SỔ CÁI",
        "Không đọc từ tờ trình: `vonCanUsd` là vốn XIN, còn Phân Bổ thường "
        + "cấp ít hơn. Lấy số xin mà báo là vốn bị quên thì thổi phồng nó.");
      k1.appendChild(bangMoCoi(ds));
      if (ds.soKhongDoDuocVon)
        k1.appendChild(giai("Có " + ds.soKhongDoDuocVon + " tờ KHÔNG đọc "
          + "được vốn đã cấp, nên ô «Vốn mồ côi» ở trên không cộng ra tổng — "
          + "một lỗ thì cả tổng mù, không cộng vòng qua lỗ hổng."));
      f.appendChild(k1);
    }

    if (!ds.lech && daDong) {
      var kb = khoi("Những tờ đã được đóng");
      kb.appendChild(bangMoCoi(dsHien));
      f.appendChild(kb);
    }

    var kt = t.keToan || {}, sv = t.soViThe || [];
    var kk = khoi("Kế toán theo thời gian",
      "Mỗi vòng, mỗi vị thế đang mở được hỏi «thu/mất bao nhiêu kể từ vòng "
      + "trước». Ty nào chưa biết tự kế toán thì KHAI ra — vốn của nó nằm "
      + "trong NAV mà không ai cộng lãi lỗ, và im lặng chuyện đó là nói NAV "
      + "đúng trong khi nó thiếu một khoản chưa biết.");
    var dk = el("div", "day-so");
    dk.appendChild(oSo("Vị thế đang mở", so(kt.soViThe || 0),
      so(kt.soKeToanDuoc || 0) + " kế toán được vòng này"));
    dk.appendChild(oSo("Thu vòng này", tien(kt.thuUsd, 4),
      "phí " + tien(kt.phiUsd, 4)));
    dk.appendChild(oSo("Ròng vòng này", tien(kt.rongUsd, 4),
      (kt.rongUsd || 0) >= 0 ? "vào danh mục" : "ra khỏi danh mục",
      (kt.rongUsd || 0) >= 0 ? "duong" : "am"));
    dk.appendChild(oSo("KHÔNG có kế toán", so(kt.soKhongCoKeToan || 0),
      (kt.soKhongCoKeToan || 0)
        ? tien(kt.vonKhongDuocKeToanUsd, 0) + " không ai cộng lãi lỗ"
        : "mọi ty đang giữ vốn đều kế toán được",
      (kt.soKhongCoKeToan || 0) ? "am" : "duong"));
    /* «Không đo được» KHÁC «thu 0», và cỗ máy này phải nói ra cái khác
       ấy bằng số. Vòng mù nay GIỮ LẠI cửa sổ cho vòng sau đo bù — với
       thu nhập tới theo MỐC (funding 8 giờ một lần), nuốt đúng cửa sổ
       mười giây chứa mốc là nuốt tám giờ thu nhập, và sổ ghi «thu 0» y
       hệt một engine không kiếm được gì. Quá một giờ thì bỏ, và chỗ bỏ
       ấy là con số dưới đây — nó đo THU NHẬP ĐÃ MẤT, không đo lỗi. */
    dk.appendChild(oSo("Vòng MÙ · giữ lại",
      so(kt.soMuGiuLai || 0),
      (kt.soMuGiuLai || 0)
        ? "cửa sổ chưa ghi sổ, dồn cho vòng sau đo bù"
        : "không vòng nào khai «không đo được»",
      (kt.soMuGiuLai || 0) ? "cho" : "duong"));
    if (kt.soMuBoQua || kt.gioMuBoQua) {
      dk.appendChild(oSo("Quãng ĐÃ BỎ HẲN",
        (kt.gioMuBoQua || 0).toFixed(2) + "h",
        so(kt.soMuBoQua || 0) + " cửa sổ mù quá một giờ — thu nhập trong "
        + "quãng ấy sẽ KHÔNG bao giờ vào sổ", "am"));
    }
    kk.appendChild(dk);
    if (kt.vi) kk.appendChild(giai(kt.vi));
    if (sv.length) {
      kk.appendChild(bang(
        [{ t: "Tờ trình" }, { t: "Ty" }, { t: "Vốn", n: true },
         { t: "Đã giữ", n: true }, { t: "Hạn giữ", n: true },
         { t: "Thu", n: true }, { t: "Phí", n: true },
         { t: "Lãi/lỗ", n: true }, { t: "Kế toán" }],
        sv.map(function (x) {
          return [{ t: String(x.ma).slice(0, 12) },
                  { t: (TEN_DEP[x.chienLuoc] || [x.chienLuoc])[0] },
                  { t: tien(x.vonUsd, 0), c: "n" },
                  { t: (x.daGiuGio || 0).toFixed(2) + "h", c: "n" },
                  { t: (x.giuGio || 0).toFixed(0) + "h", c: "n" },
                  { t: tien(x.thuCongDonUsd, 4), c: "n" },
                  { t: tien(x.phiCongDonUsd, 4), c: "n" },
                  { t: tien(x.laiLoUsd, 4), c: "n" },
                  { t: x.coKeToan === false ? "CHƯA CÓ"
                       : (x.soVongKhongDoDuoc ? "mù " + x.soVongKhongDoDuoc
                                                + " vòng" : "đủ") }];
        })));
      /* BẢNG NÀY BỊ CẮT. Ảnh chụp chỉ mang 40 vị thế đầu để payload khỏi
         phình, còn `soViTheDayDu` mới là số thật. Không nói ra thì người
         đọc đếm 40 dòng và kết luận cỗ máy đang giữ 40 — đo 30/08 nó
         giữ 106. Cùng cái bẫy đã cắn ở `hua-qua-dang-mo`: gộp từ danh
         sách ĐÃ CẮT rồi đem so với một con số tính trên toàn bộ. */
      if (t.soViTheDayDu != null && t.soViTheDayDu > sv.length) {
        kk.appendChild(giai("Bảng trên chỉ hiện " + so(sv.length) + " trên "
          + so(t.soViTheDayDu) + " vị thế — ảnh chụp cắt bớt cho payload "
          + "khỏi phình, và phần hiện ra chọn theo thứ tự từ điển nên "
          + "KHÔNG phải một mẫu đại diện. Mọi con số gộp phải đọc từ ô "
          + "riêng của nó, đừng cộng từ bảng này."));
      }
    }
    /* VÌ SAO, không chỉ BAO NHIÊU. Mỗi ty viết một câu mỗi vòng kế toán
       («N mốc funding trong Xh», «apyBase là số quá khứ và IL chưa đo»),
       và trước đây câu ấy bị vứt ngay sau khi đọc. Đo 30/08:
       `basis.cash_carry.v1` chạy 5.222 vòng, không vòng nào mù, thu đúng
       0,0000 USD — bảng lợi suất nói được BAO NHIÊU nhưng không nói nổi
       vì sao, và câu trả lời nằm sẵn trong câu ty ấy viết. */
    var vty = kt.viTheoTy || {};
    var mvty = Object.keys(vty);
    if (mvty.length) {
      kk.appendChild(bang(
        [{ t: "Ty" }, { t: "Kế toán vòng gần nhất nói gì" }],
        mvty.sort().map(function (k) {
          return [{ t: (TEN_DEP[k] || [k])[0] }, { t: vty[k] }];
        })));
    }
    (kt.daDong || []).forEach(function (x) {
      var b = el("div", "viec-1 nhe");
      b.appendChild(el("b", null, "Vừa đóng · "
        + (TEN_DEP[x.chienLuoc] || [x.chienLuoc])[0] + " · "
        + tien(x.laiLoUsd, 4)));
      b.appendChild(el("span", null, x.lyDo));
      kk.appendChild(b);
    });
    (kt.loi || []).forEach(function (m) {
      var b = el("div", "viec-1");
      b.appendChild(el("b", null, "Kế toán lỗi"));
      b.appendChild(el("span", null, String(m)));
      kk.appendChild(b);
    });
    f.appendChild(kk);

    var k2 = khoi("Danh mục đang giữ những chân nào");
    var vt = dm.viThe || {}, ma = Object.keys(vt);
    if (!ma.length) {
      k2.appendChild(giai(dm.soViThe
        ? "danh mục báo " + dm.soViThe + " vị thế nhưng không trả về chân nào"
        : "Danh mục KHÔNG giữ chân nào. Đây là rỗng ĐO ĐƯỢC — khác hẳn rỗng "
          + "vì không nhìn thấy. " + (dm.loiNhac || "")));
    } else {
      var hang = [];
      ma.forEach(function (m) {
        (vt[m] || []).forEach(function (c) {
          hang.push([{ t: m }, { t: (TEN_DEP[c.chienLuoc] || [c.chienLuoc])[0] },
                     { t: c.ben }, { t: c.taiSan }, { t: c.cang },
                     { t: c.chuoi || "—" }, { t: tien(c.vonUsd), c: "n" }]);
        });
      });
      k2.appendChild(bang([{ t: "Tờ trình" }, { t: "Ty" }, { t: "Bên" },
                           { t: "Tài sản" }, { t: "Cảng" }, { t: "Chuỗi" },
                           { t: "Vốn", n: true }], hang));
    }
    f.appendChild(k2);

    var k3 = khoi("Vị thế ở cỗ máy khác",
      "Thị Bạc Ty không quản, nhưng phải THẤY — nếu không thì NAV thiếu một "
      + "phần và mọi trần rộng hơn sự thật.");
    var ng = t.vonNgoai || [];
    if (!ng.length) k3.appendChild(giai("chưa khai nguồn vốn ngoài nào"));
    else k3.appendChild(bang(
      [{ t: "Nguồn" }, { t: "Đọc được" }, { t: "Vị thế", n: true },
       { t: "Đã cam kết", n: true }, { t: "Chưa phòng hộ", n: true },
       { t: "Tuổi số liệu", n: true }],
      ng.map(function (v) {
        return [{ t: v.ten }, { el: cot(v.docDuoc ? "PAPER" : "FAULT") },
                { t: v.docDuoc ? so(v.soViThe) : "—", c: "n" },
                { t: v.docDuoc ? tien(v.daCamKetUsd) : "—", c: "n" },
                { t: v.docDuoc ? tien(v.chuaPhongHoUsd) : "—", c: "n" },
                { t: gio(v.tuoiGiay), c: "n" }];
      })));
    f.appendChild(k3);

    var k4 = khoi("Cả đời vị thế, theo sổ đăng ký");
    k4.appendChild(bang([{ t: "Nấc" }, { t: "Số", n: true }],
      [["Đã cấp vốn", ph.DA_CAP_VON], ["Đã mở", ph.DA_MO],
       ["Đã đóng", ph.DA_DONG], ["Hỏng (legging)", ph.HONG],
       ["Hết hạn", ph.HET_HAN]].map(function (x) {
        return [{ t: x[0] }, { t: so(x[1] || 0), c: "n" }];
      })));
    k4.appendChild(giai("«Đã mở» trừ «Đã đóng» phải bằng số danh mục đang "
      + "giữ. Không bằng thì phần chênh chính là ô «Mồ côi» ở trên."));
    f.appendChild(k4);
    return f;
  }

  function bangMoCoi(ds) {
    var xong = {};
    (ds.daDong || []).forEach(function (m) { xong[m] = true; });
    return bang(
      [{ t: "Mã tờ trình" }, { t: "Ty" }, { t: "Tài sản" }, { t: "Mở lúc" },
       { t: "Vốn đã cấp", n: true }, { t: "Vốn xin", n: true },
       { t: "Hiện sao" }],
      (ds.moCoi || []).map(function (x) {
        return [{ t: x.ma },
                { t: (TEN_DEP[x.chienLuoc] || [x.chienLuoc])[0] },
                { t: x.taiSan },
                { t: String(x.moLuc || "").slice(0, 16).replace("T", " ") },
                { t: x.vonDaCapUsd == null ? "KHÔNG đo được"
                                           : tien(x.vonDaCapUsd), c: "n" },
                { t: tien(x.vonXinUsd), c: "n" },
                { t: xong[x.ma] ? "đã đóng ở sổ" : "CÒN mồ côi" }];
      }));
  }

  /* ══════════════════ TRANG: CƠ HỘI ═════════════════════════════
   * Bảng cơ hội của CẢ hệ, viết bằng ngôn ngữ chung (tờ trình) chứ không
   * bằng ngôn ngữ nội bộ của một ty. Đây là chỗ trả lời "vòng vừa rồi máy
   * thấy gì, và vì sao gần như không cái nào qua".                        */
  function ve_co_hoi() {
    var f = document.createDocumentFragment();
    var t = (S && S.trungUong) || {}, lat = t.latCatVong || {};
    var tt = t.toTrinh || [], dc = dsDongCo();

    var tho = 0, qua = 0;
    (t.ty || []).forEach(function (x) {
      tho += x.soCoHoi || 0; qua += x.soQuaCongTy || 0;
    });

    var k = khoi("Vòng này máy thấy gì",
      "Bốn con số dưới đây là bốn cái sàng nối tiếp nhau. Sàng gắt là dấu "
      + "hiệu LÀNH — ở những góc cạnh tranh nhất của thị trường, từ chối "
      + "giỏi đáng giá hơn phát hiện nhiều.");
    var d = el("div", "day-so");
    d.appendChild(oSo("Cơ hội thô", so(tho), "chín ty cộng lại, vòng này"));
    d.appendChild(oSo("Qua cổng ty", so(qua),
      tho ? ((qua / tho) * 100).toFixed(2) + "% — tầng rủi ro THỨ NHẤT" : ""));
    d.appendChild(oSo("Thành tờ trình", so(tt.length),
      "viết bằng ngôn ngữ chung của Thị Bạc Ty"));
    d.appendChild(oSo("Được cấp vốn",
      lat.phanBo ? so(lat.phanBo.soCap) : "0",
      lat.cauDaoNgat ? "⚠ cầu dao NGẮT — không cam kết đồng nào"
                     : tien(lat.phanBo && lat.phanBo.tongCapUsd),
      lat.cauDaoNgat ? "am" : null));
    k.appendChild(d);
    f.appendChild(k);

    var k2 = khoi("Tờ trình vòng này — cả chín ty trong một bảng",
      "Cột «phí đủ chưa» là cột đáng đọc nhất: một tuyến có chặng không đo "
      + "được thì CẢ tuyến không đo được, và ty khai ra thay vì cộng vòng "
      + "qua lỗ hổng.");
    if (!tt.length) {
      k2.appendChild(giai("Không ty nào nộp tờ trình nào trong vòng vừa rồi. "
        + "Đây là kết quả BÌNH THƯỜNG: mọi cơ hội đã bị chính ty của nó loại "
        + "ở cổng thứ nhất."));
    } else {
      k2.appendChild(bang(
        [{ t: "Ty" }, { t: "Tài sản" }, { t: "Cảng" },
         { t: "NET bps", n: true }, { t: "Vốn xin", n: true },
         { t: "Giữ", n: true }, { t: "Rủi ro cao nhất", n: true },
         { t: "Tin cậy", n: true }, { t: "Phí đủ chưa" }],
        tt.slice(0, 60).map(function (x) {
          var rr = x.ruiRo || {};
          var thieu = (x.phiConThieu || []).length;
          return [
            { t: (TEN_DEP[x.chienLuoc] || [x.chienLuoc])[0] },
            { t: x.taiSan || "—" },
            { t: (x.cang || []).join(", ") || "—" },
            { t: x.netUocBps == null ? "—" : x.netUocBps.toFixed(2), c: "n" },
            { t: tien(x.vonCanUsd, 0), c: "n" },
            { t: gio((x.giuGio || 0) * 3600), c: "n" },
            { t: rr.caoNhat == null ? "—" : rr.caoNhat.toFixed(2), c: "n" },
            { t: x.tinCay == null ? "—" : x.tinCay.toFixed(2), c: "n" },
            { t: x.moHinhPhiDuChua ? "đủ"
                 : "THIẾU " + thieu + ": " + (x.phiConThieu || []).join(", ") }
          ];
        })));
      if (tt.length > 60)
        k2.appendChild(giai("Hiện 60 tờ đầu trong " + tt.length + " tờ."));
    }
    f.appendChild(k2);

    var k3 = khoi("Rồi chuyện gì xảy ra với chúng");
    k3.appendChild(bang([{ t: "Khâu" }, { t: "Số", n: true }, { t: "Nghĩa là" }],
      [[{ t: "Trung Ương nhận" }, { t: so(lat.soToTrinhNhan), c: "n" },
        { t: "qua Thông Chính, đúng khuôn ToTrinh" }],
       [{ t: "Ghi vào sổ đăng ký" }, { t: so(lat.soGhiNhan), c: "n" },
        { t: "được cấp một mã theo dõi được cả đời" }],
       [{ t: "Bỏ vì TRÙNG" }, { t: so(lat.soBoTrung), c: "n" },
        { t: "cùng dấu vân với một tờ vừa vào — cùng một cơ hội thấy lại, "
             + "không phải cơ hội mới" }],
       [{ t: "Cầu dao" }, { t: lat.cauDaoNgat ? "NGẮT" : "đóng", c: "n" },
        { t: (lat.lyDoNgat || []).join("; ")
             || "không điều kiện nào bật; phân bổ được phép chạy" }],
       [{ t: "Thực thi" }, { t: so(lat.soThucThi), c: "n" },
        { t: "mô phỏng — lớp ký lệnh chưa tồn tại" }]]));
    f.appendChild(k3);

    var k4 = khoi("Phễu từ đầu tới giờ");
    k4.appendChild(vePheu(t.pheuDayDu || {}));
    f.appendChild(k4);

    var vs = (S && S.viSaoTuChoi) || {};
    var kv = Object.keys(vs);
    var k5 = khoi("Vì sao bị từ chối — ty chênh funding",
      "Bảng này CHỈ của một ty: các ty khác chưa nộp bảng lý do theo mã. "
      + "Ghi rõ phạm vi còn hơn để người đọc tưởng đây là cả hệ.");
    if (!kv.length) k5.appendChild(giai("chưa có lý do nào được đếm"));
    else k5.appendChild(bang([{ t: "Lý do" }, { t: "Số lần", n: true }],
      kv.sort(function (a, b) { return vs[b] - vs[a]; }).map(function (x) {
        return [{ t: x }, { t: so(vs[x]), c: "n" }];
      })));
    f.appendChild(k5);

    var k6 = khoi("Mỗi động cơ thấy bao nhiêu");
    k6.appendChild(bang(
      [{ t: "Động cơ" }, { t: "Trạng thái" }, { t: "Quét", n: true },
       { t: "Cơ hội", n: true }, { t: "Qua cổng", n: true },
       { t: "Ngưỡng vốn", n: true }],
      dc.map(function (x) {
        return [{ t: x.ten }, { el: cot(x.tt) },
                { t: x.dung ? so(x.soQuet) : "—", c: "n" },
                { t: x.dung ? so(x.soCoHoi) : "—", c: "n" },
                { t: x.dung ? so(x.soQua) : "—", c: "n" },
                { t: x.dung ? tien(x.nguong, 0) : "—", c: "n" }];
      })));
    f.appendChild(k6);
    return f;
  }

  /* ══════════════════ TRANG: LỜI / LỖ ═══════════════════════════ */
  function ve_loi_lo() {
    var f = document.createDocumentFragment();
    var t = (S && S.trungUong) || {}, hn = t.hieuNang || {}, sc = t.soCai || {};
    var tt = (S && S.trungUong && S.trungUong.thucThi) || {};

    var k = khoi("Lời / lỗ",
      "KHÔNG trộn tiền thật với mô phỏng. Lớp ký lệnh chưa tồn tại, nên mọi "
      + "con số dưới đây đều là SỔ GIẤY.");
    var d = el("div", "day-so");
    d.appendChild(oSo("Tiền thật", "—", "chưa có giao dịch tiền thật nào", "nhat"));
    var kt2 = t.keToan || {};
    d.appendChild(oSo("Kế toán vòng này", tien(kt2.rongUsd, 4),
      (kt2.soViThe || 0) + " vị thế · "
      + ((kt2.soKhongCoKeToan || 0) ? kt2.soKhongCoKeToan + " CHƯA kế toán"
                                    : "đều kế toán được"),
      (kt2.soKhongCoKeToan || 0) ? "am" : null, true));
    /* `laiLoPhanTram` ĐO ĐƯỢC từ điểm NAV thứ hai; `duDeKetLuan` là cửa
       của CAGR (đòi ≥168 giờ). Gộp hai thứ ấy vào một ô thì một con số đã
       đo được bị giấu sau cửa của một con số KHÁC — người đọc thấy «chưa
       kết luận» và tưởng máy chưa biết gì, trong khi nó biết −0,0080%. */
    d.appendChild(oSo("Sổ giấy · lãi lỗ TAY LÁI",
      hn.laiLoPhanTram == null ? "chưa đo được" : phan(hn.laiLoPhanTram),
      hn.laiLoPhanTram == null
        ? "có đoạn NAV không dương — phép nhân chuỗi không nói được gì"
        : "đã trừ mọi đồng chủ bỏ thêm vào",
      hn.laiLoPhanTram == null ? "nhat"
        : (hn.laiLoPhanTram >= 0 ? "duong" : "am"),
      hn.laiLoPhanTram == null));
    d.appendChild(oSo("Quy ra NĂM (CAGR)",
      hn.duDeKetLuan ? phan(hn.cagrPhanTram) : "chưa kết luận",
      hn.duDeKetLuan ? "gộp từ TÍCH CHUỖI, không từ NAV cuối / NAV đầu"
                     : "cần ≥ 168 giờ dữ liệu · đang có "
                       + so(hn.soGio, 1) + "h",
      hn.duDeKetLuan ? ((hn.cagrPhanTram || 0) >= 0 ? "duong" : "am")
                     : "nhat",
      !hn.duDeKetLuan));
    /* Một con số ĐÔ-LA trần trụi là đúng thứ điều `khong-do-bang-so-do`
       cấm đọc thành điểm số. Nên nó đi kèm MẪU SỐ ngay dưới. */
    var _vdd0 = t.vonDangDung || {};
    d.appendChild(oSo("Đã thực hiện", tien(t.danhMuc && t.danhMuc.laiLoDaThucHienUsd),
      _vdd0.vonGioUsd
        ? "trên " + so(Math.round(_vdd0.vonGioUsd)) + " vốn-giờ — đọc con "
          + "số đô một mình là đọc sai thứ"
        : "ghi vào sổ cái khi đóng vị thế"));
    d.appendChild(oSo("Sụt vốn tối đa", phan(hn.sutVonToiDaPhanTram),
      hn.dangDuoiDay ? "đang dưới đỉnh" : "chưa từng xuống dưới đỉnh"));
    k.appendChild(d);
    if (hn.vi) k.appendChild(giai(hn.vi));
    f.appendChild(k);

    /* HAI mẫu số, hai câu hỏi. Máy demo rót 6.000 trên 100.000 vốn ảo: trên
       vốn TỔNG nó gần như đứng yên, trên vốn ĐANG DÙNG nó chạy ~7%/năm. Gộp
       hai câu ấy thì hoặc ta chê oan chiến lược, hoặc ta khoe một tỉ suất mà
       phần lớn vốn không hề hưởng. */
    var vd = t.vonDangDung || {};
    var kvd = khoi("Trên vốn ĐANG DÙNG — khác hẳn trên vốn tổng",
      "Tiền nằm im không lãi, nhưng nó cũng không phải lỗi của chiến lược. "
      + "Hai con số này trả lời hai câu: cỗ máy làm ăn ra sao, và chiến "
      + "lược làm ăn ra sao.");
    var dvd = el("div", "day-so");
    dvd.appendChild(oSo("Lợi suất / năm trên vốn đang dùng",
      vd.loiSuatNamPhanTram == null ? "chưa đo được" : phan(vd.loiSuatNamPhanTram),
      "thu ròng ÷ vốn-giờ",
      vd.loiSuatNamPhanTram == null ? "nhat"
        : (vd.loiSuatNamPhanTram >= 0 ? "duong" : "am"),
      vd.loiSuatNamPhanTram == null));
    dvd.appendChild(oSo("Vốn dùng bình quân",
      vd.vonBinhQuanUsd == null ? "—" : tien(vd.vonBinhQuanUsd),
      "trên " + tien(t.danhMuc && t.danhMuc.vonBanDauUsd) + " vốn ảo"));
    dvd.appendChild(oSo("Vốn-giờ đã cộng",
      so(Math.round(vd.vonGioUsd || 0)),
      (vd.soGio || 0).toFixed(1) + " giờ cửa sổ đo"));
    dvd.appendChild(oSo("Thu ròng cộng dồn", tien(vd.thuRongUsd, 4),
      "thu − phí trong kỳ, KHÔNG gồm phí vào lệnh"));
    kvd.appendChild(dvd);
    if (vd.vi) kvd.appendChild(giai(vd.vi));

    /* TÁCH THEO TY. Con số gộp trả lời «tiền đang làm việc lãi bao
       nhiêu» cho cả túi; nó KHÔNG trả lời «ty nào đang làm ra tiền» — mà
       đó mới là câu vòng tiến hoá cần. Trước lượt này câu ấy chỉ có một
       nguồn: bảng hứa-vs-thực, thứ đòi 20 lần ĐÓNG mỗi ty. Đóng thì
       hiếm; cộng dồn lãi thì mỗi vòng ba mươi giây một lần. */
    var vdt = vd.theoTy || {};
    if (Object.keys(vdt).length) {
      kvd.appendChild(bang(
        [{ t: "Ty" }, { t: "Vốn-giờ", n: true }, { t: "Thu ròng", n: true },
         { t: "%/năm trên vốn ấy", n: true }],
        Object.keys(vdt).sort(function (a, b) {
          return (vdt[b].vonGioUsd || 0) - (vdt[a].vonGioUsd || 0);
        }).map(function (k) {
          var x = vdt[k];
          return [{ t: k },
                  { t: so(x.vonGioUsd, 2), c: "n" },
                  { t: tien(x.thuRongUsd, 4),
                    c: x.thuRongUsd >= 0 ? "duong" : "am" },
                  { t: x.loiSuatNamPhanTram == null ? "chưa đo được"
                       : phan(x.loiSuatNamPhanTram),
                    c: x.loiSuatNamPhanTram == null ? "nhat"
                       : (x.loiSuatNamPhanTram >= 0 ? "duong" : "am") }];
        })));
      kvd.appendChild(giai("«chưa đo được» là chưa có vốn-giờ nào để chia, "
        + "KHÁC HẲN một tỉ suất bằng 0."));
      /* Mẫu số phải CỘNG ĐÚNG. Phép tách ra đời sau con số gộp, nên phần
         vốn-giờ tích trước đó không ty nào nhận — và nó KHÔNG chia lại
         được, vì sổ chỉ giữ tổng. Đặt tên cho nó, đừng để hai con số cạnh
         nhau mâu thuẫn. */
      if (vd.vonGioChuaTachUsd > 0) {
        kvd.appendChild(giai("Cộng lại: " + so(vd.vonGioChuaTachUsd, 0)
          + " vốn-giờ CHƯA TÁCH ĐƯỢC + " + so(vd.vonGioUsd
            - vd.vonGioChuaTachUsd, 0) + " đã tách = " + so(vd.vonGioUsd, 0)
          + " gộp. Phần chưa tách là quãng tích TRƯỚC khi phép tách này ra "
          + "đời; sổ chỉ giữ tổng nên không chia lại được. Nó teo dần theo "
          + "thời gian, và mọi vốn-giờ từ nay đều có tên ty."));
      }
    }
    f.appendChild(kvd);

    /* HẬU KIỂM trên băng — phép đo duy nhất trong cả cỗ máy dám mang tên
       ấy. Sổ giấy nói cơ hội này lãi bao nhiêu; băng nói nó ĐÃ lãi bao
       nhiêu. Hai con số ấy lệch nhau là thứ đáng đọc nhất trên trang này. */
    var th = (S && S.tienHoa) || null;
    var kth = khoi("Hậu kiểm trên BĂNG — sổ giấy nói một đằng",
      "Chạy lại toàn bộ băng đã ghi, tra funding THỰC NHẬN tại từng mốc kết "
      + "toán. Không đủ băng phía sau một cơ hội thì KHÔNG đoán — thà không "
      + "đo còn hơn đo một nửa rồi gọi đó là kết quả.");
    if (!th) {
      kth.appendChild(giai(((S && S.loiTienHoa)
        ? "lượt hậu kiểm gần nhất LỖI: " + S.loiTienHoa
        : "chưa có lượt hậu kiểm nào — lượt đầu chạy ngay khi máy lên, "
          + "rồi mỗi 6 giờ một lượt ở luồng nền")));
    } else {
      var dth = el("div", "day-so");
      dth.appendChild(oSo("Cơ hội hậu kiểm được", so(th.soDoDuoc),
        so(th.soKhungBang) + " khung băng",
        (th.soDoDuoc || 0) >= 30 ? null : "nhat"));
      dth.appendChild(oSo("Kỳ vọng THỰC",
        th.kyVongTruoc == null ? "chưa đo được"
          : th.kyVongTruoc.toFixed(2) + " bps",
        "mỗi cơ hội qua cửa",
        th.kyVongTruoc == null ? "nhat"
          : (th.kyVongTruoc >= 0 ? "duong" : "am"),
        th.kyVongTruoc == null));
      dth.appendChild(oSo("Lượt này", th.thu ? "THỬ" : "ÁP THẬT",
        th.thu ? "không vặn tham số nào" : "đã ghi vào config",
        th.thu ? "nhat" : "am", true));
      kth.appendChild(dth);
      /* Tham số tên `tc`, không phải `t`: trong cả file này `t` là
         `S.trungUong`, và một callback che mất nó làm người đọc — lẫn bộ
         kiểm «khoá trang đọc» — hiểu `t.ma` là một trường của Trung Ương. */
      (th.trieuChung || []).forEach(function (tc) {
        var b = el("div", "viec-1");
        b.appendChild(el("b", null, "TRIỆU CHỨNG · " + tc.ma));
        b.appendChild(el("span", null, tc.moTa || ""));
        kth.appendChild(b);
      });
      if (th.ghiChu) kth.appendChild(giai(th.ghiChu));
    }
    f.appendChild(kth);

    var k2 = khoi("Vì sao chưa kết luận được",
      "Quy một con số nửa ngày ra năm là bịa ra một CAGR. Hệ thống TỪ CHỐI "
      + "tính, thay vì đưa một con số đẹp mà sai.");
    k2.appendChild(bang([{ t: "Thước" }, { t: "Hiện có" }, { t: "Cần" }],
      [[{ t: "Giờ dữ liệu đường NAV" }, { t: (hn.soGio || 0).toFixed(1) + " giờ" },
        { t: "≥ 168 giờ" }],
       [{ t: "Số điểm đo" }, { t: so(hn.soDiem) }, { t: "—" }],
       [{ t: "Giao dịch tiền thật" }, { t: tt.moPhong ? "0 (mô phỏng)" : "—" },
        { t: "≥ 1" }]]));
    f.appendChild(k2);

    /* ĐƯỜNG SỨC CHỨA. Lợi suất TỤT theo quy mô, và một con số APR không
       kèm mức vốn là một con số bỏ bớt: 10 nghìn thì 20%/năm, một triệu
       thì 5,5%, năm triệu thì 1,1% vì hết chỗ chứa. Cùng một cỗ máy. */
    var dsc = t.duongSucChua || {};
    var ksc = khoi("Đường sức chứa — bỏ vào bao nhiêu thì lãi mấy phần trăm",
      "Xếp mọi cơ hội đang thấy theo lãi giảm dần rồi rót lần lượt, mỗi cơ "
      + "hội nhận nhiều nhất bằng sức chứa của nó. Đây là ẢNH CHỤP của "
      + "vòng này, không phải một lời hứa.");
    if ((dsc.muc || []).length) {
      ksc.appendChild(bang(
        [{ t: "Vốn" }, { t: "Rót được" }, { t: "Cơ hội" },
         { t: "APR phần đã rót" }, { t: "APR cả túi" }],
        dsc.muc.map(function (m) {
          var het = m.rotDuocUsd < m.vonUsd - 1;
          return [{ t: tien(m.vonUsd, 0) }, { t: tien(m.rotDuocUsd, 0),
                    c: het ? "am" : "n" },
                  { t: so(m.soCoHoi), c: "nhat" },
                  { t: so(m.aprTrenVonRot, 2) + "%", c: "n" },
                  { t: so(m.aprTrenCaTui, 2) + "%",
                    c: m.aprTrenCaTui >= 5 ? "duong" : "nhat" }];
        })));
    }
    if (dsc.vi) ksc.appendChild(giai(dsc.vi));
    if ((dsc.soBoViThieuLai || 0) + (dsc.soBoViThieuSucChua || 0)) {
      ksc.appendChild(giai("BỎ ngoài đường cong: "
        + so(dsc.soBoViThieuLai) + " cơ hội không khai lãi, "
        + so(dsc.soBoViThieuSucChua) + " không khai sức chứa. Không biết "
        + "thì không xếp vào, chứ không coi là 0."));
    }
    f.appendChild(ksc);

    /* TRẦN KHOÁ VỐN. Đường sức chứa ở trên hỏi «bao nhiêu TIỀN thì hết
       chỗ»; bảng này hỏi một câu khác hẳn: «cái trần 720 giờ đang chặn
       mất bao nhiêu LỢI SUẤT».

       Đo 30/08 trên máy sống: cùng 460k tiền mặt, 11 cơ hội và 2,48%/năm
       dưới trần — 23 cơ hội và 9,38%/năm nếu bỏ trần. Cả động cơ Pendle
       PT (12 tờ trình, khoá 88–137 ngày, NET 65–449 bps) đứng ngoài vì
       đúng một tham số.

       ĐO, KHÔNG đề xuất: nới trần là cửa `dat_tham_so`, đòi tên người. */
    var dkv = t.duongKhoaVon || {};
    if ((dkv.muc || []).length) {
      var kkv = khoi("Trần KHOÁ VỐN đang chặn mất bao nhiêu",
        "Khoá vốn lâu là từ chối mọi cơ hội tốt hơn xuất hiện trong ngần ấy "
        + "thời gian — cái giá ấy có thật, và bảng Xoay Chỗ ngay dưới là chỗ "
        + "đo nó. Bảng này chỉ đo phía bên kia: trần đang chặn những gì.");
      kkv.appendChild(bang(
        [{ t: "Trần khoá" }, { t: "Cơ hội" }, { t: "Sức chứa" },
         { t: "Rót được" }, { t: "APR cả túi" }, { t: "Khoá bình quân" }],
        dkv.muc.map(function (m) {
          var dang = m.tranGio === dkv.tranDangChayGio;
          return [{ t: (m.tranGio == null ? "KHÔNG trần"
                        : so(m.tranGio, 0) + " h")
                      + (dang ? "  ← đang chạy" : ""), c: dang ? "n" : null },
                  { t: so(m.soCoHoi), c: "nhat" },
                  { t: tien(m.sucChuaUsd, 0) },
                  { t: tien(m.rotDuocUsd, 0) },
                  { t: so(m.aprTrenCaTui, 2) + "%",
                    c: m.aprTrenCaTui >= 5 ? "duong" : "nhat" },
                  { t: m.khoaBinhQuanGio == null ? "—"
                       : so(m.khoaBinhQuanGio, 0) + " h", c: "nhat" }];
        })));
      if (dkv.vi) kkv.appendChild(giai(dkv.vi));
      f.appendChild(kkv);
    }

    /* XOAY CHỖ. Chỗ ngồi có hạn (trần vị thế), nên câu hỏi không phải
       "có cơ hội nào không" mà là "ai đang ngồi". Đo trên máy sống: 8 chỗ
       khoá 30 ngày ở 1,9–3,0 %/năm trong khi 9–16 % đi qua mỗi vòng rồi bị
       từ chối vì «đã đủ 12 vị thế». */
    var xc = t.xoayCho || {};
    var kxc = khoi("Xoay chỗ — ai đang ngồi, và ai đáng ngồi hơn",
      "Đổi chỗ TỐN TIỀN: phí ra + phí vào trả ngay, phần lãi hơn thì nhỏ "
      + "giọt theo giờ. Chỉ đổi khi (lãi mới − lãi cũ) × số giờ CHUNG lớn "
      + "hơn phí. Đây là phép ĐO — đường thực hiện chưa nối.");
    var dxc = el("div", "day-so");
    dxc.appendChild(oSo("Danh mục hiện tại",
      xc.aprHienTai == null ? "—" : phan(xc.aprHienTai),
      "bình quân gia quyền, lãi khai lúc mở"));
    dxc.appendChild(oSo("Nếu xoay chỗ",
      xc.aprSauKhiXoay == null ? "—" : phan(xc.aprSauKhiXoay),
      so(xc.soXoayDuoc) + " chỗ đáng đổi",
      (xc.soXoayDuoc || 0) ? "duong" : "nhat"));
    dxc.appendChild(oSo("Lợi ròng đã trừ phí", tien(xc.loiRongUsd, 3),
      xc.gioSongTrungVi == null
        ? "trong quãng hai bên cùng còn hiệu lực"
        : "trong quãng ngắn nhất giữa ba: hai bên còn hiệu lực, và "
          + "bằng chứng"));
    /* TRẦN THEO BẰNG CHỨNG. Khai ra, đừng kẹp lặng lẽ: lợi ròng tụt
       xuống mà không nói vì sao thì đọc thành «thị trường bỗng tệ đi»,
       trong khi thật ra ta vừa thôi tin một giả định. */
    if (xc.gioSongTrungVi != null) {
      dxc.appendChild(oSo("Trần theo bằng chứng",
        so(xc.gioSongTrungVi, 3) + "h",
        so(xc.soBiKepTheoBangChung) + " bị cắt · "
          + so(xc.soBiChanBoiBangChung) + " bị CHẶN HẲN",
        ((xc.soBiKepTheoBangChung || 0) + (xc.soBiChanBoiBangChung || 0))
          ? "am" : "nhat"));
      /* «Bị chặn hẳn» phải hiện RIÊNG. Khi trần chặn sạch thì số «bị
         cắt» bằng 0, và «trần 0,008h · 0 lời hứa bị cắt» đọc đúng thành
         «trần này chẳng làm gì» — trong khi nó vừa chặn tất cả. */
      if (xc.soBiChanBoiBangChung) {
        dxc.appendChild(oSo("Lời hứa đã CHẶN",
          tien(xc.loiRongBiChanUsd, 2),
          "công thức cũ sẽ nhận từng ấy — trên quãng vị thế không sống tới",
          "nhat"));
      }
      /* TUỔI của bằng chứng. Một trần dựng từ mẫu ba ngày trước vẫn dùng
         được, nhưng «trần bằng chứng» không kèm tuổi thì đọc như một
         phép đo của lúc này. Và tuổi là thứ duy nhất cho biết cỗ máy có
         đang tự nới trần ra hay không: xoay dừng ⇒ vị thế chết vì hết
         hạn giữ ⇒ mẫu mới có giờ giữ lớn ⇒ trung vị dâng. */
      if (xc.nguonBangChung) {
        var _t = xc.tuoiBangChungGiay;
        dxc.appendChild(oSo("Bằng chứng lấy từ đâu",
          so(xc.soMauBangChung || 0) + " mẫu",
          xc.nguonBangChung
            + (_t == null ? ""
               : " · mẫu mới nhất " + (_t < 3600
                   ? Math.round(_t / 60) + " phút"
                   : (_t / 3600).toFixed(1) + " giờ") + " trước"),
          (_t != null && _t > 86400) ? "cho" : "nhat"));
      }
    }
    if (xc.viConGhe) {
      kxc.appendChild(giai("CÒN GHẾ TRỐNG nên không đuổi ai — cơ hội tốt "
        + "hơn cứ ngồi vào chỗ trống. Xoay chỗ chỉ có nghĩa khi hết ghế."));
      /* Câu trên là một LỜI HỨA, và lời hứa ấy kiểm chứng được. Đo 30/08:
         54 vị thế, 66 ghế trống, 478 nghìn USD nằm không, và số vị thế
         đứng yên vòng này qua vòng khác — vì cơ hội tốt hơn nằm trong một
         họ đã chạm trần, nên ghế trống không giúp gì cho chúng. */
      dxc.appendChild(oSo("Vòng ghế trống KHÔNG lấp",
        so(xc.soVongGheTrongKhongLap),
        (xc.soVongGheTrongKhongLap || 0) >= 3
          ? "lời hứa «Phân Bổ sẽ lấp chỗ» KHÔNG được giữ"
          : "liên tiếp, số vị thế không tăng",
        (xc.soVongGheTrongKhongLap || 0) >= 3 ? "am" : "nhat"));
    }
    /* ĐÍCH bị tầng trên chặn. Không lọc thì bảng hứa một việc Phân Bổ sẽ
       từ chối làm — đo 30/08: bốn dòng lớn nhất của bảng xoay chỗ đều trỏ
       sang một ty mà Rủi Ro Tổng đang chặn sạch. */
    if (xc.soDichBiChan) {
      dxc.appendChild(oSo("Đích bị CHẶN", so(xc.soDichBiChan),
        "cơ hội tốt hơn mà Rủi Ro Tổng không cho — đã BỎ khỏi phép đo này",
        "nhat"));
    }
    dxc.appendChild(oSo("Không xoay được",
      so((xc.soBiKhoa || 0) + (xc.soKhongDoDuocThoat || 0)),
      (xc.soBiKhoa || 0) + " khoá vốn · "
      + (xc.soKhongDoDuocThoat || 0) + " chưa đo thoát", "nhat"));
    kxc.appendChild(dxc);
    if ((xc.xoay || []).length) {
      kxc.appendChild(bang(
        [{ t: "Đang giữ" }, { t: "%/năm" }, { t: "Đáng đổi sang" },
         { t: "%/năm" }, { t: "Giờ chung" }, { t: "Lợi ròng" }],
        xc.xoay.map(function (x) {
          return [{ t: x.taiSanCu }, { t: so(x.aprCu, 2), c: "n" },
                  { t: x.taiSanMoi + " · " + x.chienLuocMoi },
                  { t: so(x.aprMoi, 2), c: "n" },
                  { t: so(x.gioChung, 0) + "h", c: "nhat" },
                  { t: tien(x.loiRongUsd, 3), c: "duong" }];
        })));
    }
    if (xc.vi) kxc.appendChild(giai(xc.vi));
    f.appendChild(kxc);

    /* XOAY CHỖ ĐÃ HỨA GÌ — và vị thế mới sống được bao lâu.

       Bảng trên là lời hứa của vòng NÀY. Bảng này là hoá đơn của mọi
       vòng đã qua. Đo làn thật 30/08: 267 lần xoay trong 39 phút, tổng
       lời hứa +11.136 USD trên một cuốn sổ 10.000 USD — trong khi chính
       ty được xoay nhiều nhất đang âm 77,51 USD. Trung vị số giờ giữ
       được trước lần xoay kế: 0,008 giờ, chưa tới ba mươi giây.

       Lời hứa cộng trước phần lãi hơn của cả `giờChung` (có thể 167
       giờ) rồi trừ phí đổi MỘT lần. Phí trả đủ, lãi thì không bao giờ
       tới. Một lời hứa không ai đối chiếu là một lời hứa không tốn gì
       để nói — nên nó phải nằm ở đây, cạnh chính lời hứa ấy. */
    var xhAll = (t.soCai || {}).xoayChoHuaVaThuc || {};
    /* GẦN ĐÂY là con số phải nhìn. Cửa chặn «còn ghế trống thì không đuổi
       ai» vào 29/08 đã dừng vòng xoay ấy, nhưng 267 bút toán cũ nằm lại
       trong sổ mãi mãi — bày số cộng dồn lên đầu là dựng một ô đỏ không
       bao giờ tắt được, và ô ấy thì người ta học cách bỏ qua. */
    var xh = xhAll.ganDay || {};
    if (xhAll.soLan) {
      var kxh = khoi("Xoay chỗ đã hứa gì — và giữ được bao lâu",
        "Lợi ròng của mỗi lần xoay tính trên quãng giờ hai bên cùng còn "
        + "hiệu lực. Nếu vị thế mới bị xoay tiếp sau vài phút thì phần "
        + "lãi hơn ấy chưa bao giờ tới, còn phí đổi đã trả đủ.");
      var dxh = el("div", "day-so");
      dxh.appendChild(oSo("Xoay trong " + so(xh.gioCuaSo, 0) + "h qua",
        so(xh.soLan),
        so(xhAll.soLan) + " lần cộng dồn cả đời",
        (xh.soLan || 0) ? "" : "nhat"));
      dxh.appendChild(oSo("Lời hứa " + so(xh.gioCuaSo, 0) + "h qua",
        tien(xh.huaLoiRongUsd, 2),
        "lợi ròng đã trừ phí · " + tien(xhAll.huaLoiRongUsd, 0)
        + " cả đời"));
      dxh.appendChild(oSo("Hứa trên",
        xh.gioHuaTrungVi == null ? "—" : so(xh.gioHuaTrungVi, 1) + "h",
        "trung vị quãng giờ lời hứa tính trên"));
      var tl = xh.tiLeSongTrenHua;
      dxh.appendChild(oSo("Giữ được thật",
        xh.gioGiuTrungVi == null ? "—" : so(xh.gioGiuTrungVi, 3) + "h",
        tl == null ? "chưa đối chiếu được"
                   : so(tl * 100, 2) + "% quãng đã hứa",
        tl == null ? "nhat" : (tl < 0.2 ? "am" : "duong")));
      if (xh.soThieuGioHua) {
        dxh.appendChild(oSo("Chưa đối chiếu được", so(xh.soThieuGioHua),
          "bút toán cũ không ghi quãng hứa", "nhat"));
      }
      kxh.appendChild(dxh);
      if (!xh.soLan) {
        kxh.appendChild(giai("KHÔNG xoay lần nào trong cửa sổ này. Bảng "
          + "dưới là hoá đơn cũ, giữ lại để đọc — không phải chuyện đang "
          + "xảy ra."));
      }
      if ((xh.capLapNhieuNhat || []).length) {
        /* Cùng một cặp đi–đến lặp lại hàng chục lần nghĩa là Phân Bổ mở
           lại đúng cái chỗ Xoay Chỗ vừa bỏ. Hai tầng xếp hạng bằng hai
           thước khác nhau — đô-la mỗi giờ và %/năm — nên chúng đổi chỗ
           cho nhau mãi, và mỗi vòng trả thêm hai lần phí vào lệnh. */
        kxh.appendChild(bang(
          [{ t: "Cặp đi → đến" }, { t: "Số lần" }],
          (xh.capLapNhieuNhat || []).map(function (x) {
            return [{ t: x.cap },
                    { t: so(x.soLan), c: x.soLan >= 3 ? "am" : "n" }];
          })));
        if (xh.soCapDiLaiNhieuLan) {
          kxh.appendChild(giai(xh.soCapDiLaiNhieuLan + " cặp đi lại từ ba "
            + "lần trở lên. Cùng một cặp lặp lại nghĩa là Phân Bổ mở lại "
            + "đúng chỗ Xoay Chỗ vừa bỏ — hai tầng xếp hạng bằng hai "
            + "thước khác nhau, và mỗi vòng qua lại trả thêm phí vào "
            + "lệnh."));
        }
      }
      var mxh = Object.keys(xhAll.theoTy || {});
      if (mxh.length) {
        kxh.appendChild(bang(
          [{ t: "Ty (cộng dồn)" }, { t: "Số lần" }, { t: "Lời hứa" },
           { t: "Giữ được (trung vị)" }],
          mxh.sort(function (a2, b2) {
            return (xhAll.theoTy[b2].soLan || 0)
                 - (xhAll.theoTy[a2].soLan || 0);
          }).map(function (k) {
            var o = xhAll.theoTy[k] || {};
            return [{ t: k }, { t: so(o.soLan), c: "n" },
                    { t: tien(o.huaUsd, 2), c: "n" },
                    { t: o.gioGiuTrungVi == null
                         ? "—" : so(o.gioGiuTrungVi, 3) + "h", c: "n" }];
          })));
      }
      f.appendChild(kxh);
    }

    /* LỜI HỨA vs THỰC NHẬN — hậu kiểm cho TÁM ty không có băng. Ty chênh
       funding chạy lại băng được; tám ty kia thì tờ trình lúc mở đã hứa,
       sổ lúc đóng biết thực nhận. Trước đây những ty ĐANG kiếm được tiền
       lại là những ty không ai đối chiếu. */
    var dv = t.duDoanVaThuc || {};
    var mdv = Object.keys(dv).filter(function (k) {
      return dv[k].soDoiChieuDuoc > 0;
    });
    var kdv = khoi("Lời hứa vs THỰC NHẬN — theo ty",
      "Quy về bps MỖI GIỜ ở cả hai vế. So bps trần thì một vị thế đóng sớm "
      + "luôn «thua» lời hứa của cả cửa sổ, và cái thua ấy chỉ nói nó đóng "
      + "sớm chứ không nói nó dở.");
    if (!mdv.length) {
      kdv.appendChild(giai("chưa vị thế nào đóng KÈM ĐỦ hai vế — mỗi ty cần "
        + "ít nhất một lần đóng có khai dự đoán thì mới đối chiếu được"));
    } else {
      kdv.appendChild(bang(
        [{ t: "Ty" }, { t: "Đối chiếu" }, { t: "Giữ quá ngắn" },
         { t: "Thiếu vế" }, { t: "HỨA bps/giờ" },
         { t: "THỰC bps/giờ" }, { t: "Lệch" }],
        mdv.map(function (k) {
          var x = dv[k];
          return [{ t: k }, { t: so(x.soDoiChieuDuoc) + "/" + so(x.soDong) },
                  { t: so(x.soGiuQuaNgan), c: "n" },
                  { t: so(x.soThieuVe), c: "n" },
                  { t: so(x.duDoanBpsGio, 3), c: "n" },
                  { t: so(x.thucBpsGio, 3), c: "n" },
                  { t: x.lechBpsGio == null ? "—"
                      : (x.lechBpsGio >= 0 ? "+" : "") + so(x.lechBpsGio, 3),
                    c: x.lechBpsGio > 0 ? "am" : "duong" }];
        })));
      kdv.appendChild(giai("Lệch DƯƠNG nghĩa là HỨA QUÁ — ty ấy đang lạc "
        + "quan. Đó là con số đáng đọc nhất ở bảng này, và nó chỉ nói được "
        + "sau khi vị thế đã đóng."));
      kdv.appendChild(giai("Mẫu số CỘNG ĐÚNG: đối chiếu + giữ quá ngắn + "
        + "thiếu vế = số lần đóng. «Giữ quá ngắn» là dưới 0,25 giờ — quy "
        + "ra bps mỗi giờ ở đó là nhân một sai số nhỏ lên hàng nghìn lần. "
        + "«Thiếu vế» là lần đóng không khai đủ hứa và thực, phần lớn là "
        + "dòng ghi trước khi bút toán biết khai hai vế ấy. Không tách ra "
        + "thì người đọc trừ mẫu số ra và đọc thành ngần ấy lần thất bại."));
    }
    f.appendChild(kdv);

    var tk = t.laiLoTachKhoan || {};
    var mtk = Object.keys(tk);
    if (mtk.length) {
      var kt4 = khoi("Lãi lỗ TÁCH KHOẢN — vì con số gộp nói dối",
        "Phí vào lệnh phần lớn KHÔNG do chiến lược sinh ra. Cột «đóng» "
        + "nói vì đâu: khởi động lại (vị thế mô phỏng không sống qua đó, "
        + "nên mỗi lần restart là một lần vào lệnh mới), hay XOAY CHỖ (cỗ "
        + "máy tự đuổi vị thế của mình để nhường ghế). Hai nguyên nhân, "
        + "hai cách chữa khác hẳn nhau — và trước đây ô này chỉ kể một.");
      kt4.appendChild(bang(
        [{ t: "Ty" }, { t: "Thu", n: true }, { t: "Phí vào lệnh", n: true },
         { t: "Số lần vào", n: true }, { t: "Phí mỗi lần", n: true },
         { t: "Đóng · do xoay", n: true },
         { t: "GỘP", n: true }, { t: "CHIẾN LƯỢC", n: true }],
        mtk.sort(function (a, b) {
          return (tk[b].laiLoChienLuocUsd || 0) - (tk[a].laiLoChienLuocUsd || 0);
        }).map(function (k) {
          var v = tk[k];
          return [{ t: (TEN_DEP[k] || [k])[0] },
                  { t: tien(v.thuUsd, 4), c: "n" },
                  { t: tien(v.phiVaoUsd, 4), c: "n" },
                  { t: so(v.soLanVaoLenh), c: "n" },
                  { t: tien(v.phiMoiLanVaoUsd, 4), c: "n" },
                  /* «đóng vì đâu» là mẫu số phân biệt hai bệnh khác hẳn
                     nhau. Đo làn thật 30/08: ty cho vay 217/282 lần đóng
                     là xoay chỗ, ty basis 29/29 — chỉ người vận hành sang
                     nút restart là gửi họ đi sai đường. */
                  { t: so(v.soLanDong) + (v.phanDongDoXoayCho == null ? ""
                      : " · " + so(v.soLanDongXoayCho)),
                    c: (v.phanDongDoXoayCho || 0) >= 0.5 ? "am" : "n" },
                  { el: (function () {
                      var e = el("span", (v.laiLoUsd || 0) >= 0 ? "duong" : "am",
                                 tien(v.laiLoUsd, 4));
                      return e;
                    })() },
                  { el: (function () {
                      var e = el("b", (v.laiLoChienLuocUsd || 0) >= 0
                                 ? "duong" : "am",
                                 tien(v.laiLoChienLuocUsd, 4));
                      return e;
                    })() }];
        })));
      kt4.appendChild(giai("Cột CHIẾN LƯỢC bỏ phí vào lệnh ra. Nó trả lời "
        + "«ty này có kiếm được không», còn cột GỘP trả lời «tài khoản đã "
        + "đổi bao nhiêu». Cả hai đều đúng, và chúng khác nhau. Cột «đóng "
        + "· do xoay» đỏ khi quá nửa số lần đóng là do Xoay Chỗ — lúc ấy "
        + "phí vào lệnh không phải chuyện của người vận hành nữa, nó là "
        + "chuyện của chính cỗ máy."));
      f.appendChild(kt4);
    }

    var k3 = khoi("Sổ cái nói gì");
    var loai = sc.theoLoai || {};
    k3.appendChild(bang([{ t: "Loại bút toán" }, { t: "Số", n: true }, { t: "Tổng USD", n: true }],
      Object.keys(loai).map(function (l) {
        return [{ t: l }, { t: so(loai[l].so), c: "n" },
                { t: tien(loai[l].tongUsd), c: "n" }];
      })));
    k3.appendChild(giai("Bút toán TU_CHOI nhiều hơn CAP_VON là dấu hiệu LÀNH: "
      + "hệ thống ghi lại cả những lần nó nói không, nên vì sao nó từ chối là "
      + "một câu hỏi trả lời được bằng truy vấn."));
    f.appendChild(k3);
    return f;
  }

  /* ══════════════════ TRANG: RỦI RO ═════════════════════════════ */
  function ve_rui_ro() {
    var f = document.createDocumentFragment();
    var t = (S && S.trungUong) || {}, cd = t.cauDao || {}, rr = t.ruiRoTong || {};

    var k = khoi("Cầu dao");
    var d = el("div", "day-so");
    d.appendChild(oSo("Trạng thái", cd.dangNgat ? "ĐANG NGẮT" : "Đóng",
      cd.dangNgat ? "không cam kết thêm đồng nào" : "cho phép cấp vốn",
      cd.dangNgat ? "am" : "duong", true));
    d.appendChild(oSo("Số lần đã ngắt", so(cd.soLanNgat), "từ khi runtime khởi động"));
    k.appendChild(d);
    if ((cd.lyDo || []).length) {
      k.appendChild(bang([{ t: "Mã" }, { t: "Vì sao" }, { t: "Đóng lại" }],
        cd.lyDo.map(function (l) {
          return [{ t: l.ma }, { t: l.moTa },
                  { t: l.tuMo ? "tự đóng khi điều kiện hết" : "PHẢI có người" }];
        })));
    }
    k.appendChild(giai("Bất đối xứng có chủ ý: máy NGẮT được vì máy phát hiện "
      + "nhanh hơn người. Đóng lại thì phần lớn phải có NGƯỜI — máy không phân "
      + "biệt được «sự cố đã qua» với «sự cố vẫn còn nhưng tín hiệu tạm im», và "
      + "cái thứ hai chính là lúc đóng lại thì mất tiền."));
    f.appendChild(k);

    var k2 = khoi("Trần của Rủi Ro Tổng",
      "Rủi Ro Tổng không trả lời có/không — nó trả về một TRẦN, và Phân Bổ cấp "
      + "vốn TUẦN TỰ rồi hỏi lại sau mỗi lần, nên trần thật sự bó.");
    k2.appendChild(bang([{ t: "Trần" }, { t: "Giá trị", n: true }],
      Object.keys(rr).map(function (x) {
        var v = rr[x];
        return [{ t: x }, { t: typeof v === "number"
          ? (v <= 1 && v > 0 ? (v * 100).toFixed(0) + "%" : String(v))
          : String(v), c: "n" }];
      })));
    f.appendChild(k2);

    var hp = t.hienPhap || {};
    var k3 = khoi("Hiến pháp — luật viết dưới dạng chạy được");
    var d3 = el("div", "day-so");
    d3.appendChild(oSo("Điều", so(hp.soDieu), "mỗi điều kèm sự cố đã dạy ra nó"));
    d3.appendChild(oSo("Canh được bằng máy", so(hp.soCanhDuoc), "chạy mỗi vòng"));
    /* «KHÔNG canh được» tách làm hai, vì gộp lại là nói mình được che ít
       hơn thực tế. Bốn điều có người canh — chỉ là canh ở selftest, nơi
       được phép nhìn sang một ty; canh từ Trung Ương là phạm chính điều
       `trung-uong-khong-biet-ty`. Hai điều còn lại thì thật sự chưa ai
       canh, và đó mới là con số đáng nhìn. */
    d3.appendChild(oSo("Canh ở TẦNG KHÁC", so(hp.soCanhOTangKhac),
      "selftest canh, không phải Trung Ương", "nhat"));
    d3.appendChild(oSo("CHƯA AI canh", so(hp.soHoanToanTrong),
      "khai ra, không giấu",
      hp.soHoanToanTrong ? "nhat" : "duong"));
    d3.appendChild(oSo("Vi phạm", so(hp.soViPham),
      hp.soViPham === null || hp.soViPham === undefined
        ? "CHƯA soát" : (hp.soViPham ? "PHẢI XEM" : "sạch"),
      hp.soViPham === null || hp.soViPham === undefined
        ? "nhat" : (hp.soViPham ? "am" : "duong")));
    /* Soát hiến pháp có nhịp riêng: hàng chục điều, phần lớn phân tích cả
       cây mã, và một điều dựng hẳn một Trung Ương rồi quay hai vòng thật.
       Buồng lái hỏi mỗi vài giây, nên bản này có thể CŨ — và một con số cũ
       mà không nói mình cũ thì trông y hệt một con số mới. */
    d3.appendChild(oSo("Soát cách đây",
      hp.tuoiGiay === null || hp.tuoiGiay === undefined
        ? "—" : Math.round(hp.tuoiGiay) + "s",
      "hiến pháp là hàm của mã nguồn, nên soát theo nhịp chứ không mỗi lần hỏi",
      "nhat"));
    k3.appendChild(d3);
    if ((hp.canhOTangKhac || []).length) {
      k3.appendChild(giai("Canh ở tầng khác: "
        + hp.canhOTangKhac.map(function (x) {
            return x.ma + " → " + x.ham + "()"; }).join(", ")
        + " — và chính cái chỉ tay ấy được canh: điều "
        + "«chi-tay-phai-chi-vao-cho-co-that» đòi mỗi tên phải là một hàm CÓ "
        + "THẬT và ĐANG ĐƯỢC GỌI, vì hàm tồn tại không có nghĩa là hàm chạy."));
    }
    if ((hp.hoanToanTrong || []).length) {
      k3.appendChild(giai("CHƯA AI canh: " + hp.hoanToanTrong.join(", ")
        + " — một hiến pháp mà điều nào cũng trông như đang có hiệu lực thì "
        + "tệ hơn không có."));
    }
    (hp.viPham || []).forEach(function (v) {
      var b = el("div", "viec-1");
      b.appendChild(el("b", null, "VI PHẠM · " + v.ma));
      b.appendChild(el("span", null, v.chiTiet));
      k3.appendChild(b);
    });
    f.appendChild(k3);
    return f;
  }

  /* ══════════════════ TRANG: DỮ LIỆU ════════════════════════════ */
  function ve_du_lieu() {
    var f = document.createDocumentFragment();
    var r = (S && S.router) || {}, ng = (S && S.nguonGas) || {},
        nc = (S && S.nguonCau) || {}, cang = (S && S.cang) || [];
    var t = (S && S.trungUong) || {};

    var song = cang.filter(function (c) { return c.songSot && !c.loiCuoi; }).length;

    var k0 = khoi("Hạ tầng — cái gì nuôi cái gì",
      "Bốn cột đọc từ TRÁI sang PHẢI. Ô nào đỏ thì mọi thứ bên phải nó đang "
      + "đi trên số liệu thiếu — và đó là lý do sơ đồ này tồn tại: một cảng "
      + "chết ở cột một hiện thành «không có cơ hội nào» ở cột bốn, hai chỗ "
      + "cách nhau xa tới mức không ai nối được nếu phải nối bằng trí nhớ.");
    k0.appendChild(veSoDoHaTang(cang, r, ng, nc, t));
    f.appendChild(k0);

    var k = khoi("Nguồn dữ liệu",
      "Mọi nguồn đều CÔNG KHAI, không khoá. Ngày một nguồn cần khoá là ngày "
      + "nó thôi là nguồn và trở thành thứ khác.");
    var d = el("div", "day-so");
    d.appendChild(oSo("Cảng perp", song + " / " + cang.length,
      song === cang.length ? "tất cả đang sống" : "⚠ có cảng chết",
      song === cang.length ? "duong" : "am"));
    d.appendChild(oSo("Chuỗi dùng được", (r.chuoiDungDuoc || []).length + " / "
      + (r.chuoiCoGas || []).length,
      (r.chuoiCoGasNhungThieuGia || []).length
        ? "⚠ thiếu giá: " + r.chuoiCoGasNhungThieuGia.join(", ")
        : "có cả gas lẫn giá token gốc",
      (r.chuoiCoGasNhungThieuGia || []).length ? "am" : "duong"));
    d.appendChild(oSo("Nguồn cầu nối", nc.dangNghi ? "ĐANG NGHỈ" : "sẵn sàng",
      nc.dangNghi ? "còn " + Math.round((nc.conNghiGiay || 0) / 60) + " phút · 429 × "
        + (nc.soLan429 || 0) : (nc.soLan429 || 0) + " lần dính hạn mức",
      nc.dangNghi ? "am" : "duong", true));
    d.appendChild(oSo("Gas giữ lại", so(ng.soGiuLai),
      "lần giữ số cũ vì RPC lỗi", (ng.soGiuLai || 0) ? "nhat" : null));
    var kc = (S && S.khoCau) || {};
    d.appendChild(oSo("Báo giá cầu nạp lại", kc.co ? so(kc.nap) : "—",
      kc.co ? "từ đĩa lúc khởi động · bỏ " + so(kc.boQuaCu) + " bản quá hạn"
            : "chưa có kho trên đĩa",
      kc.co ? null : "nhat", true));
    k.appendChild(d);
    f.appendChild(k);

    var k2 = khoi("Cảng perp — sức khoẻ từng cái");
    k2.appendChild(bang(
      [{ t: "Cảng" }, { t: "Trạng thái" }, { t: "Lượt", n: true },
       { t: "Lỗi", n: true }, { t: "Trễ TB", n: true }, { t: "Tuổi", n: true }],
      cang.map(function (c) {
        return [{ t: c.ten },
                { el: cot(c.loiCuoi ? "FAULT" : c.songSot ? "PAPER" : "OFF") },
                { t: so(c.tongLuot), c: "n" }, { t: so(c.soLoi), c: "n" },
                { t: c.treTrungBinhMs != null ? Math.round(c.treTrungBinhMs) + "ms" : "—", c: "n" },
                { t: gio(c.tuoiGiay), c: "n" }];
      })));
    f.appendChild(k2);

    var k3 = khoi("Router chuyển vốn — hạ tầng, KHÔNG phải ty",
      "Nó trả lời «dời $X từ đâu tới đâu tốn gì, mất bao lâu, và có gì tôi "
      + "KHÔNG đo được không». Câu cuối mới là phần đáng giá: một chặng không "
      + "đo được thì CẢ TUYẾN không đo được, chứ không cộng vòng qua lỗ hổng.");
    k3.appendChild(bang([{ t: "Mục" }, { t: "Giá trị" }],
      [[{ t: "Chuỗi DÙNG ĐƯỢC" }, { t: (r.chuoiDungDuoc || []).join(", ") || "—" }],
       [{ t: "Đọc được gas nhưng THIẾU giá" }, { t: (r.chuoiCoGasNhungThieuGia || []).join(", ") || "không" }],
       [{ t: "Token có giá" }, { t: (r.tokenCoGia || []).join(", ") || "—" }],
       [{ t: "Chuỗi nhà" }, { t: r.nha || "—" }],
       [{ t: "Báo giá cầu trong kho" }, { t: so(r.soBaoGiaTrongKho) }]]));
    f.appendChild(k3);

    var k4 = khoi("Sổ ngoài — kết toán cỗ máy khác vào MỘT sổ cái");
    var sn = t.soNgoai || [];
    if (!sn.length) k4.appendChild(giai("chưa khai nguồn sổ ngoài nào"));
    else k4.appendChild(bang(
      [{ t: "Nguồn" }, { t: "Đọc được" }, { t: "Đã nhập", n: true },
       { t: "Bỏ sót", n: true }, { t: "Đo được bỏ sót" }],
      sn.map(function (x) {
        return [{ t: x.ten }, { el: cot(x.docDuoc ? "PAPER" : "FAULT") },
                { t: so(x.soDaVao), c: "n" }, { t: so(x.soBoSot), c: "n" },
                { t: x.boSotDoDuoc ? "có" : "chưa — cần hai lượt đọc khác số" }];
      })));
    f.appendChild(k4);
    return f;
  }

  /* ── sơ đồ hạ tầng ────────────────────────────────────────────────
   * Sơ đồ này CỐ Ý không dùng sáu màu trạng thái. Sáu màu ấy nói về động
   * cơ ("đang chạy tiền thật", "chỉ quan sát"); một nguồn dữ liệu khoẻ
   * không phải "LIVE" theo nghĩa đó, và tô nó xanh y hệt là dạy mắt đọc
   * sai. Ở đây chỉ có HAI dấu: **đỏ = đang hỏng**, **nét đứt = chưa đo
   * được sức khoẻ**. Không dấu nào nghĩa là đang đọc được.
   *
   * Và phải phân biệt "đo" với "suy": bốn cảng perp, RPC gas và LI.FI có
   * bộ đếm sức khoẻ thật; Deribit, DefiLlama, Polymarket thì không — ta
   * chỉ suy từ việc ty của chúng có ném lỗi hay không. Vẽ cả sáu cùng một
   * kiểu là biến một suy đoán thành một phép đo.                        */
  function veSoDoHaTang(cang, r, ng, nc, t) {
    var NS = "http://www.w3.org/2000/svg";
    function e(ten, thuoc) {
      var x = document.createElementNS
        ? document.createElementNS(NS, ten) : el(ten);
      for (var k in thuoc) if (thuoc[k] != null) x.setAttribute(k, thuoc[k]);
      return x;
    }
    var loiTy = {};
    (t.ty || []).forEach(function (x) { loiTy[x.ma] = !!x.loiCuoi; });
    function tyHong() {
      for (var i = 0; i < arguments.length; i++)
        if (loiTy[arguments[i]]) return true;
      return false;
    }
    var cangChet = (cang || []).filter(function (c) {
      return !c.songSot || c.loiCuoi;
    });

    var COT = [
      { nhan: "NGUỒN CÔNG KHAI", x: 8, o: [
        { id: "perp", ten: "4 sàn perp",
          phu: (cang.length - cangChet.length) + "/" + cang.length
               + " đọc được · Hyperliquid·Binance·OKX·Bybit",
          hong: cangChet.length > 0, doDuoc: true },
        { id: "deribit", ten: "Deribit", phu: "chuỗi quyền chọn — suy từ ty",
          hong: tyHong("options.put_call_parity.v1"), doDuoc: false },
        { id: "llama", ten: "DefiLlama", phu: "lãi cho vay · pool AMM · Pendle",
          hong: tyHong("lending.rate_rotation.v1", "yield.pendle_pt.v1",
                       "amm.fee_farming.v1"), doDuoc: false },
        { id: "poly", ten: "Polymarket", phu: "đọc QUA Khâm Thiên Giám",
          hong: tyHong("prediction.polymarket.v1"), doDuoc: false },
        { id: "rpc", ten: "RPC " + (r.chuoiCoGas || []).length + " chuỗi",
          phu: "giá gas · " + ((ng.soGiuLai || 0)
               ? "giữ số cũ " + ng.soGiuLai + " lần" : "chưa phải giữ số cũ"),
          hong: !!ng.loiCuoi || !(r.chuoiCoGas || []).length, doDuoc: true },
        { id: "lifi", ten: "LI.FI", phu: nc.dangNghi
            ? "ĐANG NGHỈ vì hạn mức" : "báo giá cầu nối",
          hong: !!nc.dangNghi || !!nc.loiCuoi, doDuoc: true }
      ] },
      { nhan: "HẠ TẦNG DÙNG CHUNG", x: 228, o: [
        { id: "doc", ten: "Bộ đọc chung",
          phu: "sàn · phái sinh · chuỗi — một bộ, chín ty dùng",
          hong: false, doDuoc: false },
        { id: "router", ten: "Router chuyển vốn",
          phu: (r.chuoiDungDuoc || []).length + "/"
               + (r.chuoiCoGas || []).length + " chuỗi dùng được · nhà "
               + (r.nha || "—"),
          hong: (r.chuoiCoGasNhungThieuGia || []).length > 0, doDuoc: true }
      ] },
      { nhan: "CHÍN TY, NĂM HỌ", x: 448, o: [
        { id: "ho-phai-sinh", ten: "Phái sinh", phu: "3 ty", hong: false, doDuoc: true },
        { id: "ho-tin-dung", ten: "Tín dụng", phu: "2 ty", hong: false, doDuoc: true },
        { id: "ho-chenh-lech", ten: "Chênh lệch", phu: "2 ty", hong: false, doDuoc: true },
        { id: "ho-thanh-khoan", ten: "Thanh khoản", phu: "1 ty", hong: false, doDuoc: true },
        { id: "ho-tien-doan", ten: "Tiên đoán", phu: "1 ty", hong: false, doDuoc: true }
      ] },
      { nhan: "TRUNG ƯƠNG", x: 668, o: [
        { id: "tu", ten: "Trung Ương",
          phu: "cầu dao · rủi ro tổng · phân bổ · sổ cái",
          hong: !!(t.cauDao || {}).dangNgat, doDuoc: true }
      ] }
    ];
    /* Đếm ty hỏng theo HỌ, để một ty ném lỗi hiện ra đúng ô của nó. */
    var hoCua = { "phai-sinh": 0, "tin-dung": 0, "chenh-lech": 0,
                  "thanh-khoan": 0, "tien-doan": 0 };
    (t.ty || []).forEach(function (x) {
      if (x.loiCuoi && hoCua[x.ho] != null) hoCua[x.ho] += 1;
    });
    COT[2].o.forEach(function (o) {
      var h = o.id.replace(/^ho-/, "");
      if (hoCua[h]) { o.hong = true; o.phu = o.phu + " · " + hoCua[h] + " ĐANG LỖI"; }
    });

    var W = 176, H = 54, KHE = 14, DAU = 26;
    var caoNhat = 0;
    COT.forEach(function (c) {
      caoNhat = Math.max(caoNhat, c.o.length * H + (c.o.length - 1) * KHE);
    });
    var CAO = DAU + caoNhat + 40;
    var oi = {};
    COT.forEach(function (c) {
      var cao = c.o.length * H + (c.o.length - 1) * KHE;
      var y0 = DAU + (caoNhat - cao) / 2;
      c.o.forEach(function (o, i) {
        o.x = c.x; o.y = y0 + i * (H + KHE); o.w = W; o.h = H;
        oi[o.id] = o;
      });
    });

    var svg = e("svg", { viewBox: "0 0 852 " + CAO, class: "so-do",
                         role: "img", "aria-label": "sơ đồ hạ tầng" });
    /* Cạnh vẽ TRƯỚC ô, để đường không đè lên chữ. */
    function canh(a, b, hong) {
      var A = oi[a], B = oi[b];
      if (!A || !B) return;
      var x1 = A.x + A.w, y1 = A.y + A.h / 2, x2 = B.x, y2 = B.y + B.h / 2;
      var g = (x2 - x1) / 2;
      svg.appendChild(e("path", {
        d: "M" + x1 + " " + y1 + "C" + (x1 + g) + " " + y1 + ","
           + (x2 - g) + " " + y2 + "," + x2 + " " + y2,
        class: "sd-canh" + (hong ? " hong" : "") }));
    }
    ["perp", "deribit", "llama", "poly"].forEach(function (x) {
      canh(x, "doc", oi[x].hong);
    });
    ["rpc", "lifi"].forEach(function (x) { canh(x, "router", oi[x].hong); });
    COT[2].o.forEach(function (o) { canh("doc", o.id, false); });
    ["ho-tin-dung", "ho-chenh-lech", "ho-thanh-khoan"].forEach(function (x) {
      canh("router", x, oi.router.hong);
    });
    COT[2].o.forEach(function (o) { canh(o.id, "tu", o.hong); });

    COT.forEach(function (c) {
      svg.appendChild(chuSvg(e, c.x, 16, c.nhan, "sd-nhan"));
      c.o.forEach(function (o) {
        svg.appendChild(e("rect", {
          x: o.x, y: o.y, width: o.w, height: o.h, rx: 6,
          class: "sd-o" + (o.hong ? " hong" : "") + (o.doDuoc ? "" : " suy") }));
        svg.appendChild(chuSvg(e, o.x + 11, o.y + 21, o.ten, "sd-ten"
          + (o.hong ? " hong" : "")));
        /* Chữ SVG không tự xuống dòng, nên dòng phụ phải cắt. Câu đủ đi
           vào `<title>` — cắt mà không giữ bản đủ ở đâu cả thì thông tin
           mất hẳn, chứ không phải chỉ khuất đi. */
        var phu = chuSvg(e, o.x + 11, o.y + 38, lamNgan(o.phu, 30), "sd-phu");
        var tenDay = e("title");
        tenDay.textContent = o.ten + " — " + o.phu;
        phu.appendChild(tenDay);
        svg.appendChild(phu);
      });
    });

    var w = el("div", "cuon");
    w.appendChild(svg);
    var ch = el("div", "chu-thich");
    ch.appendChild(nhanSvg("đang hỏng", "hong"));
    ch.appendChild(nhanSvg("chưa đo được sức khoẻ — chỉ SUY từ ty của nó", "suy"));
    ch.appendChild(nhanSvg("đang đọc được", ""));
    w.appendChild(ch);
    return w;
  }
  function chuSvg(e, x, y, s, lop) {
    var t = e("text", { x: x, y: y, class: lop });
    t.textContent = s;
    return t;
  }
  function nhanSvg(s, lop) {
    var d = el("span", "ct" + (lop ? " " + lop : ""));
    d.appendChild(el("i"));
    d.appendChild(el("span", null, s));
    return d;
  }
  function lamNgan(s, n) {
    s = String(s || "");
    return s.length > n ? s.slice(0, n - 1) + "…" : s;
  }

  /* ══════════════════ TRANG: SỔ CÁI ═════════════════════════════ */
  function ve_so_cai() {
    var f = document.createDocumentFragment();
    var t = (S && S.trungUong) || {}, sc = t.soCai || {}, sdk = t.soDangKy || {};
    var k = khoi("Sổ cái — chỉ THÊM, sửa bằng bút toán ĐẢO");
    var d = el("div", "day-so");
    d.appendChild(oSo("Bút toán", so(sc.soButToan), "từ " + String(sc.butDau || "").slice(0, 10)));
    d.appendChild(oSo("Lỗi ghi", so(sc.soLoiGhi),
      (sc.soLoiGhi || 0) ? "PHẢI XEM" : "sạch", (sc.soLoiGhi || 0) ? "am" : "duong"));
    d.appendChild(oSo("Tờ trình đã nhận", so(sdk.soToTrinh), "trong sổ đăng ký"));
    var tr = sdk.theoTrangThai || {};
    d.appendChild(oSo("Đã từ chối", so(tr.TU_CHOI),
      "so với " + so(tr.DA_MO || 0) + " đã mở"));
    k.appendChild(d);
    f.appendChild(k);

    var k2 = khoi("Bút toán theo loại");
    var loai = sc.theoLoai || {};
    k2.appendChild(bang([{ t: "Loại" }, { t: "Số", n: true }, { t: "Tổng USD", n: true }],
      Object.keys(loai).map(function (l) {
        return [{ t: l }, { t: so(loai[l].so), c: "n" }, { t: tien(loai[l].tongUsd), c: "n" }];
      })));
    f.appendChild(k2);

    var k3 = khoi("Tờ trình theo ty");
    var tt = sdk.theoTy || {};
    k3.appendChild(bang([{ t: "Ty" }, { t: "Tờ trình", n: true }],
      Object.keys(tt).map(function (x) {
        return [{ t: (TEN_DEP[x] || [x])[0] }, { t: so(tt[x]), c: "n" }];
      })));
    f.appendChild(k3);

    var k4 = khoi("Nhật ký");
    k4.appendChild(veNhatKyNgan());
    f.appendChild(k4);
    return f;
  }

  /* ══════════════════ TRANG: HỆ THỐNG ═══════════════════════════ */
  function ve_he_thong() {
    var f = document.createDocumentFragment();
    var t = (S && S.trungUong) || {}, tt = t.thucThi || {}, bt = t.banThamSo || {};
    var k = khoi("Vòng chạy");
    var d = el("div", "day-so");
    d.appendChild(oSo("Vòng", so(S.vong), "nhịp " + (S.nhipGiay || "—") + "s"));
    d.appendChild(oSo("Quét gần nhất", Math.round(S.quetCuoiMs || 0) + "ms",
      "lâu nhất " + Math.round(S.quetLauNhatMs || 0) + "ms"));
    d.appendChild(oSo("Chạy liên tục", gio(S.chayDuocGiay), "từ lúc khởi động"));
    d.appendChild(oSo("Chế độ", S.che || "—",
      S.tamDung ? "ĐANG TẠM DỪNG" : "đang chạy", S.tamDung ? "am" : null, true));
    k.appendChild(d);
    f.appendChild(k);

    var k2 = khoi("Lớp thực thi");
    var b = el("div", "viec-1" + (tt.moPhong ? " nhe" : ""));
    b.appendChild(el("b", null, tt.moPhong ? "MÔ PHỎNG — không đặt lệnh nào"
                                           : "ĐANG ĐẶT LỆNH THẬT"));
    b.appendChild(el("span", null, tt.loiNhac || ""));
    k2.appendChild(b);
    f.appendChild(k2);

    var k3 = khoi("Bản tham số",
      "Tham số có SỐ HIỆU và quay lui được. Đổi tham số phải đi qua Cổng Duyệt "
      + "— «tốt hơn nhưng tập trung hơn» bị từ chối, vì đó là bẻ phanh.");
    var hh = bt.hienHanh || {};
    k3.appendChild(bang([{ t: "Mục" }, { t: "Giá trị" }],
      [[{ t: "Số bản" }, { t: so(bt.soBan) }],
       [{ t: "Bản hiện hành" }, { t: "#" + (hh.so != null ? hh.so : "—") }],
       [{ t: "Ai đặt" }, { t: hh.nguoi || "—" }],
       [{ t: "Vì sao" }, { t: hh.vi || "—" }]]));
    /* Kho bản tham số THẮNG config.json — cố ý, không thì mỗi lần khởi động
       lại là xoá sạch mọi bản đã có người ký. Nhưng cái đúng ấy im lặng: sửa
       config, khởi động lại, không có gì xảy ra và cũng không có gì báo. Nên
       chỗ lệch phải hiện ra ĐÂY, cạnh bản đang chạy. */
    var lc = t.lechCauHinh || [];
    if (lc.length) {
      k3.appendChild(giai("`config.json` xin " + lc.length + " núm mà máy "
        + "KHÔNG chạy theo — kho bản tham số thắng config, và đó là cố ý. "
        + "Đường đổi tham số là Chẩn đoán → Cổng Duyệt → có người ký, "
        + "không phải sửa file."));
      k3.appendChild(bang([{ t: "Núm" }, { t: "config xin" }, { t: "đang chạy" }],
        lc.map(function (x) {
          return [{ t: x.nut }, { t: String(x.xin), c: "nhat" },
                  { t: String(x.dangChay), c: "n" }];
        })));
    }
    f.appendChild(k3);

    /* VÒNG HỌC — máy tự chẩn mình mỗi 15 phút, và cho tới lượt này kết
       quả ấy KHÔNG hiện ở đâu cả. Nó nằm trong ảnh chụp, đi qua API, và
       chỉ đọc được bằng `curl`. Cỗ máy tự học mà không ai xem nó học được
       gì là cỗ máy học cho chính nó nghe. Lần thứ sáu trong cùng cây mã:
       có mã, có phép kiểm, có dữ liệu ra, và không ai gọi. */
    var hc = t.hoc || {};
    var k4 = khoi("Vòng học — máy tự chẩn mình",
      "Chẩn xong thì đề xuất MỘT núm, chạy lại A/B trên chính tờ trình đã "
      + "có, rồi nhận hay trả lại. Đứng yên là một kết quả hợp lệ, và là "
      + "kết quả thường gặp nhất.");
    if (t.loiHoc) {
      var bl = el("div", "viec-1");
      bl.appendChild(el("b", null, "Vòng học LỖI"));
      bl.appendChild(el("span", null, String(t.loiHoc)));
      k4.appendChild(bl);
    }
    if (!(hc.trieuChung || []).length) {
      k4.appendChild(giai("chưa chẩn lượt nào — nhịp học đọc từ "
        + "`trungUong.nhipHocGiay`, và lượt đầu chạy ngay khi máy lên"));
    } else {
      k4.appendChild(bang(
        [{ t: "Triệu chứng" }, { t: "Nặng" }, { t: "Mô tả" }],
        hc.trieuChung.map(function (x) {
          return [{ t: x.ma },
                  { t: so(x.nang), c: (x.nang >= 3 ? "am" : "nhat") },
                  { t: x.moTa }];
        })));
    }
    if ((hc.deXuat || []).length) {
      k4.appendChild(bang(
        [{ t: "Núm đề xuất" }, { t: "Từ" }, { t: "Sang" }, { t: "Vì bệnh" }],
        hc.deXuat.map(function (x) {
          return [{ t: x.nut }, { t: so(x.tu, 3), c: "n" },
                  { t: so(x.den, 3), c: "n" }, { t: x.vi }];
        })));
    } else if ((hc.trieuChung || []).length) {
      k4.appendChild(giai("Có triệu chứng nhưng KHÔNG đề xuất vặn gì — "
        + "nghĩa là bệnh này không có núm nào chữa được. Đó là một câu trả "
        + "lời, không phải một chỗ trống."));
    }
    var dd = hc.doDuoc || {};
    if (dd.ketLuan) {
      k4.appendChild(giai("A/B: " + dd.ketLuan + " — " + (dd.vi || "")));
    }
    if (hc.luc) k4.appendChild(giai("chẩn lúc " + hc.luc));
    f.appendChild(k4);

    /* GHI DANH MỤC. `loiGhi` im lặng là kiểu hỏng đắt nhất ở đây: máy vẫn
       chạy, vẫn kế toán, vẫn đúng — cho tới lần khởi động lại kế tiếp, và
       lúc ấy mọi vị thế biến mất cùng với đường NAV. */
    var lu = t.luuDanhMuc || {};
    var k5 = khoi("Ghi danh mục xuống đĩa",
      "Vị thế mô phỏng sống qua khởi động lại nhờ file này. Ghi hỏng thì "
      + "máy vẫn chạy đúng — cho tới lần bật lại kế tiếp.");
    var d5 = el("div", "day-so");
    d5.appendChild(oSo("Đã nạp lại", lu.nap ? "có" : "chưa",
      so(lu.soViThe) + " vị thế · " + so(lu.soDiemNav) + " điểm NAV",
      lu.nap ? "duong" : "nhat", !lu.co));
    d5.appendChild(oSo("Máy tắt bao lâu",
      lu.giayTatMay == null ? "—" : gio(lu.giayTatMay),
      "quãng ấy KHÔNG được cộng lãi cho vị thế nào", "nhat"));
    /* CỘNG DỒN qua mọi lần khởi động, không chỉ lần này. Mỗi lần bật lại
       vứt một cửa sổ kế toán — với engine thu theo MỐC (funding 8 giờ),
       vứt đúng cửa sổ chứa mốc là mất trọn một kỳ, và sổ chỉ ghi «thu
       0», y hệt một engine không kiếm được gì. Đo 30/08:
       `basis.cash_carry.v1` chạy 5.222 vòng, không vòng nào mù, và CHƯA
       TỪNG ghi một dòng FUNDING nào. */
    d5.appendChild(oSo("Đã bật lại", so(lu.soLanKhoiDong) + " lần",
      lu.tongGiayTatMay == null ? "—"
        : "tổng " + gio(lu.tongGiayTatMay) + " tắt · mỗi lần vứt một cửa "
          + "sổ kế toán",
      (lu.soLanKhoiDong || 0) > 1 ? "nhat" : "duong"));
    d5.appendChild(oSo("Lỗi ghi", lu.loiGhi ? "CÓ" : "không",
      lu.loiGhi || "ghi được mỗi vòng", lu.loiGhi ? "am" : "duong",
      !!lu.loiGhi));
    k5.appendChild(d5);
    if (lu.vi) k5.appendChild(giai(lu.vi));
    f.appendChild(k5);

    /* THÔNG CHÍNH TY — cửa nhận tờ trình. `tongSaiKhuon` là số tờ bị trả
       vì sai khuôn, và một ty đột nhiên sai khuôn hàng loạt là một ty vừa
       hỏng chứ không phải một ty vừa nghiêm khắc. */
    /* THAM SỐ ĐANG CHẠY. Đây là những con số quyết định mọi thứ, và cho
       tới lượt này chúng không hiện ở đâu — buồng lái chỉ nói bản tham số
       SỐ MẤY chứ không nói bản ấy CHỨA GÌ. Hệ quả đo được hôm nay: họ tín
       dụng chạm trần `tranMotTy` 0,5 và đứng đó nhiều giờ, trong khi
       người xem không có cách nào thấy cái trần ấy đang là bao nhiêu. */
    var ts = t.thamSo || {}, pb2 = t.phanBo || {};
    var k7 = khoi("Tham số ĐANG CHẠY",
      "Không phải `config.json` — đây là bản tham số kho đang giữ, và nó "
      + "thắng config. Trần nào đang bó thì đọc cạnh phễu ở trang Cơ hội.");
    ["ruiRoTong", "phanBo"].forEach(function (nhom) {
      var o = nhom === "phanBo" ? pb2 : (ts[nhom] || {});
      var ds = Object.keys(o).sort();
      if (!ds.length) return;
      k7.appendChild(el("h4", null, nhom));
      k7.appendChild(bang([{ t: "Núm" }, { t: "Giá trị", n: true }],
        ds.map(function (x) {
          var v = o[x];
          return [{ t: x }, { t: typeof v === "number" ? so(v, 4)
                                : String(v), c: "n" }];
        })));
    });
    /* NÚM NÀO ĐANG CHẠM — không bắt người đọc so hai bảng bằng mắt.
       Đo 30/08: danh mục đầy 120/120 ghế và 100% lần từ chối là
       `tran-vi-the`, trong khi 27,8% vốn khả dụng nằm không. Bảng núm
       ở trên có con số 120, bảng danh mục ở trang khác có con số 120,
       và chỉ khi đặt cạnh nhau mới thấy cái trần đang bó. */
    var _dmS = t.danhMuc || {};
    if (_dmS.soViThe != null && pb2.toiDaSoViThe) {
      var _cham = _dmS.soViThe >= pb2.toiDaSoViThe;
      k7.appendChild(giai((_cham ? "⚠ ĐANG CHẠM TRẦN SỐ VỊ THẾ: "
                                 : "Số vị thế: ")
        + so(_dmS.soViThe) + "/" + so(pb2.toiDaSoViThe)
        + (_cham
           ? " — mọi cơ hội mới đều bị từ chối vì HẾT CHỖ, không phải vì "
             + "hết tiền hay vì rủi ro. Đổi con số ấy là `dat_tham_so`, "
             + "và nó đòi TÊN NGƯỜI."
           : " — còn " + so(pb2.toiDaSoViThe - _dmS.soViThe) + " chỗ.")));
    }
    f.appendChild(k7);

    /* THU VƯỢT TRẦN — lớp lỗi IN RA TIỀN. Trung Ương ghi thẳng con số
       ty đưa, nên một ty quên chia cho 8.760 giờ làm NAV phồng lên mà
       `lechTien` vẫn khớp: sổ ghi đúng con số bịa ấy. */
    var kts = t.keToan || {};
    if (kts.soThuVuotTran) {
      var kvt = khoi("THU VƯỢT TRẦN — NAV có thể đang phồng",
        "Trần dựng từ chính lời hứa của tờ trình, đã nhân biên rộng gấp "
        + "mười. Vượt nó thường là lỗi ĐƠN VỊ, không phải chợ biến động.");
      kvt.appendChild(bang(
        [{ t: "Ty" }, { t: "Thu", n: true }, { t: "Trần", n: true },
         { t: "Vượt", n: true }],
        (kts.thuVuotTran || []).map(function (x) {
          return [{ t: x.chienLuoc },
                  { t: tien(x.thuUsd, 6), c: "am" },
                  { t: tien(x.tranUsd, 6), c: "nhat" },
                  { t: x.lanVuot == null ? "—" : so(x.lanVuot, 0) + "×",
                    c: "am" }];
        })));
      kvt.appendChild(giai("Trung Ương KHÔNG cắt con số ấy — ty biết việc "
        + "của ty, và cắt là bịa ra một con số thứ ba mà không ai đo. Nó "
        + "đếm và khai; sửa là sửa MÃ của ty, không phải vặn tham số."));
      f.appendChild(kvt);
    }

    var tc = t.thongChinh || {};
    var k6 = khoi("Thông Chính Ty — cửa nhận tờ trình");
    var d6 = el("div", "day-so");
    d6.appendChild(oSo("Đã nhận", so(tc.tongNhan),
      "đang chờ " + so(tc.dangCho) + " · trần " + so(tc.tran)));
    d6.appendChild(oSo("Trả vì SAI KHUÔN", so(tc.tongSaiKhuon),
      "một ty sai khuôn hàng loạt là một ty vừa hỏng",
      (tc.tongSaiKhuon || 0) ? "am" : "duong"));
    d6.appendChild(oSo("Trả vì ĐẦY", so(tc.tongTran),
      "cửa đầy thì tờ đến sau bị trả, không xếp hàng vô hạn",
      (tc.tongTran || 0) ? "nhat" : "duong"));
    k6.appendChild(d6);
    f.appendChild(k6);

    return f;
  }

  /* ══════════════════ TRANG: MỘT ĐỘNG CƠ ════════════════════════ */
  var O_PERP = "co-hoi";
  function ve_mot_dong_co(ma) {
    var f = document.createDocumentFragment();
    var dc = dsDongCo().filter(function (x) { return x.ma === ma; })[0];
    var lui = el("a", "duong-lui", "← Mười ba động cơ");
    lui.href = "/dong-co"; lui.setAttribute("data-lien", "");
    f.appendChild(lui);

    if (!dc) {
      var l = el("div", "loi-o");
      l.appendChild(el("h2", null, "Không có động cơ nào tên «" + ma + "»"));
      f.appendChild(l);
      return f;
    }

    var k = khoi(dc.ten);
    var dd = el("div");
    dd.appendChild(cot(dc.tt));
    k.appendChild(dd);
    k.appendChild(giai(dc.vi || dc.mo || ""));

    if (!dc.dung) {
      var b = el("div", "viec-1");
      b.appendChild(el("b", null, "Chưa dựng được"));
      b.appendChild(el("span", null, "Nó cần dữ liệu KHÔNG công khai. Đó là "
        + "«không làm được từ đây», khác hẳn «chưa làm» — và sổ engine giữ "
        + "ranh giới ấy bằng phép canh chứ không bằng văn xuôi."));
      k.appendChild(b);
      f.appendChild(k);
      return f;
    }

    var d = el("div", "day-so");
    d.appendChild(oSo("Lượt quét", so(dc.soQuet)));
    d.appendChild(oSo("Cơ hội đã cân", so(dc.soCoHoi)));
    d.appendChild(oSo("Qua cổng ty", so(dc.soQua),
      dc.soCoHoi ? ((dc.soQua / dc.soCoHoi) * 100).toFixed(3) + "%" : ""));
    d.appendChild(oSo("Ngưỡng kinh tế", tien(dc.nguong, 0),
      "rót được nhiều nhất " + tien(dc.tran, 0)));
    k.appendChild(d);

    /* VÌ SAO cổng ty từ chối. Đây là cái lọc LỚN NHẤT của cả cỗ máy —
       99,98% số cơ hội chết ở đây — và cho tới lượt này nó không khai một
       chữ nào: `mot_luot()` viết `qua, _ = self.xet(co)`, vứt lý do ngay
       tại chỗ nó vừa được sinh ra. Một ty hỏng trông hệt một ty đang từ
       chối đúng. */
    if ((dc.lyDoCongTy || []).length) {
      var kl2 = el("div", "vi-sao-tu-choi");
      kl2.appendChild(el("h4", null, "Vì sao CỔNG TY từ chối"));
      var r2 = el("div", "viec-1 nhe");
      dc.lyDoCongTy.forEach(function (x) {
        r2.appendChild(el("span", null, "× " + so(x.so) + "  [" + x.ma + "] "
          + (x.cau || "")));
      });
      r2.appendChild(el("span", "nhat", "— trên " + so(dc.soBiTuChoi)
        + " lần từ chối" + (dc.soMaBiBo
          ? " · " + so(dc.soMaBiBo) + " mã bị BỎ vì quá trần 24 mã" : "")
        + (dc.soMaThieuCau
          ? " · " + so(dc.soMaThieuCau) + " mã KHÔNG kèm câu" : "")));
      kl2.appendChild(r2);
      k.appendChild(kl2);
      k.appendChild(giai("Một lần từ chối mang được NHIỀU mã, nên tổng các "
        + "mã có thể lớn hơn số lần từ chối. Gộp theo MÃ chứ không theo câu "
        + "— câu mang số bên trong thì một nguyên nhân vỡ thành hàng trăm "
        + "dòng."));
    } else if (dc.soBiTuChoi) {
      k.appendChild(giai("Cổng ty từ chối " + so(dc.soBiTuChoi) + " lần mà "
        + "KHÔNG khai mã nào — `xet()` của ty này trả về danh sách lý do "
        + "rỗng. Từ chối không lý do là một con số câm."));
    }
    f.appendChild(k);

    /* Chỉ ty chênh funding mới có tầng ba đã dựng. Nói thẳng thay vì để
       trang trống — trang trống đọc thành "hỏng". */
    if (ma !== "perpetual.funding_spread.v1" || !window.TYPERP) {
      var k2 = khoi("Tầng chi tiết");
      k2.appendChild(giai("Động cơ này chưa có trang mổ máy riêng. Số thô của "
        + "nó vẫn đọc được ở API: curl -s localhost:"
        + (location.port || "5188") + "/api/trung-uong"));
      f.appendChild(k2);
      return f;
    }

    window.TYPERP.dat(S);
    var tab = el("div", "tab-con");
    [["co-hoi", "Cơ hội"], ["bao-gia", "Báo giá"], ["cang", "Cảng"],
     ["cua", "Cửa rủi ro"], ["to-trinh", "Tờ trình"], ["hoc", "Đào tạo"],
     ["nhat-ky", "Nhật ký"]].forEach(function (x) {
      var b = el("button", O_PERP === x[0] ? "chon" : null, x[1]);
      b.type = "button";
      b.dataset.perp = x[0];
      tab.appendChild(b);
    });
    f.appendChild(tab);
    try {
      f.appendChild(window.TYPERP[O_PERP]());
    } catch (e) {
      var lo = el("div", "loi-o");
      lo.appendChild(el("h2", null, "Ô «" + O_PERP + "» vẽ hỏng"));
      lo.appendChild(el("p", null, String(e && e.message || e)));
      lo.appendChild(el("p", "giai", "Máy VẪN ĐANG CHẠY — đây là lỗi của "
        + "trang, không phải của runtime."));
      f.appendChild(lo);
    }
    return f;
  }

  /* ══════════════════ BỘ ĐỊNH TUYẾN ═════════════════════════════ */
  /* ══════════════════ TRANG: BỂ THANH KHOẢN V3 ═══════════════════
   * Trang của ty thứ mười. Nó đọc API RIÊNG (`/api/be-thanh-khoan`) chứ
   * không đọc `S`: báo cáo của nó là một thứ khác hẳn ảnh chụp Trung
   * Ương — dải, σ, quyết định theo luật, vị thế NGƯỜI giữ ở OKX — và
   * nhét nó vào `/api/trang-thai` là làm ảnh chụp ấy nặng thêm cho mọi
   * trang khác. Lần vẽ đầu hiện «đang tải», tải xong vẽ lại.           */
  var BTK = null, BTK_LOI = "", BTK_DANG_TAI = false;
  function tai_btk() {
    if (BTK_DANG_TAI || typeof fetch !== "function") return;
    BTK_DANG_TAI = true;
    var p;
    try { p = fetch("/api/be-thanh-khoan", { cache: "no-store" }); }
    catch (e) { BTK_DANG_TAI = false; return; }
    p.then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
     .then(function (j) { BTK = j; BTK_LOI = ""; })
     .catch(function (e) { BTK_LOI = String(e && e.message || e); })
     .finally(function () {
       BTK_DANG_TAI = false;
       if (duong().o === "be-thanh-khoan") { try { ve(); } catch (e) { } }
     });
  }
  function bps(v) { return v == null || !isFinite(v) ? "—" : (v >= 0 ? "+" : "") + Math.round(v) + " bps"; }
  function pc(v, n) { return v == null || !isFinite(v) ? "—" : (v * 100).toFixed(n == null ? 1 : n) + "%"; }
  var TEN_HD = { VAO: "VÀO", GIU: "GIỮ", CHO: "CHỜ", RUT: "RÚT", NOI_RONG: "NỚI DẢI",
                 THU_HEP: "THU HẸP", DOI_DAI: "ĐỔI DẢI" };
  var MAU_HD = { VAO: "LIVE", GIU: "PAPER", CHO: "OBSERVE", RUT: "FAULT",
                 NOI_RONG: "FAULT", THU_HEP: "PAPER", DOI_DAI: "FAULT" };
  function hd_badge(hd, lon) {
    var e = el("span", "btk-hd " + (MAU_HD[hd] || "OBSERVE") + (lon ? " lon" : ""),
               TEN_HD[hd] || hd || "—");
    return e;
  }
  function o_nho(ten, gt, lop) {
    var o = el("div", "btk-o");
    o.appendChild(el("span", "t", ten));
    o.appendChild(el("span", "g" + (lop ? " " + lop : ""), gt));
    return o;
  }
  function gioTuIso(s) {
    var t = Date.parse(s); if (isNaN(t)) return "—";
    var d = new Date(t);
    return ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2)
      + " " + ("0" + d.getDate()).slice(-2) + "/" + ("0" + (d.getMonth() + 1)).slice(-2);
  }

  function ve_be_thanh_khoan() {
    var f = document.createDocumentFragment();
    var src = BTK || (S && S.beThanhKhoan) || null;
    if (!src) {
      tai_btk();
      var k0 = khoi("Bể thanh khoản V3 — đang tải");
      k0.appendChild(giai(BTK_LOI
        ? "Không đọc được /api/be-thanh-khoan: " + BTK_LOI + " — ty chưa đăng ký "
          + "(Trung Ương tắt?) hoặc chưa quét lượt nào. Dòng lệnh: "
          + "python -m lp_v3.hom_nay"
        : "Đang hỏi runtime. Trang này đọc API riêng của ty thứ mười."));
      f.appendChild(k0);
      return f;
    }
    var b = src, ph = b.phien || {}, th = b.thuong || {}, cd = b.cheDo || {},
        tg = b.thiTruongGoc || {}, hd = b.tomTatHanhDong || {}, kn = b.kinhNghiem || {};

    /* ── BÂY GIỜ: một đoạn, đọc trước mọi con số ─────────────────── */
    var bg = el("p", "bay-gio");
    bg.appendChild(el("b", null, "BÂY GIỜ · " + (cd.ten || "—")));
    bg.appendChild(document.createTextNode(
      (b.lucVn || "") + ". " + (tg.cau || "") + ". " + (cd.loiKhuyen || "")
      + " Đang theo " + so((b.pool || []).length) + " pool: "
      + Object.keys(hd).map(function (k) { return (TEN_HD[k] || k) + " " + hd[k].length; }).join(", ")
      + "."));
    f.appendChild(bg);

    /* ── năm ô số ─────────────────────────────────────────────────── */
    var k = khoi("Năm câu hỏi, mười giây");
    var d = el("div", "day-so");
    d.appendChild(oSo("Thị trường gốc", tg.trangThai === "MO" ? "MỞ" : tg.trangThai === "SAP_MO" ? "SẮP MỞ" : "ĐÓNG",
      ph.gioToiMo != null ? "sàn Mỹ mở sau " + Number(ph.gioToiMo).toFixed(1) + "h"
        : ph.gioToiDong != null ? "đóng sau " + Number(ph.gioToiDong).toFixed(1) + "h" : "token chạy 24/7",
      tg.trangThai === "MO" ? "duong" : tg.trangThai === "DONG" ? "am" : null));
    d.appendChild(oSo("Thưởng còn", th.conGio == null ? "—" : Math.round(th.conGio) + " giờ",
      th.ketThuc ? "hết " + th.ketThuc + " VN" : "không có chương trình"));
    d.appendChild(oSo("Pool VÀO được", so((hd.VAO || []).length),
      (hd.VAO || []).join(", ") || "không pool nào qua đủ luật", (hd.VAO || []).length ? "duong" : null));
    d.appendChild(oSo("Vị thế đang giữ", so((b.viThe || []).length),
      (b.viThe || []).length ? "máy theo dõi mỗi 5 phút" : "ghi ở mục Vị thế bên dưới"));
    d.appendChild(oSo("Kinh nghiệm", so(kn.soQuyetDinh) + " → " + so(kn.soKetCuc),
      "quyết định đã ghi → đã chấm" + (kn.soChuaCham ? " · " + so(kn.soChuaCham) + " chờ chấm" : "")));
    k.appendChild(d);

    /* cảnh báo thế giới: nguồn mù, rủi ro thị trường gốc, sự kiện */
    var canh = el("div", "viec");
    if ((tg.ruiRo || []).length) {
      var v0 = el("div", "viec-1");
      v0.appendChild(el("b", null, "Thị trường gốc " + (tg.trangThai === "DONG" ? "ĐÓNG" : "sắp mở") + " · token 24/7"));
      v0.appendChild(el("span", null, "Rủi ro đang bật: " + tg.ruiRo.join(" · ")
        + ". Máy không dùng cùng một dải bất kể sàn Mỹ mở hay đóng."));
      canh.appendChild(v0);
    }
    if ((b.nguonMu || []).length) {
      var v1 = el("div", "viec-1 nhe");
      v1.appendChild(el("b", null, "Nguồn đang mù (" + b.nguonMu.length + ")"));
      b.nguonMu.forEach(function (x) { v1.appendChild(el("span", null, "✗ " + x)); });
      canh.appendChild(v1);
    }
    if ((ph.suKien || []).length) {
      var v2 = el("div", "viec-1 nhe");
      v2.appendChild(el("b", null, "Sự kiện 7 ngày tới"));
      ph.suKien.slice(0, 8).forEach(function (s) {
        v2.appendChild(el("span", null, gioTuIso(s.luc) + " — " + s.ten + (s.ma ? " (" + s.ma + ")" : "")));
      });
      canh.appendChild(v2);
    }
    if (th.kiemCheo) {
      var v3 = el("div", "viec-1 nhe");
      v3.appendChild(el("b", null, "Kiểm chéo quỹ thưởng"));
      v3.appendChild(el("span", null, th.kiemCheo));
      canh.appendChild(v3);
    }
    if (canh.children.length) k.appendChild(canh);
    k.appendChild(giai("Giả định đang dùng: " + (b.giaDinh || []).join(" | ")));
    f.appendChild(k);

    /* ── HỒ SƠ TÌNH BÁO từng pool ─────────────────────────────────── */
    var k2 = khoi("Hồ sơ từng pool — hành động trước, con số sau",
      "Mỗi thẻ là một pool. Dòng đầu là câu máy kết luận; APY hiển thị được TÁCH thành "
      + "phí và thưởng; các ô dưới là những gì kết luận ấy đứng trên.");
    var luoi = el("div", "btk-luoi");
    var thu = { VAO: 0, GIU: 1, DOI_DAI: 2, NOI_RONG: 3, THU_HEP: 4, RUT: 5, CHO: 6 };
    (b.pool || []).slice().sort(function (x, y) {
      var d0 = (thu[x.hanhDong] || 9) - (thu[y.hanhDong] || 9);
      if (d0) return d0;
      var nx = x.dai && x.dai.netBps != null ? x.dai.netBps : -1e18;
      var ny = y.dai && y.dai.netBps != null ? y.dai.netBps : -1e18;
      return ny - nx;
    }).forEach(function (p) {
      var dd = p.dai || {}, at = p.apyTach || {};
      var the = el("article", "btk-the");
      the.dataset.hd = MAU_HD[p.hanhDong] || "OBSERVE";
      var dau = el("header");
      var ten = el("div", "ten");
      ten.appendChild(el("b", null, p.kyHieu));
      ten.appendChild(el("i", null, "[" + (p.luat || "") + "]"));
      dau.appendChild(ten);
      dau.appendChild(hd_badge(p.hanhDong, true));
      the.appendChild(dau);
      the.appendChild(el("p", "ket-luan", p.tomTat || p.lyDo || ""));

      /* APY tách: một số lớn, rồi mỗi thành phần một dòng — như
         «25,43% = 6,38% iFARM + 19,66% Uniswap» */
      var tong = at.hienThiPct, phi = at.phiPct, thuong = at.thuongPct;
      var thanh = el("div", "btk-apy");
      var tg = el("div", "tong");
      tg.appendChild(el("span", "nhan-nho", "APY hiển thị ở OKX"));
      tg.appendChild(el("b", null, tong == null ? "—" : Number(tong).toFixed(2) + "%"));
      thanh.appendChild(tg);
      [["phi", "Phí giao dịch", phi, "phí 0,05% của pool trả cho LP"
          + (at.giaDinh ? " · tách bằng GIẢ ĐỊNH, chưa đo" : " · tách từ khối lượng")],
       ["thuong", "Thưởng OKX", thuong, (th.ketThuc ? "hết " + th.ketThuc + " VN" : "không có chương trình")
          + " · chia theo phí, chụp ngẫu nhiên"]
      ].forEach(function (r) {
        var h = el("div", "apy-hang " + r[0]);
        h.appendChild(el("i"));
        h.appendChild(el("b", null, r[2] == null ? "—" : Number(r[2]).toFixed(2) + "%"));
        var c = el("div");
        c.appendChild(el("span", "ten", r[1]));
        c.appendChild(el("span", "mo", r[3]));
        h.appendChild(c);
        thanh.appendChild(h);
      });
      var bar = el("div", "bar");
      var tongPct = (phi || 0) + (thuong || 0);
      if (tongPct > 0) {
        var i1 = el("i", "phi"); i1.style.width = ((phi || 0) / tongPct * 100).toFixed(1) + "%";
        var i2 = el("i", "thuong"); i2.style.width = ((thuong || 0) / tongPct * 100).toFixed(1) + "%";
        bar.appendChild(i1); bar.appendChild(i2);
      }
      thanh.appendChild(bar);
      the.appendChild(thanh);

      /* lưới số */
      var l = el("div", "btk-so");
      l.appendChild(o_nho("Giá", p.gia == null ? "—" : Number(p.gia).toFixed(2)
        + " · " + (p.nguonGia === "goc-tuc-thoi" ? "đang giao dịch" : p.nguonGia === "goc" ? "đóng cửa" : p.nguonGia || "?")
        + (p.tuoiGiaGio == null ? "" : ", " + (p.tuoiGiaGio < 1 ? Math.round(p.tuoiGiaGio * 60) + " phút" : Math.round(p.tuoiGiaGio) + "h")),
        p.gia == null ? "am" : null));
      l.appendChild(o_nho("σ năm", p.sigma == null ? "chưa đo — " + so(p.soPhien) + " phiên"
        : pc(p.sigma, 0) + " / " + so(p.soPhien) + " phiên (" + (p.nguonSigma || "?") + ")",
        p.sigma == null ? "am" : p.sigma > 0.8 ? "am" : null));
      l.appendChild(o_nho("TVL", tien(p.tvlUsd, 0) + ((p.tvlUsd && p.tvlUsd < 50000) ? " · MỎNG" : ""),
        (p.tvlUsd && p.tvlUsd < 50000) ? "am" : null));
      l.appendChild(o_nho("Dải đề xuất", dd.Pa == null ? "—"
        : Number(dd.Pa).toFixed(2) + " – " + Number(dd.Pb).toFixed(2) + " (±" + Number(dd.rongPct).toFixed(1) + "%, "
          + Math.round(dd.hieuSuat) + "×)"));
      l.appendChild(o_nho("P(văng) ≤", dd.pVang == null ? "—" : pc(dd.pVang, 0),
        dd.pVang == null ? null : dd.pVang > 0.6 ? "am" : dd.pVang < 0.3 ? "duong" : null));
      l.appendChild(o_nho("Phí/LVR", dd.tiLePhiTrenLvr == null ? "—" : Number(dd.tiLePhiTrenLvr).toFixed(2),
        dd.tiLePhiTrenLvr == null ? null : dd.tiLePhiTrenLvr >= 1.5 ? "duong" : "am"));
      l.appendChild(o_nho("Phí + thưởng + IL", (dd.phiBps == null ? "—" : bps(dd.phiBps)) + " · "
        + (dd.thuongBps == null ? "—" : bps(dd.thuongBps)) + " · " + (dd.ilKyVongBps == null ? "—" : bps(dd.ilKyVongBps))));
      l.appendChild(o_nho("NET / " + (dd.giuGio ? Math.round(dd.giuGio) + "h" : "cửa sổ"), bps(dd.netBps),
        dd.netBps == null ? null : dd.netBps > 0 ? "duong" : "am"));
      l.appendChild(o_nho("Điểm rủi ro", p.diemRuiRo == null ? "—" : Number(p.diemRuiRo).toFixed(2) + " / 1",
        p.diemRuiRo == null ? null : p.diemRuiRo >= 0.7 ? "am" : null));
      l.appendChild(o_nho("Vốn xin / sức chứa", tien(p.vonXinUsd, 0) + " / " + tien(p.sucChuaUsd, 0)));
      l.appendChild(o_nho("Sàn gốc", p.thiTruongGoc === "MO" ? "MỞ" : p.thiTruongGoc === "SAP_MO" ? "SẮP MỞ" : "ĐÓNG",
        p.thiTruongGoc === "MO" ? "duong" : "am"));
      var bd = p.bienDong || {};
      l.appendChild(o_nho("Biến động", bd.doi1NgayPct == null ? "—"
        : (bd.doi1NgayPct >= 0 ? "+" : "") + Number(bd.doi1NgayPct).toFixed(1) + "% ngày · "
          + (bd.doi5NgayPct == null ? "" : (bd.doi5NgayPct >= 0 ? "+" : "") + Number(bd.doi5NgayPct).toFixed(1) + "% tuần")
          + (bd.trangThai ? " · σ " + ({ NO: "đang NỞ", CO: "đang CO", ON: "ổn" })[bd.trangThai] : ""),
        bd.trangThai === "NO" ? "am" : null));
      the.appendChild(l);

      /* vì sao + tin */
      var vs = el("div", "btk-vi-sao");
      (p.luatKhop || []).slice(0, 4).forEach(function (x) {
        vs.appendChild(el("span", null, "• [" + x.ma + "] " + x.lyDo));
      });
      (p.tin || []).slice(0, 2).forEach(function (t) {
        vs.appendChild(el("span", "tin", "📰 " + (t.tieuDe || "").slice(0, 90)
          + ((t.co || []).length ? "  [" + t.co.join(", ") + "]" : "")));
      });
      if ((p.thieu || []).length) vs.appendChild(el("span", "am", "thiếu: " + p.thieu.join(", ")));
      the.appendChild(vs);
      luoi.appendChild(the);
    });
    k2.appendChild(luoi);
    k2.appendChild(giai("NET = phí + thưởng + IL kỳ vọng − gas, trên vốn xin, trong cửa sổ giữ; P(văng) là "
      + "CẬN TRÊN; «tách bằng GIẢ ĐỊNH» nghĩa là chưa có khối lượng để biết phí gốc thật — dán địa chỉ pool "
      + "và khối lượng ngày vào data/lp-v3/cau-hinh.json để đo thật."));
    f.appendChild(k2);

    /* ── VỊ THẾ ─────────────────────────────────────────────────────── */
    var k3 = khoi("Vị thế đang giữ ở OKX", "Máy không đặt lệnh và không cầm khoá. Dán ĐỊA CHỈ ví công khai để "
      + "máy tự đọc NFT vị thế Uniswap V3 trên X Layer; hoặc ghi tay bên dưới.");
    var vi = b.vi || {};
    var oVi = el("div", "btk-form");
    oVi.appendChild(el("b", null, vi.diaChi
      ? "Ví " + String(vi.diaChi).slice(0, 8) + "…" + String(vi.diaChi).slice(-4) + " (chỉ đọc) — "
        + (vi.loi ? "✗ " + vi.loi
           : so(vi.soViThe) + " vị thế trên chuỗi · " + tien(vi.giaTriUsd, 0)
             + (vi.phiChoThuUsd != null ? " · phí chưa thu " + tien(vi.phiChoThuUsd, 2) : "")
             + (vi.quanLyViThe ? " · hợp đồng " + String(vi.quanLyViThe).slice(0, 10) + "…"
                : vi.quanLyViTheDangDung === "mac-dinh-uniswap-chinh-thuc" ? " · hợp đồng Uniswap V3 mặc định" : ""))
      : "Chưa nối ví — dán địa chỉ ví X Layer. Hợp đồng mặc định là Uniswap V3 chính thức trên X Layer"
        + (vi.macDinh ? " (" + String(vi.macDinh).slice(0, 10) + "…)" : "")
        + "; đọc ra 0 vị thế thì dán thêm hash một giao dịch thêm thanh khoản để suy đúng hợp đồng."));
    var inVi = el("input"); inVi.placeholder = "0x… địa chỉ ví (công khai)"; inVi.value = vi.diaChi || "";
    inVi.style.width = "340px";
    var inTx = el("input"); inTx.placeholder = "0x… hash giao dịch thêm thanh khoản (để suy hợp đồng)";
    inTx.value = vi.txMau || ""; inTx.style.width = "440px";
    var nutVi = el("button", "nho", vi.diaChi ? "Cập nhật ví" : "Nối ví (chỉ đọc)"); nutVi.type = "button";
    nutVi.addEventListener("click", function () {
      fetch("/api/be-thanh-khoan/vi", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ diaChi: inVi.value.trim(), txMau: inTx.value.trim() }) })
        .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.detail || r.status); }); })
        .then(function () { nhac("đã đặt ví — lượt quét kế tiếp sẽ đọc vị thế"); BTK = null; ve(); })
        .catch(function (e) { nhac("đặt ví hỏng: " + (e && e.message || e)); });
    });
    oVi.appendChild(inVi); oVi.appendChild(inTx); oVi.appendChild(nutVi);
    if ((vi.ngoaiDanhMuc || []).length) {
      oVi.appendChild(el("span", "am", "Ví có " + vi.ngoaiDanhMuc.length + " vị thế ở pool CHƯA theo dõi: "
        + vi.ngoaiDanhMuc.map(function (x) { return x.kyHieu + " #" + x.tokenId; }).join(", ")
        + " — thêm pool vào cau-hinh.json để máy cân."));
    }
    k3.appendChild(oVi);
    if (!(b.viThe || []).length) {
      k3.appendChild(el("p", "viec-khong", "Chưa ghi vị thế nào."));
    } else {
      k3.appendChild(bang(
        [{ t: "Pool" }, { t: "Nguồn" }, { t: "Dải" }, { t: "Giá trị", n: true }, { t: "Trong dải" },
         { t: "IL", n: true }, { t: "Phí chưa thu", n: true }, { t: "Giữ", n: true }, { t: "Khuyên" },
         { t: "Vì sao" }, { t: "" }],
        b.viThe.map(function (v) {
          var vt = v.viThe || {}, tt = v.trangThai || {}, q = v.quyetDinh || {};
          var o = { t: "" };
          if (vt.nguon !== "chuoi") {
            var nutDong = el("button", "nho", "Đã rút — ghi kết cục");
            nutDong.type = "button"; nutDong.dataset.btkDong = vt.ma;
            o = { el: nutDong };
          }
          return [
            { t: v.kyHieu },
            { t: vt.nguon === "chuoi" ? "chuỗi #" + (vt.tokenId || "?") : "ghi tay" },
            { t: Number(vt.Pa).toFixed(2) + " – " + Number(vt.Pb).toFixed(2) },
            { t: tien(vt.vonUsd, 0), c: "n" },
            { t: tt.trongDai == null ? "?" : tt.trongDai ? "trong" : "NGOÀI", c: tt.trongDai === false ? "am" : "" },
            { t: tt.ilPct == null ? "—" : Number(tt.ilPct).toFixed(2) + "%", c: "n" },
            { t: vt.phiChoThuUsd == null ? "—" : tien(vt.phiChoThuUsd, 2), c: "n" },
            { t: tt.gioGiu == null ? "—" : Math.round(tt.gioGiu) + "h", c: "n" },
            { el: hd_badge(q.hanhDong) },
            { t: q.lyDo || "" }, o
          ];
        })));
    }
    var form = el("div", "btk-form");
    form.appendChild(el("b", null, "Ghi vị thế vừa mở ở OKX"));
    var inp = {};
    [["kyHieu", "pool (VD NVDAx-USDG)"], ["Pa", "mép dưới"], ["Pb", "mép trên"],
     ["vonUsd", "vốn USD"], ["giaMo", "giá lúc mở"]].forEach(function (x) {
      var i = el("input"); i.placeholder = x[1]; i.dataset.k = x[0]; inp[x[0]] = i; form.appendChild(i);
    });
    var nutMo = el("button", "nho", "Ghi sổ"); nutMo.type = "button";
    nutMo.addEventListener("click", function () {
      var than = {};
      Object.keys(inp).forEach(function (kk) { than[kk] = kk === "kyHieu" ? inp[kk].value.trim() : Number(inp[kk].value); });
      fetch("/api/be-thanh-khoan/vi-the", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(than) })
        .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.detail || r.status); }); })
        .then(function () { nhac("đã ghi vị thế"); BTK = null; ve(); })
        .catch(function (e) { nhac("ghi hỏng: " + (e && e.message || e)); });
    });
    form.appendChild(nutMo);
    k3.appendChild(form);
    f.appendChild(k3);

    /* ── VÒNG HỌC: dự đoán → thực tế → bài học → tiến hoá ─────────── */
    var k4 = khoi("Vòng học — dự đoán, thực tế, bài học, tiến hoá có cổng",
      "Mọi quyết định (kể cả CHỜ) được ghi kèm dải và bối cảnh; hết cửa sổ giữ thì chấm bằng đường "
      + "giá thật hoặc bằng kết cục bạn ghi từ OKX. Bài học chỉ được gọi là bài học khi n ≥ 5 và độ tin ≥ 2.");
    var mach = el("div", "mach");
    var bh = b.baiHoc, thh = b.tienHoa;
    [["Dự đoán", so(kn.soQuyetDinh) + " quyết định đã ghi", "mỗi lượt cân, một dòng mỗi pool có dải"],
     ["Thực tế", so(kn.soKetCuc) + " đã chấm" + (kn.soChuaCham ? " · " + so(kn.soChuaCham) + " chờ hết cửa sổ" : ""),
      "chấm ở mốc sau đóng cửa Mỹ, hoặc bấm Học ngay"],
     ["Bài học", bh ? so((bh.duMau || []).length) + " đủ mẫu · " + so(bh.soChuaDuMau) + " đang tích" : "chưa có",
      bh && bh.moHinh ? Object.keys(bh.moHinh).map(function (kk) { return bh.moHinh[kk]; }).join(" · ") : "cần cửa sổ giữ đầu tiên trôi qua"],
     ["Tiến hoá", thh ? thh.gan[thh.gan.length - 1] : "chưa lượt nào",
      "một núm mỗi lượt · A/B ghép cửa sổ · qua cổng thì CHỜ NGƯỜI ký (tuVanTienHoa tắt)"]
    ].forEach(function (x, i) {
      var c = el("div", "chang" + (i < 2 ? " xong" : ""));
      c.appendChild(el("span", "cham", String(i + 1)));
      var t = el("div");
      t.appendChild(el("div", "ten", x[0] + " — " + x[1]));
      t.appendChild(el("div", "phu", x[2]));
      c.appendChild(t);
      mach.appendChild(c);
    });
    k4.appendChild(mach);
    if (bh && (bh.duMau || []).length) {
      var dsBh = el("div", "viec-1");
      dsBh.appendChild(el("b", null, "Bài học đủ mẫu"));
      bh.duMau.forEach(function (c) { dsBh.appendChild(el("span", null, "★ " + c)); });
      k4.appendChild(dsBh);
    }
    var nutHoc = el("button", "nho", "Học ngay (chấm + bài học + một lượt tiến hoá)");
    nutHoc.type = "button";
    nutHoc.addEventListener("click", function () {
      fetch("/api/be-thanh-khoan/hoc", { method: "POST" })
        .then(function (r) { return r.json(); })
        .then(function (j) { nhac("học xong: chấm " + j.soCham + ", " + (j.tienHoa || "")); BTK = null; ve(); })
        .catch(function (e) { nhac("học hỏng: " + (e && e.message || e)); });
    });
    k4.appendChild(nutHoc);
    k4.appendChild(giai("Núm hiện tại: " + Object.keys(b.nut || {}).map(function (kk) { return kk + " = " + b.nut[kk]; }).join(" · ")));
    f.appendChild(k4);

    /* ── NHỊP NGÀY ──────────────────────────────────────────────────── */
    var k5 = khoi("Một ngày của ty — nhịp nào làm gì", "Mốc chạy ở lượt quét kế tiếp sau giờ của nó; máy tắt thì chạy bù và báo cáo ghi là chạy bù.");
    var vn = b.vongNgay || {};
    k5.appendChild(bang([{ t: "Nhịp" }, { t: "Việc" }],
      (b.nhip || []).map(function (x) { return [{ t: x.nhip }, { t: x.viec }]; })));
    if ((vn.mocKe || []).length) {
      k5.appendChild(giai("Mốc kế tiếp: " + vn.mocKe.map(function (m) {
        return m.moc + " lúc " + gioTuIso(m.luc) + " (còn " + Number(m.conGio).toFixed(1) + "h)"; }).join(" · ")
        + ". Đã chạy: " + Object.keys(vn.daChay || {}).map(function (kk) { return kk + " " + vn.daChay[kk]; }).join(", ")
        + ". Báo cáo ở data/lp-v3/bao-cao/."));
    }
    f.appendChild(k5);
    return f;
  }
  document.addEventListener("click", function (ev) {
    var b = ev.target.closest("button[data-btk-dong]");
    if (!b) return;
    var gia = Number(prompt("Giá lúc rút?")), phi = prompt("Phí đã thu (USD, để trống nếu chưa biết)?");
    var thuong = prompt("Thưởng đã thu (USD, để trống nếu chưa biết)?");
    if (!isFinite(gia) || gia <= 0) { nhac("cần giá lúc rút"); return; }
    fetch("/api/be-thanh-khoan/vi-the/" + b.dataset.btkDong + "/dong", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ giaDong: gia, phiThuUsd: phi === "" || phi == null ? null : Number(phi),
                             thuongThuUsd: thuong === "" || thuong == null ? null : Number(thuong) }) })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.detail || r.status); }); })
      .then(function () { nhac("đã ghi kết cục"); BTK = null; ve(); })
      .catch(function (e) { nhac("ghi hỏng: " + (e && e.message || e)); });
  });

  var TRANG = {
    "trung-tam": ve_trung_tam, "dong-co": ve_dong_co, "von": ve_von,
    "vi-the": ve_vi_the, "co-hoi": ve_co_hoi,
    "loi-lo": ve_loi_lo, "rui-ro": ve_rui_ro, "du-lieu": ve_du_lieu,
    "so-cai": ve_so_cai, "he-thong": ve_he_thong,
    "be-thanh-khoan": ve_be_thanh_khoan
  };
  function duong() {
    var p = location.pathname.replace(/^\/+|\/+$/g, "");
    if (!p) return { o: "trung-tam" };
    var m = p.split("/");
    if (m[0] === "dong-co" && m[1]) return { o: "dong-co", ma: m[1] };
    return { o: TRANG[m[0]] ? m[0] : "trung-tam" };
  }

  function ve() {
    try { veDinh(); } catch (e) { /* đỉnh không được kéo theo thân */ }
    if (!S) return;
    var d = duong(), moi;
    try {
      moi = d.ma ? ve_mot_dong_co(d.ma) : (TRANG[d.o] || ve_trung_tam)();
    } catch (e) {
      moi = document.createDocumentFragment();
      var x = el("div", "loi-o");
      x.appendChild(el("h2", null, "Trang «" + d.o + "» vẽ hỏng"));
      x.appendChild(el("p", null, String(e && e.message || e)));
      x.appendChild(el("pre", null,
        String(e && e.stack || "").split("\n").slice(0, 6).join("\n")));
      x.appendChild(el("p", "giai", "Máy VẪN ĐANG CHẠY — đây là lỗi của trang, "
        + "không phải của runtime. Dựng lại ở dòng lệnh: curl -s localhost:"
        + (location.port || "5188") + "/api/trang-thai"));
      moi.appendChild(x);
    }
    $("#than").replaceChildren(moi);
    Array.prototype.forEach.call(document.querySelectorAll("#dieu-huong a"),
      function (a) { a.classList.toggle("chon", a.dataset.o === d.o); });
  }

  function veDinh() {
    var den = $("#den-chay"), b = den.querySelector("b");
    if (!S) { den.className = "den hong"; b.textContent = "MẤT KẾT NỐI"; return; }
    var hong = !!S.loiVongCuoi;
    den.className = "den " + (S.tamDung ? "dung" : hong ? "hong" : "chay");
    b.textContent = S.tamDung ? "TẠM DỪNG" : hong ? "CÓ LỖI" : "ĐANG CHẠY";
    $("#d-vong").textContent = S.vong != null ? S.vong : "—";
    $("#d-quet").textContent = S.quetCuoiMs != null
      ? Math.round(S.quetCuoiMs) + "ms" : "—";
    $("#d-len").textContent = gio(S.chayDuocGiay);

    var bc = $("#bang-canh"), viec = dsViec();
    var nang = viec.filter(function (v) { return v.nang; });
    if (!viec.length) { bc.hidden = true; return; }
    bc.hidden = false;
    bc.className = "bang-canh" + (nang.length ? "" : " nhe");
    var v = nang[0] || viec[0];
    bc.textContent = (nang.length ? "⚠ " : "· ") + v.ten
      + (viec.length > 1 ? "  (+" + (viec.length - 1) + " việc khác)" : "")
      + (v.mo ? " — " + v.mo : "");
  }

  /* ── tải ──────────────────────────────────────────────────────── */
  function tai() {
    if (DANG_TAI) return Promise.resolve();
    DANG_TAI = true;
    return fetch("/api/trang-thai", { cache: "no-store" })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (j) {
        S = j;
        /* Nhật ký hỏng KHÔNG được kéo theo cả trang — nhưng cũng không
           được nuốt. Nuốt lỗi là cách nhanh nhất biến một trang hỏng thành
           một trang trắng không ai giải thích được, nên chỗ đáng lẽ là
           nhật ký sẽ nói ra chính lỗi ấy. */
        return fetch("/api/nhat-ky?n=40")
          .then(function (r) {
            if (!r.ok) throw new Error("HTTP " + r.status);
            return r.json();
          })
          .then(function (n) { NHAT_KY = n; LOI_NHAT_KY = ""; })
          .catch(function (e) {
            NHAT_KY = null;
            LOI_NHAT_KY = String(e && e.message || e);
          });
      })
      .then(ve)
      .catch(function (e) {
        S = null;
        try { veDinh(); } catch (x) { }
        var bc = $("#bang-canh");
        bc.hidden = false; bc.className = "bang-canh";
        bc.textContent = "KHÔNG ĐỌC ĐƯỢC RUNTIME: " + (e && e.message || e)
          + " — runtime còn chạy không? (python run.py)";
      })
      .finally(function () { DANG_TAI = false; });
  }
  function nhac(t) { $("#chan-nhac").textContent = t || ""; }

  /* ── điều hướng không tải lại trang ───────────────────────────── */
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest("a[data-lien]");
    if (a && a.origin === location.origin) {
      ev.preventDefault();
      if (a.pathname !== location.pathname) {
        history.pushState({}, "", a.pathname);
        ve();
        window.scrollTo(0, 0);
      }
      return;
    }
    var b = ev.target.closest("button[data-perp]");
    if (b) { O_PERP = b.dataset.perp; ve(); }
  });
  window.addEventListener("popstate", ve);

  $("#nut-quet").addEventListener("click", function () {
    nhac("đang quét…");
    fetch("/api/quet-ngay", { method: "POST" })
      .then(function (r) { return r.json(); })
      .then(function (j) { nhac(j.xong ? "quét xong" : "quét lỗi: " + j.loi); })
      .catch(function (e) { nhac("quét lỗi: " + e.message); })
      .then(tai);
  });
  $("#nut-dung").addEventListener("click", function () {
    fetch("/api/tam-dung", { method: "POST" })
      .then(function (r) { return r.json(); })
      .then(function (j) { nhac(j.tamDung ? "ĐÃ TẠM DỪNG" : "chạy tiếp"); })
      .then(tai);
  });
  $("#nut-doi-soat").addEventListener("click", function () {
    nhac("đang đối soát vị thế…");
    fetch("/api/doi-soat-vi-the", { method: "POST" })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        nhac(j.lech
          ? (j.canNguoi ? "VẪN LỆCH — cần người: " + j.soMoCoi + " tờ"
                        : "đóng " + (j.daDong || []).length + " tờ, còn lệch")
          : "khớp — không tờ nào mồ côi"
          + ((j.daDong || []).length ? " (vừa đóng "
             + j.daDong.length + " tờ)" : ""));
      })
      .catch(function (e) { nhac("đối soát lỗi: " + e.message); })
      .then(tai);
  });

  $("#nut-lat").addEventListener("click", function () {
    nhac("đang ghi lát cắt…");
    fetch("/api/lat-cat", { method: "POST" })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        nhac(j.daGhi ? "đã ghi " + j.duong
                     : "KHÔNG tìm thấy cung tĩnh thi-bac-ty/ — không ghi gì");
      })
      .catch(function (e) { nhac("ghi lỗi: " + e.message); });
  });

  tai();
  setInterval(tai, 5000);
})();
