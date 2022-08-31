from pymongo import MongoClient
import datetime
import sys
import certifi

from bson.objectid import ObjectId

from configparser import ConfigParser
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

global con_feedback
global db_feedback
global col_feedback

def connect_contractor_feedback_db():
  global con_feedback
  global db_feedback
  global col_feedback
  con_feedback = MongoClient('mongodb+srv://'+config['database']['USERNAME']+':'
  									+config['database']['PASSWORD']+'@'
  									+config['database']['HOST']+'/'
  									+config['Auth_asc']['DB_NAME']+
  									'?retryWrites=true&w=majority', tlsCAFile = ca)
  db_feedback = con_feedback.Contractors_Db
  col_feedback = db_feedback.feedback_info

def get_feedback_details_from_contractor_db():
  global col_feedback
  connect_contractor_feedback_db()
  feedback_data = col_feedback.find({},{"_id":0})
  return feedback_data

def get_feedbacks_from_con_db_by_acc_no(acc_no):
  global col_feedback
  connect_contractor_feedback_db()
  feedback_data = col_feedback.find({"account": str(acc_no)},{"_id":0})
  return feedback_data

def update_con_feeds_by_acc_no(acc_no,review_info):
	global col_feedback
	connect_contractor_feedback_db()
	col_feedback.update_one({"account": str(acc_no)}, {'$set' :{'account':review_info["account"],
                                                    			'feedback_type':review_info["feedback_type"],
                                                    			'feedback_source':review_info["feedback_source"],
                                                    			'order_id':review_info["order_id"],
                                                    			'feedback_description':review_info["feedback_description"],
                                                    			'ratings':review_info["ratings"]
                                                    } })
	return

def delete_feeds_by_acc_no(acc_no):
	global col_feedback
	connect_contractor_feedback_db()
	col_feedback.remove({"account": str(acc_no)})
	return "Deleted Successfully"