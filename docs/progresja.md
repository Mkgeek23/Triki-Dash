# Progresja

## System gwiazdek

Po każdej grze gracz otrzymuje 0-3 gwiazdki na podstawie:

| Warunek | Gwiazdki |
|---------|----------|
| Dystans ≥ 500 | +1 |
| Dystans ≥ 2000 i monety ≥ 10 | +1 |
| Dystans ≥ 5000 i monety ≥ 30 i combo ≥ 10 | +1 |

Jeśli wszystkie 3 daily challenges są zrobione: dodatkowa +1 gwiazdka.

Wzór: `calc_stars(score, coins, max_combo)` ~linia 660.

## Sklep ulepszeń (`show_shop` ~linia 673)

Gracz wydaje gwiazdki na ulepszenia.

### Ulepszenia

| Klucz | Nazwa | Max poziom | Efekt na poziom |
|-------|-------|-----------|-----------------|
| `sprint_level` | Dłuższy sprint | 3 | +50% czasu sprintu |
| `magnet_level` | Większy magnes | 3 | +40px zasięgu magnesu |
| `life_level` | Dodatkowe życie | 2 | +1 życie na start |

### Koszt

```python
def upgrade_cost(level, base):
    return base + level * base // 2
```

| Poziom | Koszt (base=2) |
|--------|----------------|
| 0→1 | 2 ★ |
| 1→2 | 3 ★ |
| 2→3 | 5 ★ |
| 3→MAX | - |

## Pliki zapisu

### `triki_upgrades.json`
```json
{
    "sprint_level": 0,
    "magnet_level": 0,
    "life_level": 0,
    "stars": 0
}
```
Funkcje: `load_upgrades()`, `save_upgrades(data)` ~linia 106.

### `triki_challenges.json`
```json
{
    "date": "2026-06-24",
    "challenges": [
        {"type": "coins", "desc": "Zbierz 20 monet", "target": 20, "progress": 0, "done": false},
        ...
    ]
}
```
3 losowe wyzwania dziennie z puli 15. Funkcje: `load_challenges()`, `save_challenges(data)` ~linia 135.

### Typy wyzwań

| Typ | Przykład | Śledzone w |
|-----|----------|-----------|
| `coins` | "Zbierz 20 monet" | Każda zebrana moneta |
| `dodge` | "Uniknij 5 przeszkód z rzędu" | `player.dodge_streak` |
| `distance` | "Przebiegnij 2000" | `score` |
| `sprint` | "Użyj sprintu 3 razy" | `player.sprint_count` |
| `special` | "Zbierz 3 specjalne monety" | `player.special_coins` |
| `shoot` | "Zestrzel 2 przeszkody" | Licznik trafień / drone kills |

### `triki_highscore.txt`
```
<dystans>,<gwiazdki>
```
Np. `4200,3`. Funkcje: `load_highscore()`, `save_highscore(score, stars)` ~linia 642.

### `triki_total_coins.txt`
```
<liczba>
```
Życiowa suma zebranych monet. Funkcje: `load_total_coins()`, `save_total_coins(n)` ~linia ~95.

## Bonus za wszystkie wyzwania

Po grze, jeśli wszystkie 3 dzienne wyzwania są zrobione:
```python
stars = min(3, stars + 1)  # +1 dodatkowa gwiazdka (max 3)
upgrades['stars'] += 1
```
