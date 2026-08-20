/* ═══════════════════════════════════════════════════════
   VÒNG TIẾN HOÁ — đo cung, chọn kỹ năng, ra đề, và CHẶN.

   Chạy:
     node scripts/tien-hoa.mjs do <cung>        phiếu đo, thuần số học
     node scripts/tien-hoa.mjs ky-nang <cung>   chọn skill Tàng Thư Các khớp điểm yếu
     node scripts/tien-hoa.mjs de-bai <cung>    gộp hai thứ trên thành đề bài cho model
     node scripts/tien-hoa.mjs cong <cung>      CỔNG CHẶN — mọi phép kiểm phải qua

   ── VÌ SAO CÓ FILE NÀY ────────────────────────────────
   Nhà máy tới nay chỉ làm mới DỮ LIỆU. Không node nào chạm vào
   `app.js`, `app.css` hay `index.html` của bất kỳ cung nào — nghĩa
   là giao diện chỉ tiến khi có người ngồi xuống sửa tay.

   Nhưng cho model sửa thẳng file giao diện là đâm vào đúng luật
   xương sống của repo: "đừng cho model ghi thẳng scan.js — một lỗi
   cú pháp của nó là một trang trắng cho người xem". `app.js` còn tệ
   hơn scan.js: nó là hành vi, không phải dữ liệu.

   Nên vòng này đảo thứ tự lại. Model KHÔNG được tin, nó chỉ được
   ĐỀ XUẤT; thứ quyết định là hai đầu số học kẹp nó ở giữa:

       ĐO ──► CHỌN KỸ NĂNG ──► [model đề xuất] ──► CỔNG CHẶN
       ▲                                                │
       └──────── lượt sau đo lại, thấy có tiến không ───┘

   Đầu vào là số (phiếu đo), đầu ra bị chặn bằng số (cổng). Model
   nằm giữa hai lớp không do nó viết. Bỏ một trong hai lớp đó đi thì
   đây không còn là tiến hoá, chỉ là một cái máy tự làm hỏng mình.

   ── CỐ Ý KHÔNG ĐÓNG CỨNG CUNG NÀO ─────────────────────
   Mọi lệnh đều nhận `<cung>`. Bài học từ `build-scan.mjs`: nó đóng
   cứng `const APP = join(ROOT, "dai-quan-trac")`, nên cung thứ hai
   muốn dùng lại phải chép cả file. Ở đây thêm một cung vào vòng
   tiến hoá là thêm một tham số, không phải thêm một script.
   ═══════════════════════════════════════════════════════ */

