#!/usr/bin/env python3
"""G78 SOURCE ORIGINAL 2010 iOS: map each AttackEntity and ProjectileEntity
EntityData property string into the exact destination 32-bit ARM C++ struct
offset. Read real Mach-O code+relocation data; NO fabricated weapon damage,
no original IPA/code bytes in output, no audio/game package/VPK.
"""
import argparse,collections,json,re,struct,subprocess,zipfile,sys
from pathlib import Path
import capstone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g76_original_combat'))
from g76_2010_native_arm_combat_method_provenance import parse_macho

METHODS=('AttackEntity::LoadFromFile(EntityData*)',
         'ProjectileEntity::LoadFromFile(EntityData*, ModelData)')
LOAD_CALLS={0xd7548,0xd76bc,0xd7830,0xd6f78}
def source(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  raw=z.read('Payload/IronMan2.app/IronMan2')
  resource_names=sorted(x.filename.removeprefix('Payload/IronMan2.app/')
    for x in z.infolist() if x.filename.startswith('Payload/IronMan2.app/')
    and x.filename.count('/')==2 and not x.is_dir())
 m=parse_macho(raw)
 segments=m['sections']
 def read_addr(va,length):
  for addr,size,off,name,segment in segments:
   if addr<=va and va+length<=addr+size:
    return raw[off+va-addr:off+va-addr+length]
  return None
 def signed_at(addr):
  data=read_addr(addr,4)
  return struct.unpack('<i',data)[0] if data is not None else None
 def field_name(addr):
  val=read_addr(addr,100)
  if val is None:return None
  name=val.split(b'\0',1)[0]
  if not 2<=len(name)<=86 or not re.fullmatch(rb'[a-zA-Z_][a-zA-Z0-9_.\-]{1,85}',name):return None
  return name.decode('ascii')
 names=[x[0] for x in m['entries']]
 dem=subprocess.run(['c++filt'],input='\n'.join(names)+'\n',
    capture_output=True,text=True,check=True).stdout.splitlines()
 assert len(dem)==len(names)
 native_2010_methods={entry[1]&~1:label for entry,label in zip(m['entries'],dem) if entry[1]}
 found={}
 cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 for symbol,name in zip(m['entries'],dem):
  if name not in METHODS:continue
  addr=symbol[1]&~1
  if symbol[1]&1:raise ValueError('expected ARM mode for '+name)
  blob=read_addr(addr,0x700)
  if blob is None:raise ValueError('source executable function truncated')
  ins=list(cs.disasm(blob,addr))
  captures=[]
  for idx,op in enumerate(ins):
   if op.mnemonic!='bl' or not op.op_str.startswith('#'):continue
   try:dest=int(op.op_str[1:],0)
   except ValueError:continue
   if dest not in LOAD_CALLS:continue
   last=ins[max(0,idx-9):idx]
   actual_name=None;name_addr=None;trace=[]
   for i in reversed(last):
    regmatch=re.fullmatch(r'r1, pc, (r\d+|ip|lr)',i.op_str)
    if i.mnemonic!='add' or not regmatch:continue
    reg=regmatch.group(1)
    for prev in reversed([j for j in last if j.address<i.address]):
     if prev.mnemonic!='ldr' or not prev.op_str.startswith(reg+', [pc, #'):continue
     mdisp=re.fullmatch(r'\w+, \[pc, #(0x[0-9a-f]+|\d+)\]',prev.op_str)
     if not mdisp:continue
     literal_addr=prev.address+8+int(mdisp.group(1),0)
     delta=signed_at(literal_addr)
     if delta is None:continue
     name_addr=i.address+8+delta
     actual_name=field_name(name_addr)
     trace=[hex(prev.address-addr),hex(i.address-addr)]
     break
    if actual_name:break
   raw_dest=None
   for j in reversed(last):
    t=re.fullmatch(r'r2, r4, #(0x[0-9a-f]+|\d+)',j.op_str)
    if j.mnemonic=='add' and t:
     raw_dest=int(t.group(1),0);break
   captures.append({
     'original_native_EntityData_property':actual_name,
     'field_name_string_address':hex(name_addr) if actual_name else None,
     '2010_native_load_call_target':hex(dest),
     'source_original_2010_data_getter_method_symbol':native_2010_methods.get(dest),
     'original_dest_member_offset':hex(raw_dest) if raw_dest is not None else None,
     'loader_CALL_relative_offset':hex(op.address-addr),
     'source_PC_rel_decode_steps':trace,
     'property_value_read_from_original_config_and_named':False,
     'unmapped_or_indirect_field':actual_name is None
   })
  found[name]={'original_ARM_addr':hex(addr),
      'recognized_property_calls':captures,
      'resolved_property_count':sum(x['original_native_EntityData_property'] is not None for x in captures)}
 if set(found)!=set(METHODS):raise ValueError('native source 2010 loader symbols changed')
 result={'authentic_original_IronMan2_2010_ARM':True,
   'original_WeaponDB_AttackEntity_and_ProjectileEntity_source_typed_field_loader':found,
   '2010_app_top_level_resource_filename_candidates_without_encoded_content':[
     n for n in resource_names
      if not n.startswith(('sfx_','text_','music_','video_')) and
         not n.lower().endswith(('.png','.jpg','.tga','.pvr','.wav','.mp3','.caf','.ogg'))][:160],
   'source_game_attack_damage_values_extracted':False,
   'authored_property_names_resolved_from_original_ARM_RODATA':True,
   'no_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G78_NATIVE_ORIGINAL_ATTACK_DAMAGE_EntityData_PROPERTY_MEMBER_MAP.json').write_text(
    json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 for method,rec in found.items():
  print('G78 REAL',method,rec['original_ARM_addr'],'source property names',rec['resolved_property_count'],'/',len(rec['recognized_property_calls']))
  for item in rec['recognized_property_calls']:
   print(' ORIGINAL PROPERTY',item['original_native_EntityData_property'],
       'MEMBER',item['original_dest_member_offset'],
       'getter',item['2010_native_load_call_target'])
 print('G78 Original game asset config names:',result['2010_app_top_level_resource_filename_candidates_without_encoded_content'][:80])
 print('No stat values claimed without recovering individual source EntityData instances')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();source(a.ipa,a.out)
