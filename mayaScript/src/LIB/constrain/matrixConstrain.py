#
#   Script create by Loic Huss
#   Version 1.0
#   Last Modification 28 oct 2011
#
#   Definition to create delete and reconnect constrain using matrix
#     master worldMatrix multiply by slave parentInvertMatrix
#


import pymel.core as pmc
import pymel.core.datatypes as dt
import common.vPrint as vp
import common.various as various
import clean


#                      #
#   MATRIX CONSTRAIN   #
#                      #

def matrixConstrain(master, slave, channel=[1,1,1,1], keepInfo=True, mo=False):
    """create a matrix constrain, channel (tr, ro, sc, sh)"""
    
    __checkMatrixConstrain__()
    
    # check and create pyNode variable
    master = various.checkObj(master, type=['transform', 'joint'])
    slave  = various.checkObj(slave,  type=['transform', 'joint'])

    # call the whole process function
    if master != None and slave != None:
        fine = createMatrixConstrain(master, slave, channel, keepInfo, mo, True)
        if fine:
            return True
        else:
            return False


def createMatrixConstrain(master, slave, channel, keepInfo, mo, calculateMo):
    # create constrain
    previousNode = __checkPreviousConnection__(slave)
    fine = __createMatrixConstrain__(master, slave, channel, mo, calculateMo)
    if fine:
        if keepInfo:
            __addInfo__(master, slave, channel, mo)
    else:
        return False
    __cleanPrevisouConnection__(previousNode)
    return True


def __checkMatrixConstrain__(setNameSpace=True):
    
    # check the version of maya
    # if the version of maya is 2013 the decomposeMatrix does no longer exist
    if pmc.versions.current() < 201300:
        # check if the plug in decompose matrix is load
        pmc.loadPlugin('decomposeMatrix', quiet=True)
    else:
        # check if the plug in decompose matrix is load
        pmc.loadPlugin('matrixNodes', quiet=True)

    # choose the right namespace
    if setNameSpace:
        pmc.namespace(set=':')


#                              #
#   PRIVATE CREATE CONSTRAIN   #
#                              #

def __createMatrixConstrain__(master, slave, channel, mo, calculateMo):

    # Mult node part
    inputIte = 0 # next input available in multMat.matrixIn
    # create multiply matrix node
    multMat = pmc.createNode('multMatrix', name=slave.name() + '_multMat', skipSelect=True)
    
    # if mo maintain offset is true
    if mo:
        if slave.hasAttr('cstOffMat')==False:
            pmc.addAttr(slave, longName = 'cstOffMat', dataType = 'matrix', hidden = False)
        if calculateMo:
            # variables to work with
            masterMat = dt.Matrix()
            slaveMat  = dt.Matrix()
            # get the matrix of each part
            masterMat = master.getMatrix(worldSpace=True)
            slaveMat  = slave.getMatrix(worldSpace=True)
            # inverting the master matrix to delete is information by multiplication
            masterMat = masterMat.inverse()
            offsetMat = slaveMat * masterMat
            # add matrix info into the matrix attribut
            slave.cstOffMat.set(offsetMat)
        # do the first connection
        slave.cstOffMat >> multMat.matrixIn[inputIte]
        inputIte=inputIte+1

    # connect multiply node    
    master.worldMatrix[0] >> multMat.matrixIn[inputIte]
    inputIte=inputIte+1
    slave.parentInverseMatrix[0] >> multMat.matrixIn[inputIte]
    
    
    # Deco node part
    
    # create decompose matrix node
    decoMat = pmc.createNode('decomposeMatrix', name=slave.name() + '_decoMat', skipSelect=True)
    
    # connect decompose node
    multMat.matrixSum >> decoMat.inputMatrix
    if channel[0]:
        decoMat.outputTranslate >> slave.translate
    if channel[1]:
        decoMat.outputRotate >> slave.rotate
    if channel[2]:
        decoMat.outputScale >> slave.scale
    if channel[3]:
        decoMat.outputShear >> slave.shear

    return True


#                             #
#   DELETE MATRIX CONSTRAIN   #
#                             #

def deleteMatrixConstrain(*args):
    """delete each matrix constrain system on one object"""
    for slaves in args:
        if isinstance(slaves, list):
            for slave in slaves:
                # check the obj
                slave = various.checkObj(slave, type=['transform', 'joint'])
                if slave != None:
                    __deleteMatrixConstrain__(slave)
        else:
            # check the obj
            slave = various.checkObj(slaves, type=['transform', 'joint'])
            if slave != None:
                __deleteMatrixConstrain__(slave)

        
def __deleteMatrixConstrain__(slave):
    # delete each attributs
    if slave.hasAttr('cstTgtName'):
        slave.cstTgtName.setLocked(False)
        slave.cstTgtName.delete()
    if slave.hasAttr('cstOptStr'):
        slave.cstOptStr.setLocked(False)
        slave.cstOptStr.delete()
    if slave.hasAttr('cstOffMat'):
        slave.cstOffMat.delete()
    
    # delete each connections
    previousNode = __checkPreviousConnection__(slave)
    for i in range(0, len(previousNode)):
        for j in range(0, len(previousNode[i])):
            clean.deleteAllConnections(previousNode[i][j])
    
    # delete each node
    for i in range(0, len(previousNode)):
        for j in range(0, len(previousNode[i])):
            if(previousNode[i][j]):
                pmc.delete(previousNode[i][j], hierarchy='none', all=False)




