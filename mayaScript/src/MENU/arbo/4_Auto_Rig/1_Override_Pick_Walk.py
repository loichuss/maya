##ann=Override each pick walk to easily walk through the Rig
import tools.pickwalk as arPickWalk


pmc.nameCommand( 'LH_pickwalkUp', annotation='pick walk Up', command = 'python( "arPickWalk.pickWalkUp()" );')
pmc.hotkey( keyShortcut='Up', name='LH_pickwalkUp' )
vp.vPrint('override pick walk Up is done', 2)


pmc.nameCommand( 'LH_pickwalkDown', annotation='pick walk Down', command = 'python( "arPickWalk.pickWalkDown()" );')
pmc.hotkey( keyShortcut='Down', name='LH_pickwalkDown' )
vp.vPrint('override pick walk Down is done', 2)

pmc.nameCommand( 'LH_pickwalkLeft', annotation='pick walk Left', command = 'python( "arPickWalk.pickWalkLeft()" );')
pmc.hotkey( keyShortcut='Left', name='LH_pickwalkLeft' )
vp.vPrint('override pick walk Left is done', 2)

pmc.nameCommand( 'LH_pickwalkRight', annotation='pick walk Right', command = 'python( "arPickWalk.pickWalkRight()" );')
pmc.hotkey( keyShortcut='Right', name='LH_pickwalkRight' )
vp.vPrint('override pick walk Right is done', 2)
