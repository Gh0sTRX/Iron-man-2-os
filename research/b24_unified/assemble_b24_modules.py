#!/usr/bin/env python3
"""Collect all B19/B21/B22/B22.2-B22.6/B23 source into ONE
B17-derived Vita build tree. Linkage does NOT prove runtime visualization.
Run after B17 overlay reconstruction and before configuring CMake.
"""
from pathlib import Path
import shutil

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "work"
DEST = WORK / "b24"
SOURCE_DIRS = {
    "b19/host_gameplay": "b19/host_gameplay",
    "b21_controls": "b21_controls",
    "b22_hud": "b22_hud",
    "b23_missile_lock": "b23_missile_lock",
    "b22_flight": "b22_flight",
    "b22_camera": "b22_camera",
    "b22_4_6": "b22_4_6",
    "b24_unified": "b24_unified",
    "b18_gpu_probe": "b18_gpu_probe",
}
SOURCES = [
    "b19/host_gameplay/b19_gameplay_core.c",
    "b19/host_gameplay/b19_hit_geometry.c",
    "b21_controls/b21_control_lab.c",
    "b21_controls/b21_hud_canvas.c",
    "b22_hud/b22_visor.c",
    "b23_missile_lock/b23_missile_lock.c",
    "b22_flight/im2_flight.c",
    "b22_camera/im2_camera.c",
    "b22_4_6/im2_thruster.c",
    "b22_4_6/im2_speed_fx.c",
    "b22_4_6/im2_melee_focus.c",
    "b24_unified/b24_unified.c",
    "b18_gpu_probe/b17_input_landing_gate.c",
    "b18_gpu_probe/gpu_floor_mesh.c",
]
def assemble():
    cmake_path = WORK / "CMakeLists.txt"
    if not cmake_path.is_file():
        raise SystemExit("B17 work tree missing. Reconstruct B17 first.")
    for source_dir, target_dir in SOURCE_DIRS.items():
        src = REPO / "research" / source_dir
        dst = DEST / target_dir
        if not src.is_dir():
            raise FileNotFoundError(src)
        dst.mkdir(parents=True, exist_ok=True)
        for file in src.iterdir():
            if file.is_file() and file.suffix in (".c", ".h") and not file.name.startswith(("test_", "demo_")):
                shutil.copy2(file, dst / file.name)
    for source in SOURCES:
        if not (DEST / source).is_file():
            raise RuntimeError("Missing B24 module: " + source)
    cmake = cmake_path.read_text()
    marker = "# B24_UNIFIED_SOURCE_INTEGRATION"
    if marker in cmake:
        raise RuntimeError("B24 assembler already applied")
    rootvar = "$" + "{CMAKE_CURRENT_SOURCE_DIR}"
    block = "\n" + marker + "\n" + "if(TARGET im2_beta)\ntarget_sources(im2_beta PRIVATE\n"
    block += "".join("  " + rootvar + "/b24/" + p + "\n" for p in SOURCES)
    block += ")\ntarget_include_directories(im2_beta PRIVATE\n"
    block += "".join("  " + rootvar + "/b24/" + p + "\n" for p in SOURCE_DIRS.values())
    block += ")\nendif()\n"
    cmake_path.write_text(cmake + block)
    print("B24 unified build target: " + str(len(SOURCES)) + " actual source modules assembled")
    print("Linkage is not gameplay integration; B24 per-frame adapter/GPU must be validated separately.")

if __name__ == "__main__":
    assemble()
