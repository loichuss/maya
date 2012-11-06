#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 7 nov 2012
#
#   Global variable and definition for the autorig
#

import autorig.tools.hierarchy as arHierarchy




#              #
#   VARIABLE   #
#              #

RIG      = 'RIG'
TPL      = 'TPL'
TSK      = '2SK'
SKN      = 'SKN'
TPL_NAME = '_TPLjnt'
BONES    = {
            RIG:[],
            TPL:[],
            TSK:[],
            }



#              #
#  DEFINITION  #
#              #

def decorator(attempt):
    def wrapper(func):
        def wrapped(arg):
            # create hierarchy group
            hierarchy = arHierarchy.createHierarchy()

            result = func(arg, hierarchy)
            return result   
        return wrapped
    return wrapper


