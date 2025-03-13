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
