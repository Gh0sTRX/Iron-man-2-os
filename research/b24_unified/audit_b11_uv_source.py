#!/usr/bin/env python3
"""Research ONLY: inspect B11 original game parser and 2010 vehicle UV sources.
No changes to private original assets, no packaging. Untrusted source fields
are printed as data not instructions. Emits non-asset diagnostics.
"""
from pathlib import Path
import zipfile,inspect,types
zpath=Path("research/B11_C1L1_Source_Parser.zip")
with zipfile.ZipFile(zpath) as z:
    print("B11 members",[(x.filename,x.file_size) for x in z.infolist() if x.filename.endswith((".py",".csv",".md"))])
    parser=z.read("bdae_scene_parser.py").decode()
    builder=z.read("build_scene.py").decode()
    for label,source in [("PARSER",parser),("SCENE BUILD",builder)]:
        print("===",label,"LINES",len(source.splitlines()),"===")
        lines=source.splitlines()
        for i,l in enumerate(lines):
            if any(x in l.lower() for x in ("uv", "tex", "stride", "vertex", "material", "submesh", "car_")):
                a=max(0,i-2);b=min(len(lines),i+4)
                print("  ",i+1,repr(" ".join(q.strip() for q in lines[a:b])[:390]))
        print("===",label,"IMPORTANT ROUTINES===")
        for i,l in enumerate(lines):
            if l.startswith(("def ","class ")):
                print(i+1,l[:180])
    ns={"__name__":"b11_read_only","__file__":"bdae_scene_parser.py"}
    exec(compile(parser,"bdae_scene_parser.py","exec"),ns)
    for name in ("C1L1_car_01.bdae","C1L1_car_02.bdae","C1L1_obj_001.bdae","C1L1_ground_001.bdae"):
        b=z.read("original_models/"+name)
        meshes,stats=ns["parse"](b)
        print("=== ORIGINAL MODEL",name,"MESHES",len(meshes),"STATS",stats)
        for m in meshes[:14]:
            print("MESH",m["name"],"vertices",len(m["positions"]),
                  "VERTEX SAMPLE",repr(m["positions"][:2].tolist())[:500],
                  "STRIDE",m["stride"],"UV SAMPLE",repr(m["uv"][:2].tolist())[:240],
                  "UV RANGE",m["uv"].min(axis=0).tolist(),m["uv"].max(axis=0).tolist())
            for sub in m["submeshes"][:6]:
                print("SUB", "material",sub.get("material"),"faces",len(sub["faces"]),
                      "face sample",str(sub["faces"][:2])[:190])
