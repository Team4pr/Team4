from typing import List, Tuple, Optional, Set
from ship import Ship, ShipOrientation

class Grid:
    
    
    def __init__(self, size: int = 10):
        
        self.size = size  
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.ships: List[Ship] = []          
        self.shots: Set[Tuple[int, int]] = set()    
        self.hits: Set[Tuple[int, int]] = set()     
        self.misses: Set[Tuple[int, int]] = set()   

    def resize(self, new_size: int):
        
        self.size = new_size
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.ships.clear()
        self.shots.clear()
        self.hits.clear()
        self.misses.clear()

    def place_ship(self, ship: Ship, start_pos: Tuple[int, int], orientation: str) -> bool:
        
        if not self._is_valid_orientation(orientation):
            return False
            
        positions = self._calculate_ship_positions(ship.size, start_pos, orientation)
        if not positions:
            return False

        if not self._is_valid_placement(positions):
            return False

        ship.position = positions
        ship.orientation = ShipOrientation.HORIZONTAL if orientation == 'horizontal' else ShipOrientation.VERTICAL
        self.ships.append(ship)
        
        for pos in positions:
            self.grid[pos[0]][pos[1]] = ship
            
        return True

    def _calculate_ship_positions(self, size: int, start_pos: Tuple[int, int], 
                                orientation: str) -> Optional[List[Tuple[int, int]]]:
        
        if not self._is_within_grid(start_pos):
            return None
            
        positions = []
        row, col = start_pos

        for i in range(size):
            if orientation == 'horizontal':
                new_pos = (row, col + i)
            else:  
                new_pos = (row + i, col)

            if not self._is_within_grid(new_pos):
                return None
            positions.append(new_pos)

        return positions

    def _is_within_grid(self, pos: Tuple[int, int]) -> bool:
        
        row, col = pos
        return 0 <= row < self.size and 0 <= col < self.size

    def receive_shot(self, pos: Tuple[int, int]) -> Tuple[bool, Optional[Ship]]:
        
        if not self._is_within_grid(pos) or pos in self.shots:
            return False, None

        self.shots.add(pos)
        row, col = pos
        ship = self.grid[row][col]

        if ship is None:
            self.misses.add(pos)
            return False, None

        self.hits.add(pos)
        ship.take_hit(pos)
        return True, ship if ship.is_sunk() else None

    def get_cell_state(self, pos: Tuple[int, int]) -> str:
        
        if not self._is_within_grid(pos):
            return 'invalid'
            
        if pos in self.hits:
            return 'hit'
        if pos in self.misses:
            return 'miss'
        if self.grid[pos[0]][pos[1]] is not None:
            return 'ship'
        return 'empty'

    def _is_valid_placement(self, positions: List[Tuple[int, int]]) -> bool:
        
        for row, col in positions:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    adj_pos = (row + i, col + j)
                    if (self._is_within_grid(adj_pos) and 
                        self.grid[adj_pos[0]][adj_pos[1]] is not None):
                        return False
        return True

    def _is_valid_orientation(self, orientation: str) -> bool:
        
        return orientation in ['horizontal', 'vertical']

    def all_ships_sunk(self) -> bool:
        
        return all(ship.is_sunk() for ship in self.ships)

    def get_all_ship_positions(self) -> Set[Tuple[int, int]]:
        
        positions = set()
        for ship in self.ships:
            positions.update(ship.get_positions())
        return positions

    def get_shots_fired(self) -> Set[Tuple[int, int]]:
        
        return self.shots.copy()

    def get_hits(self) -> Set[Tuple[int, int]]:
        
        return self.hits.copy()

    def get_misses(self) -> Set[Tuple[int, int]]:
        
        return self.misses.copy()

    def clear(self):
        
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.ships.clear()
        self.shots.clear()
        self.hits.clear()
        self.misses.clear()

    def to_dict(self) -> dict:
        
        return {
            'size': self.size,
            'ships': [ship.to_dict() for ship in self.ships],
            'shots': list(self.shots),
            'hits': list(self.hits),
            'misses': list(self.misses)
        }

    
    def from_dict(cls, data: dict) -> 'Grid':
        
        grid = cls(data['size'])
        grid.shots = set(data['shots'])
        grid.hits = set(data['hits'])
        grid.misses = set(data['misses'])
        
        for ship_data in data['ships']:
            ship = Ship.from_dict(ship_data)
            grid.ships.append(ship)
            for pos in ship.position:
                grid.grid[pos[0]][pos[1]] = ship
                
        return grid

grid = Grid(size=15)  
ship = Ship("Battleship", 4)  
success = grid.place_ship(ship, (0, 0), "horizontal")  
hit, sunk_ship = grid.receive_shot((0, 0))  
state = grid.get_cell_state((0, 0))  