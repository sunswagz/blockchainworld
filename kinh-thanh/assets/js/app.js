(function () {
"use strict";

/* Dữ liệu được nạp trước từ assets/js/data/*.js */
var D = window.KT_DATA;
var CHAINS      = D.CHAINS;
var SNAP_DATE   = D.SNAP_DATE;
var STRENGTH    = D.STRENGTH;
var DIMS        = D.DIMS;
var AGG         = D.AGG;
var NAMEMAP     = D.NAMEMAP;
var ENTITIES    = D.ENTITIES;
var C_          = D.C_;
var O_          = D.O_;
var LINKWORD    = D.LINKWORD;
var CITY_OK     = D.CITY_OK;
var LOOPS       = D.LOOPS;
var RETURN_NOTE = D.RETURN_NOTE;
var CITIES      = D.CITIES;

var KIND={l2:["var(--l2)","var(--l2-t)"],l3:["var(--l3)","var(--l3-t)"],app:["var(--ap)","var(--ap-t)"],
  infra:["var(--in)","var(--in-t)"],gate:["var(--br)","var(--br-t)"],band:["var(--ec)","var(--ec-t)"]};
var LEGEND=[["Tầng mở rộng (thành phố, bang, subnet)","var(--l2-t)","city"],
  ["Đặc khu / app-chain","var(--l3-t)","gate"],
  ["Ứng dụng","var(--ap-t)","apps"],
  ["Hạ tầng (đất–điện–nước–đường)","var(--in-t)","pipes"],
  ["Cửa khẩu & cầu nối","var(--br-t)","bridge"],
  ["Ví · kinh tế · quản trị","var(--ec-t)","wallet"],
  ["Quốc gia L1 (nền móng)","var(--acc-t)","castle"]];

/* ══ bộ icon kinh thành ═══════════════════════════════ */
var ICONS={
 earth:'<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2"/><path d="M12 3.4c2.4 2.4 3.6 5.3 3.6 8.6s-1.2 6.2-3.6 8.6c-2.4-2.4-3.6-5.3-3.6-8.6S9.6 5.8 12 3.4Z"/>',
 castle:'<path d="M3 21h18"/><path d="M4 21V8l2.2 1.6L8.4 8v2h7.2V8l2.2 1.6L20 8v13"/><path d="M10 21v-4.5a2 2 0 0 1 4 0V21"/><path d="M4 13h16"/>',
 towers:'<path d="M2.5 21h19"/><path d="M5 21V7.5h5.5V21"/><path d="M10.5 21V11H19v10"/><path d="M7 11h1.2M7 15h1.2M13.5 14.5h1.2M13.5 18h1.2"/>',
 tower:'<path d="M3 21h18"/><path d="M7 21V6l5-3 5 3v15"/><path d="M7 10h10M7 15h10"/>',
 mountain:'<path d="M2 20h20"/><path d="M2 20 9 8l3.2 5.2L14.6 9 22 20"/><path d="M9 8l1.6 2.7"/>',
 hub:'<circle cx="12" cy="12" r="2.6"/><circle cx="12" cy="3.6" r="1.7"/><circle cx="12" cy="20.4" r="1.7"/><circle cx="4.6" cy="7.8" r="1.7"/><circle cx="19.4" cy="7.8" r="1.7"/><circle cx="4.6" cy="16.2" r="1.7"/><circle cx="19.4" cy="16.2" r="1.7"/>',
 network:'<circle cx="12" cy="12" r="2.2"/><path d="M10.4 10.4 6.3 7M13.6 10.4 17.7 7M10.4 13.6 6.3 17M13.6 13.6l4.1 3.4"/><circle cx="5" cy="6" r="1.8"/><circle cx="19" cy="6" r="1.8"/><circle cx="5" cy="18" r="1.8"/><circle cx="19" cy="18" r="1.8"/>',
 drop:'<path d="M12 3.2c1 1.2 6 6.6 6 10.4a6 6 0 0 1-12 0c0-3.8 5-9.2 6-10.4Z"/><path d="M9.2 14.4a2.8 2.8 0 0 0 2.8 2.8"/>',
 passport:'<rect x="4.5" y="2.5" width="15" height="19" rx="2.6"/><circle cx="12" cy="10" r="3.1"/><path d="M9 17.5h6"/><path d="M12 6.9v6.2M8.9 10h6.2"/>',
 phone:'<rect x="5" y="2.5" width="14" height="19" rx="3"/><path d="M8.5 8h7M8.5 11.5h4.5"/><circle cx="12" cy="18" r="1"/>',
 city:'<path d="M2.5 21h19"/><path d="M5 21V9.5l4.5-2.5V21"/><path d="M9.5 21V12l5 2.8V21"/><path d="M14.5 21v-5l4.5 2.4V21"/><path d="M7 12h.6M7 16h.6M11.5 17h.6"/>',
 gate:'<path d="M2.5 21h19"/><path d="M4.5 21V8.5h15V21"/><path d="M9 21v-5.5a3 3 0 0 1 6 0V21"/><path d="M3 8.5h18L18.5 5h-13L3 8.5Z"/>',
 layers:'<path d="M12 2.8 3 7.2l9 4.4 9-4.4-9-4.4Z"/><path d="M3 12.2l9 4.4 9-4.4M3 16.8l9 4.4 9-4.4"/>',
 apps:'<rect x="3" y="3" width="7.4" height="7.4" rx="1.8"/><rect x="13.6" y="3" width="7.4" height="7.4" rx="1.8"/><rect x="3" y="13.6" width="7.4" height="7.4" rx="1.8"/><rect x="13.6" y="13.6" width="7.4" height="7.4" rx="1.8"/>',
 bank:'<path d="M2.5 21h19"/><path d="M12 3 3 7.8h18L12 3Z"/><path d="M5 21V11M9.5 21V11M14.5 21V11M19 21V11"/>',
 chat:'<path d="M20.5 11.8a7.8 7.8 0 0 1-7.8 7.8H4.2l2.4-2.9a7.8 7.8 0 1 1 13.9-4.9Z"/><path d="M9 11h6"/>',
 card:'<rect x="2.5" y="5" width="19" height="14" rx="2.6"/><path d="M2.5 9.8h19"/><path d="M6 15h4"/>',
 deed:'<path d="M6 2.8h8l4.5 4.5v13.9H6z"/><path d="M14 2.8v4.5h4.5"/><path d="M9 12.5h6M9 16h4"/>',
 game:'<rect x="2" y="7" width="20" height="10.6" rx="4.4"/><path d="M7 10.6v3.4M5.3 12.3h3.4"/><path d="M15.6 11.4h.02M18 13.6h.02"/>',
 robot:'<rect x="4" y="8" width="16" height="12" rx="3.4"/><path d="M12 4.6V8"/><circle cx="12" cy="3.4" r="1.3"/><path d="M9.2 13.4h.02M14.8 13.4h.02M9.5 17h5"/>',
 shield:'<path d="M12 2.8 4.5 5.6v6.1c0 4.7 3.2 7.7 7.5 8.9 4.3-1.2 7.5-4.2 7.5-8.9V5.6L12 2.8Z"/><path d="M9.2 12l2 2 3.6-3.8"/>',
 antenna:'<path d="M12 21v-6.6"/><circle cx="12" cy="12" r="2.2"/><path d="M8.1 8.1a5.5 5.5 0 0 0 0 7.8M15.9 8.1a5.5 5.5 0 0 1 0 7.8"/><path d="M5.2 5.2a9.6 9.6 0 0 0 0 13.6M18.8 5.2a9.6 9.6 0 0 1 0 13.6"/>',
 database:'<ellipse cx="12" cy="6" rx="7.6" ry="3.1"/><path d="M4.4 6v12c0 1.7 3.4 3.1 7.6 3.1s7.6-1.4 7.6-3.1V6"/><path d="M4.4 12c0 1.7 3.4 3.1 7.6 3.1s7.6-1.4 7.6-3.1"/>',
 satellite:'<circle cx="12" cy="12" r="3"/><path d="M12 5.4V2.4M12 21.6v-3M5.4 12h-3M21.6 12h-3"/><path d="M7.3 7.3 5.2 5.2M16.7 7.3l2.1-2.1M7.3 16.7l-2.1 2.1M16.7 16.7l2.1 2.1"/>',
 box:'<path d="M12 2.8 3.4 7.4v9.2L12 21.2l8.6-4.6V7.4L12 2.8Z"/><path d="M3.4 7.4 12 12l8.6-4.6M12 12v9.2"/>',
 id:'<rect x="2.6" y="4.4" width="18.8" height="15.2" rx="2.6"/><circle cx="8.8" cy="10.6" r="2.2"/><path d="M5.2 16.4c.8-1.6 2-2.4 3.6-2.4s2.8.8 3.6 2.4"/><path d="M15.4 9.6h3.8M15.4 13.4h3.8"/>',
 bridge:'<path d="M2.5 18.5h19"/><path d="M3 11.5a9 9 0 0 1 18 0"/><path d="M3 11.5v7M21 11.5v7M8.6 14.6v3.9M15.4 14.6v3.9M12 13.3v5.2"/>',
 chart:'<path d="M3 21h18"/><rect x="4.6" y="12.4" width="3.6" height="6.4" rx="1.1"/><rect x="10.2" y="7" width="3.6" height="11.8" rx="1.1"/><rect x="15.8" y="10" width="3.6" height="8.8" rx="1.1"/>',
 gear:'<circle cx="12" cy="12" r="3.1"/><path d="M12 2.6v2.6M12 18.8v2.6M21.4 12h-2.6M5.2 12H2.6M18.6 5.4l-1.8 1.8M7.2 16.8l-1.8 1.8M18.6 18.6l-1.8-1.8M7.2 7.2 5.4 5.4"/>',
 wallet:'<path d="M3 8A2.5 2.5 0 0 1 5.5 5.5H17"/><rect x="3" y="8" width="18" height="11.5" rx="2.6"/><path d="M16.8 13.8h.02"/>',
 coin:'<circle cx="12" cy="12" r="8.4"/><path d="M12 7.2v9.6"/><path d="M14.4 9.4c-.6-.8-1.5-1.2-2.5-1.2-1.4 0-2.5.8-2.5 1.9 0 2.5 5 1.4 5 3.9 0 1.1-1.1 1.9-2.5 1.9-1 0-1.9-.4-2.5-1.2"/>',
 columns:'<path d="M2.5 21h19"/><path d="M12 2.6 3.4 7v2.2h17.2V7L12 2.6Z"/><path d="M6.4 9.2V18M12 9.2V18M17.6 9.2V18"/>',
 pipes:'<path d="M2.5 7.4h6.6a3 3 0 0 1 3 3v3.2a3 3 0 0 0 3 3h6.4"/><circle cx="2.5" cy="7.4" r="1.5"/><circle cx="21.5" cy="16.6" r="1.5"/><path d="M8 5.6v3.6M16 14.8v3.6"/>',
 rocket:'<path d="M12 2.6c1.4 1.5 4.2 4.6 4.2 8.4 0 3-1.4 5.5-4.2 7.6-2.8-2.1-4.2-4.6-4.2-7.6 0-3.8 2.8-6.9 4.2-8.4Z"/><circle cx="12" cy="9.6" r="1.8"/><path d="M8.4 15 5.8 19.4l3.9-1.4M15.6 15l2.6 4.4-3.9-1.4"/>',
 person:'<circle cx="12" cy="8.2" r="3.4"/><path d="M4.8 20a7.2 7.2 0 0 1 14.4 0"/>',
 sequence:'<path d="M3.5 6h11M3.5 12h16M3.5 18h8"/><path d="M17.6 3.4 21 6l-3.4 2.6"/>',
 cpu:'<rect x="4.5" y="4.5" width="15" height="15" rx="3"/><rect x="9" y="9" width="6" height="6" rx="1.5"/><path d="M9.5 2v2.5M14.5 2v2.5M9.5 19.5V22M14.5 19.5V22M2 9.5h2.5M2 14.5h2.5M19.5 9.5H22M19.5 14.5H22"/>',
 ledger:'<path d="M4.5 5a2.5 2.5 0 0 1 2.5-2.5h12.5v19H7A2.5 2.5 0 0 0 4.5 24V5Z"/><path d="M4.5 18.2h15"/><path d="M8.5 7h7M8.5 11h5"/>',
 anchor:'<circle cx="12" cy="5" r="2.3"/><path d="M12 7.3V21.5"/><path d="M7.6 11h8.8"/><path d="M3.8 14.6a8.2 8.2 0 0 0 16.4 0"/>',
 scale:'<path d="M12 4.5v16.8M7.4 21.3h9.2"/><path d="M12 7 4.6 9M12 7l7.4 2"/><path d="M4.6 9 2 15h5.2L4.6 9Z"/><path d="M19.4 9 16.8 15H22l-2.6-6Z"/>',
 dots:'<circle cx="6" cy="12" r="1.5" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"/><circle cx="18" cy="12" r="1.5" fill="currentColor" stroke="none"/>'
};
function ico(k){
  return '<svg data-ic="'+k+'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '+
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+(ICONS[k]||ICONS.apps)+'</svg>';
}

/* Hình hiệu vẽ phỏng theo phong cách nhận diện của từng thành phố —
   đây là bản tôi tự dựng, KHÔNG phải tệp logo chính thức. */
var MARKS={
 base:'<path d="M18.5 5.07A9.5 9.5 0 1 0 18.5 18.93Z" fill="currentColor" stroke="none"/>',
 arb:'<path d="M12 2.4 3.3 7.3v9.4L12 21.6l8.7-4.9V7.3L12 2.4Z"/><path d="m8 16.6 4-8.6 4 8.6"/><path d="M10.1 13h3.8"/>',
 op:'<circle cx="12" cy="12" r="9.4" fill="currentColor" stroke="none"/><circle cx="8.4" cy="12" r="2.3" fill="none" stroke="#fff" stroke-width="1.7"/><path d="M13.6 15.4V8.6h2.3a2.1 2.1 0 0 1 0 4.2h-2.3" stroke="#fff" stroke-width="1.7" fill="none"/>',
 bnb:'<path d="M12 2.6 14.9 5.5 12 8.4 9.1 5.5 12 2.6Z"/><path d="M18.5 9.1 21.4 12l-2.9 2.9L15.6 12l2.9-2.9Z"/><path d="M5.5 9.1 8.4 12l-2.9 2.9L2.6 12l2.9-2.9Z"/><path d="M12 15.6l2.9 2.9L12 21.4 9.1 18.5 12 15.6Z"/><path d="M12 9.2 14.8 12 12 14.8 9.2 12 12 9.2Z"/>',
 moon:'<circle cx="10.4" cy="12" r="5.2"/><path d="M17 6.6a7.6 7.6 0 0 1 0 10.8"/><path d="M20.2 4.2a11.4 11.4 0 0 1 0 15.6"/>',
 osmo:'<circle cx="12" cy="12" r="3.6"/><ellipse cx="12" cy="12" rx="9.6" ry="4" transform="rotate(-32 12 12)"/><ellipse cx="12" cy="12" rx="9.6" ry="4" transform="rotate(32 12 12)"/>',
 zkfold:'<path d="M5.5 5h13L5.5 19h13"/>',
 star4:'<path d="M12 2.4 14.5 9.5 21.6 12l-7.1 2.5L12 21.6 9.5 14.5 2.4 12l7.1-2.5L12 2.4Z"/>',
 scrollm:'<path d="M6.5 3.5h9A2.5 2.5 0 0 1 18 6v12a2.5 2.5 0 0 1-2.5 2.5h-9A2.5 2.5 0 0 1 4 18V6a2.5 2.5 0 0 1 2.5-2.5Z"/><path d="M7.6 8h8M7.6 12h8M7.6 16h4.5"/>',
 lines3:'<path d="M3.6 7.4h16.8M3.6 12h16.8M3.6 16.6h10.6"/>',
 hexm:'<path d="M12 2.5 20.6 7.2v9.6L12 21.5 3.4 16.8V7.2L12 2.5Z"/><path d="M12 8.2 16.2 10.6v4.8L12 17.8l-4.2-2.4v-4.8L12 8.2Z"/>',
 burst:'<circle cx="12" cy="12" r="2.7"/><path d="M12 2.4v4.4M12 17.2v4.4M2.4 12h4.4M17.2 12h4.4M5.2 5.2l3.1 3.1M15.7 15.7l3.1 3.1M18.8 5.2l-3.1 3.1M8.3 15.7l-3.1 3.1"/>',
 shellm:'<path d="M12 3.2a8.8 8.8 0 1 1 0 17.6"/><path d="M12 6.7a5.3 5.3 0 1 1 0 10.6"/><path d="M12 3.2v17.6"/>',
 ringm:'<circle cx="12" cy="12" r="8.6"/><circle cx="12" cy="12" r="3.3"/>',
 crystal:'<path d="M12 2.6 19.2 8v8L12 21.4 4.8 16V8L12 2.6Z"/><path d="M4.8 8 12 12.4 19.2 8M12 12.4v9"/>'
};
function mark(k){
  return '<svg data-mark="'+k+'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '+
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+(MARKS[k]||ICONS.city)+'</svg>';
}
var CREST={eth:"castle",bnb:"towers",sol:"tower",avax:"mountain",dot:"hub",
           atom:"network",sui:"drop",near:"passport",ton:"phone"};
var L2ICON={eth:"city",bnb:"city",sol:"layers",avax:"mountain",dot:"hub",
            atom:"network",sui:"layers",near:"layers",ton:"phone"};
var GROUP_RULES=[
 [/defi|giao dich|tai chinh/,"bank"],
 [/staking|loi suat/,"coin"],
 [/social|noi dung/,"chat"],
 [/thanh toan|payment/,"card"],
 [/rwa|tai san thuc|to chuc/,"deed"],
 [/game|nft/,"game"],
 [/launchpad|memecoin/,"rocket"],
 [/depin|ha tang vat ly/,"antenna"],
 [/tieu dung|dai chung/,"person"],
 [/\bai\b|tac tu|tinh toan/,"robot"],
 [/rpc|node/,"antenna"],
 [/dich vu mang/,"pipes"],
 [/oracle/,"satellite"],
 [/luu tru/,"box"],
 [/danh tinh|tai khoan/,"id"],
 [/du lieu|chi muc|kham pha|dinh tuyen|phan tich/,"database"],
 [/cong cu|khung|lap trinh|van hanh|giao thuc/,"gear"],
 [/\bvi\b/,"wallet"]
];
function pickIcon(item,groupName,ctx){
  if(item && item.more) return "dots";
  if(ctx && ctx.kind==="gate") return "bridge";
  var g=norm(groupName||"");
  for(var i=0;i<GROUP_RULES.length;i++) if(GROUP_RULES[i][0].test(g)) return GROUP_RULES[i][1];
  if(!ctx) return "apps";
  if(ctx.kind==="l2") return L2ICON[current?current.id:"eth"]||"city";
  if(ctx.kind==="l3") return "gate";
  if(ctx.kind==="app") return "apps";
  if(ctx.kind==="infra") return "pipes";
  if(ctx.kind==="band") return ({wallet:"wallet",econ:"coin",gov:"columns"})[ctx.id]||"person";
  return "apps";
}

/* ══ helpers ══════════════════════════════════════════ */
function $(i){return document.getElementById(i);}
function el(t,c){var e=document.createElement(t); if(c)e.className=c; return e;}
function initials(n){
  var c=n.replace(/\(.*?\)/g,"").trim(), w=c.split(/[\s.\/&-]+/).filter(Boolean);
  if(!w.length) return "?";
  if(w.length===1) return w[0].slice(0,2).toUpperCase();
  return (w[0][0]+w[1][0]).toUpperCase();
}
function norm(s){return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/đ/g,"d");}
function byId(id){ for(var i=0;i<CHAINS.length;i++) if(CHAINS[i].id===id) return CHAINS[i]; return null; }

/* corpus for cross-country search */
var CORPUS=[];
CHAINS.forEach(function(C){
  var push=function(items,grp){ items.forEach(function(it){ if(!it.more)
    CORPUS.push({c:C.id, s:norm(it.n+" "+(it.r||"")+" "+grp)}); }); };
  C.tiers.forEach(function(T){ T.groups.forEach(function(G){ push(G.items,(G.name||T.title)); }); });
  C.bands.forEach(function(B){ push(B.items,B.title); });
  CORPUS.push({c:C.id, s:norm(C.name+" "+C.tag)});
});

var INDEX=[], current=null, active={};

/* ══ country list ═════════════════════════════════════ */
var countryList=$("countryList");
$("cCount").textContent=CHAINS.length;
function renderCountryList(){
  countryList.innerHTML="";
  RANKED.forEach(function(r){
    var C=r.chain;
    var b=el("button","nav-item ranked"); b.type="button";
    b.style.setProperty("--c",C.acc); b.style.setProperty("--t",C.accT);
    b.dataset.country=C.id; b.title=C.name+" — điểm nội lực "+r.score+"/100";
    var rk=el("span","rk"); rk.textContent=r.rank;
    var m=el("span","mono"); m.innerHTML=ico(CREST[C.id]||"earth");
    var l=el("span","lbl"); l.textContent=C.name;
    var c=el("span","cnt"); c.textContent=r.score;
    var mt=el("span","meter"); var f=el("i"); f.style.width=r.score+"%"; mt.appendChild(f);
    b.appendChild(rk); b.appendChild(m); b.appendChild(l); b.appendChild(c); b.appendChild(mt);
    b.addEventListener("click",function(){
      if(inRank) closeRanking();
      go(C.id); if(window.innerWidth<=900) setNav("full");
    });
    countryList.appendChild(b);
  });
  [].slice.call(countryList.children).forEach(function(b){
    b.dataset.on=(current && b.dataset.country===current.id)?"1":"0";
  });
}

/* ══ card builders ════════════════════════════════════ */
function makeCard(item,ctx,groupName){
  var b=el("button","card"+(item.more?" more":"")+(item.to?" gate":"")); b.type="button";
  b.style.setProperty("--c",ctx.c); b.style.setProperty("--t",ctx.t);
  var m=el("span","mono"); m.innerHTML=ico(pickIcon(item,groupName,ctx));
  var n=el("span","nm"); n.textContent=item.n;
  b.appendChild(m); b.appendChild(n);
  if(item.more){ b.setAttribute("aria-disabled","true"); b.tabIndex=-1;
    b.dataset.search=norm(item.n); b.dataset.more="1"; }
  else{
    INDEX.push({n:item.n,r:item.r,to:item.to||null,kind:ctx.kind||null,tag:ctx.tag,grp:groupName||ctx.title,
                c:ctx.c,t:ctx.t,key:ctx.id+"::"+(groupName||"")});
    b.dataset.i=String(INDEX.length-1);
    b.dataset.search=norm(item.n+" "+item.r+" "+(groupName||"")+" "+ctx.title);
    b.setAttribute("aria-haspopup","dialog");
  }
  /* móc L2BEAT — gắn huy hiệu Stage. Xoá l2beat.js là dòng này tự vô hiệu. */
  if(window.KT_L2B) window.KT_L2B.badge(b,item,ctx);
  return b;
}

/* ══ render one country ═══════════════════════════════ */
function render(id){
  var C=byId(id); if(!C) return;
  current=C; INDEX=[];
  document.documentElement.style.setProperty("--acc",C.acc);
  document.documentElement.style.setProperty("--acc-t",C.accT);
  document.title=C.name+" — bản đồ quốc gia blockchain";
  $("barTitle").textContent=C.name;
  var gl=$("hGloss");
  if(C.gloss){
    gl.hidden=false; gl.innerHTML="";
    var gh=el("h3"); gh.textContent=C.gloss.title; gl.appendChild(gh);
    if(C.gloss.note){ var gp=el("p"); gp.textContent=C.gloss.note; gl.appendChild(gp); }
    var dl=el("dl");
    C.gloss.rows.forEach(function(r){
      var row=el("div","grow");
      var dt=el("dt"); dt.textContent=r[0];
      var eq=el("span","eq"); eq.textContent="=";
      var dd=el("dd"); dd.textContent=r[1];
      row.appendChild(dt); row.appendChild(eq); row.appendChild(dd);
      dl.appendChild(row);
    });
    gl.appendChild(dl);
    if(C.gloss.foot){
      var gf=el("p"); gf.style.cssText="margin:12px 0 0;font-size:12.3px;color:var(--ink-3);line-height:1.55;border-top:1px solid var(--line);padding-top:11px";
      gf.textContent=C.gloss.foot; gl.appendChild(gf);
    }
  } else { gl.hidden=true; gl.innerHTML=""; }
  $("hCrest").innerHTML=ico(CREST[C.id]||"earth");
  $("hCap").textContent=C.cap;
  $("hName").textContent=C.name;
  $("hTag").textContent=C.tag;
  $("q").placeholder="Tìm trong "+C.name+"…";
  $("insideLabel").textContent="Bên trong "+C.name;

  var ul=$("hBullets"); ul.innerHTML="";
  C.sov.forEach(function(t){ var li=el("li"); li.textContent=t; ul.appendChild(li); });
  var ur=$("hRoles"); ur.innerHTML="";
  C.roles.forEach(function(t){ var li=el("li"); li.textContent=t; ur.appendChild(li); });

  var host=$("layers"); host.innerHTML="";
  C.tiers.forEach(function(T){
    var col=KIND[T.kind]||KIND.app;
    var sec=el("section","layer"); sec.id="sec-"+T.id; sec.dataset.layer=T.id;
    sec.style.setProperty("--c",col[0]); sec.style.setProperty("--t",col[1]);
    var head=el("div","layer-head");
    var tg=el("span","tag"); tg.textContent=T.tag;
    var h2=el("h2"); h2.textContent=T.title;
    var kk=el("span","kk"); kk.textContent=T.kicker;
    head.appendChild(tg); head.appendChild(h2); head.appendChild(kk);
    var body=el("div","layer-body");
    var note=el("p","layer-note"+(T.warn?" warn":"")); note.textContent=T.note; body.appendChild(note);
    T.groups.forEach(function(G){
      var gr=el("div","group"); gr.dataset.group="1";
      if(G.name){ var gn=el("span","group-name"); gn.textContent=G.name; gr.appendChild(gn); }
      var grid=el("div","grid");
      var ctx={id:T.id,kind:T.kind,tag:T.tag,title:T.title,c:col[0],t:col[1]};
      G.items.forEach(function(it){ grid.appendChild(makeCard(it,ctx,G.name)); });
      gr.appendChild(grid); body.appendChild(gr);
    });
    sec.appendChild(head); sec.appendChild(body); host.appendChild(sec);
  });

  var bh=$("bands"); bh.innerHTML="";
  C.bands.forEach(function(B){
    var col=KIND.band;
    var d=el("div","band"); d.id="sec-"+B.id; d.dataset.layer=B.id;
    d.style.setProperty("--c",col[0]); d.style.setProperty("--t",col[1]);
    var h3=el("h3"); h3.textContent=B.title;
    var st=el("div","stack"); st.dataset.group="1";
    var ctx={id:B.id,kind:"band",tag:"NGƯỜI DÙNG",title:B.title,c:col[0],t:col[1]};
    B.items.forEach(function(it){ st.appendChild(makeCard(it,ctx,B.title)); });
    d.appendChild(h3); d.appendChild(st); bh.appendChild(d);
  });

  /* nav + chips */
  var NAV=C.tiers.map(function(T){
    var n=0; T.groups.forEach(function(G){G.items.forEach(function(i){if(!i.more)n++;});});
    var col=KIND[T.kind]||KIND.app;
    return {id:T.id,tag:T.tag,title:T.title,c:col[0],t:col[1],count:n,
            icon:pickIcon(null,null,{id:T.id,kind:T.kind})};
  }).concat(C.bands.map(function(B){
    return {id:B.id,tag:"NG",title:B.title,c:KIND.band[0],t:KIND.band[1],count:B.items.length,
            icon:pickIcon(null,null,{id:B.id,kind:"band"})};
  }));

  active={}; NAV.forEach(function(n){ active[n.id]=true; });

  var sl=$("secList"); sl.innerHTML="";
  NAV.forEach(function(n){
    var b=el("button","nav-item"); b.type="button";
    b.style.setProperty("--c",n.c); b.style.setProperty("--t",n.t);
    b.dataset.jump=n.id; b.title=n.title;
    var m=el("span","mono"); m.innerHTML=ico(n.icon);
    var l=el("span","lbl"); l.textContent=n.title;
    var c=el("span","cnt"); c.textContent=n.count;
    b.appendChild(m); b.appendChild(l); b.appendChild(c);
    b.addEventListener("click",function(){
      var t=$("sec-"+n.id); if(t) t.scrollIntoView({behavior:"smooth",block:"start"});
      if(window.innerWidth<=900) setNav("full");
    });
    sl.appendChild(b);
  });

  var ch=$("chips"); ch.innerHTML="";
  NAV.forEach(function(n){
    var b=el("button","chip"); b.type="button";
    b.style.setProperty("--c",n.c);
    b.setAttribute("aria-pressed","true"); b.dataset.id=n.id;
    var dot=el("span","dot"); dot.style.background=n.c;
    b.appendChild(dot); b.appendChild(document.createTextNode(n.title));
    b.addEventListener("click",function(){
      active[n.id]=!active[n.id];
      b.setAttribute("aria-pressed",active[n.id]?"true":"false"); apply();
    });
    ch.appendChild(b);
  });

  [].slice.call(countryList.children).forEach(function(b){
    b.dataset.on = (b.dataset.country===C.id)?"1":"0";
  });
  $("rankBackLabel").textContent="Quay lại bản đồ "+C.name;

  apply();
}

function go(id, keepQuery){
  if(inRank){ inRank=false; $("rankWrap").hidden=true;
    document.querySelector(".main > .wrap").hidden=false; $("chips").hidden=false; }
  if(current && current.id===id && !inCity) return;
  if(inCity){ inCity=null; $("cityWrap").hidden=true;
    document.querySelector(".main > .wrap").hidden=false; $("chips").hidden=false;
    if(current && current.id===id){ $("barTitle").textContent=current.name;
      window.location.hash=id; window.scrollTo({top:0,behavior:"auto"}); return; } }
  if(!keepQuery) $("q").value="";
  if(window.location.hash.slice(1)!==id) window.location.hash=id;
  render(id);
  window.scrollTo({top:0,behavior:"auto"});
}

/* ══ filter ═══════════════════════════════════════════ */
function apply(){
  var q=norm($("q").value.trim()), shown=0;
  var cards=[].slice.call(document.querySelectorAll(".card"));
  cards.forEach(function(c){
    var sec=c.closest("[data-layer]");
    var on=sec && active[sec.dataset.layer]!==false;
    var vis=on && (!q || c.dataset.search.indexOf(q)!==-1);
    c.hidden=!vis;
    if(vis && !c.dataset.more) shown++;
  });
  document.querySelectorAll("[data-group]").forEach(function(g){
    g.hidden=!g.querySelector(".card:not([hidden])");
  });
  document.querySelectorAll("[data-layer]").forEach(function(s){
    s.hidden=!s.querySelector(".card:not([hidden])");
  });
  $("sec-hero").hidden = !!q;

  var old=document.querySelector(".empty"); if(old) old.remove();
  if(shown===0){
    /* Hai dòng, không một dòng: dòng đầu nói CHUYỆN GÌ XẢY RA, dòng sau
       nói LÀM GÌ TIẾP. Bản cũ chỉ có dòng đầu cho ca tìm không ra, nên
       người dùng đứng trước một trang trắng mà không có lối đi nào. */
    var e=el("div","empty"), tu=$("q").value.trim();
    var t=el("p","empty-t"), s=el("p","empty-s");
    if(q){
      t.textContent="Không tìm thấy “"+tu+"”";
      s.textContent="Không mục nào trong "+current.name+" khớp chữ này. "+
        "Thử một chữ ngắn hơn, hoặc xoá ô tìm để xem lại toàn bản đồ.";
    }else{
      t.textContent="Mọi tầng đang bị ẩn";
      s.textContent="Bật lại một tầng ở thanh lọc phía trên để thấy các mục của "+current.name+".";
    }
    e.appendChild(t); e.appendChild(s);
    if(q){
      var tally={};
      CORPUS.forEach(function(r){ if(r.c!==current.id && r.s.indexOf(q)!==-1) tally[r.c]=(tally[r.c]||0)+1; });
      var ks=Object.keys(tally);
      if(ks.length){
        var row=el("div","elsewhere");
        ks.slice(0,6).forEach(function(k){
          var b=el("button"); b.type="button";
          b.textContent=byId(k).name+" ("+tally[k]+")";
          /* Đọc bằng trình đọc màn hình thì "Ethereum 3" không nói lên
             gì — con số trong ngoặc chỉ có nghĩa nhờ nhãn nhóm ở trên,
             mà nhãn ấy không đi cùng nút. Nói đủ câu ngay trên nút. */
          b.setAttribute("aria-label","Xem "+tally[k]+" kết quả khớp ở "+byId(k).name);
          b.addEventListener("click",function(){ go(k,true); });
          row.appendChild(b);
        });
        var hint=el("p","empty-lab");
        hint.textContent="Có kết quả ở nước khác";
        e.appendChild(hint); e.appendChild(row);
      }
    }
    $("layers").parentNode.insertBefore(e,$("layers"));
  }
  $("hits").textContent=shown+" mục";
  onScroll();
}
$("q").addEventListener("input",function(){ if(inCity) closeCity(); if(inRank) closeRanking(); apply(); });
document.addEventListener("keydown",function(ev){
  if(ev.key==="/" && document.activeElement!==$("q")){ ev.preventDefault(); setNav("full"); $("q").focus(); }
});

/* ══ sidebar state ════════════════════════════════════ */
function setNav(m){ document.body.dataset.nav=m; }
$("toggleNav").addEventListener("click",function(){
  if(window.innerWidth<=900){ setNav("full"); return; }
  setNav(document.body.dataset.nav==="mini"?"full":"mini");
});
$("openNav").addEventListener("click",function(){ setNav("open"); });
$("openSearch").addEventListener("click",function(){ setNav("open"); $("q").focus(); });
document.addEventListener("click",function(ev){
  if(document.body.dataset.nav!=="open") return;
  if(ev.target.closest && (ev.target.closest("#nav")||ev.target.closest("#openNav")||ev.target.closest("#openSearch"))) return;
  setNav("full");
});

/* ══ drawer ═══════════════════════════════════════════ */
var drawer=$("drawer"), scrim=$("scrim"), lastFocus=null;
function dSec(title,node){
  var w=el("div","d-sec");
  if(title){ var h=el("div","d-h"); h.textContent=title; w.appendChild(h); }
  w.appendChild(node); return w;
}
function dPara(t){ var p=el("p","d-p"); p.textContent=t; return p; }
function dChips(names,onPick,icon){
  var w=el("div","d-chips");
  names.forEach(function(n){
    var b=el("button"); b.type="button";
    if(icon) b.innerHTML=ico(icon);
    b.appendChild(document.createTextNode(n));
    b.addEventListener("click",function(){ onPick(n); });
    w.appendChild(b);
  });
  return w;
}
function drawerShell(tag,grp,name,col){
  lastFocus=lastFocus||document.activeElement;
  drawer.style.setProperty("--c",col[0]); drawer.style.setProperty("--t",col[1]);
  $("dTag").textContent=tag; $("dGrp").textContent=grp; $("dName").textContent=name;
  var host=$("dBodyHost"); host.innerHTML="";
  return host;
}
function openDrawer(i){
  var d=INDEX[i]; if(!d) return;
  lastFocus=document.activeElement;
  var host=drawerShell(d.tag,d.grp,d.n,[d.c,d.t]);
  host.appendChild(dSec(null,dPara(d.r)));
  if(d.to && byId(d.to)){
    var target=byId(d.to);
    var w=el("div","d-chips");
    var b=el("button"); b.type="button";
    b.textContent="Mở bản đồ "+target.name+" →";
    b.style.borderColor=target.acc; b.style.color=target.acc;
    b.addEventListener("click",function(){ closeDrawer(); go(target.id); });
    w.appendChild(b);
    host.appendChild(dSec("Dẫn tới",w));
  }
  if(d.kind==="l2" && !d.to && CITY_OK[current.id]){
    var w2=el("div","d-chips");
    var b2=el("button"); b2.type="button";
    b2.textContent="Đi vào thành phố "+d.n+" →";
    b2.style.borderColor=current.acc; b2.style.color=current.acc;
    b2.addEventListener("click",function(){ closeDrawer(); openCity(d.n); });
    w2.appendChild(b2);
    host.appendChild(dSec("Bên trong",w2));
  }
  var mates=INDEX.filter(function(x){ return x.key===d.key && x.n!==d.n; }).slice(0,10);
  if(mates.length){
    host.appendChild(dSec("Cùng nhóm", dChips(mates.map(function(m){return m.n;}),function(n){
      var t=INDEX.filter(function(x){return x.key===d.key && x.n===n;})[0];
      if(t) openDrawer(INDEX.indexOf(t));
    })));
  }
  drawer.dataset.open="1"; scrim.dataset.open="1"; drawer.focus();
}

/* ── hồ sơ chi tiết trong thành phố ── */
var CITY_CELLS={};
function entKey(cityName,itemName){ return norm(cityName)+"::"+norm(itemName); }
function indexCityCells(city){
  var m={};
  function reg(o,sect){ m[norm(o.n)]={n:o.n,sect:sect,fb:o.s};
    (o.p||[]).forEach(function(nm){ if(!m[norm(nm)]) m[norm(nm)]={n:nm,sect:"prov",fb:""}; }); }
  city.infra.forEach(function(c){ var cur=c; while(cur){ reg(cur,"infra"); cur=cur.to; } });
  (city.orgs||[]).forEach(function(o){ m[norm(o.n)]={n:o.n,sect:"org",fb:o.s}; });
  if(city.districts) city.districts.groups.forEach(function(G){ G.items.forEach(function(o){ reg(o,"org"); }); });
  if(city.econ) city.econ.groups.forEach(function(G){ G.items.forEach(function(o){ reg(o,"econ"); }); });
  if(city.machine) city.machine.items.forEach(function(x){ reg(x,"machine"); });
  if(city.standard) m[norm(city.standard.n)]={n:city.standard.n,sect:"standard",fb:city.standard.s};
  m[norm(city.gate.n)]={n:city.gate.n,sect:"gate",fb:city.gate.note};
  CITY_CELLS[norm(city.n)]=m;
}
function cellInfo(cityName,name){
  var m=CITY_CELLS[norm(cityName)]||{};
  return m[norm(name)]||{n:name,sect:"infra",fb:""};
}
function usedByOf(key){
  var me=key.split("::")[1], city=key.split("::")[0], out=[];
  for(var k in ENTITIES){
    var kc=k.split("::")[0];
    if(kc!==city && kc!=="*") continue;
    var u=ENTITIES[k].uses||[];
    for(var i=0;i<u.length;i++) if(norm(u[i])===me){
      out.push(cellInfo(city,k.split("::")[1]).n); break; }
  }
  return out;
}
function openEntity(cityName,itemName,sect,fallback,ofRole){
  var key=entKey(cityName,itemName);
  var E=ENTITIES[key]||ENTITIES["*::"+norm(itemName)], col=(sect==="org")?KIND.app:(sect==="econ")?KIND.band:
    (sect==="machine"||sect==="standard")?KIND.l3:(sect==="prov")?KIND.l2:KIND.infra;
  lastFocus=document.activeElement;
  var sectLabel = sect==="org" ? "Cơ quan · công trình"
                : sect==="gate" ? "Cổng thành"
                : sect==="machine" ? "Bộ máy vận hành"
                : sect==="standard" ? "Bộ quy chuẩn"
                : sect==="econ" ? "Kinh tế & cư dân"
                : sect==="prov" ? "Nhà cung cấp · sản phẩm" : "Hạ tầng đô thị";
  var host=drawerShell(sectLabel, cityName, itemName, col);

  if(!E){
    if(sect==="prov"){
      host.appendChild(dSec("Vai trò",dPara(
        "Một sản phẩm đang đảm nhận vai trò “"+(ofRole||"?")+"” trong thành phố "+cityName+".")));
      if(ofRole){
        host.appendChild(dSec("Đảm nhận vai trò", dChips([ofRole],function(n){
          var ci=cellInfo(cityName,n); openEntity(cityName,ci.n,ci.sect,ci.fb); })));
      }
      var np=el("p","d-thin");
      np.textContent="Chưa có hồ sơ chi tiết cho sản phẩm này. Vai trò nó đảm nhận thì đã có — bấm vào chip ở trên.";
      host.appendChild(dSec(null,np));
      drawer.dataset.open="1"; scrim.dataset.open="1"; drawer.focus(); return;
    }
    host.appendChild(dSec("Vai trò",dPara(fallback||"Một thành phần trong hệ sinh thái của "+cityName+".")));
    var ul0=el("ul","d-chain");
    [byId(inCityParent).name+" — nền chủ quyền", cityName+" — đất và hạ tầng thành phố",
     itemName+" — "+(sectLabel.toLowerCase()), "Phục vụ người dân trong thành phố"].forEach(function(t){
      var li=el("li"); li.textContent=t; ul0.appendChild(li); });
    host.appendChild(dSec("Vị trí trong thành phố",ul0));
    var n0=el("p","d-thin");
    n0.textContent="Chưa có hồ sơ chi tiết cho mục này — phần trên dựng từ cấu trúc thành phố, chưa phải mô tả riêng.";
    host.appendChild(dSec(null,n0));
    drawer.dataset.open="1"; scrim.dataset.open="1"; drawer.focus();
    return;
  }

  var r=el("div","d-role2"); r.textContent=E.role;
  host.appendChild(dSec(null,r));
  host.appendChild(dSec("Là gì",dPara(E.what)));
  if(E.metaphor) host.appendChild(dSec("Vị trí trong thành phố",dPara(E.metaphor)));
  if(E.of){
    host.appendChild(dSec("Đảm nhận vai trò", dChips([E.of],function(n){
      var ci=cellInfo(cityName,n); openEntity(cityName,ci.n,ci.sect,ci.fb); })));
  }
  if(E.chain && E.chain.length){
    var ul=el("ul","d-chain");
    E.chain.forEach(function(t){ var li=el("li"); li.textContent=t; ul.appendChild(li); });
    host.appendChild(dSec("Dòng chảy",ul));
  }

  if(E.uses && E.uses.length){
    host.appendChild(dSec("Dựa vào", dChips(E.uses,function(n){ var ci=cellInfo(cityName,n);
      openEntity(cityName,ci.n,ci.sect,ci.fb); })));
  }
  var ub=usedByOf(key);
  if(ub.length){
    host.appendChild(dSec("Được dùng bởi", dChips(ub,function(n){ var ci=cellInfo(cityName,n);
      openEntity(cityName,ci.n,ci.sect,ci.fb); })));
  }
  if(E.special) host.appendChild(dSec("Điểm đáng chú ý",dPara(E.special)));
  if(E.compare && E.compare.length){
    var c=el("div","d-cmp");
    E.compare.forEach(function(x){
      var d1=el("div"); var b=el("b"); b.textContent=x.n;
      var sp=el("span"); sp.textContent=x.s;
      d1.appendChild(b); d1.appendChild(sp); c.appendChild(d1);
    });
    host.appendChild(dSec("So với",c));
  }
  if(E.where){
    var w=el("div","d-where"); w.textContent=E.where;
    host.appendChild(dSec("Chạy ở đâu",w));
  }
  drawer.dataset.open="1"; scrim.dataset.open="1"; drawer.focus();
}
function closeDrawer(){
  drawer.dataset.open="0"; scrim.dataset.open="0";
  if(lastFocus && lastFocus.focus) lastFocus.focus();
}
document.addEventListener("click",function(ev){
  if(!ev.target.closest) return;
  var provHit=ev.target.closest(".prov");
  if(provHit && provHit.dataset.prov){
    openEntity(provHit.dataset.city||current.name, provHit.dataset.prov, "prov", "", provHit.dataset.of);
    return;
  }
  var cellHit=ev.target.closest(".cell, .gate, .node.std");
  if(cellHit && cellHit.dataset.cell){
    openEntity(cellHit.dataset.city, cellHit.dataset.cell, cellHit.dataset.sect, cellHit.dataset.fallback);
    return;
  }
  var hit=ev.target.closest(".card");
  if(!hit || !hit.dataset.i) return;
  var rec=INDEX[+hit.dataset.i];
  if(rec && rec.kind==="l2" && !rec.to && openCity(rec.n)) return;
  openDrawer(+hit.dataset.i);
});
$("dClose").addEventListener("click",closeDrawer);
scrim.addEventListener("click",closeDrawer);
document.addEventListener("keydown",function(ev){
  if(ev.key==="Escape"){
    if(drawer.dataset.open==="1") closeDrawer();
    else if(document.body.dataset.nav==="open") setNav("full");
  }
});




function fmtUsd(v){
  if(v>=1e9) return "$"+(v/1e9).toFixed(v/1e9>=10?1:2)+"b";
  if(v>=1e6) return "$"+(v/1e6).toFixed(v/1e6>=100?0:(v/1e6>=10?1:2))+"m";
  return "$"+Math.round(v/1e3)+"k";
}
function fmtNum(v){
  if(v>=1e6) return (v/1e6).toFixed(2)+"m";
  if(v>=1e3) return Math.round(v/1e3)+"k";
  return String(v);
}
function fmtCell(v,f){ return f==="usd"?fmtUsd(v):f==="score"?(v+"/100"):
  f==="int"?Math.round(v).toLocaleString("vi-VN"):fmtNum(v); }
/* thang log: nếu dùng thang thẳng thì Ethereum full vạch, tám nước còn lại gần như trắng */
function normLog(v,min,max){
  if(max<=min) return 100;
  var lv=Math.log10(Math.max(v,1)), lo=Math.log10(Math.max(min,1)), hi=Math.log10(Math.max(max,1));
  return Math.max(0,Math.min(100, (lv-lo)/(hi-lo)*100));
}
var RANKED=[];
function computeRanking(){
  var ids=CHAINS.map(function(c){return c.id;});
  var bounds={};
  DIMS.forEach(function(D){
    var vals=ids.map(function(i){return STRENGTH[i][D.k];});
    bounds[D.k]={min:Math.min.apply(null,vals), max:Math.max.apply(null,vals)};
  });
  RANKED=ids.map(function(i){
    var S=STRENGTH[i], parts={}, total=0;
    DIMS.forEach(function(D){
      var sc = D.k==="dec" ? S.dec : normLog(S[D.k],bounds[D.k].min,bounds[D.k].max);
      parts[D.k]=sc; total += sc*D.w/100;
    });
    return {id:i, chain:byId(i), score:Math.round(total), parts:parts, raw:S};
  }).sort(function(a,b){ return b.score-a.score; });
  RANKED.forEach(function(r,ix){ r.rank=ix+1; });

  /* Khai danh sách phòng cho CỔNG CHẶN của vòng tiến hoá
     (scripts/tien-hoa.mjs). Cung này điều hướng bằng <button> có
     addEventListener chứ không bằng <a href="#…">, nên bộ đo không có
     một cái href nào để nhặt — nó thấy KHÔNG phòng nào và chấm thước
     "Mọi phòng vẽ được" là trượt, trong khi cả 24 quốc gia vẽ bình
     thường trên trình duyệt. Đài Quan Trắc đã dính đúng chuyện này và
     giải bằng đúng cách này.

     Khai TRONG computeRanking() chứ không phải một lần lúc nạp: RANKED
     mới là nơi biết có những quốc gia nào, và nó dựng từ dữ liệu bot
     ghi 4 lượt/ngày. */
  window.__TUYEN = RANKED.map(function(r){ return "#" + r.id; });

  return RANKED;
}
function rankOf(id){
  for(var i=0;i<RANKED.length;i++) if(RANKED[i].id===id) return RANKED[i];
  return null;
}

var rankSort="score", rankDesc=true, inRank=false;
function openRanking(){
  inRank=true;
  var host=$("rankBody"); host.innerHTML="";
  $("rankBackLabel").textContent="Quay lại bản đồ "+current.name;

  var hero=el("div","rank-hero");
  var h=el("h2"); h.textContent="Bảng xếp hạng nội lực 9 quốc gia"; hero.appendChild(h);
  var p1=el("p");
  p1.textContent="Không xếp theo số mục tôi viết trong bản đồ — con số đó chỉ nói lên tôi viết nhiều hay ít. "+
    "Điểm dưới đây ghép từ năm chỉ số, bốn trong đó là số đo thật lấy từ DefiLlama ngày "+SNAP_DATE+".";
  var p2=el("p");
  p2.textContent="Các chỉ số chênh nhau hàng nghìn lần, nên tôi chấm theo thang log. Nếu chấm thẳng thì "+
    "Ethereum đầy vạch còn tám nước kia gần như trắng — đúng về mặt số học nhưng vô dụng để so sánh.";
  hero.appendChild(p1); hero.appendChild(p2);
  var rb=el("button","refresh"); rb.type="button"; rb.id="btnRefresh";
  rb.innerHTML='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 4v5h-5"/></svg>';
  rb.appendChild(document.createTextNode("Cập nhật vốn khoá trực tiếp"));
  var st=el("span","rstatus"); st.id="rStatus"; st.textContent="đang dùng số chụp ngày "+SNAP_DATE;
  rb.addEventListener("click",refreshTVL);
  var rw=el("div"); rw.appendChild(rb); rw.appendChild(st);
  hero.appendChild(rw);
  host.appendChild(hero);

  host.appendChild(rankTable());

  var note=el("div","rk-note");
  var nh=el("h3"); nh.textContent="Năm chỉ số và trọng số"; note.appendChild(nh);
  var wg=el("div","wgrid");
  DIMS.forEach(function(D){
    var w=el("div","wrow");
    var b=el("b"); b.textContent=D.n;
    var em=el("em"); em.textContent=D.w+"%"; b.appendChild(em);
    var sp=el("span"); sp.textContent=D.d;
    var tg=el("span","src "+(D.meas?"meas":"judg")); tg.textContent=D.meas?"số đo":"đánh giá";
    w.appendChild(b); w.appendChild(sp); w.appendChild(document.createElement("br")); w.appendChild(tg);
    wg.appendChild(w);
  });
  note.appendChild(wg);
  var cav=el("div","caveat");
  cav.innerHTML="<b>Bốn chỗ cần biết trước khi tin bảng này.</b> "+
    "Một: <b>Cosmos</b> và <b>Polkadot</b> là tổng cả hệ, cộng từ các nước thành viên và các bang — không phải một chuỗi đơn lẻ. "+
    "Hai: dữ liệu địa chỉ hoạt động của Cosmos và Polkadot trên DefiLlama <b>còn thiếu nhiều</b>, nên điểm Hoạt động của hai nước này bị thấp hơn thực tế. "+
    "Ba: cột <b>Phi tập trung</b> là tôi chấm, không phải số đo — nếu anh thấy sai thì đó là chỗ nên cãi trước. "+
    "Bốn: TVL và stablecoin <b>đổi theo giá thị trường từng ngày</b>; bảng này là ảnh chụp, không phải chân lý.";
  note.appendChild(cav);
  /* móc đóng dấu — chứng cứ bản số liệu này trên IPFS */
  if(window.KT_PROV) window.KT_PROV.section(note);
  host.appendChild(note);

  $("rankWrap").hidden=false;
  document.querySelector(".main > .wrap").hidden=true;
  $("cityWrap").hidden=true;
  $("chips").hidden=true;
  $("barTitle").textContent="Bảng xếp hạng nội lực";
  window.location.hash="rank";
  window.scrollTo({top:0,behavior:"auto"});
}
function rankTable(){
  var wrapd=el("div","tablewrap");
  var t=el("table","rank");
  var thead=el("thead"), tr=el("tr");
  var cols=[{k:"rank",n:"Hạng",l:1},{k:"name",n:"Quốc gia",l:1},{k:"score",n:"Điểm nội lực"}]
    .concat(DIMS.map(function(D){ return {k:D.k,n:D.n}; }));
  cols.forEach(function(c){
    var th=el("th", c.l?"l":""); th.textContent=c.n;
    if(c.k===rankSort) th.dataset.sorted="1";
    th.addEventListener("click",function(){
      if(rankSort===c.k) rankDesc=!rankDesc; else { rankSort=c.k; rankDesc=true; }
      var host=$("rankBody"); var old=host.querySelector(".tablewrap");
      host.replaceChild(rankTable(), old);
    });
    tr.appendChild(th);
  });
  thead.appendChild(tr); t.appendChild(thead);

  var rows=RANKED.slice();
  rows.sort(function(a,b){
    var av,bv;
    if(rankSort==="rank"||rankSort==="score"){ av=a.score; bv=b.score; }
    else if(rankSort==="name"){ return (rankDesc?1:-1)*a.chain.name.localeCompare(b.chain.name); }
    else { av=a.raw[rankSort]; bv=b.raw[rankSort]; }
    return rankDesc? bv-av : av-bv;
  });

  var tb=el("tbody");
  rows.forEach(function(r){
    var row=el("tr");
    var td0=el("td","l"); td0.textContent="#"+r.rank; td0.style.fontFamily='"IBM Plex Mono",monospace';
    td0.style.color="var(--ink-3)"; row.appendChild(td0);

    var td1=el("td","l");
    var cell=el("div","rk-cell");
    var ic=el("span","rk-ic"); ic.style.background=r.chain.accT; ic.style.color=r.chain.acc;
    ic.innerHTML=ico(CREST[r.id]||"earth");
    var nm=el("span","rk-nm"); nm.textContent=r.chain.name;
    cell.appendChild(ic); cell.appendChild(nm);
    cell.addEventListener("click",function(){ closeRanking(); go(r.id); });
    td1.appendChild(cell); row.appendChild(td1);

    var td2=el("td");
    var sc=el("div","rk-score");
    var bar=el("span","rk-bar"); var fill=el("i");
    fill.style.width=r.score+"%"; fill.style.background=r.chain.acc; bar.appendChild(fill);
    var val=el("span","rk-val"); val.textContent=r.score;
    sc.appendChild(bar); sc.appendChild(val);
    td2.appendChild(sc); row.appendChild(td2);

    DIMS.forEach(function(D){
      var td=el("td");
      td.textContent=fmtCell(r.raw[D.k],D.fmt)+((r.raw.partial&&D.k==="addr")?" *":"");
      if(r.raw.partial&&D.k==="addr") td.style.color="var(--ink-3)";
      row.appendChild(td);
    });
    tb.appendChild(row);
  });
  t.appendChild(tb); wrapd.appendChild(t);
  return wrapd;
}
function closeRanking(){
  if(!inRank) return;
  inRank=false;
  $("rankWrap").hidden=true;
  document.querySelector(".main > .wrap").hidden=false;
  $("chips").hidden=false;
  $("barTitle").textContent=current.name;
  window.location.hash=current.id;
  window.scrollTo({top:0,behavior:"auto"});
}

function refreshTVL(){
  var btn=$("btnRefresh"), st=$("rStatus");
  btn.disabled=true; st.textContent="đang gọi DefiLlama…";
  fetch("https://api.llama.fi/v2/chains").then(function(r){
    if(!r.ok) throw new Error("HTTP "+r.status);
    return r.json();
  }).then(function(rows){
    var by={}; rows.forEach(function(x){ by[x.name]=x.tvl; });
    var hit=0;
    for(var id in NAMEMAP){ if(by[NAMEMAP[id]]!=null){ STRENGTH[id].tvl=by[NAMEMAP[id]]; hit++; } }
    for(var a in AGG){
      var sum=0,n=0;
      AGG[a].forEach(function(nm){ if(by[nm]!=null){ sum+=by[nm]; n++; } });
      if(n){ STRENGTH[a].tvl=sum; hit++; }
    }
    computeRanking(); renderCountryList();
    var host=$("rankBody"); host.replaceChild(rankTable(), host.querySelector(".tablewrap"));
    st.textContent="đã cập nhật "+hit+"/9 nước lúc "+new Date().toLocaleTimeString("vi-VN");
    btn.disabled=false;
  }).catch(function(e){
    st.textContent="không gọi được DefiLlama ("+e.message+") — vẫn dùng số chụp ngày "+SNAP_DATE;
    btn.disabled=false;
  });
}


function genericCity(name, chain){
  return {parent:chain.id, n:name, generic:true,
   intro:"Chưa có bản đồ riêng cho thành phố này. Dưới đây là sơ đồ chung — đúng về cấu trúc dòng chảy, nhưng chưa nêu tên dự án cụ thể.",
   infra:[
    C_("antenna","RPC / Nodes","cửa vào chuỗi cho mọi ứng dụng",
       C_("database","Indexer","đọc và sắp xếp dữ liệu onchain"),"đọc trạng thái"),
    C_("satellite","Oracle","đưa giá và dữ liệu ngoài đời vào hợp đồng",
       C_("bridge","Cầu nối","chuyển tài sản sang chuỗi khác"),"dữ liệu thế giới thật"),
    C_("card","Stablecoin","đơn vị thanh toán trong thành phố"),
    C_("id","Ví / tài khoản","danh tính và tài sản của người dân")],
   orgs:[O_("bank","Tín dụng","vay và cho vay"),O_("coin","Chợ thanh khoản","nơi đổi tài sản"),
         O_("chat","Mạng xã hội","giao tiếp"),O_("game","Game & NFT","giải trí và vật phẩm"),
         O_("robot","AI & tác tử","tự động hoá"),O_("card","Thương mại","mua bán hàng hoá")],
   gate:{n:"Ví + cổng vào",q:"Cổng thành",tabs:["Ví","Cầu nối","Khám phá ứng dụng"],
         note:"Người dân bước vào bằng ví của mình và trang cầu nối của thành phố."}};
}

/* ══ dựng trang thành phố ═════════════════════════════ */
function citySlug(n){ return norm(n).replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,""); }
function cityKey(n){ return norm(n); }
function cityFor(name){
  var c=CITIES[cityKey(name)];
  if(c) return c;
  if(current && CITY_OK[current.id]) return genericCity(name, current);
  return null;
}
function sectLabelEl(no,text){
  var l=el("div","sect-label");
  var n=el("span","tno"); n.textContent=no;
  l.appendChild(n); l.appendChild(document.createTextNode(text));
  return l;
}
function districtsEl(groups,cityName,sect,col){
  var w=el("div");
  groups.forEach(function(G){
    var d=el("div","district");
    var h=el("div","dhead");
    var i=el("span","di"); i.style.setProperty("--c",col[0]); i.style.setProperty("--t",col[1]);
    i.innerHTML=ico(G.ic||"apps");
    var n=el("span","dn"); n.textContent=G.name;
    var ln=el("span","dl");
    h.appendChild(i); h.appendChild(n); h.appendChild(ln);
    var g=el("div","org-grid");
    G.items.forEach(function(it){ g.appendChild(cellEl(it,col,cityName,sect)); });
    d.appendChild(h); d.appendChild(g); w.appendChild(d);
  });
  return w;
}
function arrowEl(label){
  var a=el("div","arrow");
  a.innerHTML='<span class="ln"></span>'+(label?'<span class="lab">'+label+'</span>':"")+
              '<span class="ln"></span><span class="ar">▼</span>';
  return a;
}
function cellEl(c,col,cityName,sect){
  var d=el("button","cell"); d.type="button";
  if(cityName){ d.dataset.cell=c.n; d.dataset.sect=sect||"infra"; d.dataset.city=cityName;
    d.dataset.fallback=c.s||""; }
  d.style.setProperty("--c",col[0]); d.style.setProperty("--t",col[1]);
  var m=el("span","mono"); m.innerHTML=ico(c.ic);
  var box=el("div");
  var t=el("div","t"); t.textContent=c.n;
  var s=el("div","s"); s.textContent=c.s;
  box.appendChild(t); box.appendChild(s);
  if(c.p && c.p.length){
    var pl=el("div","provlead"); pl.textContent=(c.plead||"Ai đang làm việc này");
    var pw=el("div","provs");
    c.p.forEach(function(nm){
      var b=el("button","prov"); b.type="button";
      b.dataset.prov=nm; b.dataset.city=cityName||""; b.dataset.of=c.n;
      b.textContent=nm;
      pw.appendChild(b);
    });
    box.appendChild(pl); box.appendChild(pw);
  }
  d.appendChild(m); d.appendChild(box);
  return d;
}
var inCity=null, inCityParent="eth";
function openCity(name){
  var city=cityFor(name); if(!city) return false;
  var P=byId(city.parent)||current;
  inCity=citySlug(name); inCityParent=(byId(city.parent)||current).id;
  indexCityCells(city);
  var host=$("cityBody"); host.innerHTML="";
  $("cityBackLabel").textContent="Quay lại bản đồ "+P.name;

  /* chủ đề riêng của thành phố */
  var W=$("cityWrap"), TH=city.theme;
  if(TH){
    W.dataset.brand=TH.brand||"1";
    W.style.setProperty("--acc",TH.acc); W.style.setProperty("--acc-t",TH.accT);
    W.style.setProperty("--pacc",P.acc);
  } else { delete W.dataset.brand; W.style.removeProperty("--acc");
    W.style.removeProperty("--acc-t"); W.style.removeProperty("--pacc"); }

  var flow=el("div","flow");

  /* nước mẹ */
  var top=el("div","node top");
  top.innerHTML='<span class="badge"><span class="tno">①</span>'+P.cap.replace(/^Layer 1 · /,"Layer 1 — ")+'</span>'+
    '<div class="t">'+P.name+'</div><div class="s">Nền chủ quyền: quyết toán, bảo mật và kinh tế gốc</div>';
  flow.appendChild(top);
  /* bộ quy chuẩn nằm giữa nước mẹ và thành phố */
  if(city.standard){
    flow.appendChild(arrowEl(city.standard.linkUp||"settlement + bảo mật"));
    var std=el("div","node std"); std.setAttribute("role","button"); std.tabIndex=0;
    std.dataset.cell=city.standard.n; std.dataset.sect="standard"; std.dataset.city=city.n;
    std.dataset.fallback=city.standard.s;
    std.innerHTML='<span class="badge"><span class="tno">②</span>'+city.standard.badge+'</span>'+
      '<div class="t">'+city.standard.n+'</div><div class="s">'+city.standard.s+'</div>';
    flow.appendChild(std);
    flow.appendChild(arrowEl(city.standard.linkDown||"xây theo tiêu chuẩn"));
  } else {
    flow.appendChild(arrowEl(LINKWORD[P.id]||"nối vào"));
  }

  /* khung thành phố */
  var frame=el("div","city-frame");
  var head=el("div","city-head");
  var crest=el("div","crest2");
  crest.innerHTML=(TH&&TH.mark)?mark(TH.mark):ico(L2ICON[P.id]||"city");
  head.appendChild(crest);
  var h2=el("h2"); h2.textContent=city.n; head.appendChild(h2);
  var q=el("div","quote"); q.textContent="③ “Đất thành phố” · lớp thực thi"; head.appendChild(q);
  var ip=el("p"); ip.textContent=city.intro; head.appendChild(ip);
  frame.appendChild(head);

  /* móc L2BEAT — hồ sơ tự trị, đặt ngay dưới tên thành phố vì nó
     trả lời câu hỏi đầu tiên: thành phố này tự trị đến đâu. */
  if(window.KT_L2B) window.KT_L2B.section(frame,city.n,P.id);

  /* bộ máy vận hành — đặt ngay dưới tên thành phố */
  if(city.machine){
    var sm=el("div","city-sect");
    var mbox=el("div","machine");
    mbox.appendChild(sectLabelEl("③","Bộ máy vận hành L2"));
    var mg=el("div","mgrid");
    city.machine.items.forEach(function(m){
      mg.appendChild(cellEl(m,["#fff","rgba(255,255,255,.13)"],city.n,"machine"));
    });
    mbox.appendChild(mg);
    if(city.machine.foot){
      var mf=el("p","mnote");
      mf.innerHTML='<span>↧</span><span>'+city.machine.foot+'</span>';
      mbox.appendChild(mf);
    }
    if(city.machine.note){
      var mn=el("p","layer-note"); mn.style.margin="0 0 13px"; mn.textContent=city.machine.note;
      sm.appendChild(mn);
    }
    sm.appendChild(mbox);
    frame.appendChild(sm);
  }

  /* hạ tầng đô thị */
  var s1=el("div","city-sect");
  var l1=sectLabelEl("④","Hạ tầng đô thị · cổng giao tiếp"); s1.appendChild(l1);
  if(city.generic){ var gn=el("div","genericnote"); gn.textContent=city.intro; s1.insertBefore(gn,l1); }
  var fg=el("div","flow-grid");
  city.infra.forEach(function(c){
    var colu=el("div"), cur=c;
    colu.appendChild(cellEl(cur,KIND.infra,city.n,"infra"));
    while(cur.to){
      var ma=el("div","mini-arrow");
      ma.innerHTML='<span class="ln"></span>'+(cur.edge?'<span class="lab">'+cur.edge+'</span>':"")+
                   '<span class="ln"></span><span class="ar">▼</span>';
      colu.appendChild(ma);
      cur=cur.to;
      colu.appendChild(cellEl(cur,KIND.infra,city.n,"infra"));
    }
    fg.appendChild(colu);
  });
  s1.appendChild(fg); frame.appendChild(s1);

  /* ⑤ kinh tế & cư dân */
  if(city.econ){
    var se=el("div","city-sect");
    se.appendChild(sectLabelEl("⑤","Kinh tế & cư dân"));
    if(city.econ.note){ var en=el("p","layer-note"); en.textContent=city.econ.note; se.appendChild(en); }
    se.appendChild(districtsEl(city.econ.groups,city.n,"econ",KIND.band));
    frame.appendChild(se);
  }

  /* ⑥ công trình · các ngành */
  var s2=el("div","city-sect");
  s2.appendChild(sectLabelEl("⑥","Công trình · các ngành"));
  if(city.districts){
    if(city.districts.note){ var dn2=el("p","layer-note"); dn2.textContent=city.districts.note; s2.appendChild(dn2); }
    s2.appendChild(districtsEl(city.districts.groups,city.n,"org",KIND.app));
  } else {
    var og=el("div","org-grid");
    (city.orgs||[]).forEach(function(o){ og.appendChild(cellEl(o,KIND.app,city.n,"org")); });
    s2.appendChild(og);
  }
  frame.appendChild(s2);

  /* cổng thành */
  var s3=el("div","city-sect");
  var l3=sectLabelEl("⑦","Cổng thành · quảng trường"); s3.appendChild(l3);
  var gt=el("button","gate"); gt.type="button"; gt.style.cursor="pointer";
  gt.dataset.cell=city.gate.n; gt.dataset.sect="gate"; gt.dataset.city=city.n;
  gt.dataset.fallback=city.gate.note||"";
  var gi=el("div","gi"); gi.innerHTML=ico("gate"); gt.appendChild(gi);
  var gtt=el("div","t"); gtt.textContent=city.gate.n; gt.appendChild(gtt);
  var gq=el("div","q"); gq.textContent="“"+city.gate.q+"”"; gt.appendChild(gq);
  var gnn=el("p","note"); gnn.textContent=city.gate.note; gt.appendChild(gnn);
  var tb=el("div","tabs");
  city.gate.tabs.forEach(function(t){ var sp=el("span"); sp.textContent=t; tb.appendChild(sp); });
  if(city.gate.foot){ var gfo=el("p","note"); gfo.style.cssText="margin:12px auto 0;max-width:52ch";
    gfo.textContent=city.gate.foot; gt.appendChild(gfo); }
  gt.appendChild(tb); s3.appendChild(gt); frame.appendChild(s3);

  var miss=[];
  if(!city.standard) miss.push("②");
  if(!city.machine) miss.push("③ bộ máy");
  if(!city.econ) miss.push("⑤");
  if(!city.districts) miss.push("⑥ chia ngành");
  if(miss.length){
    var mw=el("p","layer-note warn"); mw.style.margin="14px 16px 16px";
    mw.textContent="Thành phố này chưa dựng đủ bảy tầng. Còn thiếu: tầng "+miss.join(", ")+
      ". Khung bảy tầng là mẫu chuẩn — số tầng bị khuyết cho thấy chỗ chưa có dữ liệu riêng, không phải chỗ thành phố không có.";
    frame.appendChild(mw);
  }
  flow.appendChild(frame);
  if(TH&&TH.note){ var bn=el("p","brandnote"); bn.textContent=TH.note; flow.appendChild(bn); }
  flow.appendChild(arrowEl("đi vào"));
  var user=el("div","node");
  user.innerHTML='<div class="t">Người dùng</div>'+
    '<div class="s">Tương tác với ứng dụng, sở hữu tài sản, trả phí — và chính họ khép kín vòng tuần hoàn</div>';
  flow.appendChild(user);
  host.appendChild(flow);

  /* vòng tuần hoàn */
  var loop=el("div","loop");
  var lh=el("h3"); lh.textContent="Vòng tuần hoàn sinh thái"; loop.appendChild(lh);
  var ol=el("ol");
  (city.loop||LOOPS[P.id]||LOOPS.eth).forEach(function(t,i){
    var li=el("li"); var b=el("b"); b.textContent=(i+1);
    var sp=el("span"); sp.textContent=t;
    li.appendChild(b); li.appendChild(sp); ol.appendChild(li);
  });
  loop.appendChild(ol);
  var ret=el("div","ret");
  ret.innerHTML='<span>↻</span><span>'+(city.loopNote||RETURN_NOTE[P.id]||RETURN_NOTE.eth)+'</span>';
  loop.appendChild(ret);
  host.appendChild(loop);

  $("cityWrap").hidden=false;
  document.querySelector(".main > .wrap").hidden=true;
  $("chips").hidden=true;
  $("barTitle").textContent=P.name+" › "+city.n;
  window.location.hash=P.id+"/"+inCity;
  window.scrollTo({top:0,behavior:"auto"});
  return true;
}
function closeCity(){
  if(!inCity) return;
  inCity=null;
  $("cityWrap").hidden=true;
  document.querySelector(".main > .wrap").hidden=false;
  $("chips").hidden=false;
  $("barTitle").textContent=current.name;
  window.location.hash=current.id;
  window.scrollTo({top:0,behavior:"auto"});
}
$("cityBack").addEventListener("click",closeCity);
$("rankBack").addEventListener("click",closeRanking);
$("openRank").addEventListener("click",function(){
  if(inCity) { inCity=null; $("cityWrap").hidden=true; }
  openRanking(); if(window.innerWidth<=900) setNav("full");
});

