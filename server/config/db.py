#----------------------------------------------------------------------------------------
#                                   Import Statements
#----------------------------------------------------------------------------------------

import os 
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

#----------------------------------------------------------------------------------------
#                                   Logic Statements
#----------------------------------------------------------------------------------------

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=10000
)

# Test connection (temporary)
try:
    client.admin.command("ping")
    print("MongoDB connected successfully")
except Exception as e:
    print("MongoDB connection failed:", e)

db = client[DB_NAME]
users_collection = db['users']