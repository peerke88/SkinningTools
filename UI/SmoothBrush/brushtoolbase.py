# -*- coding: utf-8 -*-
try:
    import cStringIO
except:
    import io as cStringIO
from maya import cmds, mel

'''
Abstract base class that handles custom brush tool callbacks.
'''
class BrushToolBase(object):
    knownContexts = {}
    
    callbackMap = {
        # mouse drag
        'beforeStrokeCmd':     ('beforeStroke', '', '', ''),
        # mouse drag
        'duringStrokeCmd':     ('duringStroke', '', '', ''),
        # mouse up
        'afterStrokeCmd':      ('afterStroke', '', '', ''),
        'toolOnProc':          ('toolSelected', '', '', ''),
        'toolOffProc':         ('toolDeselected', '', '', ''),
        # initial click on a surface received
        'toolSetupCmd':        ('toolEnter', 'string $contextName', '\'"+$contextName+"\'', ''),
        'toolCleanupCmd':      ('toolExit', 'string $contextName', '\'"+$contextName+"\'', ''),
        # gets the object name in the selection list to process
        'getSurfaceCommand':   ('processSelectedObject', 'string $name', '\'"+$name+"\'', 'string'),
        # called on mouse down for each selected surface
        'getArrayAttrCommand': ('getArrayAttrCommand', '', '', 'string'), 
        # mouse up
        'finalizeCmd':         ('finalize', 'string $contextName', '\'"+$contextName+"\'', ''),
        # argument is a comma separated string; split to get a list of names, all referring to different doube[] attributes (one string referring to one double ARRAY attribute)
        'setValueCommand':     ('setValue', 'string $slot, int $index, float $value', '\'"+$slot+"\', "+$index+", "+$value+"', ''),
        # vertex attribute set, provdes the slot (currently always -1?) index of the attribute and the value to set; which attribute to set is up to the user, which surface we're painting on should be cached during initialize() as this receives the surface name
        'initializeCmd':       ('initialize', 'string $name', '\'"+$name+"\'', ''),
        # vertex attribute get, must return the requested value...
        'getValueCommand':     ('getValue', '', '', 'float')
        }
    
    toolSetupPrefix = 'artUserPaintCtx -e -surfaceConformedBrushVertices 0'
    
    def __init__(self, contextName, safe=False):
        
        if contextName in BrushToolBase.knownContexts.keys():
            BrushToolBase.knownContexts[contextName]._activate()
            return
        
        BrushToolBase.knownContexts[contextName] = self
        
        # set up kwargs to bind forwarding functions back to this class
        self.__kwargs = {}
        if cmds.artUserPaintCtx(self.__scriptingContext, q=True, exists=True):
            if safe:
                cmds.error('Could not create Brush Tool (artUserPaintCtx) with name %s, a context with this name already exists.'%contextName)
                return
            self.__kwargs['e'] = True
    
        # set up generic fowarding for all possible callbacks
        self.__toolSetupMel = BrushToolBase.toolSetupPrefix
        
        buffer = cStringIO.StringIO()
        for key in BrushToolBase.callbackMap.keys():
            if key == 'toolSetupCmd': #tool setup must be done in mel for some reason
                continue
            value, melArgStr, pyArgStr, returnType = BrushToolBase.callbackMap[key]
            if not hasattr(self, value): #function not implemented, do not register
                self.__kwargs[key] = ''
                self.__toolSetupMel += '-%s "" '%key
                continue
            buffer.write('global proc %s %s_%s(%s){ %s python("from skinningTool.SmoothBrush.brushtoolbase import BrushToolBase;BrushToolBase.knownContexts[\'%s\'].%s(%s)"); }\n'%(returnType, key, contextName, melArgStr, 'return' if returnType else '', contextName, value, pyArgStr))
            self.__toolSetupMel += '-%s "%s_%s" '%(key, key, contextName)
            
        mel.eval(buffer.getvalue())
        buffer.close()
        
        self.__toolSetupMel += '"%s";'%cmds.currentCtx()
        value, melArgAtr, pyArgStr, returnType = BrushToolBase.callbackMap['toolSetupCmd']
        if hasattr(self, value):
            self.__toolSetupMel += '\npython("from skinningTool.SmoothBrush.brushtoolbase import BrushToolBase;BrushToolBase.knownContexts[\'%s\'].%s(%s)");'%(contextName, value, pyArgStr)
        mel.eval('global proc toolSetupCmd_%s(string $contextName){ %s }\n'%(contextName, self.__toolSetupMel))
        self.__toolSetupCmd = 'toolSetupCmd_%s'%contextName
        self.__contextName = contextName
        
        self._activate()
        
    @property
    def __scriptingContext(self):
        # maya hardcodes it's custom paint brush tool to this name, so our contexts are just setting storages on the class object
        # and whenever changing 'context' we swap the callback function names on the only context maya understands
        try: cmds.ScriptPaintToolOptions() 
        except: pass # if the current context is faulty this will generate MEL errors, but we'll still be in the right context
        return cmds.currentCtx()

    def _emptyKwargs(self):
        kwargs = {}
        for key in self.__kwargs.keys():
            kwargs[key] = ''
        kwargs['e'] = True
        return kwargs
        
    def _activate(self):
        kwargs = self._emptyKwargs()
        kwargs['toolSetupCmd'] = self.__toolSetupCmd
        
        if 'e' not in self.__kwargs.keys():
            cmds.artUserPaintCtx(self.__scriptingContext, **kwargs)
            self.__kwargs['e'] = True
        else:
            cmds.artUserPaintCtx(self.__scriptingContext, **kwargs)
        
    def initialize(self, objectName):
        #required for drag commands to trigger properly
        pass
        
    def toolExit(self, contextName): # exit 2
        kwargs = self._emptyKwargs()
        cmds.artUserPaintCtx(contextName, **kwargs)
        