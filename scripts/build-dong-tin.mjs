#!/usr/bin/env node
/* ═══════════════════════════════════════════════════════
   DÒNG TIN — bài viết thật, ảnh thật, và một lớp phán đoán
   của model được ĐÁNH DẤU LÀ PHÁN ĐOÁN.

   Chạy ba bước, giống hệt đường của bản quét, và tách ba bước
   vì cùng một lý do:

     1. --de-bai   lấy RSS → chọn bài → assets/data/tin-de-bai.json
     2. (Actions)  Claude Code Action đọc đề bài, viết
                   assets/data/tin-phan-tich.json — JSON THÔ
     3. (không cờ) đọc cả hai, kiểm, dựng assets/js/tin.js

   ĐỪNG cho model ghi thẳng tin.js. Đó là file trình duyệt nạp; một
   lỗi cú pháp của model thành một trang trắng.

   ── VÌ SAO RSS CHỨ KHÔNG PHẢI GDELT ────────────────────
   GDELT DOC API có ảnh (`socialimage`) và không cần khoá, nhưng nó
   trả 429 ngay cả khi nghỉ 20 giây — hạn mức dùng chung cho cả thế
   giới, không đoán trước được. Nặng hơn: nó chọn hộ mình nguồn nào
   được vào. Yêu cầu ở đây là "nguồn uy tín", mà uy tín thì phải do
   người chọn và ghi rõ, không để một API xếp hạng thay.

   Nên NGUON dưới đây là danh sách TƯỜNG MINH, và mỗi nguồn mang một
   nhãn `loai` hiện lên giao diện. Tân Hoa Xã nằm trong danh sách,
   nhưng nằm kèm nhãn "báo nhà nước Trung Quốc" — đọc được thì phải
   biết mình đang đọc ai. Đó chính là "sáu dấu ≠" của cung này áp
   vào chỗ lấy tin.

   ── RANH GIỚI PHẢI GIỮ ─────────────────────────────────
   Bài báo là DỮ LIỆU. Phân tích của model là PHÁN ĐOÁN. Hai thứ đó
   không được trộn vào nhau trong giao diện, và không được trộn ở
   đây: mỗi mục có `bai` (nguyên văn từ nguồn) và `ai` (model viết),
   tách hẳn hai nhánh.

   Mỗi phán đoán buộc phải trỏ vào một mắt xích CÓ THẬT của đúng chủ
   thể đó. Model bịa id thì mục bị loại, không phải được sửa hộ —
   sửa hộ là dạy đường ống chấp nhận rác.
   ═══════════════════════════════════════════════════════ */
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const GOC = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const APP = resolve(GOC, "dai-quan-trac");
const RA_DE = resolve(APP, "assets/data/tin-de-bai.json");
const RA_PT = resolve(APP, "assets/data/tin-phan-tich.json");
const RA_JS = resolve(APP, "assets/js/tin.js");

/* Bao nhiêu bài mỗi chủ thể được đưa cho model. Đây là cái van chi
   phí duy nhất của bước 2 — model đọc từng bài, nên số này nhân
   thẳng vào lượt dùng. 6 × 3 chủ thể = 18 bài một lượt. */
const MOI_CHU_THE = 6;
/* Điểm tối thiểu để một bài được coi là có liên quan. Không có
   ngưỡng thì mọi tin trong feed đều lọt, và bảng thành máy đọc RSS
   chứ không phải đài quan trắc. */
const DIEM_TOI_THIEU = 4;
/* Mỗi nguồn được tối đa bấy nhiêu bài trong MỘT chủ thể. Không có
   trần này thì bảng Trung Quốc thành 4/6 bài của riêng SCMP — và
   một bảng chép lại một toà soạn thì không phải một bảng quan trắc. */
const TOI_DA_MOI_NGUON = 2;
/* Cũ hơn bấy nhiêu ngày thì loại hẳn, dù điểm từ khoá cao tới đâu.
   Feed VietnamNet giữ tới 1000 mục nên không có trần này là tin
   tháng 6 xếp trên tin hôm nay. */
const CU_NHAT_NGAY = 14;
/* Và mỗi feed chỉ lấy phần ĐẦU — RSS xếp mới trước cũ, nên đây là
   cách rẻ nhất để một feed khổng lồ không nuốt cả rổ. */
const MOI_FEED = 40;

