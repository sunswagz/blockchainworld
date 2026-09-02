(function () {
"use strict";

/* IC và svg là bộ icon — thuộc GIAO DIỆN, không thuộc chủ thể nào,
   nên lấy một lần và không đổi khi chuyển nước. */
var D0 = window.DQT_DATA;
var IC = D0.IC, svg = D0.svg;

/* Lớp PHƯƠNG PHÁP — khung.js. Đứng TRÊN chỗ chia chủ thể nên KHÔNG
   nằm trong nhóm biến đổi theo nước bên dưới. Chính nhờ vậy bảng
   chấm Hướng Hoa Cường so thẳng được với Vingroup và THACO. */
var K_ = window.DQT_KHUNG || {};
var THANG = K_.THANG || [], TIEUCHI = K_.TIEUCHI || [];

/* ═══════════════════════════════════════════════════════
   ĐỪNG VIẾT CỨNG SỐ ĐẾM VÀO CHUỖI HIỂN THỊ

   Loại lỗi này đã cắn NĂM lần trong cung, và lần nào cũng im lặng —
   trang vẫn vẽ, không lỗi nào ném ra, chỉ có chữ là nói dối:

     · "4 cấp độ" và "có bốn cấp"  → Việt Nam 4, Trung Quốc 5.
       Thanh bên nói "5 cấp độ" còn tiêu đề ngay dưới nói "bốn",
       trên CÙNG một trang.
     · "MẮT XÍCH n/11"             → cả hai nước đều có 16.
     · "Mười hai đồng hồ ... cả mười hai đặt tay" → câu này hiện
       trên trang Việt Nam, nơi có 11 đồng hồ và 7 cái ĐÃ tự đo.
       Sai sự thật, ngay giữa bảng cảnh báo.
     · "than nội địa của Trung Quốc" làm ví dụ bộ đệm → hiện luôn
       trên trang mạch của Việt Nam.
     · CẢ MỘT ĐOẠN VĂN cố định trong vScen() và vLevels(): "Nga và
       Hormuz đánh vào Trung Quốc…" và "Ranh giới nằm giữa cấp 2 và
       cấp 3…". Không con số nào sai, nên hai lệnh grep bên dưới
       KHÔNG bắt được — mà ba bảng xếp kịch bản theo ba trục khác
       hẳn nhau, và nhánh C của Tổng kết là nhánh TỐT. Đã chuyển
       xuống dữ liệu thành KB và RANH.

   Luật: mọi con số và mọi ví dụ đặc thù trong chuỗi hiển thị phải
   lấy từ dữ liệu của CHỦ THỂ ĐANG XEM — CHAIN.length, GAUGES.length,
   LEVELS.length, DEM, chuThe(state.cht).ten. Chủ thể thứ ba ĐÃ được
   thêm (Tổng kết), và đúng như dự đoán ở đây: nó làm lộ ra ổ thứ năm,
   loại ổ mà không phép kiểm nào bắt được.

   Cách soát nhanh khi sửa file này:
     grep -n "'[^']*(một|hai|ba|bốn|năm|[0-9]+) (cấp|đồng hồ|mắt xích|chiến trường)" app.js
     grep -n "Việt Nam|Trung Quốc" app.js   ← phải nằm trong chú thích hoặc CHUTHE
   Và lệnh thứ ba, vì hai lệnh trên chỉ soi CON SỐ và TÊN NƯỚC:
     đọc mọi chuỗi dài trong view dùng chung và hỏi "câu này còn
     đúng khi đổi sang chủ thể khác không?". Đúng cho một bảng thì
     nó thuộc về dữ liệu của bảng đó, không thuộc về view.
   ═══════════════════════════════════════════════════════ */

/* Lớp CHỦ THỂ — đổi hết khi chuyển nước. Phải là `let` chứ không
   phải `const`: napChuThe() gán lại toàn bộ rồi render lại. */
let THEATERS = [], GAUGES = [], CHAIN = [], CHAIN_SRC = {},
    LEVELS = [], SCEN = [], LIB = [], SOI = [], DANHSACH = [], SOLIEU = [],
    BOMACH = null, BANCO = null,
    COMPASS = null, DODAC = [];

/* ============================================================
   SỐ ĐO TỰ ĐỘNG — do.js, sinh 4 lượt/ngày, không gọi AI

   Luật cứng: SỐ ĐO KHÔNG BAO GIỜ ĐÈ LÊN ĐÈN NGƯỜI DÙNG TỰ ĐẶT.
   Ghi đè im lặng một lần là mất niềm tin vào cả bảng, và người
   dùng sẽ không biết cái mình đang nhìn là phán đoán của mình
   hay của máy.

   Nên state.gg giữ nguyên nghĩa cũ — lựa chọn của NGƯỜI — và
   'n' đổi nghĩa một chút: "không có ý kiến riêng". Khi đó nếu
   có số đo thì lấy số đo, không có thì để trống. Nhờ vậy vòng
   bấm cũ (n → g → y → r → n) tự nhiên có luôn nghĩa "trả về
   cho máy đo", không cần thêm trạng thái nào. */
/* Số đo tự động cũng thuộc về MỘT chủ thể. Đọc thẳng window ở đây là
   chỗ Trung Quốc sẽ mượn số đo của Việt Nam nếu hai bên trùng id đồng
   hồ. napChuThe() gán lại theo nước đang xem. */
let DO = {}, DO_LUC = null;

/* Đèn thực tế của một đồng hồ, sau khi hoà người và máy. */
/* Quá bấy nhiêu giờ kể từ lần lấy THÀNH CÔNG gần nhất thì một con số
   thôi được coi là số đo. Nhịp bot là 6 giờ, nên 24 giờ nghĩa là đã
   lỡ bốn lượt liền — quá ngưỡng mạng chập chờn, đã là nguồn chết.

   `luc` là dấu thời gian của lần lấy được số THẬT: lúc hỏng, bộ lấy
   bê nguyên bản ghi cũ sang và chỉ thêm cờ `oi`, nên `luc` không bị
   dời theo. Không cần thêm trường nào. */
const OI_GIO = 24;
function tuoiDo(d){
  if(!d || !d.luc) return null;
  const t = new Date(d.luc).getTime();
  return Number.isFinite(t) ? (Date.now() - t) / 3.6e6 : null;
}
/* Đọc số đo qua ĐÂY, đừng đọc thẳng DO[id]. Trả null khi số đã đông
   cứng, nhờ vậy đồng hồ tụt về "chưa quan trắc" thay vì sáng bằng
   một con số bốn ngày tuổi. Con số vẫn còn trong DO để bảng đồng hồ
   hiện ra kèm lời cảnh báo — giấu đi thì người đọc mất luôn manh
   mối là nguồn đã chết. */
function soDo(id){
  const d = DO[id];
  if(!d) return null;
  const t = tuoiDo(d);
  return (t != null && t > OI_GIO) ? null : d;
}
function den(id){
  const tay = gGG(id);
  if(tay && tay !== 'n') return tay;
  const d = soDo(id);
  return (d && d.muc) ? d.muc : 'n';
}
/* Đèn đó từ đâu ra — giao diện phải nói thật chỗ này. */
function nguonDen(id){
  const tay = gGG(id);
  if(tay && tay !== 'n') return 'tay';
  return soDo(id) ? 'tu' : 'chua';
}
function demDen(){
  const r = {g:0,y:0,r:0,n:0};
  GAUGES.forEach(g=>{ r[den(g.id)]++; });
  r.dat = r.g + r.y + r.r;
  return r;
}
/* Quy tắc đọc cấp — gom về một chỗ, trước đây chép ở hai view
   và đã bắt đầu lệch nhau. */
function capDo(){
  const d = demDen();
  if(!d.dat) return 0;
  return d.r>=4 ? 4 : d.r>=2 ? 3 : (d.y+d.r)>=3 ? 2 : 1;
}

/* Sparkline: SVG nội tuyến, không thư viện. Chuỗi lịch sử do
   Yahoo trả sẵn ~64 phiên nên không phải tự tích luỹ nhiều tháng
   mới có hình. */
function spark(lich, mau){
  if(!lich || lich.length < 4) return '';
  const n = lich.slice(-40), lo = Math.min(...n), hi = Math.max(...n), W = 74, H = 20;
  const bien = (hi - lo) || 1;
  const pts = n.map((v,i)=>{
    const x = (i/(n.length-1))*W;
    const y = H - ((v-lo)/bien)*(H-3) - 1.5;
    return x.toFixed(1)+','+y.toFixed(1);
  }).join(' ');
  const cuoi = pts.split(' ').pop().split(',');
  /* CỠ NỘI TẠI, không chỉ viewBox. W và H đúng bằng .spk trong
     app.css (74×20) nên bố cục không đổi một pixel nào — nhưng nếu
     người dùng đang kẹt bản CSS cũ trong cache, SVG chỉ có viewBox
     sẽ phình kín trang. Đó là kiểu hỏng CLAUDE.md chép lại từ lần
     icon Cổng Thành phình ra vì quên nâng CACHE_VERSION.

     Đường spark chỉ vẽ khi có từ 4 mốc lịch sử trở lên, nên nó nằm
     im nhiều ngày rồi mới hiện — và thước svg-co bắt được đúng lượt
     dữ liệu đủ 4 mốc, chứ không phải lúc dòng này được viết. */
  return '<svg class="spk" width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none" aria-hidden="true">'+
    '<polyline points="'+pts+'" fill="none" stroke="'+mau+'" stroke-width="1.4" '+
    'stroke-linejoin="round" stroke-linecap="round"/>'+
    '<circle cx="'+cuoi[0]+'" cy="'+cuoi[1]+'" r="1.8" fill="'+mau+'"/></svg>';
}
const MAU = {g:'#2ea043', y:'#d29922', r:'#f0503f', n:'#4b5563'};

function gioDo(iso){
  if(!iso) return '';
  const t = new Date(iso);
  if(isNaN(t)) return '';
  const p = n=>String(n).padStart(2,'0');
  return p(t.getUTCDate())+'/'+p(t.getUTCMonth()+1)+' '+p(t.getUTCHours())+':'+p(t.getUTCMinutes())+' UTC';
}

/* ============================================================
   TRẠNG THÁI
   ============================================================ */
const LVLS = ['n','g','y','r'];
const LVNAME = {n:'chưa quan trắc', g:'xanh', y:'vàng', r:'đỏ'};
/* ============================================================
   CHỦ THỂ — lớp cho phép Đài Quan Trắc soi nhiều nước

   Nút chuyển chủ thể chỉ hiện khi có từ hai chủ thể trở lên.

   Nhưng phần khoá trạng thái phải làm NGAY BÂY GIỜ, không phải
   lúc thêm nước thứ hai. state.gg trước đây là map phẳng theo id
   đồng hồ; chủ thể thứ hai có đồng hồ trùng id là đè nhau ngay.
   Chuyển sang khoá 'vn:nangluong' lúc chỉ có một chủ thể thì an
   toàn tuyệt đối vì không có gì để va. Làm sau thì phải vừa tách
   vừa gỡ va chạm trên dữ liệu thật của người dùng.

   Mỗi chủ thể khai `co` — nó có những nhóm nào. Thanh bên chỉ vẽ
   phần có; không thì nước thiếu bảng đồng hồ sẽ hiện một mục rỗng
   và trông như hỏng. */
const CHUTHE = [
  {id:'vn', ten:'Việt Nam',   co:'🇻🇳', kho:'DQT_DATA', khoSoi:'DQT_SOI',
   khoDo:'DQT_DO', khoScan:'DQT_SCAN', tepScan:'assets/js/scan.js',
   hoi:'Nền kinh tế chịu được không?'},
  /* Trung Quốc CHƯA có đường quét tự động và CHƯA có số đo — khai
     null chứ không bỏ trống, để giao diện nói thẳng "chưa có" thay vì
     lặng lẽ hiện dữ liệu của nước bên cạnh. Chính chỗ này từng trộn:
     Dòng chảy của Trung Quốc hiện tín hiệu Hormuz của Việt Nam. */
  {id:'tq', ten:'Trung Quốc', co:'🇨🇳', kho:'DQT_TQ',   khoSoi:'DQT_TQ_SOI',
   khoDo:"DQT_TQ_DO", khoScan:"DQT_TQ_SCAN", tepScan:"assets/js/tq/scan.js",
   hoi:'Quyền lực giữ được không?'},
  /* Chủ thể thứ ba KHÔNG phải một nước mà là CHỖ HAI NƯỚC MÓC VÀO
     NHAU. Nó không có chiến trường, không có bản quét, không có số
     đo — khai null cả ba đường tự động là có chủ ý: nó là khung đọc,
     không phải bảng quan trắc thứ ba. Nhờ các nhóm tự lọc khi rỗng,
     không cần một dòng `if (là tổng kết)` nào trong toàn bộ app. */
  {id:'tk', ten:'Tổng kết',   co:'🔗', kho:'DQT_TK',   khoSoi:null,
   khoDo:null, khoScan:null, tepScan:null,
   viTri:'BỐN PHÍA CỦA KHỚP NỐI',
   hoi:'Hai đoàn tàu móc vào nhau ở đâu?'}
].filter(c=>window[c.kho]);   /* chủ thể thiếu file dữ liệu thì biến mất
                                 khỏi thanh chuyển, không hiện mục rỗng */
const chuThe = id => CHUTHE.find(c=>c.id===id) || CHUTHE[0];

/* Nạp dữ liệu của chủ thể đang chọn. Gọi lúc khởi động và mỗi lần
   chuyển nước. Mọi mảng đều có mặc định [] — chủ thể chưa có bảng
   đồng hồ thì mục đó tự biến mất khỏi thanh bên, không hiện rỗng. */
function napChuThe(){
  const c = chuThe(state.cht);
  const d = window[c.kho] || {}, s = window[c.khoSoi] || {};
  THEATERS = d.THEATERS||[]; GAUGES = d.GAUGES||[]; CHAIN = d.CHAIN||[];
  CHAIN_SRC = d.CHAIN_SRC||{};
  LEVELS = d.LEVELS||[];     SCEN = d.SCEN||[];     LIB = d.LIB||[];
  SOI = s.SOI||[];           DANHSACH = s.DANHSACH||[];
  BOMACH = d.BOMACH||null;  BANCO = d.BANCO||null;
  DEM = d.DEM||[];
  SOLIEU = d.SOLIEU||[];  COMPASS = d.COMPASS||null;  DODAC = d.DODAC||[];
  KB = d.KB||null;  RANH = d.RANH||null;
  const tin = window.DQT_TIN || null;
  TIN = (tin && tin.bai && tin.bai[c.id]) || [];
  TIN_LUC = (tin && tin.generatedAt) || null;
  const dd = c.khoDo ? window[c.khoDo] : null;
  DO = (dd && dd.do) ? dd.do : {};
  DO_LUC = (dd && dd.generatedAt) || null;
  dungRoutes();
  /* Trang đang mở có thể không tồn tại ở chủ thể vừa nạp — Tổng kết
     không có Dòng chảy chẳng hạn. Không lùi ở đây thì render() vẫn
     rơi vào nhánh 'flow' và vẽ một trang rỗng trông như lỗi. */
  if(!coRoute(state.route)) state.route = dauTien();
  kiemMach();
}

/* Chuyển nước. Cố GIỮ NGUYÊN LOẠI TRANG đang xem — đang ở bảng đồng
   hồ Việt Nam thì sang bảng đồng hồ Trung Quốc, không văng về trang
   chủ. Trang không tồn tại ở chủ thể mới (một hồ sơ soi chẳng hạn)
   thì lùi về Dòng chảy. */
function doiChuThe(id){
  if(id===state.cht) return;
  const cu = state.route;
  state.cht = id; napChuThe();
  /* Bộ lọc Dòng chảy giữ id chiến trường của nước cũ thì sang nước mới
     nó lọc ra 0 dòng và trông như mất hết tin. */
  state.filter = 'all';
  state.route = coRoute(cu) ? cu : dauTien();
  save();
  /* Thanh bên và nút chuyển vẽ TRƯỚC nội dung, có chủ ý. Một lỗi trong
     một khung nhìn thì chỉ hỏng khung đó; người dùng vẫn còn thanh bên
     để đi chỗ khác. Thứ tự ngược lại đã làm cả giao diện đứng im và
     trông y như "nút chuyển nước không hoạt động". */
  renderNav(); veChuThe(); render();   /* render() tự gọi renderTicker() */
}

const state = {
  cht: CHUTHE[0].id,
  route:'flow',
  /* Không điền sẵn nữa — gTH/gGG trả 'n' khi thiếu khoá. Điền sẵn
     theo id phẳng chính là thứ vừa phải gỡ. */
  th:  {},
  gg:  {},
  sig: [],           // tín hiệu từ quét trực tiếp
  log: [],           // nhật ký kết nối
  filter:'all',
  scanning:false,
  /* Nhóm nào đang mở trong thanh bên. Khoá là tên nhóm, thiếu khoá
     nghĩa là MỞ — nhờ vậy thêm nhóm mới sau này tự mở, không phải
     nhớ khai thêm dòng nào. */
  mo:{},
  /* Mục hồ sơ nào đang mở. Khoá 'soi:<hồ sơ>:<mục>' — có tên hồ
     sơ trong khoá để mở hồ sơ khác không kế thừa thói quen đọc
     của hồ sơ trước. */
  muc:{}
};
const RANK={n:0,g:1,y:2,r:3};

/* Soi mạch của CHỦ THỂ ĐANG NẠP — gọi từ napChuThe(), không phải lúc
   nạp module. Chạy lúc nạp module là chỗ bộ kiểm này từng vô dụng:
   CHAIN khi đó còn rỗng nên nó không bắt được gì, lại còn báo nhầm 16
   dòng "thừa". Bộ kiểm chạy sai thời điểm còn tệ hơn không có, vì nó
   dạy người đọc bỏ qua cảnh báo. */
function kiemMach(){
  const co = new Set(GAUGES.map(g=>g.id)), ct = new Set(THEATERS.map(t=>t.id)), loi=[];
  CHAIN.forEach(c=>{
    const s=CHAIN_SRC[c.id];
    if(!s){ loi.push('mắt xích "'+c.id+'" thiếu dòng trong CHAIN_SRC'); return; }
    if(s[0]==='th'){ if(!ct.has(s[1])) loi.push('"'+c.id+'" trỏ tới chiến trường không có: '+s[1]); }
    else s.slice(1).forEach(g=>{ if(!co.has(g)) loi.push('"'+c.id+'" trỏ tới đồng hồ không có: '+g); });
  });
  Object.keys(CHAIN_SRC).forEach(id=>{
    if(!CHAIN.some(c=>c.id===id)) loi.push('CHAIN_SRC thừa dòng "'+id+'" — không mắt xích nào dùng');
  });
  if(loi.length) console.error('[Đài Quan Trắc · '+chuThe(state.cht).ten+
    '] mạch truyền dẫn lệch:\n  · '+loi.join('\n  · '));
}
/* Đọc qua den() chứ không đọc thẳng state.gg — nhờ vậy số đo tự
   động cũng thắp được mạch truyền dẫn, không chỉ đèn đặt tay. Đây
   là chỗ vòng tuần hoàn khép lại: đo → ngưỡng → đèn → mạch sáng. */
function lvOf(chainId){
  const s=CHAIN_SRC[chainId];
  /* Thiếu dòng thì trả 'n', KHÔNG ném lỗi. Đây là bài học vừa trả giá:
     một dòng thiếu làm lvOf ném ngay trong render(), render() nằm
     TRƯỚC renderNav() nên thanh bên không kịp vẽ lại — và triệu chứng
     hiện ra là "bấm chuyển nước mà giao diện không đổi", chẳng liên
     quan gì tới nguyên nhân thật. Một dòng dữ liệu sai chỉ được phép
     làm xám MỘT chip; kiemMach() lo phần báo cho người sửa. */
  if(!s) return 'n';
  if(s[0]==='th') return gTH(s[1]);
  if(s[0]==='gg') return den(s[1]);
  return s.slice(1).reduce((a,g)=>RANK[den(g)]>RANK[a]?den(g):a,'n');
}
function srcLabel(chainId){
  const s=CHAIN_SRC[chainId];
  if(s[0]==='th') return 'mức của chiến trường <b>'+esc(TH(s[1]).short)+'</b>';
  if(s[0]==='gg') return 'đồng hồ <b>'+esc(GAUGES.find(g=>g.id===s[1]).t)+'</b>';
  return 'mức cao hơn giữa hai đồng hồ <b>'+s.slice(1).map(g=>esc(GAUGES.find(x=>x.id===g).t)).join('</b> và <b>')+'</b>';
}

/* ---- lưu / nạp ---- */
async function save(){
  try{ if(window.storage) await window.storage.set('daiquantrac:v1', JSON.stringify({cht:state.cht,th:state.th,gg:state.gg,mo:state.mo,muc:state.muc,sig:state.sig.slice(0,120),log:state.log.slice(0,60)})); }catch(e){}
}
async function load(){
  try{ if(!window.storage) return;
    const r = await window.storage.get('daiquantrac:v1');
    if(r&&r.value){ const d=JSON.parse(r.value);
      Object.assign(state.th, doiKhoa(d.th)); Object.assign(state.gg, doiKhoa(d.gg));
      Object.assign(state.mo,d.mo||{}); Object.assign(state.muc,d.muc||{});
      state.sig=d.sig||[]; state.log=d.log||[];
      if(d.cht && CHUTHE.some(c=>c.id===d.cht)) state.cht=d.cht;
    }
  }catch(e){}
}

/* Chuyển dữ liệu đã lưu từ dạng phẳng sang dạng có tiền tố chủ thể.
   Người dùng cũ có localStorage kiểu {nangluong:'y'}; thiếu bước
   này thì mọi đèn họ tự đặt biến mất không dấu vết ngay lần mở
   trang đầu tiên sau khi cập nhật.

   Nhận diện bằng dấu ':' — khoá mới luôn có, khoá cũ không bao
   giờ có. Chạy được nhiều lần mà không hỏng, nên không cần cờ
   "đã chuyển" lưu riêng. */
function doiKhoa(o){
  const r={}; if(!o) return r;
  for(const k of Object.keys(o)) r[k.indexOf(':')>=0 ? k : 'vn:'+k] = o[k];
  return r;
}

/* ---- đọc/ghi trạng thái theo chủ thể ----
   Mọi chỗ chạm vào đèn phải đi qua bốn hàm này, không đọc thẳng
   state.gg[id] nữa. Một chỗ đọc thẳng sót lại là một chỗ đèn của
   nước này hiện sang nước kia — và lỗi đó im lặng. */
const K   = id => state.cht+':'+id;
/* Tín hiệu và nhật ký nằm CHUNG một mảng nhưng mỗi dòng mang cờ 'cht'.
   Mọi khung nhìn phải đọc qua hai hàm này, không đọc thẳng state.sig —
   một chỗ đọc thẳng sót lại là một chỗ tin của nước này hiện ở nước
   kia. Đã dính thật: id chiến trường "nga" có ở CẢ HAI nước, nên lọc
   theo th là không đủ. */
const sigCT = () => state.sig.filter(x => (x.cht||'vn') === state.cht);
const logCT = () => state.log.filter(x => (x.cht||'vn') === state.cht);
const gGG = id => state.gg[K(id)] || 'n';
const sGG = (id,v) => { state.gg[K(id)] = v; };
const gTH = id => state.th[K(id)] || 'n';
const sTH = (id,v) => { state.th[K(id)] = v; };

/* ---- tiện ích ---- */
const $  = s=>document.querySelector(s);
const el = (t,c,h)=>{const n=document.createElement(t); if(c)n.className=c; if(h!=null)n.innerHTML=h; return n;};
const esc= s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const TH = id=>THEATERS.find(t=>t.id===id);
function ago(iso){
  const d=(Date.now()-new Date(iso).getTime())/1000;
  if(isNaN(d)) return iso||'';
  if(d<60) return 'vừa xong';
  if(d<3600) return Math.floor(d/60)+' phút trước';
  if(d<86400) return Math.floor(d/3600)+' giờ trước';
  return Math.floor(d/86400)+' ngày trước';
}
let toastT;
function toast(msg,spin){
  const t=$('#toast'); t.innerHTML=(spin?'<span class="spin"></span>':'')+'<span>'+msg+'</span>'; t.classList.add('on');
  clearTimeout(toastT); if(!spin) toastT=setTimeout(()=>t.classList.remove('on'),3200);
}

/* ============================================================
   ĐIỀU HƯỚNG
   ============================================================ */
/* ROUTES phải dựng LẠI mỗi lần chuyển chủ thể, vì số mắt xích, số
   đồng hồ, số cấp độ và danh sách hồ sơ đều khác nhau giữa hai nước
   (Việt Nam 4 cấp độ, Trung Quốc 5). Viết cứng "4 cấp độ" là một
   nhãn nói dối ở nước còn lại.

   Nhóm nào rỗng thì tự bị loại ở cuối hàm — chủ thể thiếu phần nào
   thì thanh bên không hiện phần đó, thay vì hiện một mục trống. */
const SO = {3:'ba',4:'bốn',5:'năm',6:'sáu'};
let KB = null, RANH = null;
/* TIN nạp từ window.DQT_TIN — file do bot ghi, có thể CHƯA TỒN TẠI.
   Mọi chỗ đọc nó phải chịu được mảng rỗng. */
let TIN = [], TIN_LUC = null;
let DEM = [];
let ROUTES = [];
/* Trang này có tồn tại ở chủ thể đang xem không, và nếu không thì
   lùi về đâu. Bỏ qua mục 'Chủ thể' (chúng mang cờ `cht`) vì lùi về
   một nút chuyển nước là không lùi về đâu cả. */
const coRoute = id => ROUTES.some(g=>g.items.some(it=>it.id===id ||
  (it.con||[]).some(x=>x.id===id)));
const dauTien = () => { for(const g of ROUTES) for(const it of g.items)
  if(!it.cht) return it.id; return 'flow'; };
function dungRoutes(){
  const c = chuThe(state.cht);
  ROUTES = [
  {g:'Chủ thể', items: CHUTHE.map(x=>({id:'cht/'+x.id, t:x.co+'  '+x.ten,
     ic:'map', sub:x.hoi.toUpperCase(), cht:x.id}))},
  {g:'Quan trắc', items:
    /* Tổng kết không có chiến trường nhưng CÓ tin, nên trang này vẫn
       phải mở được — nó chỉ rụng đi khi chẳng có gì để hiện cả. */
    (THEATERS.length || TIN.length
      ? [{id:'flow', t:'Dòng chảy', ic:'flow',
          sub:THEATERS.length ? 'REALTIME' : TIN.length+' BÀI BÁO'}] : [])
    .concat(CHAIN.length ? [{id:'chain', t:'Mạch truyền dẫn', ic:'chain', sub:CHAIN.length+' MẮT XÍCH'}] : [])
    .concat(GAUGES.length ? [{id:'gauges', t:'Bảng cảnh báo sớm', ic:'gauge', sub:GAUGES.length+' ĐỒNG HỒ'}] : [])},
  {g:'Chiến trường', items: THEATERS.map(t=>({id:'th/'+t.id, t:t.name, ic:t.ic, sub:t.role.toUpperCase(), th:t.id}))},
  {g:'Mô hình', items:
    (LEVELS.length ? [{id:'levels', t:LEVELS.length+' cấp độ', ic:'stairs', sub:'ÁP LỰC → KHỦNG HOẢNG'}] : [])
    .concat(SCEN.length ? [{id:'scen', t:'Kịch bản A/B/C', ic:'play', sub:'PHÂN NHÁNH'}] : [])
    .concat(COMPASS ? [{id:'compass', t:'Kẹp bốn phía', ic:'map',
       sub:c.viTri || 'VỊ TRÍ '+c.ten.toUpperCase()}] : [])},
  /* Hồ sơ mang theo `con` — danh sách mục của chính nó. Thanh bên
     nhờ đó có tầng thứ ba, và người đọc nhảy thẳng tới đúng mục
     thay vì mở hồ sơ rồi cuộn tìm giữa 16 mục. */
  /* Chỉ chủ thể nào KHAI bo mạch mới có nhóm này — Việt Nam không
     khai nên nhóm tự rỗng và bị lọc đi ở cuối hàm. Không cần một
     dòng "nếu là Trung Quốc thì..." nào cả. */
  {g:'Bo mạch quyền lực', items: (BOMACH ? [{id:'bomach', t:'Bo mạch 2026', ic:'factory',
      sub:BOMACH.tang.reduce((a,t)=>a+t.ds.length,0)+' Ổ CẮM',
      con:BOMACH.tang.map(t=>({id:'bomach/'+t.id, t:t.tn, ic:'chain'}))}] : [])
    .concat(BANCO ? [{id:'banco', t:'Bàn cờ Mỹ–Trung', ic:'eagle', sub:'HAI BO MẠCH'}] : [])},
  {g:'Soi quyền lực', items: (SOI.length ? [{id:'soi', t:'Khung 7 tiêu chí', ic:'gauge', sub:'DÙNG LẠI ĐƯỢC'}] : [])
    .concat(SOI.map(s=>({id:'soi/'+s.id, t:s.ten, ic:s.ic, sub:'HỒ SƠ',
      con:(s.muc||[]).map(m=>({id:'soi/'+s.id+'/'+m.id, t:m.t, ic:m.ic||'book'}))})))},
  {g:'Hồ sơ nền', items: LIB.map(l=>({id:'lib/'+l.id, t:l.t, ic:l.id==='nhanthuc'?'brain':'book', sub:'CỤM '+l.n}))
    .concat([{id:'src', t:'Nguồn & nhật ký', ic:'src', sub:'MINH BẠCH'}])}
  ];
  /* Loại nhóm rỗng, và loại luôn nhóm Chủ thể khi mới có một nước —
     một nút chuyển chỉ dẫn tới chính nó thì chỉ tổ gây bối rối. */
  ROUTES = ROUTES.filter(g => g.items.length && !(g.g==='Chủ thể' && CHUTHE.length<2));

  /* Khai danh sách phòng cho CỔNG CHẶN của vòng tiến hoá
     (scripts/tien-hoa.mjs). Thanh bên ở đây là nút có onclick chứ
     không phải thẻ <a>, nên cổng không có `href` nào để nhặt và
     trước đó nó chỉ soi được 1 trong hơn 100 phòng — "qua cả năm
     phép" mà thực ra chưa soi gì.

     Khai TRONG dungRoutes() chứ không phải một lần lúc nạp: ROUTES
     đổi theo chủ thể, khai một lần là bỏ sót hai bảng còn lại. Gộp
     dồn qua Set để đủ cả ba. */
  window.__TUYEN = [...new Set([...(window.__TUYEN||[]),
    ...ROUTES.flatMap(g => g.items.flatMap(it =>
      ['#'+it.id, ...(it.con||[]).map(c => '#'+c.id)]))])];
}

function renderNav(){
  const w=$('#navscroll'); w.innerHTML='';
  ROUTES.forEach(sec=>{
    /* Nhóm chứa trang đang xem thì LUÔN mở, kể cả người dùng đã
       thu gọn nó. Không có luật này thì đi tới một mục bằng ⌘K
       hoặc bằng đường dẫn sẽ mở ra một thanh bên không đánh dấu
       chỗ nào cả — người đọc mất phương hướng và tưởng hỏng. */
    const trong = it => it.id===state.route ||
      (it.con||[]).some(c=>c.id===state.route) ||
      (it.con&&it.con.length&&state.route.indexOf(it.id+'/')===0);
    const coHere = sec.items.some(trong);
    const dong = state.mo[sec.g]===false && !coHere;

    /* Đèn nặng nhất bên trong. Thu gọn mà giấu luôn cảnh báo thì
       chính là biến nút thu gọn thành nút tắt chuông báo cháy. */
    let nang='n';
    sec.items.forEach(it=>{ if(it.th && RANK[gTH(it.th)]>RANK[nang]) nang=gTH(it.th); });

    const g=el('div','grp'+(dong?' dong':''));
    const h=el('button','navlab');
    h.setAttribute('aria-expanded', dong?'false':'true');
    h.innerHTML='<span class="nl-tw">'+
      '<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" '+
      'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg>'+
      '</span><span class="nl-t">'+esc(sec.g)+'</span>'+
      (dong?'<span class="nl-n">'+sec.items.length+'</span>'+
            (nang!=='n'?'<span class="dot '+nang+'"></span>':''):'');
    h.onclick=()=>{ state.mo[sec.g] = dong; save(); renderNav(); };
    g.appendChild(h);

    /* Vẫn dựng đủ mục rồi để CSS ẩn, không phải bỏ hẳn. Nhờ vậy
       chế độ thanh bên 62px — nơi nhãn nhóm bị ẩn và không còn gì
       để bấm mở lại — vẫn cho CSS hiện lại toàn bộ. */
    sec.items.forEach(it=>{
      const coCon = !!(it.con && it.con.length);
      /* Hồ sơ đang xem thì cây con LUÔN bung, cùng lý do với
         nhóm: đang đứng trong đó mà thanh bên không chỉ ra chỗ
         nào thì người đọc mất phương hướng. */
      const dangXem = coCon && state.route.indexOf(it.id)===0;
      const conMo = coCon && (state.mo[it.id]===true || dangXem);

      const b=el('button','nv'+(state.route===it.id?' on':'')+(coCon?' cha':'')+(conMo?' bung':''));
      let right='';
      if(it.th) right='<span class="dot '+gTH(it.th)+'"></span>';
      else if(it.id==='flow'&&sigCT().length) right='<span class="nv-x">'+sigCT().length+'</span>';
      else if(coCon) right='<span class="nv-x">'+it.con.length+'</span>';
      b.innerHTML=(coCon?'<span class="nv-tw"><svg viewBox="0 0 24 24" width="10" height="10" '+
          'fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" '+
          'stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></span>':'')+
        '<span class="ic">'+svg(it.ic)+'</span><b>'+esc(it.t)+'</b>'+right;
      /* Bấm vào mũi tên = chỉ đóng/mở cây con. Bấm vào phần còn
         lại = đi tới hồ sơ. Gộp hai việc vào một nút thì không
         xem được hồ sơ mà không bung 16 mục ra. */
      b.onclick=(ev)=>{
        if(coCon && ev.target.closest('.nv-tw')){
          state.mo[it.id] = !conMo; save(); renderNav(); return;
        }
        go(it.id);
      };
      g.appendChild(b);

      if(coCon){
        const cw=el('div','con'+(conMo?'':' dong'));
        it.con.forEach(c=>{
          const cb=el('button','nv nv-con'+(state.route===c.id?' on':''));
          cb.innerHTML='<span class="ic">'+svg(c.ic)+'</span><b>'+esc(c.t)+'</b>';
          cb.onclick=()=>go(c.id);
          cw.appendChild(cb);
        });
        g.appendChild(cw);
      }
    });
    w.appendChild(g);
  });
}

/* Nút chuyển chủ thể trên thanh trên cùng. Chỉ dựng khi có từ hai
   chủ thể — một nút đơn độc thì vô nghĩa và chiếm chỗ. */
function veChuThe(){
  const o=$('#chtbar'); if(!o) return;
  if(CHUTHE.length<2){ o.style.display='none'; return; }
  o.innerHTML='';
  CHUTHE.forEach(c=>{
    const b=el('button','chtb'+(c.id===state.cht?' on':''));
    b.innerHTML='<span class="chtc">'+c.co+'</span><b>'+esc(c.ten)+'</b>';
    b.title=c.ten+' — '+c.hoi;
    b.onclick=()=>{ doiChuThe(c.id); veChuThe(); };
    o.appendChild(b);
  });
}

/* Đường nhảy qua thanh bên (WCAG 2.4.1). Trả false để CHẶN trình
   duyệt đổi location.hash: bộ định tuyến ở đây đọc thẳng hash làm
   tên phòng, nên nhảy tới "#main" theo lối thường sẽ đá người dùng
   vào một phòng không tồn tại. Tự chuyển tiêu điểm là đủ — #main
   có tabindex="-1" chính vì việc này. */
function boQua(){
  const m=$('#main'); if(!m) return true;
  m.focus();
  const v=$('#view'); if(v) v.scrollTop=0;
  return false;
}

function go(r){
  if(r.indexOf('cht/')===0){ const id=r.slice(4);
    doiChuThe(id); veChuThe(); return; }
  state.route=r; location.hash=r;
  closeRail(); $('#nav').classList.remove('open'); $('#scrim').classList.remove('on');
  renderNav(); render(); $('#view').scrollTop=0;
}

/* ============================================================
   TICKER
   ============================================================ */
function renderTicker(){
  const items = CHAIN.map(c=>{
    const lv = lvOf(c.id);
    return '<span class="tk"><span class="dot '+lv+'"></span>'+esc(c.t)+' <i>'+LVNAME[lv]+'</i></span>';
  }).join('');
  $('#tick').innerHTML = items+items;
}

/* ============================================================
   VIEWS
   ============================================================ */
function head(ttl,sub){ $('#ttl').textContent=ttl; $('#sub').textContent=sub; }

/* Lớp tri thức nền — knowledge-os/sinh.mjs ghi ra assets/js/v/tri-thuc.js,
   mang cả dữ liệu lẫn hàm vẽ nên khuôn giống hệt mọi cung khác. Nó KHÔNG
   đụng số liệu nào; việc duy nhất là nói trang này đang đo VIỆC KINH TẾ gì,
   và mỗi câu giải nghĩa đến từ đâu.

   Chỉ NĂM tuyến cố định được ánh xạ (flow, chain, gauges, levels, banco).
   Tuyến sinh từ dữ liệu — `th/…`, `soi/…`, `cht/…`, `lib/…` — đổi theo lượt
   bot, nên ánh xạ vào đó là ánh xạ sẽ lặng lẽ trỏ trượt. Tuyến chưa ánh xạ
   thì `them()` trả false và không vẽ gì.

   Bọc `render` chứ không sửa mười ba nhánh `return v.innerHTML='', …`: nối
   ở một chỗ sau khi nội dung đã dựng xong là một chỗ phải nhớ thay vì mười
   ba. `them()` tự gỡ khối cũ nên vẽ lại cùng tuyến không chồng khối. */
function render(){
  veTuyen();
  const TT=window.TRI_THUC;
  if(TT&&TT.them) TT.them($('#view'), state.route);
}

/* ── KHUNG · CÁI CẦU SANG BỐN TỆP TRANG ───────────────────
   Mười sáu hàm vẽ đã tách sang assets/js/trang/*.js (xem đầu một
   trong bốn tệp đó để biết vì sao). Chúng không còn thấy phạm vi của
   app.js nữa, nên phải đưa sang.

   DỰNG LẠI MỖI LẦN GỌI, không dựng một lần rồi giữ. Đây là chỗ dễ
   sai nhất và sai thì im lặng: `GAUGES`, `CHAIN`, `TIN`… được
   napChuThe() GÁN LẠI mỗi lần đổi chủ thể. Giữ một bản K cũ nghĩa là
   bấm sang Trung Quốc mà vẫn vẽ đồng hồ của Việt Nam — đúng lớp lỗi
   trộn chủ thể cung này đã trả giá một lần.

   63 định danh, tính bằng máy chứ không liệt kê tay: mỗi hàm vẽ
   được quét xem dùng những gì ở phạm vi module. Sót một cái thì
   trang trắng lúc chạy, mà `node --check` không hề thấy. */
function KHUNG(){
  return { BANCO, BOMACH, CHAIN, COMPASS, DANHSACH, DEM, DO, DODAC, DO_LUC, GAUGES, KB, LEVELS, LIB, LVLS, LVNAME, MAU, MUC_MAU, MUC_TEN, OI_GIO, RANH, SCEN, SO, SOI, SOLIEU, TH, THANG, THEATERS, TIEUCHI, TIN, TIN_LUC, ago, capDo, chuThe, demDen, den, el, esc, gGG, gTH, gioDo, go, head, logCT, lvOf, moMuc, mucBC, ngayGon, nguonDen, railChain, railSignal, render, renderNav, sGG, sTH, save, scanAll, sigCT, soDo, spark, state, svg, thanhBC, tuoiDo };
}
/* Gọi một trang. Thiếu tệp trang — mạng hỏng giữa chừng chẳng hạn —
   thì nói thẳng ra chỗ trống thay vì để trang trắng không lý do. */
function trang(ten, ...tsov){
  const T = window.DQT_TRANG || {};
  if (typeof T[ten] !== 'function'){
    const e = el('div','empty');
    e.innerHTML = '<b>Chưa nạp được trang này</b><p>Thiếu tệp <code>assets/js/trang/</code>' +
      ' — thử tải lại trang. Khung và dữ liệu vẫn còn nguyên.</p>';
    return e;
  }
  return T[ten](KHUNG(), ...tsov);
}

function veTuyen(){
  const v=$('#view'); const r=state.route;
  renderTicker();
  if(r==='flow')       return v.innerHTML='', v.appendChild(trang('vFlow'));
  if(r==='chain')      return v.innerHTML='', v.appendChild(trang('vChain'));
  if(r==='gauges')     return v.innerHTML='', v.appendChild(trang('vGauges'));
  if(r==='levels')     return v.innerHTML='', v.appendChild(trang('vLevels'));
  if(r==='scen')       return v.innerHTML='', v.appendChild(trang('vScen'));
  if(r==='compass')    return v.innerHTML='', v.appendChild(trang('vCompass'));
  if(r==='src')        return v.innerHTML='', v.appendChild(trang('vSrc'));
  if(r==='soi')        return v.innerHTML='', v.appendChild(trang('vKhung'));
  if(r==='banco')      return v.innerHTML='', v.appendChild(trang('vBanCo'));
  if(r==='bomach')     return v.innerHTML='', v.appendChild(trang('vBoMach', null));
  if(r.startsWith('bomach/')) return v.innerHTML='', v.appendChild(trang('vBoMach', r.slice(7)));
  if(r.startsWith('th/'))  return v.innerHTML='', v.appendChild(trang('vTheater', r.slice(3)));
  if(r.startsWith('lib/')) return v.innerHTML='', v.appendChild(trang('vLib', r.slice(4)));
  if(r.startsWith('soi/')){ const p=r.slice(4).split('/');
    return v.innerHTML='', v.appendChild(trang('vSoi', p[0], p[1])); }
  go(dauTien());
}

/* ---------- DÒNG TIN THẾ GIỚI ---------- */
/* Ngày ISO → dd/mm. Không dùng toLocaleDateString vì nó đổi theo máy
   người xem, và hai người đọc cùng một bảng phải thấy cùng một ngày. */
function ngayGon(s){ const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(s||''); return m? m[3]+'/'+m[2] : ''; }

const MUC_TEN = {cao:'ẢNH HƯỞNG CAO', vua:'ẢNH HƯỞNG VỪA', thap:'ẢNH HƯỞNG THẤP'};
const MUC_MAU = {cao:'r', vua:'y', thap:'g'};

function mucBC(k){ return THANG.find(x=>x.k===k) || THANG[THANG.length-1]; }

/* Thanh 4 vạch. Đọc được bằng mắt trước khi đọc bằng chữ — đó là
   toàn bộ mục đích: nhìn phát thấy chỗ nào đầy, chỗ nào rỗng. */
function thanhBC(k){
  const m=mucBC(k), b=el('span','bc');
  let s='';
  for(let i=1;i<=4;i++) s+='<i'+(i<=m.n?' class="on" style="background:'+m.acc+'"':'')+'></i>';
  b.innerHTML=s+'<b style="color:'+m.acc+'">'+m.t+'</b>';
  return b;
}

function moMuc(sid,m){
  const v=state.muc['soi:'+sid+':'+m.id];
  return v===undefined ? !!m.mo : v;
}

/* Bộ vẽ khối. Thêm kiểu mới = thêm một nhánh ở đây, dữ liệu
   trong soi.js không phải biết gì về DOM. */

function openRail(title,kind,html){
  $('#rtitle').textContent=title; $('#rkind').textContent=kind;
  $('#railbody').innerHTML=html; $('#app').classList.add('rail-open');
}
function closeRail(){ $('#app').classList.remove('rail-open'); }

function railChain(n,lv){
  const t=n.th?TH(n.th):null;
  let h='<div class="rl"><div class="rl-h">Vai trò trong mạch</div><p>'+esc(n.d)+'</p></div>'+
    (n.vi?'<div class="rl"><div class="rl-h">Truyền hay hấp thụ</div><p>'+n.vi+'</p></div>':'')+
    '<div class="rl"><div class="rl-h">Trạng thái</div><div class="chips"><span class="chip '+lv+'">'+LVNAME[lv]+'</span><span class="chip">'+esc(n.tag)+'</span></div></div>';
  h+='<div class="rl"><div class="rl-h">Nguồn màu</div><p class="muted" style="font-size:12.5px">Lấy từ '+srcLabel(n.id)+'. Đổi ở đó thì mắt xích này đổi theo.</p></div>';
  const idx=CHAIN.findIndex(c=>c.id===n.id);
  if(idx>0) h+='<div class="rl"><div class="rl-h">Nhận từ</div><p>'+esc(CHAIN[idx-1].t)+'</p></div>';
  if(idx<CHAIN.length-1) h+='<div class="rl"><div class="rl-h">Truyền sang</div><p>'+esc(CHAIN[idx+1].t)+'</p></div>';
  if(t) h+='<button class="tbtn" onclick="go(\'th/'+t.id+'\')">Mở hồ sơ '+esc(t.short)+'</button>';
  else h+='<button class="tbtn" onclick="go(\'gauges\')">Mở bảng đồng hồ</button>';
  openRail(n.t,'MẮT XÍCH '+(idx+1)+'/'+CHAIN.length,h);
}

function railSignal(s){
  const t=TH(s.th)||{};
  let h='<div class="rl"><div class="rl-h">Tín hiệu</div><p style="color:var(--fg);font-size:13.5px">'+esc(s.tieu_de)+'</p></div>';
  if(s.tac_dong) h+='<div class="rl"><div class="rl-h">Đường truyền dẫn tới '+esc(chuThe(state.cht).ten)+'</div><p>'+esc(s.tac_dong)+'</p></div>';
  h+='<div class="rl"><div class="rl-h">Chi tiết</div><dl class="kv">'+
     '<dt>chiến trường</dt><dd>'+esc(t.name||s.th)+'</dd>'+
     '<dt>ngày</dt><dd>'+esc(s.ngay||'—')+'</dd>'+
     '<dt>nguồn</dt><dd>'+esc(s.nguon||'—')+'</dd>'+
     '<dt>ghi lúc</dt><dd>'+ago(s.at)+'</dd>'+
     (s.muc?'<dt>mức đọc</dt><dd>'+LVNAME[s.muc]+'</dd>':'')+'</dl></div>';
  h+='<div class="rl"><div class="rl-h">Lưu ý</div><p class="muted" style="font-size:12.5px">Tín hiệu do lần quét trả về. Hãy mở nguồn gốc để kiểm chứng trước khi dùng — bảng này không thay thế việc đọc nguồn.</p></div>';
  h+='<button class="tbtn" onclick="go(\'th/'+s.th+'\')">Mở chiến trường</button>';
  openRail(t.short||'Tín hiệu','TÍN HIỆU TRỰC TIẾP',h);
}

/* ============================================================
   NẠP BẢN QUÉT

   Bản gốc gọi thẳng api.anthropic.com từ trình duyệt — và không
   gửi kèm khoá nào, nên lời gọi đó chưa bao giờ thành công: mọi
   lần bấm đều rơi vào nhánh catch.

   Không sửa được bằng cách thêm khoá vào đây. Trang này chạy trên
   GitHub Pages công khai, nên khoá nhúng trong mã là khoá bị lộ —
   ai mở DevTools cũng lấy được và tiêu tiền của chủ nhân.

   Nên việc quét chuyển sang chạy trên máy chủ: GitHub Actions gọi
   API bằng khoá trong Secrets, ghi kết quả ra scan.js, trang này
   chỉ đọc file đó. Xem scripts/build-scan.mjs.
   ============================================================ */
/* Nạp bản quét của MỌI chủ thể có khai đường quét, và gắn cờ 'cht' lên
   từng dòng. Trước đây hàm này đọc thẳng window.DQT_SCAN rồi đổ hết vào
   một rổ — nên tin Hormuz của Việt Nam hiện nguyên trong Dòng chảy của
   Trung Quốc. Lọc theo id chiến trường KHÔNG cứu được: "nga" là id có ở
   cả hai nước.

   Mức đèn cũng phải ghi vào khoá của ĐÚNG chủ thể sở hữu bản quét, chứ
   không phải chủ thể đang xem — nạp lúc đang đứng ở Trung Quốc mà dùng
   sTH() thì bản quét Việt Nam sẽ thắp đèn cho Trung Quốc. */
function loadScan(){
  CHUTHE.forEach(c => {
    if(!c.khoScan) return;
    const S = window[c.khoScan];
    if(!S || !Array.isArray(S.signals)) return;

    const seen = new Set(state.sig.filter(x=>(x.cht||'vn')===c.id).map(x => x.tieu_de));
    S.signals.forEach(sg => {
      if(!sg.tieu_de || seen.has(sg.tieu_de)) return;
      seen.add(sg.tieu_de);
      state.sig.push(Object.assign({}, sg, {cht:c.id}));
    });

    Object.keys(S.levels||{}).forEach(id => {
      if(LVLS.includes(S.levels[id])) state.th[c.id+':'+id] = S.levels[id];
    });

    (S.log||[]).forEach(e => {
      if(!state.log.some(x => x.at===e.at && x.t===e.t && (x.cht||'vn')===c.id))
        state.log.push(Object.assign({}, e, {cht:c.id}));
    });
  });
  state.sig.sort((a,b) => String(b.at||'').localeCompare(String(a.at||'')));
  state.sig = state.sig.slice(0,160);
  state.log.sort((a,b) => String(b.at||'').localeCompare(String(a.at||'')));
  state.log = state.log.slice(0,80);
}

/* Nút "Quét trực tiếp" giờ chỉ lấy lại bản mới nhất từ máy chủ —
   không gọi mô hình từ trình duyệt. */
async function scanAll(){
  if(state.scanning) return;
  const ct = chuThe(state.cht);
  /* Nói thẳng thay vì lặng lẽ nạp bản quét của nước khác. Đây đúng là
     chỗ trộn cũ: bấm Quét ở Trung Quốc thì nó tải scan.js của Việt Nam. */
  if(!ct.tepScan){
    toast('Chưa có đường quét tự động cho ' + ct.ten + ' — Dòng chảy trống là đúng.');
    return;
  }
  state.scanning = true;
  $('#scanAll').disabled = true;
  toast('Đang lấy bản quét mới nhất…', true);
  try{
    const res = await fetch(ct.tepScan + '?t=' + Date.now(), {cache:'no-store'});
    if(!res.ok) throw new Error('HTTP ' + res.status);
    const txt = await res.text();
    // scan.js là script thường gán window.DQT_SCAN — chạy lại trong phạm vi riêng
    new Function(txt)();
    const before = sigCT().length;
    loadScan();
    const added = sigCT().length - before;
    toast(added ? ('✓ thêm ' + added + ' tín hiệu mới') : 'Đã là bản mới nhất');
  }catch(err){
    state.log.unshift({ok:false, cht:state.cht, t:'nạp bản quét',
      d:'Không đọc được ' + ct.tepScan + ' — ' + (err.message||err), at:new Date().toISOString()});
    toast('Không lấy được bản quét. Xem Nguồn & nhật ký.');
  }
  state.scanning = false; $('#scanAll').disabled = false;
  save(); renderNav(); render();
}

/* ============================================================
   COMMAND PALETTE
   ============================================================ */
let cmdItems=[], cmdSel=0;
function allCmds(){
  const out=[];
  ROUTES.forEach(s=>s.items.forEach(i=>out.push({t:i.t,g:s.g,go:()=>go(i.id)})));
  
  out.push({t:'Lấy bản quét mới nhất',g:'Hành động',go:scanAll});
  return out;
}
function openCmd(){ $('#cmdk').classList.add('on'); $('#cmdin').value=''; filterCmd(''); $('#cmdin').focus(); }
function closeCmd(){ $('#cmdk').classList.remove('on'); }
function norm(s){ return s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d').toLowerCase(); }
function filterCmd(q){
  const n=norm(q); cmdItems=allCmds().filter(c=>!n||norm(c.t).includes(n)||norm(c.g).includes(n)); cmdSel=0; drawCmd();
}
function drawCmd(){
  $('#cmdlist').innerHTML = cmdItems.length? cmdItems.map((c,i)=>'<button class="cmdi'+(i===cmdSel?' sel':'')+'" data-i="'+i+'">'+esc(c.t)+'<span class="g">'+esc(c.g)+'</span></button>').join('')
    : '<div style="padding:20px;text-align:center;color:var(--dim);font-size:13px">Không có mục nào khớp</div>';
  $('#cmdlist').querySelectorAll('.cmdi').forEach(b=>b.onclick=()=>{ closeCmd(); cmdItems[+b.dataset.i].go(); });
}

/* ============================================================
   KHỞI ĐỘNG
   ============================================================ */
/* Đếm từ chính dữ liệu. Bản đầu viết cứng "11 mắt xích / 8 đồng hồ /
   5 chiến trường"; thêm mắt xích hay chiến trường là màn khởi động
   nói sai ngay từ giây đầu mà không có gì báo. */
const BOOTLN=['khởi tạo đài quan trắc…','nạp '+LIB.length+' cụm hồ sơ nền',
  'dựng mạch truyền dẫn '+CHAIN.length+' mắt xích','hiệu chỉnh '+GAUGES.length+' đồng hồ cảnh báo',
  'mở dòng chảy '+THEATERS.length+' chiến trường','sẵn sàng'];
function boot(){
  const b=$('#boot'); const red=!!(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  if(red){ b.classList.add('off'); setTimeout(()=>b.remove(),300); return; }
  BOOTLN.forEach((l,i)=>{ const d=el('div','ln',(i===BOOTLN.length-1?'<span class="ok">✓ </span>':'· ')+l); d.style.animationDelay=(i*0.13)+'s'; b.appendChild(d); });
  setTimeout(()=>{ b.classList.add('off'); setTimeout(()=>b.remove(),500); }, 1150);
}

document.addEventListener('keydown',e=>{
  if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){ e.preventDefault(); $('#cmdk').classList.contains('on')?closeCmd():openCmd(); return; }
  if(e.key==='Escape'){ if($('#cmdk').classList.contains('on')) closeCmd(); else closeRail(); return; }
  if($('#cmdk').classList.contains('on')){
    if(e.key==='ArrowDown'){ e.preventDefault(); cmdSel=Math.min(cmdSel+1,cmdItems.length-1); drawCmd(); }
    if(e.key==='ArrowUp'){ e.preventDefault(); cmdSel=Math.max(cmdSel-1,0); drawCmd(); }
    if(e.key==='Enter'&&cmdItems[cmdSel]){ closeCmd(); cmdItems[cmdSel].go(); }
  }
});
$('#cmdin').addEventListener('input',e=>filterCmd(e.target.value));
$('#cmdk').addEventListener('click',e=>{ if(e.target.id==='cmdk') closeCmd(); });
$('#collapse').onclick=()=>{ const a=$('#app'); a.classList.toggle('nav-collapsed');
  $('#collapse').textContent = a.classList.contains('nav-collapsed')?'›':'‹ Thu gọn'; };
$('#hamb').onclick=()=>{ $('#nav').classList.toggle('open'); $('#scrim').classList.toggle('on'); };
$('#scrim').onclick=()=>{ $('#nav').classList.remove('open'); $('#scrim').classList.remove('on'); };
$('#scanAll').onclick=scanAll;
window.addEventListener('hashchange',()=>{ const h=location.hash.slice(1); if(h&&h!==state.route){ state.route=h; renderNav(); render(); } });

(async function init(){
  boot();
  await load();
  /* SAU load() vì load() có thể khôi phục state.cht đã lưu — nạp
     trước thì dựng dữ liệu của nước mặc định rồi mới biết người
     dùng đang đứng ở nước khác. */
  napChuThe();
  veChuThe();
  loadScan();
  const h=location.hash.slice(1); if(h) state.route=h;
  renderNav(); render();
})();

/* Bốn hàm này được gọi từ thuộc tính onclick= trong HTML, mà HTML
   không nhìn thấy phạm vi của IIFE — phải phơi ra window.
   (Bản gốc không cần vì mọi thứ nằm ở phạm vi toàn cục.) */
window.scanAll   = scanAll;
window.openCmd   = openCmd;
window.closeRail = closeRail;
window.go        = go;
})();