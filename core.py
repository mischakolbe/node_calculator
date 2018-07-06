"""Create a node-network by entering a math-formula.

:created: 03/04/2018
:author: Mischa Kolbe <mischakolbe@gmail.com>
:credits: Mischa Kolbe, Steven Bills, Marco D'Ambros, Benoit Gielly,
          Adam Vanner, Niels Kleinheinz
:version: 2.0.0


Supported operations:
    .. code-block:: python

        # basic math
        +, -, *, /, **

        # angle_between
        Op.angle_between(vector_a, vector_b=[1, 0, 0])

        # average
        Op.average(*attrs)  # Any number of inputs possible

        # blend
        Op.blend(attr_a, attr_b, blend_value=0.5)

        # choice
        Op.choice(*attrs, selector=1)  # Any number of inputs possible

        # clamp
        Op.clamp(attr_a, min_value=0, max_value=1)

        # compose_matrix
        Op.compose_matrix(t=0, r=0, s=1, sh=0, ro=0)

        # condition
        Op.condition(condition, if_part=False, else_part=True)

        # cross
        Op.cross(attr_a, attr_b=0, normalize=False)

        # decompose_matrix
        Op.decompose_matrix(in_matrix)

        # dot product
        Op.dot(attr_a, attr_b=0, normalize=False)

        # inverse_matrix
        Op.inverse_matrix(in_matrix)

        # length
        Op.length(attr_a, attr_b=0)

        # matrix_distance
        Op.matrix_distance(matrix_a, matrix_b)

        # mult_matrix
        Op.mult_matrix(*attrs)  # Any number of inputs possible

        # normalize_vector
        Op.normalize_vector(in_vector, normalize=True)

        # point_matrix_mult
        Op.point_matrix_mult(in_vector, in_matrix, vector_multiply=False)

        # remap_value
        Op.remap_value(attr_a, output_min=0, output_max=1, input_min=0, input_max=1, values=None)

        # set_range
        Op.set_range(attr_a, min_value=0, max_value=1, old_min_value=0, old_max_value=1)

        # transpose_matrix
        Op.transpose_matrix(in_matrix)


Note:
    In any comment/docString of the NodeCalculator I try to adhere to the convention:
    * node: Unique name of a Maya node in the scene (dagPath only if non-unique name)
    * attr/attribute: Attribute on a Maya node in the scene
    * plug: Combination of node and attribute; node.attr

    NcNode and NcAttrs instances provide these keywords (DO NOT USE AS ATTR NAMES!):
    * attrs: Returns currently stored NcAttrs of this NcNode instance.
    * attrs_list: Returns list of stored attributes: [attr, ...] (list of strings).
    * node: Returns name of Maya node in scene (str).
    * plugs: Returns list of stored plugs: [node.attr, ...] (list of strings).

    NcList instances provide these keywords:
    * nodes: Returns all Maya nodes within the list: [node, ...] (list of strings)

    min/max operations temporary unavailable, due to broken dnMinMax-node:
        .. code-block:: python

            # min
            Op.min(*attrs)  # Any number of inputs possible

            # max
            Op.max(*attrs)  # Any number of inputs possible

            # min_abs
            Op.min_abs(*attrs)  # Any number of inputs possible

            # max_abs
            Op.max_abs(*attrs)  # Any number of inputs possible

            # abs_min_abs
            Op.abs_min_abs(*attrs)  # Any number of inputs possible

            # abs_max_abs
            Op.abs_max_abs(*attrs)  # Any number of inputs possible

Example:
    ::

        import NodeCalculator.core as noca

        a = noca.Node("pCube1")
        b = noca.Node("pCube2")
        c = noca.Node("pCube3")

        with noca.Tracer(pprint_trace=True):
            e = b.add_float(value=c.tx)
            a.s = noca.Op.condition(b.ty - 2 > c.tz, e, [1, 2, 3])
"""


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import numbers
import itertools
import copy

# Third party imports
from maya import cmds
from maya.api import OpenMaya
import pymel.core as pm

# Local imports
from . import logger
from . import lookup_table
from . import om_util
from . import nc_value
reload(logger)
reload(lookup_table)
reload(om_util)
reload(nc_value)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
NODE_NAME_PREFIX = "nc"  # Common prefix for all nodes created by nodeCalculator
STANDARD_SEPARATOR_NICENAME = "________"
STANDARD_SEPARATOR_VALUE = "________"
GLOBAL_AUTO_CONSOLIDATE = True
GLOBAL_AUTO_UNRAVEL = True
VARIABLE_BASE_NAME = "var"
VALUE_BASE_NAME = "val"


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
LOG = logger.log


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PYTHON 2.7 & 3 COMPATIBILITY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
try:
    basestring
except NameError:
    basestring = str


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# BASIC FUNCTIONALITY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Node(object):
    """Return instance of appropriate type, based on given args

    Note:
        Node is an abstract class that returns components of appropriate type
        that can then be involved in a NodeCalculator calculation.

    Args:
        item (bool, int, float, str, list, tuple): Maya node, value, list of nodes, etc.
        attrs (str, list, tuple): String or list of strings that are an attribute on this node
        auto_unravel (bool): Whether or not this instance should be unravelled if possible
        auto_consolidate (bool): Whether or not this instance should be consolidated if possible

    Returns:
        NcNode, NcList, NcValue: Instance with given args.

    Example:
        ::

            Node("pCube.tx") -> NcNode instance with pCube1 as node and tx in its NcAttrs instance
            Node([1, "pCube"]) -> NcList instance with value 1 and NcNode with pCube1
            Node(1) -> NcIntValue instance with value 1
    """

    def __new__(cls, item, attrs=None, auto_unravel=None, auto_consolidate=None, *args, **kwargs):
        if args:
            LOG.warn("unrecognized args: %s" % (str(args)))
        if kwargs:
            LOG.warn("unrecognized kwargs: %s" % (str(kwargs)))

        # Redirect plain values right away to a nc_value
        if isinstance(item, numbers.Real):
            LOG.info("Node: Redirecting to NcValue(%s)" % (str(item)))
            return nc_value.value(item)

        # Redirect lists or tuples right away to a NcList
        if isinstance(item, (list, tuple)):
            LOG.info("Node: Redirecting to NcList(%s)" % (str(item)))
            return NcList(item)

        # Redirect NcAttrs right away to a new NcNode
        if isinstance(item, NcAttrs):
            LOG.info("Node: Redirecting to NcNode(%s)" % (str(item)))
            # If auto_unravel/auto_consolidate are not specifically given: Use item settings!
            if auto_unravel is None:
                auto_unravel = item._auto_unravel
            if auto_consolidate is None:
                auto_consolidate = item._auto_consolidate
            return NcNode(item._node_mobj, item, auto_unravel, auto_consolidate)

        LOG.info("Node: Redirecting to NcNode(%s)" % (str(item)))
        # If auto_unravel/auto_consolidate are not specifically given: Turn them on!
        if auto_unravel is None:
            auto_unravel = True
        if auto_consolidate is None:
            auto_consolidate = True

        return NcNode(item, attrs, auto_unravel, auto_consolidate)

    def __init__(self, *args, **kwargs):
        """
        The init of this abstract class must not do anything: The init of the
        class it got redirected to must take care of this!
        """
        pass


def transform(name=None, **kwargs):
    """Convenience function to create a transform as a NcNode

    Args:
        name (str): Name of transform instance that will be created
        kwargs (): keyword arguments that are passed to create_node function

    Returns:
        NcNode: instance that is linked to the newly created transform

    Example:
        ::
            a = noca.transform("myTransform")
            a.t = [1, 2, 3]
    """
    return create_node(node_type="transform", name=name, **kwargs)


def locator(name=None, **kwargs):
    """Convenience function to create a locator as a NcNode

    Args:
        name (str): Name of locator instance that will be created
        kwargs (): keyword arguments that are passed to create_node function

    Returns:
        NcNode: instance that is linked to the newly created locator

    Example:
        ::
            a = noca.locator("myLoc")
            a.t = [1, 2, 3]
    """
    return create_node(node_type="locator", name=name, **kwargs)


def create_node(node_type, name=None, **kwargs):
    """Convenience function to create a new node of given type as a NcNode

    Args:
        node_type (str): Type of Maya node to be created
        name (str): Name for new Maya-node
        kwargs (): arguments that are passed to Maya createNode function

    Returns:
        NcNode: instance that is linked to the newly created transform

    Example:
        ::
            a = noca.create_node("transform", "myTransform")
            a.t = [1, 2, 3]
    """
    node = _traced_create_node(node_type, name=name, **kwargs)
    noca_node = Node(node)

    return noca_node


def set_global_auto_unravel(state):
    """Set the global auto unravel state.

    Note:
        Auto unravel tries to break up parent attributes into its child attributes:
        "t" becomes ["tx", "ty", "tz"].

        This behaviour is desired in most cases for the node calculator to work.
        But in some cases the user might want to prevent this. For example: When
        using the choice-node the user probably wants the inputs to be exactly
        the ones chosen (not broken up into child-attributes and those connected
        to the choice node).

    Args:
        state (bool): State auto unravel should be set to
    """
    global GLOBAL_AUTO_UNRAVEL
    GLOBAL_AUTO_UNRAVEL = state


