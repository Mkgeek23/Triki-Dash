# Plan: Tempo i trudność

**Cel:** Przeciwdziałanie monotonii poprzez narastającą prędkość, fale przeciwników i rotujące poziomy trudności.

## Zadania

### Narastająca prędkość
- [_] Dodać zmienną `base_speed` w `game_loop`, która rośnie liniowo co 500 dystansu (np. `speed = 4 + score // 500`)
- [_] Zwiększać częstotliwość spawnu przeszkód wraz z prędkością (spawn_tick maleje)
- [_] Zmodyfikować `BOOST_SPEED_MUL` aby sprint nadawał sens przy wyższych prędkościach (np. `min(2.0, 4.0 - base_speed / 10)`)

### Fale przeciwników
- [_] Wprowadzić zmienną `wave` – numer fali zwiększa się co 1000 dystansu
- [_] Początek fali: krótki efekt wizualny + spawn grupy 3-5 przeszkód na raz
- [_] Między falami: 1-2 sekundy przerwy (tylko monety, brak przeszkód)
- [_] Boss co 5 fal zamiast co 2000 dystansu

### Poziomy trudności
- [_] Zdefiniować 3-4 strefy (np. Łatwy 0-2000, Średni 2000-5000, Trudny 5000-10000, Szalony 10000+)
- [_] Każda strefa: inna kombinacja przeszkód, prędkość spawnu, gęstość monet
- [_] Komunikat przy wejściu w nową strefę (np. "Strefa 2 – Średnia")

## Modyfikowane pliki
- `game.py` – `game_loop()`, stałe (`SCROLL_SPEED_BASE`, `BOSS_INTERVAL`, `MILESTONE_INTERVAL`)
- `docs/mechaniki-gry.md` – aktualizacja opisu mechanik
