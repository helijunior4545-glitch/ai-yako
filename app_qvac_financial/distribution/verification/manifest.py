"""Artifact digest verifier. Does not replace a trusted release signature."""
import hashlib

def verify_sha256(path, expected_digest):
    digest=hashlib.sha256()
    with open(path,'rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()==expected_digest

class SignatureVerificationUnavailable(RuntimeError): pass

def verify_release_signature(*args, **kwargs):
    raise SignatureVerificationUnavailable("Pinned release signing key verification not implemented")
