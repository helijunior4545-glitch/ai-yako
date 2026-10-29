"""AI Yako V8: official QVAC Python SDK inference, local-model only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
from datetime import datetime, timezone

SYSTEM = ("You are AI Yako, a cautious financial risk analyst. Analyze only the scenario supplied. "
          "Identify red flags, uncertainties and safer alternatives. Never guarantee returns, "
          "never request credentials, and never execute transactions. Respond concisely in English.")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def validate_model(path):
    p = Path(path).expanduser().resolve(strict=True)
    if not p.is_file() or p.suffix.lower() != '.gguf':
        raise ValueError('A local .gguf model file is required')
    if p.stat().st_size < 1024:
        raise ValueError('Model file is too small to be valid')
    return p


def qvac_infer(scenario, model_path, expected_sha256=None):
    if not isinstance(scenario, str) or not scenario.strip() or len(scenario) > 12000:
        raise ValueError('Scenario must contain 1–12000 characters')
    model_path = validate_model(model_path)
    digest = sha256_file(model_path)
    if expected_sha256 and digest.lower() != expected_sha256.strip().lower():
        raise ValueError('SHA256 mismatch: refusing to load model')
    try:
        from tetherto.qvac_sdk.notebook import SyncClient
    except ImportError as exc:
        raise RuntimeError('Official QVAC Python SDK not installed. Run: python3 -m pip install tetherto-qvac-sdk') from exc
    history = [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': scenario.strip()}]
    started = time.monotonic()
    with SyncClient() as client:
        model = client.load_model(model_src=str(model_path))
        try:
            result = client.completion(model, history, stream=True)
            answer = ''.join(str(token) for token in result)
        finally:
            # SDK context manager releases worker resources; explicit unload when available.
            unload = getattr(client, 'unload_model', None)
            if callable(unload):
                unload(model)
    if not answer.strip():
        raise RuntimeError('QVAC returned an empty completion')
    return {
        'schema': 'ai-yako-qvac-v8-1', 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'engine': 'tetherto-qvac-sdk', 'mode': 'official-qvac-local-model',
        'model_name': model_path.name, 'model_sha256': digest,
        'scenario_sha256': hashlib.sha256(scenario.encode('utf-8')).hexdigest(),
        'duration_seconds': round(time.monotonic() - started, 3),
        'analysis': answer, 'network_isolation_verified': False,
        'financial_transaction_executed': False,
        'disclaimer': 'Analysis only; no wallet signing or transfers.'
    }


def main():
    parser = argparse.ArgumentParser(description='AI Yako V8 — official QVAC local inference')
    parser.add_argument('--model', required=True, help='Existing local GGUF model path')
    parser.add_argument('--scenario', required=True)
    parser.add_argument('--sha256', default='', help='Optional expected model SHA256')
    parser.add_argument('--output', default='', help='Optional local JSON report path')
    args = parser.parse_args()
    try:
        report = qvac_infer(args.scenario, args.model, args.sha256)
        output = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            dest = Path(args.output).expanduser()
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, 'x', encoding='utf-8') as fh:
                fh.write(output + '\n')
            os.chmod(dest, 0o600)
            print('Saved evidence:', dest)
        else:
            print(output)
    except Exception as exc:
        print('QVAC_INFERENCE_FAILED:', type(exc).__name__, str(exc))
        raise SystemExit(1)

if __name__ == '__main__':
    main()