/* ── NGUỒN ───────────────────────────────────────────────
   Đã thử và loại: Reuters (không còn feed công khai), AP (403),
   Bloomberg/FT/WSJ (không có feed miễn phí), Caixin Global và
   Global Times (404), VnEconomy (feed rỗng), The Diplomat (DNS
   không phân giải được từ đây). Ghi lại để đừng ai thử lại vòng
   nữa. */
const NGUON = [
  { id:"bbc", nuoc:"qt",       ten:"BBC",            loai:"hãng tin quốc tế",
    feed:["https://feeds.bbci.co.uk/news/business/rss.xml",
          "https://feeds.bbci.co.uk/news/world/rss.xml"] },
  { id:"guardian", nuoc:"qt",  ten:"The Guardian",   loai:"báo quốc tế",
    feed:["https://www.theguardian.com/business/rss",
          "https://www.theguardian.com/world/rss"] },
  { id:"aljazeera", nuoc:"qt", ten:"Al Jazeera",     loai:"hãng tin quốc tế",
    feed:["https://www.aljazeera.com/xml/rss/all.xml"] },
  { id:"cna", nuoc:"qt",       ten:"CNA",            loai:"hãng tin khu vực · Singapore",
    feed:["https://www.channelnewsasia.com/api/v1/rss-outbound-feed?category=6511"] },
  { id:"scmp", nuoc:"cn",      ten:"SCMP",           loai:"báo Hong Kong",
    feed:["https://www.scmp.com/rss/4/feed", "https://www.scmp.com/rss/92/feed"] },
  /* Nikkei Asia cho tới 02/09/2026: feed nar trả HTTP 200 và 50 mục,
     nhưng là RSS 1.0/RDF và mỗi <item> chỉ có title với link — KHÔNG
     thẻ ngày nào. Đường ống này xếp hạng theo độ mới, nên bài không
     ngày luôn bị vứt: nguồn góp 0 bài suốt, và phép canh feed ôi đọc
     ra "mới nhất 20699 ngày trước" chính là dấu của chuyện đó.

     Hai feed khác của Nikkei (china-up-close, business) đều 404. Japan
     Times giữ được góc nhìn báo Nhật, 30 mục, có ngày, mới trong ngày. */
  { id:"japantimes", nuoc:"qt", ten:"The Japan Times", loai:"báo Nhật",
    feed:["https://www.japantimes.co.jp/feed/"] },
  /* Nằm trong danh sách vì nó cho biết Bắc Kinh MUỐN nói gì — đó là
     dữ liệu thật về ý định, miễn là đọc đúng nó là gì. Nhãn `loai`
     hiện ngay trên thẻ để không ai đọc nhầm thành nguồn độc lập. */
  /* Tân Hoa Xã cho tới 02/09/2026: feed worldrss.xml trả HTTP 200,
     20 mục, KHÔNG lỗi nào — nhưng mục mới nhất là 3144 ngày trước
     (chuyến thăm của Pence, bão Lan, Mỹ rút UNESCO — toàn 2017).
     Bộ lọc ngày vứt sạch, nguồn góp 0 bài, và nhãn viền vàng "BÁO
     NHÀ NƯỚC" chưa từng một lần hiện lên site.

     Đã thử ba nguồn thay: english.news.cn 404, chinadaily cũng kẹt ở
     2017, globaltimes/outbrain thưa và cũ. CGTN là đài nhà nước, 50
     mục, đều trong ngày. */
  { id:"cgtn",   nuoc:"cn",    ten:"CGTN",           loai:"BÁO NHÀ NƯỚC Trung Quốc",
    feed:["https://www.cgtn.com/subscribe/rss/section/china.xml"] },
  { id:"vnexpress", nuoc:"vn", ten:"VnExpress",      loai:"báo Việt Nam",
    feed:["https://vnexpress.net/rss/kinh-doanh.rss"] },
  { id:"tuoitre", nuoc:"vn",   ten:"Tuổi Trẻ",       loai:"báo Việt Nam",
    feed:["https://tuoitre.vn/rss/kinh-doanh.rss"] },
  { id:"thanhnien", nuoc:"vn", ten:"Thanh Niên",     loai:"báo Việt Nam",
    feed:["https://thanhnien.vn/rss/kinh-te.rss"] },
  { id:"vietnamnet", nuoc:"vn",ten:"VietnamNet",     loai:"báo Việt Nam",
    feed:["https://vietnamnet.vn/rss/kinh-doanh.rss"] }
];

