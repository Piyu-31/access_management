from pymongo import MongoClient
import datetime
import sys
import certifi

from bson.objectid import ObjectId

from configparser import ConfigParser
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

global con
global db
global col

def connect_db():
  global con
  global db
  global col
  con = MongoClient('mongodb+srv://'+config['database']['USERNAME']+':'+
                    config['database']['PASSWORD']+'@'+config['database']['HOST']+'/'
                    +config['Auth_status']['DB_NAME']+'?retryWrites=true&w=majority', tlsCAFile = ca)
  db = con.Authorization
  col = db.diy_status

def get_status_codes():
  global col
  connect_db()
  status_data = col.find({})
  return status_data

def save_status_code(status_info):
  global col
  connect_db()
  col.insert(status_info)
  return "saved Successfully"

def get_status_by_status_code(scode):
  global col
  connect_db()
  status_from_db = col.find({"status_code": str(scode)})
  return status_from_db

def get_status_by_object_id(obj_id):
  global col
  connect_db()
  status_data_from_db = col.find({"_id": ObjectId(obj_id)})
  return status_data_from_db

def update_a_status_code(obj_id, status_info):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(obj_id)}, {'$set' :{'status_code':status_info["status_code"] } })
  return

def delete_a_status_code(obj_id):
  global col
  connect_db()
  col.remove({"_id": ObjectId(obj_id)})
  return "Deleted Successfully"

# ---------------------------------------------------------------------------------------------------------
# F&I Status
global con_fni
global db_fni
global col_fni

def connect_fni_db():
  global con_fni
  global db_fni
  global col_fni
  con_fni = MongoClient('mongodb+srv://'+config['database']['USERNAME']+':'+
                    config['database']['PASSWORD']+'@'+config['database']['HOST']+'/'
                    +config['Auth_status']['DB_NAME']+'?retryWrites=true&w=majority')
  db_fni = con_fni.Authorization
  col_fni = db_fni.furnish_n_install

def get_fni_status_codes():
  global col_fni
  connect_fni_db()
  status_fni_data = col_fni.find({})
  return status_fni_data

def save_fni_status_code(status_info):
  global col_fni
  connect_fni_db()
  col_fni.insert(status_info)
  return "saved Successfully"

def get_status_by_status_code(scode):
  global col_fni
  connect_fni_db()
  status_fni_from_db = col_fni.find({"status_code": str(scode)})
  return status_fni_from_db

def get_fni_status_by_object_id(obj_id):
  global col_fni
  connect_fni_db()
  fni_status_data_from_db = col_fni.find({"_id": ObjectId(obj_id)})
  return fni_status_data_from_db

def update_a_fni_status_code(obj_id, status_info):
  global col_fni
  connect_fni_db()
  col_fni.update_one({"_id": ObjectId(obj_id)}, {'$set' :{'status_code':status_info["status_code"] } })
  return

def delete_fni_status_code(obj_id):
  global col_fni
  connect_fni_db()
  col_fni.remove({"_id": ObjectId(obj_id)})
  return "Deleted Successfully"