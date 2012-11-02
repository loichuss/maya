#
#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 04 nov 2011
#
#   Different usefull definition about UI element
#

import pymel.core as pmc


class gaugeWindow():
    """UI Progress Class"""

    def __init__(self, title, status='', amount=0, maxAmount=100, type=1):
        # variables locales
        self.title       = title
        self.status      = status
        self._amount      = int(amount)
        self._maxAmount  = int(maxAmount)
        self._type       = int(type)
        self.ui          = {}
        
        # calling the create definition
        self.__create__()
    
    
    #             #
    #   SET GET   #
    #             #
    
    def getMaxAmount(self):
        return self._maxAmount
    
    def setMaxAmount(self, value):
        # chnage setting according to the new maxAmount
        if self._type == 1:
            self._maxAmount = value
            pmc.progressBar(self.gMainProgressBar, edit=True, maxValue=self._maxAmount)
        elif self._type == 2:
            self._maxAmount = value+1
            self.ui['pgb'].setMaxValue(self._maxAmount)
        
        if self._amount >= self._maxAmount:
            self.terminate()
    
    maxAmount = property(getMaxAmount, setMaxAmount)
        
    #        #
    #   UI   #
    #        #
    
    def __create__(self):
        # if type equal 1 we use the main Progress Bar
        if self._type == 1:
            self.gMainProgressBar = pmc.melGlobals['$gMainProgressBar']
            pmc.progressBar( self.gMainProgressBar, edit=True, beginProgress=True, isInterruptable=False, status=self.title, maxValue=self._maxAmount )
        
        # if type equal 2 we use a window
        elif self._type == 2:
            pmc.waitCursor( state=True )
            self._maxAmount += 1
            self.__createUI__()
            self.progress(1)
    
    def __createUI__(self):
        # window creation
        windowName = self.title.replace(' ', '')
        title      = self.title
        
        # delete if exist
        if (pmc.window(windowName, exists=True)):
            pmc.deleteUI(windowName)
        
        self.ui['win'] = pmc.window(windowName, title=title, resizeToFitChildren=False, sizeable=False, retain=False, topLeftCorner=[10,100] )
        pmc.columnLayout()
        self.ui['txt'] = pmc.text( label='  '+self.status, align='center', height=20 )
        self.ui['pgb'] = pmc.progressBar( maxValue=self._maxAmount, width=100 )
        pmc.separator( height=5, style='none' )
        
        # show window
        self.ui['win'].show()
    
    
    
    #             #
    #   ADVANCE   #
    #             #
    
    def progress(self, amount=1):
        """Advance the progress bar"""
        self._amount += int(amount)
        
        # if main progress bar
        if self._type == 1:
            pmc.progressBar(self.gMainProgressBar, edit=True, step=amount)

        # if window progress bar
        elif self._type == 2:
            if (pmc.window(self.ui['win'], exists=True)):
                self.ui['pgb'].step(amount)
        
        # terminate if amount is bigger than maxAmount
        if self._amount >= self._maxAmount:
            self.terminate()
    
    
    #               #
    #   TERMINATE   #
    #               #

    def terminate(self):
        """Terminate the progress bar"""
        
        # if main progress bar
        if self._type == 1:
            pmc.progressBar(self.gMainProgressBar, edit=True, endProgress=True)
        
        # if window progress bar
        elif self._type == 2:
            pmc.waitCursor( state=False )
            if (pmc.window(self.ui['win'], exists=True)):
                self.ui['pgb'].step(self._maxAmount)
                pmc.deleteUI(self.ui['win'])
