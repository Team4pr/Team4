import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from start_screen import StartScreen
from game_controller import GameController

## Main game class
class BattleshipGame:

    def __init__(self):

        ## PyQt
        self.app = QApplication(sys.argv)
        
        ## Creates object from the game controller class
        self.game_controller = GameController()
        
        ## Creates the main window for the game
        self.main_window = MainWindow(self.game_controller)
        self.game_controller.set_main_window(self.main_window)
        
        ## Start screen on the mai widnow
        self.start_screen = StartScreen(self.main_window)

    def run(self):

        self.start_screen.show()
        return self.app.exec()

## True when this file is run
if __name__ == "__main__":

    ## Creates the game object from the game class
    game = BattleshipGame()
    
    ## Run game
    sys.exit(game.run())