/* ── TỪ KHOÁ MỖI CHỦ THỂ ─────────────────────────────────
   `manh` ăn 3 điểm, `nhe` ăn 1. Một bài phải đủ DIEM_TOI_THIEU mới
   vào. Nhờ hai bậc, "Vietnam" một mình không đủ — phải có thêm một
   từ về cơ chế thì mới thành tin của đài này. */
const NHA = { vn:["vn"], tq:["cn"], tk:["vn","cn"] };

const KHOA = {
  vn: {
    manh:["vietnam","viet nam","việt nam","hanoi","hà nội","vnd","dong currency",
          "state bank of vietnam","ngân hàng nhà nước"],
    nhe:["tariff","thuế quan","export","xuất khẩu","import","nhập khẩu","fdi",
         "manufacturing","sản xuất","credit","tín dụng","bank","ngân hàng",
         "interest rate","lãi suất","exchange rate","tỷ giá","property","bất động sản",
         "transshipment","chuyển tải","origin","xuất xứ","section 301","supply chain",
         "chuỗi cung ứng","electricity","lưới điện","giá điện","thiếu điện","evn",
         "port","cảng","semiconductor","samsung"]
  },
  tq: {
    manh:["china","chinese","beijing","trung quốc","bắc kinh","xi jinping","tập cận bình",
          "communist party","politburo","bộ chính trị","pboc","yuan","renminbi"],
    /* Danh sách này từng có 26 từ trong khi Việt Nam có 34 — hẹp hơn,
       dù Trung Quốc được sáu nguồn TIẾNG ANH đưa tin còn Việt Nam chủ
       yếu bốn nguồn tiếng Việt. Hệ quả đo được ngày 02/09: 486 mục thô,
       cổng địa lý loại 347 (đúng — phần lớn tin BBC/Guardian không về
       Trung Quốc), rồi cổng cơ chế loại thêm 115, còn 9 bài và CẢ CHÍN
       đều của SCMP — nên trần hai bài mỗi nguồn cắt xuống 2. Trang
       Trung Quốc mỏng đi vì thiếu TỪ, không phải vì thiếu tin.

       Thiếu rõ nhất là những từ trung tâm của chính mảng này mà bảng
       Việt Nam đã có và đã chạy tốt: tariff, trade, supply chain,
       investment, lãi suất, tỷ giá. Cùng vài từ riêng của Trung Quốc:
       trừng phạt, đất hiếm, hải quan. */
    nhe:["property","bất động sản","evergrande","local government","lgfv","debt","nợ",
         "export","xuất khẩu","import","nhập khẩu","semiconductor","chip","bán dẫn",
         "purge","thanh lọc","pla","military","quân đội","stimulus","kích thích",
         "deflation","giảm phát","youth unemployment","thất nghiệp","retail sales",
         "bán lẻ","credit","tín dụng","tariff","thuế quan","trade","thương mại",
         "supply chain","chuỗi cung ứng","investment","đầu tư","manufacturing",
         "sản xuất","factory","nhà máy","interest rate","lãi suất","exchange rate",
         "tỷ giá","inflation","lạm phát","sanction","trừng phạt","rare earth",
         "đất hiếm","customs","hải quan","port","cảng"]
  },
  /* Tổng kết đo KHỚP NỐI, nên nó chỉ nhận bài chạm tới CẢ HAI phía
     hoặc chạm tới chính cái mối nối — chuỗi cung ứng, chuyển tải,
     Biển Đông, eo biển. Một tin thuần nội địa của một nước không
     thuộc về đây. */
  /* Với Tổng kết còn một dấu mạnh nữa không nằm trong danh sách từ:
     bài nào nhắc CẢ Việt Nam LẪN Trung Quốc thì tự nó đã nói về
     khớp nối. Xem `caHai` dưới chamDiem. */
  tk: {
    caHai:[["vietnam","việt nam"],["china","chinese","trung quốc"]],
    manh:["supply chain","chuỗi cung ứng","transshipment","chuyển tải","rules of origin",
          "quy tắc xuất xứ","south china sea","biển đông","hormuz","strait","eo biển",
          "decoupling","de-risking","nearshoring","friendshoring"],
    nhe:["vietnam","việt nam","china","trung quốc","asean","tariff","thuế quan",
         "factory","nhà máy","relocation","dịch chuyển","oil","dầu","shipping","vận tải",
         "trade war","chiến tranh thương mại","us-china","mỹ-trung","export control"]
  }
};

