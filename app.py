from flask import Flask,render_template,redirect,request,session,flash,url_for,g
import datetime
import sys
import random
import time
import pytz

import json

import DcAccessMgmt_db
import ConAccessMgmt_db
import ASC_AccessMgmt_db
import Ret_AccessMgmt_db
import sensitive_Info_db
import Super_userAccessMgmt_db
import Cloud_AccessMgmt_db
import status_code_db


import sendSms
from passlib.hash import sha256_crypt
from functools import wraps

import dc_accessInfo
import contractor_accessInfo
import ASC_accessInfo
import retailer_accessInfo
import cloud_accessInfo

import reviews_feedbackMgmt_db
import reviews_feedback_info

import retail_labor_rates_db
import retail_labor_ratesInfo

import labor_rates_db
import labor_ratesInfo

from configparser import ConfigParser
import configparser

config = configparser.ConfigParser()
config.read('config.ini')


app = Flask(__name__)
app.config.update(SESSION_COOKIE_NAME = 'session_access')

app.secret_key=config['SecretKey']['SECRET_KEY']
# -------------------------------------------------------------------------------------------------
# Login required
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'username_access' in session:
      return f(*args, **kwargs)
    else:
      return redirect(url_for('login'))
  return wrap

@app.route("/")
@login_required
def index():
  dc_cursor = DcAccessMgmt_db.get_dc_details_paginated(0, 30)
  dc_count = int(dc_cursor[2])
  con_cursor = ConAccessMgmt_db.get_con_details_paginated(0, 30)
  con_count = int(con_cursor[2])
  cent_cursor = ASC_AccessMgmt_db.get_asc_details_paginated(0, 30)
  cent_count = int(cent_cursor[2])
  ret_cursor = Ret_AccessMgmt_db.get_ret_details_paginated(0, 30)
  ret_count = int(ret_cursor[2])
  session['count_cloudUser'] = Cloud_AccessMgmt_db.get_count_cloud_users()
  return render_template('home.html', user = session['username_access'],
                                      count_dcuser = dc_count, 
                                      count_conuser = con_count,
                                      count_ascuser = cent_count,
                                      count_retuser = ret_count,
                                      count_user = session['count_cloudUser']
                                      )

def generate_password(letters_count, digits_count):
  sample_str = ''.join((random.choice(string.ascii_letters) for i in range(letters_count)))
  sample_str += ''.join((random.choice(string.digits) for i in range(digits_count)))
  sample_list = list(sample_str)
  final_string = ''.join(sample_list)
  return final_string

def sha_encryption(un_encrypted_password):
  encrypted_password = sha256_crypt.encrypt(un_encrypted_password)
  return encrypted_password
# Forget Password for Superusers

@app.route('/reset_password', methods=['POST'])
def reset_password():
  checkForMail = []
  check=[]
  incorrect_credentials_flag = False
  email = request.form['email']
  phone = request.form['phone']
  check_for_pw = Super_userAccessMgmt_db.check_password(email)
  for c in check_for_pw:
    checkForMail.append(c)
  if checkForMail :
    if checkForMail[0]['user_contact'] == phone:
      newPass = generate_password(4, 2)
      newPass_en = sha_encryption(newPass)
      for check in checkForMail:
        check['password'] = newPass_en
        Super_userAccessMgmt_db.update_one_password(email, check)
        send_sms_user(newPass, phone)
        flash('Successfully reset the password')
    else:
      incorrect_credentials_flag = True
      flash('incorrect user credentials')
  else:
    incorrect_credentials_flag = True
    flash('incorrect user credentials')
  return redirect(url_for('login'))

@app.route('/send_userSMS', methods=['POST'])
@login_required
def send_sms_user(password,phone):
  sendSms.send_msg(password,phone)
  return redirect(url_for('index'))
# -------------------------------------------------------------------------------------------------------------
# Door Center Section
@app.route("/DC")
@login_required
def dcWrapper():
  dc_info = []
  dcInfo_list = []
  dc_list = []
  search_page_code = ''
  search_page_term = ''

  
  if session['search_activated_dc']:
    dcInfo_list = session['dc_records']
    search_page_code = session['searched_dc_page_no']
    search_page_term = session['searched_dc_page_term']
  else:
    dc_cursor = DcAccessMgmt_db.get_dc_details_paginated(int(session['defaultPage']),int(session['rPerPage']))
    
    session['recordsPerPage'] = int(dc_cursor[1])
    session['count_dcUser'] = int(dc_cursor[2])
    session['totalPages'] = int(dc_cursor[3])
    search_page_code = '0'
    search_page_term = 'all'

    for u in dc_cursor[0]:
      dcInfo_list.append(u)
  
  session['search_activated_dc'] = False
  return render_template('DCform.html', 
                          dclist = dcInfo_list,
                          user = session['username_access'], 
                          totalPages = session['totalPages'], 
                          records_pages = session['recordsPerPage'], 
                          count_user = session['count_dcUser'],
                          search_code = search_page_code,
                          search_term = search_page_term )

@app.route("/DC_page/<pagenum>/<records_pages>/<search_code>/<search_term>", methods = ['POST'])
@login_required
def dcWrapper_paginated(pagenum,records_pages,search_code,search_term):
  dc_info = []
  dcInfo_list = []
  dc_list = []
  search_page_code = ''
  search_page_term = ''
  
  if search_code == '0':
    dc_cursor = DcAccessMgmt_db.get_dc_details_paginated(int(pagenum),int(records_pages))
    dc_info = session['dc_records']
    session['searched_dc_page_no'] = '0'
    session['searched_dc_page_term'] = 'all'
    session['search_activated_dc'] = False

  elif search_code == '1':
    dc_cursor = DcAccessMgmt_db.search_by_id(search_term,int(pagenum),int(records_pages))
    session['dc_records'] = dc_cursor
    session['searched_dc_page_no'] = '1'
    session['searched_dc_page_term'] = search_term
    session['search_activated_dc'] = True

  elif search_code == '2':
    dc_cursor = DcAccessMgmt_db.search_by_name(search_term,int(pagenum),int(records_pages))
    session['dc_records'] = dc_cursor
    session['searched_dc_page_no'] = '2'
    session['searched_dc_page_term'] = search_term
    session['search_activated_dc'] = True

  session['recordsPerPage'] = int(dc_cursor[1])
  session['count_dcUser'] = int(dc_cursor[2])
  session['totalPages'] = int(dc_cursor[3])
  search_page_code = session['searched_dc_page_no']
  search_page_term = session['searched_dc_page_term']

  for u in dc_cursor[0]:
    dcInfo_list.append(u)
  
  session['search_activated_dc'] = False
  return render_template('DCform.html', dclist = dcInfo_list, 
                                        user = session['username_access'], 
                                        totalPages = session['totalPages'], 
                                        records_pages = session['recordsPerPage'], 
                                        count_user = session['count_dcUser'],
                                        search_code = search_page_code,
                                        search_term = search_page_term )

