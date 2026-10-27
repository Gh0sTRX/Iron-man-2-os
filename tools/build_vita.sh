#!/bin/bash
set -euo pipefail
im2_repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
im2_sdk=vitasdk/vitasdk@sha256:8227da1b596d981f4513cd9b36bda1e43857f6dae5bcf4312c1cd40167f7d9bb
docker run --rm --network none --user "$(id -u):$(id -g)" \
  -v "$im2_repo:/workspace" -w /workspace "$im2_sdk" sh -c '
    set -eu
    cmake -S . -B build-vita \
      -DCMAKE_TOOLCHAIN_FILE="$VITASDK/share/vita.toolchain.cmake" \
      -DCMAKE_BUILD_TYPE=Release -DIM2_BUILD_VITA=ON
    cmake --build build-vita --target im2_beta --parallel 4
    test -s build-vita/im2_beta
  '
