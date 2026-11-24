# ORBIS - builds the ORBIS-V transforming emitter (original fictional design) in Autodesk Fusion, in a new unsaved document.
# Visual model only. Every moving part is a separate body.
# Output (screenshots, .f3d, .step, per-part STL, manifest.json) goes to OUT_DIR.
import adsk.core, adsk.fusion
import traceback, os, sys, json, importlib, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, 'out', 'ORBIS')
K = 0.1   # mm -> cm (Fusion API unit)
_log = []


def log(m):
    _log.append(str(m))


def P(x, y, z=0.0):
    return adsk.core.Point3D.create(float(x), float(y), float(z))


def VI(v):
    return adsk.core.ValueInput.createByReal(float(v))


def last_line():
    return traceback.format_exc().strip().splitlines()[-1]


# ---------------------------------------------------------------- shapes -> temporary B-rep bodies
def prism_body(root, tmp, sh, s):
    sk = root.sketches.add(root.xYConstructionPlane)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    sp = [sk.modelToSketchSpace(P(a * K, b * K, 0)) for (a, b) in sh['pts']]
    first = lines.addByTwoPoints(sp[0], sp[1])
    prev = first
    for i in range(2, len(sp)):
        prev = lines.addByTwoPoints(prev.endSketchPoint, sp[i])
    lines.addByTwoPoints(prev.endSketchPoint, first.startSketchPoint)
    sk.isComputeDeferred = False
    best, ba = None, -1.0
    for i in range(sk.profiles.count):
        pr = sk.profiles.item(i)
        a = pr.areaProperties(adsk.fusion.CalculationAccuracy.LowCalculationAccuracy).area
        if a > ba:
            best, ba = pr, a
    if best is None:
        raise RuntimeError('no closed profile')
    n0 = root.bRepBodies.count
    exts = root.features.extrudeFeatures
    inp = exts.createInput(best, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    t = (sh['hi'] - sh['lo']) * K
    inp.setDistanceExtent(False, VI(t))
    exts.add(inp)
    if root.bRepBodies.count <= n0:
        raise RuntimeError('extrude made no body')
    real = root.bRepBodies.item(root.bRepBodies.count - 1)
    bb = real.boundingBox
    wmid = (bb.minPoint.z + bb.maxPoint.z) / 2.0
    body = tmp.copy(real)
    real.deleteMe()
    try:
        sk.deleteMe()
    except Exception:
        pass
    mid = (sh['lo'] + sh['hi']) / 2.0 * K
    m = adsk.core.Matrix3D.create()
    pl = sh['plane']
    # local (u, v, w): polygon in u,v ; w is the extrusion, re-centred on 0 by -wmid
    if pl == 'xy':       # x=u, y=v, z=w + s*mid
        m.setWithArray([1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, s * mid - wmid,
                        0, 0, 0, 1])
    elif pl == 'zy':     # x=-s*w + mid, y=v, z=s*u
        m.setWithArray([0, 0, -s, mid + s * wmid,
                        0, 1, 0, 0,
                        s, 0, 0, 0,
                        0, 0, 0, 1])
    else:                # 'xz': x=u, y=-s*w + mid, z=s*v
        m.setWithArray([1, 0, 0, 0,
                        0, 0, -s, mid + s * wmid,
                        0, s, 0, 0,
                        0, 0, 0, 1])
    tmp.transform(body, m)
    return body


def shape_body(root, tmp, sh, s):
    if sh['k'] == 'csg':
        return eval_ops(root, tmp, sh['ops'], s)
    if sh['k'] == 'prism':
        return prism_body(root, tmp, sh, s)
    a = P(sh['p1'][0] * K, sh['p1'][1] * K, sh['p1'][2] * s * K)
    b = P(sh['p2'][0] * K, sh['p2'][1] * K, sh['p2'][2] * s * K)
    return tmp.createCylinderOrCone(a, sh['r'] * K, b, sh['r2'] * K)


def eval_ops(root, tmp, ops, s):
    BT = adsk.fusion.BooleanTypes
    kinds = dict(add=BT.UnionBooleanType, cut=BT.DifferenceBooleanType, int=BT.IntersectionBooleanType)
    cur = None
    for op, sh in ops:
        b = shape_body(root, tmp, sh, s)
        if cur is None:
            cur = b
        else:
            tmp.booleanOperation(cur, b, kinds[op])
    return cur


def try_fillet(root, name, r_mm):
    for r in (r_mm, r_mm * 0.6, r_mm * 0.3):
        try:
            body = root.bRepBodies.itemByName(name)
            edges = adsk.core.ObjectCollection.create()
            for e in body.edges:
                edges.add(e)
            fil = root.features.filletFeatures
            inp = fil.createInput()
            inp.edgeSetInputs.addConstantRadiusEdgeSet(edges, VI(r * K), False)
            fil.add(inp)
            log('fillet %s r=%.2f ok' % (name, r))
            return
        except Exception:
            log('fillet %s r=%.2f failed: %s' % (name, r, last_line()))


# ---------------------------------------------------------------- appearances (cosmetic only)
def _color_prop(ap):
    props = ap.appearanceProperties
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


def find_base_appearance(app):
    libs = []
    try:
        lib = app.materialLibraries.itemById('BA5EE55E-9982-449B-9D66-9F036540E140')
        if lib:
            libs.append(lib)
    except Exception:
        pass
    ml = app.materialLibraries
    libs += [ml.item(i) for i in range(ml.count)]
    for lib in libs:
        try:
            aps = lib.appearances
            n = min(aps.count, 1500)
        except Exception:
            continue
        for i in range(n):
            try:
                a = aps.item(i)
                if a.id.startswith('Prism') and a.appearanceProperties.itemById('opaque_albedo') and _color_prop(a):
                    log('base appearance: %s / %s' % (a.name, a.id))
                    return a
            except Exception:
                pass
    log('no base appearance found')
    return None


def make_appearances(app, design, materials):
    out = {}
    try:
        base = find_base_appearance(app)
        if not base:
            return out
        for key, c in materials.items():
            try:
                ap = design.appearances.addByCopy(base, 'ORBIS_' + key)
                r, g, b = c['rgb']
                _color_prop(ap).value = adsk.core.Color.create(int(r), int(g), int(b), 255)
                out[key] = ap
            except Exception:
                log('appearance %s failed: %s' % (key, last_line()))
    except Exception:
        log('appearances failed: ' + traceback.format_exc())
    return out


# ---------------------------------------------------------------- output
def screenshots(app, root, name):
    vp = app.activeViewport
    bb = root.boundingBox
    c = P((bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2, (bb.minPoint.z + bb.maxPoint.z) / 2)
    L = bb.minPoint.distanceTo(bb.maxPoint)
    views = [('right', (0, 0, 1), (0, 1, 0)), ('left', (0, 0, -1), (0, 1, 0)), ('iso', (0.65, 0.4, 0.8), (0, 1, 0)),
             ('iso_left', (0.6, 0.4, -0.8), (0, 1, 0)), ('rear', (-1, 0.3, 0.4), (0, 1, 0)), ('top', (0, 1, 0), (0, 0, -1)),
             ('below', (0.3, -1, 0.5), (1, 0, 0))]
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
            vp.saveAsImageFile(os.path.join(OUT_DIR, '%s_%s.png' % (name, vname)), 1600, 1000)
        except Exception:
            log('screenshot %s failed: %s' % (vname, last_line()))


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    t0 = time.time()
    made, fails = [], 0
    try:
        os.makedirs(os.path.join(OUT_DIR, 'parts'), exist_ok=True)
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import orbis_data
        D = importlib.reload(orbis_data)

        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        try:
            design.designType = adsk.fusion.DesignTypes.DirectDesignType
        except Exception:
            log('could not switch to direct design: ' + last_line())
        root = design.rootComponent
        tmp = adsk.fusion.TemporaryBRepManager.get()
        apps = make_appearances(app, design, D.MATERIALS)

        for p in D.PARTS:
            for s, suf in ([(1, '_R'), (-1, '_L')] if p['mirror'] else [(1, '')]):
                name = p['n'] + suf
                try:
                    body = root.bRepBodies.add(eval_ops(root, tmp, p['ops'], s))
                    body.name = name
                    if p['fillet'] > 0:
                        try_fillet(root, name, p['fillet'])
                        body = root.bRepBodies.itemByName(name)
                    if apps.get(p['m']):
                        try:
                            body.appearance = apps[p['m']]
                        except Exception:
                            pass
                    made.append((name, p['m'], p['g'] + (suf if D.GROUPS[p['g']].get('mirror') else '')))
                    log('part %s ok (faces %d)' % (name, body.faces.count))
                except Exception:
                    fails += 1
                    log('PART FAILED %s: %s' % (name, traceback.format_exc()))
                adsk.doEvents()

        screenshots(app, root, 'ORBIS')

        em = design.exportManager
        for label, fn in (('f3d', lambda: em.createFusionArchiveExportOptions(os.path.join(OUT_DIR, 'ORBIS.f3d'))),
                          ('step', lambda: em.createSTEPExportOptions(os.path.join(OUT_DIR, 'ORBIS.step')))):
            try:
                log('export %s: %s' % (label, em.execute(fn())))
            except Exception:
                log('export %s failed: %s' % (label, last_line()))
        plist = []
        for i, (name, m, g) in enumerate(made):
            fn = '%02d_%s.stl' % (i, name)
            try:
                o = em.createSTLExportOptions(root.bRepBodies.itemByName(name), os.path.join(OUT_DIR, 'parts', fn))
                o.sendToPrintUtility = False
                o.isBinaryFormat = True
                o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
                em.execute(o)
                plist.append(dict(file=fn, name=name, mat=m, group=g))
            except Exception:
                log('stl %s failed: %s' % (name, last_line()))
        bb = root.boundingBox
        man = dict(name='ORBIS', unit='mm', parts=plist, groups=D.expanded_groups(), materials=D.MATERIALS,
                   bbox_cm=dict(min=[bb.minPoint.x, bb.minPoint.y, bb.minPoint.z],
                                max=[bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z]))
        with open(os.path.join(OUT_DIR, 'manifest.json'), 'w', encoding='utf-8') as f:
            json.dump(man, f, indent=1)
        log('stl parts: %d' % len(plist))
    except Exception:
        log('FATAL: ' + traceback.format_exc())
        fails += 1
    summary = 'ORBIS: %d bodies, %d failures, %.1fs' % (len(made), fails, time.time() - t0)
    try:
        with open(os.path.join(OUT_DIR, 'log.txt'), 'w', encoding='utf-8') as f:
            f.write(summary + '\n\n' + '\n'.join(_log))
    except Exception:
        pass
    del _log[:]
    if ui:
        ui.messageBox('ORBIS finished.\n\n' + summary + '\n\nOutput: ' + OUT_DIR)
