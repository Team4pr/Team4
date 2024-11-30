import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from start_screen import StartScreen
from login_screen import LoginScreen
from game_controller import GameController
from db_manager import DatabaseManager

## Main game class
class BattleshipGame:

    def __init__(self):

        ## PyQt
        self.app = QApplication(sys.argv)
        
        ## Creates object from the database class
        self.db_manager = DatabaseManager()
        
        ## Creates object from the game controller class
        self.game_controller = GameController(self.db_manager)
        
        ## Creates the main window for the game
        self.main_window = MainWindow(self.game_controller)
        self.game_controller.set_main_window(self.main_window)
        
        ## Start screen on the mai widnow
        self.start_screen = StartScreen(self.main_window)
        
        ## login screen
        self.login_screen = LoginScreen(self.db_manager)
        self.login_screen.login_successful.connect(self.on_login_success)

    def run(self):

        self.login_screen.show()
        return self.app.exec()

    def on_login_success(self, player_data):

        self.game_controller.current_player_id = player_data['id']
        self.game_controller.current_player_name = player_data['name']
        
        self.game_controller.stats.update({
            'games_played': player_data.get('games_played', 0),
            'games_won': player_data.get('games_won', 0),
            'total_shots': player_data.get('total_shots', 0),
            'hits': player_data.get('total_hits', 0)
        })
        
        self.start_screen.show()

## True when this file is run
if __name__ == "__main__":

    ## Creates the game object from the game class
    game = BattleshipGame()
    
    ## Run game
    sys.exit(game.run())
