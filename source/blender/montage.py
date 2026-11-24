# Contact sheets from the verification frames:  python montage.py <verify dir>
import sys, os, glob, re
from PIL import Image, ImageDraw
d = sys.argv[1]
clips = {}
for f in glob.glob(os.path.join(d, 'clip_*.png')):
    m = re.match(r'clip_(.+)_(right|q)_(\d+)\.png', os.path.basename(f))
    clips.setdefault(m.group(1), {}).setdefault(m.group(2), []).append((int(m.group(3)), f))
for name, views in clips.items():
    rows = [sorted(v) for k, v in sorted(views.items())]
    w, h = Image.open(rows[0][0][1]).size
    w2, h2 = w * 2 // 3, h * 2 // 3
    sheet = Image.new('RGB', (w2 * len(rows[0]), h2 * len(rows)))
    dr = ImageDraw.Draw(sheet)
    for r, row in enumerate(rows):
        for c, (fr, f) in enumerate(row):
            sheet.paste(Image.open(f).resize((w2, h2)), (c * w2, r * h2))
            dr.text((c * w2 + 6, r * h2 + 4), '%s f%d' % (name, fr), fill=(255, 255, 0))
    sheet.save(os.path.join(d, 'sheet_%s.png' % name))
    print(name, sheet.size)
