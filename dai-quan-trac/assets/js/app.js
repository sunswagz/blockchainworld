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
  return '<svg class="spk" viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none" aria-hidden="true">'+
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
function hideToast(){ $('#toast').classList.remove('on'); }

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

function render(){
  const v=$('#view'); const r=state.route;
  renderTicker();
  if(r==='flow')       return v.innerHTML='', v.appendChild(vFlow());
  if(r==='chain')      return v.innerHTML='', v.appendChild(vChain());
  if(r==='gauges')     return v.innerHTML='', v.appendChild(vGauges());
  if(r==='levels')     return v.innerHTML='', v.appendChild(vLevels());
  if(r==='scen')       return v.innerHTML='', v.appendChild(vScen());
  if(r==='compass')    return v.innerHTML='', v.appendChild(vCompass());
  if(r==='src')        return v.innerHTML='', v.appendChild(vSrc());
  if(r==='soi')        return v.innerHTML='', v.appendChild(vKhung());
  if(r==='banco')      return v.innerHTML='', v.appendChild(vBanCo());
  if(r==='bomach')     return v.innerHTML='', v.appendChild(vBoMach(null));
  if(r.startsWith('bomach/')) return v.innerHTML='', v.appendChild(vBoMach(r.slice(7)));
  if(r.startsWith('th/'))  return v.innerHTML='', v.appendChild(vTheater(r.slice(3)));
  if(r.startsWith('lib/')) return v.innerHTML='', v.appendChild(vLib(r.slice(4)));
  if(r.startsWith('soi/')){ const p=r.slice(4).split('/');
    return v.innerHTML='', v.appendChild(vSoi(p[0], p[1])); }
  go(dauTien());
}

/* ---------- DÒNG TIN THẾ GIỚI ---------- */
/* Ngày ISO → dd/mm. Không dùng toLocaleDateString vì nó đổi theo máy
   người xem, và hai người đọc cùng một bảng phải thấy cùng một ngày. */
function ngayGon(s){ const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(s||''); return m? m[3]+'/'+m[2] : ''; }

const MUC_TEN = {cao:'ẢNH HƯỞNG CAO', vua:'ẢNH HƯỞNG VỪA', thap:'ẢNH HƯỞNG THẤP'};
const MUC_MAU = {cao:'r', vua:'y', thap:'g'};

function vTin(){
  const box=el('div','tin-khoi');
  const ng=(window.DQT_TIN||{}).nguon||{};
  box.innerHTML='<div class="tin-dau"><b>DÒNG TIN THẾ GIỚI</b>'+
    '<span>'+TIN.length+' bài liên quan tới '+esc(chuThe(state.cht).ten)+
    (TIN_LUC?' · lấy về '+esc(gioDo(TIN_LUC)):'')+'</span></div>';

  const luoi=el('div','tin-luoi');
  TIN.forEach(b=>{
    const th=el('article','tin-the');
    const nh=ng[b.n]||{t:b.n,l:''};
    /* Nguồn nhà nước phải LỘ RA ngay trên thẻ. Đọc được một bản tin
       thì trước hết phải biết mình đang đọc ai — đó là "sáu dấu ≠"
       của cung này áp vào chỗ lấy tin. */
    const nn=/NHÀ NƯỚC/.test(nh.l||'');

    /* Phần bài báo là một thẻ <a> thật: bấm ra đúng trang gốc, mở tab
       mới, và người dùng vẫn chuột phải / xem trước link được. */
    const a=el('a','tin-bai');
    a.href=b.u; a.target='_blank'; a.rel='noopener noreferrer';
    a.innerHTML=
      (b.img?'<span class="tin-anh"><img src="'+esc(b.img)+'" alt="" loading="lazy" '+
        'referrerpolicy="no-referrer" onerror="this.parentNode.remove()"></span>':'')+
      '<span class="tin-than">'+
        '<span class="tin-meta"><span class="tin-ng'+(nn?' nn':'')+'">'+esc(nh.t)+'</span>'+
        (nh.l?'<i>'+esc(nh.l)+'</i>':'')+
        (b.ng?'<em>'+esc(ngayGon(b.ng))+'</em>':'')+'</span>'+
        '<b>'+esc(b.t)+'</b>'+
        (b.mo?'<p>'+esc(b.mo)+'</p>':'')+
        '<span class="tin-di">đọc ở '+esc(nh.t)+' →</span>'+
      '</span>';
    th.appendChild(a);

    const ai=el('div','tin-ai');
    if(b.ai){
      const mx=CHAIN.find(c=>c.id===b.ai.mach);
      ai.innerHTML='<div class="tin-ai-h"><span>AI SUY LUẬN</span>'+
        '<span class="chip '+(MUC_MAU[b.ai.muc]||'')+'">'+esc(MUC_TEN[b.ai.muc]||'')+'</span>'+
        (mx?'<button class="tin-mx" onclick="go(\'chain\')">mắt xích: '+esc(mx.t)+' →</button>':'')+
        '</div><p>'+esc(b.ai.anh)+'</p>';
    } else {
      /* Chưa có thì nói chưa có. Lấp bằng một câu chung chung là dạy
         người đọc rằng khối này lúc nào cũng có chữ, và từ đó họ
         thôi phân biệt được lúc nào là suy luận thật. */
      ai.className='tin-ai trong';
      ai.innerHTML='<p>Chưa có phân tích cho bài này — lượt quét gần nhất chưa xử lý tới nó.</p>';
    }
    th.appendChild(ai);
    luoi.appendChild(th);
  });
  box.appendChild(luoi);

  const ch=el('p','tin-chan');
  ch.innerHTML='Bài viết và ảnh thuộc về nguồn, hiện nguyên văn tiêu đề và tóm tắt trong RSS của họ. '+
    '<b>Khối AI bên dưới mỗi bài là SUY LUẬN của model</b>, dựa trên tiêu đề, tóm tắt và mạch truyền dẫn '+
    'của '+esc(chuThe(state.cht).ten)+' — không phải trích dẫn từ bài, và có thể sai. Mỗi suy luận buộc phải '+
    'trỏ vào một mắt xích có thật; suy luận nào trỏ vào mắt xích không tồn tại đã bị loại từ lúc dựng.';
  box.appendChild(ch);
  return box;
}

