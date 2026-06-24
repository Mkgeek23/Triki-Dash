# Plan: Biomy

**Cel:** Zmiana otoczenia co pewien dystans, aby gra nie wyglądała tak samo przez całą rozgrywkę.

## Zadania

### System biomów
- [x] Zdefiniować listę biomów w `game_loop` (Kosmos, Lód, Wulkan, Mgła, Cyber)
- [x] Każdy biom trwa 2000 dystansu
- [x] Zmiana biomu: fade do czerni i powrót + komunikat (wbudowany w transition_alpha)

### Biom Kosmos (podstawowy)
- [x] Aktualne tło – nie wymaga zmian
- [x] Neonowa droga, fioletowe akcenty

### Biom Lód
- [x] Paleta: błękit, biel, jasnoniebieski
- [x] Droga: lodowa, niebieskie akcenty
- [x] Efekt: płatki śniegu (cząsteczki spadające po przekątnej)
- [x] Przeszkody: niebieskie (automatycznie przez biome param)

### Biom Wulkan
- [x] Paleta: czerwień, pomarańcz, czerń
- [x] Droga: rozgrzana lawa (pomarańczowe linie, czerwone tło)
- [x] Efekt: iskry (cząsteczki unoszące się do góry)
- [x] Przeszkody: pomarańczowo-czerwone

### Biom Mgła
- [x] Paleta: szarości, blade fiolety
- [x] Efekt: warstwa mgły przed graczem (gradient półprzezroczysty)
- [x] Widoczność ograniczona – brak gwiazd, stonowane kolory

### Biom Cyber
- [x] Paleta: neonowy róż, cyjan, czerń
- [x] Droga: siatka neonowych linii
- [x] Efekt: glitch (losowe kolorowe linie na ekranie)
- [x] Przeszkody: różowo-cyjanowe

### Mechanika zmiany biomu
- [x] Zmienna `current_biome` przechowująca indeks biomu
- [x] Po osiągnięciu progu dystansu: inkrementacja biomu (mod 5)
- [x] `Road.draw()` przyjmuje parametr `biome` i dostosowuje kolorystykę (paleta BIOMES)
- [x] `transition_alpha` – fade do czerni i powrót z nowymi kolorami

## Modyfikowane pliki
- `game.py` – `game_loop()`, `Road.draw()`, nowe efekty, nowe stałe kolorów
- `docs/encje.md` – rozszerzenie `Road`
- `docs/mechaniki-gry.md` – sekcja biomów
