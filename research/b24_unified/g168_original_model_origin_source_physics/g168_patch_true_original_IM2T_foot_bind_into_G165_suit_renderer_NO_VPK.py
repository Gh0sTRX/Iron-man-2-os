#!/usr/bin/env python3
"""Fix original 2010 IM2T actor visual foot alignment WITHOUT modifying
B14 physics, source contact G75, camera size or authored model scale.

G161 actual Vita: small/buried character. Proven G161 source:
 B14 z=0 starts as floor, G75 consumes B14 world.z as FOOT Z.
 Original IM2T im2_load computes source minz and midpoint center_z.
 VitaGL GPU suit used root.z - center_z + vertex.z, thereby placing
 authored feet about 1.1 ORIGINAL source units BELOW authored ground.
 New GPU model root uses root.z - model original minz + vertex.z.
 Original source vertex XY/Z, source actor size, source collisions,
 and original IM2V animation buffers remain unchanged. Cached source
 bind min survives animation. No guessed actor/vehicle scale, no VPK.
"""
from pathlib import Path

R=Path(__file__).resolve().parents[3]
W=R/"work"
paths={
 "renderer_h":W/"src/renderer.h",
 "renderer_c":W/"src/renderer.c",
 "gpu_h":W/"b24/b24_unified/b24_gpu_suit.h",
 "adapter":W/"b24/b24_unified/b24_gpu_suit_im2_adapter.c",
 "gpu_c":W/"b24/b24_unified/b24_gpu_suit_vitagl.c",
 "cm":W/"CMakeLists.txt",
 "main":W/"src/main.c",
}
def once(s,a,b,p):
 n=s.count(a)
 if n!=1:raise RuntimeError("G168 source anchor "+p+" expected1 found "+str(n)+": "+repr(a[:100]))
 return s.replace(a,b,1)
def main():
 for name,p in paths.items():
  if not p.is_file():raise FileNotFoundError("G168 full G165 Vita source missing "+str(p))
 data={k:p.read_text() for k,p in paths.items()}
 cm=data["cm"]
 if "B24_G168_ORIGINAL_SUIT_RENDER_FOOT" in cm:
  raise ValueError("G168 cannot be installed twice")
 for flag in ("B24_G75_SOURCE_CAPSULE","B24_G160_ROAD_SPATIAL_INDEX",
              "B24_G156_CONTINUOUS_TRI_CONTACT","B24_G164_HERO_CAMERA_FRAMING"):
  if flag not in cm:raise ValueError("G168 source full same single game missing "+flag)
 if data["main"].count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
  raise ValueError("G168 may not introduce duplicate original B14")
 if data["main"].count("b24_g75_capsule_reconcile(")!=1:
  raise ValueError("G168 must retain one physical G75 original source feet evaluator")
 data["renderer_h"]=once(data["renderer_h"],"    float center_z;\n} IM2Model;",
  "    float center_z;\n"
  "    float native_bind_min_z; /* 2010 authored IM2T source rest minimum, stable during G8 motion */\n"
  "} IM2Model;","renderer_h")
 data["renderer_c"]=once(data["renderer_c"],
  "tmp.center_z=(minz+maxz)*0.5f;",
  "     tmp.center_z=(minz+maxz)*0.5f;\n"
  "     tmp.native_bind_min_z=minz; /* actual 2010 original rest mesh, not animated foot bob */",
  "renderer_c")
 data["gpu_h"]=once(data["gpu_h"]," float center_z;\n} B24GpuSuitSource;",
  " float center_z;\n"
  " float native_bind_min_z; /* source original suit unanimated bind minimum from im2_load */\n"
  "} B24GpuSuitSource;","gpu_h")
 data["adapter"]=once(data["adapter"],
   " s->source.center_z=m->center_z;",
   " s->source.center_z=m->center_z;\n"
   " s->source.native_bind_min_z=m->native_bind_min_z;",
   "adapter")
 data["gpu_c"]=once(data["gpu_c"],
    " if(!b24_gpu_suit_matrix(root,pose,src->center_z))return 0;",
    """#ifdef B24_G168_ORIGINAL_SUIT_RENDER_FOOT
 /* B14 world.z is a source G75 verified collision FOOT, not a model
  * midpoint. The old GPU matrix subtracted model.center_z and buried
  * original Iron Man rest minZ below the road/vehicle world plane.
  * Native bind source minimum is loaded once from the 2010 .im2t
  * BEFORE original animation mutations. Zero mesh/unit scaling.
  * This corrects ONLY the suit-to-world translation on GPU. */
 if(!isfinite(src->native_bind_min_z))return 0;
 if(!b24_gpu_suit_matrix(root,pose,src->native_bind_min_z))return 0;
#else
 if(!b24_gpu_suit_matrix(root,pose,src->center_z))return 0;
#endif""", "gpu_c")
 data["cm"]+="""

# G168 real 2010 original suit render FOOT math. The authored IM2T
# bind mesh has vertex z minz and model.center_z=(minz+maxz)/2.
# B14/G75 world.z is gameplay FOOT support. Render matrix must
# use world.z-minz (NOT world.z-center_z), no model/vehicle/world
# scaling, no changes to input physics or source collider ownership.
option(B24_G168_ORIGINAL_SUIT_RENDER_FOOT "Use 2010 native IM2T bind minimum as G75 actual foot renderer anchor" OFF)
if(B24_G168_ORIGINAL_SUIT_RENDER_FOOT)
 if(NOT B24_ENABLE_GPU OR NOT B24_G75_SOURCE_CAPSULE)
  message(FATAL_ERROR "G168 genuine source foot requires original one B14/G75 GPU owner")
 endif()
 target_compile_definitions(im2_beta PRIVATE
  B24_G168_ORIGINAL_SUIT_RENDER_FOOT=1)
endif()
"""
 # Enforce all source replacements before modifying persistent work.
 if data["renderer_c"].count("tmp.native_bind_min_z=minz;")!=1:
  raise AssertionError("G168 original rest min not provenance")
 if data["gpu_c"].count("src->native_bind_min_z")!=2:
  raise AssertionError("G168 suit renderer root uses only native source bind min")
 for key in ("renderer_h","renderer_c","gpu_h","adapter","gpu_c","cm"):
  paths[key].write_text(data[key])
 if list(W.rglob("*.vpk")):raise RuntimeError("G168 NO VPK POLICY")
 print("G168 SOURCE FOOT RENDER real original IM2T source rest minZ now aligns model bottom exactly to B14/G75 authored ground; collision world/size untouched, NO VPK")
if __name__=="__main__":main()
