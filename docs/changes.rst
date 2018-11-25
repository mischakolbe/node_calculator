Changes
==============================================================================

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
