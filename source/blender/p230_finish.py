# Headless Blender: Fusion per-part STL + manifest -> UV, baked PBR textures, bone rig, animation clips,
# interference check, verification renders, GLB / FBX / .blend.
# blender -b --python p230_finish.py -- <src dir with manifest.json> <out dir> [res=2048] [nobake]
import bpy, bmesh, json, os, sys, math
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

args = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT = os.path.abspath(args[0]), os.path.abspath(args[1])
RES = 2048
NOBAKE = 'nobake' in args
for a in args[2:]:
    if a.startswith('res='):
        RES = int(a[4:])
os.makedirs(os.path.join(OUT, 'textures'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'verify'), exist_ok=True)
MAN = json.load(open(os.path.join(SRC, 'manifest.json'), encoding='utf-8'))
GROUPS = MAN['groups']
FPS = 30

AXIS = Matrix(((0, 0, -1, 0), (-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))   # model(X fwd,Y up,Z right) -> Blender(-Y fwd,Z up)
T = AXIS @ Matrix.Scale(0.001, 4)
TI = T.inverted()

# ------------------------------------------------------------------ animation clips (fractions of each group's motion)
SA = 0.55   # trigger rest position in single action
F_T = [(0, SA), (2, 1), (8, 1), (15, SA)]
F_H = [(0, 1), (2, 1), (3, 0), (5, 1), (15, 1)]
MAG = [(0, 0), (4, 0), (16, 2.4), (30, 2.4), (44, 0.05), (47, 0)]
CATCH = [(0, 0), (4, 1), (10, 1), (14, 0), (37, 0), (40, 1), (46, 1), (49, 0)]
CLIPS = [
    ('Idle', 2, {}),
    ('Trigger_DA_Dry', 22, dict(trigger=[(0, 0), (9, 1), (13, 1), (21, 0)], hammer=[(0, 0), (9, 0.85), (10, 0), (21, 0)])),
    ('Fire_DA', 26, dict(trigger=[(0, 0), (9, 1), (16, 1), (25, SA)], hammer=[(0, 0), (9, 0.85), (10, 0), (12, 1), (25, 1)],
                         slide=[(0, 0), (10, 0), (12, 1), (16, 0), (25, 0)])),
    ('Fire_SA', 16, dict(trigger=F_T, hammer=F_H, slide=[(0, 0), (3, 0), (5, 1), (9, 0), (15, 0)])),
    ('Fire_SA_Last', 16, dict(trigger=F_T, hammer=F_H, slide=[(0, 0), (3, 0), (5, 1), (8, 0.92), (15, 0.92)], round=[(0, 0), (15, 0)])),
    ('Reload_Empty', 70, dict(slide=[(0, 0.92), (52, 0.92), (56, 1), (59, 0), (69, 0)], hammer=[(0, 1), (69, 1)],
                              trigger=[(0, SA), (69, SA)], mag_catch=CATCH + [(69, 0)], magazine=MAG + [(69, 0)],
                              round=[(0, 0), (22, 0), (23, 1), (69, 1)])),
    ('Reload_Tactical', 56, dict(hammer=[(0, 1), (55, 1)], trigger=[(0, SA), (55, SA)], mag_catch=CATCH + [(55, 0)],
                                 magazine=MAG + [(55, 0)])),
    ('Decock', 16, dict(hammer=[(0, 1), (4, 1), (7, 0), (15, 0)], decocker=[(0, 0), (4, 1), (8, 1), (14, 0), (15, 0)],
                        trigger=[(0, SA), (4, SA), (10, 0), (15, 0)])),
    ('Slide_Rack', 24, dict(slide=[(0, 0), (8, 1), (11, 1), (14, 0), (23, 0)], hammer=[(0, 0), (8, 1), (23, 1)],
                            trigger=[(0, 0), (8, SA), (23, SA)])),
]
HAMMER_OVERCOCK = 1.0


def interp(keys, f):
    if not keys:
        return 0.0
    if f <= keys[0][0]:
        return keys[0][1]
    for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
        if f <= f1:
            t = (f - f0) / float(f1 - f0)
            t = t * t * (3 - 2 * t)
            return v0 + (v1 - v0) * t
    return keys[-1][1]


def state(clip, f):
    st = {g: interp(clip.get(g, []), f) for g in GROUPS}
    sl = st.get('slide', 0.0)
    t = min(1.0, sl / 0.3)
    st['round'] = interp(clip.get('round', [(0, 1)]), f)
    st['hammer'] = max(st.get('hammer', 0.0), HAMMER_OVERCOCK * t * t * (3 - 2 * t))   # slide pushes the hammer down
    return st


def delta_model(group, v):
    g = GROUPS[group]
    if g['type'] == 'translate':
        return Matrix.Translation(Vector(g['axis']) * g['travel'] * v)
    if g['type'] == 'rotate':
        pv = Vector(g['pivot'])
        return Matrix.Translation(pv) @ Matrix.Rotation(math.radians(g['angle'] * v), 4, Vector(g['axis'])) @ Matrix.Translation(-pv)
    return Matrix.Identity(4)


# ------------------------------------------------------------------ import
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS
objs = []
for p in MAN['parts']:
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=os.path.join(SRC, 'parts', p['file']))
    o = (set(bpy.data.objects) - before).pop()
    o.name = p['name']
    o['group'], o['mat'] = p['group'], p['mat']
    me = o.data
    me.transform(o.matrix_world)
    o.matrix_world = Matrix.Identity(4)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    objs.append(o)
