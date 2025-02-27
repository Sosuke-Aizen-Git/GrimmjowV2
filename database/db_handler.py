from pymongo import MongoClient

client = MongoClient("mongodb+srv://nitus1673:itachi@cluster0.b9uq1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
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
    client = MongoClient("mongodb+srv://nitus1673:itachi@cluster0.b9uq1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["sahil"]
