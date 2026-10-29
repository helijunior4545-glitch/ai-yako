"""Encryption interface. No plaintext fallback and no custom crypto."""
class EncryptionUnavailable(RuntimeError): pass

class LocalEncryption:
    def encrypt(self, plaintext: bytes, *, associated_data: bytes) -> bytes:
        raise EncryptionUnavailable("Authenticated encryption not configured")

    def decrypt(self, ciphertext: bytes, *, associated_data: bytes) -> bytes:
        raise EncryptionUnavailable("Authenticated encryption not configured")
