"""Maya utility functions. Using almost exclusively OpenMaya commands.

:author: Mischa Kolbe <mischakolbe@gmail.com>

Note:
    I am using this terminology when talking about plugs:

    * Array plug: A plug that allows any number of connections.
        Example: "input3D" is the array plug of the plugs "input3D[i]".
    * Array plug element: A specific plug of an array plug.
        Example: "input3D[7]" is an array plug element of "input3D".
    * Parent plug: A plug that can be split into child plugs associated with it
        Example: "translate" is the parent plug of ["tx", "ty", "ty"]
    * Child plug: A plug that makes up part of a parent plug.
        Example: "translateX" is a child plug of "translate"
"""


# IMPORTS ---
# Python imports
import re

# Third party imports
from maya import cmds
from maya.api import OpenMaya

# Local imports
from node_calculator import logger


# SETUP LOGGER ---
logger.clear_handlers()
logger.setup_stream_handler(level=logger.logging.WARN)
LOG = logger.log


# MOBJECT ---
def get_mobj(node):
    """Get the MObject of the given node.

    Args:
        node (MObject or MDagPath or str): Maya node requested as an MObject.

    Returns:
        MObject: MObject instance that is a reference to the given node.
    """
    if isinstance(node, OpenMaya.MObject):
        return node

    if isinstance(node, OpenMaya.MDagPath):
        return node.node()

    selection_list = OpenMaya.MSelectionList()
    selection_list.add(node)
    mobj = selection_list.getDependNode(0)

    return mobj


def get_name_of_mobj(mobj):
    """Get the name of an MObject.

    Args:
        mobj (MObject): MObject whose name is requested.

    Returns:
        str: Name of given MObject.
    """
    node_fn = OpenMaya.MFnDependencyNode(mobj)
    node_name = node_fn.name()

    return node_name


def get_shape_mobjs(mobj):
    """Get the shape MObjects of a given MObject.

    Args:
        mobj (MObject or MDagPath or str): MObject whose shapes are requested.

    Returns:
        list: List of MObjects of the shapes of given MObject.
    """
    if not isinstance(mobj, OpenMaya.MObject):
        mobj = get_mobj(mobj)

    return_shape_mobjs = []

    mdag_path_of_mobj = get_mdag_path(mobj)

    if mdag_path_of_mobj:
        num_shapes = mdag_path_of_mobj.numberOfShapesDirectlyBelow()

        for index in range(num_shapes):
            # Do NOT take this get_mdag_path out of the loop!
            # The ".extendToShape" afterwards acts upon the resulting mdagPath!
            mdag_path_of_mobj = get_mdag_path(mobj)
            shape_mdag_path = mdag_path_of_mobj.extendToShape(shapeNum=index)
            shape_mobj = get_mobj(shape_mdag_path)

            return_shape_mobjs.append(shape_mobj)

    return return_shape_mobjs


def is_instanced(node):
    """Check if a Maya node is instantiated.

    Args:
        node (MObject or MDagPath or str): Node to check if it's instantiated.

    Returns:
        bool: Whether given node is instantiated.
    """
    mdag_path = get_mdag_path(node)
    state = mdag_path.isInstanced()
    return state


def get_dag_path_of_mobj(mobj, full=False):
    """Get the dag path of an MObject. Either partial or full.

    Note:
        The flag "full" defines whether a full or partial DAG path should be
        returned. "Partial" simply means the shortest unique DAG path to
        describe the given MObject. "Full" always gives the entire DAG path.

    Args:
        mobj (MObject or MDagPath or str): Node whose long name is requested.
        full (bool): Return either the entire or partial DAG path. See Note.

    Returns:
        str: DAG path to the given MObject.
    """
    mdag_path = get_mdag_path(mobj)
    if mdag_path:
        if full:
            dag_path = mdag_path.fullPathName()
        else:
            dag_path = mdag_path.partialPathName()
    else:
        dag_path = get_name_of_mobj(mobj)

    return dag_path


def get_node_type(node, api_type=False):
    """Get the type of the given Maya node.

    Note:
        More versatile version of cmds.nodeType()

    Args:
        node (MObject or MDagPath or str): Node whose type should be queried.
        api_type (bool): Return Maya API type.

    Returns:
        str: Type of Maya node
    """
    mobj = get_mobj(node)

    if api_type:
        node_type = mobj.apiTypeStr
    else:
        node_type = OpenMaya.MFnDependencyNode(mobj).typeName

    return node_type


def get_all_mobjs_of_type(dependency_node_type):
    """Get all MObjects in the current Maya scene of the given OpenMaya-type.

    Args:
        dependency_node_type (OpenMaya.MFn): OpenMaya.MFn-type.

    Returns:
        list: List of MObjects of matching type.

    Example:
        ::

            get_all_mobjs_of_type(OpenMaya.MFn.kDependencyNode)
    """
    dep_node_iterator = OpenMaya.MItDependencyNodes(dependency_node_type)
    return_list = []
    while not dep_node_iterator.isDone():
        mobj = dep_node_iterator.thisNode()
        return_list.append(mobj)
        dep_node_iterator.next()

    return return_list