xs = [v.co.x for o in objs for v in o.data.vertices]
ys = [v.co.y for o in objs for v in o.data.vertices]
print('MODEL_BBOX_MM x %.1f..%.1f (len %.1f)  y %.1f..%.1f (height %.1f)' % (min(xs), max(xs), max(xs) - min(xs), min(ys), max(ys), max(ys) - min(ys)))

# ------------------------------------------------------------------ interference check (model space, mm)
SKIP = {('mag_catch', 'frame'), ('decocker', 'frame')}


def bvh_of(o, M):
    return BVHTree.FromPolygons([M @ v.co for v in o.data.vertices], [tuple(p.vertices) for p in o.data.polygons])


report = {}
for cname, n, clip in CLIPS:
    for f in range(n):
        st = state(clip, f)
        trees = {o.name: bvh_of(o, delta_model(o['group'], st[o['group']])) for o in objs}
        for a in objs:
            if a['group'] == 'frame':
                continue
            for b in objs:
                if b['group'] == a['group'] or (b['group'] != 'frame' and b.name < a.name):
                    continue
                if (a.name, b.name) in SKIP or (a['group'], b.name) in SKIP:
                    continue
                ov = trees[a.name].overlap(trees[b.name])
                if ov:
                    key = (a.name, b.name)
                    if key not in report:
                        M = delta_model(a['group'], st[a['group']])
                        cs = [M @ a.data.polygons[i].center for i, j in ov]
                        print('  FIRST %s x %s @%s f%d n=%d x[%.1f..%.1f] y[%.1f..%.1f] z[%.1f..%.1f] state=%s' % (
                            a.name, b.name, cname, f, len(ov), min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs),
                            max(c.y for c in cs), min(c.z for c in cs), max(c.z for c in cs),
                            {k: round(v, 2) for k, v in st.items() if v}))
                    r = report.setdefault(key, {})
                    r.setdefault(cname, []).append(f)
print('INTERFERENCE_REPORT pairs=%d' % len(report))
for (a, b), r in sorted(report.items()):
    print('  HIT %s x %s : %s' % (a, b, '; '.join('%s f%d-%d(%d)' % (c, min(fr), max(fr), len(fr)) for c, fr in r.items())))
json.dump({'%s|%s' % k: v for k, v in report.items()}, open(os.path.join(OUT, 'verify', 'interference.json'), 'w'), indent=1)

if 'checkonly' in args:
    sys.exit(0)

# ------------------------------------------------------------------ to Blender space, shading
for o in objs:
    o.data.transform(T)
    for poly in o.data.polygons:
        poly.use_smooth = True
    o.data.set_sharp_from_angle(angle=math.radians(32))
    vg = o.vertex_groups.new(name='round' if o.name.startswith('dummy') else ('Root' if o['group'] == 'frame' else o['group']))
    vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    o.vertex_groups.new(name='part:' + o.name).add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')


