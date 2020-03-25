import requests
from bs4 import BeautifulSoup

import time
import urllib.parse


def login(username, password):
    session = requests.Session()

    r = session.get('https://runkeeper.com')
    soup = BeautifulSoup(r.text, 'html.parser')
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(soup.find(class_='log-in').find('a')['href'][27:-2]).query)

    state = qs['state']

    session.post('https://id.asics.com/oauth2/token/auth', data={
        'username': username,
        'password': password,
        'language': 'en',
        'locale': 'en-US',
        'grant_type': 'password',
        'client_id': 'runkeeper',
        'style': 'runkeeper',
        'max_cookie_timeout': '',
        'platform': 'web'
    })

    r = session.post('https://id.asics.com/oauth2/authorize', params={
        'response_type': 'code',
        'client_id': 'runkeeper',
        'redirect_uri': 'https://runkeeper.com/asicsIDMLogin',
        'state': state
    })

    qs = urllib.parse.parse_qs(urllib.parse.urlparse(r.url).query)
    r = session.get('https://runkeeper.com/asicsIDMLogin', params={
        'submit': '',
        'code': qs['code'][0],
        'state': qs['state'][0],
        'error': ''
    })

    assert r.url == 'https://runkeeper.com/home?llsignup=false'
    print('Success!')

    return session


session = login('', '')
