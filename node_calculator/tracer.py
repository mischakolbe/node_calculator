"""Trace Maya commands executed by the NodeCalculator to return to the user.

Note:
    The actual Tracer class is in core.py because it is mutually linked to
    other classes in core.py and would cause cyclic references or tedious
    workarounds to fix.

:author: Mischa Kolbe <mischakolbe@gmail.com>
"""

# IMPORTS ---
# Python imports
from __future__ import absolute_import

# Third party imports

# Local imports
from node_calculator import om_util


class TracerMObject(object):
    """Class that allows to store metadata with MObjects, used for the Tracer.

    Note:
        The Tracer uses variable names for created nodes. This class is an easy
        and convenient way to store these variable names with the MObject.
    """

    def __init__(self, node, tracer_variable):
        """TracerMObject-class constructor.

        Args:
            node (MObject): Maya MObject
            tracer_variable (str): Variable name for this MObject.
        """
        super(TracerMObject, self).__init__()
        self.mobj = om_util.get_mobj(node)
        self._tracer_variable = tracer_variable

    @property
    def node(self):
        """Get name of Maya node this TracerMObject refers to.

        Returns:
            str: Name of Maya node in the scene.
        """
        return om_util.get_name_of_mobj(self.mobj)

    @property
    def tracer_variable(self):
        """Get variable name of this TracerMObject.

        Returns:
            str: Variable name the NodeCalculator associated with this MObject.
        """
        return self._tracer_variable
