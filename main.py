from datetime import datetime
from enum import Enum

import code
import time
import splinter


class FIELDS(Enum):
    StoreNumber = 'Store number'
    VisitDateTime = 'Date/time of visit (yymmdd HHMM)'
    ReceiptNumber = 'Receipt number (unit number)'


class QUESTIONS(Enum):
    """
    1-5 Horrible-Excellent:
        1: Horrible
        ...
        5: Excellent
    Yes|No:
        1: Yes
        2: No
    Temperature:
        1: Just right
        2:
        3:
    Order method:
        1: Inside restaurant to dine in
        2: Inside restaurant to go
        ...
    Number of visits to compeditor:
        1: 0
        2: 1
        ...
        6: 5 or more
    Number of visits to SmashBurger:
        1: 1
        2: 2
        ...
        5: 5 or more
    Type of visit:
        1: First visit to any SmashBurger
        2: First visit to this SmashBurger
        3: Return guest to this SmashBurger
    Gender:
        1: Male
        2: Female
        3: Prefer not to answer
    Age:
        1: Under 18
        2: 18-24
        ...
        8: Prefer not to answer
    """


HEADLESS = True
FEEDBACK_URL = 'https://smashburgerfeedback.survey.marketforce.com'
DATETIME_FORMAT = '%y%m%d %H%M'
DEFAULT_RECEIPT_INFO = {
    FIELDS.StoreNumber: '1683',
    FIELDS.VisitDateTime: datetime.now()
}

# Receipt info page
STORE_NUMBER_NAME = "EntryCode"
DATE_OF_VISIT_NAME = "Questions[0].OpenEndedResponse"
TIME_OF_VISIT_NAME = "Questions[1].Responses"
RECEIPT_NUMBER_NAME = "Questions[2].OpenEndedResponse"

STORE_NUMBER_PROMPT = '{}: {}{}'.format(
    FIELDS.StoreNumber.value,
    DEFAULT_RECEIPT_INFO[FIELDS.StoreNumber],
    '\b' * len(DEFAULT_RECEIPT_INFO[FIELDS.StoreNumber])
    # Print the default number but user replaces it with their typing
)

date_time = DEFAULT_RECEIPT_INFO[FIELDS.VisitDateTime].strftime(DATETIME_FORMAT)
DATETIME_PROMPT = '{}: {}{}'.format(
    FIELDS.VisitDateTime.value,
    date_time,
    '\b' * len(date_time)
)
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
        if r == '':
            r = DEFAULT_RECEIPT_INFO[FIELDS.VisitDateTime]
        else:
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


def prompt_survey_answers():
    ret = {}


def open_browser():
    browser = splinter.Browser("chrome", headless=HEADLESS)
    browser.__enter__()
    browser.visit(FEEDBACK_URL)
    return browser


class OpenDateBox:
    def __init__(self, browser):
        self.browser = browser
        self.activator = None
        self.date_box_element = None
        self.month_element = None

    def activate(self):
        self.activator = self.browser.find_link_by_text('Open Date Picker')
        if len(self.activator) != 1:
            print("Didn't find only one date box, found {}.".format(len(self.activator)))
            if len(self.activator) > 1:
                raise Exception("Found too many date box activation buttons")
            elif len(self.activator) == 0:
                raise Exception("Didn't find a date box activation")
        self.activator = self.activator[0]
        self.activator.click()

    def find_box(self):
        self.date_box_element = self.browser.find_by_css('div[class="ui-datebox-container ui-overlay-shadow ui-corner-all pop ui-body-b in"]')
        assert self.date_box_element is not None, "Found no date box elements."
        assert len(self.date_box_element) == 1, "Found too many date box elements."
        self.date_box_element = self.date_box_element[0]

    def find_month(self):
        self.month_element = self.date_box_element.find_by_tag('h4')
        assert self.month_element is not None, "Couldn't find date box month header."
        assert len(self.month_element) == 1, "Found too many date box month headers."
        self.month_element = self.month_element[0]

    def find_previous_month(self):
        self.previous_month_element = self.date_box_element.find_by_css('div[class="ui-datebox-gridminus ui-btn ui-btn-a ui-icon-minus ui-btn-icon-notext ui-btn-inline ui-shadow ui-corner-all"]')
        assert self.previous_month_element is not None, "Couldn't find previous month element."
        assert len(self.previous_month_element) == 1, "Found too many previous month elements."
        self.previous_month_element = self.previous_month_element[0]

    def find_day_grid(self):
        self.day_grid_element = self.date_box_element.find_by_css('div[class="ui-datebox-grid"]')
        assert self.day_grid_element is not None, "Couldn't find day grid element."
        assert len(self.day_grid_element) == 1, "Found too many day grid elements."
        self.day_grid_element = self.day_grid_element[0]

    def find_valid_days(self):
        valid_days = [
            *self.day_grid_element.find_by_css('div[class="ui-datebox-griddate ui-corner-all ui-btn-up-a"]'),  # Valid days this month
            *self.day_grid_element.find_by_css('div[class="ui-datebox-griddate ui-corner-all ui-btn-up-e"]')  # Current day
        ]
        return valid_days

    def find_elements(self):
        self.find_box()
        self.find_month()
        self.find_previous_month()
        self.find_day_grid()

    def get_month(self):
        month = self.month_element.text
        month = datetime.strptime(month, "%B %Y")
        return month

    def previous_month(self):
        self.previous_month_element.click()

    def select_day(self, desired_day):
        day_element = None
        days = self.find_valid_days()
        for day in days:
            if day.value == str(desired_day):
                day_element = day
                break
        assert day_element is not None, "Didn't find desired day."
        day_element.click()

    def select_month(self, month):
        assert self.get_month().month >= month, "The desired month is in the future?"
        while self.get_month().month > month:
            self.previous_month()

    def select_date(self, date):
        self.find_elements()
        self.select_month(date.month)
        self.select_day(date.day)


