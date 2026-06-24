# Plan: Różnorodność przeszkód i wrogów

**Cel:** Wprowadzenie nowych typów przeszkód i wrogów o różnych zachowaniach, przełamujących monotonię czerwonych bloków i dronów.

## Zadania

### Przeszkody ruchome
- [x] Stworzyć klasę `MovingObstacle` – przeszkoda zmieniająca pasy (sinusoidalnie lub losowo)
- [x] Określić parametry: prędkość ruchu bocznego, zakres pasów
- [x] Dodać spawn `MovingObstacle` w `game_loop` z małym prawdopodobieństwem (zone 1+, 4%)
- [x] Rysowanie: czerwony blok z delikatną poświatą kierunku ruchu

### Przeszkody wirujące
- [_] Stworzyć klasę `SpinningObstacle` – blok wirujący wokół własnej osi
- [_] Efekt wizualny: rotacja (zmiana szerokości wyświetlania symulująca obrót)
- [_] Dodać spawn w `game_loop`

### Blokady (wall)
- [x] Stworzyć klasę `WallObstacle` – blokada na 6 z 7 pasów z małą przerwą
- [x] Gracz musi szybko znaleźć przerwę i przemieścić się na odpowiedni pas
- [x] Dodać spawn przy wyższych poziomach trudności (zone 2+, 2.5%)

### Wrogowie strzelający
- [x] Rozszerzyć klasę `Drone` o możliwość strzelania
- [x] Pociski wroga: czerwone, lecą w dół, gracz musi unikać
- [x] Częstotliwość strzałów: co 60-120 klatek

### Mini-boss
- [x] Nowa klasa `MiniBoss` – pojawia się co 3 fale, ma 3 HP
- [x] Zachowanie: powolny ruch w górę i w dół, strzela pociskami
- [x] Po pokonaniu: bonus 50 punktów + efekt cząsteczkowy

## Modyfikowane pliki
- `game.py` – nowe klasy encji, `game_loop()` spawn, kolizje, rysowanie
- `docs/encje.md` – dokumentacja nowych klas
- `docs/mechaniki-gry.md` – aktualizacja
