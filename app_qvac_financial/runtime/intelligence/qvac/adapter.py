"""QVAC integration boundary; no fake inference fallback."""
class QVACNotInstalled(RuntimeError):
    pass

class QVACAdapter:
    def infer(self, prompt, context):
        raise QVACNotInstalled("Install and validate QVAC SDK/model before enabling inference")
