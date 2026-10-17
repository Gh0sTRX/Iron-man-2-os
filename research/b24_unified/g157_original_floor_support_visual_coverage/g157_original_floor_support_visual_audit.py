#!/usr/bin/env python3
"""Read-only G157 exact original 2010 C1L1 world support vs visual face QA.

Replay native G75 walkable/non-wall face classification from the REAL
original G104 source assets, not inventing floor collision. Export only
aggregate XY grid QA metadata/HTML/SVG; never original models or textures.
A visible horizontal triangle does NOT establish walkability or solidity.
"""
from __future__ import annotations
import argparse
import collections
import html
import json
import math
import struct
import zipfile
from pathlib import Path

VBO_HEADER=20+32*16
ALPHA_ATLASES={1,6,7,9,15,19,20}
GRID_STEP=4
ROI_HALF=160
WORLD_TILE=16
KNOWN_X=-1.319
KNOWN_Y=-6.747

def wall_source(p):
    a,b,c=p
    ux,uy,uz=(b[i]-a[i] for i in range(3))
    vx,vy,vz=(c[i]-a[i] for i in range(3))
    nx=uy*vz-uz*vy
    ny=uz*vx-ux*vz
    nz=ux*vy-uy*vx
    n=nx*nx+ny*ny+nz*nz
    if n<1e-8 or not math.isfinite(n):
        raise ValueError("Degenerate source triangle")
    return nz*nz<.3364*n and max(q[2] for q in p)-min(q[2] for q in p)>.1

def make_triangle(p):
    ax,ay,az=p[0]
    bx,by,bz=p[1]
    cx,cy,cz=p[2]
    u=bx-ax;v=by-ay;w=cx-ax;q=cy-ay
    det=u*q-v*w
    if abs(det)<1e-8:return None
    return (min(ax,bx,cx),max(ax,bx,cx),
            min(ay,by,cy),max(ay,by,cy),
            ax,ay,az,u,v,w,q,bz-az,cz-az,det)

def triangle_intersection_z(tri,x,y):
    if not tri or x<tri[0]-.0001 or x>tri[1]+.0001 or y<tri[2]-.0001 or y>tri[3]+.0001:
        return None
    _,_,_,_,ax,ay,az,u,v,w,q,dz1,dz2,det=tri
    dx=x-ax;dy=y-ay
    a=(dx*q-dy*w)/det
    b=(u*dy-v*dx)/det
    if a<-.0002 or b<-.0002 or a+b>1.0002:return None
    z=az+a*dz1+b*dz2
    return z if math.isfinite(z) else None

def unpack_owner_assets(path):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError("G104 original VPK zip CRC failed")
        mesh=z.read("assets/G66_city.g66m")
        collision=z.read("assets/G66_original_collision.g66c")
    if mesh[:4]!=b"G66M" or struct.unpack_from("<4I",mesh,4)!=(1,67323,32,31):
        raise ValueError("Original G66M typed real 2010 first world changed")
    if len(mesh)!=VBO_HEADER+67323*24:
        raise ValueError("Source G66M original full draw vertex length invalid")
    if collision[:4]!=b"G66C" or struct.unpack_from("<2I",collision,4)!=(1,1910):
        raise ValueError("Original 2010 G66C 1910 native face header changed")
    if len(collision)!=12+1910*36:
        raise ValueError("Native original G66C byte length invalid")
    return mesh,collision

def index_support(triangles):
    tile=collections.defaultdict(list)
    for tri in triangles:
        if tri is None:continue
        x0=max(math.floor(tri[0]/WORLD_TILE),-11)
        x1=min(math.floor(tri[1]/WORLD_TILE),11)
        y0=max(math.floor(tri[2]/WORLD_TILE),-11)
        y1=min(math.floor(tri[3]/WORLD_TILE),11)
        for cy in range(y0,y1+1):
            for cx in range(x0,x1+1):
                tile[cx,cy].append(tri)
    return tile

def sample_heights(tile,x,y):
    ans=[]
    for tri in tile.get((math.floor(x/WORLD_TILE),math.floor(y/WORLD_TILE)),()):
        z=triangle_intersection_z(tri,x,y)
        if z is not None:
            ans.append(z)
    # Source supports can overlap in height; keep original geometry
    # quantities without an invented player foot height.
    return sorted(set(round(z,4) for z in ans))

def classify(native,visual):
    if native and visual:return "both"
    if native:return "native_only"
    if visual:return "visual_only"
    return "neither"

