# ATTRS
# NewAttrs would need to be aware of holding NewNode, otherwise the setitem can not act as a setAttr for the node with attr!

try:
    basestring
except NameError:
    basestring = str

import numbers

# Local imports
import logger
reload(logger)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP LOGGER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
logger.clear_handlers()
logger.setup_stream_handler(level=logger.logging.WARN)
log = logger.log


class Atom(object):
    def __init__(self):
        super(Atom, self).__init__()

    def connect_something(self):
        print("Connecting node {} with attrs {}".format(self.node, self.attrs))


class NewAttrs(Atom):
    """
    Could have subclassed list, but need to replace most magic methods anyways, so...
    """

    def __init__(self, holder_node, attrs):
        # super(TheAttr, self).__init__()
        self.holder_node = holder_node

        if isinstance(attrs, basestring):
            self.attrs = [attrs]
        else:
            self.attrs = attrs

    @property
    def node(self):
        return self.holder_node.node

    def __repr__(self):
        """
        Repr-method for debugging purposes

        Returns:
            String of separate elements that make up Node-instance
        """
        log.debug("Attrs repr method with self")

        return str(self.attrs)

    def __str__(self):
        """
        Pretty print of Attrs class

        Returns:
            String of concatenated attrs-attributes
        """
        log.debug("Attrs str method with self")

        return str(self.attrs)

    def __setitem__(self, index, value):
        """
        Support indexed assignments for NewNode-instances with list-attrs

        Args:
            index (int): Index of item to be set
            value (NewNode, str, int, float): desired value for the given index
        """
        log.debug("Attrs setitem method with index {} & value {}".format(index, value))

        self.attrs[index] = value

    def __getitem__(self, index):
        """
        Support indexed lookup for NewNode-instances with list-attrs

        Args:
            index (int): Index of desired item

        Returns:
            Object that is at the desired index
        """
        log.debug("Attrs getitem method with index {}".format(index))

        return NewNode(self.node, self.attrs[index])


class NewNode(Atom):
    def __init__(self, node, attrs=None):

        if isinstance(node, numbers.Real):
            log.warning("Redirecting from NewNode to metadata_values: {}".format(node))
            return

        super(NewNode, self).__init__()

        # node should be MObject!

        self.node = node

        if attrs is None:
            self.attrs = NewAttrs(self, [])
        else:
            self.attrs = NewAttrs(self, attrs)


a = NewNode("pCube", ["tx", "sx", "poop"])

print("a:", a, type(a))
print("a.node:", a.node, type(a.node))
print("a.attrs:", a.attrs, type(a.attrs))
print("a.attrs.node:", a.attrs.node, type(a.attrs.node))
print

b = a.attrs[1:3]
print("b:", b, type(b))
print("b.node:", b.node, type(b.node))
print("b.attrs:", b.attrs, type(b.attrs))
print("b.attrs.node:", b.attrs.node, type(b.attrs.node))

print
a.connect_something()

a.attrs[0].connect_something()

print

c = NewNode(7.3)
