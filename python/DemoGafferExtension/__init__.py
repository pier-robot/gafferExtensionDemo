__import__( "Gaffer" )
__import__( "GafferScene" )

from ._DemoGafferExtension import *
from . import TaskAlgo

__import__( "IECore" ).loadConfig( "GAFFER_STARTUP_PATHS", subdirectory = "DemoGafferExtension" )
