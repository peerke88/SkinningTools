"""Disposable batch-only fixtures. No interactive scene may use these helpers."""
import math
import uuid
from maya import cmds
from maya.api import OpenMaya as om, OpenMayaAnim as oma


def require_batch():
    if not cmds.about(batch=True):
        raise RuntimeError('Fixtures require a separate Maya standalone/batch process')


def skin_data(mesh, skin):
    selection = om.MSelectionList()
    selection.add(mesh)
    dag = selection.getDagPath(0)
    dag.extendToShape()
    selection.add(skin)
    fn = oma.MFnSkinCluster(selection.getDependNode(1))
    component_fn = om.MFnSingleIndexedComponent()
    component = component_fn.create(om.MFn.kMeshVertComponent)
    component_fn.addElements(range(cmds.polyEvaluate(mesh, vertex=True)))
    return fn, dag, component


def snapshot(mesh, skin):
    fn, dag, component = skin_data(mesh, skin)
    influences = fn.influenceObjects()
    return {'weights': list(fn.getWeights(dag, component)[0]),
            'influences': [i.fullPathName() for i in influences],
            'logical_indices': [fn.indexForInfluenceObject(i) for i in influences],
            'physical_indices': list(range(len(influences))),
            'locks': [cmds.getAttr(i.fullPathName() + '.liw') for i in influences],
            'settings': {a: cmds.getAttr(skin + '.' + a) for a in
                         ('normalizeWeights', 'maintainMaxInfluences', 'maxInfluences')},
            'selection': cmds.ls(selection=True, long=True) or [],
            'bind_poses': cmds.listConnections(skin + '.bindPose', source=True) or []}


def write_raw(mesh, skin, weights):
    """Test arrangement only; use explicit physical indices and no normalization."""
    fn, dag, component = skin_data(mesh, skin)
    count = len(fn.influenceObjects())
    expected = cmds.polyEvaluate(mesh, vertex=True) * count
    if len(weights) != expected or any(not math.isfinite(w) or w < 0 for w in weights):
        raise ValueError('Invalid fixture weight dimensions or values')
    fn.setWeights(dag, component, om.MIntArray(range(count)), om.MDoubleArray(weights), False)


class SceneFixture:
    def __enter__(self):
        require_batch()
        self.selection = cmds.ls(selection=True, long=True) or []
        self.before_nodes = set(cmds.ls(long=True))
        self.namespace = 'reliability_' + uuid.uuid4().hex
        cmds.namespace(add=self.namespace)
        self.meshes = []
        self.skins = []
        self.joints = []
        return self

    def create(self, sparse=False, different=False, subdivisions=2):
        cmds.select(clear=True)
        joints = [cmds.joint(name=self.namespace + ':joint%d_%d' % (len(self.meshes), i),
                             position=(i * 2, 0, 0)) for i in range(3)]
        mesh = cmds.polyPlane(name=self.namespace + ':mesh%d' % len(self.meshes),
                              subdivisionsX=subdivisions, subdivisionsY=subdivisions, constructionHistory=False)[0]
        skin = cmds.skinCluster(joints[:2] if different else joints, mesh,
                                toSelectedBones=True, normalizeWeights=0)[0]
        count = 2 if different else 3
        vertex_count = cmds.polyEvaluate(mesh, vertex=True)
        write_raw(mesh, skin, [v for _ in range(vertex_count) for v in ([1.0] + [0.0] * (count-1))])
        if sparse:
            cmds.skinCluster(skin, edit=True, removeInfluence=joints[1])
            cmds.select(clear=True)
            extra = cmds.joint(name=self.namespace + ':added%d' % len(self.meshes))
            cmds.skinCluster(skin, edit=True, addInfluence=extra, weight=0.0)
            joints.append(extra)
        self.meshes.append(mesh)
        self.skins.append(skin)
        self.joints.extend(joints)
        return mesh, skin

    def isolated(self):
        fn = om.MFnMesh()
        fn.create(om.MPointArray([(0, 0, 0), (1, 0, 0), (0, 0, 1), (5, 5, 5)]),
                  om.MIntArray([3]), om.MIntArray([0, 1, 2]))
        dag = om.MDagPath.getAPathTo(fn.object())
        parent = cmds.listRelatives(dag.fullPathName(), parent=True, fullPath=True)[0]
        return cmds.rename(parent, self.namespace + ':isolated')

    def __exit__(self, exc_type, exc, traceback):
        # Only this private process is permitted. Include generated poses/history.
        new_nodes = set(cmds.ls(long=True)) - self.before_nodes
        remaining = [n for n in new_nodes if cmds.objExists(n)]
        if remaining:
            cmds.delete(remaining)
        cmds.namespace(removeNamespace=self.namespace)
        cmds.select(self.selection, replace=True) if self.selection else cmds.select(clear=True)