# ------------------------------------------------------------------ procedural materials (bake sources)
def lin(c):
    return tuple(pow(v / 255.0, 2.2) for v in c) + (1.0,)


PROC = {}


def make_proc(key, c, checker=False):
    m = bpy.data.materials.new('src_' + key)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    bsdf = N['Principled BSDF']
    metal = c['metal']
    wear = 0.45 if key in ('steel', 'steel_dark') else (0.35 if key == 'alloy' else 0.0)
    tc = N.new('ShaderNodeTexCoord')
    geo = N.new('ShaderNodeNewGeometry')
    n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 260; n1.inputs['Detail'].default_value = 5
    n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 40; n2.inputs['Detail'].default_value = 3
    L.new(tc.outputs['Object'], n1.inputs['Vector']); L.new(tc.outputs['Object'], n2.inputs['Vector'])
    bev = N.new('ShaderNodeBevel'); bev.samples = 8; bev.inputs['Radius'].default_value = 0.0004
    dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
    L.new(bev.outputs['Normal'], dot.inputs[0]); L.new(geo.outputs['Normal'], dot.inputs[1])
    edge = N.new('ShaderNodeMapRange'); edge.inputs['From Min'].default_value = 0.995; edge.inputs['From Max'].default_value = 0.9
    L.new(dot.outputs['Value'], edge.inputs['Value'])
    nm = N.new('ShaderNodeMapRange'); nm.inputs['From Min'].default_value = 0.38; nm.inputs['From Max'].default_value = 0.62
    L.new(n1.outputs[0], nm.inputs['Value'])
    wm = N.new('ShaderNodeMath'); wm.operation = 'MULTIPLY'
    L.new(edge.outputs[0], wm.inputs[0]); L.new(nm.outputs[0], wm.inputs[1])
    wa = N.new('ShaderNodeMath'); wa.operation = 'MULTIPLY'; wa.inputs[1].default_value = wear
    L.new(wm.outputs[0], wa.inputs[0])
    # base colour with slight large-scale variation, then edge wear
    var = N.new('ShaderNodeMix'); var.data_type = 'RGBA'
    b = lin(c['rgb'])
    var.inputs[6].default_value = b
    var.inputs[7].default_value = tuple(min(1.0, v * 1.5 + 0.004) for v in b[:3]) + (1.0,)
    L.new(n2.outputs[0], var.inputs[0])
    col = N.new('ShaderNodeMix'); col.data_type = 'RGBA'
    col.inputs[7].default_value = (0.16, 0.16, 0.175, 1.0)
    L.new(var.outputs[2], col.inputs[6]); L.new(wa.outputs[0], col.inputs[0])
    L.new(col.outputs[2], bsdf.inputs['Base Color'])
    # roughness: base + fine noise, smoother where worn
    r1 = N.new('ShaderNodeMapRange'); r1.inputs['To Min'].default_value = c['rough'] - 0.07; r1.inputs['To Max'].default_value = c['rough'] + 0.09
    L.new(n1.outputs[0], r1.inputs['Value'])
    r2 = N.new('ShaderNodeMix'); r2.data_type = 'FLOAT'
    r2.inputs[3].default_value = 0.22
    L.new(r1.outputs[0], r2.inputs[2]); L.new(wa.outputs[0], r2.inputs[0])
    L.new(r2.outputs[0], bsdf.inputs['Roughness'])
    bsdf.inputs['Metallic'].default_value = metal
    if checker:
        waves = []
        for ang in (0.6, -0.6):
            mp = N.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (ang, 0, 0)
            L.new(tc.outputs['Object'], mp.inputs['Vector'])
            w = N.new('ShaderNodeTexWave'); w.wave_type = 'BANDS'; w.bands_direction = 'Z'; w.inputs['Scale'].default_value = 230
            L.new(mp.outputs[0], w.inputs['Vector'])
            waves.append(w)
        mx = N.new('ShaderNodeMath'); mx.operation = 'MINIMUM'
        L.new(waves[0].outputs[1], mx.inputs[0]); L.new(waves[1].outputs[1], mx.inputs[1])
        sx = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Normal'], sx.inputs[0])
        ab = N.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; L.new(sx.outputs['X'], ab.inputs[0])
        sm = N.new('ShaderNodeMapRange'); sm.inputs['From Min'].default_value = 0.8; sm.inputs['From Max'].default_value = 0.93
        L.new(ab.outputs[0], sm.inputs['Value'])
        hm = N.new('ShaderNodeMath'); hm.operation = 'MULTIPLY'
        L.new(mx.outputs[0], hm.inputs[0]); L.new(sm.outputs[0], hm.inputs[1])
        bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 1.0; bump.inputs['Distance'].default_value = 0.0005
        L.new(hm.outputs[0], bump.inputs['Height']); L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    em = N.new('ShaderNodeEmission'); em.name = 'bake_emit'
    img = N.new('ShaderNodeTexImage'); img.name = 'bake_target'
    N.active = img
    PROC[m.name] = dict(mat=m, color=col.outputs[2], metal=metal, bsdf=bsdf, em=em, out=N['Material Output'], img=img)
    return m