@app.route('/search_dc_records/<search_code>', methods=['POST'])
@login_required
def search_dc_Records(search_code):
  dcInfo_list = []

  if int(search_code) == 1:
    session['dc_num'] = request.form['searchbynumber'].strip()
    dc_docs = DcAccessMgmt_db.search_by_id(session['dc_num'], int(session['defaultPage']), int(session['rPerPage']))
    session['searched_dc_page_no'] = '1'
    session['searched_dc_page_term'] = session['dc_num']

  if int(search_code) == 2:
    session['dc_name'] = request.form['searchbyname'].strip()
    dc_docs = DcAccessMgmt_db.search_by_name(session['dc_name'],int(session['defaultPage']),int(session['rPerPage']))
    session['searched_dc_page_no'] = '2'
    session['searched_dc_page_term'] = session['dc_name']

  for o in dc_docs[0]:
    dcInfo_list.append(o)
  session['dc_records'] = dcInfo_list
  
  session['recordsPerPage'] = int(dc_docs[1])
  session['count_dcUser'] = int(dc_docs[2])
  session['totalPages'] = int(dc_docs[3])
  
  session['search_activated_dc'] = True
  return redirect(url_for('dcWrapper'))

@app.route("/saveDC", methods=['POST'])
@login_required
def save_dc_records():
  session['edit_record'] = False
  dc_list = []
  org_id  = request.form['oid']
  email = request.form['eid']
  user_id = org_id + '_' + email
  dc_emList = []
  dc_data = DcAccessMgmt_db.get_one_dc_details(user_id)

  for d in dc_data:
    dc_emList.append(d)

  if dc_emList:
    flash('User exists... try with new one')
  else:
    dcInfo = dc_accessInfo.setDCData()
    password_Un = dcInfo["password"]
    password_Encrypt = dc_accessInfo.sha_encryption(password_Un)
    dc_info = DcAccessMgmt_db.get_dc_details_from_dc_db(org_id)
    for d in dc_info:
      dc_list.append(d)
    if dc_list:
      org_name = dc_list[0]['dc_name']

      dcInfo["password"] = password_Encrypt.strip()
      dcInfo["user_id"] = user_id.strip()
      dcInfo["org_name"] = org_name.strip()
      DcAccessMgmt_db.save_dc_details(dcInfo)
      
      password = password_Un
      phone = dcInfo['user_contact']
      user_id = dcInfo['user_id']
      first_name = dcInfo['first_name']
      org_name = dcInfo['org_name']
      send_to_DC(password,phone,user_id,first_name,org_name)
    return redirect(url_for('dcWrapper'))

@app.route("/updateDC", methods=['POST'])
@login_required
def update_dc_records():
  session['edit_record'] = True
  dcInfo = dc_accessInfo.setDCData()
  session['edit_record'] = False
  oid = request.form['id']
  DcAccessMgmt_db.update_one_dc_record(oid, dcInfo)
  return redirect(url_for('dcWrapper'))

@app.route("/editDC/<oid>", methods=['POST'])
@login_required
def edit_dc_records(oid):
  session['edit_record'] = True
  dc_recs = []
  dc_Info = DcAccessMgmt_db.get_one_dc_detail(oid)
  for d in dc_Info:
    dc_recs.append(d)
  dc_num = dc_recs[0]['org_id']
  return render_template('Dcedit.html', org_id = dc_num, dclist = dc_recs, user = session['username_access'])

@app.route('/send_DcSMS', methods=['POST'])
@login_required
def send_to_DC(password,phone,user_id,first_name,org_name):
  sendSms.send_msg(password,phone,user_id,first_name,org_name)
  return redirect(url_for('dcWrapper'))

@app.route("/deleteDCUser/<oid>", methods=['POST'])
@login_required
def delete_DcUser_by_ID(oid):
  DcAccessMgmt_db.delete_a_DcUser(oid)
  return redirect(url_for('dcWrapper'))

#Reset for DC
@app.route("/resetDC/<oid>",methods = ['POST'])
@login_required
def reset_DC(oid):
  dc_emList = []
  dc_data = DcAccessMgmt_db.get_one_dc_detail(oid)
  for d in dc_data:
    dc_emList.append(d)
  new_password = dc_accessInfo.generate_password(4, 2)


  dcInfo = {}
  new_password_en = dc_accessInfo.sha_encryption(new_password)
  new_date =  datetime.datetime.now(pytz.timezone('US/Central'))
  date_time = new_date.strftime("%Y %b %d %a %I:%M:%S%p")

  dcInfo['password'] = new_password_en
  dcInfo['created_date'] = date_time

  DcAccessMgmt_db.update_one_password(oid, dcInfo)
  phone = dc_emList[0]['user_contact']
  user_id = dc_emList[0]['user_id'] 
  first_name = dc_emList[0]['first_name']
  org_name = dc_emList[0]['org_name']
  send_to_DC(new_password,phone,user_id,first_name,org_name)
  flash('Successfully reset the password')
  return redirect(url_for('dcWrapper'))

# -------------------------------------------------------------------------------------------------------------------------
#Contractor Section
@app.route("/Con")
@login_required
def conWrapper():
  con_info = []
  conInfo_list = []
  con_list = []
  search_page_code = ''
  search_page_term = ''

  
  if session['search_activated_con']:
    conInfo_list = session['con_records']
    search_page_code = session['searched_con_page_no']
    search_page_term = session['searched_con_page_term']
  else:
    con_cursor = ConAccessMgmt_db.get_con_details_paginated(int(session['defaultPage']),int(session['rPerPage']))
    
    session['recordsPerPage'] = int(con_cursor[1])
    session['count_conUser'] = int(con_cursor[2])
    session['totalPages'] = int(con_cursor[3])
    search_page_code = '0'
    search_page_term = 'all'

    for u in con_cursor[0]:
      conInfo_list.append(u)

  session['search_activated_con'] = False
  return render_template('Conform.html', 
                          conlist = conInfo_list,
                          user = session['username_access'], 
                          totalPages = session['totalPages'], 
                          records_pages = session['recordsPerPage'], 
                          count_user = session['count_conUser'],
                          search_code = search_page_code,
                          search_term = search_page_term )

