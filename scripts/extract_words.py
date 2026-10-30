#!/usr/bin/env python3
"""Extract the SWOW-EN vocabulary (cues and responses) from complete + R100.

Reads SWOW-EN18/ (read-only) and writes SWOW-IT/traducao/vocab_cues.tsv,
vocab_respostas.tsv and cues_fora_derivados.tsv, then prints the counts used
by the plan (Task 1.1 of PIANO-traducao-swow-en-para-italiano).
"""
import csv
import collections
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN = os.path.join(ROOT, "SWOW-EN18")
OUT = os.path.join(ROOT, "SWOW-IT", "traducao")

COMPLETE = os.path.join(EN, "SWOW-EN.complete.20180827.csv")
R100 = os.path.join(EN, "SWOW-EN.R100.20180827.csv")
CUESTATS_R123 = os.path.join(EN, "cueStats.SWOW-EN.R123.20180827.csv")
RESPONSESTATS = os.path.join(EN, "responseStats.SWOW-EN.20180827.csv")

# markers that are not words (complete uses text, R100 uses NA)
MARKERS = {"Unknown word", "No more responses", "NA", ""}
SECTION_ORDER = ["seed", "set1", "set2", "set3", "set4", "set5", "set6"]


def main():
    os.makedirs(OUT, exist_ok=True)

    cue_freq_c = collections.Counter()
    cue_sections = collections.defaultdict(set)
    resp_freq_c = collections.Counter()
    for r in csv.DictReader(open(COMPLETE, encoding="utf-8")):
        cue_freq_c[r["cue"]] += 1
        cue_sections[r["cue"]].add(r["section"])
        for k in ("R1", "R2", "R3"):
            if r[k] not in MARKERS:
                resp_freq_c[r[k]] += 1

    cue_freq_r = collections.Counter()
    resp_freq_r = collections.Counter()
    for r in csv.DictReader(open(R100, encoding="utf-8")):
        cue_freq_r[r["cue"]] += 1
        for k in ("R1", "R2", "R3"):
            if r[k] not in MARKERS:
                resp_freq_r[r[k]] += 1

    deriv_cues = {r["cue"] for r in csv.DictReader(open(CUESTATS_R123, encoding="utf-8"))}
    deriv_resp = {r["response"] for r in csv.DictReader(open(RESPONSESTATS, encoding="utf-8"))}

    all_cues = set(cue_freq_c) | set(cue_freq_r)
    all_resp = set(resp_freq_c) | set(resp_freq_r)

    def case_groups(words):
        g = collections.defaultdict(list)
        for w in words:
            g[w.lower()].append(w)
        return {k: v for k, v in g.items() if len(v) > 1}

    cue_case = case_groups(all_cues)
    resp_case = case_groups(all_resp)

    # first section (in experiment order) where each cue appears
    def first_section(cue):
        secs = cue_sections.get(cue)
        if not secs:
            return "(so R100)"
        return min(secs, key=lambda s: SECTION_ORDER.index(s) if s in SECTION_ORDER else 99)

    with open(os.path.join(OUT, "vocab_cues.tsv"), "w", encoding="utf-8") as f:
        f.write("cue\tfreq_complete\tfreq_r100\tfirst_section\tin_derivados\tcase_pair\n")
        for c in sorted(all_cues, key=lambda x: (SECTION_ORDER.index(first_section(x)) if first_section(x) in SECTION_ORDER else 99, x)):
            f.write(f"{c}\t{cue_freq_c.get(c, 0)}\t{cue_freq_r.get(c, 0)}\t{first_section(c)}\t{int(c in deriv_cues)}\t{int(c.lower() in cue_case)}\n")

    # ranking: responses that are not cues, by frequency in complete
    non_cue = [w for w in all_resp if w not in all_cues]
    non_cue.sort(key=lambda w: (-resp_freq_c.get(w, 0), w))
    rank = {w: i + 1 for i, w in enumerate(non_cue)}
    with open(os.path.join(OUT, "vocab_respostas.tsv"), "w", encoding="utf-8") as f:
        f.write("response\tfreq_complete\tfreq_r100\trank_nao_cue\tis_cue\tin_derivados\tcase_pair\n")
        for w in sorted(all_resp, key=lambda x: (rank.get(x, 0), x)):
            f.write(f"{w}\t{resp_freq_c.get(w, 0)}\t{resp_freq_r.get(w, 0)}\t{rank.get(w, '')}\t{int(w in all_cues)}\t{int(w in deriv_resp)}\t{int(w.lower() in resp_case)}\n")

    outside = sorted(all_cues - deriv_cues)
    with open(os.path.join(OUT, "cues_fora_derivados.tsv"), "w", encoding="utf-8") as f:
        f.write("cue\tfreq_complete\tfreq_r100\n")
        for c in outside:
            f.write(f"{c}\t{cue_freq_c.get(c, 0)}\t{cue_freq_r.get(c, 0)}\n")

    # report
    print("cues: complete", len(cue_freq_c), "| R100", len(cue_freq_r), "| uniao", len(all_cues),
          "| derivados", len(deriv_cues))
    print("cues so no R100", len(set(cue_freq_r) - set(cue_freq_c)), "| so no complete", len(set(cue_freq_c) - set(cue_freq_r)))
    print("cues fora dos derivados (uniao - derivados)", len(outside),
          "| deles no complete", sum(1 for c in outside if c in cue_freq_c), "| no R100", sum(1 for c in outside if c in cue_freq_r))
    print("pares de caixa em cues:", len(cue_case), "| cues unicos em minuscula", len({c.lower() for c in all_cues}))
    print("respostas: complete", len(resp_freq_c), "| R100", len(resp_freq_r), "| uniao", len(all_resp),
          "| derivados", len(deriv_resp), "| so no R100", len(set(resp_freq_r) - set(resp_freq_c)))
    print("respostas que sao cue", sum(1 for w in all_resp if w in all_cues), "| nao-cue", len(non_cue),
          "| grupos de caixa em respostas", len(resp_case))
    sec_new = collections.Counter(first_section(c) for c in all_cues)
    print("cues novos por secao (1a aparicao):", {s: sec_new.get(s, 0) for s in SECTION_ORDER + ["(so R100)"]},
          "soma", sum(sec_new.values()))
    tot = sum(resp_freq_c[w] for w in non_cue)
    print("tokens de respostas nao-cue (complete)", tot, "| tokens totais", sum(resp_freq_c.values()))
    acc = 0
    marks = {1000, 5000, 12000, 20000, 40000, 60000}
    for i, w in enumerate(non_cue, 1):
        acc += resp_freq_c[w]
        if i in marks:
            print(f"  top {i}: {100*acc/tot:.1f}% dos tokens nao-cue")
    print("cauda alem do rank 40000:", len(non_cue) - 40000)
    freq1 = sum(1 for w in non_cue if resp_freq_c[w] == 1)
    print("nao-cue com freq 1:", freq1, f"({100*freq1/len(non_cue):.1f}%)")


if __name__ == "__main__":
    sys.exit(main())
