"""Module for values of base types (int, float, ...) that can store metadata.

:author: Mischa Kolbe <mischakolbe@gmail.com>

Note:
    The stored metadata on NcValues is essential to keep track of where values
    came from when the NodeCalculator is tracing.

    When a value is queried in a NodeCalculator formula it returns an NcValue
    instance, which has the value-variable attached to it. For example:
    ::

        a = noca.Node("pCube1")

        with noca.Tracer(pprint_trace=True):
            a.tx.get()

        # Printout:
        # val1 = cmds.getAttr('pCube1.tx')

    "val1" is the stored variable name of this queried value. When it is used
    in a calculation later in the formula the variable name is used instaed of
    the value itself. For example:
    ::

        a = noca.Node("pCube1")
        b = noca.Node("pSphere1")

        with noca.Tracer(pprint_trace=True):
            curr_tx = a.tx.get()
            b.ty = curr_tx

        # Printout:
        # val1 = cmds.getAttr('pCube1.tx')
        # cmds.setAttr('pSphere1.translateY', val1)

        # Rather than plugging in the queried value (making it very unclear
        # where that value came from), value-variable "val1" is used instead.

    Furthermore: Basic math operations performed on NcValues are stored, too!
    This allows to keep track of where values came from as much as possible:
    ::

        a = noca.Node("pCube1")
        b = noca.Node("pSphere1")

        with noca.Tracer(pprint_trace=True):
            curr_tx = a.tx.get()
            b.ty = curr_tx + 2  # Adding 2 doesn't break the origin of curr_tx!

        # Printout:
        # val1 = cmds.getAttr('pCube1.tx')
        # cmds.setAttr('pSphere1.translateY', val1 + 2)  # <-- !!!

        # Note that the printed trace contains the correct calculation
        # including the value-variable "val1".

Example:
    ::

        # This works:
        a = value(1, "my_metadata")

        # This does NOT work:
        a = 1
        a.metadata = "my_metadata"
        # >>> AttributeError: 'int' object has no attribute 'metadata'
"""


# IMPORTS ---
# Python imports
import copy
import re

# Third party imports

# Local imports
from node_calculator import logger
from node_calculator import lookup_table


# SETUP LOGGER ---
logger.clear_handlers()
logger.setup_stream_handler(level=logger.logging.WARN)
LOG = logger.log


# CLEAN GLOBALS ---
# NcValue-types stay in globals() when reloaded. Must be cleaned on reload.
for key in copy.copy(globals()):
    if key.startswith("Nc") and key.endswith("Value"):
        del globals()[key]