@app.route("/Con_page/<pagenum>/<records_pages>/<search_code>/<search_term>", methods = ['POST'])
@login_required
def conWrapper_paginated(pagenum,records_pages,search_code,search_term):
  con_info = []
  conInfo_list = []
  con_list = []
  search_page_code = ''
  search_page_term = ''
  
  if search_code == '0':
    con_cursor = ConAccessMgmt_db.get_con_details_paginated(int(pagenum),int(records_pages))
    con_info = session['con_records']
    session['searched_con_page_no'] = '0'
    session['searched_con_page_term'] = 'all'
    session['search_activated_con'] = False

  elif search_code == '1':
    con_cursor = ConAccessMgmt_db.search_by_id(search_term,int(pagenum),int(records_pages))
    session['con_records'] = con_cursor
    session['searched_con_page_no'] = '1'
    session['searched_con_page_term'] = search_term
    session['search_activated_con'] = True

  elif search_code == '2':
    con_cursor = ConAccessMgmt_db.search_by_name(search_term,int(pagenum),int(records_pages))
    session['con_records'] = con_cursor
    session['searched_con_page_no'] = '2'
    session['searched_con_page_term'] = search_term
    session['search_activated_con'] = True

  session['recordsPerPage'] = int(con_cursor[1])
  session['count_conUser'] = int(con_cursor[2])
  session['totalPages'] = int(con_cursor[3])
  search_page_code = session['searched_con_page_no']
  search_page_term = session['searched_con_page_term']

  for u in con_cursor[0]:
    conInfo_list.append(u)  
  
  session['search_activated_con'] = False
  return render_template('Conform.html', conlist = conInfo_list,
                                        techlist = tech_list, 
                                        user = session['username_access'], 
                                        totalPages = session['totalPages'], 
                                        records_pages = session['recordsPerPage'], 
                                        count_user = session['count_conUser'],
                                        search_code = search_page_code,
                                        search_term = search_page_term )

@app.route('/search_con_records/<search_code>', methods=['POST'])
@login_required
def search_con_Records(search_code):
  conInfo_list = []

  if int(search_code) == 1:
    session['con_num'] = request.form['searchbynumber'].strip()
    con_docs = ConAccessMgmt_db.search_by_id(session['con_num'], int(session['defaultPage']), int(session['rPerPage']))
    session['searched_con_page_no'] = '1'
    session['searched_con_page_term'] = session['con_num']

  if int(search_code) == 2:
    session['con_name'] = request.form['searchbyname'].strip()
    con_docs = ConAccessMgmt_db.search_by_name(session['con_name'],int(session['defaultPage']),int(session['rPerPage']))
    session['searched_con_page_no'] = '2'
    session['searched_con_page_term'] = session['con_name']

  for o in con_docs[0]:
    conInfo_list.append(o)
  session['con_records'] = conInfo_list
  
  session['recordsPerPage'] = int(con_docs[1])
  session['count_conUser'] = int(con_docs[2])
  session['totalPages'] = int(con_docs[3])
  
  session['search_activated_con'] = True
  return redirect(url_for('conWrapper'))

@app.route("/saveCon", methods=['POST'])
@login_required
def save_con_records():
  session['edit_record'] = False
  con_list = []
  org_id  = request.form['oid']
  email = request.form['eid']
  sub_user_type = request.form['usubtype']
  if sub_user_type == 'Key Contact':
    user_id = 'K'+org_id + '_' + email
  else:
    user_id = 'T'+org_id + '_' + email
  con_emList = []
  con_data = ConAccessMgmt_db.get_one_con_details(user_id)
  for c in con_data:
    con_emList.append(c)
  if con_emList:
    flash('User exists... try with new one')
  else:
    
    ConInfo = contractor_accessInfo.setConData()
    password_Un = ConInfo["password"]
    password_Encrypt=contractor_accessInfo.sha_encryption(password_Un)
    con_info = ConAccessMgmt_db.get_con_details_from_con_db(org_id)
    for con in con_info:
      con_list.append(con)
    if con_list:
        org_name = con_list[0]['contractor_name']

        ConInfo["password"] = password_Encrypt.strip()
        ConInfo["user_id"] = user_id.strip()
        ConInfo["org_name"] = org_name.strip()
        ConAccessMgmt_db.save_con_details(ConInfo)

        password = password_Un
        phone = ConInfo['user_contact']
        user_id = ConInfo['user_id']
        first_name = ConInfo['first_name']
        org_name = ConInfo['org_name']
        send_to_con(password,phone,user_id,first_name,org_name)
    return redirect(url_for('conWrapper'))

@app.route("/updateCon", methods=['POST'])
@login_required
def update_con_records():
  session['edit_record'] = True
  Con_Info = contractor_accessInfo.setConData()
  session['edit_record'] = False
  oid  = request.form['id']
  ConAccessMgmt_db.update_con_user_record(oid, Con_Info)
  return redirect(url_for('conWrapper'))

@app.route("/editCon/<oid>", methods=['POST'])
@login_required
def edit_con_records(oid):
  session['edit_record'] = True
  con_recs = []
  con_info = ConAccessMgmt_db.get_con_user_detail(oid)
  for c in con_info:
    con_recs.append(c)
  con_num = con_recs[0]['org_id']
  return render_template('Conedit.html', org_id = con_num, 
                                        conlist = con_recs, 
                                        user = session['username_access'])

@app.route('/send_ConSMS', methods=['POST'])
@login_required
def send_to_con(password,phone,user_id,first_name,org_name):
  sendSms.send_msg(password,phone,user_id,first_name,org_name)
  return redirect(url_for('conWrapper'))

@app.route("/deleteConUser/<oid>", methods=['POST'])
@login_required
def delete_conUser_by_ID(oid):
  ConAccessMgmt_db.delete_a_conUser(oid)
  return redirect(url_for('conWrapper'))

#Reset for Contractor
@app.route("/resetcon/<oid>",methods = ['POST'])
@login_required
def reset_con(oid):
  con_emList = []
  con_data = ConAccessMgmt_db.get_con_user_detail(oid)
  for c in con_data:
    con_emList.append(c)
  new_password = contractor_accessInfo.generate_password(4, 2)
  new_password_en = contractor_accessInfo.sha_encryption(new_password)

  conInfo = {}
  new_date =  datetime.datetime.now(pytz.timezone('US/Central'))
  date_time = new_date.strftime("%Y %b %d %a %I:%M:%S%p")

  conInfo['password'] = new_password_en
  conInfo['created_date'] = date_time

  ConAccessMgmt_db.update_one_password(oid, conInfo)
  phone = con_emList[0]['user_contact']
  user_id = con_emList[0]['user_id']
  first_name = con_emList[0]['first_name']
  org_name = con_emList[0]['org_name']
  send_to_con(new_password,phone,user_id,first_name,org_name)
  flash('Successfully reset the password')
  return redirect(url_for('conWrapper'))
