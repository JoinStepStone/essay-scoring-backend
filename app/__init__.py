from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin
from gridfs import GridFS
import os

UPLOAD_FOLDER = './app/uploads/'
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://excel-app-peach.vercel.app"}})
app.config["SECRET_KEY"] = "db24c608640f5034b30b8e1e1eb5618ed0ffdbf5"
app.config["MONGO_URI"] = (
    "mongodb://localhost:27017/todo_db" if False else os.environ.get('MONGODB_URI')
)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# del app.config["MONGO_URI"]
# del app.config["PERMANENT_SESSION_LIFETIME"]

# mongodb database
mongodb_client = PyMongo(app)
db = mongodb_client.db
gridFileStorage = GridFS(db)

user_simulation_database = db.usersimulation
simulation_database = db.simulation
user_database = db.user
name_storage_database = db.storage

from .routes.authorization import *
from .routes.admin import *
from .routes.student import *
