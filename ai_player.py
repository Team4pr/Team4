from typing import Tuple, Optional, Set
import random
from player import Player
from ship import Ship
from constants import GRID_SIZE

class AIPlayer(Player):
   
    
    def __init__(self):
        super().__init__()
       
        self.last_hit = None                         
        self.potential_targets = []                  
        self.hit_positions: Set[Tuple[int, int]] = set()  
        self.hunting_mode = False                    
        self.hunt_direction = None                   
        self.first_hit = None                       
        
    def get_shot_position(self) -> Tuple[int, int]:
        
        try:
            
            if not hasattr(self, 'grid') or not self.grid:
                raise ValueError("Grid not initialized")

            
            if self.hunting_mode and self.hit_positions:
                position = self._get_hunting_shot()
            elif self.potential_targets:
                position = self._get_smart_target()
            else:
                position = self._get_random_shot()

           
            if not self._is_valid_target(position):
                position = self._get_safe_random_shot()

            return position

        except Exception as e:
            print(f"Error in get_shot_position: {e}")
            return self._get_safe_random_shot()

    def _get_safe_random_shot(self) -> Tuple[int, int]:
        
        available = [
            (r, c) 
            for r in range(self.grid.size) 
            for c in range(self.grid.size)
            if self._is_valid_target((r, c))
        ]
        return random.choice(available) if available else (0, 0)

    def update_strategy(self, hit: bool, position: Tuple[int, int]):
        
        if hit:
            if not self.hunting_mode:
                self.hunting_mode = True
                self.first_hit = position
            self.hit_positions.add(position)
            self._update_potential_targets(position)
        else:
            if self.hunting_mode:
                self._adjust_hunting_strategy()

    def _adjust_hunting_strategy(self):
       
        if self.hunt_direction:
            
            self.hunt_direction = self._get_perpendicular_direction()
            if not self._get_next_directional_shot():
                self._reset_hunting()

    def _get_hunting_shot(self) -> Tuple[int, int]:
       
        if not self.hunt_direction:
            if len(self.hit_positions) > 1:
                self.hunt_direction = self._determine_ship_direction()
                return self._get_next_directional_shot()
            return self._get_smart_target()
        
        next_shot = self._get_next_directional_shot()
        if next_shot:
            return next_shot
            
        self.hunt_direction = self._get_perpendicular_direction()
        next_shot = self._get_next_directional_shot()
        if next_shot:
            return next_shot
            
        self._reset_hunting()
        return self._get_random_shot()
        
    def _get_smart_target(self) -> Tuple[int, int]:
        
        while self.potential_targets:
            target = self.potential_targets.pop(0)
            if self._is_valid_target(target):
                return target
        return self._get_random_shot()
        
    def _get_random_shot(self) -> Tuple[int, int]:
       
        grid_size = self.grid.size
        
        
        sector_size = 5 if grid_size > 10 else 3
        sectors = []
        
        
        for base_row in range(0, grid_size, sector_size):
            for base_col in range(0, grid_size, sector_size):
                sector_density = 0
                valid_positions = []
                
                for r in range(base_row, min(base_row + sector_size, grid_size)):
                    for c in range(base_col, min(base_col + sector_size, grid_size)):
                        if (r, c) not in self.shots:
                            valid_positions.append((r, c))
                            sector_density += self._calculate_area_density((r, c))
                
                if valid_positions:
                    sectors.append((valid_positions, sector_density / len(valid_positions)))
        
        
        if sectors:
            
            total_density = sum(density for _, density in sectors)
            if total_density > 0:
                r = random.random() * total_density
                current = 0
                for positions, density in sectors:
                    current += density
                    if r <= current:
                        return random.choice(positions)
        
        
        available_positions = [
            (row, col) for row in range(grid_size) for col in range(grid_size)
            if (row, col) not in self.shots
        ]
        return random.choice(available_positions) if available_positions else (0, 0)
        
    def _update_potential_targets(self, position: Tuple[int, int]):
        
        row, col = position
        grid_size = self.grid.size
        
        
        search_radius = 2 if grid_size > 10 else 1
        
        
        adjacent = []
        for r in range(-search_radius, search_radius + 1):
            for c in range(-search_radius, search_radius + 1):
                if r == 0 and c == 0:
                    continue
                new_pos = (row + r, col + c)
                if self._is_valid_target(new_pos):
                    
                    priority = 1.0 / (abs(r) + abs(c))
                    adjacent.append((new_pos, priority))
        
        
        adjacent.sort(key=lambda x: x[1], reverse=True)
        new_targets = [pos for pos, _ in adjacent if pos not in self.potential_targets]
        
        
        if len(self.hit_positions) > 1:
            direction = self._determine_ship_direction()
            if direction:
                new_targets.sort(key=lambda pos: 
                    self._calculate_target_priority(pos, direction))
        
        self.potential_targets.extend(new_targets)

    def _calculate_target_priority(self, position: Tuple[int, int], direction: str) -> float:
        
        priority = 0.0
        
       
        for hit_pos in self.hit_positions:
            distance = abs(position[0] - hit_pos[0]) + abs(position[1] - hit_pos[1])
            priority += 1.0 / (distance + 1)
        
        
        density = self._calculate_area_density(position)
        priority += density * 2
        
        
        if direction == 'horizontal' and any(pos[0] == position[0] for pos in self.hit_positions):
            priority *= 1.5
        elif direction == 'vertical' and any(pos[1] == position[1] for pos in self.hit_positions):
            priority *= 1.5
            
        return priority

    def _calculate_area_density(self, position: Tuple[int, int], radius: int = 2) -> float:
        
        row, col = position
        valid_positions = 0
        empty_positions = 0
        
        for r in range(row - radius, row + radius + 1):
            for c in range(col - radius, col + radius + 1):
                if self._is_valid_target((r, c)):
                    valid_positions += 1
                    if (r, c) not in self.shots:
                        empty_positions += 1
                        
        return empty_positions / max(valid_positions, 1)
        
    def _determine_ship_direction(self) -> Optional[str]:
       
        hits = list(self.hit_positions)
        if len(hits) < 2:
            return None
            
        row_diff = hits[-1][0] - hits[-2][0]
        col_diff = hits[-1][1] - hits[-2][1]
        
        if row_diff != 0:
            return 'vertical'
        if col_diff != 0:
            return 'horizontal'
        return None
        
    def _get_next_directional_shot(self) -> Optional[Tuple[int, int]]:
       
        if not self.hunt_direction or not self.first_hit:
            return None
            
        row, col = self.first_hit
        if self.hunt_direction == 'horizontal':
            possible = [(row, col + 1), (row, col - 1)]
        else:  
            possible = [(row + 1, col), (row - 1, col)]
            
        valid_shots = [pos for pos in possible if self._is_valid_target(pos)]
        return valid_shots[0] if valid_shots else None
        
    def _is_valid_target(self, pos: Tuple[int, int]) -> bool:
        
        row, col = pos
        grid_size = self.grid.size
        return (0 <= row < grid_size and 
                0 <= col < grid_size and 
                pos not in self.shots)
                
    def _reset_hunting(self):
        
        self.hunting_mode = False
        self.hunt_direction = None
        self.first_hit = None
        self.hit_positions.clear()
        
    def _is_adjacent_to_sunk_ship(self, pos: Tuple[int, int], ship: Ship) -> bool:
       
        for ship_pos in ship.position:
            if abs(pos[0] - ship_pos[0]) <= 1 and abs(pos[1] - ship_pos[1]) <= 1:
                return True
        return False
        
    def _get_perpendicular_direction(self) -> str:
        
        return 'vertical' if self.hunt_direction == 'horizontal' else 'horizontal'
        
    def _is_in_line_with_hits(self, pos: Tuple[int, int], direction: str) -> bool:
       
        for hit in self.hit_positions:
            if direction == 'horizontal' and pos[0] == hit[0]:
                return True
            if direction == 'vertical' and pos[1] == hit[1]:
                return True
        return False