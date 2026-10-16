#!/usr/bin/env python3
"""G99 optional VPK-free ALL 248 genuine owner 2010 original Mark V rigged
IM2V clip WebGL inspection gallery. Adds source clips to already verified
G96 G91 HTML so no re-invented mesh/lighting/camera/input needed.
Does NOT hook all 248 distinct clips to user original iOS moveset states;
source-only global browser clip QA/scrubber. NO VPK.
"""
import argparse,base64,hashlib,json,re,struct
from pathlib import Path
import numpy as np
def exactly(s,a,b):
 k=s.count(a)
 if k!=1:raise ValueError('G99 source G91 exact one anchor required; found '+str(k)+' for '+a[:75])
 return s.replace(a,b,1)
def main(html_dir,animation_dir,out,qa):
 s=html_dir.read_text()
 marker=re.search(r'<script type="application/json" id="g91data">([\s\S]*?)</script>',s)
 if not marker:raise ValueError('G99 genuinely verified G96 standalone Mark V pose metadata missing')
 data=json.loads(marker.group(1))
 existing=set(data['streams'])
 files=sorted(animation_dir.glob('suitcase_ironman_*.im2v'))
 if len(files)!=248:raise ValueError('G85 source needs EXACT 248 original clips, found '+str(len(files)))
 duration={}
 bytes_source=0;total_frames=0
 for p in files:
  raw=p.read_bytes()
  magic,nv,frames,hz,ms=struct.unpack_from('<4sIIII',raw)
  if magic!=b'IM2V' or nv!=629 or hz!=20 or frames<1 or frames>10000:
   raise ValueError('authentic Mark V source 629v 20Hz invalid '+p.name)
  if len(raw)!=20+629*12*frames or frames!=((ms-1)//50+2 if ms else 1):
   raise ValueError('genuine original G85 source animation duration broken '+p.name)
  original_xyz=np.frombuffer(raw,dtype='<f4',offset=20)
  if not np.isfinite(original_xyz).all():
   raise ValueError('source animation sample NaN cannot draw '+p.name)
  stem=p.stem
  if stem in existing:
   expected=base64.b64decode(data['streams'][stem])
   if expected!=raw:raise ValueError('G96 original source clip CHANGED: '+stem)
  else:
   data['streams'][stem]=base64.b64encode(raw).decode('ascii')
  duration[stem]={'original_duration_ms':ms,'2010_weighted_vertices':629,
        'original_20Hz_frames':frames,'source_stream_sha256':hashlib.sha256(raw).hexdigest()}
  bytes_source+=len(raw);total_frames+=frames
 assert len(data['streams'])==248
 serialized=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
 s=s[:marker.start(1)]+serialized+s[marker.end(1):]
 s=exactly(s,'<button id="g91melee">Kombo (J)</button>',
  '''<button id="g91melee">Kombo (J)</button>
<label for="g99search">Tüm 248 gerçek 2010 hareketi:</label>
<input type="search" id="g99search" placeholder="animasyon adı (walk, hover, fly, combo, throw...)" style="min-width:220px;flex:1">
<select id="g99choice" aria-label="Özgün 248 Mark V klibi" style="min-width:220px;max-width:100%"></select>
<button type="button" id="g99play">Kaynak klibi oynat</button>
<button type="button" id="g99stop">Normal hareket rotasına dön</button>''')
 s=exactly(s,"const index91=new Uint16Array(decode91(a91.source_triangles_u16).buffer);",
  '''const index91=new Uint16Array(decode91(a91.source_triangles_u16).buffer);
if(Object.keys(a91.streams).length!==248)throw Error('G99 source requires all 248 genuine 2010 Mark V original baked clip streams');''')
 s=exactly(s,"function clip91(now){\n if(state91.attack){",
  """function clip91(now){
 if(state91.galleryClip && streams91[state91.galleryClip])return state91.galleryClip;
 if(state91.attack){""")
 overlay="""
/* G99 real original iOS 2010 full Mark V animation gallery.
 * This diagnostic selector does NOT assert original 2010 playable inputs,
 * unlike G83's actual source C movement/aim/flight route.
 */
const gallery99=Object.keys(a91.streams).sort();
const options99=document.getElementById('g99choice');
const search99=document.getElementById('g99search');
function refresh99(){
 const find=search99.value.trim().toLowerCase();
 const prev=options99.value;
 options99.replaceChildren();
 for(const k of gallery99){
  if(find&&!k.toLowerCase().includes(find))continue;
  const o=document.createElement('option');
  o.value=k;o.textContent=k.replace(/^suitcase_ironman_/,'')+
   ' ('+streams91[k].ms+' ms, '+streams91[k].frames+' source 20Hz frames)';
  options99.add(o);
 }
 if([...options99.options].some(o=>o.value===prev))options99.value=prev;
}
search99.oninput=refresh99;refresh99();
document.getElementById('g99play').onclick=()=>{
 if(!streams91[options99.value])return;
 state91.galleryClip=options99.value;state91.attack='';
 lastClip91='';start91=performance.now();
 state91.notice='G99 248-source-only clip gallery: NOT native attack/flight permission';
 render();
};
document.getElementById('g99stop').onclick=()=>{
 state91.galleryClip='';lastClip91='';state91.notice='G83 native C source route resumed';render();
};
"""
 s=exactly(s,"let t91=0;",overlay+"\nlet t91=0;")
 qa_data={'original_2010_MarkV_all_248_source_clips':248,
          'source_all_original_baked_20Hz_frames':total_frames,
          'source_2010_total_clip_bytes_merged':bytes_source,
          'source_G83_active_keyboard_movement_preserved':True,
          'all_248_clips_NATIVE_VITA_GAMEPLAY_STATE_MAPPED':False,
          'original_2010_damage_frame_or_attack_permissions_proven':False,
          'source_ANIM_timebase_sampled_at_20Hz':True,
          'UV_PVR_and_2010_629v_MarkV_source_mesh_kept':True,
          'original_source_named_clips':duration,
          'NO_VPK':True}
 if s.count('id="g99choice"')!=1 or s.count('function refresh99()')!=1:
  raise ValueError('G99 overlay source lost gallery or duplicated overlay')
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(s)
 qa_data['gallery_html_sha256']=hashlib.sha256(s.encode()).hexdigest()
 qa.parent.mkdir(parents=True,exist_ok=True)
 qa.write_text(json.dumps(qa_data,ensure_ascii=False,indent=2)+'\n')
 print('PASS G99 actual 2010 ORIGINAL 248/248 Mark V B13 629v source sampled 20Hz',total_frames,
   'frames',bytes_source,'bytes. Full source WebGL gallery, NEVER 248 playable attack mappings. NO VPK.')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for arg in ('html','animations','out','qa'):p.add_argument('--'+arg,type=Path,required=True)
 a=p.parse_args();main(a.html,a.animations,a.out,a.qa)
