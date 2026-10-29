import sys
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from server.security.policies import AccessDenied, Principal, authorize_device
from runtime.finance.wdk.adapter import WDKAdapter, WDKNotInstalled
from runtime.intelligence.qvac.adapter import QVACAdapter, QVACNotInstalled

class SecurityContractTests(unittest.TestCase):
    def test_wrong_identity_denied(self):
        with self.assertRaises(AccessDenied):
            authorize_device(Principal('user-a', 'device-a'), 'user-b')
    def test_revoked_device_denied(self):
        with self.assertRaises(AccessDenied):
            authorize_device(Principal('user-a', 'device-a', False), 'user-a')
    def test_qvac_stub_never_fakes_response(self):
        with self.assertRaises(QVACNotInstalled):
            QVACAdapter().infer('hello', {})
    def test_wdk_stub_never_fakes_transaction(self):
        with self.assertRaises(WDKNotInstalled):
            WDKAdapter().prepare_transaction({})
