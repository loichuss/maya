#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 06 dec 2011
#
#   Fk bones
#

import pymel.core as pmc
import pymel.core.datatypes as dt

import common.vPrint as vp
import common.various as various

import rig.matrix
import rig.bone as bone
import rig.xfm as xfm
import rig.attribut as attribut
import constrain.matrixConstrain as matrixConstrain
import clean

import autorig.shape.biblio as arShapeBiblio
import autorig.shape as arShape
import autorig.bone as arBone
import autorig.tools.hierarchy as arHierarchy
import autorig.tools.pickwalk as arPickwalk
import autorig.attribut as arAttribut



reload(arShapeBiblio)


def decorator(attempt):
    def wrapper(func):
        def wrapped(arg):
            result = func(arg)
            return result   
        return wrapped
    return wrapper






class fk():
    def __init__(self, name, bones, parent=None, autoHierarchy=False, upVect=dt.Vector(0,1,0), upObj=None, colorOne=17, colorTwo=21):
        
        """Create an fk joints module
            - name           : the name for the module
            - bones          : a list of bone (could be a pymel object or a string)
            - parent         : the father of the module
            - autoHierarchy  : get each children of the given bone
            - upVect         : the up vector to have the proper orientation
            - upObj          : as well use to create the proper orientation but thanks to the position of an object
            - colorOne       : the color of the shape
            - colorTwo       : the color of the sub shape
            """
        
        #                           #
        #   check input variables   #
        #                           #
        
        
        # use to see if each object given are joint type
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
            if (isinstance(upVect, dt.Vector))==False:
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
            else:
                # rename properly
                if various.renameObject(upObj, prefix='_TPLjnt')==False:
                    self.check = False
                
        
        # parent object if given
        if parent:
            parent = various.checkObj(parent, type=['transform', 'joint'])
            if parent==None:
                self.check = False
        
        
        # create automatic hierarchy if desire
        if self.check:
            if autoHierarchy:
                bones = various.listChildrenByType(bones[0], type=['joint'])
                if len(bones[0].getChildren()) > 1:
                    tmp = bones[0].getChildren()[1]
                    if various.checkObj(tmp, type=['joint'], echo=False):
                        upObj = tmp
        
        
        # create vector according to object up
        if upObj:
            upVect = (upObj.getTranslation(space='world') - bones[0].getTranslation(space='world'))
            upVect.normalize() 
        
        # rename template if badly done
        if self.check:
            for i in range(len(bones)):
                # rename properly
                if not various.renameObject(bones[i], prefix='_TPLjnt'):
                    self.check = False


        # keep variable
        if self.check:
            # self part       
            self.bonesTPL = bones
            self.name     = name
            self.parent   = parent
            self.upVect   = upVect
            self.colorOne = colorOne
            self.colorTwo = colorTwo
            
            # list for each 2SK bones
            self.bones2SK = []
            self.gp       = {}
            self.offset   = []
            
            
        else:
            vp.vPrint('building %s will failed' % name, 1)
        
    
    
    
    @decorator(True)
    def build(self):
        """build FK"""
        
        if not self.check:
            vp.vPrint('missing or wrong data in module, skip building process', 1)
            return None
        
        
        """
        Truc a cacher ou a locker trouver un system
        
        creation de la hierachy pour faire la selection rapide
        
        connection des bones 2sk ensemble
        
        rajout des shapes dans les sets
        
        """
        
        # create hierarchy group
        hierarchy = arHierarchy.createHierarchy()
        
        
        # create main group then parent it
        self.gp['main'] = pmc.createNode('transform', name=self.name+'_grp')
        if self.parent:
            self.gp['main'].setParent(self.parent)
        else:
            self.gp['main'].setParent(hierarchy['SCALEOFFSET'])
        
        
        # lock attribut from group
        clean.__lockHideTransform__(self.gp['main'], channel=['t', 'r', 's'])
        
        
        # create bones
        self.jnts = []
        for i in range(len(self.bonesTPL)-1):
            # create joint
            self.jnts.append( pmc.createNode('joint', name=self.bonesTPL[i].replace('_TPLjnt', '') ) )
            self.jnts[i].setTransformation ( rig.matrix.vecToMat( dir=(self.bonesTPL[i+1].getTranslation(space='world') - self.bonesTPL[i].getTranslation(space='world')), up=self.upVect, pos=self.bonesTPL[i].getTranslation(space='world'), order='xyz' ) )
            rig.bone.__rotateToOrient__(self.jnts[i])
            
            # set parent 
            if i:
                self.jnts[i].setParent( self.jnts[i-1] )
            else:
                self.jnts[i].setParent( self.gp['main'] )
            
            
            # add shape to joint
            if i:
                tmp = arShapeBiblio.cube(name=self.jnts[i], color=self.colorOne)
            else:
                tmp = arShapeBiblio.cubeCircle(name=self.jnts[i], color=self.colorOne)
            pmc.parent(tmp.getShape(), self.jnts[i], shape=True, relative=True)
            pmc.delete(tmp)
            
            # scale shape
            arShape.scaleShape(self.jnts[i].getShape(), self.jnts[i], self.bonesTPL[i+1])
    
            # clean channel box
            self.jnts[i].rotateOrder.setKeyable(True)
            clean.__lockHideTransform__(self.jnts[i], channel=['v', 'radi'])
            
            # add xfm
            xfm.__xfm__(self.jnts[i], type='joint')
            
            # add offset
            self.offset.append( arShapeBiblio.rhombusX(name=self.jnts[i]+'_off', color=self.colorTwo, parent=self.jnts[i]) )
            self.bones2SK.append( bone.create2SK(self.jnts[i].name(), self.offset[i]) )
        
        
        # create attribut
        attribut.addAttrSeparator(self.jnts[0])
        pmc.addAttr(self.jnts[0], longName='offsetVisible', attributeType='enum', enumName='No:Yes', keyable=False, hidden=False)
        self.jnts[0].offsetVisible.showInChannelBox(True)
        
        for i in range(len(self.offset)):
            self.offset[i].visibility.setLocked(False)
            self.jnts[0].offsetVisible >> self.offset[i].visibility
            self.offset[i].visibility.setLocked(True)
        
        
        # connect 2SKjnt together
        bone.__connect2SK__(self.bones2SK)
        
        # pickwalk attribut
        arPickwalk.setPickWalk(self.jnts, type='UD')
        arPickwalk.setPickWalk(self.offset, type='UD')
        
        alternate = []
        for i in range(len(self.jnts)):
            alternate.append(self.jnts[i])
            alternate.append(self.offset[i])
        arPickwalk.setPickWalk(alternate, type='LR')
        
        
        # add into CONTROLS sets
        pmc.select(clear=True)
        set = pmc.sets(name=self.name+'_ctrls')
        pmc.sets(set, addElement=self.jnts)
        pmc.sets(hierarchy['CONTROLS'], addElement=set)
        
        setSub = pmc.sets(name=self.name+'Sub_ctrls')
        pmc.sets(setSub, addElement=self.offset)
        pmc.sets(set, addElement=setSub)
        
        
        # deselect
        pmc.select(clear=True)
        
            
        
        



"""

#toto = fk(name='myJnt', bones=[pmc.PyNode('joint1_TPLjnt'), pmc.PyNode('joint2_TPLjnt'), pmc.PyNode('joint3_TPLjnt'), pmc.PyNode('joint4_TPLjnt')])

toto = fk(name='myJnt', bones=['joint1_TPLjnt'], parent='FLY2', upVect=[0,-1,0], autoHierarchy=True)

toto.build()
del toto
"""
