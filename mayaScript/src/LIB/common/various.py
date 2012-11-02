#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 16 dec 2011
#
#   Various definition about PyNode object
#


import pymel.core as pmc
import common.vPrint as vp



def checkObj(obj, type=[], echo=True):
    """Check if one object exist in scene, if yes return a PyNode variable"""
    # check if the object exist in the current scene
    if pmc.objExists(obj):
    
        # test if the obj variable is an pynode if node create it
        if isinstance(obj, pmc.PyNode) == False:
            # if we get a string we check if any other object has the same name
            try:
                obj=pmc.PyNode(obj)
            except:
                if echo:
                    vp.vPrint('more than one node has the same name, %s' % str(obj), 1)
                return None
        
        # if component
        if isComponent(obj):
            return None
         
        # checking the type of oject
        if len(type)!=0:
            try:
                if (obj.type() in type) == False:
                    if echo:
                        vp.vPrint('%s is not a %s node' % (obj.name(), ' neither a '.join(type)), 1)
                    return None
            except:
                pass
        
        # return the PyNode variable
        return obj
    else :
        if echo:
            vp.vPrint('%s doesn\'t exist' % obj, 1)
        return None




def renameObject(obj, prefix='_TPLjnt'):
    """Check and rename object"""
    # check if string is not inside the name of the object
    if prefix not in obj.name():
        # if not rename
        obj.rename(obj.name()+prefix)
        return True
    # check if the string is at the end
    elif (obj.name().endswith(prefix)) == False:
        # create the proper name
        newName = obj.name()[0:(obj.name.rfind(prefix)+len(prefix))]
        # check if this object already exist
        if pmc.objExists(newName) == False:
            # if not rename
            obj.rename(newName)
            return True
        else:
            vp.vPrint('another object with same name %s' % newName, 1)
            return False
    else:
        return True


def listChildrenByType(obj, type=['joint']):
    """Return a list of children by type"""
    # list for each children
    objs = [obj]
    # starting the condition
    keep = True
    while keep:
        # getting each children from the latest object in the list
        children = objs[-1].getChildren()
        # if there is not object we stop the while
        if not len(children):
            keep = False
            break
        # a loop into each children
        for child in children:
            # we check the type of the current child
            if checkObj(child, type=type, echo=False):
                objs.append(child)
                keep = True
                break
            else:
                keep = False
    # then we return the list
    return objs




def getShapeType(obj):
    """Return the shape type, what ever you send him"""
    shape = None
    # check if geom is a PyNode type variable
    if isinstance(obj, pmc.PyNode) == False:
        obj=pmc.PyNode(obj)
    # check if we get a component PyNode
    if isComponent(obj):
        shape = pmc.PyNode(obj.split('.')[0])
    else:
        # if it's a transform node we simply get the shape
        tmpObj = checkObj(obj, type=['transform'], echo=False)
        if tmpObj:
            shape = tmpObj.getShape()
        else:
            # each other shapes type
            tmpObj = checkObj(obj, type=['mesh', 'nurbsSurface', 'subdiv', 'nurbsCurve', 'bezierCurve', 'lattice'], echo=False)
            if tmpObj:
                shape=tmpObj
    if shape:
        return shape.type()




def isComponent(obj):
    """Return true if the object given is a component (vertex, edge, face)"""

    # check if the obj variable is a PyNode type
    if isinstance(obj, pmc.PyNode):
        name = obj.name()
    else:
        name = str(obj)
    
    # simply check if the name contain a dot
    if '.' in name:
        return True
    else:
        return False



def getComponentType(geom):
    """Return the component type (vertex, edge, face)"""
    
    # check if geom is a PyNode type variable
    if isinstance(geom, pmc.PyNode) == False:
        geom=pmc.PyNode(geom)
    # check if geom is a component variable
    if isComponent(geom):
        # filter the node type
        if geom.nodeType() == 'mesh':
            if geom._ComponentLabel__ == 'vtx':
                return 'vertex'
            if geom._ComponentLabel__ == 'e':
                return 'edge'
            if geom._ComponentLabel__ == 'f':
                return 'face'
                


def getNumAtoms(geoms):
    """return atoms present in variable (vertices, cvs)"""
    size = 0
    vtx  = getAtoms(geoms)
    for i in range(len(vtx)):
        size += len(vtx[i])
    return size




