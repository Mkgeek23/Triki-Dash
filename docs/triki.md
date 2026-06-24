# Integracja Triki

## Sterownik BLE (`TrikiPy.py`)

Plik `TrikiPy.py` zawiera klasę `TrikiDevice` obsługującą komunikację przez Bluetooth Low Energy z kontrolerem Triki.

**Struktura danych (`TrikiData`):**
```python
TrikiData(ax, ay, az, gx, gy, gz)
```
Wszystkie wartości to surowe 16-bitowe liczby całkowite, spakowane jako `'<hhhhhh'`.

## Wątek Triki (`triki_thread` ~linia 581)

Uruchamiany jako daemon przed pokazaniem menu:

```python
thread = threading.Thread(target=triki_thread, daemon=True)
thread.start()
```

**Przebieg `_triki_loop()` (~linia 584):**
1. Próba połączenia `connectTriki(timeout=5.0)` – jeśli fail, komunikat "Triki nie znaleziony"
2. Odczyt baterii `getBatteryLevel()`
3. Start strumienia danych `startTriki()`
4. Kalibracja: 10 próbek `gx` → średnia jako `triki_offset`
5. Główna pętla: odczyt co 50ms, aktualizacja `triki_raw`, `triki_accel`, `triki_analog`
6. Wykrywanie przycisku (zbocze narastające)

## Przetwarzanie danych

### Żyroskop → `triki_analog`
```python
gx_corrected = triki_raw[0] - triki_offset  # kompensacja dryftu
if abs(gx_corrected) < 50:
    triki_analog = 0.0
else:
    triki_analog = max(-1.0, min(1.0, gx_corrected / 1000.0))
```
W menu nieużywany – zastąpiony akcelerometrem.

### Akcelerometr → potrząsanie w menu
```python
shake_mag = abs(triki_accel[0]) + abs(triki_accel[1]) + abs(triki_accel[2])
# Próg: > 22000, zbocze: < 17000
```
W spoczynku około 16384 (1g). Potrząśnięcie daje pik >25000.

### Żyroskop → sprint w grze
```python
shake_mag = abs(gy) + abs(gz)
if shake_mag > 2500 and last_shake_mag < 1000:
    # aktywacja sprintu
```

## Sterowanie w grze

### Ruch (żyroskop X)
```python
player.update(triki_analog if triki_connected else None, total_coins)
```
Wartość -1.0 (lewo) do 1.0 (prawo). `player.update()` przesuwa gracza o `val * 7` pikseli.

### Strzelanie (przycisk)
```python
if triki_button and not portal_mode:
    bullet = player.shoot()
```

### Sprint (potrząsanie)
```python
shake_mag = abs(gy) + abs(gz)
if shake_mag > 2500 and last_shake_mag < 1000 and not boost_active:
    player.boost_timer = boost_dur
```

## HUD Triki

Podczas gry wyświetlane:
- `draw_tilt_bar()` – pasek wychylenia (zielony/pomarańczowy/czerwony)
- `draw_button_indicator()` – okrąg sygnalizujący przycisk
- Bateria w lewym górnym rogu (jeśli `triki_battery >= 0`)

## Ograniczenia

- `triki_button` wymaga `global triki_button` w funkcjach menu, aby móc go wyzerować
- W menu `triki_button` jest używany tylko do akceptacji opcji (nie do strzelania)
- Żyroskop ma dryft – wymaga kalibracji `triki_offset` przy starcie