# BASIC FUNCTIONALITY ---
def value(in_val, metadata=None, created_by_user=True):
    """Create a new value with metadata of appropriate NcValue-type.

    Note:
        For clarity: The given in_val is of a certain type & an appropriate type
        of NcValue must be used. For example:
        - A value of type <int> will become a <NcIntValue>
        - A value of type <float> will become a <NcFloatValue>
        - A value of type <list> will become a <NcListValue>
        The first time a certain NcValue class is required (meaning: if it's
        not in the globals yet) the function _create_metadata_val_class is
        called to create and add the necessary class to the globals.
        Any subsequent time that particular NcValue class is needed, the
        existing class constructor in the globals is used.

        The reason for all this is that each created NcValue class is an
        instance of the appropriate base type. For example:
        - An instance of <NcIntValue> inherits from <int>
        - An instance of <NcFloatValue> inherits from <float>
        - An instance of <NcListValue> inherits from <list>

    Args:
        in_val (any type): Value of any type
        metadata (any type): Any data that should be attached to this value
        created_by_user (bool): Whether this value was created manually

    Returns:
        class-instance: New instance of appropriate NcValue-class
            Read Note for details.

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
    # Retrieve the basetype of NcValues, to make a new value of same basetype
    # This avoids making NcValues of NcValues of NcValues of ...
    if isinstance(in_val, NcValue):
        value_type = in_val.basetype
        if metadata is None:
            metadata = in_val.metadata
    else:
        value_type = type(in_val)
        if metadata is None:
            metadata = in_val

    # Construct the class name out of the type of the given in_val
    class_name = "Nc{0}Value".format(value_type.__name__.capitalize())

    # If the necessary class type already exists in the globals: Return it
    if class_name in globals():
        new_nc_value_class = globals()[class_name]

    # If it doesn't exist in the globals yet: Create necessary class type
    else:
        new_nc_value_class = _create_metadata_val_class(value_type)

        # Set the class name so it's not "new_nc_value_class" for all types!
        new_nc_value_class.__name__ = class_name
        # Add the new type to the globals
        globals()[class_name] = new_nc_value_class

    # Create a new instance of the specified type with given in_val & metadata
    return_value = new_nc_value_class(in_val)

    # These attributes can't be included in the class init above. The NcValue
    # classes mimic a regular built-in type, which does not accept other args:
    # >>>> "int() takes at most 2 arguments (3 given)"
    return_value.metadata = metadata
    return_value.created_by_user = created_by_user

    return return_value


# NODE CALCULATOR VALUE CLASS CREATIONS ---
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
        class_type (any builtin-type): Type to create a new NcValue-class for.

    Returns:
        NcValueClass: New class constructor for a NcValue class of appropriate
            type to match given class_type
    """
    # Can't inherit bool (TypeError: 'bool' not acceptable base type).
    if class_type is bool:
        # Redirect bool to integer!
        class_type = int

    class NcValueClass(class_type, NcValue):
        """Shapeshifter class that becomes overloaded form of the given type.

        Note:
            Only the attributes .metadata and .created_by_user are added by
            default. However: Any attribute can be added to an NcValueClass-
            instance.

        Example:
            ::

                (pseudo-code)
                int_nc_value_class = NcValueClass(int)
                my_int = int_nc_value_class(7)
                my_int.is_odd = True  # This would be impossible with regular int.
        """

        def __init__(self, *args, **kwargs):
            """Leave the init method unchanged."""
            class_type.__init__(self, *args, **kwargs)

        @property
        def basetype(self):
            """Access the base type this particular NcValueClass is based on.

            Returns:
                builtin-type: Type which this class is derived from.
            """
            return class_type

        @property
        def _value(self):
            """Get the held value as an instance of the basetype.

            Note:
                This property exists, because "self" in operations causes loop!

            Returns:
                builtin-type: Held value cast to its basetype.
            """
            return self.basetype(self)

        def __add__(self, other):
            """Regular addition operator + .

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("add", self, other)
            val = self._value + other
            return value(val, metadata=metadata, created_by_user=False)

        def __radd__(self, other):
            """Reflected addition operator + .

            Note:
                Fall-back method in case regular addition isn't defined/fails.

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("add", other, self)
            val = other + self._value
            return value(val, metadata=metadata, created_by_user=False)

        def __sub__(self, other):
            """Regular subtraction operator - .

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("sub", self, other)
            val = self._value - other
            return value(val, metadata=metadata, created_by_user=False)

        def __rsub__(self, other):
            """Reflected subtraction operator - .

            Note:
                Fall-back method in case regular sub isn't defined/fails.

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("sub", other, self)
            val = other - self._value
            return value(val, metadata=metadata, created_by_user=False)

        def __mul__(self, other):
            """Regular multiplication operator * .

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("mul", self, other)
            val = self._value * other
            return value(val, metadata=metadata, created_by_user=False)

        def __rmul__(self, other):
            """Reflected multiplication operator * .

            Note:
                Fall-back method in case regular mult isn't defined/fails.

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("mul", other, self)
            val = other * self._value
            return value(val, metadata=metadata, created_by_user=False)

        def __div__(self, other):
            """Regular division operator / .

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("div", self, other)
            val = self._value / other
            return value(val, metadata=metadata, created_by_user=False)

        def __rdiv__(self, other):
            """Reflected division operator / .

            Note:
                Fall-back method in case regular division isn't defined/fails.

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("div", other, self)
            val = other / self._value
            return value(val, metadata=metadata, created_by_user=False)

        def __pow__(self, other):
            """Power operator ^ .

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("pow", self, other)
            val = self._value ** other
            return value(val, metadata=metadata, created_by_user=False)

        def __eq__(self, other):
            """Equality operator: == .

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("eq", self, other)
            val = self._value == other
            return value(val, metadata=metadata, created_by_user=False)

        def __ne__(self, other):
            """Inequality operator: != .

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("ne", self, other)
            val = self._value != other
            return value(val, metadata=metadata, created_by_user=False)

        def __gt__(self, other):
            """Greater than operator: > .

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("gt", self, other)
            val = self._value > other
            return value(val, metadata=metadata, created_by_user=False)

        def __ge__(self, other):
            """Greater equal operator: >= .

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("ge", self, other)
            val = self._value >= other
            return value(val, metadata=metadata, created_by_user=False)

        def __lt__(self, other):
            """Less than operator: < .

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("lt", self, other)
            val = self._value < other
            return value(val, metadata=metadata, created_by_user=False)

        def __le__(self, other):
            """Less equal operator: <= .

            Returns:
                NcValue: Result of calculation with concatenated metadata to
                    preserve origin of values.
            """
            metadata = _concatenate_metadata("le", self, other)
            val = self._value <= other
            return value(val, metadata=metadata, created_by_user=False)

    return NcValueClass


def _concatenate_metadata(operator, input_a, input_b):
    """Concatenate the metadata for the given NcValue(s).

    Note:
        Check docString of this module for more detail why this is important.

    Args:
        operator (str): Name of the operator sign to be used for concatenation
        input_a (NcValue or int or float or bool): First part of the operation
        input_b (NcValue or int or float or bool): Second part of the operation

    Returns:
        str: Concatenated metadata for performed operation.

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
    LOG.debug("_concatenate_metadata (%s, %s, %s)", operator, input_a, input_b)

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
            input_a = "({0})".format(input_a)
        if associative_pattern.sub('', str(input_b)):
            input_b = "({0})".format(input_b)

    # Concatenate the return metadata
    return_metadata = "{0} {1} {2}".format(input_a, operator_symbol, input_b)

    return return_metadata
