import Gaffer
import GafferDispatch

## Locate all source files on disk that may be relevant to a given output TaskPlug
# Run post dispatch in a scene.
# Contexts for file path evaluation are gathered from all downstream branches.
# Source files are gathered from all upstream task nodes.
# Returns a dictionary where the key is a task node and the value is
# a list of its source files on disk
def locateSourceFiles( plug ):

	startNode = plug.node()

	isLeafTaskNode = lambda node : (
			node.isInstanceOf(GafferDispatch.TaskNode.staticTypeId())
			and not node["task"].outputs()
		)
	leaves = Gaffer.NodeAlgo.findAllDownstream( startNode, isLeafTaskNode )
	if not leaves:
		leaves = [ startNode ]

	# storing values for recursion
	sourceFileInfo = {}
	fileSwitch = False
	scriptNode = plug.node().scriptNode()

	for leafNode in leaves:
		_collectFiles(
			leafNode['task'],
			sourceFileInfo,
			scriptNode.context(),
			startNode,
			fileSwitch
		)

	return sourceFileInfo

## Recursively travels up a chain of Task Nodes, collecting any files that
# have been written.
def _collectFiles( plug, outInfo, context, startNode, fileSwitch ):
	taskNode = plug.node()
	# we start at the graph leaves but we only want to gather file paths
	# after the given plug node
	if taskNode == startNode:
		fileSwitch = True

	for pretask in taskNode.preTasks( context ):
		inputPlug = pretask.plug().getInput()
		if inputPlug:
			mergedContext = _mergeContext( context, pretask.context() )
			_collectFiles(
				inputPlug,
				outInfo,
				mergedContext,
				startNode,
				fileSwitch
			)

	files = _getFilesFromTask( taskNode, context )
	if fileSwitch and files:
		fileList = outInfo.get( taskNode, [] )
		fileList.append( files )
		outInfo[taskNode] = fileList

## Assuming that any task that is writing files has a fileName field
# return any files that are on disk for a given task and context
def _getFilesFromTask( taskNode, context ):
	if 'fileName' in taskNode.keys():
		pathStr = context.substitute( taskNode['fileName'].getValue() )
		filePath = Gaffer.FileSystemPath( pathStr )
		if filePath.isLeaf():
			return pathStr

	return None

## merge contexts, only adding new values from the new context
def _mergeContext( preContext, postContext ):
	newContext = Gaffer.Context( preContext )
	for name in postContext.names():
		value = newContext.get( name )
		if not value:
			newContext[name] = postContext.get( name )

	return newContext