/* ---------- DÒNG CHẢY ---------- */
function vFlow(){
  head('Dòng chảy','REALTIME · '+sigCT().length+' TÍN HIỆU');
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Quan trắc liên tục</div>'+
   '<h2 class="big">Dòng chảy địa chính trị</h2>'+
   '<p class="lede">'+(THEATERS.length
     ? THEATERS.length+' chiến trường, một dòng. Mỗi tín hiệu được ghi kèm <b>đường truyền dẫn tới '+esc(chuThe(state.cht).ten)+'</b> — vì một sự kiện chỉ đáng theo dõi khi biết nó chạy vào đâu.'
     : 'Bài viết từ các nguồn tin đã chọn, kèm một lớp suy luận về việc chúng chạm vào <b>khớp nối</b> ở chỗ nào. '+esc(chuThe(state.cht).ten)+' không có chiến trường riêng — nó đọc lại hai bảng kia.')+'</p>';

  /* Dải trạng thái — thứ phải đọc được trong hai giây, đặt trên
     cùng trang đầu. Cấp độ bên trái, 11 đèn bên phải: nhìn phát
     biết hệ thống đang ở đâu và đèn nào kéo nó lên. */
  /* Chủ thể không có chiến trường thì trang này CHỈ là dòng tin —
     không dải trạng thái, không bộ lọc, không mục tín hiệu. */
  if(!THEATERS.length){ if(TIN.length) w.appendChild(vTin()); return w; }
  const lvl=capDo(), dm=demDen();
  const st=el('div','trang-thai'+(lvl?' c'+lvl:''));
  let bulbs='';
  GAUGES.forEach(g=>{ const lv=den(g.id), ng=nguonDen(g.id);
    bulbs+='<i class="'+lv+(ng==='tay'?' tay':'')+'" title="'+esc(g.t)+' — '+LVNAME[lv]+
      (ng==='tay'?' (bạn đặt)':ng==='tu'?' (tự đo)':'')+'"></i>'; });
  st.innerHTML=
    '<div class="tt-cap"><span class="tt-n">'+(lvl||'—')+'</span>'+
      '<span class="tt-t"><b>'+(lvl?esc(LEVELS[lvl-1].t):'CHƯA ĐỌC RA')+'</b>'+
      '<i>'+(lvl?dm.r+' đỏ · '+dm.y+' vàng · '+dm.g+' xanh':'chưa đèn nào sáng')+'</i></span></div>'+
    '<div class="tt-den">'+bulbs+'</div>'+
    '<a class="tt-go" href="#gauges" onclick="go(\'gauges\');return false">bảng đồng hồ →</a>';
  w.appendChild(st);

  if(TIN.length) w.appendChild(vTin());

  // filter
  const fb=el('div','fbar');
  const mk=(id,label,n)=>{const b=el('button','fchip'+(state.filter===id?' on':''));
    b.innerHTML=esc(label)+(n!=null?' <span class="n">'+n+'</span>':''); b.onclick=()=>{state.filter=id;render();}; return b;};
  fb.appendChild(mk('all','Tất cả',sigCT().length));
  THEATERS.forEach(t=>fb.appendChild(mk(t.id,t.short,sigCT().filter(s=>s.th===t.id).length)));
  w.appendChild(fb);

  const list=sigCT().filter(s=>state.filter==='all'||s.th===state.filter);
  if(!list.length){
    const e=el('div','empty');
    e.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'+
      '<b>Chưa có tín hiệu nào trong dòng</b>'+
      '<p>Dòng chảy chỉ chứa dữ liệu thật lấy về từ lần quét. Chưa quét thì ở đây trống — không có tin giả lập.</p>'+
      '<button class="tbtn pri" style="margin:0 auto" onclick="scanAll()">Lấy bản quét mới nhất</button>';
    e.style.marginTop='24px';
    w.appendChild(e);
    const note=el('div','card'); note.style.marginTop='20px';
    note.innerHTML='<div class="card-h"><b>TRONG LÚC CHỜ</b></div><div class="card-b">'+
      '<p class="muted" style="font-size:12.5px;margin:0">Khung phân tích thì đã sẵn sàng: <a href="#chain" onclick="go(\'chain\')">Mạch truyền dẫn</a> cho biết cú sốc chạy qua đâu, '+
      '<a href="#gauges" onclick="go(\'gauges\')">Bảng cảnh báo sớm</a> để bạn tự đặt Xanh/Vàng/Đỏ, và <a href="#lib/mainboard" onclick="go(\'lib/mainboard\')">Mainboard</a> gói cả bốn hệ vào một sơ đồ.</p></div>';
    w.appendChild(note);
    return w;
  }

  const feed=el('div','feed');
  list.forEach((s,i)=>{
    const t=TH(s.th)||{};
    const ev=el('div','ev'+(s.fresh?' fresh':''));
    ev.innerHTML='<div class="ev-gut"><span class="ev-dot" style="background:'+(t.acc||'#58a6ff')+'"></span><span class="ev-line"></span></div>';
    const b=el('div','ev-b');
    const card=el('button','ev-card'+(s.fresh?' newflash':''));
    card.innerHTML=
      '<div class="ev-m"><span class="chip" style="border-color:'+(t.acc||'#333')+'66;color:'+(t.acc||'#aaa')+'">'+esc(t.short||s.th)+'</span>'+
      (s.muc?'<span class="chip '+s.muc+'">'+LVNAME[s.muc].toUpperCase()+'</span>':'')+
      '<span class="ev-time">'+esc(s.ngay||'')+' · '+ago(s.at)+'</span></div>'+
      '<div class="ev-txt">'+esc(s.tieu_de)+'</div>'+
      (s.tac_dong?'<div class="ev-imp"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg><span>'+esc(s.tac_dong)+'</span></div>':'')+
      (s.nguon?'<div class="ev-src"><span class="chip">nguồn</span>'+esc(s.nguon)+'</div>':'');
    card.onclick=()=>railSignal(s);
    b.appendChild(card); ev.appendChild(b); feed.appendChild(ev);
    s.fresh=false;
  });
  w.appendChild(feed);
  return w;
}

/* ---------- MẠCH TRUYỀN DẪN (chữ ký) ---------- */
function vChain(){
  head('Mạch truyền dẫn',CHAIN.length+' MẮT XÍCH · THƯỢNG NGUỒN → HẠ NGUỒN');
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Chương XX · chuỗi khóa vào nhau</div>'+
   '<h2 class="big">Cú sốc chạy qua đâu để tới cái ví của bạn</h2>'+
   '<p class="lede">Muốn biết hệ thống có đang thật sự <b>khóa vào nhau</b> hay không thì nhìn chuỗi này, không nhìn GDP. Mỗi mắt xích sáng lên theo mức bạn đặt ở bảng đồng hồ; dây dẫn chỉ chảy khi mắt xích phía trên đã ở vàng hoặc đỏ.</p>';

  const c=el('div','circuit');
  CHAIN.forEach((n,i)=>{
    const lv=lvOf(n.id);
    const prev = i>0 ? lvOf(CHAIN[i-1].id) : 'n';
    const liveIn  = i>0 && (prev==='y'||prev==='r');
    const liveOut = i<CHAIN.length-1 && (lv==='y'||lv==='r');
    const node=el('div','cnode');
    node.innerHTML =
      '<div class="cn-gut">'+
        (i>0?'<div class="cn-wire top '+(liveIn?'live':'')+'" style="--d:'+(i*.14)+'s"></div>':'<div style="height:17px"></div>')+
        '<div class="cn-mark '+lv+'">'+(i+1)+'</div>'+
        (i<CHAIN.length-1?'<div class="cn-wire bot '+(liveOut?'live':'')+'" style="--d:'+(i*.14+.07)+'s"></div>':'')+
      '</div>';
    const body=el('div','cn-body');
    const btn=el('button','cn-btn');
    btn.innerHTML='<div class="cn-top"><b>'+esc(n.t)+'</b><span class="chip '+lv+'">'+LVNAME[lv]+'</span><span class="cn-tag">'+esc(n.tag)+'</span></div>'+
      '<div class="cn-note">'+esc(n.d)+'</div>';
    btn.onclick=()=>railChain(n,lv);
    body.appendChild(btn); node.appendChild(body); c.appendChild(node);
  });
  w.appendChild(c);

  const note=el('div','card'); note.style.marginTop='18px';
  note.innerHTML='<div class="card-h"><b>ĐỌC MẠCH NÀY THẾ NÀO</b></div><div class="card-b">'+
    '<p style="margin:0 0 10px">Không phải cứ mắt xích đầu đỏ là mắt xích cuối đỏ theo. Giữa chúng có <b>bộ đệm</b>'+
      (DEM.length?' — '+DEM.map(esc).join(', '):'')+'. Bộ đệm hấp thụ một phần và làm chậm phần còn lại, và đó là lý do một cú sốc rất lớn vẫn có thể không đi tới đâu.</p>'+
    '<p style="margin:0" class="muted">Điều đáng lo không phải một mắt xích đỏ, mà là <b>nhiều mắt xích liền kề cùng chuyển vàng trong một khoảng thời gian ngắn</b> — lúc đó chúng bắt đầu khuếch đại lẫn nhau thay vì hấp thụ cho nhau.</p></div>';
  w.appendChild(note);
  return w;
}

