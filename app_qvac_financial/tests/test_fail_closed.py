import sys
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.orchestrator import AgentOrchestrator, CapabilityUnavailable
from runtime.security.policy import AuthorizationRequired, require_explicit_local_approval
from runtime.connectivity.sync_engine import SyncNotConfigured, synchronize

class FailClosedTests(unittest.TestCase):
    def test_missing_qvac_fails(self):
        with self.assertRaises(CapabilityUnavailable):
            AgentOrchestrator().analyze("balance")

    def test_missing_wdk_fails(self):
        with self.assertRaises(CapabilityUnavailable):
            AgentOrchestrator().prepare_transfer({})

    def test_agent_cannot_approve(self):
        with self.assertRaises(AuthorizationRequired):
            require_explicit_local_approval(approved=True, actor="agent")

    def test_sync_disabled(self):
        with self.assertRaises(SyncNotConfigured):
            synchronize()
