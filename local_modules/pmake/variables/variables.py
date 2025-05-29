'''
This module handles variables found in the pmake.yml files.

Variables are stored as groups, and groups are in a stack like format.

BUILD_IN variables are at level 0 effectively global.
CMD_LINE comme from the command line to pmake, almost global

Each pmake.yml file can add more variables.
Note PMAKE variables can be global or local to the pmake file.
Local means, just another entry on the variable stack.

# Then each "pmake.yml" file can add its own set of variables.
# NOTE: the pmake.yml file can also declare GLOBAL variables too!
'''
from pmake.logger import LogHelper, warn_print
from pmake.where import Where


import re



class Variable():
    def __init__( self, where,name,value):
        self.where = where
        self.name = name
        self.value = value
        # If this is used it gets flagged
        self.used = False

class VariableGroup( LogHelper ):
    '''
    This is one group of variables at one scoping level.
    '''
    def __init__(self,where : Where ):
        LogHelper.__init__(self)
        '''
        Where was this group created?
        '''
        self.where = where
        '''
        The variables
        '''
        self.vars = {}

    def add_variable( self, newvar : Variable ):
        '''
        Add a variable to this group.
        '''
        old = self.vars.get( newvar.name, None )
        if old is not None:
            E = VariableError_Duplicate( old, newvar )
            if UNIT_TEST_MODE:
                raise E
        self.vars[ newvar.name ] = newvar

    def define_variable(self,where:Where,name:str,value:str):
        '''
        Define a new variable found at this location.
        '''
        self.add_variable( Variable( where, name, value ) )

UNIT_TEST_MODE = False
def unit_test_mode():
    global UNIT_TEST_MODE
    UNIT_TEST_MODE = True

# This is the variable stack.
scope_stack = []
SCOPE_BUILT_IN = 0
scope_stack.append(None) # to be replaced
SCOPE_CMD_LINE = 1
scope_stack.append(None) # to be replaced
SCOPE_LOCAL_FIRST = 2
SCOPE_LOCAL_TOP   = -1

# The variable.value is the key, the variable is the data.
value2var = {}
longest_first = []

def clear_reverse_cache():
    '''
    Clear the reverse cache
    '''
    global value2var
    value2var = {}
    longest_first = []

def build_cache():
    global value2name
    global longest_first
    value2var = {}
    # for each variable group in the scoping rules
    for vg in scope_stack:
        for name, var in vg.vars.items():
            value2var[ var.value ] = var
            longest_first.append( var.value )
    longest_first = reversed(sorted( longest_first, key=len ))
    longest_first = longest_first[:]

def reverse_get( text ):
    '''
    The idea here is to reverse out by directory names paths.
    Given:
        FOO_DIR=/some/path/to/some/dir
        text = "/some/path/to/some/dir/src/foo.c"
        produce: "${FOO_DIR}/foo.c"
    '''
    found = True
    while found:
        found = False
        for value in longest_first:
            if value not in text:
                continue
            found = True
            parts = text.split(value)
            var = value2var( value )
            # Note that this variable is used
            var.used = True
            varname = "${%s}" % var.name
            text = varname.join( parts )
    return text



class VariableError_StackUnderflow( Exception ):
    '''This is not recoverable'''
    pass

class VariableError_Duplicate( Exception):
    def __init__( self, old, newvar ):
        self.new_where = newvar.where
        self.old_where = old.where
        Exception.__init__(self,"Duplicate: %s" % newvar.name )

class VariableError_Undefined( Exception ):
    def __init__(self,name, callstack):
        self.name = name
        self.where_stack = callstack[:]
        Exception.__init__(self,"Undefined: %s" % name )



vg = VariableGroup( Where("BUILT_IN",1 ) )
scope_stack[ SCOPE_BUILT_IN ] = vg
vg = VariableGroup( Where( "CMD_LINE",1 ) )
scope_stack[ SCOPE_CMD_LINE ] = vg

def add_cmdline_variable( name,value ):
    '''
    Adds a variable with global scope.
    '''
    where = scope_stack[ SCOPE_CMD_LINE ].where
    newvar = Variable( where, name, value )
    scope_stack[SCOPE_CMD_LINE].define_variable(where,name,value)

def add_builtin_variable(name,value):
    '''
    Adds a variable with global scope.
    '''
    where = scope_stack[ SCOPE_BUILT_IN ].where
    newvar = Variable( where, name, value )
    scope_stack[SCOPE_BUILT_IN].define_variable(where,name,value)


def define_local_variable( where, name, value ):
    '''
    Adds a variable with local scope
    '''
    scope_stack[-1].define_variable(where,name,value)

def scope_push( filename, lineno ):
    vg = VariableGroup( Where( filename, lineno ) )
    global scope_stack
    scope_stack.append(vg)

def scope_pop():
    global scope_stack
    if len(scope_stack) < SCOPE_LOCAL_FIRST:
        raise VariableError_StackUnderflow("variable stack underflow")
    assert( len(scope_stack) >= 3 )
    scope_stack = scope_stack[:-1]

def reduce_text( text_in ):
    '''
    Given the text: "/some/path/src/foo.c /some/path/src/bar.c"
    And knowing: ${PROJ_SRC_DIR} = /some/path/src
    Convert the text to: "${PROJ_SRC_DIR}/foo.c ${PROJ_SRC_DIR}/bar.c"
    '''
    return reverse_get( text_in )

def expand_text( text_in ):
    '''
    Given the variable "PROJ_SRC_DIR"=/some/path/src
    Given the text_in = "${PROJ_SRC_DIR}/*.c"
    Expand the varialbe and return "/some/path/src/*.c"
    '''
    history=[]
    for x in range( 0, 20 ):
        if '${' not in text_in:
            break

    raise NotImplementedError("not done yet")
