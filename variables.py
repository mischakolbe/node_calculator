class FloatVar(float):
    def __new__(self, value, extra):
        return float.__new__(self, value)

    def __init__(self, value, extra):
        float.__init__(value)
        self.extra = extra


class IntVar(int):
    def __new__(self, value, extra):
        return int.__new__(self, value)

    def __init__(self, value, extra):
        int.__init__(value)
        self.extra = extra


class StrVar(str):
    def __new__(self, value, extra):
        return str.__new__(self, value)

    def __init__(self, value, extra):
        str.__init__(value)
        self.extra = extra


class Var(object):
    """
    Init not needed, since CREATION of Var is redirecting to a subclass for that type.
    The INSTANTIATION happens of that sub-class, not this Var-class!
    """

    def __new__(self, value, extra):
        value_type = type(value)

        if value_type is float:
            return FloatVar(value, extra)
        elif value_type is int:
            return IntVar(value, extra)
        elif value_type is str:
            return StrVar(value, extra)
        else:
            print(
                "ERROR: Var instance cannot be created for value {} of type {}".format(
                    value,
                    value_type
                )
            )
            return False


def testDef():

    for i, value in enumerate([2, 2.0, "ass"], 1):
        a_test = Var(value, "bla"*i)
        print("a_test.extra:", a_test.extra)
        print("type(a_test):", type(a_test))
        print("isinstance(a_test, float):", isinstance(a_test, float))
        print("isinstance(a_test, int):", isinstance(a_test, int))
        print


testDef()
