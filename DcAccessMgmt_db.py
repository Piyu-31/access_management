from pymongo import MongoClient
import datetime
import sys
import certifi

from bson.objectid import ObjectId

from pymongo.collection import ReturnDocument

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
  ca = certifi.where()
  con = MongoClient('mongodb+srv://'+config['database']['USERNAME']+':'+config['database']['PASSWORD']+'@'+config['database']['HOST']+'/'+config['Auth_dc']['DB_NAME']+'?retryWrites=true&w=majority',tlsCAFile = ca)
  db = con.Authorization
  col = db.door_center

def get_dc_details():
  global col
  connect_db()
  dcbasicinfo_from_db = col.find({})
  return dcbasicinfo_from_db

def get_dc_details_paginated(pageNum, recordsPerPage):
  global col
  connect_db()
  page_no = pageNum
  rec_per_page = recordsPerPage
  count_dcUser = col.count()
  total_pages = (count_dcUser + rec_per_page - 1)//rec_per_page
  dcbasicinfo_from_db = col.find({}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [dcbasicinfo_from_db,rec_per_page,count_dcUser,total_pages]

def save_dc_details(dcInfo):
  global col
  connect_db()
  col.insert(dcInfo)
  return "saved Successfully"

def get_one_dc_detail(oid):
  global col
  connect_db()
  dcbdata_from_db = col.find({"_id": ObjectId(oid)})
  return dcbdata_from_db


def update_one_dc_record(oid, dcInfo):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(oid)}, {'$set' :{'org_id':dcInfo["org_id"],
                                                   'email':dcInfo["email"],
                                                   'first_name':dcInfo["first_name"],
                                                   'last_name':dcInfo["last_name"],  
                                                   'user_type':dcInfo["user_type"],
                                                   'user_contact':dcInfo["user_contact"]
                                                         } })
  return

def search_by_id(search_term, pagenum, records_pages):
  global col
  connect_db()
  page_no = pagenum
  rec_per_page = records_pages
  count_dcUser = col.count({'org_id':str(search_term)})
  total_pages = (count_dcUser + rec_per_page - 1)//rec_per_page
  searched_data = col.find({'org_id':str(search_term)},{"_id":0}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [searched_data, rec_per_page, count_dcUser, total_pages]

def search_by_name(search_term, pagenum, records_pages):
  global col
  connect_db()
  page_no = pagenum
  rec_per_page = records_pages
  count_dcUser = col.count({'org_name':str(search_term)})
  total_pages = (count_dcUser + rec_per_page - 1)//rec_per_page
  searched_data = col.find({'org_name':str(search_term)},{"_id":0}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [searched_data, rec_per_page, count_dcUser, total_pages]

def delete_a_DcUser(oid):
  global col
  connect_db()
  col.remove({"_id": ObjectId(oid)})
  return "Deleted Successfully"

def update_one_password(oid, dcInfo):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(oid)}, {'$set' :{'password':dcInfo["password"],
                                                     'created_date':dcInfo["created_date"]
                                                     } })
  return

def get_one_dc_details(userID):
  global col
  connect_db()
  dcbasicinfo_from_db = col.find({ "user_id": str(userID) })
  return dcbasicinfo_from_db

global con_dc_info
global db_dc_info
global col_dc_info

def connectdcInfo_db():
  global con_dc_info
  global db_dc_info
  global col_dc_info
  con_dc_info = MongoClient('mongodb+srv://'+config['database']['USERNAME']+':'+config['database']['PASSWORD']+'@'+config['database']['HOST']+'/'+config['DoorcenterDB']['DB_NAME']+'?retryWrites=true&w=majority')
  db_dc_info = con_dc_info.Door_center_db
  col_dc_info = db_dc_info.dc_basic_info

def get_dc_details_from_dc_db(orgid):
  global col_dc_info
  connectdcInfo_db()
  dcInfo_from_db = col_dc_info.find({"dc_number" : str(orgid)},{"_id":0})
  return dcInfo_from_db