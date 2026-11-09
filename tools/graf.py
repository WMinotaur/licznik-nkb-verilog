#!/usr/bin/env python3
"""Generuje graf stanow automatu (SVG) bez zewnetrznych bibliotek."""
import math
import sys

out = sys.argv[1] if len(sys.argv) > 1 else "graf.svg"

W, Hh = 860, 900
CX, CY, R = 430, 450, 340
RN, RC = 21, 30                 # promien wezla na okregu / wezla 31

def pos(i):                     # stan i (0..30) na okregu, 0 na gorze
    a = -math.pi / 2 + 2 * math.pi * i / 31
    return CX + R * math.cos(a), CY + R * math.sin(a)

def shorten(x1, y1, x2, y2, r1, r2, off=0.0):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy * off, ux * off
    return (x1 + ux * r1 + nx, y1 + uy * r1 + ny,
            x2 - ux * r2 + nx, y2 - uy * r2 + ny)

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}" '
     f'font-family="DejaVu Sans, sans-serif" font-size="13">',
     '<rect width="100%" height="100%" fill="#ffffff"/>',
     '<defs>'
     '<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
     '<path d="M0,0 L10,5 L0,10 z" fill="#1f5fbf"/></marker>'
     '<marker id="b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
     '<path d="M0,0 L10,5 L0,10 z" fill="#c0392b"/></marker>'
     '</defs>']

# przejscia x=1: kazdy stan -> 31 (przerywane)
for i in range(31):
    x, y = pos(i)
    off = -7 if i == 0 else 0
    a = shorten(x, y, CX, CY, RN, RC + 2, off)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{a[2]:.1f}" y2="{a[3]:.1f}" '
             f'stroke="#c0392b" stroke-width="1" stroke-dasharray="4 3" opacity="0.65" marker-end="url(#b)"/>')

# przejscia x=0: i -> i+1, 30 -> 0
for i in range(31):
    j = (i + 1) % 31
    x1, y1 = pos(i)
    x2, y2 = pos(j)
    a = shorten(x1, y1, x2, y2, RN, RN + 2)
    s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{a[2]:.1f}" y2="{a[3]:.1f}" '
             f'stroke="#1f5fbf" stroke-width="1.6" marker-end="url(#a)"/>')

# 31 -> 0 przy x=0
x0, y0 = pos(0)
a = shorten(CX, CY, x0, y0, RC, RN + 2, -7)
s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{a[2]:.1f}" y2="{a[3]:.1f}" '
         f'stroke="#1f5fbf" stroke-width="2" marker-end="url(#a)"/>')
s.append(f'<text x="{CX + 12}" y="{(CY + y0) / 2 + 40:.0f}" fill="#1f5fbf">x=0</text>')

# petla 31 -> 31 przy x=1
s.append(f'<path d="M{CX + 22},{CY + 21} C{CX + 70},{CY + 90} {CX - 70},{CY + 90} {CX - 22},{CY + 21}" '
         f'fill="none" stroke="#c0392b" stroke-width="1.6" marker-end="url(#b)"/>')
s.append(f'<text x="{CX}" y="{CY + 92}" text-anchor="middle" fill="#c0392b">x=1</text>')

# wezly
for i in range(31):
    x, y = pos(i)
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{RN}" fill="#eaf2ff" stroke="#1f5fbf" stroke-width="1.5"/>')
    s.append(f'<text x="{x:.1f}" y="{y + 4.5:.1f}" text-anchor="middle" fill="#0d2f66">{i}</text>')
s.append(f'<circle cx="{CX}" cy="{CY}" r="{RC}" fill="#fdecea" stroke="#c0392b" stroke-width="1.8"/>')
s.append(f'<circle cx="{CX}" cy="{CY}" r="{RC - 4}" fill="none" stroke="#c0392b" stroke-width="1"/>')
s.append(f'<text x="{CX}" y="{CY + 5}" text-anchor="middle" font-weight="bold" fill="#7b241c">31</text>')

# legenda
ly = Hh - 48
s.append(f'<line x1="30" y1="{ly}" x2="80" y2="{ly}" stroke="#1f5fbf" stroke-width="1.8" marker-end="url(#a)"/>')
s.append(f'<text x="90" y="{ly + 4}">x = 0 : następny stan w sekwencji (30 → 0, 31 → 0)</text>')
s.append(f'<line x1="30" y1="{ly + 24}" x2="80" y2="{ly + 24}" stroke="#c0392b" stroke-width="1.2" '
         f'stroke-dasharray="4 3" marker-end="url(#b)"/>')
s.append(f'<text x="90" y="{ly + 28}">x = 1 : przejście do stanu 31 (z każdego stanu)</text>')
s.append(f'<text x="30" y="30" font-size="15" font-weight="bold">Graf stanów (automat Moore\'a, wyjście = numer stanu)</text>')

s.append('</svg>')
with open(out, "w") as f:
    f.write("\n".join(s))
