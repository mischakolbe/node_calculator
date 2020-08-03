Changes
==============================================================================


Release 2.1.5
********************

Features added
--------------------
* Added getattr, attr and set methods to NcList class. > node_calculator/issues/93
* Added trigonometry operators: > node_calculator/issues/94
    * Thanks for the basic idea, Chad Vernon! https://www.chadvernon.com/blog/trig-maya/
    * sin
    * cos
    * tan
    * asin
    * acos
    * atan
    * atan2

Bugs fixed
--------------------
* Fixed MPlug retrieval of indexed AND aliased attrs (such as blendshape target weights) > node_calculator/issues/91
* Including foster children in MPlug search (such as ramp_node.colorEntryList[0].colorR) > node_calculator/issues/92


Release 2.1.4
********************

Bugs fixed
--------------------
* remap_value now accepts NoCa nodes for value-arg > node_calculator/issues/95


Release 2.1.3
********************

Features added
--------------------
* added curve_info Operator. > node_calculator/issues/82 & 87
* added reset_cleanup function to reset the cleanup-stack. > node_calculator/issues/83

Bugs fixed
--------------------
* More robust shape node creation and naming. > node_calculator/issues/86
* More descriptive error message when node doesn't exist or isn't unique. > node_calculator/issues/84
* PyMel is only loaded when necessary. > node_calculator/issues/85


Release 2.1.2
********************

Features added
--------------------
* Added the following operators: > node_calculator/issues/80

    * sum
    * quatAdd
    * quatConjugate
    * quatInvert
    * quatNegate
    * quatNormalize
    * quatProd
    * quatSub
    * quatToEuler
    * eulerToQuat
    * holdMatrix
    * reverse
    * passMatrix
    * remapColor
    * remapHsv
    * rgbToHsv
    * wtAddMatrix
    * closestPointOnMesh
    * closestPointOnSurface
    * pointOnSurfaceInfo
    * pointOnCurveInfo
    * nearestPointOnCurve
    * fourByFourMatrix

* Operator unittests are more generic now: A dictionary contains which inputs/outputs to use for each Operators test.
* Added more unittests for some issues that came up: non-unique node names, aliased attributes, accessing shape-attributes through the transform (see Features added in Release 2.1.1). > node_calculator/issues/76

Bugs fixed
--------------------
* sum(), average() and mult_matrix() operators now work correctly when given lists/tuples/NcLists as args.


Release 2.1.1
********************

Bugs fixed
--------------------
* Now supports non-unique names > node_calculator/issues/74
* Catch error when user sets a non-existent attribute on an NcList item (now only throws a warning) > node_calculator/issues/73


Release 2.1.0
********************

Incompatible changes
--------------------
* Careful: The actual NodeCalculator now lives in the node_calculator INSIDE the main repo! It's not at the top level anymore.
* The decompose_matrix and pair_blend Operators now have a "return_all_outputs"-flag. By default they return an NcNode now, not all outputs in an NcList! > node_calculator/issues/67

Features added
--------------------
* Tests are now standalone (not dependent on CMT anymore) and can be run from a console! Major kudos to Andres Weber!
* CircleCi integration to auto-run checks whenever repo is updated. Again: Major kudos to Andres Weber!
* The default Operators are now factored out into their own files: base_functions.py & base_operators.py > node_calculator/issues/59
* It's now possible to set attributes on the shape from the transform (mimicking Maya behaviour). Sudo example: pCube1.outMesh (instead of requiring pCube1Shape.outMesh) > node_calculator/issues/69
* The noca.cleanup(keep_selected=False) function allows to delete all nodes created by the NodeCalculator to unclutter heavy prototyping scenes. > node_calculator/issues/63

Bugs fixed
--------------------
* The dot-Operator now correctly returns a 1D result (returned a 3D result before) > node_calculator/issues/68


Release 2.0.1
********************

Bugs fixed
--------------------
* Aliased attributes can now be accessed (om_util.get_mplug_of_mobj couldn't find them before)
* Operation values of zero are now set correctly (they were ignored)


Release 2.0.0
********************

Dependencies
--------------------

Incompatible changes
--------------------
* "output" is now "outputs" in lookup_table.py!
* OPERATOR_LOOKUP_TABLE is now OPERATORS
* multi_input & multi_output doesn't have to be declared anymore! The tag "{array}" will cause an input/output to be interpreted as multi.

Deprecated
--------------------
* Container support. It wasn't properly implemented and Maya containers are not useful (imo).

Features added
--------------------
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
--------------------
* Uses MObjects and MPlugs to reference to Maya nodes and attributes; Renaming of objects, attributes with index, etc. are no longer an issue.
* Cleaner code; Clear separation of classes and their functionality (NcList, NcNode, NcAttrs, NcValue)
* Any child attribute will be consolidated (array, normal, ..)
* Tracer now stores values as variables (from get() or so)
* Conforms pretty well to PEP8 (apart from tests)

Testing
--------------------

Features removed
--------------------


Release 1.0.0
********************

* First working version: Create, connect and set Maya nodes with Python commands.
