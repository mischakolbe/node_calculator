"""
Create a node-network by entering a math-formula.


a1 = noca.new("A")
print a1, type(a1)

a2 = noca.new("A", ["tx"])
print a2, type(a2)

a3 = noca.new("A", ["tx", "ty"])
print a3, type(a3)

b = noca.new(2)
print b, type(b)

c = noca.new(["A", "B"])
print c, type(c)


Node or Attrs instance:
node -> returns str of Maya node
attrs -> returns Attrs-instance
attrs_list -> returns list of attributes in Attrs
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import numbers

# Third party imports
from maya import cmds

# Local imports
from . import logger
reload(logger)
from . import lookup_tables
reload(lookup_tables)
import om_util
reload(om_util)
import metadata_values
reload(metadata_values)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP LOGGER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
logger.clear_handlers()
logger.setup_stream_handler(level=logger.logging.DEBUG)
log = logger.log


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PYTHON 2.7 & 3 COMPATIBILITY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
try:
    basestring
except NameError:
    basestring = str


def new(*args):
    """
    Create a new node_calculator instance automatically, based on given args
    """
    if not args:
        # Should this return a BaseNode?...
        log.error("new: No arguments given!")

    # Redirect plain values right away to a metadata_value
    if isinstance(args[0], numbers.Real):
        log.debug("new: Redirecting to Value({})".format(*args))
        return metadata_values.val(*args)

    # Redirect lists or tuples right away to a Collection
    if isinstance(args[0], (list, tuple)):
        log.debug("new: Redirecting to Collection({})".format(*args))
        return Collection(*args)

    log.debug("new: Redirecting to Node({})".format(*args))
    return Node(*args)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ATOM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Atom(object):
    """
    Base class for Node and Attrs.
    Once instantiated this class will have access to the .node and .attrs attributes.
    Therefore all connections and operations on a Node can live in here.
    """

    def __init__(self):
        super(Atom, self).__init__()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# BaseNode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class BaseNode(Atom):

    def __init__(self):
        self.__dict__["_holder_node"] = None
        self.__dict__["_held_attrs"] = None

    def __len__(self):
        log.debug("BaseNode __len__ ({})".format(self))
        return len(self.attrs_list)

    def as_str(self):
        """
        Using the __unicode__ method in Attrs class somehow doesn't work well
        with the __getitem__ method together. Still don't know why...

        To make cmds.setAttr(a2.attrs, 1) work:
        - Specifically returning a unicode/str in attrs-@property of Node class works.
        - Commenting out __getitem__ method in Attrs class works, too but throws this error:
            # Error: Problem calling __apiobject__ method of passed object #
            # Error: attribute of type 'Attrs' is not callable #
        """
        if len(self.attrs) == 0:
            return_str = self.node
        elif len(self.attrs) == 1:
            return_str = "{}.{}".format(self.node, self.attrs_list[0])
        else:
            return_str = "{}, {}".format(self.node, self.attrs_list)

        return return_str

    def as_list(self):
        """
        Using the __unicode__ method in Attrs class somehow doesn't work well
        with the __getitem__ method together. Still don't know why...

        To make cmds.setAttr(a2.attrs, 1) work:
        - Specifically returning a unicode/str in attrs-@property of Node class works.
        - Commenting out __getitem__ method in Attrs class works, too but throws this error:
            # Error: Problem calling __apiobject__ method of passed object #
            # Error: attribute of type 'Attrs' is not callable #
        """
        if len(self.attrs) == 0:
            return_list = [self.node]
        elif len(self.attrs) == 1:
            return_list = ["{}.{}".format(self.node, self.attrs_list[0])]
        else:
            return_list = [
                "{}.{}".format(self.node, attr) for attr in self.attrs_list
            ]

        return return_list


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ATTRS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Attrs(BaseNode):
    """
    """

    def __init__(self, holder_node, attrs):
        log.debug("Attrs __init__ ({}, {})".format(holder_node, attrs))
        self.__dict__["_holder_node"] = holder_node

        if isinstance(attrs, basestring):
            self.__dict__["_held_attrs_list"] = [attrs]
        else:
            self.__dict__["_held_attrs_list"] = attrs

    @property
    def node(self):
        # log.debug("Attrs @property node")
        return self._holder_node.node

    @property
    def attrs(self):
        # log.debug("Attrs @property attrs")
        return self

    @property
    def attrs_list(self):
        return self._held_attrs_list

    def __str__(self):
        """
        For example for print(Node-instance)
        """
        log.debug("Attrs __str__ ({}, {})".format(self.node, self.attrs_list))

        return "Attrs({})".format(self.attrs_list)

    def __repr__(self):
        """
        For example for running highlighted Node-instance
        """
        log.debug("Attrs __repr__ ({}, {})".format(self.node, self.attrs_list))

        return "Attrs({})".format(self.attrs_list)

    def __unicode__(self):
        """
        For example for cmds.setAttr(Node-instance)
        """
        log.debug("Attrs __unicode__ ({}, {})".format(self.node, self.attrs_list))

        if len(self.attrs_list) == 0:
            return_value = self.node
        elif len(self.attrs_list) == 1:
            return_value = "{}.{}".format(self.node, self.attrs_list[0])
        else:
            return_value = "{}, {}".format(self.node, self.attrs_list)

        return return_value

    def __getattr__(self, name):
        log.debug("Attrs __getattr__ ({})".format(name))

        if len(self.attrs_list) != 1:
            log.error("Tried to get attr of non-singular attribute: {}".format(self.attrs_list))

        return Attrs(self._holder_node, self.attrs_list[0] + "." + name)

    def __setattr__(self, name, value):
        log.debug("Attrs __setattr__ ({})".format(name, value))

        _set_or_connect_a_to_b(self.__getattr__(name), value)

    def __getitem__(self, index):
        """
        Support indexed assignments for Node-instances with list-attrs

        Args:
            index (int): Index of item to be set
            value (Node, str, int, float): desired value for the given index
        """
        log.debug("Attrs __getitem__ ({})".format(index))

        return Attrs(self._holder_node, self.attrs_list[index])

    def __setitem__(self, index, value):
        log.debug("Attrs __setitem__ ({}, {})".format(index, value))

        if isinstance(value, numbers.Real):
            log.error(
                "Can't set Attrs item to number {}. Use a Value instance for this!".format(value)
            )
        self.attrs_list[index] = value


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NODE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Node(BaseNode):
    """
    """

    def __init__(self, node, attrs=None):
        log.debug("Node __init__ ({}, {})".format(node, attrs))

        # Plain values should be Value-instance!
        if isinstance(node, numbers.Real):
            log.error("Explicit Node __init__ with number ({}). Should be Value!".format(node))
            self.create_value(node)
            return None

        # Lists or tuples should be Collection!
        if isinstance(node, (list, tuple)):
            log.warning("Explicit Node __init__ with list or tuple ({}). Should be Collection!".format(node))
            Collection(node)
            return None

        super(Node, self).__init__()

        # Handle case where no attrs were given
        if attrs is None:
            # Initialization with "object.attrs" string
            if "." in node:
                node, attrs = node.split(".", 1)
            else:
                attrs = []

        # Make sure node truly is an mobj!
        if isinstance(node, Node):
            node_mobj = node._node_mobj
        else:
            node_mobj = om_util.get_mobj_of_node(node)

        # Using __dict__, because the setattr & getattr methods are overridden!
        self.__dict__["_node_mobj"] = node_mobj
        if isinstance(attrs, Attrs):
            self.__dict__["_held_attrs"] = attrs
        else:
            self.__dict__["_held_attrs"] = Attrs(self, attrs)

    def __str__(self):
        """
        For example for print(Node-instance)
        """
        log.debug("Node __str__ ({}, {})".format(self.node, self.attrs))

        return "Node(node: {}, attrs: {})".format(self.node, self.attrs)

    def __repr__(self):
        """
        For example for running highlighted Node-instance
        """
        log.debug("Node __repr__ ({}, {})".format(self.node, self.attrs))

        return "Node({}, {})".format(self.node, self.attrs)

    def __unicode__(self):
        """
        For example for cmds.setAttr(Node-instance)
        """
        log.debug("Node __unicode__ ({}, {})".format(self.node, self.attrs))

        return_value = self.node

        return return_value

    def __getattr__(self, name):
        log.debug("Node __getattr__ ({})".format(name))

        return Attrs(self, name)

    def __setattr__(self, name, value):
        log.debug("Node __setattr__ ({})".format(name, value))

        _set_or_connect_a_to_b(Node(self, name), value)

    def __getitem__(self, index):
        log.debug("Node __getitem__ ({})".format(index))

        return Node(self._node_mobj, self.attrs[0])

    def __setitem__(self, index, value):
        log.debug("Node __setitem__ ({}, {})".format(index, value))

        _set_or_connect_a_to_b(self[index], value)

    @property
    def attrs(self):
        return self._held_attrs

    @property
    def attrs_list(self):
        return self.attrs.attrs_list

    @property
    def node(self):
        # log.debug("Node @property node")
        return om_util.get_long_name_of_mobj(self._node_mobj)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# COLLECTION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Collection(Atom):

    def __init__(self, *args):
        super(Collection, self).__init__()

        # If arguments are given as a list: Unpack the items from it
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]

        collection_elements = []
        for arg in args:
            if isinstance(arg, (basestring, numbers.Real)):
                collection_elements.append(new(arg))
            elif isinstance(arg, (Node, Attrs, )) or "MetadataValue" in str(type(arg)):
                collection_elements.append(arg)
            else:
                log.error(
                    "Collection element {} is of unsupported type {}!".format(arg, type(arg))
                )

        self.elements = collection_elements

    def __str__(self):
        """
        For example for print(Node-instance)
        """
        log.debug("Collection __str__ ({})".format(self.elements))

        return "Collection({})".format(self.elements)

    def __repr__(self):
        """
        For example for running highlighted Node-instance
        """
        log.debug("Collection __repr__ ({})".format(self.elements))

        return "{}".format(self.elements)

    def __getitem__(self, index):
        log.debug("Collection __getitem__ ({})".format(index))

        return self.elements[index]

    def __setitem__(self, index, value):
        log.debug("Collection __setitem__ ({}, {})".format(index, value))

        self.elements[index] = value


# def _traced_create_node(operation, involved_attributes):
#     """
#     Maya-createNode that adds the executed command to the command_stack if Tracer is active
#     Creates a named node of appropriate type for the necessary operation
#     """
#     node_type = lookup_tables.NODE_LOOKUP_TABLE[operation]["node"]
#     node_name = _create_node_name(operation, involved_attributes)
#     new_node = cmds.ls(cmds.createNode(node_type, name=node_name), long=True)[0]

