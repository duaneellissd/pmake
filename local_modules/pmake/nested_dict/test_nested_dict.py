import sys
import unittest
import os

from pmake.nested_dict  import NestedDict

class NestedDict_Test( unittest.TestCase ):

    def setUp( self ):
        self.DUT = NestedDict()
    
    def tearDown(self):
        self.DUT = None

    def _do_get( self, key ):
        return self.DUT.get( key )

    def test_basic_set_get(self):
        self.DUT.set("dog","walter")
        result = self.DUT.get( "dog" )
        self.assertEqual( result, "walter" )

    def test_basic_get_fail(self):
        self.DUT.set("dog","walter")
        ok = False
        try:
            result = self._do_get('cat')
            self.fail("That should have raised an error")
        except KeyError as E:
            ok = True
        self.assert_(ok)

        
    
    def test_twolevel_set( self ):
        self.DUT.set( "all_dogs.one", "shatzi" )
        self.DUT.set( "all_dogs.two", "dolly" )
        self.DUT.set( "all_dogs.three", "walter" )
        tmp = self.DUT.get( "all_dogs.three" )
        self.assertEqual( "walter", tmp )
        tmp = self.DUT.get( 'all_dogs.one' )
        self.assertEqual( "shatzi", tmp )
        self.assertEqual( "dolly", self.DUT.get("all_dogs.two" ) )
    
    def get_test_dict(self):
        dut = { 'pet' : { 'dog' : { 'name' : 'walter', 'age' : 12 } } }
        return dut
    def test_from_to_dict(self):
        try:
            dut = NestedDict.from_dict( self.get_test_dict() )
        except Exception as E:
            print("E=%s" % str(E))
        output = dut.as_dict()
        self.assertIsInstance( output, dict )
        dut2 = output.get( 'pet' )
        self.assertIsInstance( dut2, dict )
        dut3 = dut2.get( 'dog' )
        self.assertIsInstance( dut2, dict )
        result = dut3.get('name')
        self.assertEqual( result, 'walter' )
        result = dut3.get( 'age' )
        self.assertEqual( result, 12 )
    def test_get_path( self ):
        tmp = self.get_test_dict()
        dut = NestedDict.from_dict(tmp)
        answer = dut.get('pet.dog.name')
        self.assertEqual(answer,'walter')
        answer = dut.get(('pet.dog.age'))
        self.assertEqual(answer,12)

    def test_get_path( self ):
        walter = NestedDict.from_dict( {'name':'walter','age':12})
        age = walter['age']
        self.assertEqual(age,12)

    def test_set_get_path( self ):
        self.DUT.set( 'pet.dog.walter.type', "chocolate-lab" )
        self.DUT.set( 'pet.dog.walter.age', 12 )
        self.DUT.set( 'pet.dog.walter.where', 'san-diego')
        self.DUT.set( 'pet.dog.shatzi.type', "weinerdog" )
        self.DUT.set( 'pet.dog.shatzi.age', 8 )
        self.DUT.set( 'pet.dog.shatzi.where', 'corpus-christi' )
        tmp = self.DUT.get( 'pet.dog.walter.type' )
        self.assertEqual( tmp, 'chocolate-lab' )
        tmp = self.DUT.get( 'pet.dog.shatzi.where' )
        self.assertEqual( tmp, 'corpus-christi')
        value = self.DUT['pet']['dog']['walter']['age']
        self.assertEqual( value, 12 )



if __name__ == '__main__':
   unittest.main()
   sys.exit(0)
