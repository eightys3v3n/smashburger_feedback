from enum import Enum
from datetime import datetime

class FIELDS(Enum):
	StoreNumber = 'Store number'
	VisitDateTime = 'Date/time of visit (yymmdd HHMM)'
	ReceiptNumber = 'Receipt number (unit number)'

HEADLESS = False
FEEDBACK_URL = 'https://smashburgerfeedback.survey.marketforce.com'
DATETIME_FORMAT = '%y%m%d %H%M'
DEFAULT_RECEIPT_INFO = {
	FIELDS.StoreNumber: '1683',
}

STORE_NUMBER_PROMPT = '{}: {}{}'.format(
	FIELDS.StoreNumber.value,
	DEFAULT_RECEIPT_INFO[FIELDS.StoreNumber],
	'\b' * len(DEFAULT_RECEIPT_INFO[FIELDS.StoreNumber])			#Print the default number but user replaces it with their typing
)
DATETIME_PROMPT = '{}: '.format(FIELDS.VisitDateTime.value)
RECEIPT_NUMBER_PROMPT = '{}: '.format(FIELDS.ReceiptNumber.value)

def prompt_receipt_info():
	""" Prompts for and returns the receipt store number and datetime of visit.
		Returns a dict using FIELDS for the store number and visit datetime.
	"""
	ret = {}
	
	r = ''
	while not r.isdigit():
		r = input(STORE_NUMBER_PROMPT)
		if r == '':
			r = DEFAULT_RECEIPT_INFO[FIELDS.StoreNumber]
	ret[FIELDS.StoreNumber] = r
	
	r = None
	while r is None:
		r = input(DATETIME_PROMPT)
		try:
			r = datetime.strptime(r, DATETIME_FORMAT)
		except ValueError as e:
			print(e)
			r = None
	ret[FIELDS.VisitDateTime] = r
	
	r = ''
	while not r.isdigit():
		r = input(RECEIPT_NUMBER_PROMPT)
		r = r.replace('-', '')
	ret[FIELDS.ReceiptNumber] = r
	
	return ret
	
def open_browser():
	browser = splinter.Browser("chrome", headless=HEADLESS)
	browser.__enter__()
	browser.visit(FEEDBACK_URL)
	
def receipt_info_page(browser, receipt_info):
	# Store number: ID=EntryCode Type=text
	store_num = receipt_info[FIELDS.StoreNumber]
	browser.fill('EntryCode', store_num)
	
	# Date of visit: ID=DateOfVisit Type=text Format=mm/dd/YYYY
	date_of_visit = receipt_info[FIELDS.VisitDateTime].date()
	date_of_visit = date_of_visit.strftime('%m/%d/%y')
	browser.fill('DateOfVisit', date_of_visit)
	
	"""
	Time of visit: ID=TimeOfVisit Type=select Options=
		1: -11
		2: 11-13
		3: 13-17
		4: 17-19
		5: 19-
	"""
	time = receipt_info[FIELDS.VisitDateTime].time()
	if time.hour > 19:
		time_of_visit = '5'
	elif time.hour > 17:
		time_of_visit = '4'
	elif time.hour > 13:
		time_of_visit = '3'
	elif time.hour > 11:
		time_of_visit = '2'
	else:
		time_of_visit = '1'
	browser.select('TimeOfVisit', time_of_visit)
	
	# Check number: ID=CheckNum Type=text
	check_num = receipt_info[FIELDS.ReceiptNumber]
	browser.fill('CheckNum', check_num)
	
	button = browser.find_by_class('startButton')
	button.click()
	
def close_browser(browser):
	browser.__exit__(None, None, None)

def main():
	receipt_info = prompt_receipt_info()
	print(receipt_info)
	
	browser = open_browser()
	
	#do_receipt_info_page(receipt_info)
	
	close_browser(browser)
	

if __name__ == '__main__':
	main()
