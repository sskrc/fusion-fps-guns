# Headless Blender: per-part STL + manifest.json (from the Fusion script) -> GLB / FBX with
# named parts and PBR materials.   blender -b --python convert_guns.py -- <gun_dir> [<gun_dir> ...]
import bpy, bmesh, json, os, sys, math
from mathutils import Matrix, Vector

# Fusion (X fwd, Y up, Z right; cm)  ->  Blender (-Y fwd, Z up)
AXIS = Matrix(((0, 0, -1, 0), (-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def make_mat(name, c):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    r, g, bl = [pow(v / 255.0, 2.2) for v in c['rgb']]
    b.inputs['Base Color'].default_value = (r, g, bl, 1)
    b.inputs['Metallic'].default_value = c['metal']
    b.inputs['Roughness'].default_value = c['rough']
    if c.get('emit', 0) > 0:
        b.inputs['Emission Color'].default_value = (r, g, bl, 1)
        b.inputs['Emission Strength'].default_value = c['emit']
    return m


def import_gun(gun_dir):
    man = json.load(open(os.path.join(gun_dir, 'manifest.json'), encoding='utf-8'))
    mats = {k: make_mat('%s_%s' % (man['name'], k), c) for k, c in man['colors'].items()}
    objs = []
    for p in man['parts']:
        before = set(bpy.data.objects)
        bpy.ops.wm.stl_import(filepath=os.path.join(gun_dir, 'parts', p['file']))
        o = (set(bpy.data.objects) - before).pop()
        o.name = p['name']
        o.data.name = p['name']
        o.data.materials.append(mats[p['mat']])
        objs.append(o)
    # unit detection: compare raw bbox length with manifest (cm)
    xs = [(o.matrix_world @ v.co).x for o in objs for v in o.data.vertices]
    raw = max(xs) - min(xs)
    want_cm = man['bbox_cm']['max'][0] - man['bbox_cm']['min'][0]
    unit_to_m = (want_cm / raw) * 0.01
    print('RAW_LEN', raw, 'WANT_CM', want_cm, 'scale', unit_to_m)
    T = AXIS @ Matrix.Scale(unit_to_m, 4)
    for o in objs:
        me = o.data
        me.transform(T @ o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
        for poly in me.polygons:
            poly.use_smooth = True
        try:
            me.set_sharp_from_angle(angle=math.radians(35))
        except Exception as e:
            print('set_sharp_from_angle failed', e)
    root = bpy.data.objects.new(man['name'], None)
    bpy.context.scene.collection.objects.link(root)
    for o in objs:
        o.parent = root
    return man, root, objs


def render(objs, path):
    sc = bpy.context.scene
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    c = (mn + mx) / 2
    L = (mx - mn).length
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
    sc.collection.objects.link(cam)
    cam.location = c + Vector((1.0, -0.55, 0.45)).normalized() * L * 1.25
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 60
    cam.data.clip_start = 0.01
    sc.camera = cam
    for i, (d, e) in enumerate([((1, -1, 2), 4.0), ((-1, -0.3, 0.5), 1.5)]):
        sun = bpy.data.objects.new('sun%d' % i, bpy.data.lights.new('sun%d' % i, 'SUN'))
        sun.data.energy = e
        sun.rotation_euler = Vector(d).to_track_quat('Z', 'Y').to_euler()
        sc.collection.objects.link(sun)
    w = bpy.data.worlds.new('w')
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.35, 0.38, 0.42, 1)
    sc.world = w
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            sc.render.engine = eng
            break
        except Exception:
            pass
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


for gun_dir in [os.path.abspath(a) for a in sys.argv[sys.argv.index("--") + 1:]]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    man, root, objs = import_gun(gun_dir)
    name = man['name']
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=os.path.join(gun_dir, name + '.glb'), export_format='GLB', use_selection=True)
    try:
        bpy.ops.export_scene.fbx(filepath=os.path.join(gun_dir, name + '.fbx'), use_selection=True,
                                 apply_scale_options='FBX_SCALE_UNITS', mesh_smooth_type='FACE')
    except Exception as e:
        print('FBX export failed', e)
    render(objs, os.path.join(gun_dir, name + '_render.png'))
    print('DONE', name, len(objs))
