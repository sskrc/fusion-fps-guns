# FutureGuns - builds three sci-fi FPS guns (SMG, shotgun, sniper) in Autodesk Fusion.
# Each gun is created in its own new, unsaved document. Nothing existing is touched and
# nothing is saved to the cloud. Screenshots, .f3d, .step and per-part STL go to OUT_DIR.
import adsk.core, adsk.fusion
import traceback, os, sys, json, math, importlib, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, 'out')

_log = []
_base_appearance = [None, False]


def log(msg):
    _log.append(str(msg))


def P(x, y, z=0.0):
    return adsk.core.Point3D.create(float(x), float(y), float(z))


def VI(v):
    return adsk.core.ValueInput.createByReal(float(v))


# ---------------------------------------------------------------- appearances
def _color_prop(appearance):
    props = appearance.appearanceProperties
    try:
        p = adsk.core.ColorProperty.cast(props.itemById('opaque_albedo'))
        if p:
            return p
    except Exception:
        pass
    for i in range(props.count):
        p = adsk.core.ColorProperty.cast(props.item(i))
        if p:
            return p
    return None


def _find_base_appearance(app):
    if _base_appearance[1]:
        return _base_appearance[0]
    _base_appearance[1] = True
    libs = []
    try:
        lib = app.materialLibraries.itemById('BA5EE55E-9982-449B-9D66-9F036540E140')
        if lib:
            libs.append(lib)
    except Exception:
        pass
    if not libs:
        ml = app.materialLibraries
        libs = [ml.item(i) for i in range(ml.count)]
    for lib in libs:
        try:
            aps = lib.appearances
            for nm in ('Paint - Enamel Glossy (Yellow)', 'Paint - Enamel Glossy (White)'):
                a = aps.itemByName(nm)
                if a and _color_prop(a):
                    _base_appearance[0] = a
                    log('base appearance: %s' % a.name)
                    return a
            for i in range(min(aps.count, 800)):
                a = aps.item(i)
                if a.id.startswith('Prism') and _color_prop(a) and a.appearanceProperties.itemById('opaque_albedo'):
                    _base_appearance[0] = a
                    log('base appearance (scan): %s / %s' % (a.name, a.id))
                    return a
        except Exception:
            log('appearance scan error: ' + traceback.format_exc())
    log('no base appearance found - bodies stay default colour')
    return None


def make_appearances(app, design, gun):
    out = {}
    base = _find_base_appearance(app)
    if not base:
        return out
    for key, c in gun.colors.items():
        try:
            nm = 'FG_%s_%s' % (gun.name, key)
            ap = design.appearances.itemByName(nm)
            if not ap:
                ap = design.appearances.addByCopy(base, nm)
            cp = _color_prop(ap)
            r, g, b = c['rgb']
            cp.value = adsk.core.Color.create(int(r), int(g), int(b), 255)
            if c.get('emit', 0) > 0:
                try:
                    props = ap.appearanceProperties
                    e = props.itemById('opaque_emission')
                    if e:
                        e.value = True
                    lum = props.itemById('opaque_luminance')
                    if lum:
                        lum.value = 3000.0
                    lc = adsk.core.ColorProperty.cast(props.itemById('opaque_luminance_modifier'))
                    if lc:
                        lc.value = adsk.core.Color.create(int(r), int(g), int(b), 255)
                except Exception:
                    log('emissive setup skipped for %s' % nm)
            out[key] = ap
        except Exception:
            log('appearance %s failed: %s' % (key, traceback.format_exc()))
    return out


# ---------------------------------------------------------------- geometry
def _finish(body, name, mat, apps, made):
    body.name = name
    ap = apps.get(mat)
    if ap:
        try:
            body.appearance = ap
        except Exception:
            log('appearance assign failed on %s' % name)
    made.append((body, name, mat))


