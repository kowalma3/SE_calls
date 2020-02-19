#19.02.2020 - calls1.py
import requests
import uuid
import json
from time import sleep

import conf

def login(log_info):
    '''
    login function put log line into logs.txt file
    '''
    with open('./logs.txt','a+') as fp:
        fp.write(log_info)

def checkLogs(call):
    '''
    checkLogs fuction returns True if call number was processed before,
    else returns False
    '''
    data = ''
    with open('./logs.txt','r') as fp:
        data = fp.read()

    if call in data:
        return True
    else:
        return False


def returnCallToCS(sys_id):
    '''
    returnCallToCS function returns call to CS if needed
    #'''
    pass

def getDataFromServiceNow(url, user, pwd, headers):
    '''
    getDataFromServiceNow method connects to ServiceNow
    and returns json with requested data or ERROR if connection
    problems or URL incorect
    '''


    response = requests.get(url, auth = (user,pwd), headers=headers)

    if response.status_code != 200:
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
def translate(text):
    '''
    translate function simply translate to English using microsofttranslator
    returns ERROR if connection problems, else returns translated text
    '''

    subscriptionKey = conf.SUBSCRIPTIONKEY

    base_url = 'https://api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'
    params = '&from=sv&to=en'
    constructed_url = base_url + path + params


    headers = {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    t=text
    if "Powered by Basware" in t:
        index = t.index('Powered by Basware')
        t = t[0:index]

    body = [{
        'text' : t
    }]


    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()


    t=json.dumps(response, sort_keys=True, indent=4, ensure_ascii=False, separators=(',', ': '))

    i=t.find('\"text\":')
    j=t.find('\"to\"')


    if request.status_code == 400:
        return 'ERROR'
    else:
        return response[0]['translations'][0]['text']

def main():
    '''
    main function defines all steps of this script.
    get calls
    for each call check if duplicate, if yes - return to CS, remove from list, if not translate description
    from each call, create requests
    log date, call -> request in the log file
    send request to proper group
    '''

    #main variables, very important
    host = conf.HOST
    user = conf.USR
    pwd = conf.PWD
    call_queue = conf.CALLS_QUEUE
    were_to_send = conf.WHERE_TO_QUEUE
    headers = {"Content-Type":"application/json","Accept":"application/json"}

    #define queue with calls
    url = host + '/api/now/table/new_call?sysparm_query=call_type=email^u_assignment_group=' + call_queue

    #define list of calls
    callsList = list()

    #each element of list is a dictionary, build af follow:
    d = {
        'sys_id':'',
        'number':'',
        'short_description':'',
        'description_to_be_translate':'',
        'after_translation':'',
        }
    #
    #get data to tmp variable, it is json, that need to be response.json().get('result')

    tmp = getDataFromServiceNow(url, user, pwd, headers)
    #check if connection error if not then extract data from queue
    if tmp != 'ERROR':
        data = tmp.get('result')
        for element in data:

            d['sys_id'] = element.get('sys_id','')
            d['number'] = element.get('number','')
            d['short_description'] = element.get('short_description','')
            d['description_to_be_translate'] = element.get('description','')

            if not checkLogs(element.get('number','')):
                callsList.append(d)
            else:
                returnCallToCS(element.get('sys_id',''))

    #if any call on the list then proceed
    if callsList:
        for element in callsList:
            #variable tmp stores
            tmp = translate(element.get('description_to_be_translate',''))
            if tmp != 'ERROR':
                element['after_translation'] = tmp
            else:
                returnCallToCS(element.get('sys_id',''))
                log_info = 'call + '
                login(log_info)
    else:
        print('No calls in the queue, let wait for another round :D')



if __name__ == '__main__':
    main()
