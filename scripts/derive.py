#!/usr/bin/env python3
"""Recompute the SWOW derived files (strength, cueStats, responseStats) from R100.

Task 1.3 of PIANO-traducao-swow-en-para-italiano: run on the English R100 and
compare with the original derived files; 0 divergent rows is the gate for the
Italian assembly (Story 6). The functions take rows already in memory so the
same code can run on the Italian R100 later.

Definitions (checked against the original files):
  strength N     = non-NA responses of the cue (R1: 97 for "a"; R123: 270)
  cueStats N     = participants (R1) or 3 x participants (R123)
  unknown        = participants with R1 = NA
  coverage       = % of non-NA responses that are also cues, where "cue" means
                   a member of that same file's cue list
  H              = natural-log entropy of the response distribution
  xR2, xR3       = NA(R2) - unknown and NA(R3) - NA(R2); can be negative when
                   R100 rows are shifted ([NA, x, y])
  Types          = number of distinct cues where the response was given

Cue lists are NOT mechanical: the original files cover different cues
(strength 12,217, cueStats.R123 12,216, cueStats.R1 12,176). The lists are
taken from the original files and must be carried to the Italian version.
"""
import argparse
import collections
import csv
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN = os.path.join(ROOT, "SWOW-EN18")
R100 = os.path.join(EN, "SWOW-EN.R100.20180827.csv")
ORIG = {
    "strength.R1": os.path.join(EN, "strength.SWOW-EN.R1.20180827.csv"),
    "strength.R123": os.path.join(EN, "strength.SWOW-EN.R123.20180827.csv"),
    "cueStats.R1": os.path.join(EN, "cueStats.SWOW-EN.R1.20180827.csv"),
    "cueStats.R123": os.path.join(EN, "cueStats.SWOW-EN.R123.20180827.csv"),
    "responseStats": os.path.join(EN, "responseStats.SWOW-EN.20180827.csv"),
}
NA = "NA"
# the original strength.R123 stores Strength rounded to 7 decimals in many rows
STRENGTH_TOL = 1e-7


def load_rows(path):
    """Return {cue: [(R1, R2, R3), ...]} from an R100-shaped file."""
    d = collections.defaultdict(list)
    for r in csv.DictReader(open(path, encoding="utf-8")):
        d[r["cue"]].append((r["R1"], r["R2"], r["R3"]))
    return d


def entropy(counter):
    n = sum(counter.values())
    return -sum(v / n * math.log(v / n) for v in counter.values()) if n else 0.0


def strength_tables(rows_by_cue, cues):
    t1, t123 = {}, {}
    for cue in cues:
        rows = rows_by_cue[cue]
        c1 = collections.Counter(r[0] for r in rows if r[0] != NA)
        c123 = collections.Counter(x for r in rows for x in r if x != NA)
        n1, n123 = sum(c1.values()), sum(c123.values())
        for w, v in c1.items():
            t1[(cue, w)] = (v, n1, v / n1)
        for w, v in c123.items():
            t123[(cue, w)] = (v, n123, v / n123)
    return t1, t123


def cuestats_tables(rows_by_cue, cues, cue_list_name):
    """cueStats for the given cue list; coverage counts that same list as cues."""
    cue_set = set(cues)
    t = {}
    for cue in cues:
        rows = rows_by_cue[cue]
        c1 = collections.Counter(r[0] for r in rows if r[0] != NA)
        c123 = collections.Counter(x for r in rows for x in r if x != NA)
        n1, n123 = sum(c1.values()), sum(c123.values())
        unknown = sum(1 for r in rows if r[0] == NA)
        na2 = sum(1 for r in rows if r[1] == NA)
        na3 = sum(1 for r in rows if r[2] == NA)
        cov = lambda c, n: 100.0 * sum(v for w, v in c.items() if w in cue_set) / n if n else float("nan")
        if cue_list_name == "R1":
            t[cue] = (cov(c1, n1), entropy(c1), unknown, len(rows))
        else:
            t[cue] = (cov(c123, n123), entropy(c123), unknown, na2 - unknown, na3 - na2, 3 * len(rows))
    return t


