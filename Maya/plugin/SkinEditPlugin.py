# -*- coding: utf-8 -*-
import json
from maya.api import OpenMaya
from SkinningTools.Maya.tools import weightWrite

kPluginCmdName = "SkinEditor"


def maya_useNewAPI():
    pass

class SkinEditClass(weightWrite.WeightBatch, OpenMaya.MPxCommand):
    """One validated, atomic command for physical-index mesh weight writes."""

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)
        weightWrite.WeightBatch.__init__(self)
        self._ready = False

    def doIt(self, args):
        self.parseArguments(args)
        self._apply([op['newWeights'] for op in self.operations])
        self._ready = True

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
    mplugin.registerCommand(kPluginCmdName, cmdCreator, syntaxCreator)


def uninitializePlugin(mobject):
    mplugin = OpenMaya.MFnPlugin(mobject)
    mplugin.deregisterCommand(kPluginCmdName)