/* Bài PR doanh nghiệp trộn chung feed kinh tế. Dấu vân tay rất đều,
 * và một bảng quan trắc có tin "tri ân khách hàng" thì mất hết uy
 * tín của cả những dòng đúng bên cạnh. */
const CAM = ["ra mắt","khuyến mãi","ưu đãi","tri ân","vinh danh","giải thưởng",
  "đồng hành cùng","giới thiệu giải pháp","định vị thương hiệu","khẳng định vị thế",
  "nâng tầm","kiến tạo","dấu ấn","bứt phá","trải nghiệm","tặng","quà",
  "top 10","top 50","bình chọn","lễ ký kết","nối lại đường bay","mở bán"];

/* ── TIỆN ÍCH ────────────────────────────────────────────*/
const nghi = (ms) => new Promise((r) => setTimeout(r, ms));

/* Bảng thực thể HTML. Feed tiếng Việt dùng rất nhiều thực thể có
   tên (&agrave; &ocirc;…), bỏ qua là tiêu đề hiện ra đầy rác. */
const THUC_THE = { amp:"&", lt:"<", gt:">", quot:'"', apos:"'", nbsp:" ", ndash:"–", mdash:"—",
  lsquo:"‘", rsquo:"’", ldquo:"“", rdquo:"”", hellip:"…" };
function giaiMa(s) {
  return String(s || "")
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(+d))
    .replace(/&([a-z]+);/gi, (m, t) => {
      const k = THUC_THE[t.toLowerCase()];
      if (k !== undefined) return k;
      /* Thực thể có tên kiểu &agrave; — dựng qua một vòng nữa bằng
         bảng Latin-1 rút gọn. Không nhận ra thì TRẢ NGUYÊN, đừng
         nuốt mất ký tự. */
      const L1 = "agrave à aacute á acirc â atilde ã egrave è eacute é ecirc ê igrave ì iacute í ograve ò oacute ó ocirc ô otilde õ ugrave ù uacute ú yacute ý ntilde ñ ccedil ç Agrave À Aacute Á Acirc Â Egrave È Eacute É Ocirc Ô Ugrave Ù".split(" ");
      const i = L1.indexOf(t);
      return i >= 0 && i % 2 === 0 ? L1[i + 1] : m;
    });
}
const bo = (s) => giaiMa(String(s || "").replace(/<[^>]*>/g, " ")).replace(/\s+/g, " ").trim();

/* Lấy nội dung một thẻ. RSS trộn CDATA với văn bản thường nên phải
   chịu được cả hai. */
function the(x, ten) {
  const m = x.match(new RegExp("<" + ten + "(?:\\s[^>]*)?>([\\s\\S]*?)</" + ten + ">", "i"));
  if (!m) return "";
  return m[1].replace(/^\s*<!\[CDATA\[/, "").replace(/\]\]>\s*$/, "");
}

/* Ảnh: bốn chỗ khác nhau tuỳ nguồn, thử theo thứ tự chắc chắn dần.
   SCMP dùng media:content, VnExpress dùng enclosure, Thanh Niên nhét
   <img> vào trong description. Không có thì trả null — thẻ vẫn dựng
   được, chỉ là không ảnh. */
function layAnh(x) {
  const thu = [
    /<media:content[^>]*\burl="([^"]+)"/i,
    /<media:thumbnail[^>]*\burl="([^"]+)"/i,
    /<enclosure[^>]*\burl="([^"]+)"[^>]*type="image\//i,
    /<enclosure[^>]*type="image\/[^"]*"[^>]*\burl="([^"]+)"/i,
    /<img[^>]*\bsrc="([^"]+)"/i
  ];
  for (const r of thu) {
    const m = x.match(r);
    if (!m) continue;
    const u = giaiMa(m[1]);
    /* Chỉ nhận https. Ảnh http trên trang https bị trình duyệt chặn
       im lặng — thẻ trống mà không lỗi nào báo. */
    if (/^https:\/\//i.test(u)) return u;
  }
  return null;
}

