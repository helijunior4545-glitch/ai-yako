"""Deterministic financial policy; model output never authorizes signing."""
from dataclasses import dataclass
from .intent import FinancialIntent

class PolicyViolation(PermissionError): pass

@dataclass(frozen=True)
class Policy:
    allowed_networks: tuple[str,...] = ("testnet",)
    max_amount_base_units: int = 1_000_000_000

    def check(self, intent: FinancialIntent) -> None:
        if intent.network not in self.allowed_networks: raise PolicyViolation("Network not permitted")
        if intent.amount_base_units > self.max_amount_base_units: raise PolicyViolation("Amount exceeds policy")
