from dataclasses import dataclass

from game.config.balance import DEBT_INTEREST_PER_MINUTE


@dataclass
class DebtAccount:
    """Schuld die ontstaat wanneer het saldo onder €0 komt.

    Koppelen: laat GameService bij `state.bankrupt` het tekort met `borrow()` lenen in plaats van te stoppen,
    roep `accrue_interest()` aan in de tick en voeg een endpoint toe dat `repay()` gebruikt.
    """

    amount: float = 0.0
    interest_rate_per_minute: float = DEBT_INTEREST_PER_MINUTE

    @property
    def active(self) -> bool:
        return self.amount > 0

    def borrow(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Het bedrag moet positief zijn.")
        self.amount += amount

    def accrue_interest(self, minutes: float) -> float:
        """Voegt rente toe over `minutes` minuten en geeft de toegevoegde rente terug."""
        if not self.active or minutes <= 0:
            return 0.0
        interest = self.amount * ((1 + self.interest_rate_per_minute) ** minutes - 1)
        self.amount += interest
        return interest

    def repay(self, amount: float) -> float:
        """Lost maximaal `amount` af en geeft terug hoeveel er echt is afgelost."""
        paid = max(0.0, min(amount, self.amount))
        self.amount -= paid
        return paid
