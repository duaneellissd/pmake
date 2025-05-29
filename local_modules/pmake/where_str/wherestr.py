'''
A Where Str - is nothing more then a standard string with a "where" attribute

The WHERE attribute is a pmake.Where()

This is used extensively within the parser and generators.

For example:
   You parse a YAML file - and you get a lot of strings.
   For example you might have a definition of a "library" in file:  "foo.yml" at line 23
   
In the application you have the string, 'foo', and you know the type='library'
BUT there is an error and you want to print a helpful and useful error message.
Or perhaps output a comment in your generated makfile.
Perhaps a message like this:
#
#   library: foo
#   Defined by:  file:foo.yml, at line 23
#

Thus the string that holds: 'foo.yml' also holds a "where" element.

''' 
from pmake import Where
from collections import UserString
from pmake.logger import fatal

class WhereStr( UserString ):
    def __init__(self, *args, **kwargs ):
        if len(args) != 1:
            raise Exception("expected 1 parameter")
        if 'fn' in kwargs:
            fn = kwargs.get('fn')
            del( kwargs['fn'] )
        else:
            fn = "Unknown"
        if 'ln' in kwargs:
            ln = kwargs.get('ln')
            del( kwargs['ln'] )
        else:
            ln = 1
        if "where" in kwargs:
            w = kwargs.get('where')
            w = w.clone()
            del( kwargs['where'] )
        else:
            w = Where( fn, ln )
        # strings do not take KWARGS 
        if len(kwargs) != 0:
            raise Exception("unexpected kw params: %s" % str(kwargs.keys() ))
        UserString.__init__( self, args[0] )
        self.where = w
    def as_str( self ):
        ''' Return exactly a string nothing else but a string.'''
        return str(self)
    
    def __setitem__(self, index, value):
        data_as_list = list(self.data)
        data_as_list[index] = value
        self.data = "".join(data_as_list)

    def __delitem__(self, index):
        data_as_list = list(self.data)
        del data_as_list[index]
        self.data = "".join(data_as_list)        
        