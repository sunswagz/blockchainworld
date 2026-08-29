/* Vẽ THẬT mọi trang của buồng lái, trên ba mẫu. Không cần mạng, không
   cần runtime đang chạy, không cần trình duyệt.
 *
 *     node scripts/kiem-buong-lai.mjs
 *     node scripts/kiem-buong-lai.mjs --song     (lấy từ máy đang chạy)
 *     node scripts/kiem-buong-lai.mjs --ghi-mau  (chép lại mẫu từ máy sống)
 *     node scripts/kiem-buong-lai.mjs --in von   (in cây nút của một trang)
 *
 * VÌ SAO CẦN, và vì sao `node --check` không thay được:
 *
 * `ve()` của trang này BẮT mọi lỗi rồi thay cả thân trang bằng một ô báo
 * lỗi. Đó là thiết kế đúng — trang trắng im lặng còn tệ hơn. Nhưng hệ quả
 * là **một trang hỏng KHÔNG làm gì đỏ ở đâu cả**: runtime vẫn quét, vẫn
 * mở vị thế, vẫn ghi sổ; chỉ người vận hành là mất một tầng nhìn, và mất
 * trong lúc mọi phép kiểm khác đều xanh. Nên phép kiểm này chấm ba việc:
 * hàm vẽ có NÉM không, có ra RỖNG không, và có tự dựng ô báo lỗi không.
 *
 * BA mẫu, và mẫu thứ hai với thứ ba mới là chỗ bắt được lỗi:
 *
 *   đầy đủ   ảnh chụp máy sống — mọi trường có mặt
 *   RỖNG     `{}` — chưa quét lượt nào, hoặc runtime vừa bật
 *   NULL     mọi trường có mặt nhưng mang `null`
 *
 * Mẫu NULL canh đúng luật xương sống của cỗ máy này: **`None` KHÔNG phải
 * 0**. Trung Ương cố ý trả `null` cho cái chưa đo được, nên mọi chỗ trong
 * trang gọi `.toFixed()` thẳng lên một trường như thế là một trang hỏng
 * đang chờ đúng cái phút mà con số ấy chưa đo được — tức là phút đầu
 * tiên sau mỗi lần khởi động lại.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const GOC = join(dirname(fileURLToPath(import.meta.url)), "..");
const doi = process.argv.slice(2);
const co = (t) => doi.includes(t);
const IN = co("--in") ? doi[doi.indexOf("--in") + 1] : null;
const DUONG_MAU = join(GOC, "scripts/mau-buong-lai.json");

function Nut(ten) {
  return {
    tagName: ten, children: [], _txt: "", _attr: {},
    style: {}, dataset: {}, hidden: false, href: "",
    classList: {
      _s: new Set(),
      add(...c) { c.forEach((x) => x && this._s.add(x)); },
      toggle(c, v) { v ? this._s.add(c) : this._s.delete(c); },
      contains(c) { return this._s.has(c); },
    },
    appendChild(c) { this.children.push(c); return c; },
    replaceChildren(...c) { this.children = c.filter(Boolean); },
    setAttribute(k, v) { this._attr[k] = String(v); },
    getAttribute(k) {
      return Object.prototype.hasOwnProperty.call(this._attr, k)
        ? this._attr[k] : null;
    },
    removeAttribute(k) { delete this._attr[k]; },
    addEventListener() {}, closest() { return null; },
    // `querySelector` phải TÌM THẬT. Bản đầu trả `null` cho mọi lời gọi,
    // và dòng `hVon.querySelector("a").href = "/von"` ném ngay — một lỗi
    // của bộ kiểm, không phải của trang. Báo động giả thì người ta ngừng
    // tin cả bộ kiểm.
    querySelector(s) {
      const the = String(s).trim();
      const di = (n) => {
        for (const c of n.children || []) {
          if (c.tagName === the) return c;
          if (the[0] === "." && c.classList && c.classList._s.has(the.slice(1))) {
            return c;
          }
          const s2 = di(c);
          if (s2) return s2;
        }
        return null;
      };
      return di(this);
    },
    querySelectorAll() { return []; },
    // DOM thật nối `className` với `classList`; DOM giả thì không, nên
    // mọi lớp do `el(tag, "ten-lop")` đặt đều vô hình với `classList`.
    set className(v) {
      this._cls = String(v);
      this.classList._s = new Set(String(v).split(/\s+/).filter(Boolean));
    },
    get className() { return this._cls || ""; },
    set textContent(v) { this._txt = String(v); this.children = []; },
    get textContent() { return this._txt; },
    set innerHTML(v) { this._txt = String(v); },
    get innerHTML() { return this._txt; },
  };
}

const kho = {};
// DOM giả dựng SAU khi lấy xong dữ liệu: `fetch` giả đè lên đúng thứ mà
// chế độ --song cần để đi lấy dữ liệu, và `setInterval` giả làm hỏng
// `fetch` thật của Node (undici cần Timer có `.unref()`).
function dungDomGia() {
  const lay = (s) => {
    const id = String(s).replace(/^#/, "");
    return kho[id] || (kho[id] = Nut("div"));
  };
  globalThis.document = {
    createElement: Nut,
    createElementNS: (ns, t) => Nut(t),
    createDocumentFragment: () => Nut("#frag"),
    getElementById: lay,
    querySelector: lay,
    querySelectorAll: () => [],
    addEventListener: () => {},
  };
  globalThis.location = { pathname: "/", port: "5188", origin: "http://x" };
  globalThis.history = { pushState() {} };
  globalThis.window = { addEventListener() {}, scrollTo() {} };
  globalThis.fetch = () => Promise.resolve({
    ok: true, json: () => Promise.resolve({}),
  });
  globalThis.setInterval = () => 0;
  globalThis.setTimeout = () => 0;
}

async function layTrangThai() {
  if (co("--song") || co("--ghi-mau")) {
    const r = await fetch("http://127.0.0.1:5188/api/trang-thai");
    return r.json();
  }
  return JSON.parse(readFileSync(DUONG_MAU, "utf8"));
}

/* Mọi trường lá thành `null`, GIỮ NGUYÊN hình dạng. Mảng giữ đúng một
   phần tử: mảng rỗng thì phần lớn bảng thoát sớm ở nhánh "chưa có gì" và
   thân bảng — chỗ gọi `.toFixed()` — không bao giờ được chạy. */
