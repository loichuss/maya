#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 14 dec 2011
#
#   Spine
#

import pymel.core as pmc
import pymel.core.datatypes as dt
import math

import common.vPrint as vp
import common.various as various
import clean.clean as clean
import constrain.matrixConstrain as matrixConstrain
import rig.bone
import rig.matrix
import rig.xfm as xfm
import rig.vector as vector

import bones.bone as bn
import tools.hierarchy as arHierarchy
import shapes.biblio as shapesBiblio
import shapes.shape as arShape
import tools.pickwalk as arPickwalk

reload(shapesBiblio)

class spine():
    
    def __init__(self, name, bones, parent=None, autoHierarchy=False, upVect=dt.Vector(0,1,0), upObj=None, colorOne=17, colorTwo=21):



        #                           #
        #   check input variables   #
        #                           #
        
        self.check = True
        
        
        # bones
        if (isinstance(bones, list))==False:
            bones = [bones]
        for i in range(len(bones)):
            # check object
            bones[i] = various.checkObj(bones[i], type=['joint'])
            if bones[i]==None:
                self.check = False
        
        
        # up vector
        if upObj == None:
            if (isinstance(bones, dt.Vector))==False:
                try :
                    upVect = dt.Vector(upVect)
                except:
                    vp.vPrint('%s is not a vector' % upVect, 1)
                    self.check = False
        
        # up object
        if upObj:
            upObj = various.checkObj(upObj, type=['joint'])
            if upObj==None:
                self.check = False
                      
        
        # parent object if given
        if parent:
            parent = various.checkObj(parent, type=['transform', 'joint'])
            if parent==None:
                self.check = False
        
        
        # create automatic hierarchy if desire
        if self.check:
            if autoHierarchy:
                i = 0
                bones = [bones[0]]
                while len(bones[i].getChildren()):
                    bones.append( bones[i].getChildren()[0] )
                    i += 1
                if len(bones[0].getChildren()) > 1:
                    upObj = bones[0].getChildren()[1]
        
        
        if upObj:
           # create vector according to object up
            upVect = (upObj.getTranslation(space='world') - bones[0].getTranslation(space='world'))
            upVect.normalize() 
            # rename properly
            if various.renameObject(upObj, prefix='_TPLjnt')==False:
                self.check = False
        
        # rename template if badly done
        if self.check:
            for i in range(len(bones)):
                # rename properly
                if various.renameObject(bones[i], prefix='_TPLjnt')==False:
                    self.check = False
        
        
        # checking the number of spine joint (minimum 3 including the tip)
        if len(bones)<3:
            self.check=False
            vp.vPrint('spine module need at least 3 joints', 1)

        # keep variable
        if self.check:
            # self part       
            self.bonesTPL = bones
            self.name     = name
            self.parent   = parent
            self.upVect   = upVect
            self.colorOne = colorOne
            self.colorTwo = colorTwo
            
            
        else:
            vp.vPrint('building %s will failed' % name, 1)




    def build(self):
        """build Spine"""
        
        if self.check:
        
            # list for each 2SK bones
            self.bones2SK = []
            
            # create hierarchy group
            self.hierarchy = arHierarchy.createHierarchy()
            
            # variable
            self.gp = {}
            
            # create flat vector
            self.upVectFlat  = vector.flat(self.upVect)
            self.dirVectFlat = vector.flat(self.bonesTPL[1].getTranslation(space='world') - self.bonesTPL[0].getTranslation(space='world'))
            
            
            # create group
            self.gp['main'] = pmc.createNode('transform', name=self.name+'MainRig_grp')
            if self.parent:
                self.gp['main'].setParent(self.parent)
            else:
                self.gp['main'].setParent(hierarchy['SCALEOFFSET'])
            
            
            self.gp['scale']  = pmc.createNode('transform', name=self.name+'Scale_grp', parent=self.gp['main'])
            self.gp['nxf']    = pmc.createNode('transform', name=self.name+'NFX_grp', parent=self.gp['main'])
            self.gp['ctrl']   = pmc.createNode('transform', name=self.name+'Ctrl_grp', parent=self.gp['scale'])
            self.gp['skelFk'] = pmc.createNode('transform', name=self.name+'SkelFk_grp', parent=self.gp['scale'])
            self.gp['skelIk'] = pmc.createNode('transform', name=self.name+'SkelIk_grp', parent=self.gp['scale'])
            
            
            self.gp['nxf'].inheritsTransform.set(False)
            
            # lock attribut from group
            clean.__lockHideTransform__(self.gp['main'], channel=['t', 'r', 's'])
            
            # create set
            pmc.select(clear=True)
            self.mainSets = pmc.sets(name=self.name+'_ctrls')
            self.ikSets   = pmc.sets(name=self.name+'_ik_ctrls')
            self.fkSets   = pmc.sets(name=self.name+'_fk_ctrls')
            self.subSets  = pmc.sets(name=self.name+'_sub_ctrls')
            pmc.sets(self.hierarchy['CONTROLS'], addElement=self.mainSets)
            pmc.sets(self.mainSets, addElement=self.ikSets)
            pmc.sets(self.mainSets, addElement=self.fkSets)
            pmc.sets(self.mainSets, addElement=self.subSets)
            
            # call definition
            base = self.__base__()
            fk = self.__fk__()
            ik = self.__ik__()
            
            # sets
            for key in base.keys():
                pmc.sets(key, addElement=base[key])
            for key in fk.keys():
                pmc.sets(key, addElement=fk[key])
            for key in ik.keys():
                pmc.sets(key, addElement=ik[key])
        
        
            # connect 2SK jnt together
            bn.__connect2SK__(self.bones2SK)
        
        
        
        
    #               #
    #   BASE PART   #
    #               #
    
    def __base__(self):
        
        # create main control for spine
        self.baseCtrl = shapesBiblio.donutX(name=self.name+'Base', parent=self.gp['ctrl'], color=self.colorOne )
        
        # place this last
        self.baseCtrl.setTransformation ( rig.matrix.vecToMat( dir=self.dirVectFlat, up=self.upVectFlat, pos=self.bonesTPL[0].getTranslation(space='world'), order='xyz' ) )
        xfm.__xfm__(self.baseCtrl)
        
        # scale shape
        arShape.scaleShape(self.baseCtrl.getShape(), self.bonesTPL[0], self.bonesTPL[2], axis=[1,1,1])
        
        # constrain groups into base
        matrixConstrain.matrixConstrain(self.baseCtrl, self.gp['skelFk'], channel=[1,1,0,0])
        
        # pickwalk
        arPickwalk.setPickWalk([self.baseCtrl], type='UD')
        
        
        return {self.mainSets:self.baseCtrl}
    
    
    #                  #
    #   BONES CREATE   #
    #                  #
    
    def __createBones__(self, prefix, addShapes, addXfm, father):
        
        # create bones
        jnts = []
        for i in range(len(self.bonesTPL)-1):
            # create joint
            jnts.append( pmc.createNode('joint', name=self.bonesTPL[i].replace('_TPLjnt', prefix) ) )
            jnts[i].setTransformation ( rig.matrix.vecToMat( dir=(self.bonesTPL[i+1].getTranslation(space='world') - self.bonesTPL[i].getTranslation(space='world')), up=self.upVect, pos=self.bonesTPL[i].getTranslation(space='world'), order='xyz' ) )
            rig.bone.__rotateToOrient__(jnts[i])
            # set parent 
            if i:
                jnts[i].setParent( jnts[i-1] )
            else:
                jnts[i].setParent( father )
            
            if addShapes:
                # add shape to joint
                tmp = shapesBiblio.cube(name=jnts[i], color=self.colorOne)
                
                pmc.parent(tmp.getShape(), jnts[i], shape=True, relative=True)
                pmc.delete(tmp)
                
                # scale shape
                arShape.scaleShape(jnts[i].getShape(), jnts[i], self.bonesTPL[i+1])
            
            # clean channel box
            jnts[i].rotateOrder.setKeyable(True)
            clean.__lockHideTransform__(jnts[i], channel=['v', 'radi'])
            
            if addXfm:
                # add xfm
                xfm.__xfm__(jnts[i])
        
        # create last bone
        jnts.append( pmc.createNode('joint', name=self.bonesTPL[-1].replace('_TPLjnt', prefix) ) )
        jnts[-1].setTransformation ( rig.matrix.vecToMat( dir=(self.bonesTPL[-1].getTranslation(space='world') - self.bonesTPL[-2].getTranslation(space='world')), up=self.upVect, pos=self.bonesTPL[-1].getTranslation(space='world'), order='xyz' ) )
        rig.bone.__rotateToOrient__(jnts[-1])
        jnts[-1].setParent( jnts[-2] )

        return jnts
    
    
    
    
    #             #
    #   FK PART   #
    #             #
    
    def __fk__(self):
        
        # create bones
        self.jntsFk = self.__createBones__(prefix='', addShapes=True, addXfm=True, father=self.gp['skelFk'])
         
        
        
        # Fk curve part
        self.jntsFkLoc = []
        points = []
        # create group for locator
        self.gp['skelFkLoc'] = pmc.createNode('transform', name=self.name+'_loc_grp', parent=self.gp['skelFk'])
        self.gp['skelFkLoc'].visibility.set(False)
        
        for i in range(len(self.jntsFk)):
            # create locator
            self.jntsFkLoc.append( pmc.createNode('transform', name=self.jntsFk[i].name()+'_loc', parent=self.gp['skelFkLoc']) )
            pmc.createNode('locator', name=self.jntsFk[i].name()+'_locShape', parent=self.jntsFkLoc[-1])
            
            # create constrain
            pmc.pointConstraint(self.jntsFk[i], self.jntsFkLoc[i], name=self.jntsFkLoc[i]+'_ptCst', maintainOffset=False)
            
            # add points
            points.append((i,i,i))
        
        # create curve
        self.curveFk = pmc.curve(name=self.name+'_crvFk', degree=3, point=points)
        self.curveFk.setParent(self.gp['nxf'])
        
        # connect world position of each locator into each control points
        for i in range(len(self.jntsFkLoc)):
            self.jntsFkLoc[i].getShape().worldPosition[0] >> self.curveFk.getShape().controlPoints[i]
        
        
        # pickwalk
        arPickwalk.setPickWalk(self.jntsFk[:-1], type='UD')
        
        
        return {self.fkSets:self.jntsFk[:-1]}
        
        

    #             #
    #   IK PART   #
    #             #
    
    def __ik__(self):
        
        #
        # create Ik curve from Fk curve
        #
        self.curveMid = pmc.duplicate(self.curveFk, name=self.name+'_crvMid')[0]
        self.curveIk  = pmc.duplicate(self.curveFk, name=self.name+'_crvIk')[0]
        
        
        
        
        #
        # create bones
        #
        self.jntsIk = self.__createBones__(prefix='Ik', addShapes=False, addXfm=False, father=self.gp['skelIk'])
        
        # calculate length
        self.length = 0
        self.iteLength = []
        for i in range(1, len(self.jntsIk)):
            self.iteLength.append(self.length)
            self.length += self.jntsIk[i].tx.get()
        self.iteLength.append(self.length) 
        
        
        
        #
        # create controls for spine Ik
        #
        self.spineIkCtrl    = []
        self.spineIkCtrlOff = []
        spineIkCtrlName = ['Hip', 'Middle', 'Bust']
        for i in range(3):
            # create shape
            self.spineIkCtrl.append( shapesBiblio.cylinderX(name=self.name+spineIkCtrlName[i], parent=self.gp['ctrl'], color=self.colorOne) )
            # place this last
            snap = (((i+1)*len(self.bonesTPL))/3)-1
            self.spineIkCtrl[i].setTransformation( rig.matrix.vecToMat( dir=self.dirVectFlat, up=self.upVectFlat, pos=self.bonesTPL[snap].getTranslation(space='world'), order='xyz' ) )
            xfm.__xfm__(self.spineIkCtrl[i], lock=False, prefix='_grp')
            # scale shape
            arShape.scaleShape(self.spineIkCtrl[i].getShape(), self.bonesTPL[0], self.bonesTPL[2], axis=[1,0.7,0.7])
            # create offset shape
            if (i==0) or (i==2):
                self.spineIkCtrlOff.append( shapesBiblio.starX(name=self.name+spineIkCtrlName[i]+'Offset', parent=self.spineIkCtrl[-1], color=self.colorTwo) )
                # scale shape
                arShape.scaleShape(self.spineIkCtrlOff[-1].getShape(), self.bonesTPL[0], self.bonesTPL[2], axis=[1,0.7,0.7])
        
        # create constrain for controls spine Ik
        pmc.parentConstraint(self.baseCtrl,   self.spineIkCtrl[0].getParent(),  name=self.spineIkCtrl[0]+'_paCst',  maintainOffset=True)
        pmc.parentConstraint(self.jntsFk[-1], self.spineIkCtrl[-1].getParent(), name=self.spineIkCtrl[-1]+'_paCst', maintainOffset=True)
        
        
        # create cluster influence for hip and bust controls into the middle curve
        # create array to have the right weight
        weightHip  = []
        weightBust = []
        num        = various.getNumAtoms(self.curveMid)
        for i in range(num):
            weightBust.append( self.iteLength[i] / self.length)
            weightHip.append(1-weightBust[i])
        weightHipBust = {self.spineIkCtrl[0]:weightHip, self.spineIkCtrl[-1]:weightBust}
        
        
        atomsFlat = pmc.PyNode(self.curveMid+'.cv[0:'+str(num-1)+']')
        atoms     = various.getAtoms(self.curveMid, flat=True)
        clusterIk = []
        for spineIkCtrlTmp in [self.spineIkCtrl[0], self.spineIkCtrl[-1]]:
            # create cluster
            clusterIk.append( pmc.cluster(atomsFlat, relative=False, frontOfChain=True, weightedNode=[spineIkCtrlTmp, spineIkCtrlTmp])[0])
            # connect inverse matrix
            spineIkCtrlTmp.parentInverseMatrix[0] >> clusterIk[-1].bindPreMatrix
            # rename cluster
            clusterIk[-1].rename(spineIkCtrlTmp.name()+'_clt')
            # set weight
            for i in range(len(atoms)):
                clusterIk[-1].setWeight(self.curveMid.getShape(), 0, atoms[i], weightHipBust[spineIkCtrlTmp][i], [1])

        
        
        # connect shape of the Fk curve to the shape orig of the middl
        curveMidShapeOrig = self.curveMid.getShapes()[-1]
        self.curveFk.getShape().worldSpace[0] >> curveMidShapeOrig.connections(plugs=True)[0]
        pmc.delete(curveMidShapeOrig)
        
        
        
        #
        # create motion path to constrain the middle spine control
        #
        spineIkMidHookPos = pmc.createNode('transform', name=self.spineIkCtrl[1].name()+'_hookPos', parent=self.gp['nxf'])
        # create motion path
        spineIkMidMpth = pmc.createNode('motionPath', name=self.spineIkCtrl[1].name()+'_mpth')
        self.curveMid.getShape().worldSpace[0] >> spineIkMidMpth.geometryPath
        spineIkMidMpth.allCoordinates >> spineIkMidHookPos.translate
        spineIkMidMpth.uValue.set(0.5)
        # create constrain
        pmc.pointConstraint(spineIkMidHookPos, self.spineIkCtrl[1].getParent(), name=self.spineIkCtrl[1].getParent()+'_ptCst', mo=False)
        
        # create orient system for the middle spine control
        spineIkMidHookRot = pmc.createNode('transform', name=self.spineIkCtrl[1].name()+'_hookRot', parent=self.gp['nxf'])
        pmc.pointConstraint(self.spineIkCtrl[0], spineIkMidHookRot, name=spineIkMidHookRot+'_ptCst',  maintainOffset=False)
        pmc.aimConstraint(self.spineIkCtrl[-1],  spineIkMidHookRot, name=spineIkMidHookRot+'_aimCst', maintainOffset=False, worldUpType='objectrotation', worldUpObject=self.spineIkCtrl[0], worldUpVector=[0,1,0], aimVector=[1,0,0], upVector=[0,1,0])
        pmc.orientConstraint(spineIkMidHookRot, self.spineIkCtrl[1].getParent(), name=self.spineIkCtrl[1].getParent()+'_orCst', maintainOffset=False)
        
        
        
        
        #
        # create cluster influence for middle controls
        #
        num       = various.getNumAtoms(self.curveIk)-2
        atomsFlat = pmc.PyNode(self.curveIk+'.cv[1:'+str(num)+']')
        # create cluster
        clusterIk.append( pmc.cluster(atomsFlat, relative=False, frontOfChain=True, weightedNode=[self.spineIkCtrl[1], self.spineIkCtrl[1]])[0])
        # connect inverse matrix
        self.spineIkCtrl[1].parentInverseMatrix[0] >> clusterIk[-1].bindPreMatrix
        # rename cluster
        clusterIk[-1].rename(self.spineIkCtrl[1].name()+'_clt')
        
        # connect shape of the Mid curve to the shape orig of the Ik
        curveIkShapeOrig = self.curveIk.getShapes()[-1]
        self.curveMid.getShape().worldSpace[0] >> curveIkShapeOrig.connections(plugs=True)[0]
        pmc.delete(curveIkShapeOrig)
        
        
        
        
        #
        # create spline ik
        #
        ikHand = pmc.ikHandle(startJoint=self.jntsIk[0], endEffector=self.jntsIk[-1], curve=self.curveIk, name=self.name+'ikHand', solver='ikSplineSolver', parentCurve=False, createCurve=False)
        pmc.select(clear=True)        
        ikHand[0].setParent(self.gp['nxf'])
        pmc.select(clear=True)
        ikHand[1].rename(self.name+'ikEff')
        # options for ik handle
        ikHand[0].rootTwistMode.set(True)
        ikHand[0].dTwistControlEnable.set(True)
        ikHand[0].dWorldUpType.set(4)
        # connect World Up Object
        self.spineIkCtrl[0].worldMatrix[0] >> ikHand[0].dWorldUpMatrix
        self.spineIkCtrl[2].worldMatrix[0] >> ikHand[0].dWorldUpMatrixEnd
        
        
        #
        # create motion path for each bones to get a good scale system
        #
        distTools = []
        npc = pmc.createNode('nearestPointOnCurve')
        self.curveIk.getShape().worldSpace[0] >> npc.inputCurve
        for i in range(len(self.jntsIk)):
            # create motion path
            motionPath = pmc.createNode('motionPath', name=self.jntsIk[i].name()+'_mpth')
            # connect motion path to curve Ik
            self.curveIk.getShape().worldSpace[0] >> motionPath.geometryPath
            
            # to find the proper parameter on the motion path
            npc.inPosition.set(self.jntsIk[i].getTranslation(space='world'))
            motionPath.uValue.set( npc.parameter.get())
            
            if i < (len(self.jntsIk)-1):
                # create distance tools
                distTools.append( pmc.createNode('distanceBetween', name=self.jntsIk[i].name()+'_dist') )
                # connect the first point
                motionPath.allCoordinates >> distTools[i].point1
            if i:
                # connect the second point
                motionPath.allCoordinates >> distTools[i-1].point2
        pmc.delete(npc)
        
              
        for i in range(len(distTools)):
            # create multiply
            scaleMutl = pmc.createNode('multDoubleLinear', name=self.jntsIk[i]+'_mlt')
            distTools[i].distance >> scaleMutl.input1
            scaleMutl.input2.set(1.0/distTools[i].distance.get())
            scaleMutl.output >> self.jntsIk[i].scaleX
        
        #
        # create sub control and 2SK joint 
        #
        self.spineIkCtrlSub = []
        # 2SK joint for spine hip offset
        self.spineIkCtrlSub.append( shapesBiblio.rhombusX(name=self.spineIkCtrlOff[0].name()+'_sub', parent=self.spineIkCtrlOff[0], color=self.colorTwo) )
        self.bones2SK.append( bn.create2SK(self.spineIkCtrl[0].name(), self.spineIkCtrlSub[-1]) )
        # 2SK joint for spine Ik
        for i in range(len(self.jntsIk)):
            self.spineIkCtrlSub.append( shapesBiblio.rhombusX(name=self.jntsFk[i].name()+'_sub', parent=self.jntsIk[i], color=self.colorTwo) )
            self.bones2SK.append( bn.create2SK(self.jntsFk[i].name(), self.spineIkCtrlSub[-1]) )
        # 2SK joint for spine bust offset
        self.spineIkCtrlSub.append( shapesBiblio.rhombusX(name=self.spineIkCtrlOff[-1].name()+'_sub', parent=self.spineIkCtrlOff[-1], color=self.colorTwo) )
        self.bones2SK.append( bn.create2SK(self.spineIkCtrl[-1].name(), self.spineIkCtrlSub[-1]) )
        
        
        # pickwalk
        arPickwalk.setPickWalk(self.spineIkCtrl, type='UD')
        arPickwalk.setPickWalk(self.spineIkCtrlOff, type='UD')
        arPickwalk.setPickWalk(self.spineIkCtrlSub, type='UD')
        arPickwalk.setPickWalk([self.spineIkCtrl[0], self.spineIkCtrlOff[0]], type='LR')
        arPickwalk.setPickWalk([self.spineIkCtrl[-1], self.spineIkCtrlOff[-1]], type='LR')
        
        return {self.ikSets:[self.spineIkCtrl, self.spineIkCtrlOff], self.subSets:self.spineIkCtrlSub }





toto = spine('spine', bones=['spine1_TPLjnt'], autoHierarchy=True, parent='FLY')

toto.build()
