# Plan: Power-upy

**Cel:** Dodanie power-upów zbieranych w trakcie gry, które tymczasowo zmieniają rozgrywkę.

## Zadania

### System power-upów
- [_] Zdefiniować klasę `PowerUp` (lub rozszerzyć `Target`) z polami: typ, czas trwania, ikona
- [_] Power-up pojawia się na drodze jak tarcza, z charakterystycznym wyglądem
- [_] Maksymalnie 1 aktywny power-up na raz
- [_] Kolejność spawnu: losowa, co 800-1200 dystansu

### Nieśmiertelność (gwiazdka)
- [_] Efekt: gracz ignoruje kolizje z przeszkodami przez 5 sekund
- [_] Wizualnie: złota poświata wokół gracza, migotanie
- [_] Dźwięk: wysoki, przeciągły ton
- [_] Kolizja z bossem: boss traci 1 HP zamiast gracz tracić życie

### Podwójne monety
- [_] Efekt: każda zebrana moneta daje ×2 punktów przez 8 sekund
- [_] Wizualnie: monety mają podwójny cień/poświatę
- [_] Dźwięk: wyższy dźwięk zbierania

### Spowolnienie czasu
- [_] Efekt: prędkość przewijania spada o 50% na 4 sekundy
- [_] Wizualnie: delikatny niebieski filtr na całym ekranie
- [_] Dźwięk: spowolniony dźwięk tła

### Dodatkowy pocisk (szybkostrzelność)
- [_] Efekt: amunicja regeneruje się co 10 klatek zamiast 60, max ammo = 6 przez 6 sekund
- [_] Wizualnie: cyjanowa poświata wokół gracza
- [_] Dźwięk: szybszy dźwięk strzału

### Przyciąganie monet (magnet)
- [_] Efekt: ogromny magnes (cała szerokość ekranu) przez 5 sekund
- [_] Wszystkie monety na ekranie lecą do gracza
- [_] Wizualnie: linie przyciągania od monet do gracza

### Wygląd power-upów na drodze
- [_] Nieśmiertelność: złota gwiazdka (★)
- [_] Podwójne monety: srebrny diament (♦)
- [_] Spowolnienie: niebieski klepsydra (⏳)
- [_] Szybkostrzelność: cyjanowa błyskawica (⚡)
- [_] Magnes: fioletowy magnes (🧲)

## Modyfikowane pliki
- `game.py` – nowa klasa `PowerUp`, `Player` (obsługa efektów), `game_loop()` (spawn, timery, rysowanie)
- `docs/encje.md` – dokumentacja `PowerUp`
- `docs/mechaniki-gry.md` – sekcja power-upów
