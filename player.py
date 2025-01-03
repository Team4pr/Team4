import random
from grid import Grid
from ship import Ship
from ship import SHIPS

class Player:
    
    
    def __init__(self):
       
        self.grid = Grid()                 
        self.shots = []         
        self.remaining_ships = list(SHIPS.items())      
        self.placed_ships = {}        

    def place_ship(self, ship_name, size, start_pos, 
                  orientation):
        
        
        if ship_name not in [s[0] for s in self.remaining_ships]:
            return False
            
       
        ship = Ship(ship_name, size)
        
        
        if self.grid.place_ship(ship, start_pos, orientation):
            
            self.placed_ships[ship_name] = ship
            self.remaining_ships.remove((ship_name, size))
            return True
            
        return False

    def place_ships_randomly(self):
        
        attempts = 0
        max_attempts = 500  
        original_remaining = self.remaining_ships.copy()
        
        while self.remaining_ships and attempts < max_attempts:
            ship_name, size = self.remaining_ships[0]
            orientation = random.choice(['horizontal', 'vertical'])
            
            
            valid_positions = self._get_valid_positions(size, orientation)
            if valid_positions:
                pos = random.choice(valid_positions)
                if self.place_ship(ship_name, size, pos, orientation):
                    continue
                    
            attempts += 1
            
           
            if attempts % 50 == 0:
                self.grid.clear()
                self.remaining_ships = original_remaining.copy()
                self.placed_ships.clear()
                attempts = 0
        
        
        if self.remaining_ships:
            self.remaining_ships = original_remaining
            self.placed_ships.clear()
            self.grid = Grid(self.grid.size)
            return False
            
        return True

    def receive_shot(self, position):
       
        self.shots.append(position)
        return self.grid.receive_shot(position)

    def all_ships_sunk(self):
        
        return all(ship.is_sunk() for ship in self.placed_ships.values())

    def _get_valid_positions(self, ship_size, orientation):
       
       ## Holds all valid positions
        valid_positions = []
        grid_size = self.grid.size
        
        ## Allowes the ship to be placed in any row since its horizontal
        if orientation == 'horizontal':
            max_row = grid_size
            max_col = grid_size - ship_size + 1

        ## when the ship is vertical place it in any column
        else:
            max_row = grid_size - ship_size + 1
            max_col = grid_size
        
       
        for row in range(max_row):
            for col in range(max_col):
                positions = self.grid._calculate_ship_positions(ship_size, (row, col), orientation)
                if positions and self.grid._is_valid_placement(positions):
                    valid_positions.append((row, col))
                    
        return valid_positions

    
    def get_remaining_ships(self):
       
        return self.remaining_ships

    def get_ship_positions(self, ship_name):
       
        if ship_name in self.placed_ships:
            return self.placed_ships[ship_name].get_positions()
        return []

    def get_shots_fired(self):
        
        return self.shots.copy()

    def get_hits(self):
        
        return [pos for pos in self.shots if self.grid.get_cell_state(pos) == 'hit']

    def get_misses(self):
        
        return [pos for pos in self.shots if self.grid.get_cell_state(pos) == 'miss']