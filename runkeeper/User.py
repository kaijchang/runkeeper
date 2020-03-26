import requests
from bs4 import BeautifulSoup

from urllib import parse
from datetime import datetime

import typing

FAILURE_MESSAGE = '[Failed to render "pageContent". See log for details.]'


def _check_for_failure(page: BeautifulSoup) -> bool:
    main_div = page.find('div', class_='bodyRow expand')
    return main_div is not None and main_div.text.strip() == FAILURE_MESSAGE


def _throw_perm_error():
    raise PermissionError('This data is private or not visible to you')


class User:
    def __init__(self, username: str, transport: requests = requests):
        self.username = username
        self.transport = transport

    def get_activity_count(self) -> typing.Dict[int, typing.Dict[int, int]]:
        """
        Example Return:
        {2020: {1: 10, 2: 11, 3: 15}}
        this would mean 10 activities in January 2020, 11 in February 2020, and 15 in March 2020

        :return: number of activities for each month with at least one activity
        :rtype: typing.Dict[int, typing.Dict[int, int]]
        """
        activity_list_page = BeautifulSoup(
            self.transport.get('https://runkeeper.com/user/{0}/activitylist'.format(self.username)).text, 'html.parser')

        if _check_for_failure(activity_list_page):
            _throw_perm_error()

        activities = {}

        for month in activity_list_page.find_all(class_='accordion'):
            date = datetime.strptime(month['data-date'], '%b-%d-%Y')
            if activities.get(date.year) is None:
                activities[date.year] = {}

            activities[date.year][date.month] = int(month.find(class_='activityCount').text)

        return activities

    def get_activities(self, month: int = None, year: int = None) -> typing.List[typing.Dict[str, str]]:
        """
        :param month: (optional) month of specified year to fetch activities for, current month by default
        :type month: int
        :param year: (optional) year to fetch activities for, current year by default
        :type year: int
        :return: list of activities from the specified month
        :rtype: typing.List[typing.Dict[str, str]]
        """
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year

        start_date = datetime(year, month, 1)
        activities = requests.get('https://runkeeper.com/activitiesByDateRange', params={
            'userName': self.username,
            'startDate': start_date.strftime('%b-%d-%Y')
        }).json()['activities']

        if len(activities) > 0:
            return activities[str(start_date.year)][start_date.strftime('%b')]
        else:
            return []

    def get_activity_data(self, activity_id: typing.Union[str, int]) -> typing.Dict[str, str]:
        """
        :param activity_id: id for activity to get
        :type activity_id: typing.Union[str, int]
        :return: summary of activity data including trip uuid
        :rtype: typing.Dict[str, str]
        """
        activity_page = BeautifulSoup(self.transport.get(
                'https://runkeeper.com/user/{0}/activity/{1}'.format(self.username, activity_id)).text, 'html.parser')

        if _check_for_failure(activity_page):
            _throw_perm_error()

        data = {}

        for stats_item in activity_page.find_all(class_='statsItem'):
            value_span = stats_item.find('span', class_='value')
            if value_span is not None:
                data['_'.join(stats_item.find('h5').text.split()).lower()] = stats_item.find(class_='value').text

        data['trip_uuid'] = parse.parse_qs(parse.urlparse(
             activity_page.find('meta', {'name': 'twitter:app:url:iphone'})['content']).query)['tripuuid'][0]

        return data

    def get_trip_point_data(self, trip_uuid: str) -> typing.Optional[typing.Dict[str, typing.Union[str, dict]]]:
        """
        :param trip_uuid: trip to get point data for
        :type trip_uuid: str
        :return: detailed point data from the specified
        :rtype: typing.Dict[str, typing.Union[str, dict]]
        """
        point_data_request = self.transport.get('https://runkeeper.com/ajax/pointData', params={
            'tripUuid': trip_uuid
        })

        if point_data_request.status_code == 403:
            _throw_perm_error()

        if point_data_request.status_code == 400:
            # no trip points (activity entered manually)
            return None

        return point_data_request.json()
