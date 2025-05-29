# This is the log output pmake.
# all debug output goes through this.

import datetime
import sys
import os

__ALL__=['CommonLog', 'LogHelper', 'open_log_file', 'verbose_set','fatal','debug_print','log_verbose_set', 'Where' ]

class Where():
    def __init__( self, filename, lineno ):
        self.filename = os.path.abspath( filename )
        self.lineno = lineno
        self.column = None
    def __str__(self):
        if self.column is None:
            txt = "%s:%d" % (self.filename,self.lineno)
        else:
            txt = "%s:%d: Column: %d" % (self.fileanme, self.lineno, self.column)
    def clone( self ):
        the_clone = Where( self.filename, self.lineno )
        the_clone.column = self.column
        return the_clone
    

class CommonLog( ):
    '''
    About log levels.
    for debug output, do one of two things:

         log.dbg_print( 0, "this will always print")
    or   log.dbg_print( 2, "This will only print if the level is 2 or higher")
    '''
    def __init__(self):
        self.log_fp = None
        self.log_stdout = True
        self.error_count = 0
        self.warn_count = 0
        self.verbose_level = 0


    def close_log_file(self):
        if self.log_fp is not None:
            self.log_fp.close()
            self.log_fp = None

    def open_log_file( self, filename ):
        if filename in ('/dev/stdout','-'):
            self.log_stdout = True
            return
        else:
            self.log_stdout = False
        try:
            f = open( filename, "wt" )
        except Exception as E:
            print("FATAL: Cannot open: %s" % filename )
            print("FATAL: %s" % str(E))
            sys.exit(1)
        self.log_fp = f
        # we do not write this to stdout
        self.log_fp.write("#----------------------------------------\n")
        self.log_fp.write("# LOG STARTED: %s\n" % datetime.datetime.now().isoformat())
        self.log_fp.write("# ARGS: %s\n" % ' '.join( sys.argv ) )
        self.log_fp.write("# cwd: %s\n" % os.getcwd())
        self.log_fp.write("#\n")
        self.log_fp.write("#----------------------------------------\n")

    def write_all( self, msg ):
        '''
        Just write, without adding a newline to to the message.
        '''
        if self.log_fp is not None:
            self.log_fp.write( msg )
        if self.log_stdout:
            sys.stdout.write(msg)

    def fatal( self, msg ):
        self.write_all( "FATAL_ERROR\n" )
        if not isinstance(msg,(list,tuple)):
            msg = [ msg ]
        for tmp in msg:
            self.write_all(tmp+'\n')
        sys.exit(1)

    def log_print( self, msg ):
        self.write_all( msg + '\n' )

    def error_print( self, msg ):
        self.error_count = self.error_count + 1
        self.write_all(msg+'\n')

    def warn_print( self, msg ):
        self.warn_count = self.warn_count + 1
        self.write_all(msg+'\n')

    def debug_print( self, level, msg ):
        if (level == 0) or (level >= self.verbose_level):
            self.write_all( msg+'\n' )

    def verbose_increase( self ):
        '''
        Called when '-v' is found on the commandline.
        '''
        self.verbose_level = self.verbose_level + 1

'''
By default we write all log output to a common class
'''
_common_log = CommonLog()

def getCommonLogger():
    return _common_log

class LogHelper():
    '''
    This is a helper module that one can subclass.
    It effectively adds: "self.debug()" to any and every class.
    '''
    def __init__( self, logger = None ):
        if logger is None:
            self._logger = _common_log
        else:
            self._logger = logger

    def fatal( self, msg ):
        self._logger.fatal(msg)
    def log_print( self, msg ):
        self._logger.log_print(msg)
    def debug_print( self, level, msg ):
        self._logger.debug_print(level,msg)
    def error_print( self, msg ):
        self._logger.error_print( msg )
    def warn_print( self, msg ):
        self._logger.warn_print( msg )

def close_log_file():
    _common_log.close_log_file()

def open_log_file( filename ):
    '''
    Convience function for main application to open log file
    '''
    _common_log.open_log_file( filename )

def log_verbose_set( n : int ):
    '''
    Convience function for main app argument parser to use.
    '''
    while( n > 0 ):
        n = n - 1
        _common_log.verbose_increase()


def fatal( msg ):
    _common_log.fatal( msg )

def debug_print(level,msg):
    _common_log.debug_print( level,msg )

def error_print( msg ):
    _common_log.error_print( msg )

def log_print( msg ):
    _common_log.log_print( msg )

def warn_print( msg ):
    _common_log.warn_print( msg )

def get_error_count():
    return _common_log.error_count

def get_warn_count():
    return _common_log.warn_count
