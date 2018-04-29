"""
Module to create values of base types (int, str, float, ...).
Creating a child-class for each value type allows to store metadata onto value.

Example:
    ::

        # WORKS:
        a = val(1, "metadata")

        # DOES NOT WORK:
        a = 1
        a.metadata = "metadata"
        # >>> AttributeError: 'int' object has no attribute 'metadata'
"""

# Local imports
from . import logger
reload(logger)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP LOGGER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
logger.clear_handlers()
logger.setup_stream_handler(level=logger.logging.DEBUG)
log = logger.log

# This is just to iterate faster. The MetadataValue-types stay in the globals() even when reloaded.
# Therefore cleaning globals() by hand so I don't have to restart Maya to clean globals()
import copy
a = copy.copy(globals())
for key, value in a.iteritems():
    if "MetadataValue" in str(key):
        del globals()[key]


def create_metadata_val_class(class_type):
    """
    Closure to create classes for any type

    Args:
        class_type (builtin-type): Type for which a new MetadataValue-class should be created

    Returns:
        MetadataValue-class of basetype class_type
    """

    # Can't inherit bool (TypeError: 'bool' not acceptable base type). Redirect to integer!
    if class_type is bool:
        class_type = int

    class MetadataValueClass(class_type):
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
        # All subsequent magic methods return a new MetadataValue! This is to
        # preserve the origin of the values, even when used with another regular number!
        # The property "_value" is necessary, otherwise it gets stuck in a loop!
        # -> "_value" sticks the held value into its basetype-class to perform the calculation
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        def __add__(self, other):
            """
            Regular addition operator.
            """
            return_value = self._value + other
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __radd__(self, other):
            """
            Reflected addition operator.
            Fall-back method in case regular addition is not defined & fails.
            """
            return_value = other + self._value
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __sub__(self, other):
            """
            Regular subtraction operator.
            """
            return_value = self._value - other
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __rsub__(self, other):
            """
            Reflected subtraction operator.
            Fall-back method in case regular subtraction is not defined & fails.
            """
            return_value = other - self._value
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __mul__(self, other):
            """
            Regular multiplication operator.
            """
            return_value = self._value * other
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __rmul__(self, other):
            """
            Reflected multiplication operator.
            Fall-back method in case regular multiplication is not defined & fails.
            """
            return_value = other * self._value
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __div__(self, other):
            """
            Regular division operator.
            """
            return_value = self._value / other
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __rdiv__(self, other):
            """
            Reflected division operator.
            Fall-back method in case regular division is not defined & fails.
            """
            return_value = other / self._value
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __pow__(self, other):
            """
            Regular power operator.
            """
            return_value = self._value ** other
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __eq__(self, other):
            """
            Equality operator: ==
            """
            return_value = self._value == other
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __ne__(self, other):
            """
            Inequality operator: !=
            """
            return_value = self._value != other
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __gt__(self, other):
            """
            Greater than operator: >
            """
            return_value = self._value > other
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __ge__(self, other):
            """
            Greater equal operator: >=
            """
            return_value = self._value >= other
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __lt__(self, other):
            """
            Less than operator: <
            """
            return_value = self._value < other
            return val(return_value, metadata=self.metadata, created_by_user=False)

        def __le__(self, other):
            """
            Less equal operator: <=
            """
            return_value = self._value <= other
            return val(return_value, metadata=self.metadata, created_by_user=False)

    return MetadataValueClass


def val(value, metadata=None, created_by_user=True):
    """
    Args:
        value (bool, int, float, list, dict, ...): Value of any data type
        metadata (bool, int, float, list, ...): Any data that should be attached to this value
        created_by_user (bool): Whether this val was created by the user or via script

    Returns:
        New instance of MetadataValue whose baseclass matches the base-type of the given value

    Example:
        ::

            a = val(1, "some metadata")
            print(a)
            # >>> 1
            print(a.metadata)
            # >>> "some metadata"
            print(a.basetype)
            # >>> <type 'int'>
            a.maya_node = "pCube1"  # ANY attribute can be stored onto a! Not only .metadata
            print(a.maya_node)
            # >>> pCube1

            b = val([1, 2, 3], "some other metadata")
            print(b)
            # >>> [1, 2, 3]
            print(b.metadata)
            # >>> "some other metadata"
            print(b.basetype)
            # >>> <type 'list'>
    """

    # If a MetadataValue is given: Retrieve the basetype of it,
    # to make a new value of the same basetype
    try:
        value_type = value.basetype
    except AttributeError:
        value_type = type(value)

    # Construct the class name out of the type of the given value
    class_name = "{}MetadataValue".format(value_type.__name__.capitalize())

    if class_name not in globals():
        # Create necessary class type, if it doesn't exist in the globals yet
        MetadataValue = create_metadata_val_class(value_type)

        # Setting __name__ sets the class name so it's not "MetadataValue" for all types!
        MetadataValue.__name__ = class_name
        # Add the new type to the globals
        globals()[class_name] = MetadataValue

    else:
        # If the necessary class type already exists: Return it from the globals
        MetadataValue = globals()[class_name]

    # Create a new instance of the specified type with the given value and metadata
    return_value = MetadataValue(value)
    return_value.metadata = metadata
    return_value.created_by_user = created_by_user

    return return_value
