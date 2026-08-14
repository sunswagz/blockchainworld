/* ═══════════════════════════════════════════════════════
   TẠO BIỆN XỨ — giao diện công xưởng.

   Định tuyến bằng hash:
     #/san        sàn máy — dây chuyền chạy thật, có vòng đẩy ngược
     #/may        18 máy, mỗi máy đủ 10 trường spec
     #/tang       4 tầng: bộ não → tính cách → máy → thực thi
     #/day        dây chuyền (routines)
     #/to         tổ thợ và kỹ năng
     #/duyet      bốn mức duyệt
     #/dong-co    bộ chọn động cơ — ví dụ định tuyến model
     #/lo-trinh   V1 → V2 → V3 và cây thư mục hồ sơ

   ── VÌ SAO MÔ PHỎNG CHỨ KHÔNG GỌI API THẬT ────────────
   Trang này chạy trên GitHub Pages công khai. Mọi thứ trình
   duyệt tải về đều đọc được, nên nhúng API key vào đây là làm
   lộ key — không có cách nào giấu. Đây là luật đã chốt của cả
   repo (xem dai-quan-trac: bản gốc từng gọi thẳng
   api.anthropic.com và tính năng đó chưa bao giờ chạy).

   Nên phần "kết nối mô hình AI" ở đây là BẢNG ĐỊNH TUYẾN chạy
   tại chỗ: cho thấy M07 chọn động cơ nào cho bước nào và vì
   sao. Muốn gọi thật thì dựng `scripts/build-*.mjs` chạy trong
   GitHub Actions với key trong repo Secrets, sinh ra file tĩnh
   rồi commit — đúng đường mà bốn cung kia đang đi.
   App nói rõ điều này ngay trên màn hình, không giả vờ.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var X = window.XUONG;
  var than = document.getElementById("than");
  var tieu = document.getElementById("tieu");
  var phu = document.getElementById("phu");

  if (!X) return;

  var mayTheoId = {}, khuTheoMa = {}, dcTheoMa = {}, knTheoId = {};
  X.MAY.forEach(function (m) { mayTheoId[m.id] = m; });
  X.KHU.forEach(function (k) { khuTheoMa[k.ma] = k; });
  X.DONG_CO.forEach(function (d) { dcTheoMa[d.ma] = d; });
  X.KY_NANG.forEach(function (s) { knTheoId[s.id] = s; });

  /* ── tiện ───────────────────────────────────────────── */
  function el(t, l, c) {
    var e = document.createElement(t);
    if (l) e.className = l;
    if (c != null) e.textContent = c;
    return e;
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function svg(p, w) {
    return '<svg width="' + (w || 15) + '" height="' + (w || 15) + '" viewBox="0 0 24 24" ' +
      'fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" ' +
      'stroke-linejoin="round">' + p + "</svg>";
  }
  var IC = {
    sodo: '<rect x="9" y="2" width="6" height="4" rx="1"/><rect x="2" y="10" width="6" height="4" rx="1"/>' +
          '<rect x="16" y="10" width="6" height="4" rx="1"/><rect x="9" y="18" width="6" height="4" rx="1"/>' +
          '<path d="M12 6v4M5 14v2h14v-2M12 16v2"/>',
    san: '<path d="M3 21h18M5 21V11l4-3v13M13 21V6l6-3v18"/><path d="M8 14h.01M8 17h.01M16 10h.01M16 14h.01"/>',
    may: '<rect x="3" y="8" width="18" height="12" rx="2"/><path d="M7 8V5h10v3M7 14h4M15 14h2"/>',
    tang: '<path d="M12 3 3 8l9 5 9-5-9-5Z"/><path d="m3 13 9 5 9-5M3 18l9 5 9-5"/>',
    day: '<circle cx="6" cy="12" r="3"/><circle cx="18" cy="12" r="3"/><path d="M6 9h12M6 15h12"/>',
    to: '<circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0 1 12 0"/><path d="M16 6a3 3 0 0 1 0 6M18 20a5 5 0 0 0-3-4.6"/>',
    duyet: '<path d="M12 2 4 6v6c0 5 3.4 8.9 8 10 4.6-1.1 8-5 8-10V6l-8-4Z"/><path d="m9 12 2 2 4-4"/>',
    dc: '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 2v2M15 2v2M9 20v2M15 20v2M2 9h2M2 15h2M20 9h2M20 15h2"/>',
    lo: '<path d="M3 21h18"/><path d="m4 17 5-5 4 3 7-8"/><path d="M15 7h5v5"/>',
    chay: '<path d="m6 3 14 9-14 9V3Z"/>',
    dung: '<rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/>',
    xoa: '<path d="M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14"/>',
    quay: '<path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/>',
    tay: '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/>'
  };

  /* ═══════════════ thanh bên ═══════════════ */
  var MUC_BEN = [
    ["#/so-do", "Sơ đồ nhà máy", IC.sodo],
    ["#/san", "Sàn máy", IC.san],
    ["#/may", "18 máy", IC.may],
    ["#/tang", "Bốn tầng", IC.tang],
    ["#/day", "Dây chuyền", IC.day],
    ["#/to", "Tổ thợ & kỹ năng", IC.to],
    ["#/duyet", "Bốn mức duyệt", IC.duyet],
    ["#/dong-co", "Bộ chọn động cơ", IC.dc],
    ["#/lo-trinh", "Lộ trình dựng", IC.lo]
  ];
  var DEM_BEN = { "#/may": X.MAY.length, "#/day": X.DAY.length, "#/to": X.TO.length,
                  "#/duyet": X.MUC.length, "#/dong-co": X.DONG_CO.length };

  function dungBen() {
    var h = document.getElementById("benMuc");
    h.innerHTML = "";
    h.appendChild(el("div", "blab", "Trong xưởng"));
    MUC_BEN.forEach(function (m) {
      var a = el("a", "bmuc");
      a.href = m[0];
      a.dataset.hash = m[0];
      a.innerHTML = '<span class="bic">' + svg(m[2], 16) + '</span><span class="bten">' +
        esc(m[1]) + "</span>" + (DEM_BEN[m[0]] ? '<span class="bn">' + DEM_BEN[m[0]] + "</span>" : "");
      h.appendChild(a);
    });
  }
  function sangBen(hash) {
    document.querySelectorAll("#benMuc .bmuc").forEach(function (a) {
      if (a.dataset.hash === hash) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  /* ═══════════════════════════════════════════════════════
     MÔ PHỎNG DÂY CHUYỀN

     Đường đi tuần tự đi qua 13 máy. Năm máy khu nền tảng
     (M07–M11) KHÔNG nằm trên đường đi — chúng là kho được máy
     khác gọi tới, nên chỉ nháy đèn khi bị gọi. Đây là điểm
     bản phác nói rõ và dễ vẽ sai thành một hàng dọc 18 máy.

     Hai vòng đẩy ngược, cả hai đều có thật trong bản phác:
       M13 trượt kiểm  → quay lại M12
       M18 rút bài học → ghi ngược vào M09
     ═══════════════════════════════════════════════════════ */

  var DUONG = ["M01", "M02", "M03", "M04", "M05", "M06", "M12", "M13", "M14", "M15", "M16", "M17", "M18"];
  var GOI_KHO = {                     // máy nào gọi kho nào
    M04: ["M08", "M09"], M05: ["M09"], M06: ["M07", "M10", "M11"], M12: ["M11"], M18: ["M09"]
  };
  var LOAI_VIEC = [
    { t: "Điều tra công ty", m: 1 }, { t: "Dựng trang web", m: 2 },
    { t: "Tóm tắt tài liệu nội bộ", m: 1 }, { t: "Sửa lỗi trong mã", m: 1 },
    { t: "Gửi thư báo giá", m: 2 }, { t: "Chuyển tiền nhà cung cấp", m: 3 },
    { t: "Soạn báo cáo tuần", m: 1 }, { t: "Gộp mã vào nhánh chính", m: 2 }
  ];

  var MP = null;   // trạng thái mô phỏng, chỉ sống khi đang ở #/san

  function moPhong() {
    return {
      chay: true, nhip: 620, dong: null, soJob: 0,
      job: [], cho: [], nk: [],
      dem: { xong: 0, chan: 0, tra: 0, hoc: 0 },
      nhay: {}          // id máy → số nhịp còn sáng
    };
  }

  function ghiNk(loai, may, chu) {
    var d = new Date();
    var p = function (n) { return String(n).padStart(2, "0"); };
    MP.nk.unshift({
      t: p(d.getHours()) + ":" + p(d.getMinutes()) + ":" + p(d.getSeconds()),
      m: may, x: chu, loai: loai
    });
    if (MP.nk.length > 90) MP.nk.pop();
  }

  function themJob() {
    var l = LOAI_VIEC[Math.floor(Math.random() * LOAI_VIEC.length)];
    MP.soJob++;
    var j = {
      id: "J" + String(MP.soJob).padStart(3, "0"),
      ten: l.t, muc: l.m, vt: 0, tra: 0, treo: false
    };
    MP.job.push(j);
    ghiNk("", "M01", j.id + " vào xưởng — " + j.ten);
    return j;
  }

  function nhip() {
    if (!MP || !MP.chay) return;

    // đèn kho tắt dần
    Object.keys(MP.nhay).forEach(function (k) {
      MP.nhay[k]--; if (MP.nhay[k] <= 0) delete MP.nhay[k];
    });

    // thả việc mới
    if (MP.job.length < 4 && Math.random() < 0.5) themJob();

    // đẩy từng job một bước
    for (var i = MP.job.length - 1; i >= 0; i--) {
      var j = MP.job[i];
      if (j.treo) continue;

      j.vt++;
      if (j.vt >= DUONG.length) {           // hết đường
        MP.job.splice(i, 1);
        continue;
      }
      var may = DUONG[j.vt];

      // máy này gọi kho nào thì nháy đèn kho đó
      (GOI_KHO[may] || []).forEach(function (k) { MP.nhay[k] = 2; });

      if (may === "M03" && j.muc === 3) {
        ghiNk("chan", "M03", j.id + " CHẶN — mức 3, không bao giờ tự chạy");
        MP.dem.chan++;
        MP.job.splice(i, 1);
        continue;
      }

      if (may === "M13") {
        if (Math.random() < 0.3 && j.tra < 3) {   // trượt kiểm → đẩy ngược
          j.tra++;
          j.vt = DUONG.indexOf("M12") - 1;        // -1 vì nhịp sau sẽ +1
          MP.dem.tra++;
          ghiNk("tra", "M13", j.id + " TRẢ VỀ M12 (lần " + j.tra + ") — thiếu chứng cứ");
          continue;
        }
        if (j.tra >= 3) {
          ghiNk("tra", "M13", j.id + " trả về lần 3 — dừng, hỏi người");
          j.treo = true;
          MP.cho.push({ j: j, vi: "M13", ly: "trả về 3 lần" });
          continue;
        }
        ghiNk("dat", "M13", j.id + " ĐẠT — sáu phép kiểm qua hết");
        continue;
      }

      if (may === "M14" && j.muc >= 2) {
        j.treo = true;
        MP.cho.push({ j: j, vi: "M14", ly: "mức " + j.muc + " — chờ người duyệt" });
        ghiNk("tra", "M14", j.id + " DỪNG ở cổng duyệt — mức " + j.muc);
        continue;
      }

      if (may === "M15") ghiNk("", "M15", j.id + " thực thi thật — có biên nhận");
      if (may === "M18") {
        MP.dem.hoc++;
        MP.dem.xong++;
        ghiNk("hoc", "M18", j.id + " rút BÀI HỌC → ghi ngược vào M09");
      }
    }

    veSan();
    MP.dong = setTimeout(nhip, MP.nhip);
  }

  function duyet(k, cho) {
    var c = MP.cho[k];
    if (!c) return;
    MP.cho.splice(k, 1);
    c.j.treo = false;
    if (cho) {
      ghiNk("dat", c.vi, c.j.id + " ĐƯỢC DUYỆT — sang M15 thực thi");
    } else {
      c.j.vt = DUONG.indexOf("M12") - 1;
      c.j.tra = 0;
      MP.dem.tra++;
      ghiNk("tra", c.vi, c.j.id + " TRẢ LẠI — ghi chú của người vào M18 làm bài học");
    }
    veSan();
  }

  /* ── vẽ sàn ─────────────────────────────────────────── */
  var elSan, elNk, elCho, elDem;

  function veSan() {
    if (!elSan) return;
    var oMay = {};
    MP.job.forEach(function (j) {
      var m = DUONG[j.vt];
      if (!m) return;
      oMay[m] = (oMay[m] || 0) + 1;
    });

    elSan.querySelectorAll(".o-may").forEach(function (o) {
      var id = o.dataset.may;
      var n = oMay[id] || 0;
      var treo = MP.cho.some(function (c) { return c.vi === id; });
      o.dataset.chay = (n > 0 || MP.nhay[id]) ? "1" : "0";
      o.dataset.treo = treo ? "1" : "0";
      var d = o.querySelector(".om-dem");
      if (n > 0) { d.hidden = false; d.textContent = n; } else { d.hidden = true; }
    });

    elDem.innerHTML =
      "<span>xong <b>" + MP.dem.xong + "</b></span>" +
      "<span>trả về <b>" + MP.dem.tra + "</b></span>" +
      "<span>chặn <b>" + MP.dem.chan + "</b></span>" +
      "<span>bài học <b>" + MP.dem.hoc + "</b></span>" +
      "<span>đang chạy <b>" + MP.job.filter(function (j) { return !j.treo; }).length + "</b></span>";

    // hàng chờ
    elCho.hidden = MP.cho.length === 0;
    if (MP.cho.length) {
      var ds = elCho.querySelector(".cho-ds");
      ds.innerHTML = "";
      MP.cho.forEach(function (c, i) {
        var o = el("div", "cho-o");
        o.innerHTML = '<span class="j">' + esc(c.j.id) + '</span>' +
          '<span class="t">' + esc(c.j.ten) + '</span>' +
          '<span class="m">' + esc(c.vi) + " · " + esc(c.ly) + "</span>";
        var b1 = el("button", "nut", "Duyệt");
        b1.type = "button";
        b1.addEventListener("click", function () { duyet(i, true); });
        var b2 = el("button", "nut-phu", "Trả lại");
        b2.type = "button";
        b2.addEventListener("click", function () { duyet(i, false); });
        o.appendChild(b1); o.appendChild(b2);
        ds.appendChild(o);
      });
    }

    // nhật ký
    elNk.innerHTML = "";
    if (!MP.nk.length) {
      elNk.appendChild(el("div", "nk-trong", "Chưa có gì chạy. Bấm “Chạy dây chuyền”."));
      return;
    }
    MP.nk.forEach(function (d) {
      var r = el("div", "nk-d");
      r.dataset.loai = d.loai || "";
      r.innerHTML = '<span class="nk-t">' + esc(d.t) + '</span><span class="nk-m">' +
        esc(d.m) + '</span><span class="nk-x">' + esc(d.x) + "</span>";
      elNk.appendChild(r);
    });
  }

  function trangSan() {
    tieu.textContent = "Sàn máy";
    phu.textContent = "18 máy · 4 khu · 2 vòng đẩy ngược";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML =
      "Đây là <b>toàn bộ công xưởng đang chạy</b>. Việc vào ở M01, đi hết dây, " +
      "và ra ở M18. Bấm vào máy nào cũng mở được hồ sơ đủ 10 trường của máy đó." +
      '<span class="vn"><b>Hai chỗ đáng nhìn nhất, vì chúng là thứ biến chuỗi bước ' +
      "thành dây chuyền thật:</b> M13 trượt kiểm thì <b>đẩy ngược về M12</b> chứ không " +
      "trả về đầu dây; và M14 gặp việc mức 2 trở lên thì <b>dừng hẳn chờ bạn bấm duyệt</b>. " +
      "Việc mức 3 bị M03 chặn ngay từ cổng, không chạy bước nào.</span>";
    than.appendChild(gt);

    var kh = el("section", "khoi");

    // bảng điều khiển
    var dk = el("div", "dieukhien");
    var bChay = el("button", "nut");
    bChay.type = "button";
    var bXoa = el("button", "nut-phu");
    bXoa.type = "button";
    bXoa.innerHTML = svg(IC.xoa, 14) + " Dọn sàn";
    var bNhanh = el("button", "nut-phu");
    bNhanh.type = "button";

    function veNut() {
      bChay.innerHTML = svg(MP.chay ? IC.dung : IC.chay, 14) +
        (MP.chay ? " Tạm dừng" : " Chạy dây chuyền");
      bNhanh.textContent = MP.nhip === 1000 ? "Chậm" : MP.nhip === 620 ? "Thường" : "Nhanh";
    }
    bChay.addEventListener("click", function () {
      MP.chay = !MP.chay;
      veNut();
      if (MP.chay) nhip(); else clearTimeout(MP.dong);
    });
    bNhanh.addEventListener("click", function () {
      MP.nhip = MP.nhip === 1000 ? 620 : MP.nhip === 620 ? 300 : 1000;
      veNut();
    });
    bXoa.addEventListener("click", function () {
      var c = MP.chay, n = MP.nhip;
      clearTimeout(MP.dong);
      MP = moPhong(); MP.chay = c; MP.nhip = n;
      veNut(); veSan();
      if (c) nhip();
    });

    dk.appendChild(bChay);
    dk.appendChild(bNhanh);
    dk.appendChild(bXoa);
    elDem = el("div", "dk-so");
    dk.appendChild(elDem);
    kh.appendChild(dk);

    // sàn
    elSan = el("div", "san");
    var day = el("div", "day");
    X.KHU.forEach(function (k) {
      var o = el("div", "khu-o");
      o.style.setProperty("--kc", k.mau);
      o.appendChild(el("div", "khu-ten", k.ten));
      var hang = el("div", "khu-may");
      X.MAY.filter(function (m) { return m.khu === k.ma; }).forEach(function (m) {
        var a = el("a", "o-may");
        a.href = "#/may/" + m.id;
        a.dataset.may = m.id;
        a.style.setProperty("--kc", k.mau);
        a.title = m.ten + " — " + m.tom;
        a.innerHTML = '<span class="om-den"></span><span class="om-id">' + m.id +
          '</span><span class="om-ten">' + esc(m.ten) + '</span>' +
          '<span class="om-dem" hidden></span>';
        hang.appendChild(a);
      });
      o.appendChild(hang);
      day.appendChild(o);
    });
    elSan.appendChild(day);

    var vv = el("div", "vong-ve");
    vv.innerHTML = svg(IC.quay, 15) +
      "<span>Hai vòng đẩy ngược: <b>M13 → M12</b> khi trượt kiểm, và " +
      "<b>M18 → M09</b> khi rút được bài học. Không có hai vòng này thì đây chỉ là " +
      "một chuỗi bước, không phải dây chuyền.</span>";
    elSan.appendChild(vv);
    kh.appendChild(elSan);

    // hàng chờ duyệt
    elCho = el("div", "cho-d");
    elCho.hidden = true;
    var cd = el("div", "cho-dinh");
    cd.innerHTML = svg(IC.tay, 15) + "<span>Đang chờ bạn — M14 không tự cho qua bao giờ</span>";
    elCho.appendChild(cd);
    elCho.appendChild(el("div", "cho-ds"));
    kh.appendChild(elCho);

    // nhật ký
    elNk = el("div", "nk");
    kh.appendChild(elNk);

    than.appendChild(kh);

    if (!MP) MP = moPhong();
    veNut();
    veSan();
    if (MP.chay) { clearTimeout(MP.dong); nhip(); }
  }

  /* ═══════════════ sơ đồ toàn nhà máy ═══════════════
     Bản đồ một trang: việc đi đường nào, rẽ ở đâu, quay lại chỗ nào.
     Mọi ô có mã máy đều bấm được để mở hồ sơ đủ 10 trường. */
  function trangSoDo() {
    tieu.textContent = "Sơ đồ nhà máy";
    phu.textContent = "một trang · từ bạn giao việc tới bạn duyệt";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML =
      "Đây là <b>toàn bộ xưởng trên một sơ đồ</b>. Sàn máy bày 18 máy theo khu và cho " +
      "chạy mô phỏng — nó nói xưởng <i>đang làm gì</i>. Trang này nói xưởng " +
      "<i>được nối ra sao</i>." +
      '<span class="vn"><b>Ba chi tiết chỉ sơ đồ này mới thấy:</b> M04 được nạp từ ' +
      "<b>bên hông</b> chứ không nhận từ máy trước; sau M06 việc <b>tách thành ba dây " +
      "song song</b> rồi mới gộp; và M14 là <b>chỗ rẽ thật</b> — mức 0–1 đi thẳng, mức 2 " +
      "dừng chờ bạn rồi mới nhập lại dòng. Bấm ô nào cũng mở được hồ sơ máy đó.</span>";
    than.appendChild(gt);

    var kh = el("section", "khoi");
    var sd = el("div", "sd");

    function oMay(id) {
      var m = mayTheoId[id];
      var a = el("a", "sd-o");
      a.dataset.k = "may";
      a.href = "#/may/" + id;
      a.title = m ? m.tom : "";
      a.innerHTML = '<span class="sd-id">' + id + " · " + esc(m ? m.en : "") + "</span>" +
        '<span class="sd-ten">' + esc(m ? m.ten : id) + "</span>";
      return a;
    }
    function noi() { return el("div", "sd-noi"); }

    X.SO_DO.forEach(function (b, i) {
      if (i) sd.appendChild(noi());

      if (b.k === "nguoi") {
        var n = el("div", "sd-o");
        n.dataset.k = "nguoi";
        n.title = b.y || "";
        n.innerHTML = '<span class="sd-ten">' + esc(b.ten) + '</span><span class="sd-phu">' +
          esc(b.phu) + "</span>";
        sd.appendChild(n);
        return;
      }

      if (b.k === "may") {
        if (!b.nap) { sd.appendChild(oMay(b.may)); return; }
        var hang = el("div", "sd-hang");
        hang.appendChild(oMay(b.may));
        var nap = el("div", "sd-nap");
        b.nap.forEach(function (x) {
          var a = el("a");
          a.href = "#/may/" + x.may;
          a.title = mayTheoId[x.may] ? mayTheoId[x.may].tom : "";
          a.innerHTML = "<b>" + esc(x.ten) + "</b><i>" + esc(x.phu) + "</i>";
          nap.appendChild(a);
        });
        hang.appendChild(nap);
        sd.appendChild(hang);
        return;
      }

      if (b.k === "chia" || b.k === "toa") {
        sd.appendChild(el("div", "sd-nhan", b.nhan));
        var ba = el("div", "sd-ba");
        b.o.forEach(function (x) {
          var e;
          // ô tổ thợ không có mã máy — nó dẫn sang trang tổ, không sang hồ sơ máy
          var den = x.di || (x.may ? "#/may/" + x.may : (x.to ? "#/to" : null));
          if (den) { e = el("a", "sd-o"); e.href = den; }
          else e = el("div", "sd-o");
          e.dataset.k = b.k === "chia" ? "to" : "ve";
          e.innerHTML = (x.to ? '<span class="sd-id">' + x.to + "</span>" : "") +
            '<span class="sd-ten">' + esc(x.ten) + '</span><span class="sd-phu">' +
            esc(x.phu) + "</span>";
          ba.appendChild(e);
        });
        sd.appendChild(ba);
        /* Máy làm nên bước này mà không có ô riêng — chúng là kho được
           gọi tới, không phải trạm việc đi qua. Hiện thành chip nhỏ để
           không ai tưởng sơ đồ bỏ sót chúng. */
        if (b.qua) {
          var chip = el("div", "sd-qua");
          chip.appendChild(el("span", "sd-qua-nhan", "Hai máy đứng sau bước này"));
          b.qua.forEach(function (id) {
            var m = mayTheoId[id];
            var a = el("a");
            a.href = "#/may/" + id;
            a.title = m ? m.tom : "";
            a.innerHTML = "<b>" + id + "</b> " + esc(m ? m.ten : "");
            chip.appendChild(a);
          });
          sd.appendChild(chip);
        }
        // khối "toả" có lời riêng ở dải vòng lặp cuối trang — đừng in hai lần
        if (b.y && b.k === "chia") sd.appendChild(el("p", "sd-y", b.y));
        return;
      }

      if (b.k === "gop") {
        sd.appendChild(el("div", "sd-nhan", b.nhan));
        return;
      }

      if (b.k === "kho") {
        var k = el("a", "sd-o");
        k.dataset.k = "kho";
        k.href = b.di;
        k.title = b.y || "";
        k.innerHTML = '<span class="sd-id">' + esc(b.phu) + '</span><span class="sd-ten">' +
          esc(b.ten) + "</span>";
        sd.appendChild(k);
        return;
      }

      if (b.k === "quyet") {
        var m = mayTheoId[b.may];
        var q = el("div", "sd-quyet");
        q.innerHTML =
          '<span class="sd-id">' + b.may + " · " + esc(m ? m.en : "") + "</span>" +
          '<span class="sd-ten">' + esc(m ? m.ten : "") + "?</span>" +
          '<div class="sd-re"><div class="khong"><b>KHÔNG</b><span>' + esc(b.khong) +
          "</span></div>" +
          '<div class="co"><b>CÓ</b><span>' + esc(b.co) + "</span></div></div>";
        sd.appendChild(q);
        if (b.y) sd.appendChild(el("p", "sd-y", b.y));
        return;
      }
    });

    var cuoi = X.SO_DO[X.SO_DO.length - 1];
    if (cuoi && cuoi.y && cuoi.k === "toa") {
      var v = el("div", "sd-vong");
      v.innerHTML = svg(IC.quay, 16) + "<span>" + esc(cuoi.y) + "</span>";
      sd.appendChild(v);
    }

    kh.appendChild(sd);
    than.appendChild(kh);
  }

  /* ═══════════════ 18 máy ═══════════════ */
  function trangMay(moId) {
    tieu.textContent = "18 máy";
    phu.textContent = "mỗi máy đủ 10 trường";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML =
      "Bản phác viết đủ spec cho đúng một máy (S004 Kiểm chứng tuyên bố) rồi để ngỏ " +
      "phần còn lại. Ở đây <b>cả 18 máy đều được áp đủ 10 trường</b> theo mẫu đó: " +
      "mục đích · vào · ra · luật · dụng cụ · lỗi · chuyển bước · khi nào hỏi người · " +
      "nhật ký ghi gì." +
      '<span class="vn"><b>Ba thứ đừng trộn:</b> <b>máy</b> làm một chức năng, ' +
      "<b>dây chuyền</b> quyết định thứ tự máy chạy, <b>tổ</b> là người cầm máy. " +
      "Trộn ba thứ này là lỗi hay gặp nhất khi đọc sơ đồ kiểu này.</span>";
    than.appendChild(gt);

    X.KHU.forEach(function (k) {
      var ds = X.MAY.filter(function (m) { return m.khu === k.ma; });
      var kh = el("section", "khoi");
      var d = el("div", "khoi-dinh");
      d.innerHTML = "<h2>" + esc(k.ten) + '</h2><span class="khoi-n">' + ds.length + " máy</span>";
      d.style.borderTop = "3px solid " + k.mau;
      kh.appendChild(d);
      var p = el("p", "dc-y");
      p.style.padding = "0 18px";
      p.textContent = k.y;
      kh.appendChild(p);

      var luoi = el("div", "luoi-may");
      ds.forEach(function (m) {
        var a = el("a", "tm");
        a.href = "#/may/" + m.id;
        a.style.setProperty("--kc", k.mau);
        var the = "";
        if (m.treo) the += '<span class="the the-treo">có thể treo chờ người</span>';
        if (m.vong) the += '<span class="the the-vong">đẩy ngược → ' + m.vong + "</span>";
        a.innerHTML =
          '<div class="tm-dinh"><span class="tm-id">' + m.id + '</span>' +
          '<span class="tm-en">' + esc(m.en) + "</span></div>" +
          "<h3>" + esc(m.ten) + "</h3><p>" + esc(m.tom) + "</p>" +
          (the ? '<div class="tm-the">' + the + "</div>" : "");
        luoi.appendChild(a);
      });
      kh.appendChild(luoi);
      than.appendChild(kh);
    });

    if (moId) moMay(moId);
  }

  /* ── ngăn kéo hồ sơ máy ─────────────────────────────── */
  var hoso = document.getElementById("hoso");
  var scrim = document.getElementById("scrim");

  function dongHoso() {
    hoso.dataset.open = "0";
    scrim.dataset.open = "0";
    if (/^#\/may\//.test(location.hash)) location.hash = "#/may";
  }
  document.getElementById("hosoDong").addEventListener("click", dongHoso);
  scrim.addEventListener("click", dongHoso);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && hoso.dataset.open === "1") dongHoso();
  });

  function moMay(id) {
    var m = mayTheoId[id];
    if (!m) return;
    var k = khuTheoMa[m.khu];

    var top = document.getElementById("hosoTop");
    top.style.setProperty("--kc", k.mau);
    top.querySelector(".hoso-tren").textContent = m.id + " · " + k.ten;
    top.querySelector("h2").textContent = m.ten;
    top.querySelector(".en").textContent = m.en;

    var b = document.getElementById("hosoBody");
    b.innerHTML = "";
    b.style.setProperty("--kc", k.mau);

    function muc(h, noi) {
      var s = el("div", "hs");
      s.appendChild(el("div", "hs-h", h));
      s.appendChild(noi);
      b.appendChild(s);
    }

    muc("Mục đích", el("p", "hs-p", m.tom));

    var boi = el("p", "hs-boi");
    boi.textContent = m.boi;
    muc("Vì sao cần máy này", boi);

    var vr = el("div", "hs-vr");
    vr.innerHTML =
      '<div class="hs-o"><span>Đầu vào</span><p>' + esc(m.vao) + "</p></div>" +
      '<div class="hs-o"><span>Đầu ra</span><p>' + esc(m.ra) + "</p></div>";
    muc("Vào — ra", vr);

    var ul = el("ul", "hs-ds");
    m.luat.forEach(function (l) { ul.appendChild(el("li", null, l)); });
    muc("Luật xử lý", ul);

    var cu = el("div", "hs-cu");
    m.cu.forEach(function (c) { cu.appendChild(el("span", null, c)); });
    muc("Dụng cụ được phép dùng", cu);

    var vr2 = el("div", "hs-vr");
    vr2.innerHTML =
      '<div class="hs-o"><span>Điều kiện lỗi</span><p>' + esc(m.loi) + "</p></div>" +
      '<div class="hs-o"><span>Chuyển bước</span><p>' + esc(m.chuyen) + "</p></div>" +
      '<div class="hs-o"><span>Khi nào hỏi người</span><p>' + esc(m.hoi) + "</p></div>" +
      '<div class="hs-o"><span>Nhật ký ghi gì</span><p>' + esc(m.log) + "</p></div>";
    muc("Lỗi · chuyển bước · hỏi người · nhật ký", vr2);

    hoso.dataset.open = "1";
    scrim.dataset.open = "1";
    b.scrollTop = 0;
  }

  /* ═══════════════ bốn tầng ═══════════════ */
  function trangTang() {
    tieu.textContent = "Bốn tầng";
    phu.textContent = "model chỉ là tầng dưới cùng";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML =
      "Ý cốt lõi của bản phác: <b>đừng nghĩ “tôi phải train lại Claude hay GPT”</b>. " +
      "Model là động cơ — thứ dễ thay nhất. Cái làm nên công xưởng nằm ở ba tầng trên nó." +
      '<span class="vn">Hệ quả thực tế: <b>trí nhớ, kỹ năng và quy trình là của bạn</b>, ' +
      "model là thợ có thể đổi. Grok hay model mới ra thì cắm thêm vào, không phải xây lại.</span>";
    than.appendChild(gt);

    var kh = el("section", "khoi");
    X.TANG.slice().reverse().forEach(function (t) {
      var o = el("div", "tang");
      o.style.setProperty("--tc", t.mau);
      o.innerHTML =
        '<div class="tang-so">' + t.so + "</div>" +
        '<div class="tang-noi"><div class="tang-dinh"><h3>' + esc(t.ten) + "</h3>" +
        '<span class="tang-gom">' + esc(t.gom) + "</span></div><p>" + esc(t.y) + "</p></div>";
      kh.appendChild(o);
    });
    than.appendChild(kh);
  }

  /* ═══════════════ dây chuyền ═══════════════ */
  function trangDay() {
    tieu.textContent = "Dây chuyền";
    phu.textContent = X.DAY.length + " dây";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML =
      "Dây chuyền <b>không phải một máy</b>. Nó là thứ tự các máy phải chạy — " +
      "băng chuyền nối nhiều máy lại." +
      '<span class="vn">Ô <b>viền lục</b> là bước dùng một kỹ năng cụ thể. ' +
      "Ô gạch ngang là bước do tổ hoặc người làm, không có máy nào chạy thay được.</span>";
    than.appendChild(gt);

    var kh = el("section", "khoi");
    X.DAY.forEach(function (d) {
      var o = el("div", "dc");
      var h = el("div", "dc-dinh");
      h.innerHTML = '<span class="dc-id">' + d.id + "</span><h3>" + esc(d.ten) + "</h3>";
      o.appendChild(h);
      o.appendChild(el("p", "dc-y", d.y));
      var bs = el("div", "dc-buoc");
      d.buoc.forEach(function (b) {
        var r = el("div", "dc-b");
        if (b[0] !== "—") r.dataset.kn = "1";
        var kn = knTheoId[b[0]];
        r.innerHTML = '<span class="dc-n">' + esc(b[0]) + '</span><span class="dc-t">' +
          esc(b[1]) + (kn ? " <span style=\"color:var(--fg-3)\">— " + esc(kn.ten) + "</span>" : "") +
          "</span>";
        bs.appendChild(r);
      });
      o.appendChild(bs);
      kh.appendChild(o);
    });
    than.appendChild(kh);
  }

  /* ═══════════════ tổ thợ & kỹ năng ═══════════════ */
  function trangTo() {
    tieu.textContent = "Tổ thợ & kỹ năng";
    phu.textContent = X.TO.length + " tổ · " + X.KY_NANG.length + " kỹ năng";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML =
      "<b>Kỹ năng là máy. Tổ là người vận hành máy đó.</b> Một chatbot biết tất cả thì " +
      "không kiểm soát được; chia thành tổ có nghề và có quyền riêng thì hỏng chỗ nào " +
      "biết chỗ đó." +
      '<span class="vn"><b>Chú ý cột quyền.</b> Tổ nghiên cứu cố ý KHÔNG có quyền ghi, ' +
      "và tổ kiểm chỉ đọc — tổ chấm mà sửa được thứ mình chấm thì không còn là chấm nữa. " +
      "Chỉ tổ vận hành có quyền xoá, và chỉ nhận việc đã qua cổng duyệt M14.</span>";
    than.appendChild(gt);

    var kh = el("section", "khoi");
    kh.appendChild((function () {
      var d = el("div", "khoi-dinh");
      d.innerHTML = "<h2>Tổ thợ</h2><span class=\"khoi-n\">" + X.TO.length + " tổ</span>";
      return d;
    })());
    var luoi = el("div", "luoi-to");
    X.TO.forEach(function (t) {
      var o = el("div", "oto");
      var kn = t.kn.length
        ? t.kn.map(function (s) { return '<span class="q" data-co="1">' + s + "</span>"; }).join("")
        : '<span class="q">không cầm máy</span>';
      o.innerHTML =
        '<div class="oto-dinh"><span class="oto-id">' + t.id + "</span><h3>" + esc(t.ten) + "</h3></div>" +
        '<p class="oto-vai">' + esc(t.vai) + "</p>" +
        '<div class="quyen">' + kn + "</div>" +
        '<div class="quyen">' +
          '<span class="q" data-co="' + (t.doc ? 1 : 0) + '">đọc</span>' +
          '<span class="q" data-co="' + (t.ghi ? 1 : 0) + '">ghi</span>' +
          '<span class="q" data-co="' + (t.xoa ? 1 : 0) + '">xoá</span>' +
          '<span class="q">' + esc(t.may) + "</span>" +
        "</div>" +
        '<p class="oto-y">' + esc(t.y) + "</p>";
      luoi.appendChild(o);
    });
    kh.appendChild(luoi);
    than.appendChild(kh);

    var kh2 = el("section", "khoi");
    var d2 = el("div", "khoi-dinh");
    d2.innerHTML = "<h2>Kỹ năng</h2><span class=\"khoi-n\">" + X.KY_NANG.length + " máy chuyên dụng</span>";
    kh2.appendChild(d2);
    var luoi2 = el("div", "luoi-may");
    X.KY_NANG.forEach(function (s) {
      var o = el("div", "tm");
      o.style.setProperty("--kc", "#3F9D6D");
      o.innerHTML =
        '<div class="tm-dinh"><span class="tm-id">' + s.id + "</span></div>" +
        "<h3>" + esc(s.ten) + "</h3>" +
        '<p><b style="color:var(--fg-3)">vào</b> ' + esc(s.vao) +
        ' &nbsp;<b style="color:var(--fg-3)">ra</b> ' + esc(s.ra) + "</p>" +
        '<p style="margin-top:8px;color:var(--fg-3)">' + esc(s.y) + "</p>";
      luoi2.appendChild(o);
    });
    kh2.appendChild(luoi2);
    than.appendChild(kh2);
  }

  /* ═══════════════ bốn mức duyệt ═══════════════ */
  function trangDuyet() {
    tieu.textContent = "Bốn mức duyệt";
    phu.textContent = "ranh giới giữa trợ lý và hệ thống tự chạy";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML =
      "Đây là chỗ quyết định hệ thống này là <b>trợ lý</b> hay <b>hệ thống tự chạy</b>. " +
      "Không có bảng mức này thì mọi lớp phía trên chỉ là trang trí." +
      '<span class="vn"><b>Hai luật cứu nhiều nhất:</b> mức lấy theo hành động ' +
      "<b>nặng nhất</b> mà việc có thể chạm tới, không phải hành động đầu tiên. " +
      "Và hành động chưa xếp mức thì <b>mặc định là mức 2</b>, không phải mức 0 — " +
      "mặc định sai hướng là cách một hệ thống an toàn trở nên nguy hiểm.</span>";
    than.appendChild(gt);

    var kh = el("section", "khoi");
    X.MUC.forEach(function (m) {
      var o = el("div", "mucd");
      o.style.setProperty("--mc", m.mau);
      o.innerHTML =
        '<div class="mucd-so">' + m.m + "</div>" +
        '<div class="mucd-noi"><h3>' + esc(m.ten) + "</h3><p>" + esc(m.y) + "</p>" +
        '<div class="mucd-vd">' + m.vd.map(function (v) {
          return "<span>" + esc(v) + "</span>";
        }).join("") + "</div></div>";
      kh.appendChild(o);
    });
    than.appendChild(kh);
  }

  /* ═══════════════ bộ chọn động cơ ═══════════════ */
  function trangDongCo() {
    tieu.textContent = "Bộ chọn động cơ";
    phu.textContent = "M07 · Model Gateway";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML =
      "Ý quan trọng nhất của cả bản thiết kế: <b>đừng khoá vào một hãng</b>. " +
      "Mỗi bước được giao cho động cơ mạnh ở đúng việc đó — và việc rẻ, lặp lại thì " +
      "đẩy xuống model nhỏ thay vì đốt tiền cho model đắt." +
      '<span class="vn">Chọn một việc bên dưới để xem M07 định tuyến ra sao và ' +
      "<b>vì sao</b> nó chọn động cơ đó cho từng bước.</span>";
    than.appendChild(gt);

    var kh = el("section", "khoi");

    var cb = el("div", "canhbao-key");
    cb.innerHTML = svg(IC.tay, 15) +
      " <b>Đây là bảng định tuyến chạy tại chỗ, không phải lời gọi API thật.</b> " +
      "Trang này nằm trên GitHub Pages công khai — nhúng API key vào đây là làm lộ key, " +
      "không có cách nào giấu. Muốn gọi model thật thì cho chạy <b>server-side trong " +
      "GitHub Actions</b> với key trong repo Secrets, sinh ra file tĩnh rồi commit; " +
      "trình duyệt chỉ đọc file đó. Bốn cung khác trong hệ sinh thái này đang đi đúng đường ấy.";
    kh.appendChild(cb);

    var gw = el("div", "gw");
    var chon = el("div", "gw-viec");
    var kq = el("div", "gw-kq");

    function ve(i) {
      var v = X.VIEC_MAU[i];
      chon.querySelectorAll(".gw-v").forEach(function (b, k) {
        b.setAttribute("aria-pressed", k === i ? "true" : "false");
      });
      kq.innerHTML = "";
      var top = el("div", "gw-top");
      top.innerHTML = "<b>" + esc(v.ten) + "</b>" +
        '<span class="the">' + esc(v.loai) + "</span>" +
        '<span class="the">mức duyệt ' + v.muc + "</span>" +
        (v.day !== "—" ? '<span class="the">dây ' + v.day + "</span>" : "");
      kq.appendChild(top);

      if (v.muc === 3) {
        var ch = el("div", "gw-chan");
        ch.innerHTML = "<b>M03 chặn ngay tại cổng kiểm quyền.</b> Mức 3 là “không bao giờ " +
          "tự làm” — không bước nào chạy, không token nào bị tiêu. Đây là lý do cổng " +
          "kiểm quyền đứng thứ ba chứ không đứng cuối.";
        kq.appendChild(ch);
        return;
      }

      v.buoc.forEach(function (b) {
        var d = dcTheoMa[b.d];
        var r = el("div", "gw-b");
        r.innerHTML = '<span class="gw-n">' + esc(b.m) + "</span>" +
          (d ? '<span class="gw-dc" style="--dcc:' + d.mau + '"><i></i>' + esc(d.ten) + "</span>"
             : '<span class="gw-n">—</span>') +
          '<span class="gw-ly">' + esc(b.ly) + "</span>";
        kq.appendChild(r);
      });

      if (v.muc >= 2) {
        var w = el("div", "gw-chan");
        w.style.background = "var(--vang-t)";
        w.style.color = "#E0C56B";
        w.innerHTML = "<b>Mức " + v.muc + " — dừng ở M14.</b> Các bước trên vẫn chạy và " +
          "chuẩn bị đầy đủ, nhưng hành động thật chỉ xảy ra sau khi người bấm duyệt. " +
          "Đó là ranh giới M15 giữ: <b>soạn thư không phải gửi thư</b>.";
        kq.appendChild(w);
      }
    }

    X.VIEC_MAU.forEach(function (v, i) {
      var b = el("button", "gw-v", v.ten);
      b.type = "button";
      b.setAttribute("aria-pressed", "false");
      b.addEventListener("click", function () { ve(i); });
      chon.appendChild(b);
    });
    gw.appendChild(chon);
    gw.appendChild(kq);
    kh.appendChild(gw);
    than.appendChild(kh);

    // bảng động cơ
    var kh2 = el("section", "khoi");
    var d2 = el("div", "khoi-dinh");
    d2.innerHTML = "<h2>Động cơ trong xưởng</h2><span class=\"khoi-n\">" +
      X.DONG_CO.length + " loại</span>";
    kh2.appendChild(d2);
    var luoi = el("div", "luoi-may");
    X.DONG_CO.forEach(function (d) {
      var o = el("div", "tm");
      o.style.setProperty("--kc", d.mau);
      o.innerHTML = "<h3>" + esc(d.ten) + "</h3><div class=\"tm-the\">" +
        d.manh.map(function (m) { return '<span class="the">' + esc(m) + "</span>"; }).join("") +
        "</div>";
      luoi.appendChild(o);
    });
    kh2.appendChild(luoi);
    than.appendChild(kh2);

    ve(0);
  }

  /* ═══════════════ lộ trình ═══════════════ */
  function trangLoTrinh() {
    tieu.textContent = "Lộ trình dựng";
    phu.textContent = "V1 → V2 → V3";
    than.innerHTML = "";

    var gt = el("div", "giaithich");
    gt.innerHTML =
      "<b>Đừng dựng 100 máy ngay.</b> Bản phác nói thẳng chỗ này, và nó đúng: " +
      "cái khó không phải model, mà là <b>định nghĩa quy trình</b> — mô tả việc đủ rõ, " +
      "tách được bước, biết mỗi bước vào gì ra gì, hỏng thì xử lý sao, chỗ nào cần người duyệt." +
      '<span class="vn">Mua model mạnh chỉ là mua động cơ tốt. Thứ biến nó thành ' +
      "công xưởng là những bản thiết kế bên dưới.</span>";
    than.appendChild(gt);

    var kh = el("section", "khoi");
    X.CHANG.forEach(function (c) {
      var o = el("div", "chang");
      o.innerHTML =
        '<div class="chang-v">' + c.v + "</div>" +
        '<div class="chang-noi"><h3>' + esc(c.ten) + "</h3><p>" + esc(c.y) + "</p>" +
        '<div class="chang-ds">' + c.viec.map(function (v) {
          return "<span>" + esc(v) + "</span>";
        }).join("") + "</div></div>";
      kh.appendChild(o);
    });
    than.appendChild(kh);

    var kh2 = el("section", "khoi");
    var d2 = el("div", "khoi-dinh");
    d2.innerHTML = "<h2>Cây thư mục hồ sơ</h2><span class=\"khoi-n\">" +
      X.THU_MUC.length + " thư mục</span>";
    kh2.appendChild(d2);
    var p = el("p", "dc-y");
    p.style.padding = "0 18px";
    p.textContent = "Toàn bộ trí tuệ vận hành của xưởng nằm trong những bản thiết kế này, " +
      "chứ không nằm riêng trong Claude hay ChatGPT. Đổi model thì thư mục này ở nguyên.";
    kh2.appendChild(p);
    var cay = el("div", "cay");
    X.THU_MUC.forEach(function (t) {
      var r = el("div", "cay-d");
      r.innerHTML = '<span class="cay-t">AI_FACTORY/' + esc(t[0]) + "/</span>" +
        '<span class="cay-y">' + esc(t[1]) + "</span>";
      cay.appendChild(r);
    });
    kh2.appendChild(cay);
    than.appendChild(kh2);
  }

  /* ═══════════════ định tuyến ═══════════════ */
  function dinhTuyen() {
    var h = location.hash || "#/san";
    var p = h.replace(/^#\/?/, "").split("/");

    if (MP && p[0] !== "san") { clearTimeout(MP.dong); elSan = null; }
    if (hoso.dataset.open === "1" && !(p[0] === "may" && p[1])) {
      hoso.dataset.open = "0"; scrim.dataset.open = "0";
    }

    sangBen("#/" + p[0]);
    document.getElementById("ben").dataset.mo = "0";

    if (p[0] === "may") {
      if (than.dataset.t === "may") { if (p[1]) moMay(p[1]); return; }
      than.dataset.t = "may";
      return trangMay(p[1]);
    }
    than.dataset.t = p[0];
    if (p[0] === "so-do") return trangSoDo();
    if (p[0] === "tang") return trangTang();
    if (p[0] === "day") return trangDay();
    if (p[0] === "to") return trangTo();
    if (p[0] === "duyet") return trangDuyet();
    if (p[0] === "dong-co") return trangDongCo();
    if (p[0] === "lo-trinh") return trangLoTrinh();
    than.dataset.t = "san";
    trangSan();
  }

  window.addEventListener("hashchange", dinhTuyen);
  document.getElementById("benMoNut").addEventListener("click", function () {
    var b = document.getElementById("ben");
    b.dataset.mo = b.dataset.mo === "1" ? "0" : "1";
  });

  dungBen();
  dinhTuyen();
})();