import { writeFile, mkdir } from "node:fs/promises";
import { existsSync, readdirSync, statSync, readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import vm from "node:vm";
import { dirname, join, relative, extname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);
const [, , LENH, CUNG] = process.argv;
const co_ = (ten) => {
  const i = process.argv.indexOf("--" + ten);
  return i === -1 || i === process.argv.length - 1 ? null : process.argv[i + 1];
};

function thoat(msg) { console.error(msg); process.exit(1); }
if (!LENH) thoat("Thiếu lệnh. Xem đầu file scripts/tien-hoa.mjs.");
if (!CUNG || !existsSync(join(ROOT, CUNG, "index.html")))
  thoat(`"${CUNG}" không phải một cung (không có index.html ở gốc thư mục).`);

const DUONG = (...p) => join(ROOT, CUNG, ...p);
const doc = (p) => readFileSync(p, "utf8");
const co = (p) => existsSync(p);

function quet(dir, ra = []) {
  for (const n of readdirSync(dir)) {
    const p = join(dir, n);
    statSync(p).isDirectory() ? quet(p, ra) : ra.push(p);
  }
  return ra;
}

/* ═══════════════ DOM GIẢ ═══════════════

   Đủ để chạy app.js của một cung ngoài trình duyệt. Không phải để
   mô phỏng trình duyệt cho đúng — chỉ để BẮT LỖI LÚC CHẠY, thứ
   `node --check` không bao giờ thấy vì nó chỉ soi cú pháp.

   Mẹo ở đây: shim ghi lại mọi `href` dạng "#/..." mà app gán cho
   thẻ nó tạo ra. Nhờ vậy danh sách phòng được PHÁT HIỆN chứ không
   phải khai — thêm một phòng vào app.js là cổng chặn tự soi phòng
   đó, không ai phải nhớ cập nhật danh sách ở chỗ thứ hai. */
function domGia() {
  const tuyen = new Set();
  /* Nhận cả `#/tuyen` lẫn `#tuyen` — repo đang dùng cả hai quy ước.
     Và nhặt cả trong chuỗi innerHTML: phần lớn cung dựng nguyên khối
     HTML rồi gán một lần, nên link không đi qua setter `.href` nào. */
  const gomHash = (van) => {
    for (const m of String(van).matchAll(/href="(#[^"\s]*)"/g)) {
      if (m[1].length > 1 && m[1] !== "#top") tuyen.add(m[1]);
    }
  };
  const kho = {};
  const nghe = {};

  function El(tag) {
    return {
      tagName: (tag || "div").toUpperCase(),
      _html: "", _text: "", _attr: {}, children: [], dataset: {},
      /* `style` phải có setProperty/removeProperty, không chỉ là {}.
         Cung nào đặt biến CSS bằng `el.style.setProperty("--x", v)` —
         kinh-thanh làm thế — sẽ ném ngay, và thước "vẽ được" chấm
         trượt một cung hoàn toàn lành. Mỗi API thiếu ở shim là một
         cung bị phán oan, nên thà thừa vài dòng ở đây. */
      style: { setProperty() {}, removeProperty() {}, getPropertyValue() { return ""; } },
      classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
      hidden: false, offsetWidth: 100, offsetHeight: 100,
      scrollTop: 0, scrollHeight: 100, value: "", checked: false,
      focus() {}, blur() {}, click() {}, remove() {},
      /* Hồ sơ dài cuộn tới mục đang mở — 28 phòng của cung Đài Quan
         Trắc gọi hàm này. Thiếu nó là cả 28 phòng ngã. */
      scrollIntoView() {}, matches() { return false; }, contains() { return false; },
      insertBefore(c) { this.children.push(c); return c; },
      getBoundingClientRect() { return { top: 0, left: 0, width: 100, height: 100 }; },
      set innerHTML(v) { this._html = String(v); gomHash(this._html); },
      get innerHTML() { return this._html; },
      set textContent(v) { this._text = String(v); },
      get textContent() { return this._text; },
      set href(v) {
        this._attr.href = String(v);
        if (String(v).startsWith("#") && String(v).length > 1) tuyen.add(String(v));
      },
      get href() { return this._attr.href || ""; },
      appendChild(c) { this.children.push(c); return c; },
      setAttribute(k, v) {
        this._attr[k] = String(v);
        if (k === "href" && String(v).startsWith("#") && String(v).length > 1) tuyen.add(String(v));
      },
      getAttribute(k) { return k in this._attr ? this._attr[k] : null; },
      removeAttribute(k) { delete this._attr[k]; },
      addEventListener() {},
      querySelectorAll() { return []; },
      /* Trả về một thẻ giả chứ KHÔNG trả null. Mã thật hay viết
         `hang.querySelector(".x").addEventListener(...)` không kiểm
         null — trả null là shim tự tạo ra một lỗi không có thật,
         rồi cổng chặn báo oan. Trả thẻ giả thì nhánh đó chạy tiếp,
         tức là soi được NHIỀU hơn chứ không phải ít hơn. */
      querySelector() { return El("div"); },
      closest() { return null; }
    };
  }

  global.window = {
    innerWidth: 1400, innerHeight: 900, devicePixelRatio: 1,
    addEventListener(t, f) { (nghe[t] = nghe[t] || []).push(f); },
    removeEventListener() {},
    dispatchEvent() { return true; },
    /* Trả về đối tượng có `matches` và `addEventListener` — mã hay
       viết `matchMedia("...").addEventListener("change", f)`. Thiếu
       một trong hai là ném ngay dòng đầu. */
    matchMedia() {
      return { matches: false, media: "", addEventListener() {}, removeEventListener() {}, addListener() {} };
    },
    getComputedStyle() { return { getPropertyValue() { return ""; } }; },
    localStorage: { getItem() { return null; }, setItem() {}, removeItem() {} },
    scrollTo() {},
    setTimeout(f) { return 0; },
    requestAnimationFrame(f) { f(); }
  };
  global.matchMedia = global.window.matchMedia;
  global.getComputedStyle = global.window.getComputedStyle;
  global.localStorage = global.window.localStorage;
  global.requestAnimationFrame = global.window.requestAnimationFrame;
  global.location = { hash: "", protocol: "http:" };
  global.window.location = global.location;
  /* KHÔNG gán global.navigator: từ Node 22 nó là thuộc tính chỉ-đọc của
     chính Node, gán đè là ném TypeError. Bỏ đi lại đúng hơn — pwa.js
     kiểm `"serviceWorker" in navigator`, mà navigator của Node không có
     nên nhánh service worker tự tắt, đúng thứ ta muốn khi chạy ngoài
     trình duyệt. */
  /* `window.navigator` phải có, và phải là đối tượng RIÊNG chứ không
     phải navigator của Node: mã PWA hay đọc `navigator.standalone`
     (cờ iOS), mà Node không có `window` nên không ai gán hộ. */
  global.window.navigator = { standalone: false, userAgent: "node", language: "vi" };

  const theoId = (id) => (kho[id] = kho[id] || El("div"));
  global.document = {
    readyState: "complete", title: "", head: El("head"), body: El("body"),
    documentElement: El("html"),
    getElementById(id) { return theoId(id); },
    createElement(t) { return El(t); },
    createElementNS(_, t) { return El(t); },
    createTextNode() { return El("text"); },
    addEventListener(t, f) { (nghe[t] = nghe[t] || []).push(f); },
    removeEventListener() {},
    querySelectorAll() { return []; },
    /* Trả thẻ giả, KHÔNG trả null — cùng lý do đã ghi ở El.querySelector
       bên trên, và để hai cấp nhất quán. Trước bản này document trả
       null còn thẻ trả stub, nên `document.querySelector(x).textContent
       = y` ném ở cung-bo trong khi mã đó hoàn toàn lành trên trình
       duyệt thật.

       Đánh đổi, nói rõ: cung nào thật sự trỏ vào một thẻ KHÔNG tồn
       tại thì shim này che mất. Chấp nhận — bộ đo này săn lỗi lúc
       chạy, không săn lỗi chính tả trong bộ chọn. */
    /* Tra `#id` vào ĐÚNG bảng của getElementById, không dựng thẻ mới:
       nhiều cung viết $("#view").innerHTML = … rồi chỗ khác lại
       getElementById("view") để đọc. Hai vật khác nhau thì phép đếm
       ký tự đọc phải thẻ rỗng và báo "vẽ hụt" cho một phòng vẽ đủ. */
    querySelector(sel) {
      const m = /^#([A-Za-z][\w-]*)$/.exec(String(sel || "").trim());
      return m ? theoId(m[1]) : El("div");
    }
  };
  /* Nội dung KHÔNG chỉ nằm trong innerHTML: cung nào render bằng
     appendChild thì chuỗi innerHTML của thẻ chứa luôn rỗng dù cả
     trang đã vẽ xong. Đi hết cây con mới đọc đúng thứ người xem thấy. */
  const sau = (e, mua = new Set()) => {
    if (!e || typeof e !== "object" || mua.has(e)) return "";
    mua.add(e);
    return (e._html || "") + (e.children || []).map((c) => sau(c, mua)).join("");
  };
  /* Và KHÔNG đóng cứng id thẻ chứa. Cung này gọi nó `than`, cung kia
     gọi `view`, kinh-thanh không có `than` — chú thích ngay dưới đã
     ghi đúng chuyện đó. Đọc mọi thẻ có id là trả lời đúng câu hỏi
     cần hỏi — "trang có vẽ ra gì không" — mà không phải biết tên. */
  const catTrang = () => Object.keys(kho).map((k) => sau(kho[k])).join("") + sau(global.document.body);
  return { tuyen, kho, nghe, gomHash, catTrang };
}

