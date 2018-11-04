import maya.cmds as cmds
from unittest import TestCase


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(self):
        cmds.file(new=True, force=True)

    def tearDown(self):
        cmds.file(new=True, force=True)
