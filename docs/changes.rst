Changes
==============================================================================

Release 2.1.0
*************

Incompatible changes
--------------------
* Careful: The actual NodeCalculator now lives in the node_calculator INSIDE the main repo! It's not at the top level anymore.
* The decompose_matrix and pair_blend Operators now have a "return_all_outputs"-flag. By default they return an NcNode now, not all outputs in an NcList! > node_calculator/issues/67

Features added
--------------
* Tests are now standalone (not dependent on CMT anymore) and can be run from a console! Major kudos to Andres Weber!
* CircleCi integration to auto-run checks whenever repo is updated. Again: Major kudos to Andres Weber!
* The default Operators are now factored out into their own files: base_functions.py & base_operators.py > node_calculator/issues/59
* It's now possible to set attributes on the shape from the transform (mimicking Maya behaviour). Sudo example: pCube1.outMesh (instead of requiring pCube1Shape.outMesh) > node_calculator/issues/69
* The noca.cleanup(keep_selected=False) function allows to delete all nodes created by the NodeCalculator to unclutter heavy prototyping scenes. > node_calculator/issues/63

Bugs fixed
----------
* The dot-Operator now correctly returns a 1D result (returned a 3D result before) > node_calculator/issues/68

Release 2.0.1
*************

Bugs fixed
----------
* Aliased attributes can now be accessed (om_util.get_mplug_of_mobj couldn't find them before)
* Operation values of zero are now set correctly (they were ignored)


Release 2.0.0
*************

Dependencies
------------

Incompatible changes
--------------------
* "output" is now "outputs" in lookup_table.py!
* OPERATOR_LOOKUP_TABLE is now OPERATORS
* multi_input & multi_output doesn't have to be declared anymore! The tag "{array}" will cause an input/output to be interpreted as multi.

Deprecated
----------
* Container support. It wasn't properly implemented and Maya containers are not useful (imo).

Features added
--------------
* Easy to add custom/proprietary nodes via extension
* Convenience functions for transforms, locators & create_node.
* auto_consolidate & auto_unravel can be turned off (globally & individually)
* Indexed attributes now possible (still a bit awkward, but hey..)
* Many additional operators.
* Documentation; NoCa v2 cheat sheet!
* om_util with various OpenMaya functions
* Many other small improvements.
* Any attr type can now be created.
* Attribute separator convenience function added. Default values can be specified in config.py.
* config.py to make it easy and clear where to change basic settings.
* Default extension for `Serguei Kalentchouk's maya_math_nodes <https://github.com/serguei-k/maya-math-nodes>`_
* Tests added, using `Chad Vernon's test suite <https://github.com/chadmv/cmt/tree/master/scripts/cmt/test/>`_

Bugs fixed
----------
* Uses MObjects and MPlugs to reference to Maya nodes and attributes; Renaming of objects, attributes with index, etc. are no longer an issue.
* Cleaner code; Clear separation of classes and their functionality (NcList, NcNode, NcAttrs, NcValue)
* Any child attribute will be consolidated (array, normal, ..)
* Tracer now stores values as variables (from get() or so)
* Conforms pretty well to PEP8 (apart from tests)

Testing
--------

Features removed
----------------


Release 1.0.0
*************

* First working version: Create, connect and set Maya nodes with Python commands.
