#!/usr/bin/env python3
"""Compare every original initializer field with the independent C decoder."""
import argparse
import importlib.util
from pathlib import Path
import re
import subprocess

parser=argparse.ArgumentParser(description=__doc__)
for name in ('states-header','mission-c','asset','dump-tool'):
    parser.add_argument('--'+name,required=True,type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('export_tables',root/'tools/export_original_tables.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
state=args.states_header.read_text();mission=args.mission_c.read_text()
enums={n:int(v) for n,v in re.findall(r'(B24_G137_CALL_\w+)\s*=\s*(\d+)',
       (root/'src/b24/b24_unified/b24_g137_source_mission000_intro.h').read_text())}
names=re.findall(r'"([^"\n]+)"',state.split('b24g217_original_suit_source_names',1)[1].split('};',1)[0])
expected=['N\t'+n for n in names]
for prefix,name in (('S','b24g217_true_2010_owner_states'),('E','b24g217_source_attack_trail_events')):
    for row in module.array(state,name):
        expected.append('\t'.join([prefix,row[0]]+[str(module.number(v)) for v in row[1:]]))
for row in module.array(mission,'b24_g137_source_lua_events'):
    fields=[module.number(row[0]),enums[row[1].strip()],*[module.number(v) for v in row[2:5]],
            '<NULL>' if row[5].strip()=='0' else row[5].strip(),
            module.number(row[6]),module.number(row[7])]
    expected.append('\t'.join(['L']+list(map(str,fields))))
actual=subprocess.check_output([str(args.dump_tool.resolve()),str(args.asset.resolve())],text=True).splitlines()
assert len(actual)==len(expected)==1028
assert actual==expected,'Original initializer / runtime decoder mismatch'
print('PASS original-data migration: all 1028 name/state/track/mission rows match field by field')
