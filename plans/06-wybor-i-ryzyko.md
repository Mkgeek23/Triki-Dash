# Plan: Wybór i ryzyko

**Cel:** Wprowadzenie elementów decyzyjnych – gracz musi podejmować ryzykowne decyzje, a nie tylko reagować na to co pojawia się na drodze.

## Zadania

### Rozgałęzienia trasy
- [x] Stworzyć klasę `Fork` – rozwidlenie dróg pojawiające się na drodze
- [x] Dwa warianty: lewy pas (np. więcej monet, więcej przeszkód) i prawy pas (mniej monet, bezpieczniej)
- [x] Gracz wybiera pasem, którym jedzie – po 1-2 sekundach znika druga opcja
- [x] Efekt wizualny: droga rozdziela się na dwie, z animacją
- [x] Spawn: co 1500-2500 dystansu

### Monety ryzyka
- [x] Złote monety pojawiające się na skraju drogi (przy krawędzi)
- [x] Zebranie: +10 punktów, ale ryzyko wypadnięcia (jeśli gracz jest na krawędzi i nie zbierze idealnie)
- [x] Wizualnie: migająca złota moneta z iskrami
- [x] Spawn: rzadko, przy wyższych prędkościach

### System zdrowia jako zasobu
- [ ] Dodać możliwość poświęcenia życia (celowo najechać na przeszkodę) dla bonusu
- [x] Przeszkoda "tarczowa" – można przez nią przejechać kosztem 1 życia, ale daje +50 punktów
- [x] Decyzja: jeśli gracz ma tarczę → tarcza się zużywa i dostaje punkty; jeśli nie ma → traci życie i dostaje punkty

### Sprint z ryzykiem
- [x] Sprint nie tylko przyspiesza, ale też zwiększa ryzyko kolizji
- [x] Bonus: sprint zrywa przeszkody na drodze (jak taran)
- [x] Ale: podczas sprintu gracz nie może zbierać monet (przelatują)
- [x] Decyzja: sprint teraz czy później?

### Mnożnik za mało żyć
- [x] Jeśli gracz ma tylko 1 życie: ×2 punkty za wszystko
- [x] Jeśli 2 życia: ×1.5
- [x] Jeśli 3+ życia: ×1 (standard)
- [x] Zachęca do ryzykowania i pozostawania przy niskim stanie żyć

## Modyfikowane pliki
- `game.py` – nowe klasy (`Fork`), `Player` (obsługa decyzji, system zdrowia), `game_loop()`
- `docs/encje.md` – dokumentacja nowych klas
- `docs/mechaniki-gry.md` – sekcja decyzji i ryzyka
