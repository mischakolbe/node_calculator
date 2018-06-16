"""
Module to create values of base types (int, str, float, ...).
Creating a child-class for each value type allows to store metadata onto value.

Example:
    ::

        # WORKS:
        a = value(1, "metadata")

        # DOES NOT WORK:
        a = 1
        a.metadata = "metadata"
        # >>> AttributeError: 'int' object has no attribute 'metadata'

"""

# Python modules
import re

# Local imports
from . import logger
reload(logger)
from . import lookup_table
reload(lookup_table)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP LOGGER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
logger.clear_handlers()
logger.setup_stream_handler(level=logger.logging.DEBUG)
log = logger.log

# This is just to iterate faster. The NcValue-types stay in the globals() even when reloaded.
# Therefore cleaning globals() by hand so I don't have to restart Maya to clean globals()
import copy
a = copy.copy(globals())
for key, value in a.iteritems():
    if key.startswith("Nc") and key.endswith("Value"):
        del globals()[key]


class NcValue(object):
    """
    Only exists for inheritance check: isinstance(XYZ, NcValue)
    IntNcValue, FloatNcValue, etc. makes them hard to distinguish
    """
    pass


def create_metadata_val_class(class_type):
    """
    Closure to create classes for any type

    Args:
        class_type (builtin-type): Type for which a new NcValue-class should be created

    Returns:
        NcValue-class of basetype class_type
    """

    # Can't inherit bool (TypeError: 'bool' not acceptable base type). Redirect to integer!
    if class_type is bool:
        class_type = int

    class NcValueClass(class_type, NcValue):
        def __init__(self, *args, **kwargs):
            """ Leave the init method unchanged """
            class_type.__init__(self, *args, **kwargs)

        @property
        def basetype(self):
            """ Convenience property to access the base type easily """
            return class_type

        @property
        def _value(self):
            """ Returns the held value as an instance of the basetype """
            return self.basetype(self)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # All subsequent magic methods return a new NcValue! This is to
        # preserve the origin of the values, even when used with another regular number!
        # The property "_value" is necessary, otherwise it gets stuck in a loop!
        # -> "_value" sticks the held value into its basetype-class to perform the calculation
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        def __add__(self, other):
            """
            Regular addition operator.
            """
            metadata = _concatenate_metadata("add", self, other)
            return_value = self._value + other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __radd__(self, other):
            """
            Reflected addition operator.
            Fall-back method in case regular addition is not defined & fails.
            """
            metadata = _concatenate_metadata("add", other, self)
            return_value = other + self._value
            return value(return_value, metadata=metadata, created_by_user=False)

        def __sub__(self, other):
            """
            Regular subtraction operator.
            """
            metadata = _concatenate_metadata("sub", self, other)
            return_value = self._value - other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __rsub__(self, other):
            """
            Reflected subtraction operator.
            Fall-back method in case regular subtraction is not defined & fails.
            """
            metadata = _concatenate_metadata("sub", other, self)
            return_value = other - self._value
            return value(return_value, metadata=metadata, created_by_user=False)

        def __mul__(self, other):
            """
            Regular multiplication operator.
            """
            metadata = _concatenate_metadata("mul", self, other)
            return_value = self._value * other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __rmul__(self, other):
            """
            Reflected multiplication operator.
            Fall-back method in case regular multiplication is not defined & fails.
            """
            metadata = _concatenate_metadata("mul", other, self)
            return_value = other * self._value
            return value(return_value, metadata=metadata, created_by_user=False)

        def __div__(self, other):
            """
            Regular division operator.
            """
            metadata = _concatenate_metadata("div", self, other)
            return_value = self._value / other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __rdiv__(self, other):
            """
            Reflected division operator.
            Fall-back method in case regular division is not defined & fails.
            """
            metadata = _concatenate_metadata("div", other, self)
            return_value = other / self._value
            return value(return_value, metadata=metadata, created_by_user=False)

        def __pow__(self, other):
            """
            Regular power operator.
            """
            metadata = _concatenate_metadata("pow", self, other)
            return_value = self._value ** other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __eq__(self, other):
            """
            Equality operator: ==
            """
            metadata = _concatenate_metadata("eq", self, other)
            return_value = self._value == other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __ne__(self, other):
            """
            Inequality operator: !=
            """
            metadata = _concatenate_metadata("ne", self, other)
            return_value = self._value != other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __gt__(self, other):
            """
            Greater than operator: >
            """
            metadata = _concatenate_metadata("gt", self, other)
            return_value = self._value > other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __ge__(self, other):
            """
            Greater equal operator: >=
            """
            metadata = _concatenate_metadata("ge", self, other)
            return_value = self._value >= other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __lt__(self, other):
            """
            Less than operator: <
            """
            metadata = _concatenate_metadata("lt", self, other)
            return_value = self._value < other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __le__(self, other):
            """
            Less equal operator: <=
            """
            metadata = _concatenate_metadata("le", self, other)
            return_value = self._value <= other
            return value(return_value, metadata=metadata, created_by_user=False)

    return NcValueClass