def rename_mobj(mobj, name):
    """Rename the given MObject.

    Note:
        This is currently NOT undoable!!! Therefore be careful!

    Args:
        mobj (MObject): Node to be renamed.
        name (str): New name for the node.

    Returns:
        str: New name of renamed mobj
    """
    dag_modifier = OpenMaya.MDagModifier()
    dag_modifier.renameNode(mobj, name)
    dag_modifier.doIt()

    return get_name_of_mobj(mobj)


def get_selected_nodes_as_mobjs():
    """Get all currently selected nodes in the scene as MObjects.

    Returns:
        list: List of MObjects of the selected nodes in the Maya scene.
    """
    mobjs = []

    selection_list = OpenMaya.MGlobal.getActiveSelectionList()
    if selection_list.length():

        iterator = OpenMaya.MItSelectionList(
            selection_list,
            OpenMaya.MFn.kDagNode
        )
        while not iterator.isDone():
            mobj = iterator.getDependNode()
            mobjs.append(mobj)
            iterator.next()

    return mobjs


def select_mobjs(mobjs):
    """Select the given MObjects in the Maya scene.

    Args:
        mobjs (list): List of MObjects to be selected.

    Todo:
        ::

            For some reason the version below (utilizing OpenMaya-methods) only
            selects the nodes, but they don't get selected in the outliner or
            viewport! Therefore using the cmds-version for now.

            m_selection_list = OpenMaya.MSelectionList()
            for mobj in mobjs:
                m_selection_list.add(mobj)
            OpenMaya.MGlobal.setActiveSelectionList(
                m_selection_list,
                OpenMaya.MGlobal.kReplaceList
            )
            return m_selection_list
    """
    if not isinstance(mobjs, (list, tuple)):
        mobjs = [mobjs]

    select_list = []
    for mobj in mobjs:
        select_list.append(get_dag_path_of_mobj(mobj))

    cmds.select(select_list)


# MDAG ---
def get_mdag_path(mobj):
    """Get an MDagPath from the given mobj.

    Args:
        mobj (MObject or MDagPath or str): MObject to get MDagPath for.

    Returns:
        MDagPath: MDagPath of the given mobj.
    """
    if isinstance(mobj, OpenMaya.MDagPath):
        return mobj

    if not isinstance(mobj, OpenMaya.MObject):
        mobj = get_mobj(mobj)

    mdag_path = None
    if mobj.hasFn(OpenMaya.MFn.kDagNode):
        mdag_path = OpenMaya.MDagPath.getAPathTo(mobj)
    return mdag_path


def get_mfn_dag_node(node):
    """Get an MFnDagNode of the given node.

    Args:
        node (MObject or MDagPath or str): Node to get MFnDagNode for.

    Returns:
        MFnDagNode: MFnDagNode of the given node.
    """
    mfn_dag_node = OpenMaya.MFnDagNode(get_mobj(node))

    return mfn_dag_node


def get_parents(node):
    """Get parents of the given node.

    Args:
        node (MObject or MDagPath or str): Node whose parents are queried.

    Returns:
        list: Name of parents in an ascending list: First parent first.
    """
    # Getting the parents from splitting the long name string is faster than
    # using the .parent() method recursively.
    parents = list(
        # Slice off empty first string and node itself from the full dag path
        reversed(get_dag_path_of_mobj(node, full=True).split("|")[1:-1])
    )

    return parents


def get_parent(node):
    """Get parent of the given node.

    Note:
        More versatile version of cmds.listRelatives(node, parent=True)[0]

    Args:
        node (MObject or MDagPath or str): Node to get parent of.

    Returns:
        str: Name of node's parent.
    """
    mfn_dag_node = get_mfn_dag_node(node)

    parent = get_name_of_mobj(mfn_dag_node.parent(0))
    return parent


# MPLUG ---
def set_mobj_attribute(mobj, attr, value):
    """Set attribute on given MObject to the given value.

    Note:
        Basically cmds.setAttr() that works with MObjects.

    Args:
        mobj (MObject or MDagPath or str): Node whose attribute should be set.
        attr (str): Name of attribute.
        value (int or float or bool or str): Value plug should be set to.

    TODO:
        Use OpenMaya API only! Check: austinjbaker.com/mplugs-setting-values
    """
    plug = "{0}.{1}".format(get_dag_path_of_mobj(mobj), attr)
    cmds.setAttr(plug, value)


