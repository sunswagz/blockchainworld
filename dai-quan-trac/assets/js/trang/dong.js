/* ═══════════════════════════════════════════════════════
   TRANG · Dòng chảy · tin tức · chiến trường

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

function vTin(K){
  const { CHAIN, MUC_MAU, MUC_TEN, TIN, TIN_LUC, chuThe, el, esc, gioDo, ngayGon, state } = K;
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

function vFlow(K){
  const { GAUGES, LEVELS, LVNAME, TH, THEATERS, TIN, ago, capDo, chuThe, demDen, den, el, esc, head, nguonDen, railSignal, render, sigCT, state } = K;
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
  if(!THEATERS.length){ if(TIN.length) w.appendChild(vTin(K)); return w; }
  const lvl=capDo(), dm=demDen();
  const st=el('div','trang-thai'+(lvl?' c'+lvl:''));
  let bulbs='';
  GAUGES.forEach(g=>{ const lv=den(g.id), ng=nguonDen(g.id);
    bulbs+='<i class="'+lv+(ng==='tay'?' tay':'')+'" title="'+esc(g.t)+' — '+LVNAME[lv]+
      (ng==='tay'?' (bạn đặt)':ng==='tu'?' (tự đo)':'')+'"></i>'; });
  st.innerHTML=
    '<div class="ts-cap"><span class="ts-n">'+(lvl||'—')+'</span>'+
      '<span class="ts-t"><b>'+(lvl?esc(LEVELS[lvl-1].t):'CHƯA ĐỌC RA')+'</b>'+
      '<i>'+(lvl?dm.r+' đỏ · '+dm.y+' vàng · '+dm.g+' xanh':'chưa đèn nào sáng')+'</i></span></div>'+
    '<div class="ts-den">'+bulbs+'</div>'+
    '<a class="ts-go" href="#gauges" onclick="go(\'gauges\');return false">bảng đồng hồ →</a>';
  w.appendChild(st);

  if(TIN.length) w.appendChild(vTin(K));

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

function vTheater(K, id){
  const { DO, DODAC, LVLS, LVNAME, MAU, TH, chuThe, el, esc, gTH, go, head, railSignal, render, renderNav, sTH, save, scanAll, sigCT, state, tuoiDo } = K;
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

T.vTin = vTin;
T.vFlow = vFlow;
T.vTheater = vTheater;
})();
