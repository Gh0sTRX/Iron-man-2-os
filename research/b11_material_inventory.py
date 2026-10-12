#!/usr/bin/env python3
import zipfile,re,os,sys,json,collections,hashlib,struct
archives=[
"research/B11_C1L1_Source_Parser.zip",
"research/B11_C1L1_Scene_GLBS.zip",
"research/Original_Level_BCLARA_Audit.zip"
]
output={}
for arc in archives:
 print("\n===== ARCHIVE",arc,"=====")
 info={}
 with zipfile.ZipFile(arc) as z:
  names=z.namelist()
  for name in names[:90]:
   if not name.endswith("/"):
    print("FILE",name,"BYTES",z.getinfo(name).file_size)
  info["entries"]=len(names)
  info["assets"]=[]
  for name in names:
   if not name.lower().endswith(".bdae"): continue
   b=z.read(name)
   strings=[m.group().decode('latin1') for m in re.finditer(rb'[\x20-\x7e]{4,}',b)]
   hits=[s for s in strings if ('.tga' in s.lower() or '.pvr' in s.lower() or '.png' in s.lower() or '.mat' in s.lower() or 'diffuse' in s.lower() or 'texture' in s.lower() or 'shader' in s.lower())]
   common=[s for s in strings if re.search(r'(?:^|[_/])(?:C1L1|MC_|LC_|texture|material|diffuse|lightmap|tex)',s,re.I)]
   row=dict(file=name,size=len(b),header=b[:64].hex(),strings=len(strings),material_hits=hits[:35],relevant_strings=common[:35])
   info["assets"].append(row)
   print("\nMODEL",name,"size",len(b),"first_64_bytes",b[:64].hex())
   print("texture/materials",repr(hits[:35]))
   print("other names",repr(common[:24]))
  for name in names:
   if name.lower().endswith((".py",".md",".csv")):
    s=z.read(name)
    print("SCRIPT/TEXT",name,"BYTES",len(s))
    if name.lower().endswith(".py"):
     lines=s.decode("utf-8","replace").splitlines()
     markers=[(i+1,l[:160]) for i,l in enumerate(lines) if re.search(r"material|texture|submesh|pointer|palette|tga|UV",l,re.I)]
     print("code markers",repr(markers[:35]))
 output[arc]=info
with open("B11_asset_inventory.json","w") as o:json.dump(output,o,ensure_ascii=False,indent=2)
print("\nREPORT B11_asset_inventory.json WRITTEN")