# Licznik NKB 0–30 / 31 (Verilog)

Układ synchroniczny: przy `x = 0` na wyjściu kolejno 0…30 (NKB), przy `x = 1`
wartość 31; powrót `x = 0` zaczyna sekwencję od 0.

## Wymagania (Fedora)

```bash
sudo dnf install iverilog gtkwave make python3 ImageMagick
```

ImageMagick jest opcjonalny (tylko do PNG dla Worda).

## Użycie

```bash
make          # kompilacja + symulacja + rysunki + tabele (sprawozdanie/)
make sim      # tylko symulacja, log w build/sim.log
make wave     # przebiegi w GTKWave (gotowy widok z gtkwave/licznik.gtkw)
make clean    # usuwa build/
```

## Struktura

```
src/licznik.v           opis behawioralny
src/licznik_bramki.v    opis strukturalny: 5 przerzutników D + bramki
tb/licznik_tb.v         testbench (obie wersje + test wyczerpujący)
tools/vcd2svg.py        VCD -> SVG (przebiegi do sprawozdania)
tools/graf.py           graf stanów (SVG)
tools/tabela.py         pełna tablica przejść (MD + CSV)
gtkwave/licznik.gtkw    zapisany widok GTKWave
sprawozdanie/           sprawozdanie.md + wygenerowane rysunki, tabele, log
```
