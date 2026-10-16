#!/usr/bin/env python3
"""G78D original 2010 native C1L1 class instance audit for weapons.
Prove whether AttackEntity/ProjectileEntity are actual BCLARA scene
instances or only native class schema templates; protects from inventing
per-weapon damage numbers by reading template ID as damage.
"""
import argparse,collections,json,re,zipfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
PATTERN=re.compile(r'(?i)attack|weapon|projectile|combat|bullet|missile|repuls|damage|hurt|enemy|npc')
def audit(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  source=z.read('Payload/IronMan2.app/clev')
 first=get_exact(source,decode(source,'.bclara'),'level1.bclara')
 authentic=summarize(first)
 rows=authentic['source_2010_typed_class_instances']
 classes=authentic['source_2010_class_schema']
 relevant_types=[x for x in classes if PATTERN.search(x['original_class_name'])]
 relevant_inst=[x for x in rows if PATTERN.search(
    x['original_class_name']) or PATTERN.search(x['original_name'])]
 counted=collections.Counter(x['original_class_name'] for x in rows)
 result={'original_level1_byte_count':len(first),
   'actual_original_source_193_type_count':len(classes),
   'genuine_combat_relevant_native_schema_classes':relevant_types,
   'genuine_combat_relevant_typed_native_scene_instances':[
       {'original_name':q['original_name'],
        'class':q['original_class_name'],
        'class_id':q['original_class_id'],
        'original_numeric_name_id':q['original_numeric_name_id']}
         for q in relevant_inst],
   'global_class_instance_frequency':dict(counted),
   'Source_WeaponDB_values_from_class_schema_NOT_proven':True,
   'source_only_no_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G78D_ORIGINAL_2010_CLASS_SCHEMA_WEAPON_VS_REAL_INSTANCE.json').write_text(
    json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('G78D 2010 real CLARA combat classes',
   [(x['original_class_id'],x['original_class_name']) for x in relevant_types])
 print('G78D real instantiated combat scene class frequencies',
   [(k,v) for k,v in counted.most_common() if PATTERN.search(k)])
 print('G78D named actual combat nodes sample',
   [(q['original_name'],q['original_class_name']) for q in relevant_inst[:35]])
 print('Cannot label 2010 schema class offsets as confirmed weapon damage values')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--ipa',required=True,type=Path)
 a.add_argument('--out',required=True,type=Path);q=a.parse_args();audit(q.ipa,q.out)
