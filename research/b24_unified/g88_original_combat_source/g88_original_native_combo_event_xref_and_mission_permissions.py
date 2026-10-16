#!/usr/bin/env python3
"""G88 source-only ORIGINAL 2010 iOS native ARM melee & Lua permission xrefs.
Reads owner 1.0.0 IPA ephemerally. Does NOT invent per-weapon damage or
animation hit frames from symbol names, 266/300/500ms animation lengths,
branch adjacency, or arbitrary float words. No executable/audio/VPK output.
"""
from __future__ import annotations
import argparse,bisect,collections,json,re,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_OP_MEM
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'g76_original_combat'))
from g76_2010_native_arm_combat_method_provenance import parse_macho

FOCUS=(
 'MainCharacter::GetCurrentMeleeAttackStep() const',
 'MainCharacter::StartMeleeAttack(float)',
 'MainCharacter::UpdateComboAttackAction(int)',
 'Actor::TestMeleeHit(Actor*)',
 'Actor::Damage(float)',
 'WeaponDB::GetAttackEntityByIndex(int)',
)
SCAN=re.compile(r'^(MainCharacter|Actor|AttackEntity|ProjectileEntity)::.*'
                r'(Combo|Melee|Attack|Hit|Damage|Throw|Hurt)',re.I)
def decode_original_macho(original):
 m=parse_macho(original)
 syms=m['entries']
 dem=subprocess.run(['c++filt'],input='\n'.join(row[0] for row in syms)+'\n',
    text=True,capture_output=True,check=True).stdout.splitlines()
 if len(dem)!=len(syms):raise ValueError('2010 C++ symtab damaged')
 methods=collections.defaultdict(list)
 byaddress=collections.defaultdict(list)
 for sym,name in zip(syms,dem):
  methods[name].append(sym)
  byaddress[sym[1]&~1].append(name)
 for need in FOCUS:
  # The real 2010 Mach-O symtab contains duplicate entries/aliases at
  # identical function addresses. A duplicate NAME is not a distinct
  # native executable implementation; only reject DIFFERENT addresses.
  real_addresses={sym[1]&~1 for sym in methods[need]}
  if len(real_addresses)!=1:
   similar=[k for k in methods if need.split('(')[0] in k][:8]
   raise ValueError('original 2010 function missing or divergent native address: '+
     need+' entries='+str(len(methods[need]))+' alternatives='+str(similar))
 addresses=sorted(set(s[1]&~1 for s in syms))
 d_arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 d_thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for dec in (d_arm,d_thumb):dec.detail=True
 def examine(sym,name):
  addr=sym[1]&~1
  sec=next((s for s in m['sections'] if s[3]=='__text' and s[0]<=addr<s[0]+s[1]),None)
  if not sec:return None
  ni=bisect.bisect_right(addresses,addr)
  end=addresses[ni] if ni<len(addresses) else sec[0]+sec[1]
  lim=min(end-addr,sec[0]+sec[1]-addr,8192)
  start=sec[2]+addr-sec[0]
  if lim<4 or start+lim>len(original):return None
  ins=list((d_thumb if sym[1]&1 else d_arm).disasm(original[start:start+lim],addr))
  calls=[];references=[];branches=[]
  for i in ins:
   if i.mnemonic.startswith(('bl','blx')) and i.operands:
    o=i.operands[0]
    v=o.imm if o.type==ARM_OP_IMM else None
    calls.append({'pc_offset':i.address-addr,
      'direct_known_symbol':byaddress.get(v&~1,[])[:2] if v is not None else [],
      'indirect_register_target':v is None})
   if i.mnemonic.startswith(('ldr','str','vldr','vstr')) and len(i.operands)>=2:
    for op in i.operands:
     if op.type==ARM_OP_MEM and op.mem.disp==0x824:
      references.append({'pc_offset':i.address-addr,
        'opcode':i.mnemonic,'register_operands':i.op_str[:90],
        'original_combo_step_offset_verified':True})
   if i.mnemonic.startswith(('beq','bne','bgt','bge','blt','ble','bhi','bls','cbz','cbnz')):
    branches.append({'pc_offset':i.address-addr,'opcode':i.mnemonic})
  return {'original_native_CPP_method':name,'source_address_hex':hex(sym[1]),
   'genuine_2010_macho_arm_thumb':bool(sym[1]&1),
   'source_function_bounded_bytes':lim,'decoded_instructions':len(ins),
   'original_combo_counter_offset_0x824_accesses':references,
   'direct_and_indirect_calls':calls[:100],
   'conditional_branches':branches[:80],
   'original_hit_active_timestamp_proven':False,
   'original_weapon_numeric_damage_proven':False}
 focus={name:examine(methods[name][0],name) for name in FOCUS}
 if any(v is None for v in focus.values()):raise ValueError('original C++ method mapped outside 2010 ARM code')
 # The instruction-level source getter IS a concrete proof of field +0x824.
 getter=focus[FOCUS[0]]
 refs=getter['original_combo_counter_offset_0x824_accesses']
 if not refs or not any(x['opcode'].startswith('ldr') for x in refs):
  raise ValueError('original native combo getter did not load +0x824')
 candidates=[]
 for name,rows in methods.items():
  if not SCAN.search(name) or name in FOCUS:continue
  for sym in rows[:1]:
   record=examine(sym,name)
   if not record:continue
   meaningful=(record['original_combo_counter_offset_0x824_accesses'] or
    any(any('TestMeleeHit' in t or 'UpdateComboAttackAction' in t or
                'StartMeleeAttack' in t for t in edge['direct_known_symbol'])
      for edge in record['direct_and_indirect_calls']))
   if meaningful:candidates.append(record)
 # Actually observed static Lua CALLs, not executed mission state machine.
 from importlib.util import spec_from_file_location,module_from_spec
 attack_path=ROOT/'g75_device_qa/g75_2010_attack_conditions_opcode_context.py'
 spec=spec_from_file_location('g88_g75_source_lua',str(attack_path))
 module=module_from_spec(spec);spec.loader.exec_module(module)
 return focus,candidates,module
