#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 06 dec 2011
#
#   hierarchy construction
#

import pymel.core as pmc
import clean.clean as clean


def createHierarchy():
    """hierarchy construction"""
    
    gp = {}
    
    # create groups
    grps = [['TEMPLATES'], ['BDD'], ['PERSO'], ['SKINSKEL'], ['ADDITIVERIG'], ['ANIMATION'], ['TODELETE'], ['SETUP','PERSO|'], ['SCALEOFFSET','PERSO|SETUP|'], ['NOXFORM','PERSO|SETUP|']]
    for grp in grps:
        
        # create the absolute path
        tmpName = '|'
        for i in reversed(range(len(grp))):
            tmpName += grp[i]
        
        # check if the object exist
        if pmc.objExists(tmpName):
            gp[grp[0]] = pmc.PyNode(tmpName)
        else:
            gp[grp[0]] = pmc.createNode('transform', name=grp[0], skipSelect=True)
            if len(grp)==2:
                gp[grp[0]].setParent(grp[1])
                clean.__lockHideTransform__(gp[grp[0]], channel=['v'])
    
    
    # uncheck inherits transform
    gp['BDD'].inheritsTransform.set(False)
    gp['NOXFORM'].inheritsTransform.set(False)
    
    
    # create scale offset attribut
    if gp['SCALEOFFSET'].hasAttr('scaleOffset')==False:
        pmc.addAttr(gp['SCALEOFFSET'], longName='scaleOffset', attributeType='float', defaultValue=1.0, keyable=True )
    
    # connect the scale offset attribut into the scale
    clean.__lockHideTransform__(gp['SCALEOFFSET'], channel=['s'], lock=False)
    if len(gp['SCALEOFFSET'].sx.inputs(plugs=True))==0:
        gp['SCALEOFFSET'].scaleOffset >> gp['SCALEOFFSET'].sx
    if len(gp['SCALEOFFSET'].sy.inputs(plugs=True))==0:
        gp['SCALEOFFSET'].scaleOffset >> gp['SCALEOFFSET'].sy
    if len(gp['SCALEOFFSET'].sz.inputs(plugs=True))==0:
        gp['SCALEOFFSET'].scaleOffset >> gp['SCALEOFFSET'].sz
    
    
    # hide and lock attribut
    for key in gp.keys():
        clean.__lockHideTransform__(gp[key], channel=['t', 'r', 's'])
    
    
    # create set
    pmc.select(clear=True)
    sets = ['CONTROLS']
    for set in sets:
        if pmc.objExists(set)==False:
            gp[set] = pmc.sets(name=set)
        else:
            gp[set] = pmc.nodetypes.ObjectSet('CONTROLS')
    
    return gp
