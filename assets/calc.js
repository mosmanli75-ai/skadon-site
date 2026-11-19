/* ═══ калькулятор ═══ */
document.addEventListener('DOMContentLoaded', function(){
  const D = window.CALC; if(!D) return;
  const IC = window.CALCICONS || {}, OIC = window.CALCOBJICONS || {};
  const $ = id => document.getElementById(id);
  const money = n => Math.round(n).toLocaleString('ru-RU') + ' ₽';
  const num   = n => Math.round(n).toLocaleString('ru-RU');
  const svg   = s => s ? `<svg viewBox="0 0 120 94" aria-hidden="true">${s}</svg>` : '';

  /* тип объекта → схема */
  function objIcon(name){
    const n = name.toLowerCase();
    if(n.indexOf('дом') > -1)      return OIC.house;
    if(n.indexOf('коммерц') > -1)  return OIC.shop;
    if(n.indexOf('отель') > -1)    return OIC.hotel;
    if(n.indexOf('завод') > -1 || n.indexOf('ангар') > -1) return OIC.plant;
    if(n.indexOf('многоэтаж') > -1)return OIC.tower;
    return OIC.big;
  }

  /* ── состояние ── */
  const st = { obj: 0, sel: [], vol: {}, addons: {}, region: 0, nds: 0 };

  /* ── шаг 1 · тип объекта ── */
  $('objTypes').innerHTML = D.objects.map((o,i) =>
    `<button class="copt${i===0?' on':''}" data-i="${i}">
       ${svg(objIcon(o[0]))}<b>${o[0]}</b>
     </button>`).join('');

  /* ── шаг 2 · конструкции ── */
  $('works').innerHTML = D.works.map((w,i) =>
    `<button class="cwork" data-i="${i}" aria-pressed="false">
       ${svg(IC[w.i])}<b>${w.n}</b><em>${w.u}</em>
     </button>`).join('');

  /* ── шаг 3 · объёмы по выбранным ── */
  function renderVols(){
    const box = $('vols');
    if(!st.sel.length){ box.innerHTML = ''; $('volsWrap').hidden = true; return; }
    $('volsWrap').hidden = false;
    box.innerHTML = st.sel.map(i => {
      const w = D.works[i];
      return `<label class="cvol">
        <span class="cvol-n">${w.n}</span>
        <span class="cvol-f">
          <input type="number" min="0" step="1" inputmode="decimal"
                 data-i="${i}" value="${st.vol[i] || ''}" placeholder="0">
          <em>${w.u}</em>
        </span>
      </label>`;
    }).join('');
    box.querySelectorAll('input').forEach(el =>
      el.addEventListener('input', function(){
        const v = parseFloat(this.value.replace(',', '.'));
        st.vol[this.dataset.i] = v > 0 ? v : null;
        calc();
      }));
  }

  /* ── шаг 4 · надбавки: один общий набор ── */
  function renderAddons(){
    const keys = [];
    Object.keys(D.addons).forEach(k => {
      if(st.sel.some(i => D.works[i].a[k] !== undefined) && keys.indexOf(k) < 0) keys.push(k);
    });
    $('addons').innerHTML = keys.length
      ? keys.map(k =>
        `<label class="cchk${st.addons[k]?' on':''}">
           <input type="checkbox" data-k="${k}"${st.addons[k]?' checked':''}>
           <span class="cchk-n">${D.addons[k]}</span>
         </label>`).join('')
      : '<p class="chint">Выберите конструкцию — появятся позиции, которые можно взять на нас.</p>';
    $('addons').querySelectorAll('input').forEach(el =>
      el.addEventListener('change', function(){
        st.addons[this.dataset.k] = this.checked;
        this.closest('.cchk').classList.toggle('on', this.checked);
        calc();
      }));
  }

  /* ── шаг 5 · регион ── */
  $('region').innerHTML = D.regions.map((r,i) => `<option value="${i}">${r[0]}</option>`).join('');

  /* ── расчёт ── */
  let LAST = null;

  function unitPrice(i){
    const w = D.works[i];
    const objK = D.objects[st.obj] ? D.objects[st.obj][1] : 1;
    const regK = D.regions[st.region] ? D.regions[st.region][1] : 1;
    let sum = w.b;
    for(const k in w.a){
      if(!st.addons[k]) continue;
      let v = w.a[k];
      if(k.indexOf('жиль') > -1) v *= regK;   // жильё и питание зависят от региона
      sum += v;
    }
    sum *= objK;
    if(st.nds) sum *= D.nds;
    return sum;
  }

  function calc(){
    const rows = st.sel.map(i => {
      const w = D.works[i], p = unitPrice(i), v = st.vol[i] || null;
      return { n: w.n, u: w.u, price: p, vol: v, sum: v ? p*v : null, spread: (w.s || D.spread) };
    });

    const inc = [];
    Object.keys(D.addons).forEach(k => { if(st.addons[k] && inc.indexOf(D.addons[k]) < 0) inc.push(D.addons[k]); });

    const withVol = rows.filter(r => r.sum !== null);
    const total   = withVol.reduce((a, r) => a + r.sum, 0);
    const sp      = (rows.length ? Math.max.apply(null, rows.map(r => r.spread)) : D.spread) / 100;

    LAST = {
      obj: D.objects[st.obj] ? D.objects[st.obj][0] : '',
      region: D.regions[st.region] ? D.regions[st.region][0] : '',
      nds: !!st.nds, rows: rows, inc: inc,
      total: total, lo: total*(1-sp), hi: total*(1+sp), sp: sp*100,
      allVol: rows.length > 0 && withVol.length === rows.length
    };

    /* пусто */
    if(!rows.length){
      $('result').hidden = true;
      $('empty').hidden = false;
      return;
    }
    $('result').hidden = false;
    $('empty').hidden = true;

    /* список работ */
    $('lines').innerHTML = rows.map(r => `
      <div class="cline">
        <span class="cl-n">${r.n}</span>
        <span class="cl-u">${r.vol ? num(r.vol) + ' ' + r.u : '<i>объём не указан</i>'}</span>
        <span class="cl-p">${money(r.price)}<em>/${r.u}</em></span>
        <span class="cl-s">${r.sum !== null ? money(r.sum) : '—'}</span>
      </div>`).join('');

    /* итог */
    if(withVol.length){
      $('sumTitle').textContent = withVol.length === rows.length
        ? 'Итого по объекту' : 'Итого по заполненным позициям';
      $('sum').innerHTML = money(LAST.lo) + ' – ' + money(LAST.hi);
      $('sumHint').textContent = 'Вилка ±' + LAST.sp.toFixed(0) + '% · ' + (st.nds ? 'с НДС' : 'без НДС');
    } else {
      $('sumTitle').textContent = 'Цена за единицу';
      $('sum').innerHTML = rows.length === 1
        ? money(rows[0].price * (1 - sp)) + ' – ' + money(rows[0].price * (1 + sp))
        : '—';
      $('sumHint').textContent = 'Укажите объёмы — посчитаем итог по объекту';
    }

    $('included').innerHTML = ['работа'].concat(inc).concat([st.nds ? 'с НДС' : 'без НДС'])
      .map(x => `<li>${x}</li>`).join('');
    $('note').textContent = D.note;
    $('meta').textContent = LAST.obj + ' · ' + LAST.region;
  }

  /* ── события ── */
  $('objTypes').addEventListener('click', e => {
    const b = e.target.closest('.copt'); if(!b) return;
    st.obj = +b.dataset.i;
    $('objTypes').querySelectorAll('.copt').forEach(x => x.classList.remove('on'));
    b.classList.add('on'); calc();
  });

  $('works').addEventListener('click', e => {
    const b = e.target.closest('.cwork'); if(!b) return;
    const i = +b.dataset.i, at = st.sel.indexOf(i);
    if(at > -1){ st.sel.splice(at, 1); delete st.vol[i]; }
    else st.sel.push(i);
    b.classList.toggle('on', at < 0);
    b.setAttribute('aria-pressed', at < 0 ? 'true' : 'false');
    $('selN').textContent = st.sel.length ? 'ВЫБРАНО: ' + st.sel.length : '';
    renderVols(); renderAddons(); calc();
  });

  $('region').addEventListener('change', function(){ st.region = +this.value; calc(); });
  $('nds').addEventListener('change', function(){ st.nds = +this.value; calc(); });

  $('upd').textContent = D.updated
    ? 'Расценки обновлены ' + D.updated.split('-').reverse().join('.') +
      '. Заполнены не все направления — по остальным работам звоните.'
    : '';

  /* ═══════════ ЛИСТ РАСЧЁТА: логотип, canvas, PDF, фото ═══════════ */

  /* конечная поза тессеракта — та, на которой останавливается анимация */
  const LOGO = (function(){
    const Q = Math.PI/2, T1 = 2, T2 = 3, T3 = 5;
    const adj = []; for(let v=0;v<16;v++) adj[v]=[0,1,2,3].map(k => v^(1<<k));
    const used = {}, stk = [0], out = [];
    const key = (a,b) => Math.min(a,b)*16 + Math.max(a,b);
    while(stk.length){
      const v = stk[stk.length-1]; let n = -1;
      for(let i=0;i<4;i++){ const w = adj[v][i]; if(!used[key(v,w)]){ n = w; break; } }
      if(n < 0) out.push(stk.pop()); else { used[key(v,n)] = 1; stk.push(n); }
    }
    const CIRC = out.reverse();
    const VTX = []; for(let v=0;v<16;v++) VTX.push([v&1?1:-1, v&2?1:-1, v&4?1:-1, v&8?1:-1]);
    function project(S){
      const a1=Q*T1, a2=Q*T2, a3=Q*T3, P=[], K=[];
      for(let v=0;v<16;v++){
        const a = VTX[v]; let x=a[0],y=a[1],z=a[2],w=a[3],c,s,nx,nw,nz;
        c=Math.cos(a1);s=Math.sin(a1); nx=x*c-y*s; y=x*s+y*c; x=nx;
        c=Math.cos(a2);s=Math.sin(a2); nx=x*c-w*s; nw=x*s+w*c; x=nx; w=nw;
        c=Math.cos(a3);s=Math.sin(a3); nz=z*c-w*s; nw=z*s+w*c; z=nz; w=nw;
        const k4=2.75/(2.75-w), X=x*k4, Y=y*k4, Z=z*k4, k3=4.4/(4.4-Z);
        P.push([X*k3*S, Y*k3*S]); K.push(k4*k3);
      }
      return {P:P, K:K};
    }
    let maxR = 0;
    const pr1 = project(1);
    for(let k=0;k<16;k++) maxR = Math.max(maxR, Math.hypot(pr1.P[k][0], pr1.P[k][1]));
    return function(g, cx, cy, size){
      const S = (size/2) / maxR, pr = project(S), P = pr.P, K = pr.K;
      let kmin = 1e9, kmax = -1e9;
      for(let i=0;i<16;i++){ if(K[i]<kmin) kmin=K[i]; if(K[i]>kmax) kmax=K[i]; }
      const span = Math.max(1e-6, kmax-kmin);
      g.save(); g.translate(cx, cy); g.lineCap = 'round'; g.lineJoin = 'round';
      for(let i=0;i<CIRC.length-1;i++){
        const a = P[CIRC[i]], b = P[CIRC[i+1]];
        const d = ((K[CIRC[i]]+K[CIRC[i+1]])/2 - kmin)/span;
        const col = [13+(18-13)*(1-d), 23+(49-23)*(1-d), 22+(47-22)*(1-d)];
        g.globalAlpha = 0.28 + 0.72*d;
        g.lineWidth = (0.9 + 1.7*d) * (size/100);
        g.strokeStyle = 'rgb('+(col[0]|0)+','+(col[1]|0)+','+(col[2]|0)+')';
        g.beginPath(); g.moveTo(a[0],a[1]); g.lineTo(b[0],b[1]); g.stroke();
      }
      g.restore(); g.globalAlpha = 1;
    };
  })();

  const F = 'system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif';

  /* лист A4 на canvas, 150 dpi */
  function sheet(){
    const W = 1240, H = 1754, M = 96;
    const cv = document.createElement('canvas');
    cv.width = W; cv.height = H;
    const g = cv.getContext('2d');
    g.fillStyle = '#fff'; g.fillRect(0,0,W,H);
    g.textBaseline = 'alphabetic';

    /* шапка */
    LOGO(g, M + 46, M + 46, 92);
    g.fillStyle = '#0D1716'; g.font = '600 34px ' + F;
    g.fillText('TesseracT Group', M + 116, M + 40);
    g.fillStyle = '#4A5957'; g.font = '18px ' + F;
    g.fillText('Предварительный расчёт стоимости работ', M + 116, M + 70);

    const d = new Date();
    const dd = ('0'+d.getDate()).slice(-2) + '.' + ('0'+(d.getMonth()+1)).slice(-2) + '.' + d.getFullYear();
    g.textAlign = 'right'; g.fillStyle = '#4A5957'; g.font = '17px ' + F;
    g.fillText(dd, W - M, M + 40);
    g.textAlign = 'left';

    let y = M + 120;
    g.strokeStyle = '#0D1716'; g.globalAlpha = .5; g.lineWidth = 1.4;
    g.beginPath(); g.moveTo(M, y); g.lineTo(W - M, y); g.stroke(); g.globalAlpha = 1;

    /* параметры */
    y += 44;
    g.fillStyle = '#4A5957'; g.font = '15px ' + F;
    g.fillText('ОБЪЕКТ', M, y);
    g.fillText('РЕГИОН', M + 400, y);
    g.fillText('РАСЧЁТ', M + 800, y);
    y += 28;
    g.fillStyle = '#0D1716'; g.font = '500 20px ' + F;
    g.fillText(LAST.obj, M, y);
    g.fillText(LAST.region, M + 400, y);
    g.fillText(LAST.nds ? 'с НДС' : 'без НДС', M + 800, y);

    /* таблица */
    y += 56;
    g.fillStyle = '#4A5957'; g.font = '15px ' + F;
    g.fillText('РАБОТА', M, y);
    g.textAlign = 'right';
    g.fillText('ОБЪЁМ', M + 640, y);
    g.fillText('ЦЕНА ЗА ЕД.', M + 856, y);
    g.fillText('СУММА', W - M, y);
    g.textAlign = 'left';
    y += 14;
    g.strokeStyle = '#0D1716'; g.globalAlpha = .25;
    g.beginPath(); g.moveTo(M, y); g.lineTo(W - M, y); g.stroke(); g.globalAlpha = 1;

    LAST.rows.forEach(function(r){
      y += 42;
      g.fillStyle = '#0D1716'; g.font = '19px ' + F;
      let name = r.n;
      while(g.measureText(name).width > 520 && name.length > 8) name = name.slice(0, -2);
      if(name !== r.n) name += '…';
      g.fillText(name, M, y);
      g.textAlign = 'right';
      g.fillStyle = '#2A3735'; g.font = '18px ' + F;
      g.fillText(r.vol ? num(r.vol) + ' ' + r.u : '—', M + 640, y);
      g.fillText(money(r.price), M + 856, y);
      g.fillStyle = '#0D1716'; g.font = '500 19px ' + F;
      g.fillText(r.sum !== null ? money(r.sum) : '—', W - M, y);
      g.textAlign = 'left';
      g.strokeStyle = '#0D1716'; g.globalAlpha = .12;
      g.beginPath(); g.moveTo(M, y + 14); g.lineTo(W - M, y + 14); g.stroke(); g.globalAlpha = 1;
    });

    /* итог */
    y += 70;
    g.fillStyle = '#4A5957'; g.font = '15px ' + F;
    g.fillText(LAST.allVol ? 'ИТОГО ПО ОБЪЕКТУ' : 'ИТОГО ПО ЗАПОЛНЕННЫМ ПОЗИЦИЯМ', M, y);
    y += 44;
    g.fillStyle = '#0D1716'; g.font = '600 40px ' + F;
    g.fillText(LAST.total > 0 ? money(LAST.lo) + ' – ' + money(LAST.hi) : '—', M, y);
    y += 30;
    g.fillStyle = '#4A5957'; g.font = '16px ' + F;
    g.fillText('Вилка ±' + LAST.sp.toFixed(0) + '%, цены ' + (LAST.nds ? 'с НДС' : 'без НДС'), M, y);

    /* что входит */
    y += 54;
    g.fillStyle = '#4A5957'; g.font = '15px ' + F;
    g.fillText('В ЦЕНУ ВХОДИТ', M, y);
    y += 30;
    g.fillStyle = '#0D1716'; g.font = '18px ' + F;
    const inc = ['работа'].concat(LAST.inc).join(' · ');
    let line = '', yy = y;
    inc.split(' · ').forEach(function(part, i){
      const t = line ? line + ' · ' + part : part;
      if(g.measureText(t).width > W - 2*M){ g.fillText(line, M, yy); yy += 28; line = part; }
      else line = t;
    });
    if(line) g.fillText(line, M, yy);
    y = yy;

    /* оговорка */
    y += 60;
    g.fillStyle = '#4A5957'; g.font = '16px ' + F;
    const dis = 'Расчёт предварительный. Точная цена определяется по проекту, объёмам и графику работ. '
              + 'Не является публичной офертой.';
    let ln = '';
    dis.split(' ').forEach(function(wd){
      const t = ln ? ln + ' ' + wd : wd;
      if(g.measureText(t).width > W - 2*M){ g.fillText(ln, M, y); y += 26; ln = wd; }
      else ln = t;
    });
    if(ln) g.fillText(ln, M, y);

    /* подвал */
    const fy = H - M;
    g.strokeStyle = '#0D1716'; g.globalAlpha = .25; g.lineWidth = 1.2;
    g.beginPath(); g.moveTo(M, fy - 52); g.lineTo(W - M, fy - 52); g.stroke(); g.globalAlpha = 1;
    if(D.updated){
      g.fillStyle = '#8B9C99'; g.font = '15px ' + F;
      g.fillText('Расценки от ' + D.updated.split('-').reverse().join('.'), M, fy - 68);
    }
    g.fillStyle = '#0D1716'; g.font = '500 18px ' + F;
    g.fillText('skadon.ru', M, fy - 18);
    g.fillStyle = '#4A5957'; g.font = '18px ' + F;
    g.textAlign = 'center'; g.fillText('+7 928 146-01-11', W/2, fy - 18);
    g.textAlign = 'right';  g.fillText('mustafa@osmanli.ru', W - M, fy - 18);
    g.textAlign = 'left';
    return cv;
  }

  /* JPEG → однослойный PDF A4 (без библиотек) */
  function pdfFromJpeg(bytes, pw, ph){
    const W = 595.28, H = 841.89;
    const chunks = [], offs = [];
    let len = 0;
    const push = s => {
      const b = typeof s === 'string'
        ? Uint8Array.from(s, c => c.charCodeAt(0) & 0xff) : s;
      chunks.push(b); len += b.length; return len;
    };
    push('%PDF-1.4\n%\xE2\xE3\xCF\xD3\n');
    const obj = (n, body) => { offs[n] = len; push(n + ' 0 obj\n' + body + '\nendobj\n'); };

    obj(1, '<< /Type /Catalog /Pages 2 0 R >>');
    obj(2, '<< /Type /Pages /Kids [3 0 R] /Count 1 >>');
    obj(3, '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ' + W.toFixed(2) + ' ' + H.toFixed(2) +
           '] /Resources << /XObject << /Im0 5 0 R >> >> /Contents 4 0 R >>');
    const cont = 'q ' + W.toFixed(2) + ' 0 0 ' + H.toFixed(2) + ' 0 0 cm /Im0 Do Q';
    obj(4, '<< /Length ' + cont.length + ' >>\nstream\n' + cont + '\nendstream');

    offs[5] = len;
    push('5 0 obj\n<< /Type /XObject /Subtype /Image /Width ' + pw + ' /Height ' + ph +
         ' /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ' +
         bytes.length + ' >>\nstream\n');
    push(bytes);
    push('\nendstream\nendobj\n');

    const xref = len;
    let x = 'xref\n0 6\n0000000000 65535 f \n';
    for(let i=1;i<=5;i++) x += ('0000000000' + offs[i]).slice(-10) + ' 00000 n \n';
    push(x);
    push('trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n' + xref + '\n%%EOF\n');

    let total = 0; chunks.forEach(c => total += c.length);
    const all = new Uint8Array(total); let p = 0;
    chunks.forEach(c => { all.set(c, p); p += c.length; });
    return new Blob([all], {type: 'application/pdf'});
  }

  function fname(ext){
    const d = new Date();
    return 'raschet-tesseract-' + d.getFullYear() + ('0'+(d.getMonth()+1)).slice(-2) +
           ('0'+d.getDate()).slice(-2) + '.' + ext;
  }

  function deliver(blob, name){
    const file = new File([blob], name, {type: blob.type});
    if(navigator.canShare && navigator.canShare({files: [file]})){
      navigator.share({files: [file], title: 'Расчёт · TesseracT Group'}).catch(function(){});
      return;
    }
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name; document.body.appendChild(a); a.click();
    setTimeout(function(){ URL.revokeObjectURL(url); a.remove(); }, 800);
  }

  function ready(){
    if(!LAST || !LAST.rows.length){ alert('Сначала выберите конструкции.'); return false; }
    return true;
  }

  $('btnPdf').addEventListener('click', function(){
    if(!ready()) return;
    const cv = sheet();
    const b64 = cv.toDataURL('image/jpeg', 0.92).split(',')[1];
    const bin = atob(b64), bytes = new Uint8Array(bin.length);
    for(let i=0;i<bin.length;i++) bytes[i] = bin.charCodeAt(i);
    deliver(pdfFromJpeg(bytes, cv.width, cv.height), fname('pdf'));
    sendCopy('pdf');
  });

  $('btnPng').addEventListener('click', function(){
    if(!ready()) return;
    sheet().toBlob(function(b){ deliver(b, fname('png')); }, 'image/png');
    sendCopy('png');
  });

  /* копия расчёта нам */
  let sent = false;
  function sendCopy(how){
    if(sent || !LAST) return; sent = true;
    setTimeout(function(){ sent = false; }, 20000);
    try{
      fetch('/api/lead', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          kind: 'calc', how: how, page: location.pathname,
          obj: LAST.obj, region: LAST.region, nds: LAST.nds,
          rows: LAST.rows.map(r => ({n: r.n, u: r.u, vol: r.vol, price: Math.round(r.price), sum: r.sum ? Math.round(r.sum) : null})),
          inc: LAST.inc, lo: Math.round(LAST.lo), hi: Math.round(LAST.hi)
        })
      }).catch(function(){});
    }catch(e){}
  }

  renderVols(); renderAddons(); calc();
});
