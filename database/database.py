import motor.motor_asyncio
from config import DB_URI, DB_NAME


class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        
    def new_user(self, id):
        return dict(_id = id)
               
    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'_id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
            
    async def get_all_users(self):
        return self.col.find({})
    
    async def delete_user(self, user_id):
        await self.col.delete_many({'_id': int(user_id)})

    
db = Database(DB_URI, DB_NAME)



