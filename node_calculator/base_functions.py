"""Basic NodeCalculator functions."""
# This is an extension that is loaded by default.

# The main difference to the base_operators is that functions rely on operators!
# They combine existing operators to create more complex setups.

from node_calculator.core import noca_op
from node_calculator.core import Op

# Any Maya plugin that should be loaded for the NodeCalculator
REQUIRED_EXTENSION_PLUGINS = []


# Dict of all available operations: used node-type, inputs, outputs, etc.
EXTENSION_OPERATORS = {}


@noca_op
def soft_approach(in_value, fade_in_range=0.5, target_value=1):
    """Follow in_value, but approach the target_value slowly.

    Note:
        Only works for 1D inputs!

    Args:
        in_value (NcNode or NcAttrs or str or int or float): Value or attr
        fade_in_range (NcNode or NcAttrs or str or int or float): Value or
            attr. This defines a range over which the target_value will be
            approached. Before the in_value is within this range the output
            of this and the in_value will be equal. Defaults to 0.5.
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
