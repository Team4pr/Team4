from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMainWindow
from PyQt6.QtCore import Qt
from instructions_screen import InstructionsScreen
import sys

class StartScreen(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.instructions_window = InstructionsScreen()
        self.init_ui()

    def init_ui(self):
        self.showFullScreen()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(50)
        layout.addStretch()

        title = QLabel("BATTLESHIP GAME\n TEAM 4")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 36px; color: black; font-weight: bold;")
        layout.addWidget(title)

        self.add_button(layout, "New Game", "#00cc35", self.start_new_game)
        self.add_button(layout, "Instructions", "#0faaff", self.show_instructions)
        self.add_button(layout, "Exit", "#e52c3b", self.close_game)
        layout.addStretch()

    def add_button(self, layout, text, color, callback):
        button = QPushButton(text)
        button.setFixedSize(300, 80)
        button.clicked.connect(callback)
        button.setStyleSheet(f"background-color: {color}; font-size: 20px; color: white; font-weight: bold;")
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)

    def start_new_game(self):
        self.main_window.raise_()
        self.main_window.show()
        self.main_window.start_new_game()

    def show_instructions(self):
        self.instructions_window.show()
        self.instructions_window.raise_()
         self.instructions_window.showFullScreen()

    def close_game(self):
        sys.exit()