function docFeed(xml, ng) {
  const khoi = xml.match(/<item[\s>][\s\S]*?<\/item>/gi) || xml.match(/<entry[\s>][\s\S]*?<\/entry>/gi) || [];
  return khoi.map((x) => {
    const link = bo(the(x, "link")) || (x.match(/<link[^>]*href="([^"]+)"/i) || [])[1] || "";
    const tieu = bo(the(x, "title"));
    const mo = bo(the(x, "description") || the(x, "summary") || the(x, "content:encoded"));
    const ngay = bo(the(x, "pubDate") || the(x, "published") || the(x, "updated"));
    return { tieu, link: giaiMa(link), mo: mo.slice(0, 420), anh: layAnh(x),
             ngay: chuanNgay(ngay), nguon: ng.id, nuoc: ng.nuoc };
  }).filter((b) => b.tieu && /^https?:\/\//.test(b.link));
}

function chuanNgay(s) {
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) return null;
  return d.toISOString().slice(0, 10);
}

function tuoiNgay(ngay) {
  if (!ngay) return 999;
  return Math.floor((Date.now() - new Date(ngay + "T00:00:00Z").getTime()) / 86400000);
}

/* Khớp theo TỪ, không theo chuỗi con. Không dùng \\b của regex vì nó
 * dựa trên [A-Za-z0-9_] nên tiếng Việt có dấu bị cắt sai ngay giữa
 * từ. Tự kiểm hai ký tự kề bên thì đúng cho cả hai bảng chữ. */
const CHU = /[\p{L}\p{N}]/u;
function chua(hay, kim) {
  let i = hay.indexOf(kim);
  while (i >= 0) {
    const truoc = i === 0 ? "" : hay[i - 1];
    const sau = hay[i + kim.length] || "";
    if (!CHU.test(truoc) && !CHU.test(sau)) return true;
    i = hay.indexOf(kim, i + 1);
  }
  return false;
}

/* `so` là cuốn sổ tuỳ chọn ghi bài rụng ở CỬA NÀO. Hai cửa có hai
   cách chữa khác hẳn: rụng ở địa lý thì thêm từ khoá tên nước, rụng
   ở cơ chế thì nới danh sách từ cơ chế. Không tách ra thì cả hai
   trông giống nhau — đều là "0 điểm" — và người sửa đoán bừa. */
function chamDiem(b, k, nha, so) {
  const t = (b.tieu || "").toLowerCase(), m = (b.mo || "").toLowerCase();
  /* Chặn trước, rẻ nhất */
  if (CAM.some((w) => t.includes(w))) return 0;
  let d = 0, comanh = false;
  /* Tiêu đề nặng hơn tóm tắt: một từ khoá trong tiêu đề nói bài đó
     VỀ chuyện ấy, còn trong tóm tắt thì thường chỉ là nhắc qua. */
  for (const w of k.manh) {
    if (chua(t, w)) { d += 3; comanh = true; }
    else if (chua(m, w)) { d += 1; comanh = true; }
  }
  /* CỔNG ĐỊA LÝ. Bài của báo quốc tế phải nhắc tên nước — không thì
     tin "Indonesia macaque export" lọt vào bảng Việt Nam mà không
     nhắc Việt Nam lần nào. Nhưng bài của báo TRONG NƯỚC thì mặc
     nhiên qua cổng: mọi bài của Tuổi Trẻ đều về Việt Nam, và bắt
     chúng viết chữ "Việt Nam" ra là lọc ngược. */
  /* Dấu mạnh phụ: đủ mọi nhóm trong `caHai` cùng có mặt. */
  if (k.caHai && k.caHai.every((nhom) => nhom.some((w) => chua(t, w) || chua(m, w)))) {
    d += 4; comanh = true;
  }
  if (!comanh && !nha.includes(b.nuoc)) { if (so) so.diaLy++; return 0; }
  if (nha.includes(b.nuoc)) d += 2;
  /* CỔNG CƠ CHẾ. Từ về cơ chế phải nằm NGAY TRONG TIÊU ĐỀ. Trong
     tóm tắt thì mọi bài PR ngân hàng cũng có chữ "tín dụng". */
  let coche = 0;
  for (const w of k.nhe) { if (chua(t, w)) { d += 2; coche++; } else if (chua(m, w)) d += 1; }
  if (!coche) { if (so) so.coChe++; return 0; }
  /* Độ mới CỘNG vào chứ không nhân: một tin rất liên quan của tuần
     trước vẫn nên thắng một tin hôm nay chỉ chạm hờ. Nhưng ngang
     điểm nội dung thì tin mới luôn thắng. */
  const tu = tuoiNgay(b.ngay);
  d += tu <= 1 ? 5 : tu <= 3 ? 3 : tu <= 7 ? 1 : 0;
  return d;
}

