"""Create a node-network by entering a math-formula.

:author: Mischa Kolbe <mischakolbe@gmail.com>
:credits: Mischa Kolbe, Steven Bills, Marco D'Ambros, Benoit Gielly,
          Adam Vanner, Niels Kleinheinz
:version: 2.0.0


Note:
    In any comment/docString of the NodeCalculator I use this convention:

    * node: Name of a Maya node in the scene (dagPath if name isn't unique)
    * attr/attribute: Attribute on a Maya node in the scene
    * plug: Combination of node and attribute; node.attr

    NcNode and NcAttrs instances provide these keywords:

    * attrs: Returns currently stored NcAttrs of this NcNode instance.
    * attrs_list: Returns list of stored attrs: [attr, ...] (list of strings).
    * node: Returns name of Maya node in scene (str).
    * plugs: Returns list of stored plugs: [node.attr, ...] (list of strings).

    NcList instances provide these keywords:

    * nodes: Returns Maya nodes inside NcList: [node, ...] (list of strings)


Supported operations:
    ::

        # Basic math
        +, -, *, /, **

        # To see the available Operators, use:
        Op.available()
        # Or to see all Operators and their full docString:
        Op.available(full=True)


Example:
    ::

        import node_calculator.core as noca

        a = noca.Node("pCube1")
        b = noca.Node("pCube2")
        c = noca.Node("pCube3")

        with noca.Tracer(pprint_trace=True):
            e = b.add_float("someAttr", value=c.tx)
            a.s = noca.Op.condition(b.ty - 2 > c.tz, e, [1, 2, 3])
"""


# IMPORTS ---
# Python imports
import copy
import itertools
import math
import numbers
import os
import re
import sys

# Third party imports
from maya import cmds
from maya.api import OpenMaya
import pymel.core as pm

# Local imports
from node_calculator import config
from node_calculator import logger
from node_calculator import lookup_table
from node_calculator import nc_value
from node_calculator import om_util
from node_calculator import tracer


# PYTHON 2.7 & 3 COMPATIBILITY ---
try:
    basestring
except NameError:
    basestring = str
try:
    reload
except NameError:
    # Python 3
    from imp import reload


# Reload modules when in DEV mode
if os.environ.get("MAYA_DEV", False):
    reload(config)
    reload(logger)
    reload(lookup_table)
    reload(nc_value)
    reload(om_util)
    reload(tracer)


# CONSTANTS ---
NODE_PREFIX = config.NODE_PREFIX
DEFAULT_SEPARATOR_NAME = config.DEFAULT_SEPARATOR_NAME
DEFAULT_SEPARATOR_VALUE = config.DEFAULT_SEPARATOR_VALUE
VARIABLE_PREFIX = config.VARIABLE_PREFIX
VALUE_PREFIX = config.VALUE_PREFIX
GLOBAL_AUTO_CONSOLIDATE = config.GLOBAL_AUTO_CONSOLIDATE
GLOBAL_AUTO_UNRAVEL = config.GLOBAL_AUTO_UNRAVEL
OPERATORS = lookup_table.BASIC_OPERATORS


# SETUP LOGGER ---
logger.clear_handlers()
logger.setup_stream_handler(level=logger.logging.WARN)
LOG = logger.log


# BASIC FUNCTIONALITY ---
class Node(object):
    """Return instance of appropriate type, based on given args

    Note:
        Node is an abstract class that returns components of appropriate type
        that can then be involved in a NodeCalculator calculation.

    Args:
        item (bool or int or float or str or list or tuple): Maya node, value,
            list of nodes, etc.
        attrs (str or list or tuple): String or list of strings that are an
            attribute on this node. Defaults to None.
        auto_unravel (bool): Should attrs automatically be unravelled into
            child attrs when operations are performed on this Node?
            Defaults to None, which means GLOBAL_AUTO_UNRAVEL is used.
            NodeCalculator works best if this is left unchanged!
        auto_consolidate (bool): Should attrs automatically be consolidated
            into parent attrs when operations are performed on this Node, to
            reduce the amount of connections?
            Defaults to None, which means GLOBAL_AUTO_UNRAVEL is used.
            Sometimes parent plugs don't update/evaluate reliably. If that's
            the case; use this flag or noca.set_global_auto_consolidate(False).

    Returns:
        NcNode or NcList or NcValue: Instance with given args.

    Example:
        ::

            # NcNode instance with pCube1 as node and tx as attr
            Node("pCube.tx")
            # NcNode instance with pCube1 as node and tx as attr
            Node("pCube", "tx")
            # NcNode instance with pCube1 as node and tx as attr
            Node("pCube", ["tx"])

            # NcList instance with value 1 and NcNode with pCube1
            Node([1, "pCube"])

            # NcIntValue instance with value 1
            Node(1)
    """

    def __new__(
            cls,
            item,
            attrs=None,
            auto_unravel=None,
            auto_consolidate=None):
        # Redirect plain values to a nc_value
        if isinstance(item, numbers.Real):
            LOG.debug("Node: Redirecting to NcValue(%s)", item)
            return nc_value.value(item)

        # Redirect lists or tuples to a NcList
        if isinstance(item, (list, tuple)):
            LOG.debug("Node: Redirecting to NcList(%s)", item)
            return NcList(item)

        # Redirect NcAttrs to a new NcNode
        if isinstance(item, NcAttrs):
            LOG.debug("Node: Redirecting to NcNode(%s)", item)
            # If auto_unravel flag wasn't specified: Use item settings!
            if auto_unravel is None:
                auto_unravel = item._auto_unravel
            # If auto_consolidate flag wasn't specified: Use item settings!
            if auto_consolidate is None:
                auto_consolidate = item._auto_consolidate
            return NcNode(item._node_mobj, item, auto_unravel, auto_consolidate)

        # Redirect anything else to a new NcNode
        LOG.debug("Node: Redirecting to NcNode(%s)", item)
        # If auto_unravel/auto_consolidate flags weren't specified: Use globals
        if auto_unravel is None:
            auto_unravel = GLOBAL_AUTO_UNRAVEL
        if auto_consolidate is None:
            auto_consolidate = GLOBAL_AUTO_CONSOLIDATE

        return NcNode(item, attrs, auto_unravel, auto_consolidate)

    def __init__(self, *args, **kwargs):
        """Pass this init.

        The Node-class only serves to redirect to the appropriate type
        based on the given args! Therefore the init must not do anything.

        Args:
            args (list): This dummy-init accepts any arguments.
            kwargs (dict): This dummy-init accepts any keyword arguments.
        """
        pass


def transform(name=None, **kwargs):
    """Create a Maya transform node as an NcNode.

    Args:
        name (str): Name of transform instance that will be created
        kwargs (dict): keyword arguments given to create_node function

    Returns:
        NcNode: Instance that is linked to the newly created transform

    Example:
        ::

            a = noca.transform("myTransform")
            a.t = [1, 2, 3]
    """
    return create_node(node_type="transform", name=name, **kwargs)


def locator(name=None, **kwargs):
    """Create a Maya locator node as an NcNode.

    Args:
        name (str): Name of locator instance that will be created
        kwargs (dict): keyword arguments given to create_node function

    Returns:
        NcNode: Instance that is linked to the newly created locator

    Example:
        ::

            a = noca.locator("myLoc")
            a.t = [1, 2, 3]
    """
    return create_node(node_type="locator", name=name, **kwargs)


def create_node(node_type, name=None, **kwargs):
    """Create a new node of given type as an NcNode.

    Args:
        node_type (str): Type of Maya node to be created
        name (str): Name for new Maya-node
        kwargs (dict): arguments that are passed to Maya createNode function

    Returns:
        NcNode: Instance that is linked to the newly created transform

    Example:
        ::

            a = noca.create_node("transform", "myTransform")
            a.t = [1, 2, 3]
    """
    attrs = kwargs.pop("attrs", None)
    node = _traced_create_node(node_type, name=name, **kwargs)
    noca_node = Node(node, attrs=attrs)

    return noca_node


def set_global_auto_unravel(state):
    """Set the global auto unravel state.

    Note:
        Auto unravel breaks up a parent attr into its child attrs:
        "translate" becomes ["translateX", "translateY", "translateZ"].

        This behaviour is desired in most cases for the NodeCalculator to work.
        But in some cases the user might want to prevent this. For example:
        When using the choice-node the user probably wants the inputs to be
        exactly the ones chosen (not broken up into child-attributes and those
        connected to the choice node).

    Args:
        state (bool): State auto unravel should be set to
    """
    global GLOBAL_AUTO_UNRAVEL
    GLOBAL_AUTO_UNRAVEL = state


def set_global_auto_consolidate(state):
    """Set the global auto consolidate state.

    Note:
        Auto consolidate combines full set of child attrs to their parent attr:
        ["translateX", "translateY", "translateZ"] becomes "translate".

        Consolidating plugs is preferable: it will make your node graph cleaner
        and easier to read.
        However: Using parent plugs can sometimes cause update issues on attrs!

    Args:
        state (bool): State auto consolidate should be set to
    """
    global GLOBAL_AUTO_CONSOLIDATE
    GLOBAL_AUTO_CONSOLIDATE = state


def noca_op(func):
    """Add given function to the Op-class.

    Note:
        This is a decorator used in NodeCalculator extensions! It makes it easy
        for the user to add additional operators to the Op-class.

        Check the tutorials and example extension files to see how you can
        create your own extensions.

    Args:
        func (executable): Function to be added to Op as a method.
    """
    setattr(Op, func.__name__, func)


