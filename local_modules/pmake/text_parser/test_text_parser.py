import sys
import unittest
import os
import shutil
import tempfile

from pmake.text_parser  import SimpleTextParser

_temp_dir=None

class SimpleTextParser_Test( unittest.TestCase ):

    def getTempDir( self ):
        # IMPLIMENTATION INFORMATION:
        # We do not use the "secure temp file/directory stuff"
        # We do not make a unique one every time
        #
        # Reason:
        #   On failure we want to be able to inspect files
        #   this will help greatly to debug issues with the test.
        # And there is no simple way to detect if/when all tests pass or fail.
        # So - rather then create hundreds of unique names we use fixed names.
        global _temp_dir
        if _temp_dir is None:
            # We use the same name over and over again on purpose.
            tmp = tempfile.gettempdir()
            _temp_dir = os.path.join( tmp, 'text-parse-unit-test' )
            # If it exists, destroy it.
            if os.path.exists( _temp_dir ):
                shutil.rmtree( _temp_dir )
            # and then create it, thus it is empty.
            os.makedirs( _temp_dir )
        return _temp_dir


    def temp_filename( self, name ):
        '''
        Create a file in the temp directory
        '''
        return os.path.join( self.getTempDir(), name )
    
    def setUp( self ):
        self.DUT = SimpleTextParser()
    
    def tearDown(self):
        self.DUT = None

    def test_10_lines(self):
        fn = self.temp_filename("10_lines.txt")
        expected = []
        with open( fn, "wt" ) as f:
            for x in range( 0, 10 ):
                txt = "line %s\n" % x
                expected.append(txt)
                f.write(txt)

        self.DUT.open_file( fn )
        for x in range(0,10):
            txt = self.DUT.raw_next_line()
            if len(txt) == 0:
                break
            self.assertEqual( txt, expected[x] )

    def _write_expected( self, text ):
        '''
        Used when constructing a #if/#else/#endif test
        We write this to the file we are parsing.
        and write the text to the expected list.
        '''
        self.test_fp.write( text )
        self.expected.append(text)

    def create_include_test_files( self, filenameA, filenameB ):
        self.expected = []
        fpA = open( filenameA, "wt" )
        fpB = open( filenameB, 'wt' )
        self.test_fp = fpA
        for x in range(0,5):
            self._write_expected( "lineA-%d\n" % x )
        self.expected.append(SimpleTextParser.INCLUDE_BARRIER)
        tmp = '#include "includeB"\n'
        fpA.write(tmp)
        self.test_fp = fpB
        for x in range(0,5):
            self._write_expected("lineB-%d\n" % x )
        # EOF(B)
        self.expected.append( SimpleTextParser.INCLUDE_BARRIER)
        self.test_fp = fpA
        for x in range(5,10):
            self._write_expected( "postB-%d\n" %  x )
        # And the file should end with a "blank" line
        # EOF(A)
        self.expected.append( '' )
        fpA.close()
        fpB.close()
        return self.expected

    def cat_file( self, filename ):
        os.system("cat %s" % filename )

    def read_expected( self, filename_to_read : str,  expected_lines : list ):
        '''
        We have created at test file we should read
        It contains what we are expecting from the processed line reader
        '''
        self.cat_file( filename_to_read )
        self.DUT.open_file( filename_to_read )

        # tmpE = expected, tmpA = actual
        for x in range(0, len(expected_lines) ):
            # get the expected
            tmpE = expected_lines[x]
            # And the actual.
            tmpA = self.DUT.next_preprocessed_line().as_str()
            # they must be the same.
            self.assertEqual( tmpE, tmpA )
        print("Success")


    def test_include_file( self ):
        '''
        This tests #include files
        '''
        expected = []
        filenameA = self.temp_filename( 'includeA' )
        filenameB = self.temp_filename( 'includeB' )

        expected = self.create_include_test_files( filenameA, filenameB )

        self.read_expected( filenameA, expected )

    def _write_preprocessor( self, txt ):
        '''
        Write a #if/#else/#endif statement to the output 
        '''
        self.test_fp.write(txt)
        # The parser returns this instead of the text written
        self.expected.append( SimpleTextParser.PREPROCESSING_LINE )

    def _write_disabled( self, txt ):
        '''
        Write text to a section where we are inside an #if False
        '''
        self.test_fp.write( txt )
        self.expected.append( SimpleTextParser.IF_DISABLED )

    def _create_if_else_endif( self ):
        '''
        This is the test creator for #if/#else/#endif
        '''
        filenameA = self.temp_filename( "if-else-endif" )
        self.test_fp = open( filenameA, "wt" )
        self.expected = []
        self._write_expected("start-with-a-1\n")
        self._write_preprocessor("#if 1\n")
        self._write_expected("this-is-enabled\n")
        self._write_expected("This-too\n")
        self._write_preprocessor( "#else\n")
        self._write_disabled("disabled\n")
        self._write_preprocessor("#endif\n")
        self._write_expected("start-with-a-0\n")
        self._write_preprocessor("#if 0\n")
        self._write_disabled("this is disabled\n")
        self._write_preprocessor("#else\n")
        self._write_expected("this is enabled in the else\n")
        self._write_preprocessor("#endif\n")
        self._write_expected("normal text here\n")
        self._write_preprocessor("#if 1\n")
        self._write_expected("before-elif\n")
        self._write_preprocessor("#elif 1\n")
        self._write_expected("inside-elif-1\n")
        self._write_preprocessor("#elif 0\n")
        self._write_disabled("inside elif-0\n")
        self._write_preprocessor("#endif\n")
        self._write_expected("normal-text\n")
        self.test_fp.close()
        self.test_fp = None
        return filenameA, self.expected


    def expression_evaluator( self, parser, expression ):
        # this test evaluator is trivail it only accepts 0 and 1.
        # A REAL evaluator might do expressions and variables
        # But that is not part of the unit test for the parser.
        expression=int(expression)

        return expression==1

    def test_if_else_endif(self):
        filenameA, expected = self._create_if_else_endif()
        self.DUT.if_evaluator = self.expression_evaluator
        self.read_expected( filenameA, expected )

    def create_if_error(self):
        self.expected = []
        fn = self.temp_filename("if-error.txt")
        self.test_fp = open(fn,"wt")
        self.write_expected("this should be here\n")
        self.test_fp.write("#if NotANumber\n")
        self.expected.append(None)
        return fn, self.expected





                  

if __name__ == '__main__':
   unittest.main()
   sys.exit(0)
