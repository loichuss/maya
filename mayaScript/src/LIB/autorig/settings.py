#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 7 nov 2012
#
#   Global variable and definition for the autorig
#


import pymel.core as pmc
import common.vPrint as vp
import autorig.tools.hierarchy as arHierarchy


#              #
#   VARIABLE   #
#              #

TPL_NAME     = '_TPL'
TPL_NAME_JNT = TPL_NAME+'jnt'
TPL_NAME_PVT = '_PVT'

STRUCT = {
          'GRP':{},
          'RIG':{},
          'TPL':{},
          '2SK':[],
          }



#              #
#  DEFINITION  #
#              #

def completion():
    def wrapper(method):
        def wrapped(self, *args, **kwargs):
            
            # check if the module can be created
            if not self.check:
                vp.vPrint('missing or wrong data in module, skip building process', 1)
                return False
    
            # create hierarchy group
            kwargs['hierarchy'] = arHierarchy.createHierarchy()
            
            kwargs['framework'] = {
                     'CONTROLS': {},
                     'PICK':     {},
                     }
            #args.append(hierarchy, _work)
            result = method(self, *args, **kwargs)
            
            # unselect everything
            pmc.select(clear=True)


            if not result:
                return result
            

            #              #
            #  Create Set  #
            #              #
            
            
            # loop per set
            for elts in sorted(kwargs['framework']['CONTROLS'].keys()):
                
                if elts == '':
                    pmc.sets(kwargs['hierarchy']['CONTROLS'], addElement=kwargs['framework']['CONTROLS'][elts])
                else:
                    # create and fill the set
                    elt = elts.split('|')
                    set = pmc.sets(name=elt[-1])
                    pmc.sets(set, addElement=kwargs['framework']['CONTROLS'][elts])
                    
                    # parent the set
                    if len(elt)==1:
                        pmc.sets(kwargs['hierarchy']['CONTROLS'], addElement=set)
                    else:
                        pmc.sets(elt[-2], addElement=set)
            
            
            
            
            # unselect
            pmc.select(clear=True)
            
            
            return result   
        return wrapped
    return wrapper

