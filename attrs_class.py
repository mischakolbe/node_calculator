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

import om_util
reload(om_util)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP LOGGER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
logger.clear_handlers()
logger.setup_stream_handler(level=logger.logging.WARN)
log = logger.log


class Atom(object):
    """
    Base class for Node and Attrs.
    Once instantiated this class will have access to the .node and .attrs attributes.
    Therefore all connections and operations on a Node can live in here.
    """

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
        """
        log.debug("Attrs repr method with self")

        return self.attrs

    def __str__(self):
        """
        Pretty print of Attrs class
        """
        log.debug("Attrs str method with self")

        return str(self.attrs)

    def __setitem__(self, index, value):
        """
        Support indexed assignments for NewNode-instances with list-attrs
        """
        log.debug("Attrs setitem method with index {} & value {}".format(index, value))

        self.attrs[index] = value

    def __getitem__(self, index):
        """
        Support indexed lookup for NewNode-instances with list-attrs
        """
        log.debug("Attrs getitem method with index {}".format(index))

        return NewNode(self.holder_node.mobj, self.attrs[index])


class NewNode(Atom):
    """
    Since new node is directly set up using the given nodes MObject it's no longer
    possible to create noca.Nodes without the Maya nodes existing(!)
    This was not very sensible anyways, because as soon as operations on that node
    are performed that node MUST exist anyways (plug-connections, etc.)

        Note:
        Each Node-object has a mandatory node-attribute and an optional attrs-attribute.
        The attribute "attrs" is a keyword!!!
        Node().attrs returns the currently stored node/attrs-combo!
    """

    def __init__(self, node_mobj, attrs=None):
        # Redirect plain values right away to a metadata_value
        if isinstance(node_mobj, numbers.Real):
            log.warning("Redirecting from NewNode to metadata_values: {}".format(node_mobj))
            # metadata_varlues.val(node_mobj)
            return

        super(NewNode, self).__init__()

        # Handle case where no attrs were given
        if attrs is None:
            # Initialization with "object.attrs" string
            if "." in node_mobj:
                node_mobj, attrs = node_mobj.split(".")
            else:
                attrs = []

        # Make sure node_mobj is an mobj indeed!
        node_mobj = om_util.get_mobj_of_node(node_mobj)

        # Initialize node and attrs instance variable
        # node should be MObject!
        # Using __dict__, because the setattr & getattr methods are overridden!
        self.__dict__["node_mobj"] = node_mobj
        self.__dict__["held_attrs"] = NewAttrs(self, attrs)

    @property
    def attrs(self):
        return self.held_attrs.attrs

    @property
    def node(self):
        return om_util.get_long_name_of_mobj(self.node_mobj)

    def __getitem__(self, index):
        """
        Support indexed lookup for NewNode-instances with list-attrs
        """
        log.debug("Attrs getitem method with index {}".format(index))

        return NewNode(self.node_mobj, self.attrs[index])

    def __repr__(self):
        """
        Repr-method for debugging purposes
        """
        log.debug("Attrs repr method with self")

        return "(> {}, {} <)".format(self.node, self.attrs)

    def __str__(self):
        """
        Pretty print of Attrs class
        """
        log.debug("Attrs str method with self")

        return "NewNode instance with node {} and attrs {}".format(self.node, self.attrs)

    def __setattr__(self, name, value):
        """
        Set or connect attribute (name) to the given value.
        """
        log.debug("Node setattr method with name {} & value {}".format(name, value))

        _set_or_connect_a_to_b(self.__getattr__(name), value)

    def __getattr__(self, name):
        """
        A getattr of a Node-object returns a Node-object. Always returns a new
        Node-instance, EXCEPT when keyword "attrs" is used to return itself!

        __getattr__ does NOT get called if attribute already exists on Node:
        self.held_attrs does not call __getattr__!
        """
        log.debug("Node getattr method with name {}".format(name))

        if name == "attrs":
            if not len(self.attrs):
                log.warning("No attributes on requested Node-object! {}".format(self.node))
            return self
        else:
            return NewNode(self.node_mobj, name)

    def __setitem__(self, index, value):
        """
        Support indexed assignments for Node-instances with list-attrs

        Args:
            index (int): Index of item to be set
            value (Node, str, int, float): desired value for the given index
        """
        log.debug("Node setitem method with index {} & value {}".format(index, value))

        _set_or_connect_a_to_b(NewNode(self.node_mobj, self.attrs[index]), value)
        # self.attrs[index] = value

    def rename(self, name):
        """
        Mostly for fun: Enabling the renaming of the Maya node.
        Currently not properly undoable!!
        """
        om_util.rename_mobj(self.node_mobj, name)


def _set_or_connect_a_to_b(obj_a, obj_b):
    print("Would set/connect {} to {}".format(obj_a, obj_b))


# node_a_name = "pCube1"
# node_a_attrs = ["tx", "rx", "ty"]
# noca_node_a = NewNode(node_a_name, node_a_attrs)
