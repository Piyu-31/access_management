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
  con = MongoClient('mongodb+srv://'+config['database']['USERNAME']+':'+config['database']['PASSWORD']+'@'+config['database']['HOST']+'/'+config['Auth_ret']['DB_NAME']+'?retryWrites=true&w=majority', tlsCAFile = ca)
  db = con.Authorization
  col = db.retailers

def get_ret_details():
  global col
  connect_db()
  retdata_from_db = col.find({})
  return retdata_from_db

def get_ret_details_paginated(pageNum, recordsPerPage):
  global col
  connect_db()
  page_no = pageNum
  rec_per_page = recordsPerPage
  count_retUser = col.count()
  total_pages = (count_retUser + rec_per_page - 1)//rec_per_page
  retdata_from_db = col.find({}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [retdata_from_db,rec_per_page,count_retUser,total_pages]

def save_ret_details(retInfo):
  global col
  connect_db()
  col.insert(retInfo)
  return "saved Successfully"

def get_ret_user_detail(oid):
  global col
  connect_db()
  retdata_from_db = col.find({"_id": ObjectId(oid)})
  return retdata_from_db

def update_ret_user_record(oid, retInfo):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(oid)}, {'$set' :{'org_id':retInfo["org_id"],
                                                     'email':retInfo["email"],
                                                     'first_name':retInfo["first_name"],
                                                     'last_name':retInfo["last_name"],  
                                                     'user_type':retInfo["user_type"],
                                                     'user_contact':retInfo["user_contact"]
                                                         } })
  return


def search_by_id(search_term, pagenum, records_pages):
  global col
  connect_db()
  page_no = pagenum
  rec_per_page = records_pages
  count_retUser = col.count({'org_id':str(search_term)})
  total_pages = (count_retUser + rec_per_page - 1)//rec_per_page
  searched_data = col.find({'org_id':str(search_term)},{"_id":0}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [searched_data, rec_per_page, count_retUser, total_pages]

def search_by_name(search_term, pagenum, records_pages):
  global col
  connect_db()
  page_no = pagenum
  rec_per_page = records_pages
  count_retUser = col.count({'org_name':str(search_term)})
  total_pages = (count_retUser + rec_per_page - 1)//rec_per_page
  searched_data = col.find({'org_name':str(search_term)},{"_id":0}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [searched_data, rec_per_page, count_retUser, total_pages]

def delete_a_retUser(oid):
  global col
  connect_db()
  col.remove({"_id": ObjectId(oid)})
  return "Deleted Successfully"


def update_one_password(oid, retInfo):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(oid)}, {'$set' :{'password':retInfo["password"],
                                                    'created_date':retInfo["created_date"]
                                                    } })
  return

def get_one_ret_details(userID):
  global col
  connect_db()
  retinfo_from_db = col.find({ "user_id": str(userID) })
  return retinfo_from_db

def connect_ret_info_db():
  global con_ret_info
  global db_ret_info
  global col_ret_info
  con_ret_info = MongoClient('mongodb+srv://'+config['database']['USERNAME']+':'+config['database']['PASSWORD']+'@'+config['database']['HOST']+'/'+config['RetailerDB']['DB_NAME']+'?retryWrites=true&w=majority')
  db_ret_info = con_ret_info.Retailer_db
  col_ret_info = db_ret_info.retailer_basic_info

def get_ret_details_from_ret_db(org_id):
  global col_ret_info
  connect_ret_info_db()
  retInfo_from_db = col_ret_info.find({"account" : str(org_id)},{"_id":0})
  return retInfo_from_db