# ------------------------------------------------------------------------------------------------------------------------
# ASC Section
@app.route("/central")
@login_required
def centralWrapper():
  asc_info = []
  ascInfo_list = []
  asc_list = []
  org_Id = ''
  org_Name = ''
  search_page_code = ''
  search_page_term = ''

  
  if session['search_activated_asc']:
    ascInfo_list = session['asc_records']
    search_page_code = session['searched_asc_page_no']
    search_page_term = session['searched_asc_page_term']
  else:
    asc_cursor = ASC_AccessMgmt_db.get_asc_details_paginated(int(session['defaultPage']),int(session['rPerPage']))
    
    session['recordsPerPage'] = int(asc_cursor[1])
    session['count_ascUser'] = int(asc_cursor[2])
    session['totalPages'] = int(asc_cursor[3])
    search_page_code = '0'
    search_page_term = 'all'

    for u in asc_cursor[0]:
      ascInfo_list.append(u)

  
  asc_info = ASC_AccessMgmt_db.get_asc_details()
  for asc in asc_info:
    asc_list.append(asc)
  if asc_list:
    org_Id = config['org']['ORG_ID']
    org_Name = config['org']['ORG_NAME']
  else:
    org_Id = config['org']['ORG_ID']
    org_Name = config['org']['ORG_NAME']
    flash('No Central Facility user exists')
  
  session['search_activated_asc'] = False
  return render_template('ASCform.html', 
                          Asclist = ascInfo_list, 
                          asc_info_list = asc_list,
                          orgID = org_Id,
                          orgName = org_Name,
                          user = session['username_access'], 
                          totalPages = session['totalPages'], 
                          records_pages = session['recordsPerPage'], 
                          count_user = session['count_ascUser'],
                          search_code = search_page_code,
                          search_term = search_page_term )

@app.route("/cental_page/<pagenum>/<records_pages>/<search_code>/<search_term>", methods = ['POST'])
@login_required
def centralWrapper_paginated(pagenum,records_pages,search_code,search_term):
  asc_info = []
  ascInfo_list = []
  asc_list = []
  org_Id = ''
  org_Name = ''
  search_page_code = ''
  search_page_term = ''
  
  if search_code == '0':
    asc_cursor = ASC_AccessMgmt_db.get_asc_details_paginated(int(pagenum),int(records_pages))
    asc_info = session['asc_records']
    session['searched_asc_page_no'] = '0'
    session['searched_asc_page_term'] = 'all'
    session['search_activated_asc'] = False

  elif search_code == '1':
    asc_cursor = ASC_AccessMgmt_db.search_by_contact_number(search_term,int(pagenum),int(records_pages))
    session['asc_records'] = asc_cursor
    session['searched_asc_page_no'] = '1'
    session['searched_asc_page_term'] = search_term
    session['search_activated_asc'] = True

  elif search_code == '2':
    asc_cursor = ASC_AccessMgmt_db.search_by_first_name(search_term,int(pagenum),int(records_pages))
    session['asc_records'] = asc_cursor
    session['searched_asc_page_no'] = '2'
    session['searched_asc_page_term'] = search_term
    session['search_activated_asc'] = True

  session['recordsPerPage'] = int(asc_cursor[1])
  session['count_ascUser'] = int(asc_cursor[2])
  session['totalPages'] = int(asc_cursor[3])
  search_page_code = session['searched_asc_page_no']
  search_page_term = session['searched_asc_page_term']
  
  for u in asc_cursor[0]:
    ascInfo_list.append(u)

  
  asc_info = ASC_AccessMgmt_db.get_asc_details()
  for asc in asc_info:
    asc_list.append(asc)
  if asc_list: 
    org_Id = asc_list[0]['org_id']
    org_Name = asc_list[0]['org_name']
  else:
    flash('No Organisation Id Exist')
  
  session['search_activated_asc'] = False
  return render_template('ASCform.html', Asclist = ascInfo_list, 
                                        asc_info_list = asc_list,
                                        user = session['username_access'],
                                        orgID = org_Id,
                                        orgName = org_Name,
                                        totalPages = session['totalPages'], 
                                        records_pages = session['recordsPerPage'], 
                                        count_user = session['count_ascUser'],
                                        search_code = search_page_code,
                                        search_term = search_page_term )

@app.route('/search_centeral_records/<search_code>', methods=['POST'])
@login_required
def search_central_Records(search_code):
  ascInfo_list = []

  if int(search_code) == 1:
    session['asc_num'] = request.form['searchbynumber'].strip()
    asc_docs = ASC_AccessMgmt_db.search_by_contact_number(session['asc_num'], int(session['defaultPage']), int(session['rPerPage']))
    session['searched_asc_page_no'] = '1'
    session['searched_asc_page_term'] = session['asc_num']

  if int(search_code) == 2:
    session['asc_name'] = request.form['searchbyname'].strip()
    asc_docs = ASC_AccessMgmt_db.search_by_first_name(session['asc_name'],int(session['defaultPage']),int(session['rPerPage']))
    session['searched_asc_page_no'] = '2'
    session['searched_asc_page_term'] = session['asc_name']

  for o in asc_docs[0]:
    ascInfo_list.append(o)
  session['asc_records'] = ascInfo_list
  session['recordsPerPage'] = int(asc_docs[1])
  session['count_ascUser'] = int(asc_docs[2])
  session['totalPages'] = int(asc_docs[3])
  
  session['search_activated_asc'] = True
  return redirect(url_for('centralWrapper'))

@app.route("/savecentral", methods=['POST'])
@login_required
def save_center_records():
  session['edit_record'] = False
  orgid = request.form['oid']
  email = request.form['eid']
  user_id = orgid + '_' + email
  asc_emList = []
  asc_data = ASC_AccessMgmt_db.get_one_asc_details(user_id)
  for d in asc_data:
    asc_emList.append(d)
  if asc_emList:
    flash('User exists... try with new one')
  else:
    AscInfo = ASC_accessInfo.setAscData()
    password_Un = AscInfo["password"]
    password_Encrypt=ASC_accessInfo.sha_encryption(password_Un)
    AscInfo["password"] = password_Encrypt.strip()
    AscInfo["user_id"] = user_id.strip()
    ASC_AccessMgmt_db.save_asc_details(AscInfo)
    password = password_Un
    phone = AscInfo['user_contact']
    user_id = AscInfo['user_id']
    first_name = AscInfo['first_name']
    org_name = AscInfo['org_name']
    send_sms_center(password,phone,user_id,first_name,org_name)
  return redirect(url_for('centralWrapper'))

@app.route("/updatecenter", methods=['POST'])
@login_required
def update_center_records():
  session['edit_record'] = True
  Asc_Info = ASC_accessInfo.setAscData()
  session['edit_record'] = False
  oid = request.form['id']
  ASC_AccessMgmt_db.update_asc_user_record(oid, Asc_Info)
  return redirect(url_for('centralWrapper'))

@app.route("/editcent/<oid>", methods=['POST'])
@login_required
def edit_center_records(oid):
  session['edit_record'] = True
  asc_list=[]
  asc_recs = []
  asc_info = ASC_AccessMgmt_db.get_asc_user_detail(oid)
  for asc in asc_info:
    asc_recs.append(asc)
  asc_num = asc_recs[0]['org_id']
  return render_template('ASCedit.html',org_id = asc_num, Asclist = asc_recs, user = session['username_access'])

