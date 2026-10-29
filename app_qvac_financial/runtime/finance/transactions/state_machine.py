"""Transaction intent state machine; no signing or broadcast implementation."""
from enum import Enum

class State(str, Enum):
    DRAFT="draft"
    PREPARED="prepared"
    AWAITING_APPROVAL="awaiting_approval"
    APPROVED="approved"
    SIGNED="signed"
    BROADCAST="broadcast"
    CONFIRMED="confirmed"
    REJECTED="rejected"

ALLOWED = {
    State.DRAFT: {State.PREPARED, State.REJECTED},
    State.PREPARED: {State.AWAITING_APPROVAL, State.REJECTED},
    State.AWAITING_APPROVAL: {State.APPROVED, State.REJECTED},
    State.APPROVED: {State.SIGNED, State.REJECTED},
    State.SIGNED: {State.BROADCAST},
    State.BROADCAST: {State.CONFIRMED},
}

def transition(current: State, target: State) -> State:
    if target not in ALLOWED.get(current, set()):
        raise ValueError(f"Invalid transaction transition: {current} -> {target}")
    return target
