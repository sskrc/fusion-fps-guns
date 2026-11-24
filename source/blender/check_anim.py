# Re-import an exported GLB/FBX and report how far each bone actually moves in every clip.
import bpy, sys, math
f = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
(bpy.ops.import_scene.gltf if f.lower().endswith('.glb') else bpy.ops.import_scene.fbx)(filepath=f)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.animation_data_create()
for tr in list(arm.animation_data.nla_tracks):
    arm.animation_data.nla_tracks.remove(tr)
sc = bpy.context.scene
rest = {b.name: (arm.matrix_world @ b.matrix_local) for b in arm.data.bones}
for act in sorted(bpy.data.actions, key=lambda a: a.name):
    arm.animation_data.action = act
    try:
        if len(act.slots) and arm.animation_data.action_slot is None:
            arm.animation_data.action_slot = act.slots[0]
    except Exception:
        pass
    a, b = int(act.frame_range[0]), int(math.ceil(act.frame_range[1]))
    mx = {}
    for fr in range(a, b + 1):
        sc.frame_set(fr)
        for pb in arm.pose.bones:
            M = arm.matrix_world @ pb.matrix
            d = (M.translation - rest[pb.name].translation).length * 1000
            ang = math.degrees((rest[pb.name].to_quaternion().rotation_difference(M.to_quaternion())).angle)
            ang = min(ang, 360 - ang)
            sca = M.to_scale().x / max(1e-9, rest[pb.name].to_scale().x)
            m = mx.setdefault(pb.name, [0, 0, 1])
            m[0], m[1], m[2] = max(m[0], d), max(m[1], ang), min(m[2], sca)
    print('ANIM %-22s' % act.name.split('|')[-1], ' '.join('%s:%.0fmm/%.0fdeg%s' % (k, v[0], v[1], '/hidden' if v[2] < 0.01 else '') for k, v in sorted(mx.items()) if v[0] > 0.05 or v[1] > 0.5 or v[2] < 0.5))
