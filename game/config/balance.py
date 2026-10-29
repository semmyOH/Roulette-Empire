"""Balanswaarden van Roulette Empire.

Pas hier de getallen aan om het spel makkelijker of moeilijker te maken. De rest van de code leest
alles uit dit bestand, dus nergens anders staan "magische getallen".
"""

# Geld
STARTING_BALANCE = 100.0
# Onderhoud betaal je per botspin: elke keer dat een bot speelt kost dat €1. Zonder bots geen onderhoud.
UPKEEP_PER_BOT_SPIN = 1.0

# Tijd
# Langere pauzes (tabblad dicht, server uit) tellen niet mee: de speltijd staat dan stil.
MAX_TICK_SECONDS = 5.0
AUTOSAVE_INTERVAL_SECONDS = 30.0
HISTORY_SIZE = 15

# Roulette
MIN_BET = 1
# Hoger dan dit kan Lucky Wheel de winstkans van een inzet niet krijgen.
MAX_WIN_CHANCE = 0.75

# Upgrades: nieuwe prijs = basisprijs × UPGRADE_PRICE_GROWTH ^ niveau
UPGRADE_PRICE_GROWTH = 1.5

# Volgorde hier = volgorde in de winkel.
# effect: win_chance (winstkans × (1 + value × niveau)), payout (winst × (1 + value × niveau)),
#         upkeep (onderhoud × (1 - value) ^ niveau), bots (value extra bots per niveau)
UPGRADES = {
    "lucky_wheel": {
        "name": "Lucky Wheel",
        "description": "+5% winstkans per niveau",
        "base_price": 100,
        "effect": "win_chance",
        "value": 0.05,
    },
    "better_tables": {
        "name": "Better Tables",
        "description": "+10% uitbetaling per niveau",
        "base_price": 250,
        "effect": "payout",
        "value": 0.10,
    },
    "efficient_staff": {
        "name": "Efficient Staff",
        "description": "10% lagere onderhoudskosten per niveau",
        "base_price": 500,
        "effect": "upkeep",
        "value": 0.10,
    },
    "junior_bot": {
        "name": "Junior Roulette Bot",
        "description": "Zet elke 5 s €5 in, kost €1 onderhoud per spin",
        "base_price": 300,
        "effect": "bots",
        "value": 1,
    },
}

# Bots: elke bot zet elke 5 seconden €5 in op rood of zwart (winst +€5 of verlies -€5).
JUNIOR_BOT_INTERVAL_SECONDS = 5.0
JUNIOR_BOT_BET = 5

# Toekomstige systemen (nog niet actief in het spel)
DEBT_INTEREST_PER_MINUTE = 0.02
REPUTATION_START = 50
