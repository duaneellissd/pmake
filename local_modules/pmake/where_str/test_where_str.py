import sys
import unittest
import os

from pmake import Where
from pmake.where_str import WhereStr


class WhereStr_Test( unittest.TestCase ):
    def test_basic_str(self):
        try:
            ws = WhereStr("hello world")
        except Exception as E:
            print("E=%s" % str(E))
        self.assertEqual( "hello world", ws )

    def test_basic_with_only_fn( self ):
        ws = WhereStr( "hello world", fn="dog" )
        self.assertEqual(ws.where.filename,"dog")
        self.assertEqual(ws.where.lineno,1)

    def test_basic_with_only_ln( self ):
        ws = WhereStr( "hello world", ln=1234 )
        self.assertEqual(ws.where.filename,"Unknown")
        self.assertEqual(ws.where.lineno,1234)
    
    def test_with_where( self ):
        w = Where( "dogs-and-cats", 1234 )
        ws = WhereStr( "goodbye cruel world", where=w )
        self.assertEqual( ws.where.filename, "dogs-and-cats" )
        self.assertEqual( ws.where.lineno, 1234 )
        self.assertEqual( ws, "goodbye cruel world" )

    def test_slice( self ):
        w = WhereStr("abcdefg" )
        self.assertEqual( w[0] , 'a' )
        self.assertEqual( w[0:3] , 'abc' )
        tmp = w[-1]
        self.assertEqual( tmp, "g" )
        tmp = w[-3:]
        self.assertEqual( tmp, "efg" )
  
    def test_too_few_params(self):
        ok = False
        try:
            w = WhereStr()
        except Exception as E:
            ok = True
        self.assertTrue(ok)

    def test_too_many_params(self):
        ok = False
        try:
            w = WhereStr('dog','cat')
        except Exception as E:
            ok = True
        self.assertTrue(ok)
    def test_kw_ok(self):
        w = WhereStr( 'test', fn='The_FN_Param', ln=12345678 )
        self.assertEqual( w, 'test' )
        self.assertEqual( w.where.filename, 'The_FN_Param' )
        self.assertEqual( w.where.lineno, 12345678 )
        where = Where( "xyzzy", 42 )
        w = WhereStr( "plugh", where=where)
        self.assertEqual( w, 'plugh' )
        self.assertEqual( w.where.filename, 'xyzzy' )
        self.assertEqual( w.where.lineno, 42 )
    def test_bad_kw( self ):
        ok = False
        try:
            w = WhereStr( 'test', fn="xyz", ln=1134, junk_parameter='crap' )
        except Exception as E:
            ok = True
        self.assertTrue( ok )





if __name__ == '__main__':
   unittest.main()
   sys.exit(0)
