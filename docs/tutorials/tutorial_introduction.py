# INTRODUCTION


import node_calculator.core as noca

# Initiate Node-objects for all test-geos
a_geo = noca.Node("A_geo")
b_geo = noca.Node("B_geo")
c_geo = noca.Node("C_geo")

# Average all directions of the A-translation
translate_a_average = noca.Op.average(a_geo.tx, a_geo.ty, a_geo.tz)
# Create a "floor collider" based on the height of B
b_height_condition = noca.Op.condition(b_geo.ty > 0, b_geo.ty, 0)

# Drive C-translation by different example-formula for each direction
c_geo.translate = [b_geo.tx / 2 - 2, b_height_condition * 2, translate_a_average]


# ~~~ VS ~~~


from maya import cmds

# Average all directions of the A-translation
var1 = cmds.createNode("plusMinusAverage", name="A_translate_average")
cmds.setAttr(var1 + ".operation", 3)
cmds.connectAttr("A_geo.tx", var1 + ".input3D[0].input3Dx", force=True)
cmds.connectAttr("A_geo.ty", var1 + ".input3D[1].input3Dx", force=True)
cmds.connectAttr("A_geo.tz", var1 + ".input3D[2].input3Dx", force=True)

# Create a "floor collider" based on the height of B
var2 = cmds.createNode("condition", name="height_condition")
cmds.setAttr(var2 + ".operation", 2)
cmds.connectAttr("B_geo.ty", var2 + ".firstTerm", force=True)
cmds.setAttr(var2 + ".secondTerm", 0)
cmds.connectAttr("B_geo.ty", var2 + ".colorIfTrueR", force=True)
cmds.setAttr(var2 + ".colorIfFalseR", 0)

# Drive C-translation by different example-formula for each direction
var3 = cmds.createNode("multiplyDivide", name="half_B_tx")
cmds.setAttr(var3 + ".operation", 2)
cmds.connectAttr("B_geo.tx", var3 + ".input1X", force=True)
cmds.setAttr(var3 + ".input2X", 2)
var4 = cmds.createNode("plusMinusAverage", name="offset_half_b_tx_by_2")
cmds.setAttr(var4 + ".operation", 2)
cmds.connectAttr(var3 + ".outputX", var4 + ".input3D[0].input3Dx", force=True)
cmds.setAttr(var4 + ".input3D[1].input3Dx", 2)
var5 = cmds.createNode("multiplyDivide", name="double_height_condition")
cmds.setAttr(var5 + ".operation", 1)
cmds.connectAttr(var2 + ".outColorR", var5 + ".input1X", force=True)
cmds.setAttr(var5 + ".input2X", 2)
cmds.connectAttr(var4 + ".output3Dx", "C_geo.translateX", force=True)
cmds.connectAttr(var5 + ".outputX", "C_geo.translateY", force=True)
cmds.connectAttr(var1 + ".output3Dx", "C_geo.translateZ", force=True)
