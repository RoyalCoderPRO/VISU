import urllib.request

url = "http://localhost:8501/app/static/engine_explorer.html"
req = urllib.request.Request(url, headers={"Accept": "text/html,application/xhtml+xml"})
try:
    r = urllib.request.urlopen(req, timeout=10)
    content = r.read()
    print("Status:", r.status)
    print("Content-Type:", r.headers.get("Content-Type"))
    print("Content-Length:", len(content))
    print("First 400 bytes:", content[:400].decode("utf-8", errors="replace"))
except Exception as e:
    print("Error:", e)

