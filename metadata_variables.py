"""
Module to create variable of base types (int, str, float, ...) that allow storing metadata

Creating a child-class for each variable type allows to store metadata on variables.
For example:

DOES NOT WORK:
a = 1
a.metadata = "metadata"
AttributeError: 'int' object has no attribute 'metadata'

WORKS:
a = var(1, "metadata")
print a
>>> 1
print a.metadata
>>> "metadata"
print a.basetype
>>> <type 'int'>
a.maya_node = "pCube1"  # In fact: ANY attribute can be stored onto a(!)
print a.maya_node
>>> pCube1
"""


def create_metadata_var_class(class_type):
    """
    Closure to create classes for all types
    """
    # Can't inherit bool (TypeError: 'bool' not acceptable base type). Redirect to integer!
    if class_type is bool:
        class_type = int

    class MetadataVarClass(class_type):
        def __init__(self, *args, **kwargs):
            """ Leave the init method unchanged """
            class_type.__init__(self, *args, **kwargs)

        @property
        def basetype(self):
            """ Convenience property to access the base type easily """
            return class_type

    return MetadataVarClass


def var(value, metadata=None):
    # If a MetadataVar is passed on: Retrieve the basetype of it to make a new variable
    try:
        value_type = value.basetype
    except AttributeError:
        value_type = type(value)

    # Construct the class name out of the type of the given value
    class_name = "{}MetadataVar".format(value_type.__name__.capitalize())

    if class_name not in globals():
        # If the necessary class type doesn't exist in the globals yet: Create it
        MetadataVar = create_metadata_var_class(value_type)

        # Setting __name__ sets the class name so it's not "ReturnClass" for all types!
        MetadataVar.__name__ = class_name
        # Add the new type to the globals
        globals()[class_name] = MetadataVar

    else:
        # If the necessary class type already exists: Return it from the globals
        MetadataVar = globals()[class_name]

    # Create a new instance of the specified type with the given value and metadata
    return_value = MetadataVar(value)
    return_value.metadata = metadata

    return return_value
