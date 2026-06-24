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
| `BOSS_INTERVAL` | 2000 | Co ile dystansu pojawia się boss |
| `MILESTONE_INTERVAL` | 1000 | Co ile dystansu kamień milowy |
| `BOOST_DURATION` | 120 | Czas sprintu w klatkach |
| `NIGHT_INTERVAL` | 900 | Co ile ticków noc |
| `NIGHT_DURATION` | 300 | Jak długo trwa noc |

## Przeszkody

- Pojawiają się losowo na pasach, spawn_tick co ~15-30 klatek (zależy od wyniku)
- Typy: normalne (kolor czerwony), zróżnicowane rozmiary (0.8-1.2x)
- Po zestrzeleniu: dzielą się na 2 mniejsze części (jeśli nie są już małe)
- Kolizja z graczem: traci życie, jeśli nie ma tarczy
- Boss: pojawia się co 2000 dystansu, ma pasek HP (3-7 życia w zależności od boss_count)

## Monety

- Zwykłe (żółte): 1 punkt
- Srebrne: 2 punkty
- Złote: 5 punktów, liczą się do `special_coins`
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

- Każde zestrzelenie/przeszkoda zwiększa combo
- Co 5 combo: mnożnik punktów +1, flare efekt
- Próg zmiany mnożnika: 0, 5, 10, 15, 20... combo
- Maksymalny mnożnik: 10
- Pasek combo na dole ekranu

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
