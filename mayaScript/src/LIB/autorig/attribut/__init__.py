#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 09 dec 2011
#
#   various attributs definition for AutoRig
#



import pymel.core as pmc
import common.vPrint as vp
import common.various as various




#                  #
#   STORE POSING   #
#                  #


def storePosingRIG(*args):
    """Save posing from CONTROLS set"""
    
    if args:
        for arg in args:
            if isinstance(arg, list) == False:
                arg = [arg]
            for i in range(len(arg)):
                arg[i] = various.checkObj(arg[i], type=['transform', 'joint'])
            if (None in arg)==False:
                __storePosingRIG__(arg)
    else:
        __storePosingRIG__(None)



def __storePosingRIG__(elts):
    if elts==None:
        # get each element inside CONTROL
        if pmc.objExists('CONTROLS'):
            elts = pmc.sets('CONTROLS', query=True)
            i=0
            while i<len(elts):
                if pmc.objectType(elts[i]) == 'objectSet':
                    elts.extend(pmc.sets(elts[i], query=True))
                    elts.pop(i)
                    i -= 1
                i += 1
        else:
            vp.vPrint('No CONTROLS set funded', 1)
        fromSelection = False
    else:
        if pmc.objExists('CONTROLS')==False:
            vp.vPrint('No CONTROLS set funded', 1)
            elts = None
        fromSelection = True
    
    if elts:
        pmc.select(clear=True)
        # create set were each curve will be stored
        if pmc.objExists('rigPosingSet')==False:
            pmc.sets(name='rigPosingSet')
        
        # create sub sets if need
        bindPoseSet = 'RIG_bindPose'
        if pmc.objExists(bindPoseSet)==False:
            bindPose = pmc.sets(name=bindPoseSet)
            pmc.sets('rigPosingSet', addElement=bindPose)
        
        
        for elt in elts:
            isMember = True
            
            if fromSelection:
                isMember = pmc.sets('CONTROLS', isMember=elt)
             
            if isMember:
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
                
                
                attrs = pmc.listAttr(elt, keyable=True)
                
                for attr in attrs:
                    attr = pmc.PyNode(elt+'.'+attr)
                    if attr.type() == 'enum':
                        pmc.addAttr(set, longName=attr.longName()+'_stored', attributeType='byte', defaultValue=attr.get())
                    elif attr.type() in ['double', 'doubleAngle', 'doubleLinear', 'byte', 'bool', 'long', 'short', 'char', 'float']:
                        pmc.addAttr(set, longName=attr.longName()+'_stored', attributeType=attr.type(), defaultValue=attr.get())
                    pmc.PyNode(set+'.'+attr.longName()+'_stored').setLocked(True)
            else:
                vp.vPrint('%s is not a member of CONTROLS set' % elt, 1)



def storePosingRIGUI():
    storePosingRIG(pmc.ls(sl=True))





#                    #
#   RESTORE POSING   #
#                    #



def restorePosingRIG(*args):
    """restore posing"""
    if args:
        for arg in args:
            if isinstance(arg, list) == False:
                arg = [arg]
            for i in range(len(arg)):
                arg[i] = various.checkObj(arg[i], type=['transform', 'joint'])
            if (None in arg)==False:
                __restorePosingRIG__(arg)
    else:
        __restorePosingRIG__(None)




def __restorePosingRIG__(elts):

    if elts==None:
        # get each objects from rigShapesSet
        if pmc.objExists('RIG_bindPose'):
            elts = pmc.sets('RIG_bindPose', query=True)
        fromSelection=False
    else:
        fromSelection=True
    
    if elts:
        for elt in elts:
            if fromSelection:
                if pmc.objExists(elt.name()+'_storedPos'):
                    obj = elt.name()+'_storedPos'
                    attrs = pmc.listAttr(elt, keyable=True)
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
                    attrs = pmc.listAttr(obj, keyable=True)
                    for i in range(len(attrs)):
                        try:
                            pmc.PyNode(obj+'.'+attrs[i]).set(pmc.PyNode(elt+'.'+attrs[i]+'_stored').get())
                             
                        except:
                            vp.vPrint('No data founded from %s in rigPosingSet set' % elt.name(), 1)
                else:
                    vp.vPrint('Object %s doesn\'t exist' % elt.name().replace('_storedPos', ''), 1)




def restorePosingRIGUI():
    restorePosingRIG(pmc.ls(sl=True))


