"""
Module with overloaded base types (int, str, float, ...) that allow storing metadata

"""


def create_class(class_type):
    """
    Closure to create classes for all types
    """
    # Can't inherit bool: TypeError: type 'bool' is not an acceptable base type
    if class_type is bool:
        # Redirecting bool to an integer
        class_type = int
    # if class_type is list:
    class NewClass(class_type):
        def __new__(self, value, metadata):
            return class_type.__new__(self, value)

        def __init__(self, value, metadata):
            class_type.__init__(value)
            self.metadata = metadata

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

    print ReturnClass
    print value
    # Return a new instance of the specified type with the given value and metadata
    return_value = ReturnClass(value, metadata)
    print return_value

    return return_value


# for i, test in enumerate([1.0, 1, "abc", {}, [], False][:], 1):
#     new = var(test, "aaa"*i)
#     new_base_type = new.__class__.__bases__[0]

#     print(new, new.metadata, type(new))
#     print("TypeCheck", type(test) is new_base_type)
#     print
# l = [1, 2, 3]
# print l.immutable()
# a = var([1, 2, 3])
# print(a)

