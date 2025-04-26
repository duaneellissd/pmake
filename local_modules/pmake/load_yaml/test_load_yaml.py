import unittest
import os
import sys
from pmake.load_yaml import load_yaml

test_files_dir = os.path.join(os.path.dirname( os.path.abspath(__file__)), "test_data" )

class YamlLoaderTest( unittest.TestCase ):
    def test_CleanLoad( self ):
        fn = os.path.join( test_files_dir, "no-error.yml" )
        data = load_yaml( fn )
        print("DATA")
        print( str(data))

    def test_TabError(self):
        fn =os.path.join( test_files_dir, "tab-error.yml" )
        data = None
        with self.assertRaises( SystemExit ):
            print("The error below is expected and is part of this test.")
            data = load_yaml( fn )
        print("data =  %s" % data )
    