/* ── CHẠY THỬ TRONG TIẾN TRÌNH CON, CÓ HẠN GIỜ ─────────────
   Đo thử trên cả mười cung mới lộ ra: bộ đo này KHÔNG hề dùng chung
   được như nó tự nhận. `kinh-thanh` treo hẳn — 14 file, 375 KB JS,
   và nó không có `id="than"` mà cả phần vẽ ở đây dựa vào. Nhận
   `<cung>` làm tham số không có nghĩa là dùng được cho mọi cung; nó
   chỉ có nghĩa là không đóng cứng TÊN cung.

   Một vòng lặp vô hạn trong JS thì không `try/catch` nào bắt được,
   nên phần động phải chạy ở TIẾN TRÌNH CON có hạn giờ. Treo thì giết,
   và ba thước động thành "KHÔNG ĐO ĐƯỢC" — không phải "trượt".

   Phân biệt đó là toàn bộ giá trị của bản sửa này: chấm trượt một
   thước mình chưa từng đo được cũng là nói dối bằng số, y như chấm
   đạt. Trước bản này, chín cung ngoài Hộ Bộ đều bị chấm 4/7 mà ba
   thước động trong đó chưa hề chạy. */
const HAN_GIAY = 45;

/* Nhường một nhịp cho microtask và setTimeout(0). Cung nào khởi động
   có `await` — Đài Quan Trắc dùng `await load()` — thì thiếu chỗ này
   là cổng chụp ảnh lúc app mới chạy được nửa câu đầu, rồi kết luận
   "qua cả năm phép · 0 phòng". Qua mà không soi gì thì tệ hơn trượt. */
const nhip = () => new Promise((r) => setTimeout(r, 0));

async function thuVeConThuc() {
  const html = doc(DUONG("index.html"));
  const src = [...html.matchAll(/<script src="([^"]+)"/g)].map((m) => m[1]);
  const g = domGia();
  const loi = [];
  for (const s of src) {
    const p = DUONG(...s.split("/"));
    if (!co(p)) { loi.push(`thiếu ${s}`); continue; }
    try {
      /* XOÁ CACHE trước mỗi lần nạp. `cong --so` gọi thuVe() hai lần
         trong CÙNG một tiến trình, và lần hai `require` trả bản đã nạp
         nên IIFE của app.js không chạy lại — không phòng nào được phát
         hiện, phiếu tụt 7/7 → 6/7 vì một lý do không có thật. Chốt
         "không được xấu đi" mà báo nhầm thì nó chặn cả đề xuất đúng,
         và vòng tiến hoá đứng im mà không ai hiểu vì sao. */
      delete require.cache[require.resolve(p)];
      require(p);
    } catch (e) { loi.push(`${s}: ${e.message.slice(0, 140)}`); }
  }
  /* Hai nhịp: `await load()` rồi bên trong còn `await` nữa là chuyện
     thường, một nhịp không đủ cho dòng cuối của init() chạy xong. */
  await nhip(); await nhip();
  /* Mồi phòng từ index.html tĩnh, và từ bản khai TÙY CHỌN `__TUYEN`.
     Cung điều hướng bằng nút onclick không có `href` nào để nhặt —
     Đài Quan Trắc có hơn trăm phòng mà chỉ lộ ra một. Cung không khai
     thì chạy y như cũ. */
  g.gomHash(html);
  const khai = global.window && global.window.__TUYEN;
  if (Array.isArray(khai)) {
    for (const t of khai) {
      const h = String(t || "").trim();
      if (h.length > 1 && h.startsWith("#")) g.tuyen.add(h);
    }
  }
  const phong = [];
  for (const t of g.tuyen) {
    global.location.hash = t;
    global.window.location.hash = t;
    try {
      (g.nghe.hashchange || []).forEach((f) => f());
      await nhip();
      const h = g.catTrang();
      phong.push({
        tuyen: t, ky: h.length,
        gach: (h.match(/>—</g) || []).length,
        rac: /undefined|\[object Object\]|NaN(?![a-zA-Z])/.test(h)
      });
    } catch (e) {
      phong.push({ tuyen: t, ky: 0, gach: 0, rac: false, nga: e.message.slice(0, 120) });
      loi.push(`${t}: ${e.message.slice(0, 120)}`);
    }
  }
  return { phong, loi };
}

