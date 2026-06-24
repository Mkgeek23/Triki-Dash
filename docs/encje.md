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

## `Bullet` ~linia 428

Pocisk gracza. Leci w górę. Po trafieniu w przeszkodę: dzieli ją na 2 mniejsze lub niszczy. Po trafieniu w drona: -1 HP (dron ma 2 HP). Po trafieniu w tarczę: zbiera ją.

Rysowanie: cyjanowy pocisk z fioletowym trailerm.

## `EnemyBullet` ~linia 452

Pocisk wroga (dronów i mini-bossów). Leci w dół. Kolizja z graczem: traci życie lub tarczę.

Rysowanie: czerwone koło z jaśniejszym wnętrzem.

## `Drone` ~linia 469

Latający wróg. Porusza się sinusoidalnie w poziomie (`x += sin(krok) * 2`). Wymaga 2 trafień. Po zniszczeniu: spawni tarczę (shield). Strzela pociskami `EnemyBullet` co 60-120 klatek od momentu spawnu (pierwszy strzał po 30-90 klatkach).

Rysowanie: czerwono-różowe koło z wirującymi kropkami.

## `Target` ~linia 517

Tarcza (power-up shield). Pulsuje, pokazuje mnożnik combo gracza. Po zebraniu: `player.shielded = True`.

## `MovingObstacle` ~linia 549

Ruchoma przeszkoda. Porusza się w dół z prędkością scrolla, jednocześnie oscyluje sinusoidalnie w poziomie. Nie opuszcza obszaru pasów. Pojawia się od zone 1 (score ≥ 2000) z prawdopodobieństwem 4%.

- `size` = 28px
- `move_speed` = 1.0-2.5 (sinusoidalna amplituda)
- Kolizja z graczem: strata życia lub tarczy

Rysowanie: ceglasty prostokąt z jaśniejszym wewnętrznym blokiem i migającą kreską wskazującą kierunek ruchu, obsługa night mode.

## `WallObstacle` ~linia 577

Blokada drogowa. Zajmuje 6 z 7 pasów, pozostawiając jedną lukę (losowy pas). Pojawia się od zone 2 (score ≥ 5000) z prawdopodobieństwem 2.5%.

- `gap_lane` – pas z przerwą (0-6)
- Kolizja: sprawdza czy gracz jest na zablokowanym pasie I czy jego prostokąt nachodzi na ścianę

Rysowanie: czerwone prostokąty na zablokowanych pasach, obsługa night mode.

## `MiniBoss` ~linia 605

Mini-boss pojawiający się co 3 fale (score co 3000, od 3 fali). Ma 3 HP. Po pojawieniu się zatrzymuje na górze ekranu i oscyluje w pionie, strzelając pociskami `EnemyBullet` co 40-90 klatek.

## `PowerUp` ~linia 593

Power-up zbierany na drodze. Pojawia się co 800-1200 dystansu. 5 typów:

| Typ | Kolor | Ikona | Efekt |
|-----|-------|-------|-------|
| `star` | Złoty | 5 kropek (gwiazdki) | Nieśmiertelność 5s (`player.invincible`) |
| `double` | Srebrny | Dwa okręgi | Podwójne monety 8s (`pt * 2`) |
| `slow` | Niebieski | Dwie elipsy (klepsydra) | Spowolnienie 4s (`scroll * 0.5`) |
| `rapid` | Cyjan | Trójkąt (błyskawica) | Szybkostrzelność 6s (max_ammo=6, cooldown=5) |
| `magnet` | Fioletowy | Okrąg + prostokąt | Magnes 5s (`m_range = WIDTH`) |

Rysowanie: kolorowe koło z glow efektem i białą ikoną wewnątrz. Unosi się (bob).

- `size` = 50px
- Bonus za zniszczenie: +50 punktów, efekt cząsteczkowy
- Kolizja z graczem: strata życia lub tarczy

Rysowanie: fioletowy/czerwony prostokąt z trzema wirującymi kropkami (wzór podobny do drim), obsługa night mode.

## `Fork` ~linia 768

Rozwidlenie trasy – gracz wybiera lewy (ryzykowny) lub prawy (bezpieczny) pas. Pojawia się co 1500-2500 dystansu.

**Losowanie nagród:**
- Lewy pas: losuje z `['coins', 'speed']` (więcej monet lub sprint)
- Prawy pas: losuje z `['shield', 'points']` (tarcza lub punkty)

**Działanie:**
- `timer` = 120 klatek (~2s), po czym fork się rozwiązuje
- `resolve(player, obstacles, coin_objs, scroll)` – sprawdza po której stronie środka drogi jest gracz, przyznaje nagrodę
- Rysowanie: półprzezroczysty overlay z trójkątnymi strzałkami w lewo/prawo i etykietami nagród

## `Road` ~linia 643

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

**`draw(screen, speed, tod, night, portal_mode, biome=0)`:** Rysuje wszystko. Parametr `biome` określa paletę kolorów (0-4, patrz BIOMES). Gwiazdy tylko w biome 0 (Kosmos).
