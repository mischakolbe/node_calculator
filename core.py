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


def new(item, attrs=None, prevent_unravelling=False):
    """
    Create a new node_calculator instance automatically, based on given args
    """

    # Redirect plain values right away to a metadata_value
    if isinstance(item, numbers.Real):
        log.debug("new: Redirecting to Value({})".format(item))
        return metadata_values.val(item)

    # Redirect lists or tuples right away to a Collection
    if isinstance(item, (list, tuple)):
        log.debug("new: Redirecting to Collection({})".format(item))
        return Collection(item)

    log.debug("new: Redirecting to Node({})".format(item))
    return Node(item, attrs, prevent_unravelling)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ATOM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Atom(object):
    """
    Base class for Node and Attrs.
    Once instantiated this class will have access to the .node and .attrs attributes.
    Therefore all connections and operations on a Node can live in here.
    """

    # Stack that keeps track of the created nodes. Used for Container-class
    created_nodes_stack = []
    # Stack that keeps track of all executed maya-commands. Used for Tracer-class
    executed_commands_stack = []
    trace_commands = False
    traced_nodes = None
    traced_variables = None

    def __init__(self):
        super(Atom, self).__init__()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# BaseNode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class BaseNode(Atom):

    def __init__(self, prevent_unravelling=False):
        self.__dict__["_holder_node"] = None
        self.__dict__["_held_attrs"] = None

        self.__dict__["prevent_unravelling"] = prevent_unravelling

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

    @property
    def prevent_unravelling(self):
        return self._holder_node.prevent_unravelling

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

        _unravel_and_set_or_connect_a_to_b(self.__getattr__(name), value)

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
            return False
        self.attrs_list[index] = value


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NODE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Node(BaseNode):
    """
    """

    def __init__(self, node, attrs=None, prevent_unravelling=False):
        log.debug("Node __init__ ({}, {}, {})".format(node, attrs, prevent_unravelling))

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

        super(Node, self).__init__(prevent_unravelling)

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

        # Take care of keyword attrs!
        if name == "attrs":
            return self.attrs

        return Attrs(self, name)

    def __setattr__(self, name, value):
        log.debug("Node __setattr__ ({})".format(name, value))

        _unravel_and_set_or_connect_a_to_b(self.__getattr__(name), value)

    def __getitem__(self, index):
        log.debug("Node __getitem__ ({})".format(index))

        return Node(self._node_mobj, self.attrs[index], prevent_unravelling=self.prevent_unravelling)

    def __setitem__(self, index, value):
        log.debug("Node __setitem__ ({}, {})".format(index, value))

        _unravel_and_set_or_connect_a_to_b(self[index], value)

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
        log.debug("Collection __init__ ({})".format(args))
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