def get_attr_of_mobj(mobj, attr):
    """Get value of attribute on MObject.

    Note:
        Basically cmds.getAttr() that works with MObjects.

    Args:
        mobj (MObject or MDagPath or str): Node whose attr should be queried.
        attr (str): Name of attribute.

    Returns:
        list or tuple or int or float or bool or str: Value of queried plug.
    """
    plug = "{0}.{1}".format(get_dag_path_of_mobj(mobj), attr)
    value = cmds.getAttr(plug)

    return value


def is_valid_mplug(mplug):
    """Check whether given mplug is a valid MPlug.

    Args:
        mplug (MObject or MPlug or MDagPath or str): Potential MPlug.

    Returns:
        bool: True if given mplug actually is an MPlug instance.
    """
    if not isinstance(mplug, OpenMaya.MPlug):
        LOG.debug("Expected an MPlug, got %s of type %s", mplug, type(mplug))
        return False
    return True


def get_parent_mplug(mplug):
    """Get the parent MPlug of the given mplug.

    Note:
        .tx -> .t

    Args:
        mplug (MPlug): MPlug whose parent MPlug to get.

    Returns:
        MPlug or None: Parent MPlug or None if that doesn't exist.
    """
    if not is_valid_mplug(mplug):
        return None

    mplug_parent = None

    if mplug.isChild:
        mplug_parent = mplug.parent()

    return mplug_parent


def get_child_mplug(mplug, child):
    """Get the child MPlug of the given mplug.

    Note:
        .t -> .tx

    Args:
        mplug (MPlug): MPlug whose child MPlug to get.
        child (str): Name of the child plug

    Returns:
        MPlug or None: Child MPlug or None if that doesn't exist.
    """
    if not is_valid_mplug(mplug):
        return None

    mplug_child = None

    for child_plug in get_child_mplugs(mplug):
        if str(child_plug).endswith("." + child):
            mplug_child = child_plug

    return mplug_child


def get_child_mplugs(mplug):
    """Get all child MPlugs of the given mplug.

    Note:
        .t -> [.tx, .ty, .tz]

    Args:
        mplug (MPlug): MPlug whose child MPlugs to get.

    Returns:
        list: List of child MPlugs.
    """
    if not is_valid_mplug(mplug):
        return None

    child_plugs = []

    if mplug.isCompound:
        num_children = mplug.numChildren()
        for child_index in range(num_children):
            child_plugs.append(mplug.child(child_index))

    return child_plugs


def get_array_mplug_elements(mplug):
    """Get all array element MPlugs of the given mplug.

    Note:
        .input3D -> .input3D[0], .input3D[1], ...

    Args:
        mplug (MPlug): MPlug whose array element MPlugs to get.

    Returns:
        list: List of array element MPlugs.
    """
    if not is_valid_mplug(mplug):
        return None

    array_elements = []

    if mplug.isArray:
        num_elements = mplug.evaluateNumElements()
        for element_index in range(num_elements):
            mplug_element = mplug.elementByPhysicalIndex(element_index)
            array_elements.append(mplug_element)

    return array_elements


def get_array_mplug_by_index(mplug, index, physical=True):
    """Get array element MPlug of given mplug by its physical or logical index.

    Note:
        .input3D -> .input3D[3]

        PHYSICAL INDEX:
        This function will NOT create a plug if it doesn't exist! Therefore
        this function is particularly useful for iteration through the element
        plugs of an array plug.

        The index can range from 0 to numElements() - 1.

        LOGICAL INDEX:
        Maya will create a plug at the requested index if it doesn't exist.
        This function is therefore very useful to reliably get an array element
        MPlug, even if that particular index doesn't necessarily already exist.

        The logical index is the sparse array index used in MEL scripts.

    Args:
        mplug (MPlug): MPlug whose array element MPlug to get.
        index (int): Index of array element plug.
        physical (bool): Look for element at physical index. If set to False it
            will look for the logical index!

    Returns:
        MPlug or None: MPlug at the requested index.
    """
    if not is_valid_mplug(mplug):
        return None

    return_mplug = None

    if not mplug.isArray:
        LOG.warn("%s is not an array plug!", mplug)
        return return_mplug

    if physical:
        # Look for physical index
        num_elements = mplug.evaluateNumElements()
        if num_elements > index:
            return_mplug = mplug.elementByPhysicalIndex(index)

    else:
        # Look for logical index
        return_mplug = mplug.elementByLogicalIndex(index)

    return return_mplug


