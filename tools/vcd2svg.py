#!/usr/bin/env python3
"""Rysuje przebiegi czasowe z pliku VCD do SVG (bez zewnetrznych bibliotek).

Przyklad:
  python3 vcd2svg.py build/licznik.vcd out.svg --scope licznik_tb \
      --signals clk rst x y --from 0 --to 200 --px 6
"""
import argparse
import html
import re

UNITS = {"s": 1e9, "ms": 1e6, "us": 1e3, "ns": 1.0, "ps": 1e-3, "fs": 1e-6}


def parse_vcd(path, scope):
    with open(path) as f:
        text = f.read()
    hdr, _, body = text.partition("$enddefinitions")
    body = body.split("$end", 1)[1]

    ts = 1.0
    m = re.search(r"\$timescale\s+(\d+)\s*([a-z]+)\s+\$end", hdr)
    if m:
        ts = int(m.group(1)) * UNITS[m.group(2)]

    ids, widths, changes, stack = {}, {}, {}, []
    for m in re.finditer(r"\$(scope|upscope|var)\b(.*?)\$end", hdr, re.S):
        kind, rest = m.group(1), m.group(2).split()
        if kind == "scope":
            stack.append(rest[1])
        elif kind == "upscope":
            stack.pop()
        elif ".".join(stack) == scope:
            width, vid, name = int(rest[1]), rest[2], rest[3]
            ids[vid] = name
            widths[name] = width
            changes[name] = []

    t = 0.0
    toks = body.split()
    i = 0
    while i < len(toks):
        tk = toks[i]
        if tk[0] == "#":
            t = int(tk[1:]) * ts
        elif tk[0] in "bBrR":
            vid = toks[i + 1]
            i += 1
            if vid in ids:
                changes[ids[vid]].append((t, tk[1:]))
        elif tk[0] in "01xXzZ" and len(tk) > 1:
            if tk[1:] in ids:
                changes[ids[tk[1:]]].append((t, tk[0]))
        i += 1
    return changes, widths, t


def segments(chg, t0, t1):
    """Lista (start, koniec, wartosc) w oknie [t0, t1]."""
    val = "x"
    pts = []
    for t, v in chg:
        if t <= t0:
            val = v
        elif t < t1:
            pts.append((t, v))
    segs, start = [], t0
    for t, v in pts:
        if v != val:
            segs.append((start, t, val))
            start, val = t, v
    segs.append((start, t1, val))
    return segs


def bus_text(v):
    if any(c in v.lower() for c in "xz"):
        return v.lower()[0]
    return str(int(v, 2))


def render(changes, widths, signals, t0, t1, px, tick, out, title):
    LBL, ROW, H, TOP = 70, 46, 26, 46
    width = LBL + (t1 - t0) * px + 30
    height = TOP + ROW * len(signals) + 50
    X = lambda t: LBL + (t - t0) * px

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height}" '
        f'viewBox="0 0 {width:.0f} {height}" font-family="DejaVu Sans Mono, monospace" font-size="12">',
        f'<rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    if title:
        s.append(f'<text x="{LBL}" y="22" font-size="14" font-weight="bold" '
                 f'fill="#222">{html.escape(title)}</text>')

    # siatka czasu
    bottom = TOP + ROW * len(signals)
    t = (int(t0 // tick) + 1) * tick if t0 % tick else t0
    n = 0
    while t <= t1 + 1e-9:
        x = X(t)
        s.append(f'<line x1="{x:.1f}" y1="{TOP - 6}" x2="{x:.1f}" y2="{bottom}" '
                 f'stroke="#e3e3e3" stroke-width="1"/>')
        if round(t / tick) % 5 == 0:
            s.append(f'<line x1="{x:.1f}" y1="{bottom}" x2="{x:.1f}" y2="{bottom + 6}" stroke="#555"/>')
            s.append(f'<text x="{x:.1f}" y="{bottom + 20}" text-anchor="middle" '
                     f'fill="#555">{t:g}</text>')
        t += tick
        n += 1
    s.append(f'<text x="{width - 10:.0f}" y="{bottom + 38}" text-anchor="end" fill="#555">czas [ns]</text>')

    for row, name in enumerate(signals):
        if name not in changes:
            raise SystemExit(f"brak sygnalu '{name}' w VCD")
        yb = TOP + row * ROW + ROW - 10     # linia "0"
        yt = yb - H                          # linia "1"
        ym = (yb + yt) / 2
        label = name + (f"[{widths[name]-1}:0]" if widths[name] > 1 else "")
        s.append(f'<text x="{LBL - 8}" y="{ym + 4:.1f}" text-anchor="end" fill="#222">{label}</text>')
        segs = segments(changes[name], t0, t1)

        if widths[name] == 1:
            pts = []
            for a, b, v in segs:
                y = yt if v == "1" else yb if v == "0" else ym
                pts += [(X(a), y), (X(b), y)]
            d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            s.append(f'<polyline points="{d}" fill="none" stroke="#1f5fbf" stroke-width="1.6"/>')
        else:
            k = 3
            for a, b, v in segs:
                xa, xb = X(a), X(b)
                kk = min(k, (xb - xa) / 2)
                d = (f"M{xa:.1f},{ym:.1f} L{xa + kk:.1f},{yt} L{xb - kk:.1f},{yt} "
                     f"L{xb:.1f},{ym:.1f} L{xb - kk:.1f},{yb} L{xa + kk:.1f},{yb} Z")
                fill = "#fde7e7" if bus_text(v) in "xz" else "#eaf2ff"
                s.append(f'<path d="{d}" fill="{fill}" stroke="#1f5fbf" stroke-width="1.2"/>')
                txt = bus_text(v)
                if xb - xa >= 8 * len(txt) + 4:
                    s.append(f'<text x="{(xa + xb) / 2:.1f}" y="{ym + 4:.1f}" '
                             f'text-anchor="middle" fill="#0d2f66">{txt}</text>')

    s.append("</svg>")
    with open(out, "w") as f:
        f.write("\n".join(s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vcd")
    ap.add_argument("out")
    ap.add_argument("--scope", default="licznik_tb")
    ap.add_argument("--signals", nargs="+", default=["clk", "rst", "x", "y"])
    ap.add_argument("--from", dest="t0", type=float, default=0)
    ap.add_argument("--to", dest="t1", type=float, default=None)
    ap.add_argument("--px", type=float, default=4, help="pikseli na ns")
    ap.add_argument("--tick", type=float, default=10, help="krok siatki [ns]")
    ap.add_argument("--title", default="")
    a = ap.parse_args()

    changes, widths, end = parse_vcd(a.vcd, a.scope)
    t1 = a.t1 if a.t1 is not None else end
    render(changes, widths, a.signals, a.t0, t1, a.px, a.tick, a.out, a.title)


if __name__ == "__main__":
    main()
