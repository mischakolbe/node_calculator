"""
Module with custom base types (int, str, float, ...) that allow storing metadata

Creating a child-class for each variable type allows to store metadata on variables.
For example:
DOES NOT WORK:
a = 1
a.metadata = "metadata"
AttributeError: 'int' object has no attribute 'metadata'

WORKS:
a = var(1)
a.metadata = "metadata"
print a.metadata
>>> "metadata"
print a
>>> 1
print a.basetype
>>> <type 'int'>
"""


def create_metadata_var_class(class_type):
    """
    Closure to create classes for all types
    """
    # Can't inherit bool (TypeError: 'bool' not acceptable base type). Redirect to integer!
    if class_type is bool:
        class_type = int

    class MetadataVarOfGivenType(class_type):
        def __init__(self, *args, **kwargs):
            """ Leave the init method unchanged """
            class_type.__init__(self, *args, **kwargs)

        @property
        def basetype(self):
            """ Convenience property to access the base type easily """
            return class_type

    return MetadataVarOfGivenType


def var(value, metadata=""):
    # Construct the class name out of the type of the given value
    class_name = "{}MetadataVar".format(type(value).__name__.capitalize())

    if class_name not in globals():
        # If the necessary class type doesn't exist in the globals yet: Create it
        ReturnClass = create_metadata_var_class(type(value))

        # Setting __name__ sets the class name so it's not "ReturnClass" for all types!
        ReturnClass.__name__ = class_name
        # Add the new type to the globals
        globals()[class_name] = ReturnClass

    else:
        # If the necessary class type already exists: Return it from the globals
        ReturnClass = globals()[class_name]

    # Create a new instance of the specified type with the given value and metadata
    return_value = ReturnClass(value)
    return_value.metadata = metadata

    return return_value
