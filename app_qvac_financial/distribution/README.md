# Distribution contract
Build desktop/Android clients independently from Django. Distribute models as separate versioned artifacts with signed manifests and SHA-256 integrity checks. A hash alone is insufficient against a compromised distribution server: validate a trusted signing key. No unsigned auto-update mechanism is implemented in V1.
