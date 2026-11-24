import bpy, sys
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[sys.argv.index('--') + 1])
print('GLB_OBJECTS', [(o.name, o.type) for o in bpy.data.objects if o.type in ('MESH', 'ARMATURE')])
print('GLB_ACTIONS', sorted((a.name, int(a.frame_range[1] - a.frame_range[0]) + 1) for a in bpy.data.actions))
for o in bpy.data.objects:
    if o.type == 'ARMATURE':
        print('GLB_BONES', [b.name for b in o.data.bones])
    if o.type == 'MESH':
        print('GLB_MESH', len(o.data.vertices), 'dims_m', [round(d, 4) for d in o.dimensions], 'mats', [m.name for m in o.data.materials])
print('GLB_IMAGES', [(i.name, tuple(i.size)) for i in bpy.data.images])
