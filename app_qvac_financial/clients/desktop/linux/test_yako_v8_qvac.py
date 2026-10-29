import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import yako_v8_qvac as v8

class QvacV8Tests(unittest.TestCase):
    def test_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'file.gguf'; p.write_bytes(b'hello')
            self.assertEqual(v8.sha256_file(p), '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824')
    def test_missing(self):
        with self.assertRaises(FileNotFoundError): v8.validate_model('/does/not/exist.gguf')
    def test_tiny(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'tiny.gguf'; p.write_bytes(b'bad')
            with self.assertRaises(ValueError): v8.validate_model(p)
    def test_empty_scenario(self):
        with self.assertRaises(ValueError): v8.qvac_infer(' ', '/missing.gguf')
    def test_sha_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'model.gguf'; p.write_bytes(b'x' * 2048)
            with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
                v8.qvac_infer('check this', p, '0' * 64)

if __name__ == '__main__': unittest.main()