def receipt_info_page(browser, receipt_info):
    # Store number: HTML_Name=STORE_NUMBER_NAME Type=text
    store_num = receipt_info[FIELDS.StoreNumber]
    browser.fill(STORE_NUMBER_NAME, store_num)

    # Date of visit: HTML_Name=DATE_OF_VISIT_NAME Type=text Format=mm/dd/YYYY
    date_of_visit = receipt_info[FIELDS.VisitDateTime].date()

    date_box = OpenDateBox(browser)
    date_box.activate()
    date_box.select_date(date_of_visit)

    """
    Time of visit: HTML_Name=TIME_OF_VISIT_NAME Type=select Options=
        1: -11
        2: 11-13
        3: 13-17
        4: 17-19
        5: 19-
    """
    visit_time = receipt_info[FIELDS.VisitDateTime].time()
    if visit_time.hour > 19:
        time_of_visit = '5'
    elif visit_time.hour > 17:
        time_of_visit = '4'
    elif visit_time.hour > 13:
        time_of_visit = '3'
    elif visit_time.hour > 11:
        time_of_visit = '2'
    else:
        time_of_visit = '1'
    browser.select(TIME_OF_VISIT_NAME, time_of_visit)

    # Check number: HTML_Name=RECEIPT_NUMBER_NAME Type=text
    check_num = receipt_info[FIELDS.ReceiptNumber]
    browser.fill(RECEIPT_NUMBER_NAME, check_num)

    button = browser.find_by_css('div[class=startButton]')
    time_started = time.time()
    while not button.visible and time.time() - time_started < 20:
        time.sleep(0.5)
    button.mouse_over()
    button.click()


def select_ratio(browser, name, value):
    input_element = browser.find_by_css('input[name="{}"][value="{}"]'.format(name, value))
    clickable_element = input_element.find_by_xpath('..')
    clickable_element.click()


def begin_survey(browser):
    button = browser.find_by_value("Begin Survey")
    button.click()


def click_next(browser):
    next_button = browser.find_by_value('Next')
    next_button.click()


def page_1(browser):
    """
    Satisfaction:
        Name:    Questions[0].Responses
        Type:    select(1-5) # Horrible-Excellent
        Answer:  5 # Excellent
    Next
    Confirm
    """
    
    select_ratio(browser, 'Questions[0].Responses', '5')
    click_next(browser)
    yes_button = browser.find_by_text('Yes')
    yes_button[1].click() # No idea why there are two yes buttons, but only the second one works.
    

def page_2(browser):
    """
    Order method:
        Name:    Questions[0].Responses
        Type:    select(1...) Order in eat in, ...
        Answer:  1
    Received correct order:
        Name:    Questions[1].Responses
        Type:    select(1,2) # Yes, No
        Answer:  1
    Next
    """

    select_ratio(browser, 'Questions[0].Responses', '1')
    select_ratio(browser, 'Questions[1].Responses', '1')
    click_next(browser)
    

def page_3(browser):
    """
    Food Quality:
        Name:    Questions[0].Responses
        Type:    select(1-5) # Horrible-Excellent
        Answer:  5
    Next
    """
    
    select_ratio(browser, 'Questions[0].Responses', '5')
    click_next(browser)
    
    