/* Đọc CHAIN id thật của từng chủ thể từ chính file dữ liệu trình
   duyệt — một nguồn sự thật, không chép tay sang đây. */
function machCua(tep, bien) {
  const hop = { window: {} };
  vm.createContext(hop);
  vm.runInContext(readFileSync(resolve(APP, "assets/js", tep), "utf8"), hop);
  const d = hop.window[bien] || {};
  return { ten: d.__ten || bien, mach: (d.CHAIN || []).map((c) => ({ id: c.id, t: c.t })) };
}
const CHU_THE = [
  { id:"vn", ten:"Việt Nam",   tep:"data.js",    bien:"DQT_DATA",
    hoi:"Tin này ảnh hưởng thế nào tới nền kinh tế Việt Nam?" },
  { id:"tq", ten:"Trung Quốc", tep:"tq/data.js", bien:"DQT_TQ",
    hoi:"Tin này ảnh hưởng thế nào tới khả năng giữ quyền lực và năng lực tài khoá của ĐCSTQ?" },
  { id:"tk", ten:"Tổng kết",   tep:"tk/data.js", bien:"DQT_TK",
    hoi:"Tin này siết hay nới KHỚP NỐI giữa Việt Nam và Trung Quốc, và giữa cả hai với Mỹ?" }
];

/* ── BƯỚC 1 · RA ĐỀ ──────────────────────────────────────*/
const SUC = {};

