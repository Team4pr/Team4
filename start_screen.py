from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                           QMessageBox, QMainWindow)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
from instructions_screen import InstructionsScreen
from settings_screen import SettingsScreen

class StartScreen(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.instructions_window = None
        self.settings_window = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Battleship Game")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #2c3e50;
                padding: 20px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                min-width: 200px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)

        title = QLabel("BATTLESHIP")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(36)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
            }
        """)
        layout.addWidget(title)

        buttons_data = [
            ("New Game", self.start_new_game, "#2ecc71"),
            ("Instructions", self.show_instructions, "#3498db"),
            ("Settings", self.show_settings, "#e67e22"),
            ("Exit", self.close_game, "#e74c3c")
        ]

        for text, handler, color in buttons_data:
            btn = QPushButton(text)
            btn.setMinimumSize(300, 60)
            btn.clicked.connect(handler)
            btn.setFont(QFont("Arial", 14))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: {self._darken_color(color)};
                }}
            """)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def start_new_game(self):
        self.hide()
        self.main_window.show()
        self.main_window.start_new_game()

    def show_instructions(self):
        if not self.instructions_window:
            self.instructions_window = InstructionsScreen()
            self.instructions_window.setWindowFlags(Qt.WindowType.Window)
            self.instructions_window.setWindowTitle("Game Instructions")
            self.instructions_window.resize(800, 600)
        self.instructions_window.show()
        self.instructions_window.raise_()

    def show_settings(self):
        if not self.settings_window:
            if not self.main_window.game_controller.current_player_id:
                QMessageBox.warning(self, "Error", "No player is currently logged in.")
                return
            current_settings = {
                'grid_size': self.main_window.game_controller.grid_size
            }
            self.settings_window = SettingsScreen(
                current_settings, 
                current_player_id=self.main_window.game_controller.current_player_id,
                db_manager=self.main_window.game_controller.db_manager
            )
            self.settings_window.setWindowFlags(Qt.WindowType.Window)
            self.settings_window.setWindowTitle("Game Settings")
            self.settings_window.resize(500, 400)
            self.settings_window.settings_changed.connect(self.apply_settings)
        self.settings_window.show()
        self.settings_window.raise_()

    def apply_settings(self, new_settings):
        self.main_window.game_controller.update_settings(new_settings)
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")

    def close_game(self):
        reply = QMessageBox.question(
            self, 'Exit Game',
            'Are you sure you want to exit?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.instructions_window:
                self.instructions_window.close()
            if self.settings_window:
                self.settings_window.close()
            if self.main_window:
                self.main_window.close()
            self.close()

    def _darken_color(self, color: str, factor: float = 0.8) -> str:
        color = color.lstrip('#')
        r = int(color[:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:], 16)
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def closeEvent(self, event):
        try:
            reply = QMessageBox.question(
                self, 'Exit Game',
                'Are you sure you want to exit the game?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.instructions_window:
                    self.instructions_window.close()
                if self.settings_window:
                    self.settings_window.close()
                if self.main_window:
                    self.main_window.close()
                event.accept()
            else:
                event.ignore()
        except Exception as e:
            print(f"Error during window closure: {e}")
            event.accept()
