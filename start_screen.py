import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                           QMessageBox, QMainWindow)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
from instructions_screen import InstructionsScreen

class StartScreen(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.instructions_window = InstructionsScreen()
        self.init_ui()

    def init_ui(self):

        ## program window title and size
        self.setWindowTitle("Battleship Game - TEAM 4")
        self.showFullScreen()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(60)

        layout.addStretch()
        
        ## setting up the title label
        title = QLabel("BATTLESHIP GAME\n TEAM 4")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 36px; color: #2c3e50; font-weight: bold;")
        layout.addWidget(title)


        ## setting up the ui buttons in the start screen
        startGame_button = QPushButton("New Game")
        startGame_button.setFixedSize(300, 80)
        startGame_button.clicked.connect(self.start_new_game)
        startGame_button.setStyleSheet("background-color: #00cc35; font-size: 22px; color: #f4f4f4; font-weight: bold;")

        layout.addWidget(startGame_button, alignment=Qt.AlignmentFlag.AlignCenter)

        instructions_button = QPushButton("Instructions")
        instructions_button.setFixedSize(300, 80)
        instructions_button.clicked.connect(self.show_instructions)
        instructions_button.setStyleSheet("background-color: #0faaff; font-size: 22px; color: #f4f4f4; font-weight: bold;")

        layout.addWidget(instructions_button, alignment=Qt.AlignmentFlag.AlignCenter)

        exit_button = QPushButton("Exit")
        exit_button.setFixedSize(300, 80)
        exit_button.clicked.connect(self.close_game)
        exit_button.setStyleSheet("background-color: #e52c3b; font-size: 22px; color: #f4f4f4; font-weight: bold;")

        layout.addWidget(exit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def start_new_game(self):

        self.main_window.setWindowFlags(Qt.WindowType.Window)
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.start_new_game()

    def show_instructions(self):
        
        self.instructions_window.setWindowFlags(Qt.WindowType.Window)
        self.instructions_window.setWindowTitle("Game Instructions")
        self.instructions_window.showFullScreen()
        self.instructions_window.show()
        self.instructions_window.raise_()
    
    def close_game(self):
            
        sys.exit()

