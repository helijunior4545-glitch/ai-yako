import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = ("django", "app_config", "app_billing", "app_whatsapp_ops", "app_qvac_financial.server")

class ArchitectureTests(unittest.TestCase):
    def test_local_runtime_import_boundary(self):
        for folder in (ROOT / "runtime", ROOT / "shared"):
            for file in folder.rglob("*.py"):
                tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
                for node in ast.walk(tree):
                    names = []
                    if isinstance(node, ast.Import):
                        names = [item.name for item in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        names = [node.module or ""]
                    for name in names:
                        self.assertFalse(any(name == f or name.startswith(f + ".") for f in FORBIDDEN), f"Forbidden import {name} in {file}")

    def test_no_commercial_model_dependency(self):
        for file in (ROOT / "server" / "django" / "models").rglob("*.py"):
            self.assertNotIn("app_config.Loja", file.read_text(encoding="utf-8"))
