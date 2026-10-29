"""Deterministic intent validation; NO authorization or signing in this module."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from uuid import UUID

class InvalidIntent(ValueError): pass

@dataclass(frozen=True)
class FinancialIntent:
    intent_id: UUID
    chain: str
    destination: str
    asset: str
    amount_base_units: int
    network: str = "testnet"

    def __post_init__(self):
        if not isinstance(self.intent_id, UUID): raise InvalidIntent("UUID required")
        if not self.chain.strip() or not self.destination.strip() or not self.asset.strip():
            raise InvalidIntent("Missing chain, destination or asset")
        if isinstance(self.amount_base_units, bool) or not isinstance(self.amount_base_units, int) or self.amount_base_units <= 0:
            raise InvalidIntent("Amount must be a positive integer in base units")
        if self.network != "testnet": raise InvalidIntent("V2 only permits testnet intent preparation")
