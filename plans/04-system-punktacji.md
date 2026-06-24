# Plan: System punktacji

**Cel:** Urozmaicenie systemu punktacji poprzez łańcuchy monet, cele poboczne i rozbudowany system combo.

## Zadania

### Łańcuchy monet
- [_] Stworzyć `CoinChain` – 5-8 monet w jednym pasie, równomiernie rozmieszczonych
- [_] Bonus za zebranie całego łańcucha: +50 punktów + efekt wizualny + dźwięk
- [_] Spawn: co 300-500 dystansu zamiast pojedynczych monet
- [_] Wizualizacja: monety połączone świetlną linią

### System combo
- [_] Obecny mnożnik (co 5 combo) zastąpić progresywnym: +0.1 mnożnika za każde combo
- [_] Maksymalny mnożnik: 15 (zamiast 10)
- [_] Combo reset: natychmiast po kolizji z przeszkodą (obecnie jest, ale można dodać pasek wyświetlający czas do resetu)
- [_] Bonus za combo po śmierci: za każde 10 combo +5 gwiazdek (przelicznik)

### Cele poboczne w trakcie gry
- [_] Wyświetlać małe wyzwanie na górze ekranu, np. "Zostań na pasie 3 przez 5s"
- [_] Pula celów: utrzymaj pas, zbierz X monet bez zmiany pasa, uniknij Y przeszkód z rzędu
- [_] Nagroda za cel: +100 punktów + 1 moneta specjalna
- [_] Nowy cel pojawia się co 20-30 sekund

### Punkty za szybkie zmiany pasa
- [_] Rejestrować czas między zmianami pasa
- [_] Jeśli zmiana w ciągu < 500ms od poprzedniej: bonus +5 punktów (szybki slalom)
- [_] Mnożnik za serię szybkich zmian: x2/x3/x5

### Perfect clear
- [_] Śledzić czy gracz ominął falę przeszkód bez użycia tarczy
- [_] Bonus za falę bez szwanku: +100 punktów + efekt błysku

## Modyfikowane pliki
- `game.py` – `Player` (combo, timing), `game_loop()` (spawn łańcuchów, cele, naliczanie)
- `docs/mechaniki-gry.md` – aktualizacja systemu punktacji
- `docs/progresja.md` – aktualizacja przeliczników
