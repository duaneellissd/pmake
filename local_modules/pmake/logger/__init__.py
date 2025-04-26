# This is the log output pmake.
# all debug output goes through this.

import datetime
import sys
import os

__ALL__=['CommonLog', 'LogHelper', 'open_log_file', 'verbose_set','fatal','debug_print']

class CommonLog( ):
    '''
    About log levels.
    for debug output, do one of two things:

         log.dbg_print( 0, "this will always print")
    or   log.dbg_print( 2, "This will only print if the level is 2 or higher")
    '''
    def __init__(self):
        self.log_fp_list =[ sys.stdout ]
        self.error_count = 0
        self.warn_count = 0
        self.debug_level = 0

    def open_log_file( self, filename ):
        try:
            f = open( filename, "wt" )
        except Exception as E:
            print("FATAL: Cannot open: %s" % filename )
            print("FATAL: %s" % str(E))
            sys.exit(1)
        self.log_fp.list.append( f )
        f.write("#----------------------------------------\n")
        f.write("# LOG STARTED: %s\n" % datetime.datetime.now().isodate())
        f.write("# ARGS: %s\n" % ' '.join( sys.argv ) )
        f.write("# cwd: %s\n" % os.getcwd())
        f.write("#\n")
        f.write("#----------------------------------------\n")

    def write_all( self, msg ):
        '''
        Just write, without adding a newline to to the message.
        '''
        for f in self.log_fp_list:
            f.write( msg )

    def fatal( self, msg ):
        self.write_all( "FATAL_ERROR\n" )
        self.write_all( msg+'\n' )
        sys.exit(1)


    def error_print( self, msg ):
        self.error_count = self.error_count + 1
        self.write_all(msg+'\n')

    def warning_print( self, msg ):
        self.warn_count = self.warn_count + 1
        self.write_all(msg+'\n')

    def debug_print( self, level, msg ):
        if (level > 0) or (level >= self.debug_level):
            self.write_all( msg+'\n' )

    def verbose_increase( self ):
        '''
        Called when '-v' is found on the commandline.
        '''
        self.debug_level = self.debug_level + 1

'''
By default we write all log output to a common class
'''
common_log = CommonLog()


def open_log_file( filename ):
    '''
    Convience function for main application to open log file
    '''
    common_log.open_log_file( filename )

def verbose_set( n : int ):
    '''
    Convience function for main app argument parser to use.
    '''
    while( n > 0 ):
        n = n - 1
        common_log.verbose_increase()

class LogHelper():
    '''
    This is a helper module that one can subclass.
    It effectively adds: "self.debug()" to any and every class.
    '''
    def __init__( self, logger = None ):
        if logger is None:
            self._logger = common_log
        else:
            self._logger = logger

    def fatal( self, msg ):
        self._logger.fatal(msg)
    def debug_print( self, level, msg ):
        self._logger.debug_print(level,msg)
    def error_print( self, msg ):
        self._logger.error_print( msg )
    def warning_print( self, msg ):
        self._logger.warning_print( msg )

def fatal( msg ):
    common_log.fatal( msg )

def debug_print(level,msg):
    common_log.debug_print( level,msg )

def error_print( msg ):
    common_log.error_print( msg )

def warning_print( msg ):
    common_log.warning_print( msg )
