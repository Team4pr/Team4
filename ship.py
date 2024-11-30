
from dataclasses import dataclass, field  
from typing import List, Tuple  
from enum import Enum  


class ShipOrientation(Enum):
    HORIZONTAL = 'horizontal' 
    VERTICAL = 'vertical'     

@dataclass
class Ship:

    
    name: str 
    size: int  
    position: List[Tuple[int, int]] = field(default_factory=list)  
    orientation: ShipOrientation = ShipOrientation.HORIZONTAL 
    hits: List[Tuple[int, int]] = field(default_factory=list)

    def __post_init__(self):
        
        
        if self.size <= 0:
            raise ValueError("Ship size must be positive")
            

        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Ship name must be a non-empty string")
        
        
        self.position = list(dict.fromkeys(self.position))
        self.hits = list(dict.fromkeys(self.hits))
        

        if self.position and len(self.position) != self.size:
            raise ValueError(f"Position length ({len(self.position)}) must match ship size ({self.size})")

    def is_sunk(self) -> bool:
        
        return len(self.hits) == self.size

    def take_hit(self, position: Tuple[int, int]) -> bool:
        
        if not self.position:
            return False
            
        if position in self.position and position not in self.hits:
            self.hits.append(position)
            return True
        return False

    def get_positions(self) -> List[Tuple[int, int]]:
        
        return self.position.copy() 

    def is_hit_at(self, position: Tuple[int, int]) -> bool:
        
        return position in self.hits

    def get_damage_percentage(self) -> float:
        
        if not self.size:
            return 0.0
        return (len(self.hits) / self.size) * 100

    def is_valid_position(self, position: List[Tuple[int, int]]) -> bool:
        
        if len(position) != self.size:
            return False

        
        sorted_pos = sorted(position)
        
        
        rows = [pos[0] for pos in sorted_pos]
        cols = [pos[1] for pos in sorted_pos]
        
        if len(set(rows)) == 1:  
            return (max(cols) - min(cols) + 1 == self.size and 
                   self.orientation == ShipOrientation.HORIZONTAL)
        elif len(set(cols)) == 1:  
            return (max(rows) - min(rows) + 1 == self.size and 
                   self.orientation == ShipOrientation.VERTICAL)
        
        return False

    def set_position(self, position: List[Tuple[int, int]], 
                    orientation: ShipOrientation) -> bool:
        
        if not isinstance(orientation, ShipOrientation):
            return False
            
        self.orientation = orientation
        if self.is_valid_position(position):
            self.position = position
            return True
        return False

    def clear_hits(self):

        self.hits.clear()

    def __str__(self) -> str:
        
        status = "SUNK" if self.is_sunk() else f"Health: {100 - self.get_damage_percentage()}%"
        return f"{self.name} ({self.size}) - {status}"