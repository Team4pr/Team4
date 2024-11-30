import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_manager import DatabaseManager, DatabaseError


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        try:
            self.test_db_path = 'test_battleship.db'
            if os.path.exists(self.test_db_path):
                os.remove(self.test_db_path)
            self.db_manager = DatabaseManager(self.test_db_path)
        except Exception as e:
            self.fail(f"Failed to setup test database: {str(e)}")

    def tearDown(self):
        try:
            if hasattr(self, 'db_manager'):
                self.db_manager.close()
            if os.path.exists(self.test_db_path):
                os.remove(self.test_db_path)
        except Exception as e:
            print(f"Warning: Error during cleanup: {str(e)}")

    def test_create_tables(self):
        try:
            self.db_manager.create_tables()
            tables = self.db_manager.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [table[0] for table in tables]

            expected_tables = ['players', 'game_history', 'ship_statistics', 'player_settings']
            for table in expected_tables:
                self.assertIn(table, table_names)
        except Exception as e:
            self.fail(f"Failed to create tables: {str(e)}")

    def test_create_and_get_player(self):
        player_name = "TestPlayer"
        player_id = self.db_manager.create_player(player_name)
        self.assertIsNotNone(player_id)

        player = self.db_manager.get_player(player_id)
        self.assertIsNotNone(player)
        self.assertEqual(player['name'], player_name)
        self.assertEqual(player['games_played'], 0)

    def test_duplicate_player_name(self):
        player_name = "TestPlayer"
        self.db_manager.create_player(player_name)

        with self.assertRaises(DatabaseError):
            self.db_manager.create_player(player_name)

    def test_save_game_result(self):
        player_id = self.db_manager.create_player("TestPlayer")

        result = {
            'outcome': 'win',
            'moves': 30,
            'hits': 15,
            'misses': 15,
            'duration': 300,
            'grid_size': 10
        }

        try:
            self.db_manager.save_game_result(player_id, result)

            player = self.db_manager.get_player(player_id)
            self.assertEqual(player['games_played'], 1)
            self.assertEqual(player['games_won'], 1)
            self.assertEqual(player['total_shots'], 30)
            self.assertEqual(player['total_hits'], 15)
        except Exception as e:
            self.fail(f"Failed to save game score: {str(e)}")

    def test_get_player_statistics(self):
        player_id = self.db_manager.create_player("TestPlayer")

        results = [
            {'outcome': 'win', 'moves': 20, 'hits': 10, 'misses': 10, 'duration': 200},
            {'outcome': 'loss', 'moves': 25, 'hits': 12, 'misses': 13, 'duration': 250}
        ]

        for result in results:
            self.db_manager.save_game_result(player_id, result)

        stats = self.db_manager.get_player_statistics(player_id)
        self.assertEqual(stats['total_games'], 2)
        self.assertEqual(stats['wins'], 1)

    def test_find_player_by_name(self):
        player_name = "TestPlayer"
        original_id = self.db_manager.create_player(player_name)

        found_player = self.db_manager.find_player_by_name(player_name)
        self.assertIsNotNone(found_player)
        self.assertEqual(found_player['id'], original_id)

        not_found = self.db_manager.find_player_by_name("NonExistentPlayer")
        self.assertIsNone(not_found)

    def test_get_leaderboard(self):
        players = [
            ("Player1", [{'outcome': 'win'}, {'outcome': 'win'}]),
            ("Player2", [{'outcome': 'win'}, {'outcome': 'loss'}]),
            ("Player3", [{'outcome': 'loss'}, {'outcome': 'loss'}])
        ]

        for name, results in players:
            player_id = self.db_manager.create_player(name)
            for result in results:
                result.update({'moves': 20, 'hits': 10, 'misses': 10, 'duration': 200})
                self.db_manager.save_game_result(player_id, result)

        leaderboard = self.db_manager.get_leaderboard()
        self.assertEqual(len(leaderboard), 3)
        self.assertEqual(leaderboard[0]['name'], "Player1")  

    def test_delete_player_data(self):
        player_id = self.db_manager.create_player("TestPlayer")

        result = {
            'outcome': 'win',
            'moves': 20,
            'hits': 10,
            'misses': 10,
            'duration': 200
        }
        self.db_manager.save_game_result(player_id, result)

        self.db_manager.delete_player_data(player_id)

        player = self.db_manager.get_player(player_id)
        self.assertIsNone(player)

    def test_connection_management(self):
        self.assertTrue(self.db_manager.check_connection())

        self.db_manager.close()
        self.assertFalse(self.db_manager.check_connection())

        self.db_manager.reconnect()
        self.assertTrue(self.db_manager.check_connection())

    def test_backup_database(self):
        backup_path = 'backup_test.db'

        try:
            self.db_manager.create_player("TestPlayer")

            self.db_manager.backup_database(backup_path)

            self.assertTrue(os.path.exists(backup_path))
        finally:
            if os.path.exists(backup_path):
                os.remove(backup_path)


if __name__ == '__main__':
    unittest.main()
