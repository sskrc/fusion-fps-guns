# Headless Blender: ORBIS per-part STL + manifest -> interference check, UV, baked PBR + emission textures,
# bone rig, transformation clips, verification renders, GLB / FBX / .blend, plus a per-part GLB and rig.json for the web viewer.
# blender -b --python orbis_finish.py -- <Orbis data dir> <src dir with manifest.json> <out dir> [res=2048] [checkonly]
import bpy, bmesh, json, os, sys, math
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

args = sys.argv[sys.argv.index('--') + 1:]
sys.path.insert(0, os.path.abspath(args[0]))
import orbis_data as D
SRC, OUT = os.path.abspath(args[1]), os.path.abspath(args[2])
RES = 2048
for a in args[3:]:
    if a.startswith('res='):
        RES = int(a[4:])
NAME = 'ORBIS'
os.makedirs(os.path.join(OUT, 'textures'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'verify'), exist_ok=True)
MAN = json.load(open(os.path.join(SRC, 'manifest.json'), encoding='utf-8'))
GROUPS = D.expanded_groups()

AXIS = Matrix(((0, 0, -1, 0), (-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))   # model(X fwd,Y up,Z right) -> Blender(-Y fwd,Z up)
T = AXIS @ Matrix.Scale(0.001, 4)
TI = T.inverted()


def group_matrix(group, st):
    M = Matrix.Identity(4)
    for step in GROUPS[group]['steps']:
        v = st.get(step['dof'], 0.0)
        if step['type'] == 'move':
            M = M @ Matrix.Translation(Vector(step['axis']) * step['travel'] * v)
        else:
            pv = Vector(step['pivot'])
            M = M @ Matrix.Translation(pv) @ Matrix.Rotation(math.radians(step['angle'] * v), 4, Vector(step['axis'])) @ Matrix.Translation(-pv)
    return M


# ------------------------------------------------------------------ import
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = D.FPS
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
for ax, nm in ((0, 'x'), (1, 'y'), (2, 'z')):
    vals = [v.co[ax] for o in objs for v in o.data.vertices]
    print('MODEL_BBOX_MM %s %.1f..%.1f (%.1f)' % (nm, min(vals), max(vals), max(vals) - min(vals)))

# ------------------------------------------------------------------ interference check over every clip frame (model space, mm)
report = {}
for clip in D.CLIPS:
    cname, n, _ = clip
    for f in range(n):
        st = D.clip_state(clip, f)
        mats_g = {g: group_matrix(g, st) for g in GROUPS}
        trees = {}
        for o in objs:
            M = mats_g[o['group']]
            trees[o.name] = BVHTree.FromPolygons([M @ v.co for v in o.data.vertices], [tuple(p.vertices) for p in o.data.polygons])
        for i, a in enumerate(objs):
            for b in objs[i + 1:]:
                if a['group'] == b['group'] or a.name.endswith('_pin') or b.name.endswith('_pin'):
                    continue
                ov = trees[a.name].overlap(trees[b.name])
                if ov:
                    key = (a.name, b.name)
                    if key not in report:
                        M = mats_g[a['group']]
                        cs = [M @ a.data.polygons[i2].center for i2, j2 in ov]
                        print('  FIRST %s x %s @%s f%d n=%d x[%.0f..%.0f] y[%.0f..%.0f] z[%.0f..%.0f]' % (
                            a.name, b.name, cname, f, len(ov), min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs),
                            max(c.y for c in cs), min(c.z for c in cs), max(c.z for c in cs)))
                    report.setdefault(key, {}).setdefault(cname, []).append(f)
print('INTERFERENCE_REPORT pairs=%d' % len(report))
for (a, b), r in sorted(report.items()):
    print('  HIT %s x %s : %s' % (a, b, '; '.join('%s f%d-%d(%d)' % (c, min(fr), max(fr), len(fr)) for c, fr in r.items())))
json.dump({'%s|%s' % k: v for k, v in report.items()}, open(os.path.join(OUT, 'verify', 'interference.json'), 'w'), indent=1)
if 'checkonly' in args:
    sys.exit(0)

