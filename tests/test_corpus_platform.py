"""Platform selection and real installer/fallback call sites; no network needed."""
from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import poetry_library as lib
import setup_poetry_library as setup


class TestCorpusPlatform(unittest.TestCase):
    def test_native_paths_for_both_platforms(self):
        root = Path("corpus") / "venv"
        self.assertEqual(lib.venv_python(root, "nt"), root / "Scripts" / "python.exe")
        self.assertEqual(lib.venv_python(root, "posix"), root / "bin" / "python")

    def test_installer_uses_selected_interpreter_for_pip_and_index(self):
        for platform in ("nt", "posix"):
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as temp:
                home = Path(temp).resolve()
                (home / "chinese-poetry").mkdir()
                python = lib.venv_python(home / "venv", platform)
                python.parent.mkdir(parents=True)
                python.touch()
                with patch.object(setup, "verify_source"), patch.object(setup, "venv_python", return_value=python), \
                     patch.object(setup.subprocess, "run") as run, redirect_stdout(io.StringIO()):
                    self.assertEqual(setup.main(["--home", str(home)]), 0)
                self.assertEqual([c.args[0][0] for c in run.call_args_list], [str(python)] * 2)
                self.assertIn("pip", run.call_args_list[0].args[0])
                self.assertEqual(run.call_args_list[1].args[0][-1], "index")

    def test_missing_dependency_reexecs_using_platform_interpreter(self):
        for platform in ("nt", "posix"):
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as temp:
                home = Path(temp)
                python = lib.venv_python(home / "venv", platform)
                python.parent.mkdir(parents=True)
                python.touch()
                with patch.dict(sys.modules, {"opencc": None}), \
                     patch.object(lib, "venv_python", return_value=python), \
                     patch.object(lib.os, "execv") as execute:
                    lib.ensure_optional_python(home)
                self.assertEqual(execute.call_args.args[0], str(python))
                self.assertEqual(execute.call_args.args[1][2:], sys.argv[1:])

    def test_same_interpreter_does_not_reexec_forever(self):
        with patch.dict(sys.modules, {"opencc": None}), \
             patch.object(lib, "venv_python", return_value=Path(sys.executable)), \
             patch.object(lib.os, "execv") as execute:
            lib.ensure_optional_python(Path("unused"))
        execute.assert_not_called()

    def test_missing_venv_does_not_select_another_platform_or_spawn(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(sys.modules, {"opencc": None}), \
             patch.object(lib.os, "execv") as execute:
            lib.ensure_optional_python(Path(temp))
        execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
