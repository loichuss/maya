#
#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 08 nov 2011
#
#   Different Tools for Skinning
#


import pymel.core as pmc
import common.vPrint as vp
import common.various as various





#                      #
#   GET ID INFLUENCE   #
#                      #

def getIdInfluence(skinNode, influence):
    skinNodeInfs = skinNode.getInfluence()
    for i in range(0, len(skinNodeInfs)):
        if skinNodeInfs[i] == influence:
            return i



#                   #
#   MISSING BONES   #
#                   #

def findMissingInfluence(skinNode, influences):
    """from one skinCluster PyNode variable and a list of bones the function will return if any bones are missing in the skinCluster node"""
    # checking skin cluster node
    skinNode = various.checkObj(skinNode, type=['skinCluster'])
    
    # if we get a string we convert it as a list
    if isinstance(influences, str):
        influences = [influences]
    
    # check if the list of bones as string that we get exist
    influencesOut = []
    for influence in influences:
        tmp = various.checkObj(influence, type=['joint'])
        if tmp != None:
            influencesOut.append(tmp)
    
    # calling the private function
    if skinNode != None:
        return __findMissingInfluence__(skinNode, influencesOut)





def __findMissingInfluence__(skinNode, influences):
    # variables
    bonesMissing = []

    # to get the list of bones working with the skin cluster 
    skinNodeInfs = skinNode.influenceObjects()
    
    # loop in array to check if anything is missing
    for influence in influences:
        if (influence in skinNodeInfs) == False:
            bonesMissing.append(influence)
    
    return bonesMissing






#               #
#   ADD BONES   #
#               #

def addInfluence(skinNode, influences, **kwargs):
    # check kwargs
    if ('skipSelect' in kwargs.keys())==False:
        kwargs['skipSelect'] = True
    
    """Add influences into skinCluster"""
    # check if the skin node exist
    skinNode   = various.checkObj(skinNode, type=['skinCluster'])
    
    # if we get a string we convert it as a list
    if isinstance(influences, str):
        influences = [influences]
        
    # check if the list of bones as string that we get exist
    influencesOut = []
    for influence in influences:
        tmp = various.checkObj(influence, type=['joint'])
        if tmp != None:
            influencesOut.append(tmp)

    # calling the private function
    if skinNode != None:
        if len(influencesOut)!=0:
            __addInfluence__(skinNode, influencesOut, skipSelect=kwargs['skipSelect'])
        else:
            vp.vPrint('no joint founded' % tmp, 1)






def __addInfluence__(skinNode, influences, skipSelect=True):
    skinInfluences = skinNode.influenceObjects()
    if skipSelect:
        sels = pmc.ls(sl=True)
    for influence in influences:
        if (influence in skinInfluences) == False:
            skinNode.addInfluence(influence, weight=0.0)
        else:
            vp.vPrint('Influence object %s is already attached' % influence, 1)
    if skipSelect:
        pmc.select(sels, replace=True)



#               #
#   NORMALIZE   #
#               #


def normalize(skinNode, geoms, methode=0, keepBonesLocked=False):
    """normalize"""
    
    # get atom if possible
    geoms = various.getAtoms(geoms)
    
    # get influence list
    joints = skinNode.influenceObjects()
    
    # get which bones is not locked
    a = []
    for i in range(len(joints)):
        if (keepBonesLocked==False) or (joints[i].liw.get()==False):
            a.append(i)
    
    # loop on goemetry
    for geom in geoms:
        # loop again to get a single object no [x:x]
        for geo in geom:
            # the length will be the total of each influence
            length     = 0
            lengthLock = 0
            data       = []
            # loop for each bones
            for i in range(len(joints)):
                wts = skinNode.getWeights(geo, i)
                for wt in wts:
                    if keepBonesLocked:
                        if joints[i].liw.get():
                            lengthLock += wt
                        else:
                            length += wt
                    else:
                        length += wt
                    data.append(wt)
            print length
            print lengthLock
            # if lenght is not equal 1.0 we aren't normalize
            if (length+lengthLock) != 1.0:
                
                skinPerc = []
                
                # check if not everything is locked
                if len(a) == len(data):
                    keepBonesLocked = False
                    
                    
                # more complexe methode when some bones has to be kept as they are
                if keepBonesLocked:
                
                    # we check if the length of the locked bones is less than 1.0
                    if lengthLock < 1.0:
                        # check if length is not equal at zero
                        if length:
                            # multiply each influence by the invert length
                            length = (1-lengthLock) / length
                            if methode == 0:
                                for i in range(0, len(a)):
                                    skinPerc.append( (joints[a[i]], data[a[i]]*length) )
                            else:
                                for i in range(0, len(a)):
                                    data[i] = data[a[i]]*length
                                    
                        else:
                            add = (1-lengthLock) / len(a)
                            if methode == 0:
                                for i in range(0, len(a)):
                                    skinPerc.append( (joints[a[i]], data[a[i]]+add) )
                            else:
                                for i in range(0, len(a)):
                                    data[i] = data[a[i]]+add
                        
                    # otherwise we just keep other weight at 0
                    else :
                        if methode == 0:
                            for i in range(0, len(a)):
                                skinPerc.append( (joints[i], 0) )
                        else:
                            for i in range(0, len(a)):
                                data[i] = 0
            
                # simple one
                else :
                    if methode == 0:
                        for i in range(0, len(a)):
                            skinPerc.append( (joints[i], data[i]/length) )
                    else: 
                        for i in range(0, len(a)):
                            data[i] = data[i]/length
                
                # keeping and changing the normalization weights
                previousNormalize = skinNode.normalizeWeights.get()
                skinNode.normalizeWeights.set(0)
                
                # set with the right data
                if methode == 0:
                    pmc.skinPercent( skinNode, geo, transformValue=skinPerc)
                else:
                    skinNode.setWeights(geo, a, data, normalize=False)
                
                # changing the normalization weights from previous data
                skinNode.normalizeWeights.set(previousNormalize)
