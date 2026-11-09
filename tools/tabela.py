#!/usr/bin/env python3
"""Generuje pelna tablice przejsc / wzbudzen przerzutnikow D (Markdown + CSV)."""
import sys

out_md = sys.argv[1] if len(sys.argv) > 1 else "tabela_przejsc.md"
out_csv = out_md.rsplit(".", 1)[0] + ".csv"


def nxt(q, x):
    if x:
        return 31
    return 0 if q >= 30 else q + 1


def b5(v):
    return format(v, "05b")


rows = []
for x in (0, 1):
    for q in range(32):
        rows.append((x, q, nxt(q, x)))

md = ["# Tablica przejść i wzbudzeń przerzutników D", "",
      "Dla przerzutnika D wzbudzenie jest równe stanowi następnemu: D = Q(t+1).", "",
      "| x | Q (dec) | Q4 Q3 Q2 Q1 Q0 | Q(t+1) (dec) | D4 D3 D2 D1 D0 |",
      "|:-:|:-------:|:--------------:|:------------:|:--------------:|"]
for x, q, n in rows:
    md.append(f"| {x} | {q} | {' '.join(b5(q))} | {n} | {' '.join(b5(n))} |")

with open(out_md, "w") as f:
    f.write("\n".join(md) + "\n")

with open(out_csv, "w") as f:
    f.write("x;Q;Q4;Q3;Q2;Q1;Q0;Qnext;D4;D3;D2;D1;D0\n")
    for x, q, n in rows:
        f.write(";".join(map(str, [x, q, *b5(q), n, *b5(n)])) + "\n")
