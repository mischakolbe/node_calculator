"""Additional operators for the NodeCalculator; proprietary or custom nodes.

Note:
    If you want to separate out this extension file from the core functionality
    of the NodeCalculator (to maintain your proprietary additions in a separate
    repo or so) you simply have to add the folder where this noca_extension
    module will live to the __init__.py of the node_calculator-module!

    Check noca_extension_maya_math_nodes.py to see an example of how to write a
    NodeCalculator extension.


:author: You ;)
"""

# DON'T import node_calculator.core as noca! It's a cyclical import that fails!
# Most likely the only two things needed from the node_calculator:
from node_calculator.core import noca_op
from node_calculator.core import _create_operation_node


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ STEP 1: REQUIRED PLUGINS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
If your operators require certain Maya plugins to be loaded: Add the name(s) of
those plugin(s) to this list.

You can use this script to find out what plugin a certain node type lives in:

node_type = ""  # Enter node type here!
for plugin in cmds.pluginInfo(query=True, listPlugins=True):
    plugin_types = cmds.pluginInfo(plugin, query=True, dependNode=True) or []
    for plugin_type in plugin_types:
        if plugin_type == node_type:
            print "\n>>> {} is part of the plugin {}".format(node_type, plugin)
'''
REQUIRED_EXTENSION_PLUGINS = []


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ STEP 2: OPERATORS DICTIONARY ~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
EXTENSION_OPERATORS holds the data for each available operation:
the necessary node-type, its inputs, outputs, etc.
This unified data enables to abstract node creation, connection, etc.

Mandatory flags:
- node: Type of Maya node necessary
- inputs: input attributes (list of lists)
- outputs: output attributes (list)

Optional flags:
- operation: many Maya nodes have an "operation" attribute that sets the
    operation mode of the node. Use this flag to set this attribute.
- output_is_predetermined: should outputs be truncated to dimensionality of
    inputs or should they always stay exactly as specified?


Check here to see lots of examples for the EXTENSION_OPERATORS-dictionary:
_operator_lookup_table_init (in lookup_table.py)
'''
EXTENSION_OPERATORS = {
    # "example_operation": {
    #     "node": "mayaNodeForThisOperation",
    #     "inputs": [
    #         ["singleInputParam"],
    #         ["input1X", "input1Y", "input1Z"],
    #         ["input2X", "input2Y", "input2Z"],
    #         ["input[{array}].inX", "input[{array}].inY", "input[{array}].inZ"],
    #     ],
    #     "outputs": [
    #         ["outputX", "outputY", "outputZ"],
    #     ],
    #     "operation": 3,
    #     "output_is_predetermined": False,
    # }
}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ STEP 3: OPERATOR FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
Add a function for every operation that should be accessible via noca.Op!

Let's look at this example:
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@noca_op
def example_operation(attr_a, attr_b=(0, 1, 2), attr_c=False):
    created_node = _create_operation_node(
        'example_operation', attr_a, attr_b, attr_c
    )
    return created_node
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

The decorator @noca_op is mandatory! It will take care of adding the function
to noca.Op!

I recommend using the same name for the function as the one you chose for the
corresponding EXTENSION_OPERATORS-key to avoid confusion what belongs together!

The function arguments will be what the user can specify when calling this
operation via noca.Op.example_operation(). Feel free to use default values.

Inside the function you can do whatever is necessary to make your operator work.
Most likely you will want to use the _create_operation_node-function at some
point. It works like this:
>   The first argument must be the name of the operation. It's used as a key to
    look up the data you stored in EXTENSION_OPERATORS! As mentioned: I suggest
    you use the same name for the EXTENSION_OPERATORS-key and the function name
    to prevent any confusion what belongs together!
>   The following arguments will be used (in order!) to connect or set the
    inputs specified for this operation in the EXTENSION_OPERATORS dictionary.
>   The created node is returned as a noca.NcNode-instance. It has the outputs
    specified in the EXTENSION_OPERATORS associated with it.

To properly integrate your additional operation into the NodeCalculator you
must return the returned NcNode instance of _create_operation_node! That way
the newly created node and its outputs can be used in further operations.


Check here to see lots of examples for the operator functions:
OperatorMetaClass (in core.py)
(Again: the @noca_op decorator takes care of integrating your functions into
this class. No need to add the argument "self".
'''