mats = {}
for o in objs:
    key = o['mat'] + ('_grip' if o.name.startswith('grip_panel') else '')
    if key not in mats:
        mats[key] = make_proc(key, MAN['materials'][o['mat']], checker=key.endswith('_grip'))
    o.data.materials.clear()
    o.data.materials.append(mats[key])

# ------------------------------------------------------------------ join + UV
bpy.ops.object.select_all(action='DESELECT')
for o in objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
bpy.ops.object.join()
gun = bpy.context.view_layer.objects.active
gun.name = 'P230'
gun.data.name = 'P230'
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003)
bpy.ops.object.mode_set(mode='OBJECT')
print('MESH verts=%d tris=%d' % (len(gun.data.vertices), sum(len(p.vertices) - 2 for p in gun.data.polygons)))

# ------------------------------------------------------------------ bake
IMGS = {}


def bake(kind):
    img = bpy.data.images.new('P230_' + kind, RES, RES, alpha=False, is_data=(kind != 'BaseColor'))
    IMGS[kind] = img
    for d in PROC.values():
        nt = d['mat'].node_tree
        d['img'].image = img
        nt.nodes.active = d['img']
        for l in list(d['out'].inputs['Surface'].links):
            nt.links.remove(l)
        if kind in ('BaseColor', 'Metallic'):
            for l in list(d['em'].inputs['Color'].links):
                nt.links.remove(l)
            if kind == 'BaseColor':
                nt.links.new(d['color'], d['em'].inputs['Color'])
            else:
                d['em'].inputs['Color'].default_value = (d['metal'],) * 3 + (1,)
            nt.links.new(d['em'].outputs[0], d['out'].inputs['Surface'])
        else:
            nt.links.new(d['bsdf'].outputs[0], d['out'].inputs['Surface'])
    btype = dict(BaseColor='EMIT', Metallic='EMIT', Roughness='ROUGHNESS', Normal='NORMAL', AO='AO')[kind]
    sc.cycles.samples = 48 if kind == 'AO' else 12
    bpy.ops.object.bake(type=btype, margin=6, use_clear=True)
    img.filepath_raw = os.path.join(OUT, 'textures', 'P230_%s.png' % kind)
    img.file_format = 'PNG'
    img.save()
    px = img.pixels[:]
    n = len(px) // 4
    step = max(1, n // 20000)
    vals = [(px[i * 4] + px[i * 4 + 1] + px[i * 4 + 2]) / 3 for i in range(0, n, step)]
    print('BAKE %s mean=%.3f min=%.3f max=%.3f' % (kind, sum(vals) / len(vals), min(vals), max(vals)))


final = bpy.data.materials.new('P230')
final.use_nodes = True
if not NOBAKE:
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    bpy.ops.object.select_all(action='DESELECT')
    gun.select_set(True)
    bpy.context.view_layer.objects.active = gun
    for kind in ('BaseColor', 'Metallic', 'Roughness', 'Normal', 'AO'):
        bake(kind)
    nt = final.node_tree
    bsdf = nt.nodes['Principled BSDF']

    def tex(kind):
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = IMGS[kind]
        return t
    nt.links.new(tex('BaseColor').outputs[0], bsdf.inputs['Base Color'])
    nt.links.new(tex('Metallic').outputs[0], bsdf.inputs['Metallic'])
    nt.links.new(tex('Roughness').outputs[0], bsdf.inputs['Roughness'])
    nmap = nt.nodes.new('ShaderNodeNormalMap')
    nt.links.new(tex('Normal').outputs[0], nmap.inputs['Color'])
    nt.links.new(nmap.outputs[0], bsdf.inputs['Normal'])
    gun.data.materials.clear()
    gun.data.materials.append(final)
    for poly in gun.data.polygons:
        poly.material_index = 0

# ------------------------------------------------------------------ per-part GLB for the web viewer (no skin, shared texture)
site = gun.copy()
site.data = gun.data.copy()
sc.collection.objects.link(site)
bpy.ops.object.select_all(action='DESELECT')
site.select_set(True)
bpy.context.view_layer.objects.active = site
part_objs = []
for name in [v.name for v in site.vertex_groups if v.name.startswith('part:')]:
    bpy.ops.object.select_all(action='DESELECT')
    site.select_set(True)
    bpy.context.view_layer.objects.active = site
    bpy.ops.object.vertex_group_set_active(group=name)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.vertex_group_select()
    bpy.ops.mesh.separate(type='SELECTED')
    bpy.ops.object.mode_set(mode='OBJECT')
    new = [o for o in bpy.context.selected_objects if o is not site]
    if new:
        new[0].name = name[5:]
        new[0].data.name = name[5:]
        part_objs.append(new[0])
print('SITE_PARTS', len(part_objs), 'leftover verts', len(site.data.vertices))
bpy.data.objects.remove(site, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
for o in part_objs:
    o.vertex_groups.clear()
    o.select_set(True)
bpy.context.view_layer.objects.active = part_objs[0]
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'P230_parts.glb'), export_format='GLB', use_selection=True,
                          export_animations=False, export_skins=False, export_yup=True)
