#!/usr/bin/env python3
"""One user-authorized G161 Vita hardware QA VPK. NOT a final game.

Uses the PREVIOUSLY HARDWARE-TESTED G106 source-faithful source-asset
packer with NEW unique title ID. Actual executable is latest
G160 whole-game ARM ELF + SFO/SELF from VitaSDK (never substitute G106
binary). All G66M/G66C, 31 atlases, genuine G73 sky and 248 source Mark V
clips checked by inherited packer. No new fake assets, no forced Lua ACK.
"""
import argparse
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREVIOUS=ROOT/"research/b24_unified/g106_visual_repair/g106_pack_stark_sky_alpha_light_feedback_beta.py"
TITLE_ID="IM2G16101"

REQUIRED_FLAGS=(
 "B24_G68_CITY_BACKEND",
 "B24_G71_ALPHA_PASSES",
 "B24_G73_REAL_SKY",
 "B24_G106_SOURCE_FLY_ATTACK_MARKV",
 "B24_G108_SOURCE_VISUAL_WALLS",
 "B24_G134_LIMIT_LONG_FRAME_DISPLACEMENT",  # patch marker is in C source
 "B24_G136_SOURCE_B14_WORLD_BOUNDS",
 "B24_G156_CONTINUOUS_TRI_CONTACT",
 "B24_G159_ROAD_FLOOR_CANDIDATE",
 "B24_G160_ROAD_SPATIAL_INDEX",
 "B24_G85_NATIVE_MARKV_629",
 "B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP",
)

def pack(work,build,out):
    cm=(work/"CMakeLists.txt").read_text()
    main=(work/"src/main.c").read_text()
    src=(work/"b24/b24_unified/b24_g75_source_capsule.c").read_text()
    road=(work/"b24/b24_unified/b24_g159_real_source_road.c").read_text()
    csr=(work/"b24/b24_unified/b24_g160_original_road_spatial.c").read_text()
    for flag in REQUIRED_FLAGS:
        present=flag in (src if flag=="B24_G134_LIMIT_LONG_FRAME_DISPLACEMENT" else cm)
        if not present:raise ValueError("G161 source missing "+flag)
    if main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
        raise ValueError("Not ONE original B14 player game")
    if main.count("b24_unified_tick(&b24_game,&b24_obs);")!=1:
        raise ValueError("Not ONE B24 game tick")
    if "b24_g160_index_query" not in road or "b24_g160_index_build" not in road:
        raise ValueError("This is not G160 accelerated source road runtime")
    if "b24_g160_index_query" not in csr:raise ValueError("G160 original source index module missing")
    cache=(build/"CMakeCache.txt").read_text()
    for flag in REQUIRED_FLAGS:
        if flag=="B24_G134_LIMIT_LONG_FRAME_DISPLACEMENT":continue
        if (flag+":BOOL=ON") not in cache:
            raise ValueError("G161 actual VitaSDK build flag must be ON "+flag)
    if "IM2G16101" not in cm or "IM2G10601" in cm:
        raise ValueError("G161 title ID missing or accidentally reused G106")
    spec=importlib.util.spec_from_file_location("g106_source_owner_packaging",PREVIOUS)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # This only configures inherited validation and SFO expectation;
    # it NEVER reuses the G106 executable or original APK/VPK bytes.
    mod.TITLE_ID=TITLE_ID
    mod.main(work,build,out)
    manifest_path=out.with_suffix(".qa.json")
    info=json.loads(manifest_path.read_text())
    if info.get("title_id")!=TITLE_ID or not info.get("vpk_generated_by_real_vita_CMake"):
        raise ValueError("Signed Vita QA manifest title or source false")
    with zipfile.ZipFile(out) as z:
        if z.testzip() is not None:raise ValueError("G161 VPK ZIP CRC failed")
        files=set(z.namelist())
        must={"eboot.bin","sce_sys/param.sfo",
              "assets/G66_city.g66m","assets/G66_original_collision.g66c",
              "assets/G73_original_sky_mesh.g73m",
              "assets/G73_original_sky_tex_00.g66t",
              "assets/G73_original_sky_tex_01.g66t"}
        if not must.issubset(files):raise ValueError("G161 original game material not packaged")
        if len([p for p in files if p.startswith("assets/G66_city_tex_")
                and p.endswith(".g66t")])!=31:raise ValueError("Not 31 real 2010 city atlases")
        if len([p for p in files if p.startswith("animations/suitcase_ironman_")
                and p.endswith(".im2v")])!=248:raise ValueError("Not 248 real source Mark V clips")
        if mod.psf(z).get("TITLE_ID")!=TITLE_ID:raise ValueError("G161 actual signed title ID wrong")
    info.update({
      "kind":"G161 one deliberate user-authorized Iron Man 2 iOS->PSVita first-world device QA, NOT playable completed original mission",
      "source_branch":"feature/b24-unified-gameplay",
      "G161_unique_title_id_prevents_replacing_older_G106_G104":True,
      "G161_vita_elf_compiled_source_flags":list(REQUIRED_FLAGS),
      "G160_real_source_road_spatial_CSR_compiled":True,
      "G159_real_original_c1l1_road_material_surface_experimental":True,
      "G159_native_iOS_road_collision_solidness_proven":False,
      "G156_real_source_wall_continuous_contact_compiled":True,
      "G134_long_frame_displacement_source_guard_compiled":True,
      "G106_real_original_sky_and_alpha_compiled":True,
      "G106_MarkV_stage2_rush_source_attack_candidate_compiled":True,
      "hardware_gameplay_validation_passed":False,
      "hardware_sky_alpha_validation_passed":False,
      "hardware_collision_validation_passed":False,
      "hardware_fps_measured":False,
      "authentic_Mission000_QTE_1456_accepted":False,
      "first_mission_finish_proven":False,
      "source_qa": "G160 original 2010 source 62065 old-vs-CSR same supports; full G75 host; G156 C11 wall; native PS Vita ARM build, no physical Vita claim",
      "known_TEST_WARNINGS":
        "Original 2010 Mission000 QTE1456 script PC6 is source BLOCKED. G159 road solidity is experimental. Device visual/movement/audio/fps not tested. It must NOT be labelled a complete playable first mission."
    })
    manifest_path.write_text(json.dumps(info,indent=2,ensure_ascii=False)+"\n")
    print("G161 USER AUTHORIZED FIRST WORLD VITA DEVICE TEST VPK",out,
          "size",out.stat().st_size,
          "sha256",info["vpk_sha256"],"TITLE_ID",TITLE_ID)
    return info

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--work",type=Path,required=True)
    p.add_argument("--build",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    pack(args.work,args.build,args.out)

if __name__=="__main__":main()