def get_mplug_of_node_and_attr(node, attr_str):
    """Get an MPlug to the given node & attr combination.

    Args:
        node (MObject or MDagPath or str): Node whose attr should be queried.
        attr_str (str): Name of attribute.

    Returns:
        MPlug or None: MPlug of given node.attr or None if that doesn't exist.

    Raises:
        RuntimeError: If the desired mplug does not exist.
    """
    mobj = get_mobj(node)

    attrs = split_attr_string(attr_str)

    mplug = None

    for attr, index in attrs:
        if mplug is None:
            mplug = get_mplug_of_mobj(mobj, attr)
        else:
            mplug = get_child_mplug(mplug, attr)

        if not mplug:
            msg = "mplug {0}.{1} doesn't seem to exist!".format(node, attr_str)
            raise RuntimeError(msg)

        if index is not None:
            if not mplug.isArray:
                LOG.warn(
                    "mplug for %s.%s is supposed to have an index, "
                    "but is not an array attr!", node, attr_str
                )
            mplug = get_array_mplug_by_index(mplug, index, physical=False)

    return mplug


def get_mplug_of_mobj(mobj, attr):
    """Get MPlug from the given MObject and attribute combination.

    Args:
        mobj (MObject): MObject of node.
        attr (str): Name of attribute on node.

    Returns:
        MPlug: MPlug of the given node/attr combination.
    """
    node_mfn_dep_node = OpenMaya.MFnDependencyNode(mobj)

    mplug = None

    if node_mfn_dep_node.hasAttribute(attr):
        # findPlug-flags: (attr, wantNetworkedPlug)
        mplug = node_mfn_dep_node.findPlug(attr, False)

    # Check for aliased plugs, if none was found yet.
    if not mplug:
        alias_list = node_mfn_dep_node.getAliasList()
        for alias, attr_name in alias_list:
            if attr == alias:
                mplug = get_mplug_of_mobj(mobj, attr_name)

    return mplug


def get_mplug_of_plug(plug):
    """Get the MPlug to any given plug.

    Args:
        plug (MPlug or str): Name of plug; "name.attr"

    Returns:
        MPlug: MPlug of the requested plug.
    """
    if isinstance(plug, OpenMaya.MPlug):
        return plug

    node, attr = plug.split(".", 1)
    mplug = get_mplug_of_node_and_attr(node, attr)

    return mplug


def split_plug_string(plug):
    """Split string referring to a plug into its separate elements.

    Note:
        "namespace:some|dag|path|node.attr_a[attr_a_index].attr_b" ->
        (namespace, dag_path, node, [(attr_a, attr_a_index), (attr_b, None)])

    Args:
        plug (str): Name of plug; "name.attr"

    Returns:
        tuple: Tuple of elements that make up plug (namespace, dag_path, node, attrs)
    """
    node, attr = plug.split(".", 1)

    namespace, dag_path, node = split_node_string(node)
    attrs = split_attr_string(attr)

    return (namespace, dag_path, node, attrs)


def split_attr_string(attr):
    """Split string referring to an attr on a Maya node into its elements.

    Note:
        "attr_a[attr_a_index].attr_b[attr_b_index]. ..." ->
        [(attr_a, attr_a_index), (attr_b, attr_b_index), ...]

        The index for an attribute that has no index will be None.

    Args:
        attr (str): Name of attribute.

    Returns:
        list: List of tuples of the form (attribute, attribute-index)

    Raises:
        ValueError: If given string is not in the pattern described in Note.
    """
    attr_pattern = re.compile(r"(\w+)(?:\[(\d+)\])?\.?")

    matches = attr_pattern.findall(attr)

    if not matches:
        msg = (
            "String '{0}' could not be broken down into components that "
            "represent a Maya attr!".format(attr)
        )
        raise ValueError(msg)

    cleaned_matches = []
    for attribute, index in matches:
        if index:
            index = int(index)
        else:
            index = None
        cleaned_matches.append((attribute, index))

    return cleaned_matches


def split_node_string(node):
    """Split string referring to a Maya node name into its separate elements.

    Note:
        "namespace1:namespace2:some|dag|path|node" ->
        (namespaces, dag_path, node)

    Args:
        node (str): Name of Maya node, potentially with namespaces & dagPath.

    Returns:
        tuple: Tuple of the form (namespaces, dag_path, node)

    Raises:
        ValueError: If given string is not in the pattern described in Note.
        RuntimeError: If the given string looks like it stands for multiple
            Maya-nodes; a string that yields multiple regex-matches.

    """
    node_pattern = re.compile(r"((?:\w+:)*)?\|?((?:\w+\|)*)?(\w+)")

    matches = node_pattern.findall(node)

    if not matches:
        msg = (
            "String '{0}' could not be broken down into components that "
            "represent a Maya node!".format(node)
        )
        raise ValueError(msg)

    if len(matches) > 1:
        msg = (
            "String '{0}' yielded multiple nodes as results. "
            "Should be singular node!".format(node)
        )
        raise RuntimeError(msg)

    namespaces, dag_path, node = matches[0]

    # Split off last colon, if namespaces exist.
    if namespaces:
        namespaces = namespaces.rsplit(":", 1)[0]

    return (namespaces, dag_path, node)
