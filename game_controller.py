from player import Player
from ai_player import AIPlayer
from grid import Grid
from ship import SHIPS

class GameController:
    def __init__(self):
        self.player = None
        self.ai_player = None
        self.current_turn = None
        self.game_over = False
        self.selected_position = None
        self.grid_size = Grid().size  
        self.main_window = None
        self.stats = {
            'total_shots': 0,
            'hits': 0,
            'misses': 0
        }

    def start_new_game(self):
        self.player = Player()
        self.ai_player = AIPlayer()
        
        self.current_turn = 'player'
        self.game_over = False
        
        # Reset statistics for new game
        self.stats.update({
            'total_shots': 0,
            'hits': 0,
            'misses': 0
        })
        
        # AI places its ships randomly
        self.ai_player.place_ships_randomly()
        return True
    



    ### placing ships
    def place_player_ship(self, ship_name, start_pos, orientation):
        if self.player is None:
            return False
            
        success = self.player.place_ship(ship_name, SHIPS[ship_name], start_pos, orientation)
        
        if success and not self.player.remaining_ships:
            self.start_gameplay()
            
        return success
        
    def place_player_ships_randomly(self):
        if self.player is None:
            return False
        
        success = self.player.place_ships_randomly()
        if success:
            self.start_gameplay()
        return success
    






    ## gameplay
    def start_gameplay(self):
        if not self.player or not self.ai_player:
            return False
            
        if self.player.remaining_ships or self.ai_player.remaining_ships:
            return False
            
        self.current_turn = 'player'
        return True

    def process_player_shot(self, position):
        if self.current_turn != 'player':
            return {'valid': False}
            
        if self.ai_player.grid.get_cell_state(position) in ['hit', 'miss']:
            return {'valid': False}
            
        hit, sunk_ship = self.ai_player.receive_shot(position)
        self.stats['total_shots'] += 1
        if hit:
            self.stats['hits'] += 1
        else:
            self.stats['misses'] += 1
            
        result = {
            'valid': True,
            'hit': hit,
            'sunk': sunk_ship is not None,
            'ship_name': sunk_ship.name if sunk_ship else None,
            'game_over': False
        }
        
        if hit and self.ai_player.all_ships_sunk():
            self.end_game()
            result['game_over'] = True
            result['winner'] = 'player'
        else:
            self.current_turn = 'ai'
            
        return result
        
    def process_ai_turn(self):
        if self.current_turn != 'ai':
            return {'valid': False}
        
        position = self.ai_player.get_shot_position()
        
        hit, sunk_ship = self.player.receive_shot(position)
        
        result = {
            'valid': True,
            'position': position,
            'hit': hit,
            'sunk': sunk_ship is not None,
            'ship_name': sunk_ship.name if sunk_ship else None,
            'game_over': False
        }
        
        if hit and self.player.all_ships_sunk():
            self.end_game()
            result['game_over'] = True
            result['winner'] = 'ai'
        else:
            self.current_turn = 'player'
        
        return result

    def end_game(self):
        self.game_over = True
        self.current_turn = None
        self.selected_position = None

    def get_cell_state(self, is_player_grid, position):
        grid = self.player.grid if is_player_grid else self.ai_player.grid
        return grid.get_cell_state(position)

    def set_main_window(self, main_window):
        self.main_window = main_window
        main_window.game_controller = self

    def get_current_turn(self):
        return self.current_turn