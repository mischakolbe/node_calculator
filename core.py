"""
node_calculator - Create a node-network by entering a math-formula.

Supported operations (defaultValues after '='):
- Basic math:   +, -, *, /, **
- condition:    Op.condition(condition, if_part=False, else_part=True)
- length:       Op.length(attr_a, attr_b=0)
- average:      Op.average(*attrs)  # Any number of inputs possible
- dot-product:  Op.dot(attr_a, attr_b=0)
- cross-product:Op.cross(attr_a, attr_b=0)
- blend:        Op.blend(attr_a, attr_b, blend_value=0.5)
- remap:        Op.remap(attr_a, min_value=0, max_value=1, old_min_value=0, old_max_value=1)
- clamp:        Op.clamp(attr_a, min_value=0, max_value=1)

Example:
    ::

        import node_calculator as noca
        a = noca.Node("pCube1")
        b = noca.Node("pCube2")
        c = noca.Node("pCube3")
        with noca.Container(name="my_cont", notes="Formula: b.ty-2*c.tz", create=True) as cont:
            a.t = noca.Op.blend(b.ty - 2 * c.tz, c.s, 0.3)
        with noca.Tracer(pprint_trace=True) as tracer:
            e = b.customAttr.as_float(value=c.tx)
            a.s = noca.Op.condition(b.ty - 2 > c.tz, e, [1, 2, 3])

ToDo:
    - Try to reduce connections of compound-attributes (plusMinusAverage, etc.)
    - Not depend on name of object..?
    - Add short, byte, vector, matrix, ... attributes
    - Attributes currently always unravel. That is not always desirable!
        For example choice-nodes should pass through EXACTLY what is given/asked!
        But these different cases are hard to detect right now (what is connected to what)
        Currently connecting a.t to choice-node connects a.tz and b.t = choice.output
        connects choice.output to all 3 directions (b.tx, b.ty, b.tz).
        Should connect this way: a.t -> choice.input[0] and choice.output -> b.t

        Given conn A to B: unravelling A doesn't make sense if B doesn't get unravelled.
        A type-query with excluded node-types for unravelling might help? Not perfect either...
    - It's currently impossible to access indexed attributes:
        choice.input[0] = a.tx  # This won't do anything, because the index bombs
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
from .logger import logger


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOAD NECESSARY PLUGINS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
cmds.loadPlugin("matrixNodes", quiet=True)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUTHORSHIP
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
__author__ = "Mischa Kolbe"
__credits__ = [
    "Mischa Kolbe", "Steven Bills", "Marco D'Ambros", "Benoit Gielly", "Adam Vanner",
    "Niels Kleinheinz"
]
__version__ = "1.1.1"
__maintainer__ = "Mischa Kolbe"
__email__ = "mischakolbe@gmail.com"
__updated__ = "2017 12 03"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Dict of all available operations: used node-type, inputs, outputs, etc.
NODE_LOOKUP_TABLE = {}

# All attribute types that can be created by the node_calculator and their default creation values
ATTR_LOOKUP_TABLE = {
    # General settings - Applies to ALL attribute types!
    "base_attr": {
        "keyable": True,
    },
    # Individual settings - Applies only to that specific type
    "bool": {
        "attributeType": "bool",
    },
    "int": {
        "attributeType": "long",
    },
    "float": {
        "attributeType": "double",
    },
    "enum": {
        "attributeType": "enum",
    },
}


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
        # Initialize the NODE_LOOKUP_TABLE_dictionary with all available operations
        self._initialize_node_lookup_table()

    def _initialize_node_lookup_table(self):
        """
        Fill the global NODE_LOOKUP_TABLE-dictionary with all available operations

        Note:
            NODE_LOOKUP_TABLE is a dict that holds the data for each available operation:
            the necessary node-type, its inputs, outputs, etc.
            This unified data enables to abstract node creation, connection, etc.
        """
        global NODE_LOOKUP_TABLE

        NODE_LOOKUP_TABLE = {
            "blend": {
                "node": "blendColors",
                "inputs": [
                    ["color1R", "color1G", "color1B"],
                    ["color2R", "color2G", "color2B"],
                    ["blender"],
                ],
                "output": ["outputR", "outputG", "outputB"],
            },
            "length": {
                "node": "distanceBetween",
                "inputs": [
                    ["point1X", "point1Y", "point1Z"],
                    ["point2X", "point2Y", "point2Z"],
                ],
                "output": ["distance"],
            },
            "distanceBetweenMatrices": {
                "node": "distanceBetween",
                "inputs": [
                    ["inMatrix1"],
                    ["inMatrix2"],
                ],
                "output": ["distance"],
            },
            "clamp": {
                "node": "clamp",
                "inputs": [
                    ["inputR", "inputG", "inputB"],
                    ["minR", "minG", "minB"],
                    ["maxR", "maxG", "maxB"],
                ],
                "output": ["outputR", "outputG", "outputB"],
            },
            "remap": {
                "node": "setRange",
                "inputs": [
                    ["valueX", "valueY", "valueZ"],
                    ["minX", "minY", "minZ"],
                    ["maxX", "maxY", "maxZ"],
                    ["oldMinX", "oldMinY", "oldMinZ"],
                    ["oldMaxX", "oldMaxY", "oldMaxZ"],
                ],
                "output": ["outValueX", "outValueY", "outValueZ"],
            },
            "average": {
                "node": "plusMinusAverage",
                "inputs": [
                    [
                        "input3D[{multi_index}].input3Dx",
                        "input3D[{multi_index}].input3Dy",
                        "input3D[{multi_index}].input3Dz"
                    ],
                ],
                "multi_index": True,
                "output": ["output3Dx", "output3Dy", "output3Dz"],
                "operation": 3,
            },
            "multMatrix": {
                "node": "multMatrix",
                "inputs": [
                    [
                        "matrixIn[{multi_index}]"
                    ],
                ],
                "multi_index": True,
                "output": ["matrixSum"],
            },
            "decomposeMatrix": {
                "node": "decomposeMatrix",
                "inputs": [
                    ["inputMatrix"],
                ],
                "output": [
                    "outputTranslateX", "outputTranslateY", "outputTranslateZ",
                    "outputRotateX", "outputRotateY", "outputRotateZ",
                    "outputScaleX", "outputScaleY", "outputScaleZ",
                    "outputShearX", "outputShearY", "outputShearZ",
                ],
            },
            "composeMatrix": {
                "node": "composeMatrix",
                "inputs": [
                    ["inputTranslateX", "inputTranslateY", "inputTranslateZ"],
                    ["inputRotateX", "inputRotateY", "inputRotateZ"],
                    ["inputScaleX", "inputScaleY", "inputScaleZ"],
                    ["inputShearX", "inputShearY", "inputShearZ"],
                    ["inputRotateOrder"],
                    ["useEulerRotation"],
                ],
                "output": ["outputMatrix"],
            },
            "choice": {
                "node": "choice",
                "inputs": [
                    [
                        "input[{multi_index}]",
                    ],
                ],
                "multi_index": True,
                "output": ["output"],
            },
            "normalizeVector": {
                "node": "vectorProduct",
                "inputs": [
                    ["input1X", "input1Y", "input1Z"],
                    ["normalizeOutput"],
                ],
                "output": ["outputX", "outputY", "outputZ"],
                "operation": 0,
            }
        }

        # Fill NODE_LOOKUP_TABLE with condition operations
        for i, condition_operator in enumerate(["eq", "ne", "gt", "ge", "lt", "le"]):
            NODE_LOOKUP_TABLE[condition_operator] = {
                "node": "condition",
                "inputs": [
                    ["firstTerm"],
                    ["secondTerm"],
                ],
                # The condition node is a special case!
                # It gets created during the magic-method-comparison and fully connected after
                # being passed on to the cond()-method in this OperatorMetaClass
                "output": [
                    None
                ],
                "operation": i,
            }

        # Fill NODE_LOOKUP_TABLE with +,- operations
        for i, add_sub_operator in enumerate(["add", "sub"]):
            NODE_LOOKUP_TABLE[add_sub_operator] = {
                "node": "plusMinusAverage",
                "inputs": [
                    [
                        "input3D[{multi_index}].input3Dx",
                        "input3D[{multi_index}].input3Dy",
                        "input3D[{multi_index}].input3Dz"
                    ],
                ],
                "multi_index": True,
                "output": ["output3Dx", "output3Dy", "output3Dz"],
                "operation": i + 1,
            }

        # Fill NODE_LOOKUP_TABLE with *,/,** operations
        for i, mult_div_operator in enumerate(["mul", "div", "pow"]):
            NODE_LOOKUP_TABLE[mult_div_operator] = {
                "node": "multiplyDivide",
                "inputs": [
                    ["input1X", "input1Y", "input1Z"],
                    ["input2X", "input2Y", "input2Z"],
                ],
                "output": ["outputX", "outputY", "outputZ"],
                "operation": i + 1,
            }

        # Fill NODE_LOOKUP_TABLE with vectorProduct operations
        for i, vector_product_operator in enumerate(["dot", "cross"]):
            NODE_LOOKUP_TABLE[vector_product_operator] = {
                "node": "vectorProduct",
                "inputs": [
                    ["input1X", "input1Y", "input1Z"],
                    ["input2X", "input2Y", "input2Z"],
                    ["normalizeOutput"],
                ],
                "output": ["outputX", "outputY", "outputZ"],
                "operation": i + 1,
            }

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
            Node-object with condition-node and outColorR-attribute

        Example:
            ::

                Op.condition(Node("pCube1.tx") => 2, Node("pCube2.ty")+2, 5 - 1234567890)
                       |    condition-part    |   "if true"-part   | "if false"-part
        """
        # Make sure condition_node is of expected Node-type!
        # condition_node was created during comparison of Node-object(s)
        if not isinstance(condition_node, Node):
            logger.error("{0} isn't Node-instance.".format(condition_node))
        if cmds.objectType(condition_node.node) != "condition":
            logger.error("{0} isn't of type condition.".format(condition_node))

        condition_inputs = [
            ["colorIfTrueR", "colorIfTrueG", "colorIfTrueB"],
            ["colorIfFalseR", "colorIfFalseG", "colorIfFalseB"],
        ]
        condition_outputs = ["outColorR", "outColorG", "outColorB"]

        max_dim = max([len(_get_unravelled_value_as_list(x)) for x in [if_part, else_part]])

        for i, (condition_node_input, obj_to_connect) in enumerate(
            zip(condition_inputs, [if_part, else_part])
        ):
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
            Node-object with blend-node and outputR-attribute

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
    def distanceBetweenMatrices(matrix_a, matrix_b):
        """
        Create distanceBetween-node hooked up to inMatrix attrs

        Args:
            matrix_a (Node, str): Matrix Plug
            matrix_b (Node, str): Matrix Plug

        Returns:
            Node-object with distanceBetween-node and distance-attribute

        Example:
            >>> Op.len(Node("pCube.worldMatrix"), Node("pCube2.worldMatrix"))
        """
        return _create_and_connect_node('distanceInMatrix', matrix_a, matrix_b)

    @staticmethod
    def clamp(attr_a, min_value=0, max_value=1):
        """
        Create clamp-node

        Args:
            attr_a (Node, str, int, float): Input value
            min_value (Node, int, float, list): min-value for clamp-operation
            max_value (Node, int, float, list): max-value for clamp-operation

        Returns:
            Node-object with clamp-node and output-attribute(s)

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
            Node-object with setRange-node and output-attribute(s)

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
            Node-object with vectorProduct-node and output-attribute(s)

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
            Node-object with vectorProduct-node and output-attribute(s)

        Example:
            >>> Op.cross(Node("pCube.t"), [1, 2, 3], True)
        """
        return _create_and_connect_node('cross', attr_a, attr_b, normalize)

    @staticmethod
    def normalizeVector(in_vector, normalize=True):
        """
        Create vectorProduct-node to normalize the given vector

        Args:
            in_vector (Node, str, int, float, list): Plug or value for vector A
            normalize (Node, boolean): Whether resulting vector should be normalized

        Returns:
            Node-object with vectorProduct-node and output-attribute(s)

        Example:
            >>> Op.normalizeVector(Node("pCube.t"))
        """
        # Making normalize a flag allows the user to connect attributes to it
        return _create_and_connect_node('normalizeVector', in_vector, normalize)

    @staticmethod
    def average(*attrs):
        """
        Create plusMinusAverage-node for averaging input attrs

        Args:
            attrs (Node, string, list): Any number of inputs to be averaged

        Returns:
            Node-object with plusMinusAverage-node and output-attribute(s)

        Example:
            >>> Op.average(Node("pCube.t"), [1, 2, 3])
        """
        return _create_and_connect_node('average', *attrs)

    @staticmethod
    def multMatrix(*attrs):
        """
        Create multMatrix-node for multiplying matrices

        Args:
            attrs (Node, string, list): Any number of matrix inputs to be multiplied

        Returns:
            Node-object with multMatrix-node and output-attribute(s)

        Example:
            out = Node('pSphere')
            matrix_mult = Op.multMatrix(
                Node('pCube1.worldMatrix'), Node('pCube2').worldMatrix
            )
            decomp = Op.decomposeMatrix(matrix_mult)
            out.t = decomp.outputTranslate
            out.r = decomp.outputRotate
            out.s = decomp.outputScale
        """
        return _create_and_connect_node('multMatrix', *attrs)

    @staticmethod
    def decomposeMatrix(in_matrix):
        """
        Create decomposeMatrix-node to disassemble matrix into components (t, rot, etc.)

        Args:
            in_matrix (Node, string): one matrix attribute to be decomposed

        Returns:
            Node-object with decomposeMatrix-node and output-attribute(s)

        Example:
            driver = Node('pCube1')
            driven = Node('pSphere1')
            decomp = Op.decomposeMatrix(driver.worldMatrix)
            driven.t = decomp.outputTranslate
            driven.r = decomp.outputRotate
            driven.s = decomp.outputScale
        """
        return _create_and_connect_node('decomposeMatrix', in_matrix)

    @staticmethod
    def composeMatrix(
            t=0, r=0, s=1, sh=0, ro=0,
            translate=None, rotate=None, scale=None, shear=None, rotateOrder=None,
            useEulerRotation=True,
    ):
        """
        Create composeMatrix-node to assemble matrix from components (translation, rotation etc.)

        Args:
            t (Node, str, int, float): translate for matrix composition
            r (Node, str, int, float): rotate for matrix composition
            s (Node, str, int, float): scale for matrix composition
            sh (Node, str, int, float): shear for matrix composition
            ro (Node, str, int, float): rotateOrder for matrix composition
            translate, rotate, scale, shear, rotateOrder: Reflect the long names
                for the flags above. LongName flags take precedence!

        Returns:
            Node-object with composeMatrix-node and output-attribute(s)

        Example:
            in_a = Node('pCube1')
            in_b = Node('pCube2')
            decomp_a = Op.decomposeMatrix(in_a.worldMatrix)
            decomp_b = Op.decomposeMatrix(in_b.worldMatrix)
            Op.composeMatrix(r=decomp_a.outputRotate, s=decomp_b.outputScale)
        """
        if translate is not None:
            t = translate
        if rotate is not None:
            r = rotate
        if scale is not None:
            s = scale
        if shear is not None:
            sh = shear
        if rotateOrder is not None:
            ro = rotateOrder

        return _create_and_connect_node('composeMatrix', t, r, s, sh, ro, useEulerRotation)

    @staticmethod
    def choice(*inputs, **kwargs):
        """
        Create choice-node to switch between various input attributes

        Args:
            One or many inputs (any type possible). Optional selector (s=node.attr).
            Note: Multi index input seems to also require one 'selector' per index. So we package
            a copy of the same selector for each input

        Returns:
            Node-object with choice-node and output-attribute(s)

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


# Create Operator-class from OperatorMetaClass (check its doc string for reason why)
class Op(object):
    __metaclass__ = OperatorMetaClass


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
        if isinstance(node, numbers.Real) or isinstance(node, (list, tuple)):
            self.__dict__["node"] = None
            self.__dict__["attrs"] = node
        # Initialization with "object.attrs" string
        elif attrs is None and "." in node:
            node_part, attrs_part = node.split(".")
            self.__dict__["node"], self.__dict__["attrs"] = node_part, [attrs_part]
        # Initialization where node and attribute(optional) are specifically given
        else:
            self.__dict__["node"] = node
            if isinstance(attrs, basestring):
                self.__dict__["attrs"] = [attrs]
            else:
                self.__dict__["attrs"] = attrs

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
        if name == "attrs":
            if self.attrs is None:
                logger.error("No attributes on requested Node-object! {}".format(self.node))
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
        if self.node is None:
            return str(self.attrs)
        elif self.attrs is None:
            return str(self.node)
        else:
            return str(self.plug())

    def __repr__(self):
        """
        Repr-method for debugging purposes

        Returns:
            String of separate elements that make up Node-instance
        """
        return "Node('{0}', '{1}')".format(self.node, self.attrs)

    def __len__(self):
        """
        Return the length of the Node-attrs variable.

        Returns:
            Int: 0 if attrs is None, 1 if it's not an array, otherwise len(attrs)
        """
        logger.warn("Using the Node-len method!")
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
        self.attrs[index] = value

    def __getitem__(self, index):
        """
        Support indexed lookup for Node-instances with list-attrs

        Args:
            index (int): Index of desired item

        Returns:
            Object that is at the desired index
        """
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
        if self.node is None:
            return self.attrs
        plug = self.plug()
        if plug is not None:
            if isinstance(plug, (list, tuple)):
                return_value = []
                for elem in plug:
                    return_value.append(self._get_maya_attr(elem))
                return return_value

            else:
                return self._get_maya_attr(plug)
        else:
            return None

    def set(self, value):
        """
        Helper function to allow easy setting of a Node-attributes.
        Equivalent to a setAttr.

        Args:
            value (Node, str, int, float, list, tuple): Connect attributes to this
                object or set attributes to this value/array
        """
        _set_or_connect_a_to_b(self, value)

    def plug(self):
        """
        Helper function to allow easy access to the Node-attributes.

        Returns:
            String of common notation "node.attrs" or None if attrs is undefined!
        """
        if self.attrs is None:
            return None
        elif self.node is None:
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
            >>> Node("pCube1").userAttr.as_bool(value=True)
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
            >>> Node("pCube1").userAttr.as_int(value=123)
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
            >>> Node("pCube1").userAttr.as_float(value=3.21)
        """
        return self._add_traced_attr("float", name, **kwargs)

    def add_enum(self, name, enumName=["Off", "On"], cases=None, **kwargs):
        """
        Create a boolean-attribute for the given attribute

        Args:
            name (str): Name for the new attribute to be created
            enumName (list, str): User-choices for the resulting enum-attribute
            cases (list, str): Overrides enumName, which I find a horrific name
            kwargs (dict): User specified attributes to be set for the new attribute

        Returns:
            The Node-instance with the node and new attribute

        Example:
            >>> Node("pCube1").userAttr.as_enum(cases=["A", "B", "C"], value=2)
        """
        if cases is not None:
            enumName = cases
        if isinstance(enumName, (list, tuple)):
            enumName = ":".join(enumName)

        return self._add_traced_attr("enum", name, enumName=enumName, **kwargs)

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
        if _is_valid_maya_attr(attr):
            return_value = cmds.getAttr(attr)
            # getAttr of 3D-plug returns list of a tuple. This unravels that abomination
            if isinstance(return_value, list):
                if len(return_value) == 1 and isinstance(return_value[0], tuple):
                    return_value = list(return_value[0])
            return return_value
        else:
            return attr

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
            logger.warn("Attribute {} already existed!".format(attr))
            return Node(attr)

        # Make a copy of the default values for the given attrType
        attr_variables = ATTR_LOOKUP_TABLE["base_attr"].copy()
        attr_variables.update(ATTR_LOOKUP_TABLE[attr_type])
        logger.debug("Copied default attr_variables: {}".format(attr_variables))

        # Add the attr variable into the dictionary
        attr_variables["longName"] = attr_name
        # Override default values with kwargs
        attr_variables.update(kwargs)
        logger.debug("Added custom attr_variables: {}".format(attr_variables))

        # Extract attributes that need to be set via setAttr-command
        set_attr_values = {
            "channelBox": attr_variables.pop("channelBox", None),
            "lock": attr_variables.pop("lock", None),
        }
        attr_value = attr_variables.pop("value", None)
        logger.debug("Extracted set_attr-variables from attr_variables: {}".format(attr_variables))
        logger.debug("set_attr-variables: {}".format(set_attr_values))

        # Add the attribute
        _traced_add_attr(self.node, **attr_variables)

        # Filter for any values that need to be set via the setAttr command. Oh Maya...
        set_attr_values = {
            key: val for (key, val) in set_attr_values.iteritems()
            if val is not None
        }
        logger.debug("Pruned set_attr-variables: {}".format(set_attr_values))

        # If there is no value to be set; set any attribute flags directly
        if attr_value is None:
            _traced_set_attr(attr, **set_attr_values)
        else:
            # If a value is given; use the set_or_connect function
            _set_or_connect_a_to_b(attr, attr_value, **set_attr_values)

        return Node(attr)


