"""
app.py — VISU · Automobile Data Explorer
=========================================
Single-page app with a top navbar. Sections are switched via JS —
no Streamlit multipage routing needed.
"""
from pathlib import Path
import json
import streamlit as st
from backend.data import load_automobiles

st.set_page_config(
    page_title="VISU · Automobile Explorer",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide all Streamlit chrome — the HTML provides its own UI
st.markdown("""
<style>
    #MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Load assets ───────────────────────────────────────────────────────────────
_explorer_html = (Path(__file__).parent / "frontend" / "explorer.html").read_text(encoding="utf-8")

df = load_automobiles()
_data_json = json.dumps(df.to_dict(orient="records"))

# Extract the <head> imports from explorer.html so we can reuse them
import re
_head_match = re.search(r"<head>(.*?)</head>", _explorer_html, re.DOTALL)
_explorer_head = _head_match.group(1) if _head_match else ""

# Extract the <body> content from explorer.html
_body_match = re.search(r"<body>(.*?)</body>", _explorer_html, re.DOTALL)
_explorer_body = _body_match.group(1) if _body_match else _explorer_html

# ── Build combined HTML ───────────────────────────────────────────────────────
PAL = ["#38bdf8","#818cf8","#f472b6","#34d399","#fb923c","#facc15","#a78bfa","#f87171","#2dd4bf","#e879f9"]

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<!-- Inherit all of explorer's head (fonts, scripts, styles) -->
{_explorer_head}
<!-- Chart.js for Price Relationships page -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<style>
/* ── Navbar ──────────────────────────────────────────────────────────── */
#visu-nav {{
  position: sticky; top: 0; z-index: 9999;
  background: #070b14;
  border-bottom: 1px solid #1e293b;
  display: flex; align-items: center; gap: 0;
  padding: 0 24px;
  height: 48px;
}}
.nav-brand {{
  font-weight: 800; font-size: 1.05rem; letter-spacing: 2px;
  background: linear-gradient(90deg,#38bdf8,#818cf8);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-right: 32px; white-space: nowrap;
}}
.nav-tab {{
  height: 48px; padding: 0 20px;
  background: none; border: none; border-bottom: 2px solid transparent;
  color: #64748b; font-size: .82rem; font-weight: 600; letter-spacing: .5px;
  cursor: pointer; transition: all .2s; white-space: nowrap;
  font-family: 'Inter', sans-serif;
}}
.nav-tab:hover  {{ color: #94a3b8; }}
.nav-tab.active {{ color: #38bdf8; border-bottom-color: #38bdf8; }}

/* ── Sections ────────────────────────────────────────────────────────── */
.visu-section {{ display: none; }}
.visu-section.active {{ display: block; }}

/* ── Price Relationships styles ──────────────────────────────────────── */
#sec-price {{
  font-family: 'Inter', sans-serif;
  background: #0a0e1a; color: #e2e8f0;
  padding: 28px 28px 48px;
}}
#sec-price h1 {{
  font-size: 1.5rem; font-weight: 700;
  background: linear-gradient(90deg,#38bdf8,#818cf8,#f472b6);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: 4px;
}}
.pr-subtitle {{
  color: #475569; font-family: monospace; font-size: .72rem;
  letter-spacing: 2px; margin-bottom: 24px;
}}
.pr-controls {{
  display: flex; flex-wrap: wrap; gap: 14px;
  margin-bottom: 22px; align-items: flex-end;
}}
.pr-ctrl {{ display: flex; flex-direction: column; gap: 5px; }}
.pr-ctrl label {{
  font-size: .7rem; color: #64748b;
  letter-spacing: 1px; text-transform: uppercase;
}}
.pr-ctrl select {{
  background: #111827; color: #e2e8f0;
  border: 1px solid #1e293b; border-radius: 6px;
  padding: 7px 12px; font-size: .82rem; cursor: pointer; outline: none;
  font-family: 'Inter', sans-serif;
}}
.pr-ctrl select:focus {{ border-color: #38bdf8; }}
.pr-kpi-row {{
  display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 22px;
}}
.pr-kpi {{
  background: #111827; border: 1px solid #1e293b;
  border-radius: 10px; padding: 12px 18px; flex: 1; min-width: 110px;
}}
.pr-kpi .val {{ font-size: 1.15rem; font-weight: 700; color: #38bdf8; }}
.pr-kpi .lbl {{
  font-size: .67rem; color: #64748b;
  text-transform: uppercase; letter-spacing: 1px; margin-top: 3px;
}}
.pr-grid {{
  display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 18px;
}}
.pr-card {{
  background: #111827; border: 1px solid #1e293b;
  border-radius: 12px; padding: 18px;
}}
.pr-card h3 {{
  font-size: .78rem; color: #94a3b8; letter-spacing: 1.5px;
  text-transform: uppercase; margin-bottom: 14px; font-weight: 600;
}}
.pr-chart-wrap  {{ position: relative; height: 290px; }}
.pr-chart-tall  {{ position: relative; height: 330px; }}
</style>
</head>
<body style="margin:0;padding:0;background:#0a0e1a;">

<!-- ═══════════════════ NAVBAR ═══════════════════ -->
<nav id="visu-nav">
  <span class="nav-brand">⬡ VISU</span>
  <button class="nav-tab active" onclick="showSection('explorer', this)">🏎️ Engine Explorer</button>
  <button class="nav-tab"        onclick="showSection('price',    this)">💰 Price Relationships</button>
</nav>

<!-- ═══════════════════ SECTION: ENGINE EXPLORER ═══════════════════ -->
<div id="sec-explorer" class="visu-section active">
  {_explorer_body}
</div>

<!-- ═══════════════════ SECTION: PRICE RELATIONSHIPS ═══════════════════ -->
<div id="sec-price" class="visu-section">
  <h1>💰 Price Relationships</h1>
  <p class="pr-subtitle">1985 WARD'S AUTOMOTIVE YEARBOOK · 205 RECORDS</p>

  <!-- KPIs -->
  <div class="pr-kpi-row" id="prKpis"></div>

  <!-- Controls -->
  <div class="pr-controls">
    <div class="pr-ctrl">
      <label>X-Axis Variable</label>
      <select id="prXVar">
        <option value="horsepower">Horsepower (hp)</option>
        <option value="engine-size">Engine Size (cc)</option>
        <option value="curb-weight">Curb Weight (lbs)</option>
        <option value="width">Width (in)</option>
        <option value="length">Length (in)</option>
        <option value="peak-rpm">Peak RPM</option>
        <option value="compression-ratio">Compression Ratio</option>
        <option value="avg-mpg">Avg MPG</option>
        <option value="bore">Bore</option>
        <option value="stroke">Stroke</option>
      </select>
    </div>
    <div class="pr-ctrl">
      <label>Color By</label>
      <select id="prColorBy">
        <option value="body-style">Body Style</option>
        <option value="fuel-type">Fuel Type</option>
        <option value="drive-wheels">Drive Wheels</option>
        <option value="engine-type">Engine Type</option>
      </select>
    </div>
    <div class="pr-ctrl">
      <label>Category (bar chart)</label>
      <select id="prCatVar">
        <option value="body-style">Body Style</option>
        <option value="fuel-type">Fuel Type</option>
        <option value="drive-wheels">Drive Wheels</option>
        <option value="engine-type">Engine Type</option>
        <option value="make">Make (Top 12)</option>
        <option value="num-of-cylinders">No. of Cylinders</option>
      </select>
    </div>
  </div>

  <!-- Charts -->
  <div class="pr-grid">
    <div class="pr-card">
      <h3 id="prScatterTitle">Price vs Horsepower</h3>
      <div class="pr-chart-wrap"><canvas id="prCScatter"></canvas></div>
    </div>
    <div class="pr-card">
      <h3 id="prBarTitle">Avg Price by Body Style</h3>
      <div class="pr-chart-wrap"><canvas id="prCBar"></canvas></div>
    </div>
  </div>
  <div class="pr-card">
    <h3>Correlation of All Features with Price (Pearson r)</h3>
    <div class="pr-chart-tall"><canvas id="prCCorr"></canvas></div>
  </div>
</div>

<!-- ═══════════════════ SCRIPTS ═══════════════════ -->
<script>
// ── Section switching ──────────────────────────────────────────────────────
function showSection(id, btn) {{
  document.querySelectorAll('.visu-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
  document.getElementById('sec-' + id).classList.add('active');
  btn.classList.add('active');
  // Init price charts lazily on first visit
  if (id === 'price' && !window._priceInited) {{
    window._priceInited = true;
    prInit();
  }}
  sendHeight();
}}

// ── Price Relationships data & charts ──────────────────────────────────────
const PR_DATA = {_data_json};
const PR_PAL  = {json.dumps(PAL)};

const AXIS = {{
  grid: {{color:'#1e293b'}},
  ticks: {{color:'#64748b', font:{{size:8}}}},
  border: {{color:'#1e293b'}}
}};

function prNum(r,k) {{ return r[k]!=null && !isNaN(r[k]) ? +r[k] : null; }}

function pearson(xs, ys) {{
  const n=xs.length; if(n<3) return 0;
  const mx=xs.reduce((a,b)=>a+b,0)/n, my=ys.reduce((a,b)=>a+b,0)/n;
  let num=0,dx=0,dy=0;
  for(let i=0;i<n;i++){{const a=xs[i]-mx,b=ys[i]-my;num+=a*b;dx+=a*a;dy+=b*b;}}
  return (dx&&dy)?num/Math.sqrt(dx*dy):0;
}}

function linReg(pts) {{
  const xs=pts.map(p=>p.x),ys=pts.map(p=>p.y),n=xs.length;
  const mx=xs.reduce((a,b)=>a+b,0)/n,my=ys.reduce((a,b)=>a+b,0)/n;
  let num=0,den=0;
  for(let i=0;i<n;i++){{num+=(xs[i]-mx)*(ys[i]-my);den+=(xs[i]-mx)**2;}}
  const m=den?num/den:0,c=my-m*mx;
  const minX=Math.min(...xs),maxX=Math.max(...xs);
  return [{{x:minX,y:m*minX+c}},{{x:maxX,y:m*maxX+c}}];
}}

let prScatter=null, prBar=null, prCorr=null;

function mkPrChart(id,cfg) {{
  const el=document.getElementById(id);
  if(!el) return null;
  return new Chart(el.getContext('2d'),cfg);
}}

function prInit() {{
  // KPIs
  const prices=PR_DATA.map(r=>prNum(r,'price')).filter(v=>v!=null);
  const hp=PR_DATA.map(r=>prNum(r,'horsepower')).filter(v=>v!=null);
  const mpg=PR_DATA.map(r=>prNum(r,'avg-mpg')).filter(v=>v!=null);
  const avg=a=>a.reduce((s,v)=>s+v,0)/a.length;
  const kpis=[
    ['Avg Price','$'+avg(prices).toLocaleString('en',{{maximumFractionDigits:0}})],
    ['Price Range','$'+Math.min(...prices).toLocaleString()+'–$'+Math.max(...prices).toLocaleString()],
    ['Avg HP',avg(hp).toFixed(0)+' hp'],
    ['Avg MPG',avg(mpg).toFixed(1)+' mpg'],
    ['Records',PR_DATA.length],
  ];
  document.getElementById('prKpis').innerHTML=kpis.map(([l,v])=>
    `<div class="pr-kpi"><div class="val">${{v}}</div><div class="lbl">${{l}}</div></div>`
  ).join('');

  prRenderScatter();
  prRenderBar();
  prRenderCorr();

  document.getElementById('prXVar').addEventListener('change', prRenderScatter);
  document.getElementById('prColorBy').addEventListener('change', prRenderScatter);
  document.getElementById('prCatVar').addEventListener('change', prRenderBar);
}}

function prRenderScatter() {{
  const xKey=document.getElementById('prXVar').value;
  const cbKey=document.getElementById('prColorBy').value;
  document.getElementById('prScatterTitle').textContent=
    'Price vs '+document.getElementById('prXVar').selectedOptions[0].text;
  const groups={{}};
  PR_DATA.forEach(r=>{{
    const x=prNum(r,xKey),y=prNum(r,'price'),g=r[cbKey]||'Unknown';
    if(x!=null&&y!=null) (groups[g]=groups[g]||[]).push({{x,y}});
  }});
  const keys=Object.keys(groups).sort();
  const datasets=keys.map((k,i)=>{{
    return {{label:k,data:groups[k],
             backgroundColor:PR_PAL[i%PR_PAL.length]+'aa',
             borderColor:PR_PAL[i%PR_PAL.length],
             borderWidth:1,pointRadius:4,pointHoverRadius:6,type:'scatter'}};
  }});
  const allPts=PR_DATA.map(r=>{{const x=prNum(r,xKey),y=prNum(r,'price');return x&&y?{{x,y}}:null;}}).filter(Boolean);
  if(allPts.length>2) datasets.push({{
    label:'Trend',type:'line',data:linReg(allPts),
    borderColor:'#ffffff55',borderWidth:1.5,borderDash:[5,4],
    pointRadius:0,fill:false,tension:0
  }});
  if(prScatter) prScatter.destroy();
  prScatter=mkPrChart('prCScatter',{{
    type:'scatter',data:{{datasets}},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{
        legend:{{labels:{{color:'#94a3b8',font:{{size:8}},boxWidth:10,padding:8}}}},
        tooltip:{{callbacks:{{label:i=>`${{i.dataset.label}}: (${{i.parsed.x.toFixed(0)}}, $${{i.parsed.y.toLocaleString()}})`}}}}
      }},
      scales:{{
        x:{{...AXIS,title:{{display:true,text:document.getElementById('prXVar').selectedOptions[0].text,color:'#64748b',font:{{size:8}}}}}},
        y:{{...AXIS,title:{{display:true,text:'Price ($)',color:'#64748b',font:{{size:8}}}},ticks:{{...AXIS.ticks,callback:v=>'$'+v.toLocaleString()}}}}
      }},animation:{{duration:200}}
    }}
  }});
}}

function prRenderBar() {{
  const catKey=document.getElementById('prCatVar').value;
  document.getElementById('prBarTitle').textContent=
    'Avg Price by '+document.getElementById('prCatVar').selectedOptions[0].text;
  const sums={{}},counts={{}};
  PR_DATA.forEach(r=>{{
    const g=r[catKey]||'Unknown',p=prNum(r,'price');
    if(p!=null){{sums[g]=(sums[g]||0)+p;counts[g]=(counts[g]||0)+1;}}
  }});
  let entries=Object.entries(sums).map(([k,s])=>[k,s/counts[k]]).sort((a,b)=>b[1]-a[1]);
  if(catKey==='make') entries=entries.slice(0,12);
  if(prBar) prBar.destroy();
  prBar=mkPrChart('prCBar',{{
    type:'bar',
    data:{{
      labels:entries.map(([k])=>k),
      datasets:[{{
        data:entries.map(([,v])=>v),
        backgroundColor:PR_PAL.slice(0,entries.length).map(c=>c+'99'),
        borderColor:PR_PAL.slice(0,entries.length),
        borderWidth:1.4,borderRadius:4
      }}]
    }},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:i=>'$'+i.raw.toLocaleString('en',{{maximumFractionDigits:0}})}}}}}},
      scales:{{
        x:{{...AXIS,ticks:{{...AXIS.ticks,maxRotation:30}}}},
        y:{{...AXIS,ticks:{{...AXIS.ticks,callback:v=>'$'+v.toLocaleString()}}}}
      }},animation:{{duration:200}}
    }}
  }});
}}

function prRenderCorr() {{
  const feats=[
    ['Horsepower','horsepower'],['Engine Size','engine-size'],
    ['Curb Weight','curb-weight'],['Width','width'],['Length','length'],
    ['Wheel Base','wheel-base'],['Bore','bore'],['Stroke','stroke'],
    ['Compression','compression-ratio'],['Peak RPM','peak-rpm'],['Avg MPG','avg-mpg'],
  ];
  const vals=feats.map(([,k])=>{{
    const pairs=PR_DATA.map(r=>{{const x=prNum(r,k),y=prNum(r,'price');return x!=null&&y!=null?[x,y]:null;}}).filter(Boolean);
    return pairs.length>4?pearson(pairs.map(p=>p[0]),pairs.map(p=>p[1])):0;
  }});
  const sorted=[...feats.map(([l],i)=>{{return{{l,v:vals[i]}};}})].sort((a,b)=>b.v-a.v);
  if(prCorr) prCorr.destroy();
  prCorr=mkPrChart('prCCorr',{{
    type:'bar',
    data:{{
      labels:sorted.map(x=>x.l),
      datasets:[{{
        label:'Pearson r',data:sorted.map(x=>x.v),
        backgroundColor:sorted.map(x=>x.v>=0?'#38bdf888':'#f472b688'),
        borderColor:sorted.map(x=>x.v>=0?'#38bdf8':'#f472b6'),
        borderWidth:1.5,borderRadius:4
      }}]
    }},
    options:{{
      indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:i=>'r = '+i.raw.toFixed(3)}}}}}},
      scales:{{x:{{...AXIS,min:-1,max:1,ticks:{{...AXIS.ticks,callback:v=>v.toFixed(1)}}}},y:{{...AXIS}}}},
      animation:{{duration:200}}
    }}
  }});
}}

// ── Auto-resize iframe ────────────────────────────────────────────────────────
function sendHeight() {{
  document.body.style.minHeight = '0';
  const h = document.documentElement.scrollHeight || document.body.scrollHeight;
  window.parent.postMessage({{isStreamlitMessage:true, type:'streamlit:setFrameHeight', height:h}}, '*');
}}
window.addEventListener('load', sendHeight);
[600, 1200, 2000].forEach(t => setTimeout(sendHeight, t));
</script>

</body>
</html>"""

st.iframe(html, height=7000, scrolling=False)
