import uuid
import unittest

from pmake.logger import fatal, open_log_file, close_log_file, get_error_count, log_verbose_set, debug_print,error_print

__ALL__ = ['unit_test_logger_main']

_log_filename = None

def tempname():
    '''
    We need a persistent filename that is not deleted like tempfile does.*
    '''
    global _log_filename
    if _log_filename is None:
        _log_filename = "/tmp/" + str( uuid.uuid1() )
    return _log_filename

def reset_log_file():
    name = tempname()
    close_log_file()
    open_log_file( name )

def get_log_lines():
    close_log_file()
    with( open( tempname(), "rt") ) as f:
        lines = f.readlines()

    for x in range(0,len(lines)):
        lines[x] = lines[x].strip()
    return lines


class unit_test_logger( unittest.TestCase ):
    def test_fatal(self):
        print("TEST FATAL")
        with self.assertRaises(SystemExit):
            fatal("This should die")
    def test_debug(self):
        reset_log_file()
        log_verbose_set(3)
        # these should show  up as the last 3 lines
        debug_print(0,"level-0")
        debug_print(2,"level-2") # but not this one.
        debug_print(3,"level-3")
        debug_print(4,"level-4")
        close_log_file()
        lines = get_log_lines()
        self.assertEqual( "level-0" , lines[-3] )
        self.assertEqual( "level-3" , lines[-2] )
        self.assertEqual( "level-4" , lines[-1] )
        self.assertEqual( get_error_count() , 0 )

    def test_error( self ):
        reset_log_file()
        error_print("This is an error")
        lines = get_log_lines()
        self.assertEqual( "This is an error", lines[-1] )
        self.assertEqual( get_error_count(), 1 )
        

def unit_test_logger_main():
	print("UNIT_TEST_LOGGER_MAIN")
	unittest.main()
if __name__ == '__main__':
   unit_test_logger_main()
