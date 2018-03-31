"""
Module with overloaded base types (int, str, float, ...) that allow storing metadata

"""


def create_class(class_type):
    """
    Closure to create classes for all types
    """
    # Inheritance for dictionaries are complicated: Can't catch metadata easily!
    if class_type is dict:
        raise NotImplementedError("MetaVariables can NOT be dictionary!")

    # Can't inherit bool: TypeError: type 'bool' is not an acceptable base type
    if class_type is bool:
        # Redirecting bool to an integer
        class_type = int

    # If dealing with hashable types: Override __new__
    if class_type.__hash__:
        # int, str, float, ... are hashable (= immutable for our purposes)
        class NewClass(class_type):
            def __new__(self, value, metadata):
                return class_type.__new__(self, value)

            def __init__(self, value, metadata):
                class_type.__init__(value)
                self.metadata = metadata

            @property
            def basetype(self):
                return class_type

    else:
        class NewClass(class_type):
            def __init__(self, args, metadata):
                class_type.__init__(self, args)
                self.metadata = metadata

            @property
            def basetype(self):
                return class_type

    return NewClass


def var(value, metadata=""):
    value_type = type(value)

    class_name = "{}Var".format(value_type.__name__.capitalize())
    if class_name not in globals():
        # Create a new instance of the
        ReturnClass = create_class(value_type)
        # Setting __name__ allows to use the variable class_name as the actual name for the class
        ReturnClass.__name__ = class_name
        globals()[class_name] = ReturnClass
    else:
        ReturnClass = globals()[class_name]

    # Return a new instance of the specified type with the given value and metadata
    return_value = ReturnClass(value, metadata)
    # return_value.metadata = "asdfasdf"

    return return_value


# a = var(1, "bla")
# print a
# print a.metadata
