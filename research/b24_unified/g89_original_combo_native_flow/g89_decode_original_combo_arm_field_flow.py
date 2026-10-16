#!/usr/bin/env python3
"""G89: source-backed ORIGINAL 2010 iOS ARM combo-step native read/write data-flow.
Disassemble the 2010 ARM Mach-O from the user's IPA *only in an ephemeral job*.
Record exact source instruction neighborhoods around the verified +0x824 field,
conditional branch targets and original direct-call names. NO guessed combat
hit windows, weapon damage, original attack enum, executable, or VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,re,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_MEM,ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g76_original_combat'))
from g76_2010_native_arm_combat_method_provenance import parse_macho

TARGETS={
 'MainCharacter::GetCurrentMeleeAttackStep() const':0xea3b8,
 'MainCharacter::StartMeleeAttack(float)':0xee04c,
 'MainCharacter::UpdateComboAttackAction(int)':0xf18e4,
 'Actor::TestMeleeHit(Actor*)':0xdfd94,
 'Actor::Damage(float)':0xd9194,
 'WeaponDB::GetAttackEntityByIndex(int)':0xab3ec,
}
OTHER=re.compile(r'^(MainCharacter|Actor|CNPC|AttackEntity|ProjectileEntity)::.*'
                 r'(Combo|Melee|Attack|Damage|Hit|Hurt)',re.I)
COMBO_OFFSET=0x824
def branch_kind(m):
 n=m.lower().split('.')[0]
 if n in ('b','bx','bl','blx','cbz','cbnz'):return n
 if n.startswith('b') and n[1:] in ('eq','ne','cs','hs','cc','lo',
                   'mi','pl','vs','vc','hi','ls','ge','lt','gt','le'):return n
 return None
def research(ipa,out):
 if ipa.stat().st_size != 248613763:raise ValueError('original owner 2010 iOS 1.0.0 file size mismatch')
 with zipfile.ZipFile(ipa) as z:
  binary=z.read('Payload/IronMan2.app/IronMan2')
 parsed=parse_macho(binary)
 rows=parsed['entries']
 labels=subprocess.run(['c++filt'],input='\n'.join(r[0] for r in rows)+'\n',
       capture_output=True,text=True,check=True).stdout.splitlines()
 if len(labels)!=len(rows):raise ValueError('native original 2010 symbols count changed')
 byname=collections.defaultdict(list);byaddr=collections.defaultdict(list)
 for row,name in zip(rows,labels):
  byname[name].append(row)
  byaddr[row[1]&~1].append(name)
 for name,expected in TARGETS.items():
  addresses={r[1]&~1 for r in byname[name]}
  if addresses!={expected}:raise ValueError('original 2010 exact native method address drift: '+name+' '+str(addresses))
 addresses=sorted(set(r[1]&~1 for r in rows))
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for decoder in (arm,thumb):decoder.detail=True
 section=[s for s in parsed['sections'] if s[3]=='__text']
 def disassemble(row):
  addr=row[1]&~1
  sec=next((s for s in section if s[0]<=addr<s[0]+s[1]),None)
  if not sec:return None
  idx=bisect.bisect_right(addresses,addr)
  next_symbol=addresses[idx] if idx<len(addresses) else sec[0]+sec[1]
  size=min(next_symbol-addr,sec[0]+sec[1]-addr,8192)
  filepos=sec[2]+addr-sec[0]
  if size<4 or filepos+size>len(binary):return None
  decoded=list((thumb if row[1]&1 else arm).disasm(binary[filepos:filepos+size],addr))
  if not decoded:return None
  return addr,size,decoded
 def note(i,base):
  return {'offset_hex':hex(i.address-base),'mnemonic':i.mnemonic,
          'operands':i.op_str[:100]}
 def method_record(name,row):
  raw=disassemble(row)
  if raw is None:return None
  start,source_size,ops=raw
  refs=[];branches=[];calls=[]
  for idx,i in enumerate(ops):
   for op in i.operands:
    if op.type==ARM_OP_MEM and op.mem.disp==COMBO_OFFSET:
     op_kind=('write' if i.mnemonic.startswith(('str','vstr','stm','swp'))
              else 'read' if i.mnemonic.startswith(('ldr','vldr','ldm'))
              else 'other')
     window=[note(x,start) for x in ops[max(0,idx-7):min(len(ops),idx+11)]]
     refs.append({'source_pc_hex':hex(i.address),
       'offset_hex':hex(i.address-start),'operation':op_kind,
       'original_ARM_insn':note(i,start),
       'nearby_ordered_native_instructions':window,
       'field_source_verified':'MainCharacter combo step +0x824',
       'control_flow_interpretation_verified':False})
   if i.mnemonic.startswith(('bl','blx')) and i.operands:
    op=i.operands[0];target=(op.imm&~1) if op.type==ARM_OP_IMM else None
    calls.append({'offset_hex':hex(i.address-start),
     'target_address_hex':hex(target) if target is not None else None,
     'symbol_names':byaddr.get(target,[])[:3] if target is not None else [],
     'indirect_register_call':target is None})
   kind=branch_kind(i.mnemonic)
   if kind is None or kind in ('bl','blx'):continue
   target=None
   if i.operands and i.operands[-1].type==ARM_OP_IMM:
    target=i.operands[-1].imm&~1
   branches.append({'offset_hex':hex(i.address-start),
      'mnemonic':i.mnemonic,
      'immediate_target_in_same_bounded_function':
       bool(target is not None and start<=target<start+source_size),
      'immediate_target_relative_hex':
       hex(target-start) if target is not None and start<=target<start+source_size else None})
  return {'source_symbol':name,'native_address_hex':hex(start),
   'function_bounded_bytes':source_size,'decoded_instructions':len(ops),
   'combo_0x824_accesses':refs,'conditional_or_jump_edges':branches[:160],
   'direct_and_register_calls':calls[:120],
   'did_not_prove_2010_hit_window':True,'did_not_prove_combo_input_buffer_rule':True}
 focus={}
 for name in TARGETS:
  rec=method_record(name,byname[name][0])
  if rec is None:raise ValueError('native target not disassembled: '+name)
  focus[name]=rec
 if not any(e['operation']=='read' for e in
    focus['MainCharacter::GetCurrentMeleeAttackStep() const']['combo_0x824_accesses']):
  raise ValueError('original getter +0x824 read not observed')
 if len(focus['MainCharacter::StartMeleeAttack(float)']['combo_0x824_accesses'])<3:
  raise ValueError('original StartMeleeAttack 3 combo memory instructions not found')
 related=[]
 seen=set()
 for name,items in byname.items():
  if not OTHER.search(name) or name in focus:continue
  row=items[0]
  key=row[1]&~1
  if key in seen:continue
  seen.add(key)
  rec=method_record(name,row)
  if rec is None:continue
  significant=bool(rec['combo_0x824_accesses'])
  if not significant:
   significant=any(any(any(term in n for term in (
     'StartMeleeAttack','UpdateComboAttackAction','TestMeleeHit','GetCurrentMeleeAttackStep'))
     for n in c['symbol_names']) for c in rec['direct_and_register_calls'])
  if significant:related.append(rec)
 counts=collections.Counter(x['operation'] for x in
        focus['MainCharacter::StartMeleeAttack(float)']['combo_0x824_accesses'])
 report={'game':'user owned original Iron Man 2 iOS 2010 v1.0.0',
 'source_2010_ARM_methods_verified':len(focus),
 'actual_source_StartMeleeAttack_combo_0x824_operations':dict(counts),
 'exact_source_method_bounded_instruction_flow':focus,
 'other_original_methods_referencing_combo_step_or_melee_call':related[:50],
 'related_symbol_count':len(related),
 'source_native_0x824_field_accesses_are_REAL':True,
 'native_combo_0x824_field_value_semantics_fully_reconstructed':False,
 'original_source_hit_active_start_end_frames':None,
 'original_source_attack_per_weapon_damage_numeric_values':None,
 '2010_iOS_native_attack_controller_enabled_on_Vita':False,
 'no_original_executable_assembly_bytes_exported':True,
 'no_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G89_REAL_ORIGINAL_2010_ARM_COMBO_0x824_BRANCH_AND_WRITES.json').write_text(
      json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G89 authentic owner 2010 ARM combo +0x824 read/write provenance 6 method addresses')
 print('G89 MAIN StartMeleeAttack 0x824 access count:',dict(counts))
 for name,rec in focus.items():
  print('ORIGINAL FN',name,'pc',rec['native_address_hex'],
        'instructions',rec['decoded_instructions'],'branches',len(rec['conditional_or_jump_edges']),
        'calls',len(rec['direct_and_register_calls']))
  for entry in rec['combo_0x824_accesses']:
   print('  VERIFIED 0x824',entry['source_pc_hex'],entry['operation'],
         entry['original_ARM_insn']['mnemonic'],entry['original_ARM_insn']['operands'])
   for entry2 in entry['nearby_ordered_native_instructions']:
    print('    CTX',entry2['offset_hex'],entry2['mnemonic'],entry2['operands'])
 print('RELATED METHODS',len(related))
 for rec in related[:20]:
  print('  RELATED',rec['source_symbol'],rec['native_address_hex'],
       '0x824 entries',len(rec['combo_0x824_accesses']))
 print('SOURCE HIT FRAMES/DAMAGE STILL UNKNOWN. NO VPK.')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();research(a.ipa,a.out)
