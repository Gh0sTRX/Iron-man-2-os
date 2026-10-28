cmake_minimum_required(VERSION 3.21)
project(IronMan2Vita C)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(_vita_default OFF)
if(DEFINED ENV{VITASDK})
  set(_vita_default ON)
endif()
option(IM2_BUILD_VITA "Build the full Vita game ELF (never SELF/VPK)" ${_vita_default})
option(IM2_FRAME_DIAGNOSTICS "Bounded frame/dt/CPU submission CSV" ON)
option(IM2_SANITIZERS "Host AddressSanitizer and UndefinedBehaviorSanitizer" OFF)
set(IM2_ASSET_ROOT "" CACHE PATH "External locally authorized runtime assets for integration tests")
set(IM2_MODULE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src/b24/b24_unified")
set(IM2_INCLUDE_DIRS src src/b24/b19/host_gameplay src/b24/b21_controls
  src/b24/b22_hud src/b24/b23_missile_lock src/b24/b22_flight src/b24/b22_camera
  src/b24/b22_4_6 src/b24/b24_unified src/b24/b18_gpu_probe)
include(cmake/VitaFeatures.cmake)

if(IM2_BUILD_VITA)
  if(NOT DEFINED ENV{VITASDK} OR NOT CMAKE_C_COMPILER MATCHES "arm-vita-eabi")
    message(FATAL_ERROR "Use the pinned VitaSDK toolchain; see BUILDING.md")
  endif()
  include(cmake/VitaSources.cmake)
  add_executable(im2_beta ${IM2_VITA_SOURCES}
    src/b24/b24_unified/im2_original_tables.c src/b24/b24_unified/im2_frame_trace.c
    src/b24/b24_unified/im2_audio_catalog.c)
  target_include_directories(im2_beta PRIVATE ${IM2_INCLUDE_DIRS})
  target_compile_definitions(im2_beta PRIVATE ${IM2_VITA_DEFINITIONS})
  if(IM2_FRAME_DIAGNOSTICS)
    target_compile_definitions(im2_beta PRIVATE IM2_FRAME_DIAGNOSTICS=1 B24_GPU_PROFILE_LOG=1)
  endif()
  target_link_libraries(im2_beta "-Wl,--start-group"
    SDL2 vitaGL vitashark SceShaccCgExt stdc++ mathneon m taihen_stub
    SceAppMgr_stub SceAppUtil_stub SceAudio_stub SceAudioIn_stub SceCtrl_stub
    SceCommonDialog_stub SceDisplay_stub SceGxm_stub SceShaccCg_stub SceSysmodule_stub
    ScePower_stub SceTouch_stub SceVshBridge_stub SceKernelDmacMgr_stub SceMotion_stub
    SceIme_stub SceHid_stub SceLibKernel_stub SceFios2_stub "-Wl,--end-group")
else()
  include(CTest)
  if(IM2_SANITIZERS)
    add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address,undefined)
  endif()
  add_compile_options(-Wall -Wextra -Werror -pedantic)
  # Keep assertions enabled even when someone selects a Release host build.
  add_compile_options(-UNDEBUG)
  add_library(im2_world STATIC src/b14_world.c
    src/b24/b24_unified/b24_g75_source_capsule.c
    src/b24/b24_unified/b24_g108_visible_original_wall_grid.c
    src/b24/b24_unified/b24_g159_real_source_road.c
    src/b24/b24_unified/b24_g160_original_road_spatial.c
    src/b24/b24_unified/b24_gpu_g68_collision.c
    src/b24/b24_unified/b24_c1_original_collision.c)
  target_include_directories(im2_world PUBLIC ${IM2_INCLUDE_DIRS})
  target_compile_definitions(im2_world PUBLIC B24_G75_SOURCE_CAPSULE=1
    B24_G108_SOURCE_VISUAL_WALLS=1 B24_G159_ROAD_FLOOR_CANDIDATE=1
    B24_G160_ROAD_SPATIAL_INDEX=1 B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL=1)
  target_link_libraries(im2_world PUBLIC m)
  add_library(im2_tables STATIC src/b24/b24_unified/im2_original_tables.c
    src/b24/b24_unified/b24_g137_source_mission000_intro.c)
  target_include_directories(im2_tables PUBLIC ${IM2_MODULE_DIR})
  add_library(im2_audio STATIC src/b24/b24_unified/im2_audio_catalog.c
    src/b24/b24_unified/b24_g141_owner_pcm_stream.c)
  target_include_directories(im2_audio PUBLIC ${IM2_MODULE_DIR})
  add_library(im2_trace STATIC src/b24/b24_unified/im2_frame_trace.c
    src/b24/b24_unified/b24_gpu_cpu_profile.c)
  target_include_directories(im2_trace PUBLIC ${IM2_MODULE_DIR})
  target_link_libraries(im2_trace PUBLIC m)
  add_library(im2_controls STATIC
    src/b24/b19/host_gameplay/b19_gameplay_core.c src/b24/b19/host_gameplay/b19_hit_geometry.c
    src/b24/b21_controls/b21_control_lab.c src/b24/b21_controls/b21_hud_canvas.c
    src/b24/b22_hud/b22_visor.c src/b24/b23_missile_lock/b23_missile_lock.c
    src/b24/b22_flight/im2_flight.c src/b24/b22_camera/im2_camera.c
    src/b24/b22_4_6/im2_thruster.c src/b24/b22_4_6/im2_speed_fx.c
    src/b24/b22_4_6/im2_melee_focus.c src/b24/b24_unified/b24_unified.c
    src/b24/b24_unified/b24_camera_recenter.c)
  target_include_directories(im2_controls PUBLIC ${IM2_INCLUDE_DIRS})
  target_link_libraries(im2_controls PUBLIC m)
  add_library(im2_motion STATIC src/b24/b24_unified/b24_original_im2v_stream.c
    src/b24/b24_unified/b24_hover_pose_blend.c src/b24/b24_unified/b24_g8_melee_source_chain.c
    src/b24/b24_unified/b24_g8_live_original_motion.c)
  target_sources(im2_motion PRIVATE
    src/b24/b24_unified/b24_g83_unified_movement_aim.c
    src/b24/b24_unified/b24_g83_authentic_timed_router.c
    src/b24/b24_unified/b24_g82_original_combat_coordinator.c
    src/b24/b24_unified/b24_g76_original_native_damage_math.c
    src/b24/b24_unified/b24_g77_melee_source_radius.c
    src/b24/b24_unified/b24_g169_native_source_unibeam.c
    src/b24/b24_unified/b24_g11_original_unibeam_sequence.c)
  target_include_directories(im2_motion PUBLIC ${IM2_INCLUDE_DIRS})
  target_compile_definitions(im2_motion PUBLIC B24_G85_NATIVE_MARKV_629=1
    B24_G165_WM_SOURCE_DIRECTIONAL_FALLBACK=1 B24_G172_WM_NATIVE_M_GROUND_BANK=1
    B24_G173_AUTHORED_UNIBEAM_POSE_PRIORITY=1)
  target_link_libraries(im2_motion PUBLIC m)
  if(BUILD_TESTING)
    add_subdirectory(tests)
  endif()
endif()
