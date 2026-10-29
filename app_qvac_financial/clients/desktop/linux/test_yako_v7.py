import tempfile
import unittest
from pathlib import Path
from yako_v7_engine import analyze, digest

class V7Tests(unittest.TestCase):
    def test_rules_offline(self):
        r=analyze('urgent guaranteed leverage')
        self.assertEqual(len(r['rules']['flags']),3)
        self.assertIsNone(r['local_inference'])
        self.assertFalse(r['qvac_official_integration'])
    def test_empty(self):
        with self.assertRaises(ValueError): analyze('   ')
    def test_incomplete_runner(self):
        with self.assertRaises(ValueError): analyze('test',runner='/tmp/runner')
    def test_digest(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sample'; p.write_bytes(b'abc')
            self.assertEqual(digest(p),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
    def test_length(self):
        with self.assertRaises(ValueError): analyze('x'*12001)
if __name__=='__main__': unittest.main()
