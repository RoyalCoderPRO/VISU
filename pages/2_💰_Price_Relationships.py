"""
pages/2_💰_Price_Relationships.py
================================
Interactive explorer for how every numeric feature relates to price.
Data is embedded as JSON so the page works on Streamlit Cloud with no
external file server.
"""
from pathlib import Path
import json
import streamlit as st
from backend.data import load_automobiles

st.set_page_config(
    page_title="Price Relationships · VISU",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Embed data as JSON ────────────────────────────────────────────────────────
df = load_automobiles()
data_json = json.dumps(df.to_dict(orient="records"))

# ── Build self-contained HTML ─────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',sans-serif;background:#0a0e1a;color:#e2e8f0;padding:24px 28px 40px}}
h1{{font-size:1.6rem;font-weight:700;background:linear-gradient(90deg,#38bdf8,#818cf8,#f472b6);
   -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px}}
.subtitle{{color:#475569;font-family:monospace;font-size:.72rem;letter-spacing:2px;margin-bottom:28px}}
.controls{{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:22px;align-items:flex-end}}
.ctrl-group{{display:flex;flex-direction:column;gap:5px}}
label{{font-size:.72rem;color:#64748b;letter-spacing:1px;text-transform:uppercase}}
select{{background:#111827;color:#e2e8f0;border:1px solid #1e293b;border-radius:6px;
        padding:7px 12px;font-size:.82rem;cursor:pointer;outline:none}}
select:focus{{border-color:#38bdf8}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px}}
.card{{background:#111827;border:1px solid #1e293b;border-radius:12px;padding:18px}}
.card-full{{background:#111827;border:1px solid #1e293b;border-radius:12px;padding:18px}}
.card h3{{font-size:.82rem;color:#94a3b8;letter-spacing:1.5px;text-transform:uppercase;
          margin-bottom:14px;font-weight:600}}
.chart-wrap{{position:relative;height:300px}}
.chart-wrap-tall{{position:relative;height:340px}}
.stat-row{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:20px}}
.stat{{background:#111827;border:1px solid #1e293b;border-radius:10px;
       padding:12px 18px;flex:1;min-width:120px}}
.stat .val{{font-size:1.2rem;font-weight:700;color:#38bdf8}}
.stat .lbl{{font-size:.68rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-top:3px}}
</style>
</head>
<body>

<h1>💰 Price Relationships</h1>
<p class="subtitle">1985 WARD'S AUTOMOTIVE YEARBOOK · 205 RECORDS</p>

<!-- KPI strip -->
<div class="stat-row" id="kpiStrip"></div>

<!-- Controls -->
<div class="controls">
  <div class="ctrl-group">
    <label>X-Axis Variable</label>
    <select id="xVar">
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
  <div class="ctrl-group">
    <label>Color By</label>
    <select id="colorBy">
      <option value="body-style">Body Style</option>
      <option value="fuel-type">Fuel Type</option>
      <option value="drive-wheels">Drive Wheels</option>
      <option value="engine-type">Engine Type</option>
    </select>
  </div>
  <div class="ctrl-group">
    <label>Category (bar chart)</label>
    <select id="catVar">
      <option value="body-style">Body Style</option>
      <option value="fuel-type">Fuel Type</option>
      <option value="drive-wheels">Drive Wheels</option>
      <option value="engine-type">Engine Type</option>
      <option value="make">Make (Top 12)</option>
      <option value="num-of-cylinders">No. of Cylinders</option>
    </select>
  </div>
</div>

<!-- Charts grid -->
<div class="grid">
  <div class="card">
    <h3 id="scatterTitle">Price vs Horsepower</h3>
    <div class="chart-wrap"><canvas id="cScatter"></canvas></div>
  </div>
  <div class="card">
    <h3 id="barTitle">Avg Price by Body Style</h3>
    <div class="chart-wrap"><canvas id="cBar"></canvas></div>
  </div>
</div>

<div class="card-full">
  <h3>Correlation of All Features with Price (Pearson r)</h3>
  <div class="chart-wrap-tall"><canvas id="cCorr"></canvas></div>
</div>

<script>
const RAW = {data_json};

const PAL = ['#38bdf8','#818cf8','#f472b6','#34d399','#fb923c','#facc15','#a78bfa','#f87171','#2dd4bf','#e879f9','#4ade80','#fbbf24'];

const AXIS_STYLE = {{
  grid:{{color:'#1e293b'}},
  ticks:{{color:'#64748b',font:{{size:8}}}},
  border:{{color:'#1e293b'}}
}};

function num(r,k){{ return r[k]!=null && !isNaN(r[k]) ? +r[k] : null; }}

// ── Pearson r ────────────────────────────────────────────────────────────────
function pearson(xs,ys){{
  const n=xs.length;
  if(n<3) return 0;
  const mx=xs.reduce((a,b)=>a+b,0)/n, my=ys.reduce((a,b)=>a+b,0)/n;
  let num=0,dx=0,dy=0;
  for(let i=0;i<n;i++){{
    const a=xs[i]-mx,b=ys[i]-my;
    num+=a*b; dx+=a*a; dy+=b*b;
  }}
  return (dx&&dy)?num/Math.sqrt(dx*dy):0;
}}

// ── Linear regression ────────────────────────────────────────────────────────
function linReg(pts){{
  const xs=pts.map(p=>p.x),ys=pts.map(p=>p.y),n=xs.length;
  const mx=xs.reduce((a,b)=>a+b,0)/n,my=ys.reduce((a,b)=>a+b,0)/n;
  let num=0,den=0;
  for(let i=0;i<n;i++){{num+=(xs[i]-mx)*(ys[i]-my);den+=(xs[i]-mx)**2;}}
  const m=den?num/den:0,c=my-m*mx;
  const minX=Math.min(...xs),maxX=Math.max(...xs);
  return [{{x:minX,y:m*minX+c}},{{x:maxX,y:m*maxX+c}}];
}}

// ── KPI strip ────────────────────────────────────────────────────────────────
function renderKPIs(){{
  const prices=RAW.map(r=>num(r,'price')).filter(v=>v!=null);
  const hp=RAW.map(r=>num(r,'horsepower')).filter(v=>v!=null);
  const mpg=RAW.map(r=>num(r,'avg-mpg')).filter(v=>v!=null);
  const avg=a=>a.reduce((s,v)=>s+v,0)/a.length;
  const kpis=[
    ['Avg Price','$'+avg(prices).toLocaleString('en',{{maximumFractionDigits:0}})],
    ['Price Range','$'+Math.min(...prices).toLocaleString()+'–$'+Math.max(...prices).toLocaleString()],
    ['Avg HP', avg(hp).toFixed(0)+' hp'],
    ['Avg MPG', avg(mpg).toFixed(1)+' mpg'],
    ['Records', RAW.length],
  ];
  document.getElementById('kpiStrip').innerHTML=kpis.map(([l,v])=>
    `<div class="stat"><div class="val">${{v}}</div><div class="lbl">${{l}}</div></div>`
  ).join('');
}}

// ── Charts ───────────────────────────────────────────────────────────────────
let cScatter=null, cBar=null, cCorr=null;

function mkChart(id,cfg){{
  const el=document.getElementById(id);
  if(!el) return null;
  return new Chart(el.getContext('2d'),cfg);
}}

function renderScatter(){{
  const xKey=document.getElementById('xVar').value;
  const cbKey=document.getElementById('colorBy').value;
  document.getElementById('scatterTitle').textContent=
    'Price vs '+document.getElementById('xVar').selectedOptions[0].text;

  const groups={{}};
  RAW.forEach(r=>{{
    const x=num(r,xKey),y=num(r,'price'),g=r[cbKey]||'Unknown';
    if(x!=null&&y!=null){{(groups[g]=groups[g]||[]).push({{x,y}});}}
  }});

  const keys=Object.keys(groups).sort();
  const datasets=keys.map((k,i)=>{{
    const pts=groups[k];
    return {{label:k,data:pts,backgroundColor:PAL[i%PAL.length]+'aa',
             borderColor:PAL[i%PAL.length],borderWidth:1,pointRadius:4,
             pointHoverRadius:6,type:'scatter'}};
  }});

  // Regression line over all points
  const allPts=RAW.map(r=>{{const x=num(r,xKey),y=num(r,'price');return x!=null&&y!=null?{{x,y}}:null;}}).filter(Boolean);
  if(allPts.length>2){{
    datasets.push({{
      label:'Trend',type:'line',
      data:linReg(allPts),
      borderColor:'#ffffff55',borderWidth:1.5,
      borderDash:[5,4],pointRadius:0,fill:false,
      tension:0
    }});
  }}

  if(cScatter) cScatter.destroy();
  cScatter=mkChart('cScatter',{{
    type:'scatter',
    data:{{datasets}},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{
        legend:{{labels:{{color:'#94a3b8',font:{{size:8}},boxWidth:10,padding:8}}}},
        tooltip:{{callbacks:{{
          label:i=>`${{i.dataset.label}}: (${{i.parsed.x.toFixed(0)}}, $${{i.parsed.y.toLocaleString()}})`
        }}}}
      }},
      scales:{{
        x:{{...AXIS_STYLE,title:{{display:true,text:document.getElementById('xVar').selectedOptions[0].text,color:'#64748b',font:{{size:8}}}}}},
        y:{{...AXIS_STYLE,title:{{display:true,text:'Price ($)',color:'#64748b',font:{{size:8}}}},
           ticks:{{...AXIS_STYLE.ticks,callback:v=>'$'+v.toLocaleString()}}}}
      }},
      animation:{{duration:250}}
    }}
  }});
}}

function renderBar(){{
  const catKey=document.getElementById('catVar').value;
  document.getElementById('barTitle').textContent=
    'Avg Price by '+document.getElementById('catVar').selectedOptions[0].text;

  const sums={{}},counts={{}};
  RAW.forEach(r=>{{
    let g=r[catKey]||'Unknown';
    const p=num(r,'price');
    if(p!=null){{sums[g]=(sums[g]||0)+p;counts[g]=(counts[g]||0)+1;}}
  }});

  let entries=Object.entries(sums).map(([k,s])=>[k,s/counts[k]]).sort((a,b)=>b[1]-a[1]);
  if(catKey==='make') entries=entries.slice(0,12);

  if(cBar) cBar.destroy();
  cBar=mkChart('cBar',{{
    type:'bar',
    data:{{
      labels:entries.map(([k])=>k),
      datasets:[{{
        data:entries.map(([,v])=>v),
        backgroundColor:PAL.slice(0,entries.length).map(c=>c+'99'),
        borderColor:PAL.slice(0,entries.length),
        borderWidth:1.4,borderRadius:4
      }}]
    }},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{
        legend:{{display:false}},
        tooltip:{{callbacks:{{label:i=>'Avg: $'+i.raw.toLocaleString('en',{{maximumFractionDigits:0}})}}}}
      }},
      scales:{{
        x:{{...AXIS_STYLE,ticks:{{...AXIS_STYLE.ticks,maxRotation:30}}}},
        y:{{...AXIS_STYLE,ticks:{{...AXIS_STYLE.ticks,callback:v=>'$'+v.toLocaleString()}}}}
      }},
      animation:{{duration:250}}
    }}
  }});
}}

function renderCorr(){{
  const features=[
    ['Horsepower','horsepower'],['Engine Size','engine-size'],
    ['Curb Weight','curb-weight'],['Width','width'],['Length','length'],
    ['Wheel Base','wheel-base'],['Bore','bore'],['Stroke','stroke'],
    ['Compression','compression-ratio'],['Peak RPM','peak-rpm'],['Avg MPG','avg-mpg'],
  ];
  const vals=features.map(([,k])=>{{
    const pairs=RAW.map(r=>{{const x=num(r,k),y=num(r,'price');return x!=null&&y!=null?[x,y]:null;}}).filter(Boolean);
    return pairs.length>4?pearson(pairs.map(p=>p[0]),pairs.map(p=>p[1])):0;
  }});
  const sorted=[...features.map(([l],i)=>{{return{{l,v:vals[i]}};}})].sort((a,b)=>b.v-a.v);

  if(cCorr) cCorr.destroy();
  cCorr=mkChart('cCorr',{{
    type:'bar',
    data:{{
      labels:sorted.map(x=>x.l),
      datasets:[{{
        label:'Pearson r with Price',
        data:sorted.map(x=>x.v),
        backgroundColor:sorted.map(x=>x.v>=0?'#38bdf888':'#f472b688'),
        borderColor:sorted.map(x=>x.v>=0?'#38bdf8':'#f472b6'),
        borderWidth:1.5,borderRadius:4
      }}]
    }},
    options:{{
      indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{{
        legend:{{display:false}},
        tooltip:{{callbacks:{{label:i=>'r = '+i.raw.toFixed(3)}}}}
      }},
      scales:{{
        x:{{...AXIS_STYLE,min:-1,max:1,
           ticks:{{...AXIS_STYLE.ticks,callback:v=>v.toFixed(1)}}}},
        y:{{...AXIS_STYLE}}
      }},
      animation:{{duration:250}}
    }}
  }});
}}

// ── Wire controls ─────────────────────────────────────────────────────────────
document.getElementById('xVar').addEventListener('change',renderScatter);
document.getElementById('colorBy').addEventListener('change',renderScatter);
document.getElementById('catVar').addEventListener('change',renderBar);

// ── Initial render ────────────────────────────────────────────────────────────
renderKPIs();
renderScatter();
renderBar();
renderCorr();

// ── Auto-resize iframe ────────────────────────────────────────────────────────
function sendHeight(){{
  document.body.style.minHeight='0';
  const h=document.documentElement.scrollHeight||document.body.scrollHeight;
  window.parent.postMessage({{isStreamlitMessage:true,type:'streamlit:setFrameHeight',height:h}},'*');
}}
window.addEventListener('load',sendHeight);
[600,1200,2000].forEach(t=>setTimeout(sendHeight,t));
</script>
</body>
</html>"""

st.components.v1.html(html, height=5000, scrolling=False)
