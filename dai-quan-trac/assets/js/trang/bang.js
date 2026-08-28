/* ═══════════════════════════════════════════════════════
   TRANG · Năm bảng phân tích: mạch · đồng hồ · cấp độ · kịch bản · la bàn

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

function vChain(K){
  const { CHAIN, DEM, LVNAME, el, esc, head, lvOf, railChain } = K;
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

function vGauges(K){
  const { DO, DODAC, DO_LUC, GAUGES, LEVELS, LVLS, MAU, OI_GIO, capDo, demDen, den, el, esc, gGG, gioDo, head, nguonDen, render, renderNav, sGG, save, soDo, spark, tuoiDo } = K;
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

function vLevels(K){
  const { LEVELS, RANH, SO, capDo, el, esc, head } = K;
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

function vScen(K){
  const { KB, SCEN, el, esc, head } = K;
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

function vCompass(K){
  const { COMPASS, chuThe, el, esc, go, head, state } = K;
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

T.vChain = vChain;
T.vGauges = vGauges;
T.vLevels = vLevels;
T.vScen = vScen;
T.vCompass = vCompass;
})();
