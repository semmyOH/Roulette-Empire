"""Fouten die de speler te zien krijgt. De tekst wordt direct in de interface getoond."""


class GameError(Exception):
    """Een actie mag niet, bijvoorbeeld door onvoldoende saldo."""


class InvalidBetError(GameError):
    """De inzet klopt niet (verkeerd type, bedrag of getal)."""


class UnknownUpgradeError(GameError):
    """Er bestaat geen upgrade met dit id."""
