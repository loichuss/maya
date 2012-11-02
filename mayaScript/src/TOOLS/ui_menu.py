#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 13 nov 2011
#
#   parsing folder to create menu
#

import pymel.core as pmc
import os
import common.vPrint as vp

class createMenuPath():


    def __init__(self, name, path):
        # variable
        self.UIelts = {}
        self.name   = str(name)
        
        # changing the slash
        if os.sep == '/':     # on linux
            path = path.replace('\\', os.sep)
        else:
            path = path.replace('/', os.sep)
        print path
        path = path.strip()
        
                
        # if the path works we continue
        if os.path.isdir(path):
            self.path        = path
            self.defaultPath = path
            self.createMenu()
        else:
            vp.vPrint('the folder doesn\'t exist %s' % path, 1)
    
    def delMenu(self):
        if(pmc.menu(self.name, exists=True)):
            pmc.deleteUI(self.name)
            vp.vPrint('Menu %s is deleted' % self.name, 2)
    
    
    def printPath(self):
        vp.vPrint('The current path is : %s' % self.path, 2)
        
        
    def setDefaultPath(self):
        self.path = self.defaultPath
        self.createMenu()
    
    def createMenu(self):
        # global variable from MEL to refere the main window
        mainWindow = pmc.melGlobals['$gMainWindow']
        
        # delete the menu if it already exist
        if(pmc.menu(self.name, exists=True)):
            pmc.deleteUI(self.name)
        
        # create menu
        self.UIelts['menu'] = pmc.menu(self.name, label=self.name, tearOff=True, parent=mainWindow )
        
        # parsing the folder to create the menu elements
        iteStart = self.path.count(os.sep)
        for root, dirs, files in os.walk(self.path, followlinks=False):
            # dirs part
            dirs.sort()
            self.__createMenuItem__(dirs, root, True, iteStart)
            # files part
            files.sort()
            self.__createMenuItem__(files, root, False, iteStart)
        self.__toolsMenu__()
    

    def __createMenuItem__(self, nodes, root, folder, iteStart):
        ite = root.count(os.sep)
        for node in nodes:
            if ite==iteStart:  # if we are in the root the parent for the item is the menu itself
                cParent = 'menu'
            else:
                allFolder  = root.split(os.sep)
                lastFolder = allFolder[len(allFolder)-1]
                cParent    = str(ite-iteStart-1)+lastFolder # to get the parent dico Key
            
            if folder:
                # check if the current folder has sub folder, if yes the menuItem will be a subMenu
                if len(os.listdir(root+os.sep+node))==0:
                    self.UIelts[str(ite-iteStart)+node] = pmc.menuItem( label=' '.join(node.split('_')[1:]), parent=self.UIelts[cParent] )
                else:
                    self.UIelts[str(ite-iteStart)+node] = pmc.menuItem( label=' '.join(node.split('_')[1:]), parent=self.UIelts[cParent], tearOff=True, subMenu=True )
            else:
                # opening the file to get annotation information and command
                fileOpen = open(root+os.sep+node, 'r')
                annot    = None
                comm     = None
                
                # loop on each line
                for line in fileOpen:
                    # deleting space before and after
                    line = line.strip()
                    if 'ann=' in line:
                        annot = line.split('ann=')[1].replace('\n', '')
                    if line.startswith('#')==False:
                        if comm:
                            comm += (line+'\n')
                        else:
                            comm = line
                fileOpen.close()
                
                # if we didn't find any annotation       
                if annot == None:
                    annot = 'No annotation found inside file'
                
                # creating item
                self.UIelts[str(ite-iteStart)+node] = pmc.menuItem( label=' '.join(node.split('_')[1:]).split('.')[0], parent=self.UIelts[cParent], annotation=annot, command=comm )
    


    def __toolsMenu__(self):
        pmc.menuItem( divider=True,                   parent=self.UIelts['menu'] )
        pmc.menuItem( label='print current path',     parent=self.UIelts['menu'], command=pmc.Callback( self.printPath ))
        pmc.menuItem( label='set new path',           parent=self.UIelts['menu'] )
        pmc.menuItem( label='reload',                 parent=self.UIelts['menu'], command=pmc.Callback( self.createMenu ))
        pmc.menuItem( label='reload from main path',  parent=self.UIelts['menu'], command=pmc.Callback( self.setDefaultPath ))
        pmc.menuItem( label='delete menu',            parent=self.UIelts['menu'], command=pmc.Callback( self.delMenu ))
        pmc.menuItem( divider=True,                   parent=self.UIelts['menu'] )
        # verbose part
        """self.UIelts['verbose'] = pmc.menuItem( label='set Verbosity', parent=self.UIelts['menu'], tearOff=True, subMenu=True )
        pmc.menuItem( label='0', parent=self.UIelts['verbose'], radioButton=True )
        pmc.menuItem( label='1', parent=self.UIelts['verbose'], radioButton=True )
        pmc.menuItem( label='2', parent=self.UIelts['verbose'], radioButton=True )"""

createMenuPath('LH_Tools', 'C:\Users\loic\workspace\mayaScript\src\MENU/arbo')


