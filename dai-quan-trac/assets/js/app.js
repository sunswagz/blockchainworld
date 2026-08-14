(function () {
"use strict";

var D = window.DQT_DATA;
var IC = D.IC, svg = D.svg, THEATERS = D.THEATERS, GAUGES = D.GAUGES;
var CHAIN = D.CHAIN, LEVELS = D.LEVELS, SCEN = D.SCEN, LIB = D.LIB;
var THANG = D.THANG, TIEUCHI = D.TIEUCHI, SOI = D.SOI;

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
var DO = (window.DQT_DO && window.DQT_DO.do) ? window.DQT_DO.do : {};
var DO_LUC = (window.DQT_DO && window.DQT_DO.generatedAt) || null;

/* Đèn thực tế của một đồng hồ, sau khi hoà người và máy. */
function den(id){
  const tay = state.gg[id];
  if(tay && tay !== 'n') return tay;
  const d = DO[id];
  return (d && d.muc) ? d.muc : 'n';
}
/* Đèn đó từ đâu ra — giao diện phải nói thật chỗ này. */
function nguonDen(id){
  const tay = state.gg[id];
  if(tay && tay !== 'n') return 'tay';
  return DO[id] ? 'tu' : 'chua';
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
const state = {
  route:'flow',
  th:  Object.fromEntries(THEATERS.map(t=>[t.id,'n'])),
  gg:  Object.fromEntries(GAUGES.map(g=>[g.id,'n'])),
  sig: [],           // tín hiệu từ quét trực tiếp
  log: [],           // nhật ký kết nối
  filter:'all',
  scanning:false
};
/* Mỗi mắt xích trong CHAIN PHẢI có một dòng ở đây, không thì lvOf()
   đọc undefined[0] và cả trang trắng. Thêm mắt xích mà quên dòng này
   là lỗi chết ngay — có kiểm tự động ở cuối file để không quên. */
const CHAIN_SRC = {hormuz:['th','hormuz'],gia_dau:['gg','nangluong'],tq:['th','tq'],dauvao:['gg','tq'],
  cpi:['max','nangluong','tq'],
  hangrao:['max','xuatkhau','xuatxu'],phisan:['gg','san'],bienloi:['max','san','xuatkhau'],
  sangloc:['gg','doanhnghiep'],vieclam:['gg','doanhnghiep'],
  tygia:['gg','tygia'],laisuat:['gg','laisuat'],tindung:['gg','nganhang'],
  bds:['gg','bds'],niemtin:['gg','niemtin'],hanhvi:['gg','niemtin']};
const RANK={n:0,g:1,y:2,r:3};

/* Tự soi lúc nạp: mắt xích thiếu nguồn, hoặc nguồn trỏ tới đồng hồ /
   chiến trường không tồn tại. Cả ba lỗi này đều làm trang trắng hoặc
   sáng sai mức mà không có thông báo nào. Rẻ, chạy một lần, và nói rõ
   sai ở đâu thay vì để "Cannot read properties of undefined". */
(function kiemMach(){
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
  if(loi.length) console.error('[Đài Quan Trắc] mạch truyền dẫn lệch:\n  · '+loi.join('\n  · '));
})();
/* Đọc qua den() chứ không đọc thẳng state.gg — nhờ vậy số đo tự
   động cũng thắp được mạch truyền dẫn, không chỉ đèn đặt tay. Đây
   là chỗ vòng tuần hoàn khép lại: đo → ngưỡng → đèn → mạch sáng. */
function lvOf(chainId){
  const s=CHAIN_SRC[chainId];
  if(s[0]==='th') return state.th[s[1]];
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
  try{ if(window.storage) await window.storage.set('daiquantrac:v1', JSON.stringify({th:state.th,gg:state.gg,sig:state.sig.slice(0,120),log:state.log.slice(0,60)})); }catch(e){}
}
async function load(){
  try{ if(!window.storage) return;
    const r = await window.storage.get('daiquantrac:v1');
    if(r&&r.value){ const d=JSON.parse(r.value); Object.assign(state.th,d.th||{}); Object.assign(state.gg,d.gg||{}); state.sig=d.sig||[]; state.log=d.log||[]; }
  }catch(e){}
}

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
const ROUTES = [
  {g:'Quan trắc', items:[
    {id:'flow',   t:'Dòng chảy',        ic:'flow',   sub:'REALTIME'},
    {id:'chain',  t:'Mạch truyền dẫn',  ic:'chain',  sub:CHAIN.length+' MẮT XÍCH'},
    {id:'gauges', t:'Bảng cảnh báo sớm',ic:'gauge',  sub:GAUGES.length+' ĐỒNG HỒ'}
  ]},
  {g:'Chiến trường', items: THEATERS.map(t=>({id:'th/'+t.id, t:t.name, ic:t.ic, sub:t.role.toUpperCase(), th:t.id}))},
  {g:'Mô hình', items:[
    {id:'levels', t:'4 cấp độ',      ic:'stairs', sub:'ÁP LỰC → KHỦNG HOẢNG'},
    {id:'scen',   t:'Kịch bản A/B/C',ic:'play',   sub:'PHÂN NHÁNH'},
    {id:'compass',t:'Kẹp bốn phía',  ic:'map',    sub:'VỊ TRÍ VIỆT NAM'}
  ]},
  {g:'Soi quyền lực', items: [{id:'soi', t:'Khung 7 tiêu chí', ic:'gauge', sub:'DÙNG LẠI ĐƯỢC'}]
    .concat(SOI.map(s=>({id:'soi/'+s.id, t:s.ten, ic:s.ic, sub:'HỒ SƠ'})))},
  {g:'Hồ sơ nền', items: LIB.map(l=>({id:'lib/'+l.id, t:l.t, ic:l.id==='nhanthuc'?'brain':'book', sub:'CỤM '+l.n}))
    .concat([{id:'src', t:'Nguồn & nhật ký', ic:'src', sub:'MINH BẠCH'}])}
];

function renderNav(){
  const w=$('#navscroll'); w.innerHTML='';
  ROUTES.forEach(sec=>{
    const g=el('div','grp');
    g.appendChild(el('div','navlab',esc(sec.g)));
    sec.items.forEach(it=>{
      const b=el('button','nv'+(state.route===it.id?' on':''));
      let right='';
      if(it.th) right='<span class="dot '+state.th[it.th]+'"></span>';
      else if(it.id==='flow'&&state.sig.length) right='<span class="nv-x">'+state.sig.length+'</span>';
      b.innerHTML='<span class="ic">'+svg(it.ic)+'</span><b>'+esc(it.t)+'</b>'+right;
      b.onclick=()=>go(it.id);
      g.appendChild(b);
    });
    w.appendChild(g);
  });
}

function go(r){
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
  if(r.startsWith('th/'))  return v.innerHTML='', v.appendChild(vTheater(r.slice(3)));
  if(r.startsWith('lib/')) return v.innerHTML='', v.appendChild(vLib(r.slice(4)));
  if(r.startsWith('soi/')) return v.innerHTML='', v.appendChild(vSoi(r.slice(4)));
  go('flow');
}

/* ---------- DÒNG CHẢY ---------- */
function vFlow(){
  head('Dòng chảy','REALTIME · '+state.sig.length+' TÍN HIỆU');
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Quan trắc liên tục</div>'+
   '<h2 class="big">Dòng chảy địa chính trị</h2>'+
   '<p class="lede">'+THEATERS.length+' chiến trường, một dòng. Mỗi tín hiệu được ghi kèm <b>đường truyền dẫn tới Việt Nam</b> — vì một sự kiện chỉ đáng theo dõi khi biết nó chạy vào đâu.</p>';

  /* Dải trạng thái — thứ phải đọc được trong hai giây, đặt trên
     cùng trang đầu. Cấp độ bên trái, 11 đèn bên phải: nhìn phát
     biết hệ thống đang ở đâu và đèn nào kéo nó lên. */
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

  // filter
  const fb=el('div','fbar');
  const mk=(id,label,n)=>{const b=el('button','fchip'+(state.filter===id?' on':''));
    b.innerHTML=esc(label)+(n!=null?' <span class="n">'+n+'</span>':''); b.onclick=()=>{state.filter=id;render();}; return b;};
  fb.appendChild(mk('all','Tất cả',state.sig.length));
  THEATERS.forEach(t=>fb.appendChild(mk(t.id,t.short,state.sig.filter(s=>s.th===t.id).length)));
  w.appendChild(fb);

  const list=state.sig.filter(s=>state.filter==='all'||s.th===state.filter);
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
    '<p style="margin:0 0 10px">Không phải cứ mắt xích số 1 đỏ là số 11 đỏ theo. Giữa chúng có <b>bộ đệm</b> — than nội địa của Trung Quốc, dự trữ, chính sách tiền tệ, tiết kiệm của hộ gia đình. Bộ đệm hấp thụ một phần và làm chậm phần còn lại.</p>'+
    '<p style="margin:0" class="muted">Điều đáng lo không phải một mắt xích đỏ, mà là <b>nhiều mắt xích liền kề cùng chuyển vàng trong một khoảng thời gian ngắn</b> — lúc đó chúng bắt đầu khuếch đại lẫn nhau thay vì hấp thụ cho nhau.</p></div>';
  w.appendChild(note);
  return w;
}

/* ---------- BẢNG ĐỒNG HỒ ---------- */
function vGauges(){
  const d=demDen(), N=GAUGES.length, tuDo=GAUGES.filter(g=>DO[g.id]).length;
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
    b.innerHTML='<span class="dot g"></span> Số đo gần nhất '+esc(gioDo(DO_LUC))+
      ' · nguồn Yahoo Finance, open.er-api, GDELT · <b>0 đồng chi phí</b>';
    w.appendChild(b);
  }

  const card=el('div','card');
  card.appendChild(el('div','card-h','<b>THỨ TỰ TỪ THƯỢNG NGUỒN XUỐNG</b><span class="chip">'+d.dat+'/'+N+'</span>'));
  const body=el('div');
  GAUGES.forEach((g,i)=>{
    const lv=den(g.id), ng=nguonDen(g.id), m=DO[g.id];
    const row=el('button','gauge g-'+ng); row.style.width='100%'; row.style.textAlign='left';

    let so='';
    if(m){
      const dd = m.doi7==null ? '' : '<i class="'+(m.doi7>0?'up':m.doi7<0?'dn':'')+'">'+
        (m.doi7>0?'▲ +':m.doi7<0?'▼ ':'')+m.doi7+'% / 7 phiên</i>';
      so='<span class="gauge-s">'+spark(m.lich,MAU[lv])+
         '<b>'+esc(String(m.so))+'</b><span class="dv">'+esc(m.dv||'')+'</span>'+dd+'</span>';
    }
    const nhan = ng==='tay' ? '<span class="pv tay">bạn đặt</span>'
               : ng==='tu'  ? '<span class="pv tu">tự đo '+esc(gioDo(m.luc))+'</span>'
                            : '<span class="pv chua">chưa có nguồn</span>';

    row.innerHTML='<span class="gauge-i '+lv+'">'+(i+1)+'</span>'+
      '<span class="gauge-t"><b>'+esc(g.t)+' '+nhan+'</b><span>'+esc(g.d)+'</span></span>'+
      so+'<span class="meter"><i class="'+lv+'"></i></span>';
    row.onclick=()=>{ const cu=state.gg[g.id]; state.gg[g.id]=LVLS[(LVLS.indexOf(cu)+1)%4]; save(); render(); renderNav(); };
    body.appendChild(row);
  });
  card.appendChild(body); w.appendChild(card);

  /* Ngưỡng phải mở ra xem được. Một cái đèn đỏ mà không nói được
     "đỏ theo mốc nào" thì chỉ là một cái đèn đỏ. */
  const ngw=GAUGES.filter(g=>DO[g.id]&&DO[g.id].nguong);
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
  const lv=state.th[id];
  w.innerHTML='<div class="eyebrow">Chiến trường · '+esc(t.short)+'</div>'+
   '<div style="display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;margin-bottom:10px">'+
     '<div style="font-size:34px;line-height:1">'+t.flag+'</div>'+
     '<div style="flex:1;min-width:220px"><h2 class="big" style="margin-bottom:4px">'+esc(t.name)+'</h2>'+
     '<div class="chips"><span class="chip '+lv+'">'+LVNAME[lv]+'</span><span class="chip b">'+esc(t.role)+'</span><span class="chip p">'+esc(t.scen)+'</span></div></div></div>'+
   '<p class="lede">'+t.lede+'</p>';

  const bar=el('div'); bar.style.cssText='display:flex;gap:8px;flex-wrap:wrap;margin:0 0 22px';
  const sb=el('button','tbtn pri'); sb.innerHTML='Lấy bản quét mới nhất'; sb.onclick=scanAll;
  const cyc=el('button','tbtn'); cyc.innerHTML='Đặt mức: <b style="margin-left:4px">'+LVNAME[lv]+'</b>';
  cyc.onclick=()=>{ state.th[id]=LVLS[(LVLS.indexOf(state.th[id])+1)%4]; save(); render(); renderNav(); };
  bar.appendChild(sb); bar.appendChild(cyc); w.appendChild(bar);

  // tín hiệu của chiến trường này
  const mine=state.sig.filter(s=>s.th===id);
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
  t.clocks.forEach((c,i)=>{ const r=el('div','gauge'); r.innerHTML='<span class="gauge-i n">'+(i+1)+'</span><span class="gauge-t"><b>'+esc(c)+'</b></span>'; cb.appendChild(r); });
  cl.appendChild(cb); w.appendChild(cl);

  w.appendChild(el('h3','sec','Đánh vào Việt Nam theo đường nào'));
  const hl=el('ul','tight'); hl.innerHTML=t.hits.map(h=>'<li>'+esc(h)+'</li>').join(''); w.appendChild(hl);
  return w;
}

/* ---------- 4 CẤP ĐỘ ---------- */
function vLevels(){
  head('4 cấp độ','ÁP LỰC → KHỦNG HOẢNG HỆ THỐNG');
  const cur = capDo();
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Chương XVII</div><h2 class="big">Từ "áp lực" đến "khủng hoảng" có bốn cấp</h2>'+
   '<p class="lede">Phần lớn tranh cãi về kinh tế là do hai người đang đứng ở hai cấp khác nhau mà dùng chung một từ. Cấp 1 và cấp 4 không phải cùng một câu chuyện ở mức độ khác nhau — chúng khác nhau về <b>cơ chế</b>.</p>';
  const lad=el('div','ladder');
  LEVELS.forEach(L=>{ const d=el('div','lv l'+L.n+(cur===L.n?' on':''));
    d.innerHTML='<div class="lv-n">'+L.n+'</div><div class="lv-b"><b>'+esc(L.t)+(cur===L.n?' — ĐANG ĐỌC RA':'')+'</b><p>'+esc(L.d)+'</p><p style="margin-top:6px;color:var(--fg2)"><b>'+esc(L.r)+'</b></p></div>';
    lad.appendChild(d); });
  w.appendChild(lad);
  const q=el('blockquote'); q.style.marginTop='20px';
  q.innerHTML= cur? 'Bảng đồng hồ hiện đang đọc ra <b>cấp '+cur+'</b>. Đây là kết quả của các mức bạn tự đặt, không phải một chẩn đoán độc lập.' 
                  : 'Chưa đặt đồng hồ nào nên chưa cấp nào được tô sáng. <a href="#gauges" onclick="go(\'gauges\')">Đặt bảng đồng hồ</a> trước.';
  w.appendChild(q);
  const q2=el('blockquote'); q2.style.borderLeftColor='var(--purple)'; q2.style.background='#a371f70d';
  q2.innerHTML='Ranh giới thật sự nằm giữa cấp 2 và cấp 3: cấp 3 là lúc <b>vòng lặp bắt đầu tự chạy</b> mà không cần thêm cú sốc mới nào từ bên ngoài.';
  w.appendChild(q2);
  return w;
}

/* ---------- KỊCH BẢN ---------- */
function vScen(){
  head('Kịch bản A/B/C','PHÂN NHÁNH THEO NGUỒN SỐC');
  const w=el('div','wrap wide');
  w.innerHTML='<div class="eyebrow">Chương 11</div><h2 class="big">Ba nhánh, một điểm hạ lưu</h2>'+
   '<p class="lede">Nga và Hormuz đánh vào Trung Quốc theo <b>hai kiểu khác nhau</b> — nên không thể gộp chung thành "sốc dầu". Tách ra mới thấy vì sao kịch bản C không phải là A cộng B, mà nặng hơn cả tổng của hai.</p>';
  const g=el('div','grid g3');
  SCEN.forEach(s=>{ const c=el('div','card'); c.style.borderColor=s.acc+'44';
    c.innerHTML='<div class="card-h" style="background:'+s.acc+'12"><b style="color:'+s.acc+'">KỊCH BẢN '+s.k+'</b></div>'+
      '<div class="card-b"><b style="display:block;font-size:14.5px;margin-bottom:3px">'+esc(s.t)+'</b>'+
      '<div class="chip" style="margin-bottom:11px">'+esc(s.w)+'</div>'+
      '<pre class="ascii" style="font-size:10.5px;margin-bottom:12px">'+esc(s.asc)+'</pre>'+
      '<ul class="tight" style="margin:0;font-size:12.5px">'+s.pts.map(p=>'<li>'+esc(p)+'</li>').join('')+'</ul></div>';
    g.appendChild(c); });
  w.appendChild(g);
  const q=el('blockquote'); q.style.marginTop='22px';
  q.innerHTML='Kịch bản C là trường hợp một cú sốc năng lượng trở thành <b>cú sốc hệ thống khu vực</b> — vì Trung Quốc mất đồng thời cả chân lục địa lẫn chân biển, và phần áp lực không hấp thụ được sẽ truyền thẳng xuống toàn chuỗi Á châu.';
  w.appendChild(q);
  return w;
}

/* ---------- KẸP BỐN PHÍA ---------- */
function vCompass(){
  head('Kẹp bốn phía','VỊ TRÍ CỦA VIỆT NAM');
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Chương XVI</div><h2 class="big">Việt Nam nằm đúng giao điểm</h2>'+
   '<p class="lede">Cách nói cẩn thận: không phải "tất cả đang cùng đánh Việt Nam", mà là <b>Việt Nam nằm đúng giao điểm của nhiều hệ thống nên một số cú sốc khác nguồn có khả năng cùng hội tụ tại đây</b>.</p>';
  const c=el('div','compass');
  const cell=(cls,side,t,p,th)=>{const d=el('div','cp '+cls);
    d.innerHTML='<div class="side">'+side+'</div><b>'+t+'</b><p>'+p+'</p>';
    if(th){d.style.cursor='pointer';d.onclick=()=>go('th/'+th);} return d;};
  c.appendChild(cell('n','PHÍA TRÊN','Hormuz / Nga','Năng lượng ↑ — cổ chai biển và chân lục địa cùng nằm ở thượng nguồn.','hormuz'));
  c.appendChild(cell('w','PHÍA TRÁI','Trung Quốc','Đầu vào ↑ — máy móc, linh kiện, hóa chất, hàng trung gian.','tq'));
  const core=el('div','cp core');
  core.innerHTML='<div class="flag">🇻🇳</div><b>VIỆT NAM</b><p style="color:var(--fg2)">Giao điểm của bốn hướng</p>';
  core.style.cursor='pointer'; core.onclick=()=>go('th/vn');
  c.appendChild(core);
  c.appendChild(cell('e','PHÍA PHẢI','Mỹ / EU','Đầu ra ? — thuế, nhu cầu tiêu dùng, điều kiện thương mại.','my'));
  c.appendChild(cell('s','PHÍA DƯỚI','Hệ thống nội địa','Ngân hàng · bất động sản · tín dụng · niềm tin — bộ khuếch đại nằm bên trong.','vn'));
  w.appendChild(c);
  const q=el('blockquote'); q.style.marginTop='20px';
  q.innerHTML='Ba hướng trên đánh vào <b>vật chất</b>. Hướng thứ tư — hệ thống nội địa — không tạo ra cú sốc, nhưng quyết định cú sốc bị hấp thụ hay bị khuếch đại.';
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

  const ho=el('div'); ho.style.cssText='display:flex;gap:8px;flex-wrap:wrap;margin-top:26px;padding-top:20px;border-top:1px solid var(--line)';
  ho.appendChild(el('div','eyebrow','Đã soi'));
  w.appendChild(ho);
  const hs=el('div'); hs.style.cssText='display:flex;gap:8px;flex-wrap:wrap;margin-top:8px';
  SOI.forEach(s=>{ const b=el('button','fchip'); b.textContent=s.ten+' · '+s.nguoi; b.onclick=()=>go('soi/'+s.id); hs.appendChild(b); });
  const cho=el('span','tc-soon','Các tên khác gắn với bộ máy quản lý — chưa soi');
  hs.appendChild(cho);
  w.appendChild(hs);
  return w;
}

function vSoi(id){
  const S=SOI.find(x=>x.id===id); if(!S) return go('soi'),el('div');
  head(S.ten,'HỒ SƠ · '+S.nguoi.toUpperCase());
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

  if(S.phanchung){
    w.appendChild(el('h3','sec',S.phanchung.t));
    const p=el('p'); p.style.cssText='max-width:74ch;color:var(--fg2)';
    p.innerHTML='Phần dễ bị bỏ qua nhất, và là phần làm kết luận đáng tin: nếu giả thuyết A đúng thì <b>không thể có</b> những chuyện dưới đây.';
    w.appendChild(p);
    const pw=el('div','pc-w');
    S.phanchung.ds.forEach(x=>{ const c=el('div','pc');
      c.innerHTML='<b>'+esc(x.t)+'</b><p>'+x.d+'</p>'; pw.appendChild(c); });
    w.appendChild(pw);
  }

  if(S.tang){
    w.appendChild(el('h3','sec',S.tang.t));
    const tw=el('div','tang-w');
    S.tang.ds.forEach(x=>{ const c=el('div','tang'); c.style.setProperty('--a',x.acc);
      c.innerHTML='<div class="tang-n">TẦNG '+x.n+'</div><b>'+esc(x.t)+'</b>'+
        '<div class="tang-vd">'+esc(x.vd)+'</div><p>'+esc(x.d)+'</p>';
      tw.appendChild(c); });
    w.appendChild(tw);
    if(S.tang.a) w.appendChild(el('pre','ascii',S.tang.a));
  }

  if(S.socket){
    w.appendChild(el('h3','sec',S.socket.t));
    const p=el('p'); p.style.cssText='max-width:74ch;color:var(--fg2)'; p.innerHTML=S.socket.d;
    w.appendChild(p);
    const ow=el('div','oc-w');
    S.socket.oc.forEach(o=>{ ow.appendChild(el('span','oc',o)); });
    w.appendChild(ow);
    if(S.socket.a) w.appendChild(el('pre','ascii',S.socket.a));
  }

  if(S.dongtien){
    w.appendChild(el('h3','sec',S.dongtien.t));
    const p=el('p'); p.style.cssText='max-width:74ch;color:var(--fg2)'; p.innerHTML=S.dongtien.d;
    w.appendChild(p);
    const tl=el('div','tl');
    S.dongtien.moc.forEach(m=>{ const r=el('div','tl-r'+(m.hot?' hot':''));
      r.innerHTML='<div class="tl-y">'+esc(m.y)+'</div><div class="tl-b"><b>'+esc(m.t)+'</b><p>'+m.d+'</p></div>';
      tl.appendChild(r); });
    w.appendChild(tl);
    const q=el('blockquote'); q.innerHTML=S.dongtien.kl; w.appendChild(q);
  }

  if(S.doc){
    w.appendChild(el('h3','sec','Đọc cho đúng'));
    S.doc.forEach(x=>{ const c=el('div','sai-dung');
      c.innerHTML='<div class="sd-s"><span>NÓI SAI</span>'+esc(x.sai)+'</div>'+
        '<div class="sd-d"><span>NÓI ĐÚNG</span>'+x.dung+'</div>';
      w.appendChild(c); });
  }

  if(S.ruiro){
    w.appendChild(el('h3','sec',S.ruiro.t));
    const p=el('p'); p.style.cssText='max-width:74ch;color:var(--fg2)'; p.innerHTML=S.ruiro.d;
    w.appendChild(p);
    if(S.ruiro.a) w.appendChild(el('pre','ascii',S.ruiro.a));
    if(S.ruiro.d2){ const p2=el('p'); p2.style.cssText='max-width:74ch;color:var(--fg2)'; p2.innerHTML=S.ruiro.d2; w.appendChild(p2); }
  }

  if(S.gap){
    w.appendChild(el('h3','sec',S.gap.t));
    const p=el('p'); p.style.cssText='max-width:74ch;color:var(--fg2)'; p.innerHTML=S.gap.d;
    w.appendChild(p);
    const gl=el('div','gap-w');
    S.gap.ds.forEach((x,i)=>{ const c=el('div','gap');
      c.innerHTML='<span class="gap-n">'+(i+1)+'</span>'+esc(x); gl.appendChild(c); });
    w.appendChild(gl);
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
  head('Nguồn & nhật ký','MINH BẠCH');
  const w=el('div','wrap');
  w.innerHTML='<div class="eyebrow">Cái gì từ đâu ra</div><h2 class="big">Nguồn & nhật ký</h2>'+
   '<p class="lede">Một bảng quan trắc chỉ dùng được nếu biết rõ dòng nào là dữ liệu, dòng nào là phán đoán. Đây là chỗ tách bạch điều đó.</p>';

  const g=el('div','grid g3');
  [['Khung phân tích','Toàn bộ mạch truyền dẫn, 4 cấp độ, kịch bản A/B/C, thư viện '+LIB.length+' cụm — trích và phân loại từ hồ sơ bạn cung cấp. Cố định, không tự đổi.','b'],
   ['Bảng đồng hồ','Do bạn tự đặt. Không có nguồn tự động nào ghi vào đây. Màu bạn chọn là phán đoán của bạn.','p'],
   ['Dòng chảy','Chỉ được lấp đầy bằng kết quả quét trực tiếp qua tìm kiếm web. Trống nếu chưa quét — không có dữ liệu giả lập.','g']
  ].forEach(([t,d,c])=>{ const k=el('div','card');
    k.innerHTML='<div class="card-h"><b>'+esc(t.toUpperCase())+'</b><span class="chip '+c+'">'+(c==='b'?'cố định':c==='p'?'thủ công':'trực tiếp')+'</span></div><div class="card-b"><p class="muted" style="margin:0;font-size:12.5px">'+esc(d)+'</p></div>';
    g.appendChild(k); });
  w.appendChild(g);

  w.appendChild(el('h3','sec','Số liệu được nhắc trong hồ sơ nền'));
  const ul=el('ul','tight');
  ul.innerHTML=[
   'Nghi Sơn cung cấp khoảng 40% nhu cầu sản phẩm xăng dầu của Việt Nam — theo Bộ Công Thương.',
   'Than chiếm khoảng 62% tiêu thụ năng lượng sơ cấp và ~60% sản lượng điện của Trung Quốc — theo EIA.',
   'Trung Quốc nhập khẩu dầu thô năm 2024 khoảng 11,1 triệu thùng/ngày — theo EIA.',
   'Bất động sản được FATF xếp vào nhóm có rủi ro rửa tiền đáng kể.',
   'Tín dụng/GDP và tỷ trọng tín dụng bất động sản của Việt Nam ở mức cao — theo World Bank.'
  ].map(s=>'<li>'+esc(s)+'</li>').join('');
  w.appendChild(ul);
  const warn=el('blockquote'); warn.style.borderLeftColor='var(--warn)';
  warn.innerHTML='Những con số trên được ghi lại đúng như hồ sơ nguồn nêu. Chúng là <b>ảnh chụp tại thời điểm viết</b>, không tự cập nhật — hãy đối chiếu lại trước khi dùng để ra quyết định.';
  w.appendChild(warn);

  w.appendChild(el('h3','sec','Nhật ký kết nối'));
  if(!state.log.length){
    w.appendChild(el('div','empty','<b>Chưa có lần quét nào</b><p>Mỗi lần quét sẽ ghi lại ở đây: chiến trường nào, lúc nào, thành công hay thất bại.</p>'));
  }else{
    const c=el('div','card'); const b=el('div');
    state.log.slice(0,30).forEach(l=>{ const r=el('div','gauge');
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
    '<div class="rl"><div class="rl-h">Trạng thái</div><div class="chips"><span class="chip '+lv+'">'+LVNAME[lv]+'</span><span class="chip">'+esc(n.tag)+'</span></div></div>';
  h+='<div class="rl"><div class="rl-h">Nguồn màu</div><p class="muted" style="font-size:12.5px">Lấy từ '+srcLabel(n.id)+'. Đổi ở đó thì mắt xích này đổi theo.</p></div>';
  const idx=CHAIN.findIndex(c=>c.id===n.id);
  if(idx>0) h+='<div class="rl"><div class="rl-h">Nhận từ</div><p>'+esc(CHAIN[idx-1].t)+'</p></div>';
  if(idx<CHAIN.length-1) h+='<div class="rl"><div class="rl-h">Truyền sang</div><p>'+esc(CHAIN[idx+1].t)+'</p></div>';
  if(t) h+='<button class="tbtn" onclick="go(\'th/'+t.id+'\')">Mở hồ sơ '+esc(t.short)+'</button>';
  else h+='<button class="tbtn" onclick="go(\'gauges\')">Mở bảng đồng hồ</button>';
  openRail(n.t,'MẮT XÍCH '+(idx+1)+'/11',h);
}

function railSignal(s){
  const t=TH(s.th)||{};
  let h='<div class="rl"><div class="rl-h">Tín hiệu</div><p style="color:var(--fg);font-size:13.5px">'+esc(s.tieu_de)+'</p></div>';
  if(s.tac_dong) h+='<div class="rl"><div class="rl-h">Đường truyền dẫn tới Việt Nam</div><p>'+esc(s.tac_dong)+'</p></div>';
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
function loadScan(){
  const S = window.DQT_SCAN;
  if(!S || !Array.isArray(S.signals)) return;

  const seen = new Set(state.sig.map(x => x.tieu_de));
  S.signals.forEach(s => {
    if(!s.tieu_de || seen.has(s.tieu_de)) return;
    seen.add(s.tieu_de);
    state.sig.push(s);
  });
  state.sig.sort((a,b) => String(b.at||'').localeCompare(String(a.at||'')));
  state.sig = state.sig.slice(0,160);

  Object.keys(S.levels||{}).forEach(id => {
    if(LVLS.includes(S.levels[id])) state.th[id] = S.levels[id];
  });

  (S.log||[]).forEach(entry => {
    if(!state.log.some(x => x.at === entry.at && x.t === entry.t)) state.log.push(entry);
  });
  state.log.sort((a,b) => String(b.at||'').localeCompare(String(a.at||'')));
  state.log = state.log.slice(0,80);
}

/* Nút "Quét trực tiếp" giờ chỉ lấy lại bản mới nhất từ máy chủ —
   không gọi mô hình từ trình duyệt. */
async function scanAll(){
  if(state.scanning) return;
  state.scanning = true;
  $('#scanAll').disabled = true;
  toast('Đang lấy bản quét mới nhất…', true);
  try{
    const res = await fetch('assets/js/scan.js?t=' + Date.now(), {cache:'no-store'});
    if(!res.ok) throw new Error('HTTP ' + res.status);
    const txt = await res.text();
    // scan.js là script thường gán window.DQT_SCAN — chạy lại trong phạm vi riêng
    new Function(txt)();
    const before = state.sig.length;
    loadScan();
    const added = state.sig.length - before;
    toast(added ? ('✓ thêm ' + added + ' tín hiệu mới') : 'Đã là bản mới nhất');
  }catch(err){
    state.log.unshift({ok:false, t:'nạp bản quét',
      d:'Không đọc được scan.js — ' + (err.message||err), at:new Date().toISOString()});
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