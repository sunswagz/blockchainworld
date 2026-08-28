/* ═══════════════════════════════════════════════════════
   TRANG · Soi quyền lực: khung bảy tiêu chí và hồ sơ

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

function vKhung(K){
  const { DANHSACH, SOI, THANG, TIEUCHI, el, esc, go, head, mucBC, thanhBC } = K;
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

function veKhoi(K, k){
  const { el, esc } = K;
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

function vSoi(K, id, mucId){
  const { CHAIN, SOI, TIEUCHI, el, esc, go, head, moMuc, mucBC, render, save, state, svg, thanhBC } = K;
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
      (m.khoi||[]).forEach(k=>{ const n=veKhoi(K, k); if(n) body.appendChild(n); });
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

T.vKhung = vKhung;
T.veKhoi = veKhoi;
T.vSoi = vSoi;
})();
