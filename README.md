# Pinecrest-Resort-Booking-System
This web application allows users to register, log in, and manage their room bookings at the Pinecrest Resort. It provides an easy-to-use interface for booking rooms, checking room availability, and updating or canceling reservations. Additionally, it includes an admin dashboard for managing room information and viewing bookings.

## **Features**
**User Authentication:** Users can sign up, log in, and maintain their sessions with secure cookies.

**Room Booking:** Users can book rooms, specifying check-in and check-out dates, room type, and special requests.

**Booking Management:** Users can view, update, and cancel their bookings.

**Room Availability Check:** Ensures that rooms are available for the specified dates before allowing bookings.

**Responsive Design:** Built using Jinja2 templates for rendering HTML, ensuring a smooth user experience.

**Admin Dashboard:** Admins can add new rooms, delete rooms, view all bookings, and update room information.

## **Technologies Used**
**Backend:** FastAPI

**Database:** MongoDB with Motor (asynchronous driver)

**Templating:** Jinja2

**Authentication:** URLSafeTimedSerializer for secure session management

**Frontend:** HTML, CSS, JavaScript

### **Set Up the Environment:**
Create a virtual environment and install the required packages:
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

### **Set Up MongoDB:**
Make sure you have a MongoDB instance running and update the MongoDB connection string in the code:
client = AsyncIOMotorClient("mongodb+srv://<username>:<password>@<cluster-url>/PinecrestResort")

### **Run the Application:**
uvicorn main:app --reload

### **Access the Application:**
Open your browser and go to http://127.0.0.1:8000.

## **Project Structure**
**main.py:** The main entry point for the FastAPI application.

**models.py:** Contains Pydantic models for the data schema.

**routes.py:** Defines all the API routes and their handlers.

**admin_routes.py:** Defines API routes and handlers for admin functionalities.

**templates/:** Directory containing Jinja2 templates for HTML pages.

**static/:** Directory for static files like CSS and JavaScript.

**Admin Dashboard:**

**Add Rooms:** Admins can add new room details including name, description, total rooms, tagline, and images.

**Delete Rooms:** Admins can delete existing rooms.

**View Bookings:** Admins can view all user bookings.

**Update Rooms:** Admins can update room information as needed.

### **Contact**
If you have any questions or suggestions, feel free to open an issue or contact at umymashahzad@gmail.com.
