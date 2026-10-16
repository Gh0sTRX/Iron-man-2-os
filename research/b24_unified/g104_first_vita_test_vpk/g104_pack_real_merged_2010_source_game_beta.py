#!/usr/bin/env python3
"""G104 USER-AUTHORIZED REAL Vita test VPK packaging for actual G95/G92
B24 unified native-game ELF. This is NOT a full original iOS combat port.
Requires VitaSDK CMake-generated REAL signed SELF + original SFO, then
packages all original G68 Stark Expo scene+collision assets and all source
G85 248 Mark V 629-vertex IM2V, G8/WM animations, five original suits.
No guessed original 2010 damage/hit frames; G11 immortal debug practice dummy.
New app TITLE_ID prevents overwriting old B24 port VPK.
"""
import argparse,hashlib,json,os,struct,zipfile
from pathlib import Path
TITLE_ID='IM2G10401'
OUTNAME='IronMan2_B24_G104_G95_Stark_Expo_MarkV_248_Original_Movement_Static_Dummy_TEST.vpk'
def psf(z):
 raw=z.read('sce_sys/param.sfo')
 magic,ver,keybase,datbase,n=struct.unpack_from('<5I',raw)
 if magic!=0x46535000:raise ValueError('Vita original SFO invalid')
 res={}
 for i in range(n):
  koff,fmt,length,maxlen,off=struct.unpack_from('<HHIII',raw,20+i*16)
  key=raw[keybase+koff:].split(b'\0',1)[0].decode('ascii')
  value=raw[datbase+off:datbase+off+length]
  res[key]=value.split(b'\0',1)[0].decode('utf8','replace') if fmt==0x204 else value
 return res
