Prompt: Bouw Browsergame "Roulette Empire"
Je bent een ervaren full-stack gameontwikkelaar en softwarearchitect.
Ontwikkel een complete browsergame genaamd Roulette Empire, een idle/tycoon-managementspel waarin de speler een gokimperium opbouwt rond roulette.
Doel van de game
De speler begint met een startkapitaal van €100 en probeert door middel van roulette, automatisering, strategische upgrades en risicomanagement een zo groot mogelijk vermogen op te bouwen.
De gameplay moet een combinatie zijn van:
Idle Game
Tycoon/Management Game
Incremental Progression
Risk vs Reward Mechanieken
Technische Stack
Backend
Python 3
Flask
REST API architectuur
SQLite database
SQLAlchemy ORM
Frontend
HTML5
CSS3
Vanilla JavaScript (geen frameworks)
Data-opslag
SQLite
Permanente savegame-opslag
Automatisch opslaan
Architectuurvereisten
Gebruik een modulaire en uitbreidbare structuur zodat toekomstige systemen eenvoudig toegevoegd kunnen worden zonder bestaande code te herschrijven.
Voorbeeld:
Plain Text
/backend
app.py
routes/
services/
models/
database/
 
/frontend
css/
js/
templates/
 
/game
upgrades/
bots/
tournaments/
events/
reputation/
Pas principes toe zoals:
Separation of Concerns
DRY (Don't Repeat Yourself)
Object-Oriented Programming
Service Pattern
Configuratiebestanden voor balanswaarden
MVP Functionaliteiten (Eerste Versie)
Implementeer eerst uitsluitend onderstaande systemen.
1. Geldsysteem
Speler heeft:
Huidig saldo
Totale winst
Totale verliezen
Netto waarde
Voorbeeld:
Plain Text
Saldo: €100
Totale winst: €350
Totale verlies: €180
Netto winst: €170
2. Handmatige Roulette Spins
Knop:
Plain Text
[ Spin Roulette ]
Bij elke spin:
Willekeurige winst of verlies
Kansverdeling configureerbaar
Resultaat direct zichtbaar
Voorbeeld:
Plain Text
Je wint €12
Je verliest €8
Je wint €35
3. Upgradewinkel
Speler kan upgrades kopen.
MVP upgrades:
Lucky Wheel
Effect:
+5% winstkans
Startprijs:
Plain Text
€100
Better Tables
Effect:
+10% gemiddelde uitbetaling
Startprijs:
Plain Text
€250
Efficient Staff
Effect:
10% lagere onderhoudskosten
Startprijs:
Plain Text
€500
Upgradeprijzen moeten exponentieel stijgen.
Voorbeeld:
Plain Text
Nieuwe prijs = Basisprijs × 1.5^niveau
4. Onderhoudskosten
Het imperium heeft kosten.
Elke seconde:
Plain Text
saldo -= onderhoudskosten
Basis:
Plain Text
€1 per seconde
Moet zichtbaar zijn in de interface.
5. Automatische Bot
Upgrade:
Plain Text
Junior Roulette Bot
Effect:
Speelt automatisch elke 5 seconden
Bot kan:
Winst maken
Verlies maken
Balans moet eerlijk blijven.
6. Opslaan van Voortgang
Sla op:
Geld
Upgrades
Bots
Statistieken
Gebruik SQLite.
Opslaan:
Automatisch
Handmatig via knop
Toekomstige Systemen (Voorbereiden, Nog Niet Volledig Implementeren)
Maak alvast uitbreidbare interfaces/classes voor:
Schuldensysteem
Wanneer saldo < €0
Eigenschappen:
Schuldbedrag
Rente per minuut
Mogelijkheid tot aflossen
Reputatiesysteem
Waarden:
Plain Text
0 - 100
Invloed op:
Events
Sponsordeals
Toernooien
AI-Toernooien
Computertegenstanders strijden tegen speler.
Eigenschappen:
Ranking
Beloningen
Moeilijkheidsniveaus
Willekeurige Events
Voorbeelden:
Jackpot Festival
Nieuwe Casino Wetgeving
Serverstoring
Sponsordeal
Events kunnen:
Winsten verhogen
Kosten verhogen
Reputatie beïnvloeden
Risicoprofielen
Keuzes:
Veilig
Lage risico's
Lage opbrengsten
Gebalanceerd
Gemiddeld risico
Gemiddelde opbrengsten
Agressief
Hoge volatiliteit
Maniak
Extreem risico
Zeer hoge potentiële winsten
UI Vereisten
Toon minimaal:
Saldo
Netto winst
Onderhoudskosten
Actieve bots
Laatste spinresultaat
Upgradewinkel
Gebruik een moderne casino/tycoon-stijl:
Donkere achtergrond
Gouden accenten
Responsive design
Duidelijke statistieken
Output Vereisten
Genereer:
Volledige projectstructuur
Backend code (Flask)
Frontend code (HTML/CSS/JS)
SQLite models
API endpoints
Upgrade systeem
Save/load systeem
Uitleg van architectuurkeuzes
Installatie-instructies
Stapsgewijze uitbreidingshandleiding voor toekomstige features
Lever volledig werkende code aan en zorg ervoor dat het project direct lokaal gestart kan worden met:
Shell
pip install -r requirements.txt
python app.py
Geef geen pseudocode. Lever productieklare, uitvoerbare code.
Verbeteringen aangebracht
Veel concretere architectuurvereisten.
Duidelijke MVP-afbakening.
Balansregels voor upgrades toegevoegd.
Voorbereiding voor toekomstige systemen zonder scope-creep.
Expliciete output-eisen zodat AI minder snel onderdelen overslaat.
Schaalbare projectstructuur voor verdere ontwikkeling.