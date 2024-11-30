from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from constants import GRID_SIZE, CELL_SIZE, WATER_COLOR, SHIP_COLOR, HIT_COLOR, MISS_COLOR
import logging

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


class MainWindow(QMainWindow):
    

    def __init__(self, game_controller):
        
        super().__init__()
        self.game_controller = game_controller  
        self.player_grid_buttons = []  # Array storing the player's grid buttons
        self.ai_grid_buttons = []  # # Array storing the oppenent's grid buttons
        self.selected_ship = None  # The ship currently assigned to the position
        self.selected_orientation = 'horizontal' # Ship's orientation (horizontal/vertical)
        self.selected_attack_pos = None  # Initialize selected_attack_pos
        self.init_ui()  # Start UI configuration

    # Extract CSS styles into constants
    BUTTON_STYLE = """
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
        }
    """

    def init_ui(self):
        
        # Set the window title and minimum size to display.
        self.setWindowTitle('Battleship Game')
        self.setMinimumSize(1200, 600)

        # Create the central element and the main layout
        central_widget = QWidget()  # Create a new central element
        self.setCentralWidget(central_widget)  # Set it as the center element of the window
        main_layout = QHBoxLayout(central_widget)  # Create a horizontal layout for the center element

        # Create the three main sections of the interface
        player_section = self.create_grid_section("Your Fleet", is_player=True)  # Player grid section
        ai_section = self.create_grid_section("Enemy Waters", is_player=False)  # Opponent grid section
        control_panel = self.create_control_panel()  # # Central control panel

        #  Add sections in order to the main layout
        main_layout.addLayout(player_section)  # Player grid on the left
        main_layout.addLayout(control_panel)  # Control panel in the middle
        main_layout.addLayout(ai_section)  # Opponent grid on the right

        # Apply design style to interface elements
        self.setStyleSheet(self.BUTTON_STYLE + """
            QLabel {
                color: #2c3e50;           
                font-size: 14px;           
            }
        """)

    def create_grid_section(self, title: str, is_player: bool) -> QVBoxLayout:
       
        # Create main layout
        layout = QVBoxLayout()

        #  Add title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Create grid with current size from console Set distance between cells
        grid = QGridLayout()
        grid.setSpacing(1)  # Set the spacing between cells

        # Get the current grid size
        current_size = self.game_controller.grid_size
        buttons = []  # Array to store buttons

        # Create grid buttons
        for row in range(current_size):
            row_buttons = []  #  Row of buttons
            for col in range(current_size):
                # Create a new button
                button = QPushButton()
                # Set the button size based on the grid size (max 600px)
                button_size = min(40, 600 // current_size)
                button.setFixedSize(button_size, button_size)
                button.setStyleSheet(f"background-color: {WATER_COLOR};")

                # Bind the appropriate event to the button according to the grid type
                if not is_player:
                    # Bind the attack event to the opponent's grid
                    button.clicked.connect(
                        lambda checked, r=row, c=col: self.handle_attack(r, c))
                else:
                    # Bind the ship placement event to the player's grid
                    button.clicked.connect(
                        lambda checked, r=row, c=col: self.handle_ship_placement(r, c))

                # Add the button to the grid and the array
                grid.addWidget(button, row, col)
                row_buttons.append(button)
            buttons.append(row_buttons)

        # Store the buttons in the appropriate variable
        if is_player:
            self.player_grid_buttons = buttons
        else:
            self.ai_grid_buttons = buttons

        # Add the grid to the main layout
        layout.addLayout(grid)
        return layout

    def create_control_panel(self) -> QVBoxLayout:
        
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Set the spacing between elements

        # Status panel
        status_panel = QVBoxLayout()

        # Game state label
        self.status_label = QLabel("Welcome to Battleship!")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                background-color: #f0f0f0;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        status_panel.addWidget(self.status_label)

        #  Current role indicator
        self.turn_label = QLabel("Game not started")
        self.turn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.turn_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
                margin: 5px;
            }
        """)
        status_panel.addWidget(self.turn_label)

        # Last action label
        self.action_label = QLabel("")
        self.action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.action_label.setWordWrap(True)  # Allow text wrapping
        self.action_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 10px;
                margin: 5px;
                min-height: 50px;
            }
        """)
        status_panel.addWidget(self.action_label)

        layout.addLayout(status_panel)

        #  Game Controls Set
        game_controls = QVBoxLayout()
        game_controls.setSpacing(10)

        # New Game Button
        new_game_btn = QPushButton("New Game")
        new_game_btn.setMinimumSize(200, 50)
        new_game_btn.clicked.connect(self.start_new_game)
        new_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        game_controls.addWidget(new_game_btn)

        # Ship Placement Controls
        self.ship_placement_group = QVBoxLayout()

        # Ship selection button
        self.ship_buttons = {}
        if self.game_controller.player:
            for ship_name, size in self.game_controller.player.remaining_ships:
                btn = QPushButton(f"{ship_name} ({size} cells)")
                btn.clicked.connect(lambda checked, name=ship_name: self.select_ship(name))
                self.ship_buttons[ship_name] = btn
                self.ship_placement_group.addWidget(btn)

        # Orientation change button
        self.orientation_btn = QPushButton("Rotate Ship (Horizontal)")
        self.orientation_btn.clicked.connect(self.toggle_orientation)
        self.ship_placement_group.addWidget(self.orientation_btn)

        # Random mode button
        random_placement_btn = QPushButton("Random Ship Placement")
        random_placement_btn.clicked.connect(self.random_ship_placement)
        random_placement_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.ship_placement_group.addWidget(random_placement_btn)

        game_controls.addLayout(self.ship_placement_group)

        # Fire button
        self.fire_btn = QPushButton("Fire!")
        self.fire_btn.setMinimumSize(200, 50)
        self.fire_btn.clicked.connect(self.confirm_attack)
        self.fire_btn.setEnabled(False)  
        self.fire_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        game_controls.addWidget(self.fire_btn)

        # End game button
        self.end_game_btn = QPushButton("End Game")
        self.end_game_btn.clicked.connect(self.confirm_end_game)
        self.end_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        game_controls.addWidget(self.end_game_btn)

        layout.addLayout(game_controls)

        # Show statistics
        self.stats_label = QLabel()
        self.update_stats_display()
        layout.addWidget(self.stats_label)

        layout.addStretch()  # إضافة مسافة مرنة في النهاية
        return layout

    def handle_attack(self, row: int, col: int):
        
        # Input validation
        if not (0 <= row < self.game_controller.grid_size) or not (0 <= col < self.game_controller.grid_size):
            self.update_status("Invalid target position!")
            return

        # Check game state and player role
        if self.game_controller.get_game_state() != 'playing':
            self.action_label.setText("Game hasn't started yet!")
            return

        if self.game_controller.current_turn != 'player':
            self.action_label.setText("Wait for your turn!")
            return

        #  Check target validity
        if self.game_controller.get_cell_state(False, (row, col)) in ['hit', 'miss']:
            self.action_label.setText("You already fired at this position!")
            return

        # Set target and activate Fire button
        self.selected_attack_pos = (row, col)
        self.fire_btn.setEnabled(True)
        self._highlight_selected_cell(row, col)

        # Update game state
        self.action_label.setText("Press Fire! to attack selected position")
        self.turn_label.setText("Your Turn")
        self.turn_label.setStyleSheet("""
            QLabel {
                background-color: #2ecc71;
                color: white;
            }
        """)

    def _highlight_selected_cell(self, row: int, col: int):
       
        # Reset all cells format to their original state
        for r in range(len(self.ai_grid_buttons)):
            for c in range(len(self.ai_grid_buttons[r])):
                cell_state = self.game_controller.get_cell_state(False, (r, c))
                if cell_state == 'hit':
                    self.ai_grid_buttons[r][c].setStyleSheet(f"background-color: {HIT_COLOR};")
                elif cell_state == 'miss':
                    self.ai_grid_buttons[r][c].setStyleSheet(f"background-color: {MISS_COLOR};")
                else:
                    self.ai_grid_buttons[r][c].setStyleSheet(f"background-color: {WATER_COLOR};")

        # Highlight the selected cell while keeping its original color
        cell_state = self.game_controller.get_cell_state(False, (row, col))
        base_color = {
            'hit': HIT_COLOR,
            'miss': MISS_COLOR,
            'empty': WATER_COLOR,
        }.get(cell_state, WATER_COLOR)

        # Apply hover formatting while keeping its original color
        self.ai_grid_buttons[row][col].setStyleSheet(f"""
            QPushButton {{
                background-color: {base_color};
                border: 2px solid #e74c3c;
            }}
            QPushButton:hover {{
                background-color: {base_color};
                border: 3px solid #c0392b;
            }}
        """)

    def confirm_attack(self):
       
        if not hasattr(self, 'selected_attack_pos'):
            return
        row, col = self.selected_attack_pos
        # Execute the attack
        result = self.game_controller.process_player_shot((row, col))
        if not result['valid']:
            self.update_status(result['message'])
            return
        # Refresh the AI ​​grid
        button = self.ai_grid_buttons[row][col]
        if result['hit']:
            button.setStyleSheet(f"background-color: {HIT_COLOR};")
        else:
            button.setStyleSheet(f"background-color: {MISS_COLOR};")

        # Disable the Fire button and remove the specified location
        self.fire_btn.setEnabled(False)
        delattr(self, 'selected_attack_pos')

        self.update_status(result['message'])
        self.update_stats_display()

        # Check the game is over
        if result['game_over']:
            self.game_over(result['winner'])
        else:
            
            self._disable_ai_grid()
            
            QTimer.singleShot(1000, self.process_ai_turn)

    def process_ai_turn(self):
       
        self.update_status("AI is thinking...")
        QTimer.singleShot(500, self._execute_ai_turn)

    def _execute_ai_turn(self):
        
        # Process AI turn and store result
        result = self.game_controller.process_ai_turn()

        # Validate attack
        if not result['valid']:
            return

        # Get attack coordinates and target cell button
        row, col = result['position']
        button = self.player_grid_buttons[row][col]

        # Process attack result and update interface
        if result['hit']:
            
            button.setStyleSheet(f"background-color: {HIT_COLOR};")
            message = "💥 AI Hit! "
            if result['sunk']:
               
                message += f"AI sunk your {result['ship_name']}! 🚢"
        else:
            
            button.setStyleSheet(f"background-color: {MISS_COLOR};")
            message = "AI Missed! 💨"

        
        self.update_status(message)
        self.update_stats_display()

        
        if result['game_over']:
            self.game_over(result['winner'])
        else:
           
            self._enable_ai_grid()
            # Display player turn message after a short delay
            QTimer.singleShot(500, lambda: self.update_status("Your turn! Select a target"))

    def _disable_ai_grid(self):
       
        self.set_ai_grid_enabled(False)

    def _enable_ai_grid(self):
        
        self.set_ai_grid_enabled(True)

    def set_ai_grid_enabled(self, enabled: bool):
        for row in self.ai_grid_buttons:
            for button in row:
                button.setEnabled(enabled)

    def confirm_end_game(self):
        
        

     if reply == QMessageBox.StandardButton.Y:
        if self.game_controller.get_game_state() == 'ended':
            self.start_new_game()
            return

        # عرض رسالة تأكيد
        reply = QMessageBox.question(
            self, 
            'End Game',
            'Are you sure you want to end the current game?\nThis will count as a loss.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            #  End the current game
            if self.game_controller.force_end_game():
               
                self._disable_all_controls()
               
                self.update_status("Game ended manually")
                
                self.update_stats_display()
                
                QMessageBox.information(self, 'Game Ended', 'The game has been ended.')
                
                QTimer.singleShot(1000, self.start_new_game)

    def _disable_all_controls(self):
        
        self._disable_ai_grid()
        self.fire_btn.setEnabled(False)

        # Disable ship buttons
        for btn in self.ship_buttons.values():
            btn.setEnabled(False)
    
        self.orientation_btn.setEnabled(False)

    def update_game_phase(self):
        
        game_state = self.game_controller.get_game_state()

        # Update the state of the buttons based on the game stage
        # Enable the ship buttons and the direction button only in the setup stage
        for btn in self.ship_buttons.values():
            btn.setEnabled(game_state == 'setup')
        self.orientation_btn.setEnabled(game_state == 'setup')

        # Disable/enable the corresponding grid based on the game phase
        # Enable the opponent's grid only during the game
        for row in self.ai_grid_buttons:
            for button in row:
                button.setEnabled(game_state == 'playing')

        # Update status message by game stage
        if game_state == 'setup':
            
            self.update_status("Place your ships!")
        elif game_state == 'playing':
            if self.game_controller.current_turn == 'player':
                
                self.update_status("Your turn! Select a target")
            else:
               
                self.update_status("AI's turn...")
        elif game_state == 'ended':
           
            self.fire_btn.setEnabled(False)

    def handle_ship_placement(self, row: int, col: int):
        
        # Check ship selection before attempting to place
        if not self.selected_ship:
            self.update_status("Select a ship first!")
            return

        # Attempt to place the ship at the specified location using the controller
        if self.game_controller.place_player_ship(
                self.selected_ship, (row, col), self.selected_orientation):
            # Update the player grid view after successfully placing the ship
            self.update_player_grid()
            # Disable the button of the placed ship
            self.ship_buttons[self.selected_ship].setEnabled(False)
            # Reset the selected ship
            self.selected_ship = None

            # Check if all ships are placed
            if not self.game_controller.player.remaining_ships:
                # Start the game when ships are placed
                self.start_game()
                self.update_status("All ships placed! Game started - Your turn!")
            else:
                
                self.update_status("Select next ship to place")
        else:
           
            self.update_status("Invalid placement! Try another position")

    def select_ship(self, ship_name: str):
        
        self.selected_ship = ship_name
        self.update_status(f"Place your {ship_name}")

    def toggle_orientation(self):
        
        self.selected_orientation = 'vertical' if self.selected_orientation == 'horizontal' else 'horizontal'
        self.orientation_btn.setText(f"Rotate Ship ({self.selected_orientation})")

    def random_ship_placement(self):
        
        if self.game_controller.place_player_ships_randomly():  
            self.update_player_grid() 
            for btn in self.ship_buttons.values():  
                btn.setEnabled(False)
            self.start_game()  # Start the game after placing ships

    def update_player_grid(self):
        
        current_size = self.game_controller.grid_size
        # Update each cell in the grid only if its state changes
        for row in range(current_size):
            for col in range(current_size):
                # Get the cell state from the controller
                state = self.game_controller.get_cell_state(True, (row, col))
                # Get the cell button from the array
                button = self.player_grid_buttons[row][col]
                # Determine the new style based on the state
                new_style = ""
                if state == 'ship':
                    new_style = f"background-color: {SHIP_COLOR};"
                elif state == 'hit':
                    new_style = f"background-color: {HIT_COLOR};"
                elif state == 'miss':
                    new_style = f"background-color: {MISS_COLOR};"
                else:
                    new_style = f"background-color: {WATER_COLOR};"

                # Update style only if it's different
                if button.styleSheet() != new_style:
                    button.setStyleSheet(new_style)

    def start_new_game(self):
        
        # Display confirmation dialog
        reply = QMessageBox.question(
            self, 
            'New Game',
            'Are you sure you want to start a new game?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            
            self.game_controller.start_new_game()
            
            self.reset_ui()
           
            self.update_status("Place your ships!")

    def start_game(self):
        """Start the game after placing the ships"""
        # Disable ship mode controls
        self.orientation_btn.setEnabled(False)
        for btn in self.ship_buttons.values():
            btn.setEnabled(False)

        # Reset attack controls
        self.fire_btn.setEnabled(False)
        if hasattr(self, 'selected_attack_pos'):
            delattr(self, 'selected_attack_pos')

       # Enable AI Network for First Round
        self._enable_ai_grid()

       # start playing
        if self.game_controller.start_gameplay():
            self.update_status("Game started - Select a target and press Fire!")
        else:
            self.update_status("Error starting game!")

    def reset_ui(self):
        """Reset the UI for a new game"""
       # Reset UI to start a new game

        # Create a new center widget and set it as the center widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create grid sections for player and AI with new size
        player_section = self.create_grid_section("Your Fleet", is_player=True)
        ai_section = self.create_grid_section("Enemy Waters", is_player=False)

       # Create a control panel
        control_panel = self.create_control_panel()

        # Add sections to the master layout
        main_layout.addLayout(player_section)
        main_layout.addLayout(control_panel)
        main_layout.addLayout(ai_section)

        # Reset other UI elements
        self.orientation_btn.setEnabled(True)  # Enable direction button
        self.selected_ship = None  # Reset the selected ship
        self.selected_orientation = 'horizontal'  # Reset the selected direction
        self.update_status("Place your ships!")  # Update game status

        # Reset attack related variables
        if hasattr(self, 'selected_attack_pos'):
            delattr(self, 'selected_attack_pos')  # Remove the specified attack site if it exists.
        self.fire_btn.setEnabled(False)  # Disable attack button

    def game_over(self, winner: str):
        """Handle game over"""
        if winner == 'player':
            message = "🎉 Congratulations! You Won! 🎉"
            color = "#2ecc71"  # Green
        else:
            message = "Game Over! AI Wins!"
            color = "#e74c3c"  # Red

        # Update game status
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                background-color: {color};
                color: white;
                border-radius: 8px;
                margin: 5px;
            }}
        """)
        self.status_label.setText(message)
        self.turn_label.setText("Game Over")
        self.action_label.setText(f"Final Score:\nHits: {self.game_controller.stats['hits']}\n"
                                  f"Total Shots: {self.game_controller.stats['total_shots']}")

        # عرض رسالة النتيجة
        QMessageBox.information(self, 'Game Over', message)

        # إعادة تشغيل اللعبة بعد تأخير قصير
        QTimer.singleShot(2000, self.start_new_game)

    def update_status(self, message: str):
        
        self.action_label.setText(message)

        # Update role indicator
        if self.game_controller.get_game_state() == 'playing':
            current_turn = "Your Turn" if self.game_controller.current_turn == 'player' else "AI's Turn"
            self.turn_label.setText(current_turn)

            # Change the color of the role indicator
            if self.game_controller.current_turn == 'player':
                self.turn_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        padding: 10px;
                        background-color: #2ecc71;  /*green for player*/
                        color: white;
                        border-radius: 5px;
                        margin: 5px;
                    }
                """)
            else:
                self.turn_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        padding: 10px;
                        background-color: #e74c3c;  /*red for opponent*/ 
                        color: white;
                        border-radius: 5px;
                        margin: 5px;
                    }
                """)
        else:
            self.turn_label.setText("Game not started")
            self.turn_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    padding: 10px;
                    background-color: #95a5a6;
                    color: white;
                    border-radius: 5px;
                    margin: 5px;
                }
            """)

    def update_stats_display(self):
        "" "Update game statistics display" ""
        stats = self.game_controller.stats
        player_name = getattr(self.game_controller, 'current_player_name', 'Unknown Player')

        if stats['total_shots'] > 0:
            accuracy = (stats['hits'] / stats['total_shots']) * 100
        else:
            accuracy = 0

        stats_text = f"""
        Player: {player_name}
        ---------------
        Total Games: {stats['games_played']}
        Games Won: {stats['games_won']}
        Win Rate: {(stats['games_won'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0:.1f}%
        
        Current Game:
        - Shots: {stats['total_shots']}
        - Hits: {stats['hits']}
        - Misses: {stats['misses']}
        - Accuracy: {accuracy:.1f}%
        """
        self.stats_label.setText(stats_text)

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Display confirmation message before closing
            reply = QMessageBox.question(
                self, 'Exit Game',
                'Are you sure you want to exit the game?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Save game state if it is running
                if self.game_controller.game_state == 'playing':
                    self.game_controller.force_end_game()
                
                # Cleaning resources
                for row in self.player_grid_buttons:
                    for button in row:
                        button.deleteLater()
                for row in self.ai_grid_buttons:
                    for button in row:
                        button.deleteLater()
                    
                event.accept()
            else:
                event.ignore() # Cancel the closure if the user chooses "No"
            
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
            QMessageBox.critical(self, 'Error', 'An error occurred while closing the game.')
            event.accept()

    def show_confirm_dialog(self, message: str) -> bool:
        """Show confirmation dialog"""
        reply = QMessageBox.question(
            self,
            'Confirm Action',
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
