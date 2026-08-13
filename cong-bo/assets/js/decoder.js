/* ═══════════════════════════════════════════════════════
   GIẢI MÃ LỜI GỌI — chạy hẳn trong trình duyệt.

   Dán vào một chuỗi calldata (0x…) của giao dịch Ethereum, trả về
   tên hàm và từng tham số đã đọc ra nghĩa.

   ── VÌ SAO TỰ VIẾT ────────────────────────────────────
   L2BEAT có sẵn tools-api.l2beat.com/api/decode, nhưng nó đang
   trả 500 (đã thử cả POST đúng dạng). Mà việc này vốn không cần
   máy chủ: bóc 4 byte đầu làm selector, tra tên hàm, rồi đọc
   tham số theo quy tắc mã hoá ABI — toàn bộ làm được tại chỗ.

   Chỉ một chỗ cần mạng: tra tên hàm từ selector. Dùng
   api.openchain.xyz (có CORS) và có bảng tra sẵn cho những hàm
   hay gặp, nên mất mạng vẫn đọc được phần lớn lời gọi thường.

   KHÔNG dùng 4byte.directory: nó không trả header CORS nên
   trình duyệt chặn thẳng.

   ── GIỚI HẠN ĐÃ BIẾT ──────────────────────────────────
   Đọc được: mọi kiểu tĩnh (uintN, intN, address, bool, bytesN)
   và kiểu động một tầng (string, bytes, mảng T[]). Tuple lồng
   nhau và mảng của tuple thì báo "chưa đọc được" chứ không đoán
   bừa — đọc sai một tham số còn tệ hơn nói thẳng là không đọc được.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  /* Selector của những hàm gặp nhiều nhất. Có bảng này thì phần
     lớn lời gọi thường đọc được ngay, không cần chờ mạng. */
  var SAN = {
    "0xa9059cbb": "transfer(address,uint256)",
    "0x23b872dd": "transferFrom(address,address,uint256)",
    "0x095ea7b3": "approve(address,uint256)",
    "0x70a08231": "balanceOf(address)",
    "0xdd62ed3e": "allowance(address,address)",
    "0x18160ddd": "totalSupply()",
    "0x313ce567": "decimals()",
    "0x06fdde03": "name()",
    "0x95d89b41": "symbol()",
    "0x40c10f19": "mint(address,uint256)",
    "0x42966c68": "burn(uint256)",
    "0x2e1a7d4d": "withdraw(uint256)",
    "0xd0e30db0": "deposit()",
    "0x3ccfd60b": "withdraw()",
    "0xf2fde38b": "transferOwnership(address)",
    "0x8da5cb5b": "owner()",
    "0x715018a6": "renounceOwnership()",
    "0x3659cfe6": "upgradeTo(address)",
    "0x4f1ef286": "upgradeToAndCall(address,bytes)",
    "0x5c60da1b": "implementation()",
    "0x1cff79cd": "execute(address,bytes)",
    "0xb61d27f6": "execute(address,uint256,bytes)",
    "0x2f2ff15d": "grantRole(bytes32,address)",
    "0xd547741f": "revokeRole(bytes32,address)",
    "0x91d14854": "hasRole(bytes32,address)",
    "0x38ed1739": "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
    "0x7ff36ab5": "swapExactETHForTokens(uint256,address[],address,uint256)",
    "0x022c0d9f": "swap(uint256,uint256,address,bytes)",
    "0xe8e33700": "addLiquidity(address,address,uint256,uint256,uint256,uint256,address,uint256)"
  };

  var CACHE = {};   /* selector → chữ ký, nhớ trong phiên */

  function la0x(s) { return /^0x[0-9a-fA-F]*$/.test(s); }

  /* ── tra tên hàm ──────────────────────────────────── */
  function traTen(sel) {
    if (SAN[sel]) return Promise.resolve({ ky: SAN[sel], tu: "bảng sẵn" });
    if (CACHE[sel]) return Promise.resolve({ ky: CACHE[sel], tu: "openchain.xyz" });
    return fetch("https://api.openchain.xyz/signature-database/v1/lookup?function=" +
      encodeURIComponent(sel) + "&filter=true")
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) {
        var ds = j && j.result && j.result.function && j.result.function[sel];
        if (!ds || !ds.length) return { ky: null, tu: null };
        CACHE[sel] = ds[0].name;
        return { ky: ds[0].name, tu: "openchain.xyz" };
      })
      .catch(function () { return { ky: null, tu: null, loi: true }; });
  }

  /* ── tách danh sách kiểu từ chữ ký ────────────────── */
  /* "swap(uint256,address[],(uint8,bytes))" → ["uint256","address[]","(uint8,bytes)"]
     Phải đếm ngoặc: cắt bừa theo dấu phẩy sẽ xé đôi tuple. */
  function tachKieu(ky) {
    var i = ky.indexOf("(");
    if (i === -1) return { ten: ky, kieu: [] };
    var ten = ky.slice(0, i);
    var than = ky.slice(i + 1, ky.lastIndexOf(")"));
    if (!than.trim()) return { ten: ten, kieu: [] };
    var ra = [], sau = 0, cur = "";
    for (var j = 0; j < than.length; j++) {
      var c = than[j];
      if (c === "(") sau++;
      if (c === ")") sau--;
      if (c === "," && sau === 0) { ra.push(cur.trim()); cur = ""; continue; }
      cur += c;
    }
    if (cur.trim()) ra.push(cur.trim());
    return { ten: ten, kieu: ra };
  }

  /* ── đọc một từ 32 byte ───────────────────────────── */
  function tu(hex, i) { return hex.slice(i * 64, i * 64 + 64); }
  function soTu(h) { return BigInt("0x" + (h || "0")); }

  function docTinh(kieu, w) {
    if (kieu === "address") return "0x" + w.slice(24);
    if (kieu === "bool") return soTu(w) ? "true" : "false";
    if (/^bytes([0-9]+)$/.test(kieu)) {
      var n = parseInt(kieu.slice(5), 10);
      return "0x" + w.slice(0, n * 2);
    }
    if (/^uint/.test(kieu)) return soTu(w).toString();
    if (/^int/.test(kieu)) {
      var v = soTu(w);
      var nguong = 1n << 255n;
      return (v >= nguong ? v - (1n << 256n) : v).toString();
    }
    return null;
  }

  var DONG = /^(string|bytes)$/;

  function docDong(kieu, hex, off) {
    /* off tính bằng byte từ đầu vùng tham số */
    var i = off / 32;
    var len = Number(soTu(tu(hex, i)));
    var dat = hex.slice((i + 1) * 64, (i + 1) * 64 + len * 2);
    if (kieu === "bytes") return { v: "0x" + dat, ghi: len + " byte" };
    /* string: giải UTF-8 */
    try {
      var b = new Uint8Array(len);
      for (var k = 0; k < len; k++) b[k] = parseInt(dat.substr(k * 2, 2), 16);
      return { v: new TextDecoder().decode(b), ghi: len + " byte" };
    } catch (e) { return { v: "0x" + dat, ghi: len + " byte (không phải UTF-8)" }; }
  }

  function docMang(kieu, hex, off) {
    var base = kieu.slice(0, kieu.lastIndexOf("["));
    var i = off / 32;
    var n = Number(soTu(tu(hex, i)));
    if (n > 512) return { loi: "mảng khai " + n + " phần tử — quá dài, bỏ qua" };
    var ra = [];
    for (var k = 0; k < n; k++) {
      var w = tu(hex, i + 1 + k);
      var v = docTinh(base, w);
      ra.push(v === null ? "0x" + w : v);
    }
    return { v: ra, ghi: n + " phần tử" };
  }

  /* ── giải mã toàn bộ ──────────────────────────────── */
  function giaiMa(data) {
    data = String(data || "").trim();
    if (!data) return { loi: "Chưa dán gì vào." };
    if (!la0x(data)) return { loi: "Không phải chuỗi hex bắt đầu bằng 0x." };
    if (data.length < 10) return { loi: "Quá ngắn — cần ít nhất 4 byte selector (10 ký tự)." };
    if ((data.length - 2) % 2) return { loi: "Số ký tự lẻ — chuỗi hex phải chẵn." };

    var sel = data.slice(0, 10).toLowerCase();
    var than = data.slice(10);
    if (than.length % 64) {
      return { sel: sel, canhBao: "Phần tham số dài " + (than.length / 2) +
        " byte, không chia hết cho 32 — có thể bị cắt hoặc không phải lời gọi hàm chuẩn." };
    }
    return { sel: sel, than: than, soTu: than.length / 64 };
  }

  function docThamSo(ky, than) {
    var t = tachKieu(ky);
    var ra = [], viTri = 0;
    for (var i = 0; i < t.kieu.length; i++) {
      var k = t.kieu[i];
      var w = tu(than, viTri);
      var muc = { kieu: k, tho: "0x" + w };

      if (k.indexOf("(") === 0 || /\)\[/.test(k) || (k.indexOf("[") !== -1 && k.indexOf("(") !== -1)) {
        /* tuple, hoặc mảng của tuple */
        muc.v = null;
        muc.ghi = "chưa đọc được kiểu này";
      } else if (DONG.test(k)) {
        var o = Number(soTu(w));
        try { var d = docDong(k, than, o); muc.v = d.v; muc.ghi = d.ghi; }
        catch (e) { muc.v = null; muc.ghi = "không đọc được phần động"; }
      } else if (k.slice(-2) === "[]") {
        var o2 = Number(soTu(w));
        try {
          var m = docMang(k, than, o2);
          if (m.loi) { muc.v = null; muc.ghi = m.loi; }
          else { muc.v = m.v; muc.ghi = m.ghi; }
        } catch (e) { muc.v = null; muc.ghi = "không đọc được mảng"; }
      } else {
        var v = docTinh(k, w);
        muc.v = v;
        if (v === null) muc.ghi = "chưa đọc được kiểu này";
      }
      ra.push(muc);
      viTri++;
    }
    return { ten: t.ten, thamSo: ra };
  }

  window.CB_DECODE = {
    giaiMa: giaiMa,
    traTen: traTen,
    docThamSo: docThamSo,
    tachKieu: tachKieu,
    soHam: Object.keys(SAN).length
  };
})();
