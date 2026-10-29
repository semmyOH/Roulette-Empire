from game.events.base import GameEvent

EVENT_CATALOG = {
    event.event_id: event
    for event in [
        GameEvent(
            event_id="jackpot_festival",
            name="Jackpot Festival",
            description="Hogere uitbetalingen aan alle tafels.",
            duration_seconds=60,
            payout_multiplier=1.5,
            reputation_change=5,
        ),
        GameEvent(
            event_id="new_casino_law",
            name="Nieuwe Casino Wetgeving",
            description="Strengere regels maken het runnen van het casino duurder.",
            duration_seconds=120,
            upkeep_multiplier=1.5,
        ),
        GameEvent(
            event_id="server_outage",
            name="Serverstoring",
            description="Storingen kosten geld en klanten.",
            duration_seconds=30,
            upkeep_multiplier=2.0,
            reputation_change=-5,
        ),
        GameEvent(
            event_id="sponsor_deal",
            name="Sponsordeal",
            description="Een sponsor betaalt een deel van de kosten.",
            duration_seconds=90,
            upkeep_multiplier=0.5,
            reputation_change=3,
            min_reputation=60,
        ),
    ]
}