/* ---------- BẢNG ĐỒNG HỒ ---------- */
function vGauges(){
  const d=demDen(), N=GAUGES.length, tuDo=GAUGES.filter(g=>soDo(g.id)).length;
  /* Nguồn im quá lâu — đếm riêng để nói ra, chứ không lặng lẽ trừ đi. */
  const chet=GAUGES.filter(g=>DO[g.id]&&!soDo(g.id));
  head('Bảng cảnh báo sớm',d.dat+'/'+N+' ĐỒNG HỒ SÁNG');
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Đo tự động + phán đoán của bạn</div>'+
   '<h2 class="big">'+N+' đồng hồ, ba màu</h2>'+
   '<p class="lede"><b>'+tuDo+' đồng hồ tự đo</b> từ nguồn công khai, cập nhật 4 lượt/ngày, không gọi AI. '+
   (N-tuDo)+' đồng hồ còn lại chưa có nguồn miễn phí đủ tin nên vẫn <b>đặt tay</b> — nhấp để xoay vòng '+
   '<span class="chip g">xanh</span> → <span class="chip y">vàng</span> → <span class="chip r">đỏ</span>. '+
   'Đèn bạn tự đặt <b>luôn thắng</b> số đo; bấm hết vòng là trả lại cho máy đo.</p>';

  if(DO_LUC){
    const b=el('div','do-luc');
    b.innerHTML='<span class="dot '+(chet.length?'y':'g')+'"></span> Số đo gần nhất '+esc(gioDo(DO_LUC))+
      ' · Yahoo Finance · open.er-api · Federal Register · <b>0 đồng chi phí</b>'+
      (chet.length?'<br><b style="color:var(--gold)">'+chet.length+' nguồn đã im hơn '+OI_GIO+' giờ</b> — '+
        chet.map(g=>esc(g.t)).join(', ')+'. Số cũ vẫn hiện nhưng KHÔNG còn thắp đèn.':'');
    w.appendChild(b);
  }

  const card=el('div','card');
  card.appendChild(el('div','card-h','<b>THỨ TỰ TỪ THƯỢNG NGUỒN XUỐNG</b><span class="chip">'+d.dat+'/'+N+'</span>'));
  const body=el('div');
  GAUGES.forEach((g,i)=>{
    const lv=den(g.id), ng=nguonDen(g.id), m=DO[g.id];
    /* Số vẫn hiện, nhưng kèm tuổi thật của nó. Giấu đi thì người đọc
       mất manh mối; hiện trơn thì họ tưởng là số sống. */
    const cu=m&&!soDo(g.id) ? Math.round(tuoiDo(m)) : null;
    const row=el('button','gauge g-'+ng); row.style.width='100%'; row.style.textAlign='left';

    let so='';
    if(cu!=null){
      /* Đặt TRƯỚC ô số, không phải sau: người đọc thấy con số trước
         rồi mới thấy chú thích thì họ đã tin con số mất rồi. */
      so+='<span class="do-chet">nguồn im '+(cu>=48?Math.round(cu/24)+' ngày':cu+' giờ')+
        ' — số dưới đây là lần lấy được cuối cùng, không phải số hiện tại</span>';
    }
    if(m){
      const dd = m.doi7==null ? '' : '<i class="'+(m.doi7>0?'up':m.doi7<0?'dn':'')+'">'+
        (m.doi7>0?'▲ +':m.doi7<0?'▼ ':'')+m.doi7+'% / 7 phiên</i>';
      so+='<span class="gauge-s">'+spark(m.lich,MAU[lv])+
         '<b>'+esc(String(m.so))+'</b><span class="dv">'+esc(m.dv||'')+'</span>'+dd+'</span>';
    }
    const nhan = ng==='tay' ? '<span class="pv tay">bạn đặt</span>'
               : ng==='tu'  ? '<span class="pv tu">tự đo '+esc(gioDo(m.luc))+'</span>'
                            : '<span class="pv chua">chưa có nguồn</span>';

    row.innerHTML='<span class="gauge-i '+lv+'">'+(i+1)+'</span>'+
      '<span class="gauge-t"><b>'+esc(g.t)+' '+nhan+'</b><span>'+esc(g.d)+'</span>'+
        (g.vi?'<span class="gauge-vi">'+g.vi+'</span>':'')+'</span>'+
      so+'<span class="meter"><i class="'+lv+'"></i></span>';
    row.onclick=()=>{ const cu=gGG(g.id); sGG(g.id, LVLS[(LVLS.indexOf(cu)+1)%4]); save(); render(); renderNav(); };
    body.appendChild(row);
  });
  card.appendChild(body); w.appendChild(card);

  /* Ngưỡng phải mở ra xem được. Một cái đèn đỏ mà không nói được
     "đỏ theo mốc nào" thì chỉ là một cái đèn đỏ. */
  const ngw=GAUGES.filter(g=>soDo(g.id)&&DO[g.id].nguong);
  if(ngw.length){
    w.appendChild(el('h3','sec','Ngưỡng đang dùng'));
    const p=el('p'); p.style.cssText='max-width:74ch;color:var(--fg2)';
    p.innerHTML='Đây là phần duy nhất mang phán đoán con người. Số thì máy đo, còn <b>ranh giới bao nhiêu là đỏ</b> thì do người đặt — viết một lần, kiểm được, và không đổi ý giữa chừng như một model.';
    w.appendChild(p);
    const tb=el('div','nguong-w');
    ngw.forEach(g=>{ const m=DO[g.id], n=m.nguong;
      const c=el('div','nguong'); c.style.setProperty('--a',MAU[den(g.id)]);
      const vach = n.nghich
        ? '<span class="g">≥ '+n.g+'</span><span class="y">'+n.r+'–'+n.g+'</span><span class="r">≤ '+n.r+'</span>'
        : '<span class="g">≤ '+n.g+'</span><span class="y">'+n.g+'–'+n.r+'</span><span class="r">≥ '+n.r+'</span>';
      c.innerHTML='<b>'+esc(g.t)+'</b><div class="nguong-v">'+vach+'</div><p>'+esc(n.can)+'</p>'+
        (m.ghi?'<p class="nguong-g">'+esc(m.ghi)+'</p>':'');
      tb.appendChild(c); });
    w.appendChild(tb);
  }

  /* Số đo nền — có thật, đo được, nhưng KHÔNG phải đồng hồ chính.
     Tách hẳn ra để không ai tưởng Trung Quốc đã có mười hai đồng hồ
     tự đo, trong khi cả mười hai vẫn đặt tay. */
  const nen = DODAC.filter(x => !x.gg);
  if(nen.length){
    w.appendChild(el('h3','sec','Số đo nền — không phải đồng hồ chính'));
    const p2=el('p'); p2.style.cssText='max-width:74ch;color:var(--fg2)';
    const tuDo2 = GAUGES.filter(g=>DODAC.some(x=>x.gg===g.id)).length;
    p2.innerHTML = (tuDo2===0
      ? 'Cả <b>'+GAUGES.length+'</b> đồng hồ ở trên đo <b>tài khoá và quyền lực</b>, và không cái nào có nguồn công khai miễn phí đủ tin — nên cả '+GAUGES.length+' vẫn <b>đặt tay</b>. '
      : '<b>'+tuDo2+'/'+GAUGES.length+'</b> đồng hồ ở trên đã tự đo được; '+(GAUGES.length-tuDo2)+' cái còn lại chưa có nguồn miễn phí đủ tin nên vẫn <b>đặt tay</b>. ')+
      nen.length+' số dưới đây thì đo được, nhưng chúng chỉ nói <b>lớp cú sốc bên ngoài</b> đang căng hay chùng. Đừng đọc chúng như thước đo sức bền của chế độ.';
    w.appendChild(p2);
    const nw=el('div','nguong-w');
    nen.forEach(x=>{ const m=DO[x.id];
      const c=el('div','nguong'); c.style.setProperty('--a', m?MAU[m.muc]:'var(--vien)');
      const vach = x.nghich
        ? '<span class="g">≥ '+x.g+'</span><span class="y">'+x.r+'–'+x.g+'</span><span class="r">≤ '+x.r+'</span>'
        : '<span class="g">≤ '+x.g+'</span><span class="y">'+x.g+'–'+x.r+'</span><span class="r">≥ '+x.r+'</span>';
      c.innerHTML='<b>'+esc(x.nhan)+'</b>'+
        (m ? '<div class="nguong-v" style="margin-bottom:6px"><b>'+esc(String(m.so))+' '+esc(x.dv||'')+'</b></div>' :
             '<p style="color:var(--fg2)"><i>chưa có lượt đo nào — nguồn đã khai, chờ bot chạy</i></p>')+
        '<div class="nguong-v">'+vach+'</div><p>'+esc(x.can)+'</p>'+
        (x.ghi?'<p class="nguong-g">'+esc(x.ghi)+'</p>':'');
      nw.appendChild(c); });
    w.appendChild(nw);
  }

  const lvl=capDo();
  const s=el('div'); s.style.marginTop='26px';
  s.innerHTML='<h3 class="sec">Suy ra từ bảng đồng hồ</h3>';
  if(!lvl){
    s.innerHTML+='<div class="empty"><b>Chưa đèn nào sáng</b><p>Không suy ra được gì từ một bảng trống — và không nên giả vờ là suy ra được.</p></div>';
  }else{
    const L=LEVELS[lvl-1];
    s.innerHTML+='<div class="card"><div class="card-h"><b>CẤP '+L.n+' — '+esc(L.t)+'</b><span class="chip '+(lvl>2?'r':lvl>1?'y':'g')+'">'+d.r+' đỏ · '+d.y+' vàng</span></div>'+
      '<div class="card-b"><p style="margin:0 0 8px">'+esc(L.d)+'</p><p style="margin:0" class="muted"><b>'+esc(L.r)+'</b></p></div></div>'+
      '<p class="muted" style="font-size:12px;margin-top:10px">Quy tắc đọc: ≥4 đỏ → cấp 4 · ≥2 đỏ → cấp 3 · ≥3 vàng/đỏ → cấp 2 · còn lại → cấp 1. Đây là quy ước của bảng này, không phải một chuẩn mực chính thức.</p>';
  }
  w.appendChild(s);
  return w;
}