def main(work,build,destination):
 if not (work/'src/main.c').is_file():raise ValueError('Missing actual native B24 main!')
 src=(work/'src/main.c').read_text()
 cm=(work/'CMakeLists.txt').read_text()
 for term in ('G92_STATIC_DUMMY_SOURCE_IN_SINGLE_MAIN','B24_G85_NATIVE_MARKV_629',
              'B24_G87_REAL_TRANSITION_EVENTS','G84_OPTIONAL_TRUE_B24_MAIN'):
  if term not in src:raise ValueError('The actual source gameplay missing '+term)
 for flag in ('B24_G92_STATIC_DUMMY_SOURCE_PREVIEW','B24_G85_NATIVE_MARKV_629',
              'B24_G75_ORIGINAL_SUN_LIGHTING_CANDIDATE'):
  if flag not in cm:raise ValueError('Missing actual opt-in game CMake '+flag)
 paths=sorted(build.glob('*.vpk'))
 if len(paths)!=1:raise ValueError('Real VitaSDK CMake must generate exactly ONE base VPK; found '+str(paths))
 base=paths[0]
 if not base.stat().st_size>20000:raise ValueError('Missing actual generated Vita package')
 with zipfile.ZipFile(base) as z:
  n=set(z.namelist())
  if not {'eboot.bin','sce_sys/param.sfo'}.issubset(n):
   raise ValueError('VitaSDK did not sign and package original real eboot.bin')
  info=psf(z)
  if info.get('TITLE_ID')!=TITLE_ID:raise ValueError('G104 independently installable title ID wrong '+str(info))
  if z.testzip():raise ValueError('VitaSDK created a damaged VPK')
 to_add={}
 for folder,suffix in [
  ('animations','.im2v'),('animations','.im2k'),('animations','.im2m'),
  ('models','.im2t'),('maps','.im2map'),('maps','.c1g2'),
  ('maps','.c1uv'),('maps','.c1ma'),('maps','.c1wc'),('maps','.c1tx'),
  ('assets','.g66m'),('assets','.g66t'),('assets','.g66c'),
  ('assets','.g73m')]:
  root=work/folder
  if not root.is_dir():continue
  for f in root.glob('*'+suffix):
   to_add[f.relative_to(work).as_posix()]=f
 if len([x for x in to_add if x.startswith('animations/') and x.endswith('.im2v')])<248:
  raise ValueError('Missing G85 original MarkV 248 source pose bank')
 mk=[x for x in to_add if x.startswith('animations/suitcase_ironman_') and x.endswith('.im2v')]
 if len(mk)!=248:raise ValueError('NOT all genuine 248 MarkV 2010 source clips '+str(len(mk)))
 for name in mk:
  raw=to_add[name].read_bytes()
  if len(raw)<20:raise ValueError('G85 original animation invalid')
  magic,nv,frames,fps,ms=struct.unpack_from('<4sIIII',raw)
  if magic!=b'IM2V' or nv!=629 or fps!=20 or frames<1 or len(raw)!=20+frames*nv*12:
   raise ValueError('G85 original MarkV 629-vertex 20Hz pose stream malformed: '+name)
 city=to_add.get('assets/G66_city.g66m')
 collision=to_add.get('assets/G66_original_collision.g66c')
 if not city or not collision:raise ValueError('Missing ORIGINAL 2010 Stark Expo source scene/collision in package')
 raw=collision.read_bytes()
 if struct.unpack_from('<II',raw,4)!=(1,1910):
  raise ValueError('Original 2010 C1L1 collision 1910 triangles source wrong')
 atlases=[x for x in to_add if x.startswith('assets/G66_city_tex_') and x.endswith('.g66t')]
 if len(atlases)!=31:raise ValueError('G68 true 2010 city must include 31 original texture atlases')
 destination.parent.mkdir(parents=True,exist_ok=True)
 # Keep certified VitaSDK eboot.bin and SFO content, inject ALL genuine
 # source asset payloads, replace only stale source files when necessary.
 # Copy compressed existing VPK contents, so no guessed eboot/stub.
 with zipfile.ZipFile(base) as orig,zipfile.ZipFile(destination,'w',allowZip64=True) as out:
  original=set()
  for name in orig.namelist():
   source=to_add.pop(name,None)
   data=source.read_bytes() if source is not None else orig.read(name)
   i=orig.getinfo(name)
   out.writestr(i,data)
   original.add(name)
  for name,source in sorted(to_add.items()):
   out.write(source,arcname=name,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
 with zipfile.ZipFile(destination) as z:
  if z.testzip():raise ValueError('G104 candidate VPK ZIP integrity bad')
  final=set(z.namelist())
  if len(final)!=len(z.namelist()):raise ValueError('Duplicate ZIP member names')
  assert psf(z)['TITLE_ID']==TITLE_ID
  assert {'eboot.bin','sce_sys/param.sfo','assets/G66_city.g66m',
    'assets/G66_original_collision.g66c','models/suitcase.im2t'}.issubset(final)
  assert len([n for n in final if n.startswith('animations/suitcase_ironman_') and n.endswith('.im2v')])==248
  assert len([n for n in final if n.startswith('assets/G66_city_tex_') and n.endswith('.g66t')])==31
  if len(z.read('eboot.bin'))<100000:raise ValueError('eboot generated too small')
 size=destination.stat().st_size
 dig=hashlib.sha256(destination.read_bytes()).hexdigest()
 qa={'candidate_filename':destination.name,'title_id':TITLE_ID,
  'kind':'EXPERIMENTAL user-authorized PS Vita gameplay beta for visible world and one dummy',
  'source_native_program':'REAL VitaSDK CMake im2_beta executable signed into eboot.bin',
  'original_source_game_full_attack_damage_completed':False,
  'original_source_damage_per_26_attack_verified':False,
  '2010_original_hit_active_frames_verified':False,
  'original_2010_enemy_npc_AI_included':False,
  'real_PSVita_hardware_playback_verified':False,
  'original_2010_G68_city_mesh_verified':True,
  'original_2010_G68_collision_1910_verified':True,
  'original_C1L1_31_texture_atlases_verified':True,
  'original_2010_MarkV_248_pose_streams_packaged':248,
  'single_real_B14_physics_and_G83_animation_main':True,
  'G92_one_stationary_indestructible_dummy_with_DEBUG_flash':True,
  'G95_native_source_Sun_color_candidate_not_exact_original_shader':True,
  'known_TEST_WARNINGS':'Experimental movement/flight/combo and primitive invulnerable dummy; real iOS combat timings/damage/AI unsupported, Vita frame rate and startup not device-tested',
  'vpk_size_bytes':size,'vpk_sha256':dig,'vpk_generated_by_real_vita_CMake':True}
 destination.with_suffix('.qa.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False)+'\n')
 print('G104 AUTHORISED BETA REAL Vita VPK PASS',destination,size,dig)
 print('G104 original 2010 source 248 MarkV pose, 31 city atlases, 1910 collision; source light and in-game dummy enabled; NOT full original iOS combat.')
if __name__=='__main__':
 a=argparse.ArgumentParser()
 a.add_argument('--work',type=Path,required=True)
 a.add_argument('--build',type=Path,required=True)
 a.add_argument('--out',type=Path,required=True)
 o=a.parse_args();main(o.work,o.build,o.out)
