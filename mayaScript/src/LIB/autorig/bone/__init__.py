#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 17 nov 2011
#
#   Definition about joint in autorig
#

import pymel.core as pmc
import clean
import common.various as various
import autorig.tools.hierarchy as arHierarchy
import constrain.matrixConstrain as matrixConstrain
import rig.bone



def create2SK(name, parent, lock=True, zeroOut=False):
    """create 2SK joint"""
    if parent:
        obj = pmc.createNode('joint', name=name+'_2SKjnt', parent=parent, skipSelect=True)
        if zeroOut:
            obj.setTransformation([[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]])
    else:
        obj = pmc.createNode('joint', name=name+'_2SKjnt', skipSelect=True)
    obj.overrideEnabled.set(1)
    obj.overrideColor.set(3)
    obj.radius.set(0.75)
    if lock:
        clean.__lockHideTransform__(obj, channel=['t', 'r', 's', 'v', 'radius'])
    return obj





def connect2SK(jnts):
    """connect 2SK joints from a given list"""
    # check if each object given are joints
    jntsTmp = []
    for jnt in jnts:
        jnt = various.checkObj(jnt, type=['joint'])
        if jnt:
            jntsTmp.append(jnt)
    __connect2SK__(jntsTmp)


def __connect2SK__(jnts):
    # create the connection
    for i in range(len(jnts)):
        # add attribut
        if pmc.objExists(jnts[i]+'.childSKN')==False:
            pmc.addAttr(jnts[i], longName='childSKN', attributeType='bool', defaultValue=False, keyable=False)
        
        if i:
            jnts[i-1].childSKN >> jnts[i].childSKN





def createSKN():
    
    # create hierachy
    hierarchy = arHierarchy.createHierarchy()
    
    # get each 2SK joint
    jnts2SK = pmc.ls('*2SKjnt')
    
    # loop for each 2SK jnt
    jnt = []
    for jnt2SK in jnts2SK:
        # check if SKN jnt already exist
        if pmc.objExists(jnt2SK.name().replace('2SKjnt', 'SKNjnt'))==False:
            # create the SKN jnt
            jnt.append( pmc.createNode('joint', name=jnt2SK.name().replace('2SKjnt', 'SKNjnt'), parent=hierarchy['SKINSKEL']) )
            # place
            matrixConstrain.snapObject(jnt2SK, jnt[-1])
            # rotation in orient
            rig.bone.__rotateToOrient__(jnt[-1])
    
    # set parent
    for i in range(len(jnt)):
        try:
            jnt[i].setParent( pmc.PyNode(jnt[i].replace('SKNjnt', '2SKjnt')).childSKN.inputs()[0].replace('2SKjnt', 'SKNjnt') )
        except:
            pass





#                  #
#   STORE POSING   #
#                  #


def storePosingSKN(*args):
    """Save SKN posing"""
    
    if args:
        for arg in args:
            if isinstance(arg, list) == False:
                arg = [arg]
            for i in range(len(arg)):
                arg[i] = various.checkObj(arg[i], type=['joint'])
            if (None in arg)==False:
                __storePosingSKN__(arg)
    else:
        __storePosingSKN__(None)



def __storePosingSKN__(elts):
    if elts==None:
        # get each SKN
        elts = pmc.ls('*SKNjnt')
        if len(elts)==0:
            vp.vPrint('No SKN funded', 1)
        fromSelection = False
    else:
        fromSelection = True
    
    if elts:
        pmc.select(clear=True)
        # create set were each curve will be stored
        if pmc.objExists('rigPosingSet')==False:
            pmc.sets(name='rigPosingSet')
        
        # create sub sets if need
        bindPoseSet = 'SKN_bindPose'
        if pmc.objExists(bindPoseSet)==False:
            bindPose = pmc.sets(name=bindPoseSet)
            pmc.sets('rigPosingSet', addElement=bindPose)
        
        
        for elt in elts:
             
            # check if any previous set exist
            if pmc.objExists(elt.name()+'_storedPos'):
                if pmc.sets(bindPoseSet, query=True, size=True) == 1:
                    pmc.delete(elt.name()+'_storedPos')
                    pmc.sets(name=bindPoseSet)
                    pmc.sets('rigPosingSet', addElement=bindPoseSet)
                else:
                    pmc.delete(elt.name()+'_storedPos')
            # create set
            set = pmc.sets(name=elt.name()+'_storedPos')
            pmc.sets(bindPoseSet, addElement=set)
            
            
            attrs = ['t', 'r', 's', 'jo']
            
            for attr in attrs:
                pmc.addAttr(set, longName=attr+'_stored', attributeType='double3')
                pmc.addAttr(set, longName=attr+'_stored'+'x', attributeType='double', defaultValue=pmc.PyNode(elt+'.'+attr+'x').get(), parent=attr+'_stored')
                pmc.addAttr(set, longName=attr+'_stored'+'y', attributeType='double', defaultValue=pmc.PyNode(elt+'.'+attr+'y').get(), parent=attr+'_stored')
                pmc.addAttr(set, longName=attr+'_stored'+'z', attributeType='double', defaultValue=pmc.PyNode(elt+'.'+attr+'z').get(), parent=attr+'_stored')




