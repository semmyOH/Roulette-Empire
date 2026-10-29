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
