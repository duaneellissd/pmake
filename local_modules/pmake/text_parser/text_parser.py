'''
This is a basic text Preprocessor much like the CPP preprocessor.

 - Lines that start with "#" are generally comments.
 - Blank lines are ignored.
 - Basic support for #incude "FILENAME" is provided.
 - Basic support for #if/#else/#elif/#endif is supported.

Because this class is abstract you must provide a few functions.
They are:
  - evaluate_if_statement, this gets the text after the "#if" 
    This must return True or False, 
    if this is not provided the #if/#else etc is ignored
  - Other features to be deteremined at some later date
  
You can provide
  - an include path list.

The parser is a pull parser.
    Step 1 - you open the file.
    Step 2 - call either:  next_raw_line()
             or call: next_preprocessed_line()
    
    You may intermix the two at your own peril.
    ie: You may sometimes need to read lines in a raw fashion.
        Considering parsing a YAML multi-line tripple quoted string.

The text (string) that is returned is a "WhereStr()" 
Basically it is a string, but with a "where" attribute
The where attribute tells you where the line came from.

To support #if/#else/#endif you must provide an evaluator function
The evaluator function evaluates the "if" expression and returns True or False.
Below is a trivial example:

Examples: Setup:
    # this is a simple #if/#elif evaluator.
    def my_evaluator( parser, text ):
        text = text.strip().lower()
        # Does it look like or smell like TRUE
        if text in ('true','t','yes','y','1'):
            return True # then return true
        # Or does it look/smell ike FALSE?
        if text in ('false','f','no','n','0'):
            return False # then return false
        # Otherwise we declare a syntax error
        parser.syntax_error("Invalid #el/#elif expression: %s" % text )

    # Create our parser
    stp = SimplePreProcessor()
    # Support Include paths.
    stp.add_include_path( "some-directory" )
    stp.add_include_path( "another-directory" )
    # Support #if statements.
    stp.provide_evaluate_function(  my_evaluator )

Example in PULL mode:
    stp.pull_open_file( "somefile" )
    while True:
        text = stp.next_preprocessed_ine()
        if len(text) == 0:
            print("END OF FILE")
            break
        print("File: %s, Line: %d\nText Is: %s" %
            text.where.filename,
            text.where.linenumber,
            text )

'''
import os
import re
from pmake.logger import LogHelper
from pmake.where import Where
from pmake.where_str import WhereStr
from typing import List
import typing

_kw_flow_control = ('if','else','endif','elif')
re_keyword = re.compile('^[#](?P<keyword>(include|if|else|endif|elif))(?P<expression>.*)$')

__ALL__ = ['ParseError', 'SimpleTextParser']

class ParseError( Exception ):
    def __init__(self, where : Where, msg : str ):
        Exception.__init__( self, msg )
        self.where = where.clone()

class IfEntry( ):
    '''
    This is used to support the #if/#else/#endif
    '''
    def __init__(self, parser : "SimpleTextParser" , state :bool ):
        self.parser = parser
        self.where : Where = parser.where.clone()
        self.state : bool = state  #true or false
        self.in_else : bool = False # We begin life in the #If side of the #else

    def handle_else( self ):
        '''
        The parser has discovered an #else statement.
        '''
        if self.in_else:
            self.parser.syntax_error("already in #else state\n")
        # flip to the else side
        self._in_else = True
        # and invert the state
        self.state = not self.state
    
class IncludeEntry():
    '''
    We is a stack/list to manage include files, this is an entry in that stack
    '''
    def __init__( self, parent : "SimpleTextParser", filename : str, where: Where ):
        self.parent : "SimpleTextParser" = parent
        # Where did the #include statement begin.
        self.previous_where : Where  = parent._where.clone()
        self.parent._where.lineno = 0
        if not os.path.isfile(filename):
            self.parent.syntax_error("no such file: %s" % filename )
        self.fp : typing.TextIO = open( filename, "rt" )

    def next_line( self ) -> WhereStr:
        '''
        Read the next line from the file
        '''
        txt = self.fp.readline()
        self.parent._where.lineno = self.parent._where.lineno + 1
        # And we return the where location
        return WhereStr( txt, where=self.parent._where.clone() )
    
    def pop( self ):
        '''
        Called when we pop the entry off the include stack.
        '''
        # Restore the parser to the previous location.
        self.parent._where = self.previous_where.clone()
        # clean up.
        self.fp.close()
        self.fp = None


