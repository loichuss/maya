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
import rig.xfm as xfm
import rig.attribut as attribut
import clean

import autorig.shape.biblio as arShapeBiblio
import autorig.shape as arShape
import autorig.bone as arBone
import autorig.tools.pickwalk as arPickwalk
from autorig.settings import *

import copy





class fk(object):
    def __init__(self, name, bones, parent=None, up=dt.Vector(0,1,0), colorOne=17, colorTwo=21):
        
        """
        Create an fk joints module
            - name           : the name for the module
            - bones          : a list of bone (could be a pymel object or a string)
            - parent         : the father of the module (could be a pymel object or a string)
            - up             : the up vector to have the proper orientation (could be an array or a dt.Vector class or a pymel object or a string)
            - colorOne       : the color of the shape
            - colorTwo       : the color of the sub shape
        """
                
        
        # use to see if each object given are joint type
        self.check       = True
        self.name        = name
        self.colorOne    = colorOne
        self.colorTwo    = colorTwo
        self._parent     = None
        self._up         = None
        self._bones      = copy.copy(BONES)

        
        # check bones parent and up
        self.bones       = bones
        self.parent      = parent
        self.up          = up
        
        
        # keep variable
        self.gp          = {}
        




    #             #
    #  BONES TPL  #
    #             #
    
    @property
    def bones(self):
        return self._bones[TPL]

    @bones.setter
    def bones(self, bones):
        """check if the bones that we receive are available"""
        
        # create the dictionary
        self._bones[TPL] = []
        
        # create a list is we got only one element
        if (isinstance(bones, list))==False:
            bones = [bones]
            

        for i in range(len(bones)):
            # check object
            tmp = various.checkObj(bones[i], type=['joint'])
            
            if tmp!=None:
                self._bones[TPL].append(tmp)
            else:
                vp.vPrint('template does\'nt exist %s, skip' % (bones[i]), 1)
                self.check = False
                
        # rename properly the template
        self.renameTemplate()
        
    @bones.deleter
    def bones(self):
        self._bones[TPL] = []
    
    
    
    
    
    
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
                if various.renameObject(up, prefix=TPL_NAME)==False:
                    self.check = False
                    return
                
        # create vector according to object up
        if up:
            if len(self._bones[TPL]):
                self._up = (up.getTranslation(space='world') - self._bones[TPL][0].getTranslation(space='world'))
                self._up.normalize()

    @up.deleter
    def up(self):
        self._up = None

    
    
    
    
    #                #
    #  RENAME TOOLS  #
    #                #
    
    def renameTemplate(self):
        # rename template if badly done
        for i in range(len(self._bones[TPL])):
            # rename properly
            if not various.renameObject(self._bones[TPL][i], prefix=TPL_NAME):
                self.check = False





    #           #
    #   BUILD   #
    #           #


    @decorator(True)
    def build(self, hierarchy):
        """build FK"""
        
        if not self.check:
            vp.vPrint('missing or wrong data in module, skip building process', 1)
            return False
        
        
        """
        Truc a cacher ou a locker trouver un system               : le faire petit a petit
        
        creation de la hierachy pour faire la selection rapide    : decorateur
        
        connection des bones 2sk ensemble                         
        
        rajout des shapes dans les sets                           : decorateur
        
        - creation d'un group parent
        """
        
        
        # create main group then parent it
        self.gp['main'] = pmc.createNode('transform', name=self.name+'_grp')
        if self.parent:
            self.gp['main'].setParent(self.parent)
        else:
            self.gp['main'].setParent(hierarchy['SCALEOFFSET'])
        
        
        # lock attribut from group
        clean.__lockHideTransform__(self.gp['main'], channel=['t', 'r', 's'])
        
        
        # create bones
        self._bones[RIG] = {'main':[], 'off':[]}
        self._bones[TSK] = []
        for i in range(len(self._bones[TPL])):
            
            # create joint
            self._bones[RIG]['main'].append( pmc.createNode('joint', name=self._bones[TPL][i].replace(TPL_NAME, '') ) )
            if i < (len(self._bones[TPL])-1):
                print 't', i
                self._bones[RIG]['main'][i].setTransformation( rig.matrix.vecToMat( dir=(self._bones[TPL][i+1].getTranslation(space='world') - self._bones[TPL][i].getTranslation(space='world')), up=self.up, pos=self._bones[TPL][i].getTranslation(space='world'), order='xyz' ) )
            else:
                self._bones[RIG]['main'][i].setTransformation( rig.matrix.vecToMat( dir=(self._bones[TPL][i].getTranslation(space='world') - self._bones[TPL][i-1].getTranslation(space='world')), up=self.up, pos=self._bones[TPL][i].getTranslation(space='world'), order='xyz' ) )

            rig.bone.__rotateToOrient__(self._bones[RIG]['main'][i])
            
            # set parent 
            if i:
                self._bones[RIG]['main'][i].setParent( self._bones[RIG]['main'][i-1] )
            else:
                self._bones[RIG]['main'][i].setParent( self.gp['main'] )
            
            
            # add shape to joint
            tmp = None
            if i==0:
                tmp = arShapeBiblio.cubeCircle(name=self._bones[RIG]['main'][i], color=self.colorOne)
            elif i < (len(self._bones[TPL])-1):
                    print 'b', i
                    tmp = arShapeBiblio.cube(name=self._bones[RIG]['main'][i], color=self.colorOne)

            
            if tmp:    
                pmc.parent(tmp.getShape(), self._bones[RIG]['main'][i], shape=True, relative=True)
                pmc.delete(tmp)
                
                # scale shape
                arShape.scaleShape(self._bones[RIG]['main'][i].getShape(), self._bones[RIG]['main'][i], self._bones[TPL][i+1])
    
            # clean channel box
            self._bones[RIG]['main'][i].rotateOrder.setKeyable(True)
            clean.__lockHideTransform__(self._bones[RIG]['main'][i], channel=['v', 'radi'])
            
            # add xfm
            xfm.__xfm__(self._bones[RIG]['main'][i], type='joint')
            
            # add offset
            self._bones[RIG]['off'].append( arShapeBiblio.rhombusX(name=self._bones[RIG]['main'][i]+'_off', color=self.colorTwo, parent=self._bones[RIG]['main'][i]) )
            self._bones[TSK].append( arBone.create2SK(self._bones[RIG]['main'][i].name(), self._bones[RIG]['off'][i]) )
        
        
        # create attribut
        attribut.addAttrSeparator(self._bones[RIG]['main'][0])
        pmc.addAttr(self._bones[RIG]['main'][0], longName='offsetVisible', attributeType='enum', enumName='No:Yes', keyable=False, hidden=False)
        self._bones[RIG]['main'][0].offsetVisible.showInChannelBox(True)
        
        for i in range(len(self._bones[RIG]['off'])):
            self._bones[RIG]['off'][i].visibility.setLocked(False)
            self._bones[RIG]['main'][0].offsetVisible >> self._bones[RIG]['off'][i].visibility
            self._bones[RIG]['off'][i].visibility.setLocked(True)
        
        
        # connect 2SKjnt together
        arBone.__connect2SK__(self._bones[TSK])
        
        # pickwalk attribut
        arPickwalk.setPickWalk(self._bones[RIG]['main'], type='UD')
        arPickwalk.setPickWalk(self._bones[RIG]['off'], type='UD')
        
        alternate = []
        for i in range(len(self._bones[RIG]['main'])):
            alternate.append(self._bones[RIG]['main'][i])
            alternate.append(self._bones[RIG]['off'][i])
        arPickwalk.setPickWalk(alternate, type='LR')
        
        
        # add into CONTROLS sets
        pmc.select(clear=True)
        set = pmc.sets(name=self.name+'_ctrls')
        pmc.sets(set, addElement=self._bones[RIG]['main'])
        pmc.sets(hierarchy['CONTROLS'], addElement=set)
        
        setSub = pmc.sets(name=self.name+'Sub_ctrls')
        pmc.sets(setSub, addElement=self._bones[RIG]['off'])
        pmc.sets(set, addElement=setSub)
        
        
        # deselect
        pmc.select(clear=True)
        
            
        
        

toto = fk(name='myJnt', bones=['joint1_TPLjnt', 'joint2_TPLjnt', 'joint3_TPLjnt', 'joint4_TPLjnt', 'joint5_TPLjnt'], up='joint6_TPLjnt')
toto.build()
"""

#toto = fk(name='myJnt', bones=[pmc.PyNode('joint1_TPLjnt'), pmc.PyNode('joint2_TPLjnt'), pmc.PyNode('joint3_TPLjnt'), pmc.PyNode('joint4_TPLjnt')])

toto = fk(name='myJnt', bones=['joint1_TPLjnt'], parent='FLY2', upVect=[0,-1,0], autoHierarchy=True)

toto.build()
del toto
"""
