from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin

UPLOAD_FOLDER = './app/uploads/'

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = "db24c608640f5034b30b8e1e1eb5618ed0ffdbf5"
app.config["MONGO_URI"] = "mongodb://localhost:27017/todo_db"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# mongodb database
mongodb_client = PyMongo(app)
db = mongodb_client.db

user_simulation_database = db.usersimulation
simulation_database = db.simulation
user_database = db.user

from .routes.authorization import *
from .routes.admin import *
from .routes.student import *
