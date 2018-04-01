"""
Unit tests for metadata_values.py
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import unittest

# Local imports
if __name__ == "__main__":
    # Make sure relative paths don't mess up the import procedure, if script is run directly
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import metadata_values
else:
    from .. import metadata_values


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Value of all the types that should be tested
TEST_VALUES = [
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

    Args:
        value (bool, int, float, list, dict, ...): Value of any data type

    Returns:
        test function for the given value & its type
    """
    value_type = type(value)

    def test(self):
        meta_val = metadata_values.val(value, "metadata")
        self.assertEqual(meta_val, value)
        self.assertEqual(meta_val.metadata, "metadata")
        self.assertEqual(
            meta_val.__class__.__name__,
            "{}MetadataValue".format(value_type.__name__.capitalize())
        )

        # bool can not be a base type. Tests must reflect that! Redirecting bool to int!
        if value_type is bool:
            bool_proof_type = int
        else:
            bool_proof_type = value_type

        self.assertEqual(meta_val.basetype, bool_proof_type)
        self.assertEqual(meta_val.__class__.__bases__[0], bool_proof_type)
    return test


def _test_type_singleton(value):
    """
    The instance for every given type should be from a singleton class!

    Args:
        value (bool, int, float, list, dict, ...): Value of any data type

    Returns:
        test function for the given value & its type
    """

    def test(self):
        meta_val_a = metadata_values.val(value, "metadata_a")
        meta_val_b = metadata_values.val(value, "metadata_b")
        self.assertIs(meta_val_a.basetype, meta_val_b.basetype)
    return test


def _test_subclass_proof(value):
    """
    Making a meta_val of an existing MetadataValue should result in the same
    baseclass-type, NOT a MetadataValue with basetype MetadataValue!

    Args:
        value (bool, int, float, list, dict, ...): Value of any data type

    Returns:
        test function for the given value & its type
    """

    def test(self):
        # bool can not be a base type. Tests must reflect that! Redirecting bool to int!
        value_type = type(value)
        if value_type is bool:
            value_type = int

        meta_val_a = metadata_values.val(value, "metadata_a")
        meta_val_b = metadata_values.val(meta_val_a, "metadata_b")

        self.assertIs(meta_val_a.basetype, value_type)
        self.assertIs(meta_val_b.basetype, value_type)
    return test


class TestMetadataValueMeta(type):

    def __new__(_mcs, _name, _bases, _dict):
        """
        Overriding the class creation method allows to create unittests for various
        types on the fly; without specifying the same test for each type specifically
        """

        # Add tests for each given value(-type)
        for value in TEST_VALUES:
            type_nice_name = type(value).__name__

            # Add basic tests
            type_test_name = "test_{}".format(type_nice_name)
            _dict[type_test_name] = _test_type(value)

            # Add singleton test
            type_singleton_test_name = "test_{}_singleton".format(type_nice_name)
            _dict[type_singleton_test_name] = _test_type_singleton(value)

            # Add test to make sure MetadataValue of MetadataValue uses correct basetype
            type_subclass_test_name = "test_{}_subclass".format(type_nice_name)
            _dict[type_subclass_test_name] = _test_subclass_proof(value)

        return type.__new__(_mcs, _name, _bases, _dict)


class TestMetadataValue(unittest.TestCase):
    """ Metaclass helps to instantiate the TestMetadataValueMeta with all tests """
    __metaclass__ = TestMetadataValueMeta


if __name__ == '__main__':
    unittest.main()
