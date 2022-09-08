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
  con = MongoClient('mongodb+srv://'+config['database']['USERNAME']+':'+config['database']['PASSWORD']+'@'+config['database']['HOST']+'/'+config['Auth_cloud']['DB_NAME']+'?retryWrites=true&w=majority', tlsCAFile = ca)
  db = con.Authorization
  col = db.nexus_cloud

def get_cloud_details():
  global col
  connect_db()
  cloud_data = col.find({})
  return cloud_data

def get_cloud_details_paginated(pageNum, recordsPerPage):
  global col
  connect_db()
  page_no = pageNum
  rec_per_page = recordsPerPage
  count_cloudUser = col.count()
  total_pages = (count_cloudUser + rec_per_page - 1)//rec_per_page
  cloud_recs = col.find({}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [cloud_recs,rec_per_page,count_cloudUser,total_pages]

def get_count_cloud_users():
  global col
  connect_db()
  count_cloudUser = col.count()
  return count_cloudUser


def save_cloud_details(cloudInfo):
  global col
  connect_db()
  col.insert(cloudInfo)
  return "saved Successfully"

def get_cloud_user_detail(oid):
  global col
  connect_db()
  cloud_data = col.find({"_id": ObjectId(oid)})
  return cloud_data

def update_cloud_user_record(oid, cloud_Info):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(oid)}, {'$set' :{'org_id':cloud_Info["org_id"],
                                                   'email':cloud_Info["email"],
                                                   'first_name':cloud_Info["first_name"],
                                                   'last_name':cloud_Info["last_name"], 
                                                   'user_type':cloud_Info["user_type"],
                                                   'user_contact':cloud_Info["user_contact"]
                                                         } })
  return

def delete_a_cloudUser(oid):
  global col
  connect_db()
  col.remove({"_id": ObjectId(oid)})
  return "Deleted Successfully"

def update_one_password(oid, cldInfo):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(oid)}, {'$set' :{'password':cldInfo["password"],
                                                    'created_date':cldInfo["created_date"]
                                                    } })
  return

def get_one_cloud_details(userID):
  global col
  connect_db()
  cloud_records = col.find({ "user_id": str(userID) })
  return cloud_records

