#!/usr/bin/env python3
"""G140 real user's Iron Man 2 iOS 2010 1.0.0 IPA 803 RIFF original WWW
audio metadata, filename-scoped Level1 unmodified WAV export and offline
FFmpeg PCM 48k stereo preview, optional 1.0.3 SHA-by-filename comparison.
No original IPA or WAV payload is committed to GitHub. NO Vita VPK.
Authoritative extracted Level1 WAV 73 original items tested 2026-10-17.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,struct,subprocess,zipfile
def riff_fmt(raw):
 if len(raw)<44 or raw[:4]!=b'RIFF' or raw[8:12]!=b'WAVE':
  raise ValueError('original WWW is not RIFF WAVE')
 if int.from_bytes(raw[4:8],'little')+8>len(raw):
  raise ValueError('original WAVE raw RIFF length corrupted')
 pos=12;fmt=None,data=None
 while pos+8<=len(raw):
  key=raw[pos:pos+4];n=struct.unpack_from('<I',raw,pos+4)[0];pos+=8
  if pos+n>len(raw):raise ValueError('original WAVE chunk overflow')
  if key==b'fmt ':
   if n<16:raise ValueError('bad fmt')
   tag,ch,rate,avg,align,bits=struct.unpack_from('<HHIIHH',raw,pos)
   fmt={'codec_tag':tag,'channels':ch,'sample_rate':rate,
        'avg_bytes_per_sec':avg,'block_align':align,'bits_per_sample':bits}
  elif key==b'data':data=n
  pos+=n+(n&1)
 if fmt is None or data is None:raise ValueError('missing original WAVE fmt/data')
 fmt['audio_payload_bytes']=data
 return fmt
def selected_2010_level1(name):
 return ('vfx_dialogue_level1_' in name or 'vfx_briefing_level1_' in name or
  name.startswith(('m_expo_','sfx_ambiance_expo','sfx_expo_')) or
  name in ('m_ch1_action.www','sfx_repulsor_shoot.www',
           'sfx_combo_1.www','sfx_missile_minigame_hover.www'))
def audit_ipa(path,out=None):
 row=[]
 with zipfile.ZipFile(path) as z:
  entries=sorted((x for x in z.infolist()
   if x.filename.startswith('Payload/IronMan2.app/') and
      x.filename.endswith('.www') and '/' not in x.filename[len('Payload/IronMan2.app/'):
      ] and not x.is_dir()),key=lambda e:e.filename)
  for f in entries:
   name=f.filename.rsplit('/',1)[-1]
   source=z.read(f);fmt=riff_fmt(source)
   v={'original_name':name,'real_WAV_sha256':hashlib.sha256(source).hexdigest(),
    'original_WAV_bytes':len(source),'original_RIFF_data':fmt,
    'selected_Level1_by_filename_NOT_original_numeric_ID':selected_2010_level1(name)}
   row.append(v)
   if out and v['selected_Level1_by_filename_NOT_original_numeric_ID']:
    (out/name.replace('.www','.wav')).write_bytes(source)
 return row
def run(v100,out,v103):
 out.mkdir(parents=True,exist_ok=True)
 selected=out/'original_2010_Level1_WAV';selected.mkdir(exist_ok=True)
 data=audit_ipa(v100,selected)
 if len(data)!=803:raise ValueError('not verified owner original iOS version1.0.0 803 WWW')
 names=[r for r in data if r['selected_Level1_by_filename_NOT_original_numeric_ID']]
 if len(names)!=73:raise ValueError('source first level filename inventory changed')
 report={'source_iOS_2010_v100_bytes':v100.stat().st_size,
 'audio_all_original_WWW_RIFF_WAVE_count':len(data),'original_Level1_selected_WAV_count':len(names),
 'codec_counts':[{'codec':codec,'channels':ch,'hz':hz,'bits':bits,'count':num}
  for (codec,ch,hz,bits),num in sorted(Counter((
   r['original_RIFF_data']['codec_tag'],
   r['original_RIFF_data']['channels'],
   r['original_RIFF_data']['sample_rate'],
   r['original_RIFF_data']['bits_per_sample']) for r in data).items())],
 'source_audio':data,'numeric_music88_and_voice320_2010_native_mapping_verified':False,
 'actual_audio_hardware_playback_verified':False,'NO_VPK':True}
 if v103:
  newer=audit_ipa(v103)
  a={x['original_name']:x['real_WAV_sha256'] for x in data}
  b={x['original_name']:x['real_WAV_sha256'] for x in newer}
  report['version_1_0_3_audio_real_hash_comparison']={
   'identical':[n for n in sorted(a.keys()&b.keys()) if a[n]==b[n]],
   'modified':[n for n in sorted(a.keys()&b.keys()) if a[n]!=b[n]],
   'added_in_1_0_3':sorted(b.keys()-a.keys()),'removed_since_1_0_0':sorted(a.keys()-b.keys())}
 else:
  report['version_1_0_3_audio_real_hash_comparison']='NOT RUN: 1.0.3 original IPA not supplied or retrieved'
 (out/'G140_original_2010_all_audio_sha_codec_Level1_manifest.json').write_text(
   json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 proof=[]
 for name in ('m_expo_intro_cutscene_1.www','m_ch1_action.www',
  'vfx_briefing_level1_jarvis.www','vfx_dialogue_level1_tony_1.www',
  'sfx_repulsor_shoot.www','sfx_ambiance_expo.www'):
  source=selected/name.replace('.www','.wav')
  if not source.exists():raise ValueError('G140 missing authentic source '+name)
  dest=out/(source.stem+'.pcm')
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',
   str(source),'-vn','-f','s16le','-acodec','pcm_s16le','-ar','48000',
   '-ac','2',str(dest)],check=True)
  if dest.stat().st_size<2048 or dest.stat().st_size%4:
   raise ValueError('G140 offline true 2010 audio decoded PCM payload invalid')
  proof.append({'source':name,'pcm':dest.name,
   'pcm_bytes':dest.stat().st_size})
 (out/'G140_real_owner_audio_to_Vita_pcm_proof.json').write_text(
   json.dumps(proof,indent=2)+'\n')
 print('PASS original 2010 user iOS v1.0.0 audio 803/803 genuine RIFF WAVE, original Level1 73 WAV unchanged, 6 PCM48 stereo, 1.0.3 comparison only if source supplied, NO VPK.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--v100',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 p.add_argument('--v103',type=Path)
 a=p.parse_args();run(a.v100,a.out,a.v103)
