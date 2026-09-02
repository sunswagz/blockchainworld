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
import { existsSync, readdirSync, statSync, readFileSync, appendFileSync, mkdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { docShell } from "./mang-truoc.mjs";
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

/* Cung nào tới lượt hôm nay — xem scripts/vong-xoay.mjs cho lý do
   một node xoay bảy cung thay vì bảy node. Danh sách nằm ở file
   riêng vì `npm run kiem` phải đọc được nó, mà import file NÀY là
   chạy luôn phần thân của nó. */
if (LENH === "xoay") {
  const { cungHomNay } = await import("./vong-xoay.mjs");
  const c = cungHomNay();
  const ra = co_("ra");
  if (ra) await writeFile(ra, `cung=${c}\n`, { flag: "a" });
  console.log(c);
  process.exit(0);
}

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
      /* `parentNode` phải CÓ, và phải theo được lối `x.parentNode.insertBefore(y, x)`
         — khuôn "chèn một thẻ ngay TRƯỚC thẻ này", dùng thật ở ba chỗ trong
         kinh-thanh và ở pwa.js của mọi cung. Thiếu nó thì `.parentNode` là
         undefined và cả file ném ngay lúc nạp, rồi thước "Mọi phòng vẽ được"
         chấm trượt một cung hoàn toàn lành: kinh-thanh bị 5/7 vì đúng chuyện
         này, trong khi mã của nó chạy bình thường trên trình duyệt.
         Cùng luật với mục mang-truoc.mjs trong CLAUDE.md — công cụ phải theo
         được mã thật, không phải bẻ mã cho vừa công cụ. */
      parentNode: null,
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
      insertBefore(c) { this.children.push(c); if (c) c.parentNode = this; return c; },
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
      appendChild(c) { this.children.push(c); if (c) c.parentNode = this; return c; },
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
      querySelector() { return trongCay(); },
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
  /* ── navigator: CHỈ tạo khi Node chưa có ────────────────────
     Lý luận cũ ở đây — "bỏ đi lại đúng hơn, navigator của Node không
     có serviceWorker nên nhánh ấy tự tắt" — chỉ ĐÚNG TỪ NODE 21.
     Trước đó Node không có `navigator` nào cả, và
     `"serviceWorker" in navigator` không tắt nhánh mà ném thẳng
     ReferenceError.

     Workflow chạy Node 20 (setup-node@v5, node-version "20"). Máy
     người viết chạy Node 24. Nên cùng một dòng mã cho hai kết quả
     khác nhau, và cái sai chỉ xảy ra ở chỗ không ai nhìn:

       máy  → pwa.js nạp gọn  → "Mọi phòng vẽ được" ĐẠT  → 17/17
       CI   → pwa.js ném lỗi  → thước TRƯỢT              → 12/13

     Sổ nhà máy ghi đúng chuyện đó suốt nhiều lượt — "trượt: Mọi
     phòng vẽ được · assets/js/pwa.js: navigator is not defined" — ở
     `thai-boc-tu-tien-hoa` và `tao-bien-xu-tien-hoa`. Và nó tệ hơn
     một thước sai bình thường: điểm yếu ấy nằm ở pwa.js, NGOÀI ba
     file model được phép sửa, nên mỗi lượt model đi vá một thứ nó
     không với tới được. Hai vòng tiến hoá mất lượt vì một khác biệt
     phiên bản Node.

     `defineProperty` chứ không gán thẳng: từ Node 22 `navigator` là
     thuộc tính chỉ-đọc của chính Node và `global.navigator = …` ném
     TypeError — đó là chỗ lý luận cũ đúng, giữ nguyên phần ấy. */
  if (typeof globalThis.navigator === "undefined") {
    Object.defineProperty(globalThis, "navigator", {
      value: { userAgent: "node", language: "vi" },
      configurable: true, writable: true,
    });
  }
  /* `window.navigator` phải có, và phải là đối tượng RIÊNG chứ không
     phải navigator của Node: mã PWA hay đọc `navigator.standalone`
     (cờ iOS), mà Node không có `window` nên không ai gán hộ. */
  global.window.navigator = { standalone: false, userAgent: "node", language: "vi" };

  /* Thẻ shim phát ra phải trông như thẻ ĐANG NẰM TRONG trang: có cha, và
     cha ấy là `body` — thứ `catTrang()` có đi qua. Trả một thẻ mồ côi thì
     `x.parentNode` là undefined, và thứ được chèn "cạnh" nó rơi ra ngoài
     phép đếm ký tự. */
  const trongCay = () => { const e = El("div"); e.parentNode = global.document.body; return e; };
  const theoId = (id) => (kho[id] = kho[id] || trongCay());
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
      return m ? theoId(m[1]) : trongCay();
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
  /* NEO TRONG TRANG KHÔNG PHẢI TUYẾN. `<a href="#than">` là đường
     nhảy qua thanh bên (WCAG 2.4.1), không phải một phòng — mà bộ dò
     tuyến nhặt mọi href bắt đầu bằng "#", nên nó đếm thêm một phòng
     ma. Đo thật: Hộ Bộ nhảy 8 phòng lên 9 ngay lúc thêm đường nhảy,
     và "phòng" thứ chín chỉ là phòng trước đó vẽ lại.

     Phân biệt được vì neo trỏ vào một `id` CÓ THẬT trong trang, còn
     tuyến thì không: `#/kho-bac` hay `#kho-bac` là mã phòng, không
     có thẻ nào mang id đó. */
  for (const t of [...g.tuyen]) {
    const id = t.replace(/^#\/?/, "");
    if (id && html.includes(`id="${id}"`)) g.tuyen.delete(t);
  }

  /* ── CUNG MỘT TRANG ────────────────────────────────────
     Vòng gạt neo ngay trên xoá mọi "#x" trỏ vào một id có thật. Với
     cung định tuyến thì đúng — nhưng Thị Bạc Ty và Tử Cấm Thành
     CUỘN theo neo chứ không đổi phòng, nên cả sáu, bảy tuyến của
     chúng đều là neo thật và danh sách về 0.

     0 phòng làm BA thước nói sai cùng một lúc:
       ✗ "Mọi phòng vẽ được"      trượt vì không có gì để vẽ
       ✓ "Ít ô trống mỗi phòng"   đạt · "0 dấu — trên 0 phòng"
       ✓ "Không rò undefined"     đạt · vì không soi gì cả
     Hai cái đạt mới là chỗ nguy: xanh mà không đo được gì, đúng
     loại hỏng im lặng mà cả bộ thước này sinh ra để chặn — và cùng
     họ với thước svg xanh suốt vì regex hỏng hồi 28/08.

     Không có tuyến thì trang CHÍNH NÓ là phòng duy nhất. Đo nó ở
     trạng thái vừa nạp xong, không đụng hash. */
  const motTrang = g.tuyen.size === 0;
  const dsTuyen = motTrang ? ["(trang chính)"] : [...g.tuyen];

  const phong = [];
  for (const t of dsTuyen) {
    if (!motTrang) {
      global.location.hash = t;
      global.window.location.hash = t;
    }
    try {
      if (!motTrang) (g.nghe.hashchange || []).forEach((f) => f());
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
  /* MỌI khối :root, không phải khối đầu tiên.

     Trước đây là `css.match(...)` — chỉ khối đầu. Một cung khai token
     làm hai khối (Hộ Bộ vẫn vậy: màu ở khối một, nhãn nguồn tri thức
     ở khối hai) thì nửa sau chưa từng được soi lần nào.

     Và nó hỏng theo lối tệ nhất: chèn một khối :root MỚI lên trước —
     đúng việc scripts/thang-chu.mjs làm — là phép đo tương phản
     chuyển sang "không đo được", mẫu số tụt một, còn ĐIỂM THÌ VẪN
     ĐẸP. Đo được do-sat-vien 10/11 → 10/10, nhìn ngoài như không mất
     gì, thật ra vừa mất một phép kiểm. Bắt được lúc thử chính
     thang-chu.mjs; không thử thì nó đã trôi. */
  const goc = [...css.matchAll(/:root\s*\{([\s\S]*?)\}/g)];
  if (!goc.length) return { cap: [], thieu: "không tìm thấy khối :root" };
  const bien = {};
  for (const g of goc)
    for (const m of g[1].matchAll(/(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})/g)) {
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
  /* MỌI file .css của cung, không chỉ hai cái tên quen.

     Danh sách cứng ["app.css","halls.css"] bỏ sót đúng những cung
     chia CSS ra nhiều file: Kinh Thành có BẢY file và năm cái chưa
     từng được soi, Đài Quan Trắc có ba và một cái chưa. Nghĩa là
     "Kinh Thành 13/13" là điểm chấm trên hai phần bảy số CSS của
     nó — một con số đẹp đo trên một mẩu.

     Hỏng im lặng theo đúng lối tệ nhất: thêm một file CSS mới không
     làm thước nào đỏ lên, nó chỉ lặng lẽ ra khỏi tầm đo. */
  const css = readdirSync(DUONG("assets/css"))
    .filter((f) => f.endsWith(".css")).sort()
    .map((f) => doc(DUONG("assets/css", f))).join("\n");

  /* Ba thước dưới dò bằng CHUỖI THÔ, nên phải cắt chú thích trước.
     Không cắt thì một dòng giải thích nhắc `transition: width` bị
     tính thành một hiệu ứng chạm bố cục thật, và một cỡ px nhắc
     trong chú thích thành một bậc thang thật.

     Đã báo nhầm: Đài Quan Trắc bị tính 2 hiệu ứng chạm bố cục, mà
     mẫu in ra chính là câu chú thích kể chuyện đã GỠ hiệu ứng đó.
     Cung nào càng ghi rõ lý do trong CSS thì càng bị phạt.

     `doMau` KHÔNG dùng bản này: nó ghép cặp theo khối luật `{ }` nên
     chú thích vốn đã không lọt vào cặp nào. */
  const cssMa = css.replace(/\/\*[\s\S]*?\*\//g, " ");

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
  const svgTran = [...html.matchAll(/<svg\b([^>]*)>/g)].filter((m) => {
    if (/aria-hidden|role=|aria-label/.test(m[1])) return false;
    const truoc = html.slice(Math.max(0, m.index - 240), m.index);
    const cha = [...truoc.matchAll(/<(?:span|button|a|div)\b([^>]*)>/g)].pop();
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

  /* ═══ BA PHÉP ĐO ĐẾN TỪ KỆ DỤNG CỤ ═══════════════════
     Ba luật dưới KHÔNG do repo này nghĩ ra. Chúng nằm trong hai
     SKILL.md trên kệ `.claude/skills/`, nhập từ Tàng Thư Các bằng
     `scripts/nhap-skill.mjs`:

       baseline-ui   ibelick/ui-skills      (MIT)
       frontend-design  anthropics/skills   (xem LICENSE.txt)

     Vì sao dịch chúng thành phép canh chứ không chép vào lời nhắc:
     luật nằm trong văn xuôi thì lượt sau model đọc hay không đọc là
     hên xui, và không ai biết cung nào đang phạm. Thành thước thì nó
     hiện trên phiếu, vào đề bài, và cổng chặn giữ được nó.

     Thước nào cung không có gì để đo thì trả `null` — không đo được
     khác hẳn trượt, và mẫu số chỉ đếm thước đo được. */

  /* frontend-design: "set a clear type scale with intentional weights,
     widths, and spacing". Đếm số cỡ px RỜI RẠC còn viết thẳng vào
     rule. Đo được Hộ Bộ 32 cỡ, trong đó mười một cỡ chen giữa 11 và
     13px — đó không phải thang, đó là số bốc từng lúc. Cung nào đã
     đưa cỡ chữ vào biến thì đếm này về 0 và thước tự đạt.

     ĐẾM CẢ NẤC TRONG BIẾN, không chỉ px viết thẳng. Không đếm thì
     thước này lách được bằng một phép đổi tên: `12.3px` thành
     `var(--t-7)` là px biến sạch, thước báo 0, mà cung vẫn có đúng
     32 giá trị rời rạc — chỉ là chúng đã dọn vào một chỗ. Dọn vào
     một chỗ là tốt, nhưng nó không phải cái thước này hỏi.

     Câu hỏi thật: cung dùng BAO NHIÊU giá trị khác nhau. Nấc hay px
     đều là một giá trị. `scripts/thang.mjs` sinh ra chính những nấc
     ấy, nên nếu không đếm chúng thì tôi vừa dựng một cái máy để lách
     cái thước của chính mình. */
  const nacChu = new Set([...cssMa.matchAll(/--t-\d+\s*:\s*[\d.]+px/g)].map((m) => m[0])).size;
  const coPx = [...cssMa.matchAll(/font-size:\s*([\d.]+)px/g)].map((m) => m[1]);
  const soCo = new Set(coPx).size + nacChu;

  /* baseline-ui: "MUST animate only compositor props (transform,
     opacity) · NEVER animate layout properties (width, height, top,
     left, margin, padding)". Mỗi khung hình của một transition chạm
     bố cục là một lượt tính lại bố cục CẢ TRANG. */
  const chuyenXau = [...cssMa.matchAll(/transition:[^;}]*/g)]
    .map((m) => m[0])
    .filter((t) => /\b(width|height|top|left|right|bottom|margin|padding)\b/.test(t));

  /* baseline-ui: "MUST use tabular-nums for data". `font-variant-numeric`
     DI TRUYỀN, nên một dòng ở body/html/:root là phủ cả trang — bắt
     từng rule khai lại thì thành báo nhầm.

     Soi HAI loại mặt số, không phải một:

       · khối dùng font mono
       · khối dựng BẢNG (table/td/th/.bang/.cot/.o-so)

     Bản đầu chỉ soi mono, và đó là soi nhầm chỗ. Font mono vốn đã đều
     chữ nên tabular-nums ở đó gần như vô hại lẫn vô ích; chỗ số THẬT
     SỰ nhảy ngang là bảng dùng font thường — Hộ Bộ chính là vậy, bảng
     của nó chạy "Be Vietnam Pro", chữ số rộng hẹp khác nhau. Một
     thước bỏ sót đúng chỗ đau thì đo cho có.

     Đọc `cssMa` chứ không đọc `css` — cùng cái bẫy chú thích mà biến
     ấy sinh ra để gỡ, chỉ khác đường vào: bộ chọn bắt bằng chuỗi thô
     nuốt nguyên khối chú thích đứng trên rule, nên `:root` và `#than`
     của Hộ Bộ đều từng bị cờ chỉ vì đoạn văn phía trên chúng. */
  const khoi2 = [...cssMa.matchAll(/([^{}]+)\{([^{}]*)\}/g)]
    .map((m) => ({ sel: m[1].trim().replace(/\s+/g, " "), than: m[2] }));

  /* Thẻ `table|td|th` chỉ tính khi đứng làm THẺ, không tính khi là đầu
     một tên lớp. `th\b` bắt luôn `.th-d`, `.th-n`, `.th-vd` — mười ba
     khối bố cục của Hộ Bộ chẳng liên quan gì tới bảng số. */
  /* XÉT TỪNG VẾ, không xét cả chuỗi bộ chọn. Bản trước hỏi "cả
     chuỗi này có dính mặt số không" rồi lại đòi MỌI vế phải được
     phủ — hai độ mịn khác nhau, và chỗ khớp giữa chúng là chỗ báo
     oan. Đo thật ở Hộ Bộ:

       .ten-mo:hover b, .bang tbody tr[data-mo]:hover .ten-mo b,
       .ten-mo:focus-visible b { text-decoration:underline }

     Luật ấy chỉ gạch chân lúc rê chuột, không dính gì tới số. Nó bị
     cờ vì MỘT vế khác trong danh sách có chữ `.bang`, rồi hai vế
     `.ten-mo` — vốn không phải mặt số — bị đòi phải khai tabular-nums.
     Toàn thành 198/198 tụt xuống 197/198 vì đúng một lời vu oan.

     Nay `LA_SO` nhận MỘT VẾ, và một khối chỉ thiếu khi có vế NÀO ĐÓ
     tự nó là mặt số mà chưa được phủ. Khối dùng font mono thì mọi vế
     đều là mặt số — điều kiện `than` lo phần ấy. */
  const LA_SO_VE = (sel, than) => /font-family:\s*var\(--mono\)/.test(than) ||
    /(^|[\s,>+~])(table|td|th)(?![-\w])/.test(sel) ||
    /[.#](bang|cot|o-so)(?![-\w])/.test(sel);
  const LA_SO = (k) => k.sel.split(",").some((s) => LA_SO_VE(s, k.than));
  const matSo = khoi2.filter(LA_SO);

  /* Khai ở gốc là phủ cả trang, khỏi soi tiếp. Đọc trên bản đã bỏ chú
     thích: phép này đòi `body`/`html`/`:root` đứng ngay sau `}` hoặc
     đầu file, mà một đoạn chú thích chen vào giữa là nó trượt — trượt
     kiểu im lặng, vì kết quả chỉ là "soi kỹ hơn cần thiết". */
  const nvGoc = /(?:^|\})\s*(?:body|html|:root)[^{}]*\{[^{}]*tabular-nums/.test(cssMa);

  /* Tính CẢ DI TRUYỀN, không thì thước này thành máy kêu oan. Khai
     `.bang{…tabular-nums}` một lần là phủ hết `.bang th`, `.bang td`,
     `.bang tr td:first-child` — bắt từng rule khai lại là đòi một
     việc thừa, và báo nhầm đều đặn thì người ta bỏ qua cảnh báo, kéo
     theo cả lần nó đúng.

     Phép xấp xỉ, và nói thẳng là xấp xỉ: lấy TỔ HỢP ĐẦU của mỗi bộ
     chọn có khai (`.bang th` → `.bang`), rồi coi mọi bộ chọn cùng tổ
     hợp đầu là đã được phủ. Không phải phân tích tầng thác thật —
     làm thật thì phải dựng cả cây DOM — nhưng nó đúng với lối viết
     CSS của repo này, nơi bảng nào cũng có một lớp gốc mang tên. */
  /* Cắt cả lớp giả: `.o-so:hover` phải quy về `.o-so`. Không cắt thì
     mọi trạng thái hover/focus của một khối ĐÃ khai bị tính là thiếu —
     Hộ Bộ dính đúng một cờ như vậy, và cờ oan thì làm hỏng cả thước. */
  const gocSel = (s) => s.trim().split(/[\s>+~]+/)[0]
    .replace(/:{1,2}[\w-]+(\([^)]*\))?/g, "");
  const daPhu = new Set();
  for (const k of khoi2)
    if (/tabular-nums/.test(k.than))
      for (const s of k.sel.split(",")) daPhu.add(gocSel(s));

  const thieuSo = nvGoc ? [] : matSo.filter((k) =>
    !/tabular-nums/.test(k.than) &&
    k.sel.split(",").some((s) => LA_SO_VE(s, k.than) && !daPhu.has(gocSel(s))));
  const monoCo = matSo.length;
  const monoThieu = thieuSo.length;
  const coBangSo = monoCo > 0 || /<table|class="bang"/.test(html);

  /* BIẾN CSS GỌI RA MÀ KHÔNG AI KHAI — hỏng câm hoàn toàn.

     `border-left:3px solid var(--a)` với `--a` chưa khai là một
     khai báo KHÔNG HỢP LỆ LÚC TÍNH GIÁ TRỊ: trình duyệt không báo
     lỗi, không bỏ qua dòng, mà trả thuộc tính về giá trị kế thừa —
     nên viền đổi sang màu chữ và trông vẫn như một lựa chọn thiết
     kế. Không có gì đỏ lên ở bất kỳ đâu.

     Đo 29/08: Đài Quan Trắc dùng `var(--a)` ở năm chỗ (viền nhấn,
     color-mix, gradient) mà `--a` không khai ở đâu cả; Tử Cấm
     Thành có `--am` và `--am-t` trong halls.css cùng tình trạng.

     CHỈ tính dạng KHÔNG dự phòng. `var(--vien,rgba(...))` là dạng
     hợp lệ và cố ý — mười cung đang dùng nó, và bản đo đầu của
     phép này cờ cả mười một cung vì không phân biệt hai dạng.

     Và coi mọi lần `--x` xuất hiện trong js/html là ĐÃ KHAI: biến
     đặt bằng `style.setProperty` hay `style="--x:…"` thì CSS không
     thấy. Rộng tay ở đây là cố ý — thà sót một lỗi thật còn hơn vu
     oan một cung, vì thước kêu oan thì lần nó đúng cũng bị bỏ qua. */
  const jsVan = file.filter((f) => extname(f) === ".js").map((f) => doc(f)).join("\n");
  const bienKhai = new Set([...cssMa.matchAll(/(--[\w-]+)\s*:/g)].map((m) => m[1]));
  /* CHỈ hai dạng ĐẶT biến thật, không phải mọi lần `--x` hiện ra.
     Bản đầu nhận mọi lần xuất hiện, và nó nuốt luôn lỗi: Đài Quan
     Trắc ship vài trăm KB dữ liệu bot trong scan.js/tin.js, nên
     `--a` khớp đâu đó trong đống văn bản ấy và thước báo ĐẠT trong
     khi cung dùng `var(--a)` mười một lần mà không khai ở đâu cả.
     Rộng tay để khỏi vu oan là đúng; rộng tới mức không bắt được gì
     thì thước chỉ còn là một dòng xanh. */
  for (const m of (jsVan + html).matchAll(/setProperty\(\s*["'](--[\w-]+)/g)) bienKhai.add(m[1]);
  for (const m of (jsVan + html).matchAll(/(--[\w-]+)\s*:/g)) bienKhai.add(m[1]);
  const bienThieu = [...new Set([...cssMa.matchAll(/var\(\s*(--[\w-]+)\s*\)/g)]
    .map((m) => m[1]).filter((v) => !bienKhai.has(v)))];

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

  /* Ngưỡng 12: rộng hơn mọi thang chữ thật (thang của Hộ Bộ có 10
     nấc, và 10 đã là nhiều cho một bảng số dày). Đặt rộng vì thước
     này sinh ra để bắt chỗ KHÔNG có thang, không phải để ép mọi
     cung dùng đúng thang của Hộ Bộ. */
  cham("thang-chu", "Cỡ chữ đi theo thang", soCo <= 12,
    soCo === 0 ? "mọi cỡ chữ đã nằm trong biến"
      : `${soCo} giá trị khác nhau (${new Set(coPx).size} px thẳng + ${nacChu} nấc)` + (soCo > 12 ? " — nhiều hơn một thang thật có" : ""));

  cham("hieu-ung", "Hiệu ứng chỉ chạy transform/opacity", chuyenXau.length === 0,
    chuyenXau.length
      ? `${chuyenXau.length} transition chạm bố cục · ${chuyenXau[0].slice(0, 52)}`
      : "không transition nào chạm bố cục");

  cham("so-cot", "Số liệu đứng cột", coBangSo ? monoThieu === 0 : null,
    !coBangSo ? "cung không có bảng số — không đo"
      : nvGoc ? "khai ở gốc, di truyền cả trang"
      : monoThieu === 0 ? `${monoCo} mặt số (bảng + font mono), chỗ nào cũng khai`
      : `${monoThieu}/${monoCo} mặt số thiếu tabular-nums — số nhảy ngang mỗi lượt đổi`);

  /* design-system (affaan-m/ECC), tải từ Tàng Thư Các: khoảng cách
     phải rút về một thang, cùng lý do với thang cỡ chữ ngay trên.
     Khoảng trắng là thứ mắt bắt được ngay cả khi người xem không gọi
     tên được — mỗi chỗ một con số nghĩa là không ai quyết một thang.

     Ngưỡng 24 rộng hơn hẳn mọi thang thật, vì thước này bắt chỗ
     KHÔNG có thang chứ không ép ai theo thang của cung khác. */
  /* `cssMa`, không phải `css` — thước này cũng dò bằng chuỗi thô nên
     cũng dính cái bẫy chú thích mà `cssMa` ở trên sinh ra để gỡ. Sót
     lại ở đây khi ba thước kia đã được vá; một câu văn giải thích
     "padding: 12px cho vừa vạch" là một giá trị rời rạc trong mắt nó. */
  /* Cùng lý do với `nacChu` ở trên: đếm cả nấc `--k-*`, không thì
     thước lách được bằng một phép đổi tên, và scripts/thang.mjs là
     cái máy làm đúng phép đổi tên đó. */
  const nacCach = new Set([...cssMa.matchAll(/--k-\d+\s*:\s*[\d.]+px/g)].map((m) => m[0])).size;
  const kcPx = new Set([...cssMa.matchAll(/(?:padding|margin|gap)[^;}]*:\s*([^;}]+)/g)]
    .flatMap((m) => m[1].match(/\b\d+px\b/g) || []));
  const kcSo = kcPx.size + nacCach;
  cham("thang-cach", "Khoảng cách đi theo thang", kcSo <= 24,
    kcSo === 0 ? "mọi khoảng cách đã nằm trong biến"
      : `${kcSo} giá trị khác nhau (${kcPx.size} px thẳng + ${nacCach} nấc)` +
        (kcSo > 24 ? " — nhiều hơn một thang thật có" : ""));

  /* accessibility (affaan-m/ECC), WCAG 2.2 AA — tiêu chí 2.4.1
     "Bypass Blocks": phải có đường NHẢY QUA khối lặp lại.

     Mọi cung ở đây đều mở đầu bằng một thanh bên dài: hiệu, 6–54 mục
     phòng, 12 mục cung, rồi mới tới nội dung. Người dùng bàn phím
     phải Tab qua trọn khối đó ở MỖI trang, mỗi lần đổi phòng. Đo
     ngày 29/08: 12 trên 12 cung không có đường nhảy nào.

     Phép đo: một thẻ <a href="#x"> đứng TRƯỚC <nav>, và #x là id có
     thật trong trang. Đứng trước nav là phần quan trọng — một đường
     nhảy nằm sau khối cần nhảy qua thì không nhảy qua được gì.
     Cung không có <nav> thì soi 800 ký tự đầu của <body>. */
  /* `[\s\S]` chứ KHÔNG phải `[sS]`. Bản trước rơi mất hai dấu gạch
     chéo, và `[sS]` là lớp ký tự "chữ s hoặc S" — nên nó chỉ cắt nổi
     những chú thích viết toàn chữ s, tức là không cắt gì cả. Bản vá
     nằm đó, chú thích giải thích bản vá nằm đó, mà phép cắt thì chết.

     Hậu quả không dừng ở một thước im: cung nào có khối chú thích
     nhắc tên thẻ điều hướng ngay trên đường nhảy sẽ bị chấm "chưa
     có", và người viết — vừa mới thêm đường nhảy xong — sẽ tin thước
     mà thêm cái THỨ HAI. Hoàng Thành đang có đúng hai đường nhảy và
     hai khối CSS `.bo-qua` chọi nhau, từ hai phiên khác nhau.

     Lớp lỗi "regex rơi mất dấu gạch chéo" không có gì báo: nó vẫn là
     regex hợp lệ, vẫn chạy, chỉ khớp sai. */
  const htmlSach = html.replace(/<!--[\s\S]*?-->/g, " ");
  const thanTrang = htmlSach.slice(Math.max(0, htmlSach.indexOf("<body")));
  const viNav = thanTrang.search(/<nav\b/);
  const dauTrang = viNav > 0 ? thanTrang.slice(0, viNav) : thanTrang.slice(0, 800);
  const coBoQua = [...dauTrang.matchAll(/<a\b[^>]*href="#([\w-]+)"/g)]
    .some((m) => htmlSach.includes(`id="${m[1]}"`));
  cham("bo-qua", "Có đường nhảy qua thanh bên", coBoQua,
    coBoQua ? "có <a href=\"#…\"> trước thanh bên, trỏ vào id có thật"
      : "chưa có — người dùng bàn phím phải Tab qua cả thanh bên ở mỗi phòng");

  /* frontend-a11y (affaan-m/ECC): tiêu điểm bàn phím phải THẤY ĐƯỢC.
     Đây là lỗi không ai phát hiện cho tới lúc thử rời chuột ra — và
     lúc đó thì người dùng bàn phím đã lạc giữa trang từ lâu. */
  cham("bien-css", "Biến CSS gọi ra đều có khai", bienThieu.length === 0,
    bienThieu.length
      ? `${bienThieu.length} biến chưa khai, không dự phòng: ${bienThieu.slice(0, 6).join(" ")}`
      : "mọi var(--x) không dự phòng đều có nơi khai");

  const coTieuDiem = /:focus-visible/.test(css);
  cham("tieu-diem", "Tiêu điểm bàn phím thấy được", coTieuDiem,
    coTieuDiem ? "có kiểu :focus-visible"
      : "THIẾU :focus-visible — dùng bàn phím thì không biết đang đứng ở đâu");

  /* ── MỘT id MỘT CHỖ ────────────────────────────────────────
     Thước này có vì một ca hỏng THẬT, không vì lý thuyết. Ngày
     29/08 lượt thêm đường nhảy gắn id="than" lên thẻ <main> ở bốn
     cung, mà bên trong <main> đã có sẵn <div id="than"> — chỗ
     app.js vẽ phòng. Trình duyệt lấy thẻ ĐẦU TIÊN mang id đó, nên
     getElementById("than") trả về <main>, và than.innerHTML =
     p.ve() thổi bay đỉnh trang, dải cảnh báo số liệu cũ, vùng loa
     aria-live và cả chân trang khai nguồn — mỗi lần đổi phòng.

     Cả phiếu lẫn cổng chặn đều cho qua: phòng VẪN vẽ ra, chỉ là
     vào nhầm thẻ. "Mọi phòng vẽ được" xanh, năm phép của cổng
     xanh, và bản hỏng lên thẳng site. Vòng tiến hoá của một cung
     khác mới là chỗ phát hiện, một ngày sau.

     Bỏ chú thích trước khi đếm: chính khối chú thích giải thích ca
     hỏng này có nhắc lại id="than" hai lần, và đếm cả nó thì thước
     báo động vì đúng lời giải thích của mình. Dùng lại `htmlSach`
     mà thước đường-nhảy ở trên đã dựng — cùng một bản bỏ chú thích,
     không dựng lại lần hai. */
  /* ── ĐÚNG MỘT <h1> ─────────────────────────────────────────
     accesslint-audit (sickn33/agentic-awesome-skills) — kỹ năng do
     vòng dò kho Tàng Thư Các mang về ngày 29/08: "validate heading
     hierarchy". Đo cả mười hai cung: bậc tiêu đề KHÔNG cung nào
     nhảy cóc, nên phần ấy bỏ — thêm một thước xanh sẵn khắp nơi là
     thêm một dấu ✓ không canh gì.

     Nhưng SỐ h1 thì có trượt: Tử Cấm Thành mang hai cái, một là tên
     cung ("Tử Cấm Thành") và một là tiêu đề trang ("Một AI Trader
     Runtime, mổ ra xem"). Trình đọc màn hình dựng mục lục trang từ
     bậc tiêu đề; hai h1 là hai gốc, và người dùng nhảy theo tiêu đề
     sẽ thấy trang có hai phần ngang hàng không rõ cái nào chứa cái
     nào. */
  const soH1 = (htmlSach.match(/<h1\b/g) || []).length;
  cham("mot-h1", "Đúng một tiêu đề gốc", soH1 === 1,
    soH1 === 1 ? "một <h1>, mục lục trang có đúng một gốc"
      : soH1 === 0 ? "KHÔNG có <h1> — trang không có gốc mục lục"
      : `${soH1} thẻ <h1> — trình đọc màn hình thấy ${soH1} gốc ngang hàng`);

  /* ── Ô NHẬP CÓ NHÃN ────────────────────────────────────────
     Cùng nguồn: "ensure form inputs have associated labels".

     `placeholder` KHÔNG phải nhãn. Nó biến mất ngay khi người ta gõ
     chữ đầu tiên, và phần lớn trình đọc màn hình không đọc nó thay
     cho tên. Đo 29/08: Đài Quan Trắc có ô lệnh
     `<input id="cmdin" placeholder="Đi tới mục, chiến trường…">` —
     không aria-label, không <label for>. Người dùng bàn phím Tab
     tới đó và nghe "vùng nhập văn bản", hết.

     Cung không có ô nhập nào thì KHÔNG ĐO ĐƯỢC, không phải đạt —
     cho một cung điểm vì nó thiếu thứ để chấm là làm mẫu số nói
     dối. */
  const nhanFor = new Set([...htmlSach.matchAll(/<label\b[^>]*\bfor="([^"]+)"/g)].map((m) => m[1]));
  const oNhap = [...htmlSach.matchAll(/<(input|select|textarea)\b([^>]*)>/g)]
    .filter((m) => !/type="(hidden|submit|button|image)"/.test(m[2]));
  const oCam = oNhap.filter((m) => {
    if (/aria-label|aria-labelledby|title="/.test(m[2])) return false;
    const id = (m[2].match(/\bid="([^"]+)"/) || [])[1];
    return !(id && nhanFor.has(id));
  });
  cham("o-nhap", "Ô nhập có nhãn", oNhap.length ? oCam.length === 0 : null,
    !oNhap.length ? "cung không có ô nhập nào — không đo"
      : oCam.length === 0 ? `${oNhap.length} ô nhập, chỗ nào cũng có nhãn`
      : `${oCam.length}/${oNhap.length} ô nhập chỉ có placeholder — nó biến mất ngay khi gõ`);

  const demId = new Map();
  for (const m of htmlSach.matchAll(/\sid="([^"]+)"/g))
    demId.set(m[1], (demId.get(m[1]) || 0) + 1);
  const idTrung = [...demId].filter(([, n]) => n > 1);
  cham("id-trung", "Mỗi id chỉ một chỗ", idTrung.length === 0,
    idTrung.length
      ? `${idTrung.length} id trùng: ${idTrung.map(([k, n]) => `${k}×${n}`).join(", ").slice(0, 90)}` +
        ` — getElementById trả thẻ ĐẦU TIÊN, phần còn lại thành vô hình với JS`
      : `${demId.size} id, không cái nào trùng`);

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
  "bien-css": ["css", "design system", "tokens", "refactor", "lint"],
  "bo-qua": ["accessibility", "a11y", "keyboard", "wcag", "skip link", "navigation"],
  "thang-chu": ["typography", "type scale", "font", "design system", "tokens"],
  "hieu-ung": ["animation", "motion", "performance", "transition", "compositor"],
  "so-cot": ["typography", "table", "data", "tabular", "dashboard"],
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

/* ── ỨNG VIÊN MỚI TỪ DÒ KHO ────────────────────────────────
   kyNang() ở trên có hai chỗ hẹp, và cả hai đều cố ý: nó chỉ nhìn
   nhóm "giao-dien" và "lap-trinh", và chỉ khớp theo từ khoá của
   thước ĐANG TRƯỢT. Hẹp như vậy thì lượt vá bám sát điểm yếu —
   nhưng cái giá là vòng tiến hoá KHÔNG BAO GIỜ tự tìm ra thứ đáng
   học mà ta chưa nghĩ tới việc đo. Bốn lĩnh vực kiểm thử · dữ liệu
   · hạ tầng · nghiên cứu không có cửa nào vào đề bài.

   scripts/do-kho.mjs quét cả 3.696 kỹ năng mỗi tuần theo sáu lĩnh
   vực, bỏ những cái đã khai thác, và để đề xuất ở
   factory/kho-de-xuat.json. Ở đây ghép hai mục đầu bảng vào ĐUÔI
   `kyNang` — đúng cái khoá mà cả bảy đề bài đã dặn model đọc bằng
   WebFetch. Nối ở một chỗ này thì bảy vòng cùng hưởng; sửa bảy
   prompt là bảy cơ hội sót một cung.

   HAI mục thôi, và ở đuôi. Đây là gợi ý mở rộng chứ không phải việc
   chính của lượt: để nhiều hơn thì phần khớp-với-điểm-yếu bị loãng,
   và model có 24 lượt gọi chứ không vô hạn.

   Đổi `doc` sang đường raw. Bản dò ghi đường blob của github.com —
   đọc được, nhưng đó là cả một trang HTML cho một file văn bản, và
   nó khác đường mà kyNang() đang dùng. Hai kiểu đường cho cùng một
   loại tài liệu là thứ sớm muộn có người sửa nhầm một bên. */
function themUngVienMoi(k) {
  try {
    const p = join(ROOT, "factory", "kho-de-xuat.json");
    if (!co(p)) return;
    const d = JSON.parse(doc(p));
    if (!Array.isArray(d.deXuat)) return;
    const daCo = new Set(k.skill.map((s) => s.kho + "/" + s.duong));

    /* XOAY VÒNG, không đánh dấu "đã dùng".
       Cách hiển nhiên là ghi mục đã đưa vào sổ kho-da-dung.json rồi
       lượt sau bỏ qua. Nó hỏng ở đây vì hai lẽ đo được:
       — Kho đề xuất chỉ giữ 5–6 mục, mà mỗi ngày có BẢY cung chạy
         de-bai. Đánh dấu thì hết sạch trong một ngày, rồi sáu ngày
         còn lại không cung nào thấy gì cho tới lượt quét tuần sau.
       — "Đã đưa tới model" không phải "đã dùng". Ghi vào sổ khai
         thác một thứ model có thể đã đọc lướt rồi bỏ là làm sổ đó
         nói dối, và sổ ấy chính là thứ quyết định lượt quét sau bỏ
         qua cái gì.
       Xoay theo (ngày, cung) thì mỗi cung mỗi ngày thấy một cặp
       khác, qua một tuần cả kho được đọc nhiều lượt bởi nhiều cung,
       và không phải ghi gì cả — de-bai chạy trên runner, thêm một
       file phải commit là thêm một chỗ hỏng. */
    const ngay = Math.floor(Date.now() / 86400000);
    let bam = 0;
    for (const c of CUNG) bam = (bam * 31 + c.charCodeAt(0)) % 9973;
    const batDau = d.deXuat.length ? (ngay + bam) % d.deXuat.length : 0;
    const xoay = d.deXuat.map((_, i) => d.deXuat[(batDau + i) % d.deXuat.length]);

    for (const u of xoay) {
      if (k.skill.filter((s) => s.moi).length >= 2) break;
      if (!u.kho || !u.duong || daCo.has(u.kho + "/" + u.duong)) continue;
      k.skill.push({
        ten: u.ten, kho: u.kho, duong: u.duong, nhom: "do-kho", sao: null,
        giayPhep: u.giayPhep || null, khop: u.lv || [],
        moTa: (u.mo || "").slice(0, 220),
        moi: true,
        vi: "MỚI dò được từ Tàng Thư Các, chưa cung nào dùng. Không bắt " +
            "buộc phải theo — đọc, và chỉ áp dụng nếu nó thật sự hợp cung này.",
        doc: `https://raw.githubusercontent.com/${u.kho}/HEAD/${u.duong}/SKILL.md`
      });
    }
  } catch { /* Dò kho hỏng KHÔNG được phép chặn vòng tiến hoá: đây là
                phần thêm, không phải phần chính. Im lặng bỏ qua rồi
                lượt sau dò lại. */ }
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
  /* docShell — một chỗ duy nhất, xem scripts/mang-truoc.mjs. Regex cũ ở
     đây neo đầu dòng nên bỏ qua đường thứ hai trở đi trên cùng một dòng.
     dai-quan-trac viết hai đường một dòng, nên bang.js và nen.js — 30 KB —
     vô hình với cả bốn script chép cùng regex này. */
  const shell = docShell(sw).duong.map((f) => "./" + f);
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
/* Đọc lại đề bài vừa dựng rồi tóm tắt — KHÔNG đo lại, vì đo lại là
   tốn thêm một lượt dựng 54 phòng cho một dòng chữ.

   `--ra <file>`: ghi `yeu=N` vào đó (workflow truyền $GITHUB_OUTPUT).
   stdout in dòng ::notice:: kèm tên thước đang trượt.

   Có lệnh này để BASH KHÔNG PHẢI GHÉP CHUỖI quanh JSON nữa. Bản
   trước ghép bằng `$(node -e \"…\")` lồng trong nháy kép của echo và
   bash báo syntax error, làm hỏng cả bước suốt chín lượt. */
if (LENH === "tom-tat") {
  const p = DUONG("assets", "data", "de-bai-tien-hoa.json");
  if (!co(p)) thoat("chưa có đề bài — chạy `de-bai` trước.");
  const d = JSON.parse(doc(p));
  const yeu = d.phieu.diem.filter((x) => !x.dat);
  const raFile = co_("ra");
  if (raFile) await writeFile(raFile, `yeu=${yeu.length}\n`, { flag: "a" });
  console.log(`::notice::Phiếu đo ${CUNG}: ${d.phieu.dat}/${d.phieu.tong} đạt · ` +
    `${yeu.length} điểm yếu` + (yeu.length ? ` · trượt: ${yeu.map((x) => x.ten).join(", ")}` : ""));
  process.exit(0);
}

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
  themUngVienMoi(k);

  /* ── THƯỚC NÀO CHỮA KHÔNG BẰNG GIAO DIỆN THÌ PHẢI NÓI RA ────
     Một thước trượt không tự nói cách chữa nó nằm ở đâu. Model
     chỉ chạm được bốn file giao diện, nên nếu điểm yếu thật ra
     nằm ở đường ống dữ liệu, nó vẫn sẽ vá — bằng đúng thứ nó
     chạm được. Với "ô trống" thì thứ nó chạm được là chỗ làm
     dấu "—" biến mất khỏi mắt, chứ không phải chỗ làm số liệu
     có thật. Vòng tiến hoá khi ấy đang tối ưu cho việc che.

     Nên đề bài mang theo lời dặn cho những thước như vậy. */
  const LUU_Y = {
    "o-trong":
      'Dấu "—" là DỮ LIỆU HỤT, không phải lỗi giao diện. Giấu ô trống đi ' +
      'là nói dối người xem, và vẫn làm điểm lên — đừng làm thế. Cách đúng: ' +
      'để ô trống tự nói nó trống VÌ SAO, và chỉ ra một việc kế tiếp ' +
      '(baseline-ui, kho ibelick/ui-skills: "MUST give empty states one clear ' +
      'next action"). Còn nguồn số thì nằm ở scripts/build-*.mjs — NGOÀI phạm ' +
      'vi lượt này, đừng đụng.'
  };
  const luuY = phieu.diem
    .filter((d) => d.dat === false && LUU_Y[d.ma])
    .map((d) => ({ thuoc: d.ma, dan: LUU_Y[d.ma] }));

  const ra = DUONG("assets", "data", "de-bai-tien-hoa.json");
  await mkdir(dirname(ra), { recursive: true });
  await writeFile(ra, JSON.stringify({
    ghiChu: "SINH TỰ ĐỘNG bởi scripts/tien-hoa.mjs. Đừng sửa tay, đừng commit.",
    cung: CUNG, phieu, luuY, kyNang: k.skill, quetSkillLuc: k.quetLuc
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

    /* ── NHẬT KÝ TIẾN HOÁ ────────────────────────────────────
       Đề bài dặn model ghi việc nó vừa làm vào khoá `daLam`. Nhưng
       file đề bài nằm trong .gitignore, nên lời khai đó bị XOÁ sau
       mỗi lượt. Năm lượt đầu tiên của Hộ Bộ đã mất trắng lý do như
       thế, và hậu quả không nhẹ: sổ nhà máy chỉ ghi "6/7 → 6/7" năm
       lần liền, nên nhìn từ ngoài thì vòng này trông như chạy không
       tải — trong khi lượt 27/08 thật ra vá một lỗi a11y có thật
       (ngăn hồ sơ đóng bằng transform vẫn nằm trong luồng Tab).

       Một vòng tiến hoá mà thành quả không đọc được thì sớm muộn có
       người tắt nó đi, và họ tắt đúng thứ đang làm việc.

       Ghi ở đây chứ không ở workflow là có chủ ý: cổng chặn là chỗ
       DUY NHẤT biết cả phiếu trước lẫn phiếu sau, và nó chạy đúng
       một lần cho mỗi cung mỗi lượt. Đặt vào đây thì mọi cung có
       nhật ký mà không phải sửa YAML ở ba chỗ — chỗ mà mỗi lần sửa
       là một cơ hội sót một cung.

       Chỉ ghi khi có `--so`, tức là chỉ trong vòng tiến hoá. Gõ tay
       `npm run cong <cung>` để soát thì không đẻ ra dòng rác nào.

       NHƯNG `--so` KHÔNG phân biệt được CI với người: chạy thử vòng
       lặp bằng tay (`cong <cung> --so <phiếu>`) cũng đẻ ra dòng ở
       đây, và dòng ấy trông y hệt một lượt tiến hoá thật. Đã dính
       29/08 khi thử vòng xoay trên bảy cung: bảy dòng "15/15→15/15 ·
       nhan" trong khi không model nào chạy. Chạy thử xong thì
       `git checkout -- factory/tien-hoa.jsonl` trước khi commit —
       cuốn nhật ký này là thứ đã giúp tìm ra lỗi id trùng, đừng làm
       bẩn nó. */
    try {
      const deBai = DUONG("assets", "data", "de-bai-tien-hoa.json");
      const daLam = co(deBai) ? (JSON.parse(doc(deBai)).daLam || null) : null;
      const soNk = join(ROOT, "factory", "tien-hoa.jsonl");
      mkdirSync(dirname(soNk), { recursive: true });
      appendFileSync(soNk, JSON.stringify({
        luc: new Date().toISOString(), cung: CUNG,
        truoc: `${cu.dat}/${cu.tong}`, sau: `${moi.dat}/${moi.tong}`,
        nhan: loi.length ? "tra-lai" : "nhan",
        daLam: typeof daLam === "string" ? daLam.slice(0, 600) : daLam
      }) + "\n", "utf8");
    } catch (e) {
      /* Không ném: ghi nhật ký hỏng không được phép làm cổng chặn
         trượt, vì cổng mới là thứ giữ site khỏi vỡ. */
      console.log(`  (không ghi được nhật ký tiến hoá: ${e.message.slice(0, 80)})`);
    }
  }
  process.exit(loi.length ? 1 : 0);
} else {
  thoat(`Lệnh lạ "${LENH}". Có: do · ky-nang · de-bai · tom-tat · cong`);
}
