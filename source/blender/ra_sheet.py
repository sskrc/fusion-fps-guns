# Contact sheet of preview renders:  python tools/ra_sheet.py <out png> <view list e.g. right,q> <module> [<module> ...]
# One row per module; columns = every mode x view found in out/RA_preview/<module>/.
import sys, os, glob, re
from PIL import Image, ImageDraw
out, views, mods = sys.argv[1], sys.argv[2].split(','), sys.argv[3:]
rows = []
for m in mods:
    fs = {}
    for f in glob.glob(os.path.join('out', 'RA_preview', m, '*.png')):
        k = re.match(r'.+?_([A-Z0-9]+)_([a-z]+)\.png$', os.path.basename(f))
        if k and k.group(2) in views:
            fs[(k.group(1) != 'READY', k.group(1), views.index(k.group(2)))] = f
    rows.append((m, [(k[1], views[k[2]], fs[k]) for k in sorted(fs)]))
W, H = 450, 310
sheet = Image.new('RGB', (W * max(len(r[1]) for r in rows), H * len(rows)), (40, 40, 40))
dr = ImageDraw.Draw(sheet)
for r, (m, cells) in enumerate(rows):
    for c, (mode, v, f) in enumerate(cells):
        sheet.paste(Image.open(f).resize((W, H)), (c * W, r * H))
        dr.text((c * W + 6, r * H + 4), '%s %s %s' % (m, mode, v), fill=(255, 255, 0))
sheet.save(out)
print(sheet.size)
