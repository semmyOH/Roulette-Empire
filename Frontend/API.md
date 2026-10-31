# API-contract tussen frontend en backend

De frontend bevat geen spellogica. Saldo, spinresultaten, upgrades, onderhoudskosten en de bot worden
allemaal door de Flask-backend berekend. De frontend roept onderstaande endpoints aan (zie `js/api.js`).
Alle bedragen zijn in euro's (getal, mag decimalen hebben).

## Flask-koppeling

De HTML laadt de bestanden vanaf `/static/...`. In `backend/app.py` kan dat zo:

```python
app = Flask(
    __name__,
    template_folder="../Frontend/templates",
    static_folder="../Frontend",
    static_url_path="/static",
)

@app.route("/")
def index():
    return render_template("index.html")
```

## Spelstatus (`state`)

Elk endpoint dat de status verandert, stuurt de volledige nieuwe `state` terug.

```json
{
  "balance": 100.0,
  "total_won": 350.0,
  "total_lost": 180.0,
  "net_profit": 170.0,
  "total_upkeep": 42.0,
  "upkeep_per_spin": 1.0,
  "upkeep_per_round": 2.0,
  "bankrupt": false,
  "bots": { "active": 1, "interval_seconds": 5 },
  "upgrades": [
    {
      "id": "lucky_wheel",
      "name": "Lucky Wheel",
      "description": "+5% winstkans",
      "level": 0,
      "price": 100.0,
      "max_level": null
    }
  ],
  "history": [
    { "number": 17, "color": "black", "net": 10.0, "source": "player" },
    { "number": 0, "color": "green", "net": -5.0, "source": "bot" }
  ]
}
```

- `upgrades`: in de volgorde waarin ze in de winkel moeten staan. Verwachte id's: `lucky_wheel`,
  `better_tables`, `efficient_staff`, `junior_bot`. `price` is de prijs van het volgende niveau
  (`basisprijs × 1.5^niveau`). `max_level` is `null` als er geen maximum is.
- `history`: laatste spins, nieuwste eerst (de frontend toont alles wat binnenkomt, ±15 is genoeg).
  `color` is `"red"`, `"black"` of `"green"`. `net` is positief bij winst en negatief bij verlies
  (de inzet). `source` is `"player"` of `"bot"`.
- Bots zetten elke `bots.interval_seconds` €5 in op rood of zwart. Elke botspin kost onderhoud:
  `upkeep_per_spin` (€1, minder met Efficient Staff). `upkeep_per_round` is het totaal voor alle bots
  samen per ronde. Zonder bots is er geen onderhoud. Een bot speelt alleen als het saldo de inzet plus
  het onderhoud dekt, dus het saldo wordt nooit negatief.
- `bankrupt` is `true` als het saldo lager is dan de minimale inzet (€1). Dan worden spins geweigerd
  en toont de frontend de knop "Opnieuw beginnen".
- `total_upkeep`: totaal betaalde onderhoudskosten (telt niet mee in `total_lost`).

## Endpoints

### `GET /api/state`

Geeft `state` terug. De frontend vraagt dit elke seconde op, zo worden botspins en hun
onderhoudskosten zichtbaar. De backend bepaalt zelf (bijvoorbeeld op basis van verstreken tijd) hoeveel kosten er zijn
afgeschreven en hoeveel botspins er gespeeld zijn.

### `POST /api/spin`

Eén spin met één of meer inzetten (maximaal 60). Alle inzetten samen mogen niet meer zijn dan het saldo.

Request:

```json
{
  "bets": [
    { "bet_type": "red", "amount": 10 },
    { "bet_type": "dozen", "value": 1, "amount": 20 },
    { "bet_type": "street", "value": 4, "amount": 5 },
    { "bet_type": "number", "value": 17, "amount": 1 }
  ]
}
```

| `bet_type` | `value`                                    | Wint bij                  | Uitbetaling |
| ---------- | ------------------------------------------ | ------------------------- | ----------- |
| `red`, `black`, `even`, `odd` | geen                    | kleur / even / oneven (0 verliest) | 1:1 |
| `dozen`    | 1, 2 of 3 (1e 12 = 1-12, 2e 12 = 13-24, 3e 12 = 25-36) | getal in dat dozijn | 2:1 |
| `column`   | 1, 2 of 3 ("2 to 1": kolom 1 = 1, 4, 7 … 34) | getal in die kolom        | 2:1         |
| `street`   | 1 t/m 12 (straat 1 = 1-2-3, straat 12 = 34-35-36) | een van de 3 getallen | 11:1   |
| `number`   | 0 t/m 36                                   | precies dat getal         | 35:1        |

`amount` is een heel getal ≥ 1. Eén losse inzet zonder `bets`-lijst (`{ "bet_type": "red", "amount": 10 }`)
werkt ook.

Response:

```json
{
  "result": {
    "number": 12,
    "color": "red",
    "net": 45.0,
    "total_bet": 30,
    "source": "player",
    "bets": [
      { "bet_type": "dozen", "value": 1, "amount": 20, "net": 40.0 },
      { "bet_type": "street", "value": 1, "amount": 5, "net": -5.0 },
      { "bet_type": "column", "value": 3, "amount": 5, "net": 10.0 }
    ]
  },
  "state": { "...": "..." }
}
```

`net` is de winst of het verlies van alle inzetten samen; per inzet staat het in `bets`. Het wiel
draait altijd naar `result.number`. Lucky Wheel verhoogt de kans dat alle inzetten samen winst
opleveren; het getal klopt altijd met de uitkomst.

### `POST /api/upgrades/<id>/buy`

Response: `{ "state": { ... } }`

### `POST /api/save`

Response: `{ "saved_at": "2026-10-29T19:30:00Z" }`

De frontend roept dit aan bij de knop "Opslaan", elke 30 seconden en bij het sluiten van de pagina
(via `navigator.sendBeacon`, zonder body).

### `POST /api/reset`

Begint een nieuw spel (saldo €100, geen upgrades) en slaat dat direct op.

Response: `{ "state": { ... } }`

## Fouten

Bij een fout: een HTTP-statuscode 4xx/5xx met

```json
{ "error": "Onvoldoende saldo." }
```

De tekst van `error` wordt direct aan de speler getoond, dus schrijf die in het Nederlands.
