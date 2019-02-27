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
                                                # Question type     Name of field           Value
    Satisfaction = "Satisfaction"               # 1-5               Questions[0].Responses  value=5
    # find_by_value("Next")
    # Are you sure popup find_link_by_text("Yes")
    OrderPlacement = "Order placement method"   # Order method      Questions[0].Responses  value=1
    CorrectOrder = "Received correct order"     # Yes|No            Questions[1].Responses  value=1
    # find_by_value("Next")
    FoodQuality = "Food quality"                # 1-5               Questions[0].Responses  value=5
    # find_by_value("Next")
    FriendlyTeam = "Team friendliness"          # 1-5               Questions[0].Responses  value=5
    Speed = "Service speed"                     # 1-5               Questions[1].Responses  value=5
    Cleanliness = "Cleanliness"                 # 1-5               Questions[2].Responses  value=5
    # find_by_value("Next")
    Temperature = "Temperature"                 # Temperature       Questions[0].Responses  value=1
    # find_by_value("Next")
    MenuVariety = "Menu variety"                # 1-5               Questions[0].Responses  value=5
    ValueReceived = "Value received"            # 1-5               Questions[1].Responses  value=5
    # find_by_value("Next")
    ProblemDuringVisit = "Problem during visit" # Yes|No            Questions[0].Responses  value=2
    # find_by_value("Next")
    CompeditorsIn30Days = "Visits to compeditors in last 30 days" # Questions[0].Responses  value=1-6
    SmashBurgerIn30Days = "Visits to SmashBurger in last 30 days" # Questions[1].Responses  value=4
    TypeOfVisit = "Type of visit"               #                   Questions[2].Responses  value=3
    LoyaltyMember = "Loyalty member"            # Yes|No            Questions[3].Responses  value=1
    # find_by_value("Next")
    Recommendation = "Recommendation likeliness"# 1-5               Questions[0].Responses  value=5
    # find_by_value("Next")
    Compliments = "Compliments"                 # Yes|No            Questions[0].Responses  value=2
    AnyRecommendations = "Any recommendations"  # Yes|No            Questions[1].Responses  value=1
    # find_by_value("Next")
    Recommendations = "Recommendations"         # Open              Questions[0].OpenEndedResponse value="Free WiFi"
    # find_by_value("Next")
    Gender = "Gender"                           # Gender            Questions[0].Responses  value=1
    Age = "Age"                                 # Age               Questions[1].Responses  value=2


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


def do_receipt_info_page(browser, receipt_info):
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


def do_begin_survey(browser):
    button = browser.find_by_value("Begin Survey")
    button.click()


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
        do_receipt_info_page(browser, receipt_info)
        do_begin_survey(browser)
    except Exception as e:
        print(e)
        code.interact(local=locals())

    input()
    close_browser(browser)


if __name__ == '__main__':
    main()
