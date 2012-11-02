#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 15 nov 2011
#
#   copy and paste skin influence
#


import pymel.core as pmc
import maya.cmds as cmds
import common.vPrint as vp
import common.various as various
import common.decorator as dec
import skin as skinTools
import ui as uiTools



class copyPasteWeight():

    def __init__(self):
        # variables
        self._weight = {}
        self._ite    = 0
            
    
    #          #
    #   COPY   #
    #          #
    
    #@vp.inOut
    def copyWeight(self, *args):
        """save skin data"""
        self._weight = {}
        self._ite    = 0
        
        # ui loading
        uiProgressWindow = uiTools.gaugeWindow('Saving', maxAmount=len(args))
                
        for arg in args:
            if isinstance(arg, list) == False:
                arg = [arg]
            if not self.__addWeight__(arg):
                # an error was found
                uiProgressWindow.terminate()
                return False
            # ui Progress
            uiProgressWindow.progress(1)
            
        self.__divWeight__()
        
        # ui stoping
        uiProgressWindow.terminate()
        
        return True
    
    def __addWeight__(self, geoms):
        for geom in geoms:

            self._ite += various.getNumAtoms(geom)
            
            # getting skin cluster node
            skinNodes = geom.node().history(type='skinCluster')
            if len(skinNodes):
                skinNode = skinNodes[-1] 
            else:
                vp.vPrint('No skinCluster node on %s' % geom, 1)
                return False
            
            # get list joint from skin cluster
            jointsList = skinNode.influenceObjects()
            
            for i in range(len(jointsList)):
                wtsData = skinNode.getWeights(geom,i)
                # addition data into _weight variable
                for wtData in wtsData:
                    if wtData != 0.0:
                        if not self._weight.has_key(jointsList[i]):
                            self._weight[jointsList[i]] = wtData
                        else:
                            self._weight[jointsList[i]] += wtData
        return True

    def __divWeight__(self):
        # divide data according to how many vertices were on the process
        for value in self._weight.keys():
            self._weight[value] /= self._ite
    
    
    
    #           #
    #   PASTE   #
    #           #
    
    @dec.undoable
    #@vp.inOut
    def pasteWeight(self, *args, **kwargs):
        """paste skin data"""
        if len(self._weight):
            # ui loading
            uiProgressWindow = uiTools.gaugeWindow('Saving', maxAmount=len(args))            
            
            # check kwargs
            if  not kwargs.has_key('methode'):
                kwargs['methode'] = 0
            if  not kwargs.has_key('keepBonesLocked'):
                kwargs['keepBonesLocked'] = False
            if  not kwargs.has_key('addMissInf'):
                kwargs['addMissInf'] = True
            if  not kwargs.has_key('copyPercent'):
                kwargs['copyPercent'] = False
            if  not kwargs.has_key('percent'):
                kwargs['percent'] = 0.2
            
            # no point to do a copy percent if the weight deire is at 1.0
            if kwargs['copyPercent'] and (kwargs['percent']==1.0):
                kwargs['copyPercent'] = False
            
            for arg in args:
                if kwargs['copyPercent'] and kwargs['methode']==0:
                    arg = various.getAtoms(arg, flat=True)
                elif isinstance(arg, list) == False:
                    arg = [arg]
                for a in arg:
                    self.__pasteWeight__(a, methode=kwargs['methode'], keepBonesLocked=kwargs['keepBonesLocked'], addMissInf=kwargs['addMissInf'], copyPercent=kwargs['copyPercent'], percent=kwargs['percent'])
                # ui Progress
                #uiProgressWindow.progress(1)
            
            # ui stoping
            uiProgressWindow.terminate()
    
    
    def __pasteWeight__(self, geom, methode=0, keepBonesLocked=False, addMissInf=True, copyPercent=False, percent=0.2):
        # getting skin cluster node
        skinNodes = geom.node().history(type='skinCluster')
        
        # get list joint from _weight
        checkJoints = self._weight.keys()
        
        # check if the object has already a skin cluster node
        if len(skinNodes):
            skinNode = skinNodes[-1]
        else:
            skinNode = pmc.skinCluster(checkJoints, geom.node(), toSelectedBones=True, normalizeWeights=1)[0]
        
        # get each joint connect on the skin cluster
        jointsList = skinNode.influenceObjects()
        
        # check if any joint are missing
        addJoints = skinTools.__findMissingInfluence__(skinNode, checkJoints)
        
        # if anything missing and addInluence variable and true so lets add what we need
        if (len(addJoints)>0):
            if addMissInf:
                skinTools.__addInfluence__(skinNode, addJoints)
                message = []
                for i in range(len(addJoints)):
                    message.append(addJoints[i].name())
                vp.vPrint('Bone(s) added, %s' % (' '.join(message)), 1)
            else:
                message = []
                for i in range(len(addJoints)):
                    message.append(addJoints[i].name())
                vp.vPrint('Missing bone(s) influence, %s' % (' '.join(message)), 1)
                return False
        
        # keeping and changing the normalization weights
        previousNormalize = skinNode.normalizeWeights.get()
        skinNode.normalizeWeights.set(0)
        
        skinPerc = []
        
        # loop for each bones
        for bone in self._weight.keys():
            
            # check if the bone is not locked
            if (keepBonesLocked==False) or (bone.liw.get()==False):
                # get the right Id
                IdInfl = skinTools.getIdInfluence(skinNode, bone.name())
                # if we keep a part of the previous data
                if copyPercent:
                    wtsData = skinNode.getWeights(geom, IdInfl)
                    data = []
                    for wtData in wtsData:
                        data.append((wtData * (1-percent)) + (self._weight[bone] * percent))
                    if methode == 0:
                        skinPerc.append( (bone.name(), data[0]) )
                    else:
                        skinNode.setWeights(geom, [IdInfl], data, normalize=False)
                    
                else:
                    if methode == 0:
                        skinPerc.append( (bone.name(), self._weight[bone]) )
                    else:
                        skinNode.setWeights(geom, [IdInfl], [self._weight[bone]], normalize=False)
                
        
        # check if there is some influence wich weren't changed
        if copyPercent:
            # for the percent logic
            if len(checkJoints) < len(jointsList):
                for jointList in jointsList:
                    if (keepBonesLocked==False) or (jointList.liw.get()==False):
                        if (jointList in checkJoints) == False:
                            IdInfl  = skinTools.getIdInfluence(skinNode, jointList)
                            wtsData = skinNode.getWeights(geom, IdInfl)
                            data = []
                            for wtData in wtsData:
                                data.append(wtData * (1-percent))
                            if methode == 0:
                                skinPerc.append( (jointList.name(), data[0]) )
                            else: 
                                skinNode.setWeights(geom, [IdInfl], data, normalize=False)
        else:
            # or in a normal copy paste
            if len(checkJoints) < len(jointsList):
                for jointList in jointsList:
                    if (keepBonesLocked==False) or (jointList.liw.get()==False):
                        if (jointList in checkJoints) == False:
                            if methode == 0:
                                skinPerc.append( (jointList.name(), 0.0) )
                            else:
                                IdInfl = skinTools.getIdInfluence(skinNode, jointList)
                                skinNode.setWeights(geom, [IdInfl], [0], normalize=False)
        
        
        if methode == 0:
            pmc.skinPercent( skinNode, geom, transformValue=skinPerc)
        
        # normalize data if the user desire to get some bones unchanged
        if keepBonesLocked:
            skinTools.normalize(skinNode, geom, methode=methode, keepBonesLocked=True)
        
        
        # changing the normalization weights from previous data
        skinNode.normalizeWeights.set(previousNormalize)
    
        return True
    
    
    def check(self):
        """check if there is any data to copy"""
        if len(self._weight.keys()):
            return True
        else:
            return False
    
    
    def getInfluence(self):
        """return the PyNode list of bones"""
        bones = []
        for key in self._weight:
            bones.append(key)
        return bones
    
    
    def printInfluences(self):
        """Print Influences"""
        length = 0
        for key in self._weight:
            length += self._weight[key]
            vp.vPrint('%s : %s' % (key, self._weight[key]), 2)
        vp.vPrint('total : %s' % (length), 2)
    
    def __del__(self):
        del self._weight
        del self._ite