def parse_source(mesh,collision):
    native=[]
    for i in range(1910):
        p=tuple(struct.unpack_from("<3f",collision,12+i*36+j*12) for j in range(3))
        if any(not math.isfinite(c) or abs(c)>1e5 for vertex in p for c in vertex):
            raise ValueError("G66C invalid source coords")
        if not wall_source(p):
            native.append(make_triangle(p))
    if len(native)!=220:
        raise ValueError("Real 2010 G75 original nonwall collision changed")
    batches=[struct.unpack_from("<4I",mesh,20+i*16) for i in range(32)]
    if any(not math.isfinite(struct.unpack_from("<f",mesh,VBO_HEADER+i*24)[0]) for i in range(67323)):
        raise ValueError("G66M invalid world float")
    visual=[]
    alpha_face_count=0
    opaque_nonwall_face_count=0
    offset=0
    for group,(first,count,tex,flags) in enumerate(batches):
        if first!=offset or count<=0 or count%3 or count>67323-offset or (
                tex!=0xFFFFFFFF and tex>=31):
            raise ValueError("G66M bad original source batches")
        offset+=count
        if tex==0xFFFFFFFF or tex in ALPHA_ATLASES:
            alpha_face_count+=count//3
            continue
        for j in range(first,first+count,3):
            p=tuple(struct.unpack_from("<3f",mesh,VBO_HEADER+(j+k)*24) for k in range(3))
            if any(not math.isfinite(c) or abs(c)>1e5 for vertex in p for c in vertex):
                raise ValueError("G66M original vertex out-of-range")
            # skip degenerate source decorative pieces, no synthetic collision
            a,b,c=p
            ab=tuple(b[t]-a[t] for t in range(3))
            ac=tuple(c[t]-a[t] for t in range(3))
            nx=ab[1]*ac[2]-ab[2]*ac[1]
            ny=ab[2]*ac[0]-ab[0]*ac[2]
            nz=ab[0]*ac[1]-ab[1]*ac[0]
            n=nx*nx+ny*ny+nz*nz
            if n<1e-8 or nz*nz<.3364*n and max(q[2] for q in p)-min(q[2] for q in p)>.1:
                continue
            opaque_nonwall_face_count+=1
            tri=make_triangle(p)
            if tri is not None:
                visual.append(tri)
    if offset!=67323:
        raise ValueError("G66M source batch vertex account changed")
    return native,visual,{"original_collision_nonwall_faces":len(native),
       "original_collision_wall_faces":1910-len(native),
       "visual_opaque_nonwall_faces_raw":opaque_nonwall_face_count,
       "visual_opaque_nonwall_faces_nondegenerate_XY":len(visual),
       "skipped_alpha_or_missing_texture_triangles":alpha_face_count}

