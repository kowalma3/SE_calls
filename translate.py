import uuid
import json
import conf
import requests

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