def main(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError('expected original user-owned 2010 v1.0.0 IPA, no substitute release')
 with zipfile.ZipFile(ipa) as z:original=z.read('Payload/IronMan2.app/IronMan2')
 focus,candidates,g75=decode_original_macho(original)
 out.mkdir(parents=True,exist_ok=True)
 lua=out/'G88_NATIVE_LUA_COMBAT_CALL_WINDOW_METADATA.json'
 g75.examine(ipa,lua)
 l=json.loads(lua.read_text())
 calls=[x for x in l['attack_and_input_source_calls_with_instruction_context']
        if x['source_call']=='SetAttackTypeEnabled']
 if len(calls)!=12:raise ValueError('2010 native Lua attack permission call count changed')
 report={
 'verified_original_2010_iOS_executable_readonly':True,
 'original_actor_combo_step_field_offset_hex':'0x824',
 'native_method_instruction_xrefs':focus,
 'additional_natively_proven_combo_counter_or_melee_call_xrefs':candidates[:65],
 'original_level1_lua_SetAttackTypeEnabled_12_source_calls':[
  {'source_callback':q['real_original_script'],
   'static_bytecode_PC':q['source_pc'],
   'register_traced_arguments':q['source_register_traced_parameters'],
   'nearby_opcode_conditions_NOT_proven_to_guard_call':
      q['static_condition_like_instr_within_12_before']}
  for q in calls],
 'exact_attack_type_1_meaning_verified':False,
 'Lua_live_Mission000_execution_order_verified':False,
 'native_attack_hit_active_start_stop_frame_verified':False,
 'original_weapon_damage_numbers_verified':False,
 'Vita_game_hit_damage_enabled':False,
 'original_IPA_machine_code_audio_or_licensed_content_exported':False,
 'metadata_only_NO_VPK':True}
 (out/'G88_ORIGINAL_2010_COMBO_MELEE_ARM_XREFS_AND_LUA_ATTACK_PERMISSION_EVIDENCE.json').write_text(
  json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print('PASS G88 original 2010 C++ combo field +0x824 xrefs, main/native method count',
       len(focus),'extra combat references',len(candidates),
       'original Level1 Lua SetAttackTypeEnabled source CALLs',len(calls),
       'NO new asserted hit times or damage / NO VPK')
 for name,rec in focus.items():
  print(' NATIVE',name,'entry',rec['source_address_hex'],
    'counter 0x824 direct access',len(rec['original_combo_counter_offset_0x824_accesses']),
    'calls',len(rec['direct_and_indirect_calls']))
if __name__=='__main__':
 parser=argparse.ArgumentParser()
 parser.add_argument('--ipa',type=Path,required=True)
 parser.add_argument('--out',type=Path,required=True)
 args=parser.parse_args()
 main(args.ipa,args.out)
