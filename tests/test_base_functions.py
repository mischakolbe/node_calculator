"""Unit tests for noca.Op (from base_functions.py)"""
import math

from base import BaseTestCase
import node_calculator.core as noca


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBALS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


REGULAR_TEST_ANGLES = range(-360, 360, 45)
CUSTOM_TEST_ANGLES = [-361, -123, -12, 12, 123, 361, 3.1, 271.5, -35.1, -404.1]
TRIGONOMETRY_ANGLE_TEST_VALUES = REGULAR_TEST_ANGLES + CUSTOM_TEST_ANGLES


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TestFunctions(BaseTestCase):
    """Test base functions of the Op class."""

    def setUp(self):
        super(TestFunctions, self).setUp()

        # Create standard nodes on which to perform the operations on.
        # Transform test nodes
        self.tf_out_a = noca.create_node("transform", name="transform_out_A")
        self.tf_out_b = noca.create_node("transform", name="transform_out_B")
        self.tf_in_a = noca.create_node("transform", name="transform_in_A")
        self.tf_in_b = noca.create_node("transform", name="transform_in_B")

        # Matrix test nodes
        self.mat_out_a = noca.create_node("holdMatrix", name="matrix_out_A")
        self.mat_out_b = noca.create_node("holdMatrix", name="matrix_out_B")
        self.mat_in_a = noca.create_node("holdMatrix", name="matrix_in_A")

        # Quaternion test nodes
        self.quat_out_a = noca.create_node("eulerToQuat", name="quaternion_out_A")
        self.quat_out_b = noca.create_node("eulerToQuat", name="quaternion_out_B")
        self.quat_in_a = noca.create_node("quatNormalize", name="quaternion_in_A")

        # Mesh, curve and nurbsSurface test nodes
        self.mesh_out_a = noca.create_node("mesh", name="mesh_out_A")
        self.mesh_shape_out_a = noca.Node("mesh_out_AShape")
        self.curve_out_a = noca.create_node("nurbsCurve", name="curve_out_A")
        self.curve_shape_out_a = noca.Node("curve_out_AShape")
        self.surface_out_a = noca.create_node("nurbsSurface", name="surface_out_A")
        self.surface_shape_out_a = noca.Node("surface_out_AShape")

    def test_smooth_step(self):
        """ """
        fade_in_range = 0.5
        target_value = 1
        self.tf_in_a.tx = noca.Op.soft_approach(
            self.tf_out_a.tx, fade_in_range=fade_in_range, target_value=target_value
        )

        # Check whether value matches when out of range.
        self.tf_out_a.tx = -1
        self.assertEqual(-1, self.tf_in_a.tx.get())

        self.tf_out_a.tx = 0.5
        self.assertEqual(0.5, self.tf_in_a.tx.get())
        
        # Check whether value slowly approaches target value when in range.
        self.tf_out_a.tx = 0.501
        self.assertLess(self.tf_in_a.tx.get(), 0.501)
        
        self.tf_out_a.tx = 1
        self.assertLess(self.tf_in_a.tx.get(), 1)

        self.tf_out_a.tx = 100
        self.assertAlmostEqual(1, self.tf_in_a.tx.get())

    def test_sin(self):
        """ """
        # Due to potential unit conversion nodes: Test scalar and angle plugs.
        self.tf_in_a.ty = noca.Op.sin(self.tf_out_a.tx)
        self.tf_in_a.rz = noca.Op.sin(self.tf_out_a.ry)

        for test_angle in TRIGONOMETRY_ANGLE_TEST_VALUES:
            desired_value = math.sin(math.radians(test_angle))

            self.tf_out_a.tx = test_angle
            self.assertAlmostEqual(desired_value, self.tf_in_a.ty.get(), places=6)

            self.tf_out_a.ry = test_angle
            self.assertAlmostEqual(desired_value, self.tf_in_a.rz.get(), places=6)

    def test_cos(self):
        """ """
        # Due to potential unit conversion nodes: Test scalar and angle plugs.
        self.tf_in_a.ty = noca.Op.cos(self.tf_out_a.tx)
        self.tf_in_a.rz = noca.Op.cos(self.tf_out_a.ry)

        for test_angle in TRIGONOMETRY_ANGLE_TEST_VALUES:
            desired_value = math.cos(math.radians(test_angle))

            self.tf_out_a.tx = test_angle
            self.assertAlmostEqual(desired_value, self.tf_in_a.ty.get(), places=6)

            self.tf_out_a.ry = test_angle
            self.assertAlmostEqual(desired_value, self.tf_in_a.rz.get(), places=6)

    def test_tan(self):
        """ """
        # Due to potential unit conversion nodes: Test scalar and angle plugs.
        self.tf_in_a.ty = noca.Op.tan(self.tf_out_a.tx)
        self.tf_in_a.rz = noca.Op.tan(self.tf_out_a.ry)

        for test_angle in TRIGONOMETRY_ANGLE_TEST_VALUES:
            desired_value = math.tan(math.radians(test_angle))
            # NoCa uses 0 in the undefined areas that go towards +/-infinity.
            if abs(desired_value) > 1e15:
                desired_value = 0

            self.tf_out_a.tx = test_angle
            self.assertAlmostEqual(desired_value, self.tf_in_a.ty.get(), places=4)

            self.tf_out_a.ry = test_angle
            self.assertAlmostEqual(desired_value, self.tf_in_a.rz.get(), places=4)

    def test_asin(self):
        """ """
        # Due to potential unit conversion nodes: Test scalar and angle plugs.
        self.tf_in_a.ty = noca.Op.asin(self.tf_out_a.tx)
        self.tf_in_a.rz = noca.Op.asin(self.tf_out_a.ry)

        for test_angle in TRIGONOMETRY_ANGLE_TEST_VALUES:
            test_scalar = math.sin(math.radians(test_angle))
            desired_value = math.degrees(math.asin(test_scalar))

            self.tf_out_a.tx = test_scalar
            self.assertAlmostEqual(desired_value, self.tf_in_a.ty.get(), places=4)

            self.tf_out_a.ry = test_scalar
            self.assertAlmostEqual(desired_value, self.tf_in_a.rz.get(), places=4)

    def test_acos(self):
        """ """
        # Due to potential unit conversion nodes: Test scalar and angle plugs.
        self.tf_in_a.ty = noca.Op.acos(self.tf_out_a.tx)
        self.tf_in_a.rz = noca.Op.acos(self.tf_out_a.ry)

        for test_angle in TRIGONOMETRY_ANGLE_TEST_VALUES:
            test_scalar = math.cos(math.radians(test_angle))
            desired_value = math.degrees(math.acos(test_scalar))

            self.tf_out_a.tx = test_scalar
            self.assertAlmostEqual(desired_value, self.tf_in_a.ty.get(), places=4)

            self.tf_out_a.ry = test_scalar
            self.assertAlmostEqual(desired_value, self.tf_in_a.rz.get(), places=4)

    def test_atan(self):
        """ """
        # Due to potential unit conversion nodes: Test scalar and angle plugs.
        self.tf_in_a.ty = noca.Op.atan(self.tf_out_a.tx)
        self.tf_in_a.rz = noca.Op.atan(self.tf_out_a.ry)

        for test_angle in TRIGONOMETRY_ANGLE_TEST_VALUES:
            test_scalar = math.tan(math.radians(test_angle))
            desired_value = math.degrees(math.atan(test_scalar))

            self.tf_out_a.tx = test_scalar
            self.assertAlmostEqual(desired_value, self.tf_in_a.ty.get(), places=5)

            self.tf_out_a.ry = test_scalar
            self.assertAlmostEqual(desired_value, self.tf_in_a.rz.get(), places=5)

    def test_atan2(self):
        """ """
        self.tf_in_a.ty = noca.Op.atan2(self.tf_out_a.ty, self.tf_out_a.tx)

        for test_angle in TRIGONOMETRY_ANGLE_TEST_VALUES:
            test_scalar_x = math.cos(math.radians(test_angle))
            test_scalar_y = math.sin(math.radians(test_angle))
            desired_value = math.degrees(math.atan2(test_scalar_y, test_scalar_x))

            self.tf_out_a.tx = test_scalar_x
            self.tf_out_a.ty = test_scalar_y
            self.assertAlmostEqual(desired_value, self.tf_in_a.ty.get(), places=5)
