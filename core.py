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

    def unifriggincode(self):
        """
        Using the __unicode__ method in Attrs class somehow doesn't work well
        with the __getitem__ method together. Still don't know why...
        """
        if len(self.attrs) == 0:
            return "{}".format(self.node)
        elif len(self.attrs) > 1:
            return "{}, {}".format(self.node, self.attrs)
        return "{}.{}".format(self.node, self.attrs[0])

    def __init__(self):
        self.__dict__["node"] = None
        self.__dict__["_held_attrs"] = None

    def __len__(self):
        log.debug("BaseNode __len__ for ({})".format(self.attrs))
        return len(self.attrs)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ATTRS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Attrs(BaseNode):
    """
    """

    def __init__(self, holder_node, attrs):
        log.debug("Attrs __init__ ({}, {})".format(holder_node, attrs))
        self._holder_node = holder_node

        if isinstance(attrs, basestring):
            self._held_attrs = [attrs]
        else:
            self._held_attrs = attrs

    @property
    def node(self):
        # log.debug("Attrs @property node")
        return self._holder_node.node

    @property
    def attrs(self):
        # log.debug("Attrs @property attrs")
        return self._held_attrs

    def __str__(self):
        """
        For example for print(Node-instance)
        """
        log.debug("Attrs __str__ ({}, {})".format(self.node, self.attrs))

        return "Attrs({})".format(self.attrs)

    def __repr__(self):
        """
        For example for running highlighted Node-instance
        """
        log.debug("Attrs __repr__ ({}, {})".format(self.node, self.attrs))

        return "Attrs({})".format(self.attrs)

    def __getitem__(self, index):
        """
        Support indexed assignments for Node-instances with list-attrs

        Args:
            index (int): Index of item to be set
            value (Node, str, int, float): desired value for the given index
        """
        log.debug("Attrs __getitem__ ({})".format(index))

        return Attrs(self._holder_node, self._held_attrs[index])

    def __getattr__(self, name):
        log.debug("Attrs __getattr__ ({})".format(name))

        if len(self._held_attrs) != 1:
            log.error("Tried to get attr of non-singular attribute: {}".format(self._held_attrs))

        return Attrs(self._holder_node, self._held_attrs[0] + "." + name)

    def __unicode__(self):
        """
        For example for cmds.setAttr(Node-instance)
        """
        log.debug("Attrs __unicode__ ({}, {})".format(self.node, self.attrs))

        if len(self.attrs) == 0:
            return_value = self.node
        elif len(self.attrs) == 1:
            return_value = "{}.{}".format(self.node, self.attrs[0])
        else:
            return_value = "{}, {}".format(self.node, self.attrs)

        return return_value


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NODE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Node(BaseNode):
    """
    """

    def __init__(self, node_mobj, attrs=None):
        log.debug("Node __init__ ({}, {})".format(node_mobj, attrs))

        # Plain values should be Value-instance!
        if isinstance(node_mobj, numbers.Real):
            log.error("Explicit Node __init__ with number ({}). Should be Value!".format(node_mobj))
            self.create_value(node_mobj)
            return None

        # Lists or tuples should be Collection!
        if isinstance(node_mobj, (list, tuple)):
            log.warning("Explicit Node __init__ with list or tuple ({}). Should be Collection!".format(node_mobj))
            Collection(node_mobj)
            return None

        super(Node, self).__init__()

        # Handle case where no attrs were given
        if attrs is None:
            # Initialization with "object.attrs" string
            if "." in node_mobj:
                node_mobj, attrs = node_mobj.split(".", 1)
            else:
                attrs = []

        # Make sure node_mobj truly is an mobj!
        node_mobj = om_util.get_mobj_of_node(node_mobj)

        # Using __dict__, because the setattr & getattr methods are overridden!
        self.__dict__["node_mobj"] = node_mobj
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

    @property
    def attrs(self):
        # log.debug("Node @property attrs")
        # This exception is necessary for during the Node-initialization:
        # The _held_attrs is None when undefined. debug-messages might error.
        # if self._held_attrs is None:
        #     return None
        return self._held_attrs

    @property
    def node(self):
        # log.debug("Node @property node")
        return om_util.get_long_name_of_mobj(self.node_mobj)


# # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# # COLLECTION
# # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Collection(Atom):

    def __init__(self, *args):
        super(Collection, self).__init__()

        self.elements = args


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


# def _set_or_connect_a_to_b(obj_a, obj_b, **kwargs):
#     """
#     Generic function to set obj_a to value of obj_b OR connect obj_b to obj_a.

#     Note:
#         Allowed assignments are:
#         (1-D stands for 1-dimensional, X-D for multi-dimensional; 2-D, 3-D, ...)
#         Setting 1-D attribute to a 1-D value/attr  # pCube1.tx = 7
#         Setting X-D attribute to a 1-D value/attr  # pCube1.t = 7  # same as pCube1.t = [7]*3
#         Setting X-D attribute to a X-D value/attr  # pCube1.t = [1, 2, 3]

