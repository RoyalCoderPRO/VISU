"""
inject_stats.py
Appends a full descriptive-statistics section (Chart.js) into engine_explorer.html
just before </body>.  Re-runnable — removes any previously injected section first.
"""
import json, pathlib

HTML_FILE = pathlib.Path("engine_explorer.html")
DATA_FILE = pathlib.Path("_data.json")

raw = HTML_FILE.read_text(encoding="utf-8")
data_json = DATA_FILE.read_text(encoding="utf-8")

# ── Remove any previously injected section ────────────────────────────────────
START_MARKER = "<!-- ##STATS_SECTION_START## -->"
END_MARKER   = "<!-- ##STATS_SECTION_END## -->"
if START_MARKER in raw:
    s = raw.index(START_MARKER)
    e = raw.index(END_MARKER) + len(END_MARKER)
    raw = raw[:s] + raw[e:]

# ── Chart card helper — fixed-height wrapper ──────────────────────────────────
# The key fix: every canvas lives in a position:relative div with an explicit
# pixel height. Chart.js reads that height and never grows beyond it.
def card(title, canvas_id, height=200):
    return f"""
      <div style="background:#111827;border:1px solid #1e293b;border-radius:10px;padding:12px;box-sizing:border-box">
        <div style="font-family:'Share Tech Mono',monospace;font-size:.62rem;color:#64748b;letter-spacing:1.5px;margin-bottom:8px;text-transform:uppercase">{title}</div>
        <div style="position:relative;height:{height}px;width:100%">
          <canvas id="{canvas_id}"></canvas>
        </div>
      </div>"""

