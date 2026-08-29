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
    d.appendChild(oSo("Sổ giấy · lãi lỗ",
      hn.duDeKetLuan ? phan(hn.laiLoPhanTram) : "chưa kết luận",
      hn.duDeKetLuan ? "" : "cần ≥ 168 giờ dữ liệu", hn.duDeKetLuan
        ? ((hn.laiLoPhanTram || 0) >= 0 ? "duong" : "am") : "nhat",
      !hn.duDeKetLuan));
    d.appendChild(oSo("Đã thực hiện", tien(t.danhMuc && t.danhMuc.laiLoDaThucHienUsd),
      "ghi vào sổ cái khi đóng vị thế"));
    d.appendChild(oSo("Sụt vốn tối đa", phan(hn.sutVonToiDaPhanTram),
      hn.dangDuoiDay ? "đang dưới đỉnh" : "chưa từng xuống dưới đỉnh"));
    k.appendChild(d);
    if (hn.vi) k.appendChild(giai(hn.vi));
    f.appendChild(k);

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

    var tk = t.laiLoTachKhoan || {};
    var mtk = Object.keys(tk);
    if (mtk.length) {
      var kt4 = khoi("Lãi lỗ TÁCH KHOẢN — vì con số gộp nói dối",
        "Phí vào lệnh phần lớn KHÔNG do chiến lược sinh ra: vị thế mô phỏng "
        + "không sống qua một lần khởi động lại, nên mỗi lần restart là một "
        + "lần vào lệnh mới và trả phí lần nữa. Đó là chi phí VẬN HÀNH. Gộp "
        + "nó vào là bắt người đọc kết luận sai về chiến lược vì một chuyện "
        + "của người vận hành.");
      kt4.appendChild(bang(
        [{ t: "Ty" }, { t: "Thu", n: true }, { t: "Phí vào lệnh", n: true },
         { t: "Số lần vào", n: true }, { t: "Phí mỗi lần", n: true },
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
        + "đổi bao nhiêu». Cả hai đều đúng, và chúng khác nhau."));
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
    d3.appendChild(oSo("KHÔNG canh được", so(hp.soKhongCanhDuoc),
      "khai ra, không giấu", "nhat"));
    d3.appendChild(oSo("Vi phạm", so(hp.soViPham),
      hp.soViPham === null || hp.soViPham === undefined
        ? "CHƯA soát" : (hp.soViPham ? "PHẢI XEM" : "sạch"),
      hp.soViPham === null || hp.soViPham === undefined
        ? "nhat" : (hp.soViPham ? "am" : "duong")));
    /* Soát hiến pháp có nhịp riêng: 31 điều, phần lớn phân tích cả cây mã,
       và một điều dựng hẳn một Trung Ương rồi quay hai vòng thật. Buồng lái
       hỏi mỗi vài giây, nên bản này có thể CŨ — và một con số cũ mà không
       nói mình cũ thì trông y hệt một con số mới. */
    d3.appendChild(oSo("Soát cách đây",
      hp.tuoiGiay === null || hp.tuoiGiay === undefined
        ? "—" : Math.round(hp.tuoiGiay) + "s",
      "hiến pháp là hàm của mã nguồn, nên soát theo nhịp chứ không mỗi lần hỏi",
      "nhat"));
    k3.appendChild(d3);
    if ((hp.khongCanhDuoc || []).length) {
      k3.appendChild(giai("Không canh được: " + hp.khongCanhDuoc.join(", ")
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
    f.appendChild(k3);
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
  var TRANG = {
    "trung-tam": ve_trung_tam, "dong-co": ve_dong_co, "von": ve_von,
    "vi-the": ve_vi_the, "co-hoi": ve_co_hoi,
    "loi-lo": ve_loi_lo, "rui-ro": ve_rui_ro, "du-lieu": ve_du_lieu,
    "so-cai": ve_so_cai, "he-thong": ve_he_thong
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
