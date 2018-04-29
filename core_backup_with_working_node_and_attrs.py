"""Create a node-network by entering a math-formula.

# Scenarios:

# User creates a NewNode:
# noca.NewNode("A.tx") OR noca.NewNode("A") OR noca.NewNode("A", ["tx", "tz"])
# -> NewNode with MObject of "A" and attributes

# User creates a variable of a type other than NewNode:
# noca.NewNode(10.2) OR noca.var(25)
# -> var with value and possible metadata (user_input = True (?))

# User creates a Mixed input:
# noca.NewNode("A.tx", "B.ty") OR noca.Collection([4, 2, "B.ty"])
# -> Collection with NewNode and var elements
# -> When dealing with a Collection the unravelling would have to unravel this Collection first

"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import numbers
from itertools import izip

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

    def connect_something(self):
        print("Connecting node {} with attrs {}".format(self.node, self.attrs))

    def __add__(self, other):
        """
        Regular addition operator.

        Example:
            >>> Node("pCube1.ty") + 4
        """
        return _create_and_connect_node("add", self, other)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ATTRS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Attrs(Atom):
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

        return str(self.attrs)

    def __str__(self):
        """
        Pretty print of Attrs class
        """
        log.debug("Attrs str method with self")

        return str(self.attrs)

    def __unicode__(self):
        """
        """
        log.debug("Attrs unicode method with self")

        return str(self.attrs)

    def __setitem__(self, index, value):
        """
        Support indexed assignments for Node-instances with list-attrs
        """
        log.debug("Attrs setitem method with index {} & value {}".format(index, value))

        self.attrs[index] = value

    def __getitem__(self, index):
        """
        Support indexed lookup for Node-instances with list-attrs
        """
        log.debug("Attrs getitem method with index {}".format(index))

        return Node(self.holder_node.mobj, self.attrs[index])


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NODE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Node(Atom):
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
        log.debug("Node init method with node_mobj {} & attrs {}".format(node_mobj, attrs))

        # Redirect plain values right away to a metadata_value
        if isinstance(node_mobj, numbers.Real):
            log.warning("Redirecting from Node to metadata_values: {}".format(node_mobj))
            metadata_values.val(node_mobj)
            return

        super(Node, self).__init__()

        # Handle case where no attrs were given
        if attrs is None:
            # Initialization with "object.attrs" string
            if "." in node_mobj:
                node_mobj, attrs = node_mobj.split(".", 1)
            else:
                attrs = []

        # Make sure node_mobj is an mobj indeed!
        node_mobj = om_util.get_mobj_of_node(node_mobj)

        # Initialize node and attrs instance variable
        # node should be MObject!
        # Using __dict__, because the setattr & getattr methods are overridden!
        self.__dict__["node_mobj"] = node_mobj
        self.__dict__["held_attrs"] = Attrs(self, attrs)

    @property
    def attrs(self):
        return self.held_attrs.attrs

    @property
    def node(self):
        return om_util.get_long_name_of_mobj(self.node_mobj)

    def __getitem__(self, index):
        """
        Support indexed lookup for Node-instances with list-attrs
        """
        log.debug("Attrs getitem method with index {}".format(index))

        if len(self.attrs) < index + 1:
            log.error(
                "Tried to access attrs index that is outside of range: Max "
                "index of attrs {} is {}, tried to access index {}.".format(
                    self.attrs, len(self.attrs)-1, index
                )
            )

        return Attrs(self.node_mobj, self.attrs[index])

    def __repr__(self):
        """
        Repr-method for debugging purposes
        """
        log.debug("Node repr method with self")

        return "(> {}, {} <)".format(self.node, self.attrs)

    def __str__(self):
        """
        Pretty print of Node class
        """
        log.debug("Node str method with self")

        return "Node instance with node {} and attrs {}".format(self.node, self.attrs)

    def __unicode__(self):
        """
        Maya is using this method, if a Node-instance is passed to commands:
        cmds.hide(noca.Node("A_geo")) will use __str__ of noca.Node

        For some reason Maya is bitchy:
        cmds.getAttr(a) DOESN'T work. cmds.getAttr(a.__unicode__()) DOES work
        even though both call the same __unicode__ method... Wtf?!

        cmds.getAttr(a)
        # 04/25/2018 00:35:22 - node_calculator.logger - DEBUG - Node unicode method with self
        A <type 'unicode'>
        ['tx'] <type 'list'>
        tx <type 'str'>
        A.tx <type 'str'>
        # Error: TypeError: file <maya console> line 1: Object A.tx is invalid #

        cmds.getAttr(a.__unicode__())
        # 04/25/2018 00:35:26 - node_calculator.logger - DEBUG - Node unicode method with self
        A <type 'unicode'>
        ['tx'] <type 'list'>
        tx <type 'str'>
        A.tx <type 'str'>
        # Result: 0.0 #
        """
        log.debug("Node unicode method with self")

        return_value = [
            u"{}.{}".format(self.node, attr) for attr in self.attrs
        ]

        return_value = "{}.{}".format(str(self.node), str(self.attrs[0]))

        return return_value

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
            return Attrs(self.node_mobj, name)

    def __setitem__(self, index, value):
        """
        Support indexed assignments for Node-instances with list-attrs

        Args:
            index (int): Index of item to be set
            value (Node, str, int, float): desired value for the given index
        """
        log.debug("Node setitem method with index {} & value {}".format(index, value))

        _set_or_connect_a_to_b(Node(self.node_mobj, self.attrs[index]), value)
        # self.attrs[index] = value

    def rename(self, name):
        """
        Mostly for fun: Enabling the renaming of the Maya node.
        Currently not properly undoable!!
        """
        om_util.rename_mobj(self.node_mobj, name)

    def get(self):
        """
        Helper function to allow easy access to the value of a Node-attributes.
        Equivalent to a getAttr.

        Returns:
            Int, Float, List - depending on the "queried" attributes.
        """
        log.debug("Node get method with self")

        if self.node is None:
            return self.attrs
        plug = self.plug()
        if len(plug):
            if isinstance(plug, (list, tuple)):
                return_value = []
                for elem in plug:
                    return_value.append(self._get_maya_attr(elem))
                return return_value

            else:
                return self._get_maya_attr(plug)
        else:
            log.warn("Trying to get non-existent attribute! Returned None")

            return None

    def set(self, value):
        """
        Helper function to allow easy setting of a Node-attributes.
        Equivalent to a setAttr.

        Args:
            value (Node, str, int, float, list, tuple): Connect attributes to this
                object or set attributes to this value/array
        """
        log.debug("Node set method with value {}".format(value))

        _set_or_connect_a_to_b(self, value)

    def plug(self):
        """
        Helper function to allow easy access to the Node-attributes.

        Returns:
            String of common notation "node.attrs" or None if attrs is undefined!
        """
        if self.node is None:
            return self.attrs
        elif isinstance(self.attrs, (list, tuple)):
            return ["{n}.{a}".format(n=self.node, a=a) for a in self.attrs]
        else:
            return "{n}.{a}".format(n=self.node, a=self.attrs)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# COLLECTION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Collection(Node):

    def __init__(self, *args):
        super(Collection, self).__init__()

        self.elements = args


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
    unravelled_args_list = [_get_unravelled_value_as_list(x) for x in args]
    new_node = _traced_create_node(operation, unravelled_args_list)

    # If the given node-type has a node-operation; set it according to NODE_LOOKUP_TABLE
    node_operation = lookup_tables.NODE_LOOKUP_TABLE[operation].get("operation", None)
    if node_operation:
        _set_or_connect_a_to_b(new_node + ".operation", node_operation)

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
            if len(_get_unravelled_value_as_list(obj_to_connect)) > 1:
                log.error(
                    "Tried to connect multi-dimensional attribute to 1D input: "
                    "node: {} attrs: {} input: {}".format(
                        new_node,
                        new_node_input,
                        obj_to_connect
                    )
                )
            else:
                log.debug("Directly connecting 1D input to 1D obj!")
                _set_or_connect_a_to_b(new_node + "." + new_node_input[0], obj_to_connect)
                continue

        _set_or_connect_a_to_b(new_node_input_list, obj_to_connect)

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

    return new_node


def _traced_set_attr(attr, value=None, **kwargs):
    """
    Maya-setAttr that adds the executed command to the command_stack if Tracer is active
    """
    if value is None:
        cmds.setAttr(attr, edit=True, **kwargs)
    else:
        cmds.setAttr(attr, value, edit=True, **kwargs)


def _traced_get_attr(attr):
    """
    Maya-getAttr that adds the executed command to the command_stack if Tracer is active,
    Tweaked cmds.getAttr: Takes care of awkward return value of 3D-attributes
    """
    return_value = cmds.getAttr(attr)

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
    cmds.connectAttr(attr_a, attr_b, force=True)


def _is_valid_maya_attr(path):
    """ Check if given attr-path is of an existing Maya attribute """
    if isinstance(path, basestring) and "." in path:
        node, attr = path.split(".", 1)
        return cmds.attributeQuery(attr, node=node, exists=True)

    return False


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


def _check_for_parent_attribute(attribute_list):
    """
    Check whether the given attribute_list can be reduced to a single parent attribute

    Args:
        attribute_list (list): List of attributes: ["node.attribute", ...]

    Returns:
        list, None: If parent attribute was found it is returned in a list,
                    otherwise returns None
    """
    # Make sure all attributes are unique, so [outputX, outputX, outputZ] doesn't match to output)
    log.debug("_check_for_parent_attribute for {}".format(attribute_list))

    if len(set(attribute_list)) != len(attribute_list):
        return None

    # Initialize variables for a potential parent node & attribute
    potential_parent_attr = None
    potential_node = None
    checked_attributes = []

    for attr in attribute_list:
        # Any numeric value instantly breaks any chance for a parent_attr
        if isinstance(attr, numbers.Real):
            return None
        node, attr = attr.split(".", 1)
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


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UNRAVELLING INPUTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _get_unravelled_value_as_list(input_val):
    """
    Return a clean list of values or plugs

    Args:
        input_val (int, float, list, Node): input to be unravelled and returned as list

    Returns:
        list with values and (direct, ie all 1D-) plugs
    """
    log.debug("About to unravel >{0}< with {1}".format(input_val, type(input_val)))

    unravelled_input = _get_unravelled_value(input_val)
    if not isinstance(unravelled_input, list):
        unravelled_input = [unravelled_input]

    log.info("Input >{0}< --> unravelled to >{1}<".format(input_val, unravelled_input))

    return unravelled_input


def _get_unravelled_value(input_val):
    """
    Return clean plugs or values that can be set/connected by maya

    Note:
        3D plugs become list of 1D-plugs, Nodes are returned as plugs.

    Args:
        input_val (int, float, list, set, Node, str): input to be unravelled/cleaned

    Returns:
        int, str, list: Clean plugs or values
    """
    log.debug("_get_unravelled_value of {}, type {}".format(input_val, type(input_val)))

    # Return value if it's a single number
    if isinstance(input_val, numbers.Real):
        return input_val

    # If the input_val is a maya-object (ie: attribute); return its plug/unravelled child-plugs
    elif isinstance(input_val, basestring) and cmds.objExists(input_val) and "." in input_val:
        return _get_unravelled_plug(input_val)

    elif isinstance(input_val, Node):
        # If the node-attribute is unspecified: Return the attrs-attribute directly (nums & list)
        if input_val.node is None:
            return _get_unravelled_value(input_val.attrs)

        # If attrs-attribute is an array: Return a list of unravelled values of node & its attrs
        if isinstance(input_val.attrs, (list, tuple)):
            unravelled_attrs = [
                _get_unravelled_plug("{}.{}".format(input_val.node, attr))
                for attr in input_val.attrs
            ]

            if len(unravelled_attrs) > 1:
                return unravelled_attrs

            return unravelled_attrs[0]

        # In any other case: Unravel the given plug directly
        return _get_unravelled_plug(input_val.plug())

    # If the input_val is a list of some form; return a list of its unravelled content
    elif isinstance(input_val, (list, tuple, set)):
        return [_get_unravelled_value(x) for x in input_val]

    # Unrecognised input_val
    else:
        log.error(
            "Type {} of input_val {} unrecognised!".format(type(input_val), input_val)
        )


def _get_unravelled_plug(input_plug):
    """
    Return 1D or list of 1D plugs that can be connected

    Args:
        input_plug (str): plug to be split up into separate sub-plugs

    Returns:
        str, list: Either the input_plug or if it was a compound-plug: Its components
    """
    log.info("About to unravel plug >{}<".format(input_plug))

    if not cmds.objExists(input_plug):
        log.error("input_plug does not exist: {}".format(input_plug))

    node, attr = input_plug.split(".", 1)
    unravelled_plug = cmds.attributeQuery(attr, node=node, listChildren=True, exists=True)

    if isinstance(unravelled_plug, list):
        input_plug = [node + "." + plug for plug in unravelled_plug]
    else:
        # This is necessary because attributeQuery doesn't recognize input3D[0].input3Dx, etc.
        # It only recognizes input3D and returns [input3Dx, input3Dy, input3Dz].
        # Didn't manage to query indexed attrs properly ~.~
        # Since objExists was already run it is probably safe(ish) to ignore...
        log.debug("Returning untouched input_plug, it's probably a multi-index attribute!")

    log.debug("Unravelled input_plug to >{}<".format(input_plug))
    return input_plug
