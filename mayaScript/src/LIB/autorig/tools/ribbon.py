#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 17 nov 2011
#
#   Ribbon
#

import pymel.core as pmc
import clean.clean as clean
import shapes.biblio as shapesBiblio
import rig.xfm as xfm
import bones.bone as bn
import tools.pickwalk as arPickwalk
import rig.bone

class createRibbon():

    def __init__(self, name, **kwargs):
        # check kwargs
        if ('type' in kwargs.keys())==False:
            kwargs['type'] = 'spline'
        if ('nbItem' in kwargs.keys())==False:
            kwargs['nbItem'] = 4
        if ('length' in kwargs.keys())==False:
            kwargs['length'] = 6.0
        if ('ctrlName' in kwargs.keys())==False:
            kwargs['ctrlName'] = ['start', 'off', 'end']
        if ('parent' in kwargs.keys())==False:
            kwargs['parent'] = None
        if ('colorOne' in kwargs.keys())==False:
            kwargs['colorOne'] = 17
        if ('colorTwo' in kwargs.keys())==False:
            kwargs['colorTwo'] = 21
        
        # variables
        self.name      = name
        self.type      = kwargs['type']
        self.nbItem    = kwargs['nbItem']
        self.length    = kwargs['length']
        self.ctrlName  = kwargs['ctrlName']
        self.parent    = kwargs['parent']
        self.colorOne  = kwargs['colorOne']
        self.colorTwo  = kwargs['colorTwo']
        
    
    
    
    #              #
    #   creation   #
    #              #
    
    def build(self):
        # create main group
        self.grp = pmc.createNode('transform', name=self.name+'_grp', skipSelect=True)
        if self.parent:
            self.grp.setParent(self.parent)
        clean.__lockHideTransform__(self.grp, channel=['t', 'r', 's', 'v'])
        
        
        # call def according to type
        if self.type == 'nurbs':
            return self.__createNurbs__()
        elif self.type == 'spline':
            return self.__createSpline__()
    
    
    
    
    
    
    #            #
    #   SPLINE   #
    #            #
    
    def __createSpline__(self):
        # create groups
        self.strucGrp  = pmc.createNode('transform', name=self.name+'_struc',   parent=self.grp, skipSelect=True)
        self.crvGrp    = pmc.createNode('transform', name=self.name+'_crv_NXF', parent=self.grp, skipSelect=True)
        self.aimGrp    = pmc.createNode('transform', name=self.name+'_aim',     parent=self.grp, skipSelect=True)
        self.aimSubGrp = pmc.createNode('transform', name=self.name+'_cst',  parent=self.aimGrp, skipSelect=True)
        self.subGrp    = pmc.createNode('transform', name=self.name+'_sub_NXF', parent=self.grp, skipSelect=True)
        
        self.crvGrp.inheritsTransform.set(False)
        self.subGrp.inheritsTransform.set(False)
        
        
        # create spline curve
        points = []
        ite    = self.length / 3.0
        for i in range(4):
            points.append( (i*ite,0,0) )
        crv = pmc.curve(name=self.name+'_crv', degree=3, point=points)
        crv.setParent(self.crvGrp)
        
                
        # place path locator
        perCent = 1.0/(self.nbItem-1)
        pathLoc = []
        for i in range(1, self.nbItem-1):
            # create path and connect it into the spline
            mpt = pmc.createNode('motionPath', name=self.name+str(i)+'_mpt')
            crv.worldSpace[0] >> mpt.geometryPath
            mpt.uValue.set(perCent*i)
            
            # create locator
            pathLoc.append( pmc.createNode('transform', name=self.name+'_pth'+str(i)+'_loc', parent=self.crvGrp) )
            pmc.createNode('locator', name=self.name+'_pth'+str(i)+'_locShape', parent=pathLoc[-1])
            mpt.allCoordinates >> pathLoc[-1].translate
        
        
        
        # create structure
        self.strucCtrl = {}
        for i in range(len(self.ctrlName)):
            strucTmp = []
            if i == 1:
                # ctrl
                strucTmp.append( rig.bone.__transformToBone__(shapesBiblio.circleX(name=self.name+'_'+self.ctrlName[i], parent=self.strucGrp, color=self.colorOne)) )
                strucTmp[-1].radius.set(0.0)
                clean.__lockHideTransform__(strucTmp[-1], channel=['v', 'radi', 's'])  
                              
                # pos
                strucTmp.append( xfm.__xfm__(strucTmp[0], suffix='_pos', lock=False) )
            else:
                # ctrl
                strucTmp.append( rig.bone.__transformToBone__(shapesBiblio.circleX(name=self.name+'_'+self.ctrlName[i], parent=self.strucGrp, color=self.colorOne)) )
                strucTmp[-1].radius.set(0.0)
                clean.__lockHideTransform__(strucTmp[-1], channel=['v', 'radi'])
                
                
                # scale
                strucTmp.append( pmc.createNode('transform', name=self.name+'_'+self.ctrlName[i]+'_scl',    parent=strucTmp[-1],  skipSelect=True) )
                strucTmp.append( pmc.createNode('transform', name=self.name+'_'+self.ctrlName[i]+'_locScl', parent=strucTmp[-1],  skipSelect=True) )
                
                # local scale connection
                strucTmp[0].scale >> strucTmp[-1].scale
                
            # put data into dico
            self.strucCtrl[self.ctrlName[i]] = strucTmp
        
        # move the end ctrl properly
        self.strucCtrl[self.ctrlName[2]][0].setTranslation([self.length,0,0], space='world')
        
        # pickwalk
        arPickwalk.setPickWalk([self.strucCtrl[self.ctrlName[0]][0], self.strucCtrl[self.ctrlName[1]][0], self.strucCtrl[self.ctrlName[2]][0]], type='UD')
        
        # create constrain group
        self.strucCtrlGrp = []
        self.strucCtrlGrp.append( xfm.__xfm__(self.strucCtrl[self.ctrlName[0]][0], suffix='_cst_grp', lock=False) )
        self.strucCtrlGrp.append( xfm.__xfm__(self.strucCtrl[self.ctrlName[1]][0], suffix='_cst_grp', lock=False) )
        self.strucCtrlGrp.append( xfm.__xfm__(self.strucCtrl[self.ctrlName[2]][0], suffix='_cst_grp', lock=False) )
        
        # constrain between structure
        pmc.pointConstraint(self.strucCtrl[self.ctrlName[0]][0], self.strucCtrl[self.ctrlName[2]][0], self.strucCtrl[self.ctrlName[1]][1], name=self.strucCtrl[self.ctrlName[1]][1]+'_ptCst', maintainOffset=False )
        #pmc.aimConstraint(self.strucCtrl[self.ctrlName[2]][0], self.strucCtrl[self.ctrlName[1]][1], name=self.strucCtrl[self.ctrlName[1]][1].name()+'_aimCst', maintainOffset=False, worldUpType='objectrotation', worldUpObject=self.strucGrp, worldUpVector=[0,1,0], aimVector=[1,0,0],  upVector=[0,1,0])
        
        
        
        # skinning curve spline
        skinNode = pmc.skinCluster( self.strucCtrl[self.ctrlName[0]][0], self.strucCtrl[self.ctrlName[1]][0], self.strucCtrl[self.ctrlName[2]][0], crv, name=crv.name()+'_skn', ignoreSelected=0, maximumInfluences=3, dropoffRate=12.0, normalizeWeights=1)
        weights = []
        weights.extend([1, 0, 0])
        weights.extend([0, 1, 0])
        weights.extend([0, 1, 0])
        weights.extend([0, 0, 1])
        
        # set weights
        skinNode[0].setWeights(crv, [0,1,2], weights, normalize=True)
        
        # delete useless bindpose
        bindPose = self.strucCtrl[self.ctrlName[0]][0].bindPose.outputs()[0]
        pmc.delete(bindPose)
        
        
        
        # create joint aim with Ik system
        # constrain between the start ctrl and the group
        pmc.parentConstraint(self.strucCtrl[self.ctrlName[0]][0], self.aimGrp, name=self.aimGrp.name()+'_paCst', maintainOffset=False)
        pmc.aimConstraint(self.strucCtrl[self.ctrlName[2]][0], self.aimSubGrp, name=self.aimSubGrp.name()+'_aimCst', maintainOffset=False, worldUpType='objectrotation', worldUpObject=self.strucCtrl[self.ctrlName[0]][0], worldUpVector=[0,1,0], aimVector=[1,0,0],  upVector=[0,1,0])
        
        # create two joints for the ik
        jntStart = pmc.createNode('joint', name=self.name+'_base_RIGjnt', parent=self.aimSubGrp)
        jntEnd   = pmc.createNode('joint', name=self.name+'_tip_RIGjnt',  parent=jntStart)
        jntEnd.setTranslation([self.length/5.0,0,0], space='world')
        
        # create ik
        ikHand = pmc.ikHandle( name=jntStart.name()+'ikHand' ,startJoint=jntStart, endEffector=jntEnd, priority=1, weight=1.0, solver='ikSCsolver', snapHandleFlagToggle=False )
        ikHand[1].rename(jntEnd.name()+'ikEff')
        
        # parent the ik into the last ctrl
        ikHand[0].setParent(self.strucCtrl[self.ctrlName[2]][0])
        ikHand[0].setTranslation([0,0,0], space='object')
        # hide
        ikHand[0].visibility.set(False)
        clean.__lockHideTransform__(ikHand[0], channelBox=True)
        
        
        # system wich distribute the right X rotation into locator
        twistLoc = []
        for i in range(len(pathLoc)):
            twistLoc.append( pmc.createNode('transform', name=self.name+'_twist'+str(i), parent=self.strucCtrl[self.ctrlName[0]][0], skipSelect=True) )
            twistLocGrp = xfm.__xfm__(twistLoc[i], lock=False)
            
            # constrain the twist locator to the path locator
            pmc.pointConstraint(pathLoc[i], twistLocGrp, name=twistLocGrp.name()+'_ptCst', maintainOffset=False)
            
            # multiply
            mult = pmc.createNode('multDoubleLinear', name=twistLoc[i].name()+'_mlt')
            
            jntStart.rotateX >> mult.input1
            mult.input2.set(perCent*(i+1))
            mult.output >> twistLoc[i].rotateX
        
        
        # creating sub ctrl system
        self.subCtrlGrp = []
        self.subCtrl    = []
        self.bones2SK   = []
        
        for i in range(self.nbItem):
            # create ctrl
            self.subCtrl.append( shapesBiblio.rhombusX(name=self.name+'_sub'+str(i+1), color=self.colorTwo) )
            self.subCtrlGrp.append( xfm.__xfm__(self.subCtrl[i], suffix='_grp', lock=False) )
            self.subCtrlGrp[i].setParent(self.subGrp)
            # add attributs
            pmc.addAttr(self.subCtrl[i], longName='posU', attributeType='float', defaultValue=((1.0/(self.nbItem-1.0))*i) )
            pmc.addAttr(self.subCtrl[i], longName='negU', attributeType='float', defaultValue=1-((1.0/(self.nbItem-1.0))*i) )
            # bones
            self.bones2SK.append( bn.create2SK(self.name+'_sub'+str(i+1), self.subCtrl[i]) )
            
            
        # pickwalk
        arPickwalk.setPickWalk(self.subCtrl, type='UD')
        arPickwalk.setPickWalk([self.strucCtrl[self.ctrlName[0]][0], self.subCtrl[0]], type='LR')
        arPickwalk.setPickWalk([self.strucCtrl[self.ctrlName[2]][0], self.subCtrl[-1]], type='LR')
        
        # constrains for first
        pmc.pointConstraint(self.strucCtrl[self.ctrlName[0]][0], self.subCtrlGrp[0], name=self.subCtrlGrp[0].name()+'_ptCst', maintainOffset=False)
        pmc.aimConstraint(self.subCtrl[1], self.subCtrlGrp[0], name=self.subCtrlGrp[0].name()+'_aimCst', maintainOffset=False, worldUpType='objectrotation', worldUpObject=self.strucCtrl[self.ctrlName[0]][0], worldUpVector=[0,1,0], aimVector=[1,0,0],  upVector=[0,1,0])
        # constrains for last
        pmc.pointConstraint(self.strucCtrl[self.ctrlName[2]][0], self.subCtrlGrp[-1], name=self.subCtrlGrp[-1].name()+'_ptCst', maintainOffset=False)
        pmc.aimConstraint(self.subCtrl[-2], self.subCtrlGrp[-1], name=self.subCtrlGrp[-1].name()+'_aimCst', maintainOffset=False, worldUpType='objectrotation', worldUpObject=self.strucCtrl[self.ctrlName[2]][0], worldUpVector=[0,1,0], aimVector=[-1,0,0],  upVector=[0,1,0])
        
        # constrains for others
        for i in range(1, self.nbItem-1):
            pmc.pointConstraint(twistLoc[i-1], self.subCtrlGrp[i], name=self.subCtrlGrp[i].name()+'_ptCst', maintainOffset=False)
            
            if i < self.nbItem/2:
                aimVec=[1,0,0]
            else:
                aimVec=[-1,0,0]
            pmc.aimConstraint(self.strucCtrl[self.ctrlName[1]][0], self.subCtrlGrp[i], name=self.subCtrlGrp[i].name()+'_aimCst', maintainOffset=False, worldUpType='objectrotation', worldUpObject=twistLoc[i-1], worldUpVector=[0,1,0], aimVector=aimVec,  upVector=[0,1,0])
        
        
        
        # connect scale from controlors to sub
        decoMatS = pmc.createNode('decomposeMatrix', name=self.strucCtrl[self.ctrlName[0]][0]+'_decoMat', skipSelect=True)
        decoMatE = pmc.createNode('decomposeMatrix', name=self.strucCtrl[self.ctrlName[2]][0]+'_decoMat', skipSelect=True)
        
        self.strucCtrl[self.ctrlName[0]][2].worldMatrix[0] >> decoMatS.inputMatrix
        self.strucCtrl[self.ctrlName[2]][2].worldMatrix[0] >> decoMatE.inputMatrix
        
        
        # connect scale to sub control
        for i in range(1, self.nbItem-1):
            # create blend to progressively pass from the start to the end scale
            bld = pmc.createNode('blendColors', name=self.subCtrl[i].name()+str(i)+'_bld')
            decoMatS.outputScale >> bld.color1
            decoMatE.outputScale >> bld.color2
            # connect the sub control attribut neg U
            self.subCtrl[i].negU >> bld.blender
            # connect into the scale
            bld.output >> self.subCtrlGrp[i].scale
        # no point to create a blend node for the first and the last sub control
        decoMatS.outputScale >> self.subCtrlGrp[0].scale
        decoMatE.outputScale >> self.subCtrlGrp[-1].scale
        
        
        # unselect
        pmc.select(clear=True)
        
        
        # return, in order
        #   0 the main group PyNode
        #   1 the main structure group this last can receive constrain to place the ribbon PyNode
        #   2 groups of each structure controls in order (start offset end) PyNode List
        #   3 structure controls in order (start offset end) PyNode List)
        #   4 groups wich can receive a scale information in order (start end) PyNode List
        #   5 position groups which give the default position in order (offset) PyNode
        #   6 groups of sub controls PyNode List
        #   7 sub controls PyNode List
        #   8 2SKjnt PyNode List
        return [self.grp, self.strucGrp, self.strucCtrlGrp, [self.strucCtrl[self.ctrlName[0]][0], self.strucCtrl[self.ctrlName[1]][0], self.strucCtrl[self.ctrlName[2]][0]], [self.strucCtrl[self.ctrlName[0]][1], self.strucCtrl[self.ctrlName[2]][1]], self.strucCtrl[self.ctrlName[1]][1], self.subCtrlGrp, self.subCtrl, self.bones2SK]
        
    
        
        
        
        
        
    #           #
    #   NURBS   #
    #           #
    
    def __createNurbs__(self):
        # check if plugin decompose matrix is present
        pmc.loadPlugin('decomposeMatrix', quiet=True)
        
        # create groups
        folGrp        = pmc.createNode('transform', name=self.name+'_fol_NXF',   parent=self.grp, skipSelect=True)
        self.strucGrp = pmc.createNode('transform', name=self.name+'_struc_NXF', parent=self.grp, skipSelect=True)
        folGrp.inheritsTransform.set(0)
        self.strucGrp.inheritsTransform.set(0)
        
        # create plane
        plan = pmc.nurbsPlane(name=self.name+'_plane', axis=[0,1,0], width=self.length, lengthRatio=(1.0/self.length)/2.0, degree=3, patchesU=4, patchesV=1, constructionHistory=0, pivot=[self.length/2.0,0,0])[0]
        plan.inheritsTransform.set(0)
        plan.setParent(folGrp)
        pmc.rebuildSurface( plan, constructionHistory=False, replaceOriginal=True, rebuildType=0, endKnots=1, keepRange=0, keepControlPoints=0, keepCorners=0, spansV=1, degreeV=1, fitRebuild=0,  direction=1 )
        
        # create follicle + control + bones
        self.subCtrlGrp = []
        self.subCtrl    = []
        self.bones2SK   = []
        
        for i in range(self.nbItem):
            fol      = pmc.createNode('transform', name=self.name+'_fol'+str(i+1),         parent=folGrp, skipSelect=True)
            folShape = pmc.createNode('follicle',  name=self.name+'_fol'+str(i+1)+'Shape', parent=fol,    skipSelect=True)
            # connections
            plan.worldMatrix[0] >> folShape.inputWorldMatrix
            plan.local >> folShape.inputSurface
            folShape.outRotate >> fol.rotate
            folShape.outTranslate >> fol.translate
            # u and v setting
            folShape.parameterV.set(0.5)
            folShape.parameterU.set((1.0/(self.nbItem-1.0))*i)
            folShape.visibility.set(False)
            clean.__lockHideTransform__(fol, channel=['t', 'r', 's', 'v'])
            
            # sub control
            self.subCtrlGrp.append( pmc.createNode('transform', name=self.name+'_sub'+str(i+1)+'_grp') )
            self.subCtrl.append( shapesBiblio.rhombusX(name=self.name+'_sub'+str(i+1), color=self.colorTwo) )
            # add attributs
            pmc.addAttr(self.subCtrl[i], longName='posU', attributeType='float', defaultValue=((1.0/(self.nbItem-1.0))*i) )
            pmc.addAttr(self.subCtrl[i], longName='negU', attributeType='float', defaultValue=1-((1.0/(self.nbItem-1.0))*i) )
            
            self.subCtrl[-1].setParent(self.subCtrlGrp[-1])
            self.subCtrlGrp[-1].setParent(fol)
            self.subCtrlGrp[-1].setTranslation([0,0,0], space='object')
            xfm.__xfm__(self.subCtrlGrp[-1])
            
            # bones
            self.bones2SK.append( bn.create2SK(self.name+'_sub'+str(i+1), self.subCtrl[-1]) )
        
        
        # pickwalk
        arPickwalk.setPickWalk(self.subCtrl, type='UD')
        
        # create structure
        strucJnt       = []
        self.strucCtrl = {}
        for i in range(len(self.ctrlName)):
            strucTmp = []
            if i == 1:
                # ctrl
                strucTmp.append( shapesBiblio.circleX(name=self.name+'_'+self.ctrlName[i], parent=self.strucGrp, color=self.colorOne) )
                clean.__lockHideTransform__(strucTmp[-1], channel=['s'])
                strucJnt.append( pmc.createNode('joint', name=self.name+'_'+self.ctrlName[i]+'_RIGjnt', parent=strucTmp[-1], skipSelect=True) )
                
                # aim
                strucTmp.append( pmc.createNode('transform', name=self.name+'_'+self.ctrlName[i]+'_pos', parent=self.strucGrp, skipSelect=True) )
                
                # rot 
                strucTmp.append( pmc.createNode('transform', name=self.name+'_'+self.ctrlName[i]+'_aim', parent=strucTmp[-1], skipSelect=True) )
                strucTmp[0].setParent(strucTmp[-1])
                
                # up
                strucTmp.append( pmc.createNode('transform', name=self.name+'_'+self.ctrlName[i]+'_up',  parent=strucTmp[-2], skipSelect=True) )
                strucTmp[-1].setTranslation([0,self.length/2.0,0], space='world')
                
            else:
                # ctrl
                strucTmp.append( shapesBiblio.circleX(name=self.name+'_'+self.ctrlName[i], parent=self.strucGrp, color=self.colorOne) )
                clean.lockHideTransform(strucTmp[-1], channel=['rotateOrder'])
                
                # aim
                strucTmp.append( pmc.createNode('transform', name=self.name+'_'+self.ctrlName[i]+'_aim', parent=strucTmp[-1], skipSelect=True) )
                strucJnt.append( pmc.createNode('joint', name=self.name+'_'+self.ctrlName[i]+'_RIGjnt', parent=strucTmp[-1], skipSelect=True) )
                
                # scale
                strucTmp.append( pmc.createNode('transform', name=self.name+'_'+self.ctrlName[i]+'_scl',    parent=strucTmp[-1],  skipSelect=True) )
                strucTmp.append( pmc.createNode('transform', name=self.name+'_'+self.ctrlName[i]+'_locScl', parent=strucTmp[-1], skipSelect=True) )
                
                # local scale connection
                strucTmp[0].scale >> strucTmp[-1].scale
                
                # up
                strucTmp.append( pmc.createNode('transform', name=self.name+'_'+self.ctrlName[i]+'_up',  parent=strucTmp[-4], skipSelect=True) )
                strucTmp[-1].setTranslation([0,self.length/2.0,0], space='world')
            
            # put info into dico
            self.strucCtrl[self.ctrlName[i]] = strucTmp
        
        # place structure end
        self.strucCtrl[self.ctrlName[2]][0].setTranslation([self.length,0,0], space='world')
        
        # pickwalk
        arPickwalk.setPickWalk([self.strucCtrl[self.ctrlName[0]][0], self.strucCtrl[self.ctrlName[1]][0], self.strucCtrl[self.ctrlName[2]][0]], type='UD')
        arPickwalk.setPickWalk([self.strucCtrl[self.ctrlName[0]][0], self.subCtrl[0]], type='LR')
        arPickwalk.setPickWalk([self.strucCtrl[self.ctrlName[2]][0], self.subCtrl[-1]], type='LR')
        
        # create constrain group
        self.strucCtrlGrp = []
        self.strucCtrlGrp.append( xfm.__xfm__(self.strucCtrl[self.ctrlName[0]][0], suffix='_cst_grp', lock=False) )
        self.strucCtrlGrp.append( xfm.__xfm__(self.strucCtrl[self.ctrlName[1]][0], suffix='_cst_grp', lock=False) )
        self.strucCtrlGrp.append( xfm.__xfm__(self.strucCtrl[self.ctrlName[2]][0], suffix='_cst_grp', lock=False) )
        
        
        # constrain between structure
        tmp = []
        tmp.append( pmc.pointConstraint(self.strucCtrl[self.ctrlName[0]][0], self.strucCtrl[self.ctrlName[2]][0], self.strucCtrl[self.ctrlName[1]][1], name=self.strucCtrl[self.ctrlName[1]][1]+'_ptCst', maintainOffset=False ) )
        tmp.append( pmc.pointConstraint(self.strucCtrl[self.ctrlName[0]][4], self.strucCtrl[self.ctrlName[2]][4], self.strucCtrl[self.ctrlName[1]][3], name=self.strucCtrl[self.ctrlName[1]][3]+'_ptCst', maintainOffset=False ) )
        tmp.append( pmc.aimConstraint(self.strucCtrl[self.ctrlName[2]][0], self.strucCtrl[self.ctrlName[0]][1], name=self.strucCtrl[self.ctrlName[0]][1]+'_aimCst', maintainOffset=False, worldUpType='object', worldUpObject=self.strucCtrl[self.ctrlName[0]][4], aimVector=[1,0,0],  upVector=[0,1,0]) )
        tmp.append( pmc.aimConstraint(self.strucCtrl[self.ctrlName[0]][0], self.strucCtrl[self.ctrlName[2]][1], name=self.strucCtrl[self.ctrlName[2]][1]+'_aimCst', maintainOffset=False, worldUpType='object', worldUpObject=self.strucCtrl[self.ctrlName[2]][4], aimVector=[-1,0,0], upVector=[0,1,0]) )
        tmp.append( pmc.aimConstraint(self.strucCtrl[self.ctrlName[2]][0], self.strucCtrl[self.ctrlName[1]][2], name=self.strucCtrl[self.ctrlName[1]][2]+'_aimCst', maintainOffset=False, worldUpType='object', worldUpObject=self.strucCtrl[self.ctrlName[1]][3], aimVector=[1,0,0],  upVector=[0,1,0]) )
        
        clean.lockHideTransform(tmp, channelBox=True)
        
        
        
        # skinning nurbs plane
        skinNode = pmc.skinCluster( strucJnt[0], strucJnt[1], strucJnt[2], plan, name=plan.name()+'_skn', ignoreSelected=0, maximumInfluences=3, dropoffRate=12.0, normalizeWeights=1)
        weights = []
        weights.extend([1, 0, 0])
        weights.extend([1, 0, 0])
        weights.extend([0.8, 0.2, 0])
        weights.extend([0.8, 0.2, 0])
        weights.extend([0.4, 0.6, 0])
        weights.extend([0.4, 0.6, 0])
        weights.extend([0, 1, 0])
        weights.extend([0, 1, 0])
        weights.extend([0, 0.6, 0.4])
        weights.extend([0, 0.6, 0.4])
        weights.extend([0, 0.2, 0.8])
        weights.extend([0, 0.2, 0.8])
        weights.extend([0, 0, 1])
        weights.extend([0, 0, 1])
        
        # set weights
        skinNode[0].setWeights(plan, [0,1,2], weights, normalize=True)
        
        # delete useless bindpose
        bindPose = strucJnt[0].bindPose.outputs()[0]
        pmc.delete(bindPose)
        
        
        # inverse scale for bones
        for i in range(len(self.ctrlName)):
            multMat = pmc.createNode('multMatrix',      name=self.strucCtrl[self.ctrlName[i]][0]+'_invScl_multMat', skipSelect=True)
            decoMat = pmc.createNode('decomposeMatrix', name=self.strucCtrl[self.ctrlName[i]][0]+'_invScl_decoMat', skipSelect=True)
            self.strucGrp.inverseMatrix >> multMat.matrixIn[0]
            self.strucCtrl[self.ctrlName[i]][0].worldMatrix[0] >> multMat.matrixIn[1]
            
            multMat.matrixSum >> decoMat.inputMatrix
            decoMat.outputScale >> strucJnt[i].inverseScale
        
        
        
        # connect scale from controlors to sub
        decoMatS = pmc.createNode('decomposeMatrix', name=self.strucCtrl[self.ctrlName[0]][0]+'_decoMat', skipSelect=True)
        decoMatE = pmc.createNode('decomposeMatrix', name=self.strucCtrl[self.ctrlName[2]][0]+'_decoMat', skipSelect=True)
        
        self.strucCtrl[self.ctrlName[0]][3].worldMatrix[0] >> decoMatS.inputMatrix
        self.strucCtrl[self.ctrlName[2]][3].worldMatrix[0] >> decoMatE.inputMatrix
         
        
        # connect scale to sub control
        for i in range(1, self.nbItem-1):
            # create blend to progressively pass from the start to the end scale
            bld = pmc.createNode('blendColors', name=self.subCtrl[i].name()+str(i)+'_bld')
            decoMatS.outputScale >> bld.color1
            decoMatE.outputScale >> bld.color2
            # connect the sub control attribut neg U
            self.subCtrl[i].negU >> bld.blender
            # connect into the scale
            bld.output >> self.subCtrlGrp[i].scale
        # no point to create a blend node for the first and the last sub control
        decoMatS.outputScale >> self.subCtrlGrp[0].scale
        decoMatE.outputScale >> self.subCtrlGrp[-1].scale
        
        
        
        # hide and lock channels
        plan.visibility.set(False)
        clean.__lockHideTransform__(plan,   channel=['t', 'r', 's', 'v'])
        clean.__lockHideTransform__(folGrp, channel=['t', 'r', 's', 'v'])
        
        for jnt in strucJnt:
            jnt.overrideEnabled.set(1)
            jnt.overrideColor.set(3)
            jnt.radius.set(0.5)
            jnt.visibility.set(False)
            clean.__lockHideTransform__(jnt, channel=['t', 'r', 's', 'v', 'radius'])
        
        
        
        # unselect
        pmc.select(clear=True)
        
        
        # return, in order
        #   0 the main group PyNode
        #   1 the main structure group this last can receive constrain to place the ribbon PyNode
        #   2 groups of each structure controls in order (start offset end) PyNode List
        #   3 structure controls in order (start offset end) PyNode List)
        #   4 groups wich can receive a scale information in order (start end) PyNode List
        #   5 position groups which give the default position in order (offset) PyNode
        #   6 groups of sub controls PyNode List
        #   7 sub controls PyNode List
        #   8 2SKjnt PyNode List
        return [self.grp, self.strucGrp, self.strucCtrlGrp, [self.strucCtrl[self.ctrlName[0]][0], self.strucCtrl[self.ctrlName[1]][0], self.strucCtrl[self.ctrlName[2]][0]], [self.strucCtrl[self.ctrlName[0]][2], self.strucCtrl[self.ctrlName[2]][2]], self.strucCtrl[self.ctrlName[1]][1], self.subCtrlGrp, self.subCtrl, self.bones2SK]
        
    
    
    
    
    #           #
    #   clean   #
    #           #
    
    def clean(self):
        # call def according to type
        if self.type == 'nurbs':
            return self.__cleanNurbs__()
        elif self.type == 'spline':
            return self.__cleanSpline__()
    
    def __cleanSpline__(self):
        # hide groups
        self.aimGrp.visibility.set(False)
        self.crvGrp.visibility.set(False)
        
        # clean groups
        clean.__lockHideTransform__(self.strucGrp, channel=['t', 'r', 's', 'v'])
        clean.__lockHideTransform__(self.crvGrp, channel=['t', 'r', 's', 'v'])
        clean.__lockHideTransform__(self.aimGrp, channel=['t', 'r', 's', 'v'])
        clean.__lockHideTransform__(self.aimSubGrp, channel=['t', 'r', 's', 'v'])
        clean.__lockHideTransform__(self.subGrp, channel=['t', 'r', 's', 'v'])
    
    
    
    
    def __cleanNurbs__(self):
        # clean group structure
        clean.__lockHideTransform__(self.strucGrp, channel=['t', 'r', 's', 'v'])
        
        # clean sub control group
        clean.lockHideTransform(self.subCtrlGrp, channel=['t', 'r', 's', 'v'])
        
        # clean structure
        clean.lockHideTransform(self.strucCtrlGrp, channel=['t', 'r', 's', 'v'])
        
        for i in range(len(self.ctrlName)):
            for j in range(1, len(self.strucCtrl[self.ctrlName[i]])):
                clean.__lockHideTransform__(self.strucCtrl[self.ctrlName[i]][j], channel=['t', 'r', 's', 'v'])
       


