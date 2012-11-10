#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 7 nov 2012
#
#   Global variable and definition for the autorig
#


import pymel.core as pmc
import autorig.tools.hierarchy as arHierarchy



#              #
#   VARIABLE   #
#              #

TPL_NAME = '_TPLjnt'
BONES    = {
            'RIG':{},
            'TPL':[],
            '2SK':[],
            }



#              #
#  DEFINITION  #
#              #

def completion():
    def wrapper(func):
        def wrapped(arg):
            
            # create hierarchy group
            hierarchy = arHierarchy.createHierarchy()
            
            _work = {
                     'CONTROLS': {},
                     'PICK':     {},
                     }
            
            result = func(arg, hierarchy, _work)
            
            
            #              #
            #  Create Set  #
            #              #
            
            # unselect everything
            pmc.select(clear=True)
            
            # loop per set
            for elts in sorted(_work['CONTROLS']):
                
                # create and fill the set
                elt = elts.split('|')
                set = pmc.sets(name=elt[-1])
                pmc.sets(set, addElement=_work['CONTROLS'][elts])
                
                # parent the set
                if len(elt)==1:
                    pmc.sets(hierarchy['CONTROLS'], addElement=set)
                else:
                    pmc.sets(elt[-2], addElement=set)
                
            
            return result   
        return wrapped
    return wrapper


