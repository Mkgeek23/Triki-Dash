# Plan: Tempo i trudność

**Cel:** Przeciwdziałanie monotonii poprzez narastającą prędkość, fale przeciwników i rotujące poziomy trudności.

## Zadania

### Narastająca prędkość
- [x] Dodać zmienną `base_speed` w `game_loop`, która rośnie liniowo co 500 dystansu (np. `scroll = min(4 + score // 500, 14)`)
- [x] Zwiększać częstotliwość spawnu przeszkód wraz z prędkością (spawn_tick maleje dynamicznie)
- [_] Zmodyfikować `BOOST_SPEED_MUL` aby sprint nadawał sens przy wyższych prędkościach (pozostawione na później, obecny sztywny 2.0)

### Fale przeciwników
- [x] Wprowadzić zmienną `last_wave` – numer fali zwiększa się co 1000 dystansu
- [x] Początek fali: komunikat + spawn grupy 3-5 przeszkód na raz
- [x] Między falami: 90 ticks przerwy (wave_cooldown, tylko monety, brak przeszkód)
- [x] Boss co 5 fal zamiast co 2000 dystansu (sprawdza `last_wave % 5 == 0`)

### Poziomy trudności
- [x] Zdefiniować 4 strefy: Łatwa (<2000), Średnia (2000+), Trudna (5000+), Szalona (10000+)
- [x] Każda strefa: inna kombinacja przeszkód, prędkość spawnu, gęstość monet (skalowane ze `scroll`)
- [x] Komunikat przy wejściu w nową strefę (np. "STREFA 1 – ŚREDNIA")

## Modyfikowane pliki
- `game.py` – `game_loop()`, stałe (`SCROLL_SPEED_BASE`, `BOSS_INTERVAL`, `MILESTONE_INTERVAL`)
- `docs/mechaniki-gry.md` – aktualizacja opisu mechanik
