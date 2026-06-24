# Plan: Wybór i ryzyko

**Cel:** Wprowadzenie elementów decyzyjnych – gracz musi podejmować ryzykowne decyzje, a nie tylko reagować na to co pojawia się na drodze.

## Zadania

### Rozgałęzienia trasy
- [_] Stworzyć klasę `Fork` – rozwidlenie dróg pojawiające się na drodze
- [_] Dwa warianty: lewy pas (np. więcej monet, więcej przeszkód) i prawy pas (mniej monet, bezpieczniej)
- [_] Gracz wybiera pasem, którym jedzie – po 1-2 sekundach znika druga opcja
- [_] Efekt wizualny: droga rozdziela się na dwie, z animacją
- [_] Spawn: co 1500-2500 dystansu

### Monety ryzyka
- [_] Złote monety pojawiające się na skraju drogi (przy krawędzi)
- [_] Zebranie: +10 punktów, ale ryzyko wypadnięcia (jeśli gracz jest na krawędzi i nie zbierze idealnie)
- [_] Wizualnie: migająca złota moneta z iskrami
- [_] Spawn: rzadko, przy wyższych prędkościach

### System zdrowia jako zasobu
- [_] Dodać możliwość poświęcenia życia (celowo najechać na przeszkodę) dla bonusu
- [_] Przeszkoda "tarczowa" – można przez nią przejechać kosztem 1 życia, ale daje +50 punktów
- [_] Decyzja: jeśli gracz ma tarczę → tarcza się zużywa i dostaje punkty; jeśli nie ma → traci życie i dostaje punkty

### Sprint z ryzykiem
- [_] Sprint nie tylko przyspiesza, ale też zwiększa ryzyko kolizji
- [_] Bonus: sprint zrywa przeszkody na drodze (jak taran)
- [_] Ale: podczas sprintu gracz nie może zbierać monet (przelatują)
- [_] Decyzja: sprint teraz czy później?

### Mnożnik za mało żyć
- [_] Jeśli gracz ma tylko 1 życie: ×2 punkty za wszystko
- [_] Jeśli 2 życia: ×1.5
- [_] Jeśli 3+ życia: ×1 (standard)
- [_] Zachęca do ryzykowania i pozostawania przy niskim stanie żyć

## Modyfikowane pliki
- `game.py` – nowe klasy (`Fork`), `Player` (obsługa decyzji, system zdrowia), `game_loop()`
- `docs/encje.md` – dokumentacja nowych klas
- `docs/mechaniki-gry.md` – sekcja decyzji i ryzyka
