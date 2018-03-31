"""
Unit tests for metadata_variables.py
"""
import unittest

if __name__ == "__main__":
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import metadata_variables
else:
    from .. import metadata_variables


# different assert options for testing!
# https://docs.python.org/3/library/unittest.html#unittest.TestCase.debug
class TestCore(unittest.TestCase):

    def test_bool(self):
        variable = (metadata_variables.var(True))
        self.assertEqual(variable, True)
        self.assertNotEqual(variable.__class__.__bases__[0], bool)
        self.assertEqual(variable.__class__.__bases__[0], int)

    def test_int(self):
        variable = (metadata_variables.var(1))
        self.assertEqual(variable, 1)
        self.assertEqual(variable.__class__.__bases__[0], int)

    def test_float(self):
        variable = (metadata_variables.var(1.0))
        self.assertEqual(variable, 1.0)
        self.assertEqual(variable.__class__.__bases__[0], float)

    def test_str(self):
        variable = (metadata_variables.var("one"))
        self.assertEqual(variable, "one")
        self.assertEqual(variable.__class__.__bases__[0], str)

    def test_list(self):
        variable = (metadata_variables.var([1, 2, 3]))
        self.assertEqual(variable, [1, 2, 3])
        self.assertEqual(variable.__class__.__bases__[0], list)

    def test_dict(self):
        variable = (metadata_variables.var({"a": 1, "b": 2}))
        self.assertEqual(variable, {"a": 1, "b": 2})
        self.assertEqual(variable.__class__.__bases__[0], dict)

    # def test_div(self):
    #     self.assertEqual(metadata_variables.div(10, 5), 2)
    #     self.assertEqual(metadata_variables.div(-1, 1), -1)
    #     self.assertEqual(metadata_variables.div(-1, -1), 1)

    #     with self.assertRaises(ValueError):
    #         metadata_variables.div(1, 0)


if __name__ == '__main__':
    unittest.main()


# a = var(1.0, "bla")
# b = var(2.0, "bon")
# print a
# print b
# print id(a.__class__)
# print id(b.__class__)
# print id(a)
# print id(b)
# print a.__class__ is b.__class__
# print float is float
