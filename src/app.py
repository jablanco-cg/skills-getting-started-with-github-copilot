"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from pymongo import MongoClient
from typing import Dict, Any

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# MongoDB connection
mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client['school_activities']
activities_collection = db['activities']

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initial activities data for MongoDB
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    # Sports related activities
    "Soccer Team": {
        "description": "Join the school soccer team and compete in local leagues",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball skills and play friendly matches",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    # Artistic activities
    "Art Club": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
    },
    "Drama Society": {
        "description": "Participate in acting, stage production, and school plays",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ethan@mergington.edu", "charlotte@mergington.edu"]
    },
    # Intellectual activities
    "Mathletes": {
        "description": "Compete in math competitions and solve challenging problems",
        "schedule": "Fridays, 2:30 PM - 3:30 PM",
        "max_participants": 10,
        "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["elijah@mergington.edu", "harper@mergington.edu"]
    }
}


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database with activities if it's empty"""
    print("Checking database...")
    try:
        if activities_collection.count_documents({}) == 0:
            print("Database is empty. Populating with initial data...")
            for name, details in activities.items():
                activities_collection.insert_one({"name": name, **details})
            print(f"Successfully populated database with {len(activities)} activities")
        else:
            print(f"Database already contains {activities_collection.count_documents({})} activities")
    except Exception as e:
        print(f"Error during database initialization: {e}")
    yield

app.router.lifespan_context = lifespan

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/activities")
def get_activities():
    """Get all activities"""
    cursor = activities_collection.find({}, {'_id': 0})
    activities_list = list(cursor)
    return {activity.pop('name'): activity for activity in activities_list}

@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    activity = activities_collection.find_one({"name": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up")

    # Validate activity is not at maximum capacity
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is at maximum capacity")

    # Update the participants list
    activities_collection.update_one(
        {"name": activity_name},
        {"$push": {"participants": email}}
    )

    return {"message": f"Signed up {email} for {activity_name}"}
    return {"message": f"Signed up {email} for {activity_name}"}
