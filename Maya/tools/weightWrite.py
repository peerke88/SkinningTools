# -*- coding: utf-8 -*-
"""Maya weight layout and exact batch application; no Qt or plugin registration."""
import numbers
from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim
from SkinningTools.Maya.tools import weightMath


def influenceMapping(skin):
    """Return (DAG path, physical array position, logical plug index) in API order."""
    return tuple((dag, physical, skin.indexForInfluenceObject(dag))
                 for physical, dag in enumerate(skin.influenceObjects()))


def physicalInfluences(skin):
    return OpenMaya.MIntArray([physical for dag, physical, logical in influenceMapping(skin)])


def influenceLocks(mapping):
    return [cmds.getAttr(dag.fullPathName() + '.liw') for dag, physical, logical in mapping]


def getDagpath(node, extendToShape=False):
    selection = OpenMaya.MGlobal.getSelectionListByName(node)
    try:
        dag = selection.getDagPath(0)
    except (RuntimeError, TypeError):
        return selection.getDependNode(0)
    if extendToShape and dag.node().hasFn(OpenMaya.MFn.kTransform):
        dag.extendToShape()
    return dag

def getMfnSkinCluster(node):
    selection = OpenMaya.MGlobal.getSelectionListByName(node)
    return OpenMayaAnim.MFnSkinCluster(selection.getDependNode(0))


class WeightBatch(object):
    """Prepare and apply snapshots; the calling MPxCommand owns its undo entry."""
    def __init__(self):
        self.operations = []

    getDagpath = staticmethod(getDagpath)
    getMfnSkinCluster = staticmethod(getMfnSkinCluster)

    def _signature(self, skin, dag):
        return (OpenMaya.MFnMesh(dag).numVertices,
                tuple((dag.fullPathName(), logical) for dag, physical, logical in influenceMapping(skin)))

    def _prepare(self, request):
        if not isinstance(request, dict):
            raise ValueError('SkinEditor request must be a mapping')
        dag = self.getDagpath(request['mesh'], True)
        skin = self.getMfnSkinCluster(request['skinCluster'])
        if not any(dag.node() == geometry for geometry in skin.getOutputGeometry()):
            raise ValueError('Mesh does not belong to the supplied skinCluster')
        signature = self._signature(skin, dag)
        count, mapping = signature
        vertices = list(request['vertices'])
        influences = list(request['influences'])
        if (not vertices or len(set(vertices)) != len(vertices)
                or any(isinstance(v, bool) or not isinstance(v, numbers.Integral)
                       or not 0 <= v < count for v in vertices)):
            raise ValueError('Invalid or duplicate vertex indices')
        if (not influences or len(set(influences)) != len(influences)
                or any(isinstance(i, bool) or not isinstance(i, numbers.Integral)
                       or not 0 <= i < len(mapping) for i in influences)):
            raise ValueError('Influence indices must be unique physical indices')
        weights = list(request['weights'])
        if len(weights) != len(vertices) * len(influences):
            raise ValueError('Weight array dimensions do not match components/influences')
        weightMath.validateWeights(weights)
        originals = request.get('originalWeights', [])
        if originals and len(originals) != len(weights):
            raise ValueError('Original weight array dimensions do not match')
        normalize = request.get('normalize', True)
        if not isinstance(normalize, bool):
            raise ValueError('normalize must be a boolean')
        ordered = sorted(vertices)
        component_fn = OpenMaya.MFnSingleIndexedComponent()
        component = component_fn.create(OpenMaya.MFn.kMeshVertComponent)
        component_fn.addElements(ordered)
        ordered = list(component_fn.getElements())
        old = skin.getWeights(dag, component)[0]
        weightMath.validateWeights(old, checkType=False)
        new = list(old)
        influence_count = len(mapping)
        locked = influenceLocks(influenceMapping(skin))
        source_rows = dict((vertex, row) for row, vertex in enumerate(vertices))
        for row, vertex in enumerate(ordered):
            offset = row * influence_count
            source_offset = source_rows[vertex] * len(influences)
            for column, influence in enumerate(influences):
                if not locked[influence]:
                    new[offset + influence] = float(weights[source_offset + column])
            if normalize:
                weightMath.normalizeWeightsInPlace(new, locked, offset)
        return {'skin': skin, 'dag': dag, 'component': component,
                'vertices': ordered, 'indices': OpenMaya.MIntArray(range(influence_count)),
                'signature': signature, 'oldWeights': OpenMaya.MDoubleArray(old),
                'newWeights': OpenMaya.MDoubleArray(new)}

    def _validateSettings(self, operation):
        skin = operation['skin']
        for name, needed in (('normalizeWeights', skin.findPlug('normalizeWeights', False).asInt() != 0),
                             ('maintainMaxInfluences', skin.findPlug('maintainMaxInfluences', False).asBool())):
            plug = skin.findPlug(name, False)
            if needed and (plug.isLocked or plug.isDestination):
                raise ValueError('SkinEditor cannot temporarily control %s' % name)

    def _writeExact(self, operation, weights):
        skin = operation['skin']
        normal = skin.findPlug('normalizeWeights', False)
        maintain = skin.findPlug('maintainMaxInfluences', False)
        normal_value, maintain_value = normal.asInt(), maintain.asBool()
        try:
            if normal_value:
                normal.setInt(0)
            if maintain_value:
                maintain.setBool(False)
            skin.setWeights(operation['dag'], operation['component'], operation['indices'], weights, False)
        finally:
            if maintain_value:
                maintain.setBool(maintain_value)
            if normal_value:
                normal.setInt(normal_value)

    def _write(self, operation, weights):
        self._writeExact(operation, weights)
        actual = operation['skin'].getWeights(operation['dag'], operation['component'])[0]
        if list(actual) != list(weights):
            raise RuntimeError('SkinEditor could not commit the exact weight snapshot')

    def _apply(self, arrays):
        # Check every mapping/topology before any mutation, including undo/redo.
        if len(arrays) != len(self.operations):
            raise ValueError('SkinEditor snapshot count does not match operations')
        for operation, weights in zip(self.operations, arrays):
            if len(weights) != len(operation['vertices']) * len(operation['indices']):
                raise ValueError('SkinEditor snapshot dimensions do not match')
            weightMath.validateWeights(weights, checkType=not isinstance(weights, OpenMaya.MDoubleArray))
            self._validateSettings(operation)
            if self._signature(operation['skin'], operation['dag']) != operation['signature']:
                raise RuntimeError('SkinEditor topology or influence mapping has changed')
        before = [op['skin'].getWeights(op['dag'], op['component'])[0] for op in self.operations]
        attempted = []
        try:
            for index, (operation, weights) in enumerate(zip(self.operations, arrays)):
                attempted.append(index)
                self._write(operation, weights)
        except Exception:
            # Include the failed write, which may have partially mutated its mesh.
            for index in reversed(attempted):
                op = self.operations[index]
                try:
                    self._writeExact(op, before[index])
                    actual = op['skin'].getWeights(op['dag'], op['component'])[0]
                    if list(actual) != list(before[index]):
                        raise RuntimeError('Rollback snapshot does not match')
                except Exception as rollback_error:
                    OpenMaya.MGlobal.displayError('SkinEditor rollback failed: %s' % rollback_error)
            raise
