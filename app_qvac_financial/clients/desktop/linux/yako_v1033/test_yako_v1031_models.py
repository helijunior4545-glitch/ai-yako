import tempfile
import unittest
from pathlib import Path
from yako_v1031_models import capabilities,hardware_report

class ModelSafetyTests(unittest.TestCase):
    def test_low_memory_pressure(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'meminfo';p.write_text('MemTotal: 3800000 kB\nMemAvailable: 900000 kB\nSwapTotal: 4000000 kB\nSwapFree: 1200000 kB\n')
            r=hardware_report(p)
            self.assertEqual(r['memory_pressure'],'high')
            self.assertEqual(r['ram_available_mib'],878)
            self.assertFalse(r['model_fit_verified'])
    def test_no_unverified_models_enabled(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'meminfo';p.write_text('MemTotal: 32000000 kB\nMemAvailable: 25000000 kB\n')
            r=capabilities(p)
            self.assertEqual(r['active_backend'],'qvac-sdk')
            self.assertEqual([m['id'] for m in r['models'] if m['state']=='active'],['qvac-llama-3.2-1b-q4_0'])
            self.assertFalse(r['automatic_downloads'])
            self.assertFalse(r['cloud_inference_enabled'])
            self.assertFalse(r['model_switching_implemented'])
    def test_missing_meminfo_fails_conservatively(self):
        r=hardware_report('/no/such/file')
        self.assertIsNone(r['ram_available_mib'])
        self.assertEqual(r['memory_pressure'],'unknown')
    def test_server_endpoint_registered(self):
        s=(Path(__file__).parent/'yako_v102_server.py').read_text()
        self.assertIn("url.path=='/api/model-capabilities'",s)
        self.assertIn('model_capabilities()',s)
if __name__=='__main__':unittest.main()
