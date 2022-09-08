from flask import request,session
from passlib.hash import sha256_crypt
import random
import string
import datetime
import time
import pytz

def generate_password(letters_count, digits_count):
  sample_str = ''.join((random.choice(string.ascii_letters) for i in range(letters_count)))
  sample_str += ''.join((random.choice(string.digits) for i in range(digits_count)))
  sample_list = list(sample_str)
  final_string = ''.join(sample_list)
  return final_string

def sha_encryption(un_encrypted_password):
  encrypted_password = sha256_crypt.encrypt(un_encrypted_password)
  return encrypted_password

def setConData():
  conInfo = {}

  org_id = request.form['oid']
  email = request.form['eid']
  first_name = request.form['fname']
  last_name = request.form['lname']
  user_type = request.form['utype']
  user_sub_type = request.form['usubtype']
  user_sub_type_id = request.form['usubtid']
  user_contact =  request.form['phone']
  currentDT = datetime.datetime.now(pytz.timezone('US/Central'))
  date_time = currentDT.strftime("%Y %b %d %a %I:%M:%S%p")

  #set data to the Empty list
  conInfo["org_id"]=org_id.strip()
  conInfo["email"]=email.strip()
  conInfo["first_name"]=first_name.strip()
  conInfo["last_name"]=last_name.strip()
  conInfo["user_type"]=user_type.strip()
  conInfo["user_sub_type"]=user_sub_type.strip()
  conInfo["user_sub_type_id"]=user_sub_type_id.strip()
  conInfo["user_contact"]=user_contact.strip()
  if not session['edit_record']:
    Password_Un = generate_password(4,2)
    conInfo["password"]=Password_Un.strip()
  conInfo["created_date"] = date_time.strip()

  return conInfo
