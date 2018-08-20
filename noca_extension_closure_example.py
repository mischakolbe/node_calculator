"""Example of a quick implementation of a fictional node with many operators.

Note:
    A big downside for this kind of implementation is that you won't get
    useful docStrings for your functions. Therefore, users won't be able to get
    much help by simply using the help() function on your Op - or by looking it
    up in this script.
"""

# DON'T import node_calculator.core as noca! It's a cyclical import that fails!
# Most likely the only two things needed from the node_calculator:
from node_calculator.core import noca_op
from node_calculator.core import _create_and_connect_node


REQUIRED_EXTENSION_PLUGINS = ["myMathNodePlugin"]


EXTENSION_OPERATORS = {}


# These are the available operations in our fictional math node.
# (The order is important; it is used for the operation-attribute)
MATH_NODE_OPERATORS = [
    "pow", "sqrt",
    "sin", "cos", "tan",
    "mod",
    "abs"
]


# Fill EXTENSION_OPERATORS with our math operations
for index, math_operator in enumerate(MATH_NODE_OPERATORS):
    EXTENSION_OPERATORS[math_operator] = {
        "node": "myMathNode",
        "inputs": [
            ["inFloatX", "inFloatY", "inFloatZ"],
        ],
        "outputs": [
            ["outFloatX", "outFloatY", "outFloatZ"],
        ],
        "operation": index,
    }


def _define_math_operator(operator_type):
    """
    Closure that implements math-operator with given operation-type.

    Args:
        operator_type (string): math operation type to implement

    Returns:
        math-operation function
    """
    def func(attr):
        """Function to be returned: Create & connect math node of operator_type"""
        return _create_and_connect_node(operator_type, attr)
    func.__name__ = operator_type
    return func


# Add all available math operators via closure
for math_operator in MATH_NODE_OPERATORS:
    noca_op(_define_math_operator(math_operator))
    # Example: Op.sin(Node("pCube1.tx"))
