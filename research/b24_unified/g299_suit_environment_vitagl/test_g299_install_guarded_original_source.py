#!/usr/bin/env python3
"""Host-only C source integration guards; G168 fixture is NOT Vita gameplay."""
import importlib.util
import tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
script=HERE/"g299_install_suit_light_after_G168_G279_NO_VPK.py"
spec=importlib.util.spec_from_file_location("g299_patch",script)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
reference=(HERE.parent/"b24_gpu_suit_vitagl.c").read_text()

def make(root:Path):
 dest=root/"work/b24/b24_unified/b24_gpu_suit_vitagl.c"
 dest.parent.mkdir(parents=True,exist_ok=True)
 inc=reference.index("#ifdef B24_G299_SUIT_ENVIRONMENT_CANDIDATE")
 tail=reference.index("_Static_assert(",inc)
 prior=reference[:inc]+reference[tail:]
 start=prior.index(' glBindTexture(GL_TEXTURE_2D,s->texture_id);')
 end=prior.index(' glEnableClientState(GL_VERTEX_ARRAY);',start)
 prior=prior[:start]+''' glBindTexture(GL_TEXTURE_2D,s->texture_id);
 glColor4f(1.f,1.f,1.f,1.f);
'''+prior[end:]
 a=prior.index(' glDisable(GL_TEXTURE_2D);\n#ifdef B24_G299_SUIT_ENVIRONMENT_CANDIDATE')
 b=prior.index(' glPopMatrix();',a)
 prior=prior[:a]+' glDisable(GL_TEXTURE_2D);\n'+prior[b:]
 prior=prior.replace(' if(!b24_gpu_suit_matrix(root,pose,src->center_z))return 0;',
  '''#ifdef B24_G168_ORIGINAL_SUIT_RENDER_FOOT
 if(!isfinite(src->native_bind_min_z))return 0;
 if(!b24_gpu_suit_matrix(root,pose,src->native_bind_min_z))return 0;
#else
 if(!b24_gpu_suit_matrix(root,pose,src->center_z))return 0;
#endif''')
 assert prior.count("src->native_bind_min_z")==2
 dest.write_text(prior)
 (root/"work/src").mkdir(parents=True)
 (root/"work/src/main.c").write_text(
  'b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)\n'
  'b24_g8_motion_tick_g84(\n')
 (root/"work/CMakeLists.txt").write_text(
  'B24_G168_ORIGINAL_SUIT_RENDER_FOOT\n'
  'B24_G75_ORIGINAL_SUN_LIGHTING_CANDIDATE\n'
  'B24_ENABLE_GPU\n')
 return dest

with tempfile.TemporaryDirectory(prefix="g299_synthetic_G168_source_") as d:
 root=Path(d);dest=make(root)
 original=dest.read_text()
 mod.install(root)
 patched=dest.read_text()
 assert original.count("b24_gpu_suit_draw(")==patched.count("b24_gpu_suit_draw(")==1
 assert patched.count("glDrawElements(")==1
 assert patched.count("src->native_bind_min_z")==2
 assert patched.count("glTexEnvi(")==2
 assert patched.count("g299_prior_texture_env")==3
 assert "B24_G299_SUIT_ENVIRONMENT_CANDIDATE" in (root/"work/CMakeLists.txt").read_text()
 try:mod.install(root);raise AssertionError("duplicate G299 must fail")
 except ValueError as e:assert "duplicate" in str(e)
with tempfile.TemporaryDirectory(prefix="g299_missing_original_root_") as d:
 root=Path(d);dest=make(root)
 dest.write_text(dest.read_text().replace("src->native_bind_min_z","NOT_SOURCE_FOOT"))
 try:mod.install(root);raise AssertionError("G168 foot transform missing must fail")
 except ValueError as e:assert "G168" in str(e)
 (root/"work/unfinished.vpk").write_bytes(b"DO NOT BUILD")
 try:mod.install(root);raise AssertionError("VPK presence must fail")
 except ValueError as e:assert "VPK" in str(e)
print("G299 PASS G168 original armor foot transform preserved, one GPU draw, glTexture env restored, double/missing-source/VPK fail closed. Synthetic fixture only.")