def _is_valid_maya_attr(attr):
    if isinstance(attr, basestring) and "." in attr and cmds.objExists(attr):
        return True
    else:
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
        if self.trace:
            Node.trace_commands = True
        else:
            Node.trace_commands = False

        Node.flush_command_stack()
        Node.traced_nodes = []
        Node.traced_variables = []

        return Node.executed_commands_stack

    def __exit__(self, type, value, traceback):
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
# CONTAINER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Container(object):
    """
    Container class that creates a container around everything inside the with-statement

    Example:
        ::

            with Container(name="my_cont", notes="Formula: b.ty-2*c.tz", create=True) as cont:
                a.tx = b.ty - 2 * c.tz
    """

    def __init__(self, name="noca_formula_container", notes="", create=True, note=None):
        # Allow either note or notes as keywords
        if not notes and note is not None:
            self.notes = note
        else:
            self.notes = notes
        self.name = name
        self.create = create

    def __enter__(self):
        """
        with-statement; entering-method
        Flushes created_nodes_stack (Node-classAttribute) and creates a container-node
        """
        Node.flush_node_stack()

        # Do not create a container if it should be bypassed
        if not self.create:
            return False

        # Create container and return it
        self.container_node = cmds.container(name=self.name)
        # Returned as the variable after "with Container() as"
        return self.container_node

    def __exit__(self, type, value, traceback):
        """
        with-statement; exit-method
        Stick all nodes that were created within the with-statement into the container
        """
        # Skip everything if the container was not created
        if not self.create:
            return False

        # Add all created nodes to the container
        cmds.container(
            self.container_node,
            edit=True,
            addNode=Node.created_nodes_stack,
            includeNetwork=False,
            includeHierarchyBelow=False,
        )

        # Expose connections in to/out of container
        container_plugs = []
        # listConnections with connections=True returns a single list, where;
        # - every Nth element is plug >X< on the queried node
        # - every N+1th element is the plug that is connected to plug >X<
        # The izip(*[iter()]*2)-part simply creates a list of pairs out of this single list.
        for node in Node.created_nodes_stack:
            connections = cmds.listConnections(
                node,
                plugs=True,
                source=True,
                destination=True,
                connections=True
            )
            connections = izip(*[iter(connections)]*2)

            for plug_inside_container, plug_to_check in connections:
                # plug_to_check is what plug_inside_container is connected to.
                # If that is a node inside the container, too;
                # don't expose a plug on the container for it!
                if plug_to_check.split(".")[0] not in Node.created_nodes_stack:
                    # Ignore the message-plugs
                    if plug_inside_container.split(".")[1] != "message":
                        container_plugs.append(plug_inside_container)

        # For each plug that should be exposed: Generate a name and expose it
        for plug in container_plugs:
            # Make sure there are no forbidden characters in the name
            plug_name = plug.split("|")[-1].split(".")
            node_name = ''.join(e for e in plug_name[0] if e.isalnum())
            attr_name = ''.join(e for e in plug_name[1] if e.isalnum())
            name = node_name + "_I_" + attr_name
            cmds.container(self.container_node, e=True, pb=(plug, name))

        # Add optional notes to the container. notes-attr doesn't exist by default!
        if self.notes:
            if not cmds.attributeQuery("notes", node=self.container_node, exists=True):
                cmds.addAttr(
                    self.container_node,
                    longName="notes",
                    shortName="nts",
                    dataType="string"
                )
            cmds.setAttr(self.container_node + ".notes", str(self.notes), type="string")


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
    logger.debug("Creating a new {}-operationNode with args: {}".format(operation, args))
    new_node_inputs = NODE_LOOKUP_TABLE[operation]["inputs"]
    if NODE_LOOKUP_TABLE[operation].get("multi_index", False):
        new_node_inputs = len(args) * NODE_LOOKUP_TABLE[operation]["inputs"][:]

    # Check dimension-match: args vs. NODE_LOOKUP_TABLE-inputs:
    if len(args) != len(new_node_inputs):
        logger.error(
            "Dimensions to create node don't match! "
            "Given args: {} Required node-inputs: {}".format(args, new_node_inputs)
        )

    # Unravel all given arguments and create a new node according to given operation
    unravelled_args_list = [_get_unravelled_value_as_list(x) for x in args]
    new_node = _traced_create_node(operation, unravelled_args_list)

    # Add to created_nodes_stack Node-classAttr. Necessary for container creation!
    Node.add_to_node_stack(new_node)
    # If the given node-type has a node-operation; set it according to NODE_LOOKUP_TABLE
    node_operation = NODE_LOOKUP_TABLE[operation].get("operation", None)
    if node_operation:
        _set_or_connect_a_to_b(new_node + ".operation", node_operation)

    # Find the maximum dimension involved to know what to connect. For example:
    # 3D to 3D requires 3D-input, 1D to 2D needs 2D-input, 1D to 1D only needs 1D-input
    max_dim = max([len(x) for x in unravelled_args_list])

    for i, (new_node_input, obj_to_connect) in enumerate(zip(new_node_inputs, args)):

        new_node_input_list = [(new_node + "." + x) for x in new_node_input][:max_dim]
        # multi_index inputs must always be caught and filled!
        if NODE_LOOKUP_TABLE[operation].get("multi_index", False):
            new_node_input_list = [x.format(multi_index=i) for x in new_node_input_list]

        # Support for single-dimension-inputs in the NODE_LOOKUP_TABLE. For example:
        # The blend-attr of a blendColors-node is always 1D,
        # so only a 1D obj_to_connect must be given!
        elif len(new_node_input) == 1:
            if len(_get_unravelled_value_as_list(obj_to_connect)) > 1:
                logger.error(
                    "Tried to connect multi-dimensional attribute to 1D input: "
                    "node: {} attrs: {} input: {}".format(
                        new_node,
                        new_node_input,
                        obj_to_connect
                    )
                )
            else:
                logger.debug("Directly connecting 1D input to 1D obj!")
                _set_or_connect_a_to_b(new_node + "." + new_node_input[0], obj_to_connect)
                continue

        _set_or_connect_a_to_b(new_node_input_list, obj_to_connect)

    # Support for single-dimension-outputs in the NODE_LOOKUP_TABLE. For example:
    # distanceBetween returns 1D attr, no matter what dimension the inputs were
    outputs = NODE_LOOKUP_TABLE[operation]["output"]
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
        NODE_LOOKUP_TABLE[operation]["node"]  # Node type as suffix
    ])

    return name