def set_global_auto_consolidate(state):
    """Set the global auto consolidate state.

    Note:
        Auto consolidate tries to combine full sets of child attributes into the parent attribute:
        ["tx", "ty", "tz"] becomes "t".

        Consolidating plugs is preferable: it will make your node graph cleaner and
        easier to read. However: Using parent plugs can sometimes cause update-issues!

    Args:
        state (bool): State auto consolidate should be set to
    """
    global GLOBAL_AUTO_CONSOLIDATE
    GLOBAL_AUTO_CONSOLIDATE = state


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# OPERATORS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class OperatorMetaClass(object):
    """Base class for NodeCalculator operators: Everything that goes beyond basic math (+-*/)

    Note:
        A meta-class was used, so methods of this class can be created on the fly
        in the __init__ method. Additionally; it ensures this to be a singleton class.
    """

    def __init__(self, name, bases, body):
        """Operator-class constructor

        Note:
            name, bases, body are necessary for metaClass to work properly
        """
        super(OperatorMetaClass, self).__init__()

    @staticmethod
    def angle_between(vector_a, vector_b=[1, 0, 0]):
        """Create angleBetween-node to find the angle between 2 vectors

        Args:
            vector_a (NcNode, NcAttrs, int, float, list): Vector a to consider for angle
            vector_b (NcNode, NcAttrs, int, float, list): Vector b to consider for angle

        Returns:
            NcNode: Instance with angleBetween-node and output-attribute(s)

        Example:
            Op.angle_between(
                Op.point_matrix_mult(
                    [1, 0, 0],
                    Node("pCube1").worldMatrix,
                    vector_multiply=True
                ),
                [1, 0, 0]
            )
        """
        return _create_and_connect_node('angle_between', vector_a, vector_b)

    @staticmethod
    def average(*attrs):
        """Create plusMinusAverage-node for averaging input attrs

        Args:
            attrs (NcNode, NcAttrs, string, list): Any number of inputs to be averaged

        Returns:
            NcNode: Instance with plusMinusAverage-node and output-attribute(s)

        Example:
            >>> Op.average(Node("pCube.t"), [1, 2, 3])
        """
        return _create_and_connect_node('average', *attrs)

    @staticmethod
    def blend(attr_a, attr_b, blend_value=0.5):
        """Create blendColor-node

        Args:
            attr_a (NcNode, NcAttrs, str, int, float): Plug or value to blend from
            attr_b (NcNode, NcAttrs, str, int, float): Plug or value to blend to
            blend_value (NcNode, str, int, float): Plug or value defining blend-amount

        Returns:
            NcNode: Instance with blend-node and output-attributes

        Example:
            >>> Op.blend(1, Node("pCube.tx"), Node("pCube.customBlendAttr"))
        """
        return _create_and_connect_node('blend', attr_a, attr_b, blend_value)

    @staticmethod
    def choice(*inputs, **kwargs):
        """Create choice-node to switch between various input attributes

        Note:
            Multi index input seems to also require one 'selector' per index.
            So we package a copy of the same selector for each input.

        Args:
            One or many inputs (any type possible). Optional selector (s=node.attr).

        Returns:
            NcNode: Instance with choice-node and output-attribute(s)

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
        _unravel_and_set_or_connect_a_to_b(choice_node_obj.selector, kwargs.get("selector", 0))

        return choice_node_obj

    @staticmethod
    def clamp(attr_a, min_value=0, max_value=1):
        """Create clamp-node

        Args:
            attr_a (NcNode, NcAttrs, str, int, float): Input value
            min_value (NcNode, NcAttrs, int, float, list): min-value for clamp-operation
            max_value (NcNode, NcAttrs, int, float, list): max-value for clamp-operation

        Returns:
            NcNode: Instance with clamp-node and output-attribute(s)

        Example:
            >>> Op.clamp(Node("pCube.t"), [1, 2, 3], 5)
        """
        return _create_and_connect_node('clamp', attr_a, min_value, max_value)

    @staticmethod
    def compose_matrix(**kwargs):
        """Create composeMatrix-node to assemble matrix from components (translation, rotation etc.)

        Args:
            kwargs: Possible kwargs described below (longName flags take precedence!)
            translate (NcNode, NcAttrs, str, int, float): [t] translate for matrix composition
            rotate (NcNode, NcAttrs, str, int, float): [r] rotate for matrix composition
            scale (NcNode, NcAttrs, str, int, float): [s] scale for matrix composition
            shear (NcNode, NcAttrs, str, int, float): [sh] shear for matrix composition
            rotate_order (NcNode, NcAttrs, str, int, float): [ro] rotate_order for matrix composition
            euler_rotation (NcNode, NcAttrs, bool): Apply Euler filter on rotations

        Returns:
            NcNode: Instance with composeMatrix-node and output-attribute(s)

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
    def condition(condition_node, if_part=False, else_part=True):
        """Set up condition-node.

        Note:
            condition_node must be a NcNode-instance of a Maya condition node.
            This NcNode-object gets automatically created by the overloaded
            comparison-operators of the NcNode-class and should not require manual setup!
            Simply use the usual comparison operators (==, >, <=, etc.) in the first argument.

        Args:
            condition_node (NcNode): Condition-statement. NcNode is automatically created; see notes!
            if_part (NcNode, NcAttrs, str, int, float): Value/plug if condition is true
            else_part (NcNode, NcAttrs, str, int, float): Value/plug if condition is false

        Returns:
            NcNode: Instance with condition-node and outColor-attributes

        Example:
            ::

                Op.condition(Node("pCube1.tx") >= 2, Node("pCube2.ty")+2, 5 - 1234567890)
                            |    condition-part    |   "if true"-part   |  "else"-part  |
        """
        # Make sure condition_node is of expected Node-type!
        # condition_node was created during comparison of NcNode-object(s)
        if not isinstance(condition_node, NcNode):
            LOG.error("%s isn't NcNode-instance." % (str(condition_node)))
        if cmds.objectType(condition_node.node) != "condition":
            LOG.error("%s isn't of type condition." % (str(condition_node)))

        condition_inputs = [
            ["colorIfTrueR", "colorIfTrueG", "colorIfTrueB"],
            ["colorIfFalseR", "colorIfFalseG", "colorIfFalseB"],
        ]
        condition_outputs = ["outColorR", "outColorG", "outColorB"]

        max_dim = max([len(_unravel_item_as_list(x)) for x in [if_part, else_part]])

        for condition_node_input, obj_to_connect in zip(condition_inputs, [if_part, else_part]):
            condition_node_input_list = [
                (condition_node.node + "." + x) for x in condition_node_input[:max_dim]
            ]

            _unravel_and_set_or_connect_a_to_b(condition_node_input_list, obj_to_connect)

        return Node(condition_node.node, condition_outputs[:max_dim])

    @staticmethod
    def cross(attr_a, attr_b=0, normalize=False):
        """Create vectorProduct-node for vector cross-multiplication

        Args:
            attr_a (NcNode, NcAttrs, str, int, float, list): Plug or value for vector A
            attr_b (NcNode, NcAttrs, str, int, float, list): Plug or value for vector B
            normalize (NcNode, NcAttrs, boolean): Whether resulting vector should be normalized

        Returns:
            NcNode: Instance with vectorProduct-node and output-attribute(s)

        Example:
            >>> Op.cross(Node("pCube.t"), [1, 2, 3], True)
        """
        return _create_and_connect_node('cross', attr_a, attr_b, normalize)

    @staticmethod
    def decompose_matrix(in_matrix):
        """Create decomposeMatrix-node to disassemble matrix into components (t, rot, etc.)

        Args:
            in_matrix (NcNode, NcAttrs, string): one matrix attribute to be decomposed

        Returns:
            NcNode: Instance with decomposeMatrix-node and output-attribute(s)

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
    def dot(attr_a, attr_b=0, normalize=False):
        """Create vectorProduct-node for vector dot-multiplication

        Args:
            attr_a (NcNode, NcAttrs, str, int, float, list): Plug or value for vector A
            attr_b (NcNode, NcAttrs, str, int, float, list): Plug or value for vector B
            normalize (NcNode, NcAttrs, boolean): Whether resulting vector should be normalized

        Returns:
            NcNode: Instance with vectorProduct-node and output-attribute(s)

        Example:
            >>> Op.dot(Node("pCube.t"), [1, 2, 3], True)
        """
        return _create_and_connect_node('dot', attr_a, attr_b, normalize)

    @staticmethod
    def inverse_matrix(in_matrix):
        """Create inverseMatrix-node to invert the given matrix

        Args:
            in_matrix (NcNode, NcAttrs, str): Plug or value for in_matrix

        Returns:
            NcNode: Instance with inverseMatrix-node and output-attribute(s)

        Example:
            >>> Op.inverse_matrix(Node("pCube.worldMatrix"))
        """

        return _create_and_connect_node('inverse_matrix', in_matrix)

    @staticmethod
    def length(attr_a, attr_b=0):
        """Create distanceBetween-node

        Args:
            attr_a (NcNode, NcAttrs, str, int, float): Plug or value for point A
            attr_b (NcNode, NcAttrs, str, int, float): Plug or value for point B

        Returns:
            NcNode-object with distanceBetween-node and distance-attribute

        Example:
            >>> Op.len(Node("pCube.t"), [1, 2, 3])
        """
        return _create_and_connect_node('length', attr_a, attr_b)

    @staticmethod
    def matrix_distance(matrix_a, matrix_b):
        """Create distanceBetween-node hooked up to inMatrix attrs

        Args:
            matrix_a (NcNode, NcAttrs, str): Matrix Plug
            matrix_b (NcNode, NcAttrs, str): Matrix Plug

        Returns:
            NcNode: Instance with distanceBetween-node and distance-attribute

        Example:
            >>> Op.len(Node("pCube.worldMatrix"), Node("pCube2.worldMatrix"))
        """
        return _create_and_connect_node('matrix_distance', matrix_a, matrix_b)

    @staticmethod
    def mult_matrix(*attrs):
        """Create multMatrix-node for multiplying matrices

        Args:
            attrs (NcNode, NcAttrs, string, list): Any number of matrix inputs to be multiplied

        Returns:
            NcNode: Instance with multMatrix-node and output-attribute(s)

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
    def normalize_vector(in_vector, normalize=True):
        """Create vectorProduct-node to normalize the given vector

        Args:
            in_vector (NcNode, NcAttrs, str, int, float, list): Plug or value for vector A
            normalize (NcNode, NcAttrs, boolean): Whether resulting vector should be normalized

        Returns:
            NcNode: Instance with vectorProduct-node and output-attribute(s)

        Example:
            >>> Op.normalize_vector(Node("pCube.t"))
        """
        # Making normalize a flag allows the user to connect attributes to it
        return _create_and_connect_node('normalize_vector', in_vector, normalize)

    @staticmethod
    def point_matrix_mult(in_vector, in_matrix, vector_multiply=False):
        """Create pointMatrixMult-node to transpose the given matrix

        Args:
            in_vector (NcNode, NcAttrs, str, int, float, list): Plug or value for in_vector
            in_matrix (NcNode, NcAttrs, str): Plug or value for in_matrix
            vector_multiply (NcNode, NcAttrs, str, int, bool): Plug or value for vector_multiply

        Returns:
            NcNode: Instance with pointMatrixMult-node and output-attribute(s)

        Example:
            Op.point_matrix_mult(
                Node("pSphere.t"),
                Node("pCube.worldMatrix"),
                vector_multiply=True
            )
        """

        created_node = _create_and_connect_node(
            'point_matrix_mult',
            in_vector,
            in_matrix,
            vector_multiply
        )

        return created_node

    @staticmethod
    def remap_value(attr_a, output_min=0, output_max=1, input_min=0, input_max=1, values=None):
        """Create remapValue-node

        Args:
            attr_a (NcNode, NcAttrs, str, int, float): Input value
            output_min (NcNode, NcAttrs, int, float, list): min-value
            output_max (NcNode, NcAttrs, int, float, list): max-value
            input_min (NcNode, NcAttrs, int, float, list): old min-value
            input_max (NcNode, NcAttrs, int, float, list): old max-value
            values (list): List of tuples (value_Position, value_FloatValue, value_Interp)

        Returns:
            NcNode: Instance with remapValue-node and output-attribute(s)

        Example:
            >>> Op.remap_value(Node("pCube.t"), values=[(0.1, .2, 0), (0.4, 0.3)])
        """

        created_node = _create_and_connect_node(
            'remap_value', attr_a, output_min, output_max, input_min, input_max
        )

        for index, value_data in enumerate(values or []):
            # value_Position, value_FloatValue, value_Interp
            # "x-axis", "y-axis", interpolation

            if not isinstance(value_data, (list, tuple)):
                LOG.error(
                    "The values-flag for remap_value requires a list of tuples! "
                    "Got %s instead." % (str(values))
                )

            elif len(value_data) == 2:
                pos, val = value_data
                interp = 1

            elif len(value_data) == 3:
                pos, val, interp = value_data

            else:
                LOG.error(
                    "The values-flag for remap_value requires a list of tuples "
                    "of length 2 or 3! Got %s instead." % (str(values))
                )

            # Set these attributes directly to avoid unnecessary unravelling.
            _traced_set_attr(
                "{}.value[{}]".format(created_node.node, index),
                (pos, val, interp)
            )

        return created_node

    @staticmethod
    def set_range(attr_a, min_value=0, max_value=1, old_min_value=0, old_max_value=1):
        """Create setRange-node

        Args:
            attr_a (NcNode, NcAttrs, str, int, float): Input value
            min_value (NcNode, NcAttrs, int, float, list): min-value
            max_value (NcNode, NcAttrs, int, float, list): max-value
            old_min_value (NcNode, NcAttrs, int, float, list): old min-value
            old_max_value (NcNode, NcAttrs, int, float, list): old max-value

        Returns:
            NcNode: Instance with setRange-node and output-attribute(s)

        Example:
            >>> Op.set_range(Node("pCube.t"), [1, 2, 3], 4, [-1, 0, -2])
        """
        return _create_and_connect_node(
            'set_range', attr_a, min_value, max_value, old_min_value, old_max_value
        )

    @staticmethod
    def transpose_matrix(in_matrix):
        """Create transposeMatrix-node to transpose the given matrix

        Args:
            in_matrix (NcNode, NcAttrs, str): Plug or value for in_matrix

        Returns:
            NcNode: Instance with transposeMatrix-node and output-attribute(s)

        Example:
            >>> Op.transpose_matrix(Node("pCube.worldMatrix"))
        """

        return _create_and_connect_node('transpose_matrix', in_matrix)