@app.route('/send_centerSMS', methods=['POST'])
@login_required
def send_sms_center(password,phone,user_id,first_name,org_name):
  sendSms.send_msg(password,phone,user_id,first_name,org_name)
  return redirect(url_for('centralWrapper'))

@app.route("/deleteCentUser/<oid>", methods=['POST'])
@login_required
def delete_centralUser_by_ID(oid):
  ASC_AccessMgmt_db.delete_a_ascUser(oid)
  return redirect(url_for('centralWrapper'))

#Reset for ASC
@app.route("/resetcent/<oid>",methods = ['POST'])
@login_required
def reset_central(oid):
  asc_emList = []
  asc_data = ASC_AccessMgmt_db.get_asc_user_detail(oid)
  for a in asc_data:
    asc_emList.append(a)
  new_password = ASC_accessInfo.generate_password(4, 2)
  new_password_en = ASC_accessInfo.sha_encryption(new_password)

  ascInfo = {}
  new_date =  datetime.datetime.now(pytz.timezone('US/Central'))
  date_time = new_date.strftime("%Y %b %d %a %I:%M:%S%p")

  ascInfo['password'] = new_password_en
  ascInfo['created_date'] = date_time

  ASC_AccessMgmt_db.update_one_password(oid, ascInfo)
  phone = asc_emList[0]['user_contact']
  user_id = asc_emList[0]['user_id']
  first_name = asc_emList[0]['first_name']
  org_name = asc_emList[0]['org_name']
  send_sms_center(new_password,phone,user_id,first_name,org_name)
  flash('Successfully reset the password')
  return redirect(url_for('centralWrapper'))

# ------------------------------------------------------------------------------------------------------------------------
# Retailers Section
@app.route("/Ret")
@login_required
def RetailersWrapper():
  ret_info = []
  retInfo_list = []
  ret_list = []
  search_page_code = ''
  search_page_term = ''

  
  if session['search_activated_ret'] :
    retInfo_list = session['ret_records']
    search_page_code = session['searched_ret_page_no']
    search_page_term = session['searched_ret_page_term']
  else:
    ret_cursor = Ret_AccessMgmt_db.get_ret_details_paginated(int(session['defaultPage']),int(session['rPerPage']))
    
    session['recordsPerPage'] = int(ret_cursor[1])
    session['count_retUser'] = int(ret_cursor[2])
    session['totalPages'] = int(ret_cursor[3])
    search_page_code = '0'
    search_page_term = 'all'

    for u in ret_cursor[0]:
      retInfo_list.append(u)
  session['search_activated_ret']  = False
  return render_template('Retform.html', 
                          Retlist = retInfo_list, 
                          user = session['username_access'], 
                          totalPages = session['totalPages'], 
                          records_pages = session['recordsPerPage'], 
                          count_user = session['count_retUser'],
                          search_code = search_page_code,
                          search_term = search_page_term )

@app.route("/Ret_page/<pagenum>/<records_pages>/<search_code>/<search_term>", methods = ['POST'])
@login_required
def RetailersWrapper_paginated(pagenum,records_pages,search_code,search_term):
  ret_info = []
  retInfo_list = []
  ret_list = []
  search_page_code = ''
  search_page_term = ''
  
  if search_code == '0':
    ret_cursor = Ret_AccessMgmt_db.get_ret_details_paginated(int(pagenum),int(records_pages))
    ret_info = session['ret_records']
    session['searched_ret_page_no'] = '0'
    session['searched_ret_page_term'] = 'all'
    session['search_activated_ret']  = False

  elif search_code == '1':
    ret_cursor = Ret_AccessMgmt_db.search_by_id(search_term,int(pagenum),int(records_pages))
    session['ret_records'] = ret_cursor
    session['searched_ret_page_no'] = '1'
    session['searched_ret_page_term'] = search_term
    session['search_activated_ret']  = True

  elif search_code == '2':
    ret_cursor = Ret_AccessMgmt_db.search_by_name(search_term,int(pagenum),int(records_pages))
    session['ret_records'] = ret_cursor
    session['searched_ret_page_no'] = '2'
    session['searched_ret_page_term'] = search_term
    session['search_activated_ret']  = True

  session['recordsPerPage'] = int(ret_cursor[1])
  session['count_retUser'] = int(ret_cursor[2])
  session['totalPages'] = int(ret_cursor[3])
  search_page_code = session['searched_ret_page_no']
  search_page_term = session['searched_ret_page_term']
  
  for u in ret_cursor[0]:
    retInfo_list.append(u)
  
  session['search_activated_ret']  = False
  return render_template('Retform.html', Retlist = retInfo_list,
                                        user = session['username_access'], 
                                        totalPages = session['totalPages'], 
                                        records_pages = session['recordsPerPage'], 
                                        count_user = session['count_retUser'],
                                        search_code = search_page_code,
                                        search_term = search_page_term )

@app.route('/search_ret_records/<search_code>', methods=['POST'])
@login_required
def search_ret_Records(search_code):
  retInfo_list = []

  if int(search_code) == 1:
    session['ret_num'] = request.form['searchbynumber'].strip()
    ret_docs = Ret_AccessMgmt_db.search_by_id(session['ret_num'], int(session['defaultPage']), int(session['rPerPage']))
    session['searched_ret_page_no'] = '1'
    session['searched_ret_page_term'] = session['ret_num']

  if int(search_code) == 2:
    session['ret_name'] = request.form['searchbyname'].strip()
    ret_docs = Ret_AccessMgmt_db.search_by_name(session['ret_name'],int(session['defaultPage']),int(session['rPerPage']))
    session['searched_ret_page_no'] = '2'
    session['searched_ret_page_term'] = session['ret_name']

  for o in ret_docs[0]:
    retInfo_list.append(o)
  session['ret_records'] = retInfo_list
  
  session['recordsPerPage'] = int(ret_docs[1])
  session['count_retUser'] = int(ret_docs[2])
  session['totalPages'] = int(ret_docs[3])
  
  session['search_activated_ret']  = True
  return redirect(url_for('RetailersWrapper'))


@app.route("/saveRet", methods=['POST'])
@login_required
def save_ret_records():
  session['edit_record'] = False
  ret_list = []
  org_id  = request.form['oid']
  email = request.form['eid']
  user_id = org_id + '_' + email
  ret_emList = []
  ret_data = Ret_AccessMgmt_db.get_one_ret_details(user_id)
  for r in ret_data:
    ret_emList.append(r)
  if ret_emList:
    flash('User exists... try with new one')
  else:
    RetInfo = retailer_accessInfo.setRetData()
    password_Un = RetInfo["password"]
    password_Encrypt=retailer_accessInfo.sha_encryption(password_Un)
    ret_info = Ret_AccessMgmt_db.get_ret_details_from_ret_db(org_id)
    for r in ret_info:
      ret_list.append(r)
    if ret_list:
        org_name = ret_list[0]['program_name']

        RetInfo["password"] = password_Encrypt.strip()
        RetInfo["user_id"] = user_id.strip()
        RetInfo["org_name"] = org_name.strip()
        Ret_AccessMgmt_db.save_ret_details(RetInfo)

        password = password_Un
        phone = RetInfo['user_contact']
        user_id = RetInfo['user_id']
        first_name = RetInfo['first_name']
        org_name = RetInfo['org_name']
        send_sms_ret(password,phone,user_id,first_name,org_name)
    return redirect(url_for('RetailersWrapper'))

