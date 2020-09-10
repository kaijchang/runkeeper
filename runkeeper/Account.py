import requests
from bs4 import BeautifulSoup

from urllib import parse

from .User import User


class Account(User):
    def __init__(self, email: str, password: str):
        session = requests.Session()

        login_request = session.get('https://runkeeper.com/login')
        login_query_string = parse.parse_qs(parse.urlparse(login_request.url).query)

        state = login_query_string['state'][0]

        session.post('https://id.asics.com/oauth2/token/auth', data={
            'username': email,
            'password': password,
            'language': 'en',
            'locale': 'en-US',
            'grant_type': 'password',
            'client_id': 'runkeeper',
            'style': 'runkeeper',
            'max_cookie_timeout': '',
            'platform': 'web'
        })

        authorization_request = session.post('https://id.asics.com/oauth2/authorize', params={
            'response_type': 'code',
            'client_id': 'runkeeper',
            'redirect_uri': 'https://runkeeper.com/asicsIDMLogin',
            'state': state
        })

        if authorization_request.history[0].status_code == 303:
            raise ValueError('Incorrect email or password')

        authorization_query_string = parse.parse_qs(parse.urlparse(authorization_request.url).query)

        r = session.get('https://runkeeper.com/asicsIDMLogin', params={
            'submit': '',
            'code': authorization_query_string['code'][0],
            'state': authorization_query_string['state'][0],
            'error': ''
        })

        home_page = BeautifulSoup(r.text, 'html.parser')
        super().__init__(home_page.find(class_='feed')['data-feedownerurl'], session)

    def make_proxy_user(self, username: str):
        return User(username, self.transport)
