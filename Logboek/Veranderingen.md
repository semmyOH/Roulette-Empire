- hier komen onze aanpassingen/updates in.

## 29-10-2026: Backend en spellogica (branch `feature/backend-game`)

- Verder gebouwd op de basis in `backend/`: Flask-app met `create_app()`, SQLite via SQLAlchemy en de
  routes verplaatst van `services/` naar `routes/`.
- `backend/services/`: GameService (tijd, onderhoud, bots, autosave), RouletteService, BotService,
  UpgradeService en SaveService.
- `backend/models/`: Player, PlayerUpgrade en Spin.
- `game/`: spellogica zonder Flask (roulette-regels, upgrades, Junior Roulette Bot), alle balanswaarden in
  `game/config/balance.py`, en voorbereide klassen voor schulden, reputatie, events, toernooien en
  risicoprofielen.
- Bots zetten elke 5 seconden €5 in (winst +€5 of verlies -€5). Elke botspin kost €1 onderhoud
  (2 bots = €2 per ronde, geen bots = geen onderhoud). Een bot speelt alleen als er €6 is.
- Heb je minder dan €1 (de minimale inzet), dan ben je blut: de bots stoppen en je kunt opnieuw
  beginnen (`POST /api/reset`).
- `tests/`: unittests voor de spellogica en de API.
- `docs/`: installatie, architectuur en uitbreidingshandleiding.
- `.gitignore` toegevoegd; `__pycache__` en de database staan niet meer in git.
- `README.md` bevat nu alleen hoe je de game start. De oorspronkelijke opdracht staat nog in de
  git-geschiedenis (commit `ad0c267`).
- Om de complete game te spelen moeten `feature/backend-game` en `feature/frontend-roulette` allebei
  in `main` gemerged worden.
