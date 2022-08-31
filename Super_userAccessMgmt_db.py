from pymongo import MongoClient
import datetime
import sys
import certifi

from bson.objectid import ObjectId

global con
global db
global col

def connect_db():
  global con
  global db
  global col
  con = MongoClient('mongodb+srv://Sourav:l9EG8ULwylphgjHS@nexusfieldservice.axvp7.mongodb.net/Authorization?retryWrites=true&w=majority', tlsCAFile = ca)
  db = con.Authorization
  col = db.super_users


def save_user_details(userInfo):
  global col
  connect_db()
  col.insert(userInfo)
  return "saved Successfully"

# login section
def search_authorization_by_id(id):
   global col
   connect_db()
   searched_data = col.find({'user_id':str(id)})
   return searched_data

def check_password(email):
  global col
  connect_db()
  searched_data = col.find({'user_id':str(email)})
  return searched_data 

def update_one_password(email, check):
  global col
  connect_db()
  col.update_one({"user_id": str(email)}, {'$set' :{'password':check['password']} })
  return