class Op(object):
    """Create Operator-class from OperatorMetaClass (check its docString for details)"""
    __metaclass__ = OperatorMetaClass


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NcBaseClass
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NcBaseClass(object):
    """Base class for NcLists & NcBaseNode (therefore indirectly NcNode & NcAttrs).

    Note:
        NcNode, NcAttrs and NcList are the "building blocks" of NodeCalculator calculations.
        Having NcBaseClass as their common parent class makes sure the overloaded operators
        apply to each of these "building blocks".
    """

    # Class variable; Whether Tracer is active or not
    _is_tracing = False
    # Class variable; Executed Maya commands the NodeCalculator keeps track of, if Tracer is active
    _executed_commands_stack = []
    # Class variable; Created Maya nodes the NodeCalculator keeps track of, if Tracer is active
    _traced_nodes = None
    # Class variable; Queried values the NodeCalculator keeps track of, if Tracer is active
    _traced_values = None

    def __init__(self):
        super(NcBaseClass, self).__init__()

    def __pos__(self):
        """Leading plus signs are ignored

        Example:
            >>> + Node("pCube1.ty")
        """
        LOG.debug("%s __pos__ (%s)" % (self.__class__.__name__, str(self)))

        pass

    def __neg__(self):
        """Leading minus sign multiplies by -1

        Example:
            >>> - Node("pCube1.ty")
        """
        LOG.debug("%s __neg__ (%s)" % (self.__class__.__name__, str(self)))

        result = self * -1
        return result

    def __add__(self, other):
        """Regular addition operator.

        Example:
            >>> Node("pCube1.ty") + 4
        """
        LOG.debug(
            "%s __add__ (%s, %s)" % (self.__class__.__name__, str(self), str(other))
        )

        return _create_and_connect_node("add", self, other)

    def __radd__(self, other):
        """Reflected addition operator.

        Note:
            Fall-back method in case regular addition is not defined & fails.

        Example:
            >>> 4 + Node("pCube1.ty")
        """
        LOG.debug("%s __radd__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return _create_and_connect_node("add", other, self)

    def __sub__(self, other):
        """Regular subtraction operator.

        Example:
            >>> Node("pCube1.ty") - 4
        """
        LOG.debug("%s __sub__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return _create_and_connect_node("sub", self, other)

    def __rsub__(self, other):
        """Reflected subtraction operator.

        Note:
            Fall-back method in case regular subtraction is not defined & fails.

        Example:
            >>> 4 - Node("pCube1.ty")
        """
        LOG.debug("%s __rsub__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return _create_and_connect_node("sub", other, self)

    def __mul__(self, other):
        """Regular multiplication operator.

        Example:
            >>> Node("pCube1.ty") * 4
        """
        LOG.debug("%s __mul__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return _create_and_connect_node("mul", self, other)

    def __rmul__(self, other):
        """Reflected multiplication operator.

        Note:
            Fall-back method in case regular multiplication is not defined & fails.

        Example:
            >>> 4 * Node("pCube1.ty")
        """
        LOG.debug("%s __rmul__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return _create_and_connect_node("mul", other, self)

    def __div__(self, other):
        """Regular division operator.

        Example:
            >>> Node("pCube1.ty") / 4
        """
        LOG.debug("%s __div__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return _create_and_connect_node("div", self, other)

    def __rdiv__(self, other):
        """Reflected division operator.

        Note:
            Fall-back method in case regular division is not defined & fails.

        Example:
            >>> 4 / Node("pCube1.ty")
        """
        LOG.debug("%s __rdiv__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return _create_and_connect_node("div", other, self)

    def __pow__(self, other):
        """Regular power operator.

        Example:
            >>> Node("pCube1.ty") ** 4
        """
        LOG.debug("%s __pow__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return _create_and_connect_node("pow", self, other)

    def __eq__(self, other):
        """Equality operator: ==

        Returns:
            NcNode-instance of a newly created Maya condition-node
        """
        LOG.debug("%s __eq__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return self._compare(other, "eq")

    def __ne__(self, other):
        """Inequality operator: !=

        Returns:
            NcNode-instance of a newly created Maya condition-node
        """
        LOG.debug("%s __ne__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return self._compare(other, "ne")

    def __gt__(self, other):
        """Greater than operator: >

        Returns:
            NcNode-instance of a newly created Maya condition-node
        """
        LOG.debug("%s __gt__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return self._compare(other, "gt")

    def __ge__(self, other):
        """Greater equal operator: >=

        Returns:
            NcNode-instance of a newly created Maya condition-node
        """
        LOG.debug("%s __ge__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return self._compare(other, "ge")

    def __lt__(self, other):
        """Less than operator: <

        Returns:
            NcNode-instance of a newly created Maya condition-node
        """
        LOG.debug("%s __lt__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return self._compare(other, "lt")

    def __le__(self, other):
        """Less equal operator: <=

        Returns:
            NcNode-instance of a newly created Maya condition-node
        """
        LOG.debug("%s __le__ (%s, %s)" % (self.__class__.__name__, str(self), str(other)))

        return self._compare(other, "le")

    def _compare(self, other, operator):
        """Create a Maya condition node, set to the correct operation-type.

        Args:
            other (NcNode, int, float): Attr or value to compare self-attrs with
            operator (string): Operation type available in Maya condition-nodes

        Returns:
            NcNode-instance of a newly created Maya condition-node
        """
        # Create new condition node set to the appropriate operation-type
        return_value = _create_and_connect_node(operator, self, other)

        return return_value

    @classmethod
    def _initialize_trace_variables(cls):
        """Reset all class variables used for tracing."""
        cls._flush_command_stack()
        cls._flush_traced_nodes()
        cls._flush_traced_values()

    @classmethod
    def _flush_command_stack(cls):
        """Reset the class-variable _executed_commands_stack to an empty list."""
        cls._executed_commands_stack = []

    @classmethod
    def _flush_traced_nodes(cls):
        """Reset the class-variable _traced_nodes to an empty list."""
        cls._traced_nodes = []

    @classmethod
    def _flush_traced_values(cls):
        """Reset the class-variable _traced_values to an empty list."""
        cls._traced_values = []

    @classmethod
    def _add_to_command_stack(cls, command):
        """Add a command to the class-variable _executed_commands_stack

        Args:
            command (str, list): Maya command-string or list of Maya command-strings
        """
        if isinstance(command, (list, tuple)):
            cls._executed_commands_stack.extend(command)
        else:
            cls._executed_commands_stack.append(command)

    @classmethod
    def _add_to_traced_nodes(cls, node):
        """Add a node to the class-variable _traced_nodes

        Args:
            node (TracerMObject): MObject with metadata. Check docString of TracerMObject
        """
        cls._traced_nodes.append(node)

    @classmethod
    def _get_next_variable_name(cls):
        """Return the next available variable name.

        Note:
            When Tracer is active, created nodes get a variable name assigned.

        Returns:
            variable_name (str): Next available variable name.
        """
        variable_name = "{}{}".format(VARIABLE_BASE_NAME, len(cls._traced_nodes) + 1)
        return variable_name

    @classmethod
    def _get_tracer_variable_for_node(cls, node):
        """Try to find and return traced variable for given node.

        Args:
            node (str): Name of Maya node

        Returns:
            variable (str, None): If there is a traced variable for this node:
                Return the variable, otherwise return None
        """
        for traced_node_mobj in cls._traced_nodes:
            if traced_node_mobj.node == node:
                return traced_node_mobj.tracer_variable

        return None

    @classmethod
    def _add_to_traced_values(cls, value):
        """Add a value to the class-variable _traced_values

        Args:
            value (NcValue): Value (int, float, ...) with metadata. Check docString of NcValue.
        """
        cls._traced_values.append(value)

    @classmethod
    def _get_next_value_name(cls):
        """Return the next available value name.

        Note:
            When Tracer is active, queried values get a value name assigned.

        Returns:
            value_name (str): Next available value name.
        """
        value_name = "{}{}".format(VALUE_BASE_NAME, len(cls._traced_values) + 1)
        return value_name


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NcBaseNode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NcBaseNode(NcBaseClass):
    """Base class for NcNode and NcAttrs.

    Note:
        This class will have access to the .node and .attrs attributes, once it
        is instantiated in the form of a NcNode or NcAttrs instance.
    """

    def __init__(self):
        """Initialization of any NcBaseNode class.

        Note:
            For more detail about auto_unravel & auto_consolidate check
            docString of set_global_auto_consolidate & set_global_auto_unravel!

        Args:
            auto_unravel (bool): Whether attrs of this instance should be unravelled.
            auto_consolidate (bool): Whether attrs of this instance should be consolidated.
        """
        super(NcBaseClass, self).__init__()

        self.__dict__["_holder_node"] = None
        self.__dict__["_held_attrs"] = None

        self._add_all_add_attr_methods()

    def __len__(self):
        """Return the length of the stored attributes list.

        Returns:
            length (int): Length of stored NcAttrs list. 0 if no Attrs are defined.
        """
        return len(self.attrs_list)

    def __str__(self):
        """Readable format of NcBaseNode instance.

        Note:
            For example invoked by using print(NcNode or NcAttrs instance) in Maya

        Returns:
            string (str): String of concatenated node and attrs.

        """
        return "(Node: {}, Attrs: {})".format(self.node, self.attrs_list)

    def __repr__(self):
        """Unambiguous format of NcBaseNode instance.

        Note:
            For example invoked by running highlighted NcNode or NcAttrs instance in Maya

        Returns:
            string (str): String of concatenated class-type, node and attrs.
        """
        return "{}({}, {})".format(self.__class__.__name__, self.node, self.attrs_list)

    def __iter__(self):
        """Generator to iterate over list of attributes.

        Yields:
            Node (NcNode): Next item in list of attributes.
        """
        LOG.debug("%s __iter__ (%s)" % (self.__class__.__name__, str(self)))

        i = 0
        while True:
            try:
                yield NcNode(self.node, self.attrs_list[i])
            except IndexError:
                raise StopIteration
            i += 1

    @property
    def plugs(self):
        """Property to allow easy access to the Node-plugs.

        Note:
            I refer to "node.attr" as a "plug"!

        Returns:
            return_list (list): List of plugs. Empty list if no attributes are defined!
        """
        if len(self.attrs) == 0:
            return []

        return_list = [
            "{}.{}".format(self.node, attr) for attr in self.attrs_list
        ]
        return return_list

    @property
    def nodes(self):
        """Property that returns node within list.

        Note:
            This property mostly exists to maintain consistency with NcList.
            Even though nodes of a NcNode/NcAttrs instance will always be a list
            of length 1 it might come in handy to match the property of NcLists!

        Returns:
            return_list (list): Name of Maya node this instance refers to, in a list.
        """
        return [self.node]

    def get(self):
        """Get the value of a NcNode/NcAttrs-attribute.

        Note:
            Works similar to a cmds.getAttr().

        Returns:
            return_value (int, float, list): Value of the queried attribute.
        """
        LOG.debug("%s get (%s)" % (self.__class__.__name__, str(self)))

        # If only a single attribute exists: Return its value directly
        if len(self.attrs_list) == 1:
            return_value = _traced_get_attr(self.plugs[0])
        # If multiple attributes exist: Return list of values
        elif len(self.attrs_list):
            return_value = [_traced_get_attr(x) for x in self.plugs]
        # If no attribute is given on Node: Warn user and return None
        else:
            LOG.warn("No attribute exists on %s! Returned None" % (str(self)))
            return_value = None

        return return_value

    def set(self, value):
        """Set or connect the value of a NcNode/NcAttrs-attribute.

        Note:
            Similar to a cmds.setAttr().

        Args:
            value (NcNode, NcAttrs, str, int, float, list, tuple): Connect
                attribute to this value (=object) or set attribute to this value/array
        """
        LOG.debug("%s set (%s)" % (self.__class__.__name__, str(value)))

        _unravel_and_set_or_connect_a_to_b(self, value)

    def get_shapes(self, full=False):
        """Convenience method to get shape nodes of self.node

        Note:
            Returned MObjects of shapes can can be used directly to create new NcNode instances!

        Args:
            full (bool): True returns full dag path, False returns shortest dag path

        Returns:
            shapes (list): List of MObjects of shapes.
        """

        shape_mobjs = om_util.get_shape_mobjs(self._node_mobj)

        if full:
            shapes = [om_util.get_long_name_of_mobj(mobj, full=True) for mobj in shape_mobjs]
        else:
            shapes = [om_util.get_name_of_mobj(mobj) for mobj in shape_mobjs]

        return shapes

    def info(self):
        """Convenience method to see the status of _auto_unravel and _auto_consolidate."""
        message = "auto_unravel: {}, auto_consolidate: {}".format(
            self._auto_unravel, self._auto_consolidate
        )
        print(message)

    def to_py_node(self):
        """Convenience function to get a PyNode from a NcNode/NcAttrs instance

        Returns:
            py_node (pm.PyNode): PyNode-instance of this node or plug
        """
        if not self.attrs_list:
            return pm.PyNode(self.node)
        if len(self.attrs_list) == 1:
            return pm.PyNode(self.plugs[0])

        LOG.error(
            "Tried to create PyNode from NcNode with multiple attributes: %s "
            "PyNode only supports node or single attributes!" % (str(self))
        )
        return None

    def set_auto_unravel(self, state):
        """Allows the user to change the auto unravelling state on the fly.

        Note:
            For more info about _auto_unravel: Check docString of set_global_auto_unravel

        Args:
            state (bool): Desired auto unravel state: On/Off
        """
        self.__dict__["_auto_unravel"] = state

    def set_auto_consolidate(self, state):
        """Allows the user to change the auto consolidating state on the fly.

        Note:
            For more info about _auto_consolidate: Check docString of set_global_auto_consolidate

        Args:
            state (bool): Desired auto consolidate state: On/Off
        """
        self.__dict__["_auto_consolidate"] = state

    def _add_all_add_attr_methods(self):
        """Add all possible attribute types for add_XYZ() methods via closure.

        Note:
            Allows to add attributes, similar to addAttr-command.

        Example:
            Node("pCube1").add_float("my_float_attr", defaultValue=1.1)
            Node("pCube1").add_short("my_int_attr", keyable=False)
        """
        for attr_type, attr_data in lookup_table.ATTR_TYPES.iteritems():
            # enum must be handled individually because of enumNames-flag
            if attr_type == "enum":
                continue

            data_type = attr_data["data_type"]
            func = self._define_add_attr_method(attr_type, data_type)
            self.__dict__["add_{}".format(attr_type)] = func

    def _define_add_attr_method(self, attr_type, default_data_type):
        """Closure to add add_XYZ() methods.

        Note:
            Check docString of _add_all_add_attr_methods.

        Args:
            attr_type (str): Name of data type of this attribute: bool, long, short, ...
            default_data_type (str): Either "attributeType" or "dataType". Refer to Maya docs.

        Returns:
            func (function): Function that will be added to class methods.
        """

        def func(name, **kwargs):
            """Create an attribute with given name and kwargs

            Note:
                kwargs are exactly the same as in cmds.addAttr()!

            Args:
                name (str): Name for the new attribute to be created
                kwargs (dict): User specified attributes to be set for the new attribute

            Returns:
                attr (NcNode): NcNode-instance with the node and new attribute.

            Example:
                >>> Node("pCube1").add_bool(value=True)
            """

            data_type = default_data_type
            # Since I opted for attributeType for all types that allowed
            # dataType and attributeType: Only a dataType keyword has relevance.
            if kwargs.get("dataType", None):
                data_type = "dataType"
                del kwargs["dataType"]
            # Remove attributeType keywords; attributeType is the default and
            # the actual type of the new attribute is defined by the name of the
            # method called: add_float, add_bool, ...
            if kwargs.get("attributeType", None):
                del kwargs["attributeType"]

            kwargs[data_type] = attr_type

            return self._add_traced_attr(name, **kwargs)

        return func

    def add_enum(self, name, enum_name="", cases=None, **kwargs):
        """Create a boolean-attribute for the given attribute

        Note:
            kwargs are exactly the same as in cmds.addAttr()!

        Args:
            name (str): Name for the new attribute to be created
            enum_name (list, str): User-choices for the resulting enum-attribute
            cases (list, str): Overrides enum_name, which I find a horrific name
            kwargs (dict): User specified attributes to be set for the new attribute

        Returns:
            attr (NcNode): NcNode-instance with the node and new attribute.

        Example:
            >>> Node("pCube1").add_enum(cases=["A", "B", "C"], value=2)
        """
        if "enumName" not in kwargs.keys():
            if cases is not None:
                enum_name = cases
            if isinstance(enum_name, (list, tuple)):
                enum_name = ":".join(enum_name)

            kwargs["enumName"] = enum_name

        # Replace any user inputs for attributeType. Type is defined by method name!
        kwargs["attributeType"] = "enum"

        return self._add_traced_attr(name, **kwargs)

    def add_separator(
            self,
            name=STANDARD_SEPARATOR_NICENAME,
            enum_name=STANDARD_SEPARATOR_VALUE,
            cases=None,
            **kwargs
    ):
        """Convenience method to create a separator-attribute.

        Note:
            Default name and enum_name are defined by the globals
            STANDARD_SEPARATOR_NICENAME and STANDARD_SEPARATOR_VALUE!
            kwargs are exactly the same as in cmds.addAttr()!

        Args:
            name (str): Name for the new separator to be created.
            enum_name (list, str): User-choices for the resulting enum-attribute.
            cases (list, str): Overrides enum_name, which I find a horrific name.
            kwargs (dict): User specified attributes to be set for the new attribute.

        Returns:
            attr (NcNode): NcNode-instance with the node and new attribute.

        Example:
            >>> Node("pCube1").add_separator()
        """

        # Find the next available longName for the new separator
        node = self.node
        base_long_name = "channelBoxSeparator"
        index = 1
        unique_long_name = "{}{}".format(base_long_name, index)
        while cmds.attributeQuery(unique_long_name, node=node, exists=True):
            index += 1
            unique_long_name = "{}{}".format(base_long_name, index)

        separator_attr = self.add_enum(
            unique_long_name,
            enum_name=enum_name,
            cases=cases,
            niceName=name
        )

        return separator_attr

    def _add_traced_attr(self, attr_name, **kwargs):
        """Create a Maya-attribute on the Maya-node this NcBaseNode refers to.

        Args:
            attr_name (str): Name of new attribute.
            kwargs (dict): Any user specified flags & their values.
                           Gets combined with values in DEFAULT_ATTR_FLAGS!

        Returns:
            node (NcNode): NcNode instance with the newly created attribute.
        """
        # Replace spaces in name not to cause Maya-warnings
        attr_name = attr_name.replace(' ', '_')

        # Check whether attribute already exists. If so; return it directly!
        plug = "{}.{}".format(self.node, attr_name)
        if cmds.objExists(plug):
            LOG.warn("Attribute %s already existed!" % (str(plug)))
            return self.__getattr__(attr_name)

        # Make a copy of the default addAttr command flags
        attr_variables = lookup_table.DEFAULT_ATTR_FLAGS.copy()
        LOG.debug("Copied default attr_variables: %s" % (str(attr_variables)))

        # Add the attr variable into the dictionary
        attr_variables["longName"] = attr_name
        # Override default values with kwargs
        attr_variables.update(kwargs)
        LOG.debug("Added custom attr_variables: %s" % (str(attr_variables)))

        # Extract attributes that need to be set via setAttr-command
        set_attr_values = {
            "channelBox": attr_variables.pop("channelBox", None),
            "lock": attr_variables.pop("lock", None),
        }
        attr_value = attr_variables.pop("value", None)
        LOG.debug("Extracted set_attr-variables from attr_variables: %s" % (str(attr_variables)))
        LOG.debug("set_attr-variables: %s" % (str(set_attr_values)))

        # Add the attribute
        _traced_add_attr(self.node, **attr_variables)

        # Filter for any values that need to be set via the setAttr command. Oh Maya...
        set_attr_values = {
            key: val for (key, val) in set_attr_values.iteritems()
            if val is not None
        }
        LOG.debug("Pruned set_attr-variables: %s" % (str(set_attr_values)))

        # If there is no value to be set; set any attribute flags directly
        if attr_value is None:
            _traced_set_attr(plug, **set_attr_values)
        else:
            # If a value is given; use the set_or_connect function
            _unravel_and_set_or_connect_a_to_b(plug, attr_value, **set_attr_values)

        return NcNode(plug)

    def __setattr__(self, name, value):
        """Set or connect attribute to the given value.

        Note:
            Since setattr uses __getattr__ method it works for NcNode AND NcAttrs!

            setattr is invoked by equal-sign. Does NOT work without attribute given:
            a = Node("pCube1.ty")  # Initialize Node-object with attribute given
            a.ty = 7  # Works fine if attribute is specifically called
            a = 7  # Does NOT work! It looks like the same operation as above,
                     but here Python calls the assignment operation, NOT setattr.
                     The assignment-operation can't be overridden. Sad but true.

        Args:
            name (str): Name of the attribute to be set
            value (NcNode, NcAttrs, str, int, float, list, tuple): Connect
                attribute to this object or set attribute to this value/array

        Example:
            ::

                a = Node("pCube1") # Create new NcNode-object
                a.tx = 7  # Set pCube1.tx to the value 7
                a.t = [1, 2, 3]  # Set pCube1.tx|ty|tz to 1|2|3 respectively
                a.tx = Node("pCube2").ty  # Connect pCube2.ty to pCube1.tx
        """
        LOG.debug(
            "%s __setattr__ (%s, %s)" % (self.__class__.__name__, str(name), str(value))
        )

        _unravel_and_set_or_connect_a_to_b(self.__getattr__(name), value)

    def __setitem__(self, index, value):
        """Set or connect attribute at index to the given value.

        Note:
            Since setitem uses __getitem__ method it works for NcNode AND NcAttrs!

            This looks at the list of attributes stored in the NcAttrs of this NcNode.

        Args:
            index (int): Index of item to be set
            value (NcNode, NcAttrs, str, int, float): Set/connect item at index to this.
        """
        LOG.debug(
            "%s __setitem__ (%s, %s)" % (self.__class__.__name__, str(index), str(value))
        )

        _unravel_and_set_or_connect_a_to_b(self[index], value)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NcNode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NcNode(NcBaseNode):
    """NcNodes are linked to Maya nodes and can hold attributes in the form of an NcAttrs-instance.

    Note:
        Getting attr X from an NcNode that holds attr Y returns only attr X: NcNode.X
        In contrast: Getting attr X from an NcAttrs that holds attr Y returns: NcAttrs.Y.X
    """

    def __init__(self, node, attrs=None, auto_unravel=None, auto_consolidate=None):
        """NcNode-class constructor

        Note:
            __setattr__ is changed and the usual "self.node = node" results in a loop.
            Therefore attributes need to be set a bit awkwardly; directly via __dict__!

            NcNode uses an MObject as its reference to the Maya node it belongs to.
            If the Maya node does not exist at instantiation time this will error!

        Args:
            node (str, NcNode, NcAttrs, MObject): Represents a Maya node
            attrs (str, list, NcAttrs): Represents Maya attributes on the node
            auto_unravel (bool): Whether attributes should be automatically unravelled.
                Check set_global_auto_unravel docString for more details.
            auto_consolidate (bool): Whether attributes should be automatically consolidated.
                Check set_global_auto_consolidate docString for more details.

        Attributes:
            _node_mobj (MObject): Reference to Maya node.
            _held_attrs (NcAttrs): NcAttrs instance that defines the attributes.

        Examples:
            ::

                a = Node("pCube1")  # Node invokes NcNode instantiation!
                b = Node("pCube2.ty")
                b = Node("pCube3", ["ty", "tz", "tx"])
        """
        LOG.debug(
            "%s __init__ (%s, %s, %s, %s)" % (
                self.__class__.__name__,
                str(node),
                str(attrs),
                str(auto_unravel),
                str(auto_consolidate)
            )
        )

        # Plain values should be Value-instance!
        if isinstance(node, numbers.Real):
            LOG.error(
                "Explicit NcNode __init__ with number (%s). "
                "Use Node() instead!" % (str(node))
            )
            return None

        # Lists or tuples should be NcList!
        if isinstance(node, (list, tuple)):
            LOG.error(
                "Explicit NcNode __init__ with list or tuple (%s). "
                "Use Node() instead!" % (str(node))
            )
            return None

        super(NcNode, self).__init__()

        # Handle case where no attrs were given
        if attrs is None:
            if isinstance(node, NcBaseNode):
                attrs = node.attrs
            # Initialization with "object.attrs" string
            elif "." in node:
                node, attrs = _split_plug_into_node_and_attr(node)
            else:
                attrs = []

        # If given node is an NcNode or NcAttrs; retrieve data from it!
        if isinstance(node, NcBaseNode):
            node_mobj = node._node_mobj

            # Use settings of given node if auto_unravel or auto_consolidate aren't set
            if auto_unravel is None:
                auto_unravel = node._auto_unravel
            if auto_consolidate is None:
                auto_consolidate = node._auto_consolidate
        else:
            node_mobj = om_util.get_mobj(node)
            if node_mobj is None:
                LOG.error("%s does not exist! NcNode initialization failed." % (str(node)))

        # Using __dict__, because the setattr & getattr methods are overridden!
        self.__dict__["_node_mobj"] = node_mobj
        if isinstance(attrs, NcAttrs):
            self.__dict__["_held_attrs"] = attrs
        else:
            self.__dict__["_held_attrs"] = NcAttrs(self, attrs)

        # If auto_unravel or auto_consolidate are not set; turn them on by default!
        if auto_unravel is None:
            auto_unravel = True
        if auto_consolidate is None:
            auto_consolidate = True
        self.__dict__["_auto_unravel"] = auto_unravel
        self.__dict__["_auto_consolidate"] = auto_consolidate

    def __getattr__(self, name):
        """Get a new NcAttrs instance with the MObject this NcNode points to and
        the requested attribute.

        Note:
            There are certain keywords that will NOT return a new NcAttrs, but instead:
            * attrs: Returns currently stored NcAttrs of this NcNode instance.
            * attrs_list: Returns list of stored attributes: [attr, ...] (list of strings).
            * node: Returns name of Maya node in scene (str).
            * nodes: Returns name of Maya node in scene in a list ([str]).
            * plugs: Returns list of stored plugs: [node.attr, ...] (list of strings).

        Args:
            name (str): Name of requested attribute

        Returns:
            return_value (NcAttrs): New NcAttrs instance OR stored NcAttrs
                                    instance, if keyword "attrs" was used!

        Example:
            ::

                a = Node("pCube1") # Create new Node-object
                a.tx  # invokes __getattr__ and returns a new Node-object.
                        It's the same as typing Node("a.tx")
        """
        LOG.debug("%s __getattr__ (%s)" % (self.__class__.__name__, str(name)))

        # Take care of keyword attrs!
        if name == "attrs":
            return self.attrs

        return_value = NcAttrs(
            self,
            attrs=name,
        )

        return return_value

    def __getitem__(self, index):
        """Get stored attribute at given index.

        Note:
            This looks through the list of attributes stored in the NcAttrs of this NcNode.

        Args:
            index (int): Index of desired item

        Returns:
            return_value (NcNode): New NcNode instance, only with attr at index.
        """
        LOG.debug("%s __getitem__ (%s)" % (self.__class__.__name__, str(index)))

        return_value = NcNode(
            self._node_mobj,
            self.attrs[index],
            auto_unravel=self._auto_unravel,
            auto_consolidate=self._auto_consolidate
        )

        return return_value

    @property
    def node(self):
        """Property to allow easy access to name of Maya node this NcNode is linked to.

        Returns:
            value (str): Name of Maya node in the scene.
        """
        return om_util.get_long_name_of_mobj(self._node_mobj)

    @property
    def attrs(self):
        """Property to allow easy access to currently stored NcAttrs instance of this NcNode.

        Returns:
            _held_attrs (NcAttrs): NcAttrs instance that represents Maya attributes.
        """
        return self._held_attrs

    @property
    def attrs_list(self):
        """Property to allow easy access to list of stored attributes of this NcNode instance.

        Returns:
            _held_attrs (list): List of strings that represent Maya attributes.
        """
        return self.attrs.attrs_list


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NcAttrs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NcAttrs(NcBaseNode):
    """NcAttrs are linked to an NcNode instance. NcAttrs represent attributes on Maya nodes.

    Note:
        Getting attr X from an NcAttrs that holds attr Y returns a "concatenated" attr: NcAttrs.Y.X
        In contrast: Getting attr X from an NcNode that holds attr Y only returns: NcAttrs.X
    """

    def __init__(self, holder_node, attrs):
        """NcAttrs-class constructor

        Note:
            __setattr__ is changed and the usual "self.node = node" results in a loop.
            Therefore attributes need to be set a bit awkwardly; directly via __dict__!

            NcNode uses an MObject as its reference to the Maya node it belongs to.
            If the Maya node does not exist at instantiation time this will error!

        Args:
            holder_node (NcNode): Represents a Maya node
            attrs (str, list, NcAttrs): Represents Maya attributes on the node


        Attributes:
            _holder_node (NcNode): Reference to NcNode instance this NcAttrs belongs to.
            _held_attrs_list (list): Strings that represent attributes on a Maya node.
        """
        LOG.debug("%s __init__ (%s)" % (self.__class__.__name__, str(attrs)))

        super(NcAttrs, self).__init__()

        if not isinstance(holder_node, NcNode):
            LOG.error("holder_node must be of type NcNode! Given: %s" % (str(holder_node)))
            return None

        self.__dict__["_holder_node"] = holder_node

        if attrs is None:
            attrs = []
        elif isinstance(attrs, NcAttrs):
            attrs = attrs._held_attrs_list
        elif isinstance(attrs, basestring):
            attrs = [attrs]
        self.__dict__["_held_attrs_list"] = attrs

    @property
    def node(self):
        """Property to allow easy access to name of Maya node this NcAttrs is linked to.

        Returns:
            value (str): Name of Maya node in the scene.
        """
        return self._holder_node.node

    @property
    def attrs(self):
        """Property to allow easy access to this NcAttrs instance.

        Returns:
            self (NcAttrs): NcAttrs instance that represents Maya attributes.
        """
        return self

    @property
    def attrs_list(self):
        """Property to allow easy access to list of stored attributes of this NcAttrs instance.

        Returns:
            _held_attrs (list): List of strings that represent Maya attributes.
        """
        return self._held_attrs_list

    @property
    def _node_mobj(self):
        """Property to allow easy access to the MObject this NcAttrs instance refers to.

        Note:
            MObject is stored on the NcNode this NcAttrs instance refers to!

        Returns:
            _node_mobj (MObject): MObject instance of Maya node in the scene
        """
        return self._holder_node._node_mobj

    @property
    def _auto_unravel(self):
        """Property to allow easy access to _auto_unravel attribute of _holder_node.

        Returns:
            state (bool): Whether auto unravelling is allowed
        """
        return self._holder_node._auto_unravel

    @property
    def _auto_consolidate(self):
        """Property to allow easy access to _auto_consolidate attribute of _holder_node.

        Returns:
            state (bool): Whether auto consolidating is allowed
        """
        return self._holder_node._auto_consolidate

    def __getattr__(self, name):
        """Get a new NcAttrs instance with the requested attr concatenated onto existing attr(s).

        Note:
            There are certain keywords that will NOT return a new NcAttrs, but instead:
            * attrs: Returns currently stored NcAttrs of this NcNode instance.
            * attrs_list: Returns list of stored attributes: [attr, ...] (list of strings).
            * node: Returns name of Maya node in scene (str).
            * nodes: Returns name of Maya node in scene in a list ([str]).
            * plugs: Returns list of stored plugs: [node.attr, ...] (list of strings).

        Args:
            name (str): Name of requested attribute

        Returns:
            return_value (NcAttrs): New NcAttrs instance OR self, if keyword "attrs" was used!

        Example:
            ::

                a = Node("pCube1") # Create new NcNode-object
                a.tx.ty  # invokes __getattr__ on NcNode "a" first, which returns
                           an NcAttrs instance with node: "a" & attrs: "tx".
                           The __getattr__ described here then acts on the retrieved
                           NcAttrs instance and returns a new NcAttrs instance.
                           This time with node: "a" & attrs: "tx.ty"!
        """
        LOG.debug("%s __getattr__ (%s)" % (self.__class__.__name__, str(name)))

        # Keyword "attrs" is a special case!
        if name == "attrs":
            return self

        if len(self.attrs_list) != 1:
            LOG.error("Tried to get attr of non-singular attribute: %s" % (str(self.attrs_list)))

        return_value = NcAttrs(
            self._holder_node,
            attrs=self.attrs_list[0] + "." + name,
        )

        return return_value

    def __getitem__(self, index):
        """Get stored attribute at given index.

        Note:
            This looks through the list of stored attributes.

        Args:
            index (int): Index of desired item

        Returns:
            return_value (NcNode): New NcNode instance, solely with attribute at index.
        """
        LOG.debug("%s __getitem__ (%s)" % (self.__class__.__name__, str(index)))

        return_value = NcAttrs(
            self._holder_node,
            attrs=self.attrs_list[index],
        )

        return return_value


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NcList
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NcList(NcBaseClass):
    """NcList is a list with overloaded operators (due to inheritance from NcBaseClass).

    Note:
        NcList has the following keywords:
        * nodes: Returns all Maya nodes within the list: [node, ...] (list of strings)
    """

    def __init__(self, *args):
        """NcList-class constructor

        Args:
            args (NcNode, NcAttrs, NcValue, str, list, tuple): Any number of values
                that should be stored as an array of values
        """
        LOG.debug("%s __init__ (%s)" % (self.__class__.__name__, str(args)))
        super(NcList, self).__init__()

        # If arguments are given as a list: Unpack the items from it
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]

        # Go through given args and cast them to appropriate type (NcNode, NcValue)
        list_items = []
        for arg in args:
            converted_arg = self._convert_item_to_nc_instance(arg)
            list_items.append(converted_arg)

        self._items = list_items

    def __str__(self):
        """Readable format of NcList instance.

        Note:
            For example invoked by using print(NcList instance) in Maya

        Returns:
            string (str): String of all NcList _items.
        """
        return "{}({})".format(self.__class__.__name__, self._items)

    def __repr__(self):
        """Unambiguous format of NcList instance.

        Note:
            For example invoked by running highlighted NcList instance in Maya

        Returns:
            string (str): String of concatenated class-type, node and attrs.
        """
        return "{}({})".format(self.__class__.__name__, self._items)

    def __getitem__(self, index):
        """Get stored item at given index.

        Note:
            This looks through the _items list of this NcList instance.

        Args:
            index (int): Index of desired item

        Returns:
            return_value (NcNode, NcValue): Stored item at index.
        """
        LOG.debug("%s __getitem__ (%s)" % (self.__class__.__name__, str(index)))

        return self._items[index]

    def __setitem__(self, index, value):
        """Set or connect attribute at index to the given value.

        Note:
            This looks at the _items list of this NcList instance

        Args:
            index (int): Index of item to be set
            value (NcNode, NcAttrs, str, int, float): Set/connect item at index to this.
        """
        LOG.debug("%s __setitem__ (%s, %s)" % (self.__class__.__name__, str(index), str(value)))

        self._items[index] = value

    def __len__(self):
        """Return the length of the NcList.

        Returns:
            length (int): Number of items stored in this NcList instance.
        """
        return len(self._items)

    def __delitem__(self, index):
        """Delete the item at the given index from this NcList instance.

        Args:
            index (int): Index of the item to be deleted.
        """
        del self._items[index]

    def __iter__(self):
        """Generator to iterate over items stored in this NcList instance.

        Yields:
            Next item in stored list of items.
        """
        LOG.debug("%s __iter__ ()" % (self.__class__.__name__))

        i = 0
        while True:
            try:
                yield self._items[i]
            except IndexError:
                raise StopIteration
            i += 1

    def __reversed__(self):
        """Reverse the list of stored items on this NcList instance.

        Returns:
            Reversed list of items.
        """
        return reversed(self._items)

    def __copy__(self):
        """Behavior for copy.copy().

        Returns:
            copied_list (NcList): Shallow copy of this NcList instance.
        """
        return NcList(copy.copy(self._items))

    def __deepcopy__(self):
        """Behavior for copy.deepcopy().

        Returns:
            copied_list (NcList): Deep copy of this NcList instance.
        """
        return NcList(copy.deepcopy(self._items))

    @property
    def node(self):
        """Property to warn user about inappropriate access.

        Note:
            Only NcNode & NcAttrs allow to access their node via node-property.
            Since user might not be aware of creating NcList instance: Give a
            hint that NcList instances have a nodes-property instead.

        Returns:
            None
        """
        LOG.warn(
            "Returned None for invalid node-property request from %s instance: %s. "
            "Did you mean 'nodes'?" % (self.__class__.__name__, str(self))
        )

        return None

    @property
    def nodes(self):
        """Sparse list of all nodes within NcList instance.

        Note:
            Only names of Maya nodes are in return_list.
            Furthermore: It is a sparse list without any duplicate names.

            This can be useful for example for cmds.hide(my_collection.nodes)

        Returns:
            return_list (list): List of names of Maya nodes stored in this NcList instance.
        """
        return_list = []

        for item in self._items:
            if isinstance(item, (NcBaseNode)):
                return_list.append(item.node)

        return_list = list(set(return_list))

        return return_list

    def get(self):
        """Get current value of all items within this NcList instance.

        Note:
            NcNode & NcAttrs instances in list are queried.
            NcValues are added to return list unaltered.

        Returns:
            return_list (list): List of queried values.
                Can be list of (int, float, list), depending on "queried" attributes!
        """
        return_list = []
        for item in self._items:
            if isinstance(item, NcBaseNode):
                return_list.append(item.get())
            if isinstance(item, numbers.Real):
                return_list.append(item)

        return return_list

    def append(self, value):
        """Append value to list of items.

        Note:
            Given value will be converted automatically to appropriate
            NodeCalculator type before being appended!

        Args:
            value (NcNode, NcAttrs, str, int, float): New value to be added to list.
        """
        converted_value = self._convert_item_to_nc_instance(value)
        self._items.append(converted_value)

    def insert(self, index, value):
        """Insert value to list of items at the given index.

        Note:
            Given value will be converted automatically to appropriate
            NodeCalculator type before being inserted!

        Args:
            index (int): Index at which the value should be inserted.
            value (NcNode, NcAttrs, str, int, float): New value to be inserted into list.
        """
        converted_value = self._convert_item_to_nc_instance(value)
        self._items.insert(index, converted_value)

    def extend(self, other):
        """Extend NcList with another list.

        Args:
            other (NcList, list): List to be added to the end of this NcList instance.
        """
        if isinstance(other, NcList):
            other = other._items
        self._items.extend(other)

    @staticmethod
    def _convert_item_to_nc_instance(item):
        """Convert the given item into a NodeCalculator friendly class instance.

        Args:
            item (NcNode, NcAttrs, str, int, float): Item to be converted into
                either a NcNode or a NcValue.

        Returns:
            value (NcNode, NcValue): Given item in the appropriate format.
        """
        if isinstance(item, (NcBaseNode, nc_value.NcValue)):
            return item
        elif isinstance(item, (basestring, numbers.Real)):
            return Node(item)
        else:
            LOG.error(
                "%s is of unsupported type %s! "
                "Can't convert to NcList item!" % (str(item), type(item))
            )
            return None


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SET & CONNECT PLUGS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _unravel_and_set_or_connect_a_to_b(obj_a, obj_b, **kwargs):
    """Set obj_a to value of obj_b OR connect obj_b into obj_a.

    Note:
        Allowed assignments are:
        (1-D stands for 1-dimensional, X-D for multi-dimensional; 2-D, 3-D, ...)
        Setting 1-D attribute to a 1-D value/attr  # pCube1.tx = 7
        Setting X-D attribute to a 1-D value/attr  # pCube1.t = 7  # same as pCube1.t = [7]*3
        Setting X-D attribute to a X-D value/attr  # pCube1.t = [1, 2, 3]
        Setting 1-D attribute to a X-D value/attr  # Error: Ambiguous connection!

    Args:
        obj_a (NcNode, NcAttrs, str): Needs to be a plug. Either as a
            NodeCalculator-object or as a string ("node.attr")
        obj_b (NcNode, NcAttrs, int, float, list, tuple, string): Can be a
            numeric value, a list of values or another plug either in the form
            of a NodeCalculator-object or as a string ("node.attr")
    """
    LOG.debug("_unravel_and_set_or_connect_a_to_b (%s, %s)" % (str(obj_a), str(obj_b)))

    # If both inputs are NcBaseNode instances and either has _auto_unravel off:
    # Turn it off for both
    if isinstance(obj_a, NcBaseNode) and isinstance(obj_b, NcBaseNode):
        if not obj_a._auto_unravel:
            if obj_b._auto_unravel:
                obj_b = NcNode(
                    obj_b.node,
                    obj_b.attrs,
                    auto_unravel=False,
                    auto_consolidate=obj_b._auto_consolidate
                )

        elif not obj_b._auto_unravel:
            obj_a = NcNode(
                obj_a.node,
                obj_a.attrs,
                auto_unravel=False,
                auto_consolidate=obj_a._auto_consolidate
            )

    # Unravel the given objects into a standard list-form:
    # Strings become NcNode instances, parent attributes are split up into their
    # child attributes, etc. This ensures the following setting/connecting can
    # expect the inputs to be in a consistent form.
    obj_a_unravelled_list = _unravel_item_as_list(obj_a)
    obj_b_unravelled_list = _unravel_item_as_list(obj_b)

    # As described in the docString Note: Input dimensions are crucial.
    # If they don't match they must either be matched or an error must be thrown!
    obj_a_dim = len(obj_a_unravelled_list)
    obj_b_dim = len(obj_b_unravelled_list)

    # A multidimensional connection into a 1D attribute does not make sense!
    if obj_a_dim == 1 and obj_b_dim != 1:
        LOG.error(
            "Ambiguous connection from %sD to %sD: (%s, %s)" % (
                str(obj_b_dim),
                str(obj_a_dim),
                str(obj_b_unravelled_list),
                str(obj_a_unravelled_list)
            )
        )
        return False

    # If obj_a and obj_b are higher dimensional but not the same dimension
    # the connection can't be resolved! 2D -> 3D or 4D -> 2D is ambiguous!
    if obj_a_dim > 1 and obj_b_dim > 1 and obj_a_dim != obj_b_dim:
        LOG.error(
            "Dimension mismatch for connection that can't be resolved! "
            "From %sD to %sD: (%s, %s)" % (
                str(obj_b_dim),
                str(obj_a_dim),
                str(obj_b_unravelled_list),
                str(obj_a_unravelled_list)
            )
        )
        return False

    # Dimensionality above 3 is most likely not going to be handled reliable; warn user!
    if obj_a_dim > 3:
        LOG.warn(
            "obj_a %s is %sD; greater than 3D! Many operations only work "
            "stable up to 3D!" % (str(obj_a_unravelled_list), str(obj_a_dim))
        )
    if obj_b_dim > 3:
        LOG.warn(
            "obj_b %s is %sD; greater than 3D! Many operations only work "
            "stable up to 3D!" % (str(obj_b_unravelled_list), str(obj_b_dim))
        )

    # Match input-dimensions: Both obj_X_unravelled_list will have the same
    # length, which takes care of 1D to XD setting/connecting.
    if obj_a_dim != obj_b_dim:
        obj_b_unravelled_list = obj_b_unravelled_list * obj_a_dim
        LOG.info(
            "Matched obj_b_unravelled_list %s dimension to obj_a_dim %s!" % (
                str(obj_b_unravelled_list), str(obj_a_dim),
            )
        )

    # If plug consolidation is allowed: Try to do so.
    auto_consolidate_allowed = _is_consolidation_allowed([obj_a, obj_b])
    if GLOBAL_AUTO_CONSOLIDATE and auto_consolidate_allowed:
        consolidated_plugs = _consolidate_plugs_to_min_dimension(
            obj_a_unravelled_list,
            obj_b_unravelled_list
        )
        obj_a_unravelled_list, obj_b_unravelled_list = consolidated_plugs

    # Pass the fully processed inputs to be connected
    _set_or_connect_a_to_b(obj_a_unravelled_list, obj_b_unravelled_list, **kwargs)


def _is_consolidation_allowed(inputs):
    """Check given inputs for any NcBaseNode-instance that is not set to auto consolidate

    Args:
        inputs (NcNode, NcAttrs, str, int, float, list, tuple): Items to check
            for a turned off auto-consolidation.

    Returns:
        value (bool): True, if all given items allow for consolidation.
    """
    LOG.debug("_is_consolidation_allowed (%s)" % (str(inputs)))

    if not isinstance(inputs, (tuple, list)):
        inputs = [inputs]

    for item in inputs:
        if isinstance(item, NcBaseNode):
            if not item._auto_consolidate:
                return False

    return True


def _consolidate_plugs_to_min_dimension(*plugs):
    """Try to consolidate the given input plugs.

    Note:
        A full set of child attributes can be reduced to their parent attribute:
        ["tx", "ty", "tz"] becomes ["t"]
        A 3D to 3D connection can be 1 connection if both plugs have such a parent-attribute!
        However: A 1D attr can not connect to a 3D attr and must not be consolidated.

    Args:
        *plugs (list(NcNode, NcAttrs, str, int, float, list, tuple)): Plugs to check.

    Returns:
        parent_plugs (list): Consolidated plugs, if consolidation was successful.
            Otherwise given inputs are returned unaltered.
    """
    LOG.debug("_consolidate_plugs_to_min_dimension (%s)" % (str(plugs)))

    parent_plugs = []
    for plug in plugs:
        parent_plug = _check_for_parent_attribute(plug)

        # If any plug doesn't have a parent it's impossible to consolidate plugs!
        if parent_plug is None:
            # Return early!
            return plugs

        parent_plugs.append([parent_plug])

    # If all given plugs have a parent plug: Return them as a list of lists.
    return parent_plugs


def _check_for_parent_attribute(plug_list):
    """Check whether the given plug_list can be reduced to a single parent attribute

    Args:
        plug_list (list): List of plugs: ["node.attribute", ...]

    Returns:
        potential_parent_mplug (MPlug, None): If parent attribute was found it
            is returned as an MPlug instance, otherwise None is returned
    """
    LOG.debug("_check_for_parent_attribute (%s)" % (str(plug_list)))

    # Initialize variables for a potential parent node & attribute
    potential_parent_mplug = None
    checked_mplugs = []

    for plug in plug_list:
        # Any numeric value instantly breaks any chance for a parent_attr
        if isinstance(plug, numbers.Real):
            return None

        mplug = om_util.get_mplug_of_plug(plug)
        parent_mplug = om_util.get_parent_mplug(mplug)

        # Any non-existent or faulty parent_attr breaks chance for parent_attr
        if not parent_mplug:
            return None

        # The first parent_attr becomes the potential_parent_attr.
        if potential_parent_mplug is None:
            potential_parent_mplug = parent_mplug
        # Break if any subsequent potential_parent_attr is different to the existing
        elif potential_parent_mplug != parent_mplug:
            return None

        # If the plug passed all previous tests: Add it to the list
        checked_mplugs.append(mplug)

    # Given plug_list should not be reduced if the list of all checked attributes
    # does not match the full list of available children attributes exactly!
    # Example A: [outputX] should not be reduced to [output], since Y & Z are missing!
    # Example B: [outputX, outputX, outputZ] has duplicates and should not be reduced!
    # Example C: [outputX, outputZ, outputY] isn't in the right order and should not be reduced!
    all_child_mplugs = om_util.get_child_mplugs(potential_parent_mplug)
    for checked_mplug, child_mplug in itertools.izip_longest(checked_mplugs, all_child_mplugs):
        empty_plug_detected = checked_mplug is None or child_mplug is None
        if empty_plug_detected or checked_mplug != child_mplug:
            return None

    # If it got to this point: It must be a valid parent_attr
    return potential_parent_mplug


def _set_or_connect_a_to_b(obj_a_list, obj_b_list, **kwargs):
    """Set or connect the first list of inputs to the second list of inputs.

    Args:
        obj_a_list (list): List of MPlugs to be set or connected into.
        obj_b_list (list): List of MPlugs, int, float, etc. which obj_a_list
            items will be set or connected to.
        kwargs (dict): Arguments used in _traced_set_attr (~ cmds.setAttr)

    Returns:
        status (bool): Returns False, if setting/connecting was not possible.
    """
    LOG.debug(
        "_set_or_connect_a_to_b (%s, %s, %s)" % (str(obj_a_list), str(obj_b_list), str(kwargs))
    )

    for obj_a_item, obj_b_item in zip(obj_a_list, obj_b_list):
        # Make sure obj_a_item exists in the Maya scene and get its dimensionality
        if not cmds.objExists(obj_a_item):
            LOG.error("obj_a_item seems not to be a Maya attr: %s!" % (str(obj_a_item)))

        # If obj_b_item is a simple number...
        if isinstance(obj_b_item, numbers.Real):
            # ...set 1-D obj_a_item to 1-D obj_b_item-value.
            _traced_set_attr(obj_a_item, obj_b_item, **kwargs)

        # If obj_b_item is a valid attribute in the Maya scene...
        elif isinstance(obj_b_item, OpenMaya.MPlug) or _is_valid_maya_attr(obj_b_item):
            #  ...connect it.
            _traced_connect_attr(obj_b_item, obj_a_item)

        # If obj_b_item didn't match anything; obj_b_item-type is not supported.
        else:
            LOG.error(
                "Cannot set obj_b_item: %s because of unknown type: %s" % (
                    str(obj_b_item), type(obj_b_item)
                )
            )
            return False


def _is_valid_maya_attr(plug):
    """Check if given plug is of an existing Maya attribute.

    Args:
        plug (str): String of a Maya plug in the scene (node.attr).

    Returns:
        status (bool): Whether the given plug is an existing plug in the scene.
    """
    LOG.debug("_is_valid_maya_attr (%s)" % (str(plug)))

    split_plug = _split_plug_into_node_and_attr(plug)
    if split_plug:
        return cmds.attributeQuery(split_plug[1], node=split_plug[0], exists=True)

    LOG.error("Given string '%s' does not seem to be a Maya attribute!" % (str(plug)))
    return False


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CREATE, CONNECT AND SETUP NODE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _create_and_connect_node(operation, *args):
    """Generic function to create & connect adequately named Maya nodes.

    Args:
        operation (str): Operation the new node has to perform
        *args (NcNode, NcAttrs, string): Attributes connecting into the newly created node

    Returns:
        new_node (NcNode): New NcNode instance with the newly created Maya-node
            of type OPERATOR_LOOKUP_TABLE[operation]["node"] and with attributes
            stored in OPERATOR_LOOKUP_TABLE[operation]["output"].
    """
    LOG.debug("Creating a new %s-operationNode with args: %s" % (str(operation), str(args)))

    # If a multi_index-attribute is given; create list with it of same length than args
    new_node_inputs = lookup_table.OPERATOR_LOOKUP_TABLE[operation]["inputs"]
    if lookup_table.OPERATOR_LOOKUP_TABLE[operation].get("is_multi_index", False):
        new_node_inputs = len(args) * lookup_table.OPERATOR_LOOKUP_TABLE[operation]["inputs"][:]

    # Check that dimensions match: args must be of same length as node-inputs:
    if len(args) != len(new_node_inputs):
        LOG.error(
            "Dimensions to create node don't match! Given args: %s "
            "Required node-inputs: %s" % (str(args), str(new_node_inputs))
        )

    # Unravel all given arguments and create a new node according to given operation
    unravelled_args_list = [_unravel_item_as_list(x) for x in args]
    new_node = _create_traced_operation_node(operation, unravelled_args_list)

    # If the given node-type has an operation attr; set it according to OPERATOR_LOOKUP_TABLE
    node_operation = lookup_table.OPERATOR_LOOKUP_TABLE[operation].get("operation", None)
    if node_operation:
        _unravel_and_set_or_connect_a_to_b(new_node + ".operation", node_operation)

    # Find the maximum dimension involved to know what to connect. For example:
    # 3D to 3D requires 3D-input, 1D to 2D needs 2D-input, 1D to 1D only needs 1D-input
    max_dim = max([len(x) for x in unravelled_args_list])

    # Connect all given args to the inputs of the newly created Maya node.
    for i, (plug_to_connect, new_node_input) in enumerate(zip(args, new_node_inputs)):
        new_node_input_list = [(new_node + "." + _input) for _input in new_node_input][:max_dim]
        # multi_index inputs must always be caught and filled!
        if lookup_table.OPERATOR_LOOKUP_TABLE[operation].get("is_multi_index", False):
            new_node_input_list = [x.format(multi_index=i) for x in new_node_input_list]

        # Support for single-dimension-inputs in the OPERATOR_LOOKUP_TABLE. For example:
        # The blend-attr of a blendColors-node is always 1D,
        # so only a 1D plug_to_connect must be given!
        elif len(new_node_input) == 1:
            if len(_unravel_item_as_list(plug_to_connect)) > 1:
                LOG.error(
                    "Unable to connect multi-dimensional plug %s to 1D "
                    "input %s.%s!" % (
                        str(plug_to_connect),
                        str(new_node),
                        str(new_node_input)
                    )
                )
                return False
            else:
                LOG.debug(
                    "Directly connecting 1D plug %s to 1D "
                    "input %s.%s" % (
                        str(plug_to_connect),
                        str(new_node),
                        str(new_node_input)
                    )
                )
                _unravel_and_set_or_connect_a_to_b(new_node + "." + new_node_input[0], plug_to_connect)
                continue

        _unravel_and_set_or_connect_a_to_b(new_node_input_list, plug_to_connect)

    # Support for single-dimension-outputs in the OPERATOR_LOOKUP_TABLE. For example:
    # distanceBetween returns 1D attr, no matter what dimension the inputs were
    output_is_predetermined = lookup_table.OPERATOR_LOOKUP_TABLE[operation].get(
        "output_is_predetermined", False
    )

    # Return new NcNode instance with the appropriate output-attributes.
    outputs = lookup_table.OPERATOR_LOOKUP_TABLE[operation]["output"]
    if len(outputs) == 1 or output_is_predetermined:
        # If the outputs are of length 1 or should not be altered: Return directly
        return NcNode(new_node, outputs)

    else:
        # Truncate the number of outputs according to how many attributes were processed
        return NcNode(new_node, outputs[:max_dim])


def _create_node_name(operation, *args):
    """Create a procedural Maya node name that is as descriptive as possible.

    Args:
        operation (str): Operation the new node has to perform
        *args (MPlug, NcNode, NcAttrs, list, numbers, str): Attributes
            connecting into the newly created node.

    Returns:
        name (str): Generated name for the given node operation and args.
    """
    if isinstance(args, tuple) and len(args) == 1:
        args = args[0]

    involved_args = []
    for arg in args:
        # Unwrap list of lists, if it's only one element
        if isinstance(arg, (list, tuple)) and len(arg) == 1:
            arg = arg[0]

        if isinstance(arg, OpenMaya.MPlug):
            # Get the name of MPlugs, use last attribute of plug
            plug_name = str(arg).split(".")[-1]
            involved_args.append(plug_name)

        elif isinstance(arg, NcBaseNode):
            # Use the involved attrs, if there are none; use the node name
            if arg.attrs:
                involved_args.extend(arg.as_list)
            else:
                involved_args.append(arg.node)

        elif isinstance(arg, (tuple, list)):
            # If it's a list of 1 element; use that element, otherwise use "list"
            if len(arg) == 1:
                involved_args.append(str(arg[0]))
            else:
                involved_args.append("list")

        elif isinstance(arg, numbers.Real):
            # Round floats, otherwise use number directly
            if isinstance(arg, float):
                involved_args.append(str(int(arg)) + "f")
            else:
                involved_args.append(str(arg))

        elif isinstance(arg, basestring):
            # Strings can be added directly to the list.
            involved_args.append(arg)

        else:
            # Unknown arg-type
            involved_args.append("UNK" + str(arg))

    # Combine all name-elements
    name_elements = [
        NODE_NAME_PREFIX,  # Common NodeCalculator-prefix
        operation.upper(),  # Operation type
        "_".join(involved_args),  # Involved args
        lookup_table.OPERATOR_LOOKUP_TABLE[operation]["node"]  # Node type as suffix
    ]
    name = "_".join(name_elements)

    return name


def _create_traced_operation_node(operation, attrs):
    """Create an adequately named Maya node for the given operation and
    add it to the command_stack if Tracer is active.

    Args:
        operation (str): Operation the new node has to perform
        attrs (MPlug, NcNode, NcAttrs, list, numbers, str): Attributes that
            will be connecting into the newly created node

    Returns:
        new_node (str): Name of newly created Maya node.
    """
    node_type = lookup_table.OPERATOR_LOOKUP_TABLE[operation]["node"]
    node_name = _create_node_name(operation, attrs)
    new_node = _traced_create_node(node_type, name=node_name)

    return new_node


def _traced_create_node(node_type, **kwargs):
    """Create a Maya node and add it to the _traced_nodes if Tracer is active

    Note:
        This is simply an overloaded cmds.createNode(node_type, **kwargs). It
        includes the cmds.parent-command if parenting flags are given.

        If Tracer is active: Created nodes are associated with a variable.
        If they are referred to later on in the NodeCalculator statement, the
        variable name will be used instead of their node-name.

    Args:
        node_type (str): Type of the Maya node that should be created.
        **kwargs: cmds.createNode & cmds.parent flags

    Returns:
        new_node (str): Name of newly created Maya node.
    """

    # Make sure a sensible name is in the kwargs
    name = kwargs.pop("name", node_type)

    # Separate the parent command flags from the createNode/spaceLocator kwargs.
    parent = kwargs.pop("parent", None) or kwargs.pop("p", None)
    parent_kwargs = {}
    if parent:
        if isinstance(parent, NcBaseNode):
            parent = parent.node
        for parent_flag in lookup_table.PARENT_FLAGS:
            if parent_flag in kwargs:
                parent_kwargs[parent_flag] = kwargs.pop(parent_flag)
    if "s" in parent_kwargs:
        LOG.warn(
            "The 's'-flag was used for creation of %s. Please use 'shared' or "
            "'shape' flag to avoid ambiguity! Used 's' for 'shape' "
            "in cmds.parent command!" % (str(node_type))
        )

    # Create new node
    new_node = cmds.createNode(node_type, **kwargs)

    # If the newly created node is a shape: Get its transform for consistency.
    # The NodeCalculator gives easy access to shapes via get_shapes()
    new_node_is_shape = cmds.objectType(new_node, isAType="shape")
    if new_node_is_shape:
        new_node = cmds.listRelatives(new_node, parent=True)[0]
    new_node = cmds.rename(new_node, name)

    # Parent after node creation
    if parent:
        new_node = cmds.parent(new_node, parent, **parent_kwargs)[0]

    # Add creation command and new node to traced nodes, if Tracer is active
    if NcBaseClass._is_tracing:
        # Add the newly created node to the tracer. Use the mobj for non-ambiguity
        node_variable = NcBaseClass._get_next_variable_name()
        tracer_mobj = TracerMObject(new_node, node_variable)
        NcBaseClass._add_to_traced_nodes(tracer_mobj)

        # Add the node createNode command to the command stack
        if not new_node_is_shape:
            # Add the name-kwarg back in, if the new node isn't a shape
            kwargs["name"] = name

        joined_kwargs = ", {}".format(_join_cmds_kwargs(**kwargs)) if kwargs else ""
        command = [
            "{var} = cmds.createNode('{op}'{kwargs})".format(
                var=node_variable,
                op=node_type,
                kwargs=joined_kwargs
            )
        ]

        # If shape was created: Add getting its parent and renaming it to command stack
        if new_node_is_shape:
            command.append(
                "{var} = cmds.listRelatives({var}, parent=True)[0]".format(
                    var=node_variable,
                )
            )
            command.append(
                "{var} = cmds.rename({var}, '{name}')".format(
                    var=node_variable,
                    name=name
                )
            )

        # Add the parent command to the command stack
        if parent:
            joined_parent_kwargs = _join_cmds_kwargs(**parent_kwargs)
            if joined_parent_kwargs:
                joined_parent_kwargs = ", {}".format(joined_parent_kwargs)
            command.append(
                "cmds.parent({var}, '{parent}'{kwargs})".format(
                    var=node_variable,
                    parent=parent,
                    kwargs=joined_parent_kwargs,
                )
            )

        NcBaseClass._add_to_command_stack(command)

    return new_node


def _traced_add_attr(node, **kwargs):
    """Add an attr on a Maya node & add command to _command_stack if Tracer is active

    Note:
        This is simply an overloaded cmds.addAttr(node, **kwargs).

    Args:
        node (str): Maya node the attribute should be added to.
        **kwargs: cmds.addAttr-flags
    """
    cmds.addAttr(node, **kwargs)

    # If commands are traced...
    if NcBaseClass._is_tracing:

        # If node is already part of the traced nodes: Use its variable instead
        node_variable = NcBaseClass._get_tracer_variable_for_node(node)
        node = node_variable if node_variable else "'{}'".format(node)

        # Join any given kwargs so they can be passed on to the addAttr-command
        joined_kwargs = _join_cmds_kwargs(**kwargs)

        # Add the addAttr-command to the command stack
        NcBaseClass._add_to_command_stack("cmds.addAttr({}, {})".format(node, joined_kwargs))


def _traced_set_attr(plug, value=None, **kwargs):
    """Set an attr on a Maya node & add command to _command_stack if Tracer is active

    Note:
        This is simply an overloaded cmds.setAttr(plug, value, **kwargs).

    Args:
        plug (MPlug, str): Plug of a Maya node that should be set.
        value (list, numbers, bool): Value the given plug should be set to.
        **kwargs: cmds.setAttr-flags
    """

    # Set plug to value
    if value is None:
        cmds.setAttr(plug, edit=True, **kwargs)
    elif isinstance(value, (list, tuple)):
        cmds.setAttr(plug, *value, edit=True, **kwargs)
    else:
        cmds.setAttr(plug, value, edit=True, **kwargs)

    # If commands are traced...
    if NcBaseClass._is_tracing:

        # ...look for the node of the given attribute...
        node, attr = _split_plug_into_node_and_attr(plug)
        node_variable = NcBaseClass._get_tracer_variable_for_node(node)
        if node_variable:
            # ...if it is already part of the traced nodes: Use its variable instead
            plug = "{} + '.{}'".format(node_variable, attr)
        else:
            # ...otherwise add quotes around original attr
            plug = "'{}'".format(plug)

        # Join any given kwargs so they can be passed on to the setAttr-command
        joined_kwargs = _join_cmds_kwargs(**kwargs)

        # Add the setAttr-command to the command stack
        if value is not None:
            if isinstance(value, nc_value.NcValue):
                value = value.metadata

            unpack_operator = "*" if isinstance(value, (list, tuple)) else ""
            if joined_kwargs:
                # If both value and kwargs were given
                NcBaseClass._add_to_command_stack(
                    "cmds.setAttr({}, {}{}, edit=True, {})".format(
                        plug,
                        unpack_operator,
                        value,
                        joined_kwargs,
                    )
                )
            else:
                # If only a value was given
                NcBaseClass._add_to_command_stack(
                    "cmds.setAttr({}, {}{})".format(plug, unpack_operator, value)
                )
        else:
            if joined_kwargs:
                # If only kwargs were given
                NcBaseClass._add_to_command_stack(
                    "cmds.setAttr({}, edit=True, {})".format(plug, joined_kwargs)
                )
            else:
                # If neither value or kwargs were given it was a redundant setAttr. Don't store!
                pass


def _traced_get_attr(plug):
    """Get value of an attr on a Maya node & add command to _command_stack if Tracer is active

    Note:
        This is a tweaked & overloaded cmds.getAttr(plug): Awkward return values
        of 3D-attributes are converted of tuple(list()) to a simple list().

    Args:
        plug (MPlug, str): Plug of a Maya node, whose value should be queried.

    Returns:
        return_value (list, numbers, bool, str): Queried value of Maya node plug.
    """

    # Variable to keep track of whether return value had to be unpacked or not
    list_of_tuples_returned = False

    if _is_valid_maya_attr(plug):
        return_value = cmds.getAttr(plug)
        # getAttr of 3D-plug returns list of a tuple. This unravels that abomination
        if isinstance(return_value, list):
            if len(return_value) == 1 and isinstance(return_value[0], tuple):
                list_of_tuples_returned = True
                return_value = list(return_value[0])
    else:
        return_value = plug

    if NcBaseClass._is_tracing:
        value_name = NcBaseClass._get_next_value_name()

        return_value = nc_value.value(return_value, metadata=value_name, created_by_user=False)

        NcBaseClass._add_to_traced_values(return_value)

        # ...look for the node of the given attribute...
        node, attr = _split_plug_into_node_and_attr(plug)
        node_variable = NcBaseClass._get_tracer_variable_for_node(node)
        if node_variable:
            # ...if it is already part of the traced nodes: Use its variable instead
            plug = "{} + '.{}'".format(node_variable, attr)
        else:
            # ...otherwise add quotes around original plug
            plug = "'{}'".format(plug)

        # Add the getAttr-command to the command stack
        if list_of_tuples_returned:
            NcBaseClass._add_to_command_stack("{} = list(cmds.getAttr({})[0])".format(value_name, plug))
        else:
            NcBaseClass._add_to_command_stack("{} = cmds.getAttr({})".format(value_name, plug))

    return return_value


def _join_cmds_kwargs(**kwargs):
    """Concatenates Maya command kwargs for Tracer.

    Args:
        kwargs (dict): Key/value-pairs that should be converted to a string.

    Returns:
        joined_kwargs (str): String of kwargs&values for the command in the Tracer-stack.
    """
    prepared_kwargs = []

    for key, val in kwargs.iteritems():
        # Add quotes around values that are strings
        if isinstance(val, basestring):
            prepared_kwargs.append("{}='{}'".format(key, val))
        else:
            prepared_kwargs.append("{}={}".format(key, val))

    joined_kwargs = ", ".join(prepared_kwargs)

    return joined_kwargs


def _traced_connect_attr(plug_a, plug_b):
    """Connect 2 plugs & add executed command to the command_stack if Tracer is active.

    Note:
        This is simply an overloaded cmds.connectAttr(plug_a, plug_b, force=True).

    Args:
        plug_a (MPlug, str): Source plug
        plug_b (MPlug, str): Destination plug
    """
    # Connect plug_a to plug_b
    cmds.connectAttr(plug_a, plug_b, force=True)

    # If commands are traced...
    if NcBaseClass._is_tracing:

        # Format both command arguments correctly & replace nodes with
        # variables, if they are part of the traced nodes!
        formatted_args = []
        for plug in [plug_a, plug_b]:

            # Look for the node of the current attribute...
            node, attr = _split_plug_into_node_and_attr(plug)
            node_variable = NcBaseClass._get_tracer_variable_for_node(node)
            if node_variable:
                # ...if it is already part of the traced nodes: Use its variable instead...
                formatted_attr = "{} + '.{}'".format(node_variable, attr)
            # ...otherwise make sure it's stored as a string
            else:
                formatted_attr = "'{}'".format(plug)
            formatted_args.append(formatted_attr)

        # Add the connectAttr-command to the command stack
        NcBaseClass._add_to_command_stack(
            "cmds.connectAttr({0}, {1}, force=True)".format(*formatted_args)
        )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UNRAVELLING INPUTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _unravel_item_as_list(item):
    """Convert input into clean list of values or MPlugs.

    Args:
        item (NcNode, NcAttrs, NcList, int, float, list, str): input to be
            unravelled and returned as list.

    Returns:
        unravelled_item (list): List consistent of values or MPlugs
    """
    LOG.debug("_unravel_item_as_list (%s)" % (str(item)))

    unravelled_item = _unravel_item(item)

    # The returned value MUST be a list!
    if not isinstance(unravelled_item, list):
        unravelled_item = [unravelled_item]

    return unravelled_item


def _unravel_item(item):
    """Turn input into MPlugs or values that can be set/connected by Maya.

    Note:
        The items of a list are all unravelled as well!
        Parent plug becomes list of child plugs: "t" -> ["tx", "ty", "tz"]

    Args:
        item (NcList, NcNode, NcAttrs, NcValue, list, tuple, str, numbers):
            input to be unravelled/cleaned.

    Returns:
        value (MPlug, NcValue, int, float, list): MPlug or value
    """
    LOG.debug("_unravel_item (%s)" % (str(item)))

    if isinstance(item, NcList):
        return _unravel_nc_list(item)

    elif isinstance(item, NcBaseNode):
        return _unravel_base_node_instance(item)

    elif isinstance(item, (list, tuple)):
        return _unravel_list(item)

    elif isinstance(item, basestring):
        return _unravel_str(item)

    elif isinstance(item, numbers.Real):
        return item

    else:
        LOG.error(
            "_unravel_item can't unravel %s of type %s" % (str(item), type(item))
        )


def _unravel_nc_list(nc_list):
    """Unravel NcList instance; get value or MPlug of its NcList-items.

    Args:
        nc_list (NcList): NcList to be unravelled.

    Returns:
        value (list): List of unravelled NcList-items.
    """
    LOG.debug("_unravel_nc_list (%s)" % (str(nc_list)))

    # An NcList is basically just a list; redirect to _unravel_list
    return _unravel_list(nc_list._items)


def _unravel_list(list_instance):
    """Unravel list instance; get value or MPlug of its items.

    Args:
        list_instance (list, tuple): list to be unravelled.

    Returns:
        unravelled_list (list): List of unravelled items.
    """
    LOG.debug("_unravel_list (%s)" % (str(list_instance)))

    unravelled_list = []

    for item in list_instance:
        unravelled_item = _unravel_item(item)
        unravelled_list.append(unravelled_item)

    return unravelled_list


def _unravel_base_node_instance(base_node_instance):
    """Unravel NcBaseNode instance; get name of node or MPlug of Maya attribute
    it refers to.

    Args:
        base_node_instance (NcNode, NcAttrs): Instance to find Mplug for.

    Returns:
        return_value (MPlug, str): MPlug of the Maya attribute the given
            NcNode/NcAttrs refers to or name of node, if no attrs are defined.
    """
    LOG.debug("_unravel_base_node_instance (%s)" % (str(base_node_instance)))

    # If there are no attributes specified on the given NcNode/NcAttrs: return node name
    if len(base_node_instance.attrs_list) == 0:
        return_value = base_node_instance.node
    # If a single attribute is defined; try to unravel it into child attributes (if they exist)
    elif len(base_node_instance.attrs_list) == 1:
        # If unravelling is allowed: Try to unravel plug...
        if GLOBAL_AUTO_UNRAVEL and base_node_instance._auto_unravel:
            return_value = _unravel_plug(base_node_instance.node, base_node_instance.attrs_list[0])
        # ...otherwise get MPlug of given attribute directly.
        else:
            return_value = om_util.get_mplug_of_node_and_attr(
                base_node_instance.node,
                base_node_instance.attrs_list[0]
            )
    # If multiple attributes are defined; Return list of unravelled plugs
    else:
        return_value = [
            _unravel_plug(base_node_instance.node, attr) for attr in base_node_instance.attrs_list
        ]

    return return_value


def _unravel_str(str_instance):
    """Convert name of a Maya plug into an MPlug.

    Args:
        str_instance (str): Name of the plug; "node.attr"

    Returns:
        return_value (MPlug, None): MPlug of the Maya attribute, None if given
            string doesn't refer to a valid Maya plug in the scene.
    """
    LOG.debug("_unravel_str (%s)" % (str(str_instance)))

    node, attr = _split_plug_into_node_and_attr(str_instance)
    return _unravel_plug(node, attr)


def _unravel_plug(node, attr):
    """Convert Maya node/attribute combination into an MPlug.

    Note:
        Tries to break up a parent attribute into its child attributes:
        .t -> [tx, ty, tz]

    Args:
        node (str): Name of the Maya node
        attr (str): Name of the attribute on the Maya node

    Returns:
        return_value (MPlug, list): MPlug of the Maya attribute, list of MPlugs
            if a parent attribute was unravelled to its child attributes.
    """
    LOG.debug("_unravel_plug (%s, %s)" % (str(node), str(attr)))

    return_value = om_util.get_mplug_of_node_and_attr(node, attr)

    # Try to unravel the found MPlug into child attributes
    child_plugs = om_util.get_child_mplugs(return_value)
    if child_plugs:
        return_value = [child_plug for child_plug in child_plugs]

    return return_value


def _split_plug_into_node_and_attr(plug):
    """Split given plug into its node and attribute part.

    Args:
        plug (MPlug, str): Plug of a Maya node/attribute combination.

    Returns:
        node, attr (tuple of strings, None): Separated node and attribute part
            or None if separation was not possible.
    """

    if isinstance(plug, OpenMaya.MPlug):
        plug = str(plug)

    if isinstance(plug, basestring) and "." in plug:
        node, attr = plug.split(".", 1)
        return (node, attr)

    LOG.error("Given plug %s could not be split into node and attr parts!" % (str(plug)))
    return None


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Tracer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Tracer(object):
    """Class that returns all Maya commands executed by NodeCalculator formula.

    Note:
        Any NodeCalculator formula enclosed in a with-statement will be logged.

    Example:
        ::

            with Tracer(pprint_trace=True) as s:
                a.tx = b.ty - 2 * c.tz
            print(s)
    """

    def __init__(self, trace=True, print_trace=False, pprint_trace=False, cheers_love=False):
        """Tracer-class constructor.

        Args:
            trace (bool): Enables/disables tracing.
            print_trace (bool): Enable printing command stack as a list.
            pprint_trace (bool): Enable printing command stack as a multi-line string.
        """
        self.trace = trace
        self.print_trace = print_trace
        self.pprint_trace = pprint_trace
        self.cheers_love = cheers_love

    def __enter__(self):
        """with-statement "start method". Sets up NcBaseClass class variables for tracing.

        Note:
            The returned variable is what X in "with noca.Tracer() as X" will be.

        Returns:
            NcBaseClass._executed_commands_stack (list): List of all executed commands.
        """
        NcBaseClass._is_tracing = bool(self.trace)

        NcBaseClass._initialize_trace_variables()

        return NcBaseClass._executed_commands_stack

    def __exit__(self, exc_type, value, traceback):
        """with-statement "end method". Print executed commands during tracing, if desired."""

        # Tell the user if he/she wants to print results but they were not traced!
        if not self.trace and (self.print_trace or self.pprint_trace or self.cheers_love):
            LOG.warn("NodeCalculator commands were not traced!")
            return False

        # Print executed commands as list
        if self.print_trace:
            print("NodeCalculator command-stack:", NcBaseClass._executed_commands_stack)

        # Print executed commands on separate lines
        if self.cheers_love:
            # A bit of nerd-fun...
            print("~~~~~~~~~~~~~~~~~~ The cavalry's here: ~~~~~~~~~~~~~~~~~~")
            for item in NcBaseClass._executed_commands_stack:
                print(item)
            print("~~ You know... The world could always use more heroes! ~~")

        elif self.pprint_trace:
            print("~~~~~~~~~~~~~ NodeCalculator command-stack: ~~~~~~~~~~~~~")
            for item in NcBaseClass._executed_commands_stack:
                print(item)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        NcBaseClass._is_tracing = False


class TracerMObject(object):
    """Class that allows to store metadata with MObjects, used for the Tracer.

    Note:
        The Tracer uses variable names for created nodes. This class is an easy
        and convenient way to store these variable names with the MObject itself.
    """

    def __init__(self, node, tracer_variable):
        """TracerMObject-class constructor.

        Args:
            node (MObject): Maya MObject
            tracer_variable (str): Variable name for this MObject.
        """
        super(TracerMObject, self).__init__()
        self.mobj = om_util.get_mobj(node)
        self._tracer_variable = tracer_variable

    @property
    def node(self):
        """Property to allow easy access to name of Maya node this TracerMObject stores.

        Returns:
            value (str): Name of Maya node in the scene.
        """
        return om_util.get_name_of_mobj(self.mobj)

    @property
    def tracer_variable(self):
        """Property to allow easy access to variable name of this TracerMObject.

        Returns:
            value (str): Variable name the NodeCalculator associated with this MObject.
        """
        return self._tracer_variable
