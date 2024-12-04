from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QScrollArea, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class InstructionsScreen(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):

        self.setWindowTitle("Battleship Instructions")
        self.setMinimumSize(1920, 1080)
        
        main_layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        title = QLabel("How to Play Battleship")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)

        # Game Overview Section
        section_title = QLabel("Game Overview")
        section_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        content_layout.addWidget(section_title)

        section_content = QLabel(
            "Battleship is a strategy guessing game for two players. It is played on two grids, "
            "on which each player's fleet of ships are marked. The locations of the ships are "
            "hidden from the other player. Players alternate turns calling 'shots' at the other "
            "player's ships, and the objective  is to destroy the opposing player's ships."
        )
        section_content.setFont(QFont("Arial", 12))
        section_content.setWordWrap(True)
        content_layout.addWidget(section_content)

        # Ships Section
        section_title = QLabel("Ships")
        section_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        content_layout.addWidget(section_title)

        section_content = QLabel(
            "Your fleet consists of 5 ships:\n"
            "• Aircraft Carrier - 5 cells long\n"
            "• Battleship - 4 cells long\n"
            "• Submarine - 3 cells long\n"
            "• Destroyer - 3 cells long\n"
            "• Patrol Boat - 2 cells long\n"
            "Each ship occupies a number of consecutive spaces on the grid, arranged either "
            "horizontally or vertically."
        )
        section_content.setFont(QFont("Arial", 12))
        section_content.setWordWrap(True)
        content_layout.addWidget(section_content)

        # Placing Your Ships Section
        section_title = QLabel("Placing Your Ships")
        section_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        content_layout.addWidget(section_title)

        section_content = QLabel(
            "To place your ships:\n"
            "1. Select a ship from the ship buttons on the screen\n"
            "2. Use the 'Rotate Ship' button to change orientation (horizontal/vertical)\n"
            "3. Click on your grid where you want to place the ship\n\n"
            "Rules for placement:\n"
            "• Ships cannot overlap\n"
            "• Ships cannot be placed diagonally\n"
            "• Ships cannot extend beyond the grid\n"
            "• Ships cannot touch each other (including diagonally)\n"
            "You can also use the 'Random Ship Placement' button to automatically place all ships."
        )
        section_content.setFont(QFont("Arial", 12))
        section_content.setWordWrap(True)
        content_layout.addWidget(section_content)

        # How to Play Section
        section_title = QLabel("How to Play")
        section_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        content_layout.addWidget(section_title)

        section_content = QLabel(
            "When all ships are placed, the game begins:\n"
            "1. Click on a cell in the enemy's grid to attack that position\n"
            "2. Red marks indicate hits\n"
            "3. White marks indicate misses\n"
            "4. The AI will automatically take its turn after yours\n"
            "5. When you sink a ship you will see a message\n"
            "The game status will be shown in the middle panel, keeping you informed of:\n"
            "- Whose turn it is\n"
            "- Hit or miss results\n"
            "- Ships that have been sunk"
        )
        section_content.setFont(QFont("Arial", 12))
        section_content.setWordWrap(True)
        content_layout.addWidget(section_content)

        # Winning the Game Section
        section_title = QLabel("Winning the Game")
        section_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        content_layout.addWidget(section_title)

        section_content = QLabel(
            "The game ends when either you or the AI has sunk all of the opponent's ships. "
            "The first player to sink all their opponent's ships wins the game!\n"
            "After the game ends, you can choose to:\n"
            "- Start a new game\n"
            "- View game instructions\n"
            "- Return to the main menu"
        )
        section_content.setFont(QFont("Arial", 12))
        section_content.setWordWrap(True)
        content_layout.addWidget(section_content)

        # Back to Menu Button
        back_btn = QPushButton("Back to Menu")
        back_btn.setMinimumSize(200, 50)
        back_btn.clicked.connect(self.close)
        back_btn.setStyleSheet("background-color: #e52c3b; font-size: 14px;")
        content_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        ## adding a scroll wheel
        scroll.setWidget(content)
        main_layout.addWidget(scroll)