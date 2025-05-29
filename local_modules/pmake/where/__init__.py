__ALL__ = ['Where']

class Where():
    def __init__(self, filename,lineno):
        self.filename = filename
        self.lineno = lineno
    def __str__(self):
        return "%s:%d:" % (self.filename, self.lineno)
    
    def copy( self ):
        return Where( self.filename, self.lineno )
    def clone( self ):
        return self.copy()
