"""Example of a quick implementation of a fictional node with many operators.

Note:
    You CAN add useful/specific docStrings for your functions when you use
    closures to implement them. I recommend you go that extra mile. Everyone
    using your Operators will be grateful! Take a look at the _format_docstring
    decorator inside core.py and how it's used! An example is in this extension.
"""

# DON'T import node_calculator.core as noca! It's a cyclical import that fails!
# Most likely the only two things needed from the node_calculator:
from node_calculator.core import noca_op
from node_calculator.core import _create_operation_node
from node_calculator.core import _format_docstring


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
    node_type = EXTENSION_OPERATORS[operator_type]["node"]

    @_format_docstring(node_type=node_type, operation=operator_type)
    def func(attr_a):
        """Create & connect {node_type}-node to perform {operation}-operation.

        Args:
            attr_a (NcNode or NcAttrs or string): Maya node attribute.

        Returns:
            NcNode: Instance with node and output-attribute(s)

        Example:
            Op.{operation}(Node("pCube1.tx"))
        """
        return _create_operation_node(operator_type, attr_a)

    func.__name__ = operator_type
    return func


# Add all available math operators via closure
for math_operator in MATH_NODE_OPERATORS:
    noca_op(_define_math_operator(math_operator))
