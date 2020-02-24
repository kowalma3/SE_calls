import requests
from time import sleep
import json

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

def createRequest(sys_id, host,user,pwd, headers, message, group = '01277d7537281f4010e81d8643990efa'):
    url = host+ '/api/now/table/new_call/'+str(sys_id)
    data = json.dumps({'u_service':'35f71052dbb6670447ff303c7c9619aa','call_type': 'Request','request_item': 'Change request' ,'u_sr_category': 'Support Request', 'Service Offering': 'EDI / B2B Integration Sweden'})

    answer = putToServiceNow(url, user, pwd, headers, data)

    if answer == 'OK':
        sleep(3)
        link = ''
        url1 = host + '/api/now/table/new_call?sysparm_query=sys_id=' + sys_id
        response = getFromServiceNow(url1, user, pwd, headers)

        while True:
            link = response.get('result')[0].get('transferred_to')
            if isinstance(link,str):
                sleep(3)
                response = getFromServiceNow(url1, user, pwd, headers)
            else:
                link = link.get('link')
                break

        if link :
            data = json.dumps({'u_owner':group,'assignment_group':group,'work_notes': '>>'+ message})
            answer = putToServiceNow(link, user, pwd, headers, data)

            if answer == 'OK':
                return 'OK'
            else: return 'ERROR'

    else: return 'ERROR'
