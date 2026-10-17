#!/usr/bin/env python3
"""G126 actual native ARM 2010 CNPC::isAttackState source helper 0x9F910.
Analyze original this+0x2BC state-list helper called with -1 and associated
source C++ demangled method. Goal: port genuine state node retrieval to Vita
instead of relying on diagnostic preverified externally provided last node.
No guessed pointers; no original IPA committed; NO VPK.
"""
import argparse,json,struct,bisect,subprocess,zipfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
import capstone
TARGET=0x9f910
def run(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError("exact original game IPA required")
 with zipfile.ZipFile(ipa) as z:data=z.read("Payload/IronMan2.app/IronMan2")
 parsed=parse_macho(data)
 symbols=sorted(parsed["entries"],key=lambda x:x[1]&~1)
 addresses=sorted(set(i[1]&~1 for i in symbols))
 ix=bisect.bisect_right(addresses,TARGET)-1
 near=addresses[max(0,ix-3):ix+6]
 records=[]
 for a in near:
  syms=[z[0] for z in symbols if z[1]&~1==a]
  dem=subprocess.run(['c++filt'],input="\n".join(syms)+"\n",text=True,
    capture_output=True,check=True).stdout.splitlines()
  records.append({'source_2010_native_address_hex':hex(a),
    'mangled_original_Cplusplus_symbol_names':syms[:12],
    'demangled_original_Cplusplus_class_names':dem[:12]})
 sec=next(s for s in parsed['sections'] if s[3]=='__text' and s[0]<=TARGET<s[0]+s[1])
 after=addresses[bisect.bisect_right(addresses,TARGET)]
 limit=min(256,after-TARGET)
 where=sec[2]+TARGET-sec[0]
 start_sym=[s for s in symbols if s[1]&~1==TARGET]
 if not start_sym:raise ValueError('0x9f910 is not actual owner original method entry')
 thumb=bool(start_sym[0][1]&1)
 engine=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB if thumb else capstone.CS_MODE_ARM)
 decoded=list(engine.disasm(data[where:where+limit],TARGET))
 if len(decoded)<3:raise ValueError("2010 original source helper no ARM disassembly")
 assembly=[{'address':hex(i.address),'mnemonic':i.mnemonic,'operands':i.op_str} for i in decoded]
 result={'target_native_owner_address':'0x9f910',
  'original_2010_source_method_neighborhood':records,
  'native_original_helper_assembly':assembly,
  'source_helper_bound_until_next_actual_original_symbol_bytes':after-TARGET,
  'true_original_state_node_pointer_semantics_fully_recovered':False,
  'native_iOS_program_runtime_executed_during_this_analysis':False,
  'user_IPA_released':False,'VPK_generated':False}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G126_CNPC_LAST_NODE_0x9F910_NATIVE_ORIGINAL_ARM_POINTER_HELPER_SOURCE.json').write_text(
 json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('G126 source native 2010 CNPC+0x2BC last-node helper real name:')
 for row in records:print(row['source_2010_native_address_hex'],row['demangled_original_Cplusplus_class_names'][:3])
 print('G126 actual iOS ARM helper bytes',after-TARGET)
 for row in assembly:print('G126_ARM',row)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.ipa,a.out)
