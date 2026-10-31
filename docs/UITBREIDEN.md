# Uitbreidingshandleiding

Algemene regel: spelregels komen in `game/`, het koppelen aan de server in `backend/services/`, en een
nieuw endpoint in `backend/routes/`. Voeg bij elke uitbreiding een test toe in `tests/`.

## Een upgrade toevoegen

### Met een bestaand effect (geen code nodig)

Voeg een item toe aan `UPGRADES` in `game/config/balance.py`:

```python
"vip_lounge": {
    "name": "VIP Lounge",
    "description": "+20% uitbetaling per niveau",
    "base_price": 2000,
    "effect": "payout",
    "value": 0.20,
    "max_level": 5,  # optioneel
},
```

Hij verschijnt direct in de winkel, wordt opgeslagen en werkt mee in elke spin.

### Met een nieuw soort effect

1. Voeg een veld toe aan `Modifiers` in `game/modifiers.py`, bijvoorbeeld `bot_bet_multiplier: float = 1.0`.
2. Maak een subklasse van `Upgrade` in `game/upgrades/effects.py` met een eigen `apply()`.
3. Registreer hem in `EFFECT_TYPES` in `game/upgrades/catalog.py` en gebruik de naam bij `"effect"`.
4. Gebruik het nieuwe veld waar het effect moet werken (bijvoorbeeld in `BotService`).

## Een nieuw soort inzet toevoegen (bijvoorbeeld split of hoek)

1. Voeg de soort toe aan `BetType` en `PAYOUT_RATIOS` in `game/roulette.py`.
2. Heeft hij een `value` nodig, voeg dan een regel toe aan `VALUE_RULES` (laagste, hoogste, foutmelding).
3. Bepaal in `covered_numbers()` welke getallen ermee winnen.
4. Voeg in `Frontend/js/betting.js` een vak toe met `createSpot()`, met zijn plek op de tafel voor
   bureaublad en mobiel, en zet het label en de uitbetaling in `BET_TYPES` in `Frontend/js/config.js`.
5. Voeg een test toe in `tests/test_game_logic.py`.

## Een nieuwe bot toevoegen

1. Maak `game/bots/<naam>.py` met een subklasse van `Bot`: geef `bot_type`, `interval_seconds` en
   `choose_bet()`.
2. Laat `BotService` meerdere bottypes beheren: maak van `self.bot` een lijst of dict, met per type een
   eigen timer in `GameState` en een eigen upgrade die het aantal bepaalt.
3. Voeg de balanswaarden toe aan `game/config/balance.py`.

## Schuldensysteem koppelen (`game/debt/`)

1. Voeg `debt: DebtAccount` toe aan `GameState` en laad/bewaar hem in `SaveService` (kolom `Player.debt`
   bestaat al).
2. In `GameService._tick()`: als het saldo onder €0 komt, leen het tekort met `debt.borrow()` en zet het
   saldo op €0 in plaats van te stoppen. Roep `debt.accrue_interest(elapsed / 60)` aan. Pas ook
   `GameState.bankrupt` aan, zodat spelen met schuld mogelijk blijft.
3. Voeg `POST /api/debt/repay` toe in een nieuw bestand `routes/debt_routes.py` dat `debt.repay()` gebruikt,
   en registreer de blueprint in `routes/__init__.py`.
4. Stuur `debt` mee in `GameService._serialize()` en toon het in de frontend.
5. Rente aanpassen: `DEBT_INTEREST_PER_MINUTE` in `balance.py`.

## Reputatie koppelen (`game/reputation/`)

1. Voeg `reputation: Reputation` toe aan `GameState` en bewaar `value` in `Player.reputation`.
2. Verander reputatie bij gebeurtenissen, bijvoorbeeld via `GameEvent.reputation_change` of bij grote winsten.
3. Gebruik `reputation.influence()` (-1 tot +1) als factor voor eventkansen, sponsordeals of
   toernooibeloningen, en `reputation.allows(minimum)` om iets vrij te spelen.

## Willekeurige events koppelen (`game/events/`)

1. Nieuwe events voeg je toe in `game/events/catalog.py`.
2. Maak een `EventScheduler` in `services/__init__.py` en geef hem aan `GameService`.
3. In `_tick()`: roep `maybe_start(reputation, elapsed)` aan, bewaar het actieve event met zijn eindtijd
   in `GameState`, en verwerk `reputation_change` bij de start.
4. In `_modifiers()`: roep `event.apply(modifiers)` aan voor het actieve event. Omdat alles via
   `Modifiers` loopt, werken spins, bots en onderhoud direct mee.
5. Stuur het actieve event mee in de status, zodat de frontend een melding kan tonen.

## Risicoprofielen koppelen (`game/risk_profiles/`)

1. Bewaar het gekozen profiel-id bij de speler (nieuwe kolom in `Player`).
2. Maak een bot die `RiskProfile.make_bet(balance, rng)` gebruikt in `choose_bet()`.
3. Voeg `POST /api/risk-profile` toe om een profiel te kiezen, en een keuzemenu in de frontend.

## AI-toernooien koppelen (`game/tournaments/`)

1. Maak `services/tournament_service.py` die een `Tournament` aanmaakt met `AIOpponent`s.
2. Speel rondes met `RouletteWheel` en een eigen `GameState` per deelnemer; vermenigvuldig de score van
   AI-tegenstanders met `difficulty.skill`.
3. Bepaal de plaats met `rank_of()` en keer `reward_for(rank)` uit aan de speler.
4. Voeg endpoints toe in `routes/tournament_routes.py` (aanmelden, status, resultaat).

## Database aanpassen

`db.create_all()` maakt alleen nieuwe tabellen aan, geen nieuwe kolommen in bestaande tabellen. Heb je een
kolom toegevoegd, verwijder dan tijdens het ontwikkelen `backend/database/roulette_empire.db`. Voor
echte spelers is een migratietool als Flask-Migrate de volgende stap.
