#The first thing we do is import some of the things we will need in the program
import sys  #This helps us deal with the system that the program is running on
from PyQt6.QtWidgets import QApplication  # This is part of the PyQt6 library that we use to create a graphical interface
from gui.main_window import MainWindow  # We import the main window from a file called main_window
from gui.start_screen import StartScreen  # We import the start screen from a file called start_screen
from gui.login_screen import LoginScreen  # We import the login screen from a file named login_screen.
from models.game_controller import GameController  # We import the game controller from a file called game_controller
from database.db_manager import DatabaseManager  # We import the database manager from a file called db_manager

# Here you will find a category called Battleship Game.
class BattleshipGame:
   """
   This category is responsible for running the game and linking all the parts together
    """
    
    def __init__(self):
       """
       This is the start function that runs as soon as we create an object of this class
        "" "
        #We create the PyQt application, which is the basis on which we will work
        self.app = QApplication(sys.argv)
        
        # We create a database manager to store and retrieve data.
        self.db_manager = DatabaseManager()
        
       # We make a game controller to manage the game
        self.game_controller = GameController(self.db_manager)
        
        # We create the main window in which the game will appear
        self.main_window = MainWindow(self.game_controller)
        self.game_controller.set_main_window(self.main_window)

        # We create the start screen that will appear as soon as the game starts
        self.start_screen = StartScreen(self.main_window)
        
        # We create a login screen for the player to enter his data
        self.login_screen = LoginScreen(self.db_manager)
        self.login_screen.login_successful.connect(self.on_login_success)

    def run(self):
        """This is a function that runs the game."""
        # We display the first login screen.
        self.login_screen.show()
        return self.app.exec()

    def on_login_success(self, player_data):
        """This is a function that deals with successful login"""
        # We store player information in the game controller.
        self.game_controller.current_player_id = player_data['id']
        self.game_controller.current_player_name = player_data['name']
        
        # We update the player's statistics
        self.game_controller.stats.update({
            'games_played': player_data.get('games_played', 0),
            'games_won': player_data.get('games_won', 0),
            'total_shots': player_data.get('total_shots', 0),
            'hits': player_data.get('total_hits', 0)
        })
        
        # We display the start screen after logging in.
        self.start_screen.show()


# Here we determine the starting point of the program.
if __name__ == "__main__":
    # We create an object of the class BattleshipGame
    game = BattleshipGame()
    
    # We run the game and exit with the appropriate code
    sys.exit(game.run())
