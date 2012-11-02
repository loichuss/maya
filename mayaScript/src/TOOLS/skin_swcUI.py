#
#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 07 nov 2011
#
#   SaveLoadSkinUI
#


import pymel.core as pmc
import common.vPrint as vp
import common.various as various
import skin.swc as swc

reload(swc)

class swcUI():
    # variables
    mainUI = {}
    nameUI = {}
    boneUI = {}
    boneRenameUI = {}
    boneSearchUI = {}
    mainSize  = [200, 600]
    nameSize  = [200, 600]
    boneSize  = [400, 400]
    boneRenameSize  = [220, 50]
    boneSearchSize  = [300, 50]
    objSwc    = None
    
    def __init__(self):
        self.buildMainUI()
    
    
    
    #             #
    #   MAIN UI   #
    #             #
    
    def buildMainUI(self):
        """create main UI"""
        # window creation
        windowName = 'SkinSaveLoad'
        title      = 'Skin Save and Load'
        
        if (pmc.window(windowName, exists=True)):
            pmc.deleteUI(windowName)
        
        self.mainUI['window']   = pmc.window(windowName, title=title, width=self.mainSize[0], height=self.mainSize[1], resizeToFitChildren=False, sizeable=False, retain=True )

        self.mainUI['layMain']  = pmc.columnLayout( width=self.mainSize[0], height=self.mainSize[1] )
        self.mainUI['layInfo']  = pmc.columnLayout( width=self.mainSize[0], height=20, enableBackground=True, backgroundColor=[0.1,0.1,0.1] )
        self.mainUI['txtInfo']  = pmc.text( label='Save And Copy Skin Cluster Data', align='center', width=self.mainSize[0], height=20 )
        pmc.setParent( '..' )
        pmc.separator( height=10, style='none' )
        
        self.mainUI['layChoice'] = pmc.rowLayout( numberOfColumns=2, columnWidth2=(25, (self.mainSize[0])-25), height=30 )
        self.mainUI['btnChoice'] = pmc.button( label='>', annotation='Select an empty Group', width=20  )
        self.mainUI['txtChoice'] = pmc.textField( text='SWC_saveLoad_grp', editable=False, width=(self.mainSize[0])-40 )
        pmc.setParent( '..' )
        
        self.mainUI['layTop']   = pmc.rowLayout( numberOfColumns=2, columnWidth2=(self.mainSize[0]/2-2, self.mainSize[0]/2-2), height=40 )
        self.mainUI['btnSave']  = pmc.button( label='Save', annotation='Save SkinCluster Weight on object selected', width=self.mainSize[0]/2-3 )
        self.mainUI['btnLoad']  = pmc.button( label='Load', annotation='Load SkinCluster Weight on object selected', width=self.mainSize[0]/2-3 )
        pmc.setParent( '..' )
        pmc.rowLayout( numberOfColumns=2, columnWidth2=(self.mainSize[0]/2-5, self.mainSize[0]/2-5), annotation='Delete previous skin cluster if founded', height=20 )
        pmc.text( label='', align='center', width=self.nameSize[0]/2 )
        self.mainUI['chbSkin']  = pmc.checkBox( label='Del Skin', value=True, width=self.mainSize[0]/2-5 )
        pmc.setParent( '..' )
        pmc.separator( height=10, style='none' )
        
        self.mainUI['layBtm']     = pmc.frameLayout( label='SWC Tools', borderVisible=True, collapsable=True, collapse=False, width=self.mainSize[0], marginWidth=10 )
        pmc.separator( height=5, style='none' )
        self.mainUI['btnChange']  = pmc.button( label='Change SWC name ...',      annotation='To properly rename a SWC object', width=self.mainSize[0]-20 )
        self.mainUI['btnBone']    = pmc.button( label='Assign bones influences ...', annotation='To re attribut the influence of bones into others', width=self.mainSize[0]-20 )
        pmc.separator( height=5, style='none' )
        pmc.setParent( '..' )
        
        # add command
        self.mainUI['btnChoice'].setCommand(pmc.Callback( self.__selectGrp__ ))
        self.mainUI['btnSave'].setCommand(pmc.Callback( self.__callSWCSave__ ))
        self.mainUI['btnLoad'].setCommand(pmc.Callback( self.__callSWCLoad__ ))
        self.mainUI['btnChange'].setCommand(pmc.Callback( self.changeNameUI ))
        self.mainUI['btnBone'].setCommand(pmc.Callback( self.assignBonesUI ))
        
        # show window
        self.mainUI['window'].show()
    
    
    
    
    
    #                     #
    #   FOR MAIN UI DEF   #
    #                     #
    
    def __selectGrp__(self):
        """get the current selection as SWC group to work with"""
        obj = various.checkObj(pmc.ls(sl=True)[-1], type=['transform'])
        if obj != None:
            if len(obj.getShapes())==0:
                pmc.textField(self.mainUI['txtChoice'], edit=True, text=obj.name())
            else:
                vp.vPrint('%s is not an empty group' % obj, 1)
    
    def __callSWCSave__(self):
        """saving into new object the skin data"""
        swc.SWCsaveSkin(pmc.ls(sl=True), grpName=self.mainUI['txtChoice'].getText() )
        # if the bone reassign is open update it
        if (pmc.window('SkinSaveLoadBone', exists = True)):
            pmc.deleteUI('SkinSaveLoadBone')
        
    def __callSWCLoad__(self):
        """loading skin data from SWC object"""
        swc.SWCloadSkin(pmc.ls(sl=True), grpName=self.mainUI['txtChoice'].getText(), delSkin=self.mainUI['chbSkin'].getValue() )
    
    
    
    
    #             #
    #   NAME UI   #
    #             #
    
    def changeNameUI(self):
        """create UI to easily change the name of SWC object"""
        # window creation
        windowName = 'SkinSaveLoadName'
        title      = 'Change SWC Name'
        
        # finding if any objSWC was already selected by user
        self.__selectSwc__('')
        if self.objSwc == None:
            txtChoice  = '...'
        else:
            txtChoice  = self.objSwc.split('|')[-1]
        
        # creating the window
        if (pmc.window(windowName, exists = True)):
            pmc.deleteUI(windowName)
        
        self.nameUI['window']    = pmc.window(windowName, title = title, width=self.nameSize[0], height=self.nameSize[1], resizeToFitChildren=False, sizeable=False, retain=True )

        self.nameUI['layMain']   = pmc.columnLayout( width=self.nameSize[0], height=self.nameSize[1] )
        self.nameUI['layInfo']   = pmc.columnLayout( width=self.nameSize[0], height=20, enableBackground=True, backgroundColor=[0.1,0.1,0.1] )
        self.nameUI['txtInfo']   = pmc.text( label='Rename SWC Object', align='center', width=self.nameSize[0], height=20 )
        pmc.setParent( '..' )
        pmc.separator( height=10, style='none' )
        
        self.nameUI['layChoice'] = pmc.rowLayout( numberOfColumns=2, columnWidth2=(25, (self.nameSize[0])-25), height=30 )
        self.nameUI['btnChoice'] = pmc.button( label='>', annotation='Select a SWC object', width=20  )
        self.nameUI['txtChoice'] = pmc.textField( text=txtChoice, editable=False, width=(self.nameSize[0])-40 )
        pmc.setParent( '..' )
        pmc.separator( height=10, style='none' )
        
        self.nameUI['btnRename'] = pmc.button( label='Rename SWC', annotation='From current selection', width=self.nameSize[0], height=25 )
        
        # add command
        self.nameUI['btnChoice'].setCommand(pmc.Callback( self.__selectSwc__, 'name' ))
        self.nameUI['btnRename'].setCommand(pmc.Callback( self.__renameSwc__ ))
        
        # show window
        self.nameUI['window'].show()
    




    #                     #
    #   FOR NAME UI DEF   #
    #                     #    
    
    def __selectSwc__(self, keyUI):
        """get the current selection as SWC object to work with"""
        # get the selection
        obj = pmc.ls(sl=True)
        if len(obj) > 0:
            self.objSwc = various.checkObj(obj[-1], type=['transform'])
            if self.objSwc != None:
                # check if the selection is a SWC object
                if self.objSwc.hasAttr('def_jointName'):
                    if keyUI == 'name':
                        self.nameUI['txtChoice'].setText(self.objSwc.name().split('|')[-1])
                    elif keyUI == 'bone':
                        self.boneUI['txtChoice'].setText(self.objSwc.name().split('|')[-1])
                        self.__boneList__()
                else:
                    self.objSwc = None
                    vp.vPrint('%s, is not a SWC object' % self.objSwc, 1)
    
    
    def __renameSwc__(self):
        """rename the SWC object according to the current selection"""
        obj = various.checkObj(pmc.ls(sl=True)[-1], type=['transform'])
        swc.SWCrename(obj, self.objSwc)
        self.nameUI['txtChoice'].setText(self.objSwc.split('|')[-1])
    

    


    #              #
    #   BONES UI   #
    #              #
    
    def assignBonesUI(self):
        """create UI to reassign bones influences"""
        # window creation
        windowName = 'SkinSaveLoadBone'
        title      = 'Reassign Bones Influences'
        
        # finding if any objSWC was already selected by user
        self.__selectSwc__('')
        if self.objSwc == None:
            txtChoice  = '...'
        else:
            txtChoice  = self.objSwc.split('|')[-1]
        
        # creating the window
        if (pmc.window(windowName, exists = True)):
            pmc.deleteUI(windowName)
        
        self.boneUI['window']    = pmc.window(windowName, title = title, width=self.boneSize[0], height=self.boneSize[1], resizeToFitChildren=False, sizeable=True, retain=True )
        
        self.boneUI['layForm']   = pmc.formLayout(numberOfDivisions=100)
        self.boneUI['txtInfo']   = pmc.text( label='Reassign Bones Influences with Import Export', align='center', height=20, enableBackground=True, backgroundColor=[0.1,0.1,0.1] )
        
        self.boneUI['layChoice'] = pmc.rowLayout( numberOfColumns=2, height=30, columnOffset2=[5,5], adjustableColumn=2 )
        self.boneUI['btnChoice'] = pmc.button( label='>', annotation='Select a SWC object', width=20  )
        self.boneUI['txtChoice'] = pmc.textField( text=txtChoice, editable=False )
        pmc.setParent( '..' )
        
        self.boneUI['txtHelp01'] = pmc.text( label='Default Bones' )
        self.boneUI['txtHelp02'] = pmc.text( label='Reassign Bones' )
        self.boneUI['txtHelp03'] = pmc.text( label='Rename by' )
        
        self.boneUI['layScroll'] = pmc.scrollLayout( horizontalScrollBarThickness=16, verticalScrollBarThickness=16, childResizable=True, minChildWidth=10 )
        self.boneUI['layList']   = pmc.formLayout( numberOfDivisions=100, width=10 )
        self.boneUI['tslBoneL']  = pmc.textScrollList( numberOfRows=10, allowMultiSelection=True, showIndexedItem=4, enable=False)
        self.boneUI['tslBoneM']  = pmc.textScrollList( numberOfRows=10, allowMultiSelection=True, showIndexedItem=4, enable=False, width=20)
        self.boneUI['tslBoneR']  = pmc.textScrollList( numberOfRows=10, allowMultiSelection=True, showIndexedItem=4, selectIndexedItem=1 )
        pmc.popupMenu()
        pmc.menuItem( label='Selections',  annotation='Pick from selection',            command=pmc.Callback( self.__renameBySelection__ ) )
        pmc.menuItem( label='Research',    annotation='Search and replace',             command=pmc.Callback( self.__renameBySearchUI__ ) )
        pmc.menuItem( label='Renaming',    annotation='Rename manually',                command=pmc.Callback( self.__renameManuallyBoneUI__ ) )
        pmc.menuItem( label='Reset',       annotation='Reset name from items selected', command=pmc.Callback( self.__renameByReset__ ) )
        pmc.menuItem( divider=True)
        pmc.menuItem( label='Check Bones', annotation='Check if each Bones exists',     command=pmc.Callback( self.__checkBones__ ) )
        pmc.setParent( '..' )
        pmc.setParent( '..' )
        
        self.boneUI['layRename'] = pmc.columnLayout( )
        self.boneUI['btnReSel']  = pmc.button( label='Selections', annotation='Pick from selection', width=60 )
        self.boneUI['btnReSer']  = pmc.button( label='Research',   annotation='Search and replace', width=60 )
        self.boneUI['btnReMan']  = pmc.button( label='Renaming',   annotation='Rename manually', width=60 )
        pmc.separator( height=15, style='none' )
        self.boneUI['btnReRes']  = pmc.button( label='Reset',      annotation='Reset name from items selected', width=60 )
        pmc.setParent( '..' )
        
        self.boneUI['btnSave']   = pmc.button( label='Save',   annotation='Saving Data into SWC object' )
        self.boneUI['btnReset']  = pmc.button( label='Reset',  annotation='Reset from defaut Data' )
        self.boneUI['btnExport'] = pmc.button( label='Export', annotation='Export Data into file' )
        self.boneUI['btnImport'] = pmc.button( label='Import', annotation='Import Data from file')
        
        # form layout
        pmc.formLayout( self.boneUI['layForm'], edit=True, attachForm=[(self.boneUI['txtInfo'], 'top', 0), (self.boneUI['txtInfo'], 'left', 0), (self.boneUI['txtInfo'], 'right', 0)] )
        pmc.formLayout( self.boneUI['layForm'], edit=True, attachForm=[(self.boneUI['btnExport'], 'bottom', 5), (self.boneUI['btnExport'], 'left', 5)], attachPosition=[(self.boneUI['btnExport'], 'right', 2, 50)])
        pmc.formLayout( self.boneUI['layForm'], edit=True, attachForm=[(self.boneUI['btnImport'], 'bottom', 5), (self.boneUI['btnImport'], 'right', 5)], attachPosition=[(self.boneUI['btnImport'], 'left', 2, 50)])
        
        pmc.formLayout( self.boneUI['layForm'], edit=True, attachForm=[(self.boneUI['btnSave'], 'left',   5)], attachControl=[(self.boneUI['btnSave'], 'bottom', 5, self.boneUI['btnExport'])], attachPosition=[(self.boneUI['btnSave'], 'right', 2, 50)])
        pmc.formLayout( self.boneUI['layForm'], edit=True, attachForm=[(self.boneUI['btnReset'], 'right', 5)], attachControl=[(self.boneUI['btnReset'], 'bottom', 5, self.boneUI['btnImport'])], attachPosition=[(self.boneUI['btnReset'], 'left', 2, 50)])
        
        pmc.formLayout( self.boneUI['layForm'], edit=True, attachForm=[(self.boneUI['layChoice'], 'left', 5)], attachControl=[(self.boneUI['layChoice'], 'top', 5, self.boneUI['txtInfo'])], attachPosition=[(self.boneUI['layChoice'], 'right', 5, 100)])
        
        pmc.formLayout( self.boneUI['layForm'], edit=True, attachForm=[(self.boneUI['txtHelp01'], 'left', 7)], attachControl=[(self.boneUI['txtHelp01'], 'top', 5, self.boneUI['layChoice'])] )
        pmc.formLayout( self.boneUI['layForm'], edit=True, attachPosition=[(self.boneUI['txtHelp02'], 'left', 0, 48)], attachControl=[(self.boneUI['txtHelp02'], 'top', 5, self.boneUI['layChoice'])] )        
        pmc.formLayout( self.boneUI['layForm'], edit=True, attachForm=[(self.boneUI['txtHelp03'], 'right', 8)], attachControl=[(self.boneUI['txtHelp03'], 'top', 5, self.boneUI['layChoice'])] )
        
        pmc.formLayout( self.boneUI['layForm'], edit=True, attachForm=[(self.boneUI['layRename'], 'right', 5)], attachControl=[(self.boneUI['layRename'], 'top', 5, self.boneUI['txtHelp01'])] )
        pmc.formLayout( self.boneUI['layForm'], edit=True, attachForm=[(self.boneUI['layScroll'], 'left',  5)], attachControl=[(self.boneUI['layScroll'], 'top', 5, self.boneUI['txtHelp01']), (self.boneUI['layScroll'], 'bottom', 5, self.boneUI['btnSave']), (self.boneUI['layScroll'], 'right', 2, self.boneUI['layRename'])])
        
        pmc.formLayout( self.boneUI['layList'], edit=True, attachForm=[(self.boneUI['tslBoneL'], 'left',  2), (self.boneUI['tslBoneL'], 'top', 2), (self.boneUI['tslBoneL'], 'bottom', 2)], attachPosition=[(self.boneUI['tslBoneL'], 'right', 2, 47)])
        pmc.formLayout( self.boneUI['layList'], edit=True, attachForm=[(self.boneUI['tslBoneM'], 'top', 2),   (self.boneUI['tslBoneM'], 'bottom', 2)], attachControl=[(self.boneUI['tslBoneM'], 'left', 2, self.boneUI['tslBoneL'])] )
        pmc.formLayout( self.boneUI['layList'], edit=True, attachForm=[(self.boneUI['tslBoneR'], 'right', 2), (self.boneUI['tslBoneR'], 'top', 2), (self.boneUI['tslBoneR'], 'bottom', 2)], attachControl=[(self.boneUI['tslBoneR'], 'left', 24, self.boneUI['tslBoneL'])])
        
        
        
        
        
        #pmc.formLayout( form, edit=True, attachForm=[(b1, 'top', 5), (b1, 'left', 5), (b2, 'left', 5), (b2, 'bottom', 5), (b2, 'right', 5), (column, 'top', 5), (column, 'right', 5) ], attachControl=[(b1, 'bottom', 5, b2), (column, 'bottom', 5, b2)], attachPosition=[(b1, 'right', 5, 75), (column, 'left', 0, 75)], attachNone=(b2, 'top') )

        
        if self.objSwc != None:
            self.__boneList__()
        
        # add command
        self.boneUI['btnChoice'].setCommand(pmc.Callback( self.__selectSwc__, 'bone'  ))
        self.boneUI['btnReMan'].setCommand(pmc.Callback( self.__renameManuallyBoneUI__ ))
        self.boneUI['btnReSel'].setCommand(pmc.Callback( self.__renameBySelection__ ))
        self.boneUI['btnReSer'].setCommand(pmc.Callback( self.__renameBySearchUI__ ))
        self.boneUI['btnReRes'].setCommand(pmc.Callback( self.__renameByReset__ ))
        self.boneUI['btnSave'].setCommand(pmc.Callback( self.__assignBones__ ))
        self.boneUI['btnReset'].setCommand(pmc.Callback( self.__resetBones__ ))
        self.boneUI['btnExport'].setCommand(pmc.Callback( self.__exportBone__ ))
        self.boneUI['btnImport'].setCommand(pmc.Callback( self.__importBone__ ))
        self.boneUI['tslBoneR'].doubleClickCommand(pmc.Callback( self.__renameManuallyBoneUI__ ))
        
        #self.boneUI['tslBoneR'].selectCommand(pmc.Callback( self.__selectEachLit__ ))
        
        # show window
        self.boneUI['window'].show()


    
    

    #                     #
    #   FOR BONE UI DEF   #
    #                     #
    
    
    def __selectEachLit__(self):
        """not used definition, select each items in other text scroll list"""
        items = self.boneUI['tslBoneR'].getSelectIndexedItem()
        self.boneUI['tslBoneL'].deselectAll()
        self.boneUI['tslBoneL'].setSelectIndexedItem(items)
        self.boneUI['tslBoneM'].deselectAll()
        self.boneUI['tslBoneM'].setSelectIndexedItem(items)
    
    
    def __boneList__(self):
        """fill each text scroll list"""
        # getting data from objSwc
        bonesOld = self.objSwc.def_jointName.get()
        bonesNew = self.objSwc.def_corJointName.get()
        
        # remove previous items to refresh
        self.boneUI['tslBoneL'].removeAll()
        self.boneUI['tslBoneR'].removeAll()
        
        # fill the text scroll list
        self.boneUI['tslBoneL'].append(bonesOld)
        self.boneUI['tslBoneR'].append(bonesNew)
        #self.boneUI['tslBoneL'].setSelectIndexedItem(1)
        self.boneUI['tslBoneR'].setSelectIndexedItem(1)
        
        # middle part
        self.__checkBones__()
        #self.boneUI['tslBoneM'].setSelectIndexedItem(1)
        
        # properly resize the list
        self.boneUI['tslBoneL'].setNumberOfRows(len(bonesOld)+1)
        self.boneUI['tslBoneR'].setNumberOfRows(len(bonesNew)+1)


    def __checkBones__(self):
        """check if each bones exists in scene"""
        # fill the text scroll list
        bonesNew = self.boneUI['tslBoneR'].getAllItems()
        isOk = []
        # check each bones
        for i in range(0, len(bonesNew)):
            obj = various.checkObj(bonesNew[i], type=['joint'], echo=False)
            if obj == None:
                isOk.append('X')
            else:
                isOk.append('')
        # add the isOk array
        self.boneUI['tslBoneM'].removeAll()
        self.boneUI['tslBoneM'].append(isOk)
    
    
    def __checkBone__(self, item):
        """check if one bone exist in scene"""
        bonesNew = self.boneUI['tslBoneR'].getAllItems()
        obj = various.checkObj(bonesNew[item-1], type=['joint'], echo=False)
        if obj == None:
            name = 'X'
        else:
            name = ' '
        self.boneUI['tslBoneM'].removeIndexedItem(item)
        self.boneUI['tslBoneM'].appendPosition([item, name])
        
        
    def __renameManuallyBoneUI__(self):
        """create UI to rename one item"""
        # check if we have an object to work with
        if self.objSwc != None:
            # take the latest Item selected and select only this one
            boneIte  = self.boneUI['tslBoneR'].getSelectIndexedItem()
            if len(boneIte) > 1:
                self.boneUI['tslBoneR'].deselectAll()
                self.boneUI['tslBoneR'].setSelectIndexedItem(boneIte[-1])
            boneName = self.boneUI['tslBoneR'].getSelectItem()[-1]
            
            # window creation
            windowName = 'SkinSaveLoadBoneRename'
            title      = 'New Name'
            
            # creating the window
            if (pmc.window(windowName, exists = True)):
                pmc.deleteUI(windowName)
            
            self.boneRenameUI['window']    = pmc.window(windowName, title = title, width=self.boneRenameSize[0], height=self.boneRenameSize[1], resizeToFitChildren=False, sizeable=False )
            self.boneRenameUI['layMain']   = pmc.columnLayout( width=self.boneRenameSize[0], height=self.boneRenameSize[1] )
            self.boneRenameUI['layChoice'] = pmc.rowLayout( numberOfColumns=2, columnWidth2=((self.boneRenameSize[0])-40, 40), height=self.boneRenameSize[1] )
            self.boneRenameUI['txtChoice'] = pmc.textField( text=boneName, editable=True, width=(self.boneRenameSize[0])-45 )
            self.boneRenameUI['btnChoice'] = pmc.button( label='ok', annotation='Press it to rename the bones', width=37  )
            
            # add command
            self.boneRenameUI['btnChoice'].setCommand(pmc.Callback( self.__renameManuallyBone__, boneIte[-1] ))

            # show window
            self.boneRenameUI['window'].show()
            
            # replace properly the window at the middle of the father window
            self.boneRenameUI['window'].setTopLeftCorner([self.boneUI['window'].getTopEdge()+self.boneUI['window'].getHeight()/2-self.boneRenameSize[1]/2, self.boneUI['window'].getLeftEdge()+self.boneUI['window'].getWidth()/2-self.boneRenameSize[0]/2])
    
    def __renameManuallyBone__(self, item):
        """rename item manually"""
        # changing name
        self.__renameBone__(self.boneRenameUI['txtChoice'].getText(), item)
        # closing the window no more need
        pmc.deleteUI(self.boneRenameUI['window'])
        
        
    def __renameBySelection__(self):
        """rename item by current selection"""
        # get each items selected
        items = self.boneUI['tslBoneR'].getSelectIndexedItem()
        
        # and each object in scene selected
        objs = pmc.ls(sl=True)
        for i in range(0, len(items)):
            if i >= len(objs):
                j = len(objs)-1
            else:
                j = i
            obj = various.checkObj(objs[j], type=['joint'])
            if obj != None:
                self.__renameBone__(obj.name(), items[i])
    
    
    def __renameBySearchUI__(self):
        """create UI to rename by search and replace methode"""
        # check if we have an object to work with
        if self.objSwc != None:
            # get selected item
            boneName = self.boneUI['tslBoneR'].getSelectItem()[-1]
            
            # window creation
            windowName = 'SkinSaveLoadBoneSearch'
            title      = 'Search and Replace Name'
            
            # creating the window
            if (pmc.window(windowName, exists = True)):
                pmc.deleteUI(windowName)
            
            self.boneSearchUI['window']    = pmc.window(windowName, title = title, width=self.boneSearchSize[0], height=self.boneSearchSize[1], resizeToFitChildren=False, sizeable=False, retain=True )
            self.boneSearchUI['layMain']   = pmc.columnLayout( width=self.boneSearchSize[0], height=self.boneSearchSize[1] )
            self.boneSearchUI['layChoice'] = pmc.rowLayout( numberOfColumns=4, columnWidth4=((self.boneSearchSize[0])/2-45, 10, (self.boneSearchSize[0])/2-45, 25), height=self.boneSearchSize[1] )
            self.boneSearchUI['txtSearch'] = pmc.textField( text=boneName, editable=True, width=(self.boneSearchSize[0])/2-45 )
            pmc.text( label=' > ', width=10 )
            self.boneSearchUI['txtReplace']= pmc.textField( text='', editable=True, width=(self.boneSearchSize[0])/2-45 )
            self.boneSearchUI['btnChoice'] = pmc.button( label='ok', annotation='Press it to rename the bones', width=25  )
            
            # add command
            self.boneSearchUI['btnChoice'].setCommand(pmc.Callback( self.__renameBySearch__ ))
            
            # show window
            self.boneSearchUI['window'].show()
            
            # replace properly the window at the middle of the father window
            self.boneSearchUI['window'].setTopLeftCorner([self.boneUI['window'].getTopEdge()+self.boneUI['window'].getHeight()/2-self.boneSearchSize[1]/2, self.boneUI['window'].getLeftEdge()+self.boneUI['window'].getWidth()/2-self.boneSearchSize[0]/2])
    
    
    def __renameBySearch__(self):
        """rename item by search and replace methode"""
        # get each items selected
        items = self.boneUI['tslBoneR'].getSelectIndexedItem()
        
        # get text field info
        searchStr   = self.boneSearchUI['txtSearch'].getText()
        replaceStr  = self.boneSearchUI['txtReplace'].getText()
        allItemsStr = self.boneUI['tslBoneR'].getAllItems()
        for i in range(0, len(items)):
            self.__renameBone__(allItemsStr[items[i]-1].replace(searchStr, replaceStr), items[i])
        
        # closing the window no more need
        pmc.deleteUI(self.boneSearchUI['window'])
    
    
    def __renameByReset__(self):
        """rename item from the default name"""
        # get each items selected
        items = self.boneUI['tslBoneR'].getSelectIndexedItem()
        allItemsStr = self.boneUI['tslBoneL'].getAllItems()
        
        for i in range(0, len(items)):
            self.__renameBone__(allItemsStr[items[i]-1], items[i])
    
    
    def __renameBone__(self, name, item):
        """rename item"""
        # renaming the joint according to the new name
        self.boneUI['tslBoneR'].removeIndexedItem(item)
        self.boneUI['tslBoneR'].appendPosition([item, name])
        self.boneUI['tslBoneR'].setSelectIndexedItem(item)
        self.__checkBone__(item)
    
    
    def __exportBone__(self):
        """export into file current data"""
        # check if we have an object to work with
        if self.objSwc != None:
            # opening file dialog to choose a file
            basicFilter = "*.swc"
            path = pmc.fileDialog2(fileFilter=basicFilter, dialogStyle=2, caption='Export Bones Influences', okCaption='Export', fileMode=0)
            if (path):
                # get all items from both array
                itemsL = self.boneUI['tslBoneL'].getAllItems()
                itemsR = self.boneUI['tslBoneR'].getAllItems()
                
                # create and open the file
                f = open(str(path[0]), 'w')
                
                # writting in the file
                f.write('# SWC export for %s \n' % self.objSwc.name())
                for i in range(0, len(itemsL)):
                    f.write(str(itemsL[i]).replace('=', '_'))
                    f.write('=')
                    f.write(str(itemsR[i]).replace('=', '_'))
                    f.write('\n')
                
                # and then close the file
                f.close()
                vp.vPrint('Export Done, %s' % path[0], 2)
    
    
    def __importBone__(self):
        """import from file data"""
        # check if we have an object to work with
        if self.objSwc != None:
            # opening file dialog to choose a file
            basicFilter = "*.swc"
            path = pmc.fileDialog2(fileFilter=basicFilter, dialogStyle=2, caption='Import Bones Influences', okCaption='Import', fileMode=1)
            if (path):
                # get all items from both array
                itemsL = self.boneUI['tslBoneL'].getAllItems()
                itemsR = self.boneUI['tslBoneR'].getAllItems()
                
                # open the file
                f = open(str(path[0]), 'r')
                
                for line in f:
                    if line.count('#') == 0:
                        if line != '\n':
                            tmp = line.split('=')
                            if itemsL.count(tmp[0]) > 0:
                                index = itemsL.index(tmp[0])
                                self.__renameBone__(tmp[1].replace('\n', ''), index+1)
                    
                # and then close the file
                f.close()
    
    
    def __assignBones__(self):
        """saving data into SWC object by calling the SWCassignBones definition"""
        swc.SWCassignBones(self.objSwc, self.boneUI['tslBoneR'].getAllItems())
    
    
    def __resetBones__(self):
        """reset data from SWC object by calling the SWCresetData definition"""
        swc.__SWCresetData__(self.objSwc)
        self.__boneList__()
    

