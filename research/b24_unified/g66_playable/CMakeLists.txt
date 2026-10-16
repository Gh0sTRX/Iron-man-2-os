cmake_minimum_required(VERSION 3.15)
if(NOT DEFINED CMAKE_TOOLCHAIN_FILE AND DEFINED ENV{VITASDK})
  set(CMAKE_TOOLCHAIN_FILE "$ENV{VITASDK}/share/vita.toolchain.cmake" CACHE FILEPATH "PS Vita toolchain")
endif()
project(IronMan2_B24_G65_Playable C)
set(CMAKE_C_STANDARD 11)
set(VITA_TITLEID "IM2G65001")
set(VITA_VERSION "01.00")
include("$ENV{VITASDK}/share/vita.cmake" REQUIRED)
add_executable(g65_playable main.c)
target_compile_options(g65_playable PRIVATE -O2 -Wall -Wextra)
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
  message(FATAL_ERROR "Missing required VitaSDK library ${lib}")
 endif()
endforeach()
target_link_libraries(g65_playable "-Wl,--start-group" ${VITA_LIBRARIES} "-Wl,--end-group")
vita_create_self(eboot.bin g65_playable UNSAFE)
file(GLOB ASSETS "${CMAKE_CURRENT_LIST_DIR}/assets/*")
set(PACKED)
foreach(asset ${ASSETS})
 get_filename_component(file "${asset}" NAME)
 list(APPEND PACKED "${asset}" "assets/${file}")
endforeach()
list(LENGTH ASSETS NUM_ASSETS)
if(NUM_ASSETS LESS 30)
 message(FATAL_ERROR "G65 source assets missing: ${NUM_ASSETS}")
endif()
vita_create_vpk(IronMan2_B24_G65_Playable_Beta.vpk ${VITA_TITLEID} eboot.bin
 VERSION ${VITA_VERSION}
 NAME "Iron Man 2 - B24 G65 Playable Beta"
 FILE ${PACKED})