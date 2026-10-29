"""Device keystore interface. No insecure file or environment-variable fallback."""
class SecureKeyStorageUnavailable(RuntimeError): pass

class SecureKeyStorage:
    def create_nonexportable_key(self, label: str):
        raise SecureKeyStorageUnavailable("Platform secure keystore not integrated")

    def sign(self, key_handle, digest: bytes):
        raise SecureKeyStorageUnavailable("Platform secure keystore not integrated")
