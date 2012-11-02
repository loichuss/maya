import pymel.core as pmc

gVerb = 2


def vPrint(txt, verb=2, type=0):
    """global verbose print function
        # gVerb = 2 print each step
        # gVerb = 1 print problemes
        # gVerb = 0 print nothing
        # type = 0 print
        # type = 1 warning
        # type = 2 error
    """
    global gVerb
    if verb <= gVerb:
        
        # to properly distinguish probleme from everything else
        if verb == 1:
            start = '\t1# '
        else:
            start = '\t # '
        
        # and then print everything
        if type == 0:
            print start + txt
        elif type == 1:
            pmc.warning(start + txt)
        else:
            pmc.error(start + txt)



def inOut(func):
    def wrapper(*args, **kwargs):
        vPrint('Start %s' % func.__name__ , 2)
        result = func(*args, **kwargs)
        vPrint('End   %s' % func.__name__ , 2)
        return result
    return wrapper



"""class inOut(object):
    def __init__(self, f):
        self.f = f
    
    def __call__(self, _callable):
        def wrapper(*args, **kwargs):
            vp.vPrint('Start %s' % _callable.__name__ , 2)
            fReturn = _callable(*args, **kwargs)
            vp.vPrint('End   %s' % _callable.__name__ , 2)
            return fReturn
        return wrapper"""


