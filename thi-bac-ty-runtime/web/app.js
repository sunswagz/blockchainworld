/* Buồng lái Thị Bạc Ty.
 *
 * Một luật duy nhất chi phối cả file, và nó lấy từ bài học của buồng lái Khâm
 * Thiên Giám: **trang trắng không được phép im lặng**. Ở đó `ve()` xoá thân
 * trang rồi mới vẽ, một hàm vẽ ném giữa chừng để lại thân trang rỗng, và
 * `.catch(function(){})` nuốt lỗi — nhìn y hệt máy chết trong khi máy vẫn chạy.
 *
 * Nên ở đây:
 *   · cập nhật đỉnh TRƯỚC, trong try riêng — đồng hồ không bao giờ kẹt
 *   · dựng xong phần thay thế RỒI mới thay, không xoá trước
 *   · vẽ hỏng thì HIỆN lỗi ra đúng chỗ đáng lẽ là nội dung
 *   · không đọc được runtime thì nói ra ở dải cảnh báo
 */
(function () {
  "use strict";

  var S = null, O = "co-hoi", DANG_TAI = false, TU_DANG_CHAN = false;

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
          { t: (t.chan || []).map(function (c) {
              return c.ben.charAt(0) + " " + c.cang; }).join(" / "), c: "trai" },
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
  function ve_trung_uong() {
    var f = document.createDocumentFragment();
    var T = S.trungUong || {};

    if (T.tat) {
      f.appendChild(o("Thị Bạc Ty đang TẮT",
        el("p", "cho", T.loiNhac || "Trung Ương không chạy."),
        "Ty vẫn quét và vẫn trình, nhưng không tầng nào cấp vốn. "
        + "Bật ở CONFIG['trungUong']['bat']."));
      return f;
    }

    var dm = T.danhMuc || {}, cd = T.cauDao || {}, lat = T.latCatVong || {};
    var pb = lat.phanBo || null;

    /* ── cờ trung thực đứng ĐẦU, trước mọi con số ────────────────────── */
    if (dm.nguonThat === false) {
      var canh = el("div", "loi-o");
      canh.appendChild(el("h2", null, "MÔ PHỎNG — không đồng nào là thật"));
      canh.appendChild(el("p", null, dm.loiNhac
        || "Không đọc số dư từ sàn nào."));
      canh.appendChild(el("p", "giai",
        "Mọi con số dưới đây là SỔ GIẤY. Lớp ký lệnh chưa tồn tại, nên "
        + "không cấu hình nào biến bảng này thành lệnh thật. Cờ này đứng "
        + "trên đầu chứ không nhét cuối bảng: người đọc phải gặp nó TRƯỚC "
        + "khi gặp con số."));
      f.appendChild(canh);
    }

    /* Vốn ngoài: phần gia sản Thị Bạc Ty THẤY mà không QUẢN. Cờ này đứng
       ngay dưới cờ mô phỏng, vì nó nói NAV có đủ hay không — và mọi trần
       đều tính theo NAV. */
    if (dm.loiNhacNgoai) {
      var cn = el("div", "loi-o");
      cn.appendChild(el("h2", null, "NAV ĐANG THIẾU MỘT PHẦN"));
      cn.appendChild(el("p", null, dm.loiNhacNgoai));
      (dm.ngoai || []).filter(function (x) { return !x.docDuoc; })
        .forEach(function (x) {
          cn.appendChild(el("p", "vi", "· " + x.ten + " — " + (x.vi || "?")));
        });
      f.appendChild(cn);
    }

    /* ── cầu dao ──────────────────────────────────────────────────────── */
    if (cd.dangNgat) {
      var c2 = el("div", "loi-o");
      c2.appendChild(el("h2", null, "CẦU DAO ĐANG NGẮT"));
      (cd.lyDo || []).forEach(function (l) {
        c2.appendChild(el("p", null, "· " + l.ma + " — " + l.moTa
          + (l.tuMo ? "  (tự đóng lại khi hết)" : "  (PHẢI có người đóng)")));
      });
      c2.appendChild(el("p", "giai",
        "Ngắt thì vẫn quét, vẫn ghi nhận, vẫn chẩn đoán — chỉ KHÔNG cam kết "
        + "vốn. Dừng cả việc quan sát là tự làm mình mù đúng lúc cần nhìn "
        + "nhất. Lý do không tự mở phải đóng bằng: "
        + "curl -X POST 'localhost:" + (location.port || "5188")
        + "/api/cau-dao/dong-lai?ma=<mã>&nguoi=<tên>'"));
      f.appendChild(c2);
    }

    /* ── số tổng ──────────────────────────────────────────────────────── */
    var l = el("div", "luoi");
    [["NAV (sổ giấy)", "$" + so(dm.navUsd, 2)],
     ["Thị Bạc Ty tự quản", "$" + so(dm.tuQuanUsd, 2)],
     ["vốn ngoài (thấy, không quản)",
      dm.ngoaiDayDu === false ? "KHÔNG ĐỌC ĐƯỢC" : "$" + so(dm.ngoaiUsd, 2)],
     ["tiền mặt", "$" + so(dm.tienMatUsd, 2)],
     ["dùng vốn", dm.tiLeDungVon == null ? "—"
        : (dm.tiLeDungVon * 100).toFixed(1) + "%"],
     ["vị thế đang mở", (dm.soViThe == null ? (T.thucThi || {}).soPhien : dm.soViThe)],
     ["cầu dao", cd.dangNgat ? "NGẮT" : "đóng"],
     ["bút toán", (T.soCai || {}).soButToan],
     ["tầng đi tắt", (T.soDangKy || {}).soChuyenSai],
     ["bản tham số", "#" + (((T.banThamSo || {}).hienHanh || {}).so || "—")]
    ].forEach(function (x) {
      var d = el("div", "so");
      d.appendChild(el("div", "n", String(x[1] == null ? "—" : x[1])));
      d.appendChild(el("div", "t", x[0]));
      l.appendChild(d);
    });
    f.appendChild(o("Thị Bạc Ty — bộ máy chia vốn", l,
      "«Tầng đi tắt» phải luôn là 0. Khác 0 nghĩa là có tầng gọi vượt cấp — "
      + "vốn tới được vị thế mà Rủi Ro Tổng chưa từng thấy tờ trình. Đó là "
      + "lỗi kiến trúc, không phải lỗi tham số."));

    /* ── cái phễu ─────────────────────────────────────────────────────── */
    var p = T.pheuDayDu || {};
    var nac = p.nac || [];
    var NHAN_NAC = {
      coHoiTho: "cơ hội thô", quaCongTy: "qua cổng ty",
      DUYET_RUI_RO: "qua rủi ro tổng", DA_CAP_VON: "được cấp vốn",
      DA_MO: "đã mở vị thế", DA_DONG: "đã đóng"
    };
    f.appendChild(o("Cái phễu — cỗ máy này có học không", bang(
      [{ t: "Nấc", trai: 1 }, { t: "số" }, { t: "còn lại" }],
      nac.map(function (n) {
        return [
          { t: NHAN_NAC[n.ten] || n.ten, c: "trai" },
          { t: String(n.so) },
          /* `None` chứ không phải 0%: "chưa thấy cơ hội nào" khác hẳn
           * "thấy rồi mà không cái nào qua". */
          { t: n.tiLe == null ? "—" : (n.tiLe * 100).toFixed(1) + "%",
            c: n.tiLe == null ? "nhat" : null }
        ];
      }).concat([
        [{ t: "— bị từ chối", c: "trai" }, { t: String(p.tuChoi == null ? "—" : p.tuChoi) }, { t: "" }],
        [{ t: "— hỏng khi mở", c: "trai" }, { t: String(p.hong == null ? "—" : p.hong) }, { t: "" }]
      ])),
      "Từng con số một mình vô nghĩa; cả phễu thì nói rất nhiều. Cột «còn "
      + "lại» chia cho số cơ hội THẬT, không phải số lượt quét — cùng một "
      + "cơ hội quét lại 120 lần mỗi giờ chỉ vào sổ một lần "
      + ((lat.soBoTrung || 0) ? "(vòng vừa rồi bỏ " + lat.soBoTrung
          + " lượt trùng)" : "") + "."));

    /* ── giữ tối thiểu bao lâu mới CHẠM một mốc ──────────────────── */
    var gtt = S.giuToiThieuGio || [];
    if (gtt.length) {
      f.appendChild(o("Giữ dưới bao lâu thì thu ĐÚNG BẰNG KHÔNG", bang(
        [{ t: "cảng", trai: 1 }, { t: "mã", trai: 1 },
         { t: "phải giữ ít nhất" }, { t: "chu kỳ" }],
        gtt.map(function (x) {
          return [{ t: x.san, c: "trai" }, { t: x.ma, c: "trai" },
                  { t: (x.gio || 0).toFixed(2) + "h",
                    c: (x.gio || 0) > 4 ? "am" : null },
                  { t: (x.chuKyGio || 0) + "h" }];
        })),
        "Funding trả theo MỐC, không chảy liên tục. Giữ bốn giờ trên một "
        + "sàn kết toán tám giờ có thể thu đúng bằng KHÔNG — và người vận "
        + "hành không nên phải tự suy ra điều đó từ bảng mốc kế tiếp."));
    }

    /* ── Router · sổ ngoài · engine chưa dựng ────────────────────────
       Ba cơ chế chạy mà trước 27/08 buồng lái KHÔNG thấy. Một cơ chế
       không ai nhìn được là một cơ chế không ai tin, và nó im lặng hỏng
       đúng như ba cửa giả trong `bac/rui_ro.py` đã im lặng. */
    var R = S.router || null;
    if (R) {
      var rd = el("div");
      if (R.co === false) {
        rd.appendChild(el("p", "am", "Router CHƯA dựng — "
          + (R.vi || "các ty giữ nguyên khai báo phiConThieu")));
      } else {
        var thieuGas = (R.chuoiThieuGas || []);
        rd.appendChild(el("p", thieuGas.length ? "vi" : "qua",
          "gas SỐNG trên " + (R.chuoiCoGas || []).length + " chuỗi: "
          + (R.chuoiCoGas || []).join(", ")
          + (thieuGas.length ? " · THIẾU: " + thieuGas.join(", ") : "")));
        rd.appendChild(el("p", "giai",
          "nhà = " + (R.nha || "?") + " · giá token gốc đọc được: "
          + ((R.tokenCoGia || []).join(", ") || "KHÔNG có")
          + " · báo giá cầu trong kho: " + (R.soBaoGiaTrongKho || 0)));
        if (!(R.tokenCoGia || []).length) {
          rd.appendChild(el("p", "am",
            "Không có giá token gốc thì MỌI chặng gas đều mù, và cái mù ấy "
            + "chảy lên tận tổng — đó là thiết kế, không phải lỗi."));
        }
      }
      var NC = S.nguonCau || {};
      if (NC.dangNghi) {
        rd.appendChild(el("p", "am",
          "NGUỒN CẦU NỐI đang NGHỈ vì hạn mức (429) — còn "
          + Math.round((NC.conNghiGiay || 0) / 60) + " phút, đã dính "
          + (NC.soLan429 || 0) + " lần. Mọi tuyến liên chuỗi MÙ tới lúc "
          + "ấy, và các ty giữ nguyên khai báo phiConThieu."));
      } else if (NC.soLan429) {
        rd.appendChild(el("p", "vi", "nguồn cầu nối đã dính 429 "
          + NC.soLan429 + " lần trong phiên này — hạn mức miễn phí có "
          + "thật, và nạp trước quá tay là tự chặn mình."));
      }
      f.appendChild(o("Router chuyển vốn — hạ tầng, KHÔNG phải ty", rd,
        "Nó trả lời «dời $X từ đâu tới đâu tốn gì, mất bao lâu, và có gì "
        + "tôi KHÔNG đo được không». Câu cuối mới là phần đáng giá: một "
        + "chặng không đo được thì CẢ TUYẾN không đo được, chứ không cộng "
        + "vòng qua lỗ hổng."));
    }

    var SN = (T.soNgoai || []);
    if (SN.length) {
      var snd = el("div");
      SN.forEach(function (x) {
        snd.appendChild(el("p", x.docDuoc ? "qua" : "vi",
          x.ten + ": " + (x.docDuoc ? "đọc được" : "KHÔNG đọc được — "
            + (x.vi || "").slice(0, 70))
          + " · đã nhập " + (x.soDaVao || 0) + " bút toán"
          + (x.soBoSot ? " · BỎ SÓT " + x.soBoSot : "")
          + (x.boSotDoDuoc ? "" : " · chưa đo được bỏ sót")));
      });
      f.appendChild(o("Sổ ngoài — kết toán cỗ máy khác vào MỘT sổ cái", snd,
        "Bên kia chỉ đưa 12 bản ghi gần nhất. Kết toán hơn 12 lần giữa hai "
        + "lượt hỏi thì phần giữa mất hẳn, và mất trong im lặng — sổ vẫn "
        + "cân, vẫn không lỗi, chỉ thiếu tiền. Nên `soBoSot` đếm ra được, "
        + "và «không thiếu» khác «không biết có thiếu không»."));
    }

    var DC = S.dongCoChuaCo || null;
    if (DC && DC.soDongCo) {
      var dcd = el("div");
      dcd.appendChild(el("p", DC.soQuetDuoc ? "vi" : "qua",
        DC.soDongCo + " engine trong sổ · ĐÃ DỰNG " + DC.soDaDung
        + " · quét được nhưng chưa dựng " + DC.soQuetDuoc
        + " · CHẶN " + DC.soChan));
      var tt = DC.theoTrangThai || {};
      ["DA_DUNG", "SAN_SANG", "QUET_DUOC", "CHAN"].forEach(function (k) {
        if ((tt[k] || []).length) {
          dcd.appendChild(el("p", k === "CHAN" ? "giai" : "vi",
            k + ": " + tt[k].join(", ")));
        }
      });
      dcd.appendChild(el("p", "giai", "đọc đủ kèm từng điều kiện: curl -s "
        + "localhost:" + (location.port || "5188")
        + "/api/dong-co-chua-co?day_du=true"));
      f.appendChild(o("Engine CHƯA dựng — điều kiện chặn viết dạng CHẠY ĐƯỢC",
        dcd,
        "Bảng văn xuôi cũ nói «sáu engine bị chặn» và nó HỎNG trong cùng "
        + "một ngày: Router ra đời buổi chiều và gỡ điều kiện của hai dòng. "
        + "Nên mỗi engine nay mang điều kiện chặn của chính nó dưới dạng "
        + "hàm canh, và sổ TỰ biết cái nào đã dựng bằng cách nạp thử gói."));
    }

    /* ── hiến pháp: điều nào đang THẬT SỰ được canh ─────────────────── */
    var hp = T.hienPhap;
    if (hp) {
      var hpd = el("div", hp.soViPham ? "loi-o" : null);
      if (hp.soViPham) {
        hpd.appendChild(el("h2", null, "VI PHẠM HIẾN PHÁP"));
        (hp.viPham || []).forEach(function (v) {
          hpd.appendChild(el("p", "am", "· " + v.ma + " — " + v.chiTiet));
        });
      } else {
        hpd.appendChild(el("p", "qua",
          hp.soDieu + " điều · " + hp.soCanhDuoc + " canh được · KHÔNG vi phạm"));
      }
      hpd.appendChild(el("p", "vi", "KHÔNG canh được (" + hp.soKhongCanhDuoc
        + "): " + (hp.khongCanhDuoc || []).join(", ")));
      hpd.appendChild(el("p", "giai", hp.loiNhac));
      hpd.appendChild(el("p", "giai", "đọc đủ kèm lý do từng điều: curl -s "
        + "localhost:" + (location.port || "5188")
        + "/api/hien-phap?day_du=true"));
      f.appendChild(o("Hiến pháp — luật viết dưới dạng CHẠY ĐƯỢC", hpd,
        "Kho này đã tự chứng minh rằng nguyên tắc nằm trong văn xuôi thì "
        + "không giữ được gì: `bac/rui_ro.py` từng khai ba cửa mà `xet()` "
        + "không đọc tới, và buồng lái bày chúng dưới nhãn «đang có hiệu "
        + "lực» suốt nhiều tuần. Nên mỗi điều mang theo phép canh của nó, "
        + "và điều nào KHÔNG canh được thì phải khai ra là không canh được."));
    }

    /* ── chế độ vận hành từng ty ─────────────────────────────────────
       Toàn bộ hệ thống chạy được; toàn bộ vốn KHÔNG cần chạy ở toàn bộ
       chiến lược. Bảng này là chỗ nhìn thấy sự tách ấy. */
    var ct = T.cheTy || [];
    if (ct.length) {
      f.appendChild(o("Engine nào được cấp vốn, engine nào chỉ QUAN SÁT", bang(
        [{ t: "Engine", trai: 1 }, { t: "họ", trai: 1 }, { t: "chế độ" },
         { t: "cần tối thiểu" }, { t: "rót được nhiều nhất" },
         { t: "vì sao", trai: 1 }],
        ct.map(function (x) {
          return [
            { t: x.ma, c: "trai" },
            { t: x.ho, c: "trai" },
            { t: x.che, c: x.duocCapVon ? "qua" : "chan" },
            { t: x.vonToiThieuUsd == null ? "—" : "$" + so(x.vonToiThieuUsd, 0) },
            { t: "$" + so(x.tranMotCoHoiUsd, 0) },
            { t: x.vi, c: "vi" }
          ];
        })),
        "QUAN_SAT = quét, trình, ghi sổ — nhưng KHÔNG BAO GIỜ được cấp vốn. "
        + "GIAY = được cấp trên sổ giấy. THAT = tiền thật, và nó chưa với "
        + "tới được vì lớp ký lệnh chưa tồn tại. Chế độ suy TẤT ĐỊNH từ NAV "
        + "và ngưỡng kinh tế của từng engine — không ai gõ tay, và máy không "
        + "được tự ép một engine lên chế độ cao hơn."));
    }

    /* ── hiệu năng và chi phí hạ tầng ───────────────────────────────── */
    var hn = T.hieuNang;
    if (hn) {
      var ht = hn.haTang || {};
      var hd = el("div");
      hd.appendChild(bang(
        [{ t: "Thước", trai: 1 }, { t: "giá trị" }],
        [["lãi lỗ so vốn ban đầu",
          hn.laiLoPhanTram == null ? "—" : so(hn.laiLoPhanTram, 2) + "%"],
         ["CAGR", hn.cagrPhanTram == null ? "chưa đủ mẫu"
            : so(hn.cagrPhanTram, 2) + "%"],
         ["sụt vốn tối đa (từ đỉnh)", so(hn.sutVonToiDaPhanTram, 2) + "%"],
         ["lâu nhất chưa về đỉnh cũ", gio((hn.gioDuoiDayLauNhat || 0) * 3600)],
         ["đang dưới đáy", hn.dangDuoiDay ? "CÓ" : "không"],
         ["hạ tầng mỗi năm", "$" + so(ht.chiPhiNamUsd, 0)],
         ["vốn cần để hoà hạ tầng (20%/năm)",
          "$" + so((ht.vonHoaVon || {})["20%"], 0)],
         ["vốn cần để có ÍT NHẤT một engine chạy bằng tiền",
          hn.vonCanDeCoMotEngineChay == null ? "—"
            : "$" + so(hn.vonCanDeCoMotEngineChay, 0)]
        ].map(function (r) {
          return [{ t: r[0], c: "trai" }, { t: String(r[1]) }];
        })));
      if (hn.duDeKetLuan === false && hn.vi) {
        hd.appendChild(el("p", "cho", hn.vi));
      }
      if ((hn.giayVaThat || {}).doiChieuDuoc === false) {
        hd.appendChild(el("p", "giai", "đối chiếu giấy ↔ thật: "
          + hn.giayVaThat.vi));
      }
      f.appendChild(o("Hiệu năng — đo bằng đường NAV, không bằng một APR", hd,
        "Vốn thật đi qua 100 × 1,12 × 1,31 × 0,92 × 1,22, chứ không phải "
        + "100 × 1,5^n. Một năm âm ở giữa ăn vào cái nền mà mọi năm sau nhân "
        + "lên từ đó. Và $100 kiếm 20%/năm là $20 — vẫn âm sau hạ tầng "
        + "$120/năm, nên ở giai đoạn này đánh giá bộ máy bằng số đô kiếm "
        + "được là đánh giá sai thứ."));
    }

    /* ── §22 · phễu tách theo HỌ ─────────────────────────────────────── */
    var theoHo = (p.theoHo || []);
    if (theoHo.length) {
      f.appendChild(o("Từng họ đang nuôi được vốn không", bang(
        [{ t: "Họ", trai: 1 }, { t: "cơ hội thô" }, { t: "qua cổng ty" },
         { t: "qua rủi ro tổng" }, { t: "được cấp vốn" }, { t: "đang giữ" }],
        theoHo.map(function (h) {
          return [
            { t: h.ho, c: "trai" },
            { t: String(h.coHoiTho) },
            { t: String(h.quaCongTy) },
            { t: String(h.quaRuiRoTong) },
            { t: String(h.daCapVon), c: h.daCapVon ? "qua" : null },
            { t: "$" + so(h.vonDangGiuUsd, 0) }
          ];
        })),
        "Tổng gộp nói được «cỗ máy có học không». Bảng này nói thứ khác, và "
        + "là thứ người chia vốn cần: HỌ NÀO đang nuôi được vốn. Một họ phát "
        + "hiện nhiều mà chưa bao giờ qua nổi Rủi Ro Tổng là một họ đang "
        + "tiêu thời gian máy mà không sinh ra gì."));
    }

    /* ── phân bổ vòng gần nhất ────────────────────────────────────────── */
    if (pb && (pb.daCap || []).length) {
      f.appendChild(o("Vốn đã cấp — vòng gần nhất", bang(
        [{ t: "Tài sản", trai: 1 }, { t: "ty", trai: 1 }, { t: "xin" },
         { t: "trần" }, { t: "cấp" }, { t: "NET/giờ" }, { t: "rủi ro" },
         { t: "vì sao bị cắt", trai: 1 }],
        pb.daCap.map(function (x) {
          return [
            { t: x.taiSan, c: "trai" },
            { t: x.chienLuoc, c: "trai" },
            { t: "$" + so(x.xinUsd, 0) },
            { t: "$" + so(x.choToiDaUsd, 0) },
            { t: "$" + so(x.capUsd, 2), c: "qua" },
            { t: dau(x.netMoiGioBps, 3), c: lop(x.netMoiGioBps) },
            { t: x.diemRuiRo == null ? "—" : so(x.diemRuiRo, 2) },
            { t: x.biCat ? (x.lyDoCat || []).join(" · ") : "—", c: "vi" }
          ];
        })),
        "Cấp TUẦN TỰ, không song song: sau mỗi lần cấp, Rủi Ro Tổng xét lại "
        + "trên danh mục ĐÃ cập nhật. Cấp song song thì hai tờ trình cùng "
        + "chạm một cảng đều 'lọt', và chỉ vượt trần sau khi cộng lại."));
    }

    if (pb && (pb.tuChoi || []).length) {
      f.appendChild(o("Bị từ chối — và vì sao", bang(
        [{ t: "Tờ trình", trai: 1 }, { t: "ty", trai: 1 },
         { t: "xin" }, { t: "lý do", trai: 1 }],
        pb.tuChoi.slice(0, 20).map(function (x) {
          var ly = x.lyDo;
          if (Object.prototype.toString.call(ly) === "[object Array]")
            ly = ly.join("; ");
          return [
            { t: String(x.maToTrinh || "—").slice(0, 10), c: "trai" },
            { t: x.chienLuoc || "—", c: "trai" },
            { t: x.xinUsd == null ? "—" : "$" + so(x.xinUsd, 0) },
            { t: String(ly || "—"), c: "vi" }
          ];
        })),
        "Từ chối luôn kèm lý do. Một hệ thống chỉ ghi lại lúc nó đồng ý thì "
        + "lịch sử của nó toàn thắng lợi."));
    }

    /* ── phơi nhiễm: ba thước, ba câu hỏi ─────────────────────────────── */
    var pnR = dm.phoiNhiemRong || {}, pnT = dm.phoiNhiemTho || {};
    var ts = Object.keys(pnT);
    if (ts.length) {
      f.appendChild(o("Phơi nhiễm — ba thước, ba câu hỏi khác nhau", bang(
        [{ t: "Tài sản", trai: 1 }, { t: "ròng (hướng giá)" },
         { t: "thô (thanh khoản)" }],
        ts.map(function (k) {
          return [{ t: k, c: "trai" },
                  { t: dau(pnR[k] || 0, 2), c: lop(pnR[k] || 0) },
                  { t: so(pnT[k], 2) }];
        })),
        "RÒNG trả lời «giá chạy thì ta thiệt bao nhiêu» — cặp delta-neutral "
        + "ra 0. THÔ trả lời «muốn thoát thì phải bán bao nhiêu» — cặp ấy ra "
        + "gấp đôi. Một cỗ máy chỉ đo ròng sẽ tưởng mình không có rủi ro "
        + "thanh khoản nào."));
    }

    /* ── chẩn đoán hệ ─────────────────────────────────────────────────── */
    var h = T.hoc;
    var d = el("div");
    if (!h) {
      d.appendChild(el("p", "cho", "chưa chạy lượt chẩn nào"));
    } else {
      d.appendChild(bang(
        [{ t: "Triệu chứng", trai: 1 }, { t: "nặng" }, { t: "mô tả", trai: 1 }],
        (h.trieuChung || []).map(function (t) {
          return [{ t: t.ma, c: "trai" },
                  { t: "●".repeat(t.nang), c: t.nang >= 3 ? "am" : "chan" },
                  { t: t.moTa, c: "vi" }];
        })));
      (h.deXuat || []).forEach(function (x) {
        d.appendChild(el("p", null, "đề xuất: " + x.nut + "  "
          + so(x.tu, 3) + " → " + so(x.den, 3) + "   (vì «" + x.vi + "»)"));
      });

      /* Đề xuất phải kèm SỐ ĐO, không được để trần. `doDuoc` là kết quả
         chạy lại quyết định phân bổ trên tờ trình đã ghi — nó không nói
         được lãi lỗ, nhưng nó bắt được lúc một đề xuất chỉ "tốt hơn" nhờ
         ôm rủi ro đậm hơn. */
      var dd = h.doDuoc;
      if (dd && dd.duDeKetLuan === false) {
        d.appendChild(el("p", "cho", "chưa đo được: " + dd.vi));
      } else if (dd) {
        var pt = function (v) { return v == null ? "—" : (v * 100).toFixed(0) + "%"; };
        d.appendChild(bang(
          [{ t: "Đo trên tờ trình đã ghi", trai: 1 }, { t: "A (nay)" },
           { t: "B (đề xuất)" }],
          [["vốn rót ra", "$" + so(dd.A.tongCapUsd, 0), "$" + so(dd.B.tongCapUsd, 0)],
           ["số cơ hội được cấp", dd.A.soCap, dd.B.soCap],
           ["NET/giờ bình quân (theo vốn)",
            so(dd.A.netMoiGioBinhQuanBps, 3), so(dd.B.netMoiGioBinhQuanBps, 3)],
           ["cảng dày nhất / vốn rót", pt(dd.A.tiTrongCang), pt(dd.B.tiTrongCang)],
           ["ty dày nhất / vốn rót", pt(dd.A.tiTrongTy), pt(dd.B.tiTrongTy)]
          ].map(function (r) {
            return [{ t: r[0], c: "trai" }, { t: String(r[1]) }, { t: String(r[2]) }];
          })));
        var k = el("p", dd.ketLuan === "b-tot-hon" ? "qua" : "chan",
                   dd.ketLuan + " — " + dd.vi);
        d.appendChild(k);
        d.appendChild(el("p", "giai", dd.loiNhac));
      }
      if (!(h.deXuat || []).length)
        d.appendChild(el("p", "cho",
          "không đề xuất vặn gì — đứng yên là một kết quả hợp lệ"));
    }
    /* §17 · Cổng Duyệt đứng SAU phép đo và TRƯỚC mọi đường áp dụng. */
    var cd2 = h && h.congDuyet;
    if (cd2) {
      var kh = el("div", cd2.duDieuKien ? "" : "loi-o");
      kh.appendChild(el("p", cd2.duDieuKien ? "qua" : "chan",
        cd2.duDieuKien
          ? "CỔNG DUYỆT: đủ điều kiện — " + cd2.nut + "  "
            + so(cd2.tu, 3) + " → " + so(cd2.den, 3)
          : "CỔNG DUYỆT: KHÔNG đủ điều kiện"));
      (cd2.lyDo || []).forEach(function (l) {
        kh.appendChild(el("p", "vi", "· " + l));
      });
      (cd2.ghiChu || []).forEach(function (g) {
        kh.appendChild(el("p", "giai", "~ " + g));
      });
      kh.appendChild(el("p", "giai", cd2.loiNhac));
      if (cd2.duDieuKien) {
        kh.appendChild(el("p", "giai",
          "Áp dụng phải khai tên người: curl -X POST 'localhost:"
          + (location.port || "5188")
          + "/api/ap-dung-tham-so?nguoi=<tên>'"));
      }
      d.appendChild(kh);
    }
    if (h && h.banHienHanh != null) {
      d.appendChild(el("p", "giai",
        "Bản tham số đang chạy: #" + h.banHienHanh
        + " · lịch sử ở /api/ban-tham-so · quay lui bằng "
        + "/api/quay-lui-tham-so?veSo=N&nguoi=<tên>"));
    }

    var nut = el("button", "nut", "Chẩn lại cả bộ máy");
    nut.disabled = !!TU_DANG_CHAN;
    nut.addEventListener("click", function () {
      TU_DANG_CHAN = true; ve();
      // `ghiSo=false`: xem mà không để lại dấu. Bấm nhầm một nút không được
      // phép thêm một dòng vào nhật ký xét tham số.
      fetch("/api/hoc?ghiSo=false", { method: "POST" })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (S && S.trungUong) S.trungUong.hoc = j;
          nhac("đã chẩn: " + (j.trieuChung || []).length + " triệu chứng, "
               + (j.deXuat || []).length + " đề xuất");
        })
        .catch(function (e) { nhac("chẩn lỗi: " + (e && e.message || e)); })
        .finally(function () { TU_DANG_CHAN = false; ve(); });
    });
    d.appendChild(nut);
    f.appendChild(o("Chẩn đoán hệ — và xét lại tham số", d,
      "Khác hẳn ô «Đào tạo»: ô kia chẩn xem TY này phát hiện có chuẩn không; "
      + "ô này chẩn xem CẢ BỘ MÁY có chuyển tiền tới chỗ đáng không. Và ở "
      + "đây máy chỉ ĐỀ XUẤT, không tự vặn — đổi tham số phân bổ là đổi cách "
      + "chia tiền giữa các ty, mà chuyện đó không chạy lại được nên không "
      + "A/B được, nên không tự nhận được. Người duyệt."));

    return f;
  }

  var O_VE = {
    "co-hoi": ve_co_hoi, "bao-gia": ve_bao_gia,
    "cang": ve_cang, "cua": ve_cua,
    "to-trinh": ve_to_trinh, "trung-uong": ve_trung_uong, "hoc": ve_hoc,
    "nhat-ky": ve_nhat_ky
  };

  /* ── vẽ: dựng xong RỒI mới thay, và lỗi phải HIỆN ra ───────────────── */
  function ve() {
    try { ve_dinh(); ve_canh(); } catch (e) { /* đỉnh không được kéo theo thân */ }
    if (!S) return;
    var moi;
    try {
      moi = (O_VE[O] || ve_co_hoi)();
    } catch (e) {
      moi = document.createDocumentFragment();
      var d = el("div", "loi-o");
      d.appendChild(el("h2", null, "Ô «" + O + "» vẽ hỏng"));
      d.appendChild(el("p", null, String(e && e.message || e)));
      d.appendChild(el("pre", null,
        String(e && e.stack || "").split("\n").slice(0, 6).join("\n")));
      d.appendChild(el("p", "giai",
        "Máy VẪN ĐANG CHẠY — đây là lỗi của trang, không phải của runtime. "
        + "Dựng lại lỗi ở dòng lệnh: curl -s localhost:"
        + (location.port || "5188") + "/api/trang-thai"));
      moi.appendChild(d);
    }
    var than = $("#than");
    than.replaceChildren(moi);
  }

  /* ── tải ───────────────────────────────────────────────────────────── */
  function tai() {
    if (DANG_TAI) return Promise.resolve();
    DANG_TAI = true;
    return fetch("/api/trang-thai", { cache: "no-store" })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (j) { S = j; ve(); })
      .catch(function (e) {
        var d = $("#dai-canh");
        d.hidden = false;
        d.className = "dai-canh";
        d.textContent = "KHÔNG ĐỌC ĐƯỢC RUNTIME: " + (e && e.message || e)
          + " — runtime còn chạy không? (python run.py)";
      })
      .finally(function () { DANG_TAI = false; });
  }

  function nhac(t) { $("#chan-nhac").textContent = t || ""; }

  document.addEventListener("click", function (ev) {
    var b = ev.target.closest("#tab button");
    if (b) {
      O = b.dataset.o;
      Array.prototype.forEach.call(document.querySelectorAll("#tab button"),
        function (x) { x.classList.toggle("chon", x === b); });
      ve();
    }
  });

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
