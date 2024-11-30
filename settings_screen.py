from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                           QComboBox, QHBoxLayout, QMessageBox, QTabWidget,
                           QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from constants import GRID_SIZES

class SettingsScreen(QWidget):
   
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, current_settings: dict, current_player_id: int, db_manager=None, parent=None):
        super().__init__(parent)
        self.current_settings = current_settings
        self.current_player_id = current_player_id
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Game Settings & Statistics")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        
        settings_tab = self._create_settings_tab()  
        tabs.addTab(settings_tab, "Settings")
        
        stats_tab = self._create_stats_tab()
        tabs.addTab(stats_tab, "Statistics")
        
        leaderboard_tab = self._create_leaderboard_tab()
        tabs.addTab(leaderboard_tab, "Leaderboard")
        
        achievements_tab = self._create_achievements_tab()
        tabs.addTab(achievements_tab, "Achievements")
        
        layout.addWidget(tabs)
        
    def _create_settings_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        grid_size_layout = QHBoxLayout()
        grid_size_label = QLabel("Grid Size:")
        
        self.grid_size_combo = QComboBox()
        for size in GRID_SIZES:
            self.grid_size_combo.addItem(f"{size}x{size}")
            
        current_index = GRID_SIZES.index(self.current_settings['grid_size'])
        self.grid_size_combo.setCurrentIndex(current_index)
        self.grid_size_combo.setToolTip("Select the size of the game grid.")
        
        grid_size_layout.addWidget(grid_size_label)
        grid_size_layout.addWidget(self.grid_size_combo)
        layout.addLayout(grid_size_layout)
        
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setToolTip("Save the current settings and apply changes.")
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setToolTip("Cancel any changes and close the settings window.")
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        return tab
        
    def _create_stats_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if self.db_manager and self.current_player_id:
            stats = self.db_manager.get_player_statistics(self.current_player_id)
            
            if any(stats.values()):
                stats_table = QTableWidget()
                stats_table.setColumnCount(2)
                stats_table.setHorizontalHeaderLabels(["Statistic", "Value"])
                stats_table.horizontalHeader().setStretchLastSection(True)
                
                stats_data = [
                    ("Games Played", stats.get('games_played', 0)),
                    ("Games Won", stats.get('games_won', 0)),
                    ("Win Rate", f"{stats.get('win_rate', 0):.1f}%"),
                    ("Total Shots", stats.get('total_shots', 0)),
                    ("Total Hits", stats.get('total_hits', 0)),
                    ("Accuracy", f"{stats.get('accuracy_rate', 0):.1f}%"),
                    ("Best Game", stats.get('best_game', 'N/A')),
                    ("Quick Wins", stats.get('quick_wins', 0))
                ]
                
                stats_table.setRowCount(len(stats_data))
                for i, (stat, value) in enumerate(stats_data):
                    stats_table.setItem(i, 0, QTableWidgetItem(stat))
                    stats_table.setItem(i, 1, QTableWidgetItem(str(value)))
                
                layout.addWidget(stats_table)
            else:
                no_stats_label = QLabel("You haven't played any games yet!\nPlay some games to see your statistics here.")
                no_stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_stats_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        color: #7f8c8d;
                        padding: 20px;
                    }
                """)
                layout.addWidget(no_stats_label)
        else:
            layout.addWidget(QLabel("Please log in to view statistics"))
        
        return tab
            
    def _create_leaderboard_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if self.db_manager:
            time_filter_layout = QHBoxLayout()
            time_filter_label = QLabel("Filter by Time Period:")
            self.time_filter_combo = QComboBox()
            self.time_filter_combo.addItems(["All Time", "This Week", "This Month", "This Year"])
            self.time_filter_combo.currentIndexChanged.connect(self.update_leaderboard)
            time_filter_layout.addWidget(time_filter_label)
            time_filter_layout.addWidget(self.time_filter_combo)
            layout.addLayout(time_filter_layout)
            
            self.leaderboard_table = QTableWidget()
            self.leaderboard_table.setColumnCount(5)
            self.leaderboard_table.setHorizontalHeaderLabels([
                "Rank", "Player", "Win Rate", "Games Won", "Accuracy"
            ])
            self.leaderboard_table.horizontalHeader().setStretchLastSection(True)
            
            layout.addWidget(self.leaderboard_table)
            
            self.load_leaderboard("All Time")
        else:
            layout.addWidget(QLabel("Leaderboard unavailable"))
        
        return tab
            
    def _create_achievements_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if self.db_manager and self.current_player_id:
            achievements = self.db_manager.get_player_achievements(self.current_player_id)
            
            if achievements:
                for achievement in achievements:
                    achievement_widget = QWidget()
                    achievement_layout = QHBoxLayout(achievement_widget)
                    
                    icon = QLabel(achievement['icon'])
                    title = QLabel(achievement['title'])
                    description = QLabel(achievement['description'])
                    
                    icon.setFont(QFont("Arial", 16))
                    title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                    description.setFont(QFont("Arial", 12))
                    
                    achievement_layout.addWidget(icon)
                    achievement_layout.addWidget(title)
                    achievement_layout.addWidget(description)
                    
                    layout.addWidget(achievement_widget)
            else:
                no_achievements_label = QLabel(""" 
                    No achievements unlocked yet! 
                    Keep playing to earn achievements: 
                    • Win games 
                    • Improve your accuracy 
                    • Complete special challenges 
                    Your achievements will appear here.
                """)
                no_achievements_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_achievements_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        color: #7f8c8d;
                        padding: 20px;
                    }
                """)
                layout.addWidget(no_achievements_label)
        else:
            layout.addWidget(QLabel("Please log in to view achievements"))
        
        return tab
            
    def save_settings(self):
        grid_size = int(self.grid_size_combo.currentText().split('x')[0])
        
        if grid_size != self.current_settings['grid_size']:
            reply = QMessageBox.question(
                self,
                'Confirm Changes',
                'Changing grid size will start a new game. Continue?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        new_settings = {
            'grid_size': grid_size
        }
        
        if self.db_manager:
            self.db_manager.save_game_settings(self.current_player_id, new_settings)
        
        self.settings_changed.emit(new_settings)
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
        self.close()
        
    def load_leaderboard(self, time_period: str):
        period_mapping = {
            "All Time": "all",
            "This Week": "week",
            "This Month": "month",
            "This Year": "year"
        }
        mapped_period = period_mapping.get(time_period, "all")
        
        leaderboard = self.db_manager.get_leaderboard(limit=10, time_period=mapped_period)
        
        if leaderboard:
            self.leaderboard_table.setRowCount(len(leaderboard))
            for i, player in enumerate(leaderboard):
                self.leaderboard_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.leaderboard_table.setItem(i, 1, QTableWidgetItem(player['name']))
                self.leaderboard_table.setItem(i, 2, QTableWidgetItem(f"{player['win_ratio']:.1f}%"))
                self.leaderboard_table.setItem(i, 3, QTableWidgetItem(str(player['games_won'])))
                self.leaderboard_table.setItem(i, 4, QTableWidgetItem(f"{player['accuracy']:.1f}%"))
        else:
            self.leaderboard_table.setRowCount(0)
            QMessageBox.information(self, "No Data", "No players on the leaderboard for the selected time period.")
    
    def update_leaderboard(self):
        selected_period = self.time_filter_combo.currentText()
        self.load_leaderboard(selected_period)
