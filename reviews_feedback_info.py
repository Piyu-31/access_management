from flask import request
from passlib.hash import sha256_crypt
import random
import string
import datetime
import time

def setreviewcData():
  reviewInfo = {}
  
  ratings = request.form['ratngs']
  reviewInfo["ratings"] = ratings.strip()
  
  account = request.form['accN']
  reviewInfo["account"]=account.strip()

  feedback_type = request.form['feedbacktype']
  reviewInfo["feedback_type"] = feedback_type.strip()

  feedback_source = request.form['feedbacksource']
  reviewInfo["feedback_source"] = feedback_source.strip()

  order_id = request.form['orderid']
  reviewInfo["order_id"] = order_id.strip()

  feedback_description = request.form['feedbackdesc']
  reviewInfo["feedback_description"] = feedback_description.strip()

  return reviewInfo