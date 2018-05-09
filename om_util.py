# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python imports

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







# #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #
# #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #
# #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #
# #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #











def testDef(attr="input3D[1].input3Dx"):

    node_mobj = get_mobj_of_node("B")
    print node_mobj

    node_mfn_dep_node = om.MFnDependencyNode(node_mobj)
    print node_mfn_dep_node
    has_attr = node_mfn_dep_node.hasAttribute(attr)
    print has_attr



    if has_attr:
        print "~~~~~~"
        mplug = node_mfn_dep_node.findPlug(attr, False)  # attr, wantNetworkedPlug
        print mplug, type(mplug)

        is_array = mplug.isArray
        print "is_array:", is_array
        if is_array:
            # input3D[0] -> input3D[0].input3Dx
            num_elements = mplug.evaluateNumElements()
            for element_index in range(num_elements):
                mplug_element = mplug.elementByPhysicalIndex(element_index)
                print mplug_element # input1D[0]
                is_compound = mplug_element.isCompound
                print "is_compound:", is_compound
                if is_compound:
                    num_children = mplug_element.numChildren()
                    for child_index in range(num_children):

                        print mplug_element.child(child_index) # input3D[0].input3Dx

        is_element = mplug.isElement
        print "is_element:", is_element
        if is_element:
            # input3D[0].input3Dx -> input3D[0]
            print mplug.logicalIndex()

        is_compound = mplug.isCompound
        print "is_compound:", is_compound
        if is_compound:
            # t -> tx, ty, tz
            num_children = mplug.numChildren()
            for child_index in range(num_children):

                print mplug.child(child_index)
        is_child = mplug.isChild
        print "is_child:", is_child
        if is_child:
            # tx -> t
            mplug_parent = mplug.parent()
            print mplug_parent


# #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #
# #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #
# #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #
# #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #  ## #  #


def is_valid_mplug(mplug):

    if not isinstance(mplug, om.MPlug):
        cmds.error("Expected an MPlug, got {} of type {}".format(mplug, type(mplug)))
        return False
    return True


def find_parent_plug(mplug):
    # tx -> t

    if not is_valid_mplug(mplug):
        return False

    mplug_parent = None

    if mplug.isChild:
        mplug_parent = mplug.parent()

    return mplug_parent


def find_child_plugs(mplug):
    # t -> tx, ty, tz

    if not is_valid_mplug(mplug):
        return False

    child_plugs = []

    if mplug.isCompound:
        num_children = mplug.numChildren()
        for child_index in range(num_children):
            child_plugs.append(mplug.child(child_index))

    return child_plugs


def get_mplug_of_mobj(mobj, attr):
    node_mfn_dep_node = om.MFnDependencyNode(mobj)

    if node_mfn_dep_node.hasAttribute(attr):
        return node_mfn_dep_node.findPlug(attr, False)  # attr, wantNetworkedPlug
    else:
        return None


def find_elements_of_array_plug(mplug):
    # input3D -> input3D[0].input3Dx, input3D[0].input3Dy, ...
    if not is_valid_mplug(mplug):
        return False

    array_elements = []

    if mplug.isArray:
        num_elements = mplug.evaluateNumElements()
        for element_index in range(num_elements):
            mplug_element = mplug.elementByPhysicalIndex(element_index)
            array_elements.append(mplug_element)

    return array_elements


def find_array_plug_of_element(mplug):
    # input3D[0].input3Dx -> input3D[0]
    if not is_valid_mplug(mplug):
        return False

    array_plug = None

    if mplug.isElement:
        array_plug = mplug.logicalIndex()

    return array_plug


def get_parent_plug_of_node(node, attr):
    node_mobj = get_mobj_of_node(node)
    mplug = get_mplug_of_mobj(node_mobj, attr)

    return find_parent_plug(mplug)


def get_child_plugs_of_node(node, attr):
    node_mobj = get_mobj_of_node(node)
    mplug = get_mplug_of_mobj(node_mobj, attr)

    return find_child_plugs(mplug)


def get_array_plugs_of_node(node, attr):
    node_mobj = get_mobj_of_node(node)
    mplug = get_mplug_of_mobj(node_mobj, attr)

    return find_child_plugs(mplug)


def get_element_plugs_of_node(node, attr):
    node_mobj = get_mobj_of_node(node)
    mplug = get_mplug_of_mobj(node_mobj, attr)

    return find_elements_of_array_plug(mplug)


def check_attr(node, attr):
    # Get mplug-name: item.name()

    parent_plug = get_parent_plug_of_node(node, attr)
    if parent_plug:
        print "parent_plug:", parent_plug.name()

    child_plugs = get_child_plugs_of_node(node, attr)
    if child_plugs:
        print "child_plugs:", [x.name() for x in child_plugs]

    # array_plug = find_array_plug_of_element(node, attr)
    # if array_plug:
    #     print "array_plug:", [x.name() for x in array_plugs]

    element_plugs = get_element_plugs_of_node(node, attr)
    if element_plugs:
        print "element_plugs:", [x.name() for x in element_plugs]


check_attr(node="A", attr="t")


def find_mplug_of_attr(node, attr):
    """
    This should find the correct mplug for any attr input:

    t
    translate
    tx
    translateX
    input1D
    input1D[0]
    input3D
    input3D[0]
    input3D[1]
    input3D[0].input3Dx
    input3D[1].input3Dy
    """
    pass
