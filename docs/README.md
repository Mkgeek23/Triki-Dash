# Triki Runner

Gra napisana w Pythonie + Pygame, sterowana kontrolerem Triki przez BLE lub klawiaturą. Gracz biegnie siedmiopasmową drogą w kosmicznym stylu, unika przeszkód, zbiera monety, strzela do wrogów i wchodzi do portali bonusowych.

## Spis treści dokumentacji

| Plik | Opis |
|------|------|
| [architektura.md](architektura.md) | Struktura plików, przepływ sterowania, pętla gry |
| [mechaniki-gry.md](mechaniki-gry.md) | Przeszkody, portale, bossowie, combo, power-upy |
| [menu.md](menu.md) | System menu, nawigacja Triki i klawiaturą |
| [triki.md](triki.md) | Integracja kontrolera Triki przez BLE |
| [encje.md](encje.md) | Klasy encji: Player, Road, Obstacle, Coin, itd. |
| [progresja.md](progresja.md) | Ulepszenia, gwiazdki, daily challenges, pliki zapisu |

## Szybki start

```bash
pip install -r requirements.txt
python game.py
```

## Wymagania
- Python 3.10+
- `pygame`
- `bleak` (do BLE)
- `TrikiPy` (sterownik kontrolera)
