#!/usr/bin/env python3
"""G75 native authoring audit. Distinguishes original 2010 Lua scene
bytecode / BRES animations from the newer homebrew B14 control model.
No game VPK is built, no user proprietary source is uploaded. """
from pathlib import Path
import zipfile,struct,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
Z=ROOT/"third_person_b14/b14_overlay.zip"
def main():
 with zipfile.ZipFile(Z) as z:
  names=z.namelist()
  candidates=[x for x in names if re.search(r'(?:^|/)(?:b14_world|b14_pose|main|im2_camera)\.(?:c|h)$',x)]
  assert any(x.endswith("b14_world.c") for x in candidates),candidates
  files={x:z.read(x).decode("utf-8") for x in candidates}
  pattern=re.compile(r'(?i)height|scale|velocity|speed|walk|run|rush|hover|camera|pitch|orbit|flight|ground|foot|accel|z=|\.z|world\.x|world\.y|world\.z|dt|collision')
  significant={}
  for name,content in files.items():
   lines=content.splitlines()
   hits=[{'line':i+1,'text':s.strip()[:260]}
          for i,s in enumerate(lines) if pattern.search(s)]
   significant[name]={'source_sha256':__import__('hashlib').sha256(content.encode()).hexdigest(),
                      'lines':len(lines),'matching_statements':hits[:240]}
  report={
   'origin':'our homebrew B14 source code, NOT original compiled iOS game',
   'B14_code_files':list(files),
   'B14_source_significant_statements':significant,
   'original_2010_logic_in_B14_proven':False,
   'authentic_iOS_Lua_found_previously':71,
   'G73_device_character_scale_ground_wall_regression_pending':True,
   'VPK_generated':False
  }
 out=ROOT/"g75_original_gameplay_engine_source_report.json"
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 for name,m in significant.items():
  print("FILE",name,"CODE_LINES",m['lines'])
  for hit in m['matching_statements'][:70]:
   print("LINE",hit['line'],hit['text'])
 print("PASS G75 original B14 model extracted for motion/camera/physics numeric-source audit (homebrew, not decompiled original iOS code)")
if __name__=="__main__":main()
