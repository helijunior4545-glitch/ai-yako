import unittest
from server.security.authentication.challenge import DeviceChallenge, ChallengeVerifierUnavailable, verify_device_signature
from server.security.authorization.scope import AccessGrant, require_scope
from runtime.security.key_storage import SecureKeyStorage, SecureKeyStorageUnavailable
from runtime.security.encryption import LocalEncryption, EncryptionUnavailable

class V2SecurityTests(unittest.TestCase):
    def test_grant(self):
        require_scope(AccessGrant('i','d',frozenset({'sync:read'})),identity_id='i',device_id='d',scope='sync:read')
    def test_wrong_scope(self):
        with self.assertRaises(PermissionError): require_scope(AccessGrant('i','d',frozenset()),identity_id='i',device_id='d',scope='sync:write')
    def test_revoked_grant(self):
        with self.assertRaises(PermissionError): require_scope(AccessGrant('i','d',frozenset({'sync:read'}),True),identity_id='i',device_id='d',scope='sync:read')
    def test_challenge_replay(self):
        c=DeviceChallenge('d');c.consume()
        with self.assertRaises(PermissionError):c.consume()
    def test_device_signature_unavailable(self):
        with self.assertRaises(ChallengeVerifierUnavailable):verify_device_signature()
    def test_keystore_fails_closed(self):
        with self.assertRaises(SecureKeyStorageUnavailable):SecureKeyStorage().create_nonexportable_key('test')
    def test_encryption_fails_closed(self):
        with self.assertRaises(EncryptionUnavailable):LocalEncryption().encrypt(b'data',associated_data=b'a')
