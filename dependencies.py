from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient
from itsdangerous import URLSafeTimedSerializer
from bson import ObjectId

SECRET_KEY = "Ahng^7*(><iog"
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Initialize MongoDB client
client = AsyncIOMotorClient("mongodb+srv://samiMirza:database1@database.jhvu6og.mongodb.net/PinecrestResort")
db = client.pinecrest

async def get_current_user(request: Request):
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        return None
    try:
        session_data = serializer.loads(session_cookie)
        user = await db.users.find_one({"_id": ObjectId(session_data.get("user_id"))})
        if not user:
            return None
        return user
    except:
        return None
