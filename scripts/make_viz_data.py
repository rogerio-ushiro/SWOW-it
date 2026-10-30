#!/usr/bin/env python3
"""Build viz/data.js: top associations (R123 strength) of every translated cue.

Each cue in SWOW-IT/traducao/cues.tsv gets its top-N responses; `tr` maps the
English words to Italian for every word translated so far (cues only, for now).
"""
import csv
import json
import sys
from collections import defaultdict

TOP = 20
T = "SWOW-IT/traducao/"


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


tr = {r["en"]: r["it"] for r in read_tsv(T + "cues.tsv")}
assoc = defaultdict(list)
for r in read_tsv("SWOW-EN18/strength.SWOW-EN.R123.20180827.csv"):
    c = r["cue"]
    if c in tr and len(assoc[c]) < TOP:  # file is sorted by count desc within cue
        assoc[c].append([r["response"], round(float(r["R123.Strength"]), 4)])

with open("viz/data.js", "w", encoding="utf-8") as o:
    o.write("window.SWOW = " + json.dumps({"tr": tr, "assoc": assoc}, ensure_ascii=False) + ";\n")
print(len(assoc), "cues", file=sys.stderr)
