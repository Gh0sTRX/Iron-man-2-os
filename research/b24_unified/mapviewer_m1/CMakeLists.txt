cmake_minimum_required(VERSION 3.15)
if(NOT DEFINED CMAKE_TOOLCHAIN_FILE AND DEFINED ENV{VITASDK})
  set(CMAKE_TOOLCHAIN_FILE "$ENV{VITASDK}/share/vita.toolchain.cmake" CACHE FILEPATH "PS Vita toolchain")
endif()
project(IronMan2_C1L1_Map_Viewer_M1 C)
set(CMAKE_C_STANDARD 11)
set(VITA_TITLEID "IM2M10001")
set(VITA_APP_NAME "Iron Man 2 - C1L1 Map Viewer")
set(VITA_VERSION "01.00")
include("$ENV{VITASDK}/share/vita.cmake" REQUIRED)
set(SRC_DIR ${CMAKE_CURRENT_LIST_DIR}/..)
add_executable(im2_mapviewer
  mapviewer.c
  ${SRC_DIR}/b24_c1_gpu_mesh.c
  ${SRC_DIR}/b24_c1_gpu_vitagl.c
  ${SRC_DIR}/b24_c1_gpu_uv.c
  ${SRC_DIR}/b24_c1_material_source.c
  ${SRC_DIR}/b24_c1_material_batches.c
  ${SRC_DIR}/b24_c1_2010_diffuse_bank.c
  ${SRC_DIR}/b24_gpu_c1_2010_diffuse_upload.c
  ${SRC_DIR}/b24_gpu_c1_2010_textured_material_vitagl.c
  ${SRC_DIR}/b24_gpu_camera.c)
target_include_directories(im2_mapviewer PRIVATE ${SRC_DIR})
target_compile_options(im2_mapviewer PRIVATE -Wall -Wextra -O2)
set(VITA_LIBRARIES)
foreach(lib
   vitaGL vitashark SceShaccCgExt stdc++ mathneon m
   taihen_stub
   SceAppMgr_stub SceAppUtil_stub SceAudio_stub
   SceAudioIn_stub SceAudioOut_stub SceCtrl_stub
   SceCommonDialog_stub SceDisplay_stub SceGxm_stub
   SceShaccCg_stub SceSysmodule_stub ScePower_stub
   SceTouch_stub SceVshBridge_stub SceKernelDmacMgr_stub
   SceMotion_stub SceIme_stub SceMsgDialog_stub SceHid_stub
   SceSharedFb_stub SceGxmInternalForVsh_stub SceLibKernel_stub
   SceLibcBridge_stub SceFios2_stub SceDisplayUser_stub
)
  if(EXISTS "$ENV{VITASDK}/arm-vita-eabi/lib/lib${lib}.a")
    list(APPEND VITA_LIBRARIES ${lib})
  elseif(lib STREQUAL "vitaGL" OR lib STREQUAL "vitashark" OR
         lib STREQUAL "stdc++" OR lib STREQUAL "mathneon" OR lib STREQUAL "m")
    message(FATAL_ERROR "Required Vita SDK lib missing ${lib}")
  endif()
endforeach()
target_link_libraries(im2_mapviewer "-Wl,--start-group" ${VITA_LIBRARIES} "-Wl,--end-group")
vita_create_self(eboot.bin im2_mapviewer UNSAFE)
file(GLOB SOURCE_MAPS "${CMAKE_CURRENT_LIST_DIR}/maps/*")
set(PACKAGE_MAP_FILES)
foreach(asset ${SOURCE_MAPS})
  get_filename_component(filename "${asset}" NAME)
  list(APPEND PACKAGE_MAP_FILES "${asset}" "maps/${filename}")
endforeach()
list(LENGTH SOURCE_MAPS ASSET_COUNT)
if(ASSET_COUNT LESS 8)
  message(FATAL_ERROR "Real original C1L1 map file packaging incomplete: ${ASSET_COUNT}")
endif()
vita_create_vpk(IronMan2_C1L1_MapViewer_M1.vpk ${VITA_TITLEID} eboot.bin
  VERSION ${VITA_VERSION}
  NAME ${VITA_APP_NAME}
  FILE ${PACKAGE_MAP_FILES})
