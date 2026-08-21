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

  var S = null, O = "co-hoi", DANG_TAI = false;

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
      vonMoiCoHoiUsd: "vốn mỗi cơ hội (USD)",
      vonToiDaUsd: "vốn tối đa (USD)",
      donBayToiDa: "đòn bẩy tối đa"
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
      + "dòng nào trong nó gọi mạng hay gọi model."));

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

  var O_VE = {
    "co-hoi": ve_co_hoi, "bao-gia": ve_bao_gia,
    "cang": ve_cang, "cua": ve_cua, "nhat-ky": ve_nhat_ky
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
