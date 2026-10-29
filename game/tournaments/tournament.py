from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Difficulty(Enum):
    EASY = ("Makkelijk", 0.9)
    NORMAL = ("Normaal", 1.0)
    HARD = ("Moeilijk", 1.15)

    def __init__(self, label: str, skill: float):
        self.label = label
        self.skill = skill  # Factor op de score van de AI-tegenstander.


@dataclass
class AIOpponent:
    name: str
    difficulty: Difficulty
    score: float = 0.0


@dataclass
class Tournament:
    """Een toernooi waarin de speler het opneemt tegen AI-tegenstanders.

    Koppelen: voeg een TournamentService toe die rondes speelt (bijvoorbeeld met RouletteService en
    een eigen GameState per deelnemer), scores bijhoudt en `reward_for()` uitkeert.
    """

    name: str
    difficulty: Difficulty
    entry_fee: float
    rewards: list[float]  # Beloning per plaats: rewards[0] voor de winnaar.
    opponents: list[AIOpponent] = field(default_factory=list)

    def ranking(self, player_name: str, player_score: float) -> list[tuple[str, float]]:
        scores = [(player_name, player_score)] + [(o.name, o.score) for o in self.opponents]
        return sorted(scores, key=lambda entry: entry[1], reverse=True)

    def rank_of(self, player_name: str, player_score: float) -> int:
        names = [name for name, _ in self.ranking(player_name, player_score)]
        return names.index(player_name) + 1

    def reward_for(self, rank: int) -> float:
        return self.rewards[rank - 1] if 1 <= rank <= len(self.rewards) else 0.0

    def play_round(self):
        raise NotImplementedError("Toernooien worden in een latere versie speelbaar.")