def build_plate(comp, tmp, p, apps, made):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines

    def loop(pts):
        sp = [sk.modelToSketchSpace(P(x, y, 0)) for (x, y) in pts]
        first = lines.addByTwoPoints(sp[0], sp[1])
        prev = first
        for i in range(2, len(sp)):
            prev = lines.addByTwoPoints(prev.endSketchPoint, sp[i])
        lines.addByTwoPoints(prev.endSketchPoint, first.startSketchPoint)

    loop(p['pts'])
    for h in p['holes']:
        loop(h)
    sk.isComputeDeferred = False

    best, best_area = None, -1.0
    for i in range(sk.profiles.count):
        pr = sk.profiles.item(i)
        a = pr.areaProperties(adsk.fusion.CalculationAccuracy.LowCalculationAccuracy).area
        if a > best_area:
            best, best_area = pr, a
    if best is None:
        raise RuntimeError('no closed profile')

    n0 = comp.bRepBodies.count
    exts = comp.features.extrudeFeatures
    inp = exts.createInput(best, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.setDistanceExtent(False, VI(p['t']))
    exts.add(inp)
    if comp.bRepBodies.count <= n0:
        raise RuntimeError('extrude made no body')
    body = comp.bRepBodies.item(comp.bRepBodies.count - 1)

    if p.get('ch', 0) > 0:
        try:
            edges = adsk.core.ObjectCollection.create()
            seen = set()
            for f in body.faces:
                pl = adsk.core.Plane.cast(f.geometry)
                if pl and abs(abs(pl.normal.z) - 1.0) < 1e-6:
                    for e in f.edges:
                        if e.tempId not in seen:
                            seen.add(e.tempId)
                            edges.add(e)
            ch = comp.features.chamferFeatures
            ci = ch.createInput2()
            ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, VI(p['ch']), False)
            ch.add(ci)
            body = comp.bRepBodies.item(comp.bRepBodies.count - 1)
        except Exception:
            log('chamfer skipped on %s: %s' % (p['n'], traceback.format_exc().strip().splitlines()[-1]))
            body = comp.bRepBodies.item(comp.bRepBodies.count - 1)

    bb = body.boundingBox
    mid = (bb.minPoint.z + bb.maxPoint.z) / 2.0
    targets = [(p['z'], '')]
    if p.get('mirror'):
        targets = [(p['z'], '_R'), (-p['z'], '_L')]
    for zc, suffix in targets:
        c = tmp.copy(body)
        m = adsk.core.Matrix3D.create()
        m.translation = adsk.core.Vector3D.create(0, 0, zc - mid)
        tmp.transform(c, m)
        nb = comp.bRepBodies.add(c)
        _finish(nb, p['n'] + suffix, p['m'], apps, made)
    body.deleteMe()
    try:
        sk.deleteMe()
    except Exception:
        pass


def build_cyl(comp, tmp, p, apps, made):
    signs = [(1, '_R'), (-1, '_L')] if p.get('mirror') else [(1, '')]
    for s, suffix in signs:
        a = P(p['p1'][0], p['p1'][1], p['p1'][2] * s)
        b = P(p['p2'][0], p['p2'][1], p['p2'][2] * s)
        body = tmp.createCylinderOrCone(a, p['r'], b, p['r2'])
        if p.get('bore', 0) > 0:
            d = a.vectorTo(b)
            d.normalize()
            d.scaleBy(0.2)
            a2 = P(a.x - d.x, a.y - d.y, a.z - d.z)
            b2 = P(b.x + d.x, b.y + d.y, b.z + d.z)
            tool = tmp.createCylinderOrCone(a2, p['bore'], b2, p['bore'])
            tmp.booleanOperation(body, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType)
        nb = comp.bRepBodies.add(body)
        _finish(nb, p['n'] + suffix, p['m'], apps, made)


def build_box(comp, tmp, p, apps, made):
    signs = [(1, '_R'), (-1, '_L')] if p.get('mirror') else [(1, '')]
    for s, suffix in signs:
        c, sz = p['c'], p['s']
        obb = adsk.core.OrientedBoundingBox3D.create(
            P(c[0], c[1], c[2] * s),
            adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
            sz[0], sz[1], sz[2])
        nb = comp.bRepBodies.add(tmp.createBox(obb))
        _finish(nb, p['n'] + suffix, p['m'], apps, made)


