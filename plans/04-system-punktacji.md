# Plan: System punktacji

**Cel:** Urozmaicenie systemu punktacji poprzez łańcuchy monet, cele poboczne i rozbudowany system combo.

## Zadania

### Łańcuchy monet
- [x] Stworzyć `CoinChain` – 5-8 monet w jednym pasie, równomiernie rozmieszczonych (przez chain_id w CoinObj)
- [x] Bonus za zebranie całego łańcucha: +50 punktów + efekt wizualny (flare + particles)
- [x] Spawn: 20% szansa zamiast normalnej monety, co 300-500 dystansu
- [x] Wizualizacja: złote linie łączące monety w łańcuchu

### System combo
- [x] Mnożnik progresywny: `min(int(combo * 0.1) + 1, 15)` zamiast starego `coins_collected // 5 + 1`
- [x] Maksymalny mnożnik: 15 (zamiast 10)
- [x] Combo inkrementowane za: zebranie monety, zestrzelenie przeszkody (+1), drona (+2), mini-bossa (+3), zmianę pasa (+1)
- [x] Combo reset: natychmiast po kolizji z przeszkodą (przez `player.combo = 0`)

### Cele poboczne w trakcie gry
- [_] Wyświetlać małe wyzwanie na górze ekranu
- [_] Pula celów: utrzymaj pas, zbierz X monet, uniknij Y przeszkód
- [_] Nagroda za cel: +100 punktów + 1 moneta specjalna
- [_] Nowy cel pojawia się co 20-30 sekund

### Punkty za szybkie zmiany pasa
- [x] Rejestrować czas między zmianami pasa (`last_lane_change_tick`)
- [x] Jeśli zmiana w ciągu < 30 ticków (<500ms): bonus +5 punktów za slalom
- [x] Mnożnik za serię szybkich zmian: x1-x5 (bonus = min(slalom_count, 5) * 5)

### Perfect clear
- [x] Śledzić czy gracz ominął falę przeszkód bez utraty życia (`wave_clear = True/False`)
- [x] Bonus za falę bez szwanku: +100 punktów + flare efekt

## Modyfikowane pliki
- `game.py` – `Player` (combo, timing), `game_loop()` (spawn łańcuchów, cele, naliczanie)
- `docs/mechaniki-gry.md` – aktualizacja systemu punktacji
- `docs/progresja.md` – aktualizacja przeliczników
