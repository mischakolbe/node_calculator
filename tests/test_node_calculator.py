"""
Unit tests for overall noca functionality:
- Plug unravelling
- Set or connect
"""


# ERROR EXPECTED, IF noca.link IS NOT PRESENT!
# c.t = noca.link([a.ty, a.tx, 2]) - 5
# c.t = noca.link([a.ty, a.tx, 2]) * [1, 4, b.tx]

# Make example networks for all types!


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import unittest

# Local imports
from cmt.test import TestCase
import node_calculator.core as noca


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TestNodeCalculatorCore(TestCase):

    @unittest.skip("Not implemented yet")
    def test_xyz(self):
        """ Test XYZ """
        pass
