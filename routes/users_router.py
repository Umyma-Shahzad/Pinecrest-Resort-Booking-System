from datetime import date
import hashlib
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel,Field
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
class Booking(BaseModel):
    id: int
    fullname: str
    phone_number: str
    email: str
    checkin_date: str
    checkout_date: str
    room_type: str
    number_of_rooms: int
    special_request: Optional[str] = None

class User(BaseModel):
    username: str
    password: str
    email: str
    bookings: List[Booking] = []

# Dependency function to check room availability
async def check_availability(room_type: str, checkin_date: date, checkout_date: date, number_of_rooms: int):
    bookings = await db.bookings.find({
        "room_type": room_type,
        "$or": [
            {"checkin_date": {"$lt": checkout_date, "$gte": checkin_date}},
            {"checkout_date": {"$gt": checkin_date, "$lte": checkout_date}}
        ]
    }).to_list(length=None)

    total_rooms_booked = sum([booking["number_of_rooms"] for booking in bookings])
    available_rooms = 10 - total_rooms_booked

    if number_of_rooms > available_rooms:
        raise HTTPException(status_code=400, detail="Not enough rooms available")

# Render booknow page
@router.get("/booknow", response_class=HTMLResponse)
async def booknow(request: Request, user: dict = Depends(get_current_user)):
    user = await get_current_user(request)
    room_cursor = db.rooms.find()
    rooms = await room_cursor.to_list(length=None)
    if not user:
        return RedirectResponse('/login', status_code=302)
    return templates.TemplateResponse("booknow.html", {"request": request, "rooms": rooms})



# Render login page
@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Render signup page
@router.get("/signup")
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# Signing up
@router.post("/signup")
async def signup(request: Request, username: str = Form(...), password: str = Form(...)):
    user = await db.users.find_one({"username": username})

    if user:
        return RedirectResponse(url="/signup?error=1", status_code=302)

    await db.users.insert_one(
        {
            "username": username,
            "password": get_password_hash(password),
            "bookings":[]
        }
    )

    return RedirectResponse(url="/login", status_code=302)

# Logging in
@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = await db.users.find_one({"username": username})

    if not user or user["password"] != get_password_hash(password):
        return RedirectResponse(url="/login?error=1", status_code=302)

    response = RedirectResponse(url="/", status_code=302)

    session_data = {"user_id": str(user["_id"])}
    session_cookie = serializer.dumps(session_data)
    response.set_cookie("session", session_cookie)

    return response

# Add booking
@router.post("/booknow", response_class=RedirectResponse)
async def booknow_post(request: Request, fullname: str = Form(...), phone_number: str = Form(...), email: str = Form(...),
                       checkin_date: str = Form(...), checkout_date: str = Form(...), room_type: str = Form(...),
                       number_of_rooms: int = Form(...), special_request: Optional[str] = Form(None), 
                       user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse('/login', status_code=302)

    await check_availability(room_type, checkin_date, checkout_date, number_of_rooms)

    booking = Booking(
        id = random.randint(10**9, 10**10),
        fullname=fullname,
        phone_number=phone_number,
        email=email,
        checkin_date=checkin_date,
        checkout_date=checkout_date,
        room_type=room_type,
        number_of_rooms=number_of_rooms,
        special_request=special_request
    )
    await db.bookings.insert_one(booking.dict())

    user["bookings"].append(booking.dict())
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"bookings": user["bookings"]}})
    return RedirectResponse("/bookings", status_code=303)

# Show user bookings
@router.get("/bookings", response_class=HTMLResponse)
async def bookings(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse('/login', status_code=302)
    return templates.TemplateResponse("bookings.html", {"request": request, "bookings": user["bookings"]})

# Update booking
@router.post("/update-booking/{booking_id}", response_class=RedirectResponse)
async def update_booking(request: Request, booking_id: int, fullname: str = Form(...), phone_number: str = Form(...), email: str = Form(...),
                         checkin_date: str = Form(...), checkout_date: str = Form(...), room_type: str = Form(...),
                         number_of_rooms: int = Form(...), special_request: Optional[str] = Form(None), 
                         user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse('/login', status_code=302)

    booking = await db.bookings.find_one({"id":booking_id, "email": email})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    await check_availability(room_type, checkin_date, checkout_date, number_of_rooms)

    updated_booking = Booking(
        id=booking_id,
        fullname=fullname,
        phone_number=phone_number,
        email=email,
        checkin_date=checkin_date,
        checkout_date=checkout_date,
        room_type=room_type,
        number_of_rooms=number_of_rooms,
        special_request=special_request
    )

    await db.bookings.update_one({"id":booking_id}, {"$set": updated_booking.dict()})

    for b in user["bookings"]:
        if b["id"] == booking_id:
            user["bookings"].remove(b)
            user["bookings"].append(updated_booking.dict())
            break

    await db.users.update_one({"_id": user["_id"]}, {"$set": {"bookings": user["bookings"]}})

    return RedirectResponse("/bookings", status_code=303)

# Cancel booking
@router.post("/cancel-booking/{booking_id}", response_class=RedirectResponse)
async def cancel_booking(request: Request, booking_id: int, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse('/login', status_code=302)

    booking = await db.bookings.find_one({"id": booking_id})
    print(booking   )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    await db.bookings.delete_one({"id": booking_id})

    user["bookings"] = [b for b in user["bookings"] if b["id"] != booking_id]
    print(user["bookings"])
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"bookings": user["bookings"]}})

    return RedirectResponse("/bookings", status_code=303)
