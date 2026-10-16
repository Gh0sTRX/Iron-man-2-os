#!/usr/bin/env python3
"""G97: trace full bounded ORIGINAL 2010 iOS ARM source methods that
actually load attack data, do projectile/melee attacks, test/hit, and
apply damage. No reverse invented WeaponDB numerical values or hit frames.
User-owned IPA read transiently. JSON function OPCODES and bounded
xrefs ONLY; do not redistribute executable or 3D licensed resources.
"""
from __future__ import annotations
import argparse,bisect,collections,json,subprocess,sys,zipfile,re,struct
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_MEM,ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g76_original_combat'))
from g76_2010_native_arm_combat_method_provenance import parse_macho
CHECKED_NAMES=[
 'AttackEntity::LoadFromFile(', 'AttackEntity::DoAttack(',
 'AttackEntity::DoProjectileAttack(', 'ProjectileEntity::HitImpactActor(',
 'ProjectileEntity::UpdateCollisions(', 'ProjectileEntity::DoSplashDamage(',
 'ProjectileEntity::LoadFromFile(', 'WeaponDB::AddNewAttackEntity(',
 'WeaponDB::GetAttackEntityByIndex(', 'Actor::CanAttack(', 'Actor::Damage(',
 'Actor::TestMeleeHit(', 'CNPC::OnHit(', 'MainCharacter::UpdateMeleeAttackState(',
 'MainCharacter::UpdateComboAttackAction(', 'MainCharacter::DoUniBeamAttack(',
]
def main(path,out):
 if path.stat().st_size!=248613763:raise ValueError('Not exact private owner 2010 IPA')
 with zipfile.ZipFile(path) as a:executable=a.read('Payload/IronMan2.app/IronMan2')
 native=parse_macho(executable)
 symbols=native['entries']
 dem=subprocess.run(['c++filt'],input='\n'.join(x[0] for x in symbols)+'\n',
   text=True,capture_output=True,check=True).stdout.splitlines()
 if len(dem)!=len(symbols):raise ValueError('2010 C++ demangle mismatch')
 name_map=collections.defaultdict(set);addr_map=collections.defaultdict(set)
 for x,n in zip(symbols,dem):
  name_map[n].add(x[1]&~1)
  addr_map[x[1]&~1].add(n)
 addresses=sorted(addr_map)
 text_sects=[s for s in native['sections'] if s[3]=='__text']
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for cs in (arm,thumb):cs.detail=True
 methods=[]
 visited=set()
 for prefix in CHECKED_NAMES:
  aliases=sorted(n for n in name_map if n.startswith(prefix))
  if not aliases:
   # Optional original method may truly not exist; explicitly report
   # the missing source, never replace with a guessed function.
   methods.append({'original_method_prefix_requested':prefix,
     'original_symbol_found':False,'exact_damage_unknown':True})
   continue
  for name in aliases:
   rows=[r for r,n in zip(symbols,dem) if n==name]
   locations={r[1]&~1 for r in rows}
   if len(locations)!=1:
    raise ValueError('original native same name resolves divergent methods: '+name)
   row=rows[0];a=row[1]&~1
   if a in visited:continue
   visited.add(a)
   sec=next((s for s in text_sects if s[0]<=a<s[0]+s[1]),None)
   if sec is None:continue
   nxt=bisect.bisect_right(addresses,a)
   n=addresses[nxt] if nxt<len(addresses) else sec[0]+sec[1]
   size=min(n-a,sec[0]+sec[1]-a,8192)
   if size<4:continue
   file_off=sec[2]+a-sec[0]
   if file_off+size>len(executable):raise ValueError('Mach-O text outside file')
   ins=list((thumb if row[1]&1 else arm).disasm(
        executable[file_off:file_off+size],a))
   fields=[];calls=[];branches=[];touched_damage_slots=[]
   for i in ins:
    memory=[o for o in i.operands if o.type==ARM_OP_MEM]
    for op in memory:
     f={'relative_pc_hex':hex(i.address-a),
       'operation':i.mnemonic,
       'base_register_int':int(op.mem.base),
       'offset_hex':hex(op.mem.disp),
       'original_register_operands':i.op_str}
     fields.append(f)
     if op.mem.disp in (0x824,0x828,0x82c,0x830,0x3bc,0x394):
      touched_damage_slots.append(f)
    if i.mnemonic.startswith(('bl','blx')):
     target=None
     if i.operands and i.operands[0].type==ARM_OP_IMM:target=i.operands[0].imm&~1
     calls.append({'relative_pc_hex':hex(i.address-a),
       'source_original_called_address_hex':hex(target) if target is not None else None,
       'source_original_called_symbols':sorted(addr_map.get(target,set()))[:6],
       'indirect_vtable_register_call':target is None})
    if (i.mnemonic.startswith('b') or i.mnemonic in ('cbz','cbnz')) and not i.mnemonic.startswith(('bl','bic','bfi','bfc','bfx')):
     target=None
     if i.operands and i.operands[-1].type==ARM_OP_IMM:
      target=i.operands[-1].imm&~1
     branches.append({'relative_pc_hex':hex(i.address-a),'ARM_opcode':i.mnemonic,
       'source_target_within_function_relative_hex':
       hex(target-a) if target is not None and a<=target<a+size else None})
   # Full bounded source instructions useful for data-flow of load
   # descriptor slots, but do not make a reconstructed native executable.
   opcodes=[{'pc_hex':hex(i.address),'offset_hex':hex(i.address-a),
             'mnemonic':i.mnemonic,'operand_register_or_literal':i.op_str}
            for i in ins]
   methods.append({'source_method':name,'original_symbol_found':True,
    'original_ARM_address_hex':hex(a),'original_ARM_or_Thumb':'thumb' if row[1]&1 else 'ARM',
    'source_bounded_function_length_bytes':size,
    'original_decoded_instruction_count':len(ins),
    'real_native_pointer_mem_accesses':fields,
    '2010_source_combo_and_actor_resource_field_accesses':touched_damage_slots,
    'real_native_calls':calls,
    'ARM_control_flow_branch_sites':branches,
    'full_bounded_original_source_opcode_metadata_NOT_machine_bytes':opcodes,
    'original_hit_active_gameplay_frame_confirmed':False,
    'typed_actual_source_AttackEntity_damage_float_value_confirmed':False})
 if not any(x.get('original_symbol_found') and x['source_method'].startswith('AttackEntity::LoadFromFile(') for x in methods):
  raise ValueError('2010 original AttackEntity::LoadFromFile method missing')
 if not any(x.get('original_symbol_found') and x['source_method'].startswith('Actor::Damage(') for x in methods):
  raise ValueError('2010 original Actor::Damage method missing')
 if not any(x.get('original_symbol_found') and x['source_method'].startswith('MainCharacter::UpdateMeleeAttackState(') for x in methods):
  raise ValueError('2010 original native combo update missing')
 report={'version':'2010 owner iOS 1.0.0 source only',
  'targeted_original_ARM_function_records_found':sum(bool(m.get('original_symbol_found')) for m in methods),
  'original_CPP_methods':methods,
  'WEAPON_DB_SERIALIZED_DATA_ACTUALLY_TYPED':False,
  'HIT_ACTIVE_START_END_ACTUALLY_PROVED':False,
  'B24_NATIVE_VITA_ENEMY_AI_ACTUALLY_INTEGRATED':False,
  'NO_FAKE_ATTACK_DAMAGE_OR_HIT_FRAMES':True,
  'NO_ORIGINAL_IPA_GAME_BINARY_COMMITTED':True,'NO_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G97_AUTHENTIC_2010_ATTACK_ENTITY_PROJECTILE_HIT_DAMAGE_ARM_PROVENANCE.json').write_text(json.dumps(
   report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G97 ORIGINAL 2010 native method count',report['targeted_original_ARM_function_records_found'])
 for m in methods:
  if m.get('original_symbol_found'):
   print('G97 SOURCE',m['source_method'],m['original_ARM_address_hex'],
     'native instructions',m['original_decoded_instruction_count'],
     'calls',len(m['real_native_calls']),
     'mem field',len(m['real_native_pointer_mem_accesses']))
   if m['source_method'].startswith('Actor::CanAttack('):
    print('G103 genuine original 2010 native Actor::CanAttack ARM instructions, unlike arbitrary class/attack IDs')
    for a0 in m['full_bounded_original_source_opcode_metadata']:
     print('G103 ORIG ACTOR CAN ATTACK',a0['offset_hex'],a0['mnemonic'],a0['operand_register_or_literal'])
  else:print('MISSING SOURCE SYMBOL',m['original_method_prefix_requested'])
 print('NO 2010 damage or hit frames guessed; NO VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();main(a.ipa,a.out)
