# Headless Blender preview of orbis_data (the same CSG the Fusion script performs), for shape / transform checking.
# blender -b --python orbis_preview.py -- <Orbis dir> <out dir> [views] [stand-in export dir]
import bpy, bmesh, sys, os, math, json
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index('--') + 1:]
sys.path.insert(0, os.path.abspath(args[0]))
OUT = os.path.abspath(args[1])
os.makedirs(OUT, exist_ok=True)
import importlib
D = importlib.import_module(os.environ.get('GUN_MODULE', 'orbis_data'))
D = getattr(D, 'G', D)          # RogueArena modules expose a Gun object named G
GUN = os.environ.get('GUN_NAME', getattr(D, 'NAME', 'ORBIS'))
AUTO_VIEW = 'GUN_VIEW_SCALE' not in os.environ and hasattr(D, 'NAME')     # frame from the bounding box
VSCALE = float(os.environ.get('GUN_VIEW_SCALE', '0.52'))
VCENTER = tuple(float(v) for v in os.environ.get('GUN_VIEW_CENTER', '0,-0.1,-0.02').split(','))
S = 0.001
GROUPS = D.expanded_groups()


def new_obj(bm, name):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def shape_obj(sh, s):
    if sh['k'] == 'csg':
        return eval_ops(sh['ops'], s)
    bm = bmesh.new()
    if sh['k'] == 'prism':
        lo, hi, pl = sh['lo'], sh['hi'], sh['plane']

        def P(a, b, w):
            if pl == 'xy':
                return (a * S, b * S, w * s * S)
            if pl == 'zy':
                return (w * S, b * S, a * s * S)
            return (a * S, w * S, b * s * S)
        A = [bm.verts.new(P(a, b, lo)) for a, b in sh['pts']]
        B = [bm.verts.new(P(a, b, hi)) for a, b in sh['pts']]
        bm.faces.new(A)
        bm.faces.new(B)
        n = len(A)
        for i in range(n):
            bm.faces.new([A[i], A[(i + 1) % n], B[(i + 1) % n], B[i]])
    else:
        a = Vector((sh['p1'][0], sh['p1'][1], sh['p1'][2] * s)) * S
        b = Vector((sh['p2'][0], sh['p2'][1], sh['p2'][2] * s)) * S
        d = b - a
        M = Matrix.Translation((a + b) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=sh['r'] * S, radius2=sh['r2'] * S, depth=d.length, matrix=M)
    return new_obj(bm, 'shape')


def boolean(target, tool, op):
    m = target.modifiers.new('b', 'BOOLEAN')
    m.operation = {'add': 'UNION', 'cut': 'DIFFERENCE', 'int': 'INTERSECT'}[op]
    m.solver = 'EXACT'
    m.object = tool
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(tool, do_unlink=True)


def eval_ops(ops, s):
    cur = None
    for op, sh in ops:
        o = shape_obj(sh, s)
        if cur is None:
            cur = o
        else:
            boolean(cur, o, op)
    return cur


def mat(name):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    c = D.MATERIALS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    col = tuple(pow(v / 255, 2.2) for v in c['rgb']) + (1,)
    b.inputs['Base Color'].default_value = col
    b.inputs['Metallic'].default_value = c['metal'] * 0.5
    b.inputs['Roughness'].default_value = c['rough']
    if c.get('emit'):
        b.inputs['Emission Color'].default_value = col
        b.inputs['Emission Strength'].default_value = 4.0
    return m


bpy.ops.wm.read_factory_settings(use_empty=True)
objs = []
for p in D.PARTS:
    mirrored_group = D.GROUPS[p['g']].get('mirror')
    for s, suf in ([(1, '_R'), (-1, '_L')] if p['mirror'] else [(1, '')]):
        o = eval_ops(p['ops'], s)
        o.name = p['n'] + suf
        o['group'] = p['g'] + (suf if mirrored_group else '')
        o.data.materials.clear()
        o.data.materials.append(mat(p['m']))
        if p['fillet'] > 0:
            bv = o.modifiers.new('bev', 'BEVEL')
            bv.width = p['fillet'] * S
            bv.segments = 3
            bv.limit_method = 'ANGLE'
        for poly in o.data.polygons:
            poly.use_smooth = True
            poly.material_index = 0
        o.data.set_sharp_from_angle(angle=math.radians(35))
        objs.append(o)
        print('PART', o.name, o['group'], len(o.data.vertices))

