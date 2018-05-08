# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports
import copy

# Third party imports
import maya.api.OpenMaya as om
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
    node_fn = om.MFnDependencyNode(mobj)
    node_name = node_fn.name()

    return node_name


def get_shape_mobjs_of_mobj(mobj):
    num_shapes = get_mdag_path_of_mobj(mobj).numberOfShapesDirectlyBelow()

    return_shape_mobjs = []
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
    if mobj.hasFn(om.MFn.kDagNode):
        mdag_path = om.MDagPath.getAPathTo(mobj)
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
    if not isinstance(mobj, om.MObject):
        log.error("Given mobj {} is not an instance of om.MObject".format(mobj))

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
    if type(node) is om.MObject:
        return node

    selectionList = om.MSelectionList()
    selectionList.add(node)
    mobj = selectionList.getDependNode(0)

    return mobj


def get_all_mobjs_of_type(dependency_node_type):
    """
    dependency_node_type must be of "type" OpenMaya.MFn: OpenMaya.MFn.kDependencyNode etc.
    """
    dep_node_iterator = om.MItDependencyNodes(dependency_node_type)
    return_list = []
    while not dep_node_iterator.isDone():
        mobj = dep_node_iterator.thisNode()
        return_list.append(mobj)
        dep_node_iterator.next()

    return return_list


def rename_mobj(mobj, name):
    dag_modifier = om.MDagModifier()
    dag_modifier.renameNode(mobj, name)
    dag_modifier.doIt()


def set_mobj_attribute(mobj, attr, value):
    # This should be om-only, too!
    # http://austinjbaker.com/mplugs-setting-values
    dag_path = get_long_name_of_mobj(mobj)
    cmds.setAttr("{}.{}".format(dag_path, attr), value)


def selected_nodes_in_scene_as_mobjs():
    mobjs = []

    selection_list = om.MGlobal.getActiveSelectionList()
    if selection_list.length() > 0:
        iterator = om.MItSelectionList(selection_list, om.MFn.kDagNode)
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
    # m_selection_list = om.MSelectionList()
    # for mobj in mobjs:
    #     m_selection_list.add(mobj)
    # om.MGlobal.setActiveSelectionList(m_selection_list, om.MGlobal.kReplaceList)
    # return m_selection_list

    select_list = []
    for mobj in mobjs:
        select_list.append(get_long_name_of_mobj(mobj))
    cmds.select(select_list)
    return select_list
