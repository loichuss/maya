#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 07 dec 2011
#
#   Arm
#

import pymel.core as pmc
import pymel.core.datatypes as dt

import common.various as various
import clean.clean as clean
import rig.matrix
import rig.bone
import rig.xfm as xfm
import rig.attribut as attribut 
import constrain.matrixConstrain as matrixConstrain

import shapes.biblio as shapesBiblio
import shapes.shape as arShape
import bones.bone as bn
import tools.ribbon as ribbon
import attributs.attribut as arAttributs
import tools.hierarchy as arHierarchy
import tools.pickwalk as arPickwalk


reload(ribbon)


class arm():
    
    def __init__(self, name, bones, parent=None, colorOne=17, colorTwo=21):
        
        # check elements
        shoulder = various.checkObj(bones['shoulder'], type=['joint'])
        wrist    = various.checkObj(bones['wrist'][0], type=['joint'])
        wristTip = various.checkObj(bones['wrist'][1], type=['joint'])
        arm      = []
        for i in range(len(bones['arm'])):
            arm.append( various.checkObj(bones['arm'][i], type=['joint']) )
        if parent:
            parent = various.checkObj(parent, type=['joint', 'transform'])
        
        # check if each object exists
        self.check = True
        if None in arm:
            self.check = False
        if (shoulder == None) or (wrist == None) or (wristTip == None) or (parent == None):
            self.check = False
        
        # check name
        if self.check:
            for i in range(len(arm)):
                # rename properly
                if various.renameObject(arm[i], prefix='_TPLjnt')==False:
                    self.check = False
            for obj in [shoulder, wrist, wristTip]:
                # rename properly
                if various.renameObject(obj, prefix='_TPLjnt')==False:
                    self.check = False
        
        
        # create self variable
        if self.check:
            self.name        = name
            self.shoulderTPL = shoulder
            self.armTPL      = arm
            self.wristTPL    = wrist
            self.wristTipTPL = wristTip
            self.parent      = parent
            self.colorOne    = colorOne
            self.colorTwo    = colorTwo
            
            # list for each 2SK bones
            self.bones2SK = []
        else:
            vp.vPrint('building %s will failed' % name, 1)
    
    
    
    def build(self):
        """build arm"""
        if self.check:
        
            # create hierarchy group
            self.hierarchy = arHierarchy.createHierarchy()
            
            
            # create group
            self.gp = {}
            self.gp['main']  = pmc.createNode('transform', name=self.name+'_grp')
            if self.parent:
                self.gp['main'].setParent(self.parent)
            else:
                self.gp['main'].setParent(hierarchy['SCALEOFFSET'])
            self.gp['scale'] = pmc.createNode('transform', name=self.name+'_scale_grp', parent=self.gp['main'])
            self.gp['skel']  = pmc.createNode('transform', name=self.name+'_skel_grp',  parent=self.gp['scale'])
            self.gp['ctrl']  = pmc.createNode('transform', name=self.name+'_ctrl_grp',  parent=self.gp['scale'])
            self.gp['rib']   = pmc.createNode('transform', name=self.name+'_rib_grp',   parent=self.gp['ctrl'])
            self.gp['roll']  = pmc.createNode('transform', name=self.name+'_roll_grp',  parent=self.gp['ctrl'])
            self.gp['tool']  = pmc.createNode('transform', name=self.name+'_tool_grp',  parent=self.gp['scale'])
            self.gp['dist']  = pmc.createNode('transform', name=self.name+'_dist_grp',  parent=self.gp['tool'])
            self.gp['aim']   = pmc.createNode('transform', name=self.name+'_aim_grp',   parent=self.gp['tool'])
            self.gp['curve'] = pmc.createNode('transform', name=self.name+'_curve_grp', parent=self.gp['tool'])
            clean.__lockHideTransform__(self.gp['main'], channel=['t', 'r', 's'])
            clean.__lockHideTransform__(self.gp['ctrl'], channel=['t', 'r', 's', 'v'])
            
            
            # create main sets
            pmc.select(clear=True)
            self.mainSets = pmc.sets(name=self.name+'_ctrls')
            self.subSets  = pmc.sets(name=self.name+'_sub_ctrls')
            self.debSets  = pmc.sets(name=self.name+'_debug_ctrls')
            pmc.sets(self.hierarchy['CONTROLS'], addElement=self.mainSets)
            pmc.sets(self.mainSets, addElement=self.subSets)
            pmc.sets(self.mainSets, addElement=self.debSets)
            
            # create parts
            shoulder   = self.__shoulder__()
            armDefault = self.__armDefault__(shoulder[self.mainSets])
            armFK      = self.__armFK__(shoulder[self.mainSets])
            armIK      = self.__armIK__()
            armFinal   = self.__armFinal__(armIK[self.mainSets][0])
            
            
            # sets
            for key in shoulder.keys():
                pmc.sets(key, addElement=shoulder[key])
            
            for key in armDefault.keys():
                pmc.sets(key, addElement=armDefault[key])
            
            for key in armFK.keys():
                pmc.sets(key, addElement=armFK[key])
                
            for key in armIK.keys():
                pmc.sets(key, addElement=armIK[key])
           
            for key in armFinal.keys():
                pmc.sets(key, addElement=armFinal[key])
            
            
            # connect 2SK jnt together
            bn.__connect2SK__(self.bones2SK)
    
    
    
    
    #              #
    #   SHOULDER   #
    #              #
    
    def __shoulder__(self):
        
        # create main group for shoulder
        self.gp['shoulder'] = pmc.createNode('transform', name=self.shoulderTPL.name().replace('_TPLjnt', '_Skel_grp'), parent=self.gp['skel'])
        
        # create first control
        shoulder = shapesBiblio.cube(name=self.shoulderTPL.replace('_TPLjnt', ''), color=self.colorOne, parent=self.gp['shoulder'])
        
        # place this last
        shoulder.setTransformation ( rig.matrix.vecToMat( dir=(self.armTPL[0].getTranslation(space='world') - self.shoulderTPL.getTranslation(space='world')), up=dt.Vector(0,1,0), pos=self.shoulderTPL.getTranslation(space='world'), order='xyz' ) )
        xfm.__xfm__(shoulder)
        
        # scale shape
        arShape.scaleShape(shoulder.getShape(), self.shoulderTPL, self.armTPL[0])
        
        # create offset control
        shoulderOff = shapesBiblio.cube(name=self.shoulderTPL.replace('_TPLjnt', 'Offset'), color=self.colorTwo, parent=shoulder)
        self.bones2SK.append( bn.create2SK(shoulder.name(), shoulderOff) )
        
        # create attributs
        shoulder.rotateOrder.setKeyable(True)
        attribut.addAttrSeparator(shoulder)
        pmc.addAttr(shoulder, longName='offsetVisible', attributeType='enum', enumName='No:Yes', keyable=False, hidden=False)
        shoulder.offsetVisible.showInChannelBox(True)
        
        # connect attributs
        shoulderOff.rotateOrder.setKeyable(True)
        shoulderOff.visibility.setLocked(False)
        shoulder.offsetVisible >> shoulderOff.visibility
        shoulderOff.visibility.setLocked(True)
        
        # pickwalk
        arPickwalk.setPickWalk([shoulder, shoulderOff], type='LR')
        
        
        return {self.mainSets:shoulder, self.subSets:shoulderOff}
    
    
    
    
    
    
    #                     #
    #   ARM PLACE JOINT   #
    #                     #
    
    def __armPlaceJnt__(self, parent, prefix=''):
        arm = []
        for i in range(len(self.armTPL)):
            # create bone
            arm.append( pmc.createNode('joint', name=self.armTPL[i].replace('_TPLjnt', prefix) ) )
            # place
            if i == (len(self.armTPL)-1):
                arm[i].setTransformation ( rig.matrix.vecToMat( dir=(self.wristTPL.getTranslation(space='world') - self.armTPL[i].getTranslation(space='world')), up=dt.Vector(0,1,0), pos=self.armTPL[i].getTranslation(space='world'), order='xyz' ) )
            else:
                arm[i].setTransformation ( rig.matrix.vecToMat( dir=(self.armTPL[i+1].getTranslation(space='world') - self.armTPL[i].getTranslation(space='world')), up=dt.Vector(0,1,0), pos=self.armTPL[i].getTranslation(space='world'), order='xyz' ) )
            rig.bone.__rotateToOrient__(arm[i])
            # set parent 
            if i:
                arm[i].setParent( arm[i-1] )
            else:
                arm[i].setParent( parent )
        # and the last bone
        arm.append( pmc.createNode('joint', name=self.wristTPL.replace('_TPLjnt', prefix) ) )
        arm[-1].setTransformation ( rig.matrix.vecToMat( dir=(self.wristTipTPL.getTranslation(space='world') - self.wristTPL.getTranslation(space='world')), up=dt.Vector(0,1,0), pos=self.wristTPL.getTranslation(space='world'), order='xyz' ) )
        rig.bone.__rotateToOrient__(arm[-1])
        arm[-1].setParent( arm[-2] )
        
        return arm
    
    
    
    
    
    #                 #
    #   ARM DEFAULT   #
    #                 #
    
    def __armDefault__(self, shoulder):

        # main arm group
        self.gp['arm'] = pmc.createNode('transform', name=self.armTPL[0].name().replace('_TPLjnt', '_Skel_grp'), parent=self.gp['skel'])
        # place
        matrixConstrain.snapObject(shoulder, self.gp['arm'], channel=[1,1,1,1])
        matrixConstrain.snapObject(self.armTPL[0], self.gp['arm'], channel=[1,0,0,0])
        # create constrain
        matrixConstrain.matrixConstrain(shoulder, self.gp['arm'], channel=[1,1,0,1], keepInfo=False, mo=True)
        # clean channels
        clean.__lockHideTransform__(self.gp['arm'], channel=['t', 'r', 's', 'v'])
        
        # return list
        mainSetsList = []
        subSetsList  = []
        
        
        #
        # create default arm
        #
        self.arm = self.__armPlaceJnt__(parent=self.gp['arm'], prefix='')
        
        # calcul the total length 
        self.length = 0
        for i in range(len(self.armTPL)):
            self.length += (self.arm[i+1].translateX.get())
        
        
        # create on each bones one locator (locator shape has the attribut world position wich is very interesting
        self.locArm = {}
        
        # the first locator is for the shoulder
        locGrp = pmc.createNode('transform', name=shoulder.name()+'_loc', parent=shoulder)
        locGrp.visibility.set(False)
        pmc.createNode('locator',  name=locGrp.name()+'Shape', parent=locGrp)
        self.locArm[shoulder] = locGrp
        
        # and then for each arm
        for i in range(len(self.arm)):
            locGrp = pmc.createNode('transform', name=self.arm[i].name()+'_loc', parent=self.arm[i])
            locGrp.visibility.set(False)
            pmc.createNode('locator',  name=locGrp.name()+'Shape', parent=locGrp)
            self.locArm[self.arm[i]] = locGrp
            
        
        
        # create roll bones
        self.rollArm     = {}
        self.threePointArm    = {}
        self.rollArm2SK  = {}
        
        for i in range(len(self.arm)-1):
            
            # create proper variable depending on i
            if i == 0:
                masterPt = shoulder
            else:
                masterPt = self.arm[i-1]
            
            
            # create system to have one locator always matching with the current bones
            # distance tool
            distGrp = pmc.createNode('transform', name=self.arm[i].name()+'_boneDist', parent=self.gp['dist'])
            dist    = pmc.createNode('distanceDimShape', name=self.arm[i].name()+'_boneDistShape', parent=distGrp)
            # hide
            distGrp.visibility.set(False)
            
            # connect locators on distance tools
            self.locArm[masterPt].getShape().worldPosition[0] >> dist.startPoint
            self.locArm[self.arm[i]].getShape().worldPosition[0] >> dist.endPoint
            
            
            # create aim target
            aimTgt    = pmc.createNode('transform', name=self.arm[i].name()+'_aim',  parent=self.gp['aim'])
            aimTgtLoc = pmc.createNode('locator',   name=aimTgt.name()+'Shape', parent=aimTgt)
            aimTgt.visibility.set(False)
            aimTgtGrp = xfm.__xfm__(aimTgt, lock=False)
            aimTgtGrp.inheritsTransform.set(False)
            matrixConstrain.matrixConstrain(self.arm[i], aimTgtGrp, channel=[1,1,0,1], keepInfo=False)
            dist.distance >> aimTgt.translateX
            
            
            
            # create roll system
            # create main group
            rollGrp = pmc.createNode('transform', name=self.arm[i].name()+'_roll_grp', parent=self.gp['roll'])
            
            # create constrain
            pmc.pointConstraint(masterPt, rollGrp, name=rollGrp.name()+'_ptCst', maintainOffset=False)
            pmc.aimConstraint(aimTgt, rollGrp, name=rollGrp.name()+'_aimCst', maintainOffset=False, worldUpType='objectrotation', worldUpObject=masterPt, worldUpVector=[0,1,0], aimVector=[1,0,0], upVector=[0,1,0])
            
            # create sub group and constrain it
            subRollGrp = pmc.createNode('transform', name=self.arm[i].name()+'SubRoll_grp', parent=rollGrp)
            pmc.pointConstraint(self.arm[i], subRollGrp, name=subRollGrp.name()+'_ptCst', maintainOffset=False)
            
            # create shape and 2SK
            mainSetsList.append( shapesBiblio.circleX(name=self.arm[i].name()+'Roll', color=self.colorOne, parent=subRollGrp) )
            subSetsList.append(  shapesBiblio.rhombusX(name=self.arm[i].name()+'SubRoll', color=self.colorTwo, parent=mainSetsList[-1]) )
            rollTmp = [mainSetsList[-1], subSetsList[-1]]
            clean.__lockHideTransform__(rollTmp[-2], channel=['ry', 'rz', 's', 'v'])
            jnt = bn.create2SK(rollTmp[-2].name(), rollTmp[-1])
            
            # pickwalk
            arPickwalk.setPickWalk([rollTmp[-2], rollTmp[-1]], type='LR')
        
            # scale
            clean.__lockHideTransform__(jnt, channel=['s'], lock=False)
            self.arm[i].scaleY >> jnt.scaleY
            self.arm[i].scaleZ >> jnt.scaleZ
            clean.__lockHideTransform__(jnt, channel=['s'])
            
            # add into dico
            self.rollArm[self.arm[i]]    = rollTmp
            self.rollArm2SK[self.arm[i]] = jnt
            
        
        
        for i in range(2, len(self.arm)):
            # three points circular to get a perfect circle for offset part in ribbon bone
            tpc = pmc.createNode('makeThreePointCircularArc', name=self.arm[i].name()+'_tpc')
            tpc.sections.set(4)
            self.locArm[self.arm[i-2]].getShape().worldPosition[0] >> tpc.point1
            self.locArm[self.arm[i-1]].getShape().worldPosition[0] >> tpc.point2
            self.locArm[self.arm[i]].getShape().worldPosition[0] >> tpc.point3
            
            
            # nearest point for i-2
            npc = pmc.createNode('nearestPointOnCurve', name=self.arm[i-2].name()+'_npc')
            # connections
            tpc.outputCurve >> npc.inputCurve
            # add into dico
            if (self.arm[i-2] in self.threePointArm.keys()):
                self.threePointArm[self.arm[i-2]].append(npc)
            else:
                self.threePointArm[self.arm[i-2]] = [npc]
            
            
            # nearest point for i-1
            npc = pmc.createNode('nearestPointOnCurve', name=self.arm[i-1].name()+'_npc')
            # connections
            tpc.outputCurve >> npc.inputCurve
            # add into dico
            if (self.arm[i-1] in self.threePointArm.keys()):
                self.threePointArm[self.arm[i-1]].append(npc)
            else:
                self.threePointArm[self.arm[i-1]] = [npc]
        
    
        # return
        return {self.mainSets:mainSetsList, self.subSets:subSetsList}
    
    
    
    
    
    
    
    
    #            #
    #   ARM FK   #
    #            #
    
    def __armFK__(self, shoulder):
        
        
        self.armFk = self.__armPlaceJnt__(parent=self.gp['arm'], prefix='fk')
        
        
        # create controlor
        for i in range(len(self.armFk)):
            # put a better rotate order
            self.armFk[i].rotateOrder.set(3)
            
            # add shape to joint
            tmp = shapesBiblio.cube(name=self.armFk[i], color=self.colorOne)
            pmc.parent(tmp.getShape(), self.armFk[i], shape=True, relative=True)
            pmc.delete(tmp)
            
            # scale shape
            if i < (len(self.armFk)-1):
                arShape.scaleShape(self.armFk[i].getShape(), self.armFk[i], self.armFk[i+1])
        
            # clean channel box
            self.armFk[i].rotateOrder.setKeyable(True)
            clean.__lockHideTransform__(self.armFk[i], channel=['t', 'v', 'radi'])
        
        # add attribut for the first fk bone
        attribut.addAttrSeparator(self.armFk[0])
        # ADD CONSTRAINT ORIENT
        
        
        # pickwalk
        chain = [shoulder]
        chain.extend(self.armFk[0:-1])
        arPickwalk.setPickWalk(chain, type='UD')
        
        return {self.mainSets:self.armFk}
        
        
    
    
    
    
    
    
    #            #
    #   ARM IK   #
    #            #
        
    def __armIK__(self):
    
    
        self.armIk = self.__armPlaceJnt__(parent=self.gp['arm'], prefix='ik')
        
        
        # create ik controlor
        ikCtrl = shapesBiblio.circleX(name=self.wristTPL.replace('_TPLjnt', 'Ctrl'), color=self.colorOne, parent=self.gp['arm'])
        matrixConstrain.snapObject(self.armIk[-1], ikCtrl)
        xfm.__xfm__(ikCtrl)
        # orient constrain to control the latest joint on arm
        pmc.orientConstraint(ikCtrl, self.armIk[-1], name=self.armIk[-1].name()+'_orCst', maintainOffset=False)
        
        
        # create ik handle
        ikHand = pmc.ikHandle( name=self.armTPL[0].name().replace('_TPLjnt', 'ikHand') ,startJoint=self.armIk[0], endEffector=self.armIk[-1], priority=1, weight=1.0, solver='ikRPsolver', snapHandleFlagToggle=False )
        ikHand[1].rename(self.wristTPL.replace('_TPLjnt', 'ikEff'))
        ikHand[0].setParent(self.gp['tool'])
        ikHand[0].visibility.set(False)
        # constrain between the controlor and the handle
        pmc.pointConstraint(ikCtrl, ikHand[0], name=ikHand[0].name()+'_ptCst', maintainOffset=False)
        
        
        
        # pole vector
        pvCtrl = shapesBiblio.diamondSpike(name=self.armTPL[0].replace('_TPLjnt', '_pv'), color=self.colorOne, parent=self.gp['ctrl'])
        # place
        pvCtrl.setTransformation( rig.matrix.vecToMat( dir=(self.wristTPL.getTranslation(space='world') - self.armTPL[0].getTranslation(space='world')), up=(((self.armTPL[0].getTranslation(space='world') + self.wristTPL.getTranslation(space='world'))/2.0) - self.armTPL[len(self.armTPL)/2].getTranslation(space='world')), pos=self.armTPL[len(self.armTPL)/2].getTranslation(space='world'), order='xyz' ) )
        pvCtrl.translateBy([0,-((self.length / len(self.armTPL)) * 1.5),0], space='preTransform')
        pvCtrl.rotate.set([0,0,0])
        xfm.__xfm__(pvCtrl, suffix='_grp')
        # clean channel
        clean.__lockHideTransform__(pvCtrl, channel=['r', 's'])
        # add constrain
        pmc.poleVectorConstraint(pvCtrl, ikHand[0], name=pvCtrl.name()+'_pvCst')
        
        
        
        
    
        
        # stretch part
        # create distance tools
        distGrp = pmc.createNode('transform', name=self.name+'_dist', parent=self.gp['dist'])
        dist    = pmc.createNode('distanceDimShape', parent=distGrp)
        
        # locators
        distStart = pmc.createNode('locator')
        distEnd   = pmc.createNode('locator')
        distStart.getParent().rename(self.arm[0].name()+'_distStart')
        distEnd.getParent().rename(self.arm[-1].name()+'_distEnd')
        distStart.getParent().setParent(self.gp['dist'])
        distEnd.getParent().setParent(self.gp['dist'])
        distStart.worldPosition[0] >> dist.startPoint
        distEnd.worldPosition[0] >> dist.endPoint
        
        distStart = distStart.getParent()
        distEnd = distEnd.getParent()
    
        # hide
        dist.getParent().visibility.set(False)
        distStart.visibility.set(False)
        distEnd.visibility.set(False)
        # constrain
        pmc.pointConstraint(self.armIk[0], distStart, name=distStart.name()+'_ptCst', maintainOffset=False)
        pmc.pointConstraint(ikCtrl, distEnd,  name=distEnd.name()+'_ptCst',   maintainOffset=False)
        
        # get global scale
        # check if the plug in decompose matrix is load
        pmc.loadPlugin('decomposeMatrix', quiet=True)
        decoMat = pmc.createNode('decomposeMatrix', name=self.name + '_decoMat', skipSelect=True)
        self.gp['scale'].worldMatrix >> decoMat.inputMatrix
        
        # multiply the global scale by the length
        globalScaleMult = pmc.createNode('multDoubleLinear', name=self.name+'GlobalScale_mlt')
        decoMat.outputScaleX >> globalScaleMult.input1
        globalScaleMult.input2.set(self.length)
        
        # divide current length by the defaut one
        self.distMult = pmc.createNode('multiplyDivide', name=dist.getParent().name()+'_mlt')
        self.distMult.operation.set(2)
        dist.distance >> self.distMult.input1X
        globalScaleMult.output >> self.distMult.input2X
        # clamp
        distClamp = pmc.createNode('clamp', name=dist.getParent().name()+'_clp')
        distClamp.minR.set(1.0)
        distClamp.maxR.set(1.0)
        self.distMult.outputX >> distClamp.inputR
        # stretch factor
        distFactorMult = pmc.createNode('multDoubleLinear', name=dist.getParent().name()+'Factor_mlt')
        distClamp.outputR >> distFactorMult.input1
        # condition 
        distCond = pmc.createNode('condition', name=dist.getParent().name()+'_cdt')
        distCond.secondTerm.set(1.0)
        distCond.colorIfFalseR.set(1.0)
        distFactorMult.output >> distCond.colorIfTrueR
        
        
        
        
        # create smooth Ik
        anim = pmc.createNode('animCurveUU', name=self.name+'_crv')
        pmc.setKeyframe(anim, float=0.8,  value=0.0,  inTangentType='flat', outTangentType='flat')
        pmc.setKeyframe(anim, float=1.0,  value=0.01, inTangentType='flat', outTangentType='linear')
        pmc.setKeyframe(anim, float=1.05, value=0.0,  inTangentType='flat', outTangentType='flat')
        self.distMult.outputX >> anim.input
        # mutliply by user smoothIk
        animMult = pmc.createNode('multDoubleLinear', name=self.name+'Curve_mlt')
        anim.output >> animMult.input1
        # add with previous scale process
        animAdd = pmc.createNode('addDoubleLinear', name=self.name+'Curve_add')
        distCond.outColorR >> animAdd.input1
        animMult.output >> animAdd.input2
        
        
    
        
        # squash  a=1/stretch
        squash = pmc.createNode('multiplyDivide', name=self.name+'Squash_mlt')
        squash.operation.set(2)
        squash.input1X.set(1.0)
        animAdd.output >> squash.input2X
        # squash difference  b=a-1
        squashDif = pmc.createNode('addDoubleLinear', name=self.name+'Squash_min')
        #squashDif.operation.set(2)
        squash.outputX >> squashDif.input1
        squashDif.input2.set(-1.0)
        # squash factor  c=b*UI
        squashFactor = pmc.createNode('multDoubleLinear', name=self.name+'Squash_mdl')
        squashDif.output >> squashFactor.input1
        
        
    
        
        # add attribut for controlor
        pmc.addAttr(ikCtrl, longName='subCtrlVisible', attributeType='enum', enumName='None:Offset:Sub:Debug', keyable=False, hidden=False)
        attribut.addAttrSeparator(ikCtrl, 'ik')
        pmc.addAttr(ikCtrl, longName='ikfk',          attributeType='float', defaultValue=1.0, keyable=True, minValue=0.0, maxValue=1.0 )
        pmc.addAttr(ikCtrl, longName='twist',         attributeType='float', keyable=True)
        pmc.addAttr(ikCtrl, longName='smoothIk',      attributeType='float', defaultValue=0.0,  keyable=True, minValue=0.0, maxValue=1.0 )
        ikCtrl.subCtrlVisible.showInChannelBox(True)
        attribut.addAttrSeparator(ikCtrl, 'Stretch')
        pmc.addAttr(ikCtrl, longName='stretch',       attributeType='bool',  defaultValue=True, keyable=True )
        pmc.addAttr(ikCtrl, longName='stretchFactor', attributeType='float', defaultValue=1.0,  keyable=True, minValue=0.001 )
        pmc.addAttr(ikCtrl, longName='stretchMin',    attributeType='float', defaultValue=1.0,  keyable=True, minValue=0.0, maxValue=1.0 )
        pmc.addAttr(ikCtrl, longName='stretchMax',    attributeType='float', defaultValue=1.05, keyable=True, minValue=1.0 )
        attribut.addAttrSeparator(ikCtrl, 'Squash')
        pmc.addAttr(ikCtrl, longName='squash',        attributeType='bool',  defaultValue=True, keyable=True )
        pmc.addAttr(ikCtrl, longName='squashFactor',  attributeType='float', defaultValue=1.0,  keyable=True )
        pmc.addAttr(ikCtrl, longName='squashFalloff', attributeType='float', defaultValue=0.5,  keyable=True )
        attribut.addAttrSeparator(ikCtrl, 'Circle')
        
        
        # connect attribut for controlor
        ikCtrl.twist >> ikHand[0].twist
        ikCtrl.stretch >> distCond.firstTerm
        ikCtrl.stretchFactor >> distFactorMult.input2
        ikCtrl.stretchMin >> distClamp.minR
        ikCtrl.stretchMax >> distClamp.maxR
        ikCtrl.squashFactor >> squashFactor.input2
        ikCtrl.smoothIk >> animMult.input2
        
        
        
        
        # prepare falloff squash system
        size = len(self.arm)
        if size%2:
            half = [size/2, size/2]
        else:
            half = [(size/2)-1, size/2]
        
        if half[0] != 0:
            unit = (1.0/half[0])
        else:
            unit = 0
        
        # create system for squash fallof Ui
        squashUiMdl = pmc.createNode('multDoubleLinear', name=ikCtrl.name()+'_mdl')
        ikCtrl.squashFalloff >> squashUiMdl.input1
        squashUiMdl.input2.set(-1.0)
        
        # loop on each bone
        for i in range(len(self.arm)):
            # create attribut for each bones about his position
            if i < half[0]:
                defaultVal = (unit*(half[0]-i))
            elif i in half:
                defaultVal = 0.0
            elif i > half[1]:
                defaultVal = (unit*(i-half[1]))
            # add attribut into ik bone
            pmc.addAttr(self.armIk[i], longName='falloff', attributeType='float', defaultValue=defaultVal, keyable=True, minValue=0.0, maxValue=1.0 )
            
            # A=UI* falloff attribut present in Ik bone
            sqBoneUi = pmc.createNode('multDoubleLinear', name=self.armIk[i].name()+'SquashPerBoneUI_mdl')
            self.armIk[i].falloff >> sqBoneUi.input1
            squashUiMdl.output >> sqBoneUi.input2
            
            # B=c*A
            sqBone = pmc.createNode('multDoubleLinear', name=self.armIk[i].name()+'SquashPerBone_mdl')
            sqBoneUi.output >> sqBone.input1
            squashFactor.output >> sqBone.input2
            
            # C=c+B
            sqBoneAdd = pmc.createNode('addDoubleLinear', name=self.armIk[i].name()+'SquashPerBone_add')
            squashFactor.output >> sqBoneAdd.input1
            sqBone.output >> sqBoneAdd.input2
            
            # squash  D=1+C
            sqBonePlus = pmc.createNode('addDoubleLinear', name=self.armIk[i].name()+'SquashPerBone_plu')
            sqBonePlus.input1.set(1.0)
            sqBoneAdd.output >> sqBonePlus.input2
            
            # condition 
            squashCond = pmc.createNode('condition', name=self.armIk[i].name()+'SquashPerBone_cdt')
            ikCtrl.squash >> squashCond.firstTerm
            squashCond.secondTerm.set(1.0)
            squashCond.colorIfFalseR.set(1.0)
            sqBonePlus.output >> squashCond.colorIfTrueR
        
            
            #
            # connections with scale
            
            # stretch
            animAdd.output >> self.armIk[i].scaleX
            
            # squash
            squashCond.outColorR >> self.armIk[i].scaleY
            squashCond.outColorR >> self.armIk[i].scaleZ
        
        
        
        # visibility logic
        self.visCond = []
        for i in range(2,4):
            self.visCond.append( pmc.createNode('condition', name=self.name+'Vis'+str(i)+'_cdt') )
            self.visCond[-1].secondTerm.set(i)
            self.visCond[-1].operation.set(4)
            ikCtrl.subCtrlVisible >> self.visCond[-1].firstTerm
        # hide subRoll
        for key in self.rollArm:
            self.rollArm[key][1].visibility.setLocked(False)
            self.visCond[1].outColorR >> self.rollArm[key][1].visibility
            self.rollArm[key][1].visibility.setLocked(True)
        # hide first roll arm
        self.rollArm[self.arm[0]][0].visibility.setLocked(False)
        ikCtrl.subCtrlVisible >> self.rollArm[self.arm[0]][0].visibility
        self.rollArm[self.arm[0]][0].visibility.setLocked(True)
        # hide latest FK control
        self.armFk[-1].visibility.setLocked(False)
        self.visCond[1].outColorR >> self.armFk[-1].visibility
        self.armFk[-1].visibility.setLocked(True)
        
        
        
        # add attribut for pole vector
        attribut.addAttrSeparator(pvCtrl)
        # ADD CONSTRAINT ORIENT

        # pickwalk
        arPickwalk.setPickWalk([ikCtrl, pvCtrl], type='LR')
        
        
        return {self.mainSets:[ikCtrl, pvCtrl]}






    #               #
    #   ARM FINAL   #
    #               #
    
    def __armFinal__(self, ikCtrl):
    
        # return list
        mainSetsList = []
        subSetsList  = []
        debSetsList = []
        
        # constrain to smoothly go from Ik to Fk
        minus = pmc.createNode('plusMinusAverage', name=ikCtrl.name()+'_min')
        minus.operation.set(2)
        minus.input1D[0].set(1)
        ikCtrl.ikfk >> minus.input1D[1]
        for i in range(len(self.armFk)):
            # orient constrain
            orCst = pmc.orientConstraint(self.armFk[i], self.armIk[i], self.arm[i], name=self.arm[i].name()+'_orCst', maintainOffset=False)
            # set the interpolation to shortest
            orCst.interpType.set(2)
            minus.output1D >> orCst.target[0].targetWeight.inputs(plugs=True)[0]
            ikCtrl.ikfk >> orCst.target[1].targetWeight.inputs(plugs=True)[0]
            
            # scale constrain
            bld = pmc.createNode('blendColors', name=self.arm[i].name()+'_bld')
            self.armIk[i].scale >> bld.color1
            self.armFk[i].scale >> bld.color2
            ikCtrl.ikfk >> bld.blender
            bld.output >> self.arm[i].scale
            
            if i < (len(self.armFk)-1):
                # fk vibility
                self.armFk[i].visibility.setLocked(False)
                minus.output1D >> self.armFk[i].visibility
                self.armFk[i].visibility.setLocked(True)
        
        
        
        # ribbon bones + visibility sub control
        for i in range(len(self.armTPL)):
            # create ribbon
            rib     = ribbon.createRibbon(self.arm[i].name()+'_rib', parent=self.gp['rib'], colorOne=self.colorTwo, colorTwo=self.colorTwo, type='spline')
            ribCtrl = rib.build()
            
            # keep data for sets
            subSetsList.extend(ribCtrl[3])
            debSetsList.extend(ribCtrl[7])
            
            
            # constrains
            # root of ribbon group
            matrixConstrain.matrixConstrain( self.gp['scale'], ribCtrl[1], channel=[1,1,1,1], keepInfo=False, mo=False)
            
            if (self.arm[i] in self.rollArm.keys()):
                startPt = self.rollArm[self.arm[i]][0]
            else:
                startPt = self.arm[i]
            
            if (self.arm[i+1] in self.rollArm.keys()):
                endPt   = self.rollArm[self.arm[i+1]][0]
            else:
                endPt   = self.arm[i+1]
            
            startAim   = endPt
            endAim     = startPt
            startUpAim = startPt
            endUpAim   = endPt
            
            
            # point constrain
            pmc.pointConstraint(startPt,  ribCtrl[2][0], name=ribCtrl[2][0].name()+'_ptCst', maintainOffset=False)
            pmc.pointConstraint(endPt,    ribCtrl[2][2], name=ribCtrl[2][2].name()+'_ptCst', maintainOffset=False)
            
            # aim constrain
            pmc.aimConstraint(startAim, ribCtrl[2][0], name=ribCtrl[2][0].name()+'_aimCst', maintainOffset=False, worldUpType='objectrotation', worldUpObject=startUpAim, worldUpVector=[0,1,0], aimVector=[1,0,0],  upVector=[0,1,0])
            pmc.aimConstraint(endAim,   ribCtrl[2][2], name=ribCtrl[2][2].name()+'_aimCst', maintainOffset=False, worldUpType='objectrotation', worldUpObject=endUpAim,   worldUpVector=[0,1,0], aimVector=[-1,0,0], upVector=[0,1,0])
            pmc.aimConstraint(self.arm[i],   ribCtrl[2][1].getParent(), name=ribCtrl[2][1].getParent().name()+'_aimCst', maintainOffset=False, worldUpType='objectrotation', worldUpObject=self.arm[i],   worldUpVector=[0,1,0], aimVector=[-1,0,0], upVector=[0,1,0])
            
            # scale constrain for last control
            matrixConstrain.matrixConstrain(self.arm[i], ribCtrl[4][0], channel=[0,0,1,1], keepInfo=False)
            matrixConstrain.matrixConstrain(self.arm[i+1], ribCtrl[4][1], channel=[0,0,1,1], keepInfo=False)
            
            
            # circle effect
            offLoc = pmc.createNode('locator', name=ribCtrl[5].name()+'Shape' ,parent=ribCtrl[5])
            offLoc.visibility.set(False)
            offCir = []
            for j in range(len(self.threePointArm[self.arm[i]])):
                offLoc.worldPosition[0] >> self.threePointArm[self.arm[i]][j].inPosition
            
                # create transform node wich will receive the position on curve
                offCir.append( pmc.createNode('transform', name=ribCtrl[2][1].name()+'_circle', parent=self.gp['curve']) )
                offCir[-1].inheritsTransform.set(False)
                self.threePointArm[self.arm[i]][j].result.position >> offCir[-1].translate
            
            # constrain point to switch from one position to another
            ptCst = pmc.pointConstraint(ribCtrl[5], offCir, ribCtrl[2][1], name=ribCtrl[2][1].name()+'_ptCst', skip=('x'))
            
            # ui element pos
            pmc.addAttr(ikCtrl, longName=self.arm[i].name(), attributeType='float', defaultValue=0.0, keyable=True, minValue=0.0, maxValue=1.0 )
            attr = pmc.PyNode(ikCtrl+'.'+self.arm[i].name())
            
            # create condition if each bones are aligned or stretched
            cdt = pmc.createNode('condition', name=self.arm[i].name()+'Circle_cdt')
            cdt.operation.set(3)
            cdt.colorIfTrueR.set(0.0)
            cdt.secondTerm.set(1.0)
            self.distMult.outputX >> cdt.firstTerm
            attr >> cdt.colorIfFalseR
            
            for j in range(len(self.threePointArm[self.arm[i]])):
                cdt.outColorR >> ptCst.target[j+1].targetWeight.inputs(plugs=True)[0]
            
            # ui element neg
            minus = pmc.createNode('plusMinusAverage', name=self.arm[i].name()+'Circle_min')
            minus.operation.set(2)
            minus.input1D[0].set(1)
            cdt.outColorR >> minus.input1D[1]
            minus.output1D >> ptCst.target[0].targetWeight.inputs(plugs=True)[0]
            
            
            # visibility attribut
            for j in range(len(ribCtrl[3])):
                if j == 1:
                    ribCtrl[3][j].visibility.setLocked(False)
                    ikCtrl.subCtrlVisible >> ribCtrl[3][j].visibility
                    ribCtrl[3][j].visibility.setLocked(True)
                else:
                    ribCtrl[3][j].visibility.setLocked(False)
                    self.visCond[1].outColorR >> ribCtrl[3][j].visibility
                    ribCtrl[3][j].visibility.setLocked(True)
            
            for j in range(len(ribCtrl[7])):
                ribCtrl[7][j].visibility.setLocked(False)
                self.visCond[0].outColorR >> ribCtrl[7][j].visibility
                ribCtrl[7][j].visibility.setLocked(True)
            
            
            # fill bones2SK list
            if (self.arm[i] in self.rollArm2SK.keys()):
                self.bones2SK.append( self.rollArm2SK[self.arm[i]] )
            self.bones2SK.extend( ribCtrl[8] )
            
            # clean ribbon
            rib.clean()
        
   
        
        #
        # hide lock
        #
        
        # default part
        clean.lockHideTransform(self.arm, channel=['t', 'r', 's', 'v', 'radi'])
        for key in self.locArm:
            clean.__lockHideTransform__(self.locArm[key], channel=['t', 'r', 's', 'v'])
        
        # ik part
        self.armIk[0].visibility.set(False)
    
    
        return {self.subSets:subSetsList, self.debSets:debSetsList}
    
    
    
    
    #
    # last clean and lock
    #
    def __clean__(self):
        # groups
        for key in self.gp:
            clean.__lockHideTransform__(self.gp[key], channel=['t', 'r', 's', 'v'])
    
    

"""

toto = arm(name='L_arm', bones={'shoulder':'L_shoulder_TPLjnt', 'arm':['L_arm_TPLjnt', 'L_foreArm_TPLjnt'], 'wrist':['L_wrist_TPLjnt', 'L_wristTip_TPLjnt']}, parent='FLY2')
toto.build()
del toto
"""
