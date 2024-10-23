import mysql.connector
import configparser

# Create a config parser
config = configparser.ConfigParser()

# Read the credentials from the INI file
config.read('db_credentials.ini')

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def mysql_connect(self):
        """Initialize the database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=config['mysql']['host'],
                user=config['mysql']['user'],
                password=config['mysql']['password'],
                database=config['mysql']['database']
            )
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as e:
            print(f"Error connecting to database: {e}")
            return False
        return True

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()