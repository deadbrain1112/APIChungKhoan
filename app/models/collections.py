from bson import ObjectId

def to_dict(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc
