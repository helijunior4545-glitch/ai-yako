"""Fail-closed orchestration skeleton. No simulated financial execution."""
class CapabilityUnavailable(RuntimeError):
    pass

class AgentOrchestrator:
    def __init__(self, inference=None, wallet=None):
        self.inference = inference
        self.wallet = wallet

    def analyze(self, request: str) -> str:
        if self.inference is None:
            raise CapabilityUnavailable("QVAC inference adapter is not installed")
        return self.inference.infer(request, {})

    def prepare_transfer(self, intent):
        if self.wallet is None:
            raise CapabilityUnavailable("WDK wallet adapter is not installed")
        return self.wallet.prepare_transaction(intent)
