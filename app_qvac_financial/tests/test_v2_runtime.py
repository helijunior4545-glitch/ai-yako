import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PersistenceBoundaryTests(unittest.TestCase):
    def test_no_sqlite_store(self):
        self.assertFalse((ROOT / 'runtime/persistence/sqlite/store.py').exists())

    def test_host_wiring_documented(self):
        doc = (ROOT / 'docs/HOST_INTEGRATION.md').read_text(encoding='utf-8')
        self.assertIn('app_qvac_financial.urls', doc)
        self.assertIn('PostgreSQL', doc)
