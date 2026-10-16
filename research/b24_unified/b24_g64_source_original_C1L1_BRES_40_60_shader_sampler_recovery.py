#!/usr/bin/env python3
"""G64: authentic 2010 BRES variable-size native 40/60B shader texture links.

G11 only accepted 60B property records. Several apparent missing diffuse
surfaces use 40B properties, including 1,683 C1L1_3building triangles.
Never infer sphere UV/shader from an atlas link alone. Source-only; no VPK.
"""
import argparse,collections,hashlib,json,struct,zipfile
from pathlib import Path

STEMS=("C1L1_ground_001","C1L1_obj_001","C1L1_obj_002","C1L1_obj_003",
       "C1L1_obj_004","C1L1_car_01","C1L1_car_02","C1L1_light_001",
       "C1L1_light_002","C1L1_light_003")
TARGETS={"c1l1_3building","Material__12","Material__17","Material__19",
         "Material__20","Material__21","Material__46","Standard_16dd"}

def u(blob,p):
    return struct.unpack_from("<I",blob,p)[0] if p is not None and 0<=p<=len(blob)-4 else None

def string(blob,p):
    if p is None or not 0<=p<len(blob):return None
    end=blob.find(b"\0",p,min(p+108,len(blob)))
    if end<0 or end-p<3:return None
    x=blob[p:end]
    return x.decode("latin1") if all(32<=c<127 for c in x) else None

def decode(stem,blob):
    count=u(blob,16); table=u(blob,20); end=u(blob,24)
    assert 0<count<100000 and table>=32 and table+4*count==end<len(blob)
    reloc={u(blob,table+4*i) for i in range(count)}
    mat_records={}
    atlas_records={}
    for p in range(32,len(blob)-64,4):
        if p in reloc and p+4 in reloc and p+12 in reloc:
            a=string(blob,u(blob,p));b=string(blob,u(blob,p+4))
            c=string(blob,u(blob,p+12))
            if a and a==b and c and c.startswith("#") and a in c and u(blob,p+8)==0:
                mat_records[p]=a
        if p in reloc and p+4 in reloc and p+8 in reloc:
            fields=[string(blob,u(blob,p+k)) for k in (0,4,8)]
            if all(fields) and fields[0].lower().endswith(".tga") and all("tga" in s.lower() for s in fields[1:]):
                atlas_records[p]=fields[0]
    def largest_run(records,stride):
        roots=[k for k in records if k-stride not in records]
        runs=[]
        for start in roots:
            n=1
            while start+n*stride in records:n+=1
            runs.append((n,start))
        assert runs
        return max(runs)
    nmats,matbase=largest_run(mat_records,64)
    ntex,texbase=largest_run(atlas_records,20)
    mats=[mat_records[matbase+64*i] for i in range(nmats)]
    textures=[atlas_records[texbase+20*i] for i in range(ntex)]
    shaderbase=None
    b0=texbase+20*ntex
    for p in range(max(32,b0-200),min(len(blob)-88,b0+600),4):
        if string(blob,u(blob,p))!=mats[0]+"-fx":continue
        if all(string(blob,u(blob,p+88*i+4))==mat for i,mat in enumerate(mats)):
            shaderbase=p;break
    assert shaderbase is not None
    props=[u(blob,shaderbase+88*i+12) for i in range(nmats)]
    assert props==sorted(set(props)) and props[0]==shaderbase+88*nmats
    results=[]
    for i,mat in enumerate(mats):
        p=props[i];limit=props[i+1] if i+1<nmats else matbase
        n=limit-p
        assert n in (20,40,60), (stem,mat,n)
        words=struct.unpack_from("<"+"I"*(n//4),blob,p)
        # 40B variant ends at word 9; 60B variant at word 14. Source
        # indices are local to this exact BRES 20B authored TGA table.
        # A 20B shader constant record is NOT treated as a sampler.
        idx=words[-1]
        valid=n in (40,60) and idx<len(textures) and words[0] in (1,0xFF959595,0xFF000000)
        results.append({"source":stem,"material":mat,"native_property_offset":p,
                        "native_property_size":n,"texture_table_index":idx if valid else None,
                        "original_TGA":textures[idx] if valid else None})
    return results

def main(zippath,out):
    allrows=[]
    fingerprints={}
    with zipfile.ZipFile(zippath) as z:
        for stem in STEMS:
            raw=z.read("original_models/"+stem+".bdae")
            fingerprints[stem]=hashlib.sha256(raw).hexdigest()
            allrows+=decode(stem,raw)
    mapping={s:{r["material"]:r["original_TGA"] for r in allrows if r["source"]==s} for s in STEMS}
    expected={"Material__20":"C1L1_earth02.tga","Material__21":"C1L1_earth.tga",
              "Material__12":"C1L1_earth03.tga","Material__17":"c1l1_building2.tga",
              "Material__19":"C1L1_ground_light.TGA","c1l1_3building":"c1l1_building.tga"}
    for s in ("C1L1_light_001","C1L1_light_002","C1L1_light_003"):
        for material,texture in expected.items():
            assert mapping[s][material].lower()==texture.lower(),(s,material)
    assert sum(mapping[s].get("c1l1_3building","").lower()=="c1l1_building.tga" for s in STEMS)==7
    report={"stage":"G64","source_files_sha256":fingerprints,
            "proofs":[r for r in allrows if r["material"] in TARGETS],
            "2010_native_shader_property_40_60_tex_binding_proven":True,
            "sphere20_21_original_UV_shader_mapping_proven":False,
            "native_source_meshes_modified":False,"new_VPK":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print("PASS G64 40/60B property records, 7 original BRES building atlas links, 3 original BRES globe 20/21 atlas links; native UV shader still unresolved")

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--zip",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    args=a.parse_args()
    main(args.zip,args.out)
