"""
Unit tests for noca.metadata_value
"""


# print isinstance(g, noca.metadata_value.IntMetadataValue)
# print isinstance(g, noca.metadata_value.MetadataValue)
# import numbers
# print isinstance(g, numbers.Real)






# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports

# Local imports
from cmt.test import TestCase
import node_calculator.core as noca


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
        meta_val = noca.metadata_value.value(value, "metadata")
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

            # # Add singleton test
            # type_singleton_test_name = "test_{}_singleton".format(type_nice_name)
            # _dict[type_singleton_test_name] = _test_type_singleton(value)

            # # Add test to make sure MetadataValue of MetadataValue uses correct basetype
            # type_subclass_test_name = "test_{}_subclass".format(type_nice_name)
            # _dict[type_subclass_test_name] = _test_subclass_proof(value)

        return type.__new__(_mcs, _name, _bases, _dict)


class TestMetadataValue(TestCase):
    """ Metaclass helps to instantiate the TestMetadataValueMeta with all tests """
    __metaclass__ = TestMetadataValueMeta

    def test_singleton(self):
        """
        The instance for every given type should be from a singleton class!
        """
        value = TEST_VALUES[1]

        meta_val_a = noca.metadata_value.value(value, "metadata_a")
        meta_val_b = noca.metadata_value.value(value, "metadata_b")

        self.assertIs(meta_val_a.basetype, meta_val_b.basetype)

    def test_basetype_consistency(self):
        """
        Making a meta_val of an existing MetadataValue should result in the same
        baseclass-type, NOT a MetadataValue with basetype MetadataValue!
        """
        value = TEST_VALUES[1]
        value_type = type(value)

        meta_val_a = noca.metadata_value.value(value, "metadata_a")
        meta_val_b = noca.metadata_value.value(meta_val_a, "metadata_b")

        self.assertIs(meta_val_a.basetype, value_type)
        self.assertIs(meta_val_b.basetype, value_type)
