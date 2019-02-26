from enum import Enum
from datetime import datetime

class FIELDS(Enum):
	StoreNumber = 'Store number'
	VisitDateTime = 'Date of visit (yymmdd HHMM)'
	
DATETIME_FORMAT = '%y%m%d %H%M'
DEFAULT_RECEIPT_INFO = {
	FIELDS.StoreNumber: '1683',
}

STORE_NUMBER_PROMPT = '{}: {}{}'.format(
	FIELDS.StoreNumber.value,
	DEFAULT_RECEIPT_INFO[FIELDS.StoreNumber],
	'\b' * len(DEFAULT_RECEIPT_INFO[FIELDS.StoreNumber])			#Print the default number but user replaces it with their typing
)

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
		else:
			r = r.replace('-', '')
	ret[FIELDS.StoreNumber] = r
	
	r = None
	while r is None:
		r = input('{}: '.format(FIELDS.VisitDateTime.value))
		try:
			r = datetime.strptime(r, DATETIME_FORMAT)
		except ValueError as e:
			print(e)
			r = None
	ret[FIELDS.VisitDateTime] = r
	
	return ret

def main():
	receipt_info = prompt_receipt_info()
	print(receipt_info)
	

if __name__ == '__main__':
	main()