#                                #
#   RECONNECT MATRIX CONSTRAIN   #
#                                #

def reconnectMatrixConstrain(*args):
    """reconnect matrix constrain from attribut"""
    for slaves in args:
        if isinstance(slaves, list):
            for slave in slaves:
                # check the obj
                slave = various.checkObj(slave, type=['transform', 'joint'])
                if slave != None:
                    __reconnectMatrixConstrain__(slave)
        else:
            # check the obj
            slave = various.checkObj(slaves, type=['transform', 'joint'])
            if slave != None:
                __reconnectMatrixConstrain__(slave)



def reconnectAllMatrixConstrain():
    """reconnect each objects in scene with a matrix constrain attribut"""
    objs = pmc.ls('*.cstTgtName')
    for obj in objs:
        __reconnectMatrixConstrain__(obj.node())



def __reconnectMatrixConstrain__(slave):  
    # get the attribut from cstTgtName
    try:
        master = pmc.PyNode(slave.cstTgtName.get())
    except:
        vp.vPrint('from %s master object %s doesn\'t exist' % (slave, slave.cstTgtName.get()), 1)
        return None
    # get the channel attribut
    try:
        strChannel = slave.cstOptStr.get()
        channel    = [bool(s.split('=')[1]) for s in strChannel.split()]
    except:
        channel = [1,1,1,1]
    # check if a maintain offset matrix is set
    hasMo=False
    if slave.hasAttr('cstOffMat'):
        hasMo=True
    createMatrixConstrain(master, slave, channel, True, hasMo, False)




#                                       #
#   PRIVATE CHECK PREVIOUS CONNECTION   #
#                                       #

def __checkPreviousConnection__(slave):
    source      = []
    destination = []
    
    # get source
    nodes = slave.inputs(type='decomposeMatrix', exactType=True)
    # delete duplicata in array
    for node in nodes:
        if (node in source)==False:
            source.append(node)
    
    # get destination
    nodes = slave.outputs(type='multMatrix', exactType=True)
    # delete duplicata in array
    for node in nodes:
        if (node in destination)==False:
            destination.append(node)    

    return [source, destination]




#                                       #
#   PRIVATE CLEAN PREVIOUS CONNECTION   #
#                                       #

def __cleanPrevisouConnection__(previousNode):
    # source part meaning decoMat
    for i in range(0, len(previousNode[0])):
        tmp=pmc.listConnections(previousNode[0][i], source=False, destination=True, connections=False, plugs=False)
        if len(tmp)==0:
            if(previousNode[0][i]):
                pmc.delete(previousNode[0][i], hierarchy='none', all=False)




#                      #
#   PRIVATE ADD INFO   #
#                      #

def __addInfo__(master, slave, channel, mo):
    # create master name attribut
    if slave.hasAttr('cstTgtName') == False:
        pmc.addAttr(slave, longName = 'cstTgtName', dataType = 'string', hidden = False)
    attribut = slave.cstTgtName
    attribut.setLocked(False)
    attribut.set(master.name())
    attribut.setLocked(True)
    
    # create channel array attribut
    if channel != [1,1,1,1] or slave.hasAttr('cstOptStr'):
        if slave.hasAttr('cstOptStr') == False:
            pmc.addAttr(slave, longName = 'cstOptStr', dataType = 'string', hidden = False)
        attribut = slave.cstOptStr
        attribut.setLocked(False)
        # create a better information looking
        word = ['tr', 'ro', 'sc', 'sh']
        s    = ''
        for i in range(0, len(channel)):
            s=s + word[i] + '=' + str(channel[i]) + ' '
        attribut.set(s)
        attribut.setLocked(True)
    
    # delete previous mo info if no need anymore
    if mo==False and slave.hasAttr('cstOffMat'):
        slave.cstOffMat.delete()



#                 #
#   SNAP OBJECT   #
#                 #

def snapObject(master, slave, channel=[1,1,1,1]):
    """Create and delete Matri constrain to snap object"""
    __checkMatrixConstrain__(True)
    __createMatrixConstrain__(master, slave, channel, False, False)
    __deleteMatrixConstrain__(slave)



#                               #
#   MATRIX CONSTRAIN FROM SEL   #
#                               #

def matrixConstrainUI():
    sels = pmc.ls(sl=True)
    if(len(sels)>=2):
        if matrixConstrain(sels[0], sels[1]):
            vp.vPrint('matrix constrain done', 2)

def matrixConstrainOffsetUI():
    sels = pmc.ls(sl=True)
    if(len(sels)>=2):
        if matrixConstrain(sels[0], sels[1], mo=True):
            vp.vPrint('matrix constrain with offset done', 2)

def deleteMatrixConstrainUI():
    deleteMatrixConstrain(pmc.ls(sl=True))

def reconnectMatrixConstrainUI():
    reconnectMatrixConstrain(pmc.ls(sl=True))
    
def snapObjectUI():
    snapObject(pmc.ls(sl=True)[0], pmc.ls(sl=True)[1], channel=[1,1,1,1])