# ---------------------------------------------------------------- output
def screenshots(app, root, gun_dir, name):
    vp = app.activeViewport
    bb = root.boundingBox
    c = P((bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2, (bb.minPoint.z + bb.maxPoint.z) / 2)
    L = bb.minPoint.distanceTo(bb.maxPoint)
    views = [('side', (0, 0, 1), (0, 1, 0)), ('iso', (0.65, 0.4, 0.8), (0, 1, 0)),
             ('iso_back', (-0.7, 0.45, -0.75), (0, 1, 0)), ('front', (1, 0.15, 0.25), (0, 1, 0)),
             ('top', (0, 1, 0), (0, 0, -1))]
    for vname, d, up in views:
        try:
            cam = vp.camera
            cam.isSmoothTransition = False
            cam.target = c
            cam.eye = P(c.x + d[0] * L * 2, c.y + d[1] * L * 2, c.z + d[2] * L * 2)
            cam.upVector = adsk.core.Vector3D.create(*up)
            cam.isFitView = True
            vp.camera = cam
            adsk.doEvents()
            vp.refresh()
            adsk.doEvents()
            vp.saveAsImageFile(os.path.join(gun_dir, '%s_%s.png' % (name, vname)), 1600, 900)
        except Exception:
            log('screenshot %s failed: %s' % (vname, traceback.format_exc()))


def exports(design, root, gun, gun_dir, made):
    em = design.exportManager
    for label, fn in (('f3d', lambda: em.createFusionArchiveExportOptions(os.path.join(gun_dir, gun.name + '.f3d'))),
                      ('step', lambda: em.createSTEPExportOptions(os.path.join(gun_dir, gun.name + '.step')))):
        try:
            ok = em.execute(fn())
            log('export %s: %s' % (label, ok))
        except Exception:
            log('export %s failed: %s' % (label, traceback.format_exc().strip().splitlines()[-1]))
    parts_dir = os.path.join(gun_dir, 'parts')
    os.makedirs(parts_dir, exist_ok=True)
    plist = []
    stl_fail = 0
    for i, (body, name, mat) in enumerate(made):
        fn = '%03d_%s.stl' % (i, name)
        try:
            o = em.createSTLExportOptions(body, os.path.join(parts_dir, fn))
            o.sendToPrintUtility = False
            o.isBinaryFormat = True
            o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium
            em.execute(o)
            plist.append(dict(file=fn, name=name, mat=mat))
        except Exception:
            stl_fail += 1
            if stl_fail <= 3:
                log('stl %s failed: %s' % (name, traceback.format_exc().strip().splitlines()[-1]))
        if i % 10 == 0:
            adsk.doEvents()
    bb = root.boundingBox
    manifest = dict(name=gun.name, colors=gun.colors, parts=plist,
                    bbox_cm=dict(min=[bb.minPoint.x, bb.minPoint.y, bb.minPoint.z],
                                 max=[bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z]))
    with open(os.path.join(gun_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=1)
    log('stl parts: %d ok, %d failed' % (len(plist), stl_fail))


def build_gun(app, gun):
    log('=== %s ===' % gun.name)
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    try:
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
    except Exception:
        log('could not switch to direct design: ' + traceback.format_exc())
    root = design.rootComponent
    tmp = adsk.fusion.TemporaryBRepManager.get()
    apps = make_appearances(app, design, gun)
    made = []
    fails = 0
    builders = dict(plate=build_plate, cyl=build_cyl, box=build_box)
    for i, p in enumerate(gun.parts):
        try:
            builders[p['k']](root, tmp, p, apps, made)
        except Exception:
            fails += 1
            log('PART FAILED %s: %s' % (p['n'], traceback.format_exc()))
        if i % 8 == 0:
            adsk.doEvents()
    log('bodies: %d, failed parts: %d' % (len(made), fails))
    gun_dir = os.path.join(OUT_DIR, gun.name)
    os.makedirs(gun_dir, exist_ok=True)
    screenshots(app, root, gun_dir, gun.name)
    exports(design, root, gun, gun_dir, made)
    return len(made), fails


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    summary = []
    t0 = time.time()
    try:
        os.makedirs(OUT_DIR, exist_ok=True)
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import gun_data
        importlib.reload(gun_data)
        only = None
        for gun in gun_data.all_guns():
            if only and gun.name not in only:
                continue
            try:
                n, f = build_gun(app, gun)
                summary.append('%s: %d bodies, %d failed parts' % (gun.name, n, f))
            except Exception:
                log('GUN FAILED %s: %s' % (gun.name, traceback.format_exc()))
                summary.append('%s: FAILED' % gun.name)
    except Exception:
        log('FATAL: ' + traceback.format_exc())
        summary.append('FATAL - see log.txt')
    log('elapsed %.1fs' % (time.time() - t0))
    try:
        with open(os.path.join(OUT_DIR, 'log.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary) + '\n\n' + '\n'.join(_log))
    except Exception:
        pass
    del _log[:]
    if ui:
        ui.messageBox('FutureGuns finished.\n\n' + '\n'.join(summary) + '\n\nOutput: ' + OUT_DIR)
