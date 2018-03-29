"""
Module with overloaded base types (int, str, float, ...) that allow storing metadata

"""

classes_to_create = {
    float: "FloatVar",
    int: "IntVar",
    str: "StrVar",
    list: "ListVar",
    dict: "DictVar",
}


def create_class(class_name, class_type):
    """
    Closure to create classes for all types
    """
    class NewClass(class_type):
        # Setting __name__ allows to use the variable class_name as the actual name for the class
        __name__ = class_name

        def __new__(self, value, metadata):
            return class_type.__new__(self, value)

        def __init__(self, value, metadata):
            class_type.__init__(value)
            self.metadata = metadata

    return NewClass


# Create classes via closure and add them to the globals scope with the desired class_name
for class_type, class_name in classes_to_create.iteritems():
    globals()[class_name] = create_class(class_name, class_type)


def var(value, metadata=""):
    value_type = type(value)

    if value_type is bool:
        # Booleans are singleton and can't be subclassed. Redirect to int!
        ReturnClass = globals()[classes_to_create[int]]

    elif value_type in classes_to_create:
        # If it's a supported value type: Set the ReturnClass to the appropriate type
        ReturnClass = globals()[classes_to_create[value_type]]

    else:
        # Error if the given value-type is not supported
        print("NONONO!")
        return False

    # Return a new instance of the specified type with the given value and metadata
    return ReturnClass(value, metadata)
