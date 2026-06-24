# Mechaniki gry

## Podstawowe parametry

| Stała | Wartość | Opis |
|-------|---------|------|
| `LANE_COUNT` | 7 | Liczba pasów |
| `LANE_WIDTH` | 114px | Szerokość pasa |
| `SCROLL_SPEED_BASE` | 4 | Bazowa prędkość przewijania |
| `FPS` | 60 | Klatki na sekundę |
| `PLAYER_SIZE` | 36 | Rozmiar gracza |
| `PORTAL_INTERVAL` | 3000 | Co ile dystansu pojawia się portal |
| `MILESTONE_INTERVAL` | 1000 | Co ile dystansu kamień milowy |
| `BOOST_DURATION` | 120 | Czas sprintu w klatkach |
| `NIGHT_INTERVAL` | 900 | Co ile ticków noc |
| `NIGHT_DURATION` | 300 | Jak długo trwa noc |

## Narastająca prędkość

Prędkość przewijania (`scroll`) rośnie liniowo z dystansem:

```python
scroll = min(SCROLL_SPEED_BASE + score // 500, 14)
```

- Start: 4 (przy score = 0)
- Co 500 dystansu: +1
- Maksimum: 14

Zastąpiło poprzedni system czasowy (+0.3 co 600 ticków).

## Fale przeciwników

Co 1000 dystansu rozpoczyna się nowa fala:

1. **Komunikat** "FALA X!" na środku ekranu (90 ticków)
2. **Burst przeszkód** – 3-5 przeszkód pojawia się naraz
3. **Przerwa** – 90 ticków (1.5s) bez przeszkód, tylko monety
4. **Normalny spawn** do następnej fali

Boss pojawia się co **5 fal** (fala 5, 10, 15...) zamiast co 2000 dystansu.

## Strefy trudności

| Strefa | Dystans | Nazwa | Charakterystyka |
|--------|---------|-------|-----------------|
| 0 | 0-1999 | (łatwa) | Podstawowe stawki, rzadkie grupy |
| 1 | 2000-4999 | ŚREDNIA | Zwiększony spawn, więcej grup |
| 2 | 5000-9999 | TRUDNA | Wysokie prawdopodobieństwo spawnu |
| 3 | 10000+ | SZALONA | Maksymalne tempo, częste grupy i duże przeszkody |

Przy wejściu do nowej strefy: komunikat "STREFA X – NAZWA" (120 ticków).

**Skalowanie ze scroll:**
- `spawn_chance`: 0.35 → 0.85 (prawdopodobieństwo spawnu przeszkody)
- `group_chance`: 0.1 → 0.4 (szansa na grupę zamiast pojedynczej)
- `big_chance`: 0.1 → 0.3 (szansa na dużą przeszkodę)
- `coin_spawn_chance`: 0.3 → 0.65
- `gold_chance`: 0.03 → 0.10
- `silver_chance`: 0.1 → 0.20

## Przeszkody

- Pojawiają się losowo na pasach, spawn_tick co ~20-70 klatek (zależy od scroll)
- Typy: normalne (kolor czerwony), zróżnicowane rozmiary (0.8-1.2x), małe (0.5x), duże (1.5x)
- Grupy: 2-3 małe przeszkody obok siebie (spawn_group_obstacle)
- Po zestrzeleniu: dzielą się na 2 mniejsze części (jeśli nie są już małe)
- Kolizja z graczem: traci życie, jeśli nie ma tarczy
- Boss: pojawia się co 5 fal, ma pasek HP (3-7 życia w zależności od boss_count)

### Nowe typy przeszkód (Plan 02)

| Typ | Strefa | Opis | Punkty |
|-----|--------|------|--------|
| `MovingObstacle` | 1+ (2000) | Oscyluje w poziomie, spawn 4% | 10 |
| `WallObstacle` | 2+ (5000) | Blokada 6/7 pasów, spawn 2.5% | – |
| `MiniBoss` | Fala 3,6,9... | 3 HP, strzela, +50 pkt | 50 |

### Wrogowie strzelający

- `Drone` od Plan 02: strzela czerwonymi pociskami co 60-120 klatek
- `MiniBoss`: strzela co 40-90 klatek, porusza się w pionie
- Pociski wroga (`EnemyBullet`): lecą w dół, kolizja = strata życia/tarczy

## Monety

- Zwykłe (żółte): 1 punkt
- Srebrne: 2 punkty
- Złote: 5 punktów, liczą się do `special_coins`
- Szansa na złotą/srebrną rośnie ze scroll
- Magnes: przyciąga monety w promieniu 80px + bonus z ulepszeń
- W portalu: pojawiają się co 8 klatek, dają ×50 punktów

## Portal (bonus level)

- Pojawia się co 3000 dystansu (`PORTAL_INTERVAL`)
- Trwa 5 sekund (300 klatek)
- Tło kosmiczne z gwiazdami, fioletowa droga
- Gracz może się poruszać (naprawiono – wcześniej sterowanie było zablokowane)
- Spadają monety do zebrania
- Po zakończeniu: wszystkie monety znikają, gra wraca do normy

## Combo i mnożnik

- Każde zestrzelenie/przeszkoda/moneta/zmiana pasa zwiększa `player.combo`
- Mnożnik punktów: `min(int(combo * 0.1) + 1, 15)` (progresywny, max 15x)
- Combo reset: natychmiast po kolizji (przeszkoda, pocisk wroga)
- Co 10 combo bez resetu: gracz dostaje tarczę (shield)
- Pasek combo na dole ekranu

## Łańcuchy monet (CoinChain)

