# Architectuur

## Projectstructuur

```text
backend/                 Flask-server (HTTP, database, opslaan)
  app.py                 Startpunt: maakt de app, koppelt routes en database
  config.py              Serverinstellingen (paden, poort, debug)
  requirements.txt
  database/db.py         SQLAlchemy-instantie en het aanmaken van tabellen
  models/                Databasetabellen: Player, PlayerUpgrade, Spin
  routes/                REST-endpoints (game_routes, shop_routes) en foutafhandeling
  services/              Applicatielogica, één service per verantwoordelijkheid
    game_service.py      Centrale facade: tijd, onderhoud, bots, autosave, status
    roulette_service.py  Eén spin spelen en verwerken
    bot_service.py       Bots laten spelen naarmate de tijd verstrijkt
    upgrade_service.py   Upgrades kopen en effecten berekenen
    save_service.py      Spelstatus laden uit en opslaan in SQLite

game/                    Spellogica zonder Flask of database
  config/balance.py      ALLE balanswaarden (prijzen, kosten, kansen)
  roulette.py            Roulette-regels: vakken, kleuren, inzetten, het wiel
  state.py               GameState: de status van een speler in het geheugen
  modifiers.py           Bundelt effecten (winstkans, uitbetaling, onderhoud, bots)
  errors.py              Fouten met Nederlandse tekst voor de speler
  upgrades/              Upgrade-basisklasse, effecttypes en de winkelcatalogus
  bots/                  Bot-basisklasse en JuniorRouletteBot
  debt/                  Voorbereid: schuldensysteem
  reputation/            Voorbereid: reputatie 0-100
  events/                Voorbereid: willekeurige events
  tournaments/           Voorbereid: AI-toernooien
  risk_profiles/         Voorbereid: risicoprofielen

Frontend/                HTML, CSS en vanilla JavaScript (zie Frontend/API.md)
tests/                   Unittests voor spellogica en API
```

## Hoe een verzoek loopt

```text
browser ──fetch──> routes/ ──> GameService ──> RouletteService / BotService / UpgradeService
                                   │                    │
                                   │                    └─> game/ (regels, upgrades, bots)
                                   └─> SaveService ──> models/ ──> SQLite
```

1. De frontend vraagt elke seconde `GET /api/state` op en stuurt acties (`spin`, `buy`, `save`, `reset`).
2. Een route doet niets anders dan JSON lezen, `GameService` aanroepen en JSON teruggeven.
3. `GameService` verwerkt eerst de verstreken tijd (onderhoudskosten, botspins) en voert daarna de actie uit.
4. Fouten (`GameError`) worden in `routes/errors.py` omgezet in `{"error": "..."}` met status 400/404.

## Architectuurkeuzes

**Separation of Concerns.** Er zijn drie lagen: `routes` (HTTP), `services` (applicatielogica) en `game`
(spelregels). `game/` weet niets van Flask of SQLite. Daardoor is de spellogica los te testen
(`tests/test_game_logic.py`) en kan dezelfde code later ook gebruikt worden door bijvoorbeeld toernooien
met AI-spelers.

**Service Pattern.** Elke service heeft één taak. `GameService` is de enige ingang voor de routes. De
services krijgen hun afhankelijkheden via de constructor (`services/__init__.py`), zodat je ze in tests
kunt vervangen (de API-tests gebruiken bijvoorbeeld een nep-klok).

**Configuratie voor balans.** Alle getallen die de moeilijkheid bepalen staan in
`game/config/balance.py`. De winkel wordt daar zelfs uit opgebouwd: een upgrade toevoegen met een
bestaand effecttype kan zonder code te schrijven.

**OOP en uitbreidbaarheid.** `Upgrade` en `Bot` zijn abstracte basisklassen. Een nieuw effect of een
nieuwe bot is een nieuwe subklasse; bestaande code hoeft niet te veranderen. Alle effecten komen samen in
`Modifiers`, zodat ook events en risicoprofielen later op dezelfde manier invloed kunnen hebben.

**Status in het geheugen, opslaan in SQLite.** De spelstatus staat tijdens het spelen in het geheugen
(`GameState`) en wordt opgeslagen:

- handmatig via de knop "Opslaan" (`POST /api/save`);
- automatisch elke 30 seconden (`AUTOSAVE_INTERVAL_SECONDS`), door zowel de server als de frontend;
- bij het sluiten van de pagina en bij het afsluiten van de server.

Er is één savegame (speler 1). Een `threading.RLock` zorgt dat gelijktijdige verzoeken de status niet
door elkaar halen.

**Eerlijke roulette.** Het wiel is een echt Europees wiel (37 vakken). De server bepaalt het getal; de
frontend draait er alleen naartoe. Per spin kun je op meerdere vakken tegelijk inzetten: getallen
(35:1), straten (11:1), dozijnen en kolommen (2:1) en rood/zwart/even/oneven (1:1). Welke getallen bij
een inzet horen, staat op één plek: `covered_numbers()` in `game/roulette.py`. Lucky Wheel verhoogt de
kans dat alle inzetten samen winst opleveren door een deel van de verliezende spins om te zetten in een
winnend getal, zodat getal, kleur en uitkomst altijd kloppen. Bots gebruiken
hetzelfde wiel en dezelfde upgrades als de speler.

**Tijd.** Onderhoud en bots lopen op basis van verstreken tijd tussen verzoeken. Een pauze telt maximaal
`MAX_TICK_SECONDS` (5 s) mee: als de pagina dicht is of de server uit staat, staat de speltijd stil.

**Bots en onderhoud.** Elke bot zet elke 5 seconden €5 in op rood of zwart: hij wint €5 of verliest
€5. Elke botspin kost €1 onderhoud (`UPKEEP_PER_BOT_SPIN`), dus 2 bots kosten €2 per ronde. Zonder
bots is er geen onderhoud. Efficient Staff verlaagt het bedrag per niveau met 10%. Een bot speelt
alleen als het saldo de inzet plus het onderhoud dekt (€6), dus het saldo wordt nooit negatief.

**Blut.** Heb je minder dan de minimale inzet (€1), dan stoppen de bots, worden spins geweigerd en
toont de frontend "Opnieuw beginnen". Het schuldensysteem (`game/debt/`) is voorbereid om dit later te
vervangen.

## Database

| Tabel             | Inhoud                                                                    |
| ----------------- | ------------------------------------------------------------------------- |
| `players`         | saldo, totale winst/verlies/onderhoud, bot-timer, reputatie, schuld       |
| `player_upgrades` | niveau per upgrade (het aantal bots = niveau van `junior_bot`)            |
| `spins`           | de laatste 15 spins, zodat de geschiedenis na een herstart terug is       |

De kolommen `reputation` en `debt` bestaan al voor de toekomstige systemen.

## API

Zie `Frontend/API.md` voor alle endpoints en de JSON-structuur.
