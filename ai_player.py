from typing import Tuple
import random
from player import Player

class AIPlayer(Player):
    def __init__(self):
        super().__init__()
        self.attacked_positions = set()  # Track all attacked positions

    def get_shot_position(self) -> Tuple[int, int]:
        return self._get_random_shot()

    def _get_random_shot(self) -> Tuple[int, int]:
        available_positions = [
            (row, col) 
            for row in range(self.grid.size) 
            for col in range(self.grid.size) 
            if (row, col) not in self.attacked_positions
        ]
        if available_positions:
            position = random.choice(available_positions)
            self.attacked_positions.add(position)  # Mark this position as attacked
            return position
        return (0, 0)  # Default return if no available positions

    def _is_valid_target(self, pos: Tuple[int, int]) -> bool:
        row, col = pos
        grid_size = self.grid.size
        return (0 <= row < grid_size and 0 <= col < grid_size and pos not in self.attacked_positions)