/* Vỏ bọc: gọi lại chính file này ở chế độ `--ve-json` trong tiến
   trình con. Cha đọc JSON qua stdout; con treo thì cha giết. */
function thuVe() {
  try {
    const ra = execFileSync(process.execPath,
      [fileURLToPath(import.meta.url), "ve-json", CUNG],
      { encoding: "utf8", timeout: HAN_GIAY * 1000, stdio: ["ignore", "pipe", "pipe"] });
    return JSON.parse(ra);
  } catch (e) {
    const treo = e.killed || e.signal === "SIGTERM" || /ETIMEDOUT/.test(String(e.code));
    return {
      phong: [], loi: [],
      khongDo: treo
        ? `treo quá ${HAN_GIAY}s — nhiều khả năng cung này có kiến trúc DOM khác`
        : `không chạy được: ${String(e.stderr || e.message).trim().slice(0, 120)}`
    };
  }
}

/* ═══════════════ TƯƠNG PHẢN MÀU ═══════════════
   Công thức WCAG, không phải cảm giác. Chỉ đọc biến CSS trong
   `:root` — quy ước đặt tên của repo đủ đều để ghép cặp tự động:
   mọi `--fg*` là chữ, mọi `--bg*`/`--card*` là nền. */
function raiHex(h) {
  h = h.replace("#", "").trim();
  if (h.length === 3) h = h.split("").map((c) => c + c).join("");
  if (!/^[0-9a-fA-F]{6}$/.test(h)) return null;
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
}
function sang(rgb) {
  const c = rgb.map((v) => {
    const s = v / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}
function tuongPhan(a, b) {
  const [x, y] = [sang(a), sang(b)].sort((m, n) => n - m);
  return (x + 0.05) / (y + 0.05);
}
function doMau(css) {
  const goc = css.match(/:root\s*\{([\s\S]*?)\}/);
  if (!goc) return { cap: [], thieu: "không tìm thấy khối :root" };
  const bien = {};
  for (const m of goc[1].matchAll(/(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})/g)) {
    const v = raiHex(m[2]);
    if (v) bien[m[1]] = v;
  }
  /* GHÉP CẶP THEO KHỐI LUẬT, không lấy tích chéo.

     Hai bản trước đều sai, mỗi bản một kiểu, và bản thứ hai sai tệ hơn:

       lọc theo tên `--fg*`/`--bg*`  → mù với sáu cung đặt tên khác
       tích chéo mọi chữ × mọi nền   → 126 cặp, 37 "trượt", trong đó
                                       có `--tien trên --tien` tỉ số 1

     Màu nhấn vừa làm chữ ở chỗ này vừa làm nền ở chỗ kia, nên nó rơi
     vào cả hai tập và tự ghép với chính nó. Một bộ đo tương phản báo
     37 lỗi giả thì tệ hơn hẳn không có bộ đo nào.

     Nay chỉ ghép cặp CÓ THẬT: `color` và `background` cùng xuất hiện
     trong MỘT khối luật, cộng với mọi màu chữ đặt trên nền của `body`
     (trường hợp thừa kế phổ biến nhất, và là nền của phần lớn chữ). */
  const nenBody = (() => {
    const m = css.match(/(^|[}\s])body\s*\{([\s\S]*?)\}/);
    const b = m && m[2].match(/background(?:-color)?\s*:[^;]*var\((--[\w-]+)/);
    return b ? b[1] : null;
  })();

  const capThat = new Set();
  for (const kh of css.matchAll(/\{([^{}]*)\}/g)) {
    const than = kh[1];
    const c = [...than.matchAll(/(?:^|[;\s])color\s*:[^;]*var\((--[\w-]+)/g)].map((m) => m[1]);
    const n = [...than.matchAll(/(?:^|[;\s])background(?:-color)?\s*:[^;]*var\((--[\w-]+)/g)].map((m) => m[1]);
    for (const x of c) for (const y of n) if (x !== y) capThat.add(x + "|" + y);
  }

  /* HỌC VAI TRÒ TỪ CÁCH DÙNG, không đoán theo tên.
     Bản đầu lọc `--fg*` và `--bg*` — đúng cho ba cung mới, mù với sáu
     cung cũ đặt tên khác (`--ink`, `--paper`, `--muc`…). Đo thử cả
     mười cung mới lộ ra: sáu cung im lặng "không đo được" chỉ vì bộ
     đo không đọc nổi tên biến của chúng.
     Nay quét chính các khai báo: biến nào xuất hiện sau `color:` là
     CHỮ, sau `background*:` hay `border*:` là NỀN. Quy ước đặt tên
     thành phương án dự phòng, không còn là điều kiện. */
  const vai = { chu: new Set(), nen: new Set() };
  for (const m of css.matchAll(/(^|[;{\s])(background[\w-]*|color)\s*:\s*var\((--[\w-]+)/g)) {
    (m[2] === "color" ? vai.chu : vai.nen).add(m[3]);
  }
  const loc = (t, du) => {
    const co = [...vai[t]].filter((k) => bien[k]);
    return co.length ? co : Object.keys(bien).filter((k) => du.test(k));
  };
  const chu = loc("chu", /^--(fg|ink|text|muc|chu)/);

  /* Mọi màu chữ đặt trên nền body — nhánh thừa kế, phủ phần lớn chữ
     trên trang mà không khối luật nào khai tường minh. */
  if (nenBody) for (const c of chu) if (c !== nenBody) capThat.add(c + "|" + nenBody);

  const cap = [];
  for (const k of capThat) {
    const [c, n] = k.split("|");
    if (!bien[c] || !bien[n]) continue;
    const ti = tuongPhan(bien[c], bien[n]);
    cap.push({ chu: c, nen: n, ti: Number(ti.toFixed(2)), dat: ti >= 4.5 });
  }
  return { cap: cap.sort((a, b) => a.ti - b.ti), soBien: Object.keys(bien).length };
}

/* ═══════════════ PHIẾU ĐO ═══════════════
   Mọi thước ở đây phải TỰ ĐO ĐƯỢC. Thứ nào cần người nhìn mới chấm
   được thì không thuộc về đây — đưa nó vào phiếu là biến phiếu
   thành ý kiến, mà ý kiến thì không so được giữa hai lượt. */
function do_() {
  const file = quet(DUONG());
  const html = doc(DUONG("index.html"));
  const css = ["app.css", "halls.css"]
    .filter((f) => co(DUONG("assets/css", f)))
    .map((f) => doc(DUONG("assets/css", f))).join("\n");

  const ve = thuVe();
  const mau = doMau(css);

  /* Nhãn cho người đọc màn hình: nút không chữ và không aria-label
     là một nút câm. SVG không aria-hidden thì trình đọc màn hình
     đọc ra một mớ toạ độ. */
  const nutCam = [...html.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/g)]
    .filter((m) => !/aria-label=/.test(m[1]) && !m[2].replace(/<[^>]*>/g, "").trim()).length;
  /* Một svg trang trí nằm TRONG thẻ đã có aria-hidden hoặc aria-label
     thì trình đọc màn hình vốn đã không đọc nó — cờ nó lên là báo
     nhầm. Mà cảnh báo báo nhầm mãi thì người ta bỏ qua cảnh báo, kéo
     theo cả lần nó đúng; đó là luật đã ghi trong CLAUDE.md, ở đây chỉ
     áp vào chỗ mới. Nên soi thêm ~240 ký tự ngay trước thẻ svg. */
  const svgTran = [...html.matchAll(/<svg([^>]*)>/g)].filter((m) => {
    if (/aria-hidden|role=|aria-label/.test(m[1])) return false;
    const truoc = html.slice(Math.max(0, m.index - 240), m.index);
    const cha = [...truoc.matchAll(/<(?:span|button|a|div)([^>]*)>/g)].pop();
    return !(cha && /aria-hidden|aria-label/.test(cha[1]));
  }).length;
  const svgKhongCo = [...html.matchAll(/<svg\b([^>]*)>/g)]
    .filter((m) => !/width=/.test(m[1])).length;

  const congByte = (loc) => file.filter(loc).reduce((n, f) => n + statSync(f).size, 0);
  /* VỎ là mã hành vi; mọi .js khác là NỘI DUNG. Gộp chung thì đạt hay
     trượt hoàn toàn do cung có nhiều nội dung hay không: đo được
     cong-bo vỏ 42 KB / tổng 987 KB, tang-thu-cac vỏ 56 KB / tổng
     2.109 KB. Thước ấy đẩy người ta về phía viết ít đi. */
  const LA_VO = /(^|[\\/])(app|halls|pwa|khung|sw)\.js$/;
  const nang = {
    vo: congByte((f) => LA_VO.test(f)),
    noi: congByte((f) => extname(f) === ".js" && !LA_VO.test(f)),
    js: congByte((f) => extname(f) === ".js"),
    css: congByte((f) => extname(f) === ".css"),
    anh: congByte((f) => /\.(png|jpg|webp|ico)$/.test(f))
  };

  /* Ô trống: đếm dấu "—" trong HTML đã vẽ. Nhiều gạch nghĩa là đường
     ống dữ liệu đang hụt, không phải giao diện xấu — nhưng người xem
     thì không phân biệt được hai chuyện đó. */
  /* Cộng dồn theo phòng là sai thước: cung 54 phòng bị phạt gấp mười
     cung 5 phòng dù mỗi phòng sạch như nhau, và một dải trạng thái
     hiện ở mọi phòng thì bị đếm lại từng lần. */
  const gachTong = ve.phong.reduce((n, p) => n + p.gach, 0);
  const oTrong = ve.phong.length ? Math.round((gachTong / ve.phong.length) * 10) / 10 : 0;
  const nhoNhat = ve.phong.length ? Math.min(...ve.phong.map((p) => p.ky)) : 0;

  const diem = [];
  const cham = (ma, ten, dat, y) => diem.push({ ma, ten, dat, y });

  /* `dat: null` = KHÔNG ĐO ĐƯỢC, khác hẳn `false` = trượt. Ba thước
     dưới cần chạy được app trong DOM giả; cung nào không theo hợp
     đồng đó thì chúng im lặng chứ không chấm bừa. */
  if (ve.khongDo) {
    cham("ve", "Mọi phòng vẽ được", null, ve.khongDo);
    cham("rac", "Không rò undefined/NaN ra HTML", null, "không đo được");
  } else {
    cham("ve", "Mọi phòng vẽ được",
      ve.loi.length === 0 && ve.phong.length > 0 && ve.phong.every((p) => !p.nga && p.ky > 400),
      ve.loi.length ? ve.loi.slice(0, 3).join(" · ")
        : `${ve.phong.length} phòng · nhỏ nhất ${nhoNhat} ký tự`);
    cham("rac", "Không rò undefined/NaN ra HTML",
      ve.phong.every((p) => !p.rac),
      ve.phong.filter((p) => p.rac).map((p) => p.tuyen).join(", ") || "sạch");
  }
  /* Không ghép được cặp nào là KHÔNG ĐO ĐƯỢC, không phải trượt. Phép
     ghép dựa vào quy ước đặt tên `--fg*` / `--bg*` của repo; cung nào
     đặt tên khác (`--ink`, `--paper`…) thì phép này mù, và chấm trượt
     một cung vì bộ đo không đọc được tên biến của nó là phán oan.
     Đã in ra "undefined" đúng một lần ở kinh-thanh trước khi sửa. */
  cham("tuong-phan", "Tương phản chữ/nền đạt WCAG AA",
    mau.cap.length ? mau.cap.every((c) => c.dat) : null,
    mau.cap.length
      ? `${mau.cap.filter((c) => !c.dat).length}/${mau.cap.length} cặp dưới 4.5 · thấp nhất ${mau.cap[0].ti} (${mau.cap[0].chu} trên ${mau.cap[0].nen})`
      : (mau.thieu || "không ghép được cặp --fg*/--bg* nào trong :root"));
  cham("nhan", "Nút và SVG có nhãn", nutCam === 0 && svgTran === 0,
    `${nutCam} nút câm · ${svgTran} svg không aria-hidden`);
  cham("svg-co", "SVG có cỡ nội tại", svgKhongCo === 0,
    `${svgKhongCo} svg chỉ có viewBox — CSS cũ kẹt là phình kín trang`);
  const kb = (x) => (x / 1024).toFixed(0);
  cham("nang", "Vỏ ứng dụng dưới 200 KB", nang.vo + nang.css < 200 * 1024,
    `vỏ ${kb(nang.vo)} KB + css ${kb(nang.css)} KB · nội dung ${kb(nang.noi)} KB · ảnh ${kb(nang.anh)} KB`);
  if (ve.khongDo) cham("o-trong", "Ít ô trống trên trang", null, "không đo được");
  else cham("o-trong", "Ít ô trống mỗi phòng", oTrong <= 2,
    `${oTrong} dấu — mỗi phòng (tổng ${gachTong} trên ${ve.phong.length} phòng)`);

  /* Mẫu số chỉ đếm thước ĐO ĐƯỢC. Để thước không đo được nằm trong
     mẫu số là hạ điểm một cung vì bộ đo yếu, không vì cung yếu. */
  return {
    cung: CUNG, luc: new Date().toISOString(),
    dat: diem.filter((d) => d.dat === true).length,
    tong: diem.filter((d) => d.dat !== null).length,
    khongDo: diem.filter((d) => d.dat === null).length,
    diem,
    tuongPhanXau: mau.cap.filter((c) => !c.dat).slice(0, 8),
    phong: ve.phong.map((p) => ({ tuyen: p.tuyen, ky: p.ky, gach: p.gach })),
    oTrong, nang
  };
}

/* ═══════════════ CHỌN KỸ NĂNG TỪ TÀNG THƯ CÁC ═══════════════

   Tàng Thư Các đã quét 3.600+ skill về máy, trong đó gần 400 cái
   thuộc nhóm `giao-dien`. Cho tới nay kho đó chỉ để NGƯỜI đọc.

   Ở đây nó thành đầu vào của máy: phiếu đo nói cung đang yếu chỗ
   nào, bảng dưới đổi mỗi điểm yếu thành từ khoá, rồi chấm từng skill
   theo (số từ khoá khớp × log sao). KHÔNG gọi model — chọn skill là
   việc so chuỗi, mà chỗ nào so chuỗi trả lời được thì đừng trả tiền
   cho model trả lời. Đó là luật đã có sẵn của repo, chỉ áp vào chỗ mới.

   CHỈ lấy skill có giấy phép ghi rõ. Đây là kho của người khác, và
   một SKILL.md không rõ giấy phép thì không nên đem vào đề bài của
   một repo công khai. */
const TU_KHOA = {
  "tuong-phan": ["accessibility", "a11y", "contrast", "wcag", "color", "palette", "theme"],
  "nhan": ["accessibility", "a11y", "aria", "screen reader", "semantic"],
  "svg-co": ["svg", "icon", "vector"],
  "nang": ["performance", "bundle", "optimize", "lighthouse", "web vitals"],
  "ve": ["debug", "frontend", "error"],
  "rac": ["test", "validation", "frontend"],
  "o-trong": ["empty state", "loading", "skeleton", "fallback"],
  "chung": ["frontend", "design", "ui", "ux", "interface", "layout", "typography"]
};

function kyNang(phieu) {
  const p = join(ROOT, "tang-thu-cac", "assets", "js", "data.js");
  if (!co(p)) return { loi: "chưa có tang-thu-cac/assets/js/data.js — chạy build-tangthu trước", skill: [] };
  const hop = { window: {} };
  vm.createContext(hop);
  vm.runInContext(doc(p), hop, { timeout: 20000 });
  const kho = hop.window.TT_DATA || {};
  const tatCa = kho.skills || [];

  const yeu = phieu.diem.filter((d) => !d.dat).map((d) => d.ma);
  const tu = [...new Set([...yeu.flatMap((m) => TU_KHOA[m] || []), ...TU_KHOA.chung])];

  const skill = tatCa
    .filter((s) => s.giayPhep && (s.nhom === "giao-dien" || s.nhom === "lap-trinh"))
    .map((s) => {
      const van = ((s.ten || "") + " " + (s.moTa || "")).toLowerCase();
      const khop = tu.filter((t) => van.includes(t));
      return khop.length ? { s, khop, cham: khop.length * Math.log10((s.sao || 1) + 10) } : null;
    })
    .filter(Boolean)
    .sort((a, b) => b.cham - a.cham)
    .slice(0, 8)
    .map(({ s, khop }) => ({
      ten: s.ten, kho: s.kho, duong: s.duong, nhom: s.nhom, sao: s.sao,
      giayPhep: s.giayPhep, khop,
      moTa: (s.moTa || "").slice(0, 220),
      /* `duong` của Tàng Thư Các trỏ vào THƯ MỤC skill, không phải file.
         Thiếu "/SKILL.md" là mọi URL trả 404 — và hỏng ở đây im lặng
         hoàn toàn: model WebFetch tám lần, nhận tám lần 404, rồi tự
         đoán mà không ai biết cầu nối Tàng Thư Các chưa từng chở gì.
         Đã đo: doc trần → 404, doc + /SKILL.md → 200 trên cả tám. */
      doc: s.kho && s.duong
        ? `https://raw.githubusercontent.com/${s.kho}/HEAD/${s.duong}/SKILL.md`
        : null
    }));

  return { tongSkill: tatCa.length, tuKhoa: tu, yeu, skill, quetLuc: kho.generatedAt || null };
}

/* ═══════════════ CỔNG CHẶN ═══════════════

   Không có cổng thì đây không phải vòng tiến hoá — chỉ là một cái
   máy được cấp quyền tự làm hỏng mình. Năm phép, thoát khác 0 nếu
   bất kỳ phép nào trượt. Bước gộp trong workflow đọc mã thoát này. */
function cong() {
  const loi = [];
  const file = quet(DUONG());

  for (const f of file.filter((x) => extname(x) === ".js")) {
    try { execFileSync(process.execPath, ["--check", f], { stdio: "pipe" }); }
    catch (e) { loi.push(`cú pháp ${relative(ROOT, f)}: ${String(e.stderr || e).slice(0, 140)}`); }
  }
  for (const f of file.filter((x) => /\.(json|webmanifest)$/.test(x))) {
    try { JSON.parse(doc(f)); } catch (e) { loi.push(`JSON hỏng ${relative(ROOT, f)}: ${e.message}`); }
  }

  const ve = thuVe();
  loi.push(...ve.loi.map((x) => "vẽ hụt: " + x));
  for (const p of ve.phong) {
    if (p.ky < 400) loi.push(`phòng ${p.tuyen} chỉ vẽ ${p.ky} ký tự — nghi vẽ hụt`);
    if (p.rac) loi.push(`phòng ${p.tuyen} rò undefined/NaN ra HTML`);
  }

  const ABS = [/\b(?:src|href)\s*=\s*"\/(?!\/)/, /url\(\s*\/(?!\/)/,
    /"(?:start_url|scope)"\s*:\s*"\//, /serviceWorker\.register\(\s*["']\//];
  const VAN = new Set([".html", ".css", ".js", ".json", ".webmanifest"]);
  for (const f of file) {
    if (!VAN.has(extname(f))) continue;
    doc(f).split(/\r?\n/).forEach((d, i) => {
      for (const re of ABS) {
        if (re.test(d)) loi.push(`đường dẫn tuyệt đối ${relative(ROOT, f)}:${i + 1}`);
      }
    });
  }

  const sw = doc(DUONG("sw.js"));
  const shell = [...sw.matchAll(/^\s*"(\.\/[^"]+)"/gm)].map((m) => m[1]);
  const coFile = new Set(file.map((f) => "./" + relative(DUONG(), f).split(/[\\/]/).join("/")));
  for (const s of shell) {
    if (s !== "./" && !coFile.has(s)) loi.push(`sw.js khai "${s}" nhưng không có file đó`);
  }

  console.log(loi.length
    ? `✗ CỔNG CHẶN — ${loi.length} lỗi:\n` + loi.map((x) => "   " + x).join("\n")
    : `✓ Cổng chặn: ${CUNG} qua cả năm phép · ${ve.phong.length} phòng · ${file.length} file`);
  return loi;
}

/* ═══════════════ DÒNG LỆNH ═══════════════ */
/* Chế độ nội bộ: cha gọi lại chính file này để phần vẽ chạy trong
   tiến trình con có hạn giờ. Không dành cho người gõ tay. */
if (LENH === "ve-json") {
  process.stdout.write(JSON.stringify(await thuVeConThuc()));
  process.exit(0);
}

if (LENH === "do") {
  const p = do_();
  /* `--ghi <file>` cất phiếu lại làm MỐC GỐC cho `cong --so` đối chiếu.
     Workflow gọi nó TRƯỚC khi model đụng vào bất cứ thứ gì — đo sau khi
     đã sửa rồi mới nghĩ tới việc so là đã mất mốc. */
  const raGhi = co_("ghi");
  if (raGhi) {
    await mkdir(dirname(raGhi), { recursive: true });
    await writeFile(raGhi, JSON.stringify(p, null, 2) + "\n", "utf8");
  }
  console.log(`Phiếu đo ${CUNG}: ${p.dat}/${p.tong} đạt` +
    (p.khongDo ? ` · ${p.khongDo} thước không đo được` : "") + "\n");
  for (const d of p.diem) {
    console.log(`  ${d.dat === null ? "·" : d.dat ? "✓" : "✗"} ${d.ten.padEnd(34)} ${d.y}`);
  }
  if (p.tuongPhanXau.length) {
    console.log("\n  Cặp màu chưa đạt:");
    for (const c of p.tuongPhanXau) {
      console.log(`     ${String(c.ti).padStart(5)}  ${c.chu} trên ${c.nen}`);
    }
  }
} else if (LENH === "ky-nang") {
  const k = kyNang(do_());
  if (k.loi) thoat(k.loi);
  console.log(`Chọn từ ${k.tongSkill} skill Tàng Thư Các · điểm yếu: ${k.yeu.join(", ") || "không có"}\n`);
  for (const s of k.skill) {
    console.log(`  ${(s.ten || "?").padEnd(26)} ★${String(s.sao).padStart(7)}  ${s.giayPhep}`);
    console.log(`     ${s.kho} · khớp: ${s.khop.join(", ")}`);
  }
} else if (LENH === "de-bai") {
  const phieu = do_();
  const k = kyNang(phieu);
  const ra = DUONG("assets", "data", "de-bai-tien-hoa.json");
  await mkdir(dirname(ra), { recursive: true });
  await writeFile(ra, JSON.stringify({
    ghiChu: "SINH TỰ ĐỘNG bởi scripts/tien-hoa.mjs. Đừng sửa tay, đừng commit.",
    cung: CUNG, phieu, kyNang: k.skill, quetSkillLuc: k.quetLuc
  }, null, 2) + "\n", "utf8");
  console.log(`Đề bài: ${phieu.tong - phieu.dat} điểm yếu · ${k.skill.length} kỹ năng → ${relative(ROOT, ra)}`);
} else if (LENH === "cong") {
  const loi = cong();

  /* ── CHỐT THỨ HAI: KHÔNG ĐƯỢC XẤU ĐI ────────────────────────
     Năm phép trên bắt được "VỠ". Chúng không bắt được "vẫn chạy
     nhưng XẤU HƠN" — đổi màu thành khó nhìn, gỡ một nhãn, phình
     file. Với vòng TỰ GỘP thì lỗ đó là lỗ chí mạng: đề xuất tồi
     lên thẳng site và phải đợi lượt sau mới lộ ra.

     Nên so phiếu đo trước/sau. Điểm tụt là CHẶN, dù cả năm phép
     kia đều xanh.

     Nói thẳng giới hạn: chốt này chỉ khoá được những chiều ĐO
     ĐƯỢC. Một đề xuất giữ nguyên 7/7 mà bố cục rối hơn thì nó cho
     qua. Đừng tưởng nó khoá được cái đẹp. */
  const truoc = co_("so");
  if (truoc && existsSync(truoc)) {
    const cu = JSON.parse(readFileSync(truoc, "utf8"));
    const moi = do_();
    if (moi.dat < cu.dat) {
      const tut = cu.diem.filter((d) => d.dat)
        .filter((d) => !moi.diem.find((x) => x.ma === d.ma && x.dat))
        .map((d) => d.ten);
      const cau = `ĐIỂM TỤT ${cu.dat}/${cu.tong} → ${moi.dat}/${moi.tong}` +
        (tut.length ? ` · mất: ${tut.join(", ")}` : "");
      loi.push(cau);
      console.log("✗ " + cau);
    } else {
      console.log(`  phiếu đo ${cu.dat}/${cu.tong} → ${moi.dat}/${moi.tong}` +
        (moi.dat > cu.dat ? "  ↑ tiến" : "  = giữ nguyên"));
    }
  }
  process.exit(loi.length ? 1 : 0);
} else {
  thoat(`Lệnh lạ "${LENH}". Có: do · ky-nang · de-bai · cong`);
}
