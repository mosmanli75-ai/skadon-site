/* ═══ фон: чертежи, прорезанные в полотне ═══ */
(function(){
  const SETS={
    index:[
      {f:'baza-ankernaya', s:'right:-8vw;top:2vh;width:52vw',  o:.85,d:'-2s', p:1},
      {f:'grebenka',       s:'left:-4vw;top:17vh;width:30vw',  o:.5, d:'-11s',p:0},
      {f:'baza-plan-1-1',  s:'left:-6vw;top:60vh;width:31vw',  o:.7, d:'-18s',p:1},
      {f:'sloi-1-4',       s:'right:3vw;top:70vh;width:27vw',  o:.6, d:'-6s', p:0},
      {f:'uzel-2-ugol',    s:'left:33vw;top:92vh;width:34vw',  o:.68,d:'-22s',p:1}
    ],
    objects:[
      {f:'plan-etazha',    s:'left:-7vw;top:3vh;width:40vw',   o:.7, d:'-4s', p:1},
      {f:'armirovanie-kolonny', s:'right:-4vw;top:8vh;width:30vw', o:.68,d:'-14s',p:1},
      {f:'razrez-rostverk',s:'left:20vw;top:66vh;width:56vw',  o:.6, d:'-9s', p:0},
      {f:'vedomost',       s:'right:2vw;top:96vh;width:20vw',  o:.55,d:'-20s',p:1}
    ],
    group:[
      {f:'izometriya',     s:'right:-6vw;top:4vh;width:46vw',  o:.75,d:'-3s', p:1},
      {f:'vertik-sterzhni',s:'left:-3vw;top:20vh;width:22vw',  o:.6, d:'-13s',p:0},
      {f:'razrez-dd',      s:'left:26vw;top:74vh;width:30vw',  o:.62,d:'-19s',p:1},
      {f:'baza-plan-1-1',  s:'right:4vw;top:104vh;width:26vw', o:.6, d:'-8s', p:0}
    ],
    jobs:[
      {f:'uzel-2-ugol',    s:'right:-7vw;top:2vh;width:44vw',  o:.8, d:'-2s'},
      {f:'razrez-rostverk',s:'left:-8vw;top:26vh;width:46vw',  o:.6, d:'-10s'},
      {f:'grebenka',       s:'right:8vw;top:72vh;width:28vw',  o:.55,d:'-16s'},
      {f:'vertik-sterzhni',s:'left:6vw;top:98vh;width:20vw',   o:.6, d:'-6s'}
    ],
    dorogi:[
      {f:'doroga-perspektiva', s:'right:8vw;top:6vh;width:58vw',   o:1,  d:'-2s', p:1},
      {f:'dorozhnaya-odezhda', s:'left:-5vw;top:104vh;width:40vw', o:.9, d:'-14s',p:0},
      {f:'samosval',           s:'right:-2vw;top:186vh;width:40vw', o:.8, d:'-8s', p:1}
    ],
    prom:[
      {f:'razrez-dd',      s:'right:-5vw;top:1vh;width:38vw',  o:.78,d:'-2s', p:1},
      {f:'vertik-sterzhni',s:'left:-2vw;top:12vh;width:24vw',  o:.62,d:'-15s',p:1},
      {f:'armirovanie-kolonny', s:'left:30vw;top:78vh;width:32vw',o:.6,d:'-21s',p:0},
      {f:'sloi-1-4',       s:'right:6vw;top:106vh;width:26vw', o:.6, d:'-7s', p:1}
    ]
  };
  const PAGE=(location.pathname.split('/').pop()||'index.html').replace('.html','')||'index';
  const FRAGS=SETS[PAGE]||SETS.index;

  const bg=document.createElement('div'); bg.id='bg'; bg.setAttribute('aria-hidden','true');
  const inner=document.createElement('div'); inner.id='bgIn'; bg.appendChild(inner);
  const PULSE_ON={
    index:  {'baza-ankernaya':'0s','baza-plan-1-1':'-7s','sloi-1-4':'-13s'},
    objects:{'plan-etazha':'0s','armirovanie-kolonny':'-8s','vedomost':'-14s'},
    group:  {'izometriya':'0s','razrez-dd':'-7s','vertik-sterzhni':'-13s'},
    dorogi: {'doroga-perspektiva':'0s'},
    prom:   {'razrez-dd':'0s','vertik-sterzhni':'-6s','sloi-1-4':'-12s'},
    jobs:   {'uzel-2-ugol':'0s','razrez-rostverk':'-8s','grebenka':'-15s'}
  };
  const PULSES=PULSE_ON[PAGE]||PULSE_ON.index;
  FRAGS.forEach(function(fr){
    const d=document.createElement('div');
    d.className='dr';
    d.setAttribute('style',fr.s+';opacity:'+fr.o);
    const img=document.createElement('img');
    img.src='assets/bg2/'+fr.f+'.webp'; img.alt=''; img.decoding='async';
    d.appendChild(img);
    if(PULSES[fr.f]!==undefined){
      const p=document.createElement('div');
      p.className='pulse';
      p.setAttribute('style','inset:0;--m:var(--m-'+fr.f+')');
      p.innerHTML='<b style="animation-delay:'+PULSES[fr.f]+'"></b>';
      d.appendChild(p);
    }
    inner.appendChild(d);
  });
  document.addEventListener('DOMContentLoaded',function(){
    document.body.insertBefore(bg, document.body.firstChild);
    requestAnimationFrame(function(){requestAnimationFrame(function(){bg.classList.add('on')})});
    if(window.matchMedia('(prefers-reduced-motion:reduce)').matches) return;
    let t=false;
    window.addEventListener('scroll',function(){
      if(t) return; t=true;
      requestAnimationFrame(function(){
        inner.style.transform='translate3d(0,'+(-window.scrollY*0.11).toFixed(1)+'px,0)';
        t=false;
      });
    },{passive:true});
  });
})();