def _concatenate_metadata(operator, input_a, input_b):
    log.debug("_concatenate_metadata ({}, {}, {})".format(operator, input_a, input_b))
    operator_data = lookup_table.METADATA_CONCATENATION_TABLE[operator]
    operator_symbol = operator_data.get("symbol")
    is_associative = operator_data.get("associative", False)

    # Replace input_a by its metadata, if input_a has such an attribute
    if hasattr(input_a, "metadata"):
        input_a = input_a.metadata

    # Replace input_b by its metadata, if input_b has such an attribute
    if hasattr(input_b, "metadata"):
        input_b = input_b.metadata

    # Any non-associative operation potentially needs parenthesis
    if not is_associative:
        # Match inputs that don't only consist of alphanums, spaces and dots
        associative_pattern = re.compile(r"[a-zA-Z0-9\s.]")

        # Add parenthesis to inputs that contain any characters not in pattern
        if associative_pattern.sub('', str(input_a)):
            input_a = "({})".format(input_a)
        if associative_pattern.sub('', str(input_b)):
            input_b = "({})".format(input_b)

    # Concatenate the return metadata
    return_metadata = "{} {} {}".format(input_a, operator_symbol, input_b)

    return return_metadata


def value(value, metadata=None, created_by_user=True):
    """
    Args:
        value (bool, int, float, list, dict, ...): Value of any data type
        metadata (bool, int, float, list, ...): Any data that should be attached to this value
        created_by_user (bool): Whether this value was created by the user or via script

    Returns:
        New instance of NcValue whose baseclass matches the base-type of the given value

    Example:
        ::

            a = value(1, "some metadata")
            print(a)
            # >>> 1
            print(a.metadata)
            # >>> "some metadata"
            print(a.basetype)
            # >>> <type 'int'>
            a.maya_node = "pCube1"  # ANY attribute can be stored onto a! Not only .metadata
            print(a.maya_node)
            # >>> pCube1

            b = value([1, 2, 3], "some other metadata")
            print(b)
            # >>> [1, 2, 3]
            print(b.metadata)
            # >>> "some other metadata"
            print(b.basetype)
            # >>> <type 'list'>
    """

    # If a NcValue is given: Retrieve the basetype of it,
    # to make a new value of the same basetype
    try:
        value_type = value.basetype
    except AttributeError:
        value_type = type(value)

    # Construct the class name out of the type of the given value
    class_name = "Nc{}Value".format(value_type.__name__.capitalize())

    if class_name not in globals():
        # Create necessary class type, if it doesn't exist in the globals yet
        NcValue = create_metadata_val_class(value_type)

        # Setting __name__ sets the class name so it's not "NcValue" for all types!
        NcValue.__name__ = class_name
        # Add the new type to the globals
        globals()[class_name] = NcValue

    else:
        # If the necessary class type already exists: Return it from the globals
        NcValue = globals()[class_name]

    # Create a new instance of the specified type with the given value and metadata
    return_value = NcValue(value)
    if metadata is None:
        metadata = value
    return_value.metadata = metadata
    return_value.created_by_user = created_by_user

    return return_value
