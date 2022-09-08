# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
import sensitive_Info_db

#add the function send_mail(sms_info)
def send_msg(password,phone,user_id,first_name,org_name):
	# Your Account Sid and Auth Token from twilio.com/console
	# DANGER! This is insecure. See http://twil.io/secure
	sms_Info = []
	sms_cursor = sensitive_Info_db.get_sms_details()
	for s in sms_cursor:
		sms_Info.append(s)
	if sms_Info[0]['account_name'] == 'Twilio':
		account_sid = sms_Info[0]['account_sid_no']
		auth_token =  sms_Info[0]['auth_token']
		client = Client(account_sid, auth_token)
		message = 'Hello ' + first_name + ', Welcome to Amarr Service Center Platform. Your secure credentials for ' + org_name + ' are :- Email : ' + user_id +' and Password : ' + password
		prefix = '+1'
		num=prefix + phone
		message = client.messages.create(
	                              body=message,
	                              from_='+12058589412',
	                              to=num
	                          )
	return
