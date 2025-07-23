"""
MongoDB database configuration and setup for Mergington High School API
"""

from pymongo import MongoClient
from argon2 import PasswordHasher
import logging

# In-memory fallback storage for development
_in_memory_activities = {}
_in_memory_teachers = {}
_use_memory_fallback = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to connect to MongoDB, fall back to in-memory storage
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    # Test connection
    client.admin.command('ping')
    db = client['mergington_high']
    activities_collection = db['activities']
    teachers_collection = db['teachers']
    logger.info("Connected to MongoDB successfully")
except Exception as e:
    logger.warning(f"MongoDB connection failed: {e}. Using in-memory storage for development.")
    _use_memory_fallback = True
    
    # Create mock collection classes for in-memory storage
    class MockCollection:
        def __init__(self, name):
            self.name = name
            self.data = _in_memory_activities if name == 'activities' else _in_memory_teachers
        
        def count_documents(self, filter_dict):
            return len(self.data)
        
        def insert_one(self, doc):
            doc_id = doc.get('_id', len(self.data))
            self.data[doc_id] = doc
            return type('InsertResult', (), {'inserted_id': doc_id})()
        
        def find(self, filter_dict=None):
            if filter_dict is None:
                # Return all documents with _id field included
                return [{'_id': doc_id, **doc} for doc_id, doc in self.data.items()]
            
            results = []
            for doc_id, doc in self.data.items():
                match = True
                doc_with_id = {'_id': doc_id, **doc}
                for key, value in filter_dict.items():
                    if key == "schedule_details.days":
                        # Handle nested array search like MongoDB's $in operator
                        if "$in" in value:
                            doc_days = doc.get("schedule_details", {}).get("days", [])
                            if not any(day in doc_days for day in value["$in"]):
                                match = False
                                break
                    elif key == "schedule_details.start_time":
                        # Handle time comparison
                        if "$gte" in value:
                            doc_time = doc.get("schedule_details", {}).get("start_time", "")
                            if doc_time < value["$gte"]:
                                match = False
                                break
                    elif key == "schedule_details.end_time":
                        # Handle time comparison
                        if "$lte" in value:
                            doc_time = doc.get("schedule_details", {}).get("end_time", "")
                            if doc_time > value["$lte"]:
                                match = False
                                break
                    elif doc_with_id.get(key) != value:
                        match = False
                        break
                if match:
                    results.append(doc_with_id)
            return results
        
        def find_one(self, filter_dict):
            for doc_id, doc in self.data.items():
                doc_with_id = {'_id': doc_id, **doc}
                if all(doc_with_id.get(k) == v for k, v in filter_dict.items()):
                    return doc_with_id
            return None
        
        def update_one(self, filter_dict, update_dict):
            for doc_id, doc in self.data.items():
                if all(doc.get(k) == v for k, v in filter_dict.items()):
                    if '$push' in update_dict:
                        for field, value in update_dict['$push'].items():
                            if field not in doc:
                                doc[field] = []
                            doc[field].append(value)
                    if '$pull' in update_dict:
                        for field, value in update_dict['$pull'].items():
                            if field in doc and isinstance(doc[field], list):
                                while value in doc[field]:
                                    doc[field].remove(value)
                    return type('UpdateResult', (), {'modified_count': 1})()
            return type('UpdateResult', (), {'modified_count': 0})()
        
        def aggregate(self, pipeline):
            # Simple aggregation implementation for the days endpoint
            if not pipeline:
                return []
            
            results = []
            # For the specific pipeline used in get_available_days
            if len(pipeline) >= 2 and "$unwind" in pipeline[0] and "$group" in pipeline[1]:
                all_days = set()
                for doc in self.data.values():
                    days = doc.get("schedule_details", {}).get("days", [])
                    all_days.update(days)
                
                # Return in sorted order
                for day in sorted(all_days):
                    results.append({"_id": day})
            
            return results
    
    activities_collection = MockCollection('activities')
    teachers_collection = MockCollection('teachers')

# Methods
def hash_password(password):
    """Hash password using Argon2"""
    ph = PasswordHasher()
    return ph.hash(password)

def init_database():
    """Initialize database if empty"""

    # Initialize activities if empty
    if activities_collection.count_documents({}) == 0:
        for name, details in initial_activities.items():
            activities_collection.insert_one({"_id": name, **details})
            
    # Initialize teacher accounts if empty
    if teachers_collection.count_documents({}) == 0:
        for teacher in initial_teachers:
            teachers_collection.insert_one({"_id": teacher["username"], **teacher})

# Initial database if empty
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
        "schedule_details": {
            "days": ["Monday", "Friday"],
            "start_time": "15:15",
            "end_time": "16:45"
        },
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "07:00",
            "end_time": "08:00"
        },
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Morning Fitness": {
        "description": "Early morning physical training and exercises",
        "schedule": "Mondays, Wednesdays, Fridays, 6:30 AM - 7:45 AM",
        "schedule_details": {
            "days": ["Monday", "Wednesday", "Friday"],
            "start_time": "06:30",
            "end_time": "07:45"
        },
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball tournaments",
        "schedule": "Wednesdays and Fridays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Wednesday", "Friday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore various art techniques and create masterpieces",
        "schedule": "Thursdays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Thursday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Monday", "Wednesday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and prepare for math competitions",
        "schedule": "Tuesdays, 7:15 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "07:15",
            "end_time": "08:00"
        },
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Friday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"]
    },
    "Weekend Robotics Workshop": {
        "description": "Build and program robots in our state-of-the-art workshop",
        "schedule": "Saturdays, 10:00 AM - 2:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "10:00",
            "end_time": "14:00"
        },
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "oliver@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Weekend science competition preparation for regional and state events",
        "schedule": "Saturdays, 1:00 PM - 4:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "13:00",
            "end_time": "16:00"
        },
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Sunday Chess Tournament": {
        "description": "Weekly tournament for serious chess players with rankings",
        "schedule": "Sundays, 2:00 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Sunday"],
            "start_time": "14:00",
            "end_time": "17:00"
        },
        "max_participants": 16,
        "participants": ["william@mergington.edu", "jacob@mergington.edu"]
    },
    "Manga Maniacs": {
        "description": "Explore the fantastic stories of the most interesting characters from Japanese Manga (graphic novels).",
        "schedule": "Tuesdays, 7:00 PM - 8:00 PM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "19:00",
            "end_time": "20:00"
        },
        "max_participants": 15,
        "participants": []
    }
}

initial_teachers = [
    {
        "username": "mrodriguez",
        "display_name": "Ms. Rodriguez",
        "password": hash_password("art123"),
        "role": "teacher"
     },
    {
        "username": "mchen",
        "display_name": "Mr. Chen",
        "password": hash_password("chess456"),
        "role": "teacher"
    },
    {
        "username": "principal",
        "display_name": "Principal Martinez",
        "password": hash_password("admin789"),
        "role": "admin"
    }
]

