#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 17 nov 2011
#
#   Various definition about cleaning object
#

import pymel.core as pmc
import common.vPrint as vp
import common.various as various



def multipleObj(obj):
    """Return True if the two object has the same name"""
    if len(pmc.ls('*|'+obj)) > 1:
        return True
    else:
        return False



def deleteAllConnections(*args):
    """Deleting all connections (in and out)"""
    for arg in args:
        for source, destination in arg.connections(connections=True, plugs=True):
            try:
                source // destination
            except:
                destination // source



def lockAtoms(*args, **kwargs):
    """Lock vertices or cvs components"""
    # check kwargs
    if ('lock' in kwargs.keys())==False:
        kwargs['lock'] = True
    
    for arg in args:
        if isinstance(arg, list) == False:
            arg = [arg]
        for obj in arg:
            __lockAtoms__(obj, lock=kwargs['lock'])


def __lockAtoms__(obj, lock=True):
    if various.getShapeType(obj) == 'mesh':
        for p in obj.pnts:
            p.pntx.setLocked(lock)
            p.pnty.setLocked(lock)
            p.pntz.setLocked(lock)
    else:
        for p in obj.controlPoints:
            p.xValue.setLocked(lock)
            p.yValue.setLocked(lock)
            p.zValue.setLocked(lock)


def lockHideTransform(*args, **kwargs):
    """Lock and Hide channels"""
    # check kwargs
    if ('lock' in kwargs.keys())==False:
        kwargs['lock'] = True
    if ('hide' in kwargs.keys())==False:
        kwargs['hide'] = True
    if ('channel' in kwargs.keys())==False:
            kwargs['channel'] = ['t', 'r', 's', 'v']
    if ('channelBox' in kwargs.keys())==False:
        kwargs['channelBox'] = False
    
    # working on each object given
    for arg in args:
        if isinstance(arg, list) == False:
            arg = [arg]
        for obj in arg:
            obj = various.checkObj(obj)
            if obj != None:
                __lockHideTransform__(obj, lock=kwargs['lock'], hide=kwargs['hide'], channel=kwargs['channel'], channelBox=kwargs['channelBox'])

def __lockHideTransform__(obj, lock=True, hide=True, channel=['t', 'r', 's', 'v'], channelBox=False):
    # inversing hide
    if hide:
        hide=False
    else:
        hide=True
    
    if channelBox:
        chNew = []
        attrs = pmc.listAttr(obj, keyable=True)
        attrs.extend(pmc.listAttr(obj, channelBox=True))
        for attr in attrs:
            tmp = pmc.PyNode(obj+'.'+attr).getParent()
            if tmp:
                if tmp.shortName() not in chNew:
                    chNew.append(tmp.shortName())
            else:
                chNew.append(attr)
        channel = chNew
    
    # loop on each channel given
    for chan in channel:
        # get pynode about attribut
        try:
            ch = pmc.PyNode(obj+'.'+chan)
        except:
            vp.vPrint('%s has no channel called %s' % (obj.name(), chan), 1)
            ch = None
        if ch:
            # try to get his children
            try:
                children = ch.getChildren()
            except:
                children = []
            # locking and hidding
            for child in children:
                child.showInChannelBox(hide)
                child.setLocked(lock)
                child.setKeyable(hide)
            ch.showInChannelBox(hide) 
            ch.setLocked(lock)
            ch.setKeyable(hide)


def cleanOrig(*args):
    """checking and deleting useless shapeOrig"""
    # working on each object given
    for arg in args:
        if isinstance(arg, list):
            for obj in arg:
                return __cleanOrig__(obj)
        else:
            return __cleanOrig__(arg)


def __cleanOrig__(objIn):
    obj = various.checkObj(objIn, type=['transform'])
    if obj != None:
        i=0
        # getting each shapes
        for shape in obj.getShapes():
            # check if the shape is an intermediate object
            if shape.intermediateObject.get():
                connections = shape.connections(plugs=True)
                # and without any connection
                if len(connections) == 0:
                    # we can delete it
                    pmc.delete(shape)
                    i=i+1
                elif len(connections) == 1:
                    if connections[0].node().type() in ['mesh', 'nurbsCurve']:
                        pmc.delete(shape)
                        i=i+1
        return i
    else:
        return None



def cleanOrigUI():
    for obj in pmc.ls(sl=True):
        i=cleanOrig(obj)
        if i != None:
            vp.vPrint('%s shape(s) orig deleted for %s' % (str(i), obj.name()), 2)