def getAtoms(geoms, flat=False):
    """return atoms present in variable (vertices)"""
    
    # if geoms is not a list  
    if isinstance(geoms, list)==False:
        geoms = [geoms]
    # loop
    result = []
    comp = None
    doub = False
    for geom in geoms:
        # check if geom is a PyNode type variable
        if (isinstance(geom, pmc.PyNode)) == False:
            geom=pmc.PyNode(geom)
        
        type = getShapeType(geom)
        
        if type == 'mesh':
            result.extend(getMeshAtoms(geom))
            if comp != None:
                try:
                    if comp != geom._ComponentLabel__:
                        doub = True
                except:pass
            else:
                try:
                    comp = geom._ComponentLabel__
                except:pass
        elif type == 'nurbsCurve':
            result.extend(getNurbsCurveAtoms(geom))
        elif type == 'nurbsSurface':
            result.extend(getNurbsSurfaceAtoms(geom))
        elif type == 'lattice':
            result.extend(getLatticeAtoms(geom))
        elif type == 'bezierCurve':
            result.extend(getBezierCurveAtoms(geom))
        elif type == 'subdiv':
            result.extend(getSubdivAtoms(geom))
    
    # check for double
    if doub:
        for i in sorted(range(len(result)), reverse=True):
            for j in sorted(range(len(result)), reverse=True):
                if i != j:
                    if len(result[i].indices()) >= len(result[j].indices()):
                        if result[j] in result[i]:
                            result[j] = None
                        else:
                            start = None
                            end   = None
                            if (result[j].indices()[0] >= result[i].indices()[0]) and (result[j].indices()[0] <= result[i].indices()[-1]):
                                start = result[i].indices()[-1]+1
                            if (result[j].indices()[-1] <= result[i].indices()[-1]) and (result[j].indices()[-1] >= result[i].indices()[0]):
                                end = result[i].indices()[0]-1
                            if (start!=None) and (end!=None):
                                result.pop(j)
                            elif start != None:
                                result[i] = pmc.PyNode( result[i].node().name()+'.vtx['+str(result[i].indices()[0])+':'+str(result[j].indices()[-1])+']' )
                                result.pop(j)
                            elif end != None:
                                result[i] = pmc.PyNode( result[i].node().name()+'.vtx['+str(result[j].indices()[0])+':'+str(result[i].indices()[-1])+']' )
                                result.pop(j)
    
    # create flat result
    if flat:
        resultFlat = []
        for i in range(len(result)):
            resultFlat.extend(result[i])
        return resultFlat
    else:
        return result



def getMeshAtoms(geom):
    # check if geom is a component variable
    if isComponent(geom):
        comp = geom._ComponentLabel__
        if comp:
            if comp == 'vtx':
                return [geom]
            elif comp == 'e':
                vtx = []
                for e in geom:
                    vtx.extend( [e.connectedVertices()[0].indices()[0], e.connectedVertices()[1].indices()[0]] )
                
                # flat
                vtx.sort()
                start = None
                vtxFlat = []
                for i in range(0, len(vtx)-1):
                    if ((vtx[i]+1) == vtx[i+1]) or ((vtx[i]) == vtx[i+1]):
                        if start == None:
                            start = i
                    else:
                        if start != None:
                            vtxFlat.append(pmc.PyNode( geom.node().name()+'.vtx['+str(vtx[start])+':'+str(vtx[i])+']'))
                            start = None
                if start != None :
                    vtxFlat.append(pmc.PyNode( geom.node().name()+'.vtx['+str(vtx[start])+':'+str(vtx[-1])+']'))
                return vtxFlat
            elif comp == 'f':
                vtx = []
                for f in geom:
                    vtx.extend( f.getVertices() )
                
                # flat
                vtx.sort()
                start = None
                vtxFlat = []
                for i in range(0, len(vtx)-1):
                    if ((vtx[i]+1) == vtx[i+1]) or ((vtx[i]) == vtx[i+1]):
                        if start == None:
                            start = i
                    else:
                        if start != None:
                            vtxFlat.append(pmc.PyNode( geom.node().name()+'.vtx['+str(vtx[start])+':'+str(vtx[i])+']'))
                            start = None
                if start != None :
                    vtxFlat.append(pmc.PyNode( geom.node().name()+'.vtx['+str(vtx[start])+':'+str(vtx[-1])+']'))
                return vtxFlat
    # if it's an object and not a component
    elif checkObj(geom, type=['transform', 'mesh']):
        return [geom.vtx]




def getNurbsCurveAtoms(geom):
    # check if geom is a component variable
    if isComponent(geom):
        return [geom]
    elif checkObj(geom, type=['transform', 'nurbsCurve']):
        return [geom.cv]


def getNurbsSurfaceAtoms(geom):# sf surface patch
    # check if geom is a component variable
    if isComponent(geom):
        return [geom]
    elif checkObj(geom, type=['transform', 'nurbsSurface']):
        return [geom.cv]


def getLatticeAtoms(geom):
    # check if geom is a component variable
    if isComponent(geom):
        return [geom]
    elif checkObj(geom, type=['transform', 'lattice']):
        return [geom.pt]


def getBezierCurveAtoms(geom):
    # check if geom is a component variable
    if isComponent(geom):
        return [geom]
    elif checkObj(geom, type=['transform', 'subdiv']):
        return [geom.cv]


def getSubdivAtoms(geom):
    # check if geom is a component variable
    if isComponent(geom):
        return [geom]
    elif checkObj(geom, type=['transform', 'subdiv']):
        return [geom.smp]



