# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import re

# Third party imports
from maya.api import OpenMaya
from maya import cmds

# Local imports
from . import logger
reload(logger)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP LOGGER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
logger.clear_handlers()
logger.setup_stream_handler(level=logger.logging.DEBUG)
log = logger.log


def get_name_of_mobj(mobj):
    node_fn = OpenMaya.MFnDependencyNode(mobj)
    node_name = node_fn.name()

    return node_name


def get_shape_mobjs_of_mobj(mobj):
    return_shape_mobjs = []

    mdag_path_of_mobj = get_mdag_path_of_mobj(mobj)

    if mdag_path_of_mobj:
        num_shapes = mdag_path_of_mobj.numberOfShapesDirectlyBelow()

        for index in range(num_shapes):
            # Do NOT take this get_mdag_path_of_mobj out of the loop!
            # The ".extendToShape" afterwards acts upon the resulting mdagPath!
            mdag_path_of_mobj = get_mdag_path_of_mobj(mobj)
            shape_mdag_path = mdag_path_of_mobj.extendToShape(shapeNum=index)
            shape_mobj = get_mobj_from_mdag_path(shape_mdag_path)

            return_shape_mobjs.append(shape_mobj)

    return return_shape_mobjs


def get_mdag_path_of_mobj(mobj):
    mdag_path = None
    if mobj.hasFn(OpenMaya.MFn.kDagNode):
        mdag_path = OpenMaya.MDagPath.getAPathTo(mobj)
    return mdag_path


def get_mobj_from_mdag_path(mdag):
    mobj = mdag.node()
    return mobj


def get_long_name_of_mobj(mobj, full=False):
    """
    If the given mobj corresponds to a dag-path node: Return the partial or full path
    (depending on the full-flag). Otherwise return the name of the mobj directly.

    full takes precedence - otherwise partial.
    """
    if not isinstance(mobj, OpenMaya.MObject):
        log.error("Given mobj {} is not an instance of OpenMaya.MObject".format(mobj))

    mdag_path = get_mdag_path_of_mobj(mobj)
    if mdag_path:
        if full:
            dag_path = mdag_path.fullPathName()
        else:
            dag_path = mdag_path.partialPathName()
    else:
        dag_path = get_name_of_mobj(mobj)

    return dag_path


def get_mobj_of_node(node):
    if type(node) is OpenMaya.MObject:
        return node

    selectionList = OpenMaya.MSelectionList()
    selectionList.add(node)
    mobj = selectionList.getDependNode(0)

    return mobj


def get_node_type(node, api_type=False):
    """Get node type, replaces cmds.nodeType()

    Args:
        node (str): node
        api_type (bool): return api type

    Returns:
        str: Node type
    """

    dependency_node = OpenMaya.MSelectionList().add(node).getDependNode(0)

    if api_type:
        return dependency_node.apiTypeStr

    return OpenMaya.MFnDependencyNode(dependency_node).typeName


def get_all_mobjs_of_type(dependency_node_type):
    """
    dependency_node_type must be of "type" OpenMaya.MFn: OpenMaya.MFn.kDependencyNode etc.
    """
    dep_node_iterator = OpenMaya.MItDependencyNodes(dependency_node_type)
    return_list = []
    while not dep_node_iterator.isDone():
        mobj = dep_node_iterator.thisNode()
        return_list.append(mobj)
        dep_node_iterator.next()

    return return_list


def rename_mobj(mobj, name):
    dag_modifier = OpenMaya.MDagModifier()
    dag_modifier.renameNode(mobj, name)
    dag_modifier.doIt()


def set_mobj_attribute(mobj, attr, value):
    # This should be om-only, too!
    # http://austinjbaker.com/mplugs-setting-values
    dag_path = get_long_name_of_mobj(mobj)
    cmds.setAttr("{}.{}".format(dag_path, attr), value)


def selected_nodes_in_scene_as_mobjs():
    mobjs = []

    selection_list = OpenMaya.MGlobal.getActiveSelectionList()
    if selection_list.length() > 0:
        iterator = OpenMaya.MItSelectionList(selection_list, OpenMaya.MFn.kDagNode)
        while not iterator.isDone():
            mobj = iterator.getDependNode()
            mobjs.append(mobj)
            iterator.next()

    return mobjs


def get_attr_of_mobj(mobj, attr):
    # Rewrite this to pure OM!
    path = get_long_name_of_mobj(mobj)
    value = cmds.getAttr("{}.{}".format(path, attr))

    return value


def select_mobjs(mobjs):
    """
    For some reason the first (commented out) version of this command that utilizes
    om-methods only selects the node, but it doesn't get selected in the outliner
    or viewport! Therefore using the cmds-version for now.
    """
    # m_selection_list = OpenMaya.MSelectionList()
    # for mobj in mobjs:
    #     m_selection_list.add(mobj)
    # OpenMaya.MGlobal.setActiveSelectionList(m_selection_list, OpenMaya.MGlobal.kReplaceList)
    # return m_selection_list

    select_list = []
    for mobj in mobjs:
        select_list.append(get_long_name_of_mobj(mobj))
    cmds.select(select_list)
    return select_list




"""
Array plug:
input3D

Array plug elements
input3D[0, 1, 2, ...]

Parent plug
t

Child plug
tx, ty, tz
"""


def is_valid_mplug(mplug):

    if not isinstance(mplug, OpenMaya.MPlug):
        cmds.error("Expected an MPlug, got {} of type {}".format(mplug, type(mplug)))
        return False
    return True


