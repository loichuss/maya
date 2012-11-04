#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 22 nov 2011
#
#   Definition about attribut
#


import pymel.core as pmc
import common.various as various


def addAttrSeparator(obj, name='Options'):
    """Add separator into attribut """
    # checking obj
    obj = various.checkObj(obj)
    if obj:
        # finding the possible attribut named only with '_'
        ite = 0
        longName = '_'
        while (ite<100):
            if pmc.objExists( obj.name()+'.'+longName ):
                longName += '_'
            else:
                break
            ite += 1
        
        # create the attribut
        pmc.addAttr(obj, longName=longName, attributeType='enum', enumName=name, keyable=False, hidden=False)
        attr = pmc.PyNode(obj.name()+'.'+longName)
        attr.setLocked(True)
        attr.showInChannelBox(True)