class SimpleTextParser(  LogHelper ):
    '''
    This is a simple text parser.
    All text is returned as a "WhereStr()" - not a normal string.
    This parser assumes that comments start with a "#" and continue to the end of the line.
    
    The parser can work two ways:
        a) In RAW mode - you call next_raw_line() - there is no preprocessing provided.
    
    or  b) In preprocessor mode, you call next_preprocessed_line()
           In that mode, text like: #if/#else/#elif/#endif/#include are handled for you.

    Preprocessing works like htis:    
        In preprocessing mode all lines are returned to you.
        Disabled lines are returned as a comment, ie; they start with #

        In preprocssing mode, SimpleTextParser.INCLUDE_BARRIER is also returned at the end of (include) files
        These too look like a comment so they can be ignored.

        But the purpose of which is to let the client parser detect run away complex items.
        For example: Yaml supports multi line tripple quote strings.
        
        BUT - for our purposes we do not want these to cross include file boundaries
        And the YAML client needs to be able to detect such a boundary.
        Hence, at the start/end of an #include file the parser returns the magic string
        SimpleTextParser.INCLUDE_BARRIER
        Thus the client( ie: the yaml parser) can use this to detect and declare syntax errors.

        Another magic string is returned: SimpleTextParser.PREPROCESSING_LINE
        This occurs when a line is consumed due to #if/#else/#elif/#endif
        Again, the multi-line text parser can use this to reject and raise syntax_errors

        And - disabled lines (the false condition of an #if/#else/#elif/#endif)
        these disabled lines are returned as a comment (the line begins with a #)
        
        The assumption is the client (the parser calling this) understands
        and can handle and ignore commets (Lines starting with "#")
    '''
    # Returned at the end of an include file
    INCLUDE_BARRIER = "#INCLUDE_BARRIER#\n"
    # Returned when an #if/#else/#endif is found.
    PREPROCESSING_LINE = "#PREPROCESSING_LINE#\n"
    # Returned when an preprocessed line is disabled.
    IF_DISABLED = "#IF-0#\n"
    def __init__( self ):
        LogHelper.__init__(self)
        self._test_mode = False
        # This is our include stack, entry[0] is the primary file we are reading.
        # Entry [1] is the first level of the first include file
        self._include_stack: List[IncludeEntry] = []
        # if/else/elif/endifs are handled in this stack
        self._if_stack: List[IfEntry] = []
        # The list of "-I" directories to search for include files.
        # Note: The current directory of the current source file is always searched first.
        # Second, the current directory of the application is also searched.
        self._include_path_list: List[str] = []
        # This is provided by the cilent, it evaluates an #if EXPRESSION
        self.if_evaluator: typing.Callable = None
        # Where are we at in the parser at this point in time.
        self._where = Where( "Unknown", 0 )
        # Set to True at end of Include Files
        self._include_at_eof = False

    def unit_test_mode(self):
        self._test_mode = True

    def add_include_path( self, path : str ):
        '''
        Adds an "include" directory, much like a C Compiler "-I" command line flag.
        '''
        self._include_path_list.append( path )

    @property
    def where( self ) -> Where:
        '''
        Return the current parser location (filename, lineno)
        '''
        return self._where

    @where.setter
    def where( self, value ):
        raise Exception("the Where attribute is readonly")
    
    def syntax_error( self, msg : str ):
        '''
        Today syntax errors are fatal :-(
        
        We Print/Dump the include stack and the error message.
        '''
        if self._test_mode:
            raise ParseError( self._where, msg )

        # We do not test the error dump when we have a syntax error.
        if len(self._include_stack) == 1:
            # We are not in an include file
            self.fatal("%s FATAL ERROR: %s" % ( str(self.where), msg ) )
        
        # Unwind the include stack       

        for idx in range( 1, len(self.include_stack) ):
            ife = self._include_stack[ idx ]
            self.log_print("%s (included from) depth: %d" % (str(ife.prevous_where),idx ))
        # Then die.
        self.fatal("%s, FATAL ERROR: %s" % (str(self._where), msg) )

    def raw_next_line( self ) -> WhereStr:
        ''' 
        Reads the next raw line of text from the input stream
        This returns a WhereStr() with a "where" attribute set.

        This does *NOT* handle #if/#else/#endif - hence the name raw

        Generally, with the exception of include file boundaries
        it acts like the standard function: readline()
        '''
        # get top of include stack.
        ise = self._include_stack[-1]
        # is the current file at the EOF?

        # case 0: RULE:  EOF returns ''
        # case 1: RULE:  non-eof (blank lines) return '\n'
        # case 2: RULE:  non-blank lines return: 'text\n'
        return ise.next_line()

    def open_file( self, filename : str ):
        '''
        Open a file so it can be parsed.
        '''
        assert( len(self._include_stack) == 0 )
        filename = os.path.abspath( filename )
        self._where = Where(filename,0)
        ise = IncludeEntry( self, filename, self._where )
        self._include_stack.append(ise)

    def push_include_file( self, filename: str ):
        '''
        Normally this is used by the "#include" directive.
        Open and push into an include file
        '''
        assert( len(self._include_stack) >= 1 )
        ise = IncludeEntry( self, filename, self._where )
        self._include_stack.append(ise)
        self._where = Where( filename, 0 )

    def pop_include_file( self ):
        '''
        Called at the end of an include file to return to the previous file.
        '''
        assert( len(self._include_stack) > 1 )
        ise = self._include_stack.pop()
        ise.pop()

    def close_file( self ):
        ''
        # We should be at the end of the parsing.
        assert( len(self._include_stack) == 1 )
        ise = self._include_stack.pop()
        ise.pop()

    def _if_stack_error( self, msg ):
        '''
        We are going down with an error of some type associated
        with #if/#else/#endif - so dump the if/else/endif stack
        '''
        for tmp in self._if_stack:
            self.log_print( "%s: Previous #if statement" % str(tmp.where) )
        self.syntax_error( msg )

    def _handle_if_elif( self, m : typing.Match ):
        '''
        Called to handle a #if/#elif statement'''
        # We require an evaluator to make this work.
        if self.if_evaluator is None:
            # If not present we are dead.
            self.syntax_error("No if evaluator present")

        # Fist trim the expression
        expression = m['expression'].strip()
        # Assume the state is false.
        state = False
        try:
            # Evaluate it 'wrapped' incase it throws an exception.
            state = self.if_evaluator( self, expression )
        except Exception as E:
            # Something went wrong, we bail out
            self._if_stack_error( "Expression syntax error: %s (%s)" % (expression,str(E)))

        # is this an IF or and ELIF?
        kw = m['keyword']
        if kw == 'if':
            if_entry = IfEntry( self, state )
            # Sanity check? has this gone nutz?
            if len(self._if_stack) > 50:
                self.syntax_error("#if stack is >50 deep?\n")
            self._if_stack.append(if_entry)
            return SimpleTextParser.PREPROCESSING_LINE
        if kw in 'elif':
            # We should be within an if already.
            # Get the top of the if stack
            try:
                if_entry = self._if_stack[-1]
            except IndexError as E:
                self._if_stack_error("No opening #if statement")
            # make sure we are not alread in the #else side.
            if if_entry.in_else:
                self._if_stack_error("Already inside an #else condition")
            if_entry.in_else = False
            # And set the new state, the elif EXPRESSION result
            if_entry.state = state
            return SimpleTextParser.PREPROCESSING_LINE
        # This should never occur.
        raise RuntimeError("bug in SimpleTextParser()")
    
    def _dequote_include_filename( self, filename : str ):
        '''
        We have a filename specified as part of an "#include" statement
        Remove the quote marks around the filename.
        '''
        msg = None
        if len(filename) < 3:
            self.syntax_error("include: filename too short: %s" % filename)
        # Accept: #include <foobar>
        ok = False
        if (filename[0] == '<') and( filename[-1] == '>'):
            ok = True
        if filename[0] in ('"',"'"):
            if filename[0] != filename[-1]:
                self.syntax_error("Quotes do not match: %s" % filename )
            ok = True
        if not ok:
            self.syntax_error("Invalid quotes for include file: %s" % filename )
        # strip first/last off
        return filename[1:-1]
    
    def _handle_include( self, m : typing.Match ):
        '''
        We have an #include statement.
        '''
        filename = m['expression']
        filename = self._dequote_include_filename( filename )
        # Get CWD of current file
        pathlist = []
        cwd = os.path.dirname( self._where.filename )
        pathlist.append(cwd)
        pathlist.append( os.getcwd() )
        pathlist.extend( self._include_path_list )
        # now search the path list.
        found = None
        tried = []
        for idir in pathlist:
            found = os.path.join( idir, filename )
            tried.append( found )
            if os.path.isfile( found ):
                # YEA, success!
                break
            found = None
            continue
        if found is None:
            for tmp in tried:
                self.log_print("%s: tried: %s" % (str(self._where), tmp ))
            if self._test_mode:
                raise ParseError( self._where, "no-such-file: %s" % filename )
            self.fatal("No such include: %s" % filename)
        self.push_include_file( found )
        return SimpleTextParser.INCLUDE_BARRIER

    def _handle_else( self, m : typing.Match ):
        '''
        Handle the #else statement
        '''
        txt = m['expression'].strip()
        if len(txt):
            self._if_stack_error("#else should have no parameter")
        if len(self._if_stack) == 0:
            self._if_stack_error("#else missing opening #if")
        self._if_stack[-1].handle_else()
        return SimpleTextParser.PREPROCESSING_LINE

    def _handle_endif( self, m: typing.Match ):
        '''
        Handle the #endif statement
        '''
        txt = m['expression'].strip()
        if len(txt):
            self._if_stack_error("#endif should have no parameter")
        if len(self._if_stack) == 0:
            self._if_stack_error("#endif without an #if statement!")
        self._if_stack.pop()
        return SimpleTextParser.PREPROCESSING_LINE


    def _handle_keyword( self, m ):
        '''
        We have some regex match for a keyword
        '''
        kw = m.groupdict()['keyword']
        rtext = None
        if kw == 'include':
            rtext = self._handle_include( m )
        elif kw in ('if','elif'):
            rtext = self._handle_if_elif(m)
        elif kw == 'else':
            rtext = self._handle_else(m)
        elif kw == 'endif':
            rtext = self._handle_endif(m)
        if rtext is None:
            # This should never occur.
            raise RuntimeError("internal error if/else/endif")
        return WhereStr( rtext, where=self._where )

    def next_preprocessed_line( self ):
        '''
        Return the next line from the input file
        Determine if it a #if/#else/#endif line
        if active - also handle #include statements.
        '''    
        # No a preprocessing line
        # get state of IF stack.
        state = True
        if len(self._if_stack) > 0:
            ife = self._if_stack[-1]
            state = ife.state

        while True:
            text = self.raw_next_line()
            # Make it a string, regex does not like WhereStr()
            # does it contain a keyword?
            m = re_keyword.match(str(text))
            if m is not None:
                kw = m['keyword']
                # Here we only want the flow control words, not #inlcude
                if kw in _kw_flow_control:
                    return self._handle_keyword(m)
                # include statements are handled only if the state is true
            # Process based on current #if/#else/#endif state
            if state:
                # Enabled so just return the string.
                if m is not None:
                    # there is a keyword, and it is an #include here.
                    self._handle_keyword(m)
                return text
            # Disabled, so return the magic string as a WhereStr
            return WhereStr( SimpleTextParser.IF_DISABLED, where=self._where )



