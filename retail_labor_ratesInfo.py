from flask import request
import random
import string
import datetime
import time

def setratesData():
  rateInfo = {}
  retail_labor_id_name = request.form['laboridname']
  retail_labor_service = request.form['laborgrpname']
  retail_labor_description = request.form['laboruilabel']
  retail_labor_default_value = request.form['default']

  rateInfo['retail_labor_id_name'] = retail_labor_id_name.strip()
  rateInfo['retail_labor_service'] = retail_labor_service.strip()
  rateInfo['retail_labor_description'] = retail_labor_description.strip()
  rateInfo['retail_labor_default_value'] = 0.00
  rateInfo['Status'] = True
  return rateInfo