# ------------------------------------------------------------------ to Blender space, shading, groups
for o in objs:
    o.data.transform(T)
    for poly in o.data.polygons:
        poly.use_smooth = True
    o.data.set_sharp_from_angle(angle=math.radians(32))
    o.vertex_groups.new(name='Root' if o['group'] == 'frame' else o['group']).add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    o.vertex_groups.new(name='part:' + o.name).add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')


# ------------------------------------------------------------------ procedural materials (bake sources)
def lin(c):
    return tuple(pow(v / 255.0, 2.2) for v in c) + (1.0,)


PROC = {}


def make_proc(key, c):
    m = bpy.data.materials.new('src_' + key)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    bsdf = N['Principled BSDF']
    wear = dict(core=0.4, dark=0.45).get(key, 0.0)
    tc = N.new('ShaderNodeTexCoord')
    geo = N.new('ShaderNodeNewGeometry')
    n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 220; n1.inputs['Detail'].default_value = 5
    n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 26; n2.inputs['Detail'].default_value = 3
    L.new(tc.outputs['Object'], n1.inputs['Vector']); L.new(tc.outputs['Object'], n2.inputs['Vector'])
    bev = N.new('ShaderNodeBevel'); bev.samples = 8; bev.inputs['Radius'].default_value = 0.0006
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
    var = N.new('ShaderNodeMix'); var.data_type = 'RGBA'
    b = lin(c['rgb'])
    k = 0.9 if key == 'armor' else 1.5
    var.inputs[6].default_value = b
    var.inputs[7].default_value = tuple(min(1.0, v * k + (0.0 if key == 'armor' else 0.004)) for v in b[:3]) + (1.0,)
    L.new(n2.outputs[0], var.inputs[0])
    col = N.new('ShaderNodeMix'); col.data_type = 'RGBA'
    col.inputs[7].default_value = (0.2, 0.2, 0.22, 1.0)
    L.new(var.outputs[2], col.inputs[6]); L.new(wa.outputs[0], col.inputs[0])
    L.new(col.outputs[2], bsdf.inputs['Base Color'])
    r1 = N.new('ShaderNodeMapRange'); r1.inputs['To Min'].default_value = c['rough'] - 0.06; r1.inputs['To Max'].default_value = c['rough'] + 0.08
    L.new(n1.outputs[0], r1.inputs['Value'])
    L.new(r1.outputs[0], bsdf.inputs['Roughness'])
    bsdf.inputs['Metallic'].default_value = c['metal']
    em = N.new('ShaderNodeEmission'); em.name = 'bake_emit'
    img = N.new('ShaderNodeTexImage'); img.name = 'bake_target'
    N.active = img
    PROC[m.name] = dict(mat=m, color=col.outputs[2], metal=c['metal'], bsdf=bsdf, em=em, out=N['Material Output'], img=img,
                        emit=(lin(c['rgb']) if c.get('emit') else (0, 0, 0, 1)))
    return m


mats = {}
for o in objs:
    if o['mat'] not in mats:
        mats[o['mat']] = make_proc(o['mat'], D.MATERIALS[o['mat']])
    o.data.materials.clear()
    o.data.materials.append(mats[o['mat']])

# ------------------------------------------------------------------ join + UV
bpy.ops.object.select_all(action='DESELECT')
for o in objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
bpy.ops.object.join()
gun = bpy.context.view_layer.objects.active
gun.name = NAME
gun.data.name = NAME
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003)
bpy.ops.object.mode_set(mode='OBJECT')
print('MESH verts=%d tris=%d' % (len(gun.data.vertices), sum(len(p.vertices) - 2 for p in gun.data.polygons)))

# ------------------------------------------------------------------ bake
IMGS = {}


