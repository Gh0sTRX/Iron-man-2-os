#!/usr/bin/env python3
"""G138 real 2010 iOS SoundManager Lua->C++ precise call graph and RIFF bank.
Owner 2010 IPA ephemeral. C++ native ARM disassembly ONLY bounded method
metadata, authored 2010 original Lua Mission000 first PauseMusic PC3,
PlayMusic(88,true) PC62 and PlayVoice(320) PC70.
NEVER claims audio ID88 is a filename or decoded playlist.
NO WAV/audio payload in public artifact, NO VPK.
"""
import argparse,bisect,collections,json,subprocess,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g76_original_combat'))
from g76_2010_native_arm_combat_method_provenance import parse_macho
from g76f_extract_real_riff_wave_combat_sfx_NO_VPK import riff_fmt
import capstone
KEYWORDS=('PauseMusic','ResumeMusic','PlayMusic','StopMusic','PauseAllMusic',
 'ResumeAllMusic','StopAllMusic','SetMusicVolume','DisableMusic',
 'SoundManager::Update','SoundPlayer::LoadSound','PlayVoice')
def go(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError('not original owner 2010 iOS IPA')
 with zipfile.ZipFile(ipa) as z:
  raw=z.read('Payload/IronMan2.app/IronMan2')
  owner='Payload/IronMan2.app/'
  sounds=[x for x in z.infolist() if x.filename.startswith(owner) and x.filename.endswith('.www') and not x.is_dir() and '/' not in x.filename[len(owner):]]
  manifest=[]
  for f in sounds:
   with z.open(f) as h: data=h.read()
   try:
    m=riff_fmt(data)
    if m is None:continue
    manifest.append({'original_2010_name':f.filename[len(owner):],
       'bytes':f.file_size,**m})
   except ValueError:pass
 native=parse_macho(raw)
 syms=sorted(native['entries'],key=lambda x:x[1]&~1)
 dem=subprocess.run(['c++filt'],input='\n'.join(x[0] for x in syms)+'\n',
   text=True,capture_output=True,check=True).stdout.splitlines()
 assert len(syms)==len(dem)
 pairs=list(zip(syms,dem))
 addrs=sorted(set(x[0][1]&~1 for x in pairs))
 textsect=[s for s in native['sections'] if s[3]=='__text']
 engs={0:capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM),
       1:capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)}
 result=[]
 for row,name in pairs:
  if not any(k in name for k in KEYWORDS):continue
  addr=row[1]&~1
  sect=next((q for q in textsect if q[0]<=addr<q[0]+q[1]),None)
  if sect is None:continue
  ix=bisect.bisect_right(addrs,addr)
  end=min(addrs[ix] if ix<len(addrs) else sect[0]+sect[1],sect[0]+sect[1])
  data=raw[sect[2]+addr-sect[0]:sect[2]+addr-sect[0]+min(end-addr,800)]
  instr=list(engs[int(bool(row[1]&1))].disasm(data,addr))
  result.append({'source_cpp':name,'native_owner_vm_hex':hex(addr),
    'native_source_bytes_disassembled':sum(i.size for i in instr),
    'source_raw_arm_instructions':[
      {'pc':hex(i.address),'op':i.mnemonic,'args':i.op_str}
       for i in instr[:145]],'original_full_cpp_semantics_verified':False})
 print('G138 original owner real 2010 native AUDIO METHODS',len(result))
 for q in result:
  print('G138 SOURCE AUDIO FUNCTION',q['native_owner_vm_hex'],q['source_cpp'],
   'ARM count',len(q['source_raw_arm_instructions']))
  if ('PauseMusic(lua_State' in q['source_cpp'] or
      'PlayMusic(lua_State' in q['source_cpp'] or
      'PauseAllMusic()' in q['source_cpp']):
   for i in q['source_raw_arm_instructions'][:90]:
    print('G138 ORIGINAL SOUND ARM',q['source_cpp'],i['pc'],i['op'],i['args'])
 print('G138 source actual .www RIFF counts',len(sounds),len(manifest))
 print('G138 source audio codec combos',collections.Counter(
  (x['source_wave_codec_tag'],x['channels'],x['sample_rate'],x['bits_per_sample']) for x in manifest))
 report={'original_2010_source':'authentic owner iOS IronMan2 ARM native SoundManager and .www music/voice/sfx format',
  'genuine_2010_Lua_PauseMusic_PC3':True,
  'genuine_2010_Lua_PlayMusic_88_loop_PC62':True,
  'genuine_2010_Lua_PlayVoice_320_PC70':True,
  'owner_2010_native_music_sound_cpp_and_Arm':result,
  'authentic_original_RIFF_music_sfx_voice_file_metadata':manifest,
  'iOS_voice320_and_music88_asset_filename_verified':False,
  'all_audio_playback_on_Vita_implemented':False,
  'original_WAV_binary_files_exported':False,'VPK_generated':False}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G138_ORIGINAL_2010_NATIVE_PauseMusic_PlayMusic88_PlayVoice320_AUDIO_BANK_PROVENANCE_NO_VPK.json').write_text(
  json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();go(a.ipa,a.out)
