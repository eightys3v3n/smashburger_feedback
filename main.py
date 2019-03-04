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


HEADLESS = False
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


def receipt_info_page(browser, receipt_info):
    # Store number: HTML_Name=STORE_NUMBER_NAME Type=text
    store_num = receipt_info[FIELDS.StoreNumber]
    browser.fill(STORE_NUMBER_NAME, store_num)

    # Date of visit: HTML_Name=DATE_OF_VISIT_NAME Type=text Format=mm/dd/YYYY
    date_of_visit = receipt_info[FIELDS.VisitDateTime].date()

    if date_of_visit.month == datetime.now().month:
        date_of_visit = date_of_visit.strftime('%m/%d/%y')
        date_picker = browser.find_link_by_text("Open Date Picker")
        assert len(date_picker) == 1, "Invalid date picker stuff found"
        date_picker = date_picker[0]
        date_picker.click()

        date_picker_box = browser.find_by_css('div[class="ui-datebox-grid"]')
        temp = []
        temp.extend(date_picker_box.find_by_css('div[class="ui-datebox-griddate ui-corner-all ui-btn-up-a"]')) # Valid days this month
        temp.extend(date_picker_box.find_by_css('div[class="ui-datebox-griddate ui-corner-all ui-btn-up-e"]')) # Current day
        entered_day = ""
        for e in temp:
            if e.value == str(receipt_info[FIELDS.VisitDateTime].day):
                entered_day = e
                break
        else:
            raise Exception("Didn't find a div for day {}".format(receipt_info[FIELDS.VisitDateTime].day))
        entered_day.click()

    else:
        raise NotImplementedError("Months other than the current aren't implemented")

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
    button.mouse_over()
    time.sleep(1)
    button.click()


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
    
    browser.select('Questions[0].Responses', '5')
    click_next(browser)
    code.interact(local=locals())
    

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
    
    browser.select('Questions[0].Responses', '1')
    browser.select('Questions[1].Responses', '1')
    click_next(browser)
    

def page_3(browser):
    """
    Food Quality:
        Name:    Questions[0].Responses
        Type:    select(1-5) # Horrible-Excellent
        Answer:  5
    Next
    """
    
    browser.select('Questions[0].Responses', '5')
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
    
    browser.select('Questions[0].Responses', '5')
    browser.select('Questions[1].Responses', '5')
    browser.select('Questions[2].Responses', '5')
    click_next(browser)
    
    
def page_5(browser):
    """
    Temperature:
        Name:    Questions[0].Responses
        Type:    select(1-3) # Just right, ...
        Answer:  1
    Next
    """
    
    browser.select('Questions[0].Responses', '1')
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
    
    browser.select('Questions[0].Responses', '5')
    browser.select('Questions[1].Responses', '5')
    click_next(browser)


def page_7(browser):
    """
    Problem during visit:
        Name:    Questions[0].Responses
        Type:    select(1,2) # Yes, No
        Answer:  2
    Next
    """
    
    browser.select('Questions[0].Responses', '2')
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
    
    browser.select('Questions[0].Responses', '1')
    browser.select('Questions[1].Responses', '4')
    browser.select('Questions[2].Responses', '3')
    browser.select('Questions[3].Responses', '1')
    click_next(browser)
    
    
def page_9(browser):
    """
    Recommendation:
        Name:    Questions[0].Responses
        Type:    select(1-5) # Never-Always
        Answer:  5
    Next
    """
    
    browser.select('Questions[0].Responses', '5')
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
    
    browser.select('Questions[0].Responses', '2')
    browser.select('Questions[1].Responses', '1')
    click_next(browser)


def page_11(browser):
    """
    Recommendations:
        Name:    Questions[0].OpenEndedResponse
        Type:    text
        Answer:  Free WiFi
    Next
    """
    
    browser.select('Questions[0].OpenEndedResponse', 'Free WiFi')
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
    
    browser.select('Questions[0].Responses', '1')
    browser.select('Questions[1].Responses', '2')
    #finish


def do_survey(browser):
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


def close_browser(browser):
    browser.__exit__(None, None, None)


def main():
    receipt_info = {
        FIELDS.StoreNumber: 1683,
        FIELDS.VisitDateTime: datetime(2019, 2, 24, 12, 59),
        FIELDS.ReceiptNumber: 103103
    }
    # receipt_info = prompt_receipt_info()
    # print(receipt_info)
    survey_answers = prompt_survey()
    print(survey_answers)

    browser = open_browser()

    try:
        do_survey(browser, receipt_info)   
    except Exception as e:
        print(e)
        code.interact(local=locals())

    input()
    close_browser(browser)


if __name__ == '__main__':
    main()
