"""Explainable deterministic checks, not financial advice or a risk prediction model."""
from dataclasses import dataclass
from .. import __name__ as _package
from ...security.authorization.intent import FinancialIntent

@dataclass(frozen=True)
class RiskFinding:
    code: str
    severity: str
    explanation: str

def evaluate_intent(intent: FinancialIntent, *, max_base_units: int) -> list[RiskFinding]:
    findings = []
    if intent.amount_base_units > max_base_units:
        findings.append(RiskFinding("LIMIT_EXCEEDED", "block", "Amount exceeds configured test limit"))
    if intent.network != "testnet":
        findings.append(RiskFinding("NETWORK_NOT_TEST", "block", "Only testnet is supported"))
    return findings
