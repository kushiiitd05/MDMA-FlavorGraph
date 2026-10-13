#!/usr/bin/env bash
# Assignment 2 — full reproducible pipeline.
# Reads the Assignment-1 deliverable (../A1/outputs/Q1/Q1c_recipe_ingredient.csv)
# and regenerates every Q1/Q2/Q3 output from scratch.
set -euo pipefail
PY=./.venv/bin/python

echo "== 0. corpus check"
$PY src/corpus.py

echo "== 1. Q1  frequent item set mining (Apriori, implemented from scratch)"
$PY src/fism.py

echo "== 2. Q2 + Q3  randomised controls"
$PY src/random_controls.py

echo "== 3. Q2 + Q3  figures"
$PY src/plots.py

echo "== 4. backup with checksums"
$PY src/package.py

echo "== 5. validation gate"
$PY src/validate.py
