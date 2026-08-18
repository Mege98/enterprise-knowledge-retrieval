"""Release-readiness checks that do not require GUI dependencies."""
from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APP = ROOT / "enterprise_knowledge_retrieval.py"


class ReleaseReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = APP.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_direct_start_opens_main_window_without_arguments(self) -> None:
        main = next(node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
        calls = [
            node for node in ast.walk(main)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "MainWindow"
        ]
        self.assertEqual(len(calls), 1)
        self.assertFalse(calls[0].args)
        self.assertFalse(calls[0].keywords)

    def test_source_and_filenames_are_brand_neutral(self) -> None:
        tokens = [("义" + "和"), ("车" + "桥"), ("yi" + "he"), ("ax" + "le")]
        text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in ROOT.glob("*.py"))
        names = "\n".join(path.name for path in ROOT.iterdir())
        for token in tokens:
            self.assertNotIn(token.casefold(), text.casefold())
            self.assertNotIn(token.casefold(), names.casefold())

    def test_no_hard_coded_windows_user_path(self) -> None:
        sources = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in ROOT.glob("*.py"))
        self.assertIsNone(re.search(r"[A-Za-z]:\\Users\\[^\\]+", sources))

    def test_launcher_does_not_log_process_path_or_environment_path(self) -> None:
        launcher = (ROOT / "launcher.py").read_text(encoding="utf-8")
        self.assertNotIn('f"PATH:', launcher)
        self.assertNotIn('f"Working directory:', launcher)
        self.assertNotIn('f"Python: {sys.executable}', launcher)


if __name__ == "__main__":
    unittest.main()
