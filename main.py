from fastapi import FastAPI, HTTPException, status, Depends
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.templating import Jinja2Templates
from routes.users_router import router as users_router
from routes.admin_router import router as admin_router
import bson
from bson import ObjectId


app = FastAPI()

# Initialize MongoDB client
client = AsyncIOMotorClient("mongodb+srv://samiMirza:database1@database.jhvu6og.mongodb.net/")
db = client.pinecrest

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

app.include_router(users_router)
app.include_router(admin_router)

# Render home page
@app.get("/")
async def index_page(request: Request):
    room_cursor = db.rooms.find()
    rooms = await room_cursor.to_list(length=None)
    return templates.TemplateResponse("index.html", {"request": request, "rooms": rooms})

# Render Admin dashboard page
@app.get("/dashboard")
async def dashboard(request: Request):
    room_cursor = db.rooms.find()
    rooms = await room_cursor.to_list(length=None)
    return templates.TemplateResponse("dashboard.html", {"request": request, "rooms": rooms})

# Render home page
@app.get("/home")
async def home_page(request: Request):
    room_cursor = db.rooms.find()
    rooms = await room_cursor.to_list(length=None)
    return templates.TemplateResponse("index.html", {"request": request, "rooms": rooms})
# Render room details
@app.get("/rooms/{room_id}")
async def room_details(request: Request, room_id: str):
    room = await db.rooms.find_one({"_id": ObjectId(room_id)})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return templates.TemplateResponse("room_details.html", {"request": request, "room": room})

# After clicking logout page redirect to homepage
@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
