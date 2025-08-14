#!/usr/bin/env bash
# ------------------------------------------------------------
# Usage: ./scripts/build_task.sh <task>/submission
# Compiles preprocess/compute/postprocess inside that folder.
# ------------------------------------------------------------
set -euo pipefail
ROOT="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"
TASK_DIR="$1"
BUILD="$TASK_DIR/build"
NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu || echo 4)

# Set -DCMAKE_PREFIX_PATH to the install directory of OpenFHE
cmake -S "$TASK_DIR" -B "$BUILD" \
      -DCMAKE_PREFIX_PATH="$ROOT/third_party/openfhe"
cd "$TASK_DIR/build"
make -j"$NPROC"
