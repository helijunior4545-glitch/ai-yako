"""WDK integration boundary; never store wallet keys on the server."""
class WDKNotInstalled(RuntimeError):
    pass

class WDKAdapter:
    def prepare_transaction(self, intent):
        raise WDKNotInstalled("Install and validate WDK testnet adapter")
    def request_local_approval(self, intent_id):
        raise WDKNotInstalled("Local approval UI not implemented")
    def sign_approved_transaction(self, intent_id):
        raise WDKNotInstalled("Signing disabled until local approval is implemented")
