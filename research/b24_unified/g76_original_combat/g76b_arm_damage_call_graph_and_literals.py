#!/usr/bin/env python3
"""G76B original Gameloft 2010 ARMv7 combat native CALL graph and literal candidates.
Do not infer HP/damage constants from any untyped float pool; source file
never leaves ephemeral runner. This is real Mach-O, not B14 homebrew.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,math,re,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_OP_MEM,ARM_REG_PC
sys.path.insert(0,str(Path(__file__).resolve().parent))
from g76_2010_native_arm_combat_method_provenance import MAGIC,parse_macho
TARGETS=[
 'MainCharacter::StartMeleeAttack(','MainCharacter::UpdateComboAttackAction(',
 'MainCharacter::GetCurrentMeleeAttackStep(','MainCharacter::DoUniBeamAttack(',
 'MainCharacter::ThrowMissile(','MainCharacter::CheckThrowMissile(',
 'ProjectileEntity::DoSplashDamage(','ProjectileEntity::UpdateCollisions(',
 'ProjectileEntity::StartTrajectoryFly(','WeaponDB::FindWeaponEntityById(',
 'WeaponMgr::SetCurrentWeapon(','Actor::','SpawnPoint::','NPCSpawnMgr::',
 'AIFirepower::UpdateActionAttack','AIGroundTank::UpdateActionAttack',
 'WhiplashNPC::','FirepowerNPC::',
]
NARROW=re.compile(r'(damage|health|hp\b|shield|melee|attack|projectile|impact|collision|explos|fire|weapon|hit|missile|kill|cooldown|combo|uni.?beam|throw|radius|splash|bullet|life)',re.I)
def demangle(src):
 raw='\n'.join(s[0] for s in src)+'\n'
 out=subprocess.run(['c++filt'],input=raw,text=True,capture_output=True,check=True).stdout.splitlines()
 if len(out)!=len(src):raise ValueError('symbol offset mismatch')
 return out
def root(ipa:Path,out:Path):
 with zipfile.ZipFile(ipa) as z:
  executable=z.read('Payload/IronMan2.app/IronMan2')
 m=parse_macho(executable)
 entries=m['entries'];names=demangle(entries)
 # Do not accidentally select data symbols/objects as disassembly.
 codes=[(r,n) for r,n in zip(entries,names)
        if any(s[0]<=r[1]&~1 < s[0]+s[1] and s[3]=='__text' for s in m['sections'])]
 addresses=sorted({r[1]&~1 for r,n in codes})
 by_addr=collections.defaultdict(list)
 for row,name in codes:by_addr[row[1]&~1].append(name)
 act=[(r,name) for r,name in codes if NARROW.search(name)
      and (any(name.startswith(t) for t in TARGETS) or
           any(tag in name for tag in ('::Damage','::Hurt','::Health','::GetHP','::GetHit','::SetHP')))]
 # Every interesting unique address source only
 seen=set();act=[(r,n) for r,n in act if not ((r[1]&~1) in seen or seen.add(r[1]&~1))]
 sections=m['sections']
 cs_thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 cs_arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 for cs in (cs_thumb,cs_arm):cs.detail=True
 recs=[]
 for row,name in act:
  addr=row[1]&~1
  idx=bisect.bisect_right(addresses,addr)
  nxt=addresses[idx] if idx<len(addresses) else addr+4096
  sec=next((s for s in sections if s[0]<=addr<s[0]+s[1] and s[3]=='__text'),None)
  if not sec:continue
  section_end=sec[0]+sec[1]
  lim=max(0,min(nxt-addr,section_end-addr,16384))
  if lim<4:continue
  off=sec[2]+addr-sec[0]
  if off+lim>len(executable):continue
  cs=cs_thumb if row[1]&1 else cs_arm
  dec=list(cs.disasm(executable[off:off+lim],addr))
  edges=[];conditionals=[];literals=[]
  for i in dec:
   mn=i.mnemonic
   if mn.startswith(('bl','blx')) and len(i.operands)>=1:
    op=i.operands[0];tgt=op.imm if op.type==ARM_OP_IMM else None
    near=by_addr.get(tgt&~1,[]) if tgt is not None else []
    edges.append({'instruction_offset':i.address-addr,
       'call_type':mn,'target_virtual_address':f'0x{tgt:08x}' if tgt is not None else None,
       'known_symbol_name':near[:2],'unknown_register_call':tgt is None})
   elif mn.startswith(('beq','bne','bgt','bge','blt','ble','cbz','cbnz','bhi','bls')):
    conditionals.append({'relative_offset':i.address-addr,'opcode':mn,
                         'argument_short':i.op_str[:70]})
   # Explicit source PC literal candidates, only a float candidate, not typed damage.
   if mn.startswith('ldr') and len(i.operands)>=2 and i.operands[1].type==ARM_OP_MEM:
    operand=i.operands[1].mem
    if operand.base==ARM_REG_PC and operand.index==0:
     literal=(i.address+4)&~3 if row[1]&1 else i.address+8
     literal+=operand.disp
     if sec[0]<=literal<sec[0]+sec[1]:
      read=sec[2]+literal-sec[0]
      if 0<=read<=len(executable)-4:
       v=struct.unpack_from('<I',executable,read)[0]
       fl=struct.unpack_from('<f',executable,read)[0]
       if math.isfinite(fl) and .0001<abs(fl)<100000:
        literals.append({'instruction_offset':i.address-addr,'raw_literal_hex':f'0x{v:08x}',
           'untyped_float_candidate':round(fl,7),'is_verified_damage_or_HP':False})
  if len(recs)>=300:break
  recs.append({'original_method_demangled_cpp':name,'native_start_hex':f'0x{row[1]:08x}',
               'next_symbol_limited_bytes':lim,'decoded_instructions':len(dec),
               'direct_call_edges':edges[:180],'conditions_first':conditionals[:150],
               'literal_float_candidates_first':literals[:75],
               'verified_full_high_level_C_cpp_logic':False,
               'original_HP_or_damage_formula_verified':False})
 important=[r for r in recs if r['original_method_demangled_cpp'].startswith(
  ('MainCharacter::StartMeleeAttack','MainCharacter::UpdateComboAttackAction',
   'MainCharacter::DoUniBeamAttack','ProjectileEntity::DoSplashDamage'))]
 result={'source':'true 2010 MachO ARM 32bit; no copied native binary output',
         '2010_native_methods_detailed':len(recs),
         'selected_core_methods':important,
         'other_related_methods': [r for r in recs if r not in important],
         'source_native_call_graph_analyzed':True,
         'native_instructions_are_not_translated_into_exact_game_rules':True,
         'float_candidates_are_UNTYPED_memory_constants_not_confirmed_stats':True,
         'actual_2010_gameplay_damage_constants_verified':False,
         'no_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G76B_ORIGINAL_2010_NATIVE_DAMAGE_COMBAT_DIRECT_CALL_GRAPH.json').write_text(
   json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 print('PASS G76B genuine iOS C++ ARM control-flow disassembled methods',len(recs))
 for item in important:
  print('ORIGINAL_2010_COMBAT_NATIVE_FN',item['original_method_demangled_cpp'],
    'inst',item['decoded_instructions'],'edges',len(item['direct_call_edges']),
    'branches',len(item['conditions_first']),'candidate_floats',len(item['literal_float_candidates_first']))
  for edge in item['direct_call_edges'][:12]:
   print(' DIRECT_CALL',edge['instruction_offset'],edge['known_symbol_name'][:1] or edge['target_virtual_address'])
 print('Native function addresses proven; HP or DMG still unverified without tracing typed data-flow')
if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('--ipa',required=True,type=Path);q.add_argument('--out',required=True,type=Path)
 a=q.parse_args();root(a.ipa,a.out)
