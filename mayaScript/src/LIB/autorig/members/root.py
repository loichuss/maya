#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 06 dec 2011
#
#   root
#

import pymel.core as pmc
import pymel.core.datatypes as dt
import math

import common.vPrint as vp
import common.various as various
import constrain.matrixConstrain as matrixConstrain
import rig.xfm as xfm
import clean.clean as clean

import shapes.biblio as shapesBiblio
import shapes.shape as arShape
import tools.hierarchy as arHierarchy
import tools.pickwalk as arPickwalk
import attributs.attribut as arAttributs

reload(arHierarchy)


class root():
    def __init__(self, mainCtrl, walkCtrl, pivotCtrl, color=17):
    
    
        #                           #
        #   check input variables   #
        #                           #
        
        self.check=True
        
        mainCtrl = various.checkObj(mainCtrl, type=['transform', 'joint'])
        walkCtrl = various.checkObj(walkCtrl, type=['transform', 'joint'])
        
        if mainCtrl==None:
            self.check=False
        else:
            # rename properly
            if various.renameObject(mainCtrl, prefix='_TPL')==False:
                self.check = False
        
        if walkCtrl==None:
            self.check=False
        else:
            # rename properly
            if various.renameObject(walkCtrl, prefix='_TPL')==False:
                self.check = False
        
             
        # pivotCtrl
        if (isinstance(pivotCtrl, list))==False:
            self.check=False
        else:
            
            for i in range(len(pivotCtrl)):
                if (isinstance(pivotCtrl[i], list))==False:
                    self.check=False
                else:
                    if len(pivotCtrl[i]) == 2:
                        for j in range(len(pivotCtrl[i])):
                        
                            pivotCtrl[i][j] = various.checkObj(pivotCtrl[i][j], type=['transform', 'joint'])
                            
                            if pivotCtrl[i][j]:
                                if j:
                                    prefix = '_TPL'
                                else:
                                    prefix = '_PVT'
                                # rename properly
                                if various.renameObject(pivotCtrl[i][j], prefix=prefix)==False:
                                    self.check = False
                            else:
                                self.check=False  
        
        
        # self variable
        if self.check:
            self.mainTPL   = mainCtrl 
            self.walkTPL   = walkCtrl
            self.pivotTPL  = pivotCtrl
            self.color     = color
        else:
            vp.vPrint('building root will failed', 1)
    
    
    def build(self):
        if self.check:
            
            # create hierarchy
            hierarchy = arHierarchy.createHierarchy()
            
            
            # create shapes
            # main or position
            self.mainCtrl = shapesBiblio.circleSpike(name=self.mainTPL.name().replace('_TPL', '').upper(), parent=hierarchy['SCALEOFFSET'], color=self.color)
            matrixConstrain.snapObject(self.mainTPL, self.mainCtrl, channel=[1,1,0,0])
            # resize shape
            if self.mainTPL.getShape():
                length = math.fabs(various.getAtoms(self.mainTPL.getShape())[0].getPosition(space='world')[0])
                arShape.scaleShape(self.mainCtrl.getShape(), [0,0,0], [length,0,0], axis=[0.8,0,0.8])
            # add into controls set
            pmc.sets(hierarchy['CONTROLS'], addElement=self.mainCtrl)
            
            
            # walk or offset
            self.walkCtrl = shapesBiblio.fourArrows(name=self.walkTPL.name().replace('_TPL', '').upper(), parent=self.mainCtrl, color=self.color)
            matrixConstrain.snapObject(self.walkTPL, self.walkCtrl, channel=[1,1,0,0])
            # resize shape
            if self.walkTPL.getShape():
                length = math.fabs(various.getAtoms(self.walkTPL.getShape())[0].getPosition(space='world')[0])
                arShape.scaleShape(self.walkCtrl.getShape(), [0,0,0], [length,0,0], axis=[0.8,0,0.8])
            # add into controls set
            pmc.sets(hierarchy['CONTROLS'], addElement=self.walkCtrl)
            
            
            # pivots
            self.pivotCtrl = []
            for i in range(len(self.pivotTPL)):
                if i:
                    father = self.pivotCtrl[-1]
                else:
                    father = self.walkCtrl
                self.pivotCtrl.append( shapesBiblio.cubeCenter(name=self.pivotTPL[i][1].name().replace('_TPL', '').upper(), parent=father, color=self.color) )
                matrixConstrain.snapObject(self.pivotTPL[i][0], self.pivotCtrl[-1], channel=[1,1,0,0])
                xfm.__xfm__(self.pivotCtrl[-1])
                arShape.positionShape(self.pivotCtrl[-1].getShape(), self.pivotTPL[i][1])
                
                # add into controls set
                pmc.sets(hierarchy['CONTROLS'], addElement=self.pivotCtrl[-1])
            
            
            # create xform if need
            for ctrl in [self.mainCtrl, self.walkCtrl]:
                # if position is not precisely at 0 0 0
                if ctrl.getMatrix(objectSpace=True)!=dt.Matrix():
                    xfm.__xfm__(ctrl)
            
            # create pick walk
            arPickwalk.setPickWalk(hierarchy['SCALEOFFSET'], self.mainCtrl, self.walkCtrl, self.pivotCtrl, type='UD')
            
            # deselect
            pmc.select(clear=True)
        
        
        else:
            vp.vPrint('missing or wrong data in module. Root not build', 1)

        
"""
toto = root('position_TPL', 'walk_TPL', [['fly_PVT', 'fly_TPL']])

toto.build()
"""