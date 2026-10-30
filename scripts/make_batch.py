#!/usr/bin/env python3
"""Build translation batch inputs: each cue with its top-10 responses.

Usage: make_batch.py <section> <out_dir> [size]
Takes cues whose first_section is <section>, skips those already translated
(piloto_cues_v2.tsv, cues.tsv), and writes lote_NN.txt files ("cue | r1, r2, ...").
"""
import csv
import os
import sys
from collections import defaultdict

T = "SWOW-IT/traducao/"
section, out_dir = sys.argv[1], sys.argv[2]
size = int(sys.argv[3]) if len(sys.argv) > 3 else 260

done = set()
for name in ("piloto_cues_v2.tsv", "cues.tsv"):
    if os.path.exists(T + name):
        with open(T + name, encoding="utf-8", newline="") as f:
            done |= {r[0] for r in csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}

with open(T + "vocab_cues.tsv", encoding="utf-8", newline="") as f:
    cues = [r["cue"] for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
            if r["first_section"] == section and r["cue"] not in done]

want, top = set(cues), defaultdict(list)
with open("SWOW-EN18/strength.SWOW-EN.R123.20180827.csv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
        if r["cue"] in want and len(top[r["cue"]]) < 10:
            top[r["cue"]].append(r["response"])  # file is sorted by count desc within cue

os.makedirs(out_dir, exist_ok=True)
for i in range(0, len(cues), size):
    with open(f"{out_dir}/lote_{i // size + 1:02d}.txt", "w", encoding="utf-8") as o:
        for c in cues[i:i + size]:
            o.write(f"{c} | {', '.join(top[c])}\n")
print(len(cues), "cues,", (len(cues) + size - 1) // size, "lotes")
