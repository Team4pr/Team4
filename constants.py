"""
File containing all constats for use in the game
"""

## Grid sizes available 10x10 or 15x15
GRID_SIZES = [10, 15]

## Defined default grid size of 10x10
GRID_SIZE = 10

## Pixel size in the grid
CELL_SIZE = 40

## Holds ships of different names and sizes
SHIPS = {
    'Aircraft Carrier': 5,
    'Battleship': 4,
    'Submarine': 3,
    'Destroyer': 3,
    'Patrol Boat': 2
}

## Ui element colors
WATER_COLOR = '#1E90FF'
SHIP_COLOR = '#808080'
HIT_COLOR = '#FF0000'
MISS_COLOR = '#FFFFFF'

## Finds the SQLite database file
DB_NAME = 'battleship.db'