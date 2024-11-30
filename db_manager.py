import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime

class DatabaseError(Exception):
    ## Error Handling
    def __init__(self, message: str):

        super().__init__(message)

class DatabaseManager:
    def __init__(self, db_path: str = 'battleship.db'):
        try:
            ## Establish database connection
            self.conn = sqlite3.connect(db_path)
            
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            self.create_tables()
            
        ## Erorr handling
        except sqlite3.Error as e:
            raise DatabaseError(f"Error: creating data table {str(e)}")

    def execute_safe(self, query: str, params: tuple = ()) -> sqlite3.Cursor:

        try:
            result = self.conn.execute(query, params)
            return result
            
        ## Erorr handling
        except sqlite3.Error as e:
            raise DatabaseError(f"Error: creating data table {str(e)}")

    def create_tables(self):

        try:
            with self.conn:

                # has all data for the player
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS players (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        games_played INTEGER DEFAULT 0,
                        games_won INTEGER DEFAULT 0,
                        total_shots INTEGER DEFAULT 0,
                        total_hits INTEGER DEFAULT 0,
                        accuracy REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_played TIMESTAMP
                    )
                ''')
                
                # player settings
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS player_settings (
                        player_id INTEGER PRIMARY KEY,
                        grid_size INTEGER DEFAULT 10,
                        FOREIGN KEY (player_id) REFERENCES players (id)
                            ON DELETE CASCADE
                    )
                ''')
                
                # game progress
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS game_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_id INTEGER,
                        result TEXT NOT NULL,
                        grid_size INTEGER DEFAULT 10,
                        moves INTEGER,
                        hits INTEGER,
                        misses INTEGER,
                        accuracy REAL,
                        duration INTEGER,
                        played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (player_id) REFERENCES players (id)
                            ON DELETE CASCADE
                    )
                ''')
                
                # ship status
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS ship_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id INTEGER,
                        ship_name TEXT NOT NULL,
                        was_sunk BOOLEAN,
                        hits_taken INTEGER,
                        turns_to_sink INTEGER,
                        FOREIGN KEY (game_id) REFERENCES game_history (id)
                            ON DELETE CASCADE
                    )
                ''')
                
        # Eror handling
        except sqlite3.Error as e:

            print(f"Eror: creating tables {e}")
            raise DatabaseError(f"eror: creating tables {str(e)}")

    def create_player(self, name: str) -> int:

        try:

            with self.conn:

                print(f"Creaitng new player with the name; {name}")
                
                # remove spaces
                clean_name = name.strip()
                
                cursor = self.conn.execute('''
                    INSERT INTO players 
                    (name, games_played, games_won, total_shots, total_hits, accuracy) 
                    VALUES (?, 0, 0, 0, 0, 0.0)
                ''', (clean_name,))
                

                player_id = cursor.lastrowid
                

                print(f"Player created!: {player_id}")
                
                return player_id
                
        # if name already exist
        except sqlite3.IntegrityError:
            print("error: name already exist!")
            raise DatabaseError("error: name already exist!")
            
        # error handling
        except Exception as e:
            print(f"error: creating player {e}")
            raise DatabaseError(f"eror: creating player {str(e)}")

    def get_player(self, player_id: int) -> Optional[Dict]:

        try:

            cursor = self.conn.execute(
                'SELECT * FROM players WHERE id = ?',
                (player_id,)
            )
            
            player_info = cursor.fetchone()
            
            # true when it exists
            if player_info:

                return {
                    'id': player_info[0],                       ## Player ID
                    'name': player_info[1],                     ## Player name
                    'games_played': player_info[2] or 0,        ## Games Played
                    'games_won': player_info[3] or 0,           ## Games won
                    'total_shots': player_info[4] or 0,         ## Total shots
                    'total_hits': player_info[5] or 0,          ## Total hits
                    'accuracy': player_info[6] or 0.0,          ## Hit accuracy
                    'created_at': player_info[7] or None,       ## Player creation date
                    'last_played': player_info[8] or None       ## Last play date
                }
            
            return None
            
        # error handling
        except Exception as e:
            print(f"error in getting player! {e}")
            return None

    def save_game_result(self, player_id: int, result: Dict[str, Any]):

        try:
            # handles the error if the player is not assigned
            if not self.get_player(player_id):
                raise ValueError(f"no player with name: {player_id}")
            
            ## Calculates hit accuracy
            if result['moves'] > 0:
                accuracy = (result['hits'] / result['moves']) * 100
            else:
                accuracy = 0
            
            ## Saves result in game history
            self.execute_safe('''
                INSERT INTO game_history 
                (player_id, result, grid_size, moves, hits, misses, accuracy, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                player_id,
                result['outcome'],
                result.get('grid_size', 10),
                result['moves'],
                result['hits'],
                result['misses'],
                accuracy,
                result['duration']
            ))
            
            ## Updates the player data
            self.execute_safe('''
                UPDATE players 
                SET games_played = games_played + 1,
                    games_won = games_won + CASE WHEN ? = 'win' THEN 1 ELSE 0 END,
                    total_shots = total_shots + ?,
                    total_hits = total_hits + ?,
                    accuracy = (total_hits * 100.0 / NULLIF(total_shots, 0)),
                    last_played = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                result['outcome'],
                result['moves'],
                result['hits'],
                player_id
            ))

        # error handling    
        except Exception as e:

            print(f"Error while saving game! {e}")
            raise

    def get_player_statistics(self, player_id: int) -> Dict[str, Any]:

        try:

            cursor = self.conn.execute('''
                SELECT 
                    p.games_played,
                    p.games_won,
                    p.total_shots,
                    p.total_hits,
                    p.accuracy,
                    MIN(g.moves) as best_game,
                    MAX(g.moves) as worst_game,
                    AVG(g.duration) as avg_duration,
                    COUNT(CASE WHEN g.result = 'win' AND g.moves <= 30 THEN 1 END) as quick_wins,
                    ROUND(CAST(p.games_won AS FLOAT) / NULLIF(p.games_played, 0) * 100, 2) as win_rate,
                    ROUND(AVG(g.accuracy), 2) as accuracy_rate
                FROM players p
                LEFT JOIN game_history g ON p.id = g.player_id
                WHERE p.id = ?
                GROUP BY p.id
            ''', (player_id,))
            
            row = cursor.fetchone()
            
            ## If the data row exists
            if row:
                return {
                    'games_played': row[0],          ## Total games played
                    'games_won': row[1],             ## Total games won
                    'total_shots': row[2],           ## Total shots
                    'total_hits': row[3],            ## Total hits
                    'accuracy': row[4],              ## Hit accuracy
                    'best_game': row[5],             ## Best game (least hits taken)
                    'worst_game': row[6],            ## Worst game (highest hits taken)
                    'avg_duration': row[7],          ## Average game duration
                    'quick_wins': row[8],            ## Quick wins (win in under 30 moves)
                    'win_rate': row[9],              ## Win rate
                    'accuracy_rate': row[10]         ## Hit accuracy rate
                }
            
            return {}
        
        # erro handling
        except Exception as e:

            print(f"error while retrieving stats {e}")
            return {}

    def get_game_history(self, player_id: int, limit: int = 10) -> List[Dict]:

        try:

            cursor = self.conn.execute('''
                SELECT * FROM game_history 
                WHERE player_id = ?
                ORDER BY played_at DESC
                LIMIT ?
            ''', (player_id, limit))
            

            all_games = cursor.fetchall()
            
            games_list = []
            
            for row in all_games:
                game_info = {
                    'id': row[0],               ## Game ID
                    'result': row[2],           ## Game result
                    'grid_size': row[3],        ## Game grid size
                    'moves': row[4],            ## Number of moves
                    'hits': row[5],             ## Number of hits
                    'misses': row[6],           ## Number of misses
                    'accuracy': row[7],         ## Hit accuracy
                    'duration': row[8],         ## Game duration
                    'played_at': row[10]        ## Game date
                }

                games_list.append(game_info)
            
            return games_list
        
        ## Error handling
        except Exception as e:
            print(f"Error while retrieving games data! {e}")
            return []

    def close(self):

        # closes the connectiong to database
        self.conn.close()

    def get_leaderboard(self, limit: int = 10, time_period: str = 'all') -> List[Dict]:

        try:

            time_filter = ''
            if time_period == 'week':
                time_filter = "AND g.played_at >= date('now', '-7 days')"  # Last week
            elif time_period == 'month':
                time_filter = "AND g.played_at >= date('now', '-1 month')"  # Last month
            elif time_period == 'year':
                time_filter = "AND g.played_at >= date('now', '-1 year')"  # Last year

            ## Fetch the data
            cursor = self.conn.execute(f'''
                WITH PlayerStats AS (
                    SELECT 
                        p.name,                                                    -- Player Name
                        COUNT(DISTINCT g.id) as games_played,                      -- Games Played
                        SUM(CASE WHEN g.result = 'win' THEN 1 ELSE 0 END) as games_won,  -- Game Won
                        AVG(g.accuracy) as avg_accuracy,                           -- Average Hit Accuracy
                        MIN(g.moves) as best_game,                                -- Best Game (Least moves)
                        COUNT(DISTINCT CASE WHEN g.result = 'win' AND g.moves <= 30 
                            THEN g.id END) as quick_wins                          -- Quick Wins
                    FROM players p
                    LEFT JOIN game_history g ON p.id = g.player_id
                    WHERE 1=1 {time_filter}
                    GROUP BY p.id, p.name
                    HAVING games_played > 0
                )
                SELECT 
                    name,
                    games_played,
                    games_won,
                    ROUND(CAST(games_won AS FLOAT) / games_played * 100, 2) as win_ratio,  -- Win Rate
                    ROUND(avg_accuracy, 2) as accuracy,                                     -- Accuracy
                    best_game,
                    quick_wins,
                    ROUND(CAST(quick_wins AS FLOAT) / games_won * 100, 2) as quick_win_ratio  -- Quick Win Rate
                FROM PlayerStats
                ORDER BY win_ratio DESC, accuracy DESC
                LIMIT ?
            ''', (limit,))

            results = []
            for row in cursor.fetchall():
                player_info = {
                    'name': row[0],
                    'games_played': row[1],
                    'games_won': row[2],
                    'win_ratio': row[3],
                    'accuracy': row[4],
                    'best_game': row[5],
                    'quick_wins': row[6],
                    'quick_win_ratio': row[7]
                }
                results.append(player_info)
            
            return results
        
        # error handling
        except Exception as e:

            print(f"error: in leaderboards {e}")
            return []

    def get_ship_statistics(self, player_id: int) -> Dict[str, Any]:

        cursor = self.conn.execute('''
            SELECT 
                sh.ship_name,                   -- Ship Name
                COUNT(*) as total_battles,      -- Total Battles
                -- عدد مرات الغرق
                SUM(CASE WHEN sh.was_sunk THEN 1 ELSE 0 END) as times_sunk,
                AVG(sh.hits_taken) as avg_hits_taken,        -- Average Hits
                AVG(sh.turns_to_sink) as avg_turns_to_sink   -- Average turns to sink
            FROM ship_statistics sh
            JOIN game_history gh ON sh.game_id = gh.id
            WHERE gh.player_id = ?
            GROUP BY sh.ship_name
        ''', (player_id,))
        
        ship_stats = {}
        for row in cursor.fetchall():
            ship_name = row[0]
            ship_stats[ship_name] = {
                'total_battles': row[1],      # Total battles
                'times_sunk': row[2],         # Times sunk
                'avg_hits_taken': row[3],     # Average hits taken
                'avg_turns_to_sink': row[4]   # Average turns to sink
            }
        
        return ship_stats

    def save_game_settings(self, player_id: int, settings: Dict[str, Any]):

        grid_size = settings.get('grid_size', 10)         # If not exist default to 10
        sound_on = settings.get('sound_enabled', True)    # If not exist default to True
        music_on = settings.get('music_enabled', True)    # If not exist default to True
        
        ## Stores settings in the database
        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO player_settings 
                (player_id, grid_size, sound_enabled, music_enabled)
                VALUES (?, ?, ?, ?)
            ''', (player_id, grid_size, sound_on, music_on))

    def get_game_settings(self, player_id: int) -> Dict[str, Any]:

        cursor = self.conn.execute('''
            SELECT grid_size, sound_enabled, music_enabled
            FROM player_settings
            WHERE player_id = ?
        ''', (player_id,))
        
        settings_from_db = cursor.fetchone()
        
        ## If settings exist already
        if settings_from_db:
            game_settings = {
                'grid_size': settings_from_db[0],  ## Get grid size
                'sound_enabled': bool(settings_from_db[1]),  ## Sound-effects on or off
                'music_enabled': bool(settings_from_db[2])   ## Background music on or off
            }
            return game_settings
            
        ## If settings do not exist already
        default_settings = {
            'grid_size': 10,       ## Grid size default to 10x10
            'sound_enabled': True,  ## Sound-effects default to on
            'music_enabled': True   ## Background music default to on
        }
        return default_settings

    def delete_player_data(self, player_id: int):

        with self.conn:

            self.conn.execute('''
                DELETE FROM ship_statistics 
                WHERE game_id IN (
                    SELECT id FROM game_history WHERE player_id = ?
                )
            ''', (player_id,))
            
            self.conn.execute('''
                DELETE FROM game_history 
                WHERE player_id = ?
            ''', (player_id,))
            
            self.conn.execute('''
                DELETE FROM player_settings 
                WHERE player_id = ?
            ''', (player_id,))
            
            self.conn.execute('''
                DELETE FROM players 
                WHERE id = ?
            ''', (player_id,))

    def check_connection(self) -> bool:

        try:
            self.conn.execute("SELECT 1")
            return True
            
        except sqlite3.Error:
            return False

    def reconnect(self):

        try:

            connection_status = self.check_connection()
            
            if not connection_status:

                self.conn = sqlite3.connect('battleship.db')
                self.conn.execute("PRAGMA foreign_keys = ON")
                
        ## Error handling
        except sqlite3.Error as e:
            raise DatabaseError(f"Reconnection failed! {str(e)}")

    def backup_database(self, backup_path: str):

        try:

            database_backup = sqlite3.connect(backup_path)

            with database_backup:
                self.conn.backup(database_backup)
            
            database_backup.close()
        
        ## Error handling
        except sqlite3.Error as problem:
            raise DatabaseError(f"Backup failed! {str(problem)}")

    def find_player_by_name(self, name: str) -> Optional[Dict]:

        try:

            found_player = name.strip()
            
            search_result = self.conn.execute(
                'SELECT * FROM players WHERE LOWER(name) = LOWER(?)', 
                (found_player,)
            )
            
            player_info = search_result.fetchone()
            
            if player_info:

                return {
                    'id': player_info[0],
                    'name': player_info[1],
                    'games_played': player_info[2] if player_info[2] is not None else 0,
                    'games_won': player_info[3] if player_info[3] is not None else 0,
                    'total_shots': player_info[4] if player_info[4] is not None else 0,
                    'total_hits': player_info[5] if player_info[5] is not None else 0,
                    'accuracy': player_info[6] if player_info[6] is not None else 0.0,
                    'created_at': player_info[7],
                    'last_played': player_info[8]
                }
            
            return None
            
        except Exception as problem:
            print(f"Error finding player with name: {problem}")
            return None

    def get_player_achievements(self, player_id: int) -> List[Dict]:

        ## Holds the achievements the player has
        achievements = []
        
        try:

            ## Retrieves player stats
            stats = self.get_player_statistics(player_id)
            
            ## Expert Player achievement
            if stats['games_played'] >= 100:

                ## Adds the achievement
                achievements.append({
                    'title': 'Expert Player',
                    'description': 'Played more than 100 games',
                    'icon': '🎮'
                })
            
            ## Winner Player achievement
            if stats['win_rate'] >= 75:
                
                ## Adds the achievement
                achievements.append({
                    'title': 'Winner Player', 
                    'description': 'Achieved 75% win rate',
                    'icon': '👑'
                })
            
            ## Bulls-eye Player achievement
            if stats['accuracy_rate'] >= 50:

                ## Adds the achievement
                achievements.append({
                    'title': 'Bulls-eye Player',
                    'description': 'Achieved 50% accuracy', 
                    'icon': '🎯'
                })
            
            ## Speed-runner Player achievement
            if stats['quick_wins'] >= 10:

                ## Adds the achievement
                achievements.append({
                    'title': 'Speed-runner Player',
                    'description': 'Win 10 times in less than 30 moves',
                    'icon': '⚡'
                })
            
            return achievements
        
        ## Error handling
        except Exception as e:
            print(f"Error: player achievements {e}")
            return []

    def get_player_progress(self, player_id: int) -> Dict[str, Any]:

        try:

            cursor = self.conn.execute('''
                WITH GameProgress AS (
                    SELECT 
                        DATE(played_at) as game_date,
                        COUNT(*) as games_played,
                        SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                        AVG(accuracy) as daily_accuracy
                    FROM game_history
                    WHERE player_id = ?
                    GROUP BY DATE(played_at)
                    ORDER BY game_date
                )
                SELECT 
                    game_date,
                    games_played, 
                    wins,
                    daily_accuracy,
                    SUM(games_played) OVER (ORDER BY game_date) as total_games,
                    SUM(wins) OVER (ORDER BY game_date) as total_wins
                FROM GameProgress
            ''', (player_id,))
            
            progress_data = []
            
            for row in cursor.fetchall():
                progress_data.append({
                    'date': row[0],             ## Date
                    'games_played': row[1],     ## Games played
                    'wins': row[2],             ## Win count
                    'accuracy': row[3],         ## Hit accuracy
                    'total_games': row[4],      ## Total games
                    'total_wins': row[5]        ## Total wins
                })
            
            return {
                'daily_progress': progress_data,  ## Daily progress infromation
                'improvement_rate': self._calculate_improvement_rate(progress_data)  ## Improvement rate
            }
        
        ## Error handling
        except Exception as e:
            print(f"Error: player progress {e}")
            return {}

    def _calculate_improvement_rate(self, progress_data: List[Dict]) -> float:

        ## The player must play at least two games to calculate improvement
        if len(progress_data) < 2:
            return 0.0
        
        try:
            ## Take the first 10 games
            early_games = progress_data[:10]
            
            ## Win count in the first 10 games
            early_total_wins = 0
            early_total_games = 0
            for game in early_games:
                early_total_wins = early_total_wins + game['wins']
                early_total_games = early_total_games + game['games_played']
            
            ## Calculate win rate in the first 10 games
            early_win_rate = early_total_wins / early_total_games
            
            ## Take the recent 10 games
            recent_games = progress_data[-10:]
            
            ## Win count in the recent 10 games
            recent_total_wins = 0
            recent_total_games = 0
            for game in recent_games:
                recent_total_wins = recent_total_wins + game['wins']
                recent_total_games = recent_total_games + game['games_played']
            
            ## Calculate win rate in the recent 10 games
            recent_win_rate = recent_total_wins / recent_total_games
            
            ## Calculate improvement percentage
            improvement = ((recent_win_rate - early_win_rate) / early_win_rate) * 100
            
            ## Round result if necessary
            return round(improvement, 2)
        
        ## Handles division by zero
        except ZeroDivisionError:
            return 0.0
