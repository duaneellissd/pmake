
import unittest

from pmake.logger import fatal

__ALL__ = ['unit_test_logger_main']

class unit_test_logger( unittest.TestCase ):
	def __init__(self):
		print("init for my unit test")
		unittest.TestCase.__init__()
	def test_upper(self):
		print("test upper1")
		self.assertEqual('foo'.upper(),'FOO')

	def test_isupper( self ):
		print("test upper2")
		self.assertTrue('FOO'.isupper())
		self.assertFalse('Foo'.isupper() )

	def test_fatal(self):
		print("TEST FATAL")
		with self.assertRaises(SystemExit):
			fatal("This should die")
	

def unit_test_logger_main():
	print("UNIT_TEST_LOGGER_MAIN")
	unittest.main()
if __name__ == '__main__':
   unit_test_logger_main()
	