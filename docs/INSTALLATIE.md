# Installatie

## Benodigd

- Python 3.10 of nieuwer (getest met 3.12)
- Een moderne browser

## Starten

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Open daarna <http://localhost:5000>.

De savegame komt in `backend/database/roulette_empire.db` en wordt automatisch aangemaakt. Verwijder dit
bestand om helemaal opnieuw te beginnen (of gebruik "Opnieuw beginnen" als je blut bent).

Tip: gebruik een virtuele omgeving, zodat de pakketten niet in je algemene Python komen:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
```

## Instellingen (omgevingsvariabelen, optioneel)

| Variabele               | Standaard                             | Betekenis                               |
| ----------------------- | ------------------------------------- | --------------------------------------- |
| `PORT`                  | `5000`                                | Poort van de server                     |
| `FLASK_DEBUG`           | `1`                                   | `0` zet de debugmodus en auto-reload uit |
| `ROULETTE_DATABASE`     | `backend/database/roulette_empire.db` | Pad naar de savegame                    |
| `ROULETTE_FRONTEND_DIR` | `Frontend`                            | Map met `templates/`, `css/` en `js/`   |

## Tests

Vanuit de hoofdmap van de repo:

```bash
python -m unittest discover -s tests -v
```

De tests gebruiken een tijdelijke database en raken je savegame niet aan.
