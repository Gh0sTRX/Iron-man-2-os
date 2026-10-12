import zipfile, re, struct, collections
ARCH="research/B11_C1L1_Source_Parser.zip"
for name in ["C1L1_sky_001.bdae","C1L1_car_01.bdae","C1L1_ground_001.bdae"]:
 with zipfile.ZipFile(ARCH) as z: b=z.read("original_models/"+name)
 print("\n\n===== POINTER AUDIT",name,"bytes",len(b),"=====")
 def u(p): return struct.unpack_from("<I",b,p)[0] if 0<=p<=len(b)-4 else None
 print("FIRST_HEADER_DWORDS",[(hex(i),hex(u(i))) for i in range(0,0x80,4)])
 ss=[]
 for m in re.finditer(rb"[\x20-\x7e]{5,}",b):
  try:s=m.group().decode("ascii")
  except:s="?"
  if any(x in s.lower() for x in [".tga","material_","-fx","_tga","/textures/"]):
   ss.append((m.start(),s))
 interesting=ss[:]
 if len(interesting)>35:interesting=interesting[:25]+interesting[-10:]
 for pos,s in interesting:
  if len(s)>80:continue
  refs=[p for p in range(0,len(b)-3,4) if u(p)==pos]
  print("STRING",hex(pos),repr(s),"PTR_FIELDS",[hex(x) for x in refs[:12]])
  if (".tga" in s.lower() or "material" in s.lower()) and refs:
   for p in refs[:3]:
    lo=max(0,p-16);hi=min(len(b)-3,p+44)
    words=[(hex(q),hex(u(q))) for q in range(lo//4*4,hi,4)]
    print("REFERENCE_NEIGHBORS",hex(p),words)
