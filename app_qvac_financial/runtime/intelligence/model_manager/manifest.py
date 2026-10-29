"""Model metadata checks. A checksum is not a trusted signature."""
from dataclasses import dataclass
import hashlib
from pathlib import Path

@dataclass(frozen=True)
class ModelManifest:
    model_id: str
    version: str
    sha256: str
    byte_size: int
    source: str

    def verify_file_integrity(self, path):
        path = Path(path)
        if path.stat().st_size != self.byte_size: return False
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024*1024), b''):
                digest.update(chunk)
        return digest.hexdigest() == self.sha256