# OPERATORS ---
class OperatorMetaClass(object):
    """MetaClass for NodeCalculator operators that go beyond basic math.

    Note:
        A meta-class was used to ensure the "Op"-class to be a singleton class.
        Some methods are created on the fly in the __init__ method.
    """

    def __init__(self, name, bases, body):
        """OperatorMetaClass-class constructor

        Note:
            name, bases, body are necessary for __metaclass__ to work properly
        """
        for required_plugin in lookup_table.BASIC_REQUIRED_PLUGINS:
            cmds.loadPlugin(required_plugin, quiet=True)

        super(OperatorMetaClass, self).__init__()

    def available(self, full=False):
        """Print all available operators.

        Args:
            full (bool): If False only the operator-names are printed. If True
                the docString of all operators is printed. Defaults to False.
        """
        excluded = ["available"]

        print("\n############ Available NodeCalculator Operators ############")

        for item in dir(self):
            # Skip all methods that are (semi-)private.
            if not item.startswith("_") and item not in excluded:
                # Print the entire docString.
                if full:
                    title_text = "{0}:".format(item)
                    title_str = "{0}\n{1}\n{2}".format(
                        "="*60, title_text, "-"*len(title_text)
                    )
                    print(title_str)
                    print(getattr(self, item).__doc__)
                # Print the operator-name only.
                else:
                    print(item)

        print("##############################################################")

    @staticmethod
    def angle_between(vector_a, vector_b=(1, 0, 0)):
        """Create angleBetween-node to find the angle between 2 vectors.

        Args:
            vector_a (NcNode or NcAttrs or int or float or list): Vector to
                consider for angle between
            vector_b (NcNode or NcAttrs or int or float or list): Vector to
                consider for angle between

        Returns:
            NcNode: Instance with angleBetween-node and output-attribute(s)

        Example:
            ::

                matrix = Node("pCube1").worldMatrix
                pt = Op.point_matrix_mult(
                    [1, 0, 0], matrix, vector_multiply=True
                )
                Op.angle_between(pt, [1, 0, 0])
        """
        return _create_operation_node('angle_between', vector_a, vector_b)

    @staticmethod
    def average(*attrs):
        """Create plusMinusAverage-node for averaging input attrs.

        Args:
            attrs (NcNode or NcAttrs or string or list): Inputs to be averaged

        Returns:
            NcNode: Instance with plusMinusAverage-node and output-attribute(s)

        Example:
            ::

                Op.average(Node("pCube.t"), [1, 2, 3])
        """
        return _create_operation_node('average', attrs)

    @staticmethod
    def blend(attr_a, attr_b, blend_value=0.5):
        """Create blendColor-node.

        Args:
            attr_a (NcNode or NcAttrs or str or int or float): Plug or value to
                blend from
            attr_b (NcNode or NcAttrs or str or int or float): Plug or value to
                blend to
            blend_value (NcNode or str or int or float): Plug or value defining
                blend-amount

        Returns:
            NcNode: Instance with blend-node and output-attributes

        Example:
            ::

                Op.blend(1, Node("pCube.tx"), Node("pCube.customBlendAttr"))
        """
        return _create_operation_node('blend', attr_a, attr_b, blend_value)

    @staticmethod
    def choice(inputs, selector=0):
        """Create choice-node to switch between various input attributes.

        Note:
            Multi index input seems to also require one 'selector' per index.
            So we package a copy of the same selector for each input.

        Args:
            inputs (list): Any number of input values or plugs
            selector (NcNode or NcAttrs or int): Selector-attr on choice node
                to select one of the inputs based on their index.

        Returns:
            NcNode: Instance with choice-node and output-attribute(s)

        Example:
            ::

                option_a = Node("pCube1.tx")
                option_b = Node("pCube2.tx")
                switch = Node("pSphere1").add_bool("optionSwitch")
                choice_node = Op.choice([option_a, option_b], selector=switch)
                Node("pTorus1").tx = choice_node
        """
        choice_node_obj = _create_operation_node('choice', inputs, selector)

        return choice_node_obj

    @staticmethod
    def clamp(attr_a, min_value=0, max_value=1):
        """Create clamp-node.

        Args:
            attr_a (NcNode or NcAttrs or str or int or float): Input value
            min_value (NcNode or NcAttrs or int or float or list): min-value
                for clamp-operation
            max_value (NcNode or NcAttrs or int or float or list): max-value
                for clamp-operation

        Returns:
            NcNode: Instance with clamp-node and output-attribute(s)

        Example:
            ::

                Op.clamp(Node("pCube.t"), [1, 2, 3], 5)
        """
        return _create_operation_node('clamp', attr_a, min_value, max_value)

    @staticmethod
    def compose_matrix(**kwargs):
        """Create composeMatrix-node to assemble matrix from transforms.

        Args:
            kwargs (dict): Possible kwargs below. longName flags take
                precedence over the short names in [brackets]!
            translate (NcNode or NcAttrs or str or int or float): [t] translate
            rotate (NcNode or NcAttrs or str or int or float): [r] rotate
            scale (NcNode or NcAttrs or str or int or float): [s] scale
            shear (NcNode or NcAttrs or str or int or float): [sh] shear
            rotate_order (NcNode or NcAttrs or str or int): [ro] rot-order
            euler_rotation (NcNode or NcAttrs or bool): Euler rot or quaternion

        Returns:
            NcNode: Instance with composeMatrix-node and output-attribute(s)

        Example:
            ::

                in_a = Node('pCube1')
                in_b = Node('pCube2')
                decomp_a = Op.decompose_matrix(in_a.worldMatrix)
                decomp_b = Op.decompose_matrix(in_b.worldMatrix)
                Op.compose_matrix(r=decomp_a.outputRotate, s=decomp_b.outputScale)
        """
        # Using kwargs not to have a lot of flags in the function call
        translate = kwargs.get("translate", kwargs.get("t", 0))
        rotate = kwargs.get("rotate", kwargs.get("r", 0))
        scale = kwargs.get("scale", kwargs.get("s", 1))
        shear = kwargs.get("shear", kwargs.get("sh", 0))
        rotate_order = kwargs.get("rotate_order", kwargs.get("ro", 0))
        euler_rotation = kwargs.get("euler_rotation", True)

        compose_matrix_node = _create_operation_node(
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
            An appropriate NcNode-object gets automatically created when
            NodeCalculator objects are used in comparisons (==, >, >=, <, <=).
            Simply use comparison operators in the first argument. See example.

        Args:
            condition_node (NcNode): Condition-statement. See note and example.
            if_part (NcNode or NcAttrs or str or int or float): Value/plug that
                is returned if the condition evaluates to true.
            else_part (NcNode or NcAttrs or str or int or float): Value/plug
                that is returned if the condition evaluates to false.

        Returns:
            NcNode: Instance with condition-node and outColor-attributes

        Example:
            ::

                condition_node = Node("pCube1.tx") >= 2
                pass_on_if_true = Node("pCube2.ty") + 2
                pass_on_if_false = 5 - Node("pCube2.tz").get()
                # Op.condition(condition-part, "if true"-part, "if false"-part)
                Op.condition(condition_node, pass_on_if_true, pass_on_if_false)
        """
        # Make sure condition_node is of expected Node-type!
        if not isinstance(condition_node, NcNode):
            LOG.warn("%s isn't NcNode-instance.", condition_node)
        if cmds.objectType(condition_node.node) != "condition":
            LOG.warn("%s isn't of type condition.", condition_node)

        # Determine how many attrs were given & need to be connected
        max_dim = max(
            [len(_unravel_item_as_list(part)) for part in [if_part, else_part]]
        )

        # Connect the given if/else parts to the condition node
        cond_input_attrs = [
            ["colorIfTrueR", "colorIfTrueG", "colorIfTrueB"],
            ["colorIfFalseR", "colorIfFalseG", "colorIfFalseB"],
        ]
        node_name = condition_node.node
        for input_attrs, part in zip(cond_input_attrs, [if_part, else_part]):
            condition_input_list = [
                "{0}.{1}".format(node_name, attr)
                for attr in input_attrs[:max_dim]
            ]

            _unravel_and_set_or_connect_a_to_b(condition_input_list, part)

        # Return new NcNode instance with condition node and its output attrs.
        cond_output_attrs = ["outColorR", "outColorG", "outColorB"]
        return_value = NcNode(node_name, cond_output_attrs[:max_dim])
        return return_value

    @staticmethod
    def cross(attr_a, attr_b=0, normalize=False):
        """Create vectorProduct-node for vector cross-multiplication.

        Args:
            attr_a (NcNode or NcAttrs or str or int or float or list): Vector A
            attr_b (NcNode or NcAttrs or str or int or float or list): Vector B
            normalize (NcNode or NcAttrs or boolean): Whether resulting vector
                should be normalized

        Returns:
            NcNode: Instance with vectorProduct-node and output-attribute(s)

        Example:
            ::

                Op.cross(Node("pCube.t"), [1, 2, 3], True)
        """
        return _create_operation_node('cross', attr_a, attr_b, normalize)

    @staticmethod
    def decompose_matrix(in_matrix):
        """Create decomposeMatrix-node to disassemble matrix into transforms.

        Args:
            in_matrix (NcNode or NcAttrs or string): matrix attr to decompose

        Returns:
            NcNode: Instance with decomposeMatrix-node and output-attribute(s)

        Example:
            ::

                driver = Node('pCube1')
                driven = Node('pSphere1')
                decomp = Op.decompose_matrix(driver.worldMatrix)
                driven.t = decomp.outputTranslate
                driven.r = decomp.outputRotate
                driven.s = decomp.outputScale
        """
        return _create_operation_node('decompose_matrix', in_matrix)

    @staticmethod
    def dot(attr_a, attr_b=0, normalize=False):
        """Create vectorProduct-node for vector dot-multiplication.

        Args:
            attr_a (NcNode or NcAttrs or str or int or float or list): Vector A
            attr_b (NcNode or NcAttrs or str or int or float or list): Vector B
            normalize (NcNode or NcAttrs or boolean): Whether resulting vector
                should be normalized

        Returns:
            NcNode: Instance with vectorProduct-node and output-attribute(s)

        Example:
            ::

                Op.dot(Node("pCube.t"), [1, 2, 3], True)
        """
        return _create_operation_node('dot', attr_a, attr_b, normalize)

    @staticmethod
    def exp(attr_a):
        """Raise attr_a to the base of natural logarithms.

        Args:
            attr_a (NcNode or NcAttrs or str or int or float): Value or attr

        Returns:
            NcNode: Instance with multiplyDivide-node and output-attr(s)

        Example:
            ::

                Op.exp(Node("pCube.t"))
        """
        return math.e ** attr_a

    @staticmethod
    def inverse_matrix(in_matrix):
        """Create inverseMatrix-node to invert the given matrix.

        Args:
            in_matrix (NcNode or NcAttrs or str): Matrix to invert

        Returns:
            NcNode: Instance with inverseMatrix-node and output-attribute(s)

        Example:
            ::

                Op.inverse_matrix(Node("pCube.worldMatrix"))
        """
        return _create_operation_node('inverse_matrix', in_matrix)

    @staticmethod
    def length(attr_a, attr_b=0):
        """Create distanceBetween-node to measure length between given points.

        Args:
            attr_a (NcNode or NcAttrs or str or int or float): Start point
            attr_b (NcNode or NcAttrs or str or int or float): End point

        Returns:
            NcNode: Instance with distanceBetween-node and distance-attribute

        Example:
            ::

                Op.len(Node("pCube.t"), [1, 2, 3])
        """
        return _create_operation_node('length', attr_a, attr_b)

    @staticmethod
    def matrix_distance(matrix_a, matrix_b=None):
        """Create distanceBetween-node to measure distance between matrices.

        Args:
            matrix_a (NcNode or NcAttrs or str): Matrix defining start point.
            matrix_b (NcNode or NcAttrs or str): Matrix defining end point.

        Returns:
            NcNode: Instance with distanceBetween-node and distance-attribute

        Example:
            ::

                Op.len(Node("pCube.worldMatrix"), Node("pCube2.worldMatrix"))
        """
        if matrix_b is None:
            return _create_operation_node('matrix_distance', matrix_a)
        return _create_operation_node('matrix_distance', matrix_a, matrix_b)

    @staticmethod
    def mult_matrix(*attrs):
        """Create multMatrix-node for multiplying matrices.

        Args:
            attrs (NcNode or NcAttrs or string or list): Matrices to multiply

        Returns:
            NcNode: Instance with multMatrix-node and output-attribute(s)

        Example:
            ::

                matrix_mult = Op.mult_matrix(
                    Node('pCube1.worldMatrix'), Node('pCube2').worldMatrix
                )
                decomp = Op.decompose_matrix(matrix_mult)
                out = Node('pSphere')
                out.translate = decomp.outputTranslate
                out.rotate = decomp.outputRotate
                out.scale = decomp.outputScale
        """
        return _create_operation_node('mult_matrix', attrs)

    @staticmethod
    def normalize_vector(in_vector, normalize=True):
        """Create vectorProduct-node to normalize the given vector.

        Args:
            in_vector (NcNode or NcAttrs or str or int or float or list): Vect.
            normalize (NcNode or NcAttrs or boolean): Turn normalize on/off

        Returns:
            NcNode: Instance with vectorProduct-node and output-attribute(s)

        Example:
            ::

                Op.normalize_vector(Node("pCube.t"))
        """
        # Making normalize a flag allows the user to connect attributes to it
        return_value = _create_operation_node(
            'normalize_vector',
            in_vector,
            normalize
        )
        return return_value

    @staticmethod
    def pair_blend(
            translate_a=0,
            rotate_a=0,
            translate_b=0,
            rotate_b=0,
            weight=1,
            quat_interpolation=False):
        """Create pairBlend-node to blend between two transforms.

        Args:
            translate_a (NcNode or NcAttrs or str or int or float or list):
                Translate value of first transform.
            rotate_a (NcNode or NcAttrs or str or int or float or list):
                Rotate value of first transform.
            translate_b (NcNode or NcAttrs or str or int or float or list):
                Translate value of second transform.
            rotate_b (NcNode or NcAttrs or str or int or float or list):
                Rotate value of second transform.
            weight (NcNode or NcAttrs or str or int or float or list):
                Bias towards first or second transform.
            quat_interpolation (NcNode or NcAttrs or boolean):
                Use euler (False) or quaternions (True) to interpolate rotation

        Returns:
            NcNode: Instance with pairBlend-node and output-attribute(s)

        Example:
            ::

                a = Node("pCube1")
                b = Node("pSphere1")
                blend_attr = a.add_float("blend")
                Op.pair_blend(a.t, a.r, b.t, b.r, blend_attr)
        """
        return_value = _create_operation_node(
            'pair_blend',
            translate_a,
            rotate_a,
            translate_b,
            rotate_b,
            weight,
            quat_interpolation,
        )
        return return_value

    @staticmethod
    def point_matrix_mult(in_vector, in_matrix, vector_multiply=False):
        """Create pointMatrixMult-node to transpose the given matrix.

        Args:
            in_vector (NcNode or NcAttrs or str or int or float or list): Vect.
            in_matrix (NcNode or NcAttrs or str): Matrix
            vector_multiply (NcNode or NcAttrs or str or int or bool): Whether
                vector multiplication should be performed.

        Returns:
            NcNode: Instance with pointMatrixMult-node and output-attribute(s)

        Example:
            ::

                Op.point_matrix_mult(
                    Node("pSphere.t"),
                    Node("pCube.worldMatrix"),
                    vector_multiply=True
                )
        """
        created_node = _create_operation_node(
            'point_matrix_mult',
            in_vector,
            in_matrix,
            vector_multiply
        )

        return created_node

    @staticmethod
    def pow(attr_a, attr_b):
        """Raise attr_a to the power of attr_b.

        Args:
            attr_a (NcNode or NcAttrs or str or int or float): Value or attr
            attr_b (NcNode or NcAttrs or str or int or float): Value or attr

        Returns:
            NcNode: Instance with multiplyDivide-node and output-attr(s)

        Example:
            ::

                Op.pow(Node("pCube.t"), 2.5)
        """
        return attr_a ** attr_b

    @staticmethod
    def remap_value(
            attr_a,
            output_min=0,
            output_max=1,
            input_min=0,
            input_max=1,
            values=None):
        """Create remapValue-node to remap the given input.

        Args:
            attr_a (NcNode or NcAttrs or str or int or float): Input value
            output_min (NcNode or NcAttrs or int or float or list): minValue
            output_max (NcNode or NcAttrs or int or float or list): maxValue
            input_min (NcNode or NcAttrs or int or float or list): old minValue
            input_max (NcNode or NcAttrs or int or float or list): old maxValue
            values (list): List of tuples in the following form;
                (value_Position, value_FloatValue, value_Interp)
                The value interpolation element is optional (default: linear)

        Returns:
            NcNode: Instance with remapValue-node and output-attribute(s)

        Raises:
            TypeError: If given values isn't a list of either lists or tuples.
            RuntimeError: If given values isn't a list of lists/tuples of
                length 2 or 3.

        Example:
            ::

                Op.remap_value(
                    Node("pCube.t"),
                    values=[(0.1, .2, 0), (0.4, 0.3)]
                )
        """
        created_node = _create_operation_node(
            'remap_value', attr_a, output_min, output_max, input_min, input_max
        )

        for index, value_data in enumerate(values or []):
            # value_Position, value_FloatValue, value_Interp
            # "x-axis", "y-axis", interpolation

            if not isinstance(value_data, (list, tuple)):
                msg = (
                    "The values-flag for remap_value requires a list of "
                    "tuples! Got {0} instead.".format(values)
                )
                raise TypeError(msg)

            elif len(value_data) == 2:
                pos, val = value_data
                interp = 1

            elif len(value_data) == 3:
                pos, val, interp = value_data

            else:
                msg = (
                    "The values-flag for remap_value requires a list of "
                    "tuples of length 2 or 3! Got {0} instead.".format(values)
                )
                raise RuntimeError(msg)

            # Set these attributes directly to avoid unnecessary unravelling.
            _traced_set_attr(
                "{0}.value[{1}]".format(created_node.node, index),
                (pos, val, interp)
            )

        return created_node

    @staticmethod
    def set_range(
            attr_a,
            min_value=0,
            max_value=1,
            old_min_value=0,
            old_max_value=1):
        """Create setRange-node to remap the given input attr to a new min/max.

        Args:
            attr_a (NcNode or NcAttrs or str or int or float): Input value
            min_value (NcNode or NcAttrs or int or float or list): new min
            max_value (NcNode or NcAttrs or int or float or list): new max
            old_min_value (NcNode or NcAttrs or int or float or list): old min
            old_max_value (NcNode or NcAttrs or int or float or list): old max

        Returns:
            NcNode: Instance with setRange-node and output-attribute(s)

        Example:
            ::

                Op.set_range(Node("pCube.t"), [1, 2, 3], 4, [-1, 0, -2])
        """
        return_value = _create_operation_node(
            'set_range',
            attr_a,
            min_value,
            max_value,
            old_min_value,
            old_max_value
        )
        return return_value

    @staticmethod
    def soft_approach(in_value, fade_in_range=0.5, target_value=1):
        """Follow in_value, but approach the target_value slowly.

        Note:
            Only works for 1D inputs!

        Args:
            in_value (NcNode or NcAttrs or str or int or float): Value or attr
            fade_in_range (NcNode or NcAttrs or str or int or float): Value or
                attr. This defines a range over which the target_value will be
                approached. Before the in_value is within this range the output
                of this and the in_value will be equal.
            target_value (NcNode or NcAttrs or str or int or float): Value or
                attr. This is the value that will be approached slowly.

        Returns:
            NcNode: Instance with node and output-attr.

        Example:
            ::

                in_attr = Node("pCube.tx")
                Op.soft_approach(in_attr, fade_in_range=2, target_value=5)
                # Starting at the value 3 (because 5-2=3), the output of this
                # will slowly approach the target_value 5.
        """
        start_val = target_value - fade_in_range

        exponent = ((start_val) - in_value) / fade_in_range
        soft_approach_value = target_value - fade_in_range * Op.exp(exponent)

        is_range_valid_condition = Op.condition(
            fade_in_range > 0,
            soft_approach_value,
            target_value
        )

        is_in_range_condition = Op.condition(
            in_value > start_val,
            is_range_valid_condition,
            in_value
        )

        return is_in_range_condition

    @staticmethod
    def sqrt(attr_a):
        """Get the square root of attr_a.

        Args:
            attr_a (NcNode or NcAttrs or str or int or float): Value or attr

        Returns:
            NcNode: Instance with multiplyDivide-node and output-attr(s)

        Example:
            ::

                Op.sqrt(Node("pCube.tx"))
        """
        return attr_a ** 0.5

    @staticmethod
    def transpose_matrix(in_matrix):
        """Create transposeMatrix-node to transpose the given matrix.

        Args:
            in_matrix (NcNode or NcAttrs or str): Plug or value for in_matrix

        Returns:
            NcNode: Instance with transposeMatrix-node and output-attribute(s)

        Example:
            ::

                Op.transpose_matrix(Node("pCube.worldMatrix"))
        """
        return _create_operation_node('transpose_matrix', in_matrix)


class Op(object):
    """Create Operator-class from OperatorMetaClass.

    Note:
        Check docString of OperatorMetaClass for details.
    """

    __metaclass__ = OperatorMetaClass


# NcBaseClass ---
class NcBaseClass(object):
    """Base class for NcLists & NcBaseNode (hence indirectly NcNode & NcAttrs).

    Note:
        NcNode, NcAttrs and NcList are the "building blocks" of NodeCalculator
        calculations. Having NcBaseClass as their common parent class makes
        sure the overloaded operators apply to each of these "building blocks".
    """

    # Class variables:
    # Whether Tracer is active or not; Use "with noca.Tracer():" to trace!
    _is_tracing = False
    # Maya commands the NodeCalculator executed within "with noca.Tracer():"
    _executed_commands_stack = []
    # Maya nodes the NodeCalculator created within "with noca.Tracer():"
    _traced_nodes = None
    # Values the NodeCalculator queried within "with noca.Tracer():"
    _traced_values = None

    def __init__(self):
        """Initialize NcBaseClass instance."""
        super(NcBaseClass, self).__init__()

    def __pos__(self):
        """Leading plus signs are ignored, since they are redundant.

        Example:
            ::

                + Node("pCube1.ty")
        """
        LOG.debug("%s __pos__ (%s)", self.__class__.__name__, self)

        pass

    def __neg__(self):
        """Leading minus sign multiplies by -1.

        Example:
            ::

                - Node("pCube1.ty")
        """
        LOG.debug("%s __neg__ (%s)", self.__class__.__name__, self)

        result = self * -1
        return result

    def __add__(self, other):
        """Regular addition operator for NodeCalculator objects.

        Example:
            ::

                Node("pCube1.ty") + 4
        """
        LOG.debug("%s __add__ (%s, %s)", self.__class__.__name__, self, other)

        return _create_operation_node("add", [self, other])

    def __radd__(self, other):
        """Reflected addition operator for NodeCalculator objects.

        Note:
            Fall-back method if regular addition is not defined/fails.

        Example:
            ::

                4 + Node("pCube1.ty")
        """
        LOG.debug("%s __radd__ (%s, %s)", self.__class__.__name__, self, other)

        return _create_operation_node("add", [other, self])

    def __sub__(self, other):
        """Regular subtraction operator for NodeCalculator objects.

        Example:
            ::

                Node("pCube1.ty") - 4
        """
        LOG.debug("%s __sub__ (%s, %s)", self.__class__.__name__, self, other)

        return _create_operation_node("sub", [self, other])

    def __rsub__(self, other):
        """Reflected subtraction operator for NodeCalculator objects.

        Note:
            Fall-back method if regular subtraction is not defined/fails.

        Example:
            ::

                4 - Node("pCube1.ty")
        """
        LOG.debug("%s __rsub__ (%s, %s)", self.__class__.__name__, self, other)

        return _create_operation_node("sub", [other, self])

    def __mul__(self, other):
        """Regular multiplication operator for NodeCalculator objects.

        Example:
            ::

                Node("pCube1.ty") * 4
        """
        LOG.debug("%s __mul__ (%s, %s)", self.__class__.__name__, self, other)

        return _create_operation_node("mul", self, other)

    def __rmul__(self, other):
        """Reflected multiplication operator for NodeCalculator objects.

        Note:
            Fall-back method if regular multiplication is not defined/fails.

        Example:
            ::

                4 * Node("pCube1.ty")
        """
        LOG.debug("%s __rmul__ (%s, %s)", self.__class__.__name__, self, other)

        return _create_operation_node("mul", other, self)

    def __div__(self, other):
        """Regular division operator for NodeCalculator objects.

        Example:
            ::

                Node("pCube1.ty") / 4
        """
        LOG.debug("%s __div__ (%s, %s)", self.__class__.__name__, self, other)

        return _create_operation_node("div", self, other)

    def __rdiv__(self, other):
        """Reflected division operator for NodeCalculator objects.

        Note:
            Fall-back method if regular division is not defined/fails.

        Example:
            ::

                4 / Node("pCube1.ty")
        """
        LOG.debug("%s __rdiv__ (%s, %s)", self.__class__.__name__, self, other)

        return _create_operation_node("div", other, self)

    def __pow__(self, other):
        """Regular power operator for NodeCalculator objects.

        Example:
            ::

                Node("pCube1.ty") ** 4
        """
        LOG.debug("%s __pow__ (%s, %s)", self.__class__.__name__, self, other)

        return _create_operation_node("pow", self, other)

    def __rpow__(self, other):
        """Reflected power operator for NodeCalculator objects.

        Example:
            ::

                4 ** Node("pCube1.ty")
        """
        LOG.debug("%s __rpow__ (%s, %s)", self.__class__.__name__, self, other)

        return _create_operation_node("pow", other, self)

    def __eq__(self, other):
        """Equality operator for NodeCalculator objects.

        Returns:
            NcNode: Instance of a newly created Maya condition-node

        Example:
            ::

                Node("pCube1.ty") == 4
        """
        LOG.debug("%s __eq__ (%s, %s)", self.__class__.__name__, self, other)

        return self._compare(other, "eq")

    def __ne__(self, other):
        """Inequality operator for NodeCalculator objects.

        Returns:
            NcNode: Instance of a newly created Maya condition-node

        Example:
            ::

                Node("pCube1.ty") != 4
        """
        LOG.debug("%s __ne__ (%s, %s)", self.__class__.__name__, self, other)

        return self._compare(other, "ne")

    def __gt__(self, other):
        """Greater than operator for NodeCalculator objects.

        Returns:
            NcNode: Instance of a newly created Maya condition-node

        Example:
            ::

                Node("pCube1.ty") > 4
        """
        LOG.debug("%s __gt__ (%s, %s)", self.__class__.__name__, self, other)

        return self._compare(other, "gt")

    def __ge__(self, other):
        """Greater equal operator for NodeCalculator objects.

        Returns:
            NcNode: Instance of a newly created Maya condition-node

        Example:
            ::

                Node("pCube1.ty") >= 4
        """
        LOG.debug("%s __ge__ (%s, %s)", self.__class__.__name__, self, other)

        return self._compare(other, "ge")

    def __lt__(self, other):
        """Less than operator for NodeCalculator objects.

        Returns:
            NcNode: Instance of a newly created Maya condition-node

        Example:
            ::

                Node("pCube1.ty") < 4
        """
        LOG.debug("%s __lt__ (%s, %s)", self.__class__.__name__, self, other)

        return self._compare(other, "lt")

    def __le__(self, other):
        """Less equal operator for NodeCalculator objects.

        Returns:
            NcNode: Instance of a newly created Maya condition-node

        Example:
            ::

                Node("pCube1.ty") <= 4
        """
        LOG.debug("%s __le__ (%s, %s)", self.__class__.__name__, self, other)

        return self._compare(other, "le")

    def _compare(self, other, operator):
        """Create a Maya condition node, set to the correct operation-type.

        Args:
            other (NcNode or int or float): Compare self-attrs with other
            operator (string): Operation type available in Maya condition-nodes

        Returns:
            NcNode: Instance of a newly created Maya condition-node
        """
        # Create new condition node set to the appropriate operation-type
        return_value = _create_operation_node(operator, self, other)

        return return_value

    @classmethod
    def _initialize_trace_variables(cls):
        """Reset all class variables used for tracing."""
        cls._flush_command_stack()
        cls._flush_traced_nodes()
        cls._flush_traced_values()

    @classmethod
    def _flush_command_stack(cls):
        """Reset class-variable _executed_commands_stack to an empty list."""
        cls._executed_commands_stack = []

    @classmethod
    def _flush_traced_nodes(cls):
        """Reset class-variable _traced_nodes to an empty list."""
        cls._traced_nodes = []

    @classmethod
    def _flush_traced_values(cls):
        """Reset class-variable _traced_values to an empty list."""
        cls._traced_values = []

    @classmethod
    def _add_to_command_stack(cls, command):
        """Add a command to the class-variable _executed_commands_stack.

        Args:
            command (str or list): String or list of strings of Maya command(s)
        """
        if isinstance(command, (list, tuple)):
            cls._executed_commands_stack.extend(command)
        else:
            cls._executed_commands_stack.append(command)

    @classmethod
    def _add_to_traced_nodes(cls, node):
        """Add a node to the class-variable _traced_nodes.

        Args:
            node (TracerMObject): MObject with metadata. Check docString of
                TracerMObject for more detail!
        """
        cls._traced_nodes.append(node)

    @classmethod
    def _get_next_variable_name(cls):
        """Return the next available variable name.

        Note:
            When Tracer is active, created nodes get a variable name assigned.

        Returns:
            str: Next available variable name.
        """
        next_variable_index = len(cls._traced_nodes) + 1
        variable_name = "{0}{1}".format(
            VARIABLE_PREFIX,
            next_variable_index
        )
        return variable_name

    @classmethod
    def _get_tracer_variable_for_node(cls, node):
        """Try to find and return traced variable for given node.

        Args:
            node (str): Name of Maya node

        Returns:
            str or None: If there is a traced variable for this node:
                Return the variable, otherwise return None
        """
        for traced_node_mobj in cls._traced_nodes:
            if traced_node_mobj.node == node:
                return traced_node_mobj.tracer_variable

        return None

    @classmethod
    def _add_to_traced_values(cls, value):
        """Add a value to the class-variable _traced_values.

        Args:
            value (NcValue): Value with metadata. Check docString of NcValue.
        """
        cls._traced_values.append(value)

    @classmethod
    def _get_next_value_name(cls):
        """Return the next available value name.

        Note:
            When Tracer is active, queried values get a value name assigned.

        Returns:
            str: Next available value name.
        """
        next_value_index = len(cls._traced_values) + 1
        value_name = "{0}{1}".format(VALUE_PREFIX, next_value_index)
        return value_name


# NcBaseNode ---
class NcBaseNode(NcBaseClass):
    """Base class for NcNode and NcAttrs.

    Note:
        This class will have access to the .node and .attrs attributes, once it
        is instantiated in the form of a NcNode or NcAttrs instance.
    """

    def __init__(self):
        """Initialize of NcBaseNode class, which is used for NcNode & NcAttrs.

        Note:
            For more detail about auto_unravel & auto_consolidate check
            docString of set_global_auto_consolidate & set_global_auto_unravel!

        Args:
            auto_unravel (bool): Should attrs of this instance be unravelled.
            auto_consolidate (bool): Should instance-attrs be consolidated.
        """
        super(NcBaseNode, self).__init__()

        self.__dict__["_holder_node"] = None
        self.__dict__["_held_attrs"] = None

        self._add_all_add_attr_methods()

    def __len__(self):
        """Return the length of the stored attributes list.

        Returns:
            int: Length of stored NcAttrs list. 0 if no Attrs are defined.
        """
        return len(self.attrs_list)

    def __str__(self):
        """Print readable format of NcBaseNode instance.

        Note:
            For example invoked by using print() in Maya.

        Returns:
            str: String of concatenated node and attrs.

        """
        return "(Node: {0}, Attrs: {1})".format(self.node, self.attrs_list)

    def __repr__(self):
        """Print unambiguous format of NcBaseNode instance.

        Note:
            For example invoked by running highlighted code in Maya.

        Returns:
            str: String of concatenated class-type, node and attrs.
        """
        return_value = "{0}({1}, {2})".format(
            self.__class__.__name__,
            self.node,
            self.attrs_list
        )
        return return_value

    def __iter__(self):
        """Iterate over list of attributes.

        Yields:
            NcNode: Next item in list of attributes.

        Raises:
            StopIteration: If end of .attrs_list is reached.
        """
        LOG.debug("%s __iter__ (%s)", self.__class__.__name__, self)

        i = 0
        while True:
            try:
                yield NcNode(self.node, self.attrs_list[i])
            except IndexError:
                raise StopIteration
            i += 1

    def __setattr__(self, name, value):
        """Set or connect attribute to the given value.

        Note:
            Attribute setting works the same way for NcNode and NcAttrs
            instances. Their difference lies within the __getattr__ method.

            setattr is invoked by equal-sign. Does NOT work without attr:

            a = Node("pCube1.ty")  # Initialize Node-object with attr given

            a.ty = 7  # Works fine if attribute is specifically called

            a = 7  # Does NOT work!

            It looks like the same operation as above, but here Python calls
            the assignment operation, NOT setattr. The assignment operation
            can't be overridden.

        Args:
            name (str): Name of the attribute to be set
            value (NcNode or NcAttrs or str or int or float or list or tuple):
                Connect attr to this object or set attr to this value/array

        Example:
            ::

                a = Node("pCube1") # Create new NcNode-object
                a.tx = 7  # Set pCube1.tx to the value 7
                a.t = [1, 2, 3]  # Set pCube1.tx|ty|tz to 1|2|3 respectively
                a.tx = Node("pCube2").ty  # Connect pCube2.ty to pCube1.tx
        """
        LOG.debug(
            "%s __setattr__ (%s, %s)", self.__class__.__name__, name, value
        )

        _unravel_and_set_or_connect_a_to_b(self.__getattr__(name), value)

    def __setitem__(self, index, value):
        """Set or connect attribute at index to the given value.

        Note:
            Item setting works the same way for NcNode and NcAttrs instances.
            Their difference lies within the __getitem__ method.

            This looks at the list of attrs stored inside NcAttrs.

        Args:
            index (int): Index of item to be set
            value (NcNode or NcAttrs or str or int or float): Set/connect item
                at index to this.
        """
        LOG.debug(
            "%s __setitem__ (%s, %s)", self.__class__.__name__, index, value
        )

        _unravel_and_set_or_connect_a_to_b(self[index], value)

    @property
    def plugs(self):
        """Property to allow easy access to the Node-plugs.

        Note:
            A "plug" stands for "node.attr"!

        Returns:
            list: List of plugs. Empty list if no attributes are defined!
        """
        if not self.attrs:
            return []

        return_list = [
            "{0}.{1}".format(self.node, attr) for attr in self.attrs_list
        ]
        return return_list

    @property
    def nodes(self):
        """Property that returns node within list.

        Note:
            This property mostly exists to maintain consistency with NcList.
            Even though nodes of a NcNode/NcAttrs instance will always be a
            list of length 1 it might come in handy to match the property of
            NcLists!

        Returns:
            list: Name of Maya node this instance refers to, in a list.
        """
        return [self.node]

    def get(self):
        """Get the value of a NcNode/NcAttrs-attribute.

        Note:
            Works similar to a cmds.getAttr().

        Returns:
            int or float or list: Value of the queried attribute.
        """
        LOG.debug("%s get (%s)", self.__class__.__name__, self)

        # If only a single attribute exists: Return its value directly
        if len(self.attrs_list) == 1:
            return_value = _traced_get_attr(self.plugs[0])
        # If multiple attributes exist: Return list of values
        elif self.attrs_list:
            return_value = [_traced_get_attr(x) for x in self.plugs]
        # If no attribute is given on Node: Warn user and return None
        else:
            LOG.warn("No attribute exists on %s! Returned None", self)
            return_value = None

        return return_value

    def set(self, value):
        """Set or connect the value of a NcNode/NcAttrs-attribute.

        Note:
            Similar to a cmds.setAttr().

        Args:
            value (NcNode or NcAttrs or str or int or float or list or tuple):
                Connect attribute to this value (=plug)
                or set attribute to this value/array.
        """
        LOG.debug("%s set (%s)", self.__class__.__name__, value)

        _unravel_and_set_or_connect_a_to_b(self, value)

    def get_shapes(self, full=False):
        """Get shape nodes of self.node.

        Args:
            full (bool): Return full or shortest dag path

        Returns:
            list: List of MObjects of shapes.
        """
        shape_mobjs = om_util.get_shape_mobjs(self._node_mobj)

        shapes = [
            om_util.get_dag_path_of_mobj(mobj, full=full)
            for mobj in shape_mobjs
        ]

        return shapes

    def attr(self, attr=None):
        """Get new NcNode instance with given attr (using keywords is allowed).

        Note:
            It is pretty difficult to get an NcNode instance with any of the
            NodeCalculator keywords (node, attr, attrs, ...), except for when
            they are initialized. This method helps for those special cases.

        Args:
            attr (str): Attribute on the Maya node this instance refers to.

        Returns:
            NcNode or None: Instance with the given attr in its Attrs, or None
                if no attr was specified.
        """
        if attr is None:
            LOG.warn(
                "%s 'attr()' method call without arguments. Did you mean to "
                "use 'attrs'?", self.__class__.__name__
            )
            return None

        return NcNode(self._node_mobj, attr)

    def auto_state(self):
        """Print the status of _auto_unravel and _auto_consolidate."""
        message = "auto_unravel: {0}, auto_consolidate: {1}".format(
            self._auto_unravel, self._auto_consolidate
        )
        print(message)

    def to_py_node(self, ignore_attrs=False):
        """Get a PyNode from a NcNode/NcAttrs instance.

        Args:
            ignore_attrs (bool): Don't use attrs when creating PyNode instance.
                When set to True only the node will be used for PyNode
                instantiation. Defaults to False.

        Returns:
            pm.PyNode: PyNode-instance of this node or plug

        Raises:
            RuntimeError: If the user requested a PyNode of an NcNode/NcAttrs
                with multiple attrs. PyNodes can only contain one attr max.
        """
        # Without attrs or if they should be ignored; return PyNode with node.
        if ignore_attrs or not self.attrs_list:
            return pm.PyNode(self.node)

        # PyNode only accepts a singular attribute max.
        if len(self.attrs_list) == 1:
            return pm.PyNode(self.plugs[0])

        msg = (
            "Tried to create PyNode from NcNode with multiple attributes: {0} "
            "PyNode only supports node or single attributes! Use the flag "
            "ignore_attrs=True to omit the attrs of this noca-Node.".format(self)
        )
        raise RuntimeError(msg)

    def set_auto_unravel(self, state):
        """Change the auto unravelling state.

        Note:
            Check docString of set_global_auto_unravel for more info!

        Args:
            state (bool): Desired auto unravel state: On/Off
        """
        self.__dict__["_auto_unravel"] = state

    def set_auto_consolidate(self, state):
        """Change the auto consolidating state.

        Note:
            Check docString of set_global_auto_consolidate for more info!

        Args:
            state (bool): Desired auto consolidate state: On/Off
        """
        self.__dict__["_auto_consolidate"] = state

    def _add_all_add_attr_methods(self):
        """Add all possible attribute types for add_XYZ() methods via closure.

        Note:
            Allows to add attributes, similar to addAttr-command.

        Example:
            ::

                Node("pCube1").add_float("my_float_attr", defaultValue=1.1)
                Node("pCube1").add_short("my_int_attr", keyable=False)
        """
        for attr_type, attr_data in lookup_table.ATTR_TYPES.iteritems():
            # enum must be handled individually because of enumNames-flag
            if attr_type == "enum":
                continue

            data_type = attr_data["data_type"]
            func = self._define_add_attr_method(attr_type, data_type)
            self.__dict__["add_{0}".format(attr_type)] = func

    def _define_add_attr_method(self, attr_type, default_data_type):
        """Closure to add add_XYZ() methods.

        Note:
            Check docString of _add_all_add_attr_methods.

        Args:
            attr_type (str): Name of data type of this attr: bool, long, ...
            default_data_type (str): Either "attributeType" or "dataType". See
                Maya docs for more info.

        Returns:
            executable: Function that will be added to class methods.
        """

        @_format_docstring(attr_type=attr_type)
        def func(*args, **kwargs):
            """Create a {attr_type}-attr on the node, with given name & kwargs.

            Note:
                Use the same kwargs as in cmds.addAttr()!

                The name is awkwardly gathered through args, because the error
                when no name was specified was very cryptic!

            Args:
                args (list): Should only contain the name for the new attr
                kwargs (dict): User specified attributes to be set on new attr

            Returns:
                NcNode: NcNode-instance with the node and new attribute.

            Example:
                ::

                    Node("pCube1").add_{attr_type}("my_{attr_type}")
            """
            name = None
            # Multiple args are nonsensical for attribute creation.
            if len(args) > 1:
                msg = "Multiple args given for creation of {0} attr!".format(
                    attr_type
                )
                cmds.error(msg)

            # A single args-item can be assumed to be the name.
            if args:
                name = args[0]

            # If no name was specified, try to find it in the kwargs.
            else:
                name = kwargs.pop("name", None)
                if not name:
                    name_flags = ["niceName", "longName", "shortName"]
                    for name_flag in name_flags:
                        name = kwargs.get(name_flag, None)
                        if name:
                            break

            if not name:
                msg = "No name was given for creation of {0} attr!".format(
                    attr_type
                )
                cmds.error(msg)

            data_type = default_data_type
            # Since I opted for attributeType for all types that allowed
            # dataType and attributeType: Only a dataType keyword is relevant.
            if kwargs.get("dataType", None):
                data_type = "dataType"
                del kwargs["dataType"]
            # Remove attributeType keywords; attributeType is the default and
            # the actual type of the new attribute is defined by the name of
            # the method called: add_float, add_bool, ...
            if kwargs.get("attributeType", None):
                del kwargs["attributeType"]

            kwargs[data_type] = attr_type

            return self._add_traced_attr(name, **kwargs)

        return func

    def add_enum(self, name, enum_name="", cases=None, **kwargs):
        """Create an enum-attribute with given name and kwargs.

        Note:
            kwargs are exactly the same as in cmds.addAttr()!

        Args:
            name (str): Name for the new attribute to be created.
            enum_name (list or str): User-choices for the resulting enum-attr.
            cases (list or str): Overrides enum_name, which is a horrific name.
            kwargs (dict): User specified flags to be set for the new attr.

        Returns:
            NcNode: NcNode-instance with the node and new attribute.

        Example:
            ::

                Node("pCube1").add_enum(cases=["A", "B", "C"], value=2)
        """
        if "enumName" not in kwargs.keys():
            if cases is not None:
                enum_name = cases
            if isinstance(enum_name, (list, tuple)):
                enum_name = ":".join(enum_name)
            kwargs["enumName"] = enum_name

        elif isinstance(kwargs["enumName"], (list, tuple)):
            kwargs["enumName"] = ":".join(kwargs["enumName"])

        # Replace user inputs for attributeType. Type is defined implicitly!
        kwargs["attributeType"] = "enum"

        return self._add_traced_attr(name, **kwargs)

    def add_int(self, *args, **kwargs):
        """Create an integer-attribute on the node associated with this NcNode.

        Note:
            This function simply redirects to add_long, but most people will
            probably expect an "int" data type.

        Args:
            args (list): Arguments that will be passed on to add_long()
            kwargs (dict): Key/value pairs that will be passed on to add_long()

        Returns:
            NcNode: NcNode-instance with the node and new attribute.
        """
        return self.add_long(*args, **kwargs)

    def add_separator(
            self,
            name=DEFAULT_SEPARATOR_NAME,
            enum_name=DEFAULT_SEPARATOR_VALUE,
            cases=None,
            **kwargs):
        """Create a separator-attribute.

        Note:
            Default name and enum_name are defined by the globals
            DEFAULT_SEPARATOR_NAME and DEFAULT_SEPARATOR_VALUE!
            kwargs are exactly the same as in cmds.addAttr()!

        Args:
            name (str): Name for the new separator to be created.
            enum_name (list or str): User-choices for the resulting enum-attr.
            cases (list or str): Overrides enum_name, which is a horrific name.
            kwargs (dict): User specified flags to be set for the new attr.

        Returns:
            NcNode: NcNode-instance with the node and new attribute.

        Example:
            ::

                Node("pCube1").add_separator()
        """
        # Find the next available longName for the new separator
        node = self.node
        base_long_name = "channelBoxSeparator"
        index = 1
        unique_long_name = "{0}{1}".format(base_long_name, index)
        while cmds.attributeQuery(unique_long_name, node=node, exists=True):
            index += 1
            unique_long_name = "{0}{1}".format(base_long_name, index)

        separator_attr = self.add_enum(
            unique_long_name,
            enum_name=enum_name,
            cases=cases,
            niceName=name,
            **kwargs
        )

        return separator_attr

    def _add_traced_attr(self, attr_name, **kwargs):
        """Create a Maya-attribute on the Maya-node this NcBaseNode refers to.

        Args:
            attr_name (str): Name of new attribute.
            kwargs (dict): Any user specified flags & their values.
                           Gets combined with values in DEFAULT_ATTR_FLAGS!

        Returns:
            NcNode: NcNode instance with the newly created attribute.
        """
        # Replace spaces in name not to cause Maya-warnings
        attr_name = attr_name.replace(' ', '_')

        # Check whether attribute already exists. If so; return it directly!
        plug = "{0}.{1}".format(self.node, attr_name)
        if cmds.objExists(plug):
            LOG.warn("Attribute %s already existed!", plug)
            return self.__getattr__(attr_name)

        # Make a copy of the default addAttr command flags
        attr_variables = config.DEFAULT_ATTR_FLAGS.copy()
        LOG.debug("Copied default attr_variables: %s", attr_variables)

        # Add the attr variable into the dictionary
        attr_variables["longName"] = attr_name
        # Override default values with kwargs
        attr_variables.update(kwargs)
        LOG.debug("Added custom attr_variables: %s", attr_variables)

        # Extract attributes that need to be set via setAttr-command
        set_attr_values = {
            "channelBox": attr_variables.pop("channelBox", None),
            "lock": attr_variables.pop("lock", None),
        }
        attr_value = attr_variables.pop("value", None)
        LOG.debug("Extracted set_attr-variables: %s", set_attr_values)

        # Add the attribute
        _traced_add_attr(self.node, **attr_variables)

        # Filter for any values that need to be set via the setAttr command.
        set_attr_values = {
            key: val for (key, val) in set_attr_values.iteritems()
            if val is not None
        }
        LOG.debug("Pruned set_attr-variables: %s", set_attr_values)

        # If there is no value to be set; set any attribute flags directly
        if attr_value is None:
            _traced_set_attr(plug, **set_attr_values)
        else:
            # If a value is given; use the set_or_connect function
            _unravel_and_set_or_connect_a_to_b(
                plug, attr_value,
                **set_attr_values
            )

        return NcNode(plug)


# NcNode ---
class NcNode(NcBaseNode):
    """NcNodes are linked to Maya nodes & can hold attrs in a NcAttrs-instance.

    Note:
        Getting attr X from an NcNode that holds attr Y only returns: NcNode.X
        In contrast; NcAttrs instances "concatenate" attrs:
        Getting attr X from an NcAttrs that holds attr Y returns: NcAttrs.Y.X
    """

    def __init__(
            self,
            node,
            attrs=None,
            auto_unravel=None,
            auto_consolidate=None):
        """Initialize NcNode-class instance.

        Note:
            __setattr__ is altered. The usual "self.node=node" results in loop!
            Therefore attributes need to be set a bit awkwardly via __dict__!

            NcNode uses an MObject as its reference to the Maya node it belongs
            to. Maya node MUST therefore exist at instantiation time!

        Args:
            node (str or NcNode or NcAttrs or MObject): Represents a Maya node
            attrs (str or list or NcAttrs): Represents Maya attrs on the node
            auto_unravel (bool): Should attrs be auto-unravelled?
                Check set_global_auto_unravel docString for more details.
            auto_consolidate (bool): Should attrs be auto-consolidated?
                Check set_global_auto_consolidate docString for more details.

        Attributes:
            _node_mobj (MObject): Reference to Maya node.
            _held_attrs (NcAttrs): NcAttrs instance that defines the attrs.

        Raises:
            RuntimeError: If number was given to initialize an NcNode with.
            RuntimeError: If list/tuple was given to initialize an NcNode with.
            RuntimeError: If the given string doesn't seem to represent an
                existing Maya node in the scene.

        Example:
            ::

                a = Node("pCube1")  # Node invokes NcNode instantiation!
                b = Node("pCube2.ty")
                b = Node("pCube3", ["ty", "tz", "tx"])
        """
        LOG.debug(
            "%s __init__ (%s, %s, %s, %s)",
            self.__class__.__name__,
            node, attrs,
            auto_unravel, auto_consolidate
        )

        # Plain values should be Value-instance!
        if isinstance(node, numbers.Real):
            msg = (
                "Explicit NcNode __init__ with number: {0}  "
                "Use Node() instead!".format(node)
            )
            raise RuntimeError(msg)

        # Lists or tuples should be NcList!
        if isinstance(node, (list, tuple)):
            msg = (
                "Explicit NcNode __init__ with list or tuple: {0}  "
                "Use Node() instead!".format(node)
            )
            raise RuntimeError(msg)

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

            # If auto_unravel flag wasn't specified: Use node settings!
            if auto_unravel is None:
                auto_unravel = node._auto_unravel
            # If auto_consolidate flag wasn't specified: Use node settings!
            if auto_consolidate is None:
                auto_consolidate = node._auto_consolidate
        else:
            node_mobj = om_util.get_mobj(node)
            if node_mobj is None:
                msg = (
                    "No Maya node was found for '{0}'! The node might not "
                    "exist or its name might be non-unique.".format(node)
                )
                raise RuntimeError(msg)

        # Using __dict__, because the setattr & getattr methods are overridden!
        self.__dict__["_node_mobj"] = node_mobj
        if isinstance(attrs, NcAttrs):
            self.__dict__["_held_attrs"] = attrs
        else:
            self.__dict__["_held_attrs"] = NcAttrs(self, attrs)

        # If auto_unravel/auto_consolidate flags weren't specified: Use globals
        if auto_unravel is None:
            auto_unravel = GLOBAL_AUTO_UNRAVEL
        if auto_consolidate is None:
            auto_consolidate = GLOBAL_AUTO_CONSOLIDATE
        self.__dict__["_auto_unravel"] = auto_unravel
        self.__dict__["_auto_consolidate"] = auto_consolidate

    def __getattr__(self, name):
        """Get a new NcAttrs instance with the requested attribute.

        Note:
            There are certain keywords that will NOT return a new NcAttrs:

            * attrs: Returns currently stored NcAttrs of this NcNode instance.
            * attrs_list: Returns stored attrs: [attr, ...] (list of strings).
            * node: Returns name of Maya node in scene (str).
            * nodes: Returns name of Maya node in scene in a list ([str]).
            * plugs: Returns stored plugs: [node.attr, ...] (list of strings).

        Args:
            name (str): Name of requested attribute

        Returns:
            NcAttrs: New OR stored instance, if keyword "attrs" was used!

        Example:
            ::

                a = Node("pCube1") # Create new Node-object
                a.tx  # invokes __getattr__ and returns a new Node-object.
                        It's the same as typing Node("a.tx")
        """
        LOG.debug("%s __getattr__ (%s)", self.__class__.__name__, name)

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
            Looks through list of attrs stored in the NcAttrs of this NcNode.

        Args:
            index (int): Index of desired item

        Returns:
            NcNode: New NcNode instance, only with attr at index.
        """
        LOG.debug("%s __getitem__ (%d)", self.__class__.__name__, index)

        return_value = NcNode(
            self._node_mobj,
            self.attrs[index],
            auto_unravel=self._auto_unravel,
            auto_consolidate=self._auto_consolidate
        )

        return return_value

    @property
    def node(self):
        """Get the name of Maya node this NcNode refers to.

        Returns:
            str: Name of Maya node in the scene.
        """
        return om_util.get_dag_path_of_mobj(self._node_mobj)

    @property
    def attrs(self):
        """Get currently stored NcAttrs instance of this NcNode.

        Returns:
            NcAttrs: NcAttrs instance that represents Maya attributes.
        """
        return self._held_attrs

    @property
    def attrs_list(self):
        """Get list of stored attributes of this NcNode instance.

        Returns:
            list: List of strings that represent Maya attributes.
        """
        return self.attrs.attrs_list


# NcAttrs ---
class NcAttrs(NcBaseNode):
    """NcAttrs are linked to an NcNode instance & represent attrs on Maya node.

    Note:
        Getting attr X from an NcAttrs that holds attr Y returns: NcAttrs.Y.X
        In contrast; NcNode instances do NOT "concatenate" attrs:
        Getting attr X from an NcNode that holds attr Y only returns: NcNode.X
    """

    def __init__(self, holder_node, attrs):
        """Initialize NcAttrs-class instance.

        Note:
            __setattr__ is altered. The usual "self.node=node" results in loop!
            Therefore attributes need to be set a bit awkwardly via __dict__!

        Args:
            holder_node (NcNode): Represents a Maya node
            attrs (str or list or NcAttrs): Represents attrs on the Maya node


        Attributes:
            _holder_node (NcNode): NcNode instance this NcAttrs belongs to.
            _held_attrs_list (list): Strings that represent attrs on Maya node.

        Raises:
            TypeError: If the holder_node isn't of type NcNode.
        """
        LOG.debug("%s __init__ (%s)", self.__class__.__name__, attrs)

        super(NcAttrs, self).__init__()

        if not isinstance(holder_node, NcNode):
            msg = (
                "holder_node must be of type NcNode! Given: {0} "
                "type: {1}".format(holder_node, type(holder_node))
            )
            raise TypeError(msg)

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
        """Get name of the Maya node this NcAttrs is linked to.

        Returns:
            str: Name of Maya node in the scene.
        """
        return self._holder_node.node

    @property
    def attrs(self):
        """Get this NcAttrs instance.

        Returns:
            NcAttrs: NcAttrs instance that represents Maya attributes.
        """
        return self

    @property
    def attrs_list(self):
        """Get list of stored attributes of this NcAttrs instance.

        Returns:
            list: List of strings that represent Maya attributes.
        """
        return self._held_attrs_list

    @property
    def _node_mobj(self):
        """Get the MObject this NcAttrs instance refers to.

        Note:
            MObject is stored on the NcNode this NcAttrs instance refers to!

        Returns:
            MObject: MObject instance of Maya node in the scene
        """
        return self._holder_node._node_mobj

    @property
    def _auto_unravel(self):
        """Get _auto_unravel attribute of _holder_node.

        Returns:
            bool: Whether auto unravelling is allowed
        """
        return self._holder_node._auto_unravel

    @property
    def _auto_consolidate(self):
        """Get _auto_consolidate attribute of _holder_node.

        Returns:
            bool: Whether auto consolidating is allowed
        """
        return self._holder_node._auto_consolidate

    def __getattr__(self, name):
        """Get a new NcAttrs instance with the requested attribute.

        Note:
            The requested attr gets "concatenated" onto the existing attr(s)!

            There are certain keywords that will NOT return a new NcAttrs:

            * attrs: Returns this NcAttrs instance (self).
            * attrs_list: Returns stored attrs: [attr, ...] (list of strings).
            * node: Returns name of Maya node in scene (str).
            * nodes: Returns name of Maya node in scene in a list ([str]).
            * plugs: Returns stored plugs: [node.attr, ...] (list of strings).

        Args:
            name (str): Name of requested attribute

        Returns:
            NcAttrs: New NcAttrs instance OR self, if keyword "attrs" was used!

        Example:
            ::

                a = Node("pCube1") # Create new NcNode-object
                a.tx.ty  # invokes __getattr__ on NcNode "a" first, which
                           returns an NcAttrs instance with node: "a" & attrs:
                           "tx". The __getattr__ described here then acts on
                           the retrieved NcAttrs instance and returns a new
                           NcAttrs instance. This time with node: "a" & attrs:
                           "tx.ty"!
        """
        LOG.debug("%s __getattr__ (%s)", self.__class__.__name__, name)

        # Keyword "attrs" is a special case!
        if name == "attrs":
            return self

        if len(self.attrs_list) != 1:
            LOG.warn(
                "__getattr__ of non-singular NcAttr: %s Using first item of "
                "attrs-list %s, which could result in unwanted behaviour!",
                self, self.attrs_list
            )

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
            NcNode: New NcNode instance, solely with attribute at index.
        """
        LOG.debug("%s __getitem__ (%d)", self.__class__.__name__, index)

        return_value = NcAttrs(
            self._holder_node,
            attrs=self.attrs_list[index],
        )

        return return_value


# NcList ---
class NcList(NcBaseClass, list):
    """NcList is a list with overloaded operators (inherited from NcBaseClass).

    Note:
        NcList has the following keywords:

        * nodes: Returns Maya nodes in NcList: [node, ...] (list of strings)

        NcList inherits from list, for things like isinstance(NcList, list).
    """

    def __init__(self, *args):
        """Initialize new NcList-instance.

        Args:
            args (NcNode or NcAttrs or NcValue or str or list or tuple): Any
                number of values that should be stored as an array of values.
        """
        LOG.debug("%s __init__ (%s)", self.__class__.__name__, args)
        super(NcList, self).__init__()

        # If arguments are given as a list: Unpack the items from it
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]

        # Go through given args and cast them to NcNode or NcValue
        list_items = []
        for arg in args:
            converted_arg = self._convert_item_to_nc_instance(arg)
            list_items.append(converted_arg)

        self.__dict__["_items"] = list_items

    def __str__(self):
        """Readable format of NcList instance.

        Note:
            For example invoked by using print(NcList instance) in Maya

        Returns:
            str: String of all NcList _items.
        """
        return "{0}({1})".format(self.__class__.__name__, self._items)

    def __repr__(self):
        """Unambiguous format of NcList instance.

        Note:
            For example invoked by running highlighted NcList instance in Maya

        Returns:
            str: String of concatenated class-type, node and attrs.
        """
        return "{0}({1})".format(self.__class__.__name__, self._items)

    def __setattr__(self, name, value):
        """Set or connect list items to the given value.

        Note:
            Attribute setting works similar to NcNode and NcAttrs instances, in
            order to provide a (hopefully) seamless workflow, whether using
            NcNodes, NcAttrs or NcLists.

        Args:
            name (str): Name of the attribute to be set. "attrs" is keyword!
            value (NcNode or NcAttrs or str or int or float or list or tuple):
                Connect attr to this object or set attr to this value/array

        Example:
            ::

                setattr is invoked by equal-sign. Does NOT work without attr:
                a = Node(["pCube1.ty", "pSphere1.tx"])  # Initialize NcList.
                a.attrs = 7  # Set list items to 7; .ty on first, .tx on second.
                a.tz = 7 # Set the tz-attr on all items in the NcList to 7.
                a = 7  # Does NOT work! It looks like same operation as above,
                         but here Python calls the assignment operation, NOT
                         setattr. The assignment-operation can't be overridden.
        """
        LOG.debug(
            "%s __setattr__ (%s, %s)", self.__class__.__name__, name, value
        )

        if name == "attrs":
            _unravel_and_set_or_connect_a_to_b(self, value)

        else:
            for item in self._items:
                _unravel_and_set_or_connect_a_to_b(NcNode(item, name), value)

    def __getitem__(self, index):
        """Get stored item at given index.

        Note:
            This looks through the _items list of this NcList instance.

        Args:
            index (int): Index of desired item

        Returns:
            NcNode or NcValue: Stored item at index.
        """
        LOG.debug("%s __getitem__ (%d)", self.__class__.__name__, index)

        return self._items[index]

    def __setitem__(self, index, value):
        """Set or connect attribute at index to the given value.

        Note:
            This looks at the _items list of this NcList instance

        Args:
            index (int): Index of item to be set
            value (NcNode or NcAttrs or str or int or float): Set/connect item
                at index to this.
        """
        LOG.debug(
            "%s __setitem__ (%d, %s)", self.__class__.__name__, index, value
        )

        self.__dict__["_items"][index] = value

    def __len__(self):
        """Return the length of the NcList.

        Returns:
            int: Number of items stored in this NcList instance.
        """
        return len(self._items)

    def __delitem__(self, index):
        """Delete the item at the given index from this NcList instance.

        Args:
            index (int): Index of the item to be deleted.
        """
        del self._items[index]

    def __iter__(self):
        """Iterate over items stored in this NcList instance.

        Yields:
            NcNode or NcAttrs or NcValue: Next item in list of attributes.

        Raises:
            StopIteration: If end of NcList._items is reached.
        """
        LOG.debug("%s __iter__ ()", self.__class__.__name__)

        index = 0
        while True:
            try:
                yield self._items[index]
            except IndexError:
                raise StopIteration
            index += 1

    def __reversed__(self):
        """Reverse the list of stored items on this NcList instance.

        Returns:
            NcList: New instance with reversed list of items.
        """
        return NcList(list(reversed(self._items)))

    def __copy__(self):
        """Behavior for copy.copy().

        Returns:
            NcList: Shallow copy of this NcList instance.
        """
        return NcList(copy.copy(self._items))

    def __deepcopy__(self, memo=None):
        """Behavior for copy.deepcopy().

        Args:
            memo (dict): Memo-dictionary to be passed to deepcopy.

        Returns:
            NcList: Deep copy of this NcList instance.
        """
        return NcList(copy.deepcopy(self._items, memo))

    @property
    def node(self):
        """Property to warn user about inappropriate access.

        Note:
            Only NcNode & NcAttrs allow to access their node via node-property.
            Since user might not be aware of creating NcList instance: Give a
            hint that NcList instances have a nodes-property instead.
        """
        LOG.warn(
            "Returned None for invalid node-property request of %s instance: "
            "%s. Did you mean 'nodes'?", self.__class__.__name__, self
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
            list: List of names of Maya nodes stored in this NcList instance.
        """
        return_list = []

        for item in self._items:
            if isinstance(item, (NcBaseNode)):
                # Append node, if it's not a duplicate.
                item_node = item.node
                if item_node not in return_list:
                    # Not using list(set()) to preserve order.
                    return_list.append(item_node)

        return return_list

    def get(self):
        """Get current value of all items within this NcList instance.

        Note:
            NcNode & NcAttrs instances in list are queried.
            NcValues are added to return list unaltered.

        Returns:
            list: List of queried values. Can be list of (int, float, list),
                depending on "queried" attributes!
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
            value (NcNode or NcAttrs or str or int or float): Value to append.
        """
        converted_value = self._convert_item_to_nc_instance(value)
        self.__dict__["_items"].append(converted_value)

    def insert(self, index, value):
        """Insert value to list of items at the given index.

        Note:
            Given value will be converted automatically to appropriate
            NodeCalculator type before being inserted!

        Args:
            index (int): Index at which the value should be inserted.
            value (NcNode or NcAttrs or str or int or float): Value to insert.
        """
        converted_value = self._convert_item_to_nc_instance(value)
        self._items.insert(index, converted_value)

    def extend(self, other):
        """Extend NcList with another list.

        Args:
            other (NcList or list): List to be added to the end of this NcList.
        """
        if isinstance(other, NcList):
            other = other._items
        self._items.extend(other)

    @staticmethod
    def _convert_item_to_nc_instance(item):
        """Convert given item into a NodeCalculator friendly class instance.

        Args:
            item (NcNode or NcAttrs or str or int or float): Item to be
                converted into either an NcNode or an NcValue.

        Returns:
            NcNode or NcValue: Given item in the appropriate format.

        Raises:
            RuntimeError: If the given item cannot be converted into an NcNode
                or NcValue.
        """
        if isinstance(item, (NcBaseNode, nc_value.NcValue)):
            return item

        if isinstance(item, (basestring, numbers.Real)):
            return Node(item)

        msg = "Can't convert {0} to NcList item; unsupported type {1}!".format(
            item, type(item)
        )
        raise RuntimeError(msg)


# SET & CONNECT PLUGS ---
def _unravel_and_set_or_connect_a_to_b(obj_a, obj_b, **kwargs):
    """Set obj_a to value of obj_b OR connect obj_b into obj_a.

    Note:
        Allowed assignments are:
        (1-D stands for 1-dimensional, X-D for multi-dim; 2-D, 3-D, ...)

        > Setting 1-D attribute to a 1-D value/attr
            # pCube1.tx = 7

        > Setting X-D attribute to a 1-D value/attr
            # pCube1.t = 7  # equal to [7]*3

        > Setting X-D attribute to a X-D value/attr
            # pCube1.t = [1, 2, 3]

        > Setting 1-D attribute to a X-D value/attr
            # Error: Ambiguous connection!

        > Setting X-D attribute to a Y-D value/attr
            # Error: Dimension mismatch that can't be resolved!

    Args:
        obj_a (NcNode or NcAttrs or str): Needs to be a plug. Either as a
            NodeCalculator-object or as a string ("node.attr")
        obj_b (NcNode or NcAttrs or int or float or list or tuple or string):
            Can be a numeric value, a list of values or another plug either in
            the form of a NodeCalculator-object or as a string ("node.attr")
        kwargs (dict): Arguments used in _traced_set_attr (~ cmds.setAttr)

    Raises:
        RuntimeError: If trying to connect a multi-dimensional attr into a 1D
            attr. This is an ambiguous connection that can't be resolved.
        RuntimeError: If trying to connect a multi-dimensional attr into a
            multi-dimensional attr with different dimensionality. This is a
            dimension mismatch that can't be resolved!
    """
    LOG.debug("_unravel_and_set_or_connect_a_to_b (%s, %s)", obj_a, obj_b)

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
    # Strings become NcNode instances, parent attributes are split up into
    # their child attributes, etc. This ensures the following
    # setting/connecting can expect the inputs to be in a consistent form.
    obj_a_unravelled_list = _unravel_item_as_list(obj_a)
    obj_b_unravelled_list = _unravel_item_as_list(obj_b)

    # As described in the docString Note: Input dimensions are crucial. If they
    # don't match they must either be matched or an exception must be raised!
    obj_a_dim = len(obj_a_unravelled_list)
    obj_b_dim = len(obj_b_unravelled_list)

    # A multidimensional connection into a 1D attribute does not make sense!
    if obj_a_dim == 1 and obj_b_dim != 1:
        msg = "Ambiguous connection from {0}D to {1}D: ({2}, {3})".format(
            obj_b_dim, obj_a_dim,
            obj_b_unravelled_list, obj_a_unravelled_list
        )
        raise RuntimeError(msg)

    # If obj_a and obj_b are higher dimensional but not the same dimension
    # the connection can't be resolved! 2D -> 3D or 4D -> 2D is ambiguous!
    if obj_a_dim > 1 and obj_b_dim > 1 and obj_a_dim != obj_b_dim:
        msg = (
            "Dimension mismatch for connection that can't be resolved! "
            "From {0}D to {1}D: ({2}, {3})".format(
                obj_b_dim, obj_a_dim,
                obj_b_unravelled_list, obj_a_unravelled_list
            )
        )
        raise RuntimeError(msg)

    # Dimensionality above 3 is most likely not going to be handled reliable!
    if obj_a_dim > 3:
        LOG.warn(
            "obj_a %s is %dD; greater than 3D! Many operations only work "
            "stable up to 3D!", obj_a_unravelled_list, obj_a_dim
        )
    if obj_b_dim > 3:
        LOG.warn(
            "obj_b %s is %dD; greater than 3D! Many operations only work "
            "stable up to 3D!", obj_b_unravelled_list, obj_b_dim
        )

    # Match input-dimensions: Both obj_X_unravelled_list will have the same
    # length, which takes care of 1D to XD setting/connecting.
    if obj_a_dim != obj_b_dim:
        obj_b_unravelled_list = obj_b_unravelled_list * obj_a_dim
        LOG.debug(
            "Matched obj_b_unravelled_list %s dimension to obj_a_dim %d!",
            obj_b_unravelled_list, obj_a_dim
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
    _set_or_connect_a_to_b(
        obj_a_unravelled_list,
        obj_b_unravelled_list,
        **kwargs
    )


def _is_consolidation_allowed(inputs):
    """Check for any NcBaseNode-instance that is NOT set to auto consolidate.

    Args:
        inputs (NcNode or NcAttrs or str or int or float or list or tuple):
            Items to check for a turned off auto-consolidation.

    Returns:
        bool: True, if all given items allow for consolidation.
    """
    LOG.debug("_is_consolidation_allowed (%s)", inputs)

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
        A full set of child attributes can be reduced to their parent attr:
        ["tx", "ty", "tz"] becomes ["t"]

        A 3D to 3D connection can be 1 connection if both plugs have a parent
        attr! However, a 1D attr can not connect to a 3D attr and must NOT be
        consolidated!

    Args:
        plugs (list(NcNode or NcAttrs or str or int or float or list or tuple)):
            Plugs to check.

    Returns:
        list: Consolidated plugs, if consolidation was successful.
            Otherwise given inputs are returned unaltered.
    """
    LOG.debug("_consolidate_plugs_to_min_dimension (%s)", plugs)

    parent_plugs = []
    for plug in plugs:
        parent_plug = _check_for_parent_attribute(plug)

        # If any plug doesn't have a parent the plugs can NOT be consolidated!
        if parent_plug is None:
            # Return early!
            return plugs

        parent_plugs.append([parent_plug])

    # If all given plugs have a parent plug: Return them as a list of lists.
    return parent_plugs


def _check_for_parent_attribute(plug_list):
    """Reduce the given list of plugs to a single parent attribute.

    Args:
        plug_list (list): List of plugs: ["node.attribute", ...]

    Returns:
        MPlug or None: If parent attribute was found it
            is returned as an MPlug instance, otherwise None is returned
    """
    LOG.debug("_check_for_parent_attribute (%s)", plug_list)

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
        # If any subsequent potential_parent_attr is different to existing..
        elif potential_parent_mplug != parent_mplug:
            # ..return early, because it won't be possible to reduce this plug!
            return None

        # If the plug passed all previous tests: Add it to the list
        checked_mplugs.append(mplug)

    # Given plug_list should not be reduced if the list of all checked attrs
    # does not match the full list of available children attributes exactly!
    # -> [outputX] should not be reduced to [output]; Y & Z are missing!
    # -> [outputX, outputX, outputZ] should not be reduced; it has duplicates!
    # -> [outputX, outputZ, outputY] should not be reduced; wrong attr-order!
    all_child_mplugs = om_util.get_child_mplugs(potential_parent_mplug)
    zipped_lists = itertools.izip_longest(checked_mplugs, all_child_mplugs)
    for checked_mplug, child_mplug in zipped_lists:
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
        bool: Returns False, if setting/connecting was not possible.

    Raises:
        RuntimeError: If an item of the obj_a_list isn't a Maya attribute.
        RuntimeError: If an item of the obj_b_list can't be set/connected due
            to unsupported type.
    """
    LOG.debug(
        "_set_or_connect_a_to_b (%s, %s, %s)", obj_a_list, obj_b_list, kwargs
    )

    for obj_a_item, obj_b_item in zip(obj_a_list, obj_b_list):
        # Make sure obj_a_item exists in the Maya scene
        if not cmds.objExists(obj_a_item):
            msg = "obj_a_item doesn't seem to be a Maya attr: {0}!".format(
                obj_a_item
            )
            raise RuntimeError(msg)

        # If obj_b_item is a simple number...
        if isinstance(obj_b_item, numbers.Real):
            # ...set 1-D obj_a_item to 1-D obj_b_item-value.
            _traced_set_attr(obj_a_item, obj_b_item, **kwargs)

        # If obj_b_item is a valid attribute in the Maya scene...
        elif isinstance(obj_b_item, OpenMaya.MPlug) or _is_valid_maya_attr(obj_b_item):
            #  ...connect it.
            _traced_connect_attr(obj_b_item, obj_a_item)

        # If obj_b_item didn't match anything; obj_b_item-type isn't supported.
        else:
            msg = (
                "Cannot set obj_b_item: {0} because it is of unsupported "
                "type: {1}".format(obj_b_item, type(obj_b_item))
            )
            raise RuntimeError(msg)


def _is_valid_maya_attr(plug):
    """Check if given plug is of an existing Maya attribute.

    Args:
        plug (str): String of a Maya plug in the scene (node.attr).

    Returns:
        bool: Whether the given plug is an existing plug in the scene.
    """
    LOG.debug("_is_valid_maya_attr (%s)", plug)

    split_plug = _split_plug_into_node_and_attr(plug)
    if split_plug:
        is_existing_maya_plug = cmds.attributeQuery(
            split_plug[1],
            node=split_plug[0],
            exists=True
        )
        return is_existing_maya_plug

    LOG.debug("Given string '%s' does not seem to be a Maya attribute!", plug)
    return False


# CREATE, CONNECT AND SETUP NODE ---
def _create_operation_node(operation, *args):
    """Create & connect adequately named Maya nodes for the given operation.

    Args:
        operation (str): Operation the new node has to perform
        args (NcNode or NcAttrs or str): Attrs connecting into created node

    Returns:
        NcNode or NcList: Either new NcNode instance with the newly created
            Maya-node of type OPERATORS[operation]["node"] and with
            attributes stored in OPERATORS[operation]["outputs"].
            If the outputs are multidimensional (for example "translateXYZ" &
            "rotateXYZ") a new NcList instance is returned with NcNodes for
            each of the outputs.
    """
    LOG.debug("Creating a new %s-operationNode with args: %s", operation, args)

    # Unravel all given args to unify how they are passed on.
    unravelled_args_list = [_unravel_item_as_list(arg) for arg in args]

    # Create a named node of appropriate type for the given operation.
    new_node = _create_traced_operation_node(operation, unravelled_args_list)

    # Determine the necessary inputs for this node type and args combination.
    clean_inputs, clean_args, max_array_len, max_axis_len = _get_node_inputs(
        operation, new_node, unravelled_args_list
    )

    # Set operation attr if specified in OPERATORS for this node-type
    node_operation = OPERATORS[operation].get("operation", None)
    if node_operation is not None:
        _unravel_and_set_or_connect_a_to_b(
            "{0}.operation".format(new_node), node_operation
        )
    # Set or connect all node inputs to the given, unravelled args.
    for args_list, inputs_list in zip(clean_args, clean_inputs):
        for arg_element, input_element in zip(args_list, inputs_list):
            _unravel_and_set_or_connect_a_to_b(input_element, arg_element)

    # Determine the necessary outputs for this node and args combination.
    output_nodes = _get_node_outputs(
        operation, new_node, max_array_len, max_axis_len
    )

    # For manifold outputs: Return an NcList of NcNodes; one for each output.
    if len(output_nodes) > 1:
        return NcList(output_nodes)
    # Usually outputs are singular; one (parent)plug. Return a single NcNode.
    return output_nodes[0]


def _get_node_inputs(operation, new_node, args_list):
    """Get node-inputs based on operation-type and involved arguments.

    Note:
        To anyone delving deep enough into the NodeCalculator to reach this
        point; I apologize. This function in particular is difficult to grasp.
        The main idea is to find which node-inputs (defined in the OPERATORS-
        dictionary) are needed for the given args. Dealing with array-inputs
        and often 3D-inputs is the difficult part. I hope the following
        explanation will make it easier to understand what is happening.

        Within this function we deal a lot with different levels of arguments:

        args_list (list)
          > arg_element (list)
              > arg_item (list or MPlug/value/...)
                  > arg_axis (MPlug/value/...)

        The arg_item-level might seem redundant. The reason for its existence
        are array-input attributes (input[0], etc.). They need to be a list of
        items under one arg_element. That way one can loop over all array-input
        arg_items in an arg_element and get the correct indices, even if there
        is a mix of non-array input attrs and array-input attrs. Without this
        extra layer an input before the array-input would throw off the indices
        by 1!


        The ARGS_LIST is made up of the various arguments that will connect
        into the node.

          > [array-values, translation-values, rotation-values, ...]

        The ARG_ELEMENT is what will set/connect into an attribute "section"
        of a node. For array-inputs THIS is what matters(!), because one
        attribute section (input[{array}]) will actually be made up of
        many inputs.

          > [array-values]

        The ARG_ITEM is one particular arg_element. For arg_elements that are
        array-input the arg_item is a specific input of a array-input. For
        non-array-inputs the arg_elements & the arg_item are equivalent!

          > [array-input-value[0]]

        The ARG_AXIS is the most granular item, referring to a particular Maya
        node attribute.

          > [array-value[0].valueX]

    Args:
        operation (str): Operation the new node has to perform.
        new_node (str): Name of newly created Maya node.
        args_list (NcNode or NcAttrs or NcValue): Attrs/Values the node attrs
            will be connected/set to.

    Raises:
        RuntimeError: If trying to connect a multi-dimensional attr into a 1D
            attr. This is an ambiguous connection that can't be resolved.

    Returns:
        tuple: (clean_inputs_list, clean_args_list, max_arg_element_len, max_arg_axis_len)
            > clean_inputs_list holds all necessary node inputs for given args.
            > clean_args_list holds args that were adjusted to match clean_inputs_list.
            > max_arg_element_len holds the highest dimension of array attrs.
            > max_arg_axis_len holds highest number of attribute axis involved.

    Example:
        ::

            These are examples of how the different "levels" of the args_list look
            like, described in the Note-section. Notice how the args_list is made
            up of arg_elements, which are made up of arg_items, which in turn are
            composed of arg_axis.


            args_list = [
                [
                    [<OpenMaya.MPlug X>, <OpenMaya.MPlug Y>, <OpenMaya.MPlug Z>],
                    <OpenMaya.MPlug A>,
                    2
                ]
            ]


            # Note: This example would be for an array-input attribute of a node!
            arg_elements = [
                [<OpenMaya.MPlug X>, <OpenMaya.MPlug Y>, <OpenMaya.MPlug Z>],
                <OpenMaya.MPlug A>,
                2
            ]


            arg_item = [<OpenMaya.MPlug X>, <OpenMaya.MPlug Y>, <OpenMaya.MPlug Z>]


            arg_axis = <OpenMaya.MPlug X>
    """
    inputs_list = OPERATORS[operation]["inputs"]
    LOG.debug(
        "_get_node_inputs with args_list %s & inputs_list %s",
        args_list,
        inputs_list
    )

    # Check that dimensions match: args must be of same length as inputs:
    if len(args_list) != len(inputs_list):
        LOG.error(
            "Dimensions to create node don't match! Given args_list: %s "
            "Expected inputs_list: %s", args_list, inputs_list
        )

    # Go through all given args for the node creation and determine the
    # necessary node inputs based on these args.
    max_arg_element_len = None
    adjusted_args_list = []
    adjusted_inputs_list = []
    for arg_element, input_element in zip(args_list, inputs_list):
        # Check if the current input_element is an array-input
        is_array_element = False
        for input_axis in input_element:
            if input_axis and "{array}" in input_axis:
                is_array_element = True
                break

        if is_array_element:
            LOG.debug("Expecting %s to be for array input!", arg_element)
            # If the current input_element is an array, it must be multiplied
            # in order to match the input_element to the arg_element!
            num_arg_items = len(arg_element)
            if num_arg_items > max_arg_element_len:
                max_arg_element_len = num_arg_items

            # Add array-inputs to input element, equal to the number of args.
            input_items = []
            for _ in range(num_arg_items):
                input_items.append(input_element)
            adjusted_inputs_list.append(input_items)

            # Take the one arg_element and split its content into arg_items.
            arg_items = []
            for arg_item in arg_element:
                if not isinstance(arg_item, (tuple, list)):
                    arg_item = [arg_item]
                arg_items.append(arg_item)
            adjusted_args_list.append(arg_items)

        else:
            LOG.debug("Expecting %s to be for single input!", arg_element)
            # For a non-array input_item the input_element simply is
            # the input_element wrapped inside a list. The arg_element must
            # be wrapped into a list, too to match the two!
            adjusted_args_list.append([arg_element])
            adjusted_inputs_list.append([input_element])

    LOG.debug(
        "_get_node_inputs with adjusted_args_list %s & adjusted_inputs_list %s",
        adjusted_args_list,
        adjusted_inputs_list
    )

    # Find the maximum dimension involved to know what to connect. For example:
    # 1D to 1D needs 1D-input
    # 1D to 2D needs 2D-input  # "1D" is not a typo! ;)
    # 3D to 3D needs 3D-input
    max_dim = 0
    for adjusted_arg_element in zip(*adjusted_args_list):
        max_element_dim = max([len(x) for x in adjusted_arg_element])
        if max_element_dim > max_dim:
            max_dim = max_element_dim

    max_arg_axis_len = 0
    clean_inputs_list = []
    clean_args_list = []
    for arg_element, input_element in zip(adjusted_args_list, adjusted_inputs_list):
        # Concatenate the input axis with their node
        formatted_input_element = []
        for index, input_item in enumerate(input_element):
            formatted_input_item = []
            for axis in input_item:
                formatted_axis = axis.format(array=index)
                formatted_plug = "{0}.{1}".format(new_node, formatted_axis)
                formatted_input_item.append(formatted_plug)
            formatted_input_element.append(formatted_input_item)

        # Prune node inputs to what is necessary for given args.
        pruned_input_element = []
        pruned_arg_element = []
        for arg_item, formatted_input_item in zip(arg_element, formatted_input_element):
            # Unify the arg_item(s): Should always be a list!
            if not isinstance(arg_item, (tuple, list)):
                arg_item = [arg_item]

            # Prevent an ambiguous connection from a multi-arg into a 1D input!
            num_arg_axis = len(arg_item)
            if num_arg_axis > 1 and len(formatted_input_item) == 1:
                msg = (
                    "Unable to connect multi-dimensional args {0} to 1D input "
                    "{1}.{2}".format(arg_item, new_node, formatted_input_item)
                )
                raise RuntimeError(msg)

            # A single axis arg_item can connect into a multi-dimensional input.
            if num_arg_axis == 1 and len(formatted_input_item) > 1:
                num_arg_axis = max_dim
                arg_item = arg_item * num_arg_axis

            # Prune the amount of input-axis to the number of arg-axis.
            pruned_input_item = formatted_input_item[:num_arg_axis]
            pruned_input_element.append(pruned_input_item)
            pruned_arg_element.append(arg_item)

            # Find the maximum amount of used axis for all involved plugs.
            # This will determine how many output-axis are passed on!
            if num_arg_axis > max_arg_axis_len:
                max_arg_axis_len = num_arg_axis

        clean_inputs_list.append(pruned_input_element)
        clean_args_list.append(pruned_arg_element)

    LOG.debug(
        "_get_node_inputs with clean_inputs_list %s & clean_args_list %s",
        clean_inputs_list,
        clean_args_list
    )

    return_val = (
        clean_inputs_list,
        clean_args_list,
        max_arg_element_len,
        max_arg_axis_len
    )
    return return_val


def _get_node_outputs(operation, new_node, max_array_len, max_axis_len):
    """Get node-outputs based on operation-type and involved arguments.

    Note:
        See docString of _get_node_inputs for origin of max_array_len and
        max_axis_len, as well as what output_element or output_axis means.

    Args:
        operation (str): Operation the new node has to perform.
        new_node (str): Name of newly created Maya node.
        max_array_len (int or None): Highest dimension of arrays.
        max_axis_len (int): Highest dimension of attribute axis.

    Returns:
        list: List of NcNode instances that hold an attribute according to the
            outputs defined in the OPERATORS dictionary.
    """
    # Get the outputs for the created node, defined in OPERATORS dictionary.
    outputs = OPERATORS[operation]["outputs"]

    # Determine whether this is an array-output node.
    is_array = False
    for output_element in outputs:
        for output_axis in output_element:
            if output_axis and "{array}" in output_axis:
                is_array = True
                break

    # If this node type has an array-output...
    if is_array:
        if max_array_len is None:
            max_array_len = 1

        # ...expand the output-list to the number of array-input arguments.
        expanded_node_outputs = max_array_len * outputs

        # For each output: Add the index to all axis of the output attributes.
        new_node_outputs = []
        for index, output in enumerate(expanded_node_outputs):
            new_node_outputs.append(
                [axis.format(array=index) for axis in output]
            )
        outputs = new_node_outputs

    # The "output_is_predetermined" flag in the OPERATORS dictionary allows for
    # outputs that are nonsensical if not their full list is returned, EVEN if
    # only a partial number of inputs is given. For example:
    # A quaternion only makes sense as a 4D entity, even if (for whatever
    # reason) only a 1D, 2D or 3D input was given.
    output_is_predetermined = OPERATORS[operation].get(
        "output_is_predetermined", False
    )

    # Create a new NcNode instance for all necessary outputs.
    output_nodes = []
    for output in outputs:
        if len(output) == 1 or output_is_predetermined:
            # Return outputs directly if they should not be altered or are 1D
            node = NcNode(new_node, output)
        else:
            # Truncate number of outputs based on how many attrs were processed
            node = NcNode(new_node, output[:max_axis_len])

        output_nodes.append(node)

    return output_nodes


def _create_node_name(operation, *args):
    """Create a procedural Maya node name that is as descriptive as possible.

    Args:
        operation (str): Operation the new node has to perform
        args (MPlug or NcNode or NcAttrs or list or numbers or str): Attributes
            connecting into the newly created node.

    Returns:
        str: Generated name for the given node operation and args.
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
            # If it's a list of 1 item; use that item, otherwise use "list"
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

    # Remove invalid characters from args, to prevent Maya warning message.
    involved_args = [re.sub('[^\w_]*', '', arg) for arg in involved_args]

    # Combine all name-elements
    name_elements = [
        NODE_PREFIX,  # Common NodeCalculator-prefix
        operation.upper(),  # Operation type
        "_".join(involved_args),  # Involved args
        OPERATORS[operation]["node"]  # Node type
    ]
    # Filter out elements that are None or empty strings.
    name = "_".join([element for element in name_elements if element])

    return name


def _create_traced_operation_node(operation, attrs):
    """Create named Maya node for the given operation & add cmds to
    _command_stack if Tracer is active.

    Args:
        operation (str): Operation the new node has to perform
        attrs (MPlug or NcNode or NcAttrs or list or numbers or str): Attrs
            that will be connecting into the newly created node.

    Returns:
        str: Name of newly created Maya node.
    """
    node_type = OPERATORS[operation]["node"]
    node_name = _create_node_name(operation, attrs)
    new_node = _traced_create_node(node_type, name=node_name)

    return new_node


def _traced_create_node(node_type, **kwargs):
    """Create a Maya node and add it to the _traced_nodes if Tracer is active.

    Note:
        This is simply an overloaded cmds.createNode(node_type, \**kwargs). It
        includes the cmds.parent-command if parenting flags are given.

        If Tracer is active: Created nodes are associated with a variable.
        If they are referred to later on in the NodeCalculator statement, the
        variable name will be used instead of their node-name.

    Args:
        node_type (str): Type of the Maya node that should be created.
        kwargs (dict): cmds.createNode & cmds.parent flags

    Returns:
        str: Name of newly created Maya node.
    """
    # Make sure a sensible name is in the kwargs
    name = kwargs.pop("name", node_type)

    # Separate parent command flags from the createNode/spaceLocator kwargs.
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
            "The 's'-flag was used for creation of %s. Please use 'shared' "
            "or 'shape' flag to avoid ambiguity! Used 's' for 'shape' "
            "in cmds.parent command!", node_type
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
        # Add the newly created node to Tracer. Use mobj to avoid ambiguity
        node_variable = NcBaseClass._get_next_variable_name()
        tracer_mobj = tracer.TracerMObject(new_node, node_variable)
        NcBaseClass._add_to_traced_nodes(tracer_mobj)

        # Add the node createNode command to the command stack
        if not new_node_is_shape:
            # Add the name-kwarg back in, if the new node isn't a shape
            kwargs["name"] = name

        if kwargs:
            joined_kwargs = ", {0}".format(_join_cmds_kwargs(**kwargs))
        else:
            joined_kwargs = ""
        command = [
            "{var} = cmds.createNode('{op}'{kwargs})".format(
                var=node_variable,
                op=node_type,
                kwargs=joined_kwargs
            )
        ]

        # If shape was created:
        # Add getting its parent and renaming it to command stack.
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
                joined_parent_kwargs = ", {0}".format(joined_parent_kwargs)
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
    """Add attr to Maya node & add cmds to _command_stack if Tracer is active.

    Note:
        This is simply an overloaded cmds.addAttr(node, \**kwargs).

    Args:
        node (str): Maya node the attribute should be added to.
        kwargs (dict): cmds.addAttr-flags
    """
    cmds.addAttr(node, **kwargs)

    # If commands are traced...
    if NcBaseClass._is_tracing:

        # If node is already part of the traced nodes: Use its variable instead
        node_variable = NcBaseClass._get_tracer_variable_for_node(node)
        node = node_variable if node_variable else "'{0}'".format(node)

        # Join any given kwargs so they can be passed on to the addAttr-command
        joined_kwargs = _join_cmds_kwargs(**kwargs)

        # Add the addAttr-command to the command stack
        cmd_str = "cmds.addAttr({0}, {1})".format(node, joined_kwargs)
        NcBaseClass._add_to_command_stack(cmd_str)


def _traced_set_attr(plug, value=None, **kwargs):
    """Set attr on Maya node & add cmds to _command_stack if Tracer is active.

    Note:
        This is simply an overloaded cmds.setAttr(plug, value, \**kwargs).

    Args:
        plug (MPlug or str): Plug of a Maya node that should be set.
        value (list or numbers or bool): Value the given plug should be set to.
        kwargs (dict): cmds.setAttr-flags
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
            # ...if it is a traced node: Use its variable instead
            plug = "{0} + '.{1}'".format(node_variable, attr)
        else:
            # ...otherwise add quotes around original attr
            plug = "'{0}'".format(plug)

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
                    "cmds.setAttr({0}, {1}{2}, edit=True, {3})".format(
                        plug,
                        unpack_operator,
                        value,
                        joined_kwargs,
                    )
                )
            else:
                # If only a value was given
                cmd_str = "cmds.setAttr({0}, {1}{2})".format(
                    plug,
                    unpack_operator,
                    value
                )
                NcBaseClass._add_to_command_stack(cmd_str)
        else:
            if joined_kwargs:
                # If only kwargs were given
                cmd_str = "cmds.setAttr({0}, edit=True, {1})".format(
                    plug,
                    joined_kwargs
                )
                NcBaseClass._add_to_command_stack(cmd_str)

            # If neither value or kwargs were given it was a redundant setAttr.


def _traced_get_attr(plug):
    """Get attr of Maya node & add cmds to _command_stack if Tracer is active.

    Note:
        This is a tweaked & overloaded cmds.getAttr(plug): Awkward return
        values of 3D-attrs are converted from tuple(list()) to a simple list().

    Args:
        plug (MPlug or str): Plug of Maya node, whose value should be queried.

    Returns:
        list or numbers or bool or str: Queried value of Maya node plug.
    """
    # Variable to keep track of whether return value had to be unpacked or not
    list_of_tuples_returned = False

    if _is_valid_maya_attr(plug):
        return_value = cmds.getAttr(plug)
        # getAttr of 3D-plug returns list of tuple. This fixes that abomination
        if isinstance(return_value, list):
            if len(return_value) == 1 and isinstance(return_value[0], tuple):
                list_of_tuples_returned = True
                return_value = list(return_value[0])
    else:
        return_value = plug

    if NcBaseClass._is_tracing:
        value_name = NcBaseClass._get_next_value_name()

        return_value = nc_value.value(
            return_value,
            metadata=value_name,
            created_by_user=False
        )

        NcBaseClass._add_to_traced_values(return_value)

        # ...look for the node of the given attribute...
        node, attr = _split_plug_into_node_and_attr(plug)
        node_variable = NcBaseClass._get_tracer_variable_for_node(node)
        if node_variable:
            # ...if it is already a traced node: Use its variable instead
            plug = "{0} + '.{1}'".format(node_variable, attr)
        else:
            # ...otherwise add quotes around original plug
            plug = "'{0}'".format(plug)

        # Add the getAttr-command to the command stack
        if list_of_tuples_returned:
            cmd_str = "{0} = list(cmds.getAttr({1})[0])".format(value_name, plug)
            NcBaseClass._add_to_command_stack(cmd_str)
        else:
            cmd_str = "{0} = cmds.getAttr({1})".format(value_name, plug)
            NcBaseClass._add_to_command_stack(cmd_str)

    return return_value


def _join_cmds_kwargs(**kwargs):
    """Concatenates Maya command kwargs for Tracer.

    Args:
        kwargs (dict): Key/value-pairs that should be converted to a string.

    Returns:
        str: String of kwargs&values for the command in the Tracer-stack.
    """
    prepared_kwargs = []

    for key, val in kwargs.iteritems():
        # Add quotes around values that are strings
        if isinstance(val, basestring):
            prepared_kwargs.append("{0}='{1}'".format(key, val))
        else:
            prepared_kwargs.append("{0}={1}".format(key, val))

    joined_kwargs = ", ".join(prepared_kwargs)

    return joined_kwargs


def _traced_connect_attr(plug_a, plug_b):
    """Connect 2 plugs & add command to _command_stack if Tracer is active.

    Note:
        This is cmds.connectAttr(plug_a, plug_b, force=True) with Tracer-stuff.

    Args:
        plug_a (MPlug or str): Source plug
        plug_b (MPlug or str): Destination plug
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
                # ..if it is already a traced node: Use its variable instead...
                formatted_attr = "{0} + '.{1}'".format(node_variable, attr)
            # ...otherwise make sure it's stored as a string
            else:
                formatted_attr = "'{0}'".format(plug)
            formatted_args.append(formatted_attr)

        # Add the connectAttr-command to the command stack
        cmd_str = "cmds.connectAttr({0}, {1}, force=True)".format(
            *formatted_args
        )
        NcBaseClass._add_to_command_stack(cmd_str)


# UNRAVELLING INPUTS ---
def _unravel_item_as_list(item):
    """Convert input into clean list of values or MPlugs.

    Args:
        item (NcNode or NcAttrs or NcList or int or float or list or str):
            input to be unravelled and returned as list.

    Returns:
        list: List consistent of values or MPlugs
    """
    LOG.debug("_unravel_item_as_list (%s)", item)

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
        item (MPlug, NcList or NcNode or NcAttrs or NcValue or list or tuple or
            str or numbers): input to be unravelled/cleaned.

    Returns:
        MPlug or NcValue or int or float or list: MPlug or value

    Raises:
        TypeError: If given item is of an unsupported type.
    """
    LOG.debug("_unravel_item (%s)", item)

    if isinstance(item, OpenMaya.MPlug):
        return item

    if isinstance(item, NcList):
        return _unravel_nc_list(item)

    if isinstance(item, NcBaseNode):
        return _unravel_base_node_instance(item)

    if isinstance(item, (list, tuple)):
        return _unravel_list(item)

    if isinstance(item, basestring):
        return _unravel_str(item)

    if isinstance(item, numbers.Real):
        return item

    msg = (
        "_unravel_item can't unravel {0} of type {1}".format(item, type(item))
    )
    raise TypeError(msg)


def _unravel_nc_list(nc_list):
    """Unravel NcList instance; get value or MPlug of its NcList-items.

    Args:
        nc_list (NcList): NcList to be unravelled.

    Returns:
        list: List of unravelled NcList-items.
    """
    LOG.debug("_unravel_nc_list (%s)", nc_list)

    # An NcList is basically just a list; redirect to _unravel_list
    return _unravel_list(nc_list._items)


def _unravel_list(list_instance):
    """Unravel list instance; get value or MPlug of its items.

    Args:
        list_instance (list or tuple): list to be unravelled.

    Returns:
        list: List of unravelled items.
    """
    LOG.debug("_unravel_list (%s)", list_instance)

    unravelled_list = []

    for item in list_instance:
        unravelled_item = _unravel_item(item)
        unravelled_list.append(unravelled_item)

    return unravelled_list


def _unravel_base_node_instance(base_node_instance):
    """Unravel NcBaseNode instance.

    Get name of Maya node or MPlug of Maya attribute the NcBaseNode refers to.

    Args:
        base_node_instance (NcNode or NcAttrs): Instance to find Mplug for.

    Returns:
        MPlug or str: MPlug of the Maya attribute the given NcNode/NcAttrs
            refers to or name of node, if no attrs are defined.
    """
    LOG.debug("_unravel_base_node_instance (%s)", base_node_instance)

    # If no attrs are specified on the given NcNode/NcAttrs: return node name
    if not base_node_instance.attrs_list:
        return_value = base_node_instance.node
    # If a single attribute is defined; try to unravel it into child attributes
    elif len(base_node_instance.attrs_list) == 1:
        # If unravelling is allowed: Try to unravel plug...
        if GLOBAL_AUTO_UNRAVEL and base_node_instance._auto_unravel:
            return_value = _unravel_plug(
                base_node_instance.node,
                base_node_instance.attrs_list[0]
            )
        # ...otherwise get MPlug of given attribute directly.
        else:
            return_value = om_util.get_mplug_of_node_and_attr(
                base_node_instance.node,
                base_node_instance.attrs_list[0]
            )
    # If multiple attributes are defined; Return list of unravelled plugs
    else:
        return_value = []
        for attr in base_node_instance.attrs_list:
            return_value.append(_unravel_plug(base_node_instance.node, attr))

    return return_value


def _unravel_str(str_instance):
    """Convert name of a Maya plug into an MPlug.

    Args:
        str_instance (str): Name of the plug; "node.attr"

    Returns:
        MPlug or None: MPlug of the Maya attribute, None if given
            string doesn't refer to a valid Maya plug in the scene.
    """
    LOG.debug("_unravel_str (%s)", str_instance)

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
        MPlug or list: MPlug of the Maya attribute, list of MPlugs
            if a parent attribute was unravelled to its child attributes.
    """
    LOG.debug("_unravel_plug (%s, %s)", node, attr)

    return_value = om_util.get_mplug_of_node_and_attr(node, attr)

    # Try to unravel the found MPlug into child attributes
    child_plugs = om_util.get_child_mplugs(return_value)
    if child_plugs:
        return_value = [child_plug for child_plug in child_plugs]

    return return_value


def _split_plug_into_node_and_attr(plug):
    """Split given plug into its node and attribute part.

    Args:
        plug (MPlug or str): Plug of a Maya node/attribute combination.

    Returns:
        tuple or None: Strings of separated node and attribute part or None if
            separation was not possible.

    Raises:
        RuntimeError: If the given plug could not be split into node & attr.
    """
    if isinstance(plug, OpenMaya.MPlug):
        plug = str(plug)

    if isinstance(plug, basestring) and "." in plug:
        node, attr = plug.split(".", 1)
        return (node, attr)

    msg = "Could not split given plug {0} into node & attr parts!".format(plug)
    raise RuntimeError(msg)


# Python functions ---
def _format_docstring(*args, **kwargs):
    """Format docString of a function: Substitute placeholders with (kw)args.

    Note:
        Formatting your docString directly won't work! It won't be a string
        literal anymore and Python won't consider it a docString! Replacing
        the docString (.__doc__) via this closure circumvents this issue.

    Args:
        args (list): Arguments for the string formatting: .format()
        kwargs (list): Keyword arguments for the string formatting: .format()

    Returns:
        executable: The function with formatted docString.
    """
    def func(obj):
        obj.__doc__ = obj.__doc__.format(*args, **kwargs)
        return obj
    return func


# Tracer ---
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

    def __init__(
            self,
            trace=True,
            print_trace=False,
            pprint_trace=False,
            cheers_love=False):
        """Tracer-class constructor.

        Args:
            trace (bool): Enables/disables tracing.
            print_trace (bool): Print command stack as a list.
            pprint_trace (bool): Print command stack as a multi-line string.
            cheers_love (bool): ;)
        """
        self.trace = trace
        self.print_trace = print_trace
        self.pprint_trace = pprint_trace
        self.cheers_love = cheers_love

    def __enter__(self):
        """Set up NcBaseClass class-variables for tracing.

        Note:
            The returned variable is what X in "with noca.Tracer() as X" will
            be.

        Returns:
            list: List of all executed commands.
        """
        NcBaseClass._is_tracing = bool(self.trace)

        NcBaseClass._initialize_trace_variables()

        return NcBaseClass._executed_commands_stack

    def __exit__(self, exc_type, value, traceback):
        """Print executed commands at the end of the with-statement."""
        # Tell user if he/she wants to print results but they were not traced!
        output_desired = self.print_trace or self.pprint_trace or self.cheers_love
        if not self.trace and output_desired:
            LOG.warn("NodeCalculator commands were not traced!")

        # Print executed commands as list
        if self.print_trace:
            print(
                "NodeCalculator command-stack:",
                NcBaseClass._executed_commands_stack
            )

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


# NodeCalculator Extensions ---
def __load_extensions():
    """Import the potential NodeCalculator extensions."""

    # Make sure extensions that aren't local can be imported.
    if config.EXTENSION_PATH and config.EXTENSION_PATH not in sys.path:
        sys.path.insert(0, config.EXTENSION_PATH)

    try:
        # Without a given EXTENSION_PATH a relative import is required!
        if not config.EXTENSION_PATH or not config.EXTENSION_NAMES:
            raise ImportError
        # Try to load extensions via specific path first...
        for extension_name in config.EXTENSION_NAMES:
            noca_extension = __import__(extension_name)

            __load_extension(noca_extension)

        LOG.info(
            "NodeCalculator loaded with extension(s) %s from path %s!",
            config.EXTENSION_NAMES, config.EXTENSION_PATH
        )

    except ImportError:
        try:
            if not config.EXTENSION_NAMES:
                raise ImportError
            # ...otherwise: Look for them in the NodeCalculator module itself.

            for extension_name in config.EXTENSION_NAMES:
                noca_extension = __import__(
                    extension_name,
                    globals(),
                    locals(),
                    [],
                    level=1
                )

                __load_extension(noca_extension)

            LOG.info(
                "NodeCalculator loaded with local extension(s) %s!",
                config.EXTENSION_NAMES
            )

        except ImportError:
            LOG.info("NodeCalculator loaded without extensions!")


def __load_extension(noca_extension):
    """Load the given extension in the correct way for the NodeCalculator.

    Note:
        Check the tutorials and example extension files to see how you can
        create your own extensions.

    Args:
        noca_extension (module): Extension Python module to be loaded.
    """
    # Reloading makes sure the Operators are added to the Op class.
    reload(noca_extension)

    # Load the required plugins
    try:
        for required_plugin in noca_extension.REQUIRED_EXTENSION_PLUGINS:
            cmds.loadPlugin(required_plugin, quiet=True)
    except AttributeError:
        LOG.warning(
            "REQUIRED_EXTENSION_PLUGINS list not found in extension %s!",
            noca_extension.__name__.split(".")[-1]
        )

    # Fill the OPERATORS dictionary with the extension-data.
    try:
        OPERATORS.update(noca_extension.EXTENSION_OPERATORS)
    except AttributeError:
        LOG.warning(
            "EXTENSION_OPERATORS dictionary not found in extension! %s!",
            noca_extension.__name__.split(".")[-1]
        )


# Until I find a better solution, this function call MUST remain at the end
# of this module, due to its cyclical imports. If the extension Operators are
# loaded at the beginning, they will be overridden by the Op-class init!
__load_extensions()