function hoaNull(x) {
  if (Array.isArray(x)) return x.length ? [hoaNull(x[0])] : [];
  if (x && typeof x === "object") {
    const r = {};
    for (const k of Object.keys(x)) r[k] = hoaNull(x[k]);
    return r;
  }
  return null;
}

function dem(x) {
  return 1 + (x.children || []).reduce((a, c) => a + dem(c), 0);
}
function chu(x) {
  return ((x._txt || "") + " "
    + (x.children || []).map(chu).join(" ")).trim();
}
function inRa(x, d) {
  const t = (x._txt || "").trim();
  const c = [...(x.classList?._s ?? [])].join(".");
  if (t) console.log("  ".repeat(d) + (c ? `[${c}] ` : "") + t);
  else if (c) console.log("  ".repeat(d) + `[${c}]`);
  (x.children || []).forEach((y) => inRa(y, d + 1));
}

// Mở cái nắp của IIFE. Trang không mang móc kiểm thử nào trong mã sản
// xuất — đúng thế: một móc chỉ bộ kiểm dùng là một nhánh mà người dùng
// thật không bao giờ đi qua.
const NAP = "  globalThis._TRANG = TRANG; globalThis._ve = ve;"
  + " globalThis._datS = (d) => { S = d; };"
  + " globalThis._veMotDongCo = ve_mot_dong_co;\n})();";
const ma = readFileSync(join(GOC, "web/app.js"), "utf8");
if (!ma.includes("})();")) {
  console.error("  app.js không còn kết bằng `})();` — sửa NAP trong file này");
  process.exit(2);
}

