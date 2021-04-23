import os

import IECore
import IECoreScene

import Gaffer
import GafferDispatch
import GafferTest
import GafferDispatchTest
import GafferAppleseed
import GafferScene

import DemoGafferExtension

class TaskAlgoTest( GafferTest.TestCase ) :

	def _dispatch(self, node):

		dispatcher = GafferDispatch.LocalDispatcher()
		dispatcher["jobsDirectory"].setValue( os.path.join( self.temporaryDirectory(), "jobs" ) )
		dispatcher.dispatch( [node] )

	def testOneTaskWithFiles( self ):
		script = Gaffer.ScriptNode()
		script["writer"] = GafferDispatchTest.TextWriter()
		testFilePath = os.path.join( self.temporaryDirectory(), "test.####.txt" )
		script["writer"]["fileName"].setValue( testFilePath )

		self._dispatch(script["writer"])

		sourceFiles = DemoGafferExtension.TaskAlgo.locateSourceFiles( script["writer"]["task"] )
		self.assertTrue( sourceFiles )
		context = Gaffer.Context( script.context() )
		self.assertEqual( sourceFiles.get( script["writer"] ), [context.substitute( testFilePath )] )

	def testMultipleContexts( self ):
		script = Gaffer.ScriptNode()

		script["writer"] = GafferDispatchTest.TextWriter()
		script["writer"]["fileName"].setValue( os.path.join( self.temporaryDirectory(), "${place}.txt" ) )

		script["wedge"] = GafferDispatch.Wedge()
		script["wedge"]["preTasks"][0].setInput( script["writer"]["task"] )
		script["wedge"]["variable"].setValue( "place" )
		script["wedge"]["mode"].setValue( int( GafferDispatch.Wedge.Mode.StringList ) )
		script["wedge"]["strings"].setValue( IECore.StringVectorData( [ "london", "paris", "milan" ] ) )

		self._dispatch(script["wedge"])

		sourceFiles = DemoGafferExtension.TaskAlgo.locateSourceFiles( script["wedge"]["task"] )

		self.assertEqual(
			sourceFiles.get(script["writer"]),
			[
				os.path.join( self.temporaryDirectory(), "london.txt" ),
				os.path.join( self.temporaryDirectory(), "paris.txt" ),
				os.path.join( self.temporaryDirectory(), "milan.txt" ),
			]
		)

	def testMultipleUpstreamBranches( self ):
		script = Gaffer.ScriptNode()

		script["writer1"] = GafferDispatchTest.TextWriter()
		script["writer1"]["fileName"].setValue( os.path.join( self.temporaryDirectory(), "left.txt" ) )
		script["writer2"] = GafferDispatchTest.TextWriter()
		script["writer2"]["fileName"].setValue( os.path.join( self.temporaryDirectory(), "right.txt" ) )

		script["writer"] = GafferDispatchTest.TextWriter()
		script["writer"]["fileName"].setValue( os.path.join( self.temporaryDirectory(), "centre.txt" ) )
		script["writer"]["preTasks"][0].setInput( script["writer1"]["task"] )
		script["writer"]["preTasks"][1].setInput( script["writer2"]["task"] )

		self._dispatch(script["writer"])

		sourceFiles = DemoGafferExtension.TaskAlgo.locateSourceFiles( script["writer"]["task"] )

		self.assertEqual(
			sourceFiles.get(script["writer1"]),
			[
				os.path.join( self.temporaryDirectory(), "left.txt" ),
			]
		)
		self.assertEqual(
			sourceFiles.get(script["writer2"]),
			[
				os.path.join( self.temporaryDirectory(), "right.txt" ),
			]
		)

	def testContextBubbling( self ):
		script = Gaffer.ScriptNode()

		script["writer"] = GafferDispatchTest.TextWriter()
		script["writer"]["fileName"].setValue( os.path.join( self.temporaryDirectory(), "${place}.txt" ) )

		script["wedge"] = GafferDispatch.Wedge()
		script["wedge"]["preTasks"][0].setInput( script["writer"]["task"] )
		script["wedge"]["variable"].setValue( "place" )
		script["wedge"]["mode"].setValue( int( GafferDispatch.Wedge.Mode.StringList ) )
		script["wedge"]["strings"].setValue( IECore.StringVectorData( [ "london", "paris", "milan" ] ) )

		self._dispatch(script["wedge"])

		sourceFiles = DemoGafferExtension.TaskAlgo.locateSourceFiles( script["writer"]["task"] )

		self.assertEqual(
			sourceFiles.get(script["writer"]),
			[
				os.path.join( self.temporaryDirectory(), "london.txt" ),
				os.path.join( self.temporaryDirectory(), "paris.txt" ),
				os.path.join( self.temporaryDirectory(), "milan.txt" ),
			]
		)

	def testMultipleDownstreamContexts( self ):
		script = Gaffer.ScriptNode()

		script["writer"] = GafferDispatchTest.TextWriter()
		script["writer"]["fileName"].setValue( os.path.join( self.temporaryDirectory(), "${material}.txt" ) )

		script["wedge"] = GafferDispatch.Wedge()
		script["wedge"]["preTasks"][0].setInput( script["writer"]["task"] )
		script["wedge"]["variable"].setValue( "material" )
		script["wedge"]["mode"].setValue( int( GafferDispatch.Wedge.Mode.StringList ) )
		script["wedge"]["strings"].setValue( IECore.StringVectorData( [ "dyneema", "silnylon", "ripstop" ] ) )

		script["wedge2"] = GafferDispatch.Wedge()
		script["wedge2"]["preTasks"][0].setInput( script["writer"]["task"] )
		script["wedge2"]["variable"].setValue( "material" )
		script["wedge2"]["mode"].setValue( int( GafferDispatch.Wedge.Mode.StringList ) )
		script["wedge2"]["strings"].setValue( IECore.StringVectorData( [ "silpoly" ] ) )

		self._dispatch(script["wedge"])
		self._dispatch(script["wedge2"])

		sourceFiles = DemoGafferExtension.TaskAlgo.locateSourceFiles( script["writer"]["task"] )

		self.assertEqual(
			sourceFiles.get(script["writer"]),
			[
				os.path.join( self.temporaryDirectory(), "dyneema.txt" ),
				os.path.join( self.temporaryDirectory(), "silnylon.txt" ),
				os.path.join( self.temporaryDirectory(), "ripstop.txt" ),
				os.path.join( self.temporaryDirectory(), "silpoly.txt" ),
			]
		)
