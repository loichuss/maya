#
#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 14 nov 2011
#
#   Decorateur for Undo and Repeat
#

import pymel.core as pmc


def undoable(func):
    def wrapper(*args, **kwargs):
        pmc.undoInfo(openChunk=True)
        try:
            result = func(*args, **kwargs)
        except:
            vp.vPrint('Error', 1)
        finally:
            pmc.undoInfo(closeChunk=True)
            return result
    return wrapper



class repeatable(object):
    def __init__(self, f):
        self.f = f
    
    def __call__(self, *args, **kwargs):
        fReturn   = None
        argString = ''
        if args:
            for arg in args:
                argString += str(arg)+', '
        if kwargs:
            for key, item in kwargs.iteritems():
                argString += str(key)+'='+str(item)+', '
        
        commandToRepeat = 'python("'+__name__+'.'+self.f.__name__+'('+argString+')")'
        
        fReturn = self.f(*args, **kwargs)
        try:
            pmc.repeatLast(addCommand=commandToRepeat, addCommandLabel=self.f.__name__)
        except:
            pass
        
        return fReturn

