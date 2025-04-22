import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GameStatsManager:
    def __init__(self, db_file='gamestats.db'):
        self.db_file = db_file
        self.initialize_database()

    def get_connection(self):
        """Create and return a database connection."""
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def initialize_database(self):
        """Initialize the database and create necessary tables if they don't exist."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create the stats table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_name TEXT NOT NULL,
                    date_played TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    comments TEXT
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()

    def add_stat(self, game_name, date_played, score, comments=""):
        """Add a new game stat record to the database."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO stats (game_name, date_played, score, comments)
                VALUES (?, ?, ?, ?)
            ''', (game_name, date_played, score, comments))
            
            conn.commit()
            logger.info(f"Added new stat for game: {game_name}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding stat: {e}")
            raise
        finally:
            conn.close()

    def get_stats(self):
        """Retrieve all stats from the database."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM stats ORDER BY date_played DESC')
            stats = cursor.fetchall()
            
            return stats
        except sqlite3.Error as e:
            logger.error(f"Error retrieving stats: {e}")
            raise
        finally:
            conn.close()

    def update_stat(self, stat_id, game_name, date_played, score, comments=""):
        """Update an existing stat record."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE stats 
                SET game_name = ?, date_played = ?, score = ?, comments = ?
                WHERE id = ?
            ''', (game_name, date_played, score, comments, stat_id))
            
            conn.commit()
            logger.info(f"Updated stat with ID: {stat_id}")
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error updating stat: {e}")
            raise
        finally:
            conn.close()

    def delete_stat(self, stat_id):
        """Delete a stat record from the database."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM stats WHERE id = ?', (stat_id,))
            
            conn.commit()
            logger.info(f"Deleted stat with ID: {stat_id}")
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting stat: {e}")
            raise
        finally:
            conn.close()

    def get_stats_for_chart(self):
        """Retrieve stats formatted for chart display."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT game_name, date_played, score 
                FROM stats 
                ORDER BY date_played ASC
            ''')
            
            stats = cursor.fetchall()
            return {
                'games': [stat[0] for stat in stats],
                'dates': [stat[1] for stat in stats],
                'scores': [stat[2] for stat in stats]
            }
        except sqlite3.Error as e:
            logger.error(f"Error retrieving stats for chart: {e}")
            raise
        finally:
            conn.close()