/* ---------- CHIẾN TRƯỜNG ---------- */
function vTheater(id){
  const t=TH(id); if(!t) return go('flow'),el('div');
  head(t.name, t.role.toUpperCase());
  document.documentElement.style.setProperty('--acc',t.acc);
  const w=el('div','wrap');
  const lv=gTH(id);
  w.innerHTML='<div class="eyebrow">Chiến trường · '+esc(t.short)+'</div>'+
   '<div style="display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;margin-bottom:10px">'+
     '<div style="font-size:34px;line-height:1">'+t.flag+'</div>'+
     '<div style="flex:1;min-width:220px"><h2 class="big" style="margin-bottom:4px">'+esc(t.name)+'</h2>'+
     '<div class="chips"><span class="chip '+lv+'">'+LVNAME[lv]+'</span><span class="chip b">'+esc(t.role)+'</span><span class="chip p">'+esc(t.scen)+'</span></div></div></div>'+
   '<p class="lede">'+t.lede+'</p>';

  const bar=el('div'); bar.style.cssText='display:flex;gap:8px;flex-wrap:wrap;margin:0 0 22px';
  const sb=el('button','tbtn pri'); sb.innerHTML='Lấy bản quét mới nhất'; sb.onclick=scanAll;
  const cyc=el('button','tbtn'); cyc.innerHTML='Đặt mức: <b style="margin-left:4px">'+LVNAME[lv]+'</b>';
  cyc.onclick=()=>{ sTH(id, LVLS[(LVLS.indexOf(gTH(id))+1)%4]); save(); render(); renderNav(); };
  bar.appendChild(sb); bar.appendChild(cyc); w.appendChild(bar);

  // tín hiệu của chiến trường này
  const mine=sigCT().filter(s=>s.th===id);
  if(mine.length){
    const c=el('div','card'); c.style.marginBottom='6px';
    c.appendChild(el('div','card-h','<b>TÍN HIỆU MỚI NHẤT</b><span class="chip">'+mine.length+'</span>'));
    const b=el('div','card-b'); b.style.paddingTop='6px';
    mine.slice(0,4).forEach(s=>{
      const r=el('button'); r.style.cssText='display:block;width:100%;text-align:left;padding:9px 0;border-bottom:1px solid var(--line)';
      r.innerHTML='<div style="font-size:13px">'+esc(s.tieu_de)+'</div><div class="mono muted" style="font-size:10.5px;margin-top:3px">'+esc(s.ngay||'')+' · '+esc(s.nguon||'')+'</div>';
      r.onclick=()=>railSignal(s); b.appendChild(r);
    });
    c.appendChild(b); w.appendChild(c);
  }

  if(t.mech){
    w.appendChild(el('h3','sec','Cơ chế truyền dẫn'));
    const ol=el('div','card'); const b=el('div','card-b');
    b.innerHTML=t.mech.map((m,i)=>'<div style="display:flex;gap:10px;align-items:flex-start;padding:7px 0'+(i?';border-top:1px solid var(--line)':'')+'">'+
      '<span class="mono" style="color:var(--dim);font-size:10.5px;padding-top:3px">'+String(i+1).padStart(2,'0')+'</span><span>'+m+'</span></div>').join('');
    ol.appendChild(b); w.appendChild(ol);
  }
  if(t.ascii){ const p=el('pre','ascii',esc(t.ascii)); p.style.marginTop='14px'; w.appendChild(p); }

  if(t.layers){
    /* Tiêu đề từ dữ liệu: bản đầu viết cứng 'Hai tầng truyền dẫn', nên
       thêm tầng thứ ba là tiêu đề nói sai mà không có gì báo. */
    w.appendChild(el('h3','sec',t.layersH||'Các tầng truyền dẫn'));
    const g=el('div','grid g2');
    t.layers.forEach(L=>{ const c=el('div','card');
      c.innerHTML='<div class="card-h"><b>'+esc(L.n.toUpperCase())+'</b></div><div class="card-b"><b style="display:block;margin-bottom:6px">'+esc(L.t)+'</b><p class="muted" style="margin:0;font-size:12.5px">'+esc(L.d)+'</p></div>';
      g.appendChild(c); });
    w.appendChild(g);
  }
  if(t.circuits){
    w.appendChild(el('h3','sec','Ba mạch của cỗ máy'));
    const g=el('div','grid g3');
    t.circuits.forEach(c=>{ const k=el('div','card');
      k.innerHTML='<div class="card-h"><b>'+esc(c.k.toUpperCase())+'</b></div><div class="card-b"><b style="display:block;margin-bottom:6px;font-size:13px">'+esc(c.t)+'</b><p class="muted" style="margin:0;font-size:12.5px">'+c.d+'</p></div>';
      g.appendChild(k); });
    w.appendChild(g);
  }
  if(t.buffers){
    w.appendChild(el('h3','sec','Bộ đệm — vì sao không sập ngay'));
    const g=el('div','grid g2');
    t.buffers.forEach((b,i)=>{ const c=el('div','card'); 
      c.innerHTML='<div class="card-b" style="display:flex;gap:11px"><span class="gauge-i g" style="flex:0 0 26px">'+(i+1)+'</span><span><b style="display:block;margin-bottom:3px">'+esc(b.t)+'</b><span class="muted" style="font-size:12.5px">'+esc(b.d)+'</span></span></div>';
      g.appendChild(c); });
    w.appendChild(g);
  }
  /* Khối "nhiều cơ chế song song". Đặt SAU layers/circuits/buffers:
     khung phân tích trước, số đọc được sau — không thì Việt Nam hiện
     thẻ số liệu trước cả bốn tầng truyền dẫn giải thích chúng.
     Tiêu đề lấy từ dữ liệu, không viết cứng như 'Hai tầng truyền dẫn'
     / 'Ba mạch': thêm một mục là tiêu đề nói sai mà không ai báo.
     tt = trạng thái, để phân biệt cái ĐANG ÁP với cái mới ĐANG ĐIỀU
     TRA — gộp hai loại đó làm một là chỗ dễ đọc sai nhất của hồ sơ Mỹ. */
  if(t.mechs){
    w.appendChild(el('h3','sec',t.mechs.h));
    const g=el('div','grid g2');
    t.mechs.ds.forEach(m=>{ const c=el('div','card');
      c.innerHTML='<div class="card-h"><b>'+esc(m.t)+'</b><span class="chip '+(m.c||'')+'">'+esc(m.tt)+'</span></div>'+
        '<div class="card-b"><div class="mono" style="font-size:16px;color:var(--fg);margin-bottom:7px">'+esc(m.ma)+'</div>'+
        '<p class="muted" style="margin:0;font-size:12.5px">'+m.d+'</p></div>';
      g.appendChild(c); });
    w.appendChild(g);
  }

  if(t.keypoint){ const q=el('blockquote'); q.innerHTML=t.keypoint; q.style.marginTop='18px'; w.appendChild(q); }
  if(t.danger){ const q=el('blockquote'); q.innerHTML=t.danger; q.style.borderLeftColor='var(--dgr)'; q.style.background='#f0503f0d'; q.style.marginTop='14px'; w.appendChild(q); }

  w.appendChild(el('h3','sec','Đồng hồ cần theo dõi'));
  const cl=el('div','card'); const cb=el('div');
  /* Số đo THẬT của chiến trường này, nếu có. Trước đây trang chiến
     trường chỉ liệt kê tên các đồng hồ cần theo dõi bằng chữ; nay
     cái nào đã đo được thì hiện luôn con số, ngay cạnh danh sách. */
  const soT = DODAC.filter(x => x.th === t.id && DO[x.id]);
  if(soT.length){
    const dw=el('div','nguong-w'); dw.style.marginBottom='14px';
    soT.forEach(x=>{ const m=DO[x.id];
      const c=el('div','nguong'); c.style.setProperty('--a',MAU[m.muc]);
      c.innerHTML='<b>'+esc(x.nhan)+'</b><div class="nguong-v" style="margin:6px 0">'+
        '<b>'+esc(String(m.so))+' '+esc(x.dv||'')+'</b>'+
        (m.doi7==null?'':' <span style="color:var(--fg2)">('+(m.doi7>0?'+':'')+m.doi7+'% / 7 phiên)</span>')+
        '</div><p style="color:var(--fg2)">'+esc(m.nguon||'')+
          (m.oi?' · <b style="color:var(--gold)">chưa lấy lại được '+
            (tuoiDo(m)==null?'':Math.round(tuoiDo(m))+' giờ')+'</b>':'')+'</p>';
      dw.appendChild(c); });
    cb.appendChild(dw);
  }
  t.clocks.forEach((c,i)=>{ const r=el('div','gauge'); r.innerHTML='<span class="gauge-i n">'+(i+1)+'</span><span class="gauge-t"><b>'+esc(c)+'</b></span>'; cb.appendChild(r); });
  cl.appendChild(cb); w.appendChild(cl);

  w.appendChild(el('h3','sec','Đánh vào '+chuThe(state.cht).ten+' theo đường nào'));
  const hl=el('ul','tight'); hl.innerHTML=t.hits.map(h=>'<li>'+esc(h)+'</li>').join(''); w.appendChild(hl);
  return w;
}