# ── Build the stats section HTML ──────────────────────────────────────────────
SECTION = f"""
<!-- ##STATS_SECTION_START## -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>

<div style="max-width:1200px;margin:28px auto 0;padding:0 16px 32px">
  <div style="border-top:1px solid #1e293b;padding-top:22px">

    <!-- Header -->
    <div style="text-align:center;margin-bottom:20px">
      <h2 style="font-size:1.5rem;font-weight:700;background:linear-gradient(90deg,#38bdf8,#818cf8,#f472b6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0 0 4px">
        📊 Descriptive Statistics
      </h2>
      <p style="color:#475569;font-family:'Share Tech Mono',monospace;font-size:.72rem;letter-spacing:2px;margin:0">
        1985 WARD'S AUTOMOTIVE YEARBOOK · 205 RECORDS
      </p>
    </div>

    <!-- Filters -->
    <div id="statsFilters" style="display:flex;gap:14px;flex-wrap:wrap;justify-content:center;margin-bottom:18px"></div>

    <!-- Record count -->
    <p id="statsCount" style="text-align:center;font-family:'Share Tech Mono',monospace;font-size:.68rem;color:#475569;margin-bottom:14px"></p>

    <!-- KPI cards -->
    <div id="kpiRow" style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:22px"></div>

    <!-- Row 1: 4 histograms -->
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px">
      {card("Price Distribution",     "cHist0", 170)}
      {card("Horsepower Distribution","cHist1", 170)}
      {card("Avg MPG Distribution",   "cHist2", 170)}
      {card("Engine Size Distribution","cHist3",170)}
    </div>

    <!-- Row 2: body price + engine hp/mpg -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
      {card("Avg Price by Body Style",      "cBodyPrice", 200)}
      {card("Avg HP &amp; MPG by Engine Type", "cEngHpMpg",  200)}
    </div>

    <!-- Row 3: scatter + correlation -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
      {card("Price vs Horsepower",             "cScatter", 220)}
      {card("Feature Correlation with Price",  "cCorr",    220)}
    </div>

    <!-- Row 4: makes + drive-wheel -->
    <div style="display:grid;grid-template-columns:1.5fr 1fr;gap:12px;margin-bottom:14px">
      {card("Cars by Make (Top 15)",    "cMakes", 280)}
      {card("Drive-Wheel Distribution", "cDW",    280)}
    </div>

  </div>
</div>

<script>
(function(){{
// ── Data ──────────────────────────────────────────────────────────────────────
const RAW = {data_json};

// ── Palette ───────────────────────────────────────────────────────────────────
const PAL     = ['#38bdf8','#818cf8','#f472b6','#34d399','#fb923c','#facc15','#a78bfa','#e879f9','#2dd4bf'];
const BODY_C  = {{convertible:'#f472b6',hardtop:'#fb923c',hatchback:'#38bdf8',sedan:'#818cf8',wagon:'#34d399'}};
const ENG_C   = {{dohc:'#f472b6',l:'#a78bfa',ohc:'#38bdf8',ohcf:'#34d399',ohcv:'#fb923c',rotor:'#facc15'}};

Chart.defaults.color = '#64748b';
Chart.defaults.font.family = "'Share Tech Mono', monospace";

// ── Math helpers ──────────────────────────────────────────────────────────────
const num    = (d,k) => d.map(r=>r[k]).filter(v=>v!=null&&!isNaN(v));
const mean   = a => a.length ? a.reduce((s,v)=>s+v,0)/a.length : 0;
const median = a => {{ if(!a.length) return 0; const s=[...a].sort((a,b)=>a-b),m=Math.floor(s.length/2); return s.length%2?s[m]:(s[m-1]+s[m])/2; }};
const fmt$   = v => v==null ? '—' : '$'+Math.round(v).toLocaleString();
const fmtN   = (v,d=1) => v==null ? '—' : (+v).toFixed(d);

function hist(vals, bins=20){{
  const mn=Math.min(...vals), mx=Math.max(...vals), bw=(mx-mn)/bins||1;
  const counts=new Array(bins).fill(0);
  vals.forEach(v=>{{ const i=Math.min(Math.floor((v-mn)/bw),bins-1); counts[i]++; }});
  return {{ labels:counts.map((_,i)=>Math.round(mn+i*bw)), counts }};
}}

function pearson(xs,ys){{
  const n=xs.length; if(n<2) return 0;
  const mx=mean(xs),my=mean(ys); let num=0,dx=0,dy=0;
  for(let i=0;i<n;i++){{num+=(xs[i]-mx)*(ys[i]-my);dx+=(xs[i]-mx)**2;dy+=(ys[i]-my)**2;}}
  return (dx&&dy)?num/Math.sqrt(dx*dy):0;
}}

// ── Chart registry (destroy before recreate) ──────────────────────────────────
const CHARTS={{}};
function mkChart(id,cfg){{
  if(CHARTS[id]){{ CHARTS[id].destroy(); }}
  const canvas=document.getElementById(id);
  if(!canvas) return;
  CHARTS[id]=new Chart(canvas,cfg);
}}

// ── Shared axis defaults ──────────────────────────────────────────────────────
const gridColor = '#1e293b';
const xAxis = (opts={{}}) => ({{ ticks:{{font:{{size:7}},...(opts.ticks||{{}})}}, grid:{{color:gridColor}}, ...opts }});
const yAxis = (opts={{}}) => ({{ ticks:{{font:{{size:7}},...(opts.ticks||{{}})}}, grid:{{color:gridColor}}, ...opts }});

// ── Filter state ──────────────────────────────────────────────────────────────
let fBody='all', fEng='all', fFuel='all';
const filtered = () => RAW.filter(r=>
  (fBody==='all'||r['body-style']===fBody)&&
  (fEng ==='all'||r['engine-type']===fEng)&&
  (fFuel==='all'||r['fuel-type']===fFuel)
);

// ── Build filter dropdowns ────────────────────────────────────────────────────
function buildFilters(){{
  const bar=document.getElementById('statsFilters');
  const sel=(label,opts,cb)=>{{
    const wrap=document.createElement('div');
    wrap.style.cssText='display:flex;align-items:center;gap:8px';
    const lbl=document.createElement('span');
    lbl.textContent=label;
    lbl.style.cssText='font-family:Share Tech Mono,monospace;font-size:.62rem;color:#475569;letter-spacing:2px;text-transform:uppercase';
    const s=document.createElement('select');
    s.style.cssText='background:#111827;border:1.5px solid #1e293b;color:#e2e8f0;font-family:Share Tech Mono,monospace;font-size:.72rem;padding:5px 10px;border-radius:6px;cursor:pointer;outline:none';
    ['all',...opts].forEach(o=>s.appendChild(new Option(o==='all'?'All '+label:o.toUpperCase(),o)));
    s.addEventListener('change',()=>{{cb(s.value);renderAll();}});
    wrap.append(lbl,s); bar.appendChild(wrap);
  }};
  const uniq = k=>[...new Set(RAW.map(r=>r[k]).filter(Boolean))].sort();
  sel('Body',   uniq('body-style'),   v=>fBody=v);
  sel('Engine', uniq('engine-type'),  v=>fEng=v);
  sel('Fuel',   uniq('fuel-type'),    v=>fFuel=v);
}}

// ── KPI cards ─────────────────────────────────────────────────────────────────
function renderKPI(d){{
  const prices=num(d,'price'),hps=num(d,'horsepower'),mpgs=num(d,'avg-mpg'),sizes=num(d,'engine-size');
  const makes=[...new Set(d.map(r=>r.make).filter(Boolean))].length;
  const kpis=[
    ['Total Cars',    d.length,                 ''],
    ['Avg Price',     fmt$(mean(prices)),        ''],
    ['Avg HP',        fmtN(mean(hps),0)+' hp',  ''],
    ['Avg MPG',       fmtN(mean(mpgs),1)+' mpg',''],
    ['Median Price',  fmt$(median(prices)),      ''],
    ['Max HP',        fmtN(Math.max(...hps.length?hps:[0]),0)+' hp',''],
    ['Avg Eng.Sz',    fmtN(mean(sizes),0)+' cc',''],
    ['Unique Makes',  makes,                     ''],
  ];
  const row=document.getElementById('kpiRow');
  row.innerHTML='';
  kpis.forEach(([label,val])=>row.insertAdjacentHTML('beforeend',`
    <div style="flex:1;min-width:110px;background:#0a0e1a;border:1px solid #1e293b;border-radius:10px;padding:10px 14px;text-align:center">
      <div style="font-family:Share Tech Mono,monospace;font-size:1.1rem;font-weight:700;color:#38bdf8">${{val}}</div>
      <div style="font-size:.6rem;color:#475569;text-transform:uppercase;letter-spacing:.7px;margin-top:2px">${{label}}</div>
    </div>`));
  const countEl=document.getElementById('statsCount');
  if(countEl) countEl.textContent=`Showing ${{d.length}} of ${{RAW.length}} records`;
}}

// ── Histogram ─────────────────────────────────────────────────────────────────
function renderHist(id, vals, color){{
  if(!vals.length){{ mkChart(id,{{type:'bar',data:{{labels:[],datasets:[]}},options:{{}}}}); return; }}
  const {{labels,counts}}=hist(vals,22);
  const avg=mean(vals), mn=Math.min(...vals), bw=(Math.max(...vals)-mn)/22||1;
  const toIdx=v=>Math.min(Math.floor((v-mn)/bw),21);
  mkChart(id,{{
    type:'bar',
    data:{{ labels, datasets:[{{ data:counts, backgroundColor:color+'bb', borderColor:color, borderWidth:0.5, borderRadius:2 }}] }},
    options:{{
      responsive:true, maintainAspectRatio:false,
      plugins:{{ legend:{{display:false}}, tooltip:{{callbacks:{{title:i=>'≥ '+i[0].label,label:i=>i.formattedValue+' cars'}}}} }},
      scales:{{ x:xAxis({{ticks:{{maxTicksLimit:5}}}}), y:yAxis({{ticks:{{maxTicksLimit:4}}}}) }},
      animation:{{duration:300}}
    }},
    plugins:[{{
      id:'meanLines',
      afterDraw(chart){{
        const ctx=chart.ctx,xS=chart.scales.x,yS=chart.scales.y;
        [[avg,'#ffffff'],[median(vals),'#facc15']].forEach(([v,c])=>{{
          const px=xS.getPixelForValue(toIdx(v));
          ctx.save();ctx.strokeStyle=c;ctx.lineWidth=1.4;ctx.setLineDash([4,3]);
          ctx.beginPath();ctx.moveTo(px,yS.top);ctx.lineTo(px,yS.bottom);ctx.stroke();ctx.restore();
        }});
      }}
    }}]
  }});
}}

// ── Main render ───────────────────────────────────────────────────────────────
function renderAll(){{
  const d=filtered();
  renderKPI(d);

  renderHist('cHist0',num(d,'price'),      '#38bdf8');
  renderHist('cHist1',num(d,'horsepower'), '#f472b6');
  renderHist('cHist2',num(d,'avg-mpg'),    '#34d399');
  renderHist('cHist3',num(d,'engine-size'),'#fb923c');

  // ── Avg price by body style ──────────────────────────────────────────────
  const bodyKeys=Object.keys(BODY_C);
  mkChart('cBodyPrice',{{
    type:'bar',
    data:{{
      labels:bodyKeys.map(b=>b.charAt(0).toUpperCase()+b.slice(1)),
      datasets:[{{
        label:'Avg Price ($)',
        data:bodyKeys.map(b=>{{ const p=num(RAW.filter(r=>r['body-style']===b),'price'); return p.length?mean(p):null; }}),
        backgroundColor:bodyKeys.map(b=>BODY_C[b]+'99'),
        borderColor:bodyKeys.map(b=>BODY_C[b]),
        borderWidth:1.5,borderRadius:4
      }}]
    }},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:i=>'$'+Math.round(i.raw).toLocaleString()}}}}}},
      scales:{{x:xAxis(),y:yAxis({{ticks:{{callback:v=>'$'+v.toLocaleString(),maxTicksLimit:5}}}})}},
      animation:{{duration:300}}
    }}
  }});

  // ── HP & MPG by engine type ──────────────────────────────────────────────
  const engKeys=[...new Set(RAW.map(r=>r['engine-type']).filter(Boolean))].sort();
  mkChart('cEngHpMpg',{{
    type:'bar',
    data:{{
      labels:engKeys.map(k=>k.toUpperCase()),
      datasets:[
        {{label:'Avg HP',data:engKeys.map(e=>{{const v=num(d.filter(r=>r['engine-type']===e),'horsepower');return v.length?mean(v):null;}}),backgroundColor:'#f472b699',borderColor:'#f472b6',borderWidth:1.5,borderRadius:3}},
        {{label:'Avg MPG ×4',data:engKeys.map(e=>{{const v=num(d.filter(r=>r['engine-type']===e),'avg-mpg');return v.length?mean(v)*4:null;}}),backgroundColor:'#34d39999',borderColor:'#34d399',borderWidth:1.5,borderRadius:3}}
      ]
    }},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{labels:{{font:{{size:8}},boxWidth:12}}}}}},
      scales:{{x:xAxis(),y:yAxis({{ticks:{{maxTicksLimit:5}}}})}},
      animation:{{duration:300}}
    }}
  }});

  // ── Scatter: price vs hp ──────────────────────────────────────────────────
  const scatterDS=bodyKeys.map(b=>{{
    const pts=d.filter(r=>r['body-style']===b&&r.price&&r.horsepower).map(r=>{{return{{x:r.horsepower,y:r.price}};}});
    return{{label:b,data:pts,backgroundColor:BODY_C[b]+'bb',pointRadius:3.5,pointHoverRadius:5}};
  }});
  const spx=d.filter(r=>r.price&&r.horsepower).map(r=>r.horsepower);
  const spy=d.filter(r=>r.price&&r.horsepower).map(r=>r.price);
  const datasets=[...scatterDS];
  if(spx.length>2){{
    const mx=mean(spx),my=mean(spy); let n2=0,dn=0;
    spx.forEach((x,i)=>{{n2+=(x-mx)*(spy[i]-my);dn+=(x-mx)**2;}});
    const m=dn?n2/dn:0,b2=my-m*mx,xmn=Math.min(...spx),xmx=Math.max(...spx);
    datasets.unshift({{label:'Trend',data:[{{x:xmn,y:m*xmn+b2}},{{x:xmx,y:m*xmx+b2}}],type:'line',
      borderColor:'#ffffff55',borderWidth:1.5,borderDash:[5,4],pointRadius:0,fill:false,order:0}});
  }}
  mkChart('cScatter',{{
    type:'scatter',data:{{datasets}},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{labels:{{font:{{size:7}},boxWidth:10,padding:6}}}},tooltip:{{callbacks:{{label:i=>`HP:${{i.raw.x}}  ${{fmt$(i.raw.y)}}`}}}}}},
      scales:{{
        x:xAxis({{title:{{display:true,text:'Horsepower',font:{{size:7}}}}}}),
        y:yAxis({{title:{{display:true,text:'Price ($)',font:{{size:7}}}},ticks:{{callback:v=>'$'+v.toLocaleString(),maxTicksLimit:5}}}})
      }},
      animation:{{duration:300}}
    }}
  }});

  // ── Correlation bar ───────────────────────────────────────────────────────
  const corrFeatures=[['Horsepower','horsepower'],['Engine Size','engine-size'],['Curb Weight','curb-weight'],
    ['Width','width'],['Length','length'],['Wheel Base','wheel-base'],
    ['Avg MPG','avg-mpg'],['Peak RPM','peak-rpm'],['Compression','compression-ratio']];
  const corrVals=corrFeatures.map(([,key])=>{{
    const pairs=d.filter(r=>r[key]!=null&&r.price!=null&&!isNaN(r[key])&&!isNaN(r.price));
    return pairs.length>4?pearson(pairs.map(r=>r[key]),pairs.map(r=>r.price)):0;
  }});
  const corrSorted=[...corrFeatures.map(([l],i)=>{{return{{l,v:corrVals[i]}};}})]
    .sort((a,b)=>b.v-a.v);
  mkChart('cCorr',{{
    type:'bar',
    data:{{
      labels:corrSorted.map(x=>x.l),
      datasets:[{{
        label:'r with Price',
        data:corrSorted.map(x=>x.v),
        backgroundColor:corrSorted.map(x=>x.v>=0?'#38bdf888':'#f472b888'),
        borderColor:corrSorted.map(x=>x.v>=0?'#38bdf8':'#f472b6'),
        borderWidth:1.5,borderRadius:3
      }}]
    }},
    options:{{
      indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}}}},
      scales:{{
        x:xAxis({{min:-1,max:1,ticks:{{maxTicksLimit:6}}}}),
        y:yAxis({{ticks:{{font:{{size:7.5}}}}}})
      }},
      animation:{{duration:300}}
    }}
  }});

  // ── Makes horizontal bar ─────────────────────────────────────────────────
  const makeCounts={{}};
  d.forEach(r=>{{ if(r.make) makeCounts[r.make]=(makeCounts[r.make]||0)+1; }});
  const sortedMakes=Object.entries(makeCounts).sort((a,b)=>b[1]-a[1]).slice(0,15);
  mkChart('cMakes',{{
    type:'bar',
    data:{{
      labels:sortedMakes.map(([m])=>m),
      datasets:[{{data:sortedMakes.map(([,c])=>c),backgroundColor:'#38bdf888',borderColor:'#38bdf8',borderWidth:1.2,borderRadius:3}}]
    }},
    options:{{
      indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}}}},
      scales:{{x:xAxis({{ticks:{{maxTicksLimit:6}}}}),y:yAxis({{ticks:{{font:{{size:7.5}}}}}})}},
      animation:{{duration:300}}
    }}
  }});

  // ── Drive-wheel doughnut ─────────────────────────────────────────────────
  const dwCounts={{}};
  d.forEach(r=>{{ if(r['drive-wheels']) dwCounts[r['drive-wheels']]=(dwCounts[r['drive-wheels']]||0)+1; }});
  const dwKeys=Object.keys(dwCounts);
  mkChart('cDW',{{
    type:'doughnut',
    data:{{
      labels:dwKeys.map(k=>k.toUpperCase()),
      datasets:[{{data:dwKeys.map(k=>dwCounts[k]),backgroundColor:PAL.slice(0,dwKeys.length).map(c=>c+'cc'),borderColor:PAL.slice(0,dwKeys.length),borderWidth:2,hoverOffset:5}}]
    }},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{
        legend:{{position:'bottom',labels:{{font:{{size:9}},padding:10,boxWidth:11}}}},
        tooltip:{{callbacks:{{label:i=>i.label+': '+i.raw+' ('+Math.round(i.raw/d.length*100)+'%)'}}}}
      }},
      animation:{{duration:300}}
    }}
  }});
}}

buildFilters();
renderAll();
}})();
</script>
<!-- ##STATS_SECTION_END## -->
"""

# ── Inject before </body> ─────────────────────────────────────────────────────
assert "</body>" in raw, "Could not find </body> in HTML"
raw = raw.replace("</body>", SECTION + "\n</body>")
HTML_FILE.write_text(raw, encoding="utf-8")
print(f"Done. New size: {HTML_FILE.stat().st_size:,} bytes")
