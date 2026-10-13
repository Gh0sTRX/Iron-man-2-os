#!/usr/bin/env python3
"""Report EXACT reconstructed B24 graphics owners and candidate handoff sites.
Read-only. No Vita runtime/VPK output.
"""
from pathlib import Path
import json,re
root=Path("work")
paths=["src/main.c","src/renderer.c","CMakeLists.txt"]
needles=[
 "SDL_CreateRenderer","SDL_CreateTexture","SDL_RenderCopy","SDL_RenderPresent",
 "SDL_UpdateTexture","SDL_Init","SDL_CreateWindow","SDL_GL_CreateContext",
 "vglInit","vglSwapBuffers","SDL_DestroyRenderer",
 "im2_render(","b24_unified_draw_overlay","SDL_GameController",
 "SDL_RenderClear","glDrawElements","glClear","b24_c1_scene",
 "renderer =","SDL_Renderer"
]
result={}
for path in paths:
 s=(root/path).read_text()
 lines=s.splitlines()
 hits=[]
 for i,line in enumerate(lines):
  if any(k in line for k in needles):
   hits.append({"line":i+1,"text":line.strip()[:220],
       "before":lines[i-1].strip()[:150] if i else "",
       "after":lines[i+1].strip()[:150] if i+1<len(lines) else ""})
 result[path]={"matches":hits,"length":len(lines)}
out=Path("/tmp/B24_GRAPHICS_OWNER_AUDIT.json")
out.write_text(json.dumps(result,indent=2))
for file,report in result.items():
 print("\nB24 SOURCE",file,"LINES",report["length"])
 for row in report["matches"]:
  print(row["line"],row["text"])
assert any("SDL_UpdateTexture" in x["text"] for x in result["src/main.c"]["matches"]), "unexpected: CPU upload path moved"
print("\nPASS read-only B24 active graphics owner audit, generated /tmp/B24_GRAPHICS_OWNER_AUDIT.json, NO VPK")
