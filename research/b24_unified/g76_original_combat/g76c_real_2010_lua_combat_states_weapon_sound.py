#!/usr/bin/env python3
"""G76C independently decode original 2010 iOS Lua gameplay 'states' callbacks,
weapon/entity name registries and genuine hit/shot audio filenames.
Metadata only: not executing original Lua, not decoding actual SFX audio,
not declaring guessed combat constants. NO VPK.
"""
from __future__ import annotations
import argparse,collections,json,re,zipfile,sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode
from b24_g27_original_source_lua51_native_global_call_sites import NativeLua,HEADER,calls
KEY=re.compile(r'(?i)attack|combo|hit|hurt|death|dead|weapon|health|shield|damage|energy|projectile|melee|beam|missil|fire|aim|state|shot|splash|lock|gun|punch|kick|actor|input')
def flatten(fn,out):
 out.append(fn)
 for child in fn['original_child_functions']:flatten(child,out)
def run(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  states=z.read('Payload/IronMan2.app/states')
  origins=[m.start() for m in re.finditer(re.escape(HEADER[:5]),states)]
  lua=[]
  for ofs in origins:
   parser=NativeLua(states,ofs)
   if parser.fetch(12)!=HEADER:raise ValueError('bad real original states Lua5.1 signature')
   first=parser.function()
   allcode=[];flatten(first,allcode)
   const=[x for f in allcode for x in f['native_constants']]
   total=sum(len(f['native_function_code']) for f in allcode)
   static=[]
   for f in allcode:
    cs,_=calls(f,{})
    static+=cs
   combatconst=[v for v in const if isinstance(v,str) and KEY.search(v)]
   seen=[]
   for k in combatconst:
    if k not in seen:seen.append(k)
   lua.append({
    'original_byte_offset':ofs,'original_encoded_chunk_bytes':parser.pos-ofs,
    'lua_5_1_prototype_count':len(allcode),
    'lua_bytecode_instructions':total,
    'source_original_combat_related_constants':seen,
    'static_native_global_calls':collections.Counter(x['native_global_function'] for x in static),
    'combat_calls_examples':[{'name':x['native_global_function'],
       'arg_constants_or_register_propagation_candidates':x['literal_or_statically_tracked_arguments']}
       for x in static if KEY.search(x['native_global_function'])][:100],
    'original_runtime_combat_state_transitions_proven':False
   })
  app='Payload/IronMan2.app/'
  sound=[f for f in z.infolist() if f.filename.startswith(app)
          and '/' not in f.filename[len(app):] and f.filename.split('/')[-1].startswith('sfx_')]
  sample=[]
  for f in sound:
   short=f.filename[len(app):]
   if KEY.search(short):
    raw=z.read(f)
    sample.append({'genuine_original_sfx_filename':short,
        'compressed_asset_bytes':len(raw),
        'source_file_first_16_bytes_hex':raw[:16].hex(),
        'actual_codec_demuxed':False})
  packs=[]
  for typ,ext in [('models','.bdae'),('textures','.tga')]:
   src=z.read(app+typ)
   records=decode(src,ext)
   matched=[{'original_record_name':r.name,'native_packed_bytes':r.end-r.start}
     for r in records if KEY.search(r.name)]
   packs.append({'archive':typ,'total_native_records':len(records),
                 'combat_effect_or_weapon_named_records':matched})
  result={'origin':'2010 iOS original IPA states Lua VM and original archived filenames',
      'actual_original_state_Lua_binary_signature_count':len(origins),
      'source_state_lua_bytecode_blocks':lua,
      'source_original_SFX_total':len(sound),
      'genuine_combat_named_sfx':sample,
      'authored_combat_model_and_texture_names':packs,
      'original_sound_codec_decode_completed':False,
      'actual_damage_HP_or_fire_rate_recovered_from_state_scripts':False,
      'state_source_conditional_branch_graph_executed':False,
      'no_VPK_generated':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G76C_ORIGINAL_2010_STATES_WEAPON_EFFECT_SOUND_SOURCE_METADATA.json').write_text(json.dumps(
     result,ensure_ascii=False,indent=2,default=list)+'\n')
 print('PASS G76C real 2010 Lua game STATES',len(lua),'combat named original SFX',len(sample),'total SFX',len(sound))
 for x in lua:print('Original Lua source states chunk',x['original_byte_offset'],
   'functions',x['lua_5_1_prototype_count'],'instr',x['lua_bytecode_instructions'],
   'combat keys',x['source_original_combat_related_constants'][:25])
 print('TRUE_COMBAT_SFX_EXAMPLES',[a['genuine_original_sfx_filename'] for a in sample[:18]])
 print('Native weapon/stat values not assumed from filenames. NO VPK.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();run(a.ipa,a.out)