#     return new_node


# def _traced_set_attr(attr, value=None, **kwargs):
#     """
#     Maya-setAttr that adds the executed command to the command_stack if Tracer is active
#     """
#     if value is None:
#         cmds.setAttr(attr, edit=True, **kwargs)
#     else:
#         cmds.setAttr(attr, value, edit=True, **kwargs)


# def _traced_get_attr(attr):
#     """
#     Maya-getAttr that adds the executed command to the command_stack if Tracer is active,
#     Tweaked cmds.getAttr: Takes care of awkward return value of 3D-attributes
#     """
#     return_value = cmds.getAttr(attr)

#     return return_value


# def _traced_connect_attr(attr_a, attr_b):
#     """
#     Maya-connectAttr that adds the executed command to the command_stack if Tracer is active
#     """
#     cmds.connectAttr(attr_a, attr_b, force=True)


def _set_or_connect_a_to_b(obj_a, obj_b, **kwargs):
    """
    Generic function to set obj_a to value of obj_b OR connect obj_b to obj_a.

    Note:
        Allowed assignments are:
        (1-D stands for 1-dimensional, X-D for multi-dimensional; 2-D, 3-D, ...)
        Setting 1-D attribute to a 1-D value/attr  # pCube1.tx = 7
        Setting X-D attribute to a 1-D value/attr  # pCube1.t = 7  # same as pCube1.t = [7]*3
        Setting X-D attribute to a X-D value/attr  # pCube1.t = [1, 2, 3]

    Args:
        obj_a (Node, str): Needs to be a plug. Either as a Node-object or as a string ("node.attr")
        obj_b (Node, int, float, list, tuple, string): Can be a numeric value, a list of values
            or another plug either in the form of a Node-object or as a string ("node.attr")
    """
    # #######################
    # Make sure inputs are ok to process
    log.debug('_set_or_connect_a_to_b({}, {}) - RAW INPUT'.format(obj_a, obj_b))

    return False
    '''
    # Make sure obj_a and obj_b aren't unspecified
    if obj_a is None:
        log.error("obj_a is unspecified!")
    if obj_b is None:
        log.error("obj_b is unspecified!")

    obj_a_unravelled_list = _get_unravelled_value_as_list(obj_a)
    obj_b_unravelled_list = _get_unravelled_value_as_list(obj_b)
    log.debug('obj_a_unravelled_list {} from obj_a {}'.format(obj_a_unravelled_list, obj_a))
    log.debug('obj_b_unravelled_list {} from obj_b {}'.format(obj_b_unravelled_list, obj_b))

    obj_a_dim = len(obj_a_unravelled_list)
    obj_b_dim = len(obj_b_unravelled_list)

    # Neither given object can have dimensionality (=list-length) above 3!
    if obj_a_dim > 3:
        log.error("Dimensionality of obj_a is higher than 3! {}".format(obj_a_unravelled_list))
    if obj_b_dim > 3:
        log.error("Dimensionality of obj_b is higher than 3! {}".format(obj_b_unravelled_list))
    # #######################
    # Match input-dimensions: After this block both obj_X_unravelled_list's have the same length

    # If the dimensions of both given attributes match: Don't process them
    if obj_a_dim == obj_b_dim:
        pass

    # If one object is a single value/plug; match the others length...
    elif obj_a_dim == 1 or obj_b_dim == 1:
        if obj_a_dim < obj_b_dim:
            # ...by creating a list with the same length
            log.debug("Matching obj_a_dim to obj_b_dim!")
            obj_a_unravelled_list = obj_a_unravelled_list * obj_b_dim
        else:
            log.debug("Matching obj_b_dim to obj_a_dim!")
            obj_b_unravelled_list = obj_b_unravelled_list * obj_a_dim
    else:
        # Any other dimension-pairings are not allowed
        log.error(
            "Due to dimensions there is no reasonable way to connect "
            "{}D: {} > to > {}D: {}".format(
                obj_a_dim, obj_a_unravelled_list,
                obj_b_dim, obj_b_unravelled_list,
            )
        )
        return False

    # #######################
    # Connect or set attributes, based on whether a value or attribute is given

    # A 3D to 3D connection can be 1 connection if both have a parent-attribute!
    reduced_obj_a_list = _check_for_parent_attribute(obj_a_unravelled_list)
    reduced_obj_b_list = _check_for_parent_attribute(obj_b_unravelled_list)
    # Only reduce the connection if BOTH objects have a parent-attribute!
    # A 1D attr can not connect to a 3D attr!
    if reduced_obj_a_list is not None and reduced_obj_b_list is not None:
        obj_a_unravelled_list = reduced_obj_a_list
        obj_b_unravelled_list = reduced_obj_b_list

    log.debug("obj_a_unravelled_list: {}".format(obj_a_unravelled_list))
    log.debug("obj_b_unravelled_list: {}".format(obj_b_unravelled_list))
    for obj_a_item, obj_b_item in zip(obj_a_unravelled_list, obj_b_unravelled_list):
        # Make sure obj_a_item exists in the Maya scene and get its dimensionality
        if not cmds.objExists(obj_a_item):
            log.error("obj_a_item does not exist: {}. Must be Maya-attr!".format(obj_a_item))

        # If obj_b_item is a simple number...
        if isinstance(obj_b_item, numbers.Real):
            # # ...set 1-D obj_a_item to 1-D obj_b_item-value.
            _traced_set_attr(obj_a_item, obj_b_item, **kwargs)

        # If obj_b_item is a valid attribute in the Maya scene...
        elif _is_valid_maya_attr(obj_b_item):
            #  ...connect it.
            _traced_connect_attr(obj_b_item, obj_a_item)

        # If obj_b_item didn't match anything; obj_b_item-type is not recognized/supported.
        else:
            msg = "Cannot set obj_b_item: {1} because of unknown type: {0}".format(
                obj_b_item,
                type(obj_b_item),
            )
            log.error(msg)
    '''

# # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# # UNRAVELLING INPUTS
# # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# def _get_unravelled_value_as_list(input_val):
#     """
#     Return a clean list of values or plugs

#     Args:
#         input_val (int, float, list, Node): input to be unravelled and returned as list

#     Returns:
#         list with values and (direct, ie all 1D-) plugs
#     """
#     log.debug("About to unravel >{0}< with {1}".format(input_val, type(input_val)))

#     unravelled_input = _get_unravelled_value(input_val)
#     if not isinstance(unravelled_input, list):
#         unravelled_input = [unravelled_input]

#     log.info("Input >{0}< --> unravelled to >{1}<".format(input_val, unravelled_input))

#     return unravelled_input
