#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 15 dec 2011
#
#   Vector definition
#

import pymel.core.datatypes as dt
import math

def flat(vect):
    vectAbs = [math.fabs(vect[0]), math.fabs(vect[1]), math.fabs(vect[2])]
    composent = vectAbs.index(max(vectAbs))
    vectFlat = []
    for i in range(3):
        if i == composent:
            if vect[composent] < 0:
                vectFlat.append(-1)
            else:
                vectFlat.append(1)
        else:
            vectFlat.append(0)
    return dt.Vector(vectFlat)