def produce(path,outdir):
    mesh,col=unpack_owner_assets(path)
    native,visual,source_stats=parse_source(mesh,col)
    nidx=index_support(native)
    vidx=index_support(visual)
    reference_native=sample_heights(nidx,KNOWN_X,KNOWN_Y)
    if not any(abs(z-2.82955)<.005 for z in reference_native) or not any(abs(z-6.67306)<.005 for z in reference_native):
        raise ValueError("G157 G75 actual original stacked floor source reference mismatch")
    if sample_heights(nidx,10000,10000) or sample_heights(vidx,10000,10000):
        raise ValueError("Original source ROI index falsely expands world")
    xs=list(range(-ROI_HALF,ROI_HALF+1,GRID_STEP))
    ys=list(range(-ROI_HALF,ROI_HALF+1,GRID_STEP))
    counts=collections.Counter()
    tile_stats=collections.defaultdict(collections.Counter)
    max_native=0;max_visual=0;closest_height_delta=[]
    samples=[]
    examples=collections.defaultdict(list)
    for y in ys:
        for x in xs:
            a=sample_heights(nidx,x,y)
            b=sample_heights(vidx,x,y)
            result=classify(a,b)
            counts[result]+=1
            tile_stats[(x//32,y//32)][result]+=1
            max_native=max(max_native,len(a))
            max_visual=max(max_visual,len(b))
            if a and b:
                closest_height_delta.append(min(abs(z-z2) for z in a for z2 in b))
            if len(examples[result])<18:
                examples[result].append([x,y])
            samples.append((x,y,result,len(a),len(b)))
    assert sum(counts.values())==len(xs)*len(ys)
    assert len(xs)==81 and len(ys)==81
    report={
       "source":"User original 2010 Iron Man 2 iOS C1L1 through preexisting G104 private VPK source resource snapshot",
       "source_baseline_gitHub_run":38974292901,
       "replayed_actual_2010_source_collision":True,
       "source_stats":source_stats,
       "audit_xy_roi":{"x_min":xs[0],"x_max":xs[-1],
           "y_min":ys[0],"y_max":ys[-1],"step":GRID_STEP,
           "grid_points":len(samples),"region_is_original_mission_spawn":False,
           "sampling_method":"exact XY barycentric point in source triangle (both native G75 and visible opaque non-steep authored source faces)"},
       "classification_counts":dict(counts),
       "classification_meaning":{
           "both":"At sampled XY source G75 native nonwall and original opaque visible nonwall surface intersect, heights may differ.",
           "native_only":"Only G75 native authored nonwall source at this XY; possible invisible collision proxy.",
           "visual_only":"Only original opaque nonwall visual source at this XY, without a G75 nonwall triangle ANY height. This does NOT prove should be solid floor.",
           "neither":"No nonwall triangle at sampled XY, not proof that scene is empty or inaccessible."
       },
       "known_G75_ground_test_xy":[KNOWN_X,KNOWN_Y],
       "known_G75_exact_source_stacked_support_heights":reference_native,
       "max_native_stacked_faces_at_one_xy":max_native,
       "max_visible_stacked_faces_at_one_xy":max_visual,
       "xy_both_heights_min_delta_summary":{
           "samples":len(closest_height_delta),
           "near_or_equal_0_5":sum(x<=.5 for x in closest_height_delta),
           "offset_gt_2":sum(x>2 for x in closest_height_delta)},
       "examples_xy_source_quadrants_metadata":dict(examples),
       "tile32_counts":[{"tile_x":k[0],"tile_y":k[1],**dict(v)} for k,v in sorted(tile_stats.items())],
       "source_floor_coverage_proven_for_entire_world":False,
       "visual_only_means_walkable":False,
       "source_collision_complete":False,
       "native_vita_visual_hardware_test_passed":False,
       "new_vpk":False
    }
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"G157_original_first_level_floor_support_coverage.json").write_text(
       json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    palette={"both":"#57a975","native_only":"#4f89bd",
        "visual_only":"#ebaf58","neither":"#333b48"}
    shapes=[]
    for x,y,state,_,_ in samples:
        sx=(x+ROI_HALF)//GRID_STEP
        sy=(ROI_HALF-y)//GRID_STEP
        shapes.append(f'<rect x="{sx*7}" y="{sy*7}" width="7" height="7" fill="{palette[state]}"/>')
    legend="".join(f'<rect x="{x}" y="615" width="15" height="15" fill="{palette[k]}"/><text x="{x+20}" y="628" fill="#eeeeee" font-size="13">{html.escape(k)} ({counts[k]})</text>'
       for k,x in (("both",16),("native_only",164),("visual_only",336),("neither",497)))
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="685" height="656" viewBox="0 0 685 656"><rect width="100%" height="100%" fill="#151c26"/><text x="16" y="18" fill="white" font-family="Arial" font-size="15">G157: Original C1L1 native/visible non-steep face coverage (NOT a playable map)</text><g transform="translate(16 32)">'+''.join(shapes)+'</g>'+legend+'<text x="16" y="645" fill="#b2bac8" font-size="11">XY grid: -160..+160, step 4 original units. All Z layers projected. Not a collision/solidity decision.</text></svg>'
    (outdir/"G157_source_floor_coverages_only.svg").write_text(svg,encoding="utf-8")
    lines=["x,y,has_native_nonwall,has_visual_opaque_nonwall,native_layers,visible_layers"]
    for x,y,state,nc,vc in samples:
        lines.append(f"{x},{y},{int(nc>0)},{int(vc>0)},{nc},{vc}")
    (outdir/"G157_source_ground_support_grid.csv").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("G157 SOURCE original 2010 C1L1:",source_stats)
    print("G157 known G75 stacked source supports at (-1.319,-6.747):",reference_native)
    print("G157 XY grid world source support-vs-visible:",dict(counts))
    print("G157 true source triangulation complete; no fake authored solids, no FPS, no VPK")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preexisting-source-vpk",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    produce(a.preexisting_source_vpk,a.outdir)

if __name__=="__main__":
    main()
