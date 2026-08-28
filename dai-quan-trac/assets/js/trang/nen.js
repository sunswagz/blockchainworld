/* ═══════════════════════════════════════════════════════
   TRANG · Hồ sơ nền · bo mạch · bàn cờ · nguồn

   Tách khỏi app.js ngày 28/08/2026. Lý do là số: vỏ ứng dụng đi từ
   60 KB (12/08) lên 181 KB (28/08) — khoảng 30 KB mỗi tuần — trong
   khi ngưỡng của phiếu đo là 200 KB. Không có mỡ để cắt (28% app.js
   là chú thích tài liệu, SVG nội tuyến chỉ 1,1 KB), nên tách.

   KHÔNG đặt trong `assets/js/v/`: ở cả mười hai cung, thư mục đó là
   nơi BOT ghi dữ liệu. Mã view để lẫn vào đấy thì phiên sau sẽ tưởng
   file của mình do bot sinh ra và không dám sửa.

   ── K LÀ GÌ ───────────────────────────────────────────
   Thân hàm giữ NGUYÊN VĂN như lúc còn trong app.js. Thứ duy nhất
   thêm vào là một dòng rút gọn ở đầu mỗi hàm, lấy từ `K` đúng những
   gì hàm đó cần. Danh sách ấy do máy tính ra chứ không đoán tay —
   sót một cái là trang trắng, mà `node --check` không hề thấy.

   app.js dựng LẠI K mỗi lần gọi. Đó là điểm mấu chốt: dựng một lần
   lúc nạp thì `GAUGES` mãi là mảng của chủ thể mở trang đầu tiên, và
   bấm sang nước khác sẽ vẽ số của nước cũ — đúng lớp lỗi trộn chủ
   thể mà cung này đã trả giá một lần.

   Nạp SAU app.js trong index.html. app.js khởi động bất đồng bộ
   (`await load()`) nên tới lúc nó vẽ thì các tệp này đã nạp xong.
   ═══════════════════════════════════════════════════════ */
(function () {
const T = (window.DQT_TRANG = window.DQT_TRANG || {});

function vLib(K, id){
  const { LIB, el, esc, go, head } = K;
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

function veOCam(K, t){
  const { el, esc } = K;
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

function vBoMach(K, id){
  const { BOMACH, el, esc, go, head } = K;
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
    w.appendChild(veOCam(K, T));
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

function vBanCo(K){
  const { BANCO, el, esc, go, head } = K;
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

function vSrc(K){
  const { LEVELS, LIB, SOLIEU, ago, chuThe, el, esc, head, logCT, state } = K;
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

T.vLib = vLib;
T.veOCam = veOCam;
T.vBoMach = vBoMach;
T.vBanCo = vBanCo;
T.vSrc = vSrc;
})();