R = Matrix(((0, 0, -1, 0), (-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
if AUTO_VIEW:
    _c = [[v.co[i] for o in objs for v in o.data.vertices] for i in range(3)]
    _lo, _hi = [min(c) for c in _c], [max(c) for c in _c]
    VCENTER = (-(_lo[2] + _hi[2]) / 2, -(_lo[0] + _hi[0]) / 2, (_lo[1] + _hi[1]) / 2)
    VSCALE = max(_hi[0] - _lo[0], (_hi[1] - _lo[1]) * 900 / 620) * 1.25
    print('BBOX_MM x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (_lo[0] / S, _hi[0] / S, _lo[1] / S, _hi[1] / S, _lo[2] / S, _hi[2] / S))


def group_matrix(group, st):
    M = Matrix.Identity(4)
    for step in GROUPS[group]['steps']:
        v = st.get(step['dof'], 0.0)
        if step['type'] == 'move':
            M = M @ Matrix.Translation(Vector(step['axis']) * step['travel'] * v * S)
        else:
            pv = Vector(step['pivot']) * S
            M = M @ Matrix.Translation(pv) @ Matrix.Rotation(math.radians(step['angle'] * v), 4, Vector(step['axis'])) @ Matrix.Translation(-pv)
    return M


def pose(st):
    for o in objs:
        o.matrix_world = R @ group_matrix(o['group'], st)


sc = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'
cam.data.clip_start = 0.001
sc.camera = cam
for i, (d, e) in enumerate([((-1, -0.6, 1), 3.0), ((1, -0.5, 0.8), 3.0), ((0, 1, 0.6), 1.5)]):
    sun = bpy.data.objects.new('sun%d' % i, bpy.data.lights.new('sun%d' % i, 'SUN'))
    sun.data.energy = e
    sun.rotation_euler = Vector(d).to_track_quat('Z', 'Y').to_euler()
    sc.collection.objects.link(sun)
w = bpy.data.worlds.new('w')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.2, 0.22, 0.25, 1)
sc.world = w
for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        sc.render.engine = eng
        break
    except Exception:
        pass
sc.render.resolution_x, sc.render.resolution_y = 900, 620
VIEWS = dict(right=(-1, 0, 0), left=(1, 0, 0), q=(-0.8, -0.65, 0.45), top=(0, -0.01, 1), front=(-0.3, -1, 0.25), rear=(-0.5, 1, 0.4))


def shot(name, view, scale=None, center=None):
    scale = scale or VSCALE
    c = Vector(center or VCENTER)
    cam.location = c + Vector(VIEWS[view]).normalized() * 1.2
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = scale
    sc.render.filepath = os.path.join(OUT, '%s_%s.png' % (GUN.lower(), name))
    bpy.ops.render.render(write_still=True)


views = args[2].split(',') if len(args) > 2 and args[2] else ['right', 'q', 'top']
for mode in D.MODES:
    pose(D.MODES[mode])
    for v in views:
        shot('%s_%s' % (mode, v), v)

if len(args) > 3:      # stand-in export in the layout the Fusion script writes (raw model coords, mm)
    SD = os.path.abspath(args[3])
    os.makedirs(os.path.join(SD, 'parts'), exist_ok=True)
    plist = []
    for i, o in enumerate(objs):
        o.matrix_world = Matrix.Identity(4)
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        fn = '%02d_%s.stl' % (i, o.name)
        bpy.ops.wm.stl_export(filepath=os.path.join(SD, 'parts', fn), export_selected_objects=True, global_scale=1000.0,
                              forward_axis='Y', up_axis='Z', apply_modifiers=True)
        plist.append(dict(file=fn, name=o.name, mat=o.data.materials[0].name, group=o['group']))
    json.dump(dict(name=GUN, unit='mm', parts=plist, standin=True), open(os.path.join(SD, 'manifest.json'), 'w'), indent=1)
    print('STANDIN', len(plist))
