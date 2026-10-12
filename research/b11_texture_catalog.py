#!/usr/bin/env python3
"""Audit validated texture table triplets in 2010 BRES BDAE sources.
This does NOT claim the per-material texture slot is solved.
"""
import collections,csv,re,struct,zipfile,pathlib,json
SOURCE="research/B11_C1L1_Source_Parser.zip"
def val(b,p):
    return struct.unpack_from("<I",b,p)[0] if p>=0 and p+4<=len(b) else -1
def norm(x):
    return x.rsplit("/",1)[-1].lower().replace(".tga",".tga")
texture_rows=[]
mesh_rows=[]
material_rows=[]
errors=[]
with zipfile.ZipFile(SOURCE) as z:
    names=[x for x in z.namelist() if x.endswith(".bdae")]
    # Reuse geometry and material decoder previously tested against the scene.
    try:
        source=z.read("bdae_scene_parser.py").decode("utf-8")
        ns={"__name__":"b11_imported","__file__":"bdae_scene_parser.py"}
        exec(compile(source,"bdae_scene_parser.py","exec"),ns)
        parser=ns["parse"]
    except Exception as exc:
        parser=None
        errors.append("Existing verified scene parser unavailable: "+repr(exc))
    for name in sorted(names):
        data=z.read(name)
        strings={m.start():m.group().decode("ascii","replace") for m in re.finditer(rb"[\x20-\x7e]{4,}",data)}
        texture_records=[]
        for off in range(0,len(data)-19,4):
            a,b,c,d,e=[val(data,off+i) for i in (0,4,8,12,16)]
            sa,sb,sc=(strings.get(a,""),strings.get(b,""),strings.get(c,""))
            if (sa.lower().endswith(".tga") and sc.lower().endswith(".tga")
               and sb.lower().endswith("_tga") and d==0 and e==0
               and sa.lower()==sc.rsplit("/",1)[-1].lower()):
                texture_records.append((off,sa,sb,sc))
                texture_rows.append([name.rsplit("/",1)[-1],hex(off),sa,sb,sc])
        materials=[]
        for off in range(0,len(data)-15,4):
            a,b=val(data,off),val(data,off+4)
            sa,sb=strings.get(a,""),strings.get(b,"")
            if sa.endswith("-fx") and sb and sa[:-3]==sb and val(data,off+8)==0:
                materials.append((off,sa,sb))
                material_rows.append([name.rsplit("/",1)[-1],hex(off),sa,sb])
        print(f"ASSET {name} texture_structs={len(texture_records)} material_structs={len(materials)}")
        if texture_records:
            print(" TEXTURES "+", ".join(x[1] for x in texture_records[:35]))
        if parser:
            try:
                meshes,stats=parser(data)
                matnames={m[2].lstrip("#").lower() for m in materials}
                subcount=matched=0
                for mesh in meshes:
                    for sub in mesh["submeshes"]:
                        subcount+=1
                        mat=str(sub.get("material",""))
                        if mat.lstrip("#").lower() in matnames:matched+=1
                        mesh_rows.append([name.rsplit("/",1)[-1],mesh["name"],mat,len(sub["faces"]), "yes" if mat.lstrip("#").lower() in matnames else "no"])
                print(f" PARSED MESHES {len(meshes)} SUBMESHES {subcount} MATCHED_MATERIAL_NAMES {matched}")
            except Exception as ex:
                errors.append(name+": "+repr(ex))
        else:
            print(" GEOMETRY PARSER NOT INSTALLED")
for fn,header,rows in [
  ("B11_texture_records.csv",["bdae_file","texture_record_offset","texture_filename","texture_alias","original_export_path"],texture_rows),
  ("B11_material_records.csv",["bdae_file","material_record_offset","material_fx_name","material_name"],material_rows),
  ("B11_submesh_material_names.csv",["bdae_file","mesh_name","submesh_material_name","triangle_count","material_name_resolves"],mesh_rows)]:
    with open(fn,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f);w.writerow(header);w.writerows(rows)
summary={"asset_count":len(names),"texture_struct_count":len(texture_rows),"unique_texture_names":len(set(r[2].lower() for r in texture_rows)),"material_struct_count":len(material_rows),"submesh_count":len(mesh_rows),"submesh_material_matches":sum(r[4]=="yes" for r in mesh_rows),"error_count":len(errors),"errors":errors[:20]}
with open("B11_material_link_summary.json","w") as f:json.dump(summary,f,indent=2)
print("SUMMARY",json.dumps(summary))
for e in errors[:10]:print("ERROR",e)
