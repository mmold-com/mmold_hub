import unittest

from mmold_hub.compatibility import IncompatibleRuntimeError, normalize_version, validate_versions


class TestCompatibility(unittest.TestCase):
	def test_approved_versions_are_accepted(self):
		validate_versions("16.36.0", "16.37.0")

	def test_optional_v_prefix_is_normalized(self):
		validate_versions("v16.36.0", "v16.37.0")
		self.assertEqual(normalize_version("v16.36.0"), "16.36.0")

	def test_frappe_version_mismatch_is_rejected(self):
		with self.assertRaises(IncompatibleRuntimeError):
			validate_versions("16.36.1", "16.37.0")

	def test_erpnext_version_mismatch_is_rejected(self):
		with self.assertRaises(IncompatibleRuntimeError):
			validate_versions("16.36.0", "16.37.1")

	def test_missing_version_is_rejected(self):
		with self.assertRaises(IncompatibleRuntimeError):
			validate_versions(None, "16.37.0")

	def test_mmold_hub_major_stays_ten_below_erpnext(self):
		validate_versions("16.36.0", "16.37.0", "6.37.0")
		with self.assertRaises(IncompatibleRuntimeError):
			validate_versions("16.36.0", "16.37.0", "5.37.0")


if __name__ == "__main__":
	unittest.main()
