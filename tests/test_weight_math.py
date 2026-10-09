"""Actual pure-module tests; no Maya/Qt imports or source-body substitution."""
import subprocess
import sys
import unittest
from Maya.tools import weightMath


class WeightMathTests(unittest.TestCase):
    def test_import_has_no_host_or_ui_dependency(self):
        code = "from Maya.tools import weightMath; import sys; assert not any(n.startswith(('maya', 'PySide', 'PyQt', 'SkinningTools.UI')) for n in sys.modules)"
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_normalization_preserves_locks_zero_and_rejects_impossible_budget(self):
        source = [0.2, 0.3, 0.1]
        self.assertEqual(weightMath.normalizeWeights(source, [False, True, False]),
                         [0.4666666666666666, 0.3, 0.2333333333333333])
        self.assertEqual(source, [0.2, 0.3, 0.1])
        flat = [1, 0, 0.2, 0.3, 0.1, 1, 0]
        weightMath.normalizeWeightsInPlace(flat, [False, True, False], offset=2)
        self.assertEqual(flat, [1, 0, 0.4666666666666666, 0.3, 0.2333333333333333, 1, 0])
        self.assertEqual(weightMath.normalizeWeights([0, 0], [False, False]), [0, 0])
        for values, locks in (([0.8, 0.8, 0], [True, True, False]),
                              ([0.2, 0], [True, False])):
            with self.assertRaises(ValueError):
                weightMath.normalizeWeights(values, locks)

    def test_per_row_limits_preserve_locks_and_break_ties_by_position(self):
        self.assertEqual(weightMath.limitInfluences([0.5, 0.5, 0.1], [False]*3, 1), [0.5, 0, 0])
        self.assertEqual(weightMath.limitInfluences([0.5, 0.2, 0.3], [False, True, False], 2), [0.5, 0.2, 0])
        with self.assertRaises(ValueError):
            weightMath.limitInfluences([0.4, 0.3], [True, True], 1)

    def test_blend_integer_inputs_endpoints_and_invalid_payloads(self):
        self.assertEqual(weightMath.blendWeights(0.5, [1, 0], [0, 1, 1, 0], 2), [0.75, 0.25])
        self.assertEqual(weightMath.blendWeights(0, [0.2, 0.3], [0.4, 0.6], 1, True, 1), [0.2, 0.3])
        self.assertEqual(weightMath.blendWeights(1, [0.2, 0.3], [], 0, True, 1), [0.2, 0.3])
        for value in (float('nan'), float('inf'), -0.1, 1.1):
            with self.assertRaises(ValueError):
                weightMath.blendWeights(value, [0.2, 0.3], [0.4, 0.6], 1)
        with self.assertRaises(ValueError):
            weightMath.blendWeights(0.5, [0.2, 0.3], [0.4], 1)

    def test_table_selected_priority_locked_budget_and_zero_fallback(self):
        self.assertEqual(weightMath.normalizeEditedWeights([0.5, 0.5, 0.25], [0.25, 0.5, 0.25], [2], [0], [0, 1, 2]),
                         ([0.5, 0.25, 0.25], True))
        self.assertEqual(weightMath.normalizeEditedWeights([0, 0], [0, 0], [], [0], [0, 1]), ([0.0, 0.0], False))
        self.assertEqual(weightMath.normalizeEditedWeights([0.7, 0.4], [0.7, 0.3], [0, 1], [], [0, 1]), ([0.7, 0.4], True))

    def test_slider_policies_preserve_their_distinct_behavior(self):
        for actual, expected in zip(weightMath.sliderWeights([0.2, 0.3, 0.5], [True]*3, 0, 0.4), [0.4, 0.225, 0.375]):
            self.assertAlmostEqual(actual, expected, places=12)
        self.assertEqual(weightMath.sliderWeights([0.2, 0.3, 0.5], [True, False, True], 0, 0.9), [0.7, 0.3, 0.0])
        high = weightMath.sliderWeights([0.2, 0.3, 0.5], [True]*3, 0, 0.4, 'high')
        for actual, expected in zip(high, [0.4, 0.1125, 0.3125]):
            self.assertAlmostEqual(actual, expected, places=12)
        self.assertEqual(weightMath.sliderWeights([1, 0, 0], [True]*3, 0, 0.4), [0.4, 0.3, 0.3])

    def test_value_validation_rejects_nonfinite_and_out_of_range(self):
        weightMath.validateWeights([0, 0.5, 1])
        for value in (float('nan'), float('inf'), -0.1, 1.1, '0.5'):
            with self.assertRaises(ValueError):
                weightMath.validateWeights([value])
