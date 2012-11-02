#
#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 07 nov 2011
#
#   SaveLoadSkin
#

import pymel.core as pmc
import common.vPrint as vp
import common.various as various
import skin as skinTools
import ui as uiTools
import clean


#          #
#   SAVE   #
#          #

def SWCsaveSkin(*args, **kwargs):
    """Save skinCluster node data into extra attribut"""
    
    # check kwargs
    if ('grpName' in kwargs.keys())==False:
        kwargs['grpName'] = 'SWC_saveLoad_grp'
    
    # working on each object given
    for arg in args:
        if isinstance(arg, list) == False:
            arg = [arg]
        for obj in arg:
            obj = various.checkObj(obj, type=['transform'])
            if obj != None:
                __SWCsaveSkin__(obj, grpName=kwargs['grpName'])



@vp.inOut
def __SWCsaveSkin__(obj, grpName='SWC_saveLoad_grp'):
    # importantes variables
    prefix = 'def_'
    
    # getting skin cluster node
    skinNodes = obj.history(type='skinCluster')
    
    # if we find a skin cluster node
    if len(skinNodes):
        # check and create grp for copy object
        grp = various.checkObj(grpName, type=['transform'], echo=False)
        if grp == None:
            grp = pmc.createNode('transform', name=grpName, ss=True)
        grp.hide()
        
        for skinNode in skinNodes:
            # to get the proper shape
            index      = 0
            pathIndex  = skinNode.indexForOutputConnection(index)
            skinPath   = skinNode.getPathAtIndex(pathIndex)
            jointsList = skinNode.getInfluence()
            
            # ui loading
            uiProgressWindow = uiTools.gaugeWindow('Saving', maxAmount=len(jointsList)+1)
            
            # copy the current obj, deleting the history and each useless meshOrig
            if pmc.objExists(grpName+'|SWC_' + skinPath.name()):
                pmc.delete(grpName+'|SWC_' + skinPath.name())
                vp.vPrint('SWC %s was present' % ('SWC_' + skinPath.name()), 1)
            objSWC = pmc.duplicate(obj, inputConnections=False, parentOnly=False, renameChildren=True, name='SWC_' + skinPath.name())[0]
            objSWC.hide()
            pmc.runtime.DeleteHistory(objSWC)
            clean.cleanOrig(objSWC)
            objSWC.setParent(grp)
            
            # create children extra attribut
            __SWCaddExtraAttribut__(objSWC, prefix, jointsList)
            
            # feading each children extra attribut
            attr = pmc.PyNode(objSWC+'.'+prefix+'jointName')
            attr.set(skinNode.getInfluence())
            
            attr = pmc.PyNode(objSWC+'.'+prefix+'corJointName')
            attr.set(skinNode.getInfluence())
            
            # parsing each vertice from the shape to get the weights
            for i in range(0, len(jointsList)):
                wts       = []
                wtsData = skinNode.getWeights(skinPath,i)
                for wtData in wtsData:
                    wts.append(wtData)
                # add data into extra attribut
                attr = pmc.PyNode(objSWC+'.'+prefix+'jointArray.'+prefix+jointsList[i])
                attr.set(wts)
                # ui Progress
                uiProgressWindow.progress(1)
            
            # keeping information about normalization
            attr = pmc.PyNode(objSWC+'.'+prefix+'normalize')
            attr.set(skinNode.normalizeWeights.get())
            attr.setLocked(True)
            
            # copy each default data into the current one. The current one could be modify we always can go back to the default one
            __SWCresetData__(objSWC)
            
            # ui Progress
            uiProgressWindow.progress(1)
            
            # ui stoping
            uiProgressWindow.terminate()

    else:
        vp.vPrint('No skinCluster node on %s' % obj, 1)





#          #
#   LOAD   #
#          #

def SWCloadSkin(*args, **kwargs):
    """Load skinCluster from SWC data"""

    # check kwargs
    if ('grpName' in kwargs.keys())==False:
        kwargs['grpName'] = 'SWC_saveLoad_grp'
    if ('delSkin' in kwargs.keys())==False:
        kwargs['delSkin'] = True
    
    # working on each object given
    for arg in args:
        if isinstance(arg, list)==False:
            arg = [arg]
        
        # check the selection type
        component = various.isComponent(arg[0])
        if component == False:
            for obj in arg:
                obj = various.checkObj(obj, type=['transform'])
                if obj != None:
                    __SWCloadSkin__(obj, component, grpName=kwargs['grpName'], delSkin=kwargs['delSkin'])
        else:
            # check if the same object TO DO
            __SWCloadSkin__(arg, component, grpName=kwargs['grpName'])


