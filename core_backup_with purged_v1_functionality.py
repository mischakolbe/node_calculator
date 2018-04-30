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


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOAD NECESSARY PLUGINS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
for required_plugin in ["matrixNodes"]:
    cmds.loadPlugin(required_plugin, quiet=True)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP LOGGER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
logger.clear_handlers()
logger.setup_stream_handler(level=logger.logging.WARN)
log = logger.log


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PYTHON 2.7 & 3 COMPATIBILITY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
try:
    basestring
except NameError:
    basestring = str


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OPERATORS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class OperatorMetaClass(object):
    """
    Base class for node_calculator operators: Everything that goes beyond basic operators (+-*/)

    A meta-class was used, because many methods of this class are created on the fly
    in the __init__ method. First I simply instantiated the class, but a metaclass
    is more elegant (thanks, @sbi!).
    """

    def __init__(self, name, bases, body):
        """
        Operator-class constructor

        Note:
            name, bases, body are necessary for metaClass to work properly
        """
        super(OperatorMetaClass, self).__init__()

    @staticmethod
    def condition(condition_node, if_part=False, else_part=True):
        """
        Create condition-node

        Note:
            condition_node must be a Node-object.
            This Node-object gets automatically created by the overloaded
            comparison-operators of the Node-class and should not require manual setup!
            Simply use the usual comparison operators (==, >, <=, etc.) in the first argument.

        Args:
            condition_node (Node): Condition-statement. Node is automatically created; see notes!
            if_part (Node, str, int, float): Value/plug if condition is true
            else_part (Node, str, int, float): Value/plug if condition is false

        Returns:
            Node: Instance with condition-node and outColor-attributes

        Example:
            ::

                Op.condition(Node("pCube1.tx") >= 2, Node("pCube2.ty")+2, 5 - 1234567890)
                       |    condition-part    |   "if true"-part   | "if false"-part
        """
        # Make sure condition_node is of expected Node-type!
        # condition_node was created during comparison of Node-object(s)
        if not isinstance(condition_node, Node):
            log.error("{0} isn't Node-instance.".format(condition_node))
        if cmds.objectType(condition_node.node) != "condition":
            log.error("{0} isn't of type condition.".format(condition_node))

        condition_inputs = [
            ["colorIfTrueR", "colorIfTrueG", "colorIfTrueB"],
            ["colorIfFalseR", "colorIfFalseG", "colorIfFalseB"],
        ]
        condition_outputs = ["outColorR", "outColorG", "outColorB"]

        max_dim = max([len(_get_unravelled_value_as_list(x)) for x in [if_part, else_part]])

        for condition_node_input, obj_to_connect in zip(condition_inputs, [if_part, else_part]):
            condition_node_input_list = [
                (condition_node.node + "." + x) for x in condition_node_input[:max_dim]
            ]

            _set_or_connect_a_to_b(condition_node_input_list, obj_to_connect)

        return Node(condition_node.node, condition_outputs[:max_dim])

    @staticmethod
    def blend(attr_a, attr_b, blend_value=0.5):
        """
        Create blendColor-node

        Args:
            attr_a (Node, str, int, float): Plug or value to blend from
            attr_b (Node, str, int, float): Plug or value to blend to
            blend_value (Node, str, int, float): Plug or value defining blend-amount

        Returns:
            Node: Instance with blend-node and output-attributes

        Example:
            >>> Op.blend(1, Node("pCube.tx"), Node("pCube.customBlendAttr"))
        """
        return _create_and_connect_node('blend', attr_a, attr_b, blend_value)

    @staticmethod
    def length(attr_a, attr_b=0):
        """
        Create distanceBetween-node

        Args:
            attr_a (Node, str, int, float): Plug or value for point A
            attr_b (Node, str, int, float): Plug or value for point B

        Returns:
            Node-object with distanceBetween-node and distance-attribute

        Example:
            >>> Op.len(Node("pCube.t"), [1, 2, 3])
        """
        return _create_and_connect_node('length', attr_a, attr_b)

    @staticmethod
    def matrix_distance(matrix_a, matrix_b):
        """
        Create distanceBetween-node hooked up to inMatrix attrs

        Args:
            matrix_a (Node, str): Matrix Plug
            matrix_b (Node, str): Matrix Plug

        Returns:
            Node: Instance with distanceBetween-node and distance-attribute

        Example:
            >>> Op.len(Node("pCube.worldMatrix"), Node("pCube2.worldMatrix"))
        """
        return _create_and_connect_node('matrix_distance', matrix_a, matrix_b)

    @staticmethod
    def clamp(attr_a, min_value=0, max_value=1):
        """
        Create clamp-node

        Args:
            attr_a (Node, str, int, float): Input value
            min_value (Node, int, float, list): min-value for clamp-operation
            max_value (Node, int, float, list): max-value for clamp-operation

        Returns:
            Node: Instance with clamp-node and output-attribute(s)

        Example:
            >>> Op.clamp(Node("pCube.t"), [1, 2, 3], 5)
        """
        return _create_and_connect_node('clamp', attr_a, min_value, max_value)

    @staticmethod
    def remap(attr_a, min_value=0, max_value=1, old_min_value=0, old_max_value=1):
        """
        Create setRange-node

        Args:
            attr_a (Node, str, int, float): Input value
            min_value (Node, int, float, list): min-value for remap-operation
            max_value (Node, int, float, list): max-value for remap-operation
            old_min_value (Node, int, float, list): old min-value for remap-operation
            old_max_value (Node, int, float, list): old max-value for remap-operation

        Returns:
            Node: Instance with setRange-node and output-attribute(s)

        Example:
            >>> Op.remap(Node("pCube.t"), [1, 2, 3], 4, [-1, 0, -2])
        """
        return _create_and_connect_node(
            'remap', attr_a, min_value, max_value, old_min_value, old_max_value
        )

    @staticmethod
    def dot(attr_a, attr_b=0, normalize=False):
        """
        Create vectorProduct-node for vector dot-multiplication

        Args:
            attr_a (Node, str, int, float, list): Plug or value for vector A
            attr_b (Node, str, int, float, list): Plug or value for vector B
            normalize (Node, boolean): Whether resulting vector should be normalized

        Returns:
            Node: Instance with vectorProduct-node and output-attribute(s)

        Example:
            >>> Op.dot(Node("pCube.t"), [1, 2, 3], True)
        """
        return _create_and_connect_node('dot', attr_a, attr_b, normalize)

    @staticmethod
    def cross(attr_a, attr_b=0, normalize=False):
        """
        Create vectorProduct-node for vector cross-multiplication

        Args:
            attr_a (Node, str, int, float, list): Plug or value for vector A
            attr_b (Node, str, int, float, list): Plug or value for vector B
            normalize (Node, boolean): Whether resulting vector should be normalized

        Returns:
            Node: Instance with vectorProduct-node and output-attribute(s)

        Example:
            >>> Op.cross(Node("pCube.t"), [1, 2, 3], True)
        """
        return _create_and_connect_node('cross', attr_a, attr_b, normalize)

    @staticmethod
    def normalize_vector(in_vector, normalize=True):
        """
        Create vectorProduct-node to normalize the given vector

        Args:
            in_vector (Node, str, int, float, list): Plug or value for vector A
            normalize (Node, boolean): Whether resulting vector should be normalized

        Returns:
            Node: Instance with vectorProduct-node and output-attribute(s)

        Example:
            >>> Op.normalize_vector(Node("pCube.t"))
        """
        # Making normalize a flag allows the user to connect attributes to it
        return _create_and_connect_node('normalize_vector', in_vector, normalize)

    @staticmethod
    def average(*attrs):
        """
        Create plusMinusAverage-node for averaging input attrs

        Args:
            attrs (Node, string, list): Any number of inputs to be averaged

        Returns:
            Node: Instance with plusMinusAverage-node and output-attribute(s)

        Example:
            >>> Op.average(Node("pCube.t"), [1, 2, 3])
        """
        return _create_and_connect_node('average', *attrs)

    @staticmethod
    def mult_matrix(*attrs):
        """
        Create multMatrix-node for multiplying matrices

        Args:
            attrs (Node, string, list): Any number of matrix inputs to be multiplied

        Returns:
            Node: Instance with multMatrix-node and output-attribute(s)

        Example:
            out = Node('pSphere')
            matrix_mult = Op.mult_matrix(
                Node('pCube1.worldMatrix'), Node('pCube2').worldMatrix
            )
            decomp = Op.decompose_matrix(matrix_mult)
            out.t = decomp.outputTranslate
            out.r = decomp.outputRotate
            out.s = decomp.outputScale
        """
        return _create_and_connect_node('mult_matrix', *attrs)

    @staticmethod
    def decompose_matrix(in_matrix):
        """
        Create decomposeMatrix-node to disassemble matrix into components (t, rot, etc.)

        Args:
            in_matrix (Node, string): one matrix attribute to be decomposed

        Returns:
            Node: Instance with decomposeMatrix-node and output-attribute(s)

        Example:
            driver = Node('pCube1')
            driven = Node('pSphere1')
            decomp = Op.decompose_matrix(driver.worldMatrix)
            driven.t = decomp.outputTranslate
            driven.r = decomp.outputRotate
            driven.s = decomp.outputScale
        """
        return _create_and_connect_node('decompose_matrix', in_matrix)

    @staticmethod
    def compose_matrix(**kwargs):
        """
        Create composeMatrix-node to assemble matrix from components (translation, rotation etc.)

        Args:
            kwargs: Possible kwargs described below (longName flags take precedence!)
            translate (Node, str, int, float): [t] translate for matrix composition
            rotate (Node, str, int, float): [r] rotate for matrix composition
            scale (Node, str, int, float): [s] scale for matrix composition
            shear (Node, str, int, float): [sh] shear for matrix composition
            rotate_order (Node, str, int, float): [ro] rotate_order for matrix composition
            euler_rotation (bool): Apply Euler filter on rotations

        Returns:
            Node: Instance with composeMatrix-node and output-attribute(s)

        Example:
            in_a = Node('pCube1')
            in_b = Node('pCube2')
            decomp_a = Op.decompose_matrix(in_a.worldMatrix)
            decomp_b = Op.decompose_matrix(in_b.worldMatrix)
            Op.compose_matrix(r=decomp_a.outputRotate, s=decomp_b.outputScale)
        """

        translate = kwargs.get("translate", kwargs.get("t", 0))
        rotate = kwargs.get("rotate", kwargs.get("r", 0))
        scale = kwargs.get("scale", kwargs.get("s", 1))
        shear = kwargs.get("shear", kwargs.get("sh", 0))
        rotate_order = kwargs.get("rotate_order", kwargs.get("ro", 0))
        euler_rotation = kwargs.get("euler_rotation", True)

        compose_matrix_node = _create_and_connect_node(
            'compose_matrix',
            translate,
            rotate,
            scale,
            shear,
            rotate_order,
            euler_rotation
        )

        return compose_matrix_node

    @staticmethod
    def choice(*inputs, **kwargs):
        """
        Create choice-node to switch between various input attributes

        Args:
            One or many inputs (any type possible). Optional selector (s=node.attr).
            Note: Multi index input seems to also require one 'selector' per index. So we package
            a copy of the same selector for each input

        Returns:
            Node: Instance with choice-node and output-attribute(s)

        Example:
            option_a = Node("pCube1")
            option_b = Node("pCube2")
            driver_attr = Node("pSphere.tx")
            choice_node_obj = Op.choice(option_a.tx, option_b.tx, selector=driver_attr)
            Node("pTorus1").tx = choice_node_obj
        """
        choice_node_obj = _create_and_connect_node('choice', *inputs)
        # Since this is a multi-attr node it's hard to filter out the selector keyword
        # in a perfect manner. This should do fine though.
        _set_or_connect_a_to_b(choice_node_obj.selector, kwargs.get("selector", 0))

        return choice_node_obj


