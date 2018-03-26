"""
This test module currently does not work. Simply saving some useful code snippets
until I get the time to implement this correctly, since I will need a proper
Maya integration.

http://www.chadvernon.com/blog/maya/unit-testing-in-maya/
"""


import unittest
from .. import core


# different assert options for testing!
# https://docs.python.org/3/library/unittest.html#unittest.TestCase.debug
class TestCore(unittest.TestCase):

    def test_mult(self):
        self.assertEqual(core.mult(10, 5), 50)
        self.assertEqual(core.mult(-1, 1), -1)
        self.assertEqual(core.mult(-1, -1), 1)

    def test_div(self):
        self.assertEqual(core.div(10, 5), 2)
        self.assertEqual(core.div(-1, 1), -1)
        self.assertEqual(core.div(-1, -1), 1)

        with self.assertRaises(ValueError):
            core.div(1, 0)


if __name__ == '__main__':
    unittest.main()
