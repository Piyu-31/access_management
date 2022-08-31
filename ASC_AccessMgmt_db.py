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
  con = MongoClient('mongodb+srv://'+config['database']['USERNAME']+':'+config['database']['PASSWORD']+'@'+config['database']['HOST']+'/'+config['Auth_asc']['DB_NAME']+'?retryWrites=true&w=majority', tlsCAFile = ca)
  db = con.Authorization
  col = db.central_facility

def get_asc_details():
  global col
  connect_db()
  ascdata_from_db = col.find({})
  return ascdata_from_db

def get_asc_details_paginated(pageNum, recordsPerPage):
  global col
  connect_db()
  page_no = pageNum
  rec_per_page = recordsPerPage
  count_ascUser = col.count()
  total_pages = (count_ascUser + rec_per_page - 1)//rec_per_page
  ascdata_from_db = col.find({}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [ascdata_from_db,rec_per_page,count_ascUser,total_pages]


def save_asc_details(ascInfo):
  global col
  connect_db()
  col.insert(ascInfo)
  return "saved Successfully"

def get_asc_user_detail(oid):
  global col
  connect_db()
  ascdata_from_db = col.find({"_id": ObjectId(oid)})
  return ascdata_from_db

def update_asc_user_record(oid, ascInfo):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(oid)}, {'$set' :{'org_id':ascInfo["org_id"],
                                                   'email':ascInfo["email"],
                                                   'first_name':ascInfo["first_name"],
                                                   'last_name':ascInfo["last_name"], 
                                                   'user_type':ascInfo["user_type"],
                                                   'user_contact':ascInfo["user_contact"]
                                                         } })
  return

def search_by_contact_number(search_term, pagenum, records_pages):
  global col
  connect_db()
  page_no = pagenum
  rec_per_page = records_pages
  count_ascUser = col.count({'user_contact':str(search_term)})
  total_pages = (count_ascUser + rec_per_page - 1)//rec_per_page
  searched_data = col.find({'user_contact':str(search_term)},{"_id":0}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [searched_data, rec_per_page, count_ascUser, total_pages]

def search_by_first_name(search_term, pagenum, records_pages):
  global col
  connect_db()
  page_no = pagenum
  rec_per_page = records_pages
  count_ascUser = col.count({'first_name':str(search_term)})
  total_pages = (count_ascUser + rec_per_page - 1)//rec_per_page
  searched_data = col.find({'first_name':str(search_term)},{"_id":0}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [searched_data, rec_per_page, count_ascUser, total_pages]

def delete_a_ascUser(oid):
  global col
  connect_db()
  col.remove({"_id": ObjectId(oid)})
  return "Deleted Successfully"

def update_one_password(oid, ascInfo):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(oid)}, {'$set' :{'password':ascInfo["password"],
                                                    'created_date':ascInfo["created_date"]
                                                    } })
  return

def get_one_asc_details(userID):
  global col
  connect_db()
  ascdata_from_db = col.find({ "user_id": str(userID) })
  return ascdata_from_db

