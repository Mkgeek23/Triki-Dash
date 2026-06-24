# Plan: Różnorodność przeszkód i wrogów

**Cel:** Wprowadzenie nowych typów przeszkód i wrogów o różnych zachowaniach, przełamujących monotonię czerwonych bloków i dronów.

## Zadania

### Przeszkody ruchome
- [_] Stworzyć klasę `MovingObstacle` – przeszkoda zmieniająca pasy (sinusoidalnie lub losowo)
- [_] Określić parametry: prędkość ruchu bocznego, zakres pasów
- [_] Dodać spawn `MovingObstacle` w `game_loop` z małym prawdopodobieństwem
- [_] Rysowanie: czerwony blok z delikatną poświatą kierunku ruchu

### Przeszkody wirujące
- [_] Stworzyć klasę `SpinningObstacle` – blok wirujący wokół własnej osi
- [_] Efekt wizualny: rotacja (zmiana szerokości wyświetlania symulująca obrót)
- [_] Dodać spawn w `game_loop`

### Blokady (wall)
- [_] Stworzyć klasę `WallObstacle` – blokada na 6 z 7 pasów z małą przerwą
- [_] Gracz musi szybko znaleźć przerwę i przemieścić się na odpowiedni pas
- [_] Dodać spawn przy wyższych poziomach trudności (dystans > 3000)

### Wrogowie strzelający
- [_] Rozszerzyć klasę `Drone` o możliwość strzelania
- [_] Pociski wroga: czerwone, lecą w dół, gracz musi unikać
- [_] Częstotliwość strzałów: co 60-120 klatek

### Mini-boss
- [_] Nowa klasa `MiniBoss` – pojawia się co 1000 dystansu, ma 2-3 HP
- [_] Zachowanie: powolny ruch w górę i w dół, strzela pociskami
- [_] Po pokonaniu: bonus 50 punktów + moneta specjalna

## Modyfikowane pliki
- `game.py` – nowe klasy encji, `game_loop()` spawn, kolizje, rysowanie
- `docs/encje.md` – dokumentacja nowych klas
- `docs/mechaniki-gry.md` – aktualizacja
