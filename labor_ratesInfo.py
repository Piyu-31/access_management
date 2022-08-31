from flask import request
import random
import string
import datetime
import time

def setConlabor_ratesData():
  rateInfo = {}
  contractor_labor_id_name = request.form['laboridname']
  contractor_labor_group_name = request.form['laborgrpname']
  contractor_labor_UI_label = request.form['laboruilabel']
  contractor_labor_default_value = request.form['default']

  rateInfo['contractor_labor_id_name'] = contractor_labor_id_name.strip()
  rateInfo['contractor_labor_group_name'] = contractor_labor_group_name.strip()
  rateInfo['contractor_labor_UI_label'] = contractor_labor_UI_label.strip()

  if contractor_labor_default_value == 'rate':
    rateInfo['contractor_labor_default_value'] = 0.00
  else:
    rateInfo['contractor_labor_default_value'] = ''

  rateInfo['Status'] = True
  return rateInfo



