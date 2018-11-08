"""
Unit test base class.
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
from unittest import TestCase

# Third party imports
import maya.cmds as cmds


class BaseTestCase(TestCase):
    """Base Class for all unittests."""
    @classmethod
    def setUpClass(self):
        """Run for every Test-Class, before methods are executed."""
        cmds.file(new=True, force=True)

    def tearDown(self):
        """Run after every Test-Class method."""
        cmds.file(new=True, force=True)