const T = await layTrangThai();
if (co("--ghi-mau")) {
  writeFileSync(DUONG_MAU,
    JSON.stringify(T, null, 1).replace(/\n?$/, "\n"), "utf8");
  console.log("\n  đã ghi mẫu " + DUONG_MAU + "\n");
  process.exit(0);
}
dungDomGia();
new Function(ma.replace("})();", NAP))();

const MAU = [
  ["đầy đủ", T],
  ["RỖNG", {}],
  ["NULL", hoaNull(T)],
];

console.log("\n  Buồng lái Thị Bạc Ty — "
  + (co("--song") ? "máy đang chạy" : "mẫu trên đĩa") + "\n");
let loi = 0, xong = 0, tongNut = 0;
const TEN = Object.keys(globalThis._TRANG);
for (const [nhan, du] of MAU) {
  globalThis._datS(du);
  console.log("  ── mẫu " + nhan + " ───────────────────────────");
  for (const ten of TEN) {
    try {
      const r = globalThis._TRANG[ten]();
      const n = dem(r);
      tongNut += n;
      // Một trang vẽ ra ≤ 1 nút là một trang RỖNG — đúng cú pháp, không
      // ném, và cũng không nói gì. Vẫn là hỏng, chỉ là hỏng lặng lẽ.
      const rong = n <= 1;
      // "NaN"/"undefined" lọt ra mặt giấy là một con số bịa: người đọc
      // thấy một ô có chữ và tưởng đã đo được.
      const t = chu(r);
      const ban = /\bNaN\b|\bundefined\b|\[object Object\]/.exec(t);
      const ok = !rong && !ban;
      console.log("  " + (ok ? "OK   " : rong ? "TRỐNG" : "BẨN  ")
        + " " + ten.padEnd(11) + " " + String(n).padStart(5) + " nút"
        + (ban ? "  ← in ra «" + ban[0] + "»" : ""));
      ok ? xong++ : loi++;
      if (IN === ten && nhan === "đầy đủ") inRa(r, 2);
    } catch (e) {
      console.log("  NÉM   " + ten.padEnd(11) + " " + e.message);
      console.log(e.stack.split("\n").slice(1, 4).join("\n"));
      loi++;
    }
  }
}

// Trang mổ máy `/dong-co/<ma>` nhận mã từ URL. Mã LẠ phải ra một trang
// nói rõ là không có động cơ ấy, chứ không được ném — URL thì người gõ
// tay được, và một trang ném ở đây thành ô báo lỗi cho một chuyện hoàn
// toàn bình thường.
globalThis._datS(T);
{
  let ok = false, viCo = "";
  // Danh sách động cơ nằm ở `trungUong.cheTy`, KHÔNG ở gốc — bản đầu
  // đoán `T.dongCo` rồi in "mẫu không có động cơ nào để thử", tức là
  // nửa phép kiểm này im lặng không làm gì mà vẫn báo OK.
  const dc = ((T.trungUong || {}).cheTy) || [];
  const ma1 = Array.isArray(dc) && dc.length ? dc[0].ma : null;
  try {
    const la = globalThis._veMotDongCo("KHONG_CO_MA_NAY");
    ok = dem(la) > 1;
    if (ma1) {
      const that = globalThis._veMotDongCo(ma1);
      viCo = dem(that) > 1
        ? " · mã thật «" + ma1 + "» vẽ được"
        : " · mã THẬT ra rỗng";
      ok = ok && dem(that) > 1;
    } else {
      viCo = " · mẫu không có động cơ nào để thử mã thật";
    }
  } catch (e) {
    viCo = " · NÉM: " + e.message;
  }
  console.log("  " + (ok ? "OK   " : "LỖI  ") + " " + "mã-lạ".padEnd(11)
    + " " + (ok ? "mã lạ → vẫn có nội dung" : "mã lạ → TRỐNG hoặc NÉM") + viCo);
  ok ? xong++ : loi++;
}

