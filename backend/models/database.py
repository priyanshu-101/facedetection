from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Connect to MongoDB database"""
        try:
            mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            database_name = os.getenv('DATABASE_NAME', 'facedetection')
            
            self._client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            self._db = self._client[database_name]
            
            # Test the connection
            self._client.admin.command('ping')
            print(f"Successfully connected to MongoDB database: {database_name}")
            
        except Exception as e:
            print(f"Warning: MongoDB connection failed: {e}")
            print("The app will run but database operations will fail.")
            print("Please install and start MongoDB to use the full functionality.")
            # Don't raise the exception, let the app start anyway
            self._client = None
            self._db = None
    
    def get_database(self):
        """Get the database instance"""
        if self._db is None:
            self.connect()
        return self._db
    
    def get_collection(self, collection_name):
        """Get a specific collection"""
        db = self.get_database()
        return db[collection_name]
    
    def close_connection(self):
        """Close the database connection"""
        if self._client:
            self._client.close()
            print("MongoDB connection closed")

# Create a global database instance
db_instance = Database()
