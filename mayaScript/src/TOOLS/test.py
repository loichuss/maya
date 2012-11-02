import pymel.core as pmc
import os

def getTopNode(obj):
    parents = obj.getAllParents()

    for i in range(len(parents)-1, -1, -1):
        return parents[i]
    return obj



class tdTools_importingList(object):

    def __init__(self, filters=['.obj'], grp=None, nameSpace=None, verbose=True):
      
        # get variables
        self._files     = []
        self._filters   = filters
        self._nameSpace = nameSpace
        self.verbose    = verbose
        self._grp       = grp
      
        # check has filter
        if len(self._filters):
            self._hasFilter = True
        else:
            self._hasFilter = False
  
      

    #
    # Getter
    #
    @property
    def files(self):
        return self._files
      
    @property
    def filters(self):
        return self._filters

    @property
    def grp(self):
        if self._grp:
            return self._grp.name()
        else:
            return self._grp

    @property
    def nameSpace(self):
        return self._nameSpace
   

    #
    # Setter
    #
    @filters.setter
    def filters(self, value):
        # if none type is given
        if type(value).__name__ == 'NoneType':
            self._filters=[]
        else:
            # check if we got a list
            if type(value).__name__ != 'list':
                value = [value]
            self._filters=value
            
        # updating has filter
        if len(self._filters):
            self._hasFilter = True
        else:
            self._hasFilter = False
      
        # check list of file
        self.filterFiles()


    @grp.setter
    def grp(self, value):
        if type(value).__name__ == 'NoneType':
            self._grp = None
        elif type(value).__name__ == 'str':
            if pmc.objExists(value):
                self._grp = pmc.PyNode(value)
            else:
                if self.verbose:
                    print '\tERROR: Object doesnt exist'
        elif type(value).__name__ == 'Transform':
            self._grp = value
        else:
            if self.verbose:
                print '\tERROR: Object is not a transform'

   
    @nameSpace.setter
    def nameSpace(self, value):
        if pmc.namespace(exists=value):
            self._nameSpace = value
   

    #
    # Del
    #
    @filters.deleter
    def filters(self):
        del self._filters
  

  
  
    #
    # Files
    #
    def filterFiles(self):
        """check if each file are good, usefull if the filter change"""
        
        newFile = []
        if self._hasFilter:
            for i in range(len(self._files)):
                good = False
                for filt in self._filters:
                    if str(self._files[i]).endswith(filt):
                        good = True
                if good:
                    newFile.append(self._files[i])
                    #self._files.pop(0)
                else:
                    if self.verbose:
                        print '\tINFO: file deleted from list %s' % self._files[i]
                      
        self._files = newFile

  
    def addFile(self, f):
        """Adding a file into the list of files"""
       
        # nomalizing path
        f=os.path.normpath(f)
        
        if os.path.isfile(f):
        
            if self._hasFilter:
                good = False
                for filt in self._filters:
                    if f.endswith(filt):
                        good = True
                if not good:
                    if self.verbose:
                        print '\tERROR: file not according to the current filter %s' % f
                    return False
          
        
            if not f in self._files:
                self._files.append(f)
                if self.verbose:
                    print '\tINFO: file add %s' % f
                return True
   
    def delFile(self, f):
        """deleting one file"""
       
        if f in self._files:
            self._files.pop(self._files.index(f))
            if self.verbose:
                print '\tINFO: Delete from list %s Done' % f
       
    def delAllFiles(self):
        """deleting all files list at once"""
        self._files = []
        if self.verbose:
            print '\tINFO: Clear everything on list'
   
   
   
    #
    # Importing
    #
    def importFiles(self, i=-1):
        """Proceed the importation"""
       
        # check if user choose a group
        if self._grp:
            if pmc.objExists(self._grp.name()):
                hasGrp = True
        else:
            hasGrp = False
           
       
        # set namespace if need
        currentNamespace = pmc.namespaceInfo(currentNamespace=True)
        if self._nameSpace:
            pmc.namespace(set=self._nameSpace)
       
        # import each file
        if i>-1:
            fil = [self._files[i]]
        else:
            fil = self._files
           
        for f in fil:
            objs = pmc.importFile(f, groupReference=hasGrp, returnNewNodes=True)
           
            if objs:
                if self.verbose:
                    print '\tINFO: Import file %s Done' % f
            else:
                if self.verbose:
                    print '\tERROR: Could not import file %s' % f
                continue
                   
            if not self._grp:
                continue
           
            # parenting
            for child in objs[0].getChildren():
                child.setParent(self._grp)
           
            # delete main group
            pmc.delete(objs[0])
       
       
        # reset to previous namespace
        pmc.namespace(set=currentNamespace)
       
       





