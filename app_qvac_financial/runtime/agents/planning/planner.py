"""Structured offline planning; requires genuine QVAC adapter for language analysis."""
from dataclasses import dataclass

@dataclass(frozen=True)
class PlanStep:
    title: str
    requires_network: bool
    requires_human_approval: bool

class FinancialPlanner:
    def build_review_plan(self):
        return (
            PlanStep("Analyze locally with installed QVAC model", False, False),
            PlanStep("Validate intended operation and risk", False, False),
            PlanStep("Fetch current chain state and fees", True, False),
            PlanStep("Review and authorize final transaction", False, True),
            PlanStep("Sign locally and broadcast", True, True),
        )