for o in part_objs:
    bpy.data.objects.remove(o, do_unlink=True)
for v in [v for v in gun.vertex_groups if v.name.startswith('part:')]:
    gun.vertex_groups.remove(v)

# ------------------------------------------------------------------ rig
HEADS = dict(slide=(80, 10, 0), magazine=(18, -45, 0), mag_catch=(-7, -88, 0))
arm_data = bpy.data.armatures.new('P230_Rig')
arm = bpy.data.objects.new('P230_Rig', arm_data)
sc.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
rb = arm_data.edit_bones.new('Root')
rb.head, rb.tail = (0, 0, 0), (0, -0.03, 0)
for g, d in GROUPS.items():
    if g == 'frame':
        continue
    eb = arm_data.edit_bones.new(g)
    h = T @ Vector(d.get('pivot', HEADS.get(g, (0, 0, 0))))
    eb.head, eb.tail = h, h + Vector((0, -0.02, 0))
    eb.parent = rb
eb = arm_data.edit_bones.new('round')
h = T @ Vector((30, -5.3, 0))
eb.head, eb.tail = h, h + Vector((0, -0.02, 0))
eb.parent = rb
bpy.ops.object.mode_set(mode='OBJECT')
gun.parent = arm
gun.modifiers.new('Armature', 'ARMATURE').object = arm
for pb in arm.pose.bones:
    pb.rotation_mode = 'QUATERNION'


def apply_state(st, frame=None):
    for g in GROUPS:
        if g == 'frame':
            continue
        pb = arm.pose.bones[g]
        pb.matrix = (T @ delta_model(g, st[g]) @ TI) @ pb.bone.matrix_local
        if frame is not None:
            pb.keyframe_insert('location', frame=frame)
            pb.keyframe_insert('rotation_quaternion', frame=frame)
    pb = arm.pose.bones['round']          # dummy cartridge rides with the magazine; scaled away while the magazine is empty
    pb.matrix = (T @ delta_model('magazine', st['magazine']) @ TI) @ pb.bone.matrix_local
    k = max(st.get('round', 1.0), 0.001)
    pb.scale = (k, k, k)
    if frame is not None:
        pb.keyframe_insert('location', frame=frame)
        pb.keyframe_insert('rotation_quaternion', frame=frame)
        pb.keyframe_insert('scale', frame=frame)


