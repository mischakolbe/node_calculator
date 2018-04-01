"""
Unit tests for metadata_variables.py
"""
import unittest

# Make sure relative paths don't mess up the import procedure, if script is run directly
if __name__ == "__main__":
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import metadata_variables
else:
    from .. import metadata_variables


test_variables = [
    True,  # Boolean
    1,  # Integer
    1.0,  # Float
    "one",  # String
    (1, 2, 3),  # Tuple
    set([1, 2, 3]),  # Set
    [1, 2, 3],  # List
    {"one": 1, "two": 2}  # Dictionary
]


def _test_type(value):
    """
    Basic tests that a given value is correctly set up; correct value, type, metadata, ...
    """
    value_type = type(value)

    def test(self):
        variable = metadata_variables.var(value, "metadata")
        self.assertEqual(variable, value)
        self.assertEqual(variable.metadata, "metadata")
        self.assertEqual(
            variable.__class__.__name__,
            "{}MetadataVar".format(value_type.__name__.capitalize())
        )

        # bool can not be a base type. Tests must reflect that! Redirecting bool to int!
        if value_type is bool:
            bool_proof_type = int
        else:
            bool_proof_type = value_type

        self.assertEqual(variable.basetype, bool_proof_type)
        self.assertEqual(variable.__class__.__bases__[0], bool_proof_type)
    return test


def _test_type_singleton(value):
    """
    The instance for every given type should be from a singleton class!
    """

    def test(self):
        variable_a = metadata_variables.var(value, "metadata_a")
        variable_b = metadata_variables.var(value, "metadata_b")
        self.assertIs(variable_a.basetype, variable_b.basetype)
    return test


def _test_subclass_proof(value):
    """
    Making a variable of an existing MetadataVar should result in the same
    baseclass-type, NOT a MetadataVar with basetype MetadataVar!
    """

    def test(self):
        # bool can not be a base type. Tests must reflect that! Redirecting bool to int!
        value_type = type(value)
        if value_type is bool:
            value_type = int

        variable_a = metadata_variables.var(value, "metadata_a")
        variable_b = metadata_variables.var(variable_a, "metadata_b")

        self.assertIs(variable_a.basetype, value_type)
        self.assertIs(variable_b.basetype, value_type)
    return test


class TestMetadataVariablesMeta(type):

    def __new__(_mcs, _name, _bases, _dict):
        # Add tests for each given variable(-type)
        for variable in test_variables:
            type_nice_name = type(variable).__name__

            # Add basic tests
            type_test_name = "test_{}".format(type_nice_name)
            _dict[type_test_name] = _test_type(variable)

            # Add singleton test
            type_singleton_test_name = "test_{}_singleton".format(type_nice_name)
            _dict[type_singleton_test_name] = _test_type_singleton(variable)

            # Add test to make sure MetadataVar of MetadataVar uses correct baseclass
            type_subclass_test_name = "test_{}_subclass".format(type_nice_name)
            _dict[type_subclass_test_name] = _test_subclass_proof(variable)

        return type.__new__(_mcs, _name, _bases, _dict)


class TestMetadataVariables(unittest.TestCase):
    __metaclass__ = TestMetadataVariablesMeta


if __name__ == '__main__':
    unittest.main()
