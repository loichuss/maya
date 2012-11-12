#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 09 dec 2011
#
#   Various definition about shapes for autorig
#


import pymel.core as pmc
import pymel.core.datatypes as dt
import common.vPrint as vp
import common.various as various




#                 #
#   SCALE SHAPE   #
#                 #


def scaleShape(shape, objStart, objEnd, proportion=1, axis=[1,0,0]):
    # get distance
    distObj = pmc.createNode('distanceDimShape')
    if (isinstance(objStart, list)):
        distObj.startPoint.set(objStart)
    else:
        distObj.startPoint.set(objStart.getTranslation(space='world'))
    
    if (isinstance(objEnd, list)):
        distObj.startPoint.set(objEnd)
    else:
        distObj.endPoint.set(objEnd.getTranslation(space='world'))
    dist = distObj.distance.get()
    # delete distance object
    pmc.delete(distObj.getParent())
    # create a vector
    distVect = dt.Vector( dist*axis[0], dist*axis[1], dist*axis[2] )
    inveVect = dt.Vector( (1-axis[0])*proportion, (1-axis[1])*proportion, (1-axis[2])*proportion )
    distVect = distVect+inveVect
    # scale shape
    pmc.scale(various.getAtoms(shape, flat=True), distVect, relative=True)




#                      #
#   REPOSITION SHAPE   #
#                      #

def positionShape(shape, position, offset=[0,0,0]):
    # check the type of position
    if (isinstance(position, dt.Vector))==False:
        if (isinstance(position, list))==False:
            obj = various.checkObj(position, type=['transform', 'joint'])
            if obj:
                position = obj.getTranslation(space='world')
        else:
            position = dt.Vector(position)
    
    # get difference between the parent of the shape and the global position
    move = position - pmc.PyNode(shape).getParent().getTranslation(space='world')
    for vert in various.getAtoms(shape, flat=True):
        pmc.move(vert, move, relative=True)





#                 #
#   STORE SHAPE   #
#                 #



def storeShapes(*args):
    """Save on sets shapes from CONTROLS set"""
    if args:
        for arg in args:
            if isinstance(arg, list) == False:
                arg = [arg]
            for i in range(len(arg)):
                arg[i] = various.checkObj(arg[i], type=['transform', 'joint'])
            if (None in arg)==False:
                __storeShapes__(arg)
    else:
        __storeShapes__(None)


def __storeShapes__(elts):
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
        if pmc.objExists('rigShapesSet')==False:
            pmc.sets(name='rigShapesSet')
            
        
        for elt in elts:
            isMember = True
            
            if fromSelection:
                isMember = pmc.sets('CONTROLS', isMember=elt)
             
            if isMember:
                # check if any previous set exist
                if pmc.objExists(elt.name()+'_storedShp'):
                    if pmc.sets('rigShapesSet', query=True, size=True) == 1:
                        pmc.delete(elt.name()+'_storedShp')
                        pmc.sets(name='rigShapesSet')
                    else:
                        pmc.delete(elt.name()+'_storedShp')
                # create set
                set = pmc.sets(name=elt.name()+'_storedShp')
                pmc.sets('rigShapesSet', addElement=set)
                
                # get atoms from selection
                atoms = various.getAtoms(elt)
                
                for i in range(len(atoms)):
                    # create attribut
                    pmc.addAttr(set, longName='cv'+str(i), attributeType='double3')
                    pmc.addAttr(set, longName='cv'+str(i)+'X', attributeType='double', parent='cv'+str(i))
                    pmc.addAttr(set, longName='cv'+str(i)+'Y', attributeType='double', parent='cv'+str(i))
                    pmc.addAttr(set, longName='cv'+str(i)+'Z', attributeType='double', parent='cv'+str(i))
                    
                    # add position into attribut
                    pmc.PyNode(set+'.cv'+str(i)).set(atoms[i].getPosition(space='world'))
            else:
                vp.vPrint('%s is not a member of CONTROLS set' % elt, 1)



def storeShapesUI():
    storeShapes(pmc.ls(sl=True))





#                   #
#   RESTORE SHAPE   #
#                   #


