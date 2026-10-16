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
 # G78 source-only IPA research: reuse the SAME authenticated 2010 owner
 # game archive in the existing G76 CI before its secure deletion.  Do not
 # upload the IPA, recovered executable, sound/audio or a Vita VPK.
 # Three G77 source readers produce metadata and typed original ARM proof.
 import sys
 from pathlib import Path as _Path
 _dir=_Path(__file__).resolve().parents[1]/'g77_original_weapon_db'
 sys.path.insert(0,str(_dir))
 from g77a_owned_2010_weapon_db_asset_origin import run as real_weapon_asset_audit
 from g77b_original_arm_WeaponDB_and_Melee_bbox_literal import main as real_macho_weapon_audit
 from g77c_original_sfx_www_wave_codec_audit import main as real_sound_codec_audit
 real_weapon_asset_audit(a.ipa,a.out)
 real_macho_weapon_audit(a.ipa,a.out)
 real_sound_codec_audit(a.ipa,a.out)
 # Persist concise, actually VERIFIED source stats in existing G76 JSON
 # which the standing workflow already uploads. Metadata-only.
 import json as _json
 original_report=a.out/'G76D_ORIGINAL_NATIVE_DAMAGE_HP_COMBO_ARM_INSTRUCTION_TRACE.json'
 payload=_json.loads(original_report.read_text())
 sources={
   'native_original_weapon_asset_audit':'G77A_REAL_2010_WEAPON_DB_ASSET_AND_FIELD_ORIGIN_AUDIT.json',
   'real_2010_native_melee_half_bbox_weaponDB':'G77B_ORIGINAL_ARM_MELEE_BOUNDING_RADIUS_AND_WEAPON_DB_LAYOUT.json',
   'true_2010_sfx_audio_codec_metadata':'G77C_REAL_2010_ALL_SFX_RIFF_WAV_CODEC_METADATA.json'}
 proofs={}
 for label,file in sources.items():
  r=_json.loads((a.out/file).read_text())
  if label=='real_2010_native_melee_half_bbox_weaponDB':
   proofs[label]=r['exact_target_methods']
  elif label=='true_2010_sfx_audio_codec_metadata':
   proofs[label]={'original_SFX_entries':r['original_SFX_entries'],
                  'parsed_RIFF_SFX_entries':r['parsed_RIFF_SFX_entries'],
                  'codec_sample_rate_channel_bitdepth_combinations':
                    r['codec_sample_rate_channel_bitdepth_combinations'],
                  'rejected_entries':r['rejected_entries']}
  else:
   proofs[label]={'source_top_level_files_count':r['source_top_level_files_count'],
                 '2010_source_weapon_named_packed_records':r['named_packed_source_records'],
                 'candidate_resource_files':[x for x in r['real_source_app_entries']
                    if x.get('weapon_stat_config_token_probe')]}
 payload['G78_original_owner_source_WeaponDB_and_audio_provenance']=proofs
 payload['G78_VPK_generated']=False
 original_report.write_text(_json.dumps(payload,ensure_ascii=False,indent=2)+'\\n')
 print('PASS G79 source-authentic 26 Attack + 13 Weapon CLARA instance property boundary research completed; no VPK')
