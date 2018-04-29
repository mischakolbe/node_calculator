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

        def __getattr__(self, name):
            log.error("{} __getattr__ undefined!".format(class_type))

        def __setattr__(self, name, value):
            log.error("{} __setattr__ undefined!".format(class_type))

        def __getitem__(self, index):
            log.error("{} __getitem__ undefined!".format(class_type))

        def __setitem__(self, index, value):
            log.error("{} __setitem__ undefined!".format(class_type))

        @property
        def basetype(self):
            """ Convenience property to access the base type easily """
            return class_type

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
