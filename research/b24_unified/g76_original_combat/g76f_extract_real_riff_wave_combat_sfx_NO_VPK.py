#!/usr/bin/env python3
"""G76F unwrap owner's genuine 2010 Iron Man 2 combat SFX .www to .wav.
The original .www is in fact a RIFF WAVE audio file in confirmed samples.
No transcoding or sound fabrication. Native sound bytes kept only inside
short-lived private GitHub artifact, never committed into source, NO VPK.
"""
from __future__ import annotations
import argparse,hashlib,io,json,re,struct,wave,zipfile
from pathlib import Path
COMBAT=re.compile(r'(?i)combo|armor_hit|attack|beam|blast|cannon|missile|repuls|unibeam|explos|bullet|fire|hurt|enemy|punch|kick|impact|gun|rocket|laser|shot|weapon|whip')
def riff_fmt(raw):
 if len(raw)<44 or raw[:4]!=b'RIFF' or raw[8:12]!=b'WAVE':
  return None
 if int.from_bytes(raw[4:8],'little')+8>len(raw):
  raise ValueError('source RIFF container truncated')
 at=12;fmt=None;data=None
 while at+8<=len(raw):
  name=raw[at:at+4];size=struct.unpack_from('<I',raw,at+4)[0];at+=8
  if at+size>len(raw):raise ValueError('source RIFF chunk truncated')
  if name==b'fmt ' and size>=16:
   ft,ch,hz,avg,align,bps=struct.unpack_from('<HHIIHH',raw,at)
   fmt={'source_wave_codec_tag':ft,'channels':ch,'sample_rate':hz,
        'avg_bytes_per_sec':avg,'block_align':align,
        'bits_per_sample':bps}
  if name==b'data':
   data=size
  at+=size+(size&1)
 if fmt is None or data is None:raise ValueError('not complete source RIFF WAVE')
 fmt['wave_audio_payload_bytes']=data
 fmt['duration_seconds_estimate']=round(data/fmt['avg_bytes_per_sec'],4) if fmt['avg_bytes_per_sec'] else None
 return fmt
def run(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  allsound=sorted(e for e in z.infolist()
    if e.filename.startswith('Payload/IronMan2.app/sfx_')
    and e.filename.endswith('.www') and not e.is_dir())
  subset=[f for f in allsound if COMBAT.search(f.filename)]
  soundout=out/'authentic_2010_combat_wav'
  soundout.mkdir(parents=True,exist_ok=True)
  result=[];failed=[]
  for f in subset:
   raw=z.read(f)
   try:
    fmt=riff_fmt(raw)
    if fmt is None:raise ValueError('No real original RIFF')
    if fmt['source_wave_codec_tag']==1:
     with wave.open(io.BytesIO(raw),'rb') as w:
      assert w.getnchannels()==fmt['channels']
      assert w.getframerate()==fmt['sample_rate']
      assert w.getsampwidth()*8==fmt['bits_per_sample']
    # No generated/reencoded sound; extension repair only.
    name=f.filename.split('/')[-1].removesuffix('.www')+'.wav'
    (soundout/name).write_bytes(raw)
    result.append({'real_native_2010_sfx':f.filename.split('/')[-1],
         'unwrapped_as_wav':name,
         'original_sound_bytes_SHA256':hashlib.sha256(raw).hexdigest(),
         'source_original_bytes':len(raw),**fmt})
   except Exception as e:
    failed.append({'source':f.filename,'reason':str(e)})
  meta={'genuine_original_game':'Iron Man 2 2010 Gameloft iOS owner IPA',
        'source_sfx_www_count':len(allsound),
        'combat_named_sfx_source_count':len(subset),
        '2010_source_RIFF_WAVE_verified_and_exported':len(result),
        'source_decode_rejected':failed,
        'native_game_SFX_mission_binding_proven':False,
        'raw_sound_audio_samples_verbatim_untouched':True,
        'not_VPK':True,'original_WAV_files':result}
  (out/'G76F_2010_ORIGINAL_WEAPON_HIT_COMBO_SFX_WAV_MANIFEST.json').write_text(
    json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
  print('G76F owner original source',len(allsound),'SFX; combat',len(subset),
        'TRUE WAV converted extension',len(result),'rejected',len(failed))
  print('codecs',sorted({(r['source_wave_codec_tag'],r['channels'],r['sample_rate'],r['bits_per_sample'])
                         for r in result}))
  print('Real unique sounds copied, NO VPK or guessed re-encoding')
  assert len(result)>=20
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();run(a.ipa,a.out)
