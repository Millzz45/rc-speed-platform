#!/bin/sh
# Builds the control core as a Mac library for the simulations (rnd/tech/sim/cc.py loads it).
cd "$(dirname "$0")" && mkdir -p build && clang -std=c99 -O2 -Wall -Wextra -Werror -shared -o build/libcc.dylib core/cc_core.c && echo built build/libcc.dylib
