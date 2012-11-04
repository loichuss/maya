#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 22 nov 2011
#
#   Definition about joint
#


import pymel.core as pmc
import pymel.core.datatypes as dt
import common.various as various


def transformToBone(*args):
    """Switch from a transform node to a Joint node, keep shape and children"""
    # working on each object given
    for arg in args:
        if isinstance(arg, list) == False:
            arg = [arg]
        for obj in arg:
            obj = various.checkObj(obj, type=['transform'])
            if obj != None:
                __transformToBone__(obj)

def __transformToBone__(obj):
    name   = obj.name()
    
    # create joint
    jnt = pmc.createNode('joint', name=name+'_')
    
    # set parent
    if obj.getParent():
        jnt.setParent(obj.getParent())
    
    # set transformation
    jnt.setTranslation(obj.getTranslation(space='object'), space='object')
    jnt.setRotationOrder(obj.getRotationOrder(), reorder=True)
    jnt.jointOrientX.set(obj.getRotation(space='object')[0])
    jnt.jointOrientY.set(obj.getRotation(space='object')[1])
    jnt.jointOrientZ.set(obj.getRotation(space='object')[2])
    jnt.setScale(obj.getScale())
    jnt.setShear(obj.getShear())
    
    # get children
    children = obj.getChildren()
    for child in children:
        child = various.checkObj(child, type=['transform', 'joint'], echo=False)
        if child:
            child.setParent(jnt)
    
    # parent shape
    if obj.getShape():
        pmc.parent(obj.getShape(), jnt, shape=True, relative=True)
    
    # deleting and renaming properly
    pmc.delete(obj)
    jnt.rename(name)

    return jnt
    





def rotateToOrient(*args):
    """put each rotation information into the joint orient"""
    # working on each object given
    for arg in args:
        if isinstance(arg, list) == False:
            arg = [arg]
        for obj in arg:
            obj = various.checkObj(obj, type=['joint'])
            if obj != None:
                __rotateToOrient__(obj)

def __rotateToOrient__(obj):
    obj.setOrientation( dt.TransformationMatrix( obj.getMatrix(objectSpace=True) ).getRotationQuaternion() )
    obj.setRotation([0,0,0])
