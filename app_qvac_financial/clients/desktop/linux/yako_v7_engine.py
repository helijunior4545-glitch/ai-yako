"""AI Yako V7: evidence-first offline analysis. Generic runner, not official QVAC integration."""
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

FLAGS = {"private key": "Secret exposure", "seed phrase": "Seed phrase exposure", "urgent": "Urgency pressure", "guaranteed": "Unrealistic guarantee", "leverage": "Leverage risk", "all funds": "Concentration risk"}

def digest(path):
    h=hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def analyze(scenario, runner=None, model=None, expected_sha256=None, offline_isolation=False, timeout=120):
    scenario=scenario.strip()
    if not scenario: raise ValueError('Scenario must not be empty')
    if len(scenario)>12000: raise ValueError('Scenario exceeds 12000 characters')
    flags=[label for term,label in FLAGS.items() if term in scenario.casefold()]
    report={"schema":"ai-yako-v7-evidence-1", "timestamp_utc":datetime.now(timezone.utc).isoformat(),
            "scenario_sha256":hashlib.sha256(scenario.encode()).hexdigest(),
            "rules":{"flags":flags,"assessment":"REVIEW REQUIRED" if flags else "NOT ASSESSED"},
            "financial_execution":"DISABLED", "qvac_official_integration":False,
            "local_inference":None}
    if bool(runner)!=bool(model): raise ValueError('Provide both runner and model, or neither')
    if not runner: return report
    binary=Path(runner).expanduser().resolve(strict=True)
    weights=Path(model).expanduser().resolve(strict=True)
    if not binary.is_file() or not os.access(binary,os.X_OK): raise ValueError('Runner is not executable')
    if not weights.is_file() or weights.suffix.lower()!='.gguf': raise ValueError('Expected a local GGUF model')
    model_sha=digest(weights)
    if not expected_sha256: raise ValueError('Model SHA256 pin is required for local inference')
    if len(expected_sha256)!=64 or any(c not in '0123456789abcdef' for c in expected_sha256.lower()): raise ValueError('Invalid SHA256 pin')
    if model_sha != expected_sha256.lower(): raise ValueError('Model SHA256 mismatch; inference blocked')
    prompt=('You are a cautious financial risk analyst. Never claim to execute transactions. '
            'Separate observations from assumptions, list risks and mitigation. Scenario: '+scenario)
    cmd=[str(binary),'-m',str(weights),'-p',prompt,'-n','384','--temp','0.2']
    if offline_isolation:
        import shutil
        unshare=shutil.which('unshare')
        if not unshare: raise RuntimeError('unshare unavailable; offline isolation not established')
        cmd=[unshare,'--net','--']+cmd
    env={k:v for k,v in os.environ.items() if not any(s in k.upper() for s in ('TOKEN','PASSWORD','SECRET','API_KEY','PROXY'))}
    env.update({'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','NO_PROXY':'*'})
    started=time.monotonic()
    try:
        proc=subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, env=env, check=False)
    except subprocess.TimeoutExpired as exc: raise RuntimeError('Runner timed out') from exc
    if proc.returncode: raise RuntimeError('Runner failed (exit %d): %s' %(proc.returncode,proc.stderr[-300:]))
    report['local_inference']={"adapter":"generic-gguf-cli (NOT verified QVAC)",
        "runner_sha256":digest(binary), "model_sha256":model_sha,
        "elapsed_ms":round((time.monotonic()-started)*1000),
        "network_namespace_attempted":bool(offline_isolation),
        "output":proc.stdout[-16000:]}
    return report

def main():
    import argparse
    p=argparse.ArgumentParser(description='AI Yako V7 offline evidence CLI')
    p.add_argument('--scenario',required=True); p.add_argument('--runner'); p.add_argument('--model')
    p.add_argument('--model-sha256'); p.add_argument('--isolate-network',action='store_true')
    p.add_argument('--output',help='Optional report JSON path (refuses overwrite)')
    a=p.parse_args()
    result=analyze(a.scenario,a.runner,a.model,a.model_sha256,a.isolate_network)
    body=json.dumps(result,indent=2,ensure_ascii=False)
    if a.output:
        with open(a.output,'x',encoding='utf-8') as f: f.write(body+'\n')
        print('Evidence written:',a.output)
    else: print(body)
if __name__=='__main__': main()
