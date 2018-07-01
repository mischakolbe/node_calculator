"""Module for values of base types (int, float, ...) that allow storing metadata.

:author: Mischa Kolbe <mischakolbe@gmail.com>

Note:
    The stored metadata on NcValues is essential to keep track of where values
    came from when the NodeCalculator is tracing.

    When a value is queried in a NodeCalculator formula it returns an NcValue
    instance, which has the value-variable attached to it. For example:

        a = noca.Node("pCube1")

        with noca.Tracer(pprint_trace=True):
            a.tx.get()

        # >>> val1 = cmds.getAttr('pCube1.tx')

    "val1" is the stored variable name of this queried value. When it is used
    in a calculation later in the formula the variable name is used instaed of
    the value itself. For example:

        a = noca.Node("pCube1")
        b = noca.Node("pSphere1")

        with noca.Tracer(pprint_trace=True):
            curr_tx = a.tx.get()
            b.ty = curr_tx

        # >>> val1 = cmds.getAttr('pCube1.tx')
        # >>> cmds.setAttr('pSphere1.translateY', val1)
        # Rather than plugging in the queried value (making it very unclear
        # where that value came from), the value-variable "val1" is used instead.

    Furthermore: Basic math operations performed on NcValues are stored, too!
    This allows to keep track of where values came from as much as possible:

        a = noca.Node("pCube1")
        b = noca.Node("pSphere1")

        with noca.Tracer(pprint_trace=True):
            curr_tx = a.tx.get()
            b.ty = curr_tx + 2  # Adding 2 doesn't break the origin of curr_tx!

        # >>> val1 = cmds.getAttr('pCube1.tx')
        # >>> cmds.setAttr('pSphere1.translateY', val1 + 2)  # <-- !!!
        # Note that the printed trace contains the correct calculation including
        # the value-variable "val1".

Example:
    ::

        # This works:
        a = value(1, "my_metadata")

        # This does NOT work:
        a = 1
        a.metadata = "my_metadata"
        # >>> AttributeError: 'int' object has no attribute 'metadata'
"""

# Python modules
import re
import copy

# Third party imports

