"""
Unit tests for noca.nc_value / NcValue classes
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import numbers

# Third party imports

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

METADATAS = [
    "metadata_a",
    "metadata_b",
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


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
        meta_val = noca.nc_value.value(value, METADATAS[0])
        self.assertEqual(meta_val, value)
        self.assertEqual(meta_val.metadata, METADATAS[0])
        self.assertEqual(
            meta_val.__class__.__name__,
            "Nc{}Value".format(value_type.__name__.capitalize())
        )

        # bool can not be a base type. Tests must reflect that! Redirecting bool to int!
        if value_type is bool:
            bool_proof_type = int
        else:
            bool_proof_type = value_type

        self.assertEqual(meta_val.basetype, bool_proof_type)
        self.assertEqual(meta_val.__class__.__bases__[0], bool_proof_type)
    return test


class TestNcValueMeta(type):

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

        return type.__new__(_mcs, _name, _bases, _dict)


class TestNcValue(TestCase):
    """ Metaclass helps to instantiate the TestNcValueMeta with all tests """
    __metaclass__ = TestNcValueMeta

    def test_singleton(self):
        """
        The instance for every given type should be from a singleton class!
        """
        value = TEST_VALUES[1]

        meta_val_a = noca.nc_value.value(value, METADATAS[0])
        meta_val_b = noca.nc_value.value(value, METADATAS[1])

        self.assertIs(meta_val_a.basetype, meta_val_b.basetype)

    def test_basetype_consistency(self):
        """
        Making a meta_val of an existing NcValue should result in the same
        baseclass-type, NOT a NcValue with basetype NcValue!
        """
        value = TEST_VALUES[1]
        value_type = type(value)

        meta_val_a = noca.nc_value.value(value, METADATAS[0])
        meta_val_b = noca.nc_value.value(meta_val_a, METADATAS[1])

        self.assertIs(meta_val_a.basetype, value_type)
        self.assertIs(meta_val_b.basetype, value_type)

    def test_inheritance(self):
        """
        A metadataValue should inherit various parent classes. An int should be:
        - subclass of int
        - subclass of numbers.Real
        - subclass of NcValue
        - instance of NcIntValue
        """
        value = TEST_VALUES[1]
        value_type = type(value)

        meta_val_a = noca.nc_value.value(value, METADATAS[0])

        self.assertTrue(isinstance(meta_val_a, value_type))
        self.assertTrue(isinstance(meta_val_a, numbers.Real))
        self.assertTrue(isinstance(meta_val_a, noca.nc_value.NcValue))
        self.assertTrue(isinstance(meta_val_a, noca.nc_value.NcIntValue))

    def test_metadata_concatenation(self):
        """
        Basic math operations on NcValues are added to the metadata.
        """
        value = TEST_VALUES[1]
        meta_val_a = noca.nc_value.value(value, METADATAS[0])

        meta_val_calc = (meta_val_a + 2) / 2

        self.assertEqual(meta_val_calc.metadata, "({} + 2) / 2".format(METADATAS[0]))
