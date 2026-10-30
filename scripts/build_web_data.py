#!/usr/bin/env python3
"""Build web/data.it.json: Italian association graph for the web explorer.

Only cues already translated in SWOW-IT/traducao/cues.tsv are nodes; a response
is kept only if its English string is also a translated cue (responses are not
translated yet). Collisions (several English words -> same Italian word) sum
counts and N. Output: {cue_it: [N, [[resp_it, strength], ...top 20]]}.
"""
import csv
import json
from collections import defaultdict

TOP = 20
with open("SWOW-IT/traducao/cues.tsv", encoding="utf-8", newline="") as f:
    en2it = {r["en"]: r["it"] for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}

counts = defaultdict(lambda: defaultdict(int))  # cue_it -> resp_it -> count
n_by_cue = defaultdict(int)
seen_cue = set()
with open("SWOW-EN18/strength.SWOW-EN.R123.20180827.csv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
        cue = en2it.get(r["cue"])
        if cue is None:
            continue
        if r["cue"] not in seen_cue:  # N is repeated on every row of the cue
            seen_cue.add(r["cue"])
            n_by_cue[cue] += int(r["N"])
        resp = en2it.get(r["response"])
        if resp is not None and resp != cue:
            counts[cue][resp] += int(r["R123"])

out = {}
for cue, n in n_by_cue.items():
    top = sorted(counts[cue].items(), key=lambda kv: (-kv[1], kv[0]))[:TOP]
    out[cue] = [n, [[w, round(c / n, 4)] for w, c in top]]
with open("web/data.it.json", "w", encoding="utf-8") as o:
    json.dump(out, o, ensure_ascii=False, separators=(",", ":"))
print(len(out), "cues,", sum(len(v[1]) for v in out.values()), "ligações")