/* ---------- 4 CẤP ĐỘ ---------- */
function vLevels(){
  head(LEVELS.length+' cấp độ','ÁP LỰC → KHỦNG HOẢNG HỆ THỐNG');
  const cur = capDo();
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Chương XVII</div><h2 class="big">Từ "áp lực" đến "khủng hoảng" có '+SO[LEVELS.length]+' cấp</h2>'+
   '<p class="lede">Phần lớn tranh cãi về kinh tế là do hai người đang đứng ở hai cấp khác nhau mà dùng chung một từ. Cấp 1 và cấp '+LEVELS.length+' không phải cùng một câu chuyện ở mức độ khác nhau — chúng khác nhau về <b>cơ chế</b>.</p>';
  const lad=el('div','ladder');
  LEVELS.forEach(L=>{ const d=el('div','lv l'+L.n+(cur===L.n?' on':''));
    d.innerHTML='<div class="lv-n">'+L.n+'</div><div class="lv-b"><b>'+esc(L.t)+(cur===L.n?' — ĐANG ĐỌC RA':'')+'</b><p>'+esc(L.d)+'</p><p style="margin-top:6px;color:var(--fg2)"><b>'+esc(L.r)+'</b></p>'+
      (L.co?'<div class="lv-x"><span>CƠ CHẾ HẤP THỤ</span><p>'+L.co+'</p></div>':'')+
      (L.dau?'<div class="lv-x"><span>DẤU HIỆU QUAN SÁT ĐƯỢC</span><p>'+L.dau+'</p></div>':'')+
      (L.day?'<div class="lv-x"><span>ĐIỀU ĐẨY LÊN CẤP SAU</span><p>'+L.day+'</p></div>':'')+
      '</div>';
    lad.appendChild(d); });
  w.appendChild(lad);
  const q=el('blockquote'); q.style.marginTop='20px';
  q.innerHTML= cur? 'Bảng đồng hồ hiện đang đọc ra <b>cấp '+cur+'</b>. Đây là kết quả của các mức bạn tự đặt, không phải một chẩn đoán độc lập.' 
                  : 'Chưa đặt đồng hồ nào nên chưa cấp nào được tô sáng. <a href="#gauges" onclick="go(\'gauges\')">Đặt bảng đồng hồ</a> trước.';
  w.appendChild(q);
  /* Ranh giới nằm ở đâu là câu hỏi RIÊNG của từng thang. Bốn cấp của
     Việt Nam, năm cấp của Trung Quốc và sáu chặng của Tổng kết gãy ở ba
     chỗ khác nhau. */
  if(RANH){ const q2=el('blockquote'); q2.style.borderLeftColor='var(--purple)';
    q2.style.background='#a371f70d'; q2.innerHTML=RANH; w.appendChild(q2); }
  return w;
}

/* ---------- KỊCH BẢN ---------- */
function vScen(){
  head('Kịch bản A/B/C','PHÂN NHÁNH THEO NGUỒN SỐC');
  const w=el('div','wrap wide');
  /* Tiêu đề và đoạn dẫn lấy từ KB của CHỦ THỂ ĐANG XEM. Ba bảng xếp
     kịch bản theo ba trục hoàn toàn khác nhau — nguồn cú sốc, khả năng
     bù của các hệ, và mức căng của khớp nối — nên một câu dẫn chung là
     một câu sai ở hai chỗ. */
  w.innerHTML='<div class="eyebrow">Ba nhánh</div><h2 class="big">'+
   esc(KB&&KB.tieu ? KB.tieu : 'Kịch bản A/B/C')+'</h2>'+
   (KB&&KB.lede ? '<p class="lede">'+KB.lede+'</p>' : '');
  const g=el('div','grid g3');
  SCEN.forEach(s=>{ const c=el('div','card'); c.style.borderColor=s.acc+'44';
    c.innerHTML='<div class="card-h" style="background:'+s.acc+'12"><b style="color:'+s.acc+'">KỊCH BẢN '+s.k+'</b></div>'+
      '<div class="card-b"><b style="display:block;font-size:14.5px;margin-bottom:3px">'+esc(s.t)+'</b>'+
      '<div class="chip" style="margin-bottom:11px">'+esc(s.w)+'</div>'+
      '<pre class="ascii" style="font-size:10.5px;margin-bottom:12px">'+esc(s.asc)+'</pre>'+
      '<ul class="tight" style="margin:0;font-size:12.5px">'+s.pts.map(p=>'<li>'+esc(p)+'</li>').join('')+'</ul></div>';
    g.appendChild(c); });
  w.appendChild(g);
  if(KB&&KB.ket){ const q=el('blockquote'); q.style.marginTop='22px';
    q.innerHTML=KB.ket; w.appendChild(q); }
  return w;
}

/* ---------- KẸP BỐN PHÍA ---------- */
/* Chỉ còn là bộ VẼ. Nội dung bốn phía nằm ở COMPASS của từng chủ thể —
   Việt Nam bị kẹp giữa các nguồn cú sốc, Trung Quốc thì lõi mới là chỗ
   quyết định, nên hai bản không thể dùng chung một đoạn chữ. */
function vCompass(){
  const ct = chuThe(state.cht), C = COMPASS;
  if(!C){ const w=el('div','wrap');
    w.innerHTML='<p class="lede">Chưa dựng sơ đồ kẹp bốn phía cho '+esc(ct.ten)+'.</p>';
    return w; }
  head('Kẹp bốn phía','VỊ TRÍ CỦA '+ct.ten.toUpperCase());
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">'+esc(C.chuong)+'</div><h2 class="big">'+esc(C.tieu)+'</h2>'+
   '<p class="lede">'+C.lede+'</p>';
  const c=el('div','compass');
  const cell=h=>{ const d=el('div','cp '+h.v);
    d.innerHTML='<div class="side">'+esc(h.side)+'</div><b>'+esc(h.t)+'</b><p>'+esc(h.p)+'</p>';
    if(h.th){ d.style.cursor='pointer'; d.onclick=()=>go('th/'+h.th); } return d; };
  const H = id => C.huong.find(x=>x.v===id);
  if(H('n')) c.appendChild(cell(H('n')));
  if(H('w')) c.appendChild(cell(H('w')));
  const core=el('div','cp core');
  core.innerHTML='<div class="flag">'+C.loi.co+'</div><b>'+esc(C.loi.ten)+'</b>'+
    '<p style="color:var(--fg2)">'+esc(C.loi.d)+'</p>';
  if(C.loi.th){ core.style.cursor='pointer'; core.onclick=()=>go('th/'+C.loi.th); }
  c.appendChild(core);
  if(H('e')) c.appendChild(cell(H('e')));
  if(H('s')) c.appendChild(cell(H('s')));
  w.appendChild(c);
  const q=el('blockquote'); q.style.marginTop='20px'; q.innerHTML=C.ket;
  w.appendChild(q);
  return w;
}

/* ---------- THƯ VIỆN ---------- */
function vLib(id){
  const L=LIB.find(x=>x.id===id); if(!L) return go('flow'),el('div');
  head(L.t,'CỤM '+L.n);
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Hồ sơ nền · cụm '+L.n+'</div><h2 class="big">'+esc(L.t)+'</h2><p class="lede">'+esc(L.d)+'</p>';
  L.blocks.forEach(b=>{
    w.appendChild(el('h3','sec',esc(b.h)));
    if(b.p){ const p=el('p'); p.innerHTML=b.p; p.style.maxWidth='74ch'; p.style.color='var(--fg2)'; w.appendChild(p); }
    if(b.a){ w.appendChild(el('pre','ascii',esc(b.a))); }
  });
  const nav=el('div'); nav.style.cssText='display:flex;gap:8px;flex-wrap:wrap;margin-top:30px;padding-top:20px;border-top:1px solid var(--line)';
  LIB.forEach(o=>{ const b=el('button','fchip'+(o.id===id?' on':'')); b.innerHTML='<span class="n">'+o.n+'</span> '+esc(o.t); b.onclick=()=>go('lib/'+o.id); nav.appendChild(b); });
  w.appendChild(nav);
  return w;
}

/* ---------- BO MẠCH QUYỀN LỰC ----------

   Một tầng một trang, cộng một trang tổng. Hai mươi ổ cắm dồn vào
   một trang thì không ai đọc hết; tách bốn trang thì mỗi trang là
   một câu hỏi trả lời được: ai giữ hệ thống lại, ai cưỡng chế, ai
   giữ tiền, ai nối ra ngoài. */
