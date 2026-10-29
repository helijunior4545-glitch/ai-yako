import ast
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
COMMERCIAL=('app_config','app_billing','app_hub','app_whatsapp_ops','app_home','app_developer_network')
class V2IndependenceTests(unittest.TestCase):
    def test_no_commercial_imports(self):
        for folder in ('server','runtime','shared'):
            for p in (ROOT/folder).rglob('*.py'):
                tree=ast.parse(p.read_text(encoding='utf-8'))
                for node in ast.walk(tree):
                    if isinstance(node,ast.Import): names=[a.name for a in node.names]
                    elif isinstance(node,ast.ImportFrom): names=[node.module or '']
                    else: continue
                    for name in names:
                        self.assertFalse(any(name==x or name.startswith(x+'.') for x in COMMERCIAL),f'{p}: {name}')
    def test_no_django_runtime(self):
        for folder in ('runtime','shared'):
            for p in (ROOT/folder).rglob('*.py'):
                tree=ast.parse(p.read_text(encoding='utf-8'))
                for node in ast.walk(tree):
                    if isinstance(node,ast.Import): names=[a.name for a in node.names]
                    elif isinstance(node,ast.ImportFrom): names=[node.module or '']
                    else: continue
                    for name in names: self.assertFalse(name=='django' or name.startswith('django.'),f'{p}: {name}')
