

class NestedDict_KeyError( KeyError ):
    def __init__( self, keyname ):
        KeyError.__init__("bad key: %s" % keyname )

class NestedDict( ):
    '''
    A Nested dict is just like a dict but has features dealing with the key (or path)
    For example:
        nd = NestedDict()
        nd.pet.dog.name = "Walter"
    is the same as:
        nd['pet']['dog']['name'] = "Walter"
    is the same as:
        nd.set('pet.dog.name',"Walter")
    The same applies for "get()" operations.
    '''
    def __init__( self ):
        self._dict = dict()

    def __str__( self ):
        # Make str() work
        d = self.as_dict()
        return str(d)
    
    def __getitem__(self,name):
        return self.get(name)

    def as_dict( self ):
        '''
        Convert the nested dict into a regular dict.
        '''
        result = dict()
        for k,v in self._dict.items():
            # If we have a recursive entry, convert it also.
            if isinstance( v, NestedDict ):
                v = v.as_dict()
            result[k] = v
        return result

    def set( self, path, value ):
        '''
        Dicts have a "get" but no "set" - but we provide one anyway for completeness
        '''
        if not isinstance( path, str ):
            raise ValueError("path must be a string, not: %s" % path.__class__.__name__ )
        # We can split the string :-)
        parts = path.split('.')
        # If needed, convert dicts to NestedDicts
        if isinstance( value, dict ):
            value = NestedDict.from_dict( value )
        # Recursively set
        self._internal_set( parts, value )

    def _internal_set( self, parts, value ):
        '''
        This is recursive, we loop through layers here

        Originally, we may have had: pet.dog.name = "Walter"
        This became: parts=['pet','dog','name'], value="Walter"
        This should create a dict in the form: { 'pet' : { 'dog' : { 'name': "Walter" }}}
        Here we deal with 'pet.dog' recursively stopping at parts=['name'], and value='Walter'
        '''
        # Make sure our parts are modifiable and itterable
        assert( isinstance(parts,list) )

        # STEP 1: recursively loop over the prefix of our path.
        if len(parts) > 1:
            # Take the first name
            name = parts.pop(0)
            if name in self._dict:
                nextlevel = self._dict.get(name)
            else:
                # it does not exist, then create the level.
                nextlevel = NestedDict()
                self._dict[name] = nextlevel
            # Then recurse into the next level
            nextlevel._internal_set( parts, value )    
            return
        else:
            # We now only have 'path=name' and 'value=Walter'
            # so set the value
            self._dict[ parts[0] ]  = value

    def get( self, *args ):
        '''
        Mimic Standard dictionary like feature, dict.get()
        And we need to deal with the optional 'default' parameter
        '''
        # To start: Assume we have no default value
        have_default = False
        default_value = None
        # Parse our arguments and determine if we have default value or not.
        if len(args) == 0:
            raise TypeError( "missing path parameter")
        # Ok we know we have a path parameter, fetch the path
        path = args[0]
        # And verify path is a string
        if not isinstance(path, str ):
            raise ValueError("path parameter is not a string, it is: %s" % path.__class__.__name__)
        # Break up the path into parts, ie: "pet.dog.name" becomes ['pet','dog','name']
        parts = path.split('.')
        # Do we have a default value?
        # Do we have too many parameters?
        if len( args ) == 1:
            # No default parameter, defaults above are ok.
            pass
        elif len(args) == 2:
            # We have a default value, fetch it
            have_default = True
            default_value = args[1]
        else:
            # Too many parameters
            raise TypeError("Too many parameters")
        # go recursive.
        return self._internal_get( [], parts, have_default, default_value )

    @staticmethod
    def from_dict( from_dict ):
        result = NestedDict()
        for k,v in from_dict.items():
            result.set( k,v )
        return result
    
    def clone( self ):
        '''
        Return a copy of our self
        '''
        d = self.as_dict()
        return NestedDict.from_dict( d )

    def items(self):
        '''
        Try to support the standard dict items() call.
        '''
        return self._dict.items()

    def _internal_get( self, current_path, path, have_default, default_value ):
        '''
        this is the recursive workhorse for NestedDict.get() and __getattr__()
        '''
        while len(path) > 1:
            # Take the first name
            name = path.pop(0)
            current_path.append(name)
            try:
                value = self._dict[name]
            except KeyError:
                if have_default:
                    return default_value
                raise KeyError( "no such key: %s in path: %s" % (name, '.'.join(current_path) ))
            # We have the value and it should be a NestedDict()
            return value._internal_get( current_path, path, have_default, default_value )
        # Ok, we are at the terminal leaf node in our dict.
        # ie: We had:  "pet.dog.name" we are at "name"
        if have_default:
            value = self._dict.get( name, default_value )
            return value
        if path[0] in self._dict:
            value = self._dict.get( path[0] )
        else:
            raise KeyError( "no such key: %s in path: %s" % (path[0], '.'.join(current_path) ))
        return value
