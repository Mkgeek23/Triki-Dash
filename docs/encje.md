# Encje (klasy)

## `Particle` ~linia 78

Cząsteczki używane do efektów wizualnych.

| Atrybut | Opis |
|---------|------|
| `x, y` | Pozycja |
| `vx, vy` | Prędkość |
| `color` | Kolor RGB |
| `life` | Pozostały czas życia |
| `alive` | Czy aktywna |

Co klatkę: `update()` przesuwa, zmniejsza `life`, gasi gdy `life <= 0`.

## `Player` ~linia 179

Główna encja gracza.

**Atrybuty:**
- `x, y` – pozycja na drodze
- `lives` – życia (0 = koniec gry)
- `ammo, max_ammo` – amunicja (max 3, regeneracja 1/60 klatek)
- `boost_timer` – czas sprintu
- `shielded` – czy aktywna tarcza
- `combo` – aktualne combo
- `multiplier` – mnożnik punktów (1-10)
- `max_combo` – najwyższe combo w tej sesji
- `invincible_timer` – nieśmiertelność po stracie życia
- `special_coins` – zebrane złote monety
- `sprint_count` – liczba sprintów w tej sesji
- `dodge_streak` – liczba unikniętych przeszkód z rzędu

**Metody:**
- `update(val, total_coins)` – przesuwa gracza o `val * 7` (jeśli val nie jest None)
- `move_left()` / `move_right()` – przesunięcie o 40px
- `shoot()` – tworzy pocisk, zmniejsza ammo
- `get_rect()` – zwraca pygame.Rect do kolizji

**Rysowanie:** Kolorowy kwadrat z oczami, efekt ghost trail przy sprintach, poświata tarczy, iskierki boost.

## `Obstacle` ~linia 287

Przeszkody na drodze, także bossowie.

| Atrybut | Opis |
|---------|------|
| `x, y` | Pozycja |
| `size` | Rozmiar (0.8-1.2 x bazowy) |
| `color` | Kolor (czerwony) |
| `boss` | Czy to boss |
| `hp` | Życia (boss: 3-7) |
| `small` | Czy to fragment po zestrzeleniu |

**Boss:** większy (60px), ma pasek HP, po pokonaniu pokazuje "BOSS POKONANY!". Przy kolizji: gracz traci życie, boss znika.

## `CoinObj` ~linia 352

Monety do zebrania.

**Typy:**
| Typ | Kolor | Punkty | Special |
|-----|-------|--------|---------|
| normal | Żółty | 1 | Nie |
| silver | Srebrny | 2 | Nie |
| gold | Złoty | 5 | Tak |

Rysowanie: okrąg z glow efektem, złote mają płomień.

## `PortalObj` ~linia 396

Portal do strefy bonusowej. Pulsujący cyjanowy okrąg. Znika po dotknięciu lub po 180 klatkach.

## `Bullet` ~linia 424

Pocisk gracza. Leci w górę. Po trafieniu w przeszkodę: dzieli ją na 2 mniejsze lub niszczy. Po trafieniu w drona: -1 HP (dron ma 2 HP). Po trafieniu w tarczę: zbiera ją.

Rysowanie: cyjanowy pocisk z fioletowym trailerm.

## `Drone` ~linia 449

Latający wróg. Porusza się sinusoidalnie w poziomie (`x += sin(krok) * 2`). Wymaga 2 trafień. Po zniszczeniu: spawni tarczę (shield).

Rysowanie: czerwono-różowe koło z wirującymi kropkami.

## `Target` ~linia 489

Tarcza (power-up shield). Pulsuje, pokazuje mnożnik combo gracza. Po zebraniu: `player.shielded = True`.

## `Road` ~linia 527

Tło i droga.

**Elementy:**
- Tło: ciemne kosmiczne kolory (deep purple/blue) z delikatnym gradientem
- Gwiazdy: 80 stałych gwiazd z subtelnym migotaniem `_draw_starfield()`
- Droga: neonowy tor – fioletowa poświata na krawędziach, bardzo ciemne wnętrze
- Linie graniczne: niebiesko-cyjanowe, grubsze na krawędziach
- Pasy przerywane: neonowe cyjanowe z efektem glow (3 warstwy)
- Speed line'y: niebiesko-cyjanowe paski po bokach przy prędkości > 3
- Portal mode: fioletowe tło, 60 animowanych gwiazd, fioletowa droga

**`update(speed)`:** Przesuwa offset pasów (mod 80).

**`draw(screen, speed, tod, night, portal_mode)`:** Rysuje wszystko.
