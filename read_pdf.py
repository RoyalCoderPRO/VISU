import pymupdf
doc = pymupdf.open("Component 1.pdf")
print(f"Pages: {len(doc)}")
for i, page in enumerate(doc):
    mat = pymupdf.Matrix(2, 2)  # 2x zoom for clarity
    pix = page.get_pixmap(matrix=mat)
    out = f"page_{i+1}.png"
    pix.save(out)
    print(f"Saved {out} ({pix.width}x{pix.height})")
