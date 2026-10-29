# WebSocket security contract
No consumer routes are exposed until challenge-response authentication, device-scoped grants, origin policy, rate limits and revocation checks are implemented. Do not trust Django session or commercial tenant middleware.
