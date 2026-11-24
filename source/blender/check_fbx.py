import bpy, sys
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=sys.argv[sys.argv.index('--') + 1])
print('FBX_OBJECTS', [(o.name, o.type, [round(d, 4) for d in o.dimensions]) for o in bpy.data.objects])
print('FBX_ACTIONS', sorted(a.name for a in bpy.data.actions))
print('FBX_IMAGES', [i.name for i in bpy.data.images])
