# Architektura

## Struktura plików

```
C:\python\kapsel\
├── game.py                  # Główna gra (~1727 linii)
├── TrikiPy.py               # Sterownik BLE kontrolera Triki (~174 linie)
├── triki_upgrades.json       # Zapisy ulepszeń i gwiazdek
├── triki_challenges.json     # Stan daily challenges
├── triki_highscore.txt       # Najlepszy dystans i ocena
├── triki_total_coins.txt     # Życiowa liczba monet
├── requirements.txt          # Zależności Pythona
├── POMYSLY.md                # Pomysły na rozwój
├── .opencode/
│   └── instructions.md       # Kontekst dla AI
└── docs/
    ├── README.md             # Spis treści
    ├── architektura.md       # Ten plik
    ├── mechaniki-gry.md      # Mechaniki
    ├── menu.md               # System menu
    ├── triki.md              # Integracja Triki
    ├── encje.md              # Encje
    └── progresja.md          # Progresja
```

## Przepływ sterowania

```
main() (~linia 1700)
│
├── pygame.init()
├── Inicjalizacja dźwięków
├── Start wątku Triki (triki_thread) ~linia 581
│   └── asyncio.run(_triki_loop())
│       ├── connectTriki(timeout=5.0)
│       ├── set triki_connected = True/False
│       ├── Kalibracja offsetu żyroskopu (10 próbek)
│       └── Pętla: odczyt danych co 50ms
│
├── show_start(screen) ~linia 787
│   └── Menu startowe (Pegasus-style)
│
├── PĘTLA GRY (while triki_running):
│   ├── game_loop(screen, upgrades) ~linia 886
│   │   └── Zwraca (score, coins, max_combo, challenges) lub None
│   ├── calc_stars() – ocena 0-3
│   ├── Obsługa daily challenges
│   ├── Zapis highscore i ulepszeń
│   └── show_over(screen, ...) ~linia 891
│       └── Ekran końca gry z menu
│
└── pygame.quit()
```

## Główna pętla gry (game_loop)

```
while triki_running:
    clock.tick(FPS)  # 60 FPS
    
    # 1. Zdarzenia Pygame (klawiatura, QUIT)
    # 2. Pauza (P)
    # 3. Portal mode (bonus level) – osobna sekcja z continue
    # 4. Normalna rozgrywka:
    #    - Spawn przeszkód, monet, dronów, tarcz, portali, bossów
    #    - Aktualizacja pozycji
    #    - Kolizje (pociski→przeszkody, gracz→przeszkody, gracz→monety)
    #    - Mile stone, night cycle
    #    - Rysowanie: road, player, obstacles, coins, HUD
```

## Zmienne globalne Triki

| Zmienna | Typ | Opis |
|---------|-----|------|
| `triki_connected` | bool | Czy kontroler połączony |
| `triki_analog` | float | Wychylenie (-1.0 do 1.0) z żyroskopu X |
| `triki_raw` | tuple | (gx, gy, gz) surowe żyroskop |
| `triki_accel` | tuple | (ax, ay, az) akcelerometr |
| `triki_button` | bool | Stan przycisku (szeroko dostępny) |
| `triki_button_raw` | bool | Stan przycisku (surowy) |
| `triki_offset` | float | Offset kalibracji żyroskopu |
| `triki_battery` | int | Poziom baterii (0-100) |
| `triki_status_queue` | Queue | Komunikaty statusu z wątku BLE |
