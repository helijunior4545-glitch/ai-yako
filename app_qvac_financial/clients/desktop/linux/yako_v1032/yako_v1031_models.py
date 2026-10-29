"""AI Yako V10.31: offline model capability inventory and conservative hardware preflight.
No downloads, cloud calls, subprocesses, automatic model switching or third-party dependencies.
The currently working QVAC 1B remains the only enabled backend.
"""
import json
import os
import platform
from pathlib import Path

CATALOG = (
    {'id':'qvac-llama-3.2-1b-q4_0','label':'QVAC Llama 3.2 1B Q4_0', 'backend':'qvac-sdk', 'state':'active', 'minimum_available_mib':512},
    {'id':'external-local-model','label':'Additional local models', 'backend':'not-implemented', 'state':'unavailable', 'minimum_available_mib':None},
    {'id':'hosted-demo','label':'Hosted demonstration', 'backend':'not-implemented', 'state':'unavailable', 'minimum_available_mib':None},
)

def _meminfo(path='/proc/meminfo'):
    result={}
    try:
        for line in Path(path).read_text().splitlines():
            if ':' not in line:continue
            k,v=line.split(':',1)
            parts=v.strip().split()
            if parts and parts[0].isdigit():result[k]=int(parts[0])//1024
    except (OSError,ValueError):pass
    return result

def hardware_report(meminfo_path='/proc/meminfo'):
    mem=_meminfo(meminfo_path)
    available=mem.get('MemAvailable')
    total=mem.get('MemTotal')
    swap=mem.get('SwapTotal')
    swap_free=mem.get('SwapFree')
    # Never infer an actual model fit from memory alone.
    pressure = ('unknown' if available is None or total is None or total==0 else
                'high' if available < 1024 or available/total < .20 else
                'moderate' if available < 2048 or available/total < .35 else 'low')
    return {'os':platform.system(),'architecture':platform.machine(),
            'logical_cpu_count':os.cpu_count(), 'ram_total_mib':total,
            'ram_available_mib':available,'swap_total_mib':swap,
            'swap_used_mib':None if swap is None or swap_free is None else swap-swap_free,
            'memory_pressure':pressure,
            'gpu_compatibility':'not_tested',
            'model_fit_verified':False}

def capabilities(meminfo_path='/proc/meminfo'):
    hw=hardware_report(meminfo_path)
    return {'version':'10.31','active_model':'qvac-llama-3.2-1b-q4_0',
            'active_backend':'qvac-sdk','selection_policy':'fixed_safe_default',
            'models':[dict(item) for item in CATALOG], 'hardware':hw,
            'automatic_downloads':False,'cloud_inference_enabled':False,
            'automatic_cloud_fallback':False,'financial_data_uploaded':False,
            'model_switching_implemented':False,
            'local_inference_verified':False,
            'note':'Hardware inventory is advisory. It does not prove QVAC cache, GPU support, or successful inference. Model changes require a separately tested, explicit opt-in implementation.'}

def main():
    print(json.dumps(capabilities(),indent=2,ensure_ascii=False))
if __name__=='__main__':main()
