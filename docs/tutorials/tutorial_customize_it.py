# CUSTOMIZE IT

# example_extension.py:
from node_calculator.core import noca_op
from node_calculator.core import _create_operation_node


REQUIRED_EXTENSION_PLUGINS = ["lookdevKit"]

EXTENSION_OPERATORS = {
    "color_math_min": {
        "node": "colorMath",
        "inputs": [
            ["colorAR", "colorAG", "colorAB"],
            ["alphaA"],
            ["colorBR", "colorBG", "colorBB"],
            ["alphaB"],
        ],
        "outputs": [
            ["outColorR", "outColorG", "outColorB"],
            # ["outAlpha"], ?
        ],
        "operation": 4,
    },
}


@noca_op
def color_math_min(color_a, alpha_a=0.25, color_b=(0, 0, 1), alpha_b=0.75):
    created_node = _create_operation_node(
        'color_math_min', color_a, alpha_a, color_b, alpha_b
    )
    return created_node


# In Maya:

# CUSTOMIZE IT
import node_calculator.core as noca

# Initiate Node-objects for all test-geos
a_geo = noca.Node("A_geo")
b_geo = noca.Node("B_geo")
c_geo = noca.Node("C_geo")

c_geo.tx = noca.Op.color_math_min(
    color_a=a_geo.tx,
    alpha_a=0.5,
    color_b=b_geo.ty,
    alpha_b=0.5,
)
