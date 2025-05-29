import unittest
import os

from pmake.variables import Variables
from pmake.variables import VarError

class VariableTest( unittest.TestCase ):

    def setUp( self ):
        self.DUT = Variables()
        self.DUT.just_exit = True
        # Simple replacement.
        self.DUT.add( 'dog3', 'walter')
        self.DUT.add( 'dog1', 'shatzi')
        self.DUT.add( 'dog2', 'dolly' )
        self.DUT.add( "DOG", "${str.upper(${dog1})}")
        # create a loop
        self.DUT.add( "A", "${B}" )
        self.DUT.add( "B", "${C}" )
        self.DUT.add( "C", "${A}" )
    
    def tearDown(self):
        self.DUT = None

    def _standard_case( self, input_text, expected_text ):
        answer = self.DUT.resolve( input_text )
        self.assertEqual( answer , expected_text )

    def _expect_error( self, text, errcode ):
        self.DUT.just_exit = False
        try:
            self.DUT.resolve( text )
            # should have asserted
            assert(False)
        except VarError as E:
            self.assertEqual( E.typecode , errcode )

    def test_simple_replacement(self):
        '''Simple...'''
        self._standard_case( "${dog3}", "walter" )

    def test_nested_replacement(self):
        ''' Nested.. '''
        self.DUT.replace( "C", "${dog3}")
        answer = self.DUT.resolve("${A}")
        self.assertEqual( answer , 'walter' )
    
    def test_undefined_error(self):
        self._expect_error( "${cat}", VarError.UNDEF_VAR )

    def test_runaway_recursion(self):
        self._expect_error( "${A}", VarError.RECURSION )
    
    def test_replace_at_end(self):
        self._standard_case( "my dogs name is: ${dog3}", 'my dogs name is: walter' )

    def test_replace_at_front(self):
        self._standard_case("${dog3} is my dogs name", 'walter is my dogs name' )

    def test_multi_replace(self):
        self._standard_case( "first ${dog1} second: ${dog2} third: ${dog3} today", "first shatzi second: dolly third: walter today")

    def test_syntax_no_close(self):
        self._expect_error( "var ${dog without close", VarError.SYNTAX )

    def test_3_replacements(self):
        self._standard_case("${dog1} ${dog2} ${dog3}", "shatzi dolly walter")

    def test_toupper_replacement(self):
        self._standard_case("${DOG}", "SHATZI")

    def test_os_call_replacement(self):
        tmp = os.getcwd()
        self._standard_case("${os.getcwd()}", tmp )

    def test_dual_os_call_replacemen(self):
        tmp = os.getcwd()
        expect = "before %s after" % tmp
        self._standard_case("before ${os.getcwd()} after", expect)

    def test_os_insert_middle(self):
        tmp ="dog %s cat" % os.getcwd()
        self._standard_case("dog ${os.path.abspath(.)} cat", tmp )

    def test_os_environ(self):
        v = Variables()
        v.add_dict( os.environ )
        result = v.resolve("Your HOME dir is ${HOME}")
        expect = "Your HOME dir is %s" % os.environ['HOME']
        self.assertEqual( expect, result )
        
if __name__ == '__main__':
   unittest.main()
   sys.exit(0)
