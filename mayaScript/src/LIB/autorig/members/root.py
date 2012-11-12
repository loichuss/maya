#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 12 nov 2012
#
#   Root Module
#

import math
import copy
import pymel.core.datatypes as dt

import common.various as various
import constrain.matrixConstrain as matrixConstrain
import rig.xfm as xfm

import autorig.shape.biblio as arShapeBiblio
import autorig.shape as arShape
import autorig.tools.pickwalk as arPickwalk
import autorig.settings as arParam



class root(object):
    def __init__(self, main, walk, pivot, color=17):
        
        """
        Create a ROOT module
            - main          : the template of the main controller (could be a pymel object or a string)
            - walk          : the template of the sub or walk controller (could be a pymel object or a string)
            - pivot         : a list of third pivot, eac item of this list has to be a tuple of two elements, the first has to be a pivot the second the shape
            - color         : the color of the shape
        """

    
        #                           #
        #   check input variables   #
        #                           #
        
        # variables
        self.check       = True
        self.color       = color
        
        
        # hidden variables
        self._struct     = copy.copy(arParam.STRUCT)


        # properties variables
        self.mainTPL     = main
        self.walkTPL     = walk
        self.pivotTPL    = pivot

        
    
    
    
    
    
    #                  #
    #     CONTROLS     #
    #                  #
    
    @property
    def mainTPL(self):
        return self._struct['TPL']['main']
        
    @mainTPL.setter
    def mainTPL(self, obj):
        self._struct['TPL']['main'] = various.checkObj(obj, type=['transform', 'joint'])
        
        if self._struct['TPL']['main']:
            if various.renameObject(self._struct['TPL']['main'], prefix=arParam.TPL_NAME)==False:
                self.check = False
        else:
            self.check=False
        
    @mainTPL.deleter
    def mainTPL(self):
        self._struct['TPL']['main'] = None

    
    
    
    
    
    
    @property
    def walkTPL(self):
        return self._struct['TPL']['walk']
    
    @walkTPL.setter
    def walkTPL(self, obj):
        self._struct['TPL']['walk'] = various.checkObj(obj, type=['transform', 'joint'])
        
        if self._struct['TPL']['walk']:
            if various.renameObject(self._struct['TPL']['walk'], prefix=arParam.TPL_NAME)==False:
                self.check = False
        else:
            self.check=False
        
    @walkTPL.deleter
    def walkTPL(self):
        self._struct['TPL']['walk'] = None

    
    
    
    
    
    @property
    def pivotTPL(self):
        return self._struct['TPL']['pivot']
    
    @pivotTPL.setter
    def pivotTPL(self, objs):
        
        self._struct['TPL']['pivot'] = []
        
        if (isinstance(objs, list))==False:
            self.check=False
        else:
            
            for i in range(len(objs)):
                if (isinstance(objs[i], list))==False:
                    self.check=False
                else:
                    
                    self._struct['TPL']['pivot'].append([])
                    
                    if len(objs[i]) == 2:
                        for j in range(len(objs[i])):
                        
                            tmp = various.checkObj(objs[i][j], type=['transform', 'joint'])
                            
                            if tmp:
                                if j:
                                    prefix = arParam.TPL_NAME
                                else:
                                    prefix = arParam.TPL_NAME_PVT
                                
                                self._struct['TPL']['pivot'][i].append(tmp)
                                
                                # rename properly
                                if various.renameObject(self._struct['TPL']['pivot'][i][-1], prefix=prefix)==False:
                                    self.check = False
                            else:
                                self.check=False
 
        
    @pivotTPL.deleter
    def pivotTPL(self):
        self._struct['TPL']['pivot'] = None
    
    
    
    
    
    #           #
    #   BUILD   #
    #           #

    @arParam.completion()
    def build(self, hierarchy=None, framework=None):      
        
        
        # create shapes
        # main or position
        self._struct['RIG']['main'] = arShapeBiblio.circleSpike(name=self.mainTPL.name().replace(arParam.TPL_NAME, '').upper(), parent=hierarchy['SCALEOFFSET'], color=self.color)
        matrixConstrain.snapObject(self.mainTPL, self._struct['RIG']['main'], channel=[1,1,0,0])
        # resize shape
        if self.mainTPL.getShape():
            length = math.fabs(various.getAtoms(self.mainTPL.getShape())[0].getPosition(space='world')[0])
            arShape.scaleShape(self._struct['RIG']['main'].getShape(), [0,0,0], [length,0,0], axis=[0.8,0,0.8])
        # add into controls set
        framework['CONTROLS'][''] = [self._struct['RIG']['main']]

        
        
        # walk or offset
        self._struct['RIG']['walk'] = arShapeBiblio.fourArrows(name=self.walkTPL.name().replace(arParam.TPL_NAME, '').upper(), parent=self._struct['RIG']['main'], color=self.color)
        matrixConstrain.snapObject(self.walkTPL, self._struct['RIG']['walk'], channel=[1,1,0,0])
        # resize shape
        if self.walkTPL.getShape():
            length = math.fabs(various.getAtoms(self.walkTPL.getShape())[0].getPosition(space='world')[0])
            arShape.scaleShape(self._struct['RIG']['walk'].getShape(), [0,0,0], [length,0,0], axis=[0.8,0,0.8])
        # add into controls set
        framework['CONTROLS'][''].append(self._struct['RIG']['walk'])

        
        
        # pivots
        self._struct['RIG']['pivot'] = []
        for i in range(len(self.pivotTPL)):
            if i:
                father = self._struct['RIG']['pivot'][-1]
            else:
                father = self._struct['RIG']['walk']
            self._struct['RIG']['pivot'].append( arShapeBiblio.cubeCenter(name=self.pivotTPL[i][1].name().replace(arParam.TPL_NAME, '').upper(), parent=father, color=self.color) )
            matrixConstrain.snapObject(self.pivotTPL[i][0], self._struct['RIG']['pivot'][-1], channel=[1,1,0,0])
            xfm.__xfm__(self._struct['RIG']['pivot'][-1])
            arShape.positionShape(self._struct['RIG']['pivot'][-1].getShape(), self.pivotTPL[i][1])
            
        # add pivots into controls set
        framework['CONTROLS'][''].extend(self._struct['RIG']['pivot'])
        
        # create xform if need
        for ctrl in [self._struct['RIG']['main'], self._struct['RIG']['walk']]:
            # if position is not precisely at 0 0 0
            if ctrl.getMatrix(objectSpace=True)!=dt.Matrix():
                xfm.__xfm__(ctrl)
        
        # create pick walk
        arPickwalk.setPickWalk(hierarchy['SCALEOFFSET'], self._struct['RIG']['main'], self._struct['RIG']['walk'], self._struct['RIG']['pivot'], type='UD')
        
        # END
        return True
        


        

#exemple = root('position_TPL', 'walk_TPL', [['fly_PVT', 'fly_TPL']])
#exemple.build()
