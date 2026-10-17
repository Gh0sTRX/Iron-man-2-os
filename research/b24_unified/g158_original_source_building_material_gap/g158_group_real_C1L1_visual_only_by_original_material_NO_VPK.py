#!/usr/bin/env python3
"""G158 original 2010 C1L1 authored G66 visual roof/material provenance QA.

Not a mesh exporter or collider generator. Reuse original G157 source
barycentric floor classification. For every actual G157 visual-only sample
on the source Z~2.82955 stacked level, report which original G66M 32 draw
groups / 31 atlas ID triangles contain that sample and the nearest native
G66C non-wall height. Make hot clusters actionable for a real Vita test.
No guessed solidness, original textures, IPA, game source or new VPK.
"""
from __future__ import annotations
import argparse
import collections
import html
import json
import math
import sys
from pathlib import Path

G157=Path(__file__).resolve().parents[1]/"g157_original_floor_support_visual_coverage"
sys.path.insert(0,str(G157))
import g157_original_floor_support_visual_audit as old

SRC_Z=2.82955
LOW_Z=.0725
HIGH_Z=6.67306
Z_TOL=.5
STEP=4
ROI=160
Z_NAMES={"low":LOW_Z,"middle":SRC_Z,"high":HIGH_Z}

def build_groups(mesh):
    """Only native opaque non-steep visual triangles; preserve real batch IDs."""
    batches=[]
    grouped=collections.defaultdict(list)
    for group,(first,count,tex,flags) in enumerate(
            __import__("struct").unpack_from("<128I",mesh,20)[i:i+4]
            for i in range(0,128,4)):
        if tex==0xffffffff or tex in old.ALPHA_ATLASES:
            continue
        for i in range(first,first+count,3):
            p=tuple(__import__("struct").unpack_from(
                "<3f",mesh,old.VBO_HEADER+(i+k)*24) for k in range(3))
            a,b,c=p
            u=tuple(b[j]-a[j] for j in range(3))
            v=tuple(c[j]-a[j] for j in range(3))
            normal=(u[1]*v[2]-u[2]*v[1],
                    u[2]*v[0]-u[0]*v[2],
                    u[0]*v[1]-u[1]*v[0])
            n=sum(x*x for x in normal)
            if n<1.e-8:continue
            if normal[2]*normal[2]<.3364*n and (
                    max(p0[2] for p0 in p)-min(p0[2] for p0 in p))>.1:
                continue
            triangle=old.make_triangle(p)
            if triangle is not None:
                # Input is the original G66M GPU material group, NOT
                # an original level1 CLARA node or solidity permission.
                batches.append((triangle,group,tex,i//3))
                grouped[group].append(i//3)
    return batches,grouped

def index_visual(visual):
    tile=collections.defaultdict(list)
    for face in visual:
        tri=face[0]
        lo_x=max(math.floor(tri[0]/old.WORLD_TILE),-11)
        hi_x=min(math.floor(tri[1]/old.WORLD_TILE),11)
        lo_y=max(math.floor(tri[2]/old.WORLD_TILE),-11)
        hi_y=min(math.floor(tri[3]/old.WORLD_TILE),11)
        for yi in range(lo_y,hi_y+1):
            for xi in range(lo_x,hi_x+1):
                tile[xi,yi].append(face)
    return tile

def visible_heights(index,x,y):
    candidates=[]
    for tri,group,tex,face_id in index.get((
            math.floor(x/old.WORLD_TILE),math.floor(y/old.WORLD_TILE)),()):
        z=old.triangle_intersection_z(tri,x,y)
        if z is not None:
            candidates.append((round(z,4),group,tex,face_id))
    return candidates

def nearest_reference(native_heights,z):
    if not native_heights:
        return None,None
    nz=min(native_heights,key=lambda h:abs(h-z))
    return nz,round(z-nz,4)

def clusters_for(coords):
    available=set(coords)
    visited=set()
    clusters=[]
    for xy in sorted(available):
        if xy in visited:continue
        queue=collections.deque([xy])
        visited.add(xy)
        cells=[]
        while queue:
            v=queue.popleft()
            cells.append(v)
            for nxt in ((v[0]+STEP,v[1]),(v[0]-STEP,v[1]),
                        (v[0],v[1]+STEP),(v[0],v[1]-STEP)):
                if nxt in available and nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        clusters.append(cells)
    clusters.sort(key=lambda xs:(-len(xs),min(xs)))
    return clusters

def produce(vpk,outdir):
    mesh,coll=old.unpack_owner_assets(vpk)
    native,old_visual,source_stats=old.parse_source(mesh,coll)
    original_visual,groups=build_groups(mesh)
    if len(original_visual)!=len(old_visual):
        raise ValueError("G158 original opaque nonsteep group provenance drift")
    ni=old.index_support(native)
    vi=index_visual(original_visual)
    all_cells=[]
    middle_unmatched={}
    counters={s:collections.Counter() for s in Z_NAMES}
    material_samples=collections.Counter()
    material_unique_triangles=collections.defaultdict(set)
    min_height_support=collections.Counter()
    selected_samples=[]
    for y in range(-ROI,ROI+1,STEP):
        for x in range(-ROI,ROI+1,STEP):
            native_z=old.sample_heights(ni,x,y)
            visible_z=visible_heights(vi,x,y)
            for slug,target_z in Z_NAMES.items():
                native_at_z=[n for n in native_z if abs(n-target_z)<=Z_TOL]
                visual_at_z=[v for v in visible_z if abs(v[0]-target_z)<=Z_TOL]
                state=old.classify(native_at_z,visual_at_z)
                counters[slug][state]+=1
                if slug=="middle":
                    row={"x":x,"y":y,"state":state}
                    if state=="visual_only":
                        # A single XY may overlap multiple original visual
                        # triangles. Keep each unique group once, and one
                        # representative face closest to this real Z sample.
                        grouping=collections.defaultdict(set)
                        for z,g,tex,face_id in visual_at_z:
                            grouping[(g,tex)].add(face_id)
                            material_unique_triangles[(g,tex)].add(face_id)
                        for group_tex in grouping:
                            material_samples[group_tex]+=1
                        chosen=min(visual_at_z,key=lambda v:(
                            abs(v[0]-target_z),v[1],v[3]))
                        nz,gap=nearest_reference(native_z,chosen[0])
                        if nz is None:
                            min_height_support["no_original_nonwall_any_z"]+=1
                        elif gap>0.5:
                            min_height_support["native_lower_than_rendered"]+=1
                        elif gap<-.5:
                            min_height_support["native_higher_than_rendered"]+=1
                        else:
                            min_height_support["native_same_z_unexpected"]+=1
                        row.update({
                            "observed_source_visual_z":chosen[0],
                            "original_G66_draw_group":chosen[1],
                            "original_G66_atlas":chosen[2],
                            "source_triangle_index":chosen[3],
                            "all_source_groups_at_xy":[
                                {"group":g,"atlas":t}
                                for g,t in sorted(grouping)],
                            "nearest_native_nonwall_z":nz,
                            "visual_minus_nearest_native_z":gap
                        })
                        middle_unmatched[(x,y)]=row
                    all_cells.append(row)
                    if state=="visual_only" and len(selected_samples)<50:
                        selected_samples.append(row)
    required={"low":{"native_only":2892,"both":3669},
              "middle":{"visual_only":628,"neither":5730,"both":203},
              "high":{"neither":6521,"visual_only":40}}
    if {x:dict(counters[x]) for x in required}!=required:
        raise ValueError("G158 could not match independent original G157 source height evidence")
    if len(all_cells)!=6561 or len(middle_unmatched)!=628:
        raise ValueError("G158 no native/visual first chapter parity")
    clusters=clusters_for(middle_unmatched)
    crows=[]
    for ci,cells in enumerate(clusters):
        bygroup=collections.Counter()
        for xy in cells:
            # Attribute each source atlas on the XY to a genuine source
            # draw batch; never call it collision property.
            row=middle_unmatched[xy]
            for x in row["all_source_groups_at_xy"]:
                bygroup[(x["group"],x["atlas"])]+=1
        crows.append({
            "source_cluster_id":ci,
            "grid_sample_count":len(cells),
            "source_xy_bounds":[min(k[0] for k in cells),
                min(k[1] for k in cells),max(k[0] for k in cells),
                max(k[1] for k in cells)],
            "original_draw_groups":[{"group":key[0],"atlas":key[1],
                 "sample_hits":v} for key,v in bygroup.most_common(10)],
            "not_source_playability_decision":True
        })
    import statistics
    # Source-height diagnosis by original texture group, never turn pixel
    # identity into a physics offset or source-authored world transform.
    grouped_rows=collections.defaultdict(list)
    for row in middle_unmatched.values():
        for group in row["all_source_groups_at_xy"]:
            grouped_rows[(group["group"],group["atlas"])].append(row)
    material_rows=[]
    for (g,t),n in sorted(material_samples.items(),
                          key=lambda x:(-x[1],x[0])):
        examples=grouped_rows[(g,t)]
        if len(examples)!=n:
            raise ValueError("Original source material/sample dedup drift")
        vis=[x["observed_source_visual_z"] for x in examples]
        old_heights=[x["nearest_native_nonwall_z"] for x in examples]
        vertical_deltas=[x["visual_minus_nearest_native_z"] for x in examples]
        material_rows.append({
            "original_G66_draw_group":g,
            "original_atlas_id":t,
            "sample_xy_count":n,
            "unique_source_triangle_indices_touching_samples":
                len(material_unique_triangles[(g,t)]),
            "visible_source_Z_min_median_max":[
                round(min(vis),4),round(statistics.median(vis),4),
                round(max(vis),4)],
            "nearest_original_collision_nonwall_Z_min_median_max":
                [round(min(old_heights),4),
                 round(statistics.median(old_heights),4),
                 round(max(old_heights),4)] if all(z is not None for z in old_heights) else None,
            "visual_minus_nearest_original_collision_Z_min_median_max":
                [round(min(vertical_deltas),4),
                 round(statistics.median(vertical_deltas),4),
                 round(max(vertical_deltas),4)] if all(z is not None for z in vertical_deltas) else None,
            "source_material_or_native_solidness_unproven":True
        })
    audit={
        "source":"G104 pre-existing authentic 2010 C1L1 source, direct G66M draw group and G66C nonwall barycentric tests",
        "original_source_snapshot_G104_run_id":38974292901,
        "original_native_nonwall_face_count":len(native),
        "original_opaque_nonsteep_visual_faces":len(original_visual),
        "bounds":{"xy_min":-ROI,"xy_max":ROI,"grid_step":STEP,
            "world_units_not_screen_pixels":True,"not_original_spawn":True},
        "reference_source_z_heights":Z_NAMES,
        "height_tolerance":Z_TOL,
        "observed_source_parity":{k:dict(v) for k,v in counters.items()},
        "visual_only_middle_z_count":len(middle_unmatched),
        "visual_only_original_G66_draw_group_attribution":material_rows,
        "disconnected_visual_only_xy_clusters":len(crows),
        "clusters":crows[:75],
        "native_vertical_proximity_explanation":dict(min_height_support),
        "examples_near_original_middle_z_source_xyz":selected_samples,
        "caution":"Original draw group/atlas is not a confirmed CLARA parent node or CollisionEntity solidity flag. A no-native-near-z sample may be an unwalkable decorative surface, or a roof/bridge. No new colliders.",
        "no_original_owner_geometry_in_results":True,
        "does_not_modify_native_collision":True,
        "first_playable_device_blocked":True,
        "new_vpk":False
    }
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"G158_real_C1L1_building_surface_attribution.json").write_text(
        json.dumps(audit,ensure_ascii=False,indent=2)+"\n")
    (outdir/"G158_visual_only_original_groups.csv").write_text(
        "group,atlas,sampled_xy,unique_triangles,original_solidity_unproven\n"+
        "".join(f'{x["original_G66_draw_group"]},{x["original_atlas_id"]},'
          f'{x["sample_xy_count"]},'
          f'{x["unique_source_triangle_indices_touching_samples"]},1\n'
          for x in material_rows))
    svgrows=[]
    # No original polygon/texture resource exported; metadata raster only.
    palette=["#d97752","#f4c35f","#4bc4c4","#96a2e2","#ab88dc",
             "#65c68b","#e78cb0","#d5e088","#c0a184","#b9cbef"]
    top_group={x["original_G66_draw_group"]:i for i,x in
               enumerate(material_rows[:10])}
    counts_by_primary=collections.Counter()
    for row in all_cells:
        px=(row["x"]+ROI)//STEP
        py=(ROI-row["y"])//STEP
        if row["state"]=="visual_only":
            group=row["original_G66_draw_group"]
            counts_by_primary[group]+=1
            color=palette[top_group[group]] if group in top_group else "#eeeeee"
            title=f'original XY {row["x"]},{row["y"]} Z={row["observed_source_visual_z"]} draw group={group} atlas={row["original_G66_atlas"]} nearest native Z={row["nearest_native_nonwall_z"]}'
        else:
            color=("#354451" if row["state"]=="neither" else "#517c68")
            title=f'XY {row["x"]},{row["y"]} state={row["state"]}'
        svgrows.append(f'<rect x="{px*7}" y="{py*7}" width="7" height="7" '
            f'fill="{color}"><title>{html.escape(title)}</title></rect>')
    leg="".join(f'<text x="18" y="{615+(i//5)*19}" fill="{palette[i]}" font-size="12">'
        f'Group {g} ({material_rows[i]["sample_xy_count"]})</text>'
        for i,g in enumerate([x["original_G66_draw_group"] for x in material_rows[:10]]))
    # Public samples are metadata positions from original owner VPK, not
    # redistributable textured triangle geometry. SVG renders occupancy.
    svg=('<svg xmlns="http://www.w3.org/2000/svg" width="620" height="710" '
        'viewBox="0 0 620 710"><rect width="100%" height="100%" fill="#151d27"/>'
        '<text x="18" y="22" fill="white" font-size="14">G158 original C1L1 draw-batch attribution, Z~2.82955</text>'
        '<text x="18" y="43" fill="#cbd5e1" font-size="12">Orange/color = visible non-steep source / NO G66C nearby floor.</text>'
        '<g transform="translate(18 55)">'+''.join(svgrows)+'</g>'+leg+
        '<text x="18" y="690" fill="#9ca3af" font-size="11">Metadata grid only. Source G66 texture batches are NOT gameplay solidity proof.</text></svg>')
    (outdir/"G158_original_source_material_hotspot_visual_only.svg").write_text(svg)
    print("G158 actual G157 independent source heights:",{k:dict(v) for k,v in counters.items()})
    print("G158 G66M visual-only middle Z source GROUP top:",material_rows[:12])
    print("G158 contiguous 4-neighbor visual-only hotspots:",crows[:8])
    print("G158 native/source closest Z categories:",dict(min_height_support))
    print("G158 PASS source geometry material group attribution: 628 genuine middle-Z pixels; 0 synthetic native collider / original iOS solidity NOT proven / NO VPK")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--preexisting-source-vpk",required=True,type=Path)
    ap.add_argument("--outdir",required=True,type=Path)
    args=ap.parse_args()
    produce(args.preexisting_source_vpk,args.outdir)

if __name__=="__main__":main()
