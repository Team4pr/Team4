from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent

class LoginScreen(QWidget):
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self, db_manager, parent=None):
        
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        
        self.setWindowTitle("Battleship Login")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)  
        layout.setContentsMargins(40, 40, 40, 40)  
        
        title = QLabel("Welcome to Battleship")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setMinimumHeight(40)
        self.name_input.setFont(QFont("Arial", 12))
        self.name_input.setToolTip("Please enter a unique name (3-20 characters, letters and numbers only)")
        self.name_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.name_input)
        
        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(50)
        login_btn.clicked.connect(self.handle_login)
        login_btn.setFont(QFont("Arial", 12))
        login_btn.setToolTip("Click to login with the entered name")
        layout.addWidget(login_btn)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
    def handle_login(self):
        
        player_name = self.name_input.text().strip()
        
        if not player_name:
            QMessageBox.warning(self, "Invalid Input", "Name field cannot be empty. Please enter your name to continue.")
            self.name_input.setFocus()
            return
        
        if len(player_name) < 3:
            QMessageBox.warning(self, "Invalid Input", "Name must be at least 3 characters long. Please enter a longer name.")
            self.name_input.setFocus()
            return
        
        if len(player_name) > 20:
            QMessageBox.warning(self, "Invalid Input", "Name must be less than 20 characters. Please enter a shorter name.")
            self.name_input.setFocus()
            return
        
        if not player_name.replace(' ', '').isalnum():
            QMessageBox.warning(self, "Invalid Characters", "Name can only contain letters, numbers, and spaces. Please correct your name.")
            self.name_input.setFocus()
            return
        
        try:
            player_id = self._get_or_create_player(player_name)
            
            player = self.db_manager.get_player(player_id)
            if player:
                self.login_successful.emit(player)
                self.hide()
                QMessageBox.information(
                    self, 
                    "Login Successful", 
                    f"Welcome, {player['name']}! You have successfully logged in."
                )
            else:
                raise Exception("Could not retrieve player data. Please try again.")
                
        except Exception as e:
            QMessageBox.critical(self, "Login Failed", f"An error occurred during login: {str(e)}\nPlease try again.")
            self.name_input.setFocus()
            
    def _get_or_create_player(self, name: str) -> int:
        
        player = self.db_manager.find_player_by_name(name)
        
        if player:
            stats = self.db_manager.get_player_statistics(player['id'])
            
            win_rate = (stats['games_won'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
            accuracy = (stats['total_hits'] / stats['total_shots'] * 100) if stats['total_shots'] > 0 else 0
            
            welcome_message = f"""
            🎉 Welcome back, {player['name']}! 🎉

            📊 **Your Statistics:**
            -----------------------
            - **Games Played:** {stats['games_played']}
            - **Games Won:** {stats['games_won']}
            - **Win Rate:** {win_rate:.1f}%
            - **Total Shots:** {stats['total_shots']}
            - **Total Hits:** {stats['total_hits']}
            - **Accuracy:** {accuracy:.1f}%
            - **Best Game:** {stats['best_game'] if stats['best_game'] else 'N/A'} moves
            
            Keep up the great work and aim for higher stats!
            """
            
            QMessageBox.information(
                self, 
                "Welcome Back", 
                welcome_message
            )
            return player['id']
        else:
            player_id = self.db_manager.create_player(name)
            QMessageBox.information(
                self, 
                "Welcome to Battleship", 
                f"🎉 Welcome, {name}! 🎉\nYour account has been created successfully.\nGood luck in your first game!"
            )
            return player_id 