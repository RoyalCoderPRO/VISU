import pathlib
raw = pathlib.Path("engine_explorer.html").read_text(encoding="utf-8")
checks = [
    ("START marker", "##STATS_SECTION_START##"),
    ("END marker",   "##STATS_SECTION_END##"),
    ("Chart.js CDN", "chart.umd.min.js"),
    ("cHist0 canvas", 'id="cHist0"'),
    ("cDW canvas",    'id="cDW"'),
    ("RAW data var",  "const RAW ="),
]
for label, token in checks:
    print(label, ":", token in raw)
print("File chars:", len(raw))