async function raDe() {
  const tho = [];
  for (const ng of NGUON) {
    for (const f of ng.feed) {
      try {
        const r = await fetch(f, { headers: { "user-agent": "blockchainworld-dqt/1.0 (+github)" },
                                   redirect: "follow", signal: AbortSignal.timeout(20000) });
        if (!r.ok) { console.log("  · " + ng.id + " HTTP " + r.status + " — bỏ qua"); continue; }
        const b = docFeed(await r.text(), ng).slice(0, MOI_FEED);
        tho.push(...b);
        /* FEED ÔI. Lớp hỏng vừa cắn: HTTP 200, đủ mục, không lỗi nào,
           mà mục mới nhất cũ tám năm. Bộ lọc ngày vứt sạch trong im
           lặng, nên nguồn góp 0 bài mà không dòng nào nói vì sao —
           đúng kiểu chỉ lộ ra khi có người ngồi đọc từng feed. */
        const ngay = b.map((x) => new Date(x.ngay)).filter((d) => !isNaN(d)).sort((x, y) => y - x);
        const oi = ngay[0] ? Math.round((Date.now() - ngay[0]) / 86400000) : null;
        SUC[ng.id] = { muc: b.length, oi };
        console.log("  · " + ng.id.padEnd(11) + b.length + " mục" +
          (oi === null ? "  ⚠ KHÔNG mục nào có ngày" : oi > 30
            ? "  ⚠ mục mới nhất " + oi + " ngày trước — feed có thể đã chết" : ""));
        if (oi === null || oi > 30)
          console.log("::warning::nguồn " + ng.id + " của Đài Quan Trắc có vẻ đã chết: " +
            (oi === null ? "không mục nào có ngày" : "mục mới nhất " + oi + " ngày trước"));
      } catch (e) {
        /* Một feed chết KHÔNG được làm hỏng cả lượt. Nguồn tin thì
           luôn có cái sập, và mất một nguồn còn hơn mất cả bảng. */
        console.log("  · " + ng.id.padEnd(11) + "hỏng: " + e.message.slice(0, 50));
      }
      await nghi(900);
    }
  }

  /* Trùng bài: cùng URL, hoặc cùng tiêu đề đã chuẩn hoá (nhiều báo
     đăng lại cùng một bản tin hãng). */
  const thay = new Set(), sach = [];
  for (const b of tho) {
    const k1 = b.link.split("?")[0];
    const k2 = b.tieu.toLowerCase().replace(/[^a-z0-9à-ỹ ]/gi, "").slice(0, 60);
    if (thay.has(k1) || thay.has(k2)) continue;
    thay.add(k1); thay.add(k2); sach.push(b);
  }

  const de = { taoLuc: new Date().toISOString(), chuThe: [] };
  for (const c of CHU_THE) {
    const m = machCua(c.tep, c.bien);
    const xep = sach
      .map((b) => ({ ...b, diem: chamDiem(b, KHOA[c.id], NHA[c.id]) }))
      .filter((b) => b.diem >= DIEM_TOI_THIEU && tuoiNgay(b.ngay) <= CU_NHAT_NGAY)
      .sort((a, b) => b.diem - a.diem || String(b.ngay).localeCompare(String(a.ngay)));
    /* Duyệt theo thứ hạng và bỏ qua nguồn đã đủ chỉ tiêu. Làm sau
       khi sắp xếp chứ không lọc trước, để bài thứ ba của một nguồn
       nhường chỗ cho bài tốt nhất của nguồn kế tiếp. */
    /* PHỄU. Log cũ chỉ nói "TQ: 2/6 bài" — đúng mà vô dụng: nó không
       nói bài rụng ở CỬA NÀO. Ba cửa có ba cách chữa khác hẳn nhau:
       cổng địa lý rụng thì thêm từ khoá nước, cổng cơ chế rụng thì
       nới danh sách từ, còn trần mỗi nguồn rụng thì phải thêm NGUỒN.
       Không đếm thì lần sau lại ngồi đoán như hôm nay. */
    const so = { diaLy: 0, coChe: 0 };
    const quaCong = sach.map((b) => chamDiem(b, KHOA[c.id], NHA[c.id], so)).filter((d) => d > 0).length;
    const dem = {}, chon = [];
    let chanNguon = 0;
    for (const b of xep) {
      if (chon.length >= MOI_CHU_THE) break;
      if ((dem[b.nguon] || 0) >= TOI_DA_MOI_NGUON) { chanNguon++; continue; }
      dem[b.nguon] = (dem[b.nguon] || 0) + 1; chon.push(b);
    }
    de.chuThe.push({ id: c.id, ten: c.ten, hoi: c.hoi, mach: m.mach, bai: chon });
    console.log("  " + c.id.toUpperCase() + ": " + chon.length + "/" + MOI_CHU_THE +
      " bài · điểm " + chon.map((x) => x.diem).join(",") +
      " · nguồn " + [...new Set(chon.map((x) => x.nguon))].join(" "));
    if (chon.length < MOI_CHU_THE)
      console.log("     ⚠ thiếu " + (MOI_CHU_THE - chon.length) + " bài · phễu: " +
        sach.length + " mục thô → " + quaCong + " qua cổng điểm → " +
        xep.length + " còn trong hạn ngày → " + chon.length + " chọn" +
        " · rụng: cổng địa lý " + so.diaLy + ", cổng cơ chế " + so.coChe +
        (chanNguon ? " (trần mỗi nguồn chặn " + chanNguon + ")" : ""));
  }

  mkdirSync(dirname(RA_DE), { recursive: true });
  writeFileSync(RA_DE, JSON.stringify(de, null, 1));
  console.log("→ " + RA_DE);

  /* Bước sau gọi model, tức tốn quota. Ra đề rỗng mà vẫn thoát 0 là
     mời model chạy trên một danh sách trống rồi ghi một file rỗng —
     và file rỗng đó lại là đúng thứ phép chặn ở dung() phải xử lý.
     Chặn sớm ở đây rẻ hơn nhiều. */
  const tong = de.chuThe.reduce((a, c) => a + c.bai.length, 0);
  if (!tong) {
    console.log("! không chọn được bài nào — " +
      (tho.length ? sach.length + " bài lấy về nhưng không bài nào qua được hai cổng"
                  : "KHÔNG nguồn nào trả về bài, nhiều khả năng mất mạng"));
    process.exitCode = 1;
  }
}

/* ── BƯỚC 3 · DỰNG ───────────────────────────────────────*/
const MUC = new Set(["cao", "vua", "thap"]);