def restoreShapes(*args):
    """restore shapes"""
    if args:
        for arg in args:
            if isinstance(arg, list) == False:
                arg = [arg]
            for i in range(len(arg)):
                arg[i] = various.checkObj(arg[i], type=['transform', 'joint'])
            if (None in arg)==False:
                __restoreShapes__(arg)
    else:
        __restoreShapes__(None)


def __restoreShapes__(elts):

    if elts==None:
        # get each objects from rigShapesSet
        if pmc.objExists('rigShapesSet'):
            elts = pmc.sets('rigShapesSet', query=True)
        fromSelection=False
    else:
        fromSelection=True
    
    if elts:
        for elt in elts:
            if fromSelection:
                atoms = various.getAtoms(elt.getShape(), flat=False)
                for i in range(len(atoms)):
                    try:
                        pmc.move(atoms[i], pmc.PyNode(elt.name()+'_storedShp.cv'+str(i)).get(), absolute=True)
                    except:
                        vp.vPrint('No %s in rigShapesSet set' % (elt.name()+'_storedShp'), 1)
            else:
                if pmc.objExists(elt.name().replace('_storedShp', '')):
                    obj = pmc.PyNode(elt.name().replace('_storedShp', '')).getShape()
                    atoms = various.getAtoms(obj, flat=False)
                    for i in range(len(atoms)):
                        try:
                            pmc.move(atoms[i], pmc.PyNode(elt+'.cv'+str(i)).get(), absolute=True)
                        except:
                            vp.vPrint('No data founded from %s in rigShapesSet set' % elt.name(), 1)
                else:
                    vp.vPrint('Shape %s doesn\'t exist' % elt.name().replace('_storedShp', ''), 1)



def restoreShapesUI():
    restoreShapes(pmc.ls(sl=True))







#                     #
#   MIRRORING SHAPE   #
#                     #


def mirrorShapes(*args, **kwargs):
    """Mirroring shapes"""
    
    # check kwargs
    if ('across' in kwargs.keys())==False:
        kwargs['across'] = 'x'
    if ('direction' in kwargs.keys())==False:
        kwargs['direction'] = 'L_'
    
    # check args
    if args:
        for arg in args:
            if isinstance(arg, list) == False:
                arg = [arg]
            for i in range(len(arg)):
                arg[i] = various.checkObj(arg[i], type=['transform', 'joint'])
            if (None in arg)==False:
                __mirrorShapes__(arg, across=kwargs['across'], direction=kwargs['direction'])
    else:
        __mirrorShapes__(None, across=kwargs['across'], direction=kwargs['direction'])


def __mirrorShapes__(elts, across='x', direction='L_'):
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
            
            # delete element at center meaning without L_ or R_
            
            for i in reversed(range(len(elts))):
                if (elts[i].name().startswith(direction)==False):
                    elts.pop(i)
        else:
            vp.vPrint('No CONTROLS set funded', 1)
            
    else:
        # delete element at center meaning without L_ or R_
        for i in reversed(range(len(elts))):
            if (elts[i].name().startswith('L_')==False) and (elts[i].name().startswith('R_')==False):
                elts.pop(i)
    
    # creating the vector inverse depending on the across variable
    if across=='x':
        vectInverse = [-1,1,1]
    if across=='y':
        vectInverse = [1,-1,1]
    if across=='z':
        vectInverse = [1,1,-1]
    
    # loop into each element
    for elt in elts:
        # finding the opposite transform
        if elt.startswith('L_'):
            eltInv = various.checkObj( elt.name().replace('L_', 'R_'), type=['transform', 'joint'] )
        else:
            eltInv = various.checkObj( elt.name().replace('R_', 'L_'), type=['transform', 'joint'] )
        
        if eltInv:
            # getting atoms from both element
            atoms    = various.getAtoms(elt,    flat=False)
            atomsInv = various.getAtoms(eltInv, flat=False)
            # finding the smallest object just in case one has less atoms than the other
            if len(atoms) > len(atomsInv):
                size = len(atomsInv)
            else:
                size = len(atoms)
            # working on each atoms
            for i in range(size):
                pmc.move(atomsInv[i], atoms[i].getPosition(space='world')*vectInverse, absolute=True)


def mirrorShapesUI():
    mirrorShapes(pmc.ls(sl=True))

