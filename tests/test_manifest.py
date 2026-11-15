"""Integration import policy regression tests."""
import json
from pathlib import Path
import unittest


class ManifestTest(unittest.TestCase):
    def test_imports_use_executor(self):
        path = Path(__file__).parents[1] / "custom_components/rainbow_weather/manifest.json"
        manifest = json.loads(path.read_text())
        self.assertIs(manifest.get("import_executor"), True)
