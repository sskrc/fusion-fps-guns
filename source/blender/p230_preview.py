# Headless Blender preview of p230_data (same CSG the Fusion script performs), for shape checking only.
# blender -b --python p230_preview.py -- <P230 dir> <out dir>
import bpy, bmesh, sys, os, math, importlib
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index('--') + 1:]
sys.path.insert(0, os.path.abspath(args[0]))
OUT = os.path.abspath(args[1])
import p230_data as D
S = 0.001


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
        bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=sh['r'] * S, radius2=sh['r2'] * S,
                              depth=d.length, matrix=M)
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
    b.inputs['Base Color'].default_value = tuple(pow(v / 255, 2.2) for v in c['rgb']) + (1,)
    b.inputs['Metallic'].default_value = c['metal'] * 0.5
    b.inputs['Roughness'].default_value = c['rough']
    return m


bpy.ops.wm.read_factory_settings(use_empty=True)
objs = []
for p in D.PARTS:
    for s, suf in ([(1, '_R'), (-1, '_L')] if p['mirror'] else [(1, '')]):
        o = eval_ops(p['ops'], s)
        o.name = p['n'] + suf
        o['group'] = p['g']
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
        print('PART', o.name, len(o.data.vertices))


R = Matrix(((0, 0, -1, 0), (-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def pose(f):
    """f: dict group -> 0..1 fraction of its motion"""
    for o in objs:
        g = D.GROUPS[o['group']]
        k = f.get(o['group'], 0.0)
        if g['type'] == 'translate':
            o.matrix_world = R @ Matrix.Translation(Vector(g['axis']) * g['travel'] * k * S)
        elif g['type'] == 'rotate':
            pv = Vector(g['pivot']) * S
            o.matrix_world = R @ Matrix.Translation(pv) @ Matrix.Rotation(math.radians(g['angle'] * k), 4, Vector(g['axis'])) @ Matrix.Translation(-pv)
        else:
            o.matrix_world = R.copy()


sc = bpy.context.scene
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'
cam.data.clip_start = 0.001
sc.camera = cam
for i, (d, e) in enumerate([((-1, -0.6, 1), 2.5), ((1, -0.5, 0.8), 2.5), ((0, 1, 0.6), 1.0)]):
    sun = bpy.data.objects.new('sun%d' % i, bpy.data.lights.new('sun%d' % i, 'SUN'))
    sun.data.energy = e
    sun.rotation_euler = Vector(d).to_track_quat('Z', 'Y').to_euler()
    sc.collection.objects.link(sun)
w = bpy.data.worlds.new('w')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.22, 0.23, 0.25, 1)
w.node_tree.nodes['Background'].inputs[1].default_value = 1.0
sc.world = w
for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        sc.render.engine = eng
        break
    except Exception:
        pass
sc.render.resolution_x, sc.render.resolution_y = 1500, 1000
C = Vector((0, -0.07, -0.035))


def shot(name, d, scale=0.24, center=C):
    cam.location = center + Vector(d).normalized() * 0.6
    cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = scale
    sc.render.filepath = os.path.join(OUT, 'p230_%s.png' % name)
    bpy.ops.render.render(write_still=True)


views = args[2].split(',') if len(args) > 2 else ['right', 'left', 'iso', 'open', 'top', 'rear']
pose({})
if 'right' in views: shot('right', (-1, 0, 0))
if 'left' in views: shot('left', (1, 0, 0))
if 'iso' in views: shot('iso', (-0.8, -0.7, 0.45))
if 'isoL' in views: shot('isoL', (0.8, -0.7, 0.45))
if 'top' in views: shot('top', (0, -0.01, 1), scale=0.2, center=Vector((0, -0.075, 0)))
if 'rear' in views: shot('rear', (-0.35, 1, 0.25), scale=0.16, center=Vector((0, 0, -0.03)))
if 'open' in views:
    pose(dict(slide=1, hammer=1.25, trigger=1, magazine=0.45, mag_catch=1, decocker=0))
    shot('open', (-0.8, -0.45, 0.5), scale=0.3, center=Vector((0, -0.05, -0.05)))
    shot('open_right', (-1, 0, 0), scale=0.3, center=Vector((0, -0.05, -0.05)))

if len(args) > 3:      # stand-in export in the same layout the Fusion script writes (raw model coords, mm)
    import json
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
    json.dump(dict(name='P230', unit='mm', parts=plist, groups=D.GROUPS, materials=D.MATERIALS, standin=True),
              open(os.path.join(SD, 'manifest.json'), 'w'), indent=1)
    print('STANDIN', len(plist))
