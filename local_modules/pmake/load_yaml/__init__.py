'''
Simple wrapper around PyYAML that produces better error messages.
Otherwise you deal with Python Vomit.
'''
import os

import yaml

from pmake.logger import fatal
from pmake.logger import error_print

def load_yaml( filename ):
    if not os.path.isfile( filename ):
        error_print( "cwd: %s" % os.getcwd())
        fatal("No such file: %s" % filename )

    try:
        text = open( filename, "rt" ).read()
    except Exception as E:
        fatal("%s: Cannot open, %s" % (filename, str(E)))
    try:
        data = yaml.safe_load( text )
    except yaml.YAMLError as E:
        if hasattr(E,'problem_mark'):
            m = E.problem_mark
            fatal("%s:%d: ERROR parsing yaml: column: %d, %s" % (filename, m.line+1, m.column+1,str(E)))
        else:
            fatal("%s: Unknown YAML parse error: %s" % (filename,str(E)))

    return data
