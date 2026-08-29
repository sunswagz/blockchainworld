/* TRANG CHI TIẾT của ĐỘNG CƠ chênh lệch funding perp.
 *
 * Bảy khối vẽ ở đây từng chiếm TRANG GỐC của buồng lái, và đó là lỗi kiến
 * trúc thông tin chứ không phải lỗi của chúng: `localhost:5188/` không
 * thuộc về bất kỳ ty nào, nó thuộc về TRUNG ƯƠNG. Một động cơ trong mười
 * ba không được chiếm cửa vào của cả bộ máy.
 *
 * Nên chúng chuyển xuống `/dong-co/perpetual-funding`, nơi chúng đúng chỗ:
 * người đã bấm vào một động cơ cụ thể thì mới cần bps, mốc L+S, và lệch
 * mark. Ai chỉ muốn biết "máy có ổn không" thì không bao giờ phải nhìn.
 *
 * Đây là tầng BA của giao diện — tầng mổ máy. Tầng một trả lời "có ổn
 * không", tầng hai trả lời "vì sao", tầng này mới là số thô.
 */
window.TYPERP = (function () {
  "use strict";

  var S = null;
  function dat(x) { S = x; }
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
  var so_ = so;   // bí danh: `so` hay bị che tên bởi biến cục bộ

  function lop(v) { return v == null ? "nhat" : (v >= 0 ? "duong" : "am"); }
  function gio(g) {
    if (g == null) return "—";
    if (g < 60) return Math.round(g) + "s";
    if (g < 3600) return (g / 60).toFixed(1) + "p";
    return (g / 3600).toFixed(1) + "h";
  }

  /* ── đỉnh trang: cập nhật RIÊNG, không đi cùng phần vẽ ─────────────── */
  function ve_dinh() {
    if (!S) return;
    var c = $("#che");
    c.textContent = "chế độ " + (S.che || "—");
    c.className = "the" + (S.che === "quan-sat" ? "" : " canh");
    $("#vong").textContent = "vòng " + (S.vong == null ? "—" : S.vong);
    $("#dongho").textContent =
      "quét " + so(S.quetCuoiMs, 0) + " ms · chạy " + gio(S.chayDuocGiay);
  }

  function ve_canh() {
    var d = $("#dai-canh"), ds = [];
    if (S) {
      var chet = (S.cang || []).filter(function (c) { return !c.songSot; });
      if (chet.length)
        ds.push("MÙ MỘT MẮT: " + chet.map(function (c) { return c.ten; }).join(", ")
                + " chưa lấy được dữ liệu lần nào — bảng dưới đang thiếu cảng.");
      var oi = (S.cang || []).filter(function (c) {
        return c.songSot && c.tuoiGiay != null && c.tuoiGiay > 300;
      });
      if (oi.length)
        ds.push("dữ liệu cũ: " + oi.map(function (c) {
          return c.ten + " " + gio(c.tuoiGiay); }).join(", "));
      if (S.loiVongCuoi) ds.push("vòng gần nhất lỗi: " + S.loiVongCuoi);
      if (S.so && S.so.loiCuoi) ds.push("sổ ghi lỗi: " + S.so.loiCuoi);
    }
    if (!ds.length) { d.hidden = true; return; }
    d.hidden = false;
    d.className = "dai-canh" + (S && (S.cang || []).some(function (c) {
      return !c.songSot; }) ? "" : " nhe");
    d.textContent = ds.join("  ·  ");
  }

  /* ── các ô ─────────────────────────────────────────────────────────── */
  function bang(cot, hang) {
    var w = el("div", "cuon"), t = el("table"), th = el("thead"), tr = el("tr");
    cot.forEach(function (c) {
      var e = el("th", c.trai ? "trai" : null, c.t);
      tr.appendChild(e);
    });
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

  function o(tieu_de, noi_dung, giai) {
    var d = el("div", "o");
    d.appendChild(el("h2", null, tieu_de));
    d.appendChild(noi_dung);
    if (giai) d.appendChild(el("p", "giai", giai));
    return d;
  }

  function ve_co_hoi() {
    var f = document.createDocumentFragment();
    var ds = S.coHoi || [], qua = ds.filter(function (c) { return c.duyet; });

    var l = el("div", "luoi");
    [["cặp đã cân", ds.length],
     ["qua cửa rủi ro", qua.length],
     ["cảng sống", (S.cang || []).filter(function (c) { return c.songSot; }).length
        + "/" + (S.cang || []).length],
     ["cửa sổ giữ", so(S.giuGio, 0) + " h"],
     ["báo giá", (S.baoGia || []).length]
    ].forEach(function (x) {
      var d = el("div", "so");
      d.appendChild(el("div", "n", String(x[1])));
      d.appendChild(el("div", "t", x[0]));
      l.appendChild(d);
    });
    f.appendChild(o("Tổng quan", l));

    if (!ds.length) {
      f.appendChild(o("Cơ hội", el("p", "cho",
        "chưa cân được cặp nào — xem tab Cảng xem có cảng nào chết không"),
        "Cần ít nhất hai cảng cùng trả về một mã thì mới ghép được một cặp."));
      return f;
    }

    f.appendChild(o("Cơ hội — xếp theo NET, không theo funding thô", bang(
      [{ t: "Mã", trai: 1 }, { t: "LONG", trai: 1 }, { t: "SHORT", trai: 1 },
       { t: "gross bps/ngày" }, { t: "mốc L+S" }, { t: "thu bps" },
       { t: "phí bps" }, { t: "NET bps" }, { t: "APR*" }, { t: "lệch mark" },
       { t: "cửa", trai: 1 }, { t: "vì sao", trai: 1 }],
      ds.map(function (c) {
        return [
          { t: c.ma, c: "trai" },
          { t: c.sanLong, c: "trai" },
          { t: c.sanShort, c: "trai" },
          { t: dau(c.grossBpsNgay) },
          { t: c.soMocLong + "+" + c.soMocShort,
            c: (c.soMocLong + c.soMocShort) ? null : "am",
            title: c.choMocDauGiay != null
              ? "mốc đầu tiên sau " + gio(c.choMocDauGiay) : "" },
          { t: dau(c.thuBps), c: lop(c.thuBps) },
          { t: so(c.phiBps), c: "nhat" },
          { t: dau(c.netBps), c: lop(c.netBps) },
          { t: c.netAprPct == null ? "—" : dau(c.netAprPct, 1) + "%",
            c: "nhat" },
          { t: c.lechMarkBps == null ? "—" : so(c.lechMarkBps, 1),
            c: c.lechMarkBps == null ? "am" : "nhat" },
          { t: c.duyet ? "QUA" : "chặn", c: c.duyet ? "qua" : "chan" },
          { t: (c.lyDo || []).join(" · ") || "—", c: "vi" }
        ];
      })),
      "* APR là NGOẠI SUY của một vòng giữ ra cả năm, giả định chênh lệch y "
      + "nguyên và vào lại được ngay. Cửa sổ giữ càng ngắn thì hệ số nhân càng "
      + "lớn, nên đừng xếp hạng bằng nó — cột NET mới là thứ đáng tin. "
      + "Cột 'mốc L+S' bằng 0+0 nghĩa là giữ hết cửa sổ mà KHÔNG mốc kết toán "
      + "nào rơi vào: thu thực bằng 0, dù gross trông vẫn to."));

    var vs = S.viSaoTuChoi || {}, k = Object.keys(vs);
    if (k.length) {
      k.sort(function (a, b) { return vs[b] - vs[a]; });
      f.appendChild(o("Vì sao bị chặn — đếm theo CỬA, trên mọi cặp", bang(
        [{ t: "Cửa", trai: 1 }, { t: "số cặp" }],
        k.map(function (x) {
          return [{ t: x, c: "trai" }, { t: String(vs[x]) }];
        })),
        "Bảng trống ở trên mà không có bảng này thì người vận hành sẽ đi nới "
        + "bừa từng ngưỡng một. Đây là chỗ nói thẳng CỬA nào đang chặn — gộp "
        + "theo mã lý do, không theo câu, vì câu có mang con số."));
    }

    var dd = (S.doDai || []).filter(function (x) { return x.soMau > 0; });
    if (dd.length) {
      f.appendChild(o("Độ dai — cú loé hay mỏ thật", bang(
        [{ t: "Mã", trai: 1 }, { t: "cặp", trai: 1 }, { t: "mẫu 24h" },
         { t: "tỉ lệ NET dương" }, { t: "NET trung bình" }, { t: "đủ mẫu?", trai: 1 }],
        dd.map(function (x) {
          return [
            { t: x.ma, c: "trai" },
            { t: x.sanLong + "→" + x.sanShort, c: "trai" },
            { t: String(x.soMau) },
            { t: x.tiLeDuong == null ? "—" : so(x.tiLeDuong * 100, 0) + "%" },
            { t: dau(x.netTrungBinh), c: lop(x.netTrungBinh) },
            { t: x.duMau ? "đủ" : "chưa", c: x.duMau ? "qua" : "nhat" }
          ];
        })),
        "NET đang 12 bps mà chỉ 20% lượt quét thấy dương là một cú loé. NET 8 "
        + "bps mà 90% lượt thấy dương thì đáng giá hơn, dù con số nhỏ hơn."));
    }
    return f;
  }

  function ve_bao_gia() {
    var ds = (S.baoGia || []).slice().sort(function (a, b) {
      return a.ma === b.ma ? b.moiNgayBps - a.moiNgayBps : (a.ma < b.ma ? -1 : 1);
    });
    if (!ds.length)
      return o("Báo giá", el("p", "cho", "chưa cảng nào trả về báo giá nào"));
    return o("Báo giá thô — và chuẩn hoá về cùng đơn vị", bang(
      [{ t: "Mã", trai: 1 }, { t: "Cảng", trai: 1 }, { t: "rate/chu kỳ" },
       { t: "chu kỳ" }, { t: "bps/ngày" }, { t: "mark" }, { t: "mốc kế" },
       { t: "tuổi" }, { t: "ghi chú", trai: 1 }],
      ds.map(function (q) {
        var con = q.mocKeMs == null ? null : (q.mocKeMs - Date.now()) / 1000;
        return [
          { t: q.ma, c: "trai" },
          { t: q.san, c: "trai" },
          { t: (q.rate * 100).toFixed(5) + "%" },
          { t: so(q.intervalGio, 0) + "h" + (q.intervalSuyRa ? " ?" : ""),
            c: q.intervalSuyRa ? "am" : null,
            title: q.intervalSuyRa ? "chu kỳ phải ĐOÁN — sàn không công bố" : "" },
          { t: dau(q.moiNgayBps), c: lop(q.moiNgayBps) },
          { t: q.markPx == null ? "—" : so(q.markPx, 2),
            c: q.markPx == null ? "am" : null },
          { t: con == null ? "—" : gio(con) },
          { t: gio(q.tuoiGiay), c: (q.tuoiGiay || 0) > 90 ? "am" : "nhat" },
          { t: q.ghiChu || "", c: "vi" }
        ];
      })),
      "Cột `rate/chu kỳ` là con số sàn công bố; `bps/ngày` là sau khi chia cho "
      + "chu kỳ thật. So hai cảng bằng cột đầu là sai — 0,08%/8h nhỏ hơn "
      + "0,015%/1h, dù nhìn số thô thì ngược lại.");
  }

  function ve_cang() {
    var f = document.createDocumentFragment();
    var dh = S.dongHo || {};
    f.appendChild(o("Đồng hồ — thứ mọi phép đếm mốc dựa vào", bang(
      [{ t: "Mục", trai: 1 }, { t: "giá trị" }],
      [["đã đo được chưa", dh.daDo ? "rồi" : "CHƯA"],
       ["máy chậm hơn sàn", dh.lechGiay == null ? "—" : so(dh.lechGiay, 1) + " s"],
       ["số sàn góp mẫu", dh.soMau],
       ["ngưỡng kêu", (dh.nguongKeuMs || 0) / 1000 + " s"]
      ].map(function (x) {
        return [{ t: x[0], c: "trai" },
                { t: x[1] == null ? "—" : String(x[1]) }];
      })),
      "`mocKeMs` là giờ SÀN, còn `time.time()` là giờ MÁY. So hai đồng hồ "
      + "khác nhau thì gần biên kết toán là lật hẳn kết quả: đo thật "
      + "21/08/2026 máy chậm 6,94 phút, đủ để \"thu trọn một chu kỳ\" hoá "
      + "ra \"không mốc nào\"."));
    f.appendChild(o("Cảng", bang(
      [{ t: "Cảng", trai: 1 }, { t: "sống?", trai: 1 }, { t: "lượt hỏi" },
       { t: "lỗi" }, { t: "trễ TB" }, { t: "tuổi" }, { t: "phí taker" },
       { t: "trượt giá" }, { t: "lỗi cuối", trai: 1 }],
      (S.cang || []).map(function (c) {
        var p = (S.phiSan || {})[c.ten] || {};
        return [
          { t: c.ten, c: "trai" },
          { t: c.songSot ? "sống" : "CHƯA BAO GIỜ",
            c: c.songSot ? "qua" : "am" },
          { t: String(c.tongLuot) },
          { t: String(c.soLoi), c: c.soLoi ? "am" : "nhat" },
          { t: so(c.treTrungBinhMs, 0) + " ms" },
          { t: gio(c.tuoiGiay) },
          { t: so(p.phiTakerBps, 1) + " bps" },
          { t: so(p.truotGiaBps, 1) + " bps" },
          { t: c.loiCuoi || "", c: "vi" }
        ];
      })),
      "Phí và trượt giá ở đây là THAM SỐ trong config.json, không phải số đo "
      + "được từ sàn. Đặt quá thấp là tự vẽ ra lợi nhuận không có thật."));

    /* GIỮ TỐI THIỂU. `vong.py` tính bảng này mỗi vòng kèm một docstring nói
       thẳng vì sao nó tồn tại — «người vận hành không nên phải tự suy ra
       điều đó từ một bảng mốc kế tiếp» — rồi không ai vẽ nó. Funding trả
       theo MỐC: giữ bốn giờ trên sàn kết toán tám giờ có thể thu ĐÚNG BẰNG
       KHÔNG, và đó là chỗ dễ mất tiền nhất mà nhìn bảng bps không thấy. */
    f.appendChild(o("Giữ tối thiểu — TÁM cặp phải giữ lâu nhất", bang(
      [{ t: "Cảng", trai: 1 }, { t: "Mã", trai: 1 }, { t: "phải giữ" },
       { t: "chu kỳ" }],
      (S.giuToiThieuGio || []).map(function (x) {
        return [{ t: x.san, c: "trai" }, { t: x.ma, c: "trai" },
                { t: so(x.gio, 2) + " h",
                  c: (x.gio || 0) > (x.chuKyGio || 0) * 0.5 ? "am" : null },
                { t: so(x.chuKyGio, 0) + " h", c: "nhat" }];
      })),
      "Funding chỉ chảy TẠI MỐC, không chảy liên tục. Vào lệnh ngay sau một "
      + "mốc là phải giữ gần trọn một chu kỳ mới thu được đồng nào — và "
      + "phí vào lệnh thì trả ngay. Đây là TÁM cặp tệ nhất, không phải cả "
      + "bảng: cặp không có mặt ở đây thì chờ ít hơn cặp cuối cùng trong "
      + "bảng, chứ không phải không phải chờ."));
    return f;
  }

  function ve_cua() {
    var r = S.ruiRo || {};
    var ten = {
      grossToiThieuBpsNgay: "chênh lệch thô tối thiểu (bps/ngày)",
      netToiThieuBps: "NET tối thiểu sau phí (bps)",
      lechMarkToiDaBps: "lệch mark tối đa (bps)",
      doiHoiHaiMark: "bắt buộc có mark cả hai bên",
      tuoiToiDaGiay: "tuổi dữ liệu tối đa (giây)",
      nhanUocLuongMoc: "chấp nhận mốc phải đoán",
      doiHoiItNhatMotMoc: "bắt buộc có ít nhất một mốc kết toán",
      lechDongHoToiDaGiay: "lệch đồng hồ tối đa (giây)"
    };
    var f = document.createDocumentFragment();
    f.appendChild(o("Cửa rủi ro đang có hiệu lực", bang(
      [{ t: "Cửa", trai: 1 }, { t: "giá trị" }],
      Object.keys(r).map(function (k) {
        return [{ t: ten[k] || k, c: "trai" },
                { t: typeof r[k] === "boolean" ? (r[k] ? "có" : "không")
                                               : String(r[k]) }];
      })),
      "Cổng rủi ro là Python thuần, tất định, và có quyền phủ quyết. Không "
      + "dòng nào trong nó gọi mạng hay gọi model. Bảng này lọc theo danh "
      + "sách `CUA` trong rui_ro.py, nên một khoá khai mà không nối vào cổng "
      + "KHÔNG hiện lên đây được."));

    var v = S.von || {};
    f.appendChild(o("Trần vốn — CHƯA CÓ HIỆU LỰC", bang(
      [{ t: "Mục", trai: 1 }, { t: "giá trị" }],
      [["đang có hiệu lực", v.coHieuLuc ? "CÓ" : "KHÔNG"],
       ["vốn mỗi cơ hội", v.moiCoHoiUsd == null ? "—" : "$" + so(v.moiCoHoiUsd, 0)],
       ["vốn tối đa", v.toiDaUsd == null ? "—" : "$" + so(v.toiDaUsd, 0)],
       ["đòn bẩy tối đa", v.donBayToiDa == null ? "—" : so(v.donBayToiDa, 1)]
      ].map(function (x) {
        return [{ t: x[0], c: "trai" },
                { t: String(x[1]), c: x[0] === "đang có hiệu lực"
                    ? (v.coHieuLuc ? "qua" : "am") : null }];
      })),
      "Ba con số này KHÔNG chặn gì ở bản hiện tại — không có lớp đặt lệnh thì "
      + "không có vị thế nào để mà giới hạn, kể cả trên sổ giấy. Chúng từng "
      + "nằm trong khối `ruiRo` và hiện ngay trong bảng trên như ba cái cửa "
      + "thật; nay tách ra và khai thẳng. Sẽ có hiệu lực ở V0.6."));

    var s = S.so || {};
    f.appendChild(o("Sổ quét", bang(
      [{ t: "Mục", trai: 1 }, { t: "giá trị" }],
      [["lượt quét đã ghi", s.soLuot], ["cơ hội đã ghi", s.soCoHoi],
       ["trong đó qua cửa", s.soDuyet], ["lỗi ghi", s.soLoiGhi],
       ["file", s.duong]].map(function (x) {
        return [{ t: x[0], c: "trai" }, { t: x[1] == null ? "—" : String(x[1]) }];
      })),
      "Lượt quét KHÔNG có cơ hội nào cũng được ghi. Một tuần trắng là một "
      + "phát hiện, không phải một tuần thiếu dữ liệu."));
    return f;
  }

  function ve_nhat_ky() {
    var p = el("div", "nk");
    (S.nhatKy || []).slice().reverse().forEach(function (d) {
      var r = el("div", "l-" + (d.loai || "tin"));
      var t = el("time", null, (d.luc || "").slice(11, 19));
      r.appendChild(t);
      r.appendChild(document.createTextNode(d.muc || ""));
      p.appendChild(r);
    });
    if (!(S.nhatKy || []).length) p.appendChild(el("div", null, "(chưa có dòng nào)"));
    return o("Nhật ký", p);
  }

  /* ── ô ĐÀO TẠO ─────────────────────────────────────────────────────
   * Ba tầng xếp theo đúng thứ tự phụ thuộc, và ô này nói thẳng tầng nào
   * chưa sẵn sàng. Không có băng thì chạy lại vô nghĩa; không chạy lại
   * được thì tiến hoá chỉ là đổi số cho vui.
   */
  var HOC = { chayLai: null, tienHoa: null, doiChieu: null, dangChay: "" };

  function ve_hoc() {
    var f = document.createDocumentFragment();
    var b = S.bang || {};
    var so = S.so || {};

    var l = el("div", "luoi");
    [["khung băng phiên này", b.soKhung == null ? "—" : b.soKhung],
     ["băng đang ghi", b.bat ? "có" : "TẮT"],
     ["lượt quét đã ghi sổ", so.soLuot == null ? "—" : so.soLuot],
     ["cửa sổ giữ", so_(S.giuGio, 0) + " h"],
     ["nhịp quét", so_(S.nhipGiay, 0) + " s"]
    ].forEach(function (x) {
      var d = el("div", "so");
      d.appendChild(el("div", "n", String(x[1])));
      d.appendChild(el("div", "t", x[0]));
      l.appendChild(d);
    });
    f.appendChild(o("Nguyên liệu", l,
      "Băng ghi BÁO GIÁ THÔ mỗi lượt quét. Chạy lại cần băng phủ hết CỬA SỔ "
      + "GIỮ mới hậu kiểm được một cơ hội: với cửa sổ " + so_(S.giuGio, 0)
      + " giờ, phải chạy ít nhất ngần ấy giờ mới có mẫu đầu tiên."));

    // ── tầng 2: chạy lại ────────────────────────────────────────────
    var n2 = el("div");
    var nut2 = el("button", "nut", "Chạy lại băng ngay");
    nut2.disabled = HOC.dangChay === "chay-lai";
    nut2.addEventListener("click", function () {
      HOC.dangChay = "chay-lai"; ve();
      fetch("/api/chay-lai", { method: "POST" })
        .then(function (r) { return r.json(); })
        .then(function (j) { HOC.chayLai = j; })
        .catch(function (e) { HOC.chayLai = { loi: String(e && e.message || e) }; })
        .then(function () { HOC.dangChay = ""; ve(); });
    });
    n2.appendChild(nut2);
    if (HOC.dangChay === "chay-lai") n2.appendChild(el("span", "nhac", " đang chạy…"));

    if (HOC.chayLai) {
      var k = HOC.chayLai;
      if (k.loi) {
        n2.appendChild(el("p", "trong", "lỗi: " + k.loi));
      } else {
        n2.appendChild(bang(
          [{ t: "Mục", trai: 1 }, { t: "giá trị" }],
          [["khung băng đi qua", k.soKhung],
           ["cặp đã cân", k.soCoHoi],
           ["qua cửa", k.soQuaCua],
           ["HẬU KIỂM ĐƯỢC", k.soDoDuoc],
           ["kỳ vọng NET thực", k.kyVongBps == null ? "chưa đo được"
              : dau(k.kyVongBps) + " bps"],
           ["dự đoán lệch thực nhận", k.saiSoDuDoanBps == null ? "—"
              : dau(k.saiSoDuDoanBps) + " bps"],
           ["lãi / lỗ", k.soLai + " / " + k.soLo],
           ["lần tệ nhất", k.netThucTeNhatBps == null ? "—"
              : dau(k.netThucTeNhatBps) + " bps"],
           ["đủ mẫu (≥30)", k.duMau ? "rồi" : "CHƯA"]
          ].map(function (x) {
            return [{ t: x[0], c: "trai" },
                    { t: x[1] == null ? "—" : String(x[1]) }];
          })));
      }
    }
    f.appendChild(o("Chạy lại — funding THỰC NHẬN, không phải dự đoán", n2,
      "`kỳ vọng NET thực` tính từ funding sàn công bố TẠI TỪNG MỐC kết toán, "
      + "tra ngược từ băng. `dự đoán lệch thực nhận` dương nghĩa là mô hình "
      + "lạc quan có hệ thống — funding tụt trước khi tới mốc. Đó là con số "
      + "chỉ có băng mới đo được."));

    // ── tầng 3: tiến hoá ────────────────────────────────────────────
    var n3 = el("div");
    var nut3 = el("button", "nut", "Thử một lượt tiến hoá (không ghi)");
    nut3.disabled = HOC.dangChay === "tien-hoa";
    nut3.addEventListener("click", function () {
      HOC.dangChay = "tien-hoa"; ve();
      fetch("/api/tien-hoa?thu=true", { method: "POST" })
        .then(function (r) { return r.json(); })
        .then(function (j) { HOC.tienHoa = j; })
        .catch(function (e) { HOC.tienHoa = { loi: String(e && e.message || e) }; })
        .then(function () { HOC.dangChay = ""; ve(); });
    });
    n3.appendChild(nut3);
    if (HOC.dangChay === "tien-hoa") n3.appendChild(el("span", "nhac", " đang chạy…"));

    if (HOC.tienHoa) {
      var t = HOC.tienHoa;
      if (t.loi) {
        n3.appendChild(el("p", "trong", "lỗi: " + t.loi));
      } else {
        n3.appendChild(el("p", "giai", t.ghiChu || ""));
        if ((t.trieuChung || []).length) {
          n3.appendChild(bang(
            [{ t: "Triệu chứng", trai: 1 }, { t: "nặng" }, { t: "mô tả", trai: 1 }],
            t.trieuChung.map(function (x) {
              return [{ t: x.ma, c: "trai" },
                      { t: String(x.nang), c: x.nang >= 3 ? "am" : "nhat" },
                      { t: x.moTa, c: "vi" }];
            })));
        }
        if ((t.deXuat || []).length) {
          n3.appendChild(bang(
            [{ t: "Đề xuất", trai: 1 }, { t: "từ" }, { t: "đến" }, { t: "vì", trai: 1 }],
            t.deXuat.map(function (x) {
              return [{ t: x.nut, c: "trai" }, { t: so_(x.tu, 2) },
                      { t: so_(x.den, 2) }, { t: x.vi, c: "trai" }];
            })));
        }
        if ((t.traLai || []).length) {
          n3.appendChild(el("p", "giai",
            "TRẢ LẠI: " + t.traLai.map(function (x) {
              return x.nut + " (" + x.vi + ")"; }).join(" · ")));
        }
        if (t.nhan) {
          n3.appendChild(el("p", "giai",
            "SẼ NHẬN nếu chạy thật: " + t.nhan.nut + " " + so_(t.nhan.tu, 2)
            + " → " + so_(t.nhan.den, 2) + ", cải thiện "
            + dau(t.nhan.caiThienBps, 3) + " bps"));
        }
      }
    }
    f.appendChild(o("Tiến hoá — đứng yên là kết quả hợp lệ", n3,
      "Nút này chạy chế độ THỬ: xem sẽ vặn gì mà không ghi gì. Vặn thật cần "
      + "gọi POST /api/tien-hoa?thu=false. Bốn luật chặn tự lừa: không núm nào "
      + "chạm cửa an toàn, một lượt một núm, bước ≤25%, và chỉ nhận khi ≥30 "
      + "mẫu ở CẢ HAI bên cùng cải thiện vượt 0,15 bps."));
    return f;
  }

  /* ── ô TỜ TRÌNH ─────────────────────────────────────────────────────
   * Cùng những cơ hội ở ô đầu, nhưng viết bằng ngôn ngữ CHUNG của Thị Bạc
   * Ty. Đây là thứ trung ương đọc; `Cơ hội` là thứ ty tự nghĩ.
   */
  function ve_to_trinh() {
    var ds = S.toTrinh || [];
    var f = document.createDocumentFragment();

    var l = el("div", "luoi");
    var hopLe = ds.filter(function (t) { return t.hopLe; }).length;
    var chuaDuPhi = ds.filter(function (t) { return !t.moHinhPhiDuChua; }).length;
    var khongSuc = ds.filter(function (t) { return t.sucChuaToiDaUsd == null; }).length;
    [["tờ trình xuất ra", ds.length],
     ["đúng khuôn", hopLe + "/" + ds.length],
     ["mô hình phí chưa đủ", chuaDuPhi],
     ["chưa đo được sức chứa", khongSuc]
    ].forEach(function (x) {
      var d = el("div", "so");
      d.appendChild(el("div", "n", String(x[1])));
      d.appendChild(el("div", "t", x[0]));
      l.appendChild(d);
    });
    f.appendChild(o("Ty Phái Sinh trình lên Thị Bạc Ty", l,
      "Chỉ cơ hội đã QUA cổng ty mới được trình. Cổng ty là tầng rủi ro thứ "
      + "NHẤT (chuyên môn funding); Rủi Ro Tổng của trung ương là tầng thứ "
      + "hai, và nó nhìn phơi nhiễm toàn danh mục — thứ mà không ty nào "
      + "thấy được."));

    if (!ds.length) {
      f.appendChild(o("Tờ trình", el("p", "cho",
        "chưa cơ hội nào qua cổng ty nên chưa trình gì lên"),
        "Bảng trống ở đây KHÔNG có nghĩa là thị trường không có gì — nó có "
        + "nghĩa là cổng ty đã chặn hết. Xem ô Cơ hội, cột 'vì sao'."));
      return f;
    }

    f.appendChild(o("Tờ trình — ngôn ngữ chung", bang(
      [{ t: "Tài sản", trai: 1 }, { t: "chiến lược", trai: 1 },
       { t: "chân", trai: 1 }, { t: "xin" }, { t: "sức chứa" },
       { t: "NET bps" }, { t: "NET/giờ" }, { t: "rủi ro cao nhất" },
       { t: "chưa đo", trai: 1 }, { t: "tin cậy" }, { t: "khuôn", trai: 1 }],
      ds.map(function (t) {
        var r = t.ruiRo || {};
        return [
          { t: t.taiSan, c: "trai" },
          { t: t.chienLuoc, c: "trai" },
          /* `String(...)` chứ không `c.ben.charAt(0)`: một tờ trình thiếu
             `ben` làm cả bảng NÉM, và `ve()` bắt lỗi rồi thay THÂN TRANG
             bằng ô báo lỗi — mất luôn sáu khối kia. Một trường thiếu là
             một ô «?», không phải một trang trắng. */
          { t: (t.chan || []).map(function (c) {
              return String((c && c.ben) || "?").charAt(0) + " "
                + ((c && c.cang) || "?"); }).join(" / "), c: "trai" },
          { t: "$" + so(t.vonCanUsd, 0) },
          { t: t.sucChuaToiDaUsd == null ? "—"
              : "$" + so(t.sucChuaToiDaUsd, 0),
            c: t.sucChuaToiDaUsd == null ? "am" : null },
          { t: dau(t.netUocBps), c: lop(t.netUocBps) },
          { t: dau(t.netMoiGioBps, 3), c: lop(t.netMoiGioBps) },
          { t: r.caoNhat == null ? "—" : so(r.caoNhat, 3),
            c: r.caoNhat == null ? "am" : null },
          { t: (r.chuaDo || []).join(", ") || "—", c: "vi" },
          { t: t.tinCay == null ? "—" : so(t.tinCay, 2) },
          { t: t.hopLe ? "đúng" : "SAI", c: t.hopLe ? "qua" : "am",
            title: (t.loiKhuon || []).join(" · ") }
        ];
      })),
      "Cột NET/giờ là thước SO SÁNH giữa các ty: 20 bps giữ 24 giờ thua 6 "
      + "bps giữ 2 giờ, vì vốn quay được mười hai lượt. Cột 'chưa đo' liệt "
      + "kê mặt rủi ro ty này KHÔNG đánh giá nổi — `None` chứ không phải 0, "
      + "vì 0 nghĩa là 'đã xét, không có rủi ro' và Rủi Ro Tổng sẽ cộng "
      + "những số 0 ấy thành một danh mục an toàn giả."));

    var t0 = ds[0];
    var d0 = el("div");
    d0.appendChild(bang(
      [{ t: "Mục", trai: 1 }, { t: "giá trị", trai: 1 }],
      [["mã", t0.ma], ["họ", t0.ho],
       ["cảng", (t0.cang || []).join(", ")],
       ["giữ", so(t0.giuGio, 0) + " giờ"],
       ["gross → phí → NET",
        dau(t0.grossBps) + " → −" + so(t0.phiUocBps) + " → " + dau(t0.netUocBps)],
       ["phí CÒN THIẾU", (t0.phiConThieu || []).join(", ") || "—"],
       ["sức chứa còn thiếu", (t0.sucChuaConThieu || []).join(", ") || "—"],
       ["bằng chứng", (t0.bangChung || []).join("  ·  ")]
      ].map(function (x) {
        return [{ t: x[0], c: "trai" }, { t: String(x[1]), c: "vi" }];
      })));
    f.appendChild(o("Tờ trình đầu tiên, mở ra xem", d0,
      "Mỗi tờ trình mang theo BẰNG CHỨNG — những con số dựng nên nó. Một cỗ "
      + "máy tự chia vốn thì phải cãi lại được, và không cãi được nếu chỉ "
      + "nhận một con số trần."));
    return f;
  }

  /* ── THỊ BẠC TY: chín tầng, và cái phễu ────────────────────────────────
   *
   * Ô này bày TRUNG ƯƠNG, không bày ty. Ô "Cơ hội" và "Tờ trình" là góc nhìn
   * của một ty; ô này là góc nhìn của cỗ máy chia vốn — thứ mà theo định
   * nghĩa không ty nào thấy được.
   */
  return {
    dat: dat,
    "co-hoi": ve_co_hoi, "bao-gia": ve_bao_gia, "cang": ve_cang,
    "cua": ve_cua, "to-trinh": ve_to_trinh, "hoc": ve_hoc,
    "nhat-ky": ve_nhat_ky
  };
})();
