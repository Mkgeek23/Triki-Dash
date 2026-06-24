# System menu

## Ogólna koncepcja

Wszystkie ekrany menu mają styl Pegasus (Famicom/NES): czarne tło z gwiazdami, kolorowa ramka, opcje z migającym wskaźnikiem "►". Pełna kontrola zarówno przez Triki, jak i klawiaturę.

## Wspólne elementy

### `menu_draw_frame(screen, color)` ~linia 781
Rysuje ozdobną ramkę wokół ekranu: gruba linia (3px) w kolorze `color` z ozdobnymi nacięciami na górze.

### `make_menu_stars()` ~linia 769
Generuje listę 80 gwiazd o stałych pozycjach (x, y, brightness, radius). Używana we wszystkich ekranach.

### `draw_menu_stars(screen, stars, blink_frame)` ~linia 775
Rysuje gwiazdy z subtelnym migotaniem. Każda gwiazda ma przesuniętą fazę migotania (`i * 7`), co tworzy naturalny efekt.

### Sterowanie (wspólne we wszystkich ekranach)

| Akcja | Klawiatura | Triki |
|-------|-----------|-------|
| Następna opcja | ↓ / → | Potrząśnięcie |
| Poprzednia opcja | ↑ / ← | (brak) |
| Akceptuj | SPACJA / ENTER | Przycisk |
| Wyjście | ESC | (jeśli dostępne) |

Wykrywanie potrząsania:
```python
shake_mag = abs(triki_accel[0]) + abs(triki_accel[1]) + abs(triki_accel[2])
if shake_mag > 22000 and last_shake_mag < 17000 and now - last_tilt_time > 400:
    selected = (selected + 1) % len(options)
    last_tilt_time = now
last_shake_mag = shake_mag
```

## `show_start(screen)` ~linia 787

Menu główne, pierwszy ekran po uruchomieniu.

**Opcje:**
1. **NOWA GRA** – uruchamia `game_loop()`
2. **SKLEP** – otwiera `show_shop()`
3. **WYJŚCIE** – zamyka grę

**Dodatkowe elementy:**
- Tytuł "TRiKI RUNNER" (zielony, 56px) z kolorową linią pod spodem
- Status połączenia Triki na dole:
  - "Łączenie z Triki..." (szary) – podczas poszukiwania
  - "Triki: Połączony (Bateria: X%)" (zielony) – po sukcesie
  - "Triki: Nie znaleziony. Graj strzałkami." (czerwony) – po porażce
- Komunikat o sterowaniu na dole ekranu
- Gwiazdy w tle

## `show_over(screen, ...)` ~linia 891

Ekran po śmierci gracza.

**Opcje:**
1. **GRAJ PONOWNIE** – restart gry
2. **SKLEP** – otwiera `show_shop()`
3. **WYJŚCIE** – powrót do menu głównego

**Wyświetlane informacje:**
- "KONIEC GRY" (czerwony)
- Ocena gwiazdkowa (0-3 ★)
- Dystans, monety, rekord
- Najlepsza ocena
- Postęp daily challenges (X/3)

## `show_shop(screen, upgrades)` ~linia 673

Sklep ulepszeń, w którym gracz wydaje gwiazdki.

**Opcje:**
1. **Dłuższy sprint** – wydłuża czas sprintu o 50% na poziom (max 3)
2. **Większy magnes** – zwiększa zasięg magnesu o 40px na poziom (max 3)
3. **Dodatkowe życie** – +1 życie na start (max 2)
4. **POWRÓT** – wyjście ze sklepu

**Mechanika:**
- Koszt: `base + level * base // 2` (base=2)
- Wyświetla poziom (★/☆), koszt, "MAX" gdy fully upgraded
- Dźwięk przy kupnie (880Hz) lub błędzie (200Hz)
- Gwiazdki zdobywa się za wyniki w grze

## Przepływ między ekranami

```
main()
  └── show_start()
        ├── [NOWA GRA] → game_loop() → show_over()
        │                                 ├── [GRAJ PONOWNIE] → game_loop()
        │                                 ├── [SKLEP] → show_shop()
        │                                 └── [WYJŚCIE] → show_start()
        ├── [SKLEP] → show_shop() → show_start()
        └── [WYJŚCIE] → exit
```
