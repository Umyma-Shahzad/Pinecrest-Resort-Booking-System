from datetime import date
import hashlib
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from itsdangerous import URLSafeTimedSerializer
from dependencies import get_current_user
import random

router = APIRouter()

# Initialize MongoDB client
client = AsyncIOMotorClient("mongodb+srv://samiMirza:database1@database.jhvu6og.mongodb.net/PinecrestResort")
db = client.pinecrest

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "Ahng^7*(><iog"
serializer = URLSafeTimedSerializer(SECRET_KEY)

def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Pydantic Models
class Room(BaseModel):

    id: int
    name: str
    description: str
    total_rooms: int
    tagline: str
    image_url: str
    image_url1: str
    image_url2: str

@router.get("/admin_login")
async def adminlogin(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

# Logging in
@router.post("/admin")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    admin = await db.admin.find_one({"username": username})

    if not admin or admin["password"] != get_password_hash(password):
        return templates.TemplateResponse("admin_login.html", {"request": request, "error": "Invalid username or password"})

    response = RedirectResponse(url="/dashboard", status_code=302)

    session_data = {"admin_id": str(admin["_id"])}
    session_cookie = serializer.dumps(session_data)
    response.set_cookie("session", session_cookie)

    return response

# Render add room page
@router.get("/addroom")
async def adminlogin(request: Request):
    return templates.TemplateResponse("addroom.html", {"request": request})

# Add room using Fetch API
@router.post("/addroom", response_class=RedirectResponse)
async def addroom(request: Request, name: str = Form(...), description: str = Form(...), total_rooms: int = Form(...),
                         tagline: str = Form(...), image_url: str = Form(...), image_url1: str = Form(...), image_url2: str = Form(...)):

    room = await db.rooms.find_one({"name": name})
    if room:
         return RedirectResponse(url="/dashboard", status_code=302)

    new_room = Room(
        id = random.randint(10**9, 10**10),
        name=name,
        description=description,
        total_rooms=total_rooms,
        tagline=tagline,
        image_url=image_url,
        image_url1=image_url1,
        image_url2=image_url2
    )
    await db.rooms.insert_one(new_room.dict())
    return RedirectResponse(url="/dashboard", status_code=302)
   

# Display all user bookings
@router.get("/displayAllBookings", response_class=HTMLResponse)
async def bookings(request: Request):
    bookings_cursor = db.bookings.find()
    bookings = await bookings_cursor.to_list(length=None)
    return templates.TemplateResponse("displayAllBookings.html", {"request": request, "bookings": bookings})

# Update room using Fetch API
@router.post("/update-room/{room_id}", response_class=RedirectResponse)
async def update_room(request: Request, room_id: int, name: str = Form(...), description: str = Form(...), total_rooms: int = Form(...),
                         tagline: str = Form(...), image_url: str = Form(...), image_url1: str = Form(...), image_url2: str = Form(...)):

    room = await db.rooms.find_one({"id": room_id})
    if not room:
        return RedirectResponse(url="/dashboard", status_code=302)

    updated_room = {
        "name": name,
        "description": description,
        "total_rooms": total_rooms,
        "tagline": tagline,
        "image_url": image_url,
        "image_url1": image_url1,
        "image_url2": image_url2
    }

    await db.rooms.update_one({"id": room_id}, {"$set": updated_room})
    return RedirectResponse(url="/dashboard", status_code=302)

# Delete room using Fetch API
@router.post("/delete-room/{room_id}", response_class=JSONResponse)
async def delete_room(request: Request, room_id: int):
    room = await db.rooms.find_one({"id": room_id})
    if not room:
        return {"error": "Room not found"}

    await db.rooms.delete_one({"id": room_id})
    return {"message": "Room deleted successfully"}
    