class Op(object):
    """ Create Operator-class from OperatorMetaClass (check its doc string for reason why) """
    __metaclass__ = OperatorMetaClass


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ATTRS
# Attrs would need to be aware of holding Node, otherwise the setitem can not act as a setAttr for the node with attr!

# Maybe this?

# class Outer(object):

#     def createInner(self):
#         return Outer.Inner(self)

#     class Inner(object):
#         def __init__(self, outer_instance):
#             self.outer_instance = outer_instance
#             self.outer_instance.somemethod()

#         def inner_method(self):
#             self.outer_instance.anothermethod()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Attrs(object):
    def __init__(self, attrs=None):
        """
        """
        log.debug("Attrs init method with attrs {}".format(attrs))

        if attrs is None:
            self.__dict__["attrs"] = []
        elif isinstance(attrs, basestring):
            self.__dict__["attrs"] = [attrs]
        elif isinstance(attrs, (tuple, list)):
            self.__dict__["attrs"] = attrs
        else:
            log.warn("Unrecognised Attrs type for attrs {}".format(attrs))

    def __str__(self):
        """
        Pretty print of Attrs class

        Returns:
            String of concatenated attrs-attributes
        """
        log.debug("Attrs str method with self")

        return str(self.__dict__["attrs"])

    def __repr__(self):
        """
        Repr-method for debugging purposes

        Returns:
            String of separate elements that make up Node-instance
        """
        log.debug("Attrs repr method with self")

        return self.__dict__["attrs"]

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

    def __setitem__(self, index, value):
        """
        Support indexed assignments for Node-instances with list-attrs

        Args:
            index (int): Index of item to be set
            value (Node, str, int, float): desired value for the given index
        """
        log.debug("Attrs setitem method with index {} & value {}".format(index, value))

        # self.attrs[index] = value

    def __getitem__(self, index):
        """
        Support indexed lookup for Node-instances with list-attrs

        Args:
            index (int): Index of desired item

        Returns:
            Object that is at the desired index
        """
        log.debug("Attrs getitem method with index {}".format(index))

        # if isinstance(self.attrs[index], numbers.Real):
        #     return self.attrs[index]
        # elif self.node is None:
        #     return Node(self.attrs[index])
        # else:
        #     return Node(self.node, self.attrs[index])


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NODE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Node(object):
    """
    Base class for node_calculator objects: Components involved in a calculation.

    Note:
        Each Node-object has a mandatory node-attribute and an optional attrs-attribute.
        The attribute "attrs" is a keyword!!!
        Node().attrs returns the currently stored node/attrs-combo!
    """
    # Stack that keeps track of the created nodes. Used for Container-class
    created_nodes_stack = []
    # Stack that keeps track of all executed maya-commands. Used for Tracer-class
    executed_commands_stack = []
    trace_commands = False
    traced_nodes = None
    traced_variables = None

    def __init__(self, node, attrs=None):
        """
        Node-class constructor

        Note:
            __setattr__ is changed and the usual "self.node = node" results in a loop.
            Therefore attributes need to be set directly via __dict__!

        Args:
            node (str): Represents a Maya node
            attrs (str): Represents attributes on the node

        Example:
            ::

                a = Node("pCube1")
                b = Node("pCube2.ty")
                c = b.sx   # This is possible, because the "." (dot) invokes a getattr of
                             object b. This returns a new Node-object consisting of
                             b.node (="pCube2") and the given attributes (=["sx"])!
        """
        log.debug("Node init method with node {} & attrs {}".format(node, attrs))

        if isinstance(node, (numbers.Real, list, tuple)):
            self.__dict__["node"] = None
            self.__dict__["attrs"] = node
        # Initialization with "object.attrs" string
        elif attrs is None and "." in node:
            node_part, attrs_part = node.split(".")
            self.__dict__["node"], self.__dict__["attrs"] = node_part, Attrs(attrs_part)
        # Initialization where node and attribute(optional) are specifically given
        else:
            self.__dict__["node"] = node
            self.__dict__["attrs"] = Attrs(attrs)
            # if attrs is None:
            #     self.__dict__["attrs"] = []
            # elif isinstance(attrs, basestring):
            #     self.__dict__["attrs"] = [attrs]
            # else:
            #     self.__dict__["attrs"] = attrs

    def __getattr__(self, name):
        """
        A getattr of a Node-object returns a Node-object. Always returns a new
        Node-instance, EXCEPT when keyword "attr" is used to return itself!

        Args:
            name (str): Name of requested attribute

        Returns:
            New Node-object OR itself, if keyword "attr" was used!

        Example:
            ::

                a = Node("pCube1") # Create new Node-object
                a.tx  # invokes __getattr__ and returns a new Node-object.
                        It's the same as typing Node("a.tx")
        """
        log.debug("Node getattr method with name".format(name))

        if name == "attrs":
            if not len(self.attrs):
                log.error("No attributes on requested Node-object! {}".format(self.node))
            return self
        else:
            return Node(self.node, name)

    def __setattr__(self, name, value):
        """
        Set or connect attribute (name) to the given value.

        Note:
            setattr is invoked by equal-sign. Does NOT work without attribute given:
            a = Node("pCube1.ty")  # Initialize Node-object with attribute given
            a.ty = 7  # Works fine if attribute is specifically called
            a = 7  # Does NOT work! It looks like the same operation as above,
                     but here Python calls the assignment operation, NOT setattr.
                     The assignment-operation can't be overridden. Sad but true.

        Args:
            name (str): Name of the attribute to be set
            value (Node, str, int, float, list, tuple): Connect attribute to this
                object or set attribute to this value/array

        Example:
            ::

                a = Node("pCube1") # Create new Node-object
                a.tx = 7  # Set pCube1.tx to the value 7
                a.t = [1, 2, 3]  # Set pCube1.tx|ty|tz to 1|2|3 respectively
                a.tx = Node("pCube2").ty  # Connect pCube2.ty to pCube1.tx
        """
        log.debug("Node setattr method with name {} & value {}".format(name, value))

        _set_or_connect_a_to_b(self.__getattr__(name), value)

    def __add__(self, other):
        """
        Regular addition operator.

        Example:
            >>> Node("pCube1.ty") + 4
        """
        return _create_and_connect_node("add", self, other)

    def __radd__(self, other):
        """
        Reflected addition operator.
        Fall-back method in case regular addition is not defined & fails.

        Example:
            >>> 4 + Node("pCube1.ty")
        """
        return _create_and_connect_node("add", other, self)

    def __sub__(self, other):
        """
        Regular subtraction operator.

        Example:
            >>> Node("pCube1.ty") - 4
        """
        return _create_and_connect_node("sub", self, other)

    def __rsub__(self, other):
        """
        Reflected subtraction operator.
        Fall-back method in case regular subtraction is not defined & fails.

        Example:
            >>> 4 - Node("pCube1.ty")
        """
        return _create_and_connect_node("sub", other, self)

    def __mul__(self, other):
        """
        Regular multiplication operator.

        Example:
            >>> Node("pCube1.ty") * 4
        """
        return _create_and_connect_node("mul", self, other)

    def __rmul__(self, other):
        """
        Reflected multiplication operator.
        Fall-back method in case regular multiplication is not defined & fails.

        Example:
            >>> 4 * Node("pCube1.ty")
        """
        return _create_and_connect_node("mul", other, self)

    def __div__(self, other):
        """
        Regular division operator.

        Example:
            >>> Node("pCube1.ty") / 4
        """
        return _create_and_connect_node("div", self, other)

    def __rdiv__(self, other):
        """
        Reflected division operator.
        Fall-back method in case regular division is not defined & fails.

        Example:
            >>> 4 / Node("pCube1.ty")
        """
        return _create_and_connect_node("div", other, self)

    def __pow__(self, other):
        """
        Regular power operator.

        Example:
            >>> Node("pCube1.ty") ** 4
        """
        return _create_and_connect_node("pow", self, other)

    def __rpow__(self, other):
        """
        Reflected power operator.
        Fall-back method in case regular power is not defined & fails.

        Example:
            >>> 4 ** Node("pCube1.ty")
        """
        return _create_and_connect_node("pow", other, self)

    def __eq__(self, other):
        """
        Equality operator: ==

        Returns:
            Node-instance of a newly created Maya condition-node
        """
        return self._compare(other, "eq")

    def __ne__(self, other):
        """
        Inequality operator: !=

        Returns:
            Node-instance of a newly created Maya condition-node
        """
        return self._compare(other, "ne")

    def __gt__(self, other):
        """
        Greater than operator: >

        Returns:
            Node-instance of a newly created Maya condition-node
        """
        return self._compare(other, "gt")

    def __ge__(self, other):
        """
        Greater equal operator: >=

        Returns:
            Node-instance of a newly created Maya condition-node
        """
        return self._compare(other, "ge")

    def __lt__(self, other):
        """
        Less than operator: <

        Returns:
            Node-instance of a newly created Maya condition-node
        """
        return self._compare(other, "lt")

    def __le__(self, other):
        """
        Less equal operator: <=

        Returns:
            Node-instance of a newly created Maya condition-node
        """
        return self._compare(other, "le")

    def __str__(self):
        """
        Pretty print of the class

        Returns:
            String of concatenated node- & attrs-attributes
        """
        log.debug("Node str method with self")

        if self.node is None:
            return str(self.attrs)
        elif self.attrs is None:
            return str(self.node)

        return str(self.plug())

    def __repr__(self):
        """
        Repr-method for debugging purposes

        Returns:
            String of separate elements that make up Node-instance
        """
        log.debug("Node repr method with self")

        return "Node('{0}', '{1}')".format(self.node, self.attrs)

    def __len__(self):
        """
        Return the length of the Node-attrs variable.

        Returns:
            Int: 0 if attrs is None, 1 if it's not an array, otherwise len(attrs)
        """
        log.warn("Using the Node-len method!")
        if self.attrs is None:
            return 0

        if isinstance(self.attrs, (list, tuple)):
            return len(self.attrs)
        else:
            return 1

    def __iter__(self):
        """
        Generator to iterate over list of attributes

        Yields:
            Next item in list of attributes.
        """
        log.debug("Node iter method with self")

        i = 0
        while True:
            try:
                if isinstance(self.attrs[i], numbers.Real):
                    yield self.attrs[i]
                elif self.node is None:
                    yield Node(self.attrs[i])
                else:
                    yield Node(self.node, self.attrs[i])
            except IndexError:
                raise StopIteration
            i += 1

    def __setitem__(self, index, value):
        """
        Support indexed assignments for Node-instances with list-attrs

        Args:
            index (int): Index of item to be set
            value (Node, str, int, float): desired value for the given index
        """
        log.debug("Node setitem method with index {} & value {}".format(index, value))

        self.attrs[index] = value

    def __getitem__(self, index):
        """
        Support indexed lookup for Node-instances with list-attrs

        Args:
            index (int): Index of desired item

        Returns:
            Object that is at the desired index
        """
        log.debug("Node getitem method with index {}".format(index))

        if isinstance(self.attrs[index], numbers.Real):
            return self.attrs[index]
        elif self.node is None:
            return Node(self.attrs[index])
        else:
            return Node(self.node, self.attrs[index])

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

    def redefine_attrs(self, attrs):
        """
        Set the attrs-attribute of the Node-instance to the given attrs.

        Args:
            attr (str): Name for the new attributes of the Node-object

        Returns:
            The Node-instance

        Example:
            ::

            a = Node("pCube1.tx")  # Create the node instance with or without attribute
            a.redefine_attr("ty")  # Change the attribute of the node instance
        """
        log.debug("Node redefine_attr method with attrs {}".format(attrs))

        if isinstance(attrs, basestring):
            attrs = [attrs]

        self.__dict__["attrs"] = attrs

        return self

    def add_bool(self, name, **kwargs):
        """
        Create a boolean-attribute for the given attribute

        Args:
            name (str): Name for the new attribute to be created
            kwargs (dict): User specified attributes to be set for the new attribute

        Returns:
            The Node-instance with the node and new attribute

        Example:
            >>> Node("pCube1").add_bool(value=True)
        """
        return self._add_traced_attr("bool", name, **kwargs)

    def add_int(self, name, **kwargs):
        """
        Create an integer-attribute for the given attribute

        Args:
            name (str): Name for the new attribute to be created
            kwargs (dict): User specified attributes to be set for the new attribute

        Returns:
            The Node-instance with the node and new attribute

        Example:
            >>> Node("pCube1").add_int(value=123)
        """
        return self._add_traced_attr("int", name, **kwargs)

    def add_float(self, name, **kwargs):
        """
        Create a float-attribute for the given attribute

        Args:
            name (str): Name for the new attribute to be created
            kwargs (dict): User specified attributes to be set for the new attribute

        Returns:
            The Node-instance with the node and new attribute

        Example:
            >>> Node("pCube1").add_float(value=3.21)
        """
        return self._add_traced_attr("float", name, **kwargs)

    def add_enum(self, name, enum_name="", cases=None, **kwargs):
        """
        Create a boolean-attribute for the given attribute

        Args:
            name (str): Name for the new attribute to be created
            enum_name (list, str): User-choices for the resulting enum-attribute
            cases (list, str): Overrides enum_name, which I find a horrific name
            kwargs (dict): User specified attributes to be set for the new attribute

        Returns:
            The Node-instance with the node and new attribute

        Example:
            >>> Node("pCube1").add_enum(cases=["A", "B", "C"], value=2)
        """
        if cases is not None:
            enum_name = cases
        if isinstance(enum_name, (list, tuple)):
            enum_name = ":".join(enum_name)

        return self._add_traced_attr("enum", name, enumName=enum_name, **kwargs)

    @classmethod
    def add_to_node_stack(cls, node):
        """
        Add a node to the class-variable created_nodes_stack
        """
        cls.created_nodes_stack.append(node)

    @classmethod
    def flush_node_stack(cls):
        """
        Reset the class-variable created_nodes_stack to an empty list
        """
        cls.created_nodes_stack = []

    @classmethod
    def add_to_command_stack(cls, command):
        """
        Add a command to the class-variable executed_commands_stack
        """
        cls.executed_commands_stack.append(command)

    @classmethod
    def flush_command_stack(cls):
        """
        Reset the class-variable executed_commands_stack to an empty list
        """
        cls.executed_commands_stack = []

    def _compare(self, other, operator):
        """
        Create a Maya condition node set to the correct operation-type.

        Args:
            other (Node, int, float): Attr or value to compare self-attrs with
            operator (string): Operation type available in Maya condition-nodes

        Returns:
            Node-instance of a newly created Maya condition-node
        """
        # Create new condition node set to the appropriate operation-type
        return _create_and_connect_node(operator, self, other)

    @staticmethod
    def _get_maya_attr(attr):
        """
        Tweaked cmds.getAttr: Takes care of awkward return value of 3D-attributes
        """
        return _traced_get_attr(attr)

        # if _is_valid_maya_attr(attr):
        #     return_value = cmds.getAttr(attr)
        #     # getAttr of 3D-plug returns list of a tuple. This unravels that abomination
        #     if isinstance(return_value, list):
        #         if len(return_value) == 1 and isinstance(return_value[0], tuple):
        #             return_value = list(return_value[0])
        #     return return_value
        # else:
        #     return attr

    def _add_traced_attr(self, attr_type, attr_name, **kwargs):
        """
        Create an attribute of type attr_type for the given node/attr-combination of self.

        Args:
            attr_type (str): Attribute type. Must be specified in the ATTR_LOOKUP_TABLE!
            kwargs (dict): Any user specified flags & their values.
                           Gets combined with values in ATTR_LOOKUP_TABLE!
            XXX

        Returns:
            XXX
        """
        # Replace spaces in name not to cause Maya-warnings
        attr_name = attr_name.replace(' ', '_')

        # Check whether attribute already exists. If so; return early!
        attr = "{}.{}".format(self.node, attr_name)
        if cmds.objExists(attr):
            log.warn("Attribute {} already existed!".format(attr))
            return Node(attr)

        # Make a copy of the default values for the given attrType
        attr_variables = lookup_tables.ATTR_LOOKUP_TABLE["base_attr"].copy()
        attr_variables.update(lookup_tables.ATTR_LOOKUP_TABLE[attr_type])
        log.debug("Copied default attr_variables: {}".format(attr_variables))

        # Add the attr variable into the dictionary
        attr_variables["longName"] = attr_name
        # Override default values with kwargs
        attr_variables.update(kwargs)
        log.debug("Added custom attr_variables: {}".format(attr_variables))

        # Extract attributes that need to be set via setAttr-command
        set_attr_values = {
            "channelBox": attr_variables.pop("channelBox", None),
            "lock": attr_variables.pop("lock", None),
        }
        attr_value = attr_variables.pop("value", None)
        log.debug("Extracted set_attr-variables from attr_variables: {}".format(attr_variables))
        log.debug("set_attr-variables: {}".format(set_attr_values))

        # Add the attribute
        _traced_add_attr(self.node, **attr_variables)

        # Filter for any values that need to be set via the setAttr command. Oh Maya...
        set_attr_values = {
            key: val for (key, val) in set_attr_values.iteritems()
            if val is not None
        }
        log.debug("Pruned set_attr-variables: {}".format(set_attr_values))

        # If there is no value to be set; set any attribute flags directly
        if attr_value is None:
            _traced_set_attr(attr, **set_attr_values)
        else:
            # If a value is given; use the set_or_connect function
            _set_or_connect_a_to_b(attr, attr_value, **set_attr_values)

        return Node(attr)


