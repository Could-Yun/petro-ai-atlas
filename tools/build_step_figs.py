# -*- coding: utf-8 -*-
"""生成 assets/steps/<case>/s<n>.svg；用法：python3 tools/build_step_figs.py [case ...]"""
import sys, os, importlib, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, 'stepfig'))
ROOT = os.path.dirname(HERE)
MODS = {'seis-fault': 'seis_fault', 'geo-anomaly': 'geo_anomaly', 'geo-fracture': 'geo_fracture', 'geo-spectral': 'geo_spectral', 'geo-symbol': 'geo_symbol', 'seis-denoise': 'seis_denoise', 'seis-facies': 'seis_facies', 'seis-firstbreak': 'seis_firstbreak', 'seis-reservoir': 'seis_reservoir'}
def build(case):
    m = importlib.import_module(MODS[case])
    out = []
    for i, fn in enumerate(m.FIGS):
        from common import save
        p = os.path.join(ROOT, 'assets', 'steps', case, 's%d.svg' % (i + 1))
        n = save(fn(), p); out.append((p, n))
    return out, m.CAPS
if __name__ == '__main__':
    for c in (sys.argv[1:] or MODS):
        res, _ = build(c)
        for p, n in res: print(os.path.relpath(p, ROOT), n)
