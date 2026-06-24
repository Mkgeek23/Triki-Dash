# Plan: Power-upy

**Cel:** Dodanie power-upów zbieranych w trakcie gry, które tymczasowo zmieniają rozgrywkę.

## Zadania

### System power-upów
- [x] Zdefiniować klasę `PowerUp` z polami: typ, czas trwania, ikona
- [x] Power-up pojawia się na drodze z charakterystycznym wyglądem (koło z ikoną + glow)
- [x] Maksymalnie 1 aktywny power-up na raz (spawn tylko gdy `active_powerup is None`)
- [x] Spawn: co 800-1200 dystansu

### Nieśmiertelność (gwiazdka)
- [x] Efekt: gracz ignoruje kolizje przez 5s (przez `player.invincible = 300`)
- [x] Wizualnie: migotanie (existing invincible blink)
- [x] Kolizja z bossem: boss traci HP (automatyczne przez istniejącą logikę)

### Podwójne monety
- [x] Efekt: każda zebrana moneta daje ×2 punktów przez 8s
- [x] Wizualnie: HUD indicator "x2 MONETY"
- [x] Dźwięk: wyższy dźwięk zbierania (n/z – brak osobnego dźwięku)

### Spowolnienie czasu
- [x] Efekt: prędkość przewijania spada o 50% na 4s
- [x] Wizualnie: niebieski filtr (50,80,180,40) na całym ekranie
- [x] Wizualnie: "SPOWOLNIENIE" w HUD

### Dodatkowy pocisk (szybkostrzelność)
- [x] Efekt: max_ammo = 6, shoot_cooldown = 5, auto-regen co 10 ticków przez 6s
- [x] Wizualnie: cyjanowa poświata (0,200,255,60) wokół gracza
- [x] Wizualnie: "SZYBKOSTRZELNOŚĆ" w HUD

### Przyciąganie monet (magnet)
- [x] Efekt: magnes na całą szerokość ekranu przez 5s (`m_range = WIDTH`)
- [x] Wizualnie: fioletowa poświata (180,80,255,60) wokół gracza
- [x] Wizualnie: "MAGNES" w HUD

### Wygląd power-upów na drodze
- [x] Nieśmiertelność: złote koło z 5 kropkami (gwiazdki)
- [x] Podwójne monety: srebrne koło z dwoma okręgami
- [x] Spowolnienie: niebieskie koło z klepsydrą (2 elipsy)
- [x] Szybkostrzelność: cyjanowe koło z trójkątem (błyskawica)
- [x] Magnes: fioletowe koło z okręgiem i prostokątem

## Modyfikowane pliki
- `game.py` – nowa klasa `PowerUp`, `Player` (obsługa efektów), `game_loop()` (spawn, timery, rysowanie)
- `docs/encje.md` – dokumentacja `PowerUp`
- `docs/mechaniki-gry.md` – sekcja power-upów
