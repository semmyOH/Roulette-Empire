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

## 31-10-2026: Meerdere inzetten, dozijnen, kolommen en straten (branch `feature/meerdere-inzetten`)

- Je kunt nu per spin op meerdere vakken tegelijk inzetten. Kies een fiche (€1, €5, €10, €25 of €100)
  en klik op de vakken; de fiches stapelen zich op het bord.
- Nieuwe inzetten: 1e/2e/3e 12 (dozijnen, 2:1), "2 to 1" (kolommen, 2:1) en straten (3 getallen op een
  rij, 11:1).
- Knoppen "Ongedaan maken", "×2" en "Wissen". Na een spin blijven de inzetten liggen, zodat je ze
  opnieuw kunt spelen; winnende vakken lichten groen op.
- Op mobiel staat de tafel rechtop: dozijnen links, straten rechts, "2 to 1" onderaan.
- Backend: `POST /api/spin` neemt een lijst `bets` en geeft de uitkomst per inzet terug. Een inzet
  gebruikt nu `value` in plaats van `number` (zie `Frontend/API.md`).
- Lucky Wheel werkt op alle inzetten samen: het verhoogt de kans dat de spin in totaal winst oplevert.
- Tests uitgebreid voor de nieuwe inzetten en meerdere inzetten per spin.