# Local imports
from . import logger
from . import lookup_table


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP LOGGER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
logger.clear_handlers()
logger.setup_stream_handler(level=logger.logging.DEBUG)
LOG = logger.log


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLEAN GLOBALS (useful for dev work!)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NcValue-types stay in globals() even when reloaded. Avoids restarting Maya.
globals_copy = copy.copy(globals())
for key, value in globals_copy.iteritems():
    if key.startswith("Nc") and key.endswith("Value"):
        del globals()[key]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# BASIC FUNCTIONALITY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def value(value, metadata=None, created_by_user=True):
    """Create a new value with metadata of appropriate NcValue-type.

    Note:
        For clarity: The given value is of a certain type & an appropriate type
        of NcValue must be used. For example:
        - A value of type <int> will become a <NcIntValue>
        - A value of type <float> will become a <NcFloatValue>
        - A value of type <list> will become a <NcListValue>
        The first time a certain NcValue class is required (meaning: if it's not
        in the globals yet) the function _create_metadata_val_class is called to
        create and add the necessary class to the globals.
        Any subsequent time that particular NcValue class is needed, the
        existing class constructor in the globals is used.

        The reason for all this is that each created NcValue class is an instance
        of the appropriate base type. For example:
        - An instance of <NcIntValue> inherits from <int>
        - An instance of <NcFloatValue> inherits from <float>
        - An instance of <NcListValue> inherits from <list>

    Args:
        value (bool, int, float, list, dict, ...): Value of any type
        metadata (bool, int, float, list, ...): Any data that should be attached to this value
        created_by_user (bool): Whether this value was created by the user or via script

    Returns:
        return_value (class-instance): New instance of appropriate NcValue-class
            Read Notes for details.

    Examples:
        ::

            a = value(1, "some metadata")
            print(a)
            # >>> 1
            print(a.metadata)
            # >>> "some metadata"
            print(a.basetype)
            # >>> <type 'int'>
            a.maya_node = "pCube1"  # Not only .metadata can be stored!
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

    # Retrieve the basetype of NcValues, to make a new value of the same basetype
    if isinstance(value, NcValue):
        value_type = value.basetype
        if metadata is None:
            metadata = value.metadata
    else:
        value_type = type(value)
        if metadata is None:
            metadata = value

    # Construct the class name out of the type of the given value
    class_name = "Nc{}Value".format(value_type.__name__.capitalize())

    # If the necessary class type already exists in the globals: Return it
    if class_name in globals():
        NewNcValueClass = globals()[class_name]

    # If it doesn't exist in the globals yet: Create necessary class type
    else:
        NewNcValueClass = _create_metadata_val_class(value_type)

        # Setting __name__ sets the class name so it's not "NewNcValueClass" for all types!
        NewNcValueClass.__name__ = class_name
        # Add the new type to the globals
        globals()[class_name] = NewNcValueClass

    # Create a new instance of the specified type with the given value and metadata
    return_value = NewNcValueClass(value)
    return_value.metadata = metadata
    return_value.created_by_user = created_by_user

    return return_value


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NODE CALCULATOR VALUE CLASS CREATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NcValue(object):
    """BaseClass inherited by all NcValue-classes that are created on the fly.

    Note:
        Only exists for inheritance check: isinstance(XYZ, NcValue)
        NcIntValue, NcFloatValue, etc. are otherwise hard to identify.
    """
    pass


def _create_metadata_val_class(class_type):
    """Closure to create value class of any type.

    Note:
        Check docString of value function for more details.

    Args:
        class_type (builtin-type): Type for which a new NcValue-class should be created

    Returns:
        NcValueClass (class of appropriate type): New class constructor for a
            NcValue class of appropriate type to match given class_type
    """

    # Can't inherit bool (TypeError: 'bool' not acceptable base type). Redirect to integer!
    if class_type is bool:
        class_type = int

    class NcValueClass(class_type, NcValue):
        def __init__(self, *args, **kwargs):
            """Leave the init method unchanged"""
            class_type.__init__(self, *args, **kwargs)

        @property
        def basetype(self):
            """Convenience property to access the base type easily.

            Returns:
                class_type (builtin-type): Type which this class is derived from.
            """
            return class_type

        @property
        def _value(self):
            """Get the held value as an instance of the basetype.

            Returns:
                value (basetype): Held value cast to its basetype.
            """
            return self.basetype(self)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # All subsequent magic methods return a new NcValue! This is to
        # preserve the origin of the values, even when used with another regular number!
        # The property "_value" is necessary, otherwise it gets stuck in a loop!
        # -> "_value" sticks the held value into its basetype-class to perform the calculation
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        def __add__(self, other):
            """Regular addition operator."""
            metadata = _concatenate_metadata("add", self, other)
            return_value = self._value + other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __radd__(self, other):
            """Reflected addition operator.

            Note:
                Fall-back method in case regular addition is not defined & fails.
            """
            metadata = _concatenate_metadata("add", other, self)
            return_value = other + self._value
            return value(return_value, metadata=metadata, created_by_user=False)

        def __sub__(self, other):
            """Regular subtraction operator."""
            metadata = _concatenate_metadata("sub", self, other)
            return_value = self._value - other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __rsub__(self, other):
            """Reflected subtraction operator.

            Note:
                Fall-back method in case regular subtraction is not defined & fails.
            """
            metadata = _concatenate_metadata("sub", other, self)
            return_value = other - self._value
            return value(return_value, metadata=metadata, created_by_user=False)

        def __mul__(self, other):
            """Regular multiplication operator."""
            metadata = _concatenate_metadata("mul", self, other)
            return_value = self._value * other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __rmul__(self, other):
            """Reflected multiplication operator.

            Note:
                Fall-back method in case regular multiplication is not defined & fails.
            """
            metadata = _concatenate_metadata("mul", other, self)
            return_value = other * self._value
            return value(return_value, metadata=metadata, created_by_user=False)

        def __div__(self, other):
            """Regular division operator."""
            metadata = _concatenate_metadata("div", self, other)
            return_value = self._value / other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __rdiv__(self, other):
            """Reflected division operator.

            Note:
                Fall-back method in case regular division is not defined & fails.
            """
            metadata = _concatenate_metadata("div", other, self)
            return_value = other / self._value
            return value(return_value, metadata=metadata, created_by_user=False)

        def __pow__(self, other):
            """Power operator."""
            metadata = _concatenate_metadata("pow", self, other)
            return_value = self._value ** other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __eq__(self, other):
            """Equality operator: =="""
            metadata = _concatenate_metadata("eq", self, other)
            return_value = self._value == other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __ne__(self, other):
            """Inequality operator: !="""
            metadata = _concatenate_metadata("ne", self, other)
            return_value = self._value != other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __gt__(self, other):
            """Greater than operator: >"""
            metadata = _concatenate_metadata("gt", self, other)
            return_value = self._value > other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __ge__(self, other):
            """Greater equal operator: >="""
            metadata = _concatenate_metadata("ge", self, other)
            return_value = self._value >= other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __lt__(self, other):
            """Less than operator: <"""
            metadata = _concatenate_metadata("lt", self, other)
            return_value = self._value < other
            return value(return_value, metadata=metadata, created_by_user=False)

        def __le__(self, other):
            """Less equal operator: <="""
            metadata = _concatenate_metadata("le", self, other)
            return_value = self._value <= other
            return value(return_value, metadata=metadata, created_by_user=False)

    return NcValueClass


def _concatenate_metadata(operator, input_a, input_b):
    """Concatenate the metadata for the given NcValue(s).

    Note:
        Check docString of this module for more detail why this is important.

    Args:
        operator (str): Name of the operator sign to be used for concatenation
        input_a (NcValue, int, float, bool): First part of the operation
        input_b (NcValue, int, float, bool): Second part of the operation

    Returns:
        return_metadata (str): Concatenated metadata for performed operation.

    Examples:
        ::

            a = noca.Node("pCube1")
            b = noca.Node("pSphere1")

            with noca.Tracer(pprint_trace=True):
                curr_tx = a.tx.get()

                b.ty = curr_tx + 2

            # >>> val1 = cmds.getAttr('pCube1.tx')
            # >>> cmds.setAttr('pSphere1.translateY', val1 + 2)  # <-- !!!
    """
    LOG.debug("_concatenate_metadata (%s, %s, %s)" % (operator, input_a, input_b))

    operator_data = lookup_table.METADATA_CONCATENATION_TABLE[operator]
    operator_symbol = operator_data.get("symbol")
    is_associative = operator_data.get("associative", False)

    # If input_a is an NcValue instance: Replace input_a by its metadata
    if isinstance(input_a, NcValue):
        input_a = input_a.metadata

    # If input_b is an NcValue instance: Replace input_b by its metadata
    if isinstance(input_b, NcValue):
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