def responsestats_table(rows_by_cue, cues):
    freq1, freq123 = collections.Counter(), collections.Counter()
    types1, types123 = collections.Counter(), collections.Counter()
    for cue in cues:
        rows = rows_by_cue[cue]
        c1 = collections.Counter(r[0] for r in rows if r[0] != NA)
        c123 = collections.Counter(x for r in rows for x in r if x != NA)
        for w, v in c1.items():
            freq1[w] += v
            types1[w] += 1
        for w, v in c123.items():
            freq123[w] += v
            types123[w] += 1
    return {w: (freq1.get(w, 0), types1.get(w, 0), freq123[w], types123[w]) for w in freq123}


def _int(x):
    return 0 if x == NA else int(x)


def read_original(name):
    """Return the original table in the same shape the derive functions use."""
    path = ORIG[name]
    t = {}
    if name.startswith("strength"):
        for i, line in enumerate(open(path, encoding="utf-8")):
            if i:
                c, w, v, n, s = line.rstrip("\n").split("\t")
                t[(c, w)] = (int(v), int(n), float(s))
    elif name == "cueStats.R1":
        for r in csv.DictReader(open(path, encoding="utf-8")):
            t[r["cue"]] = (float(r["coverage"]), float(r["H"]), int(r["unknown"]), int(r["N"]))
    elif name == "cueStats.R123":
        for r in csv.DictReader(open(path, encoding="utf-8")):
            t[r["cue"]] = (float(r["coverage"]), float(r["H"]), int(r["unknown"]), int(r["xR2"]), int(r["xR3"]), int(r["N"]))
    else:
        for r in csv.DictReader(open(path, encoding="utf-8")):
            t[r["response"]] = (_int(r["Freq.R1"]), _int(r["Types.R1"]), _int(r["Freq.R123"]), _int(r["Types.R123"]))
    return t


def same(a, b, tol):
    return len(a) == len(b) and all(
        (x == y) if isinstance(x, int) and isinstance(y, int) else math.isclose(x, y, rel_tol=1e-9, abs_tol=tol)
        for x, y in zip(a, b)
    )


def compare(orig, comp, tol):
    mism = [k for k in orig if k in comp and not same(orig[k], comp[k], tol)]
    missing = [k for k in orig if k not in comp]
    extra = [k for k in comp if k not in orig]
    return mism, missing, extra


def cue_lists(originals):
    """The three original cue lists (see module docstring)."""
    s = {k[0] for k in originals["strength.R123"]}
    return {"strength": s, "R1": set(originals["cueStats.R1"]), "R123": set(originals["cueStats.R123"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--responsestats-cues", choices=["strength", "R123", "R1"], default="strength",
                    help="which cue list feeds responseStats")
    args = ap.parse_args()

    rows = load_rows(R100)
    orig = {n: read_original(n) for n in ORIG}
    lists = cue_lists(orig)
    print("listas de cues dos originais:", {k: len(v) for k, v in lists.items()})

    s1, s123 = strength_tables(rows, sorted(lists["strength"]))
    out = {
        "strength.R1": s1,
        "strength.R123": s123,
        "cueStats.R1": cuestats_tables(rows, sorted(lists["R1"]), "R1"),
        "cueStats.R123": cuestats_tables(rows, sorted(lists["R123"]), "R123"),
        "responseStats": responsestats_table(rows, sorted(lists[args.responsestats_cues])),
    }

    total = 0
    for name in ORIG:
        tol = STRENGTH_TOL if name.startswith("strength") else 1e-9
        mism, missing, extra = compare(orig[name], out[name], tol)
        total += len(mism) + len(missing) + len(extra)
        print(f"{name:14s} original={len(orig[name]):8d} recalculado={len(out[name]):8d} "
              f"valores_diferentes={len(mism):6d} so_no_original={len(missing):6d} so_no_recalculado={len(extra):6d}")
        for label, lst in (("valores", mism), ("so_original", missing), ("so_recalc", extra)):
            if lst:
                print("   ", label, "ex.:", lst[:3])
    print("DIVERGENCIAS TOTAIS:", total)
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
