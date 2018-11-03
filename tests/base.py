import maya.cmds as mc
from unittest import TestCase


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(self):
        mc.file(new=True, force=True)

    def tearDown(self):
        mc.file(new=True, force=True)