@app.route("/updateRet", methods=['POST'])
@login_required
def update_ret_records():
  session['edit_record'] = True
  Ret_Info = retailer_accessInfo.setRetData()
  session['edit_record'] = False
  oid = request.form['id']
  Ret_AccessMgmt_db.update_ret_user_record(oid, Ret_Info)
  return redirect(url_for('RetailersWrapper'))

@app.route("/editRet/<oid>", methods=['POST'])
@login_required
def edit_ret_records(oid):
  session['edit_record'] = True
  ret_recs = []
  ret_info = Ret_AccessMgmt_db.get_ret_user_detail(oid)
  for r in ret_info:
    ret_recs.append(r)
  ret_num = ret_recs[0]['org_id']
  return render_template('Retedit.html',org_id = ret_num, Retlist = ret_recs, user = session['username_access'])

@app.route('/send_retSMS', methods=['POST'])
@login_required
def send_sms_ret(password,phone,user_id,first_name,org_name):
  sendSms.send_msg(password,phone,user_id,first_name,org_name)
  return redirect(url_for('RetailersWrapper'))

@app.route("/deleteRetUser/<oid>", methods=['POST'])
@login_required
def delete_RetUser_by_ID(oid):
  Ret_AccessMgmt_db.delete_a_retUser(oid)
  return redirect(url_for('RetailersWrapper'))

@app.route("/resetRet/<oid>",methods = ['POST'])
@login_required
def reset_ret(oid):
  ret_emList = []
  ret_data = Ret_AccessMgmt_db.get_ret_user_detail(oid)
  for d in ret_data:
    ret_emList.append(d)
  new_password = retailer_accessInfo.generate_password(4, 2)
  new_password_en = retailer_accessInfo.sha_encryption(new_password)

  retInfo = {}
  new_date =  datetime.datetime.now(pytz.timezone('US/Central'))
  date_time = new_date.strftime("%Y %b %d %a %I:%M:%S%p")

  retInfo['password'] = new_password_en
  retInfo['created_date'] = date_time

  Ret_AccessMgmt_db.update_one_password(oid, retInfo)
  phone = ret_emList[0]['user_contact']
  user_id = ret_emList[0]['user_id']
  first_name = ret_emList[0]['first_name']
  org_name = ret_emList[0]['org_name']
  send_sms_ret(new_password,phone,user_id,first_name,org_name)
  flash('Successfully reset the password')
  return redirect(url_for('RetailersWrapper'))
#-----------------------------------------------------------------------------------------------------------
# Nexus Cloud
@app.route("/nexus_cloud")
@login_required
def CloudWrapper():
  cloud_list = []
  user_Id = ''
  cloud_cur = Cloud_AccessMgmt_db.get_cloud_details()
  for c in cloud_cur:
    cloud_list.append(c)
  if cloud_list:
    org_Id = config['org_cloud']['ORG_ID']
    org_Name = config['org_cloud']['ORG_NAME']
  else:
    org_Id = config['org_cloud']['ORG_ID']
    org_Name = config['org_cloud']['ORG_NAME']
    flash('No Cloud User user exists')
  session['count_cloudUser'] = Cloud_AccessMgmt_db.get_count_cloud_users()
  return render_template('cloudform.html',
                          cloudlist = cloud_list,
                          orgId = org_Id,
                          orgName = org_Name,
                          user = session['username_access'],
                          count_user = session['count_cloudUser'])


@app.route("/saveCloud", methods=['POST'])
@login_required
def save_cloud_records():
  session['edit_record'] = False
  orgid = request.form['oid']
  email = request.form['eid']
  user_id = orgid + '_' + email
  cloud_emList = []
  cloud_data = Cloud_AccessMgmt_db.get_one_cloud_details(user_id)
  for d in cloud_data:
    cloud_emList.append(d)
  if cloud_emList:
    flash('User exists... try with new one')
  else:
    cloudInfo = cloud_accessInfo.setCloudData()
    password_Un = cloudInfo["password"]
    password_Encrypt=cloud_accessInfo.sha_encryption(password_Un)
    cloudInfo["password"] = password_Encrypt.strip()
    cloudInfo["user_id"] = user_id.strip()
    Cloud_AccessMgmt_db.save_cloud_details(cloudInfo)
    password = password_Un
    phone = cloudInfo['user_contact']
    user_id = cloudInfo['user_id']
    first_name = cloudInfo['first_name']
    org_name = cloudInfo['org_name']
    send_sms_cloud(password,phone,user_id,first_name,org_name)
  return redirect(url_for('CloudWrapper'))

@app.route("/updateCloud", methods=['POST'])
@login_required
def update_cloud_records():
  session['edit_record'] = True
  cloud_Info = cloud_accessInfo.setCloudData()
  session['edit_record'] = False
  oid = request.form['id']
  Cloud_AccessMgmt_db.update_cloud_user_record(oid, cloud_Info)
  return redirect(url_for('CloudWrapper'))

@app.route("/editCloud/<oid>", methods=['POST'])
@login_required
def edit_cloud_records(oid):
  session['edit_record'] = True
  cloud_recs = []
  cloud_info = Cloud_AccessMgmt_db.get_cloud_user_detail(oid)
  for cld in cloud_info:
    cloud_recs.append(cld)
  cloud_num = cloud_recs[0]['org_id']
  return render_template('cloudedit.html',org_id = cloud_num, cloudlist = cloud_recs, user = session['username_access'])

@app.route('/send_cloudSMS', methods=['POST'])
@login_required
def send_sms_cloud(password,phone,user_id,first_name,org_name):
  sendSms.send_msg(password,phone,user_id,first_name,org_name)
  return redirect(url_for('CloudWrapper'))

@app.route("/deleteCloud/<oid>", methods=['POST'])
@login_required
def delete_clouduser_by_ID(oid):
  Cloud_AccessMgmt_db.delete_a_cloudUser(oid)
  return redirect(url_for('CloudWrapper'))

