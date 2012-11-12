#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 12 nov 2012
#
#   Fk Module
#

import copy
import pymel.core as pmc
import pymel.core.datatypes as dt

import common.vPrint as vp
import common.various as various

import rig.matrix
import rig.xfm as xfm
import rig.attribut as attribut
import clean

import autorig.shape.biblio as arShapeBiblio
import autorig.shape as arShape
import autorig.bone as arBone
import autorig.tools.pickwalk as arPickwalk
import autorig.settings as arParam





class fk(object):
    def __init__(self, name, bones, parent=None, up=dt.Vector(0,1,0), colorOne=17, colorTwo=21):
        
        """
        Create an FK joints module
            - name           : the name for the module
            - bones          : a list of bone (could be a pymel object or a string)
            - parent         : the father of the module (could be a pymel object or a string)
            - up             : the up vector to have the proper orientation (could be an array or a dt.Vector class or a pymel object or a string)
            - colorOne       : the color of the shape
            - colorTwo       : the color of the sub shape
        """
                
        # variables
        self.check       = True
        self.name        = name
        self.colorOne    = colorOne
        self.colorTwo    = colorTwo
        
        # hidden variables
        self._parent     = None
        self._up         = None
        self._struct     = copy.copy(arParam.STRUCT)

        
        # properties variables
        self.bonesTPL    = bones
        self.parent      = parent
        self.up          = up
        self.grp         = self._struct['GRP']
        




    #             #
    #  BONES TPL  #
    #             #
    
    @property
    def bonesTPL(self):
        return self._struct['TPL']['main']

    @bonesTPL.setter
    def bonesTPL(self, bones):
        """check if the bones that we receive are available"""
        
        # create the dictionary
        self._struct['TPL']['main'] = []
        
        # create a list is we got only one element
        if (isinstance(bones, list))==False:
            bones = [bones]
            

        for i in range(len(bones)):
            # check object
            tmp = various.checkObj(bones[i], type=['joint'])
            
            if tmp!=None:
                self._struct['TPL']['main'].append(tmp)
            else:
                vp.vPrint('template does\'nt exist %s, skip' % (bones[i]), 1)
                self.check = False
                
        # rename properly the template
        self.renameTemplate()
        
    @bonesTPL.deleter
    def bonesTPL(self):
        self._struct['TPL']['main'] = []
    
    
    
    
    
    
    #            #
    #   PARENT   #
    #            #
    
    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        # parent object if given
        if parent:
            self._parent = various.checkObj(parent, type=['transform', 'joint'])
            if self._parent==None:
                self.check = False
            
    @parent.deleter
    def parent(self):
        self._parent = None




        
    #            #
    #     UP     #
    #            #
    
    @property
    def up(self):
        return self._up
    
    @up.setter
    def up(self, up):
        
        # if the given variable seems to be a vector
        if (isinstance(up, dt.Vector))==True:
            self._up = up
            return
        
        if (isinstance(up, list))==True:
            try :
                self._up = dt.Vector(up)
            except:
                vp.vPrint('%s is not a vector' % up, 1)
                self.check = False
            return
        
        
        # if the given variable seems to be an object
        if (isinstance(up, str))==True:
            up = various.checkObj(up, type=['joint'])
            if up==None:
                self.check = False
                return
            else:
                # rename properly
                if various.renameObject(up, prefix=arParam.TPL_NAME_JNT)==False:
                    self.check = False
                    return
                
        # create vector according to object up
        if up:
            if len(self._struct['TPL']['main']):
                self._up = (up.getTranslation(space='world') - self._struct['TPL']['main'][0].getTranslation(space='world'))
                self._up.normalize()

    @up.deleter
    def up(self):
        self._up = None

    
    
    
    
    #                #
    #  RENAME TOOLS  #
    #                #
    
    def renameTemplate(self):
        # rename template if badly done
        for i in range(len(self._struct['TPL']['main'])):
            # rename properly
            if not various.renameObject(self._struct['TPL']['main'][i], prefix=arParam.TPL_NAME_JNT):
                self.check = False





    #           #
    #   BUILD   #
    #           #


    @arParam.completion()
    def build(self, hierarchy=None, framework=None):
        """build FK"""
        
        
        # create main group then parent it
        self.grp['main'] = pmc.createNode('transform', name=self.name+'_grp')
        if self.parent:
            self.grp['main'].setParent(self.parent)
        else:
            self.grp['main'].setParent(hierarchy['SCALEOFFSET'])
        
        
        # lock attribute from group
        clean.__lockHideTransform__(self.grp['main'], channel=['t', 'r', 's'])
        
        
        # create bones
        self._struct['RIG'] = {'main':[], 'off':[]}
        self._struct['2SK'] = []
        for i in range(len(self._struct['TPL']['main'])):
            
            # create joint
            self._struct['RIG']['main'].append( pmc.createNode('joint', name=self._struct['TPL']['main'][i].replace(arParam.TPL_NAME_JNT, '') ) )
            if i < (len(self._struct['TPL']['main'])-1):
                self._struct['RIG']['main'][i].setTransformation( rig.matrix.vecToMat( dir=(self._struct['TPL']['main'][i+1].getTranslation(space='world') - self._struct['TPL']['main'][i].getTranslation(space='world')), up=self.up, pos=self._struct['TPL']['main'][i].getTranslation(space='world'), order='xyz' ) )
            else:
                self._struct['RIG']['main'][i].setTransformation( rig.matrix.vecToMat( dir=(self._struct['TPL']['main'][i].getTranslation(space='world') - self._struct['TPL']['main'][i-1].getTranslation(space='world')), up=self.up, pos=self._struct['TPL']['main'][i].getTranslation(space='world'), order='xyz' ) )

            rig.bone.__rotateToOrient__(self._struct['RIG']['main'][i])
            
            # set parent 
            if i:
                self._struct['RIG']['main'][i].setParent( self._struct['RIG']['main'][i-1] )
            else:
                self._struct['RIG']['main'][i].setParent( self.grp['main'] )
            
            
            # add shape to joint
            tmp = None
            if i==0:
                tmp = arShapeBiblio.cubeCircle(name=self._struct['RIG']['main'][i], color=self.colorOne)
            elif i < (len(self._struct['TPL']['main'])-1):
                    tmp = arShapeBiblio.cube(name=self._struct['RIG']['main'][i], color=self.colorOne)

            
            if tmp:    
                pmc.parent(tmp.getShape(), self._struct['RIG']['main'][i], shape=True, relative=True)
                pmc.delete(tmp)
                
                # scale shape
                arShape.scaleShape(self._struct['RIG']['main'][i].getShape(), self._struct['RIG']['main'][i], self._struct['TPL']['main'][i+1])
    
            # clean channel box
            self._struct['RIG']['main'][i].rotateOrder.setKeyable(True)
            clean.__lockHideTransform__(self._struct['RIG']['main'][i], channel=['v', 'radi'])
            
            # add xfm
            xfm.__xfm__(self._struct['RIG']['main'][i], type='joint')
            
            # add offset
            self._struct['RIG']['off'].append( arShapeBiblio.rhombusX(name=self._struct['RIG']['main'][i]+'_off', color=self.colorTwo, parent=self._struct['RIG']['main'][i]) )
            self._struct['2SK'].append( arBone.create2SK(self._struct['RIG']['main'][i].name(), self._struct['RIG']['off'][i]) )
        
        
        # create attribute
        attribut.addAttrSeparator(self._struct['RIG']['main'][0])
        pmc.addAttr(self._struct['RIG']['main'][0], longName='offsetVisible', attributeType='enum', enumName='No:Yes', keyable=False, hidden=False)
        self._struct['RIG']['main'][0].offsetVisible.showInChannelBox(True)
        
        for i in range(len(self._struct['RIG']['off'])):
            self._struct['RIG']['off'][i].visibility.setLocked(False)
            self._struct['RIG']['main'][0].offsetVisible >> self._struct['RIG']['off'][i].visibility
            self._struct['RIG']['off'][i].visibility.setLocked(True)
        
        
        # connect 2SKjnt together
        arBone.__connect2SK__(self._struct['2SK'])
        
        # pickwalk attribute
        arPickwalk.setPickWalk(self._struct['RIG']['main'], type='UD')
        arPickwalk.setPickWalk(self._struct['RIG']['off'], type='UD')
        
        alternate = []
        for i in range(len(self._struct['RIG']['main'])):
            alternate.append(self._struct['RIG']['main'][i])
            alternate.append(self._struct['RIG']['off'][i])
        arPickwalk.setPickWalk(alternate, type='LR')
        
        
        # create sets
        framework['CONTROLS'][self.name+'_ctrls'] = self._struct['RIG']['main'][:-1]
        framework['CONTROLS'][self.name+'_ctrls'+'|'+self.name+'Sub_ctrls'] = self._struct['RIG']['off']
        
        # END        
        return True
            
        
        

#exemple = fk(name='myJnt', bones=['joint1_TPLjnt', 'joint2_TPLjnt', 'joint3_TPLjnt', 'joint4_TPLjnt', 'joint5_TPLjnt'], up='joint6_TPLjnt')
#exemple.build()

