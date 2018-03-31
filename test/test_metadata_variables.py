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


class TestCore(unittest.TestCase):

    def test_bool(self):
        variable = metadata_variables.var(True, "metadata")
        self.assertEqual(variable, True)
        self.assertEqual(variable.metadata, "metadata")
        self.assertEqual(variable.__class__.__name__, "BoolVar")
        self.assertNotEqual(variable.__class__.__bases__[0], bool)
        self.assertEqual(variable.basetype, int)
        self.assertEqual(variable.__class__.__bases__[0], int)

    def test_int(self):
        variable = metadata_variables.var(1, "metadata")
        self.assertEqual(variable, 1)
        self.assertEqual(variable.metadata, "metadata")
        self.assertEqual(variable.__class__.__name__, "IntVar")
        self.assertEqual(variable.basetype, int)
        self.assertEqual(variable.__class__.__bases__[0], int)

    def test_float(self):
        variable = metadata_variables.var(1.0, "metadata")
        self.assertEqual(variable, 1.0)
        self.assertEqual(variable.metadata, "metadata")
        self.assertEqual(variable.__class__.__name__, "FloatVar")
        self.assertEqual(variable.basetype, float)
        self.assertEqual(variable.__class__.__bases__[0], float)

    def test_str(self):
        variable = metadata_variables.var("one", "metadata")
        self.assertEqual(variable, "one")
        self.assertEqual(variable.metadata, "metadata")
        self.assertEqual(variable.__class__.__name__, "StrVar")
        self.assertEqual(variable.basetype, str)
        self.assertEqual(variable.__class__.__bases__[0], str)

    def test_tuple(self):
        variable = metadata_variables.var((1, 2, 3), "metadata")
        self.assertEqual(variable, (1, 2, 3))
        self.assertEqual(variable.metadata, "metadata")
        self.assertEqual(variable.__class__.__name__, "TupleVar")
        self.assertEqual(variable.basetype, tuple)
        self.assertEqual(variable.__class__.__bases__[0], tuple)

    def test_set(self):
        variable = metadata_variables.var(set([1, 2, 3]), "metadata")
        self.assertEqual(variable, set([1, 2, 3]))
        self.assertEqual(variable.metadata, "metadata")
        self.assertEqual(variable.__class__.__name__, "SetVar")
        self.assertEqual(variable.basetype, set)
        self.assertEqual(variable.__class__.__bases__[0], set)

    def test_list(self):
        variable = metadata_variables.var([1, 2, 3], "metadata")
        self.assertEqual(variable, [1, 2, 3])
        self.assertEqual(variable.metadata, "metadata")
        self.assertEqual(variable.__class__.__name__, "ListVar")
        self.assertEqual(variable.basetype, list)
        self.assertEqual(variable.__class__.__bases__[0], list)

    def test_bool_singleton(self):
        variable_a = metadata_variables.var(True, "metadata_a")
        variable_b = metadata_variables.var(False, "metadata_b")
        self.assertIs(variable_a.basetype, variable_b.basetype)

    def test_int_singleton(self):
        variable_a = metadata_variables.var(1, "metadata_a")
        variable_b = metadata_variables.var(2, "metadata_b")
        self.assertIs(variable_a.basetype, variable_b.basetype)

    def test_float_singleton(self):
        variable_a = metadata_variables.var(1.0, "metadata_a")
        variable_b = metadata_variables.var(2.0, "metadata_b")
        self.assertIs(variable_a.basetype, variable_b.basetype)

    def test_str_singleton(self):
        variable_a = metadata_variables.var("one", "metadata_a")
        variable_b = metadata_variables.var("two", "metadata_b")
        self.assertIs(variable_a.basetype, variable_b.basetype)

    def test_tuple_singleton(self):
        variable_a = metadata_variables.var((1, 2), "metadata_a")
        variable_b = metadata_variables.var((3, 4), "metadata_b")
        self.assertIs(variable_a.basetype, variable_b.basetype)

    def test_set_singleton(self):
        variable_a = metadata_variables.var(set([1, 2]), "metadata_a")
        variable_b = metadata_variables.var(set([3, 4]), "metadata_b")
        self.assertIs(variable_a.basetype, variable_b.basetype)

    def test_list_singleton(self):
        variable_a = metadata_variables.var([1, 2], "metadata_a")
        variable_b = metadata_variables.var([3, 4], "metadata_b")
        self.assertIs(variable_a.basetype, variable_b.basetype)

    def test_dict(self):
        with self.assertRaises(NotImplementedError):
            metadata_variables.var({"a": 1, "b": 2})


if __name__ == '__main__':
    unittest.main()
