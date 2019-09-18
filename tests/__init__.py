import os
import unittest


class BaseUnitTestHelper(unittest.TestCase):
    
    @property
    def base_path(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
