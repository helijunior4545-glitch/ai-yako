# Local security boundary
Use OS keystore/secure hardware when available; encrypt persisted secrets with vetted cryptography; never log secrets. Agent output is untrusted. Financial signing requires an explicit, fresh, local human approval and transaction detail verification. Do not treat sync events as blockchain truth.
