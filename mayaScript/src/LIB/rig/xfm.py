#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 20 nov 2011
#
#   Zero out function
#


import pymel.core as pmc
import common.vPrint as vp
import common.various as various
import constrain.matrixConstrain as matrixConstrain
import clean.clean as clean


def xfm(*args, **kwargs):
    """Create a zero out to transform node. kwargs are prefix and suffix"""
    # check and create kwargs
    if ('prefix' in kwargs.keys())==False:
        kwargs['prefix'] = ''
    if ('suffix' in kwargs.keys())==False:
        kwargs['suffix'] = '_XFM'
    if ('lock' in kwargs.keys())==False:
        kwargs['lock'] = True
    if ('type' in kwargs.keys())==False:
        kwargs['type'] = 'transform' 
    
    # working on each object given
    for arg in args:
        if isinstance(arg, list) == False:
            arg = [arg]
        for obj in arg:
            obj = various.checkObj(obj, type=['transform', 'joint'])
            if obj != None:
                __xfm__(obj, prefix=kwargs['prefix'], suffix=kwargs['suffix'], lock=kwargs['lock'], type=kwargs['type'])




def __xfm__(obj, prefix='', suffix='_XFM', lock=True, type='transform'):
    # create the parent object
    xfmObj=pmc.createNode(obj.type(), name=obj.namespace() + prefix + obj.stripNamespace().replace('|', '_') + suffix, parent=obj.getParent(), skipSelect=True)
    # create matrix constrain to properly place the parent object
    matrixConstrain.snapObject(obj, xfmObj)
    
    # check inverse scale connection
    if obj.type() == 'joint':
        connections = obj.inverseScale.inputs(plugs=True)
        for connection in connections:
            connection // obj.inverseScale
            connection >> xfmObj.inverseScale
        xfmObj.scale >> obj.inverseScale
        # make the joint invisible
        xfmObj.radius.set(0.0)
        xfmObj.drawStyle.set(2)
    
    # parenting part
    obj.setParent(xfmObj, noConnections=True, addObject=False, relative=True)
    
    # reset matrix
    obj.setTransformation([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    
    # locking channels
    if lock:
        clean.__lockHideTransform__(xfmObj, channelBox=True)

    return xfmObj



def xfmUI():
    xfm(pmc.ls(sl=True), lock=False)
    vp.vPrint('xfm done', 2)