def get_parent_plug(mplug):
    # tx -> t

    if not is_valid_mplug(mplug):
        return None

    mplug_parent = None

    if mplug.isChild:
        mplug_parent = mplug.parent()

    return mplug_parent


def get_child_plug(mplug, child):
    # t -> tx

    if not is_valid_mplug(mplug):
        return None

    child_plugs = get_child_plugs(mplug)

    for child_plug in child_plugs:
        if str(child_plug).endswith("." + child):
            return child_plug

    return None


def get_child_plugs(mplug):
    # t -> [tx, ty, tz]

    if not is_valid_mplug(mplug):
        return None

    child_plugs = []

    if mplug.isCompound:
        num_children = mplug.numChildren()
        for child_index in range(num_children):
            child_plugs.append(mplug.child(child_index))

    return child_plugs


def get_mplug_of_mobj(mobj, attr):
    node_mfn_dep_node = OpenMaya.MFnDependencyNode(mobj)

    if node_mfn_dep_node.hasAttribute(attr):
        return node_mfn_dep_node.findPlug(attr, False)  # attr, wantNetworkedPlug
    else:
        return None


def get_elements_of_array_plug(mplug):
    # input3D -> input3D[0], input3D[1], ...
    if not is_valid_mplug(mplug):
        return None

    array_elements = []

    if mplug.isArray:
        num_elements = mplug.evaluateNumElements()
        for element_index in range(num_elements):
            mplug_element = mplug.elementByPhysicalIndex(element_index)
            array_elements.append(mplug_element)

    return array_elements


def get_array_plug_by_physical_index(mplug, index):
    """
    The index can range from 0 to numElements() - 1.
    This function is particularly useful for iteration through the element plugs of an array plug.
    This function will NOT create a plug if it doesn't exist!
    # input3D -> input3D[0]
    """
    if not is_valid_mplug(mplug):
        return None

    if mplug.isArray:
        num_elements = mplug.evaluateNumElements()
        if num_elements > index:
            return mplug.elementByPhysicalIndex(index)

    return None


def get_array_plug_by_logical_index(mplug, index):
    """
    The logical index is the sparse array index used in MEL scripts.
    If a plug does not exist at the given Index, Maya will create a plug at that index.
    # input3D -> input3D[0]
    """
    if not is_valid_mplug(mplug):
        return None

    if mplug.isArray:
        return mplug.elementByLogicalIndex(index)
    else:
        log.error("{} is not an array plug!".format(mplug))


# def get_array_plug_of_element(mplug):
#     # input3D[0].input3Dx -> input3D[0]
#     if not is_valid_mplug(mplug):
#         return None

#     array_plug = None

#     if mplug.isElement:
#         array_plug = mplug.logicalIndex()

#     return array_plug


def get_mplug_of_node_and_attr(node, attr):
    """
    This should find the correct mplug for any node, attr input: "pCube1", "tx"

    """
    mobj = get_mobj_of_node(node)

    parent_attr, array_index, child_attr = split_attr_string(attr)
    mplug = get_mplug_of_mobj(mobj, parent_attr)

    if not mplug:
        log.error("mplug {}.{} does not seem to exist!".format(node, attr))

    if array_index is not None:
        if not mplug.isArray:
            log.error("mplug for {}.{} is supposed to have an index, but is not an array attr!".format(node, attr))
        mplug = get_array_plug_by_logical_index(mplug, array_index)

    if child_attr:
        if not mplug.numChildren():
            log.error("mplug for {}.{} is supposed to have children, but is not a parent attr!".format(node, attr))
        mplug = get_child_plug(mplug, child_attr)

    return mplug


def get_mplug_of_plug(plug):
    """
    This should find the correct mplug for any plug input: "pCube1.tx"

    """
    if isinstance(plug, OpenMaya.MPlug):
        return plug

    node, attr = plug.split(".", 1)
    mplug = get_mplug_of_node_and_attr(node, attr)

    return mplug


def split_plug_string(plug):
    """
    "namespace:some|dag|path|node.parentAttr[arrayIndex].childAttr" ->
    (namespace, dag_path, node, parent_attr, array_index, child_attr)
    """

    node, attr = plug.split(".", 1)

    namespace, dag_path, node = split_node_string(node)
    parent_attr, array_index, child_attr = split_attr_string(attr)

    return (namespace, dag_path, node, parent_attr, array_index, child_attr)


def split_attr_string(attr):
    """
    "parentAttr[arrayIndex].childAttr" ->
    (parent_attr, array_index, child_attr)
    """
    attr_pattern = re.compile(r"(\w+)(\[\d+\])?\.?(\w+)?")

    matches = attr_pattern.findall(attr)

    if not matches:
        log.error("Attr {} could not be broken down into components!".format(attr))

    if len(matches) > 1:
        log.error("Attr {} yielded multiple results. Should be singular result!".format(attr))

    parent_attr, array_index, child_attr = matches[0]

    if array_index:
        array_index_pattern = re.compile('(\d+)')
        array_index = int(array_index_pattern.findall(array_index)[0])
    else:
        array_index = None

    return (parent_attr, array_index, child_attr)


def split_node_string(node):
    """
    "namespace:some|dag|path|node" ->
    (namespace, dag_path, node)
    """
    node_pattern = re.compile(r"(\w+:)?\|?((?:\w+\|)*)?(\w+)")

    matches = node_pattern.findall(node)

    if not matches:
        log.error("Node {} could not be broken down into components!".format(node))

    if len(matches) > 1:
        log.error("Node {} yielded multiple results. Should be singular result!".format(node))

    namespace, dag_path, node = matches[0]

    if namespace:
        namespace = namespace.split(":")[0]

    return (namespace, dag_path, node)