document.addEventListener('DOMContentLoaded',function(){

/* ═══ мобильное меню ═══ */
(function(){
  const head=document.querySelector('header .wrap'), nav=document.querySelector('header nav');
  if(!head||!nav) return;
  const btn=document.createElement('button');
  btn.className='burger'; btn.setAttribute('aria-label','Меню'); btn.setAttribute('aria-expanded','false');
  btn.innerHTML='<i></i><i></i><i></i>';
  const cta=head.querySelector(':scope > .btn');
  head.insertBefore(btn, cta||null);

  const panel=document.createElement('div');
  panel.className='mnav';
  nav.querySelectorAll('a').forEach(function(a){ panel.appendChild(a.cloneNode(true)); });
  if(cta){ const c=cta.cloneNode(true); c.classList.add('btn'); panel.appendChild(c); }
  document.querySelector('header').appendChild(panel);

  btn.addEventListener('click',function(){
    const on=panel.classList.toggle('on');
    btn.classList.toggle('on',on);
    btn.setAttribute('aria-expanded',on?'true':'false');
  });
  panel.addEventListener('click',function(e){ if(e.target.tagName==='A'){ panel.classList.remove('on'); btn.classList.remove('on'); } });
})();

/* ═══ надпись ═══ */
var replayText=null;
(function(){
  const nm=document.getElementById('nm'); if(!nm) return;
  const TEXT='TesseracT Group';
  const letters=[].map.call(TEXT,function(ch,i){
    const b=document.createElement('b');
    if(ch===' '){b.className='sp';b.innerHTML='&nbsp;';}
    else{b.textContent=ch; if(i===8) b.className='hi';}
    nm.appendChild(b); return b;
  });
  let timers=[];
  replayText=function(){
    timers.forEach(clearTimeout); timers=[];
    letters.forEach(function(b){b.classList.remove('on')});
    timers.push(setTimeout(function(){
      letters.forEach(function(b,i){ timers.push(setTimeout(function(){b.classList.add('on')},i*70)); });
    },400));
  };
  replayText();
})();

/* ═══ логотип ═══ */
(function(){
  const cv=document.getElementById('logo'); if(!cv) return;
  const g=cv.getContext('2d',{alpha:true}), DPR=Math.min(2,window.devicePixelRatio||1);
  let SIZE=112;
  const adj=[]; for(let v=0;v<16;v++) adj[v]=[0,1,2,3].map(function(k){return v^(1<<k)});
  const CIRC=(function(){const used={},st=[0],out=[];
    function key(a,b){return Math.min(a,b)*16+Math.max(a,b)}
    while(st.length){const v=st[st.length-1];let n=-1;
      for(let i=0;i<4;i++){const w=adj[v][i]; if(!used[key(v,w)]){n=w;break;}}
      if(n<0) out.push(st.pop()); else{used[key(v,n)]=1;st.push(n);}}
    return out.reverse();})();
  const NSEG=CIRC.length-1;
  const VTX=[]; for(let v=0;v<16;v++) VTX.push([v&1?1:-1,v&2?1:-1,v&4?1:-1,v&8?1:-1]);
  const Q=Math.PI/2,T1=2,T2=3,T3=5,DUR=13000;
  function ease(t){return 1-Math.pow(1-t,5)}
  function project(e,S){
    const a1=Q*T1*e,a2=Q*T2*e,a3=Q*T3*e,P=[],K=[];
    for(let v=0;v<16;v++){
      const a=VTX[v]; let x=a[0],y=a[1],z=a[2],w=a[3],c,s,nx,ny,nz,nw;
      c=Math.cos(a1);s=Math.sin(a1); nx=x*c-y*s; ny=x*s+y*c; x=nx;y=ny;
      c=Math.cos(a2);s=Math.sin(a2); nx=x*c-w*s; nw=x*s+w*c; x=nx;w=nw;
      c=Math.cos(a3);s=Math.sin(a3); nz=z*c-w*s; nw=z*s+w*c; z=nz;w=nw;
      const k4=2.75/(2.75-w),X=x*k4,Y=y*k4,Z=z*k4,k3=4.4/(4.4-Z);
      P.push([X*k3*S,Y*k3*S]); K.push(k4*k3);
    }
    return {P:P,K:K};
  }
  let maxR=0;
  for(let i=0;i<=360;i++){const pr=project(ease(i/360),1);
    for(let k=0;k<16;k++){const r=Math.hypot(pr.P[k][0],pr.P[k][1]); if(r>maxR)maxR=r;}}
  let SCALE=1;
  function fit(){SIZE=Math.round(cv.getBoundingClientRect().width||112);
    cv.width=SIZE*DPR;cv.height=SIZE*DPR;g.setTransform(DPR,0,0,DPR,0,0);SCALE=(SIZE/2-4)/maxR;}
  function cssv(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
  function rgb(h){h=h.replace('#','');if(h.length===3)h=h.split('').map(function(c){return c+c}).join('');
    return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)];}
  let start=null,running=false,raf=0;
  function frame(now){
    if(start===null) start=now;
    let p=(now-start)/DUR; if(p>=1){p=1;running=false;}
    const pr=project(ease(p),SCALE),P=pr.P,K=pr.K;
    let kmin=1e9,kmax=-1e9;
    for(let i=0;i<16;i++){if(K[i]<kmin)kmin=K[i];if(K[i]>kmax)kmax=K[i];}
    const span=Math.max(1e-6,kmax-kmin), ci=COL.ink, cs=COL.slate;
    g.clearRect(0,0,SIZE,SIZE);
    g.save(); g.translate(SIZE/2,SIZE/2); g.lineCap='round'; g.lineJoin='round';
    for(let i=0;i<NSEG;i++){
      const a=P[CIRC[i]],b=P[CIRC[i+1]];
      const d=((K[CIRC[i]]+K[CIRC[i+1]])/2-kmin)/span;
      const col=[ci[0]+(cs[0]-ci[0])*(1-d),ci[1]+(cs[1]-ci[1])*(1-d),ci[2]+(cs[2]-ci[2])*(1-d)];
      g.globalAlpha=0.24+0.76*d;
      g.lineWidth=(0.9+1.7*d)*(SIZE/100);
      g.strokeStyle='rgb('+(col[0]|0)+','+(col[1]|0)+','+(col[2]|0)+')';
      g.beginPath();g.moveTo(a[0],a[1]);g.lineTo(b[0],b[1]);g.stroke();
    }
    g.restore(); g.globalAlpha=1;
    if(running) raf=requestAnimationFrame(frame);
  }
  let COL={ink:[0,0,0],slate:[0,0,0]};
  function spin(){cancelAnimationFrame(raf);fit();COL={ink:rgb(cssv('--ink')),slate:rgb(cssv('--slate'))};start=null;running=true;raf=requestAnimationFrame(frame)}
  if(window.matchMedia('(prefers-reduced-motion:reduce)').matches){
    fit(); COL={ink:rgb(cssv('--ink')),slate:rgb(cssv('--slate'))}; const pr=project(1,SCALE);
    g.save();g.translate(SIZE/2,SIZE/2);g.strokeStyle=cssv('--ink');g.lineWidth=1.5;
    for(let i=0;i<NSEG;i++){const a=pr.P[CIRC[i]],b=pr.P[CIRC[i+1]];
      g.beginPath();g.moveTo(a[0],a[1]);g.lineTo(b[0],b[1]);g.stroke();}
    g.restore();
  } else {
    requestAnimationFrame(function(){requestAnimationFrame(spin)});
    const br=document.getElementById('brand');
    if(br) br.addEventListener('click',function(e){
      if(e.target.closest('a')) return;
      if(replayText) replayText();
      if(!running) spin();
    });
    let rz; window.addEventListener('resize',function(){clearTimeout(rz);
      rz=setTimeout(function(){if(!running) fit()},200)});
  }
})();

/* ═══ появление + счётчики ═══ */
(function(){
  function count(el){
    const to=+el.dataset.count,t0=performance.now(),D=1500;
    (function step(now){
      const p=Math.min(1,(now-t0)/D),e=1-Math.pow(1-p,3);
      el.textContent=Math.round(to*e).toLocaleString('ru-RU');
      if(p<1) requestAnimationFrame(step);
    })(t0);
  }
  const io=new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(e.isIntersecting){
        e.target.classList.add('in'); io.unobserve(e.target);
        e.target.querySelectorAll('[data-count]').forEach(count);
      }
    });
  },{threshold:.12});
  document.querySelectorAll('.rise').forEach(function(el){io.observe(el)});
  const h=document.querySelector('.hero'); if(h) h.classList.add('in');
})();

/* ═══ фильтры объектов ═══ */
(function(){
  const chips=document.querySelectorAll('.chip'); if(!chips.length) return;
  const cards=document.querySelectorAll('[data-type]');
  const line=document.getElementById('countLine');
  function apply(t){
    let n=0;
    cards.forEach(function(c){
      const ok = t==='all' || c.dataset.type===t;
      c.style.display = ok ? '' : 'none';
      if(ok) n++;
    });
    if(line) line.textContent='ПОКАЗАНО ОБЪЕКТОВ: '+n;
  }
  chips.forEach(function(ch){
    ch.addEventListener('click',function(){
      chips.forEach(function(c){c.classList.remove('on')});
      ch.classList.add('on');
      apply(ch.dataset.filter);
    });
  });
  apply('all');
})();

});
