#!/usr/bin/env python3
"""Read-only comparison of a user-provided G68 installed Vita VPK.
Does not dump or export original owner atlas contents.
Prints transparency/batch evidence only.
"""
from pathlib import Path
import argparse,json,struct,zipfile
def analyze(path:Path):
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  files=set(z.namelist())
  raw=z.read('assets/G66_city.g66m')
  assert raw[:4]==b'G66M'
  version,nverts,nb,nt=struct.unpack_from('<4I',raw,4)
  assert version==1 and nb==nt+1 and nverts==67323 and nt==31
  batches=[struct.unpack_from('<4I',raw,20+16*i) for i in range(nb)]
  opaque,translucent=[],[]
  tex_bytes=0
  for i in range(nt):
   name='assets/G66_city_tex_%02d.g66t'%i
   tex=z.read(name);assert tex[:4]==b'G66T'
   v,w,h=struct.unpack_from('<3I',tex,4)
   assert v==1 and len(tex)==16+w*h*4
   tex_bytes+=w*h*4
   nonopaque=sum(tex[16+3::4][i]!=255 for i in range(w*h))
   (translucent if nonopaque else opaque).append({
    'texture_index':i,'pixel_count':w*h,'alpha_below_255':nonopaque})
  affected=[{'batch_index':i,'texture_index':b[2],'triangle_count':b[1]//3}
     for i,b in enumerate(batches)
     if b[2]!=0xffffffff and any(t['texture_index']==b[2] for t in translucent)]
  return {
   'source':'installed G68 VPK only','real_source_first_level_triangles':nverts//3,
   'texture_count':nt, 'transparent_texture_count':len(translucent),
   'transparent_texture_indices':[x['texture_index'] for x in translucent],
   'affected_source_batch_count':len(affected),
   'affected_source_triangles':sum(x['triangle_count'] for x in affected),
   'texture_rgba_mip0_bytes':tex_bytes,
   'color_space_original_shader_proven':False,
   'alpha_blend_sort_depth_write_correct_proven':False,
   'actual_skybox_skyshader_loaded_in_G68':False,
   'source_original_assets_exported':False,
  }
if __name__=='__main__':
 parser=argparse.ArgumentParser()
 parser.add_argument('--vpk',type=Path,required=True)
 p=parser.parse_args()
 print(json.dumps(analyze(p.vpk),indent=2))
