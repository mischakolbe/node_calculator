from maya import cmds


# LOAD NECESSARY PLUGINS ---
for required_plugin in ["matrixNodes"]:
    cmds.loadPlugin(required_plugin, quiet=True)
