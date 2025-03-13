from pymongo import MongoClient

client = MongoClient("mongodb+srv://itsintrovert07:sanemibot@cluster0.zd1nrbm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["sahil"]

def get_force_sub_channel(index):
    doc = db.config.find_one({"_id": "force_sub_channels"})
    if doc:
        return doc.get(f"channel_{index}", None)
    return None

def set_force_sub_channel(index, new_channel_id):
    db.config.update_one(
        {"_id": "force_sub_channels"},
        {"$set": {f"channel_{index}": new_channel_id}},
        upsert=True
    )

async def refresh_db_handler():
    global client, db
    client = MongoClient("mongodb+srv://itsintrovert07:sanemibot@cluster0.zd1nrbm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["sahil"]

def get_auto_delete_time():
    doc = db.config.find_one({"_id": "auto_delete_time"})
    if doc:
        return doc.get("time", None)
    return None

def set_auto_delete_time(new_time):
    db.config.update_one(
        {"_id": "auto_delete_time"},
        {"$set": {"time": new_time}},
        upsert=True
    )

def add_admin(user_id: int):
    db.config.update_one(
        {"_id": "admins"},
        {"$addToSet": {"admin_ids": user_id}},
        upsert=True
    )

def remove_admin(user_id: int):
    db.config.update_one(
        {"_id": "admins"},
        {"$pull": {"admin_ids": user_id}}
    )

def get_admins():
    doc = db.config.find_one({"_id": "admins"})
    if doc:
        return doc.get("admin_ids", [])
    return []

from pymongo import MongoClient

# MongoDB setup
MONGO_URI = "mongodb+srv://itsintrovert07:sanemibot@cluster0.zd1nrbm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your MongoDB URI
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["telegram_bot"]
channel_collection = db["search_channels"]

def get_search_channels():
    """Fetch searchable channels from MongoDB."""
    return {doc["chat_id"]: doc["username"] for doc in channel_collection.find()}

def add_search_channel(chat_id, username):
    """Add or update a channel in MongoDB."""
    channel_collection.update_one({"chat_id": chat_id}, {"$set": {"username": username}}, upsert=True)

def clear_search_channels():
    """Clear all stored search channels in MongoDB."""
    channel_collection.delete_many({})
