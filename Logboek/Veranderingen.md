- hier komen onze aanpassingen/updates in.

## 29-10-2026: Frontend roulette (branch `feature/frontend-roulette`)

- `Frontend/templates/index.html`: speelscherm met statistieken (saldo, netto winst, totale winst/verlies,
  onderhoudskosten, actieve bots), roulettewiel, inzetbord, upgradewinkel en laatste spins.
- `Frontend/css/style.css`: donkere casino-stijl met gouden accenten, responsive tot telefoonformaat.
- `Frontend/js/`: opgesplitst in modules:
  - `config.js`: instellingen (API-adres, intervallen, wielvolgorde)
  - `api.js`: alle fetch-calls naar de backend
  - `wheel.js`: tekent en draait het wiel
  - `betting.js`: inzetbord (rood/zwart/even/oneven/getal)
  - `ui.js`: weergave van statistieken, winkel, geschiedenis en meldingen
  - `Javascript.JS`: startpunt dat alles koppelt
- `Frontend/API.md`: welke endpoints en JSON de frontend van de Flask-backend verwacht.
- De spellogica zit niet in de frontend. Zonder backend toont de pagina "Geen verbinding met de server".
- Melding "Je bent blut!" met knop "Opnieuw beginnen" (`POST /api/reset`).
- De fiche "Max" loopt mee met het saldo (dat door botspins verandert).
- Onderhoud wordt getoond per ronde (alle bots samen) en per botspin.

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

## 29-10-2026: Branches samengevoegd

- `feature/frontend-roulette` en `feature/backend-game` zijn in `main` gemerged. De game start nu met
  `python app.py` vanuit de map `backend` (zie `README.md`).
