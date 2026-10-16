#!/usr/bin/env python3
"""G76D source-only controlled ARM disassembly of specifically mapped original
2010 combat damage functions. No complete IPA, binary bytes, VPK or engine
port. Do not claim high-level formula from disassembly alone.
"""
from __future__ import annotations
import argparse,bisect,collections,json,subprocess,sys,struct,zipfile
from pathlib import Path
import capstone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from g76_2010_native_arm_combat_method_provenance import parse_macho
CANDIDATES=(
 'Actor::Damage(Actor*, float)',
 'Actor::Damage(float)',
 'MainCharacter::Damage(Actor*, float)',
 'Actor::TestMeleeHit(Actor*)',
 'MainCharacter::StartMeleeAttack(float)',
 'MainCharacter::GetCurrentMeleeAttackStep() const',
 'MainCharacter::UpdateComboAttackAction(int)',
 'MainCharacter::DoUniBeamAttack(',
 'ProjectileEntity::DoSplashDamage()',
 'ProjectileEntity::HitImpactActor()',
 'ProjectileEntity::UpdateCollisions()',
 'WeaponDB::GetAttackEntityByIndex(int)',
 'WeaponDB::AddNewAttackEntity(EntityData*)',
 'WeaponMgr::InitWeaponData(EntityData*, Entity3D*, int)',
 'CNPC::InitShield()',
 'CNPC::OnHit(Actor*, int, float)',
 'CNPC::UpdateStateHurt(int, CNPC::NPCStateNode&)',
 'CNPC::OnDie()',
 'AttackEntity::LoadFromFile(EntityData*)',
 'AttackEntity::DoAttack(',
 'AttackEntity::DoProjectileAttack(',
 'ProjectileEntity::LoadFromFile(EntityData*, ModelData)',
 'WeaponDB::AddNewAttackEntity(EntityData*)',
 'WeaponDB::AddNewWeapon(EntityData*)',
 'WeaponDB::FindWeaponEntityById(int)',
 'DoDamage(lua_State*)',
 'SetHealth(lua_State*)',
 'Actor::CanBeHurt(Actor*)',
 'Actor::OnTargetDie(Actor*)',
 'Actor::ActiveHurtSpecialFX(bool)'
)
def run(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  exe=z.read('Payload/IronMan2.app/IronMan2')
 m=parse_macho(exe);symbols=m['entries'];dem=subprocess.run(
   ['c++filt'],input='\n'.join(x[0] for x in symbols)+'\n',
   capture_output=True,text=True,check=True).stdout.splitlines()
 if len(symbols)!=len(dem):raise ValueError('genuine 2010 symbol demangler mismatch')
 addrs=sorted({s[1]&~1 for s in symbols})
 csa=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 cst=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 results=[]
 for row,name in zip(symbols,dem):
  if not name.startswith(CANDIDATES):continue
  addr=row[1]&~1
  sec=next((s for s in m['sections'] if s[3]=='__text' and s[0]<=addr<s[0]+s[1]),None)
  if not sec:continue
  nxtidx=bisect.bisect_right(addrs,addr)
  lim=min((addrs[nxtidx]-addr) if nxtidx<len(addrs) else 8192,sec[0]+sec[1]-addr,8192)
  off=sec[2]+addr-sec[0]
  if lim<=0 or off+lim>len(exe):continue
  decoded=list((cst if row[1]&1 else csa).disasm(exe[off:off+lim],addr))
  # Original virtual addresses, ARM mnemonics and operands only. No bytes,
  # no restored iOS machine executable and no hardcoded prototype stats.
  result={
   'original_gameloft_2010_native_method':name,
   'actual_start_hex':f'0x{row[1]:08x}','bounded_length_bytes':lim,
   'original_v7_thumb_mode':bool(row[1]&1),
   'parsed_instructions':len(decoded),
   'full_routine_limited_pseudo_assembly':[
    {'relative_address':f'+0x{i.address-addr:x}',
     'op':i.mnemonic,'registers_and_immediates':i.op_str}
      for i in decoded
   ],
   'arithmetic_ops_counts':dict(collections.Counter(i.mnemonic for i in decoded
     if i.mnemonic.startswith(('vadd','vsub','vmul','vdiv','vldr','vstr','vcvt','vcmp','add','sub','mul','cmp','ldr','str')))),
   'damage_HP_field_storage_offsets_verified':False,
   'original_attack_power_numeric_values_verified':False,
   'source_only':True
  }
  results.append(result)
 result={'source':'Original iOS ARM C++ exact symbol bounded instruction decodes',
         'targeted_original_method_count':len(results),
         'original_2010_combat_native_instruction_records':results,
         'not_portable_C_recovered':True,
         'no_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G76D_ORIGINAL_NATIVE_DAMAGE_HP_COMBO_ARM_INSTRUCTION_TRACE.json').write_text(
    json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('PASS G76D original native iOS exact control-flow instruction trace',len(results),'methods')
 for r in results:
  print('TRUE_COMBAT_FUNCTION',r['original_gameloft_2010_native_method'],
        'instructions',r['parsed_instructions'],'math instruction summary',r['arithmetic_ops_counts'])
 print('NO inferred 2010 damage values unless original serialized weapon DB and typed field map are decoded')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();run(a.ipa,a.out)
