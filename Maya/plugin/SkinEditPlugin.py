# -*- coding: utf-8 -*-
import json
import math
import numbers
from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim

kPluginCmdName = "SkinEditor"


def maya_useNewAPI():
    pass

class SkinEditClass(OpenMaya.MPxCommand):
    """One validated, atomic command for physical-index mesh weight writes."""

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)
        self.operations = []
        self._ready = False

    def doIt(self, args):
        self.parseArguments(args)
        self._apply([op['newWeights'] for op in self.operations])
        self._ready = True

    def getDagpath(self, node, extendToShape=False):
        selection = OpenMaya.MGlobal.getSelectionListByName(node)
        try:
            dag = selection.getDagPath(0)
        except (RuntimeError, TypeError):
            return selection.getDependNode(0)
        if extendToShape and dag.node().hasFn(OpenMaya.MFn.kTransform):
            dag.extendToShape()
        return dag

    def getMfnSkinCluster(self, node):
        selection = OpenMaya.MGlobal.getSelectionListByName(node)
        return OpenMayaAnim.MFnSkinCluster(selection.getDependNode(0))

    def _flagArray(self, parser, flag, integral=False):
        result = []
        if parser.isFlagSet(flag):
            for index in range(parser.numberOfFlagUses(flag)):
                argument = parser.getFlagArgumentList(flag, index)
                result.append(argument.asInt(0) if integral else argument.asDouble(0))
        return result

    def parseArguments(self, args):
        parser = OpenMaya.MArgParser(self.syntax(), args)
        mesh, skin = parser.getObjectStrings()
        if parser.isFlagSet('-bt'):
            requests = json.loads(parser.flagArgumentString('-bt', 0))
            if not isinstance(requests, list) or not requests:
                raise ValueError('SkinEditor batch must contain requests')
        else:
            requests = [{'mesh': mesh, 'skinCluster': skin,
                'vertices': self._flagArray(parser, '-vid', True),
                'influences': self._flagArray(parser, '-jid', True),
                'weights': self._flagArray(parser, '-nw'),
                'originalWeights': self._flagArray(parser, '-ow'),
                'normalize': parser.flagArgumentBool('-n', 0) if parser.isFlagSet('-n') else True}]
        seen = set()
        self.operations = []
        for request in requests:
            operation = self._prepare(request)
            for vertex in operation['vertices']:
                # Component identity includes geometry, even for multi-output deformers.
                key = (operation['skin'].name(),
                       OpenMaya.MObjectHandle(operation['dag'].node()).hashCode(), vertex)
                if key in seen:
                    raise ValueError('SkinEditor batch contains overlapping vertices')
                seen.add(key)
            self.operations.append(operation)
        self.mesh = mesh
        self.skinCluster = self.operations[0]['skin']
        self.vertID = OpenMaya.MIntArray(self.operations[0]['vertices'])
        self.jointID = self.operations[0]['indices']
        self.newWeights = self.operations[0]['newWeights']
        # Actual scene state owns undo; caller -ow is accepted but never trusted.
        self.origWeights = self.operations[0]['oldWeights']
        return True

    def _signature(self, skin, dag):
        influences = skin.influenceObjects()
        return (OpenMaya.MFnMesh(dag).numVertices,
                tuple((inf.fullPathName(), skin.indexForInfluenceObject(inf)) for inf in influences))

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
        if any(not isinstance(w, numbers.Real) or math.isnan(w) or math.isinf(w)
               or not 0.0 <= w <= 1.0 for w in weights):
            raise ValueError('Weights must be finite values in [0, 1]')
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
        if any(math.isnan(w) or math.isinf(w) or not 0.0 <= w <= 1.0 for w in old):
            raise ValueError('Existing weights are outside the finite [0, 1] range')
        new = list(old)
        influence_count = len(mapping)
        locked = [cmds.getAttr(name + '.liw') for name, logical in mapping]
        source_rows = dict((vertex, row) for row, vertex in enumerate(vertices))
        for row, vertex in enumerate(ordered):
            offset = row * influence_count
            source_offset = source_rows[vertex] * len(influences)
            for column, influence in enumerate(influences):
                if not locked[influence]:
                    new[offset + influence] = float(weights[source_offset + column])
            if normalize:
                locked_sum = sum(new[offset+i] for i in range(influence_count) if locked[i])
                unlocked = [i for i in range(influence_count) if not locked[i]]
                if locked_sum > 1.0 + 1e-6:
                    raise ValueError('Locked weights exceed normalization budget')
                total = sum(new[offset+i] for i in unlocked)
                if total > 0.0:
                    factor = max(0.0, 1.0-locked_sum) / total
                    for i in unlocked:
                        new[offset+i] *= factor
                elif locked_sum > 0.0 and locked_sum < 1.0-1e-6 and unlocked:
                    raise ValueError('No unlocked weight to fill normalization budget')
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
            if any(math.isnan(w) or math.isinf(w) or not 0.0 <= w <= 1.0 for w in weights):
                raise ValueError('SkinEditor snapshot contains invalid weights')
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

    def redoIt(self):
        self._apply([op['newWeights'] for op in self.operations])

    def undoIt(self):
        self._apply([op['oldWeights'] for op in self.operations])

    def setWeight(self, inWeights):
        if len(self.operations) != 1:
            raise ValueError('setWeight requires a single prepared operation')
        self._apply([inWeights])

    def isUndoable(self):
        return self._ready


def cmdCreator():
    return SkinEditClass()


def syntaxCreator():
    syntax = OpenMaya.MSyntax()
    syntax.setObjectType(OpenMaya.MSyntax.kStringObjects, 2, 2)  # < (mesh, skincluster)

    syntax.addFlag('-vid', '-vertID', OpenMaya.MSyntax.kLong)
    syntax.addFlag('-nw', '-newWeights', OpenMaya.MSyntax.kDouble)
    syntax.addFlag('-jid', '-jointID', OpenMaya.MSyntax.kLong)
    syntax.addFlag('-ow', '-origWeights', OpenMaya.MSyntax.kDouble)
    syntax.addFlag('-bt', '-batchWeights', OpenMaya.MSyntax.kString)
    syntax.addFlag('-n', '-normalize', OpenMaya.MSyntax.kBoolean)
    syntax.makeFlagMultiUse('-vid')
    syntax.makeFlagMultiUse('-nw')
    syntax.makeFlagMultiUse('-jid')
    syntax.makeFlagMultiUse('-ow')

    return syntax


def initializePlugin(mobject):
    mplugin = OpenMaya.MFnPlugin(mobject, "Perry Leijten", "1.0", "any")
    try:
        mplugin.registerCommand(kPluginCmdName, cmdCreator, syntaxCreator)
    except:
        raise


def uninitializePlugin(mobject):
    mplugin = OpenMaya.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(kPluginCmdName)
    except:
        raise