function veOCam(t){
  const w=el('div');
  const g=el('div','the-w');
  t.ds.forEach(x=>{
    const c=el('div','the'); c.style.setProperty('--a',t.acc);
    c.innerHTML='<b>'+esc(x.ten)+'</b><div class="the-vd">'+esc(x.o)+'</div>'+
      '<p><span style="color:var(--fg2);font-size:11px;letter-spacing:.08em">ĐƯỜNG CHỈ HUY</span><br>'+x.chi+
      '<br><br><span style="color:var(--fg2);font-size:11px;letter-spacing:.08em">CHẠM TỚI</span><br>'+x.cham+
      (x.ghi?'<br><br>'+x.ghi:'')+'</p>';
    g.appendChild(c);
  });
  w.appendChild(g);
  return w;
}
function vBoMach(id){
  if(!BOMACH) return go('flow'), el('div');
  const T = id ? BOMACH.tang.find(x=>x.id===id) : null;
  const tong = BOMACH.tang.reduce((a,t)=>a+t.ds.length,0);
  head(T?T.tn:'Bo mạch 2026', T?('TẦNG '+T.n+' · '+T.ds.length+' Ổ CẮM'):(tong+' Ổ CẮM'));
  const w=el('div','wrap');

  if(!T){
    w.innerHTML='<div class="eyebrow">Giải phẫu bộ máy</div><h2 class="big">Bo mạch quyền lực 2026</h2>'+
      '<p class="lede">'+BOMACH.lede+'</p>';
    w.appendChild(el('pre','ascii',BOMACH.a));
    const q=el('blockquote'); q.innerHTML=BOMACH.ghi; w.appendChild(q);
    w.appendChild(el('h3','sec','Bốn tầng'));
    const g=el('div','the-w');
    BOMACH.tang.forEach(t=>{
      const c=el('button','the'); c.style.setProperty('--a',t.acc); c.style.textAlign='left'; c.style.cursor='pointer';
      c.innerHTML='<b>Tầng '+t.n+' · '+esc(t.t)+'</b><div class="the-vd">'+t.ds.length+' ổ cắm</div><p>'+esc(t.d)+'</p>';
      c.onclick=()=>go('bomach/'+t.id); g.appendChild(c);
    });
    w.appendChild(g);
  } else {
    w.innerHTML='<div class="eyebrow">Bo mạch · tầng '+T.n+'</div><h2 class="big">'+esc(T.t)+'</h2>'+
      '<p class="lede">'+esc(T.d)+'</p>';
    w.appendChild(veOCam(T));
  }

  const nav=el('div'); nav.style.cssText='display:flex;gap:8px;flex-wrap:wrap;margin-top:30px;padding-top:20px;border-top:1px solid var(--line)';
  const bt=el('button','fchip'+(id?'':' on')); bt.textContent='Tổng quan'; bt.onclick=()=>go('bomach'); nav.appendChild(bt);
  BOMACH.tang.forEach(t=>{ const b=el('button','fchip'+(t.id===id?' on':''));
    b.innerHTML='<span class="n">'+t.n+'</span> '+esc(t.tn); b.onclick=()=>go('bomach/'+t.id); nav.appendChild(b); });
  w.appendChild(nav);
  return w;
}

/* ---------- BÀN CỜ MỸ–TRUNG ----------

   Chỗ duy nhất trong cung mà HAI bảng gặp nhau. Bảng Việt Nam hỏi
   "nền kinh tế chịu được không", bảng Trung Quốc hỏi "quyền lực
   giữ được không" — bàn cờ này cho thấy một cú siết vào ổ cắm bên
   kia chảy tới đơn hàng và tỷ giá bên này qua đường nào. */
function vBanCo(){
  if(!BANCO) return go('flow'), el('div');
  head('Bàn cờ Mỹ–Trung','HAI BO MẠCH ĐỐI NHAU');
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Đòn và phản đòn</div><h2 class="big">Bàn cờ Mỹ–Trung</h2>'+
    '<p class="lede">'+BANCO.lede+'</p>';
  w.appendChild(el('pre','ascii',BANCO.a));
  BANCO.cot.forEach(c=>{
    w.appendChild(el('h3','sec',c.t));
    const g=el('div','the-w');
    c.ds.forEach(x=>{ const d=el('div','the'); d.style.setProperty('--a',c.acc);
      d.innerHTML='<b>'+esc(x.n)+'</b><p>'+x.d+'</p>'; g.appendChild(d); });
    w.appendChild(g);
  });
  const q=el('blockquote'); q.style.borderLeftColor='var(--dgr)'; q.style.background='#f0503f0d';
  q.innerHTML=BANCO.ket; w.appendChild(q);
  return w;
}

/* ============================================================
   SOI QUYỀN LỰC

   Hai view, và ranh giới giữa chúng là chỗ quan trọng:
   vKhung() là PHƯƠNG PHÁP — không nhắc tên ai, dùng lại nguyên
   vẹn cho đối tượng sau. vSoi() là MỘT LẦN ÁP DỤNG khung đó.
   Trộn hai thứ vào một trang thì lần soi thứ hai phải viết lại
   từ đầu, và phương pháp lặng lẽ bị uốn theo kết luận.
   ============================================================ */
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

function vKhung(){
  head('Khung 7 tiêu chí','PHƯƠNG PHÁP · DÙNG LẠI ĐƯỢC');
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Soi quyền lực · phương pháp</div>'+
   '<h2 class="big">Bảy chỗ phải soi, và năm mức được phép kết luận</h2>'+
   '<p class="lede">Sáu chiến trường đo cú sốc <b>đi từ ngoài vào</b>. Khung này đo thứ khác hẳn: bộ máy <b>bên trong</b> quyết định vốn chảy về đâu. Nó không phải nguồn sốc — nó là bộ khuếch đại và bộ chia.</p>';

  const q=el('blockquote');
  q.innerHTML='Câu hỏi "X có phải chân sau của Nhà nước không" chỉ có hai đáp án và cả hai đều cụt. Câu hỏi soi được là: <b>quyền lực chảy qua những ổ cắm nào, và ở mỗi ổ cắm bằng chứng mạnh tới đâu.</b>';
  w.appendChild(q);

  w.appendChild(el('h3','sec','Năm mức bằng chứng'));
  const p0=el('p'); p0.style.cssText='max-width:74ch;color:var(--fg2)';
  p0.innerHTML='Phần lớn tranh cãi nằm ở khoảng giữa — chỗ có dấu hiệu nhưng chưa đủ kết luận. Gộp khoảng giữa lại là chỗ suy đoán trà trộn vào chứng cứ. Và <b>"chưa thấy" khác "chưa tìm"</b>: chỉ được ghi mức 0 sau khi đã tìm đúng chỗ.';
  w.appendChild(p0);
  const tw=el('div','thang');
  THANG.forEach(m=>{ const r=el('div','th-r');
    r.innerHTML='<span class="th-n" style="color:'+m.acc+'">'+m.n+'</span>';
    r.appendChild(thanhBC(m.k));
    const d=el('span','th-d',m.d); r.appendChild(d);
    tw.appendChild(r); });
  w.appendChild(tw);

  w.appendChild(el('h3','sec','Bảy tiêu chí'));
  const g=el('div','tc-grid');
  TIEUCHI.forEach(t=>{ const c=el('div','tc');
    c.innerHTML='<div class="tc-h"><span class="tc-n">'+t.n+'</span><b>'+esc(t.t)+'</b><i>'+esc(t.en)+'</i></div>'+
      '<p class="tc-q">'+esc(t.hoi)+'</p>'+
      '<p class="tc-t"><span>TÌM GÌ</span>'+esc(t.tim)+'</p>';
    g.appendChild(c); });
  w.appendChild(g);

  w.appendChild(el('h3','sec','Vì sao phải chấm cả giả thuyết đối lập'));
  const p1=el('p'); p1.style.cssText='max-width:74ch;color:var(--fg2)';
  p1.innerHTML='Chấm một giả thuyết duy nhất thì mọi mảnh đều trông như bằng chứng ủng hộ nó. Cách chặn: viết ra <b>hai</b> giả thuyết cạnh tranh rồi chấm cả hai trên <b>cùng</b> bảy tiêu chí. Nếu cùng một bộ chứng cứ làm giả thuyết A rỗng và giả thuyết B đầy, đó mới là kết luận. Và phải chủ động đi tìm <b>phản chứng</b> — mảnh nào mà nếu giả thuyết đúng thì không thể tồn tại.';
  w.appendChild(p1);

  /* So hình dạng các bảng chấm. Tính ĐỘNG chứ không viết cứng:
     nếu hồ sơ sau ra hình khác thì khối này tự nói khác, và đó
     mới là điều đáng biết. Viết cứng "chúng giống nhau" là biến
     một phát hiện thành một khẩu hiệu. */
  if(SOI.length>1){
    const hinh = s => TIEUCHI.map(t=>(s.diem[t.id]||{}).m||'-').join('|');
    const g0 = hinh(SOI[0]);
    const deu = SOI.every(s=>hinh(s)===g0);
    w.appendChild(el('h3','sec','Hai hồ sơ đầu ra cùng một hình dạng'));
    const box=el('div','ss-w');
    SOI.forEach(s=>{
      const r=el('button','ss-r'); r.onclick=()=>go('soi/'+s.id);
      let o='';
      TIEUCHI.forEach(t=>{ const m=mucBC((s.diem[t.id]||{}).m);
        o+='<i style="background:'+m.acc+';opacity:'+(m.n?1:.28)+'" title="'+esc(t.t)+' — '+m.t+'"></i>'; });
      r.innerHTML='<span class="ss-t">'+esc(s.ten)+'</span><span class="ss-b">'+o+'</span>';
      box.appendChild(r);
    });
    w.appendChild(box);
    const q=el('blockquote');
    q.innerHTML = deu
      ? 'Vingroup đi từ <b>đất → vốn → công nghiệp</b>. THACO đi ngược lại: <b>cơ khí → ô tô → công nghiệp → rồi mới tới đất</b>. Xuất phát trái ngược, nhưng bảy tiêu chí ra <b>đúng cùng một hình</b>: ba cột xương sống quyền sở hữu trống, ba cột quan hệ Nhà nước đầy.<br><br>Nghĩa là thứ khung này đo được không phải đặc điểm của một doanh nghiệp, mà là <b>đặc điểm của mô hình</b>. Một hồ sơ thì đó là quan sát; hai hồ sơ khác gốc mà trùng hình thì bắt đầu là khuôn mẫu.'
      : 'Các hồ sơ hiện <b>không</b> ra cùng một hình dạng — chỗ khác nhau đó đáng đọc kỹ hơn chỗ giống nhau, vì nó cho biết tiêu chí nào thật sự phân biệt được đối tượng.';
    w.appendChild(q);
  }

  /* Lộ trình. Xếp theo khả năng trở thành công cụ chiến lược,
     KHÔNG theo quy mô tài sản — hai thứ đó khác nhau, và trộn
     lẫn là chỗ mọi bảng "top tập đoàn" trở nên vô dụng. */
  w.appendChild(el('h3','sec','Danh sách soi'));
  const p2=el('p'); p2.style.cssText='max-width:74ch;color:var(--fg2)';
  p2.innerHTML='Đây <b>không phải bảng xếp hạng giàu</b>. Xếp theo khả năng trở thành một công cụ doanh nghiệp tư nhân có vai trò chiến lược — một tập đoàn rất lớn mà không đứng ở ổ cắm nào của Nhà nước thì không thuộc mô hình này.';
  w.appendChild(p2);

  const dsW=el('div','ds-w');
  DANHSACH.forEach(m=>{
    const g=el('div','ds-m'); g.style.setProperty('--a',m.acc);
    g.innerHTML='<div class="ds-h"><span class="ds-n">MỨC '+m.muc+'</span><b>'+esc(m.t)+'</b></div>';
    const rows=el('div');
    m.ds.forEach(x=>{
      const done=!!x.soi;
      const r=el(done?'button':'div','ds-r'+(done?' co':''));
      r.innerHTML='<span class="ds-t">'+esc(x.ten)+'</span>'+
        '<span class="ds-o">'+esc(x.o)+'</span>'+
        (done?'<span class="ds-b co">đã soi →</span>':'<span class="ds-b">chưa soi</span>')+
        (x.ghi?'<span class="ds-g">'+esc(x.ghi)+'</span>':'');
      if(done) r.onclick=()=>go('soi/'+x.soi);
      rows.appendChild(r);
    });
    g.appendChild(rows); dsW.appendChild(g);
  });
  w.appendChild(dsW);
  return w;
}