@vp.inOut
def __SWCloadSkin__(obj, component, grpName='SWC_saveLoad_grp', delSkin=True):
    # getting the shape where the cluster node will be create
    if component:
        objShape = pmc.PyNode(obj[0].node())
    else:
        objShape = obj.getShape()
    
    # finding the SWC object
    objSwc = various.checkObj(grpName+'|SWC_' + objShape.name().replace('|', '_'))
    
    if objSwc:
        # check if the object has a skin cluster node
        prevSkinNodes = objShape.history(type='skinCluster')
       
        # get influences obejct from extra attribut
        influencesObject = objSwc.jointName.get()
        
        # ui loading
        uiProgressWindow = uiTools.gaugeWindow('Loading', maxAmount=len(influencesObject))
        
        # check if each joints are present in scene
        missing = False
        for influenceObject in influencesObject:
            if various.checkObj(influenceObject) == None:
                vp.vPrint('%s is missing in scene' % influenceObject, 1)
                missing = True
        if missing:
            uiProgressWindow.terminate()
            return False
        
        # check if the selection is component or not
        if component:
            # create a fast skinCluster node if need it
            if len(prevSkinNodes)==0:
                skinNode = pmc.skinCluster(influencesObject, objShape, toSelectedBones=True, normalizeWeights=1)
            else :
                skinNode = prevSkinNodes[-1]
            
            # check and add influence if need it
            checkInfluences = skinTools.__findMissingInfluence__(skinNode, influencesObject)
            if len(checkInfluences):
                skinTools.addInfluence(skinNode, checkInfluences)
            
            # keeping and changing the normalization weights
            previousNormalize = skinNode.normalizeWeights.get()
            skinNode.normalizeWeights.set(0)
            
            # perform the copy
            for geoms in obj:
                # updating the maxAmount
                uiProgressWindow.setMaxAmount(len(obj))
                
                keep = []
                # finding the indice vertice to work only with them
                for geom in geoms:
                    keep.append(geom._indices[0])
                
                # loop for each bones
                for i in range(0, len(influencesObject)):
                    attrAll = pmc.PyNode(objSwc+'.joinArray.'+influencesObject[i]).get()
                    attr    = []
                    IdInfl  = skinTools.getIdInfluence(skinNode, influencesObject[i])
                    for k in keep:
                        attr.append(attrAll[k])
                    skinNode.setWeights(geoms, [IdInfl], attr, normalize=False)
                
                # check if there is some influence wich weren't changed
                influencesNode = skinNode.getInfluence()
                if len(influencesObject) < len(influencesNode):
                    for influenceNode in influencesNode:
                        if (influenceNode in influencesObject) == False:
                            IdInfl = skinTools.getIdInfluence(skinNode, influenceNode)
                            skinNode.setWeights(geoms, [IdInfl], [0], normalize=False)
                
                # ui Progress
                uiProgressWindow.progress(1)
                
            
            # changing the normalization weights from previous data
            skinNode.normalizeWeights.set(previousNormalize)
            
        else:
            if len(prevSkinNodes) == 0:
                # create the skin cluster node on object
                skinNode = pmc.skinCluster(influencesObject, objShape, toSelectedBones=True, normalizeWeights=0)
            else:
                if delSkin:
                    # delete skin cluster and clean the shape orig
                    pmc.delete(prevSkinNodes)
                    clean.__cleanOrig__(obj)
                    skinNode = pmc.skinCluster(influencesObject, objShape, toSelectedBones=True, normalizeWeights=0)

                else:
                    # stop the function if a skin cluster is already present
                    vp.vPrint('%s has already a skin cluster' % objShape.getParent(), 1)
                    uiProgressWindow.terminate()
                    return False
        
            # perform the copy
            for i in range(len(influencesObject)):
                attr = pmc.PyNode(objSwc+'.joinArray.'+influencesObject[i])
                skinNode.setWeights(objShape, [i], attr.get(), normalize=False)
                
                # ui Progress
                uiProgressWindow.progress(1)
                
            skinNode.normalizeWeights.set(objSwc.normalize.get())

        # ui stoping
        uiProgressWindow.terminate()
        





#                       #
#   CREATE EXTRA ATTR   #
#                       #

def __SWCaddExtraAttribut__(obj, prefix, jointsList):

    # joint array attribut has the name of each bones
    if (obj.hasAttr(prefix+'jointName')) == False:
        pmc.addAttr(obj, longName=prefix+'jointName', dataType='stringArray', hidden=True )
    
    # if prefix we add a special axtra attribut wish is the perfect correspondance between the defaut bones and the new one
    if prefix == 'def_':
        if (obj.hasAttr(prefix+'corJointName')) == False:
            pmc.addAttr(obj, longName=prefix+'corJointName', dataType='stringArray', hidden=True )
        
    # the normalize info
    if (obj.hasAttr(prefix+'normalize')) == False:
        pmc.addAttr(obj, longName=prefix+'normalize', attributeType='long', keyable=False, hidden=True )
        
    # attribut which will contain each bones
    if (obj.hasAttr(prefix+'jointArray')) == False:
        pmc.addAttr(obj, longName=prefix+'jointArray', attributeType='compound', numberOfChildren=len(jointsList), hidden=True )
        # each bones has a extra attribut which contain the weight of each vertex)
        for i in range(0, len(jointsList)):
            pmc.addAttr(obj, dataType='doubleArray', longName=prefix+jointsList[i], parent=(prefix+'jointArray'), hidden=True )
            


