
from collections import UserList
import enum
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from . import db



#Creating model table for our CRUD database

# User model
class User(db.Model,UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50),index=True,unique=True)
    email = db.Column(db.String(150),index=True,unique=True)
    phone = db.Column(db.String(20),index=True ,unique=True)
    password_hash = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(),default=datetime.utcnow,index=True)
    
    # class constructor to pass properties
    def __init__(self, username, email, phone):
        self.username = username
        self.email = email
        self.phone = phone

    
    # define a function set_password() which takes the password provided by the user and generates a hashed version
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    # check_password uses the same concept to check if the password provided by the user during registration matches the one in the database.
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

# Enums tracker values
class Tracker_values(enum.Enum):
    Numerical = 1
    Multiple_choices = 2
 
 
# Enums tracker types   
class Tracker_type(enum.Enum):
    Temperature = 1
    SPO2 = 2
    Running = 3
    Mood = 4
 
# Tracker model
class Tracker(db.Model):
    __tablename__ = "tracker"
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.Integer, db.ForeignKey('user.id')) 
    name = db.Column(db.String(200))
    description = db.Column(db.String(800))
    tracker_type = db.Column(db.Enum(Tracker_type))
    tracker_values = db.Column(db.Enum(Tracker_values))
    options = db.Column(db.String(500))
    tracker_logs = db.relationship('Tracker_logs',back_populates='tracker')
    date_created = db.Column(db.DateTime(),default=datetime.utcnow,index=True)
    
    # class constructor to pass properties
    def __init__(self, user, name,description,tracker_type,tracker_values,options):
        self.user = user
        self.name = name
        self.description = description
        self.tracker_type = tracker_type
        self.tracker_values = tracker_values
        self.options = options





# model Tracker logs   
class Tracker_logs(db.Model):
    __tablename__ = "tracker_logs"
    id = db.Column(db.Integer, primary_key = True)
    tracker_id = db.Column(db.Integer, db.ForeignKey('tracker.id'))  
    notes = db.Column(db.String(800))
    value = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime(),default=datetime.utcnow,index=True)
    tracker = db.relationship("Tracker", back_populates="tracker_logs")
    

    def __init__(self, tracker_id, notes, value):
        self.tracker_id = tracker_id
        self.notes = notes
        self.value = value
        


