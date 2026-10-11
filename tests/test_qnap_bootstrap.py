import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from deploy.qnap import bootstrap_site


class TestQnapSiteBootstrap(unittest.TestCase):
	def test_rejects_invalid_site_name_before_reading_secrets(self):
		with patch.object(sys, "argv", ["bootstrap_site.py", "../outside"]):
			with self.assertRaisesRegex(SystemExit, "unsupported characters"):
				bootstrap_site.main()

	def test_refuses_to_overwrite_existing_site_path(self):
		with tempfile.TemporaryDirectory() as temp_dir:
			old_cwd = Path.cwd()
			try:
				os.chdir(temp_dir)
				Path("sites/existing.localhost").mkdir(parents=True)
				with patch.object(sys, "argv", ["bootstrap_site.py", "existing.localhost"]):
					with self.assertRaisesRegex(SystemExit, "refusing to overwrite"):
						bootstrap_site.main()
			finally:
				os.chdir(old_cwd)


if __name__ == "__main__":
	unittest.main()
