# AI Yako V8 — Official QVAC inference adapter

This is a **new standalone CLI** that does not modify Django, the V6/V7 GUI, or financial state.

Install the official SDK on the LOCAL Linux machine (internet required for installation):

    python3 -m pip install tetherto-qvac-sdk

Get a compatible GGUF model from a trusted source. QVAC SDK does not bundle model weights.

    cd app_qvac_financial/clients/desktop/linux
    python3 -m unittest -v test_yako_v8_qvac.py
    python3 yako_v8_qvac.py --model /absolute/path/to/model.gguf --scenario 'Analyze guaranteed 25% monthly returns with urgent deposit pressure.' --output ./yako_v8_evidence.json

Offline validation: install SDK and model while online, disconnect all networking, then run the same command. The JSON flag network_isolation_verified stays false: the tool cannot attest to system-wide isolation. Capture network state separately. Never use production wallet keys or real money.

Official documentation: https://docs.qvac.tether.io/sdk/ and https://qvac.tether.io/products/sdk

The V8 integration is not validated until a genuine QVAC completion succeeds on the user's device.
