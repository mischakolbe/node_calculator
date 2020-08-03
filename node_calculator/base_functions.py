"""Basic NodeCalculator functions.

This is an extension that is loaded by default.

The main difference to the base_operators is that functions rely on operators!
They combine existing operators to create more complex setups.
"""
from node_calculator.core import noca_op
from node_calculator.core import Op

# Any Maya plugin that should be loaded for the NodeCalculator
REQUIRED_EXTENSION_PLUGINS = []


# Dict of all available operations: used node-type, inputs, outputs, etc.
EXTENSION_OPERATORS = {}


@noca_op
def soft_approach(attr_a, fade_in_range=0.5, target_value=1):
    """Follow attr_a, but approach the target_value slowly.

    Note:
        Only works for 1D inputs!

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Value or attr
        fade_in_range (NcNode or NcAttrs or str or int or float): Value or
            attr. This defines a range over which the target_value will be
            approached. Before the attr_a is within this range the output
            of this and the attr_a will be equal. Defaults to 0.5.
        target_value (NcNode or NcAttrs or str or int or float): Value or
            attr. This is the value that will be approached slowly.
            Defaults to 1.

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

    exponent = ((start_val) - attr_a) / fade_in_range
    soft_approach_value = target_value - fade_in_range * Op.exp(exponent)

    is_range_valid_condition = Op.condition(
        fade_in_range > 0,
        soft_approach_value,
        target_value,
    )

    is_in_range_condition = Op.condition(
        attr_a > start_val,
        is_range_valid_condition,
        attr_a,
    )

    return is_in_range_condition


@noca_op
def sin(attr_a):
    """Sine of attr_a.

    Note:
        Only works for 1D inputs!

        The idea how to set this up with native Maya nodes is from Chad Vernon:
        https://www.chadvernon.com/blog/trig-maya/

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Value or attr

    Returns:
        NcNode: Instance with node and output-attr.

    Example:
        ::

            in_attr = Node("pCube.tx")
            Op.sin(in_attr)
    """
    sin = Op.euler_to_quat(attr_a * 2).outputQuatX
    return sin


@noca_op
def cos(attr_a):
    """Cosine of attr_a.

    Note:
        Only works for 1D inputs!

        The idea how to set this up with native Maya nodes is from Chad Vernon:
        https://www.chadvernon.com/blog/trig-maya/

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Value or attr

    Returns:
        NcNode: Instance with node and output-attr.

    Example:
        ::

            in_attr = Node("pCube.tx")
            Op.cos(in_attr)
    """
    cos = Op.euler_to_quat(attr_a * 2).outputQuatW
    return cos


@noca_op
def tan(attr_a):
    """Tangent of attr_a.

    Note:
        Only works for 1D inputs!

        The idea how to set this up with native Maya nodes is from Chad Vernon:
        https://www.chadvernon.com/blog/trig-maya/

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Value or attr

    Returns:
        NcNode: Instance with node and output-attr.

    Example:
        ::

            in_attr = Node("pCube.tx")
            Op.tan(in_attr)
    """
    sin = Op.sin(attr_a)
    cos = Op.cos(attr_a)
    tan = sin / cos
    divide_by_zero_safety = Op.condition(cos == 0, 0, tan)
    return divide_by_zero_safety


@noca_op
def asin(attr_a):
    """Arcsine of attr_a.

    Note:
        Only works for 1D inputs!

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Value or attr

    Returns:
        NcNode: Instance with node and output-attr.

    Example:
        ::

            in_attr = Node("pCube.tx")
            Op.asin(in_attr)
    """
    x_vector_component = Op.sqrt(1 - attr_a ** 2)
    angle_between = Op.angle_between(
        (x_vector_component, 0, 0),
        (x_vector_component, attr_a, 0),
    )
    right_angle_cond = Op.condition(x_vector_component == 0, 90, angle_between)
    sign_cond = Op.condition(attr_a >= 0, right_angle_cond, -right_angle_cond)
    return sign_cond


@noca_op
def acos(attr_a):
    """Arccosine of attr_a.

    Note:
        Only works for 1D inputs!

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Value or attr

    Returns:
        NcNode: Instance with node and output-attr.

    Example:
        ::

            in_attr = Node("pCube.tx")
            Op.acos(in_attr)
    """
    y_vector_component = Op.sqrt(1 - attr_a ** 2)
    angle_between = Op.angle_between(
        (attr_a, 0, 0),
        (attr_a, y_vector_component, 0),
    )
    right_angle_cond = Op.condition(attr_a == 0, 90, angle_between)
    flip_cond = Op.condition(
        attr_a < 0, 180 - right_angle_cond, right_angle_cond
    )
    return flip_cond


@noca_op
def atan(attr_a):
    """Arctangent of attr_a, which calculates only quadrant 1 and 4.

    Note:
        Only works for 1D inputs!

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Value or attr

    Returns:
        NcNode: Instance with node and output-attr.

    Example:
        ::

            in_attr = Node("pCube.tx")
            Op.atan(in_attr)
    """
    angle_between = Op.angle_between(
        (1, 0, 0),
        (1, attr_a, 0),
    )
    sign_cond = Op.condition(attr_a < 0, -angle_between, angle_between)
    return sign_cond


@noca_op
def atan2(attr_a, attr_b):
    """Arctangent2 of attr_b/attr_a, which calculates all four quadrants.

    Note:
        The arguments mimic the behaviour of math.atan2(y, x)! Make sure you
        pass them in the right order.

    Args:
        attr_a (NcNode or NcAttrs or str or int or float): Value or attr
        attr_b (NcNode or NcAttrs or str or int or float): Value or attr

    Returns:
        NcNode: Instance with node and output-attr.

    Example:
        ::

            x = Node("pCube.tx")
            y = Node("pCube.ty")
            Op.atan2(y, x)
    """
    # Measure the angle between a vector constructed out of given values.
    angle_between = Op.angle_between(
        (attr_b, 0, 0),
        (attr_b, attr_a, 0),
    )

    # Change the angle, depending on the quadrant it lies in.
    quadrant_1_and_4_cond = Op.condition(
        attr_a > 0,
        angle_between,
        -angle_between,
    )
    quadrant_2_and_3_cond = Op.condition(
        attr_a > 0,
        180 - angle_between,
        -180 + angle_between,
    )
    quadrant_cond = Op.condition(
        attr_b > 0,
        quadrant_1_and_4_cond,
        quadrant_2_and_3_cond,
    )

    # Take care of special case where attr_b is zero & would result in angle=0.
    right_angle_cond = Op.condition(
        attr_b == 0,
        Op.condition(attr_a < 0, -90, 90),
        quadrant_cond,
    )

    return right_angle_cond
