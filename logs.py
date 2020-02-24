def login(log_info):
    '''
    login function put log line into logs.txt file
    '''

    with open('logs.txt','a+') as fp:
        fp.write('\n'+log_info)

def checkLogs(call):
    '''
    checkLogs fuction returns True if  number was processed before,
    else returns False
    '''

    data = ''
    with open('logs.txt','r') as fp:
        data = fp.read()

    if  call in data:
        return True
    else:
        return False
