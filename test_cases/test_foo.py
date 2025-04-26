
import unittest

class Foo( unittest.TestCase ):

    def test_add( self ):
        print("Test add")
        self.assertTrue( 1+1, 2 )

if __name__ == '__main__':
    unittest.main()