def _unravel_and_set_or_connect_a_to_b(obj_a, obj_b, **kwargs):
    """
    Generic function to set obj_a to value of obj_b OR connect obj_b into obj_a.

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
    log.debug("_unravel_and_set_or_connect_a_to_b ({}, {})".format(obj_a, obj_b))

    obj_a_unravelled_list, obj_b_unravelled_list = _unravel_a_and_b(obj_a, obj_b)

    obj_a_dim = len(obj_a_unravelled_list)
    obj_b_dim = len(obj_b_unravelled_list)

    # TODO: Must take care of situation where prevent_unravelling is set to True!
    # Currently that leaves a multi-dim attr like .t as "1D" whereas it should count as "3D"!

    if obj_a_dim == 1 and obj_b_dim != 1:
        # A multidimensional connection into a 1D attribute does not make sense!
        log.error(
            "Ambiguous connection from {}D to {}D: ({}, {})".format(
                obj_b_dim,
                obj_a_dim,
                obj_b_unravelled_list,
                obj_a_unravelled_list,
            )
        )
        return False

    if obj_a_dim > 1 and obj_b_dim > 1 and obj_a_dim != obj_b_dim:
        # If obj_a and obj_b are higher dimensional but not the same dimension
        # the connection can't be resolved! 2D -> 3D or 4D -> 2D is ambiguous!
        log.error(
            "Dimension mismatch for connection that can't be resolved! "
            "From {}D to {}D: ({}, {})".format(
                obj_b_dim,
                obj_a_dim,
                obj_b_unravelled_list,
                obj_a_unravelled_list,
            )
        )
        return False

    # Match input-dimensions: Both obj_X_matched_list have the same length
    # This takes care of 1D to XD setting/connecting
    if obj_a_dim != obj_b_dim:
        log.debug(
            "Matched obj_b_unravelled_list {} dimension to obj_a_dim {}!".format(
                obj_b_unravelled_list,
                obj_a_dim,
            )
        )
        obj_b_unravelled_list = obj_b_unravelled_list * obj_a_dim

    obj_a_unravelled_list, obj_b_unravelled_list = _reduce_a_and_b_to_min_dimension(
        obj_a_unravelled_list,
        obj_b_unravelled_list
    )

    _set_or_connect_a_to_b(obj_a_unravelled_list, obj_b_unravelled_list, **kwargs)


def _reduce_a_and_b_to_min_dimension(obj_a_list, obj_b_list):
    log.debug("_reduce_a_and_b_to_min_dimension ({}, {})".format(obj_a_list, obj_b_list))

    # A 3D to 3D connection can be 1 connection if both have a parent-attribute!
    reduced_obj_a_list = _check_for_parent_attribute(obj_a_list)
    reduced_obj_b_list = _check_for_parent_attribute(obj_b_list)
    # Only reduce the connection if BOTH objects have a parent-attribute!
    # A 1D attr can not connect to a 3D attr!
    if reduced_obj_a_list is not None and reduced_obj_b_list is not None:
        return (reduced_obj_a_list, reduced_obj_b_list)
    else:
        return (obj_a_list, obj_b_list)


def _check_for_parent_attribute(plug_list):
    """
    Check whether the given attribute_list can be reduced to a single parent attribute

    Args:
        attribute_list (list): List of attributes: ["node.attribute", ...]

    Returns:
        list, None: If parent attribute was found it is returned in a list,
                    otherwise returns None
    """
    # Make sure all attributes are unique, so [outputX, outputX, outputZ] doesn't match to output)
    log.debug("_check_for_parent_attribute ({})".format(plug_list))

    if len(set(plug_list)) != len(plug_list):
        return None

    # Initialize variables for a potential parent node & attribute
    potential_parent_attr = None
    potential_node = None
    checked_attributes = []

    for attr in plug_list:
        # Any numeric value instantly breaks any chance for a parent_attr
        if isinstance(attr, numbers.Real):
            return None
        node = attr.split(".")[0]
        attr = ".".join(attr.split(".")[1:])
        parent_attr = cmds.attributeQuery(
            attr,
            node=node,
            listParent=True,
            exists=True
        )

        # Any non-existent or faulty parent_attr (namely multi-attrs) breaks chance for parent_attr
        if parent_attr is False or parent_attr is None:
            return None

        # The first parent_attr becomes the potential_parent_attr...
        if potential_parent_attr is None:
            potential_parent_attr = parent_attr
        # ...if any subsequent potential_parent_attr is different to the existing: exit
        elif potential_parent_attr != parent_attr:
            return None

        # The first node becomes the potential_node...
        if potential_node is None:
            potential_node = node
        # ...if any subsequent potential_node is different to the existing: exit
        elif potential_node != node:
            return None

        # If the attribute passed all previous tests: Add it to the list
        checked_attributes.append(attr)

    # The plug should not be reduced if the list of all checked attributes
    # does not match the full list of available children attributes!
    # Example A: [outputX] should not be reduced to [output], since Y & Z are missing!
    # Example B: [outputX, outputZ, outputY] isn't in the right order and should not be reduced!
    all_checked_attributes = [
        cmds.attributeQuery(x, node=potential_node, longName=True)
        for x in checked_attributes
    ]
    all_child_attributes = cmds.attributeQuery(
        potential_parent_attr,
        node=potential_node,
        listChildren=True,
        longName=True
    )
    if all_checked_attributes != all_child_attributes:
        return None

    # If it got to this point: It must be a parent_attr
    return [potential_node + "." + potential_parent_attr[0]]


def _set_or_connect_a_to_b(obj_a_list, obj_b_list, **kwargs):
    log.debug("_set_or_connect_a_to_b ({}, {}, {})".format(obj_a_list, obj_b_list, kwargs))

    for obj_a_item, obj_b_item in zip(obj_a_list, obj_b_list):
        # Make sure obj_a_item exists in the Maya scene and get its dimensionality
        if not cmds.objExists(obj_a_item):
            log.error("obj_a_item seems not to be a Maya attr: {}!".format(obj_a_item))

        # If obj_b_item is a simple number...
        if isinstance(obj_b_item, numbers.Real) or _is_metadata_value(obj_b_item):
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
            return False


def _is_valid_maya_attr(path):
    """ Check if given attr-path is of an existing Maya attribute """
    log.debug("_is_valid_maya_attr ({})".format(path))

    if isinstance(path, basestring) and "." in path:
        node, attr = path.split(".", 1)
        return cmds.attributeQuery(attr, node=node, exists=True)

    return False


def _unravel_a_and_b(obj_a, obj_b):
    log.debug("_unravel_a_and_b ({}, {})".format(obj_a, obj_b))

    obj_a_unravelled_list = _unravel_item_as_list(obj_a)
    log.debug("obj_a_unravelled_list {} from obj_a {}".format(obj_a_unravelled_list, obj_a))
    obj_b_unravelled_list = _unravel_item_as_list(obj_b)
    log.debug("obj_b_unravelled_list {} from obj_b {}".format(obj_b_unravelled_list, obj_b))

    return (obj_a_unravelled_list, obj_b_unravelled_list)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CREATE, CONNECT AND SETUP NODE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _create_and_connect_node(operation, *args):
    """
    Generic function to create properly named Maya nodes

    Args:
        operation (str): Operation the new node has to perform
        *args (Node, string): Attributes involved in the newly created node

    Returns:
        New Maya-node of type NODE_LOOKUP_TABLE[operation]["node"]
    """
    # If a multi_index-attribute is given; create list with it of same length than args
    log.debug("Creating a new {}-operationNode with args: {}".format(operation, args))
    new_node_inputs = lookup_tables.NODE_LOOKUP_TABLE[operation]["inputs"]
    if lookup_tables.NODE_LOOKUP_TABLE[operation].get("multi_index", False):
        new_node_inputs = len(args) * lookup_tables.NODE_LOOKUP_TABLE[operation]["inputs"][:]

    # Check dimension-match: args vs. NODE_LOOKUP_TABLE-inputs:
    if len(args) != len(new_node_inputs):
        log.error(
            "Dimensions to create node don't match! "
            "Given args: {} Required node-inputs: {}".format(args, new_node_inputs)
        )

    # Unravel all given arguments and create a new node according to given operation
    unravelled_args_list = [_unravel_item_as_list(x) for x in args]
    new_node = _traced_create_node(operation, unravelled_args_list)

    # Add to created_nodes_stack Node-classAttr. Necessary for container creation!
    Atom.add_to_node_stack(new_node)
    # If the given node-type has a node-operation; set it according to NODE_LOOKUP_TABLE
    node_operation = lookup_tables.NODE_LOOKUP_TABLE[operation].get("operation", None)
    if node_operation:
        _unravel_and_set_or_connect_a_to_b(new_node + ".operation", node_operation)

    # Find the maximum dimension involved to know what to connect. For example:
    # 3D to 3D requires 3D-input, 1D to 2D needs 2D-input, 1D to 1D only needs 1D-input
    max_dim = max([len(x) for x in unravelled_args_list])

    for i, (new_node_input, obj_to_connect) in enumerate(zip(new_node_inputs, args)):

        new_node_input_list = [(new_node + "." + x) for x in new_node_input][:max_dim]
        # multi_index inputs must always be caught and filled!
        if lookup_tables.NODE_LOOKUP_TABLE[operation].get("multi_index", False):
            new_node_input_list = [x.format(multi_index=i) for x in new_node_input_list]

        # Support for single-dimension-inputs in the NODE_LOOKUP_TABLE. For example:
        # The blend-attr of a blendColors-node is always 1D,
        # so only a 1D obj_to_connect must be given!
        elif len(new_node_input) == 1:
            if len(_unravel_item_as_list(obj_to_connect)) > 1:
                log.error(
                    "Tried to connect multi-dimensional attribute to 1D input: "
                    "node: {} attrs: {} input: {}".format(
                        new_node,
                        new_node_input,
                        obj_to_connect
                    )
                )
                return False
            else:
                log.debug("Directly connecting 1D input to 1D obj!")
                _set_or_connect_a_to_b(new_node + "." + new_node_input[0], obj_to_connect)
                continue

        _unravel_and_set_or_connect_a_to_b(new_node_input_list, obj_to_connect)

    # Support for single-dimension-outputs in the NODE_LOOKUP_TABLE. For example:
    # distanceBetween returns 1D attr, no matter what dimension the inputs were
    outputs = lookup_tables.NODE_LOOKUP_TABLE[operation]["output"]
    if len(outputs) == 1:
        return Node(new_node, outputs)
    else:
        return Node(new_node, outputs[:max_dim])


def _create_node_name(operation, *args):
    """
    Create a procedural node-name that is as descriptive as possible
    """
    if isinstance(args, tuple) and len(args) == 1:
        args = args[0]
    node_name = []
    for arg in args:
        # Unwrap list of lists, if it's only one element
        if isinstance(arg, list) and len(arg) == 1:
            arg = arg[0]

        if isinstance(arg, Node):
            # Try to find short, descriptive name, otherwise use "Node"
            if isinstance(arg.attrs, basestring):
                node_name.append(arg.attrs)
            elif isinstance(arg.attrs, numbers.Real):
                node_name.append(str(arg.attrs))
            elif isinstance(arg.attrs, list) and len(arg.attrs) == 1:
                node_name.append(str(arg.attrs[0]))
            else:
                node_name.append("Node")

        elif isinstance(arg, list):
            # If it's a list of 1 element; use that element, otherwise use "list"
            if len(arg) == 1:
                node_name.append(str(arg[0]))
            else:
                node_name.append("list")

        elif isinstance(arg, numbers.Real):
            # Round floats, otherwise use number directly
            if isinstance(arg, float):
                node_name.append(str(int(arg)) + "f")
            else:
                node_name.append(str(arg))

        elif isinstance(arg, str):
            # Return the attrs-part of a passed on string (presumably "node.attrs")
            node_name.append(arg.split(".")[-1])

        else:
            # Unknown arg-type
            node_name.append("UNK" + str(arg))

    # Combine all name-elements
    name = "_".join([
        "nc",  # Common node_calculator-prefix
        operation.upper(),  # Operation type
        "_".join(node_name),  # Involved args
        lookup_tables.NODE_LOOKUP_TABLE[operation]["node"]  # Node type as suffix
    ])

    return name


def _traced_create_node(operation, involved_attributes):
    """
    Maya-createNode that adds the executed command to the command_stack if Tracer is active
    Creates a named node of appropriate type for the necessary operation
    """
    node_type = lookup_tables.NODE_LOOKUP_TABLE[operation]["node"]
    node_name = _create_node_name(operation, involved_attributes)
    new_node = cmds.ls(cmds.createNode(node_type, name=node_name), long=True)[0]

    if Node.trace_commands:
        current_variable = Node.traced_variables
        if not current_variable:
            current_variable = "var1"
        else:
            current_variable = "var{}".format(
                int(current_variable[-1].split("var")[-1])+1
            )
        Atom.add_to_command_stack(
            "{var} = cmds.createNode('{op}', name='{name}')".format(
                var=current_variable,
                op=lookup_tables.NODE_LOOKUP_TABLE[operation]["node"],
                name=new_node
            )
        )
        Node.traced_variables.append(current_variable)
        Node.traced_nodes.append(new_node)

    return new_node


def _traced_add_attr(node, **kwargs):
    """
    Maya-addAttr that adds the executed command to the command_stack if Tracer is active
    """
    cmds.addAttr(node, **kwargs)

    # If commands are traced...
    if Node.trace_commands:

        if node in Node.traced_nodes:
            # ...check if node is already part of the traced nodes: Use its variable instead
            node = Node.traced_variables[Node.traced_nodes.index(node)]
        else:
            # ...otherwise add quotes around it
            node = "'{}'".format(node)

        # Join any given kwargs so they can be passed on to the addAttr-command
        joined_kwargs = _join_kwargs_for_cmds(**kwargs)

        # Add the addAttr-command to the command stack
        Atom.add_to_command_stack("cmds.addAttr({}, {})".format(node, joined_kwargs))


def _traced_set_attr(attr, value=None, **kwargs):
    """
    Maya-setAttr that adds the executed command to the command_stack if Tracer is active
    """

    # Set attr to value
    if value is None:
        cmds.setAttr(attr, edit=True, **kwargs)
    else:
        cmds.setAttr(attr, value, edit=True, **kwargs)

    # If commands are traced...
    if Node.trace_commands:

        # ...look for the node of the given attribute...
        node = attr.split(".")[0]
        if node in Node.traced_nodes:
            # ...if it is already part of the traced nodes: Use its variable instead
            attr = "{} + '.{}'".format(
                Node.traced_variables[Node.traced_nodes.index(node)],
                ".".join(attr.split(".")[1:])
            )
        else:
            # ...otherwise add quotes around original attr
            attr = "'{}'".format(attr)

        # Join any given kwargs so they can be passed on to the setAttr-command
        joined_kwargs = _join_kwargs_for_cmds(**kwargs)

        # Add the setAttr-command to the command stack
        if value is not None:
            if joined_kwargs:
                # If both value and kwargs were given
                Atom.add_to_command_stack(
                    "cmds.setAttr({}, {}, edit=True, {})".format(attr, value, joined_kwargs)
                )
            else:
                # If only a value was given
                Atom.add_to_command_stack("cmds.setAttr({}, {})".format(attr, value))
        else:
            if joined_kwargs:
                # If only kwargs were given
                Atom.add_to_command_stack(
                    "cmds.setAttr({}, edit=True, {})".format(attr, joined_kwargs)
                )
            else:
                # If neither value or kwargs were given it was a redundant setAttr. Don't store!
                pass


def _traced_get_attr(attr):
    """
    Maya-getAttr that adds the executed command to the command_stack if Tracer is active,
    Tweaked cmds.getAttr: Takes care of awkward return value of 3D-attributes
    """

    # Variable to keep track of whether return value had to be unpacked or not
    list_of_tuples_returned = False

    if _is_valid_maya_attr(attr):
        return_value = cmds.getAttr(attr)
        # getAttr of 3D-plug returns list of a tuple. This unravels that abomination
        if isinstance(return_value, list):
            if len(return_value) == 1 and isinstance(return_value[0], tuple):
                list_of_tuples_returned = True
                return_value = list(return_value[0])
    else:
        return_value = attr

    '''
    NEED TO FIND A WAY TO KEEP TRACK OF THESE VALUES!
    AS SOON AS VALUE IS RETURNED: THERE IS NO WAY TO TELL WHETHER THAT'S A NUMBER
    OR A QUERIED NUMBER!


    # If commands are traced...
    if Node.trace_commands:

        # ...look for the node of the given attribute...
        node = attr.split(".")[0]
        if node in Node.traced_nodes:
            # ...if it is already part of the traced nodes: Use its variable instead
            attr = "{} + '.{}'".format(
                Node.traced_variables[Node.traced_nodes.index(node)],
                ".".join(attr.split(".")[1:])
            )
        else:
            # ...otherwise add quotes around original attr
            attr = "'{}'".format(attr)

        queried_var = "AAAAA" # This would have to be like Node.traced_variables!
        # Add the getAttr-command to the command stack
        if list_of_tuples_returned:
            Atom.add_to_command_stack("{} = cmds.getAttr({})".format(queried_var, attr))
        else:
            Atom.add_to_command_stack("{} = list(cmds.getAttr({})[0])".format(queried_var, attr))
    '''

    return return_value


def _join_kwargs_for_cmds(**kwargs):
    """
    Concatenates kwargs for Tracer.

    Args:
        kwargs (dict): Keyword-pairs that should be converted to a string

    Returns:
        str: A string that can be directly fed into the command of the Tracer-stack
    """
    prepared_kwargs = []

    for key, val in kwargs.iteritems():
        if isinstance(val, basestring):
            prepared_kwargs.append("{}='{}'".format(key, val))
        else:
            prepared_kwargs.append("{}={}".format(key, val))

    joined_kwargs = ", ".join(prepared_kwargs)

    return joined_kwargs


def _traced_connect_attr(attr_a, attr_b):
    """
    Maya-connectAttr that adds the executed command to the command_stack if Tracer is active
    """
    # Connect attr_a to attr_b
    cmds.connectAttr(attr_a, attr_b, force=True)

    # If commands are traced...
    if Node.trace_commands:

        # Format both attributes correctly
        formatted_attrs = []
        for attr in [attr_a, attr_b]:

            # Look for the node of the current attribute...
            node = attr.split(".")[0]
            # ...if it is already part of the traced nodes: Use its variable instead...
            if node in Node.traced_nodes:
                node_variable = Node.traced_variables[Node.traced_nodes.index(node)]
                formatted_attr = "{} + '.{}'".format(node_variable, ".".join(attr.split(".")[1:]))
            # ...otherwise make sure it's stored as a string
            else:
                formatted_attr = "'{}'".format(attr)
            formatted_attrs.append(formatted_attr)

        # Add the connectAttr-command to the command stack
        Atom.add_to_command_stack(
            "cmds.connectAttr({0}, {1}, force=True)".format(*formatted_attrs)
        )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UNRAVELLING INPUTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _unravel_item_as_list(item):
    """
    Get unravelled item. Ensures that return value is a list
    """
    log.debug("_unravel_item_as_list ({})".format(item))
    unravelled_item = _unravel_item(item)

    if not isinstance(unravelled_item, list):
        unravelled_item = [unravelled_item]

    return unravelled_item


def _is_metadata_value(value):
    # The check for metadata variables should be better than this...
    return hasattr(value, 'metadata')


def _unravel_item(item):
    """
    Specifically supported types for item:
    - Collection
    - Node
    - Attrs
    - list, tuple
    - basestring
    - numbers
    - metadata variables
    """

    log.debug("_unravel_item ({})".format(item))

    if isinstance(item, Collection):
        return _unravel_collection(item)

    elif isinstance(item, Node):
        return _unravel_node_instance(item)

    elif isinstance(item, Attrs):
        return _unravel_attrs_instance(item)

    elif isinstance(item, (list, tuple)):
        return _unravel_list(item)

    elif isinstance(item, basestring):
        return _unravel_str(item)

    elif isinstance(item, numbers.Real) or _is_metadata_value(item):
        return item

    else:
        log.error(
            "_unravel_item can't unravel {} of type {}".format(item, type(item))
        )


def _unravel_collection(collection_instance):
    log.debug("_unravel_collection ({})".format(collection_instance))

    # A Collection is basically just a list, so redirect to _unravel_list
    return _unravel_list(collection_instance.elements)


def _unravel_node_instance(node_instance):
    log.debug("_unravel_node_instance ({})".format(node_instance))

    if len(node_instance.attrs_list) == 0:
        return_value = node_instance.node
    elif len(node_instance.attrs_list) == 1:
        if node_instance.prevent_unravelling:
            return_value = "{}.{}".format(node_instance.node, node_instance.attrs_list[0])
        else:
            return_value = _unravel_plug(node_instance.node, node_instance.attrs_list[0])
    else:
        return_value = [
            "{}.{}".format(node_instance.node, attr) for attr in node_instance.attrs_list
        ]

    return return_value


def _unravel_attrs_instance(attrs_instance):
    log.debug("_unravel_attrs_instance ({})".format(attrs_instance))

    # An Attrs instance can be easily made into a Node-instance.
    # That way only the Node unravelling must be handled.
    unravelled_node = _unravel_node_instance(
        Node(
            attrs_instance.node,
            attrs_instance,
            prevent_unravelling=attrs_instance.prevent_unravelling
        )
    )
    return unravelled_node


def _unravel_list(list_instance):
    log.debug("_unravel_list ({})".format(list_instance))

    unravelled_list = []
    for item in list_instance:
        unravelled_item = _unravel_item(item)

        unravelled_list.append(unravelled_item)

    return unravelled_list


def _unravel_str(str_instance):
    log.debug("_unravel_str ({})".format(str_instance))

    # Since a string most likely indicates a maya node or attribute:
    # Make it a Node and unravel it
    node_instance = Node(str_instance)

    return _unravel_node_instance(node_instance)


def _unravel_plug(node, attr):
    """
    Try to break up a parent-attribute into its children-attributes:
    .t -> [tx, ty, tz]

    There is probably going to be an issue with multi-index attributes
    # This is necessary because attributeQuery doesn't recognize input3D[0].input3Dx, etc.
    # It only recognizes input3D and returns [input3Dx, input3Dy, input3Dz].
    # Didn't manage to query indexed attrs properly ~.~
    # Since objExists was already run it is probably safe(ish) to ignore...
    """
    log.debug("_unravel_plug ({}, {})".format(node, attr))

    attr_children = cmds.attributeQuery(attr, node=node, listChildren=True, exists=True)

    if isinstance(attr_children, list):
        return_value = ["{}.{}".format(node, attr_child) for attr_child in attr_children]
    else:
        return_value = "{}.{}".format(node, attr)

    return return_value
