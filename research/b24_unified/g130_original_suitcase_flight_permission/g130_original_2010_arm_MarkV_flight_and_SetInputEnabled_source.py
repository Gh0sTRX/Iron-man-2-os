#!/usr/bin/env python3
"""G130 original iOS 2010 actual ARM CPP and C-function suit/flight/input gate
inventory, correlated to TRUE level1 Lua SetInputEnabled(14,false).
Mark V flight unsupported by user tentative recollection ALONE.
Inspect native engine evidence; do not disable flight on false inference,
and do not ship proprietary executable or VPK.
"""
import argparse,bisect,collections,json,re,subprocess,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
import capstone
SUIT_OR_FLIGHT=re.compile(r'(SuitCase|Suitcase|MarkV|MainCharacter|IronMan|Flight|Fly|Hover|Rush|MoveMode|InputEnabled|EnableInput|CanFly|IsFlying|Armour|Armor)',re.I)
HIGH_VALUE=re.compile(r'(CanFly|SetFly|FlyMode|IsFly|Flight|Hover|Rush|SetInputEnabled|InputEnable|DisableInput|CanMove|setInput|Suitcase)',re.I)
def run(ipa,mission,out):
 if ipa.stat().st_size!=248613763:raise ValueError("2010 owner IPA exact size required")
 with zipfile.ZipFile(ipa) as z:exe=z.read("Payload/IronMan2.app/IronMan2")
 native=parse_macho(exe)
 originals=[s[0] for s in native['entries']]
 cpp=subprocess.run(['c++filt'],input='\n'.join(originals)+'\n',
   text=True,capture_output=True,check=True).stdout.splitlines()
 assert len(cpp)==len(originals)
 records=sorted(zip(native['entries'],cpp),key=lambda z:z[0][1]&~1)
 addresses=sorted(set(x[0][1]&~1 for x in records))
 text_sections=[x for x in native['sections'] if x[3]=='__text']
 match=[]
 for sy,name in records:
  if not SUIT_OR_FLIGHT.search(name):continue
  addr=sy[1]&~1
  sec=next((s for s in text_sections if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:continue
  match.append({'original_iOS_cpp_method':name,'2010_arm_vm_addr_hex':hex(addr),
     'original_2010_arm_thumb':bool(sy[1]&1),
     'source_method_name_not_implementation':True})
 core=[]
 for sy,name in records:
  if not HIGH_VALUE.search(name):continue
  addr=sy[1]&~1
  sec=next((s for s in text_sections if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:continue
  i=bisect.bisect_right(addresses,addr)
  end=min(addresses[i] if i<len(addresses) else sec[0]+sec[1],sec[0]+sec[1])
  limit=min(end-addr,320)
  if limit<12:continue
  off=sec[2]+addr-sec[0]
  engine=capstone.Cs(capstone.CS_ARCH_ARM,
    capstone.CS_MODE_THUMB if sy[1]&1 else capstone.CS_MODE_ARM)
  instr=list(engine.disasm(exe[off:off+limit],addr))
  if len(instr)<3:continue
  core.append({'source_cpp_function':name,'2010_address_hex':hex(addr),
    'source_ARM_native_bounded_length':limit,
    'source_native_raw_ARM_control_flow':[
       {'pc':hex(ins.address),'mnemonic':ins.mnemonic,'registers_or_operands':ins.op_str}
       for ins in instr[:65]],
    'original_mission_level1_MarkV_flight_permission_completely_decoded':False})
 scene=json.loads(mission.read_text())
 assert scene['original_lua_callbacks_total']==71
 calls=[]
 for handler in scene['original_callbacks_and_static_condition_call_candidates']:
  for c in handler['interesting_calls_static_NOT_execution_order']:
   if c['original_native_function_name'] in ('SetInputEnabled','SetState',
       'MissionPause','MissionResume'):
    calls.append({'original_native_level1_Lua_callback':handler['original_native_callback'],
      'bytecode_PC':c['native_Lua_PC'],'call':c['original_native_function_name'],
      'source_literal_args':c['literal_args_from_2010_Lua_static_registers'],
      'native_low_level_input_mask_meaning_verified':False})
 report={'source':'user original iOS 2010 native executable + typed original 71 Level1 Lua5.1 source',
  'native_original_suit_and_flight_CPP_method_inventory':match,
  'original_native_flight_Calls_bounded_ARM':core,
  'real_original_level1_Mission_SetInputEnabled_and_SetState_calls':calls,
  'original_suitcase_MarkV_level1_CanFly_permitted_proven':False,
  'original_suitcase_MarkV_level1_CanFly_prohibited_proven':False,
  'native_SetInputEnabled_14_bitfield_identified':False,
  'iOS_mission_flight_control_ACTIVATED_in_Vita':False,
  'binary_in_artifacts':False,'NO_VPK':True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('G130 owner original native original CPP suit/fly/input method names',len(match),
       'disassembled high value',len(core),'original scripted input/state CALLs',len(calls))
 print('G130 native methods important')
 for x in core[:85]:print('G130 SOURCE METHOD',x['2010_address_hex'],x['source_cpp_function'])
 print('G130 original Mission000 native intro calls')
 for x in calls:
  if x['original_native_level1_Lua_callback']=='Mission000_OnStart':
   print('G130 FIRST MISSION',x['bytecode_PC'],x['call'],x['source_literal_args'])
 print('G130 original iOS flight permission remains unproven until native NPC/mission restrictions and 14 input flag are decoded, NO VPK')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--ipa',type=Path,required=True)
 a.add_argument('--mission',type=Path,required=True)
 a.add_argument('--out',type=Path,required=True)
 args=a.parse_args();run(args.ipa,args.mission,args.out)
