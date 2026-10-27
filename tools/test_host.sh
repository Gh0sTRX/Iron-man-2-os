#!/bin/bash
set -euo pipefail
im2_repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$im2_repo"
im2_cmake=${IM2_CMAKE:-cmake}
im2_ctest=${IM2_CTEST:-ctest}
im2_build=${IM2_HOST_BUILD:-build-host}
im2_flags=(-DIM2_BUILD_VITA=OFF -DCMAKE_BUILD_TYPE=Debug)
if [[ -n ${IM2_ASSET_ROOT:-} ]]; then
  im2_flags+=("-DIM2_ASSET_ROOT=$IM2_ASSET_ROOT")
else
  im2_flags+=(-DIM2_ASSET_ROOT=)
fi
im2_flags+=("-DIM2_SANITIZERS=${IM2_SANITIZERS:-OFF}")
"$im2_cmake" -S . -B "$im2_build" "${im2_flags[@]}"
"$im2_cmake" --build "$im2_build" --parallel 4
"$im2_ctest" --test-dir "$im2_build" --output-on-failure
