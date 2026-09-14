import py_compile
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("recommend.py")


class DemoCoordinateRegressionTest(unittest.TestCase):
    def test_recommend_module_compiles(self) -> None:
        py_compile.compile(str(SCRIPT), doraise=True)

    def test_offline_demo_runs_with_two_coordinates(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--demo"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("37.5301, 127.1236", result.stdout)


if __name__ == "__main__":
    unittest.main()
