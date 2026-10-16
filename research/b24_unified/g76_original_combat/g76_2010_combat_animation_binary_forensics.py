#!/usr/bin/env python3
"""G76: audit the actual 2010 owner IPA combat and damage ANIM channels.
All numbers are from original little-endian .anim bytes, not B14 gameplay.
No full original game, ANIM binaries, IPAs or VPK are emitted.
"""
from __future__ import annotations
import argparse,csv,io,json,hashlib,collections,re,struct,zipfile,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
COMBAT=re.compile(r'combo|att|attack|hit|hurt|death|dead|block|counter|shoot|fire|beam|laser|missil|cannon|explode|dodge|push|throw|kick|weapon|qte|paralys|damage|die',re.I)
DAMAGE=re.compile(r'hit|hurt|injur|dead|death|die|knock|fall|stagger|break|paralys',re.I)
def parse_anim(b:bytes):
 at=0
 def take(n):
  nonlocal at
  if n<0 or at+n>len(b):raise ValueError('original ANIM truncated')
  v=b[at:at+n];at+=n;return v
 def u8():return take(1)[0]
 def u16():return struct.unpack('<H',take(2))[0]
 def i32():return struct.unpack('<i',take(4))[0]
 def floats(n):return struct.unpack('<'+str(n)+'f',take(4*n))
 n=u16()
 if n>500:raise ValueError('implausible original animation channel names')
 names=[]
 for i in range(n):
  name=take(u16()).decode('latin1','replace')
  names.append(name)
 animated_xyz=0;animated_rot=0
 timepoints=[];position_magnitude={}
 moves=[]
 for i in range(n):
  mode=u8()
  if mode==1:
   p=floats(3)
   if not all(math.isfinite(v) for v in p):raise ValueError('bad const position')
  elif mode==0:
   count=u16()
   if count>25000:raise ValueError('key count too large')
   xyz=[]
   for _ in range(count):
    t=i32();p=floats(3)
    if not all(math.isfinite(v) for v in p):raise ValueError('bad position')
    xyz.append((t,p));timepoints.append(t)
   if xyz:
    animated_xyz+=1
    mm=max(math.dist(xyz[0][1],p) for t,p in xyz)
    moves.append({'track':names[i],'first_ms':xyz[0][0],
                  'last_ms':xyz[-1][0],
                  'key_count':len(xyz),
                  'net_translation_3d':round(math.dist(xyz[0][1],xyz[-1][1]),6),
                  'max_displacement_from_initial_3d':round(mm,6)})
  else:raise ValueError('unknown genuine XYZ mode')
 for i in range(n):
  mode=u8()
  if mode==1: take(8)
  elif mode==0:
   count=u16()
   if count>25000:raise ValueError('quaternion keys too large')
   if count: animated_rot+=1
   for _ in range(count):
    t=i32();take(8);timepoints.append(t)
  else:raise ValueError('unknown genuine QUAT mode')
 if at!=len(b):raise ValueError(f'original ANIM trailing bytes {len(b)-at}')
 sorted_tracks=sorted(moves,key=lambda e:e['max_displacement_from_initial_3d'],reverse=True)
 return {'channels':n,'animated_translation_channels':animated_xyz,
         'animated_rotation_channels':animated_rot,
         'time_first_ms':min(timepoints) if timepoints else 0,
         'time_last_ms':max(timepoints) if timepoints else 0,
         'animated_translation_stats_highest_6':sorted_tracks[:6],
         'source_track_names_with_attack_or_damage_tokens':
          [name for name in names if COMBAT.search(name)][:30],
         'original_attack_collision_contact_frame_proven':False,
         'original_damage_value_encoded_in_ANIM_proven':False}
def main(ipa:Path,out:Path):
 with zipfile.ZipFile(ipa) as z:
  assert z.testzip() is None
  infos=[x for x in z.infolist() if not x.is_dir()]
  original_archives=[{'path':x.filename,'uncompressed_bytes':x.file_size}
                     for x in infos if x.filename.startswith('Payload/IronMan2.app/')
                       and x.filename.count('/')==2]
  raw=z.read('Payload/IronMan2.app/anims')
  entries=decode(raw,'.anim')
  assert len(entries)==972
  records=[]
  for e in entries:
   if not COMBAT.search(e.name):continue
   src=get_exact(raw,entries,e.name)
   anim=parse_anim(src)
   anim.update({'name':e.name,'source_bytes':len(src),
                'source_sha256':hashlib.sha256(src).hexdigest(),
                'damage_reaction_named':bool(DAMAGE.search(e.name))})
   records.append(anim)
  names=collections.Counter()
  for x in records:
   prefix=x['name'].split('_',1)[0]
   names[prefix]+=1
  out.mkdir(parents=True,exist_ok=True)
  result={'data_origin':'true 2010 Gameloft Iron Man 2 owner IPA animation bank, 972 real files',
          'source_IPA_entry_listing':original_archives,
          'combat_related_original_named_clips':len(records),
          'combat_related_clip_categories':dict(names),
          'damage_or_death_named_clips':sum(x['damage_reaction_named'] for x in records),
          'original_anim_channel_and_time_details':records,
          'all_source_asset_names_verified':True,
          'source_animation_pose_channel_decode_not_exact_attack_hitbox_timing':True,
          'source_weapon_damage_hp_or_recharge_constants_extracted':False,
          'not_generated_vpk':True}
  (out/'G76_TRUE_2010_COMBAT_HURT_ANIM_SOURCE_CHANNEL_REPORT.json').write_text(
    json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  with (out/'G76_ORIGINAL_ATTACK_DAMAGE_CLIP_TIMELINES.csv').open('w',newline='') as f:
   w=csv.writer(f);w.writerow(['genuine_clip','track_count','moving_xyz_channels',
      'rotating_channels','source_first_ms','source_last_ms','damage_reaction','source_bytes'])
   for x in records:
    w.writerow([x['name'],x['channels'],x['animated_translation_channels'],
                x['animated_rotation_channels'],x['time_first_ms'],x['time_last_ms'],
                x['damage_reaction_named'],x['source_bytes']])
  assert records and sum(x['animated_rotation_channels']>0 for x in records)>70
  print('PASS G76 original source 972 indexed anims, parsed combat/damage clips',len(records),
        'hurt/death',result['damage_or_death_named_clips'])
  for x in records:
   if re.search(r'IronMan_Ground_Combo_|IronMan_Ground_Hurt|IronMan_Air_CounterAtt|Drone_Army.*(Attack|Hurt|Fire)',x['name'],re.I):
    print('TRUE_2010_ANIM',x['name'],'duration ms',x['time_last_ms'],
          'moving xyz',x['animated_translation_channels'],'rotating',x['animated_rotation_channels'])
  print('Original ANIM bytes parse, NOT decoded damage/hit permission logic; no VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();main(a.ipa,a.out)