#Reset for ASC
@app.route("/resetCloud/<oid>",methods = ['POST'])
@login_required
def reset_cloud(oid):
  cloud_records = []
  cloud_recs = Cloud_AccessMgmt_db.get_cloud_user_detail(oid)
  for c in cloud_recs:
    cloud_records.append(c)
  new_password = cloud_accessInfo.generate_password(4, 2)
  new_password_en = cloud_accessInfo.sha_encryption(new_password)

  cldInfo = {}
  new_date =  datetime.datetime.now(pytz.timezone('US/Central'))
  date_time = new_date.strftime("%Y %b %d %a %I:%M:%S%p")

  cldInfo['password'] = new_password_en
  cldInfo['created_date'] = date_time

  Cloud_AccessMgmt_db.update_one_password(oid, cldInfo)
  phone = cloud_records[0]['user_contact']
  user_id = cloud_records[0]['user_id']
  first_name = cloud_records[0]['first_name']
  org_name = cloud_records[0]['org_name']
  send_sms_cloud(new_password,phone,user_id,first_name,org_name)
  flash('Successfully reset the password')
  return redirect(url_for('CloudWrapper'))
#---------------------------------------------------------------------------------------------------------------
#Retailer Rates
@app.route("/rates")
@login_required
def ratesWrapper():
  rates_cursor = retail_labor_rates_db.get_rates_details()
  rates_list = []
  for i in rates_cursor:
    rates_list.append(i)
  if rates_list:
    rate = config['ret_rate']['RATE']
  else:
    rate = config['ret_rate']['RATE']
    flash('Rates does not exists')
  return render_template('ratesform.html', ret_rate = rate, rateslist = rates_list, user = session['username_access'])

@app.route("/saveRates", methods=['POST'])
@login_required
def save_rates_records():
  id_name  = request.form['laboridname']
  rates_list = []
  rate_cur = retail_labor_rates_db.get_rates_details_by_id(id_name)
  for l in rate_cur:
    rates_list.append(l)
  if rates_list:
    flash('Id name exists... try with new one')
  else:
    ratesInfo = retail_labor_ratesInfo.setratesData()
    retail_labor_rates_db.save_rates_details(ratesInfo)
    retail_labor_rates_db.update_key_field(id_name)
  return redirect(url_for('ratesWrapper'))

@app.route("/updateRates", methods=['POST'])
@login_required
def update_rates_records():
  rates_Info = retail_labor_ratesInfo.setratesData()
  ratesID=request.form['id']
  retail_labor_rates_db.update_rates_record(ratesID, rates_Info)
  return redirect(url_for('ratesWrapper'))

@app.route("/editRates/<rates_id>", methods=['POST'])
@login_required
def edit_rates_records(rates_id):
  rates_recs = []
  rates_cursor = retail_labor_rates_db.get_rates_detail_by_oid(rates_id)
  for r in rates_cursor:
    rates_recs.append(r)
  return render_template('rates_edit.html', rateslist = rates_recs, user = session['username_access'])

@app.route("/deleteRates/<rates_id>/<id_name>", methods=['POST'])
@login_required
def delete_rates(rates_id,id_name):
  retail_labor_rates_db.delete_rates_by_id(rates_id)
  # retail_labor_rates_db.delete_key_field(id_name)
  return redirect(url_for('ratesWrapper'))

@app.route("/deactivateRates/<rates_id>", methods=['POST'])
@login_required
def deactivate_rates(rates_id):
  rates_recs = []
  rates_cursor = retail_labor_rates_db.get_rates_detail_by_oid(rates_id)
  for r in rates_cursor:
    rates_recs.append(r)
  status_key = rates_recs[0]['Status']
  status_key = False
  retail_labor_rates_db.update_status_field(rates_id,status_key)
  return redirect(url_for('ratesWrapper'))

#----------------------------------------------------------------------------------------------------------------
#Contractors rates
@app.route("/Conrates")
@login_required
def Con_ratesWrapper():
  rates_cursor = labor_rates_db.get_con_labor_rates_details()
  rates_list = []
  for i in rates_cursor:
    rates_list.append(i)
  return render_template('con_ratesform.html', rateslist = rates_list, user = session['username_access'])

@app.route("/saveConRates", methods=['POST'])
@login_required
def save_con_rates_records():
  id_name  = request.form['laboridname']
  rates_list = []
  rate_cur = labor_rates_db.get_con_labor_rates_details_by_id(id_name)
  for l in rate_cur:
    rates_list.append(l)
  if rates_list:
    flash('Id name exists... try with new one')
  else:
    ratesInfo = labor_ratesInfo.setConlabor_ratesData()
    labor_rates_db.save_con_labor_rates_details(ratesInfo)
  return redirect(url_for('Con_ratesWrapper'))

@app.route("/updateConRates", methods=['POST'])
@login_required
def update_con_rates_records():
  rates_Info = labor_ratesInfo.setConlabor_ratesData()
  ratesID=request.form['id']
  labor_rates_db.update_con_labor_rates_record(ratesID, rates_Info)
  return redirect(url_for('Con_ratesWrapper'))

@app.route("/editConRates/<rates_id>", methods=['POST'])
@login_required
def edit_Conrates_records(rates_id):
  rates_recs = []
  rates_cursor = labor_rates_db.get_con_labor_rates_detail_by_id(rates_id)
  for r in rates_cursor:
    rates_recs.append(r)
  return render_template('con_rates_edit.html', rateslist = rates_recs, user = session['username_access'])

@app.route("/deleteConRates/<rates_id>", methods=['POST'])
@login_required
def delete_Conrates(rates_id):
  labor_rates_db.delete_con_labor_rates_by_id(rates_id)
  return redirect(url_for('Con_ratesWrapper'))

@app.route("/deactivateConRates/<rates_id>", methods=['POST'])
@login_required
def deactivate_Conrates(rates_id):
  rates_recs = []
  rates_cursor = labor_rates_db.get_con_labor_rates_details_by_id(rates_id)
  for r in rates_cursor:
    rates_recs.append(r)
  status_key = rates_recs[0]['Status']
  status_key = False
  labor_rates_db.update_con_labor_status_field(rates_id,status_key)
  return redirect(url_for('Con_ratesWrapper'))

#------------------------------------------------------------------------------------------------------------------
#Feedback section
@app.route("/reviews_feeds")
@login_required
def Feeds_Wrapper():
  review_cursor = reviews_feedbackMgmt_db.get_feedback_details_from_contractor_db()
  review_list = []
  for i in review_cursor:
    review_list.append(i)
  return render_template('con_reviews_feedbackform.html', reviewlist = review_list, user = session['username_access'])

@app.route("/editreviews/<acc_no>", methods=['POST'])
@login_required
def edit_Con_reviews_records(acc_no):
  feeds_recs = []
  feeds_cursor = reviews_feedbackMgmt_db.get_feedbacks_from_con_db_by_acc_no(acc_no)
  for r in feeds_cursor:
    feeds_recs.append(r)
  return render_template('con_reviews_feedback_editform.html', reviewlist = feeds_recs, user = session['username_access'])

@app.route("/updateConFeeds", methods=['POST'])
@login_required
def update_con_feeds_records():
  review_info = reviews_feedback_info.setreviewcData()
  acc_no = review_info['account']
  reviews_feedbackMgmt_db.update_con_feeds_by_acc_no(acc_no, review_info)
  return redirect(url_for('Feeds_Wrapper'))

