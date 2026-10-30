#!/usr/bin/env python3
"""Validate a translation table (cues.tsv / respostas.tsv / marcadores.tsv).

Checks the rules of SWOW-IT/traducao/GUIA.md: columns, non-empty `it`, valid
status, unique key, case pattern preserved. Exits 1 on any error; case-pattern
mismatches are warnings only (proper nouns can differ, with a note).
"""
import csv
import sys

COLUMNS = ["en", "it", "status", "nota"]
STATUS = {"ok", "ambiguo", "sem_equivalente", "nome_proprio", "erro_digitacao"}


def case_pattern(s):
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return "none"
    if all(c.isupper() for c in letters) and len(letters) > 1:
        return "UPPER"
    return "Title" if letters[0].isupper() else "lower"


def main(path):
    errors, warnings, seen = [], [], set()
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        header = next(reader, None)
        if header != COLUMNS:
            print(f"ERRO cabecalho {header} != {COLUMNS}")
            return 1
        n = 0
        for i, row in enumerate(reader, 2):
            n += 1
            if len(row) != 4:
                errors.append(f"linha {i}: {len(row)} colunas")
                continue
            en, it, status, _ = row
            if not it.strip():
                errors.append(f"linha {i}: it vazio ({en})")
            if status not in STATUS and status != "ok":
                errors.append(f"linha {i}: status invalido '{status}' ({en})")
            if en in seen:
                errors.append(f"linha {i}: chave duplicada ({en})")
            seen.add(en)
            if en != en.strip() or it != it.strip():
                errors.append(f"linha {i}: espaco nas pontas ({en})")
            pe, pi = case_pattern(en), case_pattern(it)
            if pe != "none" and pi != "none" and pe != pi:
                warnings.append(f"linha {i}: caixa {pe} -> {pi} ({en} -> {it})")
    print(f"{path}: {n} linhas, {len(errors)} erros, {len(warnings)} avisos de caixa")
    for e in errors[:20]:
        print("  ERRO", e)
    for w in warnings[:10]:
        print("  aviso", w)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
