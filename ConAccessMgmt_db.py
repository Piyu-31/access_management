from pymongo import MongoClient
import datetime
import sys

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
  con = MongoClient('mongodb+srv://'+config['database']['USERNAME']+':'
                                    +config['database']['PASSWORD']+'@'
                                    +config['database']['HOST']+'/'
                                    +config['Auth_con']['DB_NAME']
                                    +'?retryWrites=true&w=majority')
  db = con.Authorization
  col = db.contractor

def get_con_details():
  global col
  connect_db()
  condata_from_db = col.find({})
  return condata_from_db

def get_con_details_paginated(pageNum, recordsPerPage):
  global col
  connect_db()
  page_no = pageNum
  rec_per_page = recordsPerPage
  count_conUser = col.count()
  total_pages = (count_conUser + rec_per_page - 1)//rec_per_page
  condata_from_db = col.find({}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [condata_from_db,rec_per_page,count_conUser,total_pages]

def save_con_details(conInfo):
  global col
  connect_db()
  col.insert(conInfo)
  return "saved Successfully"


def get_con_user_detail(oid):
  global col
  connect_db()
  condata_from_db = col.find({"_id": ObjectId(oid)})
  return condata_from_db



def update_con_user_record(oid, conInfo):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(oid)}, {'$set' :{'org_id':conInfo["org_id"],
                                                   'email':conInfo["email"],
                                                   'first_name':conInfo["first_name"],
                                                   'last_name':conInfo["last_name"],  
                                                   'user_type':conInfo["user_type"],
                                                   'user_contact':conInfo["user_contact"],
                                                   'user_sub_type':conInfo["user_sub_type"],
                                                   'user_sub_type_id':conInfo["user_sub_type_id"],
                                                     } })
  return

def search_by_id(search_term, pagenum, records_pages):
  global col
  connect_db()
  page_no = pagenum
  rec_per_page = records_pages
  count_conUser = col.count({'org_id':str(search_term)})
  total_pages = (count_conUser + rec_per_page - 1)//rec_per_page
  searched_data = col.find({'org_id':str(search_term)},{'_id':0}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [searched_data, rec_per_page, count_conUser, total_pages]

def search_by_name(search_term, pagenum, records_pages):
  global col
  connect_db()
  page_no = pagenum
  rec_per_page = records_pages
  count_conUser = col.count({'org_name':str(search_term)})
  total_pages = (count_conUser + rec_per_page - 1)//rec_per_page
  searched_data = col.find({'org_name':str(search_term)},{'_id':0}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [searched_data, rec_per_page, count_conUser, total_pages]

def delete_a_conUser(oid):
  global col
  connect_db()
  col.remove({"_id": ObjectId(oid)})
  return "Deleted Successfully"


def update_one_password(oid, conInfo):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(oid)}, {'$set' :{'password':conInfo["password"],
                                                    'created_date':conInfo["created_date"]
                                                    } })
  return

def get_one_con_details(userID):
  global col
  connect_db()
  coninfo_from_db = col.find({ "user_id": str(userID) })
  return coninfo_from_db


def connect_con_info_db():
  global con_con_info
  global db_con_info
  global col_con_info
  global col_tech_info
  global col_keycontact


  col_kc = config['contractor']['COL_KEYCONTACT']
  con_con_info = MongoClient('mongodb+srv://Sourav:l9EG8ULwylphgjHS@nexusfieldservice.axvp7.mongodb.net/Contractors_Db?retryWrites=true&w=majority')
  db_con_info = con_con_info.Contractors_Db
  col_con_info = db_con_info.Contractors_Basic_Info
  col_tech_info = db_con_info.technician_info
  col_keycontact = db_con_info[col_kc]

def get_con_details_from_con_db(orgid):
  global col_con_info
  connect_con_info_db()
  conInfo_from_db = col_con_info.find({"account" : str(orgid)},{"_id":0})
  return conInfo_from_db

def get_tech_details_from_con_db():
  global col_tech_info
  connect_con_info_db()
  tech_info_from_db = col_tech_info.find({},{"_id":0})
  return tech_info_from_db


def get_keyContacts_from_con_db():
  global col_keycontact
  connect_con_info_db()
  key_cons_from_db = col_keycontact.find({},{"_id":0})
  return key_cons_from_db
