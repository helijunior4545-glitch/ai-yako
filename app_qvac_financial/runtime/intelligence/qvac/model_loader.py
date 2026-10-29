"""Local-only QVAC loader boundary. No silent cloud fallback."""
from .adapter import QVACNotInstalled

def load_local_qvac_model(manifest, model_path):
    if not manifest.verify_file_integrity(model_path):
        raise ValueError("Model file digest/size mismatch")
    raise QVACNotInstalled("Verified model artifact, but QVAC native runtime not integrated")