#     Args:
#         obj_a (Node, str): Needs to be a plug. Either as a Node-object or as a string ("node.attr")
#         obj_b (Node, int, float, list, tuple, string): Can be a numeric value, a list of values
#             or another plug either in the form of a Node-object or as a string ("node.attr")
#     """
#     # #######################
#     # Make sure inputs are ok to process
#     log.debug('_set_or_connect_a_to_b({}, {}) - RAW INPUT'.format(obj_a, obj_b))

#     # Make sure obj_a and obj_b aren't unspecified
#     if obj_a is None:
#         log.error("obj_a is unspecified!")
#     if obj_b is None:
#         log.error("obj_b is unspecified!")

#     obj_a_unravelled_list = _get_unravelled_value_as_list(obj_a)
#     obj_b_unravelled_list = _get_unravelled_value_as_list(obj_b)
#     log.debug('obj_a_unravelled_list {} from obj_a {}'.format(obj_a_unravelled_list, obj_a))
#     log.debug('obj_b_unravelled_list {} from obj_b {}'.format(obj_b_unravelled_list, obj_b))

#     obj_a_dim = len(obj_a_unravelled_list)
#     obj_b_dim = len(obj_b_unravelled_list)

#     # Neither given object can have dimensionality (=list-length) above 3!
#     if obj_a_dim > 3:
#         log.error("Dimensionality of obj_a is higher than 3! {}".format(obj_a_unravelled_list))
#     if obj_b_dim > 3:
#         log.error("Dimensionality of obj_b is higher than 3! {}".format(obj_b_unravelled_list))
#     # #######################
#     # Match input-dimensions: After this block both obj_X_unravelled_list's have the same length

#     # If the dimensions of both given attributes match: Don't process them
#     if obj_a_dim == obj_b_dim:
#         pass

#     # If one object is a single value/plug; match the others length...
#     elif obj_a_dim == 1 or obj_b_dim == 1:
#         if obj_a_dim < obj_b_dim:
#             # ...by creating a list with the same length
#             log.debug("Matching obj_a_dim to obj_b_dim!")
#             obj_a_unravelled_list = obj_a_unravelled_list * obj_b_dim
#         else:
#             log.debug("Matching obj_b_dim to obj_a_dim!")
#             obj_b_unravelled_list = obj_b_unravelled_list * obj_a_dim
#     else:
#         # Any other dimension-pairings are not allowed
#         log.error(
#             "Due to dimensions there is no reasonable way to connect "
#             "{}D: {} > to > {}D: {}".format(
#                 obj_a_dim, obj_a_unravelled_list,
#                 obj_b_dim, obj_b_unravelled_list,
#             )
#         )
#         return False

#     # #######################
#     # Connect or set attributes, based on whether a value or attribute is given

#     # A 3D to 3D connection can be 1 connection if both have a parent-attribute!
#     reduced_obj_a_list = _check_for_parent_attribute(obj_a_unravelled_list)
#     reduced_obj_b_list = _check_for_parent_attribute(obj_b_unravelled_list)
#     # Only reduce the connection if BOTH objects have a parent-attribute!
#     # A 1D attr can not connect to a 3D attr!
#     if reduced_obj_a_list is not None and reduced_obj_b_list is not None:
#         obj_a_unravelled_list = reduced_obj_a_list
#         obj_b_unravelled_list = reduced_obj_b_list

#     log.debug("obj_a_unravelled_list: {}".format(obj_a_unravelled_list))
#     log.debug("obj_b_unravelled_list: {}".format(obj_b_unravelled_list))
#     for obj_a_item, obj_b_item in zip(obj_a_unravelled_list, obj_b_unravelled_list):
#         # Make sure obj_a_item exists in the Maya scene and get its dimensionality
#         if not cmds.objExists(obj_a_item):
#             log.error("obj_a_item does not exist: {}. Must be Maya-attr!".format(obj_a_item))

#         # If obj_b_item is a simple number...
#         if isinstance(obj_b_item, numbers.Real):
#             # # ...set 1-D obj_a_item to 1-D obj_b_item-value.
#             _traced_set_attr(obj_a_item, obj_b_item, **kwargs)

#         # If obj_b_item is a valid attribute in the Maya scene...
#         elif _is_valid_maya_attr(obj_b_item):
#             #  ...connect it.
#             _traced_connect_attr(obj_b_item, obj_a_item)

#         # If obj_b_item didn't match anything; obj_b_item-type is not recognized/supported.
#         else:
#             msg = "Cannot set obj_b_item: {1} because of unknown type: {0}".format(
#                 obj_b_item,
#                 type(obj_b_item),
#             )
#             log.error(msg)


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