/* ══ scroll spy ═══════════════════════════════════════ */
function onScroll(){
  var cur=null;
  document.querySelectorAll("[data-layer]").forEach(function(s){
    if(s.hidden) return;
    if(s.getBoundingClientRect().top<=140) cur=s.dataset.layer;
  });
  [].slice.call($("secList").children).forEach(function(b){
    b.dataset.on=(b.dataset.jump===cur)?"1":"0";
  });
}
window.addEventListener("scroll",onScroll,{passive:true});
window.addEventListener("resize",onScroll);
function route(){
  var raw=window.location.hash.slice(1);
  if(raw==="rank"){ if(!current) render("eth"); if(!inRank) openRanking(); return; }
  if(inRank){ inRank=false; $("rankWrap").hidden=true;
    document.querySelector(".main > .wrap").hidden=false; $("chips").hidden=false; }
  var parts=raw.split("/");
  var cid=byId(parts[0])?parts[0]:"eth";
  if(!current || current.id!==cid){ if(inCity){inCity=null; $("cityWrap").hidden=true;
    document.querySelector(".main > .wrap").hidden=false; $("chips").hidden=false;} render(cid); }
  if(parts[1]){
    var want=parts[1];
    if(inCity!==want){
      var found=null;
      current.tiers.forEach(function(T){ if(T.kind!=="l2") return;
        T.groups.forEach(function(G){ G.items.forEach(function(i){
          if(!i.more && citySlug(i.n)===want) found=i.n; }); }); });
      if(found) openCity(found); else if(inCity) closeCity();
    }
  } else if(inCity){ closeCity(); }
}
window.addEventListener("hashchange",route);

/* legend */
var lg=$("legend");
LEGEND.forEach(function(p){
  var row=el("div"), i=el("i"); i.style.background=p[1]; i.innerHTML=ico(p[2]);
  var s=el("span"); s.textContent=p[0];
  row.appendChild(i); row.appendChild(s); lg.appendChild(row);
});

computeRanking();
renderCountryList();
route();
})();
