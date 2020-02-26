import requests
from time import sleep
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def getFromServiceNow(url, user, pwd, headers):
    '''
    getFromServiceNow method connects to ServiceNow
    and returns json with requested data or ERROR if connection
    problems or URL incorect
    '''
    response = requests.get(url, auth = (user,pwd), headers=headers)

    if response.status_code != 200:
        print(response.status_code)
        return 'ERROR'
    else:
        return response.json()

def putToServiceNow(url, user,pwd, headers, data):
    '''
    putToServiceNow method connects to ServiceNow and modify record
    according to data variable, data needs to be formated json.dumps(data)
    returns ERROR, if operation failed or OK if operation went good
    '''
    response = requests.put(url, auth = (user, pwd), headers=headers, data=data )

    if response.status_code != 200:
        return 'ERROR'
    else:
        return 'OK'

def returnCallToCS(sys_id, host, user, pwd, headers, message, group = '6d27bd7537281f4010e81d8643990e83' ):
    '''
    returnCallToCS function returns  to CS if needed
    '''
    data = json.dumps({'u_assignment_group':group, 'u_work_notes':message})
    url = host + '/api/now/table/new_call/'+str(sys_id)
    answer = putToServiceNow (url,user,pwd,headers,data)

    if answer == 'OK':
        return 'OK'
    else:
        return 'ERROR'

def logToTicketSystem(host,user,pwd):
    '''Login to the ticket system using web browser Firefox'''
    driver = webdriver.Firefox()
    #host='https://opusflow.service-now.com/'
    driver.get(host + '/login.do')
    elem=driver.find_element_by_id('user_name')
    elem.clear()
    elem.send_keys(user)
    elem=driver.find_element_by_id('user_password')
    elem.clear()
    elem.send_keys(pwd)
    submit_button = driver.find_elements_by_id('sysverb_login')[0]
    submit_button.click()
    sleep(5)

    return driver

def orderRequest(driver,sys_id,host,user,pwd):
    url = host + '/nav_to.do?uri=%2Fcom.glideapp.servicecatalog_cat_item_view.do%3Fsysparm_id%3D9d7c5f60f8869000b662f2c5990bd9f5%26sysparm_user%3Df914cc97208b60005df5b16d187aabdc%26sysparm_location%3D4b9b91bbdb5c7640d1597cc9bf961903%26sysparm_processing_hint%3Dsetfield:request.u_source_call%3D'+sys_id+'%26sysparm_comments%3DNEW_CALL_REF:'+sys_id+'%26sysparm_link_parent%3Da663f2c20fe7b900be2bfd4ce1050e2f'
    driver.get(url)
    sleep(2)
    iframe = driver.find_element_by_id('gsft_main')
    driver.switch_to.frame(iframe)
    sleep(2)
    element = driver.find_element_by_id('order_now')
    element.click()

def close(driver):
    driver.close()
    driver.quit()

def createRequest(sys_id, host,user,pwd, headers, message, group = '01277d7537281f4010e81d8643990efa'):
    url = host+ '/api/now/table/new_call/'+str(sys_id)
    #data = json.dumps({'u_service':'35f71052dbb6670447ff303c7c9619aa','call_type': 'Request','request_item': '9d7c5f60f8869000b662f2c5990bd9f5' ,'u_sr_category': 'Support Request', 'Service Offering': 'EDI / B2B Integration Sweden'})
    data = json.dumps({"call_type":"Request","u_service":"35f71052dbb6670447ff303c7c9619aa","request_item":"9d7c5f60f8869000b662f2c5990bd9f5","u_sr_category":"Support Request"})
    answer = putToServiceNow(url, user, pwd, headers, data)

    if answer == 'OK':

        driver = logToTicketSystem(host,user,pwd)
        orderRequest(driver,sys_id,host,user,pwd)

        sleep(3)

        link = ''
        url1 = host + '/api/now/table/new_call?sysparm_query=sys_id=' + sys_id
        response = getFromServiceNow(url1, user, pwd, headers)


        while True:
            link = response.get('result')[0].get('transferred_to')
            print(link)
            if isinstance(link,str):
                sleep(3)
                response = getFromServiceNow(url1, user, pwd, headers)
            else:
                link = link.get('link')
                break
        close(driver)
        if link :
            data = json.dumps({'u_owner':group,'assignment_group':group,'work_notes': '>>'+ message})
            answer = putToServiceNow(link, user, pwd, headers, data)

            if answer == 'OK':
                return 'OK'
            else: return 'ERROR'

    else: return 'ERROR'