/* Mục nào đang mở. Thiếu khoá = dùng mặc định `mo` của chính mục
   đó, nên hồ sơ tự quyết mục nào đáng bung sẵn — thường là phản
   chứng và phát hiện chính. */
function moMuc(sid,m){
  const v=state.muc['soi:'+sid+':'+m.id];
  return v===undefined ? !!m.mo : v;
}

/* Bộ vẽ khối. Thêm kiểu mới = thêm một nhánh ở đây, dữ liệu
   trong soi.js không phải biết gì về DOM. */
function veKhoi(k){
  if(!k||!k.k) return null;
  if(k.k==='p'){ const p=el('p','muc-p'); p.innerHTML=k.d; return p; }
  if(k.k==='a') return el('pre','ascii',k.d);
  if(k.k==='q'){ const q=el('blockquote'); if(k.do){ q.style.borderLeftColor='var(--dgr)'; q.style.background='#f0503f0d'; } q.innerHTML=k.d; return q; }
  if(k.k==='the'){ const g=el('div','the-w');
    (k.ds||[]).forEach(x=>{ const c=el('div','the'); if(x.acc) c.style.setProperty('--a',x.acc);
      c.innerHTML='<b>'+esc(x.t)+'</b>'+(x.vd?'<div class="the-vd">'+esc(x.vd)+'</div>':'')+'<p>'+x.d+'</p>';
      g.appendChild(c); });
    return g; }
  if(k.k==='moc'){ const tl=el('div','tl');
    (k.ds||[]).forEach(m=>{ const r=el('div','tl-r'+(m.hot?' hot':''));
      r.innerHTML='<div class="tl-y">'+esc(m.y)+'</div><div class="tl-b"><b>'+m.t+'</b><p>'+m.d+'</p></div>';
      tl.appendChild(r); });
    return tl; }
  if(k.k==='so'){ const g=el('div','so-w');
    (k.ds||[]).forEach(x=>{ const c=el('div','so'); if(x.acc) c.style.setProperty('--a',x.acc);
      c.innerHTML='<div class="so-t">'+esc(x.t)+'</div><div class="so-v">'+esc(x.v)+'</div>'+
        (x.d?'<div class="so-d">'+esc(x.d)+'</div>':'');
      g.appendChild(c); });
    return g; }
  if(k.k==='sd'){ const g=el('div');
    (k.ds||[]).forEach(x=>{ const c=el('div','sai-dung');
      c.innerHTML='<div class="sd-s"><span>NÓI SAI</span>'+esc(x.sai)+'</div>'+
        '<div class="sd-d"><span>NÓI ĐÚNG</span>'+x.dung+'</div>';
      g.appendChild(c); });
    return g; }
  if(k.k==='ds'){ const g=el('div','gap-w');
    (k.ds||[]).forEach((x,i)=>{ const c=el('div','gap');
      c.innerHTML='<span class="gap-n">'+(i+1)+'</span><span>'+x+'</span>'; g.appendChild(c); });
    return g; }
  if(k.k==='oc'){ const g=el('div','oc-w');
    (k.ds||[]).forEach(o=>g.appendChild(el('span','oc',o))); return g; }
  if(k.k==='thac'){ const g=el('div','thac-w');
    (k.ds||[]).forEach((x,i)=>{ const c=el('div','thac'+(i<k.ds.length-1?' noi':''));
      c.style.setProperty('--a',x.acc);
      c.innerHTML='<div class="thac-k">'+esc(x.n)+'</div><div class="thac-b">'+
        '<div class="thac-h"><b>'+esc(x.t)+'</b><span class="thac-v">'+esc(x.vai)+'</span></div>'+
        '<p>'+x.d+'</p></div>';
      g.appendChild(c); });
    return g; }
  return null;
}

