# Licznik NKB 0..30 / 31 - symulacja i materialy do sprawozdania
#
#   make          - symulacja + wszystkie rysunki i tabele
#   make sim      - tylko symulacja (log w build/sim.log)
#   make wave     - otwiera przebiegi w GTKWave
#   make clean    - usuwa wygenerowane pliki

SRC   = src/licznik.v src/licznik_bramki.v
TB    = tb/licznik_tb.v
BUILD = build
IMG   = sprawozdanie/img
VCD   = $(BUILD)/licznik.vcd
W     = python3 tools/vcd2svg.py $(VCD)
SIG   = --signals clk rst x y y_b

.PHONY: all sim wave figures clean

all: sim figures

$(BUILD)/sim: $(SRC) $(TB) | $(BUILD)
	iverilog -g2005 -Wall -o $@ $(SRC) $(TB)

$(VCD) $(BUILD)/sim.log: $(BUILD)/sim
	cd $(BUILD) && vvp sim | tee sim.log
	@grep -q "^OK:" $(BUILD)/sim.log

sim: $(BUILD)/sim.log

figures: $(VCD) | $(IMG)
	$(W) $(IMG)/przebieg_caly.svg   $(SIG) --from 0   --to 730 --px 4  --title "Pełna symulacja (T1–T4)"
	$(W) $(IMG)/przebieg_start.svg  $(SIG) --from 0   --to 90  --px 10 --title "Reset i początek sekwencji"
	$(W) $(IMG)/przebieg_30_0.svg   $(SIG) --from 280 --to 350 --px 10 --title "Koniec sekwencji: 30 → 0 (x = 0)"
	$(W) $(IMG)/przebieg_x1.svg     $(SIG) --from 340 --to 440 --px 10 --title "x = 1 w trakcie liczenia → 31, potem x = 0 → start od 0"
	$(W) $(IMG)/przebieg_x1_30.svg  $(SIG) --from 680 --to 730 --px 10 --title "x = 1 w stanie 30 → 31 → 0"
	python3 tools/graf.py   $(IMG)/graf_stanow.svg
	python3 tools/tabela.py sprawozdanie/tabela_przejsc.md
	cp $(BUILD)/sim.log sprawozdanie/sim.log
	@if command -v magick >/dev/null; then \
		for f in $(IMG)/*.svg; do magick -density 150 $$f $${f%.svg}.png; done; \
		echo "PNG wygenerowane w $(IMG)/"; \
	else echo "brak ImageMagick - pomijam PNG"; fi

wave: $(VCD)
	gtkwave $(VCD) gtkwave/licznik.gtkw &

$(BUILD) $(IMG):
	mkdir -p $@

clean:
	rm -rf $(BUILD)
