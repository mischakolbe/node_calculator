for class_type in [float]:

    class class_name(class_type):
        def __new__(self, value, metadata):
            return class_type.__new__(self, value)

        def __init__(self, value, metadata):
            class_type.__init__(value)
            self.metadata = metadata


#     print class_name
class FloatVar(float):
    def __new__(self, value, metadata):
        return float.__new__(self, value)

    def __init__(self, value, metadata):
        float.__init__(value)
        self.metadata = metadata


class IntVar(int):
    def __new__(self, value, metadata):
        return int.__new__(self, value)

    def __init__(self, value, metadata):
        int.__init__(value)
        self.metadata = metadata


class StrVar(str):
    def __new__(self, value, metadata):
        return str.__new__(self, value)

    def __init__(self, value, metadata):
        str.__init__(value)
        self.metadata = metadata


class Var(object):
    """
    Init not needed, since CREATION of Var is redirecting to a subclass for that type.
    The INSTANTIATION happens of that sub-class, not this Var-class!
    """

    def __new__(self, value, metadata=""):
        value_type = type(value)

        if value_type is float:
            return FloatVar(value, metadata)
        elif value_type is int or value_type is bool:
            return IntVar(value, metadata)
        elif value_type is str:
            return StrVar(value, metadata)
        else:
            print(
                "ERROR: Var instance cannot be created for value {} of type {}".format(
                    value,
                    value_type
                )
            )
            return False


def testDef():
    for i, value in enumerate([2.0, 2, True, "a string"], 1):
        a_test = Var(value, "bla"*i)
        print("value & type:", value, type(value))
        print("metadata:", a_test.metadata)
        print("type:", type(a_test))
        print("isinstance(float):", isinstance(a_test, float))
        print("isinstance(int):", isinstance(a_test, int))
        print("isinstance(str):", isinstance(a_test, str))
        print("baseType: ", type(a_test).__bases__[0])
        print


testDef()


a = Var(2)
b = Var("lululu")

print (a*b)