def storePosingSKNUI():
    storePosingSKN(pmc.ls(sl=True))




#                    #
#   RESTORE POSING   #
#                    #


def restorePosingSKN(*args):
    """restore SKN posing"""
    if args:
        for arg in args:
            if isinstance(arg, list) == False:
                arg = [arg]
            for i in range(len(arg)):
                arg[i] = various.checkObj(arg[i], type=['joint'])
            if (None in arg)==False:
                __restorePosingSKN__(arg)
    else:
        __restorePosingSKN__(None)




def __restorePosingSKN__(elts):

    if elts==None:
        # get each objects from rigShapesSet
        if pmc.objExists('SKN_bindPose'):
            elts = pmc.sets('SKN_bindPose', query=True)
        fromSelection=False
    else:
        fromSelection=True
    
    if elts:
        for elt in elts:
            if fromSelection:
                if pmc.objExists(elt.name()+'_storedPos'):
                    obj = elt.name()+'_storedPos'
                    attrs = ['t', 'r', 's', 'jo']
                    for i in range(len(attrs)):
                        try:
                            pmc.PyNode(elt+'.'+attrs[i]).set(pmc.PyNode(obj+'.'+attrs[i]+'_stored').get())
                        except:
                            vp.vPrint('No data founded from %s in rigPosingSet set' % elt.name(), 1)
                else:
                    vp.vPrint('Object %s doesn\'t exist' % (elt.name()+'_storedPos'), 1)
            else:
                if pmc.objExists(elt.name().replace('_storedPos', '')):
                    obj = pmc.PyNode(elt.name().replace('_storedPos', ''))
                    attrs = ['t', 'r', 's', 'jo']
                    for i in range(len(attrs)):
                        
                        try:
                            pmc.PyNode(obj+'.'+attrs[i]).set(pmc.PyNode(elt+'.'+attrs[i]+'_stored').get())
                             
                        except:
                            vp.vPrint('No data founded from %s in rigPosingSet set' % elt.name(), 1)
                else:
                    vp.vPrint('Object %s doesn\'t exist' % elt.name().replace('_storedPos', ''), 1)




def restorePosingSKNUI():
    restorePosingSKN(pmc.ls(sl=True))






#                 #
#   CONNECT SKN   #
#                 #


def connectSKN():
    # get SKN jnt
    jnts = pmc.ls('*SKNjnt')
    
    # check matrix plug in
    matrixConstrain.__checkMatrixConstrain__()
    
    for jnt in jnts:
        # check if a 2SK joint exist
        master = various.checkObj(jnt.name().replace('SKNjnt', '2SKjnt'), type=['joint'])
        if master:
            # create matrix constrain
            matrixConstrain.__createMatrixConstrain__(master, jnt, channel=[1,1,1,1], mo=False, calculateMo=False)
            # set joint orient at 0
            jnt.jointOrient.set([0,0,0])





#                   #
#   DECONNECT SKN   #
#                   #

def deconnectSKN():
    # get SKN jnt
    jnts = pmc.ls('*SKNjnt')
    
    for jnt in jnts:
        # delete matrix
        matrixConstrain.__deleteMatrixConstrain__(jnt)
    # restore data from rotate to joint orient
    __restorePosingSKN__(None)

