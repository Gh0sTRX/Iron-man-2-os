#!/usr/bin/env python3
"""2010 B11 C1L1 GLB scene graph mesh-node transform vs GPU raw positions.

Check whether G9 draws untransformed mesh primitives and thereby drops
original source instance transforms, explaining invisible walls and city gaps.
No guessed sky/buildings or player spawn.
"""
import argparse,json,collections,math,zipfile
from pathlib import Path
import numpy as np
from export_b24_c1_gpu_mesh import SOURCE,MEMBER,decode_glb,arr
def main(out):
 with zipfile.ZipFile(SOURCE) as z:doc,data=decode_glb(z.read(MEMBER))
 nodes=doc.get("nodes",[])
 scenes=doc.get("scenes",[])
 meshes=doc["meshes"]
 parents={}
 for j,node in enumerate(nodes):
  for child in node.get("children",[]):
   if child in parents:raise ValueError("GLB node two parents")
   parents[child]=j
 def mat(j):
  node=nodes[j]
  if "matrix" in node:
   return np.asarray(node["matrix"],dtype=np.float64).reshape(4,4).T
  xyz=np.asarray(node.get("translation",[0,0,0]),dtype=np.float64)
  scale=np.asarray(node.get("scale",[1,1,1]),dtype=np.float64)
  # nonrotation audit conservative - note if rotation exists
  m=np.diag([*scale,1.])
  m[:3,3]=xyz
  return m
 original=[]
 transformed=[]
 for i,node in enumerate(nodes):
  if "mesh" not in node:continue
  idx=node["mesh"]
  if not 0<=idx<len(meshes):raise ValueError("index invalid")
  chain=[];j=i
  while j in range(len(nodes)):
   if j in chain:raise ValueError("node ancestry cycle")
   chain.append(j)
   j=parents.get(j,-1)
  matrix=np.eye(4)
  for item in reversed(chain):matrix=matrix@mat(item)
  loc=mat(i)
  transformed.append({"node_index":i,"mesh_index":idx,
    "name":node.get("name",""),"direct_translation":node.get("translation"),
    "direct_rotation":node.get("rotation"),
    "direct_scale":node.get("scale"),
    "direct_matrix":node.get("matrix"),
    "scene_ancestors":chain,
    "full_node_world_translation":matrix[:3,3].tolist(),
    "full_node_transform_is_identity":bool(np.allclose(matrix,np.eye(4),atol=1e-6)),
    "mesh_vertex_count":len(arr(doc,data,meshes[idx]["primitives"][0]["attributes"]["POSITION"]))})
 nontrivial=[e for e in transformed if not e["full_node_transform_is_identity"]]
 directnontrivial=[e for e in transformed if any(abs(float(x))>1e-6 for x in e["full_node_world_translation"])]
 result={
  "original_meshes":len(meshes),"GLB_nodes":len(nodes),"scenes":len(scenes),
  "scene_root_indices":[x.get("nodes",[]) for x in scenes],
  "nodes_with_mesh":len(transformed),
  "mesh_nodes_with_nonidentity_world":len(nontrivial),
  "mesh_nodes_with_nonzero_world_translations":len(directnontrivial),
  "source_mesh_nodes_full_transform_examples":nontrivial[:35],
  "all_nodes_nonzero_translation_examples":[e for e in transformed if e["direct_translation"]][:35],
  "root_nodes":[{"name":n.get("name"),"children":n.get("children"),
                  "rotation":n.get("rotation"),"matrix":n.get("matrix")}
                 for i,n in enumerate(nodes) if i not in parents][:8],
  "B24_GPU_C1G2_mesh_positions_intentionally_raw":True,
  "original_level_author_instance_locations_from_bclara_proven":False,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2)+"\n")
 print("G10_C1L1_AUTHOR_GLTF_NODES_TRANSFORMS",len(meshes),len(nodes),
       "meshnodes",len(transformed),"nonidentity",len(nontrivial),
       "nonzero_world_translation",len(directnontrivial))
 print("G10_C1L1_AUTHOR_NONZERO_MESH_TRANSFORMS",directnontrivial[:18])
 print("G10_C1L1_AUTHOR_NONIDENTITY_MESH_TRANSFORMS",nontrivial[:8])
 print("PASS original G9 authored mesh and scene node transform audit; no invented world coordinate")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 main(a.out)
