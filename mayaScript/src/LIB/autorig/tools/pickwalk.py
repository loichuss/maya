#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 06 dec 2011
#
#   pickwalk definition
#


import pymel.core as pmc
import common.vPrint as vp

import common.various as various




#                       #
#   PICKWALK OVERRIDE   #
#                       #


def pickWalkDown():
    sels = pmc.ls(sl=True)
    pmc.select(clear=True)
    futurSel = []
    for sel in sels:
        if sel.hasAttr('pgDw') or sel.hasAttr('pgLt'):
            try:
                futurSel.append(sel.pgDw.outputs()[0])
            except:
                futurSel.append(sel)
        else:
            pmc.select(sel)
            futurSel.extend(pmc.pickWalk(d='down'))
    
    if futurSel:    
        pmc.select(futurSel, replace=True)


def pickWalkUp():
    sels = pmc.ls(sl=True)
    pmc.select(clear=True)
    futurSel = []
    for sel in sels:
        if sel.hasAttr('pgUp') or sel.hasAttr('pgLt'):
            try:
                futurSel.append(sel.pgUp.inputs()[0])
            except:
                futurSel.append(sel)
        else:
            pmc.select(sel)
            futurSel.extend(pmc.pickWalk(d='up'))
    
    if futurSel:    
        pmc.select(futurSel, replace=True)



def pickWalkLeft():
    sels = pmc.ls(sl=True)
    pmc.select(clear=True)
    futurSel = []
    for sel in sels:
        if sel.hasAttr('pgLt') or sel.hasAttr('pgUp'):
            try:
                futurSel.append(sel.pgLt.inputs()[0])
            except:
                futurSel.append(sel)
        else:
            pmc.select(sel)
            futurSel.extend(pmc.pickWalk(d='left'))
    
    if futurSel:    
        pmc.select(futurSel, replace=True)




def pickWalkRight():
    sels = pmc.ls(sl=True)
    pmc.select(clear=True)
    futurSel = []
    for sel in sels:
        if sel.hasAttr('pgRt') or sel.hasAttr('pgUp'):
            try:
                futurSel.append(sel.pgRt.outputs()[0])
            except:
                futurSel.append(sel)
        else:
            pmc.select(sel)
            futurSel.extend(pmc.pickWalk(d='right'))
    
    if futurSel:    
        pmc.select(futurSel, replace=True)







#                       #
#   PICKWALK ATTRIBUT   #
#                       #


def setPickWalk(*args, **kwargs):
    """From given object create system to overide maya pick walk"""
    # check kwargs
    if ('type' in kwargs.keys())==False:
        kwargs['type'] = 'UD'
    
    # getting each data
    objs = []
    for arg in args:
        if isinstance(arg, list):
            objs.extend(arg)
        else:
            objs.append(arg)
    
    # checking objs
    objsChecked = []
    for i in range(len(objs)):
        tmp = various.checkObj(objs[i], type=['transform', 'joint'])
        if tmp:
            objsChecked.append(tmp)
    
    # calling the private definition
    if len(objsChecked):
        __setPickWalk__(objsChecked, type=kwargs['type'])




def __setPickWalk__(objs, type='UD'):
    # add attributs
    if type == 'UD':
        attrFirst = 'pgDw'
        attrSecon = 'pgUp'
    elif type == 'LR':
        attrFirst = 'pgRt'
        attrSecon = 'pgLt'
    
    for i in range(len(objs)):
        if pmc.objExists(objs[i]+'.'+attrFirst)==False:
            pmc.addAttr(objs[i], longName=attrFirst, attributeType='bool', defaultValue=False, keyable=False)
        if pmc.objExists(objs[i]+'.'+attrSecon)==False:
            pmc.addAttr(objs[i], longName=attrSecon, attributeType='bool', defaultValue=False, keyable=False)
        
    
    # disconnect and unlock attributs    
    for i in range(len(objs)):
         # unloock attributs
        pmc.PyNode(objs[i]+'.'+attrFirst).setLocked(False)
        pmc.PyNode(objs[i]+'.'+attrSecon).setLocked(False)
        
    for i in range(len(objs)):
        # disconnect if any connection is present
        for attr in pmc.PyNode(objs[i]+'.'+attrFirst).connections(plugs=True):
            pmc.PyNode(objs[i]+'.'+attrFirst) // attr
    
        for attr in pmc.PyNode(objs[i]+'.'+attrSecon).connections(plugs=True):
            pmc.PyNode(objs[i]+'.'+attrSecon) // attr
        
        # reset value
        pmc.PyNode(objs[i]+'.'+attrFirst).set(False)
        pmc.PyNode(objs[i]+'.'+attrSecon).set(False)
    
    
    # connect attributs
    for i in range(len(objs)-1):
        pmc.PyNode(objs[i]+'.'+attrFirst) >> pmc.PyNode(objs[i+1]+'.'+attrSecon)
        pmc.PyNode(objs[i]+'.'+attrFirst).set(True)
    
    # lock attriibuts
    for i in range(len(objs)):
        pmc.PyNode(objs[i]+'.'+attrFirst).setLocked(True)
        pmc.PyNode(objs[i]+'.'+attrSecon).setLocked(True)






#                          #
#   PICKWALK OVERRIDE UI   #
#                          #

def overridePickWalkUI():
    pmc.nameCommand( 'LH_pickwalkUp', annotation='pick walk Up', command = 'python( "pickWalkUp()" );')
    pmc.hotkey( keyShortcut='Up', name='LH_pickwalkUp' )
    vp.vPrint('override pick walk Up is done', 2)
    
    
    pmc.nameCommand( 'LH_pickwalkDown', annotation='pick walk Down', command = 'python( "pickWalkDown()" );')
    pmc.hotkey( keyShortcut='Down', name='LH_pickwalkDown' )
    vp.vPrint('override pick walk Down is done', 2)
    
    pmc.nameCommand( 'LH_pickwalkLeft', annotation='pick walk Left', command = 'python( "pickWalkLeft()" );')
    pmc.hotkey( keyShortcut='Left', name='LH_pickwalkLeft' )
    vp.vPrint('override pick walk Left is done', 2)
    
    pmc.nameCommand( 'LH_pickwalkRight', annotation='pick walk Right', command = 'python( "pickWalkRight()" );')
    pmc.hotkey( keyShortcut='Right', name='LH_pickwalkRight' )
    vp.vPrint('override pick walk Right is done', 2)


