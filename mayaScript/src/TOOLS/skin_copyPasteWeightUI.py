#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 09 nov 2011
#
#   copy and paste skin influence
#

import pymel.core as pmc
import maya.cmds as cmds
import maya.mel as mel
import common.vPrint as vp
import skin as skinTools
import skin.copyPasteWeight as cpw

reload(skinTools)
reload(cpw)
class copyPasteWeightUI():

    # variables
    ui         = {}
    uiSize     = [200, 600]
    _maxHist   = 5
    
    def __init__(self):
        self._copyPaste = []
        self._iteHist   = 0
        self.buildUI()
        self.__getBonesInfluence__()
    
    #             #
    #   MAIN UI   #
    #             #
    
    def buildUI(self):
        """create main UI"""
        # window creation
        windowName = 'copyPasteWeight'
        title      = 'Copy Paste Weight'
        
        if (pmc.window(windowName, exists=True)):
            pmc.deleteUI(windowName)
        
        self.ui['window']   = pmc.window(windowName, title=title, width=self.uiSize[0], height=self.uiSize[1], resizeToFitChildren=True, sizeable=False, retain=False )

        
        self.ui['layMain']  = pmc.columnLayout( width=self.uiSize[0], height=self.uiSize[1] )
        pmc.columnLayout( width=self.uiSize[0], height=20, enableBackground=True, backgroundColor=[0.1,0.1,0.1] )
        pmc.text( label='Copy and Paste Skin Weight Data', align='center', width=self.uiSize[0], height=20 )
        pmc.setParent( '..' )
        pmc.separator( height=10, style='none' )
        
        self.ui['layTop']   = pmc.rowLayout( numberOfColumns=2, columnWidth2=(self.uiSize[0]/2-2, self.uiSize[0]/2-2), height=30 )
        self.ui['btnCopy']  = pmc.button( label='Copy', annotation='Copy skin weight data from current selection', width=self.uiSize[0]/2-3 )
        self.ui['btnPaste'] = pmc.button( label='Paste', annotation='Paste skin weight into current selection', width=self.uiSize[0]/2-3 )
        pmc.setParent( '..' )
        
        self.ui['layBtm']   = pmc.rowLayout( numberOfColumns=2, columnWidth2=(self.uiSize[0]/2-2, self.uiSize[0]/2-2), height=30 )
        self.ui['btnMiss']  = pmc.button( label='Add Influences', annotation='Add influence if needed', width=self.uiSize[0]/2-3 )
        self.ui['btnNorm']  = pmc.button( label='Normalize', annotation='Normalize skin weight on current selection', width=self.uiSize[0]/2-3 )
        pmc.setParent( '..' )
        pmc.separator( height=10, style='none' )
        
        self.ui['layBtm']   = pmc.frameLayout( label='Options', borderVisible=True, collapsable=True, collapse=False, width=self.uiSize[0], marginHeight=10, marginWidth=20 )
        self.ui['layOpt']   = pmc.formLayout( numberOfDivisions=100 )
        self.ui['flfAdd']   = pmc.floatField( value=0.2, minValue=0.0, maxValue=1.0, precision=4, step=.01, width=self.uiSize[0]/4 )
        self.ui['chbAdd']   = pmc.checkBox( label='Add weight', value=False )
        self.ui['chbMiss']  = pmc.checkBox( label='Add Bones if needed', value=True )
        self.ui['chbBone']  = pmc.checkBox( label='Unchange locked joint', value=False )
        self.ui['chbMeth']  = pmc.checkBox( label='Fast \'No Undo possible\'', value=False )

        pmc.setParent( '..' )
        
        pmc.formLayout( self.ui['layOpt'], edit=True, attachForm=[(self.ui['chbAdd'], 'left', 0), (self.ui['chbAdd'], 'top', 2)])
        pmc.formLayout( self.ui['layOpt'], edit=True, attachForm=[(self.ui['flfAdd'], 'top', 0)], attachControl=[(self.ui['flfAdd'], 'left', 5, self.ui['chbAdd'])])
        pmc.formLayout( self.ui['layOpt'], edit=True, attachForm=[(self.ui['chbMiss'], 'left', 0)], attachControl=[(self.ui['chbMiss'], 'top', 5, self.ui['chbAdd'])])
        pmc.formLayout( self.ui['layOpt'], edit=True, attachForm=[(self.ui['chbBone'], 'left', 0)], attachControl=[(self.ui['chbBone'], 'top', 5, self.ui['chbMiss'])])
        pmc.formLayout( self.ui['layOpt'], edit=True, attachForm=[(self.ui['chbMeth'], 'left', 0)], attachControl=[(self.ui['chbMeth'], 'top', 5, self.ui['chbBone'])])
        
        pmc.setParent( '..' )
        
        pmc.frameLayout( label='History', borderVisible=True, collapsable=True, collapse=False, width=self.uiSize[0] )
        self.ui['tslHist']   = pmc.textScrollList( numberOfRows=self._maxHist, allowMultiSelection=False, showIndexedItem=2)
        pmc.popupMenu()
        pmc.menuItem( label='Print Influences', annotation='Print Influences', command=pmc.Callback( self.__printInfluences__ ) )
        pmc.menuItem( divider=True)
        pmc.menuItem( label='Delete History', annotation='Delete History', command=pmc.Callback( self.__deleteHistory__ ) )
        pmc.setParent( '..' )
        
        pmc.frameLayout( label='Bones List', borderVisible=True, collapsable=True, collapse=True, width=self.uiSize[0], marginHeight=0, marginWidth=0, expandCommand=pmc.Callback( self.__getBonesInfluence__) )
        pmc.columnLayout( width=self.uiSize[0]-3 )
        pmc.radioCollection()
        pmc.rowLayout( numberOfColumns=3, columnWidth3=(self.uiSize[0]/3-10, self.uiSize[0]/3-2, self.uiSize[0]/3-2), height=25 )
        pmc.text( label='Order', align='center', width=self.uiSize[0]/3-10, height=25 )
        self.ui['rb1Bone']  = pmc.radioButton( label='by Id', select=True, changeCommand=pmc.Callback( self.__getBonesInfluence__) )
        self.ui['rb2Bone']  = pmc.radioButton( label='by Alpha', changeCommand=pmc.Callback( self.__getBonesInfluence__) )
        pmc.setParent( '..' )
        self.ui['tslBone']  = pmc.textScrollList( numberOfRows=20, allowMultiSelection=True, showIndexedItem=2, width=self.uiSize[0]-3, doubleClickCommand=pmc.Callback( self.__actionBonesInfluence__, 2 ) )
        pmc.popupMenu()
        pmc.menuItem( label='Lock',   annotation='Lock Bones',   command=pmc.Callback( self.__actionBonesInfluence__, 0) )
        pmc.menuItem( label='Unlock', annotation='Unlock Bones', command=pmc.Callback( self.__actionBonesInfluence__, 1) )
        pmc.menuItem( label='Swap',   annotation='Swap Bones',   command=pmc.Callback( self.__actionBonesInfluence__, 2) )
        pmc.menuItem( divider=True)
        pmc.menuItem( label='Refresh list', annotation='Refresh list', command=pmc.Callback( self.__getBonesInfluence__) )
        self.ui['btnBone']  = pmc.button( label='Refresh list', annotation='Refresh list', width=self.uiSize[0]-3, command=pmc.Callback( self.__getBonesInfluence__) )
        pmc.setParent( '..' )
        pmc.setParent( '..' )

        pmc.frameLayout( label='Shortcuts', borderVisible=True, collapsable=True, collapse=True, width=self.uiSize[0], marginHeight=10, marginWidth=15 )
        self.ui['layShort']  = pmc.formLayout( numberOfDivisions=100 )
        self.ui['btnSCco']   = pmc.button( label='Copy', annotation='Create short cut for Copy weight button', width=self.uiSize[0]/4 )
        self.ui['chbCoCtrl'] = pmc.checkBox( label='Ctrl', value=True )
        self.ui['chbCoAlt']  = pmc.checkBox( label='Alt',  value=False )
        self.ui['txfCopy']   = pmc.textField( text='C', width=20)
        
        self.ui['btnSCpa']   = pmc.button( label='Paste', annotation='Create short cut for Paste weight button', width=self.uiSize[0]/4 )
        self.ui['chbPaCtrl'] = pmc.checkBox( label='Ctrl', value=True )
        self.ui['chbPaAlt']  = pmc.checkBox( label='Alt',  value=False )
        self.ui['txfPaste']  = pmc.textField( text='V', width=20)
        
        
        pmc.formLayout( self.ui['layShort'], edit=True, attachForm=[(self.ui['chbCoCtrl'], 'top', 3), (self.ui['chbCoCtrl'], 'left', 0)])
        pmc.formLayout( self.ui['layShort'], edit=True, attachForm=[(self.ui['chbCoAlt'], 'top', 3)],  attachControl=[(self.ui['chbCoAlt'], 'left', 3, self.ui['chbCoCtrl'])])
        pmc.formLayout( self.ui['layShort'], edit=True, attachForm=[(self.ui['txfCopy'], 'top', 1)],   attachControl=[(self.ui['txfCopy'], 'left', 6, self.ui['chbCoAlt'])])
        pmc.formLayout( self.ui['layShort'], edit=True, attachForm=[(self.ui['btnSCco'], 'top', 0)], attachPosition=[(self.ui['btnSCco'], 'right', 0, 100), (self.ui['btnSCco'], 'left', 0, 70)]  )
        
        pmc.formLayout( self.ui['layShort'], edit=True, attachForm=[(self.ui['chbPaCtrl'], 'left', 0)],  attachControl=[(self.ui['chbPaCtrl'], 'top', 5, self.ui['btnSCco'])])
        pmc.formLayout( self.ui['layShort'], edit=True, attachControl=[(self.ui['chbPaAlt'], 'left', 3, self.ui['chbPaCtrl']), (self.ui['chbPaAlt'], 'top', 5, self.ui['btnSCco'])])
        pmc.formLayout( self.ui['layShort'], edit=True, attachControl=[(self.ui['txfPaste'], 'left', 6, self.ui['chbPaAlt']), (self.ui['txfPaste'], 'top', 2, self.ui['btnSCco'])])
        pmc.formLayout( self.ui['layShort'], edit=True, attachControl=[(self.ui['btnSCpa'], 'top', 2, self.ui['btnSCco'])], attachPosition=[(self.ui['btnSCpa'], 'right', 0, 100), (self.ui['btnSCpa'], 'left', 0, 70)]  )
        
        
        pmc.setParent( '..' )
        pmc.setParent( '..' )
        
        # add command
        self.ui['btnCopy'].setCommand(pmc.Callback( self.__copyWeight__ ))
        self.ui['btnPaste'].setCommand(pmc.Callback( self.__pasteWeight__ ))
        self.ui['btnMiss'].setCommand(pmc.Callback( self.__addInfluences__ ))
        self.ui['btnNorm'].setCommand(pmc.Callback( self.__normalize__ ))
        self.ui['btnSCco'].setCommand(pmc.Callback( self.__createShortcut__, 'copy' ))
        self.ui['btnSCpa'].setCommand(pmc.Callback( self.__createShortcut__, 'paste' ))
        
        # show window
        self.ui['window'].show()
        
        
        
        
        
    #              #
    #   Bouttons   #
    #              #
    
    def __createShortcut__(self, function):
        if function=='copy':
            pmc.nameCommand( 'LH_copySkinWeight', annotation='copy weight data', command = 'python( "copyPasteWeightUIInst.__copyWeight__()" );')
            pmc.hotkey( keyShortcut=self.ui['txfCopy'].getText()[0], ctl=self.ui['chbCoCtrl'].getValue(), alt=self.ui['chbCoAlt'].getValue(), name='LH_copySkinWeight' )
            vp.vPrint('Copy hotkey is done', 2)
        
        elif function=='paste':
            pmc.nameCommand( 'LH_pasteSkinWeight', annotation='paste weight data', command = 'python( "copyPasteWeightUIInst.__pasteWeight__()" );')
            pmc.hotkey( keyShortcut=self.ui['txfPaste'].getText()[0], ctl=self.ui['chbPaCtrl'].getValue(), alt=self.ui['chbPaAlt'].getValue(), name='LH_pasteSkinWeight' )
            vp.vPrint('Paste hotkey is done', 2)
            
    
    def __copyWeight__(self):        
        try:
            copy   = cpw.copyPasteWeight()
            result = copy.copyWeight(self.__getVertex__())
        except:
            result = None
            
        if result:
            if copy.check():
                
                self._copyPaste.insert(0, copy)
                self.ui['tslHist'].appendPosition([1, 'Copy '+str(self._iteHist)])
                self.ui['tslHist'].setSelectIndexedItem(1)
                self._iteHist += 1
                # delete older history
                if len(self._copyPaste) > self._maxHist:
                    del self._copyPaste[-1]
                    self.ui['tslHist'].removeIndexedItem(self._maxHist+1)
            
        
    def __pasteWeight__(self):
        if len(self._copyPaste):
            if self.ui['chbMeth'].getValue():
                methode = 1
            else:
                methode = 0
            self._copyPaste[self.ui['tslHist'].getSelectIndexedItem()[0]-1].pasteWeight(pmc.ls(sl=True), methode=methode, keepBonesLocked=self.ui['chbBone'].getValue(), addMissInf=self.ui['chbMiss'].getValue(), copyPercent=self.ui['chbAdd'].getValue(), percent=self.ui['flfAdd'].getValue() )

        
    def __addInfluences__(self):
        if len(self._copyPaste):
            skinNode = self.__getSkinNode__()
            if skinNode:
                addBones = skinTools.findMissingInfluence(skinNode, self._copyPaste[self.ui['tslHist'].getSelectIndexedItem()[0]-1].getInfluence())
                if addBones:
                    skinTools.addInfluence(skinNode, addBones, skipSelect=True)
                    message = []
                    for a in addBones:
                        message.append(a.name())
                    vp.vPrint('Joint(s) add, %s' % ' '.join(message), 2)

    
    def __normalize__(self):
        skinNode = self.__getSkinNode__()
        if skinNode:
            skinTools.normalize(skinNode, pmc.ls(sl=True), keepBonesLocked=self.ui['chbBone'].getValue())
            
        
    def __getSkinNode__(self):
        # finding the skin cluster from selection
        skinNodes = pmc.ls(sl=True)[0].history(type='skinCluster')
        if len(skinNodes):
            return skinNodes[-1]
        else :
            vp.vPrint('No skinCluster node on %s' % pmc.ls(sl=True)[0], 1)
            return None
    
    
    
    #                #
    #   Historique   #
    #                #
    
    def __printInfluences__(self):
        if len(self.ui['tslHist'].getSelectIndexedItem()):
            self._copyPaste[self.ui['tslHist'].getSelectIndexedItem()[0]-1].printInfluences()
    
    def __deleteHistory__(self):
        self.ui['tslHist'].removeAll()
        self._copyPaste = []
        self._iteHist   = 0
    
    
    #                #
    #   Get Vertex   #
    #                #
    
    def __getVertex__(self):
        # Easy way to ge vertex list from current selection
        keep = pmc.ls(sl=True)
        cmds.ConvertSelectionToVertices()
        #cmds.hilite()
        #cmds.selectType( objectComponent=True, allComponents=False )
        #cmds.selectType( objectComponent=True, polymeshVertex=True )
        #mel.eval('PolySelectConvert 3;')
        v = pmc.ls(sl=True)
        pmc.select(keep)
        return v
    
    #                #
    #   Bones List   #
    #                #
    
    def __getBonesInfluence__(self):
        # get skinCluster from selection
        sels = pmc.ls(sl=True)
        skinNodes = None
        for sel in sels:
            skinNodes = sel.history(type='skinCluster')
        
        # if we get any
        if skinNodes:
            skinNode   = skinNodes[-1]
            influences = skinNode.influenceObjects()
            if self.ui['rb2Bone'].getSelect():
                influences.sort()
            list       = []
            # check if the bones is locked
            for i in range(len(influences)):
                if influences[i].liw.get():
                    item = '[X]  '
                else:
                    item = '[  ]  '
                item += influences[i].name()
                list.append(item)
            # add everything into the bones list
            self.ui['tslBone'].removeAll()
            self.ui['tslBone'].append(list)
        else:
            self.ui['tslBone'].removeAll()
    
    def __actionBonesInfluence__(self, action):
        # get info from selection
        itemSel = self.ui['tslBone'].getSelectIndexedItem()
        itemStr = self.ui['tslBone'].getSelectItem()
        # loop on each item selected
        for i in range(self.ui['tslBone'].getNumberOfSelectedItems()):
            # create PyNode variable
            bone = pmc.PyNode(itemStr[i].split(']')[1].strip())
            
            if action == 0: # locking bones
                item = '[X]  '+bone.name()
                bone.liw.set(1)
                
            elif action == 1: # unlocking bones
                item = '[  ]  '+bone.name()
                bone.liw.set(0)
                
            elif action == 2: # swaping statement
                if bone.liw.get():
                    item = '[  ]  '+bone.name()
                    bone.liw.set(0)
                else:
                    item = '[X]  '+bone.name()
                    bone.liw.set(1)
            
            # updating information
            self.ui['tslBone'].removeIndexedItem(itemSel[i])
            self.ui['tslBone'].appendPosition([itemSel[i], item])
            self.ui['tslBone'].setSelectIndexedItem(itemSel[i])

