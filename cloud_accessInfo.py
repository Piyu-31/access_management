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

def setCloudData():
  cloud_info = {}
  email = request.form['eid']
  first_name = request.form['fname']
  last_name = request.form['lname']
  user_type = request.form['utype']
  user_contact =  request.form['phone']
  currentDT = datetime.datetime.now(pytz.timezone('US/Central'))
  date_time = currentDT.strftime("%Y %b %d %a %I:%M:%S%p")

  #set data to the Empty list
  cloud_info["org_id"] = "002"
  cloud_info["org_name"] = "Cloud User"
  cloud_info["email"] = email.strip()
  cloud_info["first_name"] = first_name.strip()
  cloud_info["last_name"] = last_name.strip()
  cloud_info["user_type"] = user_type.strip()
  cloud_info["user_contact"] = user_contact.strip()
  if not session['edit_record']:
    Password_Un = generate_password(4,2)
    cloud_info["password"] = Password_Un.strip()
  cloud_info["created_date"] = date_time.strip()

  return cloud_info