function vSoi(id, mucId){
  const S=SOI.find(x=>x.id===id); if(!S) return go('soi'),el('div');
  /* Vào thẳng một mục từ thanh bên: mục đó phải mở sẵn, không thì
     người dùng bấm xong lại thấy một hàng đóng và phải bấm lần nữa. */
  const nhay = mucId && (S.muc||[]).some(m=>m.id===mucId) ? mucId : null;
  if(nhay) state.muc['soi:'+S.id+':'+nhay]=true;
  head(S.ten, nhay ? 'HỒ SƠ · '+((S.muc.find(m=>m.id===nhay)||{}).t||'').toUpperCase()
                   : 'HỒ SƠ · '+S.nguoi.toUpperCase());
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Soi quyền lực · hồ sơ</div>'+
   '<h2 class="big">'+esc(S.ten)+' — '+esc(S.nguoi)+'</h2>'+
   '<div class="soi-vai">'+esc(S.vai)+'</div>'+
   '<p class="lede">'+S.lede+'</p>';

  /* hai giả thuyết — đặt TRƯỚC bảng chấm, để người đọc biết
     mình đang chấm cái gì trước khi nhìn điểm */
  const gw=el('div','gt-w');
  S.gt.forEach(g=>{ const c=el('div','gt'); c.style.borderColor=g.acc+'55';
    c.innerHTML='<div class="gt-k" style="background:'+g.acc+'22;color:'+g.acc+'">GIẢ THUYẾT '+g.k+'</div>'+
      '<b>'+esc(g.t)+'</b><div class="gt-kl" style="color:'+g.acc+'">'+esc(g.kl)+'</div><p>'+esc(g.d)+'</p>';
    gw.appendChild(c); });
  w.appendChild(gw);

  w.appendChild(el('h3','sec','Chấm trên bảy tiêu chí'));
  const p0=el('p'); p0.style.cssText='max-width:74ch;color:var(--fg2);margin-bottom:14px';
  p0.innerHTML='Đọc theo cột màu trước, đọc chữ sau. Ba tiêu chí đầu là <b>xương sống của quyền sở hữu</b> — chúng trống. Bốn tiêu chí sau là <b>quan hệ với Nhà nước</b> — chúng đầy. Chính hình dạng đó là kết luận.';
  w.appendChild(p0);

  const sc=el('div','sc');
  TIEUCHI.forEach(t=>{
    const dm=S.diem[t.id]; if(!dm) return;
    const m=mucBC(dm.m);
    const r=el('div','sc-r'); r.style.setProperty('--a',m.acc);
    const h=el('div','sc-h');
    h.innerHTML='<span class="sc-n">'+t.n+'</span><b>'+esc(t.t)+'</b>';
    h.appendChild(thanhBC(dm.m));
    r.appendChild(h);
    const q=el('div','sc-q',t.hoi); r.appendChild(q);
    const d=el('div','sc-d'); d.innerHTML=dm.d; r.appendChild(d);
    sc.appendChild(r);
  });
  w.appendChild(sc);

  /* ── CÁC MỤC THU GỌN ĐƯỢC ──────────────────────────────
     Một hồ sơ đầy đủ dài hơn màn hình rất nhiều. Đổ hết ra một
     mạch thì bảng chấm — phần quan trọng nhất — bị đẩy lên trên
     rồi trôi mất, và người đọc không biết mình đang ở đâu trong
     lập luận. Chia mục thì mỗi mục trả lời đúng một câu hỏi.

     Trạng thái mở/đóng lưu theo TỪNG hồ sơ (khoá 'soi:<id>:<mục>')
     nên mở hồ sơ khác không kế thừa thói quen đọc của hồ sơ này. */
  if(S.muc && S.muc.length){
    const thanh=el('div','muc-bar');
    const btnAll=el('button','fchip');
    const demMo=()=>S.muc.filter(m=>moMuc(S.id,m)).length;
    const veAll=()=>{ btnAll.textContent = demMo()===S.muc.length ? 'Thu gọn tất cả' : 'Mở tất cả '+S.muc.length+' mục'; };
    veAll();
    btnAll.onclick=()=>{ const mo=demMo()!==S.muc.length;
      S.muc.forEach(m=>{ state.muc['soi:'+S.id+':'+m.id]=mo; }); save(); render(); };
    thanh.appendChild(btnAll);
    thanh.appendChild(el('span','muc-dem',S.muc.length+' mục · '+
      S.muc.reduce((a,m)=>a+(m.khoi?m.khoi.length:0),0)+' khối'));
    w.appendChild(thanh);

    S.muc.forEach(m=>{
      const mo=moMuc(S.id,m);
      const box=el('div','muc'+(mo?' mo':'')+(m.id===nhay?' nhay':''));
      if(m.id===nhay){
        /* Cuộn sau khi khối đã vào DOM và transition mở đã bắt đầu,
           không thì trình duyệt tính sai vị trí của một hộp cao 0. */
        requestAnimationFrame(()=>requestAnimationFrame(()=>{
          box.scrollIntoView({behavior:'smooth', block:'start'});
        }));
      }
      const h=el('button','muc-h');
      h.setAttribute('aria-expanded',mo?'true':'false');
      h.innerHTML='<span class="muc-tw"><svg viewBox="0 0 24 24" width="12" height="12" '+
        'fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '+
        'stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></span>'+
        '<span class="muc-ic">'+svg(m.ic||'book')+'</span>'+
        '<b>'+esc(m.t)+'</b>';
      h.onclick=()=>{ state.muc['soi:'+S.id+':'+m.id]=!mo; save(); render(); };
      box.appendChild(h);
      const body=el('div','muc-b');
      (m.khoi||[]).forEach(k=>{ const n=veKhoi(k); if(n) body.appendChild(n); });
      box.appendChild(body);
      w.appendChild(box);
    });
  }

  if(S.noi&&S.noi.length){
    const nv=el('div'); nv.style.cssText='margin-top:26px;padding-top:18px;border-top:1px solid var(--line)';
    nv.appendChild(el('div','eyebrow','Nối vào mạch truyền dẫn'));
    const row=el('div'); row.style.cssText='display:flex;gap:8px;flex-wrap:wrap;margin-top:8px';
    S.noi.forEach(cid=>{ const c=CHAIN.find(x=>x.id===cid); if(!c) return;
      const b=el('button','fchip'); b.textContent=c.t; b.onclick=()=>go('chain'); row.appendChild(b); });
    nv.appendChild(row);
    w.appendChild(nv);
  }

  const bk=el('div'); bk.style.cssText='margin-top:22px';
  const b=el('button','fchip'); b.textContent='← Khung 7 tiêu chí'; b.onclick=()=>go('soi');
  bk.appendChild(b); w.appendChild(bk);
  return w;
}

/* ---------- NGUỒN & NHẬT KÝ ---------- */
function vSrc(){
  const ct = chuThe(state.cht);
  head('Nguồn & nhật ký', ct.ten.toUpperCase()+' · MINH BẠCH');
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Cái gì từ đâu ra · '+esc(ct.ten)+'</div>'+
   '<h2 class="big">Nguồn &amp; nhật ký</h2>'+
   '<p class="lede">Một bảng quan trắc chỉ dùng được nếu biết rõ dòng nào là dữ liệu, dòng nào là phán đoán. Đây là chỗ tách bạch điều đó — <b>riêng cho '+esc(ct.ten)+'</b>, không trộn với chủ thể khác.</p>';

  const g=el('div','grid g3');
  [['Khung phân tích','Toàn bộ mạch truyền dẫn, '+LEVELS.length+' cấp độ, kịch bản A/B/C, thư viện '+LIB.length+' cụm — trích và phân loại từ hồ sơ bạn cung cấp. Cố định, không tự đổi.','b'],
   ['Bảng đồng hồ', ct.khoDo
      ? 'Đèn bạn tự đặt được, và số đo tự động ghi đè khi có. Màu bạn chọn là phán đoán của bạn.'
      : 'Do bạn tự đặt. '+ct.ten+' CHƯA có số đo tự động — không nguồn nào ghi vào đây, nên mọi màu ở đó đều là phán đoán của bạn.','p'],
   ['Dòng chảy', ct.tepScan
      ? 'Chỉ được lấp đầy bằng kết quả quét trực tiếp qua tìm kiếm web. Trống nếu chưa quét — không có dữ liệu giả lập.'
      : 'CHƯA có đường quét tự động cho '+ct.ten+'. Dòng chảy trống ở đây là ĐÚNG, không phải hỏng — và cố ý không mượn tín hiệu của chủ thể khác.','g']
  ].forEach(([t,d,c])=>{ const k=el('div','card');
    k.innerHTML='<div class="card-h"><b>'+esc(t.toUpperCase())+'</b><span class="chip '+c+'">'+(c==='b'?'cố định':c==='p'?'thủ công':'trực tiếp')+'</span></div><div class="card-b"><p class="muted" style="margin:0;font-size:12.5px">'+esc(d)+'</p></div>';
    g.appendChild(k); });
  w.appendChild(g);

  w.appendChild(el('h3','sec','Số liệu được nhắc trong hồ sơ nền — '+ct.ten));
  const ul=el('ul','tight');
  ul.innerHTML=SOLIEU.map(x=>'<li>'+esc(x)+'</li>').join('');
  w.appendChild(ul);
  const warn=el('blockquote'); warn.style.borderLeftColor='var(--warn)';
  warn.innerHTML='Những con số trên được ghi lại đúng như hồ sơ nguồn nêu. Chúng là <b>ảnh chụp tại thời điểm viết</b>, không tự cập nhật — hãy đối chiếu lại trước khi dùng để ra quyết định.';
  w.appendChild(warn);

  w.appendChild(el('h3','sec','Nhật ký kết nối'));
  if(!logCT().length){
    w.appendChild(el('div','empty','<b>Chưa có lần quét nào</b><p>Mỗi lần quét sẽ ghi lại ở đây: chiến trường nào, lúc nào, thành công hay thất bại.</p>'));
  }else{
    const c=el('div','card'); const b=el('div');
    logCT().slice(0,30).forEach(l=>{ const r=el('div','gauge');
      r.innerHTML='<span class="gauge-i '+(l.ok?'g':'r')+'">'+(l.ok?'✓':'✕')+'</span><span class="gauge-t"><b>'+esc(l.t)+'</b><span>'+esc(l.d)+'</span></span><span class="mono muted" style="font-size:10.5px">'+ago(l.at)+'</span>';
      b.appendChild(r); });
    c.appendChild(b); w.appendChild(c);
  }
  return w;
}

/* ============================================================
   RAIL
   ============================================================ */
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