// Khoá trang ĐỌC có thật trong ảnh chụp không.
//
// Trang lấy dữ liệu bằng `t.<khoá>` với `t = (S && S.trungUong) || {}`.
// Đổi tên một trường trong `anh_chup()` mà quên bên đọc thì `t.cuKhoa` ra
// `undefined`, `|| {}` ngay sau đó biến nó thành rỗng, và cả một ô hiện
// «—» mãi mãi. Không lỗi, không cảnh báo, và phép kiểm vẽ-được ở trên
// vẫn xanh vì trang vẫn vẽ ra nút — chỉ là nút rỗng.
//
// Chỉ soi những HÀM có nhắc `S.trungUong`: `t` còn được dùng cho thẻ DOM
// ở vài chỗ khác (`var t = el("span", …)`), và soi cả file thì `t.style`
// bị gọi oan. Cắt chú thích và chuỗi trước khi dò, vì một chú thích giải
// thích `t.danhMuc` sẽ bị tính là chính nó.
{
  const sach = ma
    .replace(/\/\*[\s\S]*?\*\//g, " ")
    .replace(/(^|[^:])\/\/[^\n]*/g, "$1 ")
    .replace(/"(?:[^"\\\n]|\\.)*"/g, '""')
    .replace(/'(?:[^'\\\n]|\\.)*'/g, "''");
  // Cắt theo `var t =`, KHÔNG theo `function`. Bản đầu cắt theo `function`
  // và mỗi callback `.map(function (x) {…})` lại cắt khối làm đôi, nên mọi
  // `t.X` nằm sau một callback rơi vào khối không có `S.trungUong` và bị
  // bỏ qua. Nó không báo oan — nó soi ÍT hơn mình tưởng, mà một bộ kiểm
  // soi ít hơn mình tưởng thì cũng xanh y hệt một bộ kiểm soi đủ. Đo lúc
  // phát hiện: 18 khoá thay vì 22.
  const khoi = sach.split(/\bvar\s+t\s*=/);
  const doc = new Set();
  for (const k of khoi) {
    // `S.trungUong` phải nằm ở ĐẦU khối — đó là chính dòng gán. Gặp nó ở
    // giữa khối là một lần đọc khác, không phải chỗ `t` được đặt.
    if (!k.slice(0, 120).includes("S.trungUong")) continue;
    for (const m of k.matchAll(/\bt\.([A-Za-z][A-Za-z0-9]*)/g)) {
      doc.add(m[1]);
    }
  }
  // `t` của trang là `S.trungUong`, KHÔNG phải cả ảnh chụp — soi
  // nhầm tầng thì mọi khoá đều "không có" và bảng đỏ rực một cách vô
  // nghĩa, đúng kiểu báo động giả làm người ta thôi tin bộ kiểm.
  const tu = T.trungUong || {};
  const thieu = [...doc].filter((k) => !(k in tu)).sort();
  const ok = doc.size >= 28 && !thieu.length;
  console.log("  " + (ok ? "OK   " : "LỖI  ") + " " + "khoá-đọc".padEnd(11)
    + " " + doc.size + " khoá trang đọc"
    + (thieu.length ? " · KHÔNG CÓ trong ảnh chụp: " + thieu.join(", ")
                    : " · đều có thật")
    + (doc.size < 28 ? " · dò được quá ít, phép kiểm này đang canh cái rỗng"
                     : ""));
  ok ? xong++ : loi++;

  // ── CHIỀU NGƯỢC: trường nào SINH RA mà KHÔNG AI ĐỌC ──────────────────
  //
  // Sáu lần trong cùng cây mã này, cùng một cách hỏng: có mã, có phép
  // kiểm, có dữ liệu đi ra tận API — và tầng cần nó thì không gọi.
  // `duDoanVaThuc` hiện trên buồng lái mà vòng tiến hoá không đọc;
  // `hoc` (máy tự chẩn mình mỗi 15 phút) không hiện ở ĐÂU cả, chỉ lấy
  // được bằng `curl`; `luuDanhMuc.loiGhi` — ghi danh mục hỏng — cũng thế,
  // và hỏng ở đó nghĩa là mất sạch vị thế ở lần bật máy kế tiếp.
  //
  // Một trường không ai đọc là một trường không tồn tại, chỉ khác ở chỗ
  // nó tốn công tính mỗi vòng và làm người viết yên tâm.
  {
    const pyCd = readFileSync(join(GOC, "thi_bac_ty/chan_doan_he.py"), "utf8");
    const docPy = new Set(
      [...pyCd.matchAll(/anh\.get\("([A-Za-z][A-Za-z0-9]*)"/g)].map((m) => m[1]));
    // Trường chỉ dùng để LƯU hoặc để một cỗ máy khác đọc, không phải để
    // hiện — khai ở đây kèm lý do, đừng để nó lẫn vào đám không ai đọc.
    const NGOAI_LE = new Map([
      ["vong", "trang đọc `S.vong` ở TẦNG NGOÀI — cùng một con số, đếm ở "
             + "hai chỗ. Phép so ngay dưới canh chúng không rời nhau."],
    ]);
    const khongAiDoc = Object.keys(tu)
      .filter((k) => !doc.has(k) && !docPy.has(k) && !NGOAI_LE.has(k))
      .sort();
    const ok2 = !khongAiDoc.length;
    console.log("  " + (ok2 ? "OK   " : "LỖI  ") + " " + "khoá-sinh".padEnd(11)
      + " " + Object.keys(tu).length + " trường ảnh chụp"
      + (ok2 ? " · trường nào cũng có người đọc"
             : " · KHÔNG AI ĐỌC: " + khongAiDoc.join(", ")));
    ok2 ? xong++ : loi++;

    // Hai bộ đếm vòng, hai chỗ tăng, một cái tên. Hôm nay chúng bằng
    // nhau; ngày chúng rời nhau thì buồng lái hiện một con số và sổ ghi
    // một con số khác, và không ai biết tin cái nào. Rẻ hơn nhiều so với
    // đi tìm về sau.
    const ok3 = tu.vong === T.vong;
    console.log("  " + (ok3 ? "OK   " : "LỖI  ") + " " + "vòng-khớp".padEnd(11)
      + " ngoài " + T.vong + " · Trung Ương " + tu.vong
      + (ok3 ? " · khớp" : " · LỆCH, hai chỗ đếm rời nhau"));
    ok3 ? xong++ : loi++;
  }
}

// Phép kiểm cuối: một hàm vẽ NÉM thì `ve()` phải dựng Ô BÁO LỖI vào
// `#than`, tuyệt đối không để thân trang rỗng. Đây là lưới đỡ cuối cùng
// của cả trang, nên chính nó cũng phải có người canh.
{
  let ok = false, vi = "";
  const cu = globalThis._TRANG["von"];
  try {
    globalThis._TRANG["von"] = () => { throw new Error("cố tình ném"); };
    globalThis.location.pathname = "/von";
    globalThis._ve();
    const than = kho["than"];
    ok = (than.children || []).length > 0 && /vẽ hỏng/.test(chu(than));
    vi = ok ? "ném → hiện ô báo lỗi" : "ném → THÂN TRANG RỖNG";
  } catch (e) {
    vi = "chính `ve()` cũng ném: " + e.message;
  } finally {
    globalThis._TRANG["von"] = cu;
    globalThis.location.pathname = "/";
  }
  console.log("  " + (ok ? "OK   " : "LỖI  ") + " " + "trang-ném".padEnd(11)
    + " " + vi);
  ok ? xong++ : loi++;
}

console.log("\n  " + xong + "/" + (xong + loi) + " phép đạt · "
  + tongNut + " nút vẽ ra\n");
process.exit(loi ? 1 : 0);
