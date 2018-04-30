class Test(object):

    def __init__(self, node, attr):
        self.node = node
        self.attr = attr

    def __str__(self):
        print "Running str"

        return_value = "{}.{}".format(self.node, self.attr)
        return return_value

    def __repr__(self):
        print "Running repr"

        return_value = "{}.{}".format(self.node, self.attr)
        return return_value

    def __unicode__(self):
        print "Running unicode"

        return_value = "{}.{}".format(self.node, self.attr)
        return return_value



e = Test("A", "tx")

cmds.setAttr(e, 2)
