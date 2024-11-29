from typing import Tuple, Optional, Dict, Any, List, Union
from models.player import Player
from models.ai_player import AIPlayer
from models.grid import Grid
from models.ship import Ship, ShipOrientation
from database.db_manager import DatabaseManager
from utils.constants import (
    GRID_SIZE, 
    HIT_COLOR, 
    MISS_COLOR, 
    WATER_COLOR, 
    SHIP_COLOR,
    SHIPS  
)
from PyQt6.QtCore import QTimer
import random  
import logging

class GameController:
    def __init__(self, db_manager: DatabaseManager):
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        self.player = None
        self.ai_player = None
        self.current_turn = None
        self.game_over = False
        self.selected_position = None
        self.grid_size = 10  
        self.main_window = None
        self.game_state = 'setup'  
        self.stats = {
            'total_shots': 0,
            'hits': 0,
            'misses': 0,
            'games_played': 0,
            'games_won': 0,
            'current_game_duration': 0
        }
        self.logger.info("Game controller initialized")
        
    def start_new_game(self) -> bool:
        self.player = Player(grid_size=self.grid_size)
        self.ai_player = AIPlayer()
        self.ai_player.grid.resize(self.grid_size)
        
        self.current_turn = 'player'
        self.game_over = False
        self.selected_position = None
        self.game_state = 'setup'
        
        # Reset statistics for new game
        self.stats.update({
            'total_shots': 0,
            'hits': 0,
            'misses': 0,
            'current_game_duration': 0
        })
        
        # AI places its ships randomly
        self.ai_player.place_ships_randomly()
        return True
        
    def start_gameplay(self) -> bool:
        if not self.player or not self.ai_player:
            return False
            
        if self.player.remaining_ships or self.ai_player.remaining_ships:
            return False
            
        self.game_state = 'playing'
        self.current_turn = 'player'
        return True
        
    def place_player_ship(self, ship_name: str, start_pos: Tuple[int, int], 
                         orientation: str) -> bool:
    
        if self.game_state != 'setup' or not self.player:
            return False
            
        success = self.player.place_ship(ship_name, SHIPS[ship_name], start_pos, orientation)       
        
        # Check if all ships are placed
        if success and not self.player.remaining_ships:
            self.start_gameplay()
            
        return success
        
    def place_player_ships_randomly(self) -> bool:
        
        if self.game_state != 'setup' or not self.player:
            return False
            
        success = self.player.place_ships_randomly()
        if success:
            self.start_gameplay()
        return success
        
    def process_player_shot(self, position: Tuple[int, int]) -> Dict[str, Any]:
        
        if self.game_state != 'playing' or self.current_turn != 'player':
            return {'valid': False, 'message': 'Not your turn'}
            
        if self.ai_player.grid.get_cell_state(position) in ['hit', 'miss']:
            return {'valid': False, 'message': 'Position already targeted'}
            
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
            'game_over': False,
            'winner': None,
            'message': ''
        }
        
        if hit:
            result['message'] = f"Hit! "
            if sunk_ship:
                result['message'] += f"You sunk the {sunk_ship.name}!"
        else:
            result['message'] = "Miss!"
            
        # Check victory condition
        if self.ai_player.all_ships_sunk():
            self.end_game('player')
            result['game_over'] = True
            result['winner'] = 'player'
        else:
            self.current_turn = 'ai'
            
        return result
        
    def process_ai_turn(self) -> Dict[str, Any]:
        
        if self.game_state != 'playing' or self.current_turn != 'ai':
            return {'valid': False, 'message': 'Not AI turn'}
        
        try:
            # Get AI's shot position
            position = self.ai_player.get_shot_position()
            
            # Validate the position hasn't been shot before
            if position in self.ai_player.shots:
                self.logger.error(f"AI attempted to shoot already targeted position: {position}")
                return {
                    'valid': False,
                    'message': 'Position already shot',
                    'position': position
                }
            
            # Process the shot
            hit, sunk_ship = self.player.receive_shot(position)
            
            # Update AI's knowledge and strategy
            self.ai_player.update_strategy(hit, position)
            
            if sunk_ship:
                # Clear potential targets if ship sunk
                self.ai_player.potential_targets = [
                    pos for pos in self.ai_player.potential_targets
                    if pos not in sunk_ship.position
                ]
                self.ai_player._reset_hunting()
            
            # Update stats
            self.stats['total_shots'] += 1
            if hit:
                self.stats['hits'] += 1
            else:
                self.stats['misses'] += 1
            
            # Prepare result
            result = {
                'valid': True,
                'hit': hit,
                'sunk': sunk_ship is not None,
                'position': position,
                'ship_name': sunk_ship.name if sunk_ship else None,
                'game_over': False,
                'winner': None,
                'message': ''
            }

            # Update message
            if hit:
                result['message'] = "💥 AI Hit! "
                if sunk_ship:
                    result['message'] += f"AI sunk your {sunk_ship.name}! 🚢"
            else:
                result['message'] = "AI Missed! 💨"

            # Check victory condition
            if self.player.all_ships_sunk():
                self.end_game('ai')
                result['game_over'] = True
                result['winner'] = 'ai'
            else:
                self.current_turn = 'player'

            
            self.logger.info(f"AI turn - pos:{position} hit:{hit} sunk:{sunk_ship is not None}")
            
            return result

        except Exception as e:
            self.logger.error(f"Error in AI turn: {e}")
            return {
                'valid': False,
                'message': 'Error during AI turn',
                'position': (0,0)
            }

    def _get_smart_target_position(self, available_positions: List[Tuple[int, int]]) -> Tuple[int, int]:
        
        if not available_positions:
            raise ValueError("No available positions")

        
        if hasattr(self.ai_player, 'hit_positions') and self.ai_player.hit_positions:
            for hit_pos in self.ai_player.hit_positions:
                
                ship_pattern = self._detect_ship_pattern(hit_pos)
                if ship_pattern:
                    next_pos = self._get_next_position_in_pattern(ship_pattern, available_positions)
                    if next_pos:
                        return next_pos

                
                adjacent_positions = [
                    (hit_pos[0] + dx, hit_pos[1] + dy)
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                ]
                
                valid_adjacent = [
                    pos for pos in adjacent_positions
                    if pos in available_positions
                ]
                
                if valid_adjacent:
                    return self._choose_best_adjacent_position(valid_adjacent, hit_pos)

        
        density_scores = self._analyze_position_density(available_positions)
        
        
        if density_scores:
            best_position = max(density_scores, key=density_scores.get)
            return best_position

        
        checkerboard_positions = [
            pos for pos in available_positions
            if (pos[0] + pos[1]) % 2 == 0  
        ]
        if checkerboard_positions:
            return self._choose_strategic_position(checkerboard_positions)

        
        return random.choice(available_positions)

    def _analyze_position_density(self, positions: List[Tuple[int, int]]) -> Dict[Tuple[int, int], float]:
        
        density_scores = {}
        for pos in positions:
            
            adjacent_count = sum(
                1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                if (pos[0] + dx, pos[1] + dy) in positions
            )
            
            
            center_x, center_y = self.grid_size // 2, self.grid_size // 2
            distance = abs(pos[0] - center_x) + abs(pos[1] - center_y)
            
            
            density_score = adjacent_count / (distance + 1)
            density_scores[pos] = density_score
        
        return density_scores

    def _detect_ship_pattern(self, hit_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        
        pattern = [hit_pos]
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in directions:
            current_pos = hit_pos
            while True:
                next_pos = (current_pos[0] + dx, current_pos[1] + dy)
                if next_pos not in self.ai_player.hit_positions:
                    break
                pattern.append(next_pos)
                current_pos = next_pos
        
        return pattern if len(pattern) > 1 else []

    def _get_next_position_in_pattern(self, pattern: List[Tuple[int, int]], 
                                    available_positions: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        
        if len(pattern) < 2:
            return None
            
        
        dx = pattern[1][0] - pattern[0][0]
        dy = pattern[1][1] - pattern[0][1]
        
        
        start_pos = (pattern[0][0] - dx, pattern[0][1] - dy)
        end_pos = (pattern[-1][0] + dx, pattern[-1][1] + dy)
        
        
        if start_pos in available_positions:
            return start_pos
        if end_pos in available_positions:
            return end_pos
            
        return None

    def _choose_best_adjacent_position(self, adjacent_positions: List[Tuple[int, int]], 
                                     hit_pos: Tuple[int, int]) -> Tuple[int, int]:
        
        if not adjacent_positions:
            raise ValueError("No adjacent positions available")

        
        ship_direction = None
        for other_hit in self.ai_player.hit_positions:
            if other_hit != hit_pos:
                if other_hit[0] == hit_pos[0]:  
                    ship_direction = 'horizontal'
                elif other_hit[1] == hit_pos[1]:  
                    ship_direction = 'vertical'
        
        if ship_direction:
            
            aligned_positions = [
                pos for pos in adjacent_positions
                if (ship_direction == 'horizontal' and pos[0] == hit_pos[0]) or
                   (ship_direction == 'vertical' and pos[1] == hit_pos[1])
            ]
            if aligned_positions:
                return random.choice(aligned_positions)
        
        return random.choice(adjacent_positions)

    def _choose_strategic_position(self, positions: List[Tuple[int, int]]) -> Tuple[int, int]:
        
        if not positions:
            raise ValueError("No positions available")

        
        max_ship_size = 0
        for ship in self.player.grid.ships:
            if not all(pos in self.ai_player.hit_positions for pos in ship.position):
                max_ship_size = max(max_ship_size, len(ship.position))
        
        
        best_positions = []
        for pos in positions:
            space_available = self._check_available_space(pos)
            if space_available >= max_ship_size:
                best_positions.append(pos)
        
        if best_positions:
            return random.choice(best_positions)
            
        return random.choice(positions)

    def _check_available_space(self, position: Tuple[int, int]) -> int:
        
        max_space = 1
        directions = [(0, 1), (1, 0)]  
        
        for dx, dy in directions:
            space = 1
            current_pos = position
            
            while True:
                next_pos = (current_pos[0] + dx, current_pos[1] + dy)
                if not self._is_valid_position(next_pos) or next_pos in self.ai_player.shots:
                    break
                space += 1
                current_pos = next_pos
            
            current_pos = position
            
            while True:
                next_pos = (current_pos[0] - dx, current_pos[1] - dy)
                if not self._is_valid_position(next_pos) or next_pos in self.ai_player.shots:
                    break
                space += 1
                current_pos = next_pos
            
            max_space = max(max_space, space)
        
        return max_space

    def _update_ai_strategy(self, position: Tuple[int, int], hit: bool, sunk_ship: Optional[Ship]):
        
        if not hasattr(self.ai_player, 'strategy_state'):
            self.ai_player.strategy_state = {
                'last_hit': None,
                'hunt_mode': False,
                'hunt_direction': None,
                'successful_hits': []
            }
        
        if hit:
            self.ai_player.strategy_state['last_hit'] = position
            self.ai_player.strategy_state['successful_hits'].append(position)
            
            if sunk_ship:
                
                self.ai_player.strategy_state['hunt_mode'] = False
                self.ai_player.strategy_state['hunt_direction'] = None
                self.ai_player.strategy_state['successful_hits'] = [
                    hit for hit in self.ai_player.strategy_state['successful_hits']
                    if hit not in sunk_ship.position
                ]
            else:
                
                self.ai_player.strategy_state['hunt_mode'] = True
        elif self.ai_player.strategy_state['hunt_mode']:
            
            if self.ai_player.strategy_state['hunt_direction']:
                self.ai_player.strategy_state['hunt_direction'] = self._get_next_hunt_direction(
                    self.ai_player.strategy_state['hunt_direction']
                )

    def _get_next_hunt_direction(self, current_direction: Tuple[int, int]) -> Tuple[int, int]:
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        current_index = directions.index(current_direction)
        return directions[(current_index + 1) % 4]

    def _is_valid_position(self, position: Union[Tuple[int, int], List[int]]) -> bool:
        
        try:
            
            if not isinstance(position, (tuple, list)) or len(position) != 2:
                return False
                
            
            row, col = position
            
            
            if not isinstance(row, int) or not isinstance(col, int):
                return False
                
            return (0 <= row < self.grid_size and 
                   0 <= col < self.grid_size)
                   
        except Exception as e:
            print(f"Error in _is_valid_position: {e}")
            return False

    def _get_valid_random_position(self) -> Tuple[int, int]:
        
        import random
        valid_positions = [
            (row, col) 
            for row in range(self.grid_size) 
            for col in range(self.grid_size)
            if self._is_valid_position((row, col))
        ]
        return random.choice(valid_positions) if valid_positions else (0, 0)

    def end_game(self, winner: str):
        
        self.game_state = 'ended'
        self.current_turn = None
        
        
        self.stats['games_played'] += 1
        if winner == 'player':
            self.stats['games_won'] += 1
        
        self._save_game_result('win' if winner == 'player' else 'loss')

    def force_end_game(self):
        
        if self.game_state != 'ended':
            try:
                self.end_game('ai')  
                
                self.current_turn = None
                self.selected_position = None
                self.game_state = 'ended'
                
                return True
            except Exception as e:
                print(f"Error ending game: {e}")
                return False
        return False

    def _save_game_result(self, outcome: str):
        
        if not hasattr(self, 'current_player_id'):
            print("Warning: No player ID found")
            return
        
        result = {
            'outcome': outcome,
            'moves': self.stats['total_shots'],
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'duration': self.stats['current_game_duration'],
            'grid_size': self.grid_size
        }
        self.db_manager.save_game_result(self.current_player_id, result)

    def get_cell_state(self, is_player_grid: bool, position: Tuple[int, int]) -> str:
        grid = self.player.grid if is_player_grid else self.ai_player.grid
        return grid.get_cell_state(position)

    def update_settings(self, new_settings: dict):
        if 'grid_size' in new_settings:
            new_size = new_settings['grid_size']
            if new_size != self.grid_size:
                current_player_id = getattr(self, 'current_player_id', None)
                
                self.grid_size = new_size
                self.start_new_game()
                
                if current_player_id:
                    self.current_player_id = current_player_id
                
                if self.main_window:
                    self.main_window.reset_ui()

    def _update_grid_size_in_modules(self):
        import utils.constants as constants
        constants.GRID_SIZE = self.grid_size

    def set_main_window(self, main_window):
        self.main_window = main_window
        main_window.game_controller = self

    def get_game_state(self) -> str:
        return self.game_state

    def get_current_turn(self) -> str:
        return self.current_turn

    def set_current_player(self, player_data: dict):
        self.current_player_id = player_data['id']
        self.current_player_name = player_data['name']
        
        self.stats.update({
            'games_played': player_data['games_played'],
            'games_won': player_data['games_won'],
            'total_shots': player_data['total_shots'],
            'hits': player_data['total_hits']
        })

    def save_game(self) -> bool:
        
        if not self.current_player_id or self.game_state != 'playing':
            return False
        
        game_state = {
            'player_grid': {
                'ships': [(ship.name, ship.size, ship.position, ship.orientation.value) 
                         for ship in self.player.grid.ships],
                'shots': list(self.player.grid.shots),
                'hits': list(self.player.grid.hits),
                'misses': list(self.player.grid.misses)
            },
            'ai_grid': {
                'ships': [(ship.name, ship.size, ship.position, ship.orientation.value) 
                         for ship in self.ai_player.grid.ships],
                'shots': list(self.ai_player.grid.shots),
                'hits': list(self.ai_player.grid.hits),
                'misses': list(self.ai_player.grid.misses)
            },
            'ai_state': {
                'shots': list(self.ai_player.shots),
                'hit_positions': list(getattr(self.ai_player, 'hit_positions', set())),
                'hunting_mode': getattr(self.ai_player, 'hunting_mode', False),
                'last_hit': getattr(self.ai_player, 'last_hit', None)
            },
            'current_turn': self.current_turn,
            'game_state': self.game_state,
            'stats': self.stats,
            'grid_size': self.grid_size,
            'version': '1.1'  
        }
        
        return self.db_manager.save_game_state(self.current_player_id, game_state)

    def load_game(self) -> bool:
        
        if not self.current_player_id:
            return False
        
        saved_state = self.db_manager.load_game_state(self.current_player_id)
        if not saved_state:
            return False
        
        try:
            
            self.grid_size = saved_state['grid_size']
            self.current_turn = saved_state['current_turn']
            self.game_state = saved_state['game_state']
            self.stats = saved_state['stats']
            
            
            self._recreate_player_from_state(saved_state['player_grid'])
            self._recreate_ai_from_state(saved_state['ai_grid'], saved_state.get('ai_state', {}))
            
            
            self._validate_loaded_state()
            
            return True
            
        except Exception as e:
            print(f"Error loading game: {e}")
            self.start_new_game()
            return False

    def _recreate_player_from_state(self, player_state: dict):
        
        self.player = Player(self.grid_size)
        self.player.remaining_ships = []
        
        
        for ship_data in player_state['ships']:
            name, size, position, orientation = ship_data
            ship = Ship(name, size)
            ship.position = [tuple(pos) for pos in position]
            ship.orientation = ShipOrientation(orientation)
            
            self.player.grid.ships.append(ship)
            self.player.placed_ships[name] = ship
            
            for pos in ship.position:
                self.player.grid.grid[pos[0]][pos[1]] = ship
        
        
        self.player.grid.shots = set(tuple(pos) for pos in player_state['shots'])
        self.player.grid.hits = set(tuple(pos) for pos in player_state['hits'])
        self.player.grid.misses = set(tuple(pos) for pos in player_state['misses'])
        self.player.shots = self.player.grid.shots.copy()
        
        
        for ship in self.player.grid.ships:
            ship.hits = [pos for pos in ship.position if pos in self.player.grid.hits]

    def _recreate_ai_from_state(self, ai_grid_state: dict, ai_state: dict = None):
        
        self.ai_player = AIPlayer()
        self.ai_player.grid = Grid(self.grid_size)
        self.ai_player.remaining_ships = []
        
        
        for ship_data in ai_grid_state['ships']:
            name, size, position, orientation = ship_data
            ship = Ship(name, size)
            ship.position = [tuple(pos) for pos in position]
            ship.orientation = ShipOrientation(orientation)
            
            self.ai_player.grid.ships.append(ship)
            self.ai_player.placed_ships[name] = ship
            
            for pos in ship.position:
                self.ai_player.grid.grid[pos[0]][pos[1]] = ship
        
        
        self.ai_player.grid.shots = set(tuple(pos) for pos in ai_grid_state['shots'])
        self.ai_player.grid.hits = set(tuple(pos) for pos in ai_grid_state['hits'])
        self.ai_player.grid.misses = set(tuple(pos) for pos in ai_grid_state['misses'])
        self.ai_player.shots = self.ai_player.grid.shots.copy()
        
        
        for ship in self.ai_player.grid.ships:
            ship.hits = [pos for pos in ship.position if pos in self.ai_player.grid.hits]
            
        
        if ai_state:
            self.ai_player.shots = set(tuple(pos) for pos in ai_state.get('shots', []))
            self.ai_player.hit_positions = set(tuple(pos) for pos in ai_state.get('hit_positions', []))
            self.ai_player.hunting_mode = ai_state.get('hunting_mode', False)
            self.ai_player.last_hit = ai_state.get('last_hit')

    def _determine_orientation(self, positions: List[Tuple[int, int]]) -> str:
        
        if len(positions) < 2:
            return 'horizontal'  
        if positions[0][0] == positions[1][0]:
            return 'horizontal'
        return 'vertical'

    def get_save_state(self) -> dict:
        
        if not self.current_player_id or self.game_state != 'playing':
            return {
                'valid': False,
                'error': 'Game not in valid state for saving',
                'game_state': self.game_state,
                'has_player': bool(self.current_player_id)
            }
        
        try:
            return {
                'valid': True,
                'player': self.player.to_dict() if self.player else {},
                'ai': self.ai_player.to_dict() if self.ai_player else {},
                'current_turn': self.current_turn,
                'game_state': self.game_state,
                'stats': self.stats,
                'grid_size': self.grid_size,
                'version': '1.0'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'game_state': self.game_state
            }

    def restore_save_state(self, save_state: dict) -> bool:
        
        try:
            
            self.player = Player.from_dict(save_state['player'])
            
            
            self.ai_player = AIPlayer.from_dict(save_state['ai'])
            
            
            self.current_turn = save_state['current_turn']
            self.game_state = save_state['game_state']
            self.stats = save_state['stats']
            self.grid_size = save_state['grid_size']
            
            return True
        except Exception as e:
            print(f"Error restoring game state: {e}")
            return False

    def _update_ui(self, message: str = None, stats: bool = True) -> bool:
        
        if hasattr(self, 'main_window') and self.main_window:
            if message:
                self.main_window.update_status(message)
            if stats:
                self.main_window.update_stats_display()
            return True
        return False

    def _execute_ai_turn(self):
        try:
            result = self.process_ai_turn()
            if not result['valid']:
                self.logger.error("Invalid AI turn")
                return

            row, col = result['position']
            if not (0 <= row < len(self.player_grid_buttons) and 
                    0 <= col < len(self.player_grid_buttons[0])):
                self.logger.error(f"Invalid AI shot position: {row}, {col}")
                return

            button = self.player_grid_buttons[row][col]

            if result['hit']:
                button.setStyleSheet(f"background-color: {HIT_COLOR};")
                message = "💥 AI Hit! "
                if result['sunk']:
                    message += f"AI sunk your {result['ship_name']}! 🚢"
                    ship = next((s for s in self.player.grid.ships 
                               if s.name == result['ship_name']), None)
                    if ship:
                        for ship_pos in ship.position:
                            self.player_grid_buttons[ship_pos[0]][ship_pos[1]].setStyleSheet(
                                f"background-color: {HIT_COLOR};"
                            )
            else:
                button.setStyleSheet(f"background-color: {MISS_COLOR};")
                message = "AI Missed! 💨"

            self._update_ui(message)

            if result['game_over']:
                if self._update_ui():
                    self.main_window.game_over(result['winner'])
            else:
                if self._update_ui():
                    self.main_window._enable_ai_grid()
                    QTimer.singleShot(200, lambda: self.main_window.update_status("Your turn! Select a target"))

        except Exception as e:
            self.logger.error(f"Error executing AI turn: {e}")
            QTimer.singleShot(50, self._execute_ai_turn)

    def set_grid_buttons(self, player_grid_buttons, ai_grid_buttons):
        
        self.player_grid_buttons = player_grid_buttons
        self.ai_grid_buttons = ai_grid_buttons

    def save_game_state(self) -> Dict[str, Any]:
        
        try:
            if not self.player or not self.ai_player:
                return {
                    'valid': False,
                    'error': 'Players not initialized',
                    'game_state': self.game_state
                }
                
            return {
                'valid': True,
                'player': self.player.to_dict(),
                'ai_player': self.ai_player.to_dict(),
                'current_turn': self.current_turn,
                'game_state': self.game_state,
                'game_over': self.game_over,
                'grid_size': self.grid_size,
                'stats': self.stats.copy(),
                'version': '1.0'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'game_state': self.game_state,
                'traceback': str(e.__traceback__)
            }

    def load_game_state(self, state: Dict[str, Any]) -> bool:
        
        try:
            if not state or not isinstance(state, dict):
                raise ValueError("Invalid game state data")

            if state.get('version', '0.0') != '1.0':
                print("Warning: Loading game from different version")

            self.grid_size = state.get('grid_size', 10)

            if 'player' in state and state['player']:
                self.player = Player.from_dict(state['player'])
            else:
                self.player = Player(grid_size=self.grid_size)

            if 'ai_player' in state and state['ai_player']:
                self.ai_player = AIPlayer.from_dict(state['ai_player'])
            else:
                self.ai_player = AIPlayer()
                self.ai_player.grid.resize(self.grid_size)

            self.current_turn = state.get('current_turn', 'player')
            self.game_state = state.get('game_state', 'playing')
            self.game_over = state.get('game_over', False)
            
            saved_stats = state.get('stats', {})
            self.stats.update(saved_stats)

            self._validate_loaded_state()
            
            return True

        except Exception as e:
            print(f"Error loading game state: {e}")
            self.start_new_game()
            return False

    def _validate_loaded_state(self):
        
        try:
            if not self.player or not self.ai_player:
                raise ValueError("Missing players after load")

            if self.player.grid.size != self.grid_size or self.ai_player.grid.size != self.grid_size:
                self.player.grid.resize(self.grid_size)
                self.ai_player.grid.resize(self.grid_size)

            if self.game_state not in ['setup', 'playing', 'ended']:
                self.game_state = 'playing'

            if self.current_turn not in ['player', 'ai']:
                self.current_turn = 'player'

            if not hasattr(self.ai_player, 'shots'):
                self.ai_player.shots = set()
            if not hasattr(self.ai_player, 'hit_positions'):
                self.ai_player.hit_positions = set()

            self.ai_player.shots = {tuple(pos) if isinstance(pos, list) else pos 
                                  for pos in self.ai_player.shots}
            self.ai_player.hit_positions = {tuple(pos) if isinstance(pos, list) else pos 
                                          for pos in getattr(self.ai_player, 'hit_positions', set())}

            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    pos = (row, col)
                    cell_state = self.player.grid.get_cell_state(pos)
                    if cell_state in ['hit', 'miss']:
                        self.ai_player.shots.add(pos)
                        if cell_state == 'hit':
                            self.ai_player.hit_positions.add(pos)

            if hasattr(self.ai_player, '_clean_state'):
                self.ai_player._clean_state()

            self._validate_shots_and_hits()

        except Exception as e:
            print(f"Error validating loaded state: {e}")
            self.start_new_game()

    def _validate_shots_and_hits(self):
        
        try:
            
            if not hasattr(self.ai_player, 'shots'):
                self.ai_player.shots = set()
            if not hasattr(self.ai_player, 'hit_positions'):
                self.ai_player.hit_positions = set()

            self.ai_player.shots = {
                tuple(pos) if isinstance(pos, list) else pos 
                for pos in self.ai_player.shots 
                if self._is_valid_position(pos)
            }
            self.ai_player.hit_positions = {
                tuple(pos) if isinstance(pos, list) else pos 
                for pos in self.ai_player.hit_positions 
                if self._is_valid_position(pos)
            }

            if hasattr(self.ai_player, 'potential_targets'):
                self.ai_player.potential_targets = [
                    tuple(pos) if isinstance(pos, list) else pos 
                    for pos in self.ai_player.potential_targets 
                    if self._is_valid_position(pos)
                ]

        except Exception as e:
            print(f"Error validating shots and hits: {e}")
            self.ai_player.shots = set()
            self.ai_player.hit_positions = set()
            self.ai_player.potential_targets = []

    def validate_game_state(self) -> bool:
        try:
            # Basic state validation
            if self.game_state not in ['setup', 'playing', 'ended']:
                return False
            if self.current_turn not in ['player', 'ai']:
                return False
            
            # Grid size validation    
            if self.grid_size not in [10, 15]:
                return False
            
            # Player validation
            if not self.player or not self.ai_player:
                return False
            
            # Grid validation
            if not (self.player.grid.validate_grid_state() and 
                    self.ai_player.grid.validate_grid_state()):
                return False
            
            return True
        
        except Exception as e:
            logging.error(f"Game state validation error: {e}")
            return False