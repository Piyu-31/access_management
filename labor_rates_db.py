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
                    +config['labor_rates']['DB_NAME']+'?retryWrites=true&w=majority', tlsCAFile = ca)
  db = con.Labor_rates_db
  col = db.labor_rates_info

def get_con_labor_rates_details():
  global col
  connect_db()
  ratesdata_from_db = col.find({"Status" : True})
  return ratesdata_from_db

def get_con_labor_rates_details_by_id(id_name):
  global col
  connect_db()
  ratesdata_from_db = col.find({"contractor_labor_id_name" : str(id_name)})
  return ratesdata_from_db


def get_con_labor_rates_details_paginated(pageNum, recordsPerPage):
  global col
  connect_db()
  page_no = pageNum
  rec_per_page = recordsPerPage
  count_rates = col.count()
  total_pages = (count_rates + rec_per_page - 1)//rec_per_page
  ratesdata_from_db = col.find({}).skip(page_no*rec_per_page).limit(rec_per_page)
  return [ratesdata_from_db,rec_per_page,count_rates,total_pages]


def save_con_labor_rates_details(ratesInfo):
  global col
  connect_db()
  col.insert(ratesInfo)
  return "saved Successfully"

def get_con_labor_rates_detail_by_id(rates_id):
  global col
  connect_db()
  ratesdata_from_db = col.find({"_id": ObjectId(rates_id)})
  return ratesdata_from_db

def update_con_labor_rates_record(rates_id,ratesInfo ):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(rates_id)}, {'$set' :{'contractor_labor_id_name':ratesInfo["contractor_labor_id_name"],
                                                        'contractor_labor_group_name':ratesInfo["contractor_labor_group_name"],
                                                        'contractor_labor_UI_label':ratesInfo["contractor_labor_UI_label"],
                                                        'contractor_labor_default_value':ratesInfo["contractor_labor_default_value"]
                                                         } })
  return

def delete_con_labor_rates_by_id(rates_id):
  global col
  connect_db()
  col.remove({"_id": ObjectId(rates_id)})
  return "Deleted Successfully"

def update_con_labor_status_field(rates_id,status_key):
  global col
  connect_db()
  col.update_one({"_id": ObjectId(rates_id)}, {'$set' :{'Status' : status_key} })
  return
