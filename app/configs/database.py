from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb+srv://congtiengod_db_user:ahihi1234@chungkhoan.hk5fj6c.mongodb.net/?retryWrites=true&w=majority&appName=Chungkhoan"
client = AsyncIOMotorClient(MONGO_URL)
database = client["chungkhoan_pro"]

nhadautu_collection = database["ndt"]
