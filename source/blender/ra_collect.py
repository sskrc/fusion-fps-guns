# Collect the finished RogueArena models into RogueArena_models/<ID>/ and build overview sheets.  Run from the workspace root.
import glob, os, shutil
from PIL import Image, ImageDraw
DST = 'RogueArena_models'
ids = sorted(os.path.basename(os.path.dirname(os.path.dirname(p))) for p in glob.glob('out/RA/RA*/final/rig.json'))
W, H = 600, 413
for view, name in (('q', 'overview'), ('right', 'overview_side')):
    sheet = Image.new('RGB', (W * 4, H * 3), (40, 46, 56))
    d = ImageDraw.Draw(sheet)
    for i, g in enumerate(ids):
        sheet.paste(Image.open('out/RA/%s/final/verify/mode_READY_%s.png' % (g, view)).resize((W, H)), ((i % 4) * W, (i // 4) * H))
        d.text(((i % 4) * W + 8, (i // 4) * H + 6), g, fill=(255, 255, 0))
    os.makedirs(DST, exist_ok=True)
    sheet.save(os.path.join(DST, 'RogueArena_%s.png' % name))
for g in ids:
    src, dst = 'out/RA/%s/final' % g, os.path.join(DST, g)
    os.makedirs(os.path.join(dst, 'textures'), exist_ok=True)
    for f in (g + '.glb', g + '.fbx'):
        shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
    for f in glob.glob(os.path.join(src, 'textures', '*.png')):
        shutil.copy2(f, os.path.join(dst, 'textures', os.path.basename(f)))
    shutil.copy2(os.path.join(src, 'verify', 'mode_READY_q.png'), os.path.join(dst, g + '_render.png'))
    for f in ('.f3d', '.step'):
        shutil.copy2('out/RA/%s/%s%s' % (g, g, f), os.path.join(dst, g + f))
print(len(ids), 'guns ->', DST)