# ------------------------------------------------------------------ verification render setup
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'
cam.data.clip_start = 0.001
sc.camera = cam
for i, (d, e) in enumerate([((-1, -0.6, 1), 5.0), ((1, -0.5, 0.8), 5.0), ((0, 1, 0.6), 2.5), ((-0.3, 0.2, -1), 2.0)]):
    sun = bpy.data.objects.new('sun%d' % i, bpy.data.lights.new('sun%d' % i, 'SUN'))
    sun.data.energy = e
    sun.data.angle = 0.6
    sun.rotation_euler = Vector(d).to_track_quat('Z', 'Y').to_euler()
    sc.collection.objects.link(sun)
w = bpy.data.worlds.new('w')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.5, 0.52, 0.55, 1)
w.node_tree.nodes['Background'].inputs[1].default_value = 1.6
sc.world = w
for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        sc.render.engine = eng
        break
    except Exception:
        pass
VIEWS = dict(right=(-1, 0, 0), left=(1, 0, 0), q=(-0.8, -0.55, 0.5), ql=(0.8, -0.6, 0.45), rear=(-0.5, 1, 0.45), top=(-0.3, -0.05, 1))


def shot(path, view, scale=0.27, res=(900, 640), center=(0, -0.065, -0.045)):
    c = Vector(center)
    cam.location = c + Vector(VIEWS[view]).normalized() * 0.8
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = scale
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


st0 = state({}, 0)
st0['round'] = 1.0
apply_state(st0)
bpy.context.view_layer.update()
VIEWS['below'] = (-0.25, -0.5, -1)
VIEWS['front'] = (-0.45, -1, 0.2)
for v in ('right', 'left', 'q', 'ql', 'rear', 'top', 'below', 'front'):
    shot(os.path.join(OUT, 'verify', 'beauty_%s.png' % v), v, scale=0.23, res=(1600, 1100))

# ------------------------------------------------------------------ clips -> actions -> NLA
arm.animation_data_create()
ad = arm.animation_data
acts = []
for cname, n, clip in CLIPS:
    act = bpy.data.actions.new(cname)
    ad.action = act
    for f in range(n):
        apply_state(state(clip, f), frame=f)
    picks = sorted(set([0, n - 1] + [int(round(i * (n - 1) / 5.0)) for i in range(6)]))
    for f in picks:
        sc.frame_set(f)
        shot(os.path.join(OUT, 'verify', 'clip_%s_right_%03d.png' % (cname, f)), 'right', scale=0.36, res=(520, 400),
             center=(0, -0.06, -0.06))
        shot(os.path.join(OUT, 'verify', 'clip_%s_q_%03d.png' % (cname, f)), 'left' if cname == 'Decock' else 'right',
             scale=0.15, res=(520, 400), center=(0, -0.03, -0.002))
    acts.append((cname, n, act))
ad.action = None
for cname, n, act in acts:
    tr = ad.nla_tracks.new()
    tr.name = cname
    st = tr.strips.new(cname, 0, act)
    st.name = cname
    try:
        if getattr(st, 'action_slot', None) is None and len(act.slots):
            st.action_slot = act.slots[0]
    except Exception as e:
        print('slot assign note:', e)
    tr.mute = True
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
sc.frame_set(0)
print('ACTIONS', [(a.name, len(a.fcurves) if hasattr(a, 'fcurves') else -1) for _, _, a in acts])

# ------------------------------------------------------------------ export
for o in list(bpy.data.objects):
    if o.type in ('CAMERA', 'LIGHT'):
        o.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'P230.blend'))
bpy.ops.object.select_all(action='DESELECT')
gun.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
for tr in ad.nla_tracks:
    tr.mute = False
try:
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'P230.glb'), export_format='GLB', use_selection=True,
                              export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True,
                              export_force_sampling=True, export_yup=True)
    print('GLB_OK')
except Exception as e:
    print('GLB export failed:', e)
try:
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, 'P230.fbx'), use_selection=True, add_leaf_bones=False,
                             bake_anim=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=False,
                             apply_scale_options='FBX_SCALE_UNITS', path_mode='COPY', embed_textures=True)
    print('FBX_OK')
except Exception as e:
    print('FBX export failed:', e)
print('FINISH_DONE')
