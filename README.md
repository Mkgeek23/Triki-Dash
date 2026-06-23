# Triki Dash

Endless runner z obsługą kontrolera Triki (BLE) i klawiatury.

## Wymagania

- Python 3.10+
- Pygame
- Bleak (`bleak>=0.20.0`)

```
pip install pygame bleak
```

## Sterowanie

| Akcja | Klawiatura | Triki |
|-------|-----------|-------|
| Ruch | Strzałki ←/→ lub A/D | Przechylanie w lewo/prawo (żyroskop) |
| Strzał | SPACJA | Przycisk na środku obudowy |
| Sprint | S | Energiczne potrząśnięcie |
| Pauza | P | – |
| Sklep | U | – |

## Rozgrywka

- **7 pasów** – unikaj przeszkód, zbieraj monety
- **5 naboi** – strzelaj w przeszkody, drony i tarcze (odnawiają się co 10 monet)
- **Sprint (Boost)** – chwilowe przyspieszenie 2×, ładuje się co 120 klatek
- **Tarcze** – strzelaj w nie, aby zdobyć bonusowe monety (×2, ×3, ×5)
- **Portal** – pojawia się co 3000 dystansu, prowadzi do sekretnej strefy z bonusami
- **BOSS** – co 2000 dystansu, wymaga 3 trafień
- **Cykl dzień/noc** – noc zapada co 900 klatek na 300 klatek
- **Magnet** – przyciąga monety z większej odległości (ulepszenie)

## Ulepszenia (sklep)

Zbieraj gwiazdki (★) i kupuj ulepszenia w sklepie (U):

- **Sprint** – wydłuża czas boosta
- **Magnet** – zwiększa zasięg przyciągania monet
- **Życia** – dodatkowe życia

## Wyzwania dzienne

Codziennie 3 losowe wyzwania (uniki, monety, dystans, strzelanie, sprinty). Wykonanie wszystkich daje dodatkowe gwiazdki.

## Pliki

| Plik | Opis |
|------|------|
| `game.py` | Główna gra |
| `TrikiPy.py` | Sterownik BLE kontrolera Triki |
| `main.py` | Diagnostyka kontrolera Triki |
| `triki_upgrades.json` | Stan ulepszeń |
| `triki_challenges.json` | Wyzwania dzienne |
| `triki_highscore.txt` | Najlepsze wyniki |
| `triki_total_coins.txt` | Łączna liczba monet |