def bake(kind):
    img = bpy.data.images.new('%s_%s' % (NAME, kind), RES, RES, alpha=False, is_data=(kind not in ('BaseColor', 'Emission')))
    IMGS[kind] = img
    for d in PROC.values():
        nt = d['mat'].node_tree
        d['img'].image = img
        nt.nodes.active = d['img']
        for l in list(d['out'].inputs['Surface'].links):
            nt.links.remove(l)
        if kind in ('BaseColor', 'Metallic', 'Emission'):
            for l in list(d['em'].inputs['Color'].links):
                nt.links.remove(l)
            if kind == 'BaseColor':
                nt.links.new(d['color'], d['em'].inputs['Color'])
            elif kind == 'Metallic':
                d['em'].inputs['Color'].default_value = (d['metal'],) * 3 + (1,)
            else:
                d['em'].inputs['Color'].default_value = d['emit']
            nt.links.new(d['em'].outputs[0], d['out'].inputs['Surface'])
        else:
            nt.links.new(d['bsdf'].outputs[0], d['out'].inputs['Surface'])
    btype = dict(BaseColor='EMIT', Metallic='EMIT', Emission='EMIT', Roughness='ROUGHNESS', Normal='NORMAL', AO='AO')[kind]
    sc.cycles.samples = 48 if kind == 'AO' else 12
    bpy.ops.object.bake(type=btype, margin=6, use_clear=True)
    img.filepath_raw = os.path.join(OUT, 'textures', '%s_%s.png' % (NAME, kind))
    img.file_format = 'PNG'
    img.save()
    px = img.pixels[:]
    n = len(px) // 4
    step = max(1, n // 20000)
    vals = [(px[i * 4] + px[i * 4 + 1] + px[i * 4 + 2]) / 3 for i in range(0, n, step)]
    print('BAKE %s mean=%.3f min=%.3f max=%.3f' % (kind, sum(vals) / len(vals), min(vals), max(vals)))


sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
bpy.ops.object.select_all(action='DESELECT')
gun.select_set(True)
bpy.context.view_layer.objects.active = gun
for kind in ('BaseColor', 'Metallic', 'Roughness', 'Normal', 'Emission', 'AO'):
    bake(kind)
final = bpy.data.materials.new(NAME)
final.use_nodes = True
nt = final.node_tree
bsdf = nt.nodes['Principled BSDF']


def tex(kind):
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = IMGS[kind]
    return t


nt.links.new(tex('BaseColor').outputs[0], bsdf.inputs['Base Color'])
nt.links.new(tex('Metallic').outputs[0], bsdf.inputs['Metallic'])
nt.links.new(tex('Roughness').outputs[0], bsdf.inputs['Roughness'])
nt.links.new(tex('Emission').outputs[0], bsdf.inputs['Emission Color'])
bsdf.inputs['Emission Strength'].default_value = 3.0
nmap = nt.nodes.new('ShaderNodeNormalMap')
nt.links.new(tex('Normal').outputs[0], nmap.inputs['Color'])
nt.links.new(nmap.outputs[0], bsdf.inputs['Normal'])
gun.data.materials.clear()
gun.data.materials.append(final)
for poly in gun.data.polygons:
    poly.material_index = 0

# ------------------------------------------------------------------ per-part GLB + rig.json for the web viewer
site = gun.copy()
site.data = gun.data.copy()
sc.collection.objects.link(site)
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
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, '%s_parts.glb' % NAME), export_format='GLB', use_selection=True,
                          export_animations=False, export_skins=False, export_yup=True)
for o in part_objs:
    bpy.data.objects.remove(o, do_unlink=True)
for v in [v for v in gun.vertex_groups if v.name.startswith('part:')]:
    gun.vertex_groups.remove(v)
json.dump(dict(groups=GROUPS, part_group={p['name']: p['group'] for p in MAN['parts']}, dofs=D.DOFS, modes=D.MODES,
               windows=D.WINDOWS), open(os.path.join(OUT, 'rig.json'), 'w'), indent=1)

# ------------------------------------------------------------------ rig
arm_data = bpy.data.armatures.new(NAME + '_Rig')
arm = bpy.data.objects.new(NAME + '_Rig', arm_data)
sc.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
rb = arm_data.edit_bones.new('Root')
rb.head, rb.tail = (0, 0, 0), (0, -0.03, 0)
for g, d in GROUPS.items():
    if g == 'frame':
        continue
    eb = arm_data.edit_bones.new(g)
    piv = [s['pivot'] for s in d['steps'] if s['type'] == 'rot']
    h = T @ Vector(piv[0] if piv else (60, 14, 0))
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
        pb.matrix = (T @ group_matrix(g, st) @ TI) @ pb.bone.matrix_local
        if frame is not None:
            pb.keyframe_insert('location', frame=frame)
            pb.keyframe_insert('rotation_quaternion', frame=frame)


