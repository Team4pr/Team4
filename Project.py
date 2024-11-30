import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QSize
import random

# Basic Ship Class
class Ship:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.hits = 0

    def is_sunk(self):
        return self.hits >= self.size


# Basic Player Class
class Player:
    def __init__(self):
        self.grid = [['' for _ in range(10)] for _ in range(10)]
        self.ships = []

    def place_ship(self, ship, x, y, orientation):
        if orientation == 'H':
            for i in range(ship.size):
                self.grid[y][x + i] = ship.name
        else:
            for i in range(ship.size):
                self.grid[y + i][x] = ship.name
        self.ships.append(ship)

    def receive_attack(self, x, y):
        if self.grid[y][x] != '':
            ship_name = self.grid[y][x]
            for ship in self.ships:
                if ship.name == ship_name:
                    ship.hits += 1
                    if ship.is_sunk():
                        print(f"{ship_name} sunk!")
                    return True  # Hit
        return False  # Miss


# AI Class
class AI(Player):
    def make_move(self):
        x, y = random.randint(0, 9), random.randint(0, 9)
        return x, y


# Main Game Class
class Game:
    def __init__(self):
        self.player = Player()
        self.ai = AI()
        self.turn = 'player'

    def switch_turn(self):
        self.turn = 'ai' if self.turn == 'player' else 'player'

    def check_winner(self):
        if all(ship.is_sunk() for ship in self.player.ships):
            return "AI Wins!"
        elif all(ship.is_sunk() for ship in self.ai.ships):
            return "You Win!"
        return None


# GUI Class for Battleship Game
class BattleshipGameGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battleship Game")
        self.setFixedSize(600, 400)
        self.game = Game()
        
        # Layouts and Widgets
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()

        # Create player and AI grids
        self.player_grid = [[QPushButton() for _ in range(10)] for _ in range(10)]
        self.ai_grid = [[QPushButton() for _ in range(10)] for _ in range(10)]

        # Setup player grid buttons
        for row in range(10):
            for col in range(10):
                btn = self.player_grid[row][col]
                btn.setFixedSize(QSize(25, 25))
                grid_layout.addWidget(btn, row, col)

        # Setup AI grid buttons
        for row in range(10):
            for col in range(10):
                btn = self.ai_grid[row][col]
                btn.setFixedSize(QSize(25, 25))
                btn.clicked.connect(lambda _, x=row, y=col: self.player_attack(x, y))
                grid_layout.addWidget(btn, row, col + 12)  # Offset for AI grid

        main_layout.addLayout(grid_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def player_attack(self, x, y):
        if self.game.turn == 'player':
            hit = self.game.ai.receive_attack(x, y)
            self.update_grid(self.ai_grid, x, y, hit)
            self.game.switch_turn()
            self.ai_turn()

    def ai_turn(self):
        if self.game.turn == 'ai':
            x, y = self.game.ai.make_move()
            hit = self.game.player.receive_attack(x, y)
            self.update_grid(self.player_grid, x, y, hit)
            self.game.switch_turn()

    def update_grid(self, grid, x, y, hit):
        button = grid[x][y]
        button.setText("X" if hit else "O")
        button.setEnabled(False)


# Main Application Runner
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BattleshipGameGUI()
    window.show()
    sys.exit(app.exec_())