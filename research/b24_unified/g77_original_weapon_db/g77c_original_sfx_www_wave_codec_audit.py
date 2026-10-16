#!/usr/bin/env python3
"""G77C true 2010 iOS WWW->WAVE codec inventory. Source-only.
Do NOT export copyrighted WAV byte payload, complete SFX recordings,
executable, original .ipa or any Vita VPK. Only RIFF metadata per file.
"""
from __future__ import annotations
import argparse,collections,json,zipfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g76_original_combat'))
from g76f_extract_real_riff_wave_combat_sfx_NO_VPK import riff_fmt
def main(ipa,out):
 root='Payload/IronMan2.app/'
 with zipfile.ZipFile(ipa) as z:
  files=sorted((x for x in z.infolist()
    if x.filename.startswith(root+'sfx_') and x.filename.endswith('.www')
     and '/' not in x.filename[len(root):] and not x.is_dir()),key=lambda x:x.filename)
  if len(files)!=160:raise ValueError('source original 2010 SFX count changed')
  data=[];bad=[]
  for f in files:
   raw=z.read(f)
   try:
    meta=riff_fmt(raw)
    if not meta:raise ValueError('not original RIFF WAVE')
    data.append({'source_audio_filename':f.filename[len(root):],
                 'source_audio_container_bytes':len(raw),**meta})
   except Exception as ex:bad.append({'source':f.filename[len(root):],'error':str(ex)})
  counts=collections.Counter((q['source_wave_codec_tag'],q['sample_rate'],
                              q['channels'],q['bits_per_sample']) for q in data)
  report={'source_2010_iron_man_2_full_original_owner_IPA':True,
          'original_SFX_entries':len(files),
          'parsed_RIFF_SFX_entries':len(data),
          'rejected_entries':bad,
          'codec_sample_rate_channel_bitdepth_combinations':[
            {'codec_tag':a,'hz':b,'channels':c,'bits_per_sample':d,'file_count':n}
            for (a,b,c,d),n in counts.most_common()],
          'individual_sfx_source_metadata':data,
          'all_original_sound_bytes_unchanged_not_uploaded':True,
          'actual_wave_playback_on_PS_Vita_not_tested':True,
          'source_only_no_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G77C_REAL_2010_ALL_SFX_RIFF_WAV_CODEC_METADATA.json').write_text(
     json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G77C original game 160 RIFF/WAVE SFX metadata decoded',len(data),
       'rejected',len(bad))
 print('SOURCE SFX CODECS',report['codec_sample_rate_channel_bitdepth_combinations'][:18])
 print('No audio copied; no device test, no VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.ipa,a.out)
