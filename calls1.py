#24.02.2020 - calls1.py
import requests
import uuid
import json
from time import sleep

import conf
import translate
import logs
import snc
import os

def main():
    '''main function '''

    #main variables

    host = conf.HOST
    user = conf.USR
    pwd = conf.PWD
    call_queue = conf.CALLS_QUEUE
    were_to_send = conf.WHERE_TO_QUEUE
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    #define queue with calls
    url = host + '/api/now/table/new_call?sysparm_query=call_type=email^u_assignment_group=' + call_queue
    #define list of calls
    callList = list()

    #each element of list is a dictionary, build af follow:



    #get data to tmp variable, it is json, that need to be response.json().get('result')

    tmp = snc.getFromServiceNow(url, user, pwd, headers)

    data = tmp.get('result')


    for element in data:
        d = dict()
        d['sys_id'] = element.get('sys_id','')
        d['number'] = element.get('number','')
        d['short_description'] = element.get('short_description','')
        d['description_to_be_translate'] = element.get('description','')
        d['after_translation'] = translate.translate(element.get('description'))

        if not logs.checkLogs(element.get('number','')):
            callList.append(d)
        else:
            message = "Call was already processed"
            sys_id = element.get('sys_id','')
            snc.returnCallToCS(sys_id, host, user, pwd, headers, message)

    print(callList)

    for element in callList:
        message = element.get('after_translation')
        answer = snc.createRequest(element.get('sys_id',''), host, user, pwd, headers, message)
        sleep(10)
        print('po slipie')
        if answer == 'OK':
            log_info = element.get('number','') + 'request DONE'
            logs.login(log_info)
        else:
            snc.returnCallToCS(element.get('sys_id',''), host,user, pwd, headers, 'translation error, please handle')
            log_info = element.get('number','') + 'translation error, return to CS'
            login(log_info)


if __name__ == '__main__':
    main()