@app.route("/deletefeeds/<acc_no>", methods=['POST'])
@login_required
def delete_con_feed(acc_no):
  reviews_feedbackMgmt_db.delete_feeds_by_acc_no(acc_no)
  return redirect(url_for('Feeds_Wrapper'))

#-----------------------------------------------------------------------------------------------------------------
# DIY Status
@app.route("/diystatus")
@login_required
def DIY_statusWrapper():
  status_cursor = status_code_db.get_status_codes()
  status_list = []
  for i in status_cursor:
    status_list.append(i)
  return render_template('statusform.html', statuslist = status_list, user = session['username_access'])

@app.route("/savediystatus", methods=['POST'])
@login_required
def save_diy_status_records():
  status_info = {}
  status_code  = request.form['statuscode']
  print(status_code)
  status_list = []
  status_cur = status_code_db.get_status_by_status_code(status_code)
  for l in status_cur:
    status_list.append(l)
  if status_list:
    flash('Status Code exists... try with new one')
  else:
    status_info['status_code'] = status_code.strip()
    status_code_db.save_status_code(status_info)
  return redirect(url_for('DIY_statusWrapper'))

@app.route("/editstatus/<obj_id>", methods=['POST'])
@login_required
def edit_status_code(obj_id):
  status_recs = []
  stat_cur = status_code_db.get_status_by_object_id(obj_id)
  for r in stat_cur:
    status_recs.append(r)
  return render_template('statusedit.html', statlist = status_recs, user = session['username_access'])

@app.route("/updateStatusCode", methods=['POST'])
@login_required
def update_status_code_records():
  status_code  = request.form['statuscode']
  status_info['status_code'] = status_code.strip()
  obj_id = request.form['id']
  status_code_db.update_a_status_code(obj_id, status_info)
  return redirect(url_for('DIY_statusWrapper'))

@app.route("/deletecode/<obj_id>", methods=['POST'])
@login_required
def delete_status_code(obj_id):
  status_code_db.delete_a_status_code(obj_id)
  return redirect(url_for('DIY_statusWrapper'))
# -----------------------------------------------------------------------------------------------------------
# F&I Status
@app.route("/fnistatus")
@login_required
def FNI_statusWrapper():
  fni_status_cursor = status_code_db.get_fni_status_codes()
  fni_status_list = []
  for i in fni_status_cursor:
    fni_status_list.append(i)
  return render_template('fni_statusform.html', fnistatuslist = fni_status_list, user = session['username_access'])

@app.route("/savefnistatus", methods=['POST'])
@login_required
def save_fni_status_records():
  status_info = {}
  status_code  = request.form['statcode']
  print(status_code)
  fni_status_list = []
  fni_status_cur = status_code_db.get_status_by_status_code(status_code)
  for l in fni_status_cur:
    fni_status_list.append(l)
  if fni_status_list:
    flash('Status Code exists... try with new one')
  else:
    status_info['status_code'] = status_code.strip()
    status_code_db.save_fni_status_code(status_info)
  return redirect(url_for('FNI_statusWrapper'))

@app.route("/editfnistatus/<obj_id>", methods=['POST'])
@login_required
def edit_fni_status_code(obj_id):
  status_recs = []
  stat_cur = status_code_db.get_fni_status_by_object_id(obj_id)
  for r in stat_cur:
    status_recs.append(r)
  return render_template('fni_statusedit.html', fnistatlist = status_recs, user = session['username_access'])

@app.route("/updatefniStatusCode", methods=['POST'])
@login_required
def update_fni_status_code_records():
  status_code  = request.form['statuscode']
  status_info['status_code'] = status_code.strip()
  obj_id = request.form['id']
  status_code_db.update_a_fni_status_code(obj_id, status_info)
  return redirect(url_for('FNI_statusWrapper'))

@app.route("/deletefnicode/<obj_id>", methods=['POST'])
@login_required
def delete_fni_status_code(obj_id):
  status_code_db.delete_a_fni_status_code(obj_id)
  return redirect(url_for('FNI_statusWrapper'))
#-----------------------------------------------------------------------------------------------------------------

# Login Section
@app.route("/logout/")
@login_required
def logout():
  session.clear()
  return redirect(url_for('login'))

@app.route("/login/")
def login():
  user_exists_flag = False
  if 'username_access' in session:
    user_exists_flag = True
    session['search_activated_dc'] = False
    session['dc_records'] = []
    session['searched_dc_page_no'] = ''
    session['searched_dc_page_term'] = ''
    session['totalPages'] = 0
    session['recordsPerPage'] = 0
    session['count_dcUser'] = 0
    session['dc_num'] = 0
    session['dc_name'] = ''
    session['search_activated_con'] = False
    session['con_records'] = []
    session['searched_con_page_no'] = ''
    session['searched_con_page_term'] = ''
    session['count_conUser'] = 0
    session['con_num'] = 0
    session['con_name'] = ''
    session['search_activated_asc'] = False
    session['asc_records'] = []
    session['searched_asc_page_no']= ''
    session['searched_asc_page_term'] = ''
    session['count_ascUser'] = 0
    session['asc_num'] = 0
    session['asc_name'] = ''
    session['search_activated_ret'] = False
    session['ret_records'] = []
    session['searched_ret_page_no'] = ''
    session['searched_ret_page_term'] = ''
    session['count_retUser'] = 0
    session['ret_num'] = 0
    session['ret_name'] = ''
    session['count_cloudUser'] = 0
    session['rPerPage'] = config['page_count']['RECORDS_PER_PAGE']
    session['defaultPage'] = config['page_count']['DEFAULT_PAGE']
    session['searchAll'] = config['search_dccode']['SEARCH_ALL']
    session['edit_record'] = False
    return redirect(url_for('index'))
  else:
    return render_template('login.html', user = '', user_exists = user_exists_flag) 

def sha_encryption(un_encrypted_password):
    encrypted_password = sha256_crypt.encrypt(un_encrypted_password)
    return encrypted_password 

@app.route("/login/attempt", methods=['POST'])
def login_attempt():
    login_id = request.form['id']
    login_pass = request.form['pass']
    cursor = Super_userAccessMgmt_db.search_authorization_by_id(login_id)
    db_id = ''
    db_pass = ''
    db_auth_data = {}
    incorrect_pass_flag = False
    for c in cursor:
        db_auth_data = c
    if db_auth_data:
        if sha256_crypt.verify(login_pass, db_auth_data['password']):
            session['username_access'] = db_auth_data['first_name']
            session['fullname'] = db_auth_data['first_name'] + " " + db_auth_data['last_name'] 
            session.pop('_flashes', None)
        else:
            incorrect_pass_flag = True
            flash('incorrect user credentials')
    else:
        incorrect_pass_flag = True
        flash('incorrect user credentials')
    return redirect(url_for('login'))
# ---------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
  app.run(debug=True)