# ------------------------------------------------------------------ verification renders
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'
cam.data.clip_start = 0.001
sc.camera = cam
for i, (d, e) in enumerate([((-1, -0.6, 1), 4.0), ((1, -0.5, 0.8), 4.0), ((0, 1, 0.6), 2.0), ((-0.3, 0.2, -1), 1.5)]):
    sun = bpy.data.objects.new('sun%d' % i, bpy.data.lights.new('sun%d' % i, 'SUN'))
    sun.data.energy = e
    sun.data.angle = 0.6
    sun.rotation_euler = Vector(d).to_track_quat('Z', 'Y').to_euler()
    sc.collection.objects.link(sun)
w = bpy.data.worlds.new('w')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.16, 0.18, 0.22, 1)
sc.world = w
for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        sc.render.engine = eng
        break
    except Exception:
        pass
VIEWS = dict(right=(-1, 0, 0), q=(-0.8, -0.65, 0.45), top=(0, -0.01, 1), front=(-0.35, -1, 0.25), rear=(-0.5, 1, 0.4), below=(-0.4, -0.5, -1))


def shot(path, view, scale=0.52, res=(900, 620), center=(0, -0.1, -0.02)):
    c = Vector(center)
    cam.location = c + Vector(VIEWS[view]).normalized() * 1.2
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = scale
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


for mode in D.MODES:
    apply_state(D.MODES[mode])
    bpy.context.view_layer.update()
    for v in ('q', 'right', 'top', 'front', 'rear', 'below'):
        shot(os.path.join(OUT, 'verify', 'mode_%s_%s.png' % (mode, v)), v)

# ------------------------------------------------------------------ clips -> actions -> NLA
arm.animation_data_create()
ad = arm.animation_data
acts = []
for clip in D.CLIPS:
    cname, n, _ = clip
    act = bpy.data.actions.new(cname)
    ad.action = act
    for f in range(n):
        apply_state(D.clip_state(clip, f), frame=f)
    if n > 2:
        for f in sorted(set(int(round(i * (n - 1) / 5.0)) for i in range(6))):
            sc.frame_set(f)
            for v in ('right', 'q'):
                shot(os.path.join(OUT, 'verify', 'clip_%s_%s_%03d.png' % (cname, v, f)), v, scale=0.6, res=(520, 360))
    acts.append((cname, n, act))
ad.action = None
for cname, n, act in acts:
    tr = ad.nla_tracks.new()
    tr.name = cname
    stp = tr.strips.new(cname, 0, act)
    stp.name = cname
    try:
        if getattr(stp, 'action_slot', None) is None and len(act.slots):
            stp.action_slot = act.slots[0]
    except Exception as e:
        print('slot assign note:', e)
    tr.mute = True
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
sc.frame_set(0)

# ------------------------------------------------------------------ export
for o in list(bpy.data.objects):
    if o.type in ('CAMERA', 'LIGHT'):
        o.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, NAME + '.blend'))
bpy.ops.object.select_all(action='DESELECT')
gun.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
for tr in ad.nla_tracks:
    tr.mute = False
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, NAME + '.glb'), export_format='GLB', use_selection=True,
                          export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True,
                          export_force_sampling=True, export_yup=True)
print('GLB_OK')
fbx = os.path.join(OUT, NAME + '.fbx')
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, add_leaf_bones=False, bake_anim=True, bake_anim_use_nla_strips=True,
                         bake_anim_use_all_actions=False, apply_scale_options='FBX_SCALE_UNITS', path_mode='COPY', embed_textures=True)
# the FBX embeds absolute texture paths; blank out the local user name (same length, so the file stays valid)
user = os.path.basename(os.path.expanduser('~')).encode()
if user:
    data = open(fbx, 'rb').read()
    open(fbx, 'wb').write(data.replace(user, b'_' * len(user)))
print('FBX_OK')
print('FINISH_DONE')