function dung() {
  if (!existsSync(RA_DE)) { console.log("! chưa có đề bài — bỏ qua, giữ bản cũ"); return; }
  const de = JSON.parse(readFileSync(RA_DE, "utf8"));
  let pt = { chuThe: [] };
  if (existsSync(RA_PT)) {
    try { pt = JSON.parse(readFileSync(RA_PT, "utf8")); }
    catch (e) {
      /* JSON hỏng KHÔNG được coi như "chưa có phân tích". Hai thứ đó
         dẫn tới hai hành động ngược nhau: chưa có thì dựng bảng mới,
         còn hỏng thì phải giữ nguyên bản cũ và kêu lên. */
      console.log("! phân tích không phải JSON hợp lệ: " + e.message);
      console.log("! giữ bản cũ, không ghi đè");
      process.exitCode = 1;
      return;
    }
  }

  const ra = {}; let tongBai = 0, tongAi = 0, loai = 0;
  for (const c of de.chuThe) {
    const idMach = new Set(c.mach.map((m) => m.id));
    const bang = new Map();
    const kho = (pt.chuThe || []).find((x) => x.id === c.id);
    for (const a of (kho && kho.phanTich) || []) {
      /* Bốn phép kiểm, và mỗi phép đã có lý do cụ thể:
         - link phải khớp một bài CÓ THẬT trong đề, không thì model
           đang bình luận một bài nó tự nghĩ ra
         - mach phải là id thật CỦA CHÍNH chủ thể đó
         - muc phải nằm trong bảng, không thì đèn không tô được
         - anh phải có chữ, không thì thẻ hiện một ô trống */
      if (!a || typeof a !== "object") { loai++; continue; }
      if (!c.bai.some((b) => b.link === a.link)) { loai++; continue; }
      if (!idMach.has(a.mach)) { loai++; continue; }
      if (!MUC.has(a.muc)) { loai++; continue; }
      const t = String(a.anh || "").trim();
      if (t.length < 40) { loai++; continue; }
      bang.set(a.link, { mach: a.mach, muc: a.muc, anh: t.slice(0, 900) });
    }
    ra[c.id] = c.bai.map((b) => ({
      t: b.tieu, u: b.link, mo: b.mo, img: b.anh, ng: b.ngay, n: b.nguon,
      ai: bang.get(b.link) || null
    }));
    tongBai += ra[c.id].length;
    tongAi += ra[c.id].filter((x) => x.ai).length;
  }

  /* Không nhận được bài nào thì GIỮ BẢN CŨ. Một bảng tin trống người
     ta đọc thành "thế giới không có tin gì", chứ không đọc thành
     "đường ống hỏng" — đúng bài học đã ghi cho bản quét. */
  if (!tongBai) {
    console.log("! không bài nào qua được — giữ bản cũ, không ghi đè");
    process.exitCode = 1;
    return;
  }
  /* Đây là phép chặn quan trọng nhất của cả file. Bước 2 có thể báo
     thành công mà ghi ra file rỗng, hoặc ghi toàn mục sai bị loại
     hết — cả hai đều cho tongAi = 0. Dựng tiếp là đổi một bảng CÓ
     suy luận lấy một bảng KHÔNG có, im lặng hoàn toàn.

     Trừ đúng một trường hợp: chưa có file nào. Lúc đó không có gì
     để mất, và một bảng tin không kèm suy luận vẫn hơn hẳn không có
     bảng nào — giao diện đã nói rõ bài nào chưa được phân tích. */
  if (!tongAi && existsSync(RA_JS)) {
    console.log("! " + tongBai + " bài nhưng KHÔNG phân tích nào qua được" +
      (loai ? " (" + loai + " mục bị loại)" : "") + " — giữ bản cũ, không ghi đè");
    process.exitCode = 1;
    return;
  }

  const nhan = NGUON.reduce((a, n) => (a[n.id] = { t: n.ten, l: n.loai }, a), {});
  const js =
"/* SINH TỰ ĐỘNG bởi scripts/build-dong-tin.mjs — ĐỪNG SỬA TAY.\n" +
"   Bài viết lấy nguyên văn từ RSS của nguồn; khối `ai` là PHÁN ĐOÁN\n" +
"   của model, không phải trích dẫn từ bài. Giao diện phải giữ hai\n" +
"   thứ đó tách nhau. */\n" +
"window.DQT_TIN = " + JSON.stringify({ generatedAt: new Date().toISOString(), nguon: nhan, bai: ra }) + ";\n";
  mkdirSync(dirname(RA_JS), { recursive: true });
  writeFileSync(RA_JS, js);
  console.log("→ " + RA_JS + "  ·  " + tongBai + " bài · " + tongAi + " có phân tích" +
    (loai ? " · " + loai + " mục bị loại" : ""));
}

const cv = process.argv.slice(2);
if (cv.includes("--de-bai")) await raDe();
else dung();
