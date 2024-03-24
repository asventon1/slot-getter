from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

import datetime
import email
import imaplib
import mailbox

def get_mail(EMAIL_ACCOUNT, PASSWORD):

    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(EMAIL_ACCOUNT, PASSWORD)
    mail.list()
    mail.select('inbox')
    result, data = mail.uid('search', None, "ALL") # (ALL/UNSEEN)
    i = len(data[0].split())

    emails = []

    for x in range(i):
        latest_email_uid = data[0].split()[x]
        result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        # result, email_data = conn.store(num,'-FLAGS','\\Seen') 
        # this might work to set flag to seen, if it doesn't already
        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        # Header Details
        date_tuple = email.utils.parsedate_tz(email_message['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            local_message_date = "%s" %(str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
        email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
        email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
        subject = ""
        try:
            subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))
        except TypeError:
            pass



        # Body details
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                #file_name = "email_" + str(x) + ".txt"
                #output_file = open(file_name, 'w')
                #output_file.write("From: %s\nTo: %s\nDate: %s\nSubject: %s\n\nBody: \n\n%s" %(email_from, email_to,local_message_date, subject, body.decode('utf-8')))
                #output_file.close()
                
                email_dict = {
                    "from": email_from,
                    "to": email_to,
                    "date": local_message_date,
                    "subject": subject,
                    "body": body.decode('utf-8')
                }

                emails.append(email_dict)
                
            else:
                continue

    return emails

import smtplib
 
def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
 
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems

email_dict_list = get_mail("slotgetter@gmail.com", "gettheslot_1")

deactivated_people = []

for email_dict in email_dict_list:
    if(email_dict['body'].split()[0].strip().lower() == "deactivate"):
        if(email_dict['from'] not in deactivated_people):
            deactivated_people.append(email_dict['from'].lower())
    elif(email_dict['body'].split()[0].strip().lower() == "activate"):
        deactivated_people.remove(email_dict['from'].lower())
        
print(deactivated_people) 


store_dict = {}

with open("/home/asventon/python/slot-getter/people.txt") as f:
    text = f.read().split("\n")
    for i in text:
        if(i != ''):
            if(i[0] != "#"):
                line = i.split(":")
                email_deactivated = False
                for x in deactivated_people:
                    if(line[0].lower() in x):
                        email_deactivated = True
                        break
                if(not email_deactivated):
                    stores = line[1].split(",")
                    for x in stores:
                        if x in store_dict:
                            store_dict[x].append(line[0])
                        else:
                            store_dict[x] = [line[0]]

print(store_dict)

for store in store_dict.keys():

    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')

    driver = webdriver.Firefox(options=options)
    #driver = webdriver.Firefox()
    driver.get("https://www.heb.com/")
    time.sleep(5)
    try:
        close = driver.find_element_by_xpath("//button[contains(@class, 'close')]")
        close.click()
    except:
        pass
    time.sleep(1)
    open_slots = driver.find_element_by_xpath("//button[contains(@class, 'details curbside-icon')]")
    open_slots.click()
    time.sleep(1)
    change_store = driver.find_element_by_xpath("//button[contains(@class, 'change-store-button')]")
    change_store.click()
    time.sleep(1)
    change_store_input = driver.find_element_by_id("change-store-input")
    #change_store_input.send_keys("Victoria H-E-B plus!")
    #change_store_input.send_keys("parmer and whitestone")
    change_store_input.send_keys(store)
    change_store_input.submit()
    time.sleep(2)

    select_store = driver.find_element_by_xpath("//button[contains(@class, 'btn store__select-button btn-primary btn-primary--blue')]")
    select_store.click()

    time.sleep(2)

    change_week = driver.find_element_by_xpath("//button[contains(@class, 'picker-day__scroll picker-day__scroll--prev')]")
    change_week.click()

    has_slot1 = True
    has_slot2 = True

    try:
        slot1 = driver.find_element_by_xpath("//button[contains(@class, 'picker-day__button')]//div[contains(@class, 'picker-day__date')]")
    except:
        has_slot1 = False

    time.sleep(2)

    change_week = driver.find_element_by_xpath("//button[contains(@class, 'picker-day__scroll picker-day__scroll--next')]")
    change_week.click()

    time.sleep(2)

    try:
        slot1 = driver.find_element_by_xpath("//button[contains(@class, 'picker-day__button')]//div[contains(@class, 'picker-day__date')]")
    except:
        has_slot2 = False

    driver.close()

    send_string = ''

    if(has_slot1):
        send_string += "there are slots open in the next 5 days at " + store + " \n"
    else:
        send_string += "there are no slots open in the next 5 days at " + store + " \n"

    if(has_slot2):
        send_string += "there are slots open in the 5 days after that at " + store + " \n"
    else:
        send_string += "there are no slots open in the 5 days after that at " + store + " \n"

    send_string += "\n\n\nIf you would like to pause these emails just send an email to this email address slotgetter@gmail.com with the body of the email just saying deactivate. The subject line dosen't matter. There just needs to be one word deavtivate all lowercase in the body\nTo unpause emails you can send an email saying activate\n"  

    #print(send_string)

    if(has_slot1 or has_slot2):

        sendemail(from_addr    = 'slotgetter@gmail.com', 
                  to_addr_list = store_dict[store],
                  cc_addr_list = [], 
                  subject      = 'Slot open at ' + store, 
                  message      = send_string, 
                  login        = 'slotgetter@gmail.com', 
                  password     = '')
