#!/usr/bin/env python3
"""G37: decode actual 2010 original CLARA Deco source resource type fields.

This is ORIGINAL source structure evidence, not reconstructed game engine:
- Every typed Deco class instance has a 0x004D typed child-parent record,
  a 0x000B followed by tagged 4-byte UINT32 resource-like identifier,
  plus another typed 4-byte field whose role is unverified.
- One authentic 0x005C transform record per Deco linked to same parent ID.
- Scene authored-local XYZ/quat/scale are recovered from original bytes.
The engine's exact resource-manager ID→BRES model library is NOT yet solved.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,math,re,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact

PAT=re.compile(rb"[\x20-\x7e]{2,90}")
FAMILY={10:"C1L1_car_01",11:"C1L1_car_02",
        15:"C1L1_light_001",16:"C1L1_light_002",17:"C1L1_light_003",
        18:"C1L1_obj_001",19:"C1L1_obj_002",20:"C1L1_obj_003",
        21:"C1L1_obj_004"}
def audit(raw:bytes)->dict:
    assert len(raw)==339733
    assert hashlib.sha256(raw).hexdigest()=="31c794a0140d607c1abd43e463a02cab73d5e2cbbc8495d7cc96f55876aead3c"
    prototypes={}
    for m in PAT.finditer(raw[:38719]):
        p=m.start()
        if p>=6 and struct.unpack_from("<H",raw,p-2)[0]==len(m.group()):
            k=struct.unpack_from("<I",raw,p-6)[0]
            if 0<k<=400:prototypes[k]=m.group().decode("ascii")
    assert len(prototypes)==193
    class_id=next(k for k,v in prototypes.items() if v=="Deco")
    out=[]
    for m in PAT.finditer(raw):
        p=m.start()
        if p<7 or raw[p-3]!=1 or struct.unpack_from("<H",raw,p-2)[0]!=len(m.group()):continue
        id=struct.unpack_from("<I",raw,p-7)[0]
        if not 0<id<50000:continue
        end=m.end()
        if raw[end:end+5]!=b"\x80\xff\xff\xff\xff":continue
        cls=struct.unpack_from("<I",raw,end+5)[0]
        if cls!=class_id:continue
        name=m.group().decode("ascii")
        k=raw.find(b"\x4d\x00\x01",end,end+100)
        if k!=end+46:raise ValueError("original Deco 0x004D typed child header missing "+name)
        if struct.unpack_from("<I",raw,k+3)[0]!=id+2 or raw[k+7]!=0 or struct.unpack_from("<I",raw,k+8)[0]!=id:
            raise ValueError("native Deco resource-child parent ID broken "+name)
        if raw[k+20:k+24]!=b"\x0b\x00\x04\x00" or raw[k+28:k+30]!=b"\x04\x00":
            raise ValueError("original 2010 Deco typed 4B resource fields changed "+name)
        type_field=struct.unpack_from("<I",raw,k+24)[0]
        secondary=struct.unpack_from("<I",raw,k+30)[0]
        t=raw.find(b"\x5c\x00\x01",end,end+330)
        if t<0 or struct.unpack_from("<I",raw,t+8)[0]!=id:raise ValueError("native source 0x5C transform parent missing "+name)
        s=t+48
        if raw[s:s+2]!=b"\x0c\x00" or raw[s+14:s+16]!=b"\x10\x00" or raw[s+32:s+34]!=b"\x0c\x00":
            raise ValueError("original position/quaternion/scale tags changed "+name)
        xyz=struct.unpack_from("<3f",raw,s+2)
        q=struct.unpack_from("<4f",raw,s+16)
        scl=struct.unpack_from("<3f",raw,s+34)
        if not all(math.isfinite(v) for v in xyz+q+scl) or abs(sum(t*t for t in q)-1.0)>.002:
            raise ValueError("original source native transform invalid "+name)
        row={"source_Deco_name":name,"original_source_entity_ID":id,"source_class_ID":class_id,
             "original_binary_name_byte_offset":p,
             "native_source_resource_tag_0x004D_offset":k,
             "native_raw_resource_type_uint32":type_field,
             "native_raw_secondary_uint32":secondary,
             "native_transform_tag_0x005C_byte_offset":t,
             "source_X":round(xyz[0],6),"source_Y":round(xyz[1],6),"source_Z":round(xyz[2],6),
             "source_quat_xyzw":[round(a,6) for a in q],"source_scale_xyz":[round(a,6) for a in scl],
             "original_local_xyz_nonzero":any(abs(a)>0.0001 for a in xyz),
             "G36_BRES_family_NAME_CORRESPONDENCE_ONLY":FAMILY.get(type_field),
             "original_native_resource_type_index_to_BRES_filename_PROVEN":False,
             "original_runtime_world_instance_transform_PROVEN":False}
        out.append(row)
    assert len(out)==53
    freq=collections.Counter(x["native_raw_resource_type_uint32"] for x in out)
    assert len(freq)==25 and sum(x["original_local_xyz_nonzero"] for x in out)==41
    assert freq[44]==7 and freq[134]==11 and freq[136]==10
    assert sorted(x["source_Deco_name"] for x in out if x["native_raw_resource_type_uint32"]==44)==[
      "Deco_fence","Deco_fence1","Deco_fence2","Deco_fence3","Deco_fence4","Deco_fence5","Deco_fence6"]
    assert sorted(set(x["native_raw_secondary_uint32"] for x in out if x["native_raw_resource_type_uint32"]==134))==[385,386,387]
    return {
      "source_original_CLARA_SHA256":hashlib.sha256(raw).hexdigest(),
      "native_original_Deco_class_ID":class_id,
      "source_2010_original_Deco_instances":len(out),
      "distinct_source_type_field_values":len(freq),
      "native_nonzero_local_positions":41,
      "native_local_origin_positions":12,
      "source_type_field_histogram":dict(sorted(freq.items())),
      "source_decoded_native_Deco_0x4D_resource_fields_and_0x5C_transforms":out,
      "native_resource_index_to_actual_BRES_file_proven":False,
      "source_scene_parent_to_final_world_matrix_proven":False,
      "no_VPK_or_performance_changes":True}
def main():
    ap=argparse.ArgumentParser()
    x=ap.add_mutually_exclusive_group(required=True)
    x.add_argument("--ipa",type=Path)
    x.add_argument("--bclara",type=Path)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    if args.ipa:
        with zipfile.ZipFile(args.ipa) as z:
            clev=z.read("Payload/IronMan2.app/clev")
        raw=get_exact(clev,decode(clev,".bclara"),"level1.bclara")
    else:
        raw=args.bclara.read_bytes()
    result=audit(raw)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PASS G37 original owner 2010 source: 53 native Deco class items; 25 type fields; 41 placed local XYZ; 12 at local origin.")
    print("G37 source 44 fence actors=7, source 134 enemy actors=11, source 136 enemy actors=10")
    print("G37 original native resource index to BRES instance world transforms NOT YET proven; no VPK.")
if __name__=="__main__":
    main()