#                             #
#   RESET FROM DEFAULT DATA   #
#                             #


def SWCresetData(*args):
    # working on each object given
    for arg in args:
        if isinstance(arg, list) == False:
            arg = [arg]
        for obj in arg:
            obj = various.checkObj(obj, type=['transform'])
            if obj != None:
                if obj.hasAttr('def_jointName'):
                    __SWCresetData__(obj)
                else:
                    vp.vPrint('%s, is not a SWC object' % obj, 1)


@vp.inOut
def __SWCresetData__(objSWC):
    # get all data at once
    data = []
    data.append(objSWC.def_jointName.get())
    data.append(objSWC.def_jointArray.get())
    data.append(objSWC.def_normalize.get())
    
    # delete jointArray if exist
    if (objSWC.hasAttr('jointArray')):
        pmc.deleteAttr(objSWC.jointArray)
    # create current extra attribut
    __SWCaddExtraAttribut__(objSWC, '', data[0])
    
    # copy data
    # jointName
    attr = pmc.PyNode(objSWC+'.jointName')
    attr.set(data[0])
    attr = pmc.PyNode(objSWC+'.def_corJointName')
    attr.set(data[0])

    # normalization
    attr = pmc.PyNode(objSWC+'.normalize')
    attr.setLocked(False)
    attr.set(data[2])
    attr.setLocked(True)
    
    # jointArray
    for i in range(0, len(data[1])):
        attr = pmc.PyNode(objSWC+'.jointArray.'+data[0][i])
        attr.set(data[1][i])



#                 #
#   CHANGE NAME   #
#                 #

@vp.inOut
def SWCrename(obj, objSWC):
    obj    = various.checkObj(obj,    type=['transform'])
    objSWC = various.checkObj(objSWC, type=['transform'])
    
    if obj != None:
        if obj.getShape() != None:
            if objSWC != None:
                if objSWC.hasAttr('def_jointName'):
                    objSWC.rename('SWC_'+obj.getShape())
                else :
                    vp.vPrint('%s, is not a SWC object' % objSWC, 1)
        else:
            vp.vPrint('%s, doesn\'t have shape' % obj, 1)


#                    #
#   REASSIGN BONES   #
#                    #


def SWCassignBones(objSWC, bonesListIn):
    """Reassign bones influences"""
    # check objSWC
    objSWC = various.checkObj(objSWC, type=['transform'])
    
    if objSWC != None:
        if objSWC.hasAttr('def_jointName'):
            if len(bonesListIn) == len(objSWC.def_jointName.get()):
                bonesList = []
                missing = False
                # checking if in the connectionsIn array each joint exist
                for bone in bonesListIn:
                    bonesList.append(str(bone))
                __SWCassignBones__(objSWC, bonesList)
            else:
                vp.vPrint('the number of bones given is different from the number of default bones', 1)
        else:
            vp.vPrint('%s, is not a SWC object' % objSWC, 1)

@vp.inOut
def __SWCassignBones__(objSWC, bonesList):
    
    # set the attribut
    attr = pmc.PyNode(objSWC+'.jointName')
    attr.set(bonesList)
    attr = pmc.PyNode(objSWC+'.def_corJointName')
    attr.set(bonesList)
    
    # recalculate the influence according to the new data
    __SWCestimateReattribut__(objSWC)
    


def __SWCestimateReattribut__(objSWC):
    bonesNameOld   = objSWC.def_jointName.get()
    bonesNameNew   = objSWC.jointName.get()
    bonesWgt       = objSWC.def_jointArray.get()
    iteSim         = {}
    wgts           = []
    bonesNameClean = []
    
    # find if a bones has multiple copy
    forbide = []
    for i in range(0, len(bonesNameNew)):
        tmp = []
        if (i in forbide)== False:
            for j in range(0, len(bonesNameNew)):
                if (bonesNameNew[j]==bonesNameNew[i]):
                    tmp.append(j)
            forbide.extend(tmp)
            iteSim[i] = tmp
    
    # calculate weight
    for ite in iteSim:
        # name according to new weight
        bonesNameClean.append(bonesNameNew[ite])
        # copy the array
        wgt = bonesWgt[iteSim[ite][0]]
        # if the joint has more than one new destination
        if len(iteSim[ite]) > 1:
            for i in range(1, len(iteSim[ite])):
                for j in range(0, len(wgt)):
                    wgt[j] += bonesWgt[iteSim[ite][i]][j]
        wgts.append(wgt)

    # change jointName by an array without double
    objSWC.jointName.set(bonesNameClean)
    
    # delete jointArray to create a new one with the right name and number of children
    pmc.deleteAttr(objSWC.jointArray)
    __SWCaddExtraAttribut__(objSWC, '', bonesNameClean)
    for i in range(0, len(bonesNameClean)):
        attr = pmc.PyNode(objSWC+'.jointArray.'+bonesNameClean[i])
        attr.set(wgts[i])
    
