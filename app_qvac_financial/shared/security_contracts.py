"""Wire protocol security fields. Language-neutral JSON schema is canonical."""
PROTOCOL_VERSION = 2
REQUIRED_DEVICE_FIELDS = ("device_id", "identity_id", "nonce", "signature", "timestamp_utc")