def _is_valid_maya_attr(path):
    """ Check if given attr-path is of an existing Maya attribute """
    if isinstance(path, basestring) and "." in path:
        node, attr = path.split(".")
        return cmds.attributeQuery(attr, node=node, exists=True)

    return False


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TRACER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Tracer(object):
    """
    Class that returns all maya-commands inside the with-statement

    Example:
        ::

            with Tracer(pprint_trace=True) as s:
                a.tx = b.ty - 2 * c.tz
            print(s)
    """

    def __init__(self, trace=True, print_trace=False, pprint_trace=False):
        # Allow either note or notes as keywords
        self.trace = trace
        self.print_trace = print_trace
        self.pprint_trace = pprint_trace

    def __enter__(self):
        """
        with-statement; entering-method
        Flushes executed_commands_stack (Node-classAttribute) and starts tracing
        """
        # Do not add to stack if unwanted
        Node.trace_commands = bool(self.trace)

        Node.flush_command_stack()
        Node.traced_nodes = []
        Node.traced_variables = []

        return Node.executed_commands_stack

    def __exit__(self, exc_type, value, traceback):
        """
        with-statement; exit-method
        Print all executed commands, if desired
        """
        # Tell the user if he/she wants to print results but they were not traced!
        if not self.trace and (self.print_trace or self.pprint_trace):
            print("node_calculator commands were not traced!")
        else:
            # Print executed commands as list
            if self.print_trace:
                print("node_calculator command-stack:", Node.executed_commands_stack)
            # Print executed commands on separate lines
            if self.pprint_trace:
                print("~~~~~~~~~ node_calculator command-stack: ~~~~~~~~~")
                for item in Node.executed_commands_stack:
                    print(item)
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        Node.trace_commands = False


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

    # Add to created_nodes_stack Node-classAttr. Necessary for container creation!
    Node.add_to_node_stack(new_node)
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

    if Node.trace_commands:
        current_variable = Node.traced_variables
        if not current_variable:
            current_variable = "var1"
        else:
            current_variable = "var{}".format(
                int(current_variable[-1].split("var")[-1])+1
            )
        Node.add_to_command_stack(
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
        Node.add_to_command_stack("cmds.addAttr({}, {})".format(node, joined_kwargs))


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
                Node.add_to_command_stack(
                    "cmds.setAttr({}, {}, edit=True, {})".format(attr, value, joined_kwargs)
                )
            else:
                # If only a value was given
                Node.add_to_command_stack("cmds.setAttr({}, {})".format(attr, value))
        else:
            if joined_kwargs:
                # If only kwargs were given
                Node.add_to_command_stack(
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
            Node.add_to_command_stack("{} = cmds.getAttr({})".format(queried_var, attr))
        else:
            Node.add_to_command_stack("{} = list(cmds.getAttr({})[0])".format(queried_var, attr))
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
        Node.add_to_command_stack(
            "cmds.connectAttr({0}, {1}, force=True)".format(*formatted_attrs)
        )


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

    attr = ".".join(input_plug.split(".")[1:])
    node = input_plug.split(".")[0]
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
