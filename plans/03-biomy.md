# Plan: Biomy

**Cel:** Zmiana otoczenia co pewien dystans, aby gra nie wyglądała tak samo przez całą rozgrywkę.

## Zadania

### System biomów
- [_] Zdefiniować listę biomów w `game_loop` (np. Kosmos, Lód, Wulkan, Mgła, Cyber)
- [_] Każdy biom trwa 1500-2500 dystansu
- [_] Zmiana biomu: fade-out/fade-in + komunikat "Strefa: X"

### Biom Kosmos (podstawowy)
- [_] Aktualne tło – nie wymaga zmian
- [_] Neonowa droga, fioletowe akcenty

### Biom Lód
- [_] Paleta: błękit, biel, jasnoniebieski
- [_] Droga: lodowa, półprzezroczysta, z lekkim połyskiem
- [_] Efekt: delikatne płatki śniegu na ekranie (cząsteczki)
- [_] Przeszkody: niebieskie, śliskie (gracz dłużej się zatrzymuje po zmianie pasa?)

### Biom Wulkan
- [_] Paleta: czerwień, pomarańcz, czerń
- [_] Droga: rozgrzana lawa (pomarańczowe linie, czerwone tło)
- [_] Efekt: iskry (cząsteczki) unoszące się nad drogą
- [_] Przeszkody: pomarańczowo-czerwone

### Biom Mgła
- [_] Paleta: szarości, blade fiolety
- [_] Efekt: warstwa mgły przed graczem (półprzezroczysty prostokąt z gradientem)
- [_] Widoczność ograniczona – przeszkody pojawiają się bliżej
- [_] Dźwięk: przytłumione efekty

### Biom Cyber
- [_] Paleta: neonowy róż, cyjan, czerń
- [_] Droga: siatka (grid) zamiast pasów, linie świecące
- [_] Efekt: glitch (losowe poziome linie na ekranie)
- [_] Przeszkody: pikselowe, zniekształcone

### Mechanika zmiany biomu
- [_] Zmienna `current_biome` przechowująca indeks biomu
- [_] Po osiągnięciu progu dystansu: inkrementacja biomu
- [_] `Road.draw()` przyjmuje parametr `biome` i dostosowuje kolorystykę
- [_] `draw_biome_transition()` – fade do czerni i powrót z nowymi kolorami

## Modyfikowane pliki
- `game.py` – `game_loop()`, `Road.draw()`, nowe efekty, nowe stałe kolorów
- `docs/encje.md` – rozszerzenie `Road`
- `docs/mechaniki-gry.md` – sekcja biomów
