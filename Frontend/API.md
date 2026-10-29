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
  "upkeep_per_second": 1.0,
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
- `balance` mag negatief worden door onderhoudskosten.

## Endpoints

### `GET /api/state`

Geeft `state` terug. De frontend vraagt dit elke seconde op, zo worden onderhoudskosten en botspins
zichtbaar. De backend bepaalt zelf (bijvoorbeeld op basis van verstreken tijd) hoeveel kosten er zijn
afgeschreven en hoeveel botspins er gespeeld zijn.

### `POST /api/spin`

Request:

```json
{ "bet_type": "red", "amount": 10 }
{ "bet_type": "number", "number": 17, "amount": 10 }
```

`bet_type` is `"red"`, `"black"`, `"even"`, `"odd"` of `"number"`. `number` (0-36) alleen bij `"number"`.
`amount` is een heel getal ≥ 1.

Response:

```json
{
  "result": { "number": 17, "color": "black", "net": 10.0 },
  "state": { "...": "..." }
}
```

Het wiel draait altijd naar `result.number`. Als de backend upgrades als "Lucky Wheel" toepast, moet
het getal kloppen met winst of verlies (bijvoorbeeld: inzet op rood en winst, dan een rood getal).

### `POST /api/upgrades/<id>/buy`

Response: `{ "state": { ... } }`

### `POST /api/save`

Response: `{ "saved_at": "2026-10-29T19:30:00Z" }`

De frontend roept dit aan bij de knop "Opslaan", elke 30 seconden en bij het sluiten van de pagina
(via `navigator.sendBeacon`, zonder body).

## Fouten

Bij een fout: een HTTP-statuscode 4xx/5xx met

```json
{ "error": "Onvoldoende saldo." }
```

De tekst van `error` wordt direct aan de speler getoond, dus schrijf die in het Nederlands.