def page_4(browser):
    """
    Staff friendliness:
        Name:    Questions[0].Responses
        Type:    select(1-5) # Horrible-Excellent
        Answer:  5
    Speed:
        Name:    Questions[1].Responses
        Type:    select(1-5) # Horrible-Excellent
        Answer:  5
    Cleanliness:
        Name:    Questions[2].Responses
        Type:    select(1-5) # Horrible-Excellent
        Answer:  5
    Next
    """
    
    select_ratio(browser, 'Questions[0].Responses', '5')
    select_ratio(browser, 'Questions[1].Responses', '5')
    select_ratio(browser, 'Questions[2].Responses', '5')
    click_next(browser)
    
    
def page_5(browser):
    """
    Temperature:
        Name:    Questions[0].Responses
        Type:    select(1-3) # Just right, ...
        Answer:  1
    Next
    """
    
    select_ratio(browser, 'Questions[0].Responses', '1')
    click_next(browser)
    
    
def page_6(browser):
    """
    Menu variety:
        Name:    Questions[0].Responses
        Type:    select(1-5) # Horrible-Excellent
        Answer:  5
    Value received:
        Name:    Questions[1].Responses
        Type:    select(1-5)
        Answer:  5
    Next
    """
    
    select_ratio(browser, 'Questions[0].Responses', '5')
    select_ratio(browser, 'Questions[1].Responses', '5')
    click_next(browser)


def page_7(browser):
    """
    Problem during visit:
        Name:    Questions[0].Responses
        Type:    select(1,2) # Yes, No
        Answer:  2
    Next
    """
    
    select_ratio(browser, 'Questions[0].Responses', '2')
    click_next(browser)


def page_8(browser):
    """
    Visits to compeditors in last 30 days:
        Name:    Questions[0].Responses
        Type:    select(1-6)
        Answer:  
    Visits to SmahsBurger in last 30 days:
        Name:    Questions[1].Responses
        Type:    select(...)
        Answer:  4
    Type of visit:
        Name:    Questions[2].Responses
        Type:    
        Answer:  3
    Loyalty member:
        Name:    Questions[3].Responses
        Type:    select(1,2) # Yes, No
        Answer:  1
    Next
    """
    
    select_ratio(browser, 'Questions[0].Responses', '1')
    select_ratio(browser, 'Questions[1].Responses', '4')
    select_ratio(browser, 'Questions[2].Responses', '3')
    select_ratio(browser, 'Questions[3].Responses', '1')
    click_next(browser)
    
    
def page_9(browser):
    """
    Recommendation:
        Name:    Questions[0].Responses
        Type:    select(1-5) # Never-Always
        Answer:  5
    Next
    """
    
    select_ratio(browser, 'Questions[0].Responses', '5')
    click_next(browser)


def page_10(browser):
    """
    Any compliments:
        Name:    Questions[0].Responses
        Type:    select(1,2) # Yes, No
        Answer:  2
    Any recommendations:
        Name:    Questions[1].Responses
        Type:    select(1,2) # Yes, No
        Answer:  1
    Next
    """
    
    select_ratio(browser, 'Questions[0].Responses', '2')
    select_ratio(browser, 'Questions[1].Responses', '1')
    click_next(browser)


def page_11(browser):
    """
    Recommendations:
        Name:    Questions[0].OpenEndedResponse
        Type:    text
        Answer:  Free WiFi
    Next
    """
    
    browser.fill('Questions[0].OpenEndedResponse', 'Free WiFi')
    click_next(browser)


def page_12(browser):
    """
    Gender:
        Name:    Questions[0].Responses
        Type:    select(1,2,3) # Male, Female, Not specified
        Answer:  1
    Age:
        Name:    Questions[1].Responses
        Type:    select(1,2,...) # a<18, 18<=a<24, ...
        Answer:  2
    Next
    """
    
    select_ratio(browser, 'Questions[0].Responses', '1')
    select_ratio(browser, 'Questions[1].Responses', '2')
    click_next(browser)


def get_number(browser):
    number = browser.find_by_css('span[style="color: #ff0000;"]')
    number = number.find_by_tag('span')[0]
    number = number.text
    return number


def do_survey(browser, receipt_info):
    receipt_info_page(browser, receipt_info)
    begin_survey(browser)
    page_1(browser)
    page_2(browser)
    page_3(browser)
    page_4(browser)
    page_5(browser)
    page_6(browser)
    page_7(browser)
    page_8(browser)
    page_9(browser)
    page_10(browser)
    page_11(browser)
    page_12(browser)
    number = get_number(browser)
    return number


def close_browser(browser):
    browser.__exit__(None, None, None)


def main():
    global browser
    # receipt_info = {
    #     FIELDS.StoreNumber: 1683,
    #     FIELDS.VisitDateTime: datetime(2019, 3, 3, 12, 56),
    #     FIELDS.ReceiptNumber: 10015
    # }
    receipt_info = prompt_receipt_info()
    browser = open_browser()

    number = do_survey(browser, receipt_info)
    print(number)

    close_browser(browser)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        code.interact(local=locals())
