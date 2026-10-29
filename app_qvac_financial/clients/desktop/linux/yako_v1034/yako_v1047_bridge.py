"""Compatibility bridge: no QVAC or financial modules are replaced."""
import importlib.util
from pathlib import Path
MODULE=Path(__file__).resolve().parents[4]/'offline/yako_v1049_engine.py'
_spec=importlib.util.spec_from_file_location('yako_hybrid_v1047',MODULE)
_hybrid=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_hybrid)
hybrid_solve=_hybrid.solve
hybrid_enrich=_hybrid.enrich
