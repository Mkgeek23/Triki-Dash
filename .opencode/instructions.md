# Instrukcje dla AI – Triki Runner

## Projekt
- `C:\python\kapsel\` – gra Triki Runner (Pygame + Triki BLE controller)
- Główny plik: `game.py` (~1727 linii), całość w jednym pliku
- Sterownik BLE: `TrikiPy.py` (174 linie)
- Pliki zapisu: `triki_upgrades.json`, `triki_challenges.json`, `triki_highscore.txt`, `triki_total_coins.txt`

## Architektura

### Główne funkcje
| Funkcja | Linia | Opis |
|---------|-------|------|
| `main()` | ~1700 | Entry point, inicjalizacja, pętla menu→gra→game over |
| `game_loop()` | ~886 | Główna pętla rozgrywki (60 FPS) |
| `show_start()` | ~787 | Menu startowe (Pegasus-style) |
| `show_over()` | ~891 | Ekran końca gry |
| `show_shop()` | ~673 | Sklep ulepszeń |
| `triki_thread()` / `_triki_loop()` | ~581 | Wątek BLE, odczyt żyroskopu i przycisku |

### Klasy encji
| Klasa | Linia | Opis |
|-------|-------|------|
| `Road` | ~527 | Rysowanie tła kosmicznego + drogi neonowej |
| `Player` | ~179 | Gracz, ruch, amunicja, życia, boost, combo |
| `Obstacle` | ~287 | Przeszkody i bossowie |
| `CoinObj` | ~352 | Monety (normal, silver, gold) |
| `PortalObj` | ~396 | Portal do strefy bonusowej |
| `Bullet` | ~424 | Pociski gracza |
| `Drone` | ~449 | Latający wrogowie |
| `Target` | ~489 | Tarcze (power-up shield) |
| `Particle` | ~78 | Cząsteczki (efekty wizualne) |

## Konwencje kodowania
- **Brak komentarzy w kodzie** – dokumentacja w `docs/`
- Kolory RGB clampować przez `min(wartość, 255)` – nigdy nie przekraczać zakresu
- Globalne zmienne Triki: `triki_connected`, `triki_analog`, `triki_raw`, `triki_accel`, `triki_button`, `triki_offset`, `triki_battery`
- `triki_button` wymaga `global triki_button` w funkcjach, które go odczytują i zerują (`= False`)
- W `show_shop()` funkcja wewnętrzna `buy_upgrade()` używa `nonlocal upgrades` (modyfikacja słownika z zewnętrznego scope)
- Menu używają `make_menu_stars()` i `draw_menu_stars()` do kosmicznego tła z gwiazdami
- Wykrywanie potrząsania w menu: `abs(triki_accel[0]) + abs(triki_accel[1]) + abs(triki_accel[2]) > 22000` z detekcją zbocza (`last_shake_mag < 17000`)

## Paleta kolorów
| Stała | RGB | Użycie |
|-------|-----|--------|
| `BLACK` | (10, 10, 10) | Tło menu, kosmos |
| `WHITE` | (255, 255, 255) | Podstawowy tekst |
| `GREEN` | (60, 220, 80) | Tytuł menu |
| `RED` | (230, 40, 60) | Game over, frame over |
| `YELLOW` | (255, 220, 30) | Monety, informacje |
| `GOLD` | (255, 215, 0) | Gwiazdki, sklep |
| `CYAN` | (80, 220, 255) | Frame startowy, neon drogi |
| `PURPLE` | (180, 80, 255) | Tarcza, portale |
| `LIGHT_GRAY` | (140, 140, 140) | Pomocnicze teksty |
| `ORANGE` | (255, 160, 20) | Rekordy |
| `ROAD_COLOR` | (45, 45, 50) | Nieużywane (droga liczy się dynamicznie) |

## Wymiary i stałe gry
| Stała | Wartość | Opis |
|-------|---------|------|
| `WIDTH` | 800 | Szerokość okna |
| `HEIGHT` | 600 | Wysokość okna |
| `FPS` | 60 | Klatki na sekundę |
| `LANE_COUNT` | 7 | Liczba pasów |
| `LANE_WIDTH` | 114 | Szerokość pasa (WIDTH // 7) |
| `PLAYER_SIZE` | 36 | Rozmiar gracza |
| `SCROLL_SPEED_BASE` | 4 | Bazowa prędkość przewijania |
| `BOOST_SPEED_MUL` | 2.0 | Mnożnik prędkości sprintu |

## Weryfikacja kodu
- **Brak testów automatycznych** – testowanie wyłącznie manualne przez uruchomienie gry
- Sprawdzenie składni: `python -c "import py_compile; py_compile.compile('game.py', doraise=True, quiet=True)"`
- Szybki test importu: `$env:SDL_VIDEODRIVER='dummy'; python -c "import sys; sys.path.insert(0, '.'); import game; print('OK')"`
- Po zmianach uruchom grę i przetestuj ekrany menu i podstawową rozgrywkę

## Typowe problemy
- `ValueError: invalid color argument` – wartość kanału > 255, brak `min()`
- `UnboundLocalError: cannot access local variable 'triki_button'` – brak `global triki_button`
- Nieużywane stale w kodzie: `ROAD_COLOR`, `ROAD_LINE` – zdefiniowane ale nieużywane w rysowaniu
- `triki_offset` jest inicjalizowane na `0.0`, więc gdy Triki nie jest podłączone: `gx = triki_raw[0] - triki_offset = 0 - 0 = 0` (bezpieczne)

## Zasady działania

- **Nigdy nie zgaduj – zawsze pytaj.** Jeśli nie wiesz, którą opcję wybrać, nie znasz intencji użytkownika, brakuje Ci informacji do podjęcia decyzji – zadaj pytanie. Nie domyślaj się, nie zakładaj.
- **Aktualizuj dokumentację przy zmianach.** Gdy modyfikujesz istniejącą mechanikę, funkcję lub klasę, zaktualizuj odpowiedni plik w `docs/`. Gdy dodajesz nową funkcjonalność wartą udokumentowania, utwórz nowy plik w `docs/` i dodaj go do spisu treści w `docs/README.md`.

## Ważne szczegóły
- Sterowanie w menu: potrząsanie kontrolerem = następna opcja, przycisk = akceptuj
- Klawiatura w menu: strzałki/góra-dół = nawigacja, SPACJA/ENTER = akceptuj, ESC = wyjście
- Portal mode: co 3000 dystansu, 5 sekund, gracz może się poruszać (naprawione)
- Speed lines po bokach drogi pojawiają się przy speed > 3
- Night cycle co 900 ticków, trwa 300 ticków
- Boss co 2000 dystansu

## Kolejność rysowania w game loop
```
1. road.draw()              – tło kosmiczne, gwiazdy, droga neonowa, pasy
2. player.draw()             – gracz
3. obstacles/coins/portals   – przeszkody, monety, portale
4. drones/targets            – drony, tarcze
5. bullets                   – pociski
6. particles                 – cząsteczki efektów
7. draw_night_overlay()      – nakładka nocy (półprzezroczysta)
8. draw_flare()              – efekt błysku mnożnika
9. HUD                       – lives, ammo, combo, tilt bar, button indicator
```

## Format danych Triki (BLE)
Pakiet binarny: `struct.unpack('<hhhhhh', packet[2:14])` → 6 x signed 16-bit int
- `ax, ay, az` – akcelerometr (surowy, w spoczynku suma ok. 16384 = 1g)
- `gx, gy, gz` – żyroskop (angular velocity, używany do kalibracji i sprintu)
