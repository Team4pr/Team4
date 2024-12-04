from grid import Grid
from instructions_screen import InstructionsScreen

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt, QTimer

## Universal Ui elements colors
WATER_COLOR = '#3398fa'
SHIP_COLOR = '#808080'
HIT_COLOR = '#FF0000'
MISS_COLOR = '#FFFFFF'

class MainWindow(QMainWindow):

    def __init__(self, game_controller):
        super().__init__()

        self.game_controller = game_controller
        self.instructions_window = InstructionsScreen()
        self.player_grid_buttons = []  # Array storing the player's grid buttons
        self.ai_grid_buttons = []  # Array storing the opponent's grid buttons
        self.selected_ship = None  # The ship currently assigned to the position
        self.selected_orientation = 'horizontal'  # Ship's orientation (horizontal/vertical)
        self.selected_attack_pos = None  # Initialize selected_attack_pos
        
        self.init_ui()  # Start UI configuration

    def init_ui(self):
        # Set the window title size to display.
        self.setWindowTitle('Battleship Game')
        self.showFullScreen()

        # Create the central element and the main layout
        central_widget = QWidget()  # Create a new central element
        self.setCentralWidget(central_widget)  # Set it as the center element of the window
        main_layout = QHBoxLayout(central_widget)  # Create a horizontal layout for the center element

        # Create the three main sections of the interface
        player_section = self.create_grid_section("Your Fleet", is_player=True)  # Player grid section
        ai_section = self.create_grid_section("Enemy Waters", is_player=False)  # Opponent grid section
        control_panel = self.create_control_panel()  # Central control panel

        # Add sections in order to the main layout
        main_layout.addLayout(player_section)  # Player grid on the left
        main_layout.addLayout(control_panel)  # Control panel in the middle
        main_layout.addLayout(ai_section)  # Opponent grid on the right

    def create_grid_section(self, title, is_player):
        # Create main layout
        layout = QVBoxLayout()

        # Add title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Create the grid
        grid = QGridLayout()
        grid.setSpacing(1)  # Set the spacing between cells

        # Get the grid size
        grid_size = Grid().size

        grid_all_buttons = []  # Array to store buttons

        # Create grid buttons
        for row in range(grid_size):
            row_buttons = []  # Row of buttons
            for col in range(grid_size):
                # Create a new button
                grid_button = QPushButton()
                # Set the button size based on the grid size (max 600px)
                button_size = min(40, 600 // grid_size)
                grid_button.setFixedSize(button_size, button_size)
                grid_button.setStyleSheet("background-color: #1E90FF;")

                # Bind the appropriate event to the button according to the grid type
                if not is_player:
                    # Bind the attack event to the opponent's grid
                    grid_button.clicked.connect(
                        lambda checked, r=row, c=col: self.handle_attack(r, c))
                else:
                    # Bind the ship placement event to the player's grid
                    grid_button.clicked.connect(
                        lambda checked, r=row, c=col: self.handle_ship_placement(r, c))

                # Add the button to the grid and the array
                grid.addWidget(grid_button, row, col)
                row_buttons.append(grid_button)
            grid_all_buttons.append(row_buttons)

        # Store the buttons in the appropriate variable
        if is_player:
            self.player_grid_buttons = grid_all_buttons
        else:
            self.ai_grid_buttons = grid_all_buttons

        # Add the grid to the main layout
        layout.addLayout(grid)
        return layout

    def create_control_panel(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Set the spacing between elements

        # Status panel
        status_panel = QVBoxLayout()

        # Last action label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)  # Allow text wrapping
        self.status_label.setStyleSheet("font-size: 24px; margin: 5px;")
        status_panel.addWidget(self.status_label)

        layout.addLayout(status_panel)

        # Game Controls Set
        game_controls = QVBoxLayout()
        game_controls.setSpacing(10)

        # New Game Button
        new_game_btn = QPushButton("New Game")
        new_game_btn.setMinimumSize(200, 50)
        new_game_btn.clicked.connect(self.start_new_game)
        new_game_btn.setStyleSheet("background-color: #00cc35; font-size: 14px; color: #f4f4f4; padding: 10px")
        game_controls.addWidget(new_game_btn)

        # Instructions Button
        instructions_btn = QPushButton("Instructions")
        instructions_btn.setMinimumSize(200, 50)
        instructions_btn.clicked.connect(self.show_instructions)
        instructions_btn.setStyleSheet("background-color: #0faaff; font-size: 14px; color: #f4f4f4; padding: 10px")
        game_controls.addWidget(instructions_btn)

        # End game button
        self.end_game_btn = QPushButton("End Game")
        self.end_game_btn.clicked.connect(self.return_start_window)
        self.end_game_btn.setStyleSheet("background-color: #e52c3b; font-size: 14px; color: #f4f4f4; padding: 10px")
        game_controls.addWidget(self.end_game_btn)

        # Ship Placement Controls
        self.ship_placement_group = QVBoxLayout()

        # Ship selection button
        self.ship_buttons = {}
        if self.game_controller.player:
            for ship_name, size in self.game_controller.player.remaining_ships:
                btn = QPushButton(f"{ship_name} ({size} cells)")
                btn.clicked.connect(lambda checked, name=ship_name: self.select_ship(name))
                btn.setStyleSheet("background-color: #56307b; color: #f4f4f4; padding: 10px")
                self.ship_buttons[ship_name] = btn
                self.ship_placement_group.addWidget(btn)

        # Orientation change button
        self.orientation_btn = QPushButton("Rotate Ship (Horizontal)")
        self.orientation_btn.clicked.connect(self.toggle_orientation)
        self.orientation_btn.setStyleSheet("background-color: #56307b; color: #f4f4f4; padding: 10px")
        self.ship_placement_group.addWidget(self.orientation_btn)

        # Random mode button
        random_placement_btn = QPushButton("Random Ship Placement")
        random_placement_btn.clicked.connect(self.random_ship_placement)
        random_placement_btn.setStyleSheet("background-color:  #c45790; font-size: 14px; color: #f4f4f4;"
                                            "padding: 10px; font-weight: bold;")
        self.ship_placement_group.addWidget(random_placement_btn)

        game_controls.addLayout(self.ship_placement_group)

        # Fire button
        self.fire_btn = QPushButton("Fire!")
        self.fire_btn.setMinimumSize(200, 50)
        self.fire_btn.clicked.connect(self.confirm_attack)
        self.fire_btn.setEnabled(False)  
        self.fire_btn.setStyleSheet("""
            QPushButton {
                color: #f4f4f4;
                background-color: #e52c3b;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        game_controls.addWidget(self.fire_btn)

        layout.addLayout(game_controls)

        # Show statistics
        self.stats_label = QLabel()
        self.update_stats_display()
        layout.addWidget(self.stats_label)

        return layout

    def handle_ship_placement(self, row, col):
        # Check ship selection before attempting to place
        if not self.selected_ship:
            self.update_turn_status("Select a ship first!")
            return

        # Attempt to place the ship at the specified location using the controller
        if self.game_controller.place_player_ship(self.selected_ship, (row, col), self.selected_orientation):
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
                self.update_turn_status("All ships placed! Game started - Your turn!")
            else:
                self.update_turn_status("Select next ship to place")
        else:
            self.update_turn_status("Invalid placement! Try another position")

    def select_ship(self, ship_name):
        self.selected_ship = ship_name
        self.update_turn_status(f"Place your {ship_name}")

    def toggle_orientation(self):
        self.selected_orientation = 'vertical' if self.selected_orientation == 'horizontal' else 'horizontal'
        self.orientation_btn.setText(f"Rotate Ship ({self.selected_orientation})")

    def random_ship_placement(self):
        if self.game_controller.place_player_ships_randomly():  
            self.update_player_grid() 
            for btn in self.ship_buttons.values():  
                btn.setEnabled(False)
            self.start_game()  # Start the game after placing ships

    def update_turn_status(self, message):
        self.status_label.setText(message)

    def handle_attack(self, row, col):
        # Set target and activate Fire button
        self.selected_attack_pos = (row, col)
        self.fire_btn.setEnabled(True)
        self._highlight_selected_cell(row, col)

    def _highlight_selected_cell(self, row, col):
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

        ## checks if previously attacked
        if not hasattr(self, 'selected_attack_pos'):
            return
        row, col = self.selected_attack_pos
        # Execute the attack
        result = self.game_controller.process_player_shot((row, col))
        if not result['valid']:
            self.update_turn_status("Invalid attack!")
            return
        # Refresh the AI grid
        button = self.ai_grid_buttons[row][col]
        if result['hit']:
            button.setStyleSheet(f"background-color: {HIT_COLOR};")
        else:
            button.setStyleSheet(f"background-color: {MISS_COLOR};")

        # Disable the Fire button and remove the specified grid button
        self.fire_btn.setEnabled(False)
        delattr(self, 'selected_attack_pos')

        self.update_turn_status("Attack processed!")
        self.update_stats_display()

        # Check if the game is over
        if result['game_over']:
            self.game_over(result['winner'])
        else:
            self._disable_ai_grid()
            self.update_turn_status("AI Turn")

            ## waits before running the ai turn
            QTimer.singleShot(1000, self._execute_ai_turn)





    ## AI STUFF #######
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
            message = "AI Hit!"
            if result['sunk']:
                message += f" AI sunk your {result['ship_name']}!"
        else:
            button.setStyleSheet(f"background-color: {MISS_COLOR};")
            message = "AI Missed!"

        self.update_turn_status(message)
        self.update_stats_display()

        if result['game_over']:
            self.game_over(result['winner'])
        else:
            self._enable_ai_grid()

            ## waits before chaning the turn label
            QTimer.singleShot(1000, lambda: self.update_turn_status("Your turn!"))

    def _disable_ai_grid(self):
        self.set_ai_grid_enabled(False)

    def _enable_ai_grid(self):
        self.set_ai_grid_enabled(True)

    def set_ai_grid_enabled(self, enabled):
        for row in self.ai_grid_buttons:
            for button in row:
                button.setEnabled(enabled)

                


    def update_player_grid(self):
        grid_size = self.game_controller.grid_size
        # Update each cell in the grid only if its state changes
        for row in range(grid_size):
            for col in range(grid_size):
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
        self.game_controller.start_new_game()
        self.reset_ui()
        self.update_turn_status("Place your ships!")

    def start_game(self):
        """Start the game after placing the ships"""
        # Disable ship mode controls
        self.orientation_btn.setEnabled(False)
        for btn in self.ship_buttons.values():
            btn.setEnabled(False)

        # Reset attack controls
        self.fire_btn.setEnabled(False)

        # Enable AI Network for First Round
        self._enable_ai_grid()

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
        self.update_turn_status("Place your ships!")  # Update game status

        # Reset attack related variables
        if hasattr(self, 'selected_attack_pos'):
            delattr(self, 'selected_attack_pos')  # Remove the specified attack site if it exists.
        self.fire_btn.setEnabled(False)  # Disable attack button

    def update_stats_display(self):
        """Update game statistics display"""
        stats = self.game_controller.stats
        player_name = getattr(self.game_controller, 'current_player_name', 'Unknown Player')

        if stats['total_shots'] > 0:
            accuracy = (stats['hits'] / stats['total_shots']) * 100
        else:
            accuracy = 0

        stats_text = f"""
        Player: {player_name}
        ---------------
        Current Game:
        - Shots: {stats['total_shots']}
        - Hits: {stats['hits']}
        - Misses: {stats['misses']}
        - Accuracy: {accuracy:.1f}%
        """
        self.stats_label.setText(stats_text)

    def game_over(self, winner):
        if winner == 'player':
            message = "Congratulations! You Won!"
        else:
            message = "Game Over! AI Wins!"

        # Popup message
        QMessageBox.information(self, 'Game Over', message)

    def show_instructions(self):
        self.instructions_window.setWindowFlags(Qt.WindowType.Window)
        self.instructions_window.setWindowTitle("Game Instructions")
        self.instructions_window.showFullScreen()
        self.instructions_window.show()
        self.instructions_window.raise_()

    # Hides the gameplay window to show the starting window
    def return_start_window(self):
        self.hide()