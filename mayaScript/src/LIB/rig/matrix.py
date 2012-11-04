#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 21 nov 2011
#
#   Matrix definition
#

import pymel.core as pmc
import pymel.core.datatypes as dt


def vecToMat(dir=dt.Vector(1,0,0), up=dt.Vector(0,1,0), pos=dt.Vector(0,0,0), order='xyz'):
    # cross Product to get the ortho vector
    ortho  = up.cross(dir)
    ortho = dt.Vector(ortho[0]*-1.0, ortho[1]*-1.0, ortho[2]*-1.0 )
    
    # to get a perfect euclide systeme we do a second cross product wich change the Up vector
    newUp = ortho.cross(dir)
    if ( up.dot(newUp) < 0.0 ):
        # Reverse the vector
        newUp = dt.Vector(newUp[0]*-1.0, newUp[1]*-1.0, newUp[2]*-1.0 )
    up = newUp
    
    # normalize each composent
    dir.normalize()
    up.normalize()
    ortho.normalize()
    
    
    if order != 'xyz':
        mat = []
        for c in ['x', 'y', 'z']:
            if order.find(c) == 0:
                mat.append(dir)
            if order.find(c) == 1:
                mat.append(up)
            if order.find(c) == 2:
                mat.append(ortho)
        mat.append(pos)
    else:
        mat = [dir, up, ortho, pos]

    return dt.Matrix(mat)
