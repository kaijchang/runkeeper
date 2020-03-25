import requests
from bs4 import BeautifulSoup

import urllib.parse
from datetime import datetime

from .User import User

import typing


class Account(User):
    def __init__(self, email: str, password: str):
        self.session = requests.Session()

        landing_page = BeautifulSoup(self.session.get('https://runkeeper.com').text, 'html.parser')
        login_query_string = urllib.parse.parse_qs(
            urllib.parse.urlparse(landing_page.find(class_='log-in').find('a')['href'][27:-2]).query)

        state = login_query_string['state']

        self.session.post('https://id.asics.com/oauth2/token/auth', data={
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

        authorization_request = self.session.post('https://id.asics.com/oauth2/authorize', params={
            'response_type': 'code',
            'client_id': 'runkeeper',
            'redirect_uri': 'https://runkeeper.com/asicsIDMLogin',
            'state': state
        })

        if authorization_request.history[0].status_code == 303:
            raise ValueError('Incorrect email or password')

        authorization_query_string = urllib.parse.parse_qs(urllib.parse.urlparse(authorization_request.url).query)

        r = self.session.get('https://runkeeper.com/asicsIDMLogin', params={
            'submit': '',
            'code': authorization_query_string['code'][0],
            'state': authorization_query_string['state'][0],
            'error': ''
        })

        home_page = BeautifulSoup(r.text, 'html.parser')
        super().__init__(home_page.find(class_='feed')['data-feedownerurl'])

    def get_activity_list(self) -> typing.Dict[int, typing.Dict[int, int]]:
        """
        Example Return:
        {2020: {1: 10, 2: 11, 3: 15}}
        this would mean 10 activities in January 2020, 11 in February 2020, and 15 in March 2020

        :return: number of activities for each month with at least one activity
        :rtype: dict
        """
        activities = {}

        activity_list_page = BeautifulSoup(
            self.session.get('https://runkeeper.com/user/{0}/activitylist'.format(self.username)).text, 'html.parser')

        for month in activity_list_page.find_all(class_='accordion'):
            date = datetime.strptime(month['data-date'], '%b-%d-%Y')
            if activities.get(date.year) is None:
                activities[date.year] = {}

            activities[date.year][date.month] = int(month.find(class_='activityCount').text)

        return activities