def _traced_create_node(operation, involved_attributes):
    """
    Maya-createNode that adds the executed command to the command_stack if Tracer is active
    Creates a named node of appropriate type for the necessary operation
    """
    node_type = NODE_LOOKUP_TABLE[operation]["node"]
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
                op=NODE_LOOKUP_TABLE[operation]["node"],
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
                Node.add_to_command_stack("cmds.setAttr({}, {}, edit=True, {})".format(attr, value, joined_kwargs))
            else:
                # If only a value was given
                Node.add_to_command_stack("cmds.setAttr({}, {})".format(attr, value))
        else:
            if joined_kwargs:
                # If only kwargs were given
                Node.add_to_command_stack("cmds.setAttr({}, edit=True, {})".format(attr, joined_kwargs))
            else:
                # If neither value or kwargs were given it was a redundant setAttr. Don't store!
                pass


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
            "cmds.connectAttr({0[0]}, {0[1]}, force=True)".format(formatted_attrs)
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
    logger.debug('_set_or_connect_a_to_b({}, {}) - RAW INPUT'.format(obj_a, obj_b))

    # Make sure obj_a and obj_b aren't unspecified
    if obj_a is None:
        logger.error("obj_a is unspecified!")
    if obj_b is None:
        logger.error("obj_b is unspecified!")

    obj_a_unravelled_list = _get_unravelled_value_as_list(obj_a)
    obj_b_unravelled_list = _get_unravelled_value_as_list(obj_b)
    logger.debug('obj_a_unravelled_list {} from obj_a {}'.format(obj_a_unravelled_list, obj_a))
    logger.debug('obj_b_unravelled_list {} from obj_b {}'.format(obj_b_unravelled_list, obj_b))

    obj_a_dim = len(obj_a_unravelled_list)
    obj_b_dim = len(obj_b_unravelled_list)

    # Neither given object can have dimensionality (=list-length) above 3!
    if obj_a_dim > 3:
        logger.error("Dimensionality of obj_a is higher than 3! {}".format(obj_a_unravelled_list))
    if obj_b_dim > 3:
        logger.error("Dimensionality of obj_b is higher than 3! {}".format(obj_b_unravelled_list))
    # #######################
    # Match input-dimensions: After this block both obj_X_unravelled_list's have the same length

    # If the dimensions of both given attributes match: Don't process them
    if obj_a_dim == obj_b_dim:
        pass

    # If one object is a single value/plug; match the others length...
    elif obj_a_dim == 1 or obj_b_dim == 1:
        if obj_a_dim < obj_b_dim:
            # ...by creating a list with the same length
            logger.debug("Matching obj_a_dim to obj_b_dim!")
            obj_a_unravelled_list = obj_a_unravelled_list * obj_b_dim
        else:
            logger.debug("Matching obj_b_dim to obj_a_dim!")
            obj_b_unravelled_list = obj_b_unravelled_list * obj_a_dim
    else:
        # Any other dimension-pairings are not allowed
        logger.error(
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

    logger.debug("obj_a_unravelled_list: {}".format(obj_a_unravelled_list))
    logger.debug("obj_b_unravelled_list: {}".format(obj_b_unravelled_list))
    for obj_a_item, obj_b_item in zip(obj_a_unravelled_list, obj_b_unravelled_list):
        # Make sure obj_a_item exists in the Maya scene and get its dimensionality
        if not cmds.objExists(obj_a_item):
            logger.error("obj_a_item does not exist: {}. Must be Maya-attr!".format(obj_a_item))

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
            logger.error(msg)


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
    logger.debug("_check_for_parent_attribute for {}".format(attribute_list))

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
    logger.debug("About to unravel >{0}< with {1}".format(input_val, type(input_val)))

    unravelled_input = _get_unravelled_value(input_val)
    if not isinstance(unravelled_input, list):
        unravelled_input = [unravelled_input]

    logger.info("Input >{0}< --> unravelled to >{1}<".format(input_val, unravelled_input))

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
    logger.debug("_get_unravelled_value of {}, type {}".format(input_val, type(input_val)))

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
        logger.error(
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
    logger.info("About to unravel plug >{}<".format(input_plug))

    if not cmds.objExists(input_plug):
        logger.error("input_plug does not exist: {}".format(input_plug))

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
        logger.debug("Returning untouched input_plug, it's probably a multi-index attribute!")

    logger.debug("Unravelled input_plug to >{}<".format(input_plug))
    return input_plug