class tdTools_importingListUi(object):

    def __init__(self, uiName='importingFile', uiTitle='Importing File'):
  
        self.filtersList  = ['.obj']
        self.listFile     =  tdTools_importingList(filters=self.filtersList)
        self._createFilter()
       
        self.uiMain   = {}
        self.uiName   = uiName
        self.uiTitle  = uiTitle
       
        self.uiPref      = {}
        self.uiPrefName  = uiName+'Pref'
        self.uiPrefTitle = uiTitle+' Pref'
       
        self.rootNamespace = '(root)'
       
        self._buildMainUi()
  
  

    #
    # Namespace
    #
    def _updateNameSpaceList(self):
        """update namespace menu item"""
       
        # delete all items
        self._deleteNameSpaceList()
       

       
        # get current namespace
        current = pmc.namespaceInfo(currentNamespace=True)
       
        # get all namespace
        pmc.namespace(set=':')
        listNamespace = pmc.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        pmc.namespace(set=current)
       
       
        if current == ':':
            current = self.rootNamespace
       
        # add root namespace
        listNamespace.append(self.rootNamespace)

        # add menuItem
        i = 1
        for nameSpace in listNamespace:
            if nameSpace in ['UI', 'shared']:
                continue
            pmc.menuItem(label=nameSpace, parent=self.uiMain['namespaceOpM'])
           
            if nameSpace == current:
                self.uiMain['namespaceOpM'].setSelect(i)
            i=i+1

       
       
       
    def _deleteNameSpaceList(self):
        """delete each menu item from namespace list"""
        for item in pmc.optionMenu(self.uiMain['namespaceOpM'], query=True, itemListLong=True):
            pmc.deleteUI(item)
       
    
    def _selectNamespace(self):
        ite  = self.uiMain['namespaceOpM'].getSelect()
        item = pmc.optionMenu(self.uiMain['namespaceOpM'], query=True, itemListLong=True)[ite-1]
        nameSpace = pmc.menuItem(item, query=True, label=True)
       
        if nameSpace==self.rootNamespace:
            nameSpace = ':'
       
        self.listFile.nameSpace = nameSpace
       
    
    #
    # Group
    #
    def _selectGroup(self):
        sels = pmc.ls(sl=True)
       
        if not len(sels):
            self.listFile.grp = None
            self._updateGrp()
            return True
       
        for sel in sels:
            if sel.type()=='transform':
                self.listFile.grp = sel
                self._updateGrp()
                return True
        return False
       
       
    def _updateGrp(self):
        if self.listFile.grp:
            self.uiMain['choGrpBtn'].setLabel(self.listFile.grp)
        else:
            self.uiMain['choGrpBtn'].setLabel('World')
   
   
    #
    # File List
    #
    def _addFile(self, mode):
        """Add lists"""
        # open the file dialogue
        files = pmc.fileDialog2(caption='Add', fileMode=mode, dialogStyle=2, okCaption='Add', fileFilter=self.filters)
      
        if not files:
            return False
      
        # loop into each file or folder          
        for f in files:
            f=os.path.normpath(f)
            # if its a folder
            if os.path.isdir(f):
                for sub in os.listdir(f):
                    self.listFile.addFile(os.path.join(f, sub))
                  
            # if it's a file
            elif os.path.isfile(f):
                self.listFile.addFile(f)
          
        # update ui
        self._updateList()


    def _updateList(self):
        self.uiMain['fileScl'].removeAll()
      
        for f in self.listFile.files:
            self.uiMain['fileScl'].append(f)

    def _deleteItem(self):
        for ite in self.uiMain['fileScl'].getSelectItem():
            self.listFile.delFile(ite)
        self._updateList()
   
   
    def _deleteAllItem(self):
        self.listFile.delAllFiles()
        self._updateList()
   
   
   
    #
    # Importing
    #
    def _import(self):
        self.listFile.importFiles()
   
    def _importItem(self):
        for ite in self.uiMain['fileScl'].getSelectIndexedItem():
            self.listFile.importFiles(i=ite-1)
   
    #
    # Verbose UI
    #
    def _toggleVerbose(self):
        if pmc.menuItem(self.uiMain['verMei'], query=True, checkBox=True):
            self.listFile.verbose = True
        else:
            self.listFile.verbose = False
   
   
   
    #
    # Main UI
    #
    def _buildMainUi(self):
  
        # delete previous UI
        if pmc.window(self.uiName, exists=True):
            pmc.deleteUI(self.uiName, window=True)
     
     
        # create UI
        self.uiMain['win']          = pmc.window(self.uiName, title=self.uiTitle, menuBar=True, width=300, height=600)
        self.uiMain['optMen']       = pmc.menu(label='Options', tearOff=True)
        self.uiMain['verMei']       = pmc.menuItem(label='Verbosity', checkBox=True)
        self.uiMain['preMei']       = pmc.menuItem(label='Preferences')

       
        self.uiMain['mainLay']      = pmc.formLayout(numberOfDivisions=100)
        self.uiMain['titleTxt']     = pmc.text(label='Importing multiple File', backgroundColor=[0,0,0], enableBackground=True, height=20)
      
        self.uiMain['optLay']       = pmc.frameLayout(label='Options', borderStyle='in', collapse=False, collapsable=False, borderVisible=False)
        pmc.separator(style='none', height=2)
        pmc.rowLayout(numberOfColumns=2, columnWidth2=(80, 200))#,adjustableColumn=2)
        self.uiMain['grpTxt']       = pmc.text(label='Group')
        self.uiMain['choGrpBtn']    = pmc.button(label='World', width=200, height=20)
       
        pmc.setParent('..')
        pmc.rowLayout(numberOfColumns=2, columnWidth2=(80, 200))#,adjustableColumn=2)
        self.uiMain['namespaceTxt'] = pmc.text(label='Namespace')
        self.uiMain['namespaceOpM'] = pmc.optionMenu(width=200)
        #self.uiMain['namespaceTxf'] = pmc.textField(text=pmc.namespaceInfo(currentNamespace=True))
       
        pmc.setParent('..')
        pmc.separator(style='none', height=2)
        pmc.setParent('..')
       
        self.uiMain['fileLay']      = pmc.frameLayout(label='Files', borderStyle='in', collapse=False, collapsable=False)
        self.uiMain['fileScl']      = pmc.textScrollList(numberOfRows=8, allowMultiSelection=True)
       
        self.uiMain['popupMen']     = pmc.popupMenu(parent=self.uiMain['fileScl'])
        self.uiMain['addFileMei']   = pmc.menuItem(label='Add File',        parent=self.uiMain['popupMen'])
        self.uiMain['addFolderMei'] = pmc.menuItem(label='Add Folder',      parent=self.uiMain['popupMen'])
        pmc.menuItem(divider=True, parent=self.uiMain['popupMen'])
        self.uiMain['impMei']       = pmc.menuItem(label='Import Selected', parent=self.uiMain['popupMen'])
        self.uiMain['impAllMei']    = pmc.menuItem(label='Import All',      parent=self.uiMain['popupMen'])
        pmc.menuItem(divider=True, parent=self.uiMain['popupMen'])
        self.uiMain['delMei']       = pmc.menuItem(label='Delete Selected', parent=self.uiMain['popupMen'])
        self.uiMain['delAllMei']    = pmc.menuItem(label='Delete All',      parent=self.uiMain['popupMen'])
       

       
        pmc.setParent('..')
       
        self.uiMain['btnLay']       = pmc.formLayout(numberOfDivisions=100, height=70)
        self.uiMain['addFileBtn']   = pmc.button(label='Add File', height=33)
        self.uiMain['addFolderBtn'] = pmc.button(label='Add Folder', height=33)
        self.uiMain['importBtn']    = pmc.button(label='Import', height=33)
      
      
        # layout
        pmc.formLayout(self.uiMain['mainLay'], edit=True, attachPosition=[(self.uiMain['titleTxt'], 'left', 0, 0), (self.uiMain['titleTxt'], 'right', 0, 100)])
        pmc.formLayout(self.uiMain['mainLay'], edit=True, attachPosition=[(self.uiMain['optLay'], 'left', 0, 0), (self.uiMain['optLay'], 'right', 0, 100)], attachControl=[(self.uiMain['optLay'], 'top', 10, self.uiMain['titleTxt'])])
        pmc.formLayout(self.uiMain['mainLay'], edit=True, attachPosition=[(self.uiMain['fileLay'], 'left', 0, 0), (self.uiMain['fileLay'], 'right', 0, 100)], attachControl=[(self.uiMain['fileLay'], 'top', 10, self.uiMain['optLay']), (self.uiMain['fileLay'], 'bottom', 5, self.uiMain['btnLay'])])
       
       
        pmc.formLayout(self.uiMain['mainLay'], edit=True, attachPosition=[(self.uiMain['btnLay'],  'left', 5, 0),   (self.uiMain['btnLay'],   'right', 5, 100),  (self.uiMain['btnLay'], 'bottom', 2, 100)] )
       
        pmc.formLayout(self.uiMain['btnLay'],  edit=True, attachPosition=[(self.uiMain['importBtn'],    'left', 0, 0),   (self.uiMain['importBtn'],    'right', 0, 100),  (self.uiMain['importBtn'],    'bottom', 0, 100)] )
        pmc.formLayout(self.uiMain['btnLay'],  edit=True, attachPosition=[(self.uiMain['addFileBtn'],   'left', 0, 0),   (self.uiMain['addFileBtn'],   'right', 2, 50),   (self.uiMain['addFileBtn'],   'top', 0, 0)] )
        pmc.formLayout(self.uiMain['btnLay'],  edit=True, attachPosition=[(self.uiMain['addFolderBtn'], 'left', 2, 50),  (self.uiMain['addFolderBtn'], 'right', 0, 100),  (self.uiMain['addFolderBtn'], 'top', 0, 0)] )
      
       
        # add command
        self.uiMain['addFileBtn'].setCommand(pmc.Callback(self._addFile, 1))
        self.uiMain['addFolderBtn'].setCommand(pmc.Callback(self._addFile, 2))
        self.uiMain['importBtn'].setCommand(pmc.Callback(self._import))
        self.uiMain['choGrpBtn'].setCommand(pmc.Callback(self._selectGroup))
       
        #self.uiMain['addFileMei'].setCommand(pmc.Callback(self._addFile, 1))
        #self.uiMain['addFolderMei'].setCommand(pmc.Callback(self._addFile, 2))
        pmc.menuItem(self.uiMain['addFileMei'], edit=True, command=pmc.Callback(self._addFile, 1))
        pmc.menuItem(self.uiMain['addFolderMei'], edit=True, command=pmc.Callback(self._addFile, 2))
        pmc.menuItem(self.uiMain['delMei'], edit=True, command=pmc.Callback(self._deleteItem))
        pmc.menuItem(self.uiMain['delAllMei'], edit=True, command=pmc.Callback(self._deleteAllItem))
        pmc.menuItem(self.uiMain['verMei'], edit=True, command=pmc.Callback(self._toggleVerbose))
        pmc.menuItem(self.uiMain['preMei'], edit=True, command=pmc.Callback(self._buildPrefUi))
       
        pmc.menuItem(self.uiMain['impMei'], edit=True, command=pmc.Callback(self._importItem))
        pmc.menuItem(self.uiMain['impAllMei'], edit=True, command=pmc.Callback(self._import))
       
        pmc.textScrollList(self.uiMain['fileScl'], edit=True, doubleClickCommand=pmc.Callback(self._importItem))
       
        pmc.optionMenu(self.uiMain['namespaceOpM'], edit=True, changeCommand=pmc.Callback(self._selectNamespace))
       
       
        # show main ui
        pmc.showWindow(self.uiMain['win'])
       
       
        # update Ui
        self._updateNameSpaceList()
       
    
    
    
    
    #
    # Pref UI
    #
    
    def _deletePrefUi(self):
        # delete previous UI
        if pmc.window(self.uiPrefName, exists=True):
            pmc.deleteUI(self.uiPrefName, window=True)
        
        
    def _createFilter(self):
        self.filters = ''
        for i in range(len(self.filtersList)):
            self.filters += self.filtersList[i].replace('.', '').capitalize()+' (*'+self.filtersList[i]+')'
            if (i+1) < len(self.filtersList):
                self.filters += ';;'
        
    def _getNewFilter(self):
        
        self.filtersList = []
        
        if self.uiPref['objChb'].getValue():
            self.filtersList.append('.obj')
        if self.uiPref['maChb'].getValue():
            self.filtersList.append('.ma')
        if self.uiPref['mbChb'].getValue():
            self.filtersList.append('.mb')
        if self.uiPref['fbxChb'].getValue():
            self.filtersList.append('.fxb')
        
        
        self._createFilter()
        self.listFile.filters = self.filtersList
        self._updateList()
        self._deletePrefUi()
    
    
    def _buildPrefUi(self):
       
        # delete previous UI
        if pmc.window(self.uiPrefName, exists=True):
            pmc.deleteUI(self.uiPrefName, window=True)
     
     
        # create UI
        self.uiPref['win']          = pmc.window(self.uiPrefName, title=self.uiPrefTitle, menuBar=True, width=300, height=200, sizeable=False)

        self.uiPref['mainLay']      = pmc.columnLayout()
        self.uiPref['titleTxt']     = pmc.text(label='Preferences', backgroundColor=[0,0,0], enableBackground=True, height=20, width=200)
       
        self.uiPref['optLay']       = pmc.rowLayout(numberOfColumns=2, columnWidth2=(125, 75))
        self.uiPref['optTxt']       = pmc.text(label='Format filter')
       
        self.uiPref['chkLay']       = pmc.columnLayout()
        
        v=False
        if '.obj' in self.filtersList:
            v=True
        self.uiPref['objChb']       = pmc.checkBox(label='Obj', value=v)
        v=False
        if '.ma' in self.filtersList:
            v=True
        self.uiPref['maChb']        = pmc.checkBox(label='Ma', value=v)
        v=False
        if '.mb' in self.filtersList:
            v=True
        self.uiPref['mbChb']        = pmc.checkBox(label='Mb', value=v)
        v=False
        if '.fbx' in self.filtersList:
            v=True
        self.uiPref['fbxChb']       = pmc.checkBox(label='Fbx', value=v)
        
        pmc.setParent('..')
        pmc.setParent('..')
        
        pmc.rowLayout(numberOfColumns=2, columnWidth2=(100, 100))
        self.uiPref['cancelBtn'] = pmc.button(label='Cancel', height=30, width=95)
        self.uiPref['saveBtn']   = pmc.button(label='Save',   height=30, width=95)
        
        
        # command
        self.uiPref['cancelBtn'].setCommand(pmc.Callback(self._deletePrefUi))
        self.uiPref['saveBtn'].setCommand(pmc.Callback(self._getNewFilter))
        
        
        # show main ui
        pmc.showWindow(self.uiPref['win'])






tdTools_importingListUi()