- 5-8 monet pojawiających się w jednym pionowym rzędzie na losowym pasie
- 20% szansa zamiast zwykłej monety
- Połączone złotą linią
- Bonus za zebranie wszystkich: +50 punktów + flare efekt + cząsteczki

## Premia za szybki slalom

- Każda zmiana pasa (strzałki) rejestruje `diff_tick`
- Jeśli kolejna zmiana w ciągu < 30 ticków (< 500ms): bonus
- Bonus za serię: `min(slalom_count, 5) * 5` (max +25 za serię 5)
- Slalom_count resetuje się po przerwie > 30 ticków

## Perfect clear (fala bez szwanku)

- `wave_clear = True` na początku każdej fali
- Ustawiane na `False` przy każdej kolizji z przeszkodą/wrogiem
- Jeśli fala kończy się z `wave_clear = True`: +100 punktów + flare efekt

## Power-upy

Power-up pojawia się na drodze co 800-1200 dystansu (maksymalnie 1 aktywny). Po zebraniu aktywuje się na określony czas.

| Power-up | Czas | Efekt | Wizualnie |
|----------|------|-------|-----------|
| ⭐ Nieśmiertelność | 5s | Ignorowanie kolizji | Migotanie gracza |
| ♦ Podwójne monety | 8s | ×2 punkty za monety | HUD "x2 MONETY" |
| ⏳ Spowolnienie | 4s | Scroll -50% | Niebieski filtr (50,80,180,40) |
| ⚡ Szybkostrzelność | 6s | max_ammo=6, shoot_cooldown=5, auto-regen | Cyjanowa poświata wokół gracza |
| 🧲 Magnes | 5s | Przyciąganie z całego ekranu | Fioletowa poświata wokół gracza |

**Implementacja:** `PowerUp` ~linia 593, lista `powerups`, zmienne `active_powerup` / `powerup_timer` w `game_loop`.

**Spawn:** Gdy `active_powerup is None` i `score - last_powerup_score >= random(800, 1200)`.
**Kolekcja:** Kolizja z graczem → ustawia `active_powerup` i `powerup_timer` z `POWERUP_DURATION`.
**Efekty:** Modyfikacja `effective_scroll` (slow), `m_range` (magnet), `player.max_ammo`/`shoot_cooldown` (rapid), `player.invincible` (star), `pt * 2` (double).

## Sprint (boost)

- Klawisz S lub potrząśnięcie Triki (gy + gz > 2500)
- Czas trwania: 120 klatek + bonus z ulepszeń
- Podwaja prędkość przewijania (`BOOST_SPEED_MUL = 2.0`)
- Limit: 1 sprint na sekwencję (boost_active blokada)

## Night cycle

- Co 900 ticków (`NIGHT_INTERVAL`) robi się ciemno
- Noc trwa 300 ticków (`NIGHT_DURATION`)
- Półprzezroczysta niebieska nakładka (alpha 0-180)
- Działa tylko poza portalem

## Strzelanie

- Amunicja: 3 pociski
- Regeneracja: 1 pocisk co 60 klatek
- Pociski lecą w górę, niszczą przeszkody, drony i tarcze
- Drony wymagają 2 trafień
- Po zniszczeniu drona: gracz dostaje tarczę
- Pociski wroga (EnemyBullet): lecą w dół, gracz traci życie/tarczę przy kolizji

## Biomy

Co 2000 dystansu zmienia się biom otoczenia. Zmiana: fade do czerni i wyjście w nowej palecie.

| # | Nazwa | Kolory | Efekt | 
|---|-------|--------|-------|
| 0 | Kosmos | Fiolet, neonowy cyjan | Gwiazdy (domyślny) |
| 1 | Lód | Błękit, biel, jasnoniebieski | Płatki śniegu |
| 2 | Wulkan | Czerwień, pomarańcz, czerń | Iskry unoszące się do góry |
| 3 | Mgła | Szarości, blade fiolety | Warstwa mgły z gradientem |
| 4 | Cyber | Neonowy róż, cyjan, czerń | Glitch – losowe kolorowe linie |

Każdy biom ma własną paletę kolorów w `BIOMES` (game.py ~linia 47):
- `bg` – kolory tła (gradient)
- `road` – kolor drogi
- `edge` – kolor krawędzi
- `line` – kolor linii pasów
- `dash` – kolor przerywanych linii
- `accent` – kolor akcentów
- `glow` – kolor poświaty
- `spdline` – kolor speed line'ów

Efekty wizualne definiowane w `BIOME_EFFECTS`:
- `snow` – białe cząsteczki spadające po przekątnej (Lód)
- `sparks` – pomarańczowe cząsteczki unoszące się do góry (Wulkan)
- `fog` – półprzezroczysty gradient na całym ekranie (Mgła)
- `glitch` – losowe kolorowe linie poziome (Cyber)

## Tarcza (shield)

- Pojawia się jako Target na drodze
- Po zebraniu: chroni przed 1 kolizją
- Wizualnie: fioletowy okrąg wokół gracza
- Niszczy się po trafieniu w przeszkodę

## Życia

- Start: 1 + bonus z ulepszeń (life_level)
- Po stracie życia: krótka nieśmiertelność (60 klatek)
- Przy 0 życia: koniec gry
- Maksymalnie wyświetlane: 3 serca, powyżej "+N"

## Kamienie milowe

- Co 1000 dystansu (`MILESTONE_INTERVAL`)
- Dźwięk, komunikat "Dystans: X" na środku ekranu
- Przywracają 1 sztukę